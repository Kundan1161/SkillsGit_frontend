"""Catalog integration tests — list, filter, sort, search, detail.

Spec: ``prompts/marketplace/01-discovery.md`` and
``prompts/marketplace/02-skill-detail.md``.

Tests seed 3–5 skills inline so they don't depend on Agent C's seed script.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.skills.models import PricingModel, Skill, SkillStatus, SkillVersion
from src.storage.s3 import InMemoryStorage, set_storage
from src.users.models import CreatorProfile, User, UserRole


# ── Seed helpers ──────────────────────────────────────────────────────


async def _make_creator(
    session: AsyncSession,
    *,
    email: str,
    handle: str,
    display_name: str | None = None,
    is_verified: bool = False,
) -> User:
    user = User(
        email=email,
        hashed_password="x" * 32,
        display_name=display_name or handle,
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
        is_creator_verified=is_verified,
    )
    session.add(user)
    await session.flush()
    profile = CreatorProfile(user_id=user.id, handle=handle, payout_country="US")
    session.add(profile)
    await session.flush()
    return user


async def _make_skill(
    session: AsyncSession,
    *,
    creator: User,
    slug: str,
    name: str,
    tagline: str,
    category: str | None = "finance",
    tags: list[str] | None = None,
    pricing_model: PricingModel = PricingModel.ONE_TIME,
    one_time_price_cents: int | None = 1900,
    subscription_price_cents: int | None = None,
    status: SkillStatus = SkillStatus.PUBLISHED,
    rating_avg: float | None = 4.5,
    rating_count: int = 10,
    total_sales: int = 50,
    version: str = "1.0.0",
    released_at: datetime | None = None,
    description_md: str | None = None,
    ai_requirements: dict[str, Any] | None = None,
) -> tuple[Skill, SkillVersion]:
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=name,
        tagline=tagline,
        description_md=description_md or f"# {name}\n\n{tagline}",
        category=category,
        tags=tags or [],
        status=status,
        pricing_model=pricing_model,
        one_time_price_cents=one_time_price_cents,
        subscription_price_cents=subscription_price_cents,
        rating_avg=rating_avg,
        rating_count=rating_count,
        total_sales=total_sales,
    )
    session.add(skill)
    await session.flush()
    v = SkillVersion(
        skill_id=skill.id,
        version=version,
        content_hash="a" * 64,
        storage_url=f"s3://test/{slug}.md",
        ai_requirements=ai_requirements or {"required_models": ["claude-opus-4-7"]},
        changelog_md=f"## When to use\nFor {tagline}.\n\n## Examples\n### Example 1\nDemo.\n\n### Example 2\nMore.\n\n## How to apply\n1. Secret step.\n",
        released_at=released_at or datetime.now(timezone.utc),
        released_by=creator.id,
    )
    session.add(v)
    await session.flush()
    skill.latest_version_id = v.id
    session.add(skill)
    await session.flush()
    return skill, v


async def _seed_catalog(session: AsyncSession) -> dict[str, Any]:
    """Create three creators + five skills covering categories and pricing."""
    jane = await _make_creator(
        session, email="jane@example.com", handle="janedoe",
        display_name="Jane Doe", is_verified=True,
    )
    alex = await _make_creator(
        session, email="alex@example.com", handle="alexk", display_name="Alex K",
    )
    sam = await _make_creator(
        session, email="sam@example.com", handle="sam", display_name="Sam",
    )

    now = datetime.now(timezone.utc)
    dcf, _ = await _make_skill(
        session, creator=jane,
        slug="dcf-valuation", name="DCF Valuation Pro",
        tagline="Build a defensible discounted cash flow model.",
        category="finance", tags=["dcf", "valuation"],
        one_time_price_cents=1900, rating_avg=4.7, rating_count=23, total_sales=412,
        released_at=now - timedelta(days=2),
    )
    pm, _ = await _make_skill(
        session, creator=alex,
        slug="incident-postmortem", name="Incident Postmortem",
        tagline="Turn chaos into a calm blameless postmortem.",
        category="engineering", tags=["incident", "ops"],
        one_time_price_cents=1200, rating_avg=4.8, rating_count=18, total_sales=210,
        released_at=now - timedelta(days=5),
    )
    pricing, _ = await _make_skill(
        session, creator=sam,
        slug="saas-pricing-audit", name="SaaS Pricing Audit",
        tagline="Diagnose pricing leaks across plans.",
        category="operations", tags=["pricing", "saas"],
        pricing_model=PricingModel.SUBSCRIPTION,
        one_time_price_cents=None, subscription_price_cents=2900,
        rating_avg=5.0, rating_count=8, total_sales=98,
        released_at=now - timedelta(days=1),
    )
    free_skill, _ = await _make_skill(
        session, creator=jane,
        slug="design-critique", name="Design Critique",
        tagline="Get fast, actionable design feedback.",
        category="design", tags=["design", "ux"],
        pricing_model=PricingModel.FREE,
        one_time_price_cents=None, rating_avg=4.2, rating_count=4, total_sales=320,
        released_at=now - timedelta(days=10),
    )
    draft, _ = await _make_skill(
        session, creator=jane,
        slug="hidden-draft", name="Hidden Draft",
        tagline="This should not be visible.",
        status=SkillStatus.DRAFT,
        rating_avg=None, rating_count=0, total_sales=0,
    )
    await session.commit()
    return {
        "jane": jane, "alex": alex, "sam": sam,
        "dcf": dcf, "pm": pm, "pricing": pricing,
        "free": free_skill, "draft": draft,
    }


# ── Categories ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_categories_returns_seed(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Seed categories live in the migration; for in-memory sqlite, just
    # create a couple of rows.
    from src.skills.models import Category

    db_session.add_all(
        [
            Category(slug="finance", name="Finance", display_order=10),
            Category(slug="design", name="Design", display_order=20),
            Category(slug="engineering", name="Engineering", display_order=80),
            Category(slug="operations", name="Operations", display_order=70),
        ]
    )
    await db_session.commit()
    await _seed_catalog(db_session)

    r = await client.get("/v1/catalog/categories")
    assert r.status_code == 200, r.text
    body = r.json()
    assert "items" in body
    slugs = {c["slug"] for c in body["items"]}
    assert {"finance", "design", "engineering", "operations"} <= slugs
    # Counts populated.
    fin = next(c for c in body["items"] if c["slug"] == "finance")
    assert fin["skill_count"] >= 1


# ── List ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_skills_returns_only_published(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    seeded = await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills")
    assert r.status_code == 200, r.text
    body = r.json()
    ids = {s["id"] for s in body["items"]}
    assert str(seeded["draft"].id) not in ids
    # All seeded published skills present.
    assert str(seeded["dcf"].id) in ids
    assert str(seeded["pm"].id) in ids
    assert str(seeded["pricing"].id) in ids


@pytest.mark.asyncio
async def test_list_includes_creator_chip(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?limit=20")
    body = r.json()
    dcf = next(s for s in body["items"] if s["slug"] == "dcf-valuation")
    assert dcf["creator"]["handle"] == "janedoe"
    assert dcf["creator"]["is_verified"] is True
    assert dcf["one_time_price_cents"] == 1900
    assert dcf["latest_version"] == "1.0.0"


# ── Filters ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_filter_by_category(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?categories=finance")
    body = r.json()
    cats = {s["category"] for s in body["items"]}
    assert cats == {"finance"}


@pytest.mark.asyncio
async def test_filter_multi_category(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?categories=finance,engineering")
    body = r.json()
    cats = {s["category"] for s in body["items"]}
    assert cats == {"finance", "engineering"}


@pytest.mark.asyncio
async def test_filter_pricing_model(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?pricing_models=subscription")
    body = r.json()
    models = {s["pricing_model"] for s in body["items"]}
    assert models == {"subscription"}


@pytest.mark.asyncio
async def test_filter_min_rating(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?min_rating=4.8")
    body = r.json()
    for s in body["items"]:
        assert s["rating_avg"] is not None and s["rating_avg"] >= 4.8


@pytest.mark.asyncio
async def test_filter_creator_handle(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?creator_handle=janedoe")
    body = r.json()
    handles = {s["creator"]["handle"] for s in body["items"]}
    assert handles == {"janedoe"}


@pytest.mark.asyncio
async def test_filter_combination(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get(
        "/v1/catalog/skills?categories=finance,operations&pricing_models=one_time&min_rating=4&sort=top_rated"
    )
    body = r.json()
    for s in body["items"]:
        assert s["category"] in {"finance", "operations"}
        assert s["pricing_model"] == "one_time"


# ── Search ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_finds_design(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?q=design")
    body = r.json()
    slugs = {s["slug"] for s in body["items"]}
    assert "design-critique" in slugs


@pytest.mark.asyncio
async def test_search_finds_dcf(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?q=dcf")
    body = r.json()
    slugs = {s["slug"] for s in body["items"]}
    assert "dcf-valuation" in slugs


@pytest.mark.asyncio
async def test_search_no_results_empty(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?q=zzzzznopesuchskill")
    body = r.json()
    assert body["items"] == []
    assert body["page"]["has_more"] is False


# ── Sort ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_sort_most_sold(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?sort=most_sold&limit=10")
    body = r.json()
    sales = [s["total_sales"] for s in body["items"]]
    assert sales == sorted(sales, reverse=True)


@pytest.mark.asyncio
async def test_sort_price_asc(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?sort=price_asc&limit=10")
    body = r.json()
    # Free skill (price 0) should come first.
    assert body["items"][0]["slug"] == "design-critique"


@pytest.mark.asyncio
async def test_sort_newest(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?sort=newest&limit=10")
    body = r.json()
    # Pricing audit (1 day ago) should outrank dcf (2 days ago) outrank
    # postmortem (5 days ago) outrank free (10 days ago).
    slugs = [s["slug"] for s in body["items"]]
    assert slugs.index("saas-pricing-audit") < slugs.index("dcf-valuation")
    assert slugs.index("dcf-valuation") < slugs.index("incident-postmortem")


# ── Skill detail ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_skill_detail_by_uuid(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    seeded = await _seed_catalog(db_session)
    r = await client.get(f"/v1/skills/{seeded['dcf'].id}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["slug"] == "dcf-valuation"
    assert body["creator"]["handle"] == "janedoe"
    assert body["pricing"]["model"] == "one_time"
    assert body["pricing"]["one_time_price_cents"] == 1900
    assert body["latest_version"]["version"] == "1.0.0"
    assert body["stats"]["rating_avg"] == 4.7
    # "How to apply" stripped from preview.
    assert "How to apply" not in (body["preview_body_md"] or "")
    assert "Secret step" not in (body["preview_body_md"] or "")
    # Examples clipped to 1 sub-example.
    assert (body["preview_body_md"] or "").count("### Example") <= 1


@pytest.mark.asyncio
async def test_skill_detail_by_handle_slug(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    seeded = await _seed_catalog(db_session)
    r = await client.get("/v1/skills/by-handle/janedoe/dcf-valuation")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] == str(seeded["dcf"].id)


@pytest.mark.asyncio
async def test_skill_detail_exposes_inspired_by_urls_from_storage(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    storage = InMemoryStorage()
    set_storage(storage)
    try:
        seeded = await _seed_catalog(db_session)
        await storage.put_object(
            "s3://test/dcf-valuation.md",
            (
                "# DCF Valuation Pro\n\n"
                "## When to use\nFor discounted cash flow work.\n\n"
                "## Sources reviewed\n"
                "- https://github.com/acme/valuation-playbook\n"
                "- https://github.com/acme/modeling-toolkit/ (MIT)\n"
                "- https://example.com/not-a-git-source\n\n"
                "## How to apply\n"
                "1. Secret step.\n"
            ).encode("utf-8"),
            "text/markdown",
        )

        r = await client.get(f"/v1/skills/{seeded['dcf'].id}")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["inspired_by_urls"] == [
            "https://github.com/acme/valuation-playbook",
            "https://github.com/acme/modeling-toolkit",
        ]
        assert "Sources reviewed" not in (body["preview_body_md"] or "")
        assert "How to apply" not in (body["preview_body_md"] or "")
    finally:
        set_storage(InMemoryStorage())


@pytest.mark.asyncio
async def test_skill_detail_404_for_draft(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    seeded = await _seed_catalog(db_session)
    r = await client.get(f"/v1/skills/{seeded['draft'].id}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_versions_list(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    seeded = await _seed_catalog(db_session)
    r = await client.get(f"/v1/skills/{seeded['dcf'].id}/versions")
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_version_preview(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    seeded = await _seed_catalog(db_session)
    r = await client.get(
        f"/v1/skills/{seeded['dcf'].id}/versions/1.0.0/preview"
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "How to apply" not in body["preview_body_md"]


# ── Pagination ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_pagination_cursor(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/skills?limit=2")
    body = r.json()
    assert len(body["items"]) == 2
    assert body["page"]["has_more"] is True
    cur = body["page"]["next_cursor"]
    assert cur

    r2 = await client.get(f"/v1/catalog/skills?limit=2&cursor={cur}")
    body2 = r2.json()
    # No overlap.
    ids1 = {s["id"] for s in body["items"]}
    ids2 = {s["id"] for s in body2["items"]}
    assert not (ids1 & ids2)


# ── Featured ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_featured_empty_then_admin_pin(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    seeded = await _seed_catalog(db_session)
    r = await client.get("/v1/catalog/featured")
    assert r.status_code == 200
    assert r.json()["items"] == []

    # Inject a pin directly via the DB (admin endpoint requires auth — covered
    # separately in admin tests).
    from src.catalog.models import EditorialPick

    db_session.add(
        EditorialPick(skill_id=seeded["dcf"].id, slot="home", sort_order=1)
    )
    await db_session.commit()

    r2 = await client.get("/v1/catalog/featured")
    body2 = r2.json()
    assert len(body2["items"]) == 1
    assert body2["items"][0]["skill"]["slug"] == "dcf-valuation"
