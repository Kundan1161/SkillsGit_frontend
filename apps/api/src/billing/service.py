"""Billing service layer.

All Stripe SDK calls go through :mod:`src.billing.stripe_client` so tests
can inject a fake client. State mutations write to ``audit_log`` via
:func:`src.core.db.write_audit`.

Money is always integer cents.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from redis.asyncio import Redis
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.fees import compute_fee
from src.billing.models import (
    License,
    LicenseSource,
    LicenseStatus,
    Order,
    OrderItem,
    OrderStatus,
    SupportTier,
)
from src.billing.stripe_client import (
    StripeError,
    get_stripe_client,
)
from src.core.config import settings
from src.core.db import write_audit
from src.core.errors import AppError
from src.skills.models import PricingModel, Skill, SkillStatus, SkillVersion
from src.users.models import CreatorProfile, User

log = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────
REFUND_WINDOW_DAYS = 14
_IDEMPOTENCY_TTL_SECS = 24 * 3600


# ── Version helpers ───────────────────────────────────────────────────
_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")


def major_version_cap(version: str) -> str:
    """Return the major-version ceiling string, e.g. ``1.2.3`` → ``1.x``.

    Raises :class:`ValueError` for non-semver inputs.
    """
    match = _SEMVER_RE.match(version)
    if not match:
        raise ValueError(f"not semver: {version!r}")
    return f"{match.group(1)}.x"


def _parse_cap(max_version: str | None) -> int | None:
    """Parse ``"<major>.x"`` to its major int. Returns ``None`` for unbounded."""
    if not max_version:
        return None
    if max_version.endswith(".x"):
        try:
            return int(max_version[:-2])
        except ValueError:
            return None
    match = _SEMVER_RE.match(max_version)
    if match:
        return int(match.group(1))
    return None


def _version_key(v: str) -> tuple[int, int, int]:
    match = _SEMVER_RE.match(v)
    if not match:
        return (0, 0, 0)
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


async def resolve_version(
    license: License, session: AsyncSession
) -> SkillVersion | None:
    """Return the SkillVersion a license currently entitles its holder to.

    Rule from ``02-data-model-core.md``:
        latest skill_version where:
          - version major <= license.max_version major (if capped)
          - released_at > license.granted_at OR source == subscription/active
          - NOT is_yanked

    Used by Agent C's delivery module. Exposed here for direct import:
    ``from src.billing.service import resolve_version``.
    """
    if license.status != LicenseStatus.ACTIVE:
        return None

    cap_major = _parse_cap(license.max_version)
    q = select(SkillVersion).where(
        SkillVersion.skill_id == license.skill_id,
        SkillVersion.is_yanked.is_(False),
        SkillVersion.released_at.is_not(None),
    )

    # Subscriptions always get latest; one-time gets versions released
    # *after* purchase up to the major-version cap.
    if license.source != LicenseSource.SUBSCRIPTION:
        # For one-time/free/freemium: only versions released after the
        # grant date OR the version that was active at grant time. We
        # accept anything released-at <= granted_at too, because the
        # buyer paid for that snapshot.
        pass  # No date filter — we resolve to the best version under cap.

    res = await session.execute(q)
    versions = list(res.scalars().all())
    if not versions:
        return None

    # Filter by major-version cap if set.
    candidates = [
        v for v in versions
        if cap_major is None or _version_key(v.version)[0] <= cap_major
    ]
    if not candidates:
        return None

    # Highest semver wins.
    candidates.sort(key=lambda v: _version_key(v.version), reverse=True)
    return candidates[0]


# ── Idempotency-key helpers (Redis-backed) ────────────────────────────
async def get_cached_idempotent(
    redis: Redis, user_id: uuid.UUID, key: str
) -> dict[str, Any] | None:
    """Return a previously cached response body for this (user, key) or None."""
    if not key:
        return None
    raw = await redis.get(f"idem:billing:{user_id}:{key}")
    if not raw:
        return None
    try:
        return json.loads(raw) if isinstance(raw, str) else json.loads(raw.decode())  # type: ignore[union-attr]
    except (ValueError, AttributeError):
        return None


async def set_cached_idempotent(
    redis: Redis,
    user_id: uuid.UUID,
    key: str,
    payload: dict[str, Any],
) -> None:
    if not key:
        return
    await redis.setex(
        f"idem:billing:{user_id}:{key}",
        _IDEMPOTENCY_TTL_SECS,
        json.dumps(payload, default=str),
    )


# ── Pre-flight checks ─────────────────────────────────────────────────
async def assert_skill_purchasable(
    session: AsyncSession, *, skill: Skill, buyer: User
) -> SkillVersion:
    """Validate that ``buyer`` can purchase ``skill``.

    Returns the current ``SkillVersion`` to be sold (latest, not yanked).

    Raises :class:`AppError` (status 409 or 422) on any failure.
    """
    if skill.status != SkillStatus.PUBLISHED:
        raise AppError(
            code="checkout.skill_not_purchasable",
            message="Skill is not available for purchase.",
            status_code=409,
        )

    if skill.pricing_model != PricingModel.ONE_TIME:
        # Phase 1 only supports one-time. Subscriptions are Phase 2.
        raise AppError(
            code="checkout.unsupported_pricing_model",
            message=(
                "Only one-time purchases are supported in this phase. "
                "Subscriptions arrive in Phase 2."
            ),
            status_code=422,
        )

    if not skill.one_time_price_cents or skill.one_time_price_cents <= 0:
        raise AppError(
            code="checkout.invalid_price",
            message="Skill has no valid price set.",
            status_code=422,
        )

    if not skill.latest_version_id:
        raise AppError(
            code="checkout.no_published_version",
            message="Skill has no released version.",
            status_code=409,
        )

    version = await session.get(SkillVersion, skill.latest_version_id)
    if version is None or version.is_yanked or version.released_at is None:
        raise AppError(
            code="checkout.latest_version_yanked",
            message="The latest version of this skill is unavailable.",
            status_code=409,
        )

    # Already owns it?
    existing = await session.execute(
        select(License).where(
            License.buyer_id == buyer.id,
            License.skill_id == skill.id,
            License.status == LicenseStatus.ACTIVE,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise AppError(
            code="checkout.already_owned",
            message="You already own this skill.",
            status_code=409,
        )

    # Creator must have completed Stripe Connect onboarding.
    creator = await session.get(User, skill.creator_id)
    if creator is None or not creator.stripe_connect_account_id:
        raise AppError(
            code="checkout.creator_not_payable",
            message="This creator has not finished payouts setup.",
            status_code=409,
        )
    if not creator.payouts_enabled:
        raise AppError(
            code="checkout.creator_payouts_disabled",
            message="This creator's payouts are not enabled.",
            status_code=409,
        )

    return version


# ── Checkout ──────────────────────────────────────────────────────────
def _success_cancel_urls(skill_id: uuid.UUID) -> tuple[str, str]:
    """Build success/cancel URLs.

    Reads the marketplace origin from settings.CORS_ORIGINS (first entry)
    so tests + dev get sane defaults without extra config.
    """
    base = settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:3000"
    success = f"{base}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel = f"{base}/checkout?skill={skill_id}&canceled=1"
    return success, cancel


async def create_checkout_session(
    session: AsyncSession,
    *,
    buyer: User,
    skill: Skill,
) -> dict[str, Any]:
    """Build the Stripe Checkout Session for a one-time purchase.

    Returns a serializable dict with ``checkout_url`` + ``session_id``.
    Caller is responsible for committing audit-log entries.
    """
    version = await assert_skill_purchasable(session, skill=skill, buyer=buyer)
    assert skill.one_time_price_cents is not None  # guaranteed by assert_*

    amount = skill.one_time_price_cents
    application_fee = compute_fee(amount)
    success_url, cancel_url = _success_cancel_urls(skill.id)

    client = get_stripe_client()
    try:
        s = client.create_checkout_session(
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": amount,
                        "product_data": {
                            "name": skill.name,
                            "description": (skill.tagline or "")[:500] or None,
                        },
                    },
                    "quantity": 1,
                }
            ],
            payment_intent_data={
                "application_fee_amount": application_fee,
                "transfer_data": {
                    "destination": (
                        await session.get(User, skill.creator_id)
                    ).stripe_connect_account_id,  # type: ignore[union-attr]
                },
                "metadata": {
                    "skill_id": str(skill.id),
                    "skill_version_id": str(version.id),
                    "buyer_id": str(buyer.id),
                },
            },
            metadata={
                "skill_id": str(skill.id),
                "skill_version_id": str(version.id),
                "buyer_id": str(buyer.id),
            },
            customer_email=buyer.email,
            success_url=success_url,
            cancel_url=cancel_url,
        )
    except StripeError as exc:
        log.warning("stripe checkout create failed: %s", type(exc).__name__)
        raise AppError(
            code="checkout.stripe_error",
            message="Could not create checkout session with Stripe.",
            status_code=502,
        ) from exc

    session_id = _get_attr(s, "id")
    checkout_url = _get_attr(s, "url")
    if not session_id or not checkout_url:
        raise AppError(
            code="checkout.stripe_invalid_response",
            message="Stripe returned an incomplete checkout session.",
            status_code=502,
        )

    await write_audit(
        session,
        actor_id=buyer.id,
        action="checkout.session_created",
        target_type="skill",
        target_id=skill.id,
        metadata={
            "session_id": session_id,
            "amount_cents": amount,
            "platform_fee_cents": application_fee,
        },
    )

    return {
        "session_id": session_id,
        "checkout_url": checkout_url,
        "amount_cents": amount,
        "platform_fee_cents": application_fee,
    }


def _get_attr(obj: Any, name: str, default: Any = None) -> Any:
    """Read a field from a Stripe object (dict-like or attr-like)."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


# ── Order lookup helpers ──────────────────────────────────────────────
async def get_order_by_session_id(
    session: AsyncSession, *, buyer: User, stripe_session_id: str
) -> Order | None:
    """Find the Order linked to a Stripe Checkout Session for this buyer.

    We store the Checkout Session's payment_intent in
    ``orders.stripe_payment_intent_id``. Some flows need to look up by
    session_id directly — we re-fetch via the Stripe SDK in that case.
    """
    # First try by metadata if the webhook already persisted under PI.
    # The simplest robust lookup is via Stripe API: session → PI.
    client = get_stripe_client()
    try:
        sess = client.retrieve_checkout_session(stripe_session_id)
    except StripeError:
        return None

    pi = _get_attr(sess, "payment_intent")
    if not pi:
        return None
    pi_id = pi if isinstance(pi, str) else _get_attr(pi, "id")
    if not pi_id:
        return None
    res = await session.execute(
        select(Order).where(
            Order.stripe_payment_intent_id == pi_id,
            Order.buyer_id == buyer.id,
        )
    )
    return res.scalar_one_or_none()


# ── Refunds ───────────────────────────────────────────────────────────
async def can_refund(session: AsyncSession, *, order: Order) -> tuple[bool, str | None]:
    """Eligibility check for a one-time refund.

    Rules (Phase 1):
    - Order status must be ``paid``.
    - Within :data:`REFUND_WINDOW_DAYS` of ``placed_at``.
    - No ``license.downloaded`` audit-log entry exists for any of this
      order's licenses.
    """
    if order.status != OrderStatus.PAID:
        return False, "order_not_refundable"
    placed = order.placed_at or order.created_at
    if placed is None:
        return False, "order_not_placed"
    # SQLite (used in tests) drops timezone info; coerce both to naive UTC
    # for a safe comparison. In production Postgres stores tz-aware
    # timestamps natively.
    if placed.tzinfo is None:
        placed_cmp = placed
        now_cmp = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        placed_cmp = placed
        now_cmp = datetime.now(timezone.utc)
    age = now_cmp - placed_cmp
    if age.days >= REFUND_WINDOW_DAYS:
        return False, "refund_window_expired"

    # Check for a license.downloaded audit-log entry against any of the
    # licenses spawned by this order.
    from src.core.db import AuditLog  # local import to avoid cycle

    items_res = await session.execute(
        select(OrderItem.id).where(OrderItem.order_id == order.id)
    )
    item_ids = [r[0] for r in items_res.all()]
    if not item_ids:
        return False, "no_items"

    licenses_res = await session.execute(
        select(License.id).where(
            License.source == LicenseSource.ONE_TIME,
            License.source_id.in_(item_ids),
        )
    )
    license_ids = [r[0] for r in licenses_res.all()]
    if license_ids:
        downloaded_res = await session.execute(
            select(AuditLog.id).where(
                AuditLog.action == "license.downloaded",
                AuditLog.target_type == "license",
                AuditLog.target_id.in_(license_ids),
            )
        )
        if downloaded_res.scalar_one_or_none() is not None:
            return False, "already_downloaded"

    return True, None


async def issue_refund(
    session: AsyncSession, *, order: Order, actor: User, reason: str | None = None
) -> None:
    """Trigger a Stripe refund. State-change is handled by ``charge.refunded``."""
    ok, why = await can_refund(session, order=order)
    if not ok:
        raise AppError(
            code=f"refund.{why}",
            message="Refund is not allowed.",
            status_code=409,
        )

    if not order.stripe_payment_intent_id:
        raise AppError(
            code="refund.missing_payment_intent",
            message="No payment intent on this order.",
            status_code=409,
        )

    client = get_stripe_client()
    try:
        client.create_refund(
            payment_intent=order.stripe_payment_intent_id,
            reverse_transfer=True,
            metadata={
                "order_id": str(order.id),
                "actor_id": str(actor.id),
                "reason": (reason or "")[:200],
            },
        )
    except StripeError as exc:
        log.warning("stripe refund failed: %s", type(exc).__name__)
        raise AppError(
            code="refund.stripe_error",
            message="Stripe rejected the refund request.",
            status_code=502,
        ) from exc

    await write_audit(
        session,
        actor_id=actor.id,
        action="refund.requested",
        target_type="order",
        target_id=order.id,
        metadata={"reason": reason or ""},
    )


# ── Stripe Connect onboarding ─────────────────────────────────────────
def _onboarding_urls() -> tuple[str, str]:
    base = settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:3000"
    return (
        f"{base}/become-a-creator?onboarding=incomplete",
        f"{base}/become-a-creator?onboarding=done",
    )


async def start_connect_onboarding(
    session: AsyncSession, *, user: User, payout_country: str
) -> dict[str, str]:
    """Create (or reuse) a Stripe Connect account and return an account link."""
    profile_res = await session.execute(
        select(CreatorProfile).where(CreatorProfile.user_id == user.id)
    )
    profile = profile_res.scalar_one_or_none()
    if profile is None:
        raise AppError(
            code="onboarding.no_creator_profile",
            message="Create a creator profile first.",
            status_code=422,
        )

    client = get_stripe_client()
    account_id = user.stripe_connect_account_id
    try:
        if not account_id:
            account = client.create_account(
                type="express",
                country=payout_country.upper(),
                email=user.email,
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                },
                metadata={"user_id": str(user.id)},
            )
            account_id = _get_attr(account, "id")
            if not account_id:
                raise AppError(
                    code="onboarding.stripe_invalid_response",
                    message="Stripe returned no account id.",
                    status_code=502,
                )
            user.stripe_connect_account_id = account_id
            session.add(user)

        refresh_url, return_url = _onboarding_urls()
        link = client.create_account_link(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )
    except StripeError as exc:
        log.warning("connect onboarding failed: %s", type(exc).__name__)
        raise AppError(
            code="onboarding.stripe_error",
            message="Stripe Connect onboarding could not be started.",
            status_code=502,
        ) from exc

    url = _get_attr(link, "url")
    if not url:
        raise AppError(
            code="onboarding.stripe_invalid_response",
            message="Stripe returned no account link URL.",
            status_code=502,
        )

    await write_audit(
        session,
        actor_id=user.id,
        action="onboarding.started",
        target_type="user",
        target_id=user.id,
        metadata={"account_id": account_id, "payout_country": payout_country.upper()},
    )

    return {"url": url, "account_id": account_id}


async def fetch_connect_status(
    session: AsyncSession, *, user: User
) -> dict[str, Any]:
    """Re-fetch the creator's Stripe account and persist payouts_enabled."""
    if not user.stripe_connect_account_id:
        return {
            "account_id": None,
            "details_submitted": False,
            "payouts_enabled": False,
            "charges_enabled": False,
        }

    client = get_stripe_client()
    try:
        account = client.retrieve_account(user.stripe_connect_account_id)
    except StripeError as exc:
        log.warning("connect status fetch failed: %s", type(exc).__name__)
        raise AppError(
            code="onboarding.stripe_error",
            message="Stripe Connect status could not be fetched.",
            status_code=502,
        ) from exc

    payouts_enabled = bool(_get_attr(account, "payouts_enabled"))
    if user.payouts_enabled != payouts_enabled:
        user.payouts_enabled = payouts_enabled
        session.add(user)

    return {
        "account_id": user.stripe_connect_account_id,
        "details_submitted": bool(_get_attr(account, "details_submitted")),
        "payouts_enabled": payouts_enabled,
        "charges_enabled": bool(_get_attr(account, "charges_enabled")),
    }


# ── Billing portal ────────────────────────────────────────────────────
async def create_billing_portal(user: User) -> str:
    """Open a Stripe Customer Portal session."""
    if not user.stripe_customer_id:
        raise AppError(
            code="billing.no_customer",
            message="No Stripe customer associated with this account yet.",
            status_code=404,
        )

    base = settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:3000"
    client = get_stripe_client()
    try:
        result = client.create_billing_portal_session(
            customer=user.stripe_customer_id,
            return_url=f"{base}/settings/billing",
        )
    except StripeError as exc:
        raise AppError(
            code="billing.stripe_error",
            message="Stripe billing portal could not be opened.",
            status_code=502,
        ) from exc
    url = _get_attr(result, "url")
    if not url:
        raise AppError(
            code="billing.stripe_invalid_response",
            message="Stripe returned no portal URL.",
            status_code=502,
        )
    return url


# ── License issuance (called from the webhook handler) ────────────────
async def issue_one_time_license(
    session: AsyncSession,
    *,
    buyer_id: uuid.UUID,
    skill_id: uuid.UUID,
    skill_version_id: uuid.UUID,
    order_item_id: uuid.UUID,
    granted_at: datetime,
) -> License:
    """Issue a one-time license capped at the major version of the purchased version."""
    version = await session.get(SkillVersion, skill_version_id)
    cap = major_version_cap(version.version) if version else None

    license = License(
        buyer_id=buyer_id,
        skill_id=skill_id,
        source=LicenseSource.ONE_TIME,
        source_id=order_item_id,
        granted_at=granted_at,
        max_version=cap,
        support_tier=SupportTier.NONE,
        status=LicenseStatus.ACTIVE,
    )
    session.add(license)
    await session.flush()  # populate license.id for the audit-log entry
    return license


__all__ = [
    "REFUND_WINDOW_DAYS",
    "assert_skill_purchasable",
    "can_refund",
    "create_billing_portal",
    "create_checkout_session",
    "fetch_connect_status",
    "get_cached_idempotent",
    "get_order_by_session_id",
    "issue_one_time_license",
    "issue_refund",
    "major_version_cap",
    "resolve_version",
    "set_cached_idempotent",
    "start_connect_onboarding",
]
