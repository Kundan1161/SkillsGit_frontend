"""End-to-end checkout flow tests.

Stripe is mocked at the SDK-wrapper level (:mod:`src.billing.stripe_client`)
so these tests never make a real network call. The fixtures here
demonstrate the contract the wrapper must satisfy.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing import service as billing_service
from src.billing import stripe_client as stripe_module
from src.billing.fees import breakdown, compute_fee
from src.billing.models import License, LicenseStatus, Order, OrderStatus
from src.skills.models import PricingModel, Skill, SkillStatus, SkillVersion
from src.users.models import CreatorProfile, User, UserRole


# ── Fakes ─────────────────────────────────────────────────────────────
class _FakeObj(dict):
    """Stripe SDK returns objects that support both ``obj.id`` and ``obj['id']``."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class FakeStripe:
    """In-memory stand-in for the Stripe API surface we use."""

    def __init__(self) -> None:
        self.checkout_sessions: list[dict[str, Any]] = []
        self.refunds: list[dict[str, Any]] = []
        self.accounts: dict[str, dict[str, Any]] = {}
        self.account_links_created = 0
        self.next_payouts_enabled = True
        self.next_charges_enabled = True
        self.next_details_submitted = True

    # ── Checkout ────────────────────────────────────────────────────
    def create_checkout_session(self, **params: Any) -> _FakeObj:
        sid = f"cs_test_{len(self.checkout_sessions) + 1:04d}"
        self.checkout_sessions.append(params)
        return _FakeObj(
            id=sid,
            url=f"https://checkout.stripe.test/{sid}",
            payment_intent=f"pi_{sid}",
            metadata=params.get("metadata", {}),
        )

    def retrieve_checkout_session(self, session_id: str) -> _FakeObj:
        return _FakeObj(id=session_id, payment_intent=f"pi_{session_id}")

    # ── Refunds ─────────────────────────────────────────────────────
    def create_refund(self, **params: Any) -> _FakeObj:
        self.refunds.append(params)
        return _FakeObj(id=f"re_{len(self.refunds):04d}", status="pending")

    # ── Connect ─────────────────────────────────────────────────────
    def create_account(self, **params: Any) -> _FakeObj:
        aid = f"acct_test_{len(self.accounts) + 1:04d}"
        self.accounts[aid] = {
            **params,
            "id": aid,
            "details_submitted": False,
            "payouts_enabled": False,
            "charges_enabled": False,
        }
        return _FakeObj(**self.accounts[aid])

    def create_account_link(self, **params: Any) -> _FakeObj:
        self.account_links_created += 1
        return _FakeObj(
            url=f"https://connect.stripe.test/onboard/{params.get('account')}"
        )

    def retrieve_account(self, account_id: str) -> _FakeObj:
        acct = self.accounts.setdefault(
            account_id, {"id": account_id}
        )
        acct["details_submitted"] = self.next_details_submitted
        acct["payouts_enabled"] = self.next_payouts_enabled
        acct["charges_enabled"] = self.next_charges_enabled
        return _FakeObj(**acct)

    # ── Customer portal (not exercised here) ────────────────────────
    def create_billing_portal_session(self, **params: Any) -> _FakeObj:
        return _FakeObj(url="https://portal.stripe.test/abc")

    def construct_webhook_event(
        self, payload: bytes, sig_header: str, secret: str
    ) -> _FakeObj:
        import json

        return _FakeObj(**json.loads(payload.decode()))


@pytest_asyncio.fixture
async def fake_stripe() -> Any:
    f = FakeStripe()
    stripe_module.set_stripe_client(f)  # type: ignore[arg-type]
    yield f
    stripe_module.set_stripe_client(None)


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> None:
    """Clear the in-memory slowapi limiter between tests.

    The default storage is process-global, so consecutive ``/v1/auth/register``
    calls across tests can trip the ``5/hour`` cap. We reset before each
    test to keep tests independent.
    """
    try:
        from src.core.rate_limits import limiter

        if hasattr(limiter, "_storage"):
            try:
                limiter._storage.reset()  # type: ignore[attr-defined]
            except Exception:
                pass
        # slowapi >=0.1.9 keeps a per-key store; ``.reset()`` clears it.
        if hasattr(limiter, "reset"):
            try:
                limiter.reset()
            except Exception:
                pass
    except Exception:
        pass


# ── DB helpers ────────────────────────────────────────────────────────
async def _make_user(
    session: AsyncSession,
    *,
    email: str,
    role: UserRole = UserRole.BUYER,
    stripe_connect_account_id: str | None = None,
    payouts_enabled: bool = False,
) -> User:
    u = User(
        email=email,
        hashed_password="x" * 32,
        display_name=email.split("@")[0],
        role=role,
        is_active=True,
        is_verified=True,
        stripe_connect_account_id=stripe_connect_account_id,
        payouts_enabled=payouts_enabled,
    )
    session.add(u)
    await session.flush()
    return u


async def _make_creator_with_skill(
    session: AsyncSession,
    *,
    email: str,
    price_cents: int = 1900,
    status: SkillStatus = SkillStatus.PUBLISHED,
) -> tuple[User, Skill, SkillVersion]:
    user = await _make_user(
        session,
        email=email,
        role=UserRole.CREATOR,
        stripe_connect_account_id=f"acct_for_{email.split('@')[0]}",
        payouts_enabled=True,
    )
    profile = CreatorProfile(
        user_id=user.id,
        handle=email.split("@")[0],
        payout_country="US",
    )
    session.add(profile)
    await session.flush()

    skill = Skill(
        creator_id=user.id,
        slug="test-skill",
        name="Test Skill",
        tagline="A skill for testing",
        status=status,
        pricing_model=PricingModel.ONE_TIME,
        one_time_price_cents=price_cents,
    )
    session.add(skill)
    await session.flush()

    version = SkillVersion(
        skill_id=skill.id,
        version="1.2.0",
        content_hash="a" * 64,
        storage_url="s3://test/skill.md",
        released_at=datetime.now(timezone.utc),
        released_by=user.id,
    )
    session.add(version)
    await session.flush()
    skill.latest_version_id = version.id
    session.add(skill)
    await session.flush()
    return user, skill, version


async def _register_and_login(client: AsyncClient, email: str) -> dict[str, Any]:
    r = await client.post(
        "/v1/auth/register",
        json={
            "email": email,
            "password": "correct horse battery staple",
            "display_name": email.split("@")[0],
        },
    )
    assert r.status_code == 201, r.text
    return r.json()


# ── Fee math ──────────────────────────────────────────────────────────
class TestFees:
    def test_compute_fee_zero(self) -> None:
        assert compute_fee(0) == 0

    def test_compute_fee_one_dollar(self) -> None:
        # $1.00 → 20% → 20 cents.
        assert compute_fee(100, percent=20.0) == 20

    def test_compute_fee_buck_99(self) -> None:
        # $1.99 → 20% = 39.8c → bankers-round to 40c.
        assert compute_fee(199, percent=20.0) == 40

    def test_compute_fee_19(self) -> None:
        # $19.00 → 20% = 380c.
        assert compute_fee(1900, percent=20.0) == 380

    def test_compute_fee_999(self) -> None:
        # $9.99 → 20% = 199.8c → 200c.
        assert compute_fee(999, percent=20.0) == 200

    def test_compute_fee_banker_rounding(self) -> None:
        # Half-to-even cases:
        # 10c × 5% = 0.5 → 0 (round to even).
        # 30c × 5% = 1.5 → 2 (round to even).
        # 50c × 5% = 2.5 → 2 (round to even).
        # 70c × 5% = 3.5 → 4 (round to even).
        assert compute_fee(10, percent=5.0) == 0
        assert compute_fee(30, percent=5.0) == 2
        assert compute_fee(50, percent=5.0) == 2
        assert compute_fee(70, percent=5.0) == 4

    def test_compute_fee_zero_percent(self) -> None:
        assert compute_fee(1234, percent=0.0) == 0

    def test_compute_fee_hundred_percent(self) -> None:
        assert compute_fee(1234, percent=100.0) == 1234

    def test_compute_fee_negative_rejected(self) -> None:
        with pytest.raises(ValueError):
            compute_fee(-1)

    def test_compute_fee_bad_percent_rejected(self) -> None:
        with pytest.raises(ValueError):
            compute_fee(100, percent=150.0)

    def test_breakdown_sums_to_amount(self) -> None:
        for amount in (100, 199, 1234, 99999):
            b = breakdown(amount, percent=20.0)
            assert b["platform_fee_cents"] + b["creator_payout_cents"] == amount


# ── End-to-end checkout flow ──────────────────────────────────────────
@pytest.mark.asyncio
async def test_checkout_creates_stripe_session_and_returns_url(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_stripe: FakeStripe,
) -> None:
    # Set up: creator + skill, separate buyer.
    creator, skill, _version = await _make_creator_with_skill(
        db_session, email="creator@example.com"
    )
    await db_session.commit()

    # Buyer registers via the API (sets the cookie).
    await _register_and_login(client, "buyer@example.com")

    r = await client.post(
        "/v1/checkout/sessions",
        json={"skill_id": str(skill.id)},
        headers={"Idempotency-Key": "test-key-001"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["checkout_url"].startswith("https://checkout.stripe.test/")
    assert body["session_id"].startswith("cs_test_")

    # Inspect the Stripe call: must include application_fee_amount and
    # transfer_data.destination.
    assert len(fake_stripe.checkout_sessions) == 1
    params = fake_stripe.checkout_sessions[0]
    pid = params["payment_intent_data"]
    assert pid["application_fee_amount"] == compute_fee(1900)
    assert pid["transfer_data"]["destination"] == creator.stripe_connect_account_id
    # Metadata propagates ids.
    md = pid["metadata"]
    assert md["skill_id"] == str(skill.id)
    assert md["buyer_id"]


@pytest.mark.asyncio
async def test_checkout_idempotent_with_same_key(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_stripe: FakeStripe,
) -> None:
    _creator, skill, _version = await _make_creator_with_skill(
        db_session, email="creator2@example.com"
    )
    await db_session.commit()
    await _register_and_login(client, "buyer2@example.com")

    headers = {"Idempotency-Key": "same-key-please"}
    r1 = await client.post(
        "/v1/checkout/sessions", json={"skill_id": str(skill.id)}, headers=headers
    )
    r2 = await client.post(
        "/v1/checkout/sessions", json={"skill_id": str(skill.id)}, headers=headers
    )
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json() == r2.json()
    # Only one Stripe session created.
    assert len(fake_stripe.checkout_sessions) == 1


@pytest.mark.asyncio
async def test_checkout_blocks_draft_skill(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_stripe: FakeStripe,
) -> None:
    _creator, skill, _version = await _make_creator_with_skill(
        db_session, email="creator3@example.com", status=SkillStatus.DRAFT
    )
    await db_session.commit()
    await _register_and_login(client, "buyer3@example.com")

    r = await client.post(
        "/v1/checkout/sessions", json={"skill_id": str(skill.id)}
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "checkout.skill_not_purchasable"


@pytest.mark.asyncio
async def test_checkout_blocks_creator_without_payouts(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_stripe: FakeStripe,
) -> None:
    creator, skill, _version = await _make_creator_with_skill(
        db_session, email="creator4@example.com"
    )
    # Yank payouts.
    creator.payouts_enabled = False
    db_session.add(creator)
    await db_session.commit()
    await _register_and_login(client, "buyer4@example.com")

    r = await client.post(
        "/v1/checkout/sessions", json={"skill_id": str(skill.id)}
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "checkout.creator_payouts_disabled"


@pytest.mark.asyncio
async def test_checkout_blocks_already_owned(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_stripe: FakeStripe,
) -> None:
    creator, skill, version = await _make_creator_with_skill(
        db_session, email="creator5@example.com"
    )
    await db_session.commit()
    me = await _register_and_login(client, "buyer5@example.com")

    # Hand-craft a license so the buyer "already owns" it.
    lic = License(
        buyer_id=uuid.UUID(me["id"]),
        skill_id=skill.id,
        source="one_time",
        source_id=uuid.uuid4(),
        granted_at=datetime.now(timezone.utc),
        max_version="1.x",
        support_tier="none",
        status=LicenseStatus.ACTIVE,
    )
    db_session.add(lic)
    await db_session.commit()

    r = await client.post(
        "/v1/checkout/sessions", json={"skill_id": str(skill.id)}
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "checkout.already_owned"


# ── Refund flow ───────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_refund_within_window_calls_stripe(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_stripe: FakeStripe,
) -> None:
    creator, skill, version = await _make_creator_with_skill(
        db_session, email="creator6@example.com"
    )
    await db_session.commit()
    me = await _register_and_login(client, "buyer6@example.com")

    # Simulate a completed order by inserting Order + OrderItem.
    from src.billing.models import OrderItem

    order = Order(
        buyer_id=uuid.UUID(me["id"]),
        stripe_payment_intent_id="pi_test_001",
        subtotal_cents=1900,
        platform_fee_cents=380,
        creator_payout_cents=1520,
        currency="USD",
        status=OrderStatus.PAID,
        placed_at=datetime.now(timezone.utc),
    )
    db_session.add(order)
    await db_session.flush()
    item = OrderItem(
        order_id=order.id,
        skill_id=skill.id,
        skill_version_id=version.id,
        price_cents=1900,
        platform_fee_cents=380,
        creator_id=creator.id,
    )
    db_session.add(item)
    await db_session.commit()

    r = await client.post(
        f"/v1/orders/{order.id}/refund",
        json={"reason": "buyer's remorse"},
    )
    assert r.status_code == 202, r.text
    # Stripe was called with reverse_transfer.
    assert len(fake_stripe.refunds) == 1
    assert fake_stripe.refunds[0]["reverse_transfer"] is True
    assert fake_stripe.refunds[0]["payment_intent"] == "pi_test_001"


# ── Connect onboarding ────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_connect_onboarding_start_creates_account_and_link(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_stripe: FakeStripe,
) -> None:
    # Register a user and promote them to creator with a profile.
    await _register_and_login(client, "newcreator@example.com")
    r = await client.post(
        "/v1/auth/become-creator",
        json={"handle": "newcreator", "payout_country": "US"},
    )
    assert r.status_code == 201

    r = await client.post(
        "/v1/creator/onboarding/start", json={"payout_country": "US"}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["account_id"].startswith("acct_test_")
    assert body["url"].startswith("https://connect.stripe.test/onboard/")
    # Stripe SDK was invoked.
    assert len(fake_stripe.accounts) == 1
    assert fake_stripe.account_links_created == 1


@pytest.mark.asyncio
async def test_connect_status_persists_payouts_enabled(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_stripe: FakeStripe,
) -> None:
    await _register_and_login(client, "creator7@example.com")
    r = await client.post(
        "/v1/auth/become-creator",
        json={"handle": "creator7", "payout_country": "US"},
    )
    assert r.status_code == 201
    await client.post(
        "/v1/creator/onboarding/start", json={"payout_country": "US"}
    )

    fake_stripe.next_payouts_enabled = True
    r = await client.get("/v1/creator/onboarding/status")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["payouts_enabled"] is True
    assert body["details_submitted"] is True


# ── resolve_version helper ────────────────────────────────────────────
@pytest.mark.asyncio
async def test_resolve_version_caps_by_major(
    db_session: AsyncSession,
) -> None:
    creator, skill, v1_2 = await _make_creator_with_skill(
        db_session, email="creator8@example.com"
    )
    # Add a 2.0.0 version too; cap should restrict to 1.x.
    v2_0 = SkillVersion(
        skill_id=skill.id,
        version="2.0.0",
        content_hash="b" * 64,
        storage_url="s3://test/v2.md",
        released_at=datetime.now(timezone.utc),
        released_by=creator.id,
    )
    db_session.add(v2_0)
    await db_session.flush()

    license = License(
        buyer_id=creator.id,
        skill_id=skill.id,
        source="one_time",
        source_id=uuid.uuid4(),
        granted_at=datetime.now(timezone.utc),
        max_version="1.x",
        support_tier="none",
        status=LicenseStatus.ACTIVE,
    )
    db_session.add(license)
    await db_session.commit()

    resolved = await billing_service.resolve_version(license, db_session)
    assert resolved is not None
    assert resolved.version == "1.2.0"


@pytest.mark.asyncio
async def test_resolve_version_skips_yanked(
    db_session: AsyncSession,
) -> None:
    creator, skill, v1_2 = await _make_creator_with_skill(
        db_session, email="creator9@example.com"
    )
    v1_2.is_yanked = True
    db_session.add(v1_2)
    await db_session.flush()

    license = License(
        buyer_id=creator.id,
        skill_id=skill.id,
        source="one_time",
        source_id=uuid.uuid4(),
        granted_at=datetime.now(timezone.utc),
        max_version="1.x",
        support_tier="none",
        status=LicenseStatus.ACTIVE,
    )
    db_session.add(license)
    await db_session.commit()

    resolved = await billing_service.resolve_version(license, db_session)
    assert resolved is None
