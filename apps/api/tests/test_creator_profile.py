"""Public creator profile tests.

Spec: ``prompts/marketplace/02-skill-detail.md`` § Creator profile.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.skills.models import PricingModel, Skill, SkillStatus, SkillVersion
from src.users.models import CreatorProfile, User, UserRole


async def _seed_creator(
    session: AsyncSession,
    *,
    email: str,
    handle: str,
    n_skills: int = 3,
) -> tuple[User, list[Skill]]:
    user = User(
        email=email,
        hashed_password="x" * 32,
        display_name=handle.title(),
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
        is_creator_verified=True,
    )
    session.add(user)
    await session.flush()
    profile = CreatorProfile(
        user_id=user.id,
        handle=handle,
        bio="# About me\n\nI build skills.",
        website_url="https://example.com",
        social={"twitter": "https://x.com/jane", "github": "https://github.com/jane"},
        industries=["finance", "data"],
        payout_country="US",
    )
    session.add(profile)
    await session.flush()

    skills: list[Skill] = []
    for i in range(n_skills):
        s = Skill(
            creator_id=user.id,
            slug=f"skill-{i}",
            name=f"Skill {i}",
            tagline=f"Tagline {i}",
            description_md=f"Body {i}",
            category="finance",
            tags=["a", "b"],
            status=SkillStatus.PUBLISHED,
            pricing_model=PricingModel.ONE_TIME,
            one_time_price_cents=1000 + i * 100,
            rating_avg=4.0 + i * 0.1,
            rating_count=5 + i,
            total_sales=100 + i * 50,
        )
        session.add(s)
        await session.flush()
        v = SkillVersion(
            skill_id=s.id,
            version=f"1.{i}.0",
            content_hash="a" * 64,
            storage_url="s3://test/x.md",
            released_at=datetime.now(timezone.utc),
            released_by=user.id,
            ai_requirements={"required_models": ["claude-opus-4-7"]},
            changelog_md="Initial.",
        )
        session.add(v)
        await session.flush()
        s.latest_version_id = v.id
        session.add(s)
        await session.flush()
        skills.append(s)

    await session.commit()
    return user, skills


@pytest.mark.asyncio
async def test_creator_profile_returns_public_shape(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    user, _skills = await _seed_creator(
        db_session, email="jane@example.com", handle="janedoe", n_skills=3,
    )
    r = await client.get("/v1/creators/janedoe")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["handle"] == "janedoe"
    assert body["display_name"] == "Janedoe"
    assert body["bio_md"] == "# About me\n\nI build skills."
    assert body["website_url"] == "https://example.com"
    assert body["is_verified"] is True
    assert "finance" in body["industries"]
    # Stats present + math is correct.
    assert body["stats"]["total_skills"] == 3
    assert body["stats"]["total_sales"] == 100 + 150 + 200
    assert body["stats"]["rating_avg"] is not None


@pytest.mark.asyncio
async def test_creator_profile_404_unknown(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    r = await client.get("/v1/creators/nosuchhandle")
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == "creator.not_found"


@pytest.mark.asyncio
async def test_creator_skills_returns_published(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_creator(
        db_session, email="alex@example.com", handle="alexk", n_skills=3,
    )
    r = await client.get("/v1/creators/alexk/skills")
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["items"]) == 3
    handles = {s["creator"]["handle"] for s in body["items"]}
    assert handles == {"alexk"}


@pytest.mark.asyncio
async def test_creator_skills_sort_most_sold_default(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_creator(
        db_session, email="sam@example.com", handle="sam", n_skills=3,
    )
    r = await client.get("/v1/creators/sam/skills")
    body = r.json()
    sales = [s["total_sales"] for s in body["items"]]
    assert sales == sorted(sales, reverse=True)
