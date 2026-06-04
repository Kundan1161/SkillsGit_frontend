"""Creator skill upload flow tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.skills.models import Skill, SkillStatus, SkillVersion
from src.storage.s3 import InMemoryStorage, set_storage
from src.users.models import CreatorProfile, User


VALID_BODY = """---
id: janedoe/dcf-valuation-pro
version: 1.0.0
name: DCF Valuation Pro
description: Build a defensible DCF.
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
1. Steps.
"""

INVALID_BODY = """---
id: janedoe/dcf
version: not-a-semver
name: Bad
description: Bad
category: finance
license_type: one_time
ai:
  required_models:
    - made-up-model
---

# Bad

Missing required sections.
"""


@pytest.fixture(autouse=True)
def _swap_storage() -> InMemoryStorage:
    storage = InMemoryStorage()
    set_storage(storage)
    return storage


async def _register_creator(
    client: AsyncClient, db_session: AsyncSession, handle: str = "janedoe"
) -> User:
    r = await client.post(
        "/v1/auth/register",
        json={
            "email": f"{handle}@example.com",
            "password": "Seed-password-1234",
            "display_name": handle.title(),
        },
    )
    assert r.status_code == 201
    user = (
        await db_session.execute(
            select(User).where(User.email == f"{handle}@example.com")
        )
    ).scalar_one()
    db_session.add(CreatorProfile(user_id=user.id, handle=handle))
    await db_session.commit()
    return user


@pytest.mark.asyncio
async def test_upload_creates_draft_skill(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _register_creator(client, db_session)

    files = {"skills_md": ("dcf.skills.md", VALID_BODY.encode("utf-8"), "text/markdown")}
    data = {
        "name": "DCF Valuation Pro",
        "tagline": "Build a defensible DCF",
        "category": "finance",
        "tags": "dcf,valuation",
        "pricing_model": "one_time",
        "one_time_price_cents": "1900",
    }
    r = await client.post("/v1/creator/skills/", data=data, files=files)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["slug"] == "dcf-valuation-pro"
    assert body["status"] == "draft"

    # SkillVersion row created.
    version_row = (
        await db_session.execute(
            select(SkillVersion).where(SkillVersion.version == "1.0.0")
        )
    ).scalar_one()
    assert version_row.released_at is None


@pytest.mark.asyncio
async def test_upload_rejects_invalid_skill_file(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _register_creator(client, db_session)

    files = {"skills_md": ("bad.skills.md", INVALID_BODY.encode("utf-8"), "text/markdown")}
    data = {"name": "Bad", "category": "finance", "pricing_model": "one_time"}
    r = await client.post("/v1/creator/skills/", data=data, files=files)
    assert r.status_code == 422, r.text
    body = r.json()
    assert body["error"]["code"] == "skill.publish_validation_failed"
    assert isinstance(body["error"]["details"], list)
    assert len(body["error"]["details"]) >= 1


@pytest.mark.asyncio
async def test_publish_transitions_to_pending_review(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _register_creator(client, db_session)

    files = {"skills_md": ("dcf.skills.md", VALID_BODY.encode("utf-8"), "text/markdown")}
    data = {"name": "DCF", "category": "finance", "pricing_model": "one_time"}
    r = await client.post("/v1/creator/skills/", data=data, files=files)
    assert r.status_code == 201, r.text
    skill_id = r.json()["id"]

    r = await client.post(f"/v1/creator/skills/{skill_id}/publish")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "pending_review"


@pytest.mark.asyncio
async def test_full_upload_review_publish_e2e(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    creator = await _register_creator(client, db_session)
    # Upload.
    files = {"skills_md": ("dcf.skills.md", VALID_BODY.encode("utf-8"), "text/markdown")}
    data = {"name": "DCF", "category": "finance", "pricing_model": "one_time"}
    r = await client.post("/v1/creator/skills/", data=data, files=files)
    assert r.status_code == 201
    skill_id = r.json()["id"]

    # Publish (-> pending_review).
    r = await client.post(f"/v1/creator/skills/{skill_id}/publish")
    assert r.status_code == 200
    assert r.json()["status"] == "pending_review"

    # Admin approves.
    admin_email = "admin@example.com"
    await client.post("/v1/auth/logout")
    r = await client.post(
        "/v1/auth/register",
        json={"email": admin_email, "password": "Seed-password-1234"},
    )
    assert r.status_code == 201
    admin = (
        await db_session.execute(select(User).where(User.email == admin_email))
    ).scalar_one()
    admin.is_admin = True
    await db_session.commit()

    r = await client.post(f"/v1/admin/skills/{skill_id}/approve")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "published"

    skill = (
        await db_session.execute(select(Skill).where(Skill.id == skill_id))
    ).scalar_one()
    await db_session.refresh(skill)
    assert skill.status == SkillStatus.PUBLISHED
    assert skill.latest_version_id is not None
    assert skill.creator_id == creator.id


@pytest.mark.asyncio
async def test_new_version_creates_unreleased_row(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _register_creator(client, db_session)
    # Upload v1.0.
    files = {"skills_md": ("dcf.skills.md", VALID_BODY.encode("utf-8"), "text/markdown")}
    data = {"name": "DCF", "category": "finance", "pricing_model": "one_time"}
    r = await client.post("/v1/creator/skills/", data=data, files=files)
    assert r.status_code == 201, r.text
    skill_id = r.json()["id"]

    v2 = VALID_BODY.replace("version: 1.0.0", "version: 1.1.0")
    files = {"skills_md": ("dcf.skills.md", v2.encode("utf-8"), "text/markdown")}
    r = await client.post(
        f"/v1/creator/skills/{skill_id}/versions",
        data={"changelog_md": "Small fix.", "target_version": "1.1.0"},
        files=files,
    )
    assert r.status_code == 201, r.text
    assert r.json()["version"] == "1.1.0"
    assert r.json()["released_at"] is None


# Quietly ensure fixtures path is reachable — sanity check seed data is valid too.
@pytest.mark.asyncio
async def test_seed_files_validate() -> None:
    from src.skills.validator import validate_file

    seed_dir = Path(__file__).parent.parent / "scripts" / "seed_data"
    files = list(seed_dir.glob("*.skills.md"))
    assert len(files) == 6, "expected 6 seed skill files"
    for f in files:
        result = validate_file(f.read_bytes())
        assert result.is_valid, (
            f"{f.name} failed validation: {[(e.field, e.code) for e in result.errors]}"
        )
