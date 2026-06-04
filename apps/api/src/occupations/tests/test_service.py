"""Service-level unit tests for the occupations module.

These talk to the ORM directly (via the ``db_session`` fixture) and
exercise every branch of :mod:`src.occupations.service` without going
through HTTP. Router-level coverage lives in ``test_router.py``.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import AuditLog
from src.occupations import service
from src.occupations.models import Occupation, OccupationMemberRole, OccupationSkill
from src.occupations.schemas import (
    OccupationCreate,
    OccupationSkillBulkItem,
    OccupationSkillUpsert,
    OccupationUpdate,
    PublishRequest,
)
from src.skills.models import (
    PricingModel,
    Skill,
    SkillKind,
    SkillStatus,
    SkillVersion,
)
from src.users.models import CreatorProfile, User, UserRole

# ── Seed helpers ──────────────────────────────────────────────────────


async def _make_creator(
    session: AsyncSession,
    *,
    email: str,
    handle: str,
    is_creator_verified: bool = True,
    is_admin: bool = False,
) -> User:
    user = User(
        email=email,
        hashed_password="x" * 32,
        display_name=handle.title(),
        role=UserRole.CREATOR if not is_admin else UserRole.ADMIN,
        is_active=True,
        is_verified=True,
        is_creator_verified=is_creator_verified,
        is_admin=is_admin,
    )
    session.add(user)
    await session.flush()
    session.add(CreatorProfile(user_id=user.id, handle=handle, payout_country="US"))
    await session.flush()
    return user


async def _make_skill(
    session: AsyncSession,
    *,
    creator: User,
    slug: str,
    name: str | None = None,
    kind: SkillKind = SkillKind.SKILL,
    status: SkillStatus = SkillStatus.PUBLISHED,
) -> Skill:
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=name or slug.replace("-", " ").title(),
        tagline=f"Tagline for {slug}",
        description_md=f"# {slug}\n",
        category="engineering",
        tags=[slug.split("-", maxsplit=1)[0]],
        status=status,
        kind=kind,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    return skill


async def _make_version(
    session: AsyncSession,
    *,
    skill: Skill,
    version: str = "1.0.0",
    released: bool = True,
    storage_url: str | None = None,
) -> SkillVersion:
    v = SkillVersion(
        skill_id=skill.id,
        version=version,
        content_hash="a" * 64,
        storage_url=storage_url or f"s3://test/{skill.slug}.md",
        ai_requirements={"required_models": ["claude-opus-4-7"]},
        changelog_md="## When to use\nNotes.\n\n## How to apply\n1. step",
        released_at=datetime.now(UTC) if released else None,
        released_by=skill.creator_id if released else None,
        is_yanked=False,
    )
    session.add(v)
    await session.flush()
    if released:
        skill.latest_version_id = v.id
        skill.status = SkillStatus.PUBLISHED
        await session.flush()
    return v


# ── Create / update ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_occupation_requires_verified_creator(
    db_session: AsyncSession,
) -> None:
    creator = await _make_creator(
        db_session, email="anon@example.com", handle="anon",
        is_creator_verified=False,
    )
    payload = OccupationCreate(
        name="AI DevOps Engineer",
        slug="ai-devops-engineer",
        domains=["ci-cd"],
        pricing_model=PricingModel.FREE,
    )
    with pytest.raises(service.OccupationError) as exc:
        await service.create_occupation(db_session, creator=creator, payload=payload)
    assert exc.value.code == "occupation.creator_not_verified"
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_create_occupation_happy_path(db_session: AsyncSession) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    payload = OccupationCreate(
        name="AI DevOps Engineer",
        slug="ai-devops-engineer",
        summary_md="On-call lead's playbook.",
        domains=["ci-cd", "observability", "incident-response"],
        tags=["devops", "sre"],
        pricing_model=PricingModel.ONE_TIME,
        one_time_price_cents=19900,
        recommended_persona_count=2,
    )
    out = await service.create_occupation(
        db_session, creator=creator, payload=payload
    )
    assert out.slug == "ai-devops-engineer"
    assert out.kind == SkillKind.OCCUPATION
    assert out.status == SkillStatus.DRAFT
    assert out.domains == ["ci-cd", "observability", "incident-response"]
    assert out.pricing_model == PricingModel.ONE_TIME

    # Audit row.
    audit = await db_session.execute(
        select(AuditLog).where(AuditLog.action == "occupation.created")
    )
    rows = list(audit.scalars().all())
    assert len(rows) == 1
    # sqlite stores UUID as string; coerce both sides for cross-dialect parity.
    assert str(rows[0].actor_id) == str(creator.id)

    # Side table + parent row are both in place.
    skill = await db_session.get(Skill, out.skill_id)
    assert skill is not None
    assert skill.kind == SkillKind.OCCUPATION
    occ = await db_session.get(Occupation, out.skill_id)
    assert occ is not None
    assert occ.recommended_persona_count == 2


@pytest.mark.asyncio
async def test_create_occupation_rejects_pricing_mismatch(
    db_session: AsyncSession,
) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    payload = OccupationCreate(
        name="X",
        slug="x",
        domains=["x"],
        pricing_model=PricingModel.ONE_TIME,
        one_time_price_cents=None,
    )
    with pytest.raises(service.OccupationError) as exc:
        await service.create_occupation(db_session, creator=creator, payload=payload)
    assert exc.value.code == "occupation.pricing_required"


@pytest.mark.asyncio
async def test_create_occupation_slug_conflict(db_session: AsyncSession) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    payload = OccupationCreate(
        name="One",
        slug="my-slug",
        domains=["x"],
        pricing_model=PricingModel.FREE,
    )
    await service.create_occupation(db_session, creator=creator, payload=payload)
    with pytest.raises(service.OccupationError) as exc:
        await service.create_occupation(db_session, creator=creator, payload=payload)
    assert exc.value.code == "occupation.slug_conflict"
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_update_occupation_patches_fields(db_session: AsyncSession) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    initial = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="AI DevOps Engineer",
            slug="ai-devops-engineer",
            domains=["ci-cd"],
            pricing_model=PricingModel.FREE,
        ),
    )
    out = await service.update_occupation(
        db_session,
        creator=creator,
        skill_id=initial.skill_id,
        patch=OccupationUpdate(
            name="AI DevOps Engineer (v2)",
            summary_md="Updated.",
            domains=["ci-cd", "observability"],
            recommended_persona_count=3,
        ),
    )
    assert out.name == "AI DevOps Engineer (v2)"
    assert out.summary_md == "Updated."
    assert out.domains == ["ci-cd", "observability"]
    assert out.recommended_persona_count == 3


@pytest.mark.asyncio
async def test_update_occupation_not_owner_404(db_session: AsyncSession) -> None:
    owner = await _make_creator(
        db_session, email="owner@example.com", handle="owner",
    )
    intruder = await _make_creator(
        db_session, email="intruder@example.com", handle="intruder",
    )
    initial = await service.create_occupation(
        db_session,
        creator=owner,
        payload=OccupationCreate(
            name="Owned",
            slug="owned",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )
    with pytest.raises(service.OccupationError) as exc:
        await service.update_occupation(
            db_session,
            creator=intruder,
            skill_id=initial.skill_id,
            patch=OccupationUpdate(name="HACKED"),
        )
    assert exc.value.code == "occupation.not_found"
    assert exc.value.status_code == 404


# ── Membership ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_add_member_rejects_non_skill_kind(db_session: AsyncSession) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )
    # Try to add an occupation row as a member of another occupation.
    another_occ = await _make_skill(
        db_session, creator=creator, slug="other-occ",
        kind=SkillKind.OCCUPATION,
    )
    with pytest.raises(service.OccupationError) as exc:
        await service.add_or_update_member(
            db_session,
            creator=creator,
            skill_id=occ.skill_id,
            member_skill_id=another_occ.id,
            payload=OccupationSkillUpsert(domain="x"),
        )
    assert exc.value.code == "occupation.invalid_member_kind"
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_add_member_rejects_unknown_domain(db_session: AsyncSession) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["ci-cd"],
            pricing_model=PricingModel.FREE,
        ),
    )
    member = await _make_skill(db_session, creator=creator, slug="member-1")
    with pytest.raises(service.OccupationError) as exc:
        await service.add_or_update_member(
            db_session,
            creator=creator,
            skill_id=occ.skill_id,
            member_skill_id=member.id,
            payload=OccupationSkillUpsert(domain="not-declared"),
        )
    assert exc.value.code == "occupation.domain_unknown"


@pytest.mark.asyncio
async def test_add_member_upsert_round_trip(db_session: AsyncSession) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["ci-cd"],
            pricing_model=PricingModel.FREE,
        ),
    )
    member = await _make_skill(db_session, creator=creator, slug="ci-pipeline")

    first = await service.add_or_update_member(
        db_session,
        creator=creator,
        skill_id=occ.skill_id,
        member_skill_id=member.id,
        payload=OccupationSkillUpsert(
            domain="ci-cd", role=OccupationMemberRole.CORE, sort_order=0,
            pinned=True, notes_md="The backbone.",
        ),
    )
    assert first.member_skill_id == member.id
    assert first.role == OccupationMemberRole.CORE
    assert first.pinned is True

    # Upsert: same key, change role + notes.
    second = await service.add_or_update_member(
        db_session,
        creator=creator,
        skill_id=occ.skill_id,
        member_skill_id=member.id,
        payload=OccupationSkillUpsert(
            domain="ci-cd", role=OccupationMemberRole.SUPPORTING,
            sort_order=2, pinned=False, notes_md="Demoted.",
        ),
    )
    assert second.id == first.id  # same row
    assert second.role == OccupationMemberRole.SUPPORTING
    assert second.sort_order == 2
    assert second.pinned is False


@pytest.mark.asyncio
async def test_bulk_set_members_replaces_set(db_session: AsyncSession) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["ci-cd", "obs"],
            pricing_model=PricingModel.FREE,
        ),
    )
    s1 = await _make_skill(db_session, creator=creator, slug="s1")
    s2 = await _make_skill(db_session, creator=creator, slug="s2")
    s3 = await _make_skill(db_session, creator=creator, slug="s3")

    first = await service.bulk_set_members(
        db_session,
        creator=creator,
        skill_id=occ.skill_id,
        items=[
            OccupationSkillBulkItem(member_skill_id=s1.id, domain="ci-cd"),
            OccupationSkillBulkItem(member_skill_id=s2.id, domain="obs", sort_order=1),
        ],
    )
    assert len(first.items) == 2
    assert {m.member_slug for m in first.items} == {"s1", "s2"}

    # Replace with a different set.
    second = await service.bulk_set_members(
        db_session,
        creator=creator,
        skill_id=occ.skill_id,
        items=[
            OccupationSkillBulkItem(member_skill_id=s3.id, domain="ci-cd"),
        ],
    )
    assert len(second.items) == 1
    assert second.items[0].member_slug == "s3"


@pytest.mark.asyncio
async def test_bulk_set_rejects_invalid_member_kind(
    db_session: AsyncSession,
) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )
    skill_member = await _make_skill(db_session, creator=creator, slug="ok")
    persona_member = await _make_skill(
        db_session, creator=creator, slug="not-ok",
        kind=SkillKind.PERSONA,
    )
    with pytest.raises(service.OccupationError) as exc:
        await service.bulk_set_members(
            db_session,
            creator=creator,
            skill_id=occ.skill_id,
            items=[
                OccupationSkillBulkItem(member_skill_id=skill_member.id, domain="x"),
                OccupationSkillBulkItem(member_skill_id=persona_member.id, domain="x"),
            ],
        )
    assert exc.value.code == "occupation.invalid_member_kind"


@pytest.mark.asyncio
async def test_bulk_set_rejects_duplicate_items(
    db_session: AsyncSession,
) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )
    s1 = await _make_skill(db_session, creator=creator, slug="s1")
    with pytest.raises(service.OccupationError) as exc:
        await service.bulk_set_members(
            db_session,
            creator=creator,
            skill_id=occ.skill_id,
            items=[
                OccupationSkillBulkItem(member_skill_id=s1.id, domain="x"),
                OccupationSkillBulkItem(member_skill_id=s1.id, domain="x", sort_order=1),
            ],
        )
    assert exc.value.code == "occupation.duplicate_member"


@pytest.mark.asyncio
async def test_remove_member_deletes_row(db_session: AsyncSession) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )
    s1 = await _make_skill(db_session, creator=creator, slug="s1")
    await service.add_or_update_member(
        db_session,
        creator=creator,
        skill_id=occ.skill_id,
        member_skill_id=s1.id,
        payload=OccupationSkillUpsert(domain="x"),
    )
    await service.remove_member(
        db_session, creator=creator, skill_id=occ.skill_id,
        member_skill_id=s1.id,
    )
    res = await db_session.execute(
        select(OccupationSkill).where(
            OccupationSkill.occupation_id == occ.skill_id
        )
    )
    assert res.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_remove_member_not_present_404(db_session: AsyncSession) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )
    bogus = await _make_skill(db_session, creator=creator, slug="bogus")
    with pytest.raises(service.OccupationError) as exc:
        await service.remove_member(
            db_session, creator=creator,
            skill_id=occ.skill_id, member_skill_id=bogus.id,
        )
    assert exc.value.code == "occupation.member_not_found"


@pytest.mark.asyncio
async def test_reorder_members_updates_sort_order(
    db_session: AsyncSession,
) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )
    s1 = await _make_skill(db_session, creator=creator, slug="s1")
    s2 = await _make_skill(db_session, creator=creator, slug="s2")
    s3 = await _make_skill(db_session, creator=creator, slug="s3")
    await service.bulk_set_members(
        db_session,
        creator=creator,
        skill_id=occ.skill_id,
        items=[
            OccupationSkillBulkItem(member_skill_id=s1.id, domain="x", sort_order=0),
            OccupationSkillBulkItem(member_skill_id=s2.id, domain="x", sort_order=1),
            OccupationSkillBulkItem(member_skill_id=s3.id, domain="x", sort_order=2),
        ],
    )
    out = await service.reorder_members(
        db_session,
        creator=creator,
        skill_id=occ.skill_id,
        order=[(s3.id, 0), (s1.id, 1), (s2.id, 2)],
    )
    by_slug = {m.member_slug: m for m in out.items}
    assert by_slug["s3"].sort_order == 0
    assert by_slug["s1"].sort_order == 1
    assert by_slug["s2"].sort_order == 2


# ── Listing + detail + grouping ───────────────────────────────────────


@pytest.mark.asyncio
async def test_list_occupations_filters_kind_and_status(
    db_session: AsyncSession,
) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    # 1 published occupation.
    published = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Published Occ",
            slug="pub",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )
    # Hand-promote it.
    skill = await db_session.get(Skill, published.skill_id)
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.flush()

    # 1 draft occupation — should NOT appear in public listing.
    await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Draft",
            slug="draft",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )

    # 1 plain skill — must not appear.
    await _make_skill(
        db_session, creator=creator, slug="plain-skill",
        kind=SkillKind.SKILL,
    )

    items, _ = await service.list_occupations(
        db_session, service.OccupationFilters()
    )
    slugs = [i.slug for i in items]
    assert slugs == ["pub"]


@pytest.mark.asyncio
async def test_get_detail_groups_members_by_domain(
    db_session: AsyncSession,
) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["ci-cd", "observability"],
            pricing_model=PricingModel.FREE,
        ),
    )
    parent = await db_session.get(Skill, occ.skill_id)
    assert parent is not None
    parent.status = SkillStatus.PUBLISHED
    s1 = await _make_skill(db_session, creator=creator, slug="ci-1")
    s2 = await _make_skill(db_session, creator=creator, slug="ci-2")
    s3 = await _make_skill(db_session, creator=creator, slug="obs-1")
    await service.bulk_set_members(
        db_session,
        creator=creator,
        skill_id=occ.skill_id,
        items=[
            OccupationSkillBulkItem(member_skill_id=s1.id, domain="ci-cd", sort_order=0),
            OccupationSkillBulkItem(member_skill_id=s2.id, domain="ci-cd", sort_order=1),
            OccupationSkillBulkItem(member_skill_id=s3.id, domain="observability"),
        ],
    )

    detail = await service.get_occupation_detail(db_session, skill_id=occ.skill_id)
    assert detail is not None
    assert [g.domain for g in detail.groups] == ["ci-cd", "observability"]
    ci_group = detail.groups[0]
    assert [m.member_slug for m in ci_group.members] == ["ci-1", "ci-2"]


# ── Build / publish stubs ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_trigger_build_rejects_empty_membership(
    db_session: AsyncSession,
) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Empty",
            slug="empty",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )
    parent = await db_session.get(Skill, occ.skill_id)
    assert parent is not None
    await _make_version(db_session, skill=parent, version="1.0.0", released=False)
    with pytest.raises(service.OccupationError) as exc:
        await service.trigger_build(
            db_session, creator=creator,
            skill_id=occ.skill_id, version="1.0.0",
        )
    assert exc.value.code == "occupation.empty_membership"


@pytest.mark.asyncio
async def test_trigger_build_emits_audit_row(db_session: AsyncSession) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )
    parent = await db_session.get(Skill, occ.skill_id)
    assert parent is not None
    member = await _make_skill(db_session, creator=creator, slug="member")
    await service.add_or_update_member(
        db_session,
        creator=creator,
        skill_id=occ.skill_id,
        member_skill_id=member.id,
        payload=OccupationSkillUpsert(domain="x"),
    )
    await _make_version(db_session, skill=parent, version="1.0.0", released=False)

    job = await service.trigger_build(
        db_session, creator=creator,
        skill_id=occ.skill_id, version="1.0.0",
    )
    assert job.status == "queued"
    assert job.job_id.startswith("occupations:build:")

    audit = await db_session.execute(
        select(AuditLog).where(AuditLog.action == "occupation.build_queued")
    )
    assert audit.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_publish_marks_version_released(db_session: AsyncSession) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    occ = await service.create_occupation(
        db_session,
        creator=creator,
        payload=OccupationCreate(
            name="Occ",
            slug="occ",
            domains=["x"],
            pricing_model=PricingModel.FREE,
        ),
    )
    parent = await db_session.get(Skill, occ.skill_id)
    assert parent is not None
    member = await _make_skill(db_session, creator=creator, slug="m")
    await service.add_or_update_member(
        db_session,
        creator=creator,
        skill_id=occ.skill_id,
        member_skill_id=member.id,
        payload=OccupationSkillUpsert(domain="x"),
    )
    version = await _make_version(
        db_session, skill=parent, version="1.0.0", released=False
    )
    job = await service.publish_occupation(
        db_session,
        creator=creator,
        skill_id=occ.skill_id,
        payload=PublishRequest(version="1.0.0", changelog_md="First."),
    )
    assert job.status == "queued"
    await db_session.refresh(version)
    await db_session.refresh(parent)
    assert version.released_at is not None
    assert parent.status == SkillStatus.PUBLISHED
    assert parent.latest_version_id == version.id
