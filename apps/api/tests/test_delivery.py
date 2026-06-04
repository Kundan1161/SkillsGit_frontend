"""Delivery / license-download path tests.

Exercises:

- ``GET /v1/me/licenses`` returns the buyer's licenses.
- ``GET /v1/licenses/{id}/download`` produces a presigned URL backed by
  a watermarked file on the in-memory storage.
- The watermark comment is present, distinct per request, and contains
  HMAC'd license/buyer ids.
- Audit-log row is written for each download.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.models import (
    License,
    LicenseSource,
    LicenseStatus,
    SupportTier,
)
from src.core.db import AuditLog
from src.delivery.watermark import inject_distribution_block
from src.skills.models import PricingModel, Skill, SkillStatus, SkillVersion
from src.storage.s3 import InMemoryStorage, get_storage, set_storage
from src.users.models import CreatorProfile, User, UserRole


SAMPLE_BODY = """---
id: janedoe/dcf-valuation-pro
version: 1.2.0
name: DCF Valuation Pro
description: Tiny test body.
category: finance
license_type: one_time
pricing:
  one_time_cents: 1900
  currency: USD
ai:
  required_models:
    - claude-opus-4-7
---

# DCF Valuation Pro

## When to use
Use when valuing.

## How to apply
1. Step.
"""


@pytest.fixture(autouse=True)
def _swap_storage() -> InMemoryStorage:
    storage = InMemoryStorage()
    set_storage(storage)
    return storage


async def _register(client: AsyncClient, email: str, password: str = "Seed-password-1234") -> dict:
    r = await client.post(
        "/v1/auth/register",
        json={"email": email, "password": password, "display_name": email.split("@")[0]},
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _make_skill_with_version(
    session: AsyncSession, creator: User, body: bytes = SAMPLE_BODY.encode("utf-8")
) -> tuple[Skill, SkillVersion]:
    storage = get_storage()
    skill = Skill(
        creator_id=creator.id,
        slug="dcf-valuation-pro",
        name="DCF Valuation Pro",
        tagline="Test",
        category="finance",
        status=SkillStatus.PUBLISHED,
        pricing_model=PricingModel.ONE_TIME,
        one_time_price_cents=1900,
    )
    session.add(skill)
    await session.flush()

    key = f"skills/{skill.id}/1.2.0.md"
    await storage.put_object(
        key, inject_distribution_block(body.decode("utf-8")).encode("utf-8"), "text/markdown"
    )
    version = SkillVersion(
        skill_id=skill.id,
        version="1.2.0",
        content_hash="0" * 64,
        storage_url=key,
        ai_requirements={"required_models": ["claude-opus-4-7"]},
        released_at=datetime.now(timezone.utc),
        released_by=creator.id,
        is_yanked=False,
        target_version="1.2.0",
    )
    session.add(version)
    await session.flush()
    skill.latest_version_id = version.id
    await session.flush()
    return skill, version


async def _grant_license(
    session: AsyncSession, *, buyer: User, skill: Skill
) -> License:
    lic = License(
        buyer_id=buyer.id,
        skill_id=skill.id,
        source=LicenseSource.ONE_TIME,
        source_id=uuid.uuid4(),
        granted_at=datetime.now(timezone.utc),
        max_version="1.x",
        support_tier=SupportTier.NONE,
        status=LicenseStatus.ACTIVE,
    )
    session.add(lic)
    await session.flush()
    return lic


@pytest.mark.asyncio
async def test_list_my_licenses_empty(client: AsyncClient) -> None:
    await _register(client, "empty@example.com")
    r = await client.get("/v1/me/licenses")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["items"] == []
    assert body["page"]["has_more"] is False


@pytest.mark.asyncio
async def test_download_returns_presigned_url_with_watermark(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    buyer = await _register(client, "buyer@example.com")
    # Create a creator + a published skill directly in the DB.
    creator = User(
        email="creator@example.com",
        hashed_password="x",
        display_name="C",
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
    )
    db_session.add(creator)
    await db_session.flush()
    db_session.add(CreatorProfile(user_id=creator.id, handle="janedoe"))
    await db_session.flush()

    skill, _version = await _make_skill_with_version(db_session, creator)
    lic = await _grant_license(
        db_session,
        buyer=(await db_session.execute(select(User).where(User.email == "buyer@example.com"))).scalar_one(),
        skill=skill,
    )
    await db_session.commit()

    # Library lists it.
    r = await client.get("/v1/me/licenses")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["skill"]["name"] == "DCF Valuation Pro"
    assert items[0]["current_version"]["version"] == "1.2.0"

    # Download returns presigned URL.
    r = await client.get(f"/v1/licenses/{lic.id}/download")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["version"] == "1.2.0"
    assert body["download_url"].startswith("memory://")

    # The in-memory storage holds the watermarked copy.
    storage = get_storage()
    assert isinstance(storage, InMemoryStorage)
    delivery_keys = [k for k in storage.objects if k.startswith(f"delivery/{lic.id}/")]
    assert delivery_keys, "expected a watermarked delivery file"
    payload = storage.objects[delivery_keys[0]][0].decode("utf-8")
    assert "<!-- license:" in payload
    assert "buyer:" in payload
    assert "ts:" in payload

    # Audit log written.
    res = await db_session.execute(
        select(AuditLog).where(
            AuditLog.action == "license.downloaded", AuditLog.target_id == lic.id
        )
    )
    rows = list(res.scalars().all())
    assert len(rows) >= 1


@pytest.mark.asyncio
async def test_two_downloads_have_distinct_watermarks(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _register(client, "buyer2@example.com")
    creator = User(
        email="creator2@example.com",
        hashed_password="x",
        display_name="C",
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
    )
    db_session.add(creator)
    await db_session.flush()
    db_session.add(CreatorProfile(user_id=creator.id, handle="janedoe"))
    await db_session.flush()
    skill, _v = await _make_skill_with_version(db_session, creator)
    buyer = (
        await db_session.execute(select(User).where(User.email == "buyer2@example.com"))
    ).scalar_one()
    lic = await _grant_license(db_session, buyer=buyer, skill=skill)
    await db_session.commit()

    r1 = await client.get(f"/v1/licenses/{lic.id}/download")
    r2 = await client.get(f"/v1/licenses/{lic.id}/download")
    assert r1.status_code == 200
    assert r2.status_code == 200
    # The URLs point at different objects (different nonces).
    assert r1.json()["download_url"] != r2.json()["download_url"]


@pytest.mark.asyncio
async def test_download_raw_format(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _register(client, "buyer3@example.com")
    creator = User(
        email="creator3@example.com",
        hashed_password="x",
        display_name="C",
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
    )
    db_session.add(creator)
    await db_session.flush()
    db_session.add(CreatorProfile(user_id=creator.id, handle="janedoe"))
    await db_session.flush()
    skill, _v = await _make_skill_with_version(db_session, creator)
    buyer = (
        await db_session.execute(select(User).where(User.email == "buyer3@example.com"))
    ).scalar_one()
    lic = await _grant_license(db_session, buyer=buyer, skill=skill)
    await db_session.commit()

    r = await client.get(f"/v1/licenses/{lic.id}/download?format=raw")
    assert r.status_code == 200
    assert "text/markdown" in r.headers["content-type"]
    body = r.text
    assert "<!-- license:" in body
    assert "## When to use" in body


@pytest.mark.asyncio
async def test_download_404_for_non_owner(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _register(client, "attacker@example.com")
    # Create a license owned by someone else.
    other = User(
        email="other@example.com",
        hashed_password="x",
        role=UserRole.BUYER,
        display_name="Other",
        is_active=True,
        is_verified=True,
    )
    db_session.add(other)
    await db_session.flush()
    creator = User(
        email="c4@example.com",
        hashed_password="x",
        display_name="C",
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
    )
    db_session.add(creator)
    await db_session.flush()
    db_session.add(CreatorProfile(user_id=creator.id, handle="janedoe"))
    await db_session.flush()
    skill, _v = await _make_skill_with_version(db_session, creator)
    lic = await _grant_license(db_session, buyer=other, skill=skill)
    await db_session.commit()

    r = await client.get(f"/v1/licenses/{lic.id}/download")
    assert r.status_code == 404
