"""``/v1/billing`` + ``/v1/checkout`` + ``/v1/creator/onboarding`` + ``/v1/orders``.

These all live under one router file for cohesion — each has its own
URL prefix. Frontend grouping in :mod:`apps/web-marketplace/lib/api/billing.ts`
matches.

Spec: ``prompts/marketplace/03-pricing-and-checkout.md``.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.deps import (
    current_active_user,
    get_redis,
    require_creator,
)
from src.billing import service as billing_service
from src.billing.fees import breakdown
from src.billing.models import (
    License,
    Order,
    OrderStatus,
)
from src.billing.schemas import (
    BillingPortalResponse,
    CheckoutSessionResponse,
    CreateCheckoutSessionRequest,
    FinalizeResponse,
    LicenseRead,
    OnboardingStartResponse,
    OnboardingStatusResponse,
    OrderItemRead,
    OrderListResponse,
    OrderRead,
    PriceBreakdown,
    RefundRequest,
    StartOnboardingRequest,
)
from src.core.db import get_db
from src.core.errors import AppError, ErrorDetail, error_responses
from src.personas.service import check_persona_checkout_entitlement
from src.skills.models import Skill, SkillKind
from src.users.models import User

log = logging.getLogger(__name__)

# Three logical sub-prefixes share one APIRouter to keep imports tidy.
router = APIRouter(tags=["billing"])


# ── Checkout sessions ─────────────────────────────────────────────────
@router.post(
    "/v1/checkout/sessions",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Stripe Checkout Session (one-time purchase)",
    responses=error_responses(401, 404, 409, 422, 502),
)
async def create_checkout_session(
    payload: CreateCheckoutSessionRequest,
    request: Request,
    idempotency_header: str | None = Header(default=None, alias="Idempotency-Key"),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
) -> CheckoutSessionResponse:
    """Begin a Stripe Checkout flow for ``skill_id``.

    Idempotent on ``(user_id, Idempotency-Key)`` — re-invocations with the
    same key return the cached response. ``payload.idempotency_key`` is a
    body-level fallback for clients that can't set headers.

    Validation: skill is ``published``, not yanked, buyer doesn't already
    own it, creator has ``payouts_enabled``. See
    :func:`src.billing.service.assert_skill_purchasable`.
    """
    idem_key = idempotency_header or payload.idempotency_key or ""
    redis = get_redis()
    cached = await billing_service.get_cached_idempotent(redis, user.id, idem_key)
    if cached:
        return CheckoutSessionResponse(**cached)

    skill = await session.get(Skill, payload.skill_id)
    if skill is None:
        raise AppError(
            code="resource.not_found",
            message="Skill not found.",
            status_code=404,
        )

    # T-04 acceptance bullet 2: persona purchases require an active license
    # on the parent occupation. The gate is a no-op for any other ``kind``.
    if skill.kind == SkillKind.PERSONA:
        gate = await check_persona_checkout_entitlement(
            session, buyer=user, skill=skill
        )
        if not gate.ok:
            raise AppError(
                code="persona.requires_parent_occupation",
                message=(
                    "Buy the parent occupation first."
                ),
                status_code=409,
                details=[
                    ErrorDetail(
                        field="parent_occupation_id",
                        code="missing_license",
                        message=(
                            "Buyer does not hold an active license on the "
                            f"parent occupation (slug="
                            f"{gate.parent_occupation_slug or 'unknown'})."
                        ),
                    )
                ],
            )

    result = await billing_service.create_checkout_session(
        session, buyer=user, skill=skill
    )
    await session.commit()

    response = {
        "session_id": result["session_id"],
        "checkout_url": result["checkout_url"],
    }
    await billing_service.set_cached_idempotent(redis, user.id, idem_key, response)
    return CheckoutSessionResponse(**response)


@router.post(
    "/v1/checkout/sessions/{session_id}/finalize",
    response_model=FinalizeResponse,
    summary="Poll a Checkout Session for completion (UI helper)",
    responses=error_responses(401, 404),
)
async def finalize_checkout_session(
    session_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
) -> FinalizeResponse:
    """Confirm a Stripe Checkout Session for UI loading states.

    **The source of truth is the webhook**, not this call. Frontend
    polls this to know when the webhook has issued the license.
    """
    order = await billing_service.get_order_by_session_id(
        session, buyer=user, stripe_session_id=session_id
    )
    if order is None:
        return FinalizeResponse(session_id=session_id, status="open")

    # Find license (if granted yet).
    items = (
        await session.execute(
            select(License)
            .join(Order, Order.id == order.id)
            .where(License.buyer_id == user.id)
            .order_by(desc(License.granted_at))
        )
    ).scalars().all()
    license_id: uuid.UUID | None = items[0].id if items else None

    status_str = "complete" if order.status == OrderStatus.PAID else order.status.value
    return FinalizeResponse(
        session_id=session_id,
        status=status_str,
        order_id=order.id,
        license_id=license_id,
    )


# ── Orders ────────────────────────────────────────────────────────────
@router.get(
    "/v1/orders/me",
    response_model=OrderListResponse,
    summary="List the current user's recent orders",
    responses=error_responses(401),
)
async def list_my_orders(
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
) -> OrderListResponse:
    res = await session.execute(
        select(Order)
        .where(Order.buyer_id == user.id)
        .order_by(desc(Order.placed_at), desc(Order.created_at))
        .limit(limit)
    )
    orders = list(res.scalars().all())

    # Eager-load items per order to avoid N+1 on the response build.
    items_map: dict[uuid.UUID, list[OrderItemRead]] = {}
    if orders:
        order_ids = [o.id for o in orders]
        from src.billing.models import OrderItem  # local import

        items_res = await session.execute(
            select(OrderItem).where(OrderItem.order_id.in_(order_ids))
        )
        for it in items_res.scalars().all():
            items_map.setdefault(it.order_id, []).append(
                OrderItemRead.model_validate(it)
            )

    out: list[OrderRead] = []
    for o in orders:
        m = OrderRead.model_validate(o).model_dump()
        m["items"] = [item.model_dump() for item in items_map.get(o.id, [])]
        m["status"] = o.status.value if hasattr(o.status, "value") else o.status
        out.append(OrderRead.model_validate(m))

    return OrderListResponse(
        items=out,
        page={"next_cursor": None, "has_more": False, "limit": limit},
    )


@router.get(
    "/v1/orders/by-session/{session_id}",
    response_model=OrderRead | None,
    summary="Resolve an order from a Stripe Checkout Session id",
    responses=error_responses(401, 404),
)
async def get_order_by_session(
    session_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
) -> OrderRead | None:
    order = await billing_service.get_order_by_session_id(
        session, buyer=user, stripe_session_id=session_id
    )
    if order is None:
        return None
    return OrderRead.model_validate(order)


@router.post(
    "/v1/orders/{order_id}/refund",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request a refund for a one-time order",
    responses=error_responses(401, 403, 404, 409, 502),
)
async def refund_order(
    order_id: uuid.UUID,
    payload: RefundRequest,
    idempotency_header: str | None = Header(default=None, alias="Idempotency-Key"),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    redis = get_redis()
    cached = await billing_service.get_cached_idempotent(
        redis, user.id, idempotency_header or ""
    )
    if cached:
        return cached  # type: ignore[return-value]

    order = await session.get(Order, order_id)
    if order is None:
        raise AppError(code="resource.not_found", message="Order not found.", status_code=404)
    if order.buyer_id != user.id and not user.is_admin:
        raise AppError(code="auth.forbidden", message="Not your order.", status_code=403)

    await billing_service.issue_refund(
        session, order=order, actor=user, reason=payload.reason
    )
    await session.commit()
    response = {"status": "refund_pending"}
    await billing_service.set_cached_idempotent(
        redis, user.id, idempotency_header or "", response
    )
    return response


# ── Stripe Connect onboarding ─────────────────────────────────────────
@router.post(
    "/v1/creator/onboarding/start",
    response_model=OnboardingStartResponse,
    summary="Start Stripe Connect Express onboarding",
    responses=error_responses(401, 422, 502),
)
async def onboarding_start(
    payload: StartOnboardingRequest,
    user: User = Depends(require_creator),
    session: AsyncSession = Depends(get_db),
) -> OnboardingStartResponse:
    result = await billing_service.start_connect_onboarding(
        session, user=user, payout_country=payload.payout_country
    )
    await session.commit()
    return OnboardingStartResponse(**result)


@router.get(
    "/v1/creator/onboarding/status",
    response_model=OnboardingStatusResponse,
    summary="Re-fetch Stripe Connect account status",
    responses=error_responses(401, 502),
)
async def onboarding_status(
    user: User = Depends(require_creator),
    session: AsyncSession = Depends(get_db),
) -> OnboardingStatusResponse:
    result = await billing_service.fetch_connect_status(session, user=user)
    await session.commit()
    return OnboardingStatusResponse(**result)


# ── Billing portal ────────────────────────────────────────────────────
@router.post(
    "/v1/billing/portal-session",
    response_model=BillingPortalResponse,
    summary="Open the Stripe Customer billing portal",
    responses=error_responses(401, 404, 502),
)
async def billing_portal(
    user: User = Depends(current_active_user),
) -> BillingPortalResponse:
    url = await billing_service.create_billing_portal(user)
    return BillingPortalResponse(url=url)


# ── Price preview helper (used by the checkout summary card) ──────────
@router.get(
    "/v1/billing/preview",
    response_model=PriceBreakdown,
    summary="Compute platform-fee breakdown for a price",
)
async def preview_price(
    amount_cents: int = Query(..., ge=0, le=10_000_000),
) -> PriceBreakdown:
    b = breakdown(amount_cents)
    return PriceBreakdown(
        amount_cents=amount_cents,
        platform_fee_cents=b["platform_fee_cents"],
        creator_payout_cents=b["creator_payout_cents"],
    )
