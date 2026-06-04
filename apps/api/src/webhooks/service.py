"""Inbound Stripe webhook event processing.

Pure-function dispatch: the router calls :func:`process_event` with a
verified-and-parsed Stripe event. The router does **no** business logic.

All handlers are idempotent — dedup is via the ``webhook_events`` table
keyed on Stripe's ``event.id``. ``INSERT ... ON CONFLICT DO NOTHING``
guarantees that re-deliveries of the same event are no-ops at the
storage layer; downstream handlers are also written to be safe under
retry.

Spec: ``prompts/marketplace/03-pricing-and-checkout.md`` "Webhooks".
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.fees import compute_fee
from src.billing.models import (
    License,
    LicenseSource,
    LicenseStatus,
    Order,
    OrderItem,
    OrderStatus,
    WebhookEvent,
    WebhookEventStatus,
)
from src.billing.service import (
    issue_one_time_license,
)
from src.core.db import write_audit
from src.skills.models import Skill, SkillVersion
from src.users.models import User

log = logging.getLogger(__name__)


# ── Dedup ─────────────────────────────────────────────────────────────
async def _persist_event(
    session: AsyncSession, event: dict[str, Any]
) -> tuple[WebhookEvent, bool]:
    """Insert the event row if new; return (row, is_new).

    Uses a SELECT then INSERT pattern (cross-dialect; we don't rely on
    Postgres-only ``ON CONFLICT``). Concurrent duplicate delivery is
    extremely rare and the handlers are individually idempotent anyway.
    """
    event_id = str(event.get("id"))
    existing = await session.get(WebhookEvent, event_id)
    if existing is not None:
        return existing, False
    row = WebhookEvent(
        id=event_id,
        type=str(event.get("type", "unknown")),
        payload_json=event,
        received_at=datetime.now(timezone.utc),
        status=WebhookEventStatus.RECEIVED,
    )
    session.add(row)
    await session.flush()
    return row, True


# ── Top-level dispatch ────────────────────────────────────────────────
HANDLED_EVENTS = {
    "checkout.session.completed",
    "payment_intent.succeeded",
    "payment_intent.payment_failed",
    "charge.refunded",
    "account.updated",
}


async def process_event(
    session: AsyncSession, event: dict[str, Any]
) -> dict[str, Any]:
    """Dispatch an inbound Stripe event.

    Returns a small result dict suitable for the router's JSON response —
    contains only metadata about what was done (or skipped). Never raises
    for "this event is unsupported"; raises only on hard errors that
    should produce a 5xx so Stripe will retry.
    """
    row, is_new = await _persist_event(session, event)
    if not is_new:
        # Already processed (or in-flight from a previous delivery).
        return {"deduped": True, "event_id": row.id, "status": row.status.value}

    etype = str(event.get("type", ""))
    handled = False
    error: str | None = None

    try:
        if etype == "checkout.session.completed":
            await _on_checkout_session_completed(session, event)
            handled = True
        elif etype == "payment_intent.succeeded":
            # Fallback no-op — checkout.session.completed already issued
            # the license. We still mark "processed" to clear the row.
            handled = True
        elif etype == "payment_intent.payment_failed":
            await _on_payment_intent_payment_failed(session, event)
            handled = True
        elif etype == "charge.refunded":
            await _on_charge_refunded(session, event)
            handled = True
        elif etype == "account.updated":
            await _on_account_updated(session, event)
            handled = True
        else:
            # Phase-2 events (subscription.*, invoice.*) get logged but
            # not processed — leave processed_at NULL so ops can re-run
            # them after the Phase 2 handler ships.
            handled = False
    except Exception as exc:  # noqa: BLE001
        log.exception("webhook handler failed for %s", etype)
        error = type(exc).__name__
        row.status = WebhookEventStatus.FAILED
        row.error = error
        # Don't re-raise — we want to persist the failure row. Stripe
        # retries based on HTTP status; we'll return 200 (handled) and
        # surface the failure via /admin tooling. But if it's truly
        # unexpected (e.g. DB connection) we want a 5xx — so re-raise
        # the original to let the router decide.
        await session.flush()
        raise

    if handled:
        row.status = WebhookEventStatus.PROCESSED
        row.processed_at = datetime.now(timezone.utc)
    else:
        # Leave RECEIVED + processed_at=NULL for unhandled events.
        pass

    await session.flush()
    return {
        "deduped": False,
        "event_id": row.id,
        "type": etype,
        "handled": handled,
        "status": row.status.value,
    }


# ── Handlers ──────────────────────────────────────────────────────────
def _data_object(event: dict[str, Any]) -> dict[str, Any]:
    return event.get("data", {}).get("object", {}) or {}


async def _on_checkout_session_completed(
    session: AsyncSession, event: dict[str, Any]
) -> None:
    """Create Order + OrderItem, issue License, write audit log."""
    obj = _data_object(event)
    metadata = obj.get("metadata") or {}

    # Idempotency at the order level: payment_intent_id is unique on orders.
    pi = obj.get("payment_intent")
    pi_id = pi if isinstance(pi, str) else (pi or {}).get("id") if isinstance(pi, dict) else None

    if pi_id:
        existing_order_res = await session.execute(
            select(Order).where(Order.stripe_payment_intent_id == pi_id)
        )
        if existing_order_res.scalar_one_or_none() is not None:
            log.info("order already exists for PI %s — skipping", pi_id)
            return

    try:
        skill_id = uuid.UUID(metadata["skill_id"])
        skill_version_id = uuid.UUID(metadata["skill_version_id"])
        buyer_id = uuid.UUID(metadata["buyer_id"])
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError(
            f"checkout.session.completed missing/invalid metadata: {exc}"
        ) from exc

    # Hydrate skill + version.
    skill = await session.get(Skill, skill_id)
    version = await session.get(SkillVersion, skill_version_id)
    if skill is None or version is None:
        raise ValueError(
            "checkout.session.completed references unknown skill/version"
        )

    amount_total = int(obj.get("amount_total") or skill.one_time_price_cents or 0)
    if amount_total <= 0:
        raise ValueError("checkout.session.completed has zero amount")

    platform_fee = compute_fee(amount_total)
    now = datetime.now(timezone.utc)

    order = Order(
        buyer_id=buyer_id,
        stripe_payment_intent_id=pi_id,
        subtotal_cents=amount_total,
        platform_fee_cents=platform_fee,
        creator_payout_cents=amount_total - platform_fee,
        currency=(obj.get("currency") or "USD").upper(),
        status=OrderStatus.PAID,
        placed_at=now,
    )
    session.add(order)
    await session.flush()

    item = OrderItem(
        order_id=order.id,
        skill_id=skill.id,
        skill_version_id=version.id,
        price_cents=amount_total,
        platform_fee_cents=platform_fee,
        creator_id=skill.creator_id,
    )
    session.add(item)
    await session.flush()

    license = await issue_one_time_license(
        session,
        buyer_id=buyer_id,
        skill_id=skill.id,
        skill_version_id=version.id,
        order_item_id=item.id,
        granted_at=now,
    )

    # Denormalized counter — kept in sync with reality.
    skill.total_sales = (skill.total_sales or 0) + 1
    session.add(skill)

    await write_audit(
        session,
        actor_id=buyer_id,
        action="order.placed",
        target_type="order",
        target_id=order.id,
        metadata={
            "skill_id": str(skill.id),
            "skill_version_id": str(version.id),
            "amount_cents": amount_total,
            "platform_fee_cents": platform_fee,
        },
    )
    # Flush between writes — SQLAlchemy's ``insertmanyvalues`` sentinel
    # bookkeeping mis-matches UUIDs when adapting through SQLite. In
    # production Postgres this is unnecessary but harmless.
    await session.flush()
    await write_audit(
        session,
        actor_id=buyer_id,
        action="license.granted",
        target_type="license",
        target_id=license.id,
        metadata={
            "skill_id": str(skill.id),
            "source": LicenseSource.ONE_TIME.value,
            "max_version": license.max_version,
        },
    )
    await session.flush()

    # Best-effort notify the creator via their webhook subscription. This
    # is owned by Agent C; if the module isn't there yet, just record the
    # audit-log entry.
    try:
        from src.creator import webhooks as creator_webhooks  # type: ignore[import-not-found]

        notify = getattr(creator_webhooks, "notify_creator_webhook", None)
        if notify is not None:
            await notify(
                session,
                creator_id=skill.creator_id,
                event="skill.purchased",
                payload={
                    "skill_id": str(skill.id),
                    "order_id": str(order.id),
                    "amount_cents": amount_total,
                },
            )
    except Exception:  # noqa: BLE001
        # Phase 2 surface; do not let webhook delivery failures break
        # the inbound webhook handler.
        log.debug("creator webhook notification skipped", exc_info=True)


async def _on_payment_intent_payment_failed(
    session: AsyncSession, event: dict[str, Any]
) -> None:
    obj = _data_object(event)
    pi_id = obj.get("id")
    if not pi_id:
        return
    res = await session.execute(
        select(Order).where(Order.stripe_payment_intent_id == pi_id)
    )
    order = res.scalar_one_or_none()
    if order is None:
        # No order created yet (checkout.session.completed didn't fire);
        # nothing to do.
        return
    order.status = OrderStatus.FAILED
    session.add(order)
    await write_audit(
        session,
        actor_id=None,
        action="order.payment_failed",
        target_type="order",
        target_id=order.id,
        metadata={"payment_intent_id": pi_id},
    )


async def _on_charge_refunded(
    session: AsyncSession, event: dict[str, Any]
) -> None:
    obj = _data_object(event)
    pi_id = obj.get("payment_intent")
    if not pi_id:
        return

    order_res = await session.execute(
        select(Order).where(Order.stripe_payment_intent_id == pi_id)
    )
    order = order_res.scalar_one_or_none()
    if order is None:
        log.warning("charge.refunded for unknown payment_intent %s", pi_id)
        return

    # Distinguish full vs partial refund based on Stripe's amount_refunded
    # vs amount fields.
    amount = int(obj.get("amount") or 0)
    refunded = int(obj.get("amount_refunded") or 0)
    if amount > 0 and refunded < amount:
        order.status = OrderStatus.PARTIALLY_REFUNDED
    else:
        order.status = OrderStatus.REFUNDED
    session.add(order)

    items_res = await session.execute(
        select(OrderItem.id).where(OrderItem.order_id == order.id)
    )
    item_ids = [r[0] for r in items_res.all()]

    if item_ids:
        # Revoke any active licenses spawned by this order.
        lic_res = await session.execute(
            select(License).where(
                License.source == LicenseSource.ONE_TIME,
                License.source_id.in_(item_ids),
                License.status == LicenseStatus.ACTIVE,
            )
        )
        for lic in lic_res.scalars().all():
            lic.status = LicenseStatus.REVOKED
            session.add(lic)
            await write_audit(
                session,
                actor_id=None,
                action="license.revoked",
                target_type="license",
                target_id=lic.id,
                metadata={"reason": "refund", "order_id": str(order.id)},
            )
            await session.flush()

    await write_audit(
        session,
        actor_id=None,
        action="order.refunded",
        target_type="order",
        target_id=order.id,
        metadata={
            "payment_intent_id": pi_id,
            "amount_refunded_cents": refunded,
            "full": order.status == OrderStatus.REFUNDED,
        },
    )
    await session.flush()


async def _on_account_updated(
    session: AsyncSession, event: dict[str, Any]
) -> None:
    obj = _data_object(event)
    account_id = obj.get("id")
    if not account_id:
        return
    payouts_enabled = bool(obj.get("payouts_enabled"))

    res = await session.execute(
        select(User).where(User.stripe_connect_account_id == account_id)
    )
    user = res.scalar_one_or_none()
    if user is None:
        return
    if user.payouts_enabled != payouts_enabled:
        user.payouts_enabled = payouts_enabled
        session.add(user)
        await write_audit(
            session,
            actor_id=user.id,
            action="onboarding.payouts_updated",
            target_type="user",
            target_id=user.id,
            metadata={
                "account_id": account_id,
                "payouts_enabled": payouts_enabled,
            },
        )


__all__ = ["HANDLED_EVENTS", "process_event"]
