"""Admin moderation queue + approve/reject."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin.models import ModerationAction
from src.skills.models import Skill, SkillStatus, SkillVersion
from src.users.models import CreatorProfile, User, UserRole


SAMPLE_BODY = """---
id: marcoart/design-critique-rubric
version: 1.0.0
name: Design Critique Rubric
description: Tiny test body.
category: design
license_type: free
ai:
  required_models:
    - claude-sonnet-4-6
---

# Design Critique Rubric

## When to use
Use when reviewing UI.

## How to apply
1. Step.
"""


async def _make_admin_session(client: AsyncClient, db_session: AsyncSession) -> User:
    r = await client.post(
        "/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "Seed-password-1234",
            "display_name": "Admin",
        },
    )
    assert r.status_code == 201
    # Promote to admin in DB.
    u = (
        await db_session.execute(select(User).where(User.email == "admin@example.com"))
    ).scalar_one()
    u.is_admin = True
    await db_session.commit()
    return u


async def _seed_pending_skill(db_session: AsyncSession) -> Skill:
    creator = User(
        email="creator@example.com",
        hashed_password="x",
        display_name="Marco",
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
    )
    db_session.add(creator)
    await db_session.flush()
    db_session.add(CreatorProfile(user_id=creator.id, handle="marcoart"))
    await db_session.flush()

    skill = Skill(
        creator_id=creator.id,
        slug="design-critique-rubric",
        name="Design Critique Rubric",
        category="design",
        status=SkillStatus.PENDING_REVIEW,
    )
    db_session.add(skill)
    await db_session.flush()
    version = SkillVersion(
        skill_id=skill.id,
        version="1.0.0",
        content_hash="a" * 64,
        storage_url=f"skills/{skill.id}/1.0.0.md",
        ai_requirements={"required_models": ["claude-sonnet-4-6"]},
        released_at=None,
        is_yanked=False,
        target_version="1.0.0",
    )
    db_session.add(version)
    await db_session.commit()
    return skill


@pytest.mark.asyncio
async def test_non_admin_rejected(client: AsyncClient) -> None:
    r = await client.post(
        "/v1/auth/register",
        json={"email": "buyer@example.com", "password": "Seed-password-1234"},
    )
    assert r.status_code == 201

    r = await client.get("/v1/admin/moderation")
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_admin_moderation_queue_and_approve(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _make_admin_session(client, db_session)
    skill = await _seed_pending_skill(db_session)

    r = await client.get("/v1/admin/moderation")
    assert r.status_code == 200, r.text
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["skill_id"] == str(skill.id)
    assert items[0]["status"] == "pending_review"
    assert items[0]["submitted_version"] == "1.0.0"

    r = await client.post(f"/v1/admin/skills/{skill.id}/approve")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "published"
    assert body["version"] == "1.0.0"

    # Skill is now published.
    refreshed = (
        await db_session.execute(select(Skill).where(Skill.id == skill.id))
    ).scalar_one()
    await db_session.refresh(refreshed)
    assert refreshed.status == SkillStatus.PUBLISHED
    # Moderation_actions row exists.
    ma = (
        await db_session.execute(
            select(ModerationAction).where(
                ModerationAction.target_id == skill.id,
                ModerationAction.action == "approved",
            )
        )
    ).scalar_one_or_none()
    assert ma is not None


@pytest.mark.asyncio
async def test_admin_reject_keeps_pending_with_reason(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _make_admin_session(client, db_session)
    skill = await _seed_pending_skill(db_session)

    r = await client.post(
        f"/v1/admin/skills/{skill.id}/reject",
        json={"reason": "Body contains stale screenshots; refresh and resubmit."},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "pending_review"

    version = (
        await db_session.execute(
            select(SkillVersion).where(SkillVersion.skill_id == skill.id)
        )
    ).scalar_one()
    await db_session.refresh(version)
    assert version.rejection_reason is not None


@pytest.mark.asyncio
async def test_admin_verify_creator(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _make_admin_session(client, db_session)
    target = User(
        email="target@example.com",
        hashed_password="x",
        display_name="Target",
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
        is_creator_verified=False,
    )
    db_session.add(target)
    await db_session.commit()

    r = await client.post(f"/v1/admin/users/{target.id}/verify-creator")
    assert r.status_code == 200, r.text
    assert r.json()["is_creator_verified"] is True
