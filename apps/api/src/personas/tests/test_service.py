"""Service-level unit tests for the personas module.

These talk to the ORM directly (via the ``db_session`` fixture) and
exercise every branch of :mod:`src.personas.service` without going
through HTTP. Router-level coverage lives in ``test_router.py``.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.models import (
    License,
    LicenseCompositionRole,
    LicenseSource,
    LicenseStatus,
    SupportTier,
)
from src.core.db import AuditLog
from src.occupations.models import Occupation
from src.personas import service
from src.personas.models import Persona, PersonaNeuron
from src.personas.schemas import (
    NeuronOrderItem,
    PersonaCreate,
    PersonaUpdate,
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


async def _make_occupation(
    session: AsyncSession,
    *,
    creator: User,
    slug: str = "ai-devops-engineer",
    status: SkillStatus = SkillStatus.PUBLISHED,
) -> Skill:
    skill = await _make_skill(
        session, creator=creator, slug=slug,
        kind=SkillKind.OCCUPATION, status=status,
    )
    occ = Occupation(
        skill_id=skill.id,
        summary_md=f"Summary for {slug}",
        domains=["ci-cd", "observability"],
        persona_count=0,
        recommended_persona_count=2,
    )
    session.add(occ)
    await session.flush()
    return skill


async def _make_neuron(
    session: AsyncSession,
    *,
    creator: User,
    slug: str,
) -> Skill:
    return await _make_skill(
        session, creator=creator, slug=slug,
        kind=SkillKind.MEMORY_NEURON,
        status=SkillStatus.PUBLISHED,
    )


async def _attach_neuron(
    session: AsyncSession,
    *,
    persona_skill_id: uuid.UUID,
    neuron_skill_id: uuid.UUID,
    sort_order: int = 0,
    section: str | None = None,
) -> PersonaNeuron:
    row = PersonaNeuron(
        persona_id=persona_skill_id,
        neuron_skill_id=neuron_skill_id,
        sort_order=sort_order,
        section=section,
    )
    session.add(row)
    await session.flush()
    # Keep the persona's denormalized count in sync.
    persona = await session.get(Persona, persona_skill_id)
    if persona is not None:
        persona.neuron_count += 1
        await session.flush()
    return row


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
async def test_create_persona_requires_verified_creator(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    unverified = await _make_creator(
        db_session, email="anon@example.com", handle="anon",
        is_creator_verified=False,
    )
    payload = PersonaCreate(
        name="Jane",
        slug="jane",
        parent_occupation_id=parent.id,
        pricing_model=PricingModel.FREE,
    )
    with pytest.raises(service.PersonaError) as exc:
        await service.create_persona(
            db_session, creator=unverified, payload=payload
        )
    assert exc.value.code == "persona.creator_not_verified"
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_create_persona_happy_path(db_session: AsyncSession) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    payload = PersonaCreate(
        name="Jane the DevOps Lead",
        slug="jane-devops",
        parent_occupation_id=parent.id,
        creator_intro_md="12 years on-call.",
        specialization="Fintech on-call lead",
        years_of_experience=12,
        tags=["devops", "fintech"],
        pricing_model=PricingModel.FREE,
    )
    out = await service.create_persona(
        db_session, creator=creator, payload=payload
    )
    assert out.slug == "jane-devops"
    assert out.kind == SkillKind.PERSONA
    assert out.status == SkillStatus.DRAFT
    assert out.specialization == "Fintech on-call lead"
    assert out.years_of_experience == 12
    assert out.parent_occupation.skill_id == parent.id
    assert out.parent_occupation.slug == "ai-devops-engineer"

    # Audit row.
    audit = await db_session.execute(
        select(AuditLog).where(AuditLog.action == "persona.created")
    )
    rows = list(audit.scalars().all())
    assert len(rows) == 1
    assert str(rows[0].actor_id) == str(creator.id)

    # Side table + parent row are both in place.
    skill = await db_session.get(Skill, out.skill_id)
    assert skill is not None
    assert skill.kind == SkillKind.PERSONA
    persona = await db_session.get(Persona, out.skill_id)
    assert persona is not None
    assert persona.specialization == "Fintech on-call lead"
    assert str(persona.parent_occupation_id) == str(parent.id)


@pytest.mark.asyncio
async def test_create_persona_rejects_non_occupation_parent(
    db_session: AsyncSession,
) -> None:
    """T-04 acceptance bullet 1 — parent must be a kind=occupation row."""
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    # A plain skill (NOT an occupation) — should be rejected as parent.
    not_an_occupation = await _make_skill(
        db_session, creator=occ_creator, slug="just-a-skill",
        kind=SkillKind.SKILL,
    )

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    payload = PersonaCreate(
        name="Jane",
        slug="jane",
        parent_occupation_id=not_an_occupation.id,
        pricing_model=PricingModel.FREE,
    )
    with pytest.raises(service.PersonaError) as exc:
        await service.create_persona(
            db_session, creator=creator, payload=payload
        )
    assert exc.value.code == "persona.parent_occupation_invalid"
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_create_persona_rejects_unknown_parent(
    db_session: AsyncSession,
) -> None:
    import uuid as _uuid

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    payload = PersonaCreate(
        name="Jane",
        slug="jane",
        parent_occupation_id=_uuid.uuid4(),
        pricing_model=PricingModel.FREE,
    )
    with pytest.raises(service.PersonaError) as exc:
        await service.create_persona(
            db_session, creator=creator, payload=payload
        )
    assert exc.value.code == "persona.parent_occupation_invalid"


@pytest.mark.asyncio
async def test_create_persona_rejects_pricing_mismatch(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    payload = PersonaCreate(
        name="Jane",
        slug="jane",
        parent_occupation_id=parent.id,
        pricing_model=PricingModel.ONE_TIME,
        one_time_price_cents=None,
    )
    with pytest.raises(service.PersonaError) as exc:
        await service.create_persona(
            db_session, creator=creator, payload=payload
        )
    assert exc.value.code == "persona.pricing_required"


@pytest.mark.asyncio
async def test_create_persona_slug_conflict(db_session: AsyncSession) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    payload = PersonaCreate(
        name="One",
        slug="my-persona",
        parent_occupation_id=parent.id,
        pricing_model=PricingModel.FREE,
    )
    await service.create_persona(db_session, creator=creator, payload=payload)
    with pytest.raises(service.PersonaError) as exc:
        await service.create_persona(db_session, creator=creator, payload=payload)
    assert exc.value.code == "persona.slug_conflict"
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_update_persona_patches_fields(db_session: AsyncSession) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    initial = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    out = await service.update_persona(
        db_session,
        creator=creator,
        skill_id=initial.skill_id,
        patch=PersonaUpdate(
            name="Jane (v2)",
            specialization="Updated.",
            years_of_experience=15,
        ),
    )
    assert out.name == "Jane (v2)"
    assert out.specialization == "Updated."
    assert out.years_of_experience == 15


@pytest.mark.asyncio
async def test_update_persona_published_lock_on_parent_change(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent_a = await _make_occupation(db_session, creator=occ_creator, slug="occ-a")
    parent_b = await _make_occupation(db_session, creator=occ_creator, slug="occ-b")

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    initial = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent_a.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    # Force publish.
    skill = await db_session.get(Skill, initial.skill_id)
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.flush()

    with pytest.raises(service.PersonaError) as exc:
        await service.update_persona(
            db_session,
            creator=creator,
            skill_id=initial.skill_id,
            patch=PersonaUpdate(parent_occupation_id=parent_b.id),
        )
    assert exc.value.code == "persona.published_lock"
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_update_persona_not_owner_404(db_session: AsyncSession) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    owner = await _make_creator(
        db_session, email="owner@example.com", handle="owner",
    )
    intruder = await _make_creator(
        db_session, email="intruder@example.com", handle="intruder",
    )
    initial = await service.create_persona(
        db_session,
        creator=owner,
        payload=PersonaCreate(
            name="Owned",
            slug="owned",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    with pytest.raises(service.PersonaError) as exc:
        await service.update_persona(
            db_session,
            creator=intruder,
            skill_id=initial.skill_id,
            patch=PersonaUpdate(name="HACKED"),
        )
    assert exc.value.code == "persona.not_found"
    assert exc.value.status_code == 404


# ── Neuron membership ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reorder_neurons_updates_sort_order(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    n1 = await _make_neuron(db_session, creator=creator, slug="n1")
    n2 = await _make_neuron(db_session, creator=creator, slug="n2")
    n3 = await _make_neuron(db_session, creator=creator, slug="n3")
    await _attach_neuron(
        db_session,
        persona_skill_id=persona.skill_id, neuron_skill_id=n1.id, sort_order=0,
    )
    await _attach_neuron(
        db_session,
        persona_skill_id=persona.skill_id, neuron_skill_id=n2.id, sort_order=1,
    )
    await _attach_neuron(
        db_session,
        persona_skill_id=persona.skill_id, neuron_skill_id=n3.id, sort_order=2,
    )

    out = await service.reorder_neurons(
        db_session,
        creator=creator,
        skill_id=persona.skill_id,
        items=[
            NeuronOrderItem(neuron_skill_id=n3.id, sort_order=0),
            NeuronOrderItem(neuron_skill_id=n1.id, sort_order=1, section="alpha"),
            NeuronOrderItem(neuron_skill_id=n2.id, sort_order=2),
        ],
    )
    by_slug = {n.neuron_slug: n for n in out.items}
    assert by_slug["n3"].sort_order == 0
    assert by_slug["n1"].sort_order == 1
    assert by_slug["n1"].section == "alpha"
    assert by_slug["n2"].sort_order == 2


@pytest.mark.asyncio
async def test_reorder_neurons_rejects_unknown_neuron(
    db_session: AsyncSession,
) -> None:
    import uuid as _uuid

    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    with pytest.raises(service.PersonaError) as exc:
        await service.reorder_neurons(
            db_session,
            creator=creator,
            skill_id=persona.skill_id,
            items=[
                NeuronOrderItem(neuron_skill_id=_uuid.uuid4(), sort_order=0),
            ],
        )
    assert exc.value.code == "persona.neuron_not_found"


@pytest.mark.asyncio
async def test_reorder_neurons_rejects_duplicates(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    n1 = await _make_neuron(db_session, creator=creator, slug="n1")
    await _attach_neuron(
        db_session,
        persona_skill_id=persona.skill_id, neuron_skill_id=n1.id,
    )
    with pytest.raises(service.PersonaError) as exc:
        await service.reorder_neurons(
            db_session,
            creator=creator,
            skill_id=persona.skill_id,
            items=[
                NeuronOrderItem(neuron_skill_id=n1.id, sort_order=0),
                NeuronOrderItem(neuron_skill_id=n1.id, sort_order=1),
            ],
        )
    assert exc.value.code == "persona.duplicate_neuron"


@pytest.mark.asyncio
async def test_remove_neuron_deletes_row(db_session: AsyncSession) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    n1 = await _make_neuron(db_session, creator=creator, slug="n1")
    await _attach_neuron(
        db_session,
        persona_skill_id=persona.skill_id, neuron_skill_id=n1.id,
    )
    await service.remove_neuron(
        db_session,
        creator=creator,
        skill_id=persona.skill_id,
        neuron_skill_id=n1.id,
    )
    res = await db_session.execute(
        select(PersonaNeuron).where(
            PersonaNeuron.persona_id == persona.skill_id
        )
    )
    assert res.scalar_one_or_none() is None
    # Persona's denormalized count is refreshed.
    persona_row = await db_session.get(Persona, persona.skill_id)
    assert persona_row is not None
    assert persona_row.neuron_count == 0


@pytest.mark.asyncio
async def test_remove_neuron_not_present_404(db_session: AsyncSession) -> None:
    import uuid as _uuid

    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    with pytest.raises(service.PersonaError) as exc:
        await service.remove_neuron(
            db_session, creator=creator,
            skill_id=persona.skill_id, neuron_skill_id=_uuid.uuid4(),
        )
    assert exc.value.code == "persona.neuron_not_found"


# ── Listing + detail + neurons ───────────────────────────────────────


@pytest.mark.asyncio
async def test_list_personas_filters_kind_and_status(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    # Published persona.
    published = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Published",
            slug="pub",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    skill = await db_session.get(Skill, published.skill_id)
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.flush()

    # Draft persona — must not appear.
    await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Draft",
            slug="draft",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )

    # A plain skill — must not appear.
    await _make_skill(
        db_session, creator=creator, slug="plain-skill",
        kind=SkillKind.SKILL,
    )

    items, _ = await service.list_personas(
        db_session, service.PersonaFilters()
    )
    slugs = [i.slug for i in items]
    assert slugs == ["pub"]


@pytest.mark.asyncio
async def test_list_personas_filters_by_parent_occupation(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent_a = await _make_occupation(db_session, creator=occ_creator, slug="occ-a")
    parent_b = await _make_occupation(db_session, creator=occ_creator, slug="occ-b")

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    p_a = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Persona A",
            slug="persona-a",
            parent_occupation_id=parent_a.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    p_b = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Persona B",
            slug="persona-b",
            parent_occupation_id=parent_b.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    # Publish both.
    for pid in (p_a.skill_id, p_b.skill_id):
        skill = await db_session.get(Skill, pid)
        assert skill is not None
        skill.status = SkillStatus.PUBLISHED
    await db_session.flush()

    items, _ = await service.list_personas(
        db_session,
        service.PersonaFilters(parent_occupation_id=parent_a.id),
    )
    assert [i.slug for i in items] == ["persona-a"]


@pytest.mark.asyncio
async def test_get_persona_detail_includes_sample_neuron_titles(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    skill = await db_session.get(Skill, persona.skill_id)
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.flush()

    n1 = await _make_neuron(db_session, creator=creator, slug="incident-1")
    n2 = await _make_neuron(db_session, creator=creator, slug="incident-2")
    await _attach_neuron(
        db_session,
        persona_skill_id=persona.skill_id, neuron_skill_id=n1.id, sort_order=0,
    )
    await _attach_neuron(
        db_session,
        persona_skill_id=persona.skill_id, neuron_skill_id=n2.id, sort_order=1,
    )

    detail = await service.get_persona_detail(
        db_session, skill_id=persona.skill_id
    )
    assert detail is not None
    assert detail.parent_occupation.skill_id == parent.id
    assert detail.parent_occupation.slug == "ai-devops-engineer"
    # Note: alphabetical when sort_order ties.
    assert detail.sample_neuron_titles == [
        n1.name, n2.name,
    ]
    assert detail.caller_is_entitled is False  # no caller_id passed


@pytest.mark.asyncio
async def test_list_persona_neurons_404_for_non_entitled(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    skill = await db_session.get(Skill, persona.skill_id)
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.flush()

    random_buyer = await _make_creator(
        db_session, email="buyer@example.com", handle="buyer",
        is_creator_verified=False,
    )
    out = await service.list_persona_neurons(
        db_session, skill_id=persona.skill_id, caller_id=random_buyer.id,
    )
    assert out is None


@pytest.mark.asyncio
async def test_list_persona_neurons_returns_for_creator(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    # Creator/admin always entitled — even on draft personas.
    n1 = await _make_neuron(db_session, creator=creator, slug="n1")
    await _attach_neuron(
        db_session,
        persona_skill_id=persona.skill_id, neuron_skill_id=n1.id,
    )

    out = await service.list_persona_neurons(
        db_session, skill_id=persona.skill_id, caller_id=creator.id,
    )
    assert out is not None
    assert [n.neuron_slug for n in out.items] == ["n1"]


@pytest.mark.asyncio
async def test_list_persona_neurons_returns_for_license_holder(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona_out = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    skill = await db_session.get(Skill, persona_out.skill_id)
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED

    n1 = await _make_neuron(db_session, creator=creator, slug="n1")
    await _attach_neuron(
        db_session,
        persona_skill_id=persona_out.skill_id, neuron_skill_id=n1.id,
    )

    # A buyer who actually holds a license.
    import uuid as _uuid

    buyer = await _make_creator(
        db_session, email="buyer@example.com", handle="buyer",
        is_creator_verified=False,
    )
    lic = License(
        buyer_id=buyer.id,
        skill_id=persona_out.skill_id,
        source=LicenseSource.ONE_TIME,
        source_id=_uuid.uuid4(),
        granted_at=datetime.now(UTC),
        status=LicenseStatus.ACTIVE,
        support_tier=SupportTier.NONE,
        composition_role=LicenseCompositionRole.PERSONA,
        target_occupation_skill_id=parent.id,
    )
    db_session.add(lic)
    await db_session.flush()

    out = await service.list_persona_neurons(
        db_session, skill_id=persona_out.skill_id, caller_id=buyer.id,
    )
    assert out is not None
    assert [n.neuron_slug for n in out.items] == ["n1"]


# ── Persona-checkout entitlement gate (T-04 acceptance bullet 2) ─────


@pytest.mark.asyncio
async def test_persona_checkout_gate_passes_for_non_persona(
    db_session: AsyncSession,
) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    buyer = await _make_creator(
        db_session, email="buyer@example.com", handle="buyer",
        is_creator_verified=False,
    )
    skill = await _make_skill(db_session, creator=creator, slug="some-skill")
    gate = await service.check_persona_checkout_entitlement(
        db_session, buyer=buyer, skill=skill,
    )
    assert gate.ok is True
    assert gate.parent_occupation_skill_id is None


@pytest.mark.asyncio
async def test_persona_checkout_gate_blocks_without_parent_license(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona_out = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    persona_skill = await db_session.get(Skill, persona_out.skill_id)
    assert persona_skill is not None

    buyer = await _make_creator(
        db_session, email="buyer@example.com", handle="buyer",
        is_creator_verified=False,
    )
    gate = await service.check_persona_checkout_entitlement(
        db_session, buyer=buyer, skill=persona_skill,
    )
    assert gate.ok is False
    assert str(gate.parent_occupation_skill_id) == str(parent.id)
    assert gate.parent_occupation_slug == "ai-devops-engineer"
    assert gate.parent_occupation_handle == "occ-creator"


@pytest.mark.asyncio
async def test_persona_checkout_gate_passes_with_active_parent_license(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona_out = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    persona_skill = await db_session.get(Skill, persona_out.skill_id)
    assert persona_skill is not None

    import uuid as _uuid

    buyer = await _make_creator(
        db_session, email="buyer@example.com", handle="buyer",
        is_creator_verified=False,
    )
    # Mint an active OCCUPATION license on the parent for the buyer.
    lic = License(
        buyer_id=buyer.id,
        skill_id=parent.id,
        source=LicenseSource.ONE_TIME,
        source_id=_uuid.uuid4(),
        granted_at=datetime.now(UTC),
        status=LicenseStatus.ACTIVE,
        support_tier=SupportTier.NONE,
        composition_role=LicenseCompositionRole.OCCUPATION,
    )
    db_session.add(lic)
    await db_session.flush()

    gate = await service.check_persona_checkout_entitlement(
        db_session, buyer=buyer, skill=persona_skill,
    )
    assert gate.ok is True


@pytest.mark.asyncio
async def test_persona_checkout_gate_rejects_persona_license_as_anchor(
    db_session: AsyncSession,
) -> None:
    """A composition_role=persona license cannot itself serve as the anchor."""
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona_out = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    persona_skill = await db_session.get(Skill, persona_out.skill_id)
    assert persona_skill is not None

    import uuid as _uuid

    buyer = await _make_creator(
        db_session, email="buyer@example.com", handle="buyer",
        is_creator_verified=False,
    )
    # A "persona" license on the parent occupation id would be malformed
    # in production — but the gate should still refuse to treat it as
    # an anchor.
    lic = License(
        buyer_id=buyer.id,
        skill_id=parent.id,
        source=LicenseSource.ONE_TIME,
        source_id=_uuid.uuid4(),
        granted_at=datetime.now(UTC),
        status=LicenseStatus.ACTIVE,
        support_tier=SupportTier.NONE,
        composition_role=LicenseCompositionRole.PERSONA,
        target_occupation_skill_id=parent.id,
    )
    db_session.add(lic)
    await db_session.flush()

    gate = await service.check_persona_checkout_entitlement(
        db_session, buyer=buyer, skill=persona_skill,
    )
    assert gate.ok is False


# ── Build / publish stubs ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_trigger_build_rejects_empty_neurons(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona_out = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Empty",
            slug="empty",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    parent_skill = await db_session.get(Skill, persona_out.skill_id)
    assert parent_skill is not None
    await _make_version(db_session, skill=parent_skill, version="1.0.0", released=False)
    with pytest.raises(service.PersonaError) as exc:
        await service.trigger_build(
            db_session, creator=creator,
            skill_id=persona_out.skill_id, version="1.0.0",
        )
    assert exc.value.code == "persona.no_neurons"


@pytest.mark.asyncio
async def test_trigger_build_emits_audit_row(db_session: AsyncSession) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona_out = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    parent_skill = await db_session.get(Skill, persona_out.skill_id)
    assert parent_skill is not None
    n1 = await _make_neuron(db_session, creator=creator, slug="n1")
    await _attach_neuron(
        db_session,
        persona_skill_id=persona_out.skill_id, neuron_skill_id=n1.id,
    )
    await _make_version(db_session, skill=parent_skill, version="1.0.0", released=False)

    job = await service.trigger_build(
        db_session, creator=creator,
        skill_id=persona_out.skill_id, version="1.0.0",
    )
    assert job.status == "queued"
    assert job.job_id.startswith("personas:build:")

    audit = await db_session.execute(
        select(AuditLog).where(AuditLog.action == "persona.build_queued")
    )
    assert audit.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_publish_marks_version_released(db_session: AsyncSession) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator",
    )
    parent = await _make_occupation(db_session, creator=occ_creator)

    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe",
    )
    persona_out = await service.create_persona(
        db_session,
        creator=creator,
        payload=PersonaCreate(
            name="Jane",
            slug="jane",
            parent_occupation_id=parent.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    parent_skill = await db_session.get(Skill, persona_out.skill_id)
    assert parent_skill is not None
    n1 = await _make_neuron(db_session, creator=creator, slug="n1")
    await _attach_neuron(
        db_session,
        persona_skill_id=persona_out.skill_id, neuron_skill_id=n1.id,
    )
    version = await _make_version(
        db_session, skill=parent_skill, version="1.0.0", released=False
    )
    job = await service.publish_persona(
        db_session,
        creator=creator,
        skill_id=persona_out.skill_id,
        payload=PublishRequest(version="1.0.0", changelog_md="First."),
    )
    assert job.status == "queued"
    await db_session.refresh(version)
    await db_session.refresh(parent_skill)
    assert version.released_at is not None
    assert parent_skill.status == SkillStatus.PUBLISHED
    assert parent_skill.latest_version_id == version.id
