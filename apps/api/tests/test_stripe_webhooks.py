"""Stripe webhook handler tests.

The router skips signature verification under ``ENV=test`` (set in
``conftest.py``), so we can POST raw JSON. Each test verifies one
event type — plus a dedup test that re-fires the same event id.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing import stripe_client as stripe_module
from src.billing.models import (
    License,
    LicenseStatus,
    Order,
    OrderItem,
    OrderStatus,
    WebhookEvent,
    WebhookEventStatus,
)
from src.skills.models import PricingModel, Skill, SkillStatus, SkillVersion
from src.users.models import CreatorProfile, User, UserRole


# Re-use the FakeStripe from test_checkout_flow for retrieval helpers.
from tests.test_checkout_flow import FakeStripe  # noqa: E402


@pytest_asyncio.fixture
async def fake_stripe() -> Any:
    f = FakeStripe()
    stripe_module.set_stripe_client(f)  # type: ignore[arg-type]
    yield f
    stripe_module.set_stripe_client(None)


async def _setup_creator_and_skill(
    session: AsyncSession,
) -> tuple[User, Skill, SkillVersion]:
    creator = User(
        email="creator@webhook.test",
        hashed_password="x" * 32,
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
        stripe_connect_account_id="acct_webhook_creator",
        payouts_enabled=True,
    )
    session.add(creator)
    await session.flush()
    profile = CreatorProfile(user_id=creator.id, handle="webhook-creator", payout_country="US")
    session.add(profile)

    skill = Skill(
        creator_id=creator.id,
        slug="wh-skill",
        name="Webhook Skill",
        status=SkillStatus.PUBLISHED,
        pricing_model=PricingModel.ONE_TIME,
        one_time_price_cents=1900,
    )
    session.add(skill)
    await session.flush()

    version = SkillVersion(
        skill_id=skill.id,
        version="1.0.0",
        content_hash="c" * 64,
        storage_url="s3://test/v1.md",
        released_at=datetime.now(timezone.utc),
        released_by=creator.id,
    )
    session.add(version)
    await session.flush()
    skill.latest_version_id = version.id
    session.add(skill)
    await session.flush()
    return creator, skill, version


async def _make_buyer(session: AsyncSession, email: str = "buyer@webhook.test") -> User:
    buyer = User(
        email=email,
        hashed_password="x" * 32,
        role=UserRole.BUYER,
        is_active=True,
        is_verified=True,
    )
    session.add(buyer)
    await session.flush()
    return buyer


def _checkout_completed_event(
    *,
    event_id: str,
    skill_id: uuid.UUID,
    skill_version_id: uuid.UUID,
    buyer_id: uuid.UUID,
    amount_total: int = 1900,
    payment_intent_id: str = "pi_wh_001",
) -> dict[str, Any]:
    return {
        "id": event_id,
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_wh_001",
                "payment_intent": payment_intent_id,
                "amount_total": amount_total,
                "currency": "usd",
                "metadata": {
                    "skill_id": str(skill_id),
                    "skill_version_id": str(skill_version_id),
                    "buyer_id": str(buyer_id),
                },
            }
        },
    }


@pytest.mark.asyncio
async def test_webhook_checkout_session_completed_issues_license(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    creator, skill, version = await _setup_creator_and_skill(db_session)
    buyer = await _make_buyer(db_session)
    await db_session.commit()

    event = _checkout_completed_event(
        event_id="evt_001",
        skill_id=skill.id,
        skill_version_id=version.id,
        buyer_id=buyer.id,
    )

    r = await client.post("/v1/webhooks/stripe", json=event)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["handled"] is True
    assert body["status"] == "processed"

    # Order + OrderItem + License created.
    orders = (
        await db_session.execute(select(Order).where(Order.buyer_id == buyer.id))
    ).scalars().all()
    assert len(orders) == 1
    assert orders[0].status == OrderStatus.PAID
    assert orders[0].subtotal_cents == 1900
    assert orders[0].platform_fee_cents + orders[0].creator_payout_cents == 1900
    assert orders[0].stripe_payment_intent_id == "pi_wh_001"

    items = (
        await db_session.execute(
            select(OrderItem).where(OrderItem.order_id == orders[0].id)
        )
    ).scalars().all()
    assert len(items) == 1
    # SQLite returns UUID columns as strings; coerce both sides for comparison.
    assert str(items[0].skill_id) == str(skill.id)
    assert str(items[0].skill_version_id) == str(version.id)
    assert str(items[0].creator_id) == str(creator.id)
    assert items[0].price_cents == 1900

    # License with max_version capped at major of 1.0.0 → "1.x".
    licenses = (
        await db_session.execute(select(License).where(License.buyer_id == buyer.id))
    ).scalars().all()
    assert len(licenses) == 1
    assert licenses[0].max_version == "1.x"
    assert licenses[0].source.value == "one_time"
    assert licenses[0].status == LicenseStatus.ACTIVE
    assert str(licenses[0].source_id) == str(items[0].id)


@pytest.mark.asyncio
async def test_webhook_is_idempotent_on_event_id(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    creator, skill, version = await _setup_creator_and_skill(db_session)
    buyer = await _make_buyer(db_session)
    await db_session.commit()

    event = _checkout_completed_event(
        event_id="evt_idem_001",
        skill_id=skill.id,
        skill_version_id=version.id,
        buyer_id=buyer.id,
    )

    r1 = await client.post("/v1/webhooks/stripe", json=event)
    assert r1.status_code == 200
    assert r1.json()["deduped"] is False

    r2 = await client.post("/v1/webhooks/stripe", json=event)
    assert r2.status_code == 200
    assert r2.json()["deduped"] is True

    # Only one order, one license.
    orders = (
        await db_session.execute(select(Order).where(Order.buyer_id == buyer.id))
    ).scalars().all()
    assert len(orders) == 1
    licenses = (
        await db_session.execute(select(License).where(License.buyer_id == buyer.id))
    ).scalars().all()
    assert len(licenses) == 1


@pytest.mark.asyncio
async def test_webhook_payment_intent_failed_marks_order_failed(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    creator, skill, version = await _setup_creator_and_skill(db_session)
    buyer = await _make_buyer(db_session)
    # Pre-create an order in pending state.
    order = Order(
        buyer_id=buyer.id,
        stripe_payment_intent_id="pi_failing",
        subtotal_cents=1900,
        platform_fee_cents=380,
        creator_payout_cents=1520,
        currency="USD",
        status=OrderStatus.PENDING,
        placed_at=datetime.now(timezone.utc),
    )
    db_session.add(order)
    await db_session.commit()

    event = {
        "id": "evt_fail_001",
        "type": "payment_intent.payment_failed",
        "data": {"object": {"id": "pi_failing"}},
    }
    r = await client.post("/v1/webhooks/stripe", json=event)
    assert r.status_code == 200

    await db_session.refresh(order)
    assert order.status == OrderStatus.FAILED


@pytest.mark.asyncio
async def test_webhook_charge_refunded_revokes_license(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    creator, skill, version = await _setup_creator_and_skill(db_session)
    buyer = await _make_buyer(db_session)
    await db_session.commit()

    # Run checkout.session.completed to create everything.
    completed = _checkout_completed_event(
        event_id="evt_pre_refund",
        skill_id=skill.id,
        skill_version_id=version.id,
        buyer_id=buyer.id,
        payment_intent_id="pi_refund_target",
    )
    r = await client.post("/v1/webhooks/stripe", json=completed)
    assert r.status_code == 200

    # Now fire charge.refunded.
    refund_event = {
        "id": "evt_refund_001",
        "type": "charge.refunded",
        "data": {
            "object": {
                "payment_intent": "pi_refund_target",
                "amount": 1900,
                "amount_refunded": 1900,
            }
        },
    }
    r = await client.post("/v1/webhooks/stripe", json=refund_event)
    assert r.status_code == 200

    # Order is refunded; license is revoked.
    order_res = await db_session.execute(
        select(Order).where(Order.stripe_payment_intent_id == "pi_refund_target")
    )
    order = order_res.scalar_one()
    await db_session.refresh(order)
    assert order.status == OrderStatus.REFUNDED

    lic_res = await db_session.execute(
        select(License).where(License.buyer_id == buyer.id)
    )
    lic = lic_res.scalar_one()
    await db_session.refresh(lic)
    assert lic.status == LicenseStatus.REVOKED


@pytest.mark.asyncio
async def test_webhook_account_updated_persists_payouts_enabled(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user = User(
        email="onboard@webhook.test",
        hashed_password="x" * 32,
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
        stripe_connect_account_id="acct_onboard_001",
        payouts_enabled=False,
    )
    db_session.add(user)
    await db_session.commit()

    event = {
        "id": "evt_acct_001",
        "type": "account.updated",
        "data": {
            "object": {
                "id": "acct_onboard_001",
                "payouts_enabled": True,
                "details_submitted": True,
            }
        },
    }
    r = await client.post("/v1/webhooks/stripe", json=event)
    assert r.status_code == 200

    await db_session.refresh(user)
    assert user.payouts_enabled is True


@pytest.mark.asyncio
async def test_webhook_unhandled_event_logged_not_processed(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Phase-2 events get persisted with status=received, processed_at=None."""
    event = {
        "id": "evt_sub_001",
        "type": "customer.subscription.created",
        "data": {"object": {"id": "sub_xyz"}},
    }
    r = await client.post("/v1/webhooks/stripe", json=event)
    assert r.status_code == 200
    body = r.json()
    assert body["handled"] is False

    row = await db_session.get(WebhookEvent, "evt_sub_001")
    assert row is not None
    assert row.status == WebhookEventStatus.RECEIVED
    assert row.processed_at is None


@pytest.mark.asyncio
async def test_webhook_malformed_metadata_returns_500_for_retry(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    # Missing metadata → handler raises → row marked failed → 500 so Stripe retries.
    event = {
        "id": "evt_bad_001",
        "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_bad", "payment_intent": "pi_bad"}},
    }
    r = await client.post("/v1/webhooks/stripe", json=event)
    assert r.status_code == 500

    row = await db_session.get(WebhookEvent, "evt_bad_001")
    assert row is not None
    assert row.status == WebhookEventStatus.FAILED
    assert row.error is not None
