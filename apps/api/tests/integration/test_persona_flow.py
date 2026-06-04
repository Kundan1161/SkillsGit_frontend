"""End-to-end persona flow (T-14, Wave 5).

Verifies the T-04 acceptance criteria:

1. Create creator → create persona (``persona.service.create_persona``).
2. Add 3 neurons (via direct ORM since capture is its own flow tested
   in ``test_capture_flow.py``).
3. Publish via ``publish_persona`` which triggers a vault_build.
4. Assert: persona Skill row with ``kind='persona' status='published'``,
   3 ``persona_neurons`` rows, one ``vault_builds`` row with
   ``status='succeeded'``.

Also exercises the 409 gate: a buyer without an active occupation
license tries to purchase the persona — must trip
``persona.requires_parent_occupation``.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.personas import service as persona_service
from src.personas.models import Persona, PersonaNeuron
from src.personas.schemas import PersonaCreate, PublishRequest
from src.skills.models import (
    PricingModel,
    Skill,
    SkillKind,
    SkillStatus,
    SkillVersion,
)
from src.storage.s3 import InMemoryStorage
from src.vault.models import VaultBuild, VaultBuildStatus

from tests.integration._seed_helpers import (
    add_skill_with_body,
    attach_occupation_member,
    make_buyer,
    make_creator,
    make_occupation_skill,
)

_NEURON_BLOCK = {
    "situation": "Production incident at 3am.",
    "decision": "Roll back the deploy + write the runbook.",
    "outcome": "15-min impact; runbook reused 3x.",
    "recorded_at": "2024-10-15",
    "confidence": "high",
}


async def _ensure_persona_version(
    db: AsyncSession,
    *,
    storage: InMemoryStorage,
    skill: Skill,
    version: str = "1.0.0",
) -> SkillVersion:
    """Mint a placeholder SkillVersion for a persona, mirroring the
    real ``scripts/build_devops_persona.py`` flow."""
    storage_key = f"skills/{skill.id}/{version}.persona.json"
    await storage.put_object(storage_key, b"{}", "application/json")
    row = SkillVersion(
        skill_id=skill.id,
        version=version,
        content_hash="e" * 64,
        storage_url=storage_key,
        ai_requirements=None,
        changelog_md=None,
        released_at=None,
        released_by=None,
        is_yanked=False,
    )
    db.add(row)
    await db.flush([row])
    skill.latest_version_id = row.id
    await db.flush()
    return row


async def _seed_published_occupation(
    db: AsyncSession,
    storage: InMemoryStorage,
    *,
    handle: str = "occ-creator",
    slug: str = "ai-devops-engineer-it",
) -> tuple[Skill, list[Skill]]:
    """Seed a published occupation with 3 member skills."""
    occ_creator = await make_creator(
        db, email=f"{handle}@example.local", handle=handle
    )
    members = []
    for i, mslug in enumerate(
        ("ci-pipeline-architect", "ops-runbook-generator", "ops-incident-commander")
    ):
        skill, _ver = await add_skill_with_body(
            db,
            storage=storage,
            creator=occ_creator,
            creator_handle=handle,
            slug=mslug,
            name=mslug.replace("-", " ").title(),
        )
        members.append(skill)
    occ_skill, _occ_row, _occ_version = await make_occupation_skill(
        db,
        creator=occ_creator,
        slug=slug,
        name="AI DevOps Engineer (it)",
        domains=["ci-cd", "incident"],
    )
    for i, m in enumerate(members):
        await attach_occupation_member(
            db,
            occupation_skill=occ_skill,
            member_skill=m,
            domain="ci-cd" if i == 0 else "incident",
            sort_order=i,
        )
    occ_skill.status = SkillStatus.PUBLISHED
    await db.flush([occ_skill])
    return occ_skill, members


@pytest.mark.asyncio
async def test_persona_create_neurons_publish_build(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Full happy-path through the persona service + builder façade."""
    # Parent occupation (different creator, as in production).
    parent_occ, members = await _seed_published_occupation(
        db_session, memory_storage
    )

    # Persona creator.
    persona_creator = await make_creator(
        db_session, email="jane@example.local", handle="jane-demo"
    )

    # Create the persona.
    persona_payload = PersonaCreate(
        name="Jane Devops (integration)",
        slug="jane-incident-it",
        parent_occupation_id=parent_occ.id,
        creator_intro_md="Jane's persona for integration tests.",
        specialization="Integration testing",
        years_of_experience=7,
        description_md=None,
        category="personas",
        tags=["devops"],
        pricing_model=PricingModel.FREE,
    )
    persona_read = await persona_service.create_persona(
        db_session, creator=persona_creator, payload=persona_payload
    )
    assert persona_read.kind == SkillKind.PERSONA
    persona_skill_id = persona_read.id

    persona_skill = await db_session.get(Skill, persona_skill_id)
    assert persona_skill is not None
    assert persona_skill.kind == SkillKind.PERSONA

    persona_row = await db_session.get(Persona, persona_skill_id)
    assert persona_row is not None
    assert str(persona_row.parent_occupation_id) == str(parent_occ.id)

    # Add 3 neurons. Capture is its own flow (tested in test_capture_flow);
    # here we attach memory_neuron skills directly so the persona's
    # neuron_count > 0 when publish_persona runs.
    neurons: list[Skill] = []
    for i, member in enumerate(members):
        neuron_slug = f"jane-neuron-{i}"
        neuron_skill, _ = await add_skill_with_body(
            db_session,
            storage=memory_storage,
            creator=persona_creator,
            creator_handle="jane-demo",
            slug=neuron_slug,
            name=f"Jane Neuron {i}",
            kind=SkillKind.MEMORY_NEURON,
            links=[{"target": f"base/{member.slug}", "relation": "applies"}],
            neuron_block=_NEURON_BLOCK,
            parent_occupation_id=f"occ-creator/{parent_occ.slug}",
        )
        join_row = PersonaNeuron(
            persona_id=persona_skill_id,
            neuron_skill_id=neuron_skill.id,
            sort_order=i,
            section=None,
        )
        db_session.add(join_row)
        await db_session.flush([join_row])
        neurons.append(neuron_skill)

    # Bump neuron_count to match — production flow does this in the
    # capture-finalize service; here we mirror it.
    persona_row.neuron_count = 3
    await db_session.flush([persona_row])

    # Mint the persona's SkillVersion row before publish.
    await _ensure_persona_version(
        db_session, storage=memory_storage, skill=persona_skill, version="1.0.0"
    )

    # Publish — runs the persona builder inline.
    job = await persona_service.publish_persona(
        db_session,
        creator=persona_creator,
        skill_id=persona_skill_id,
        payload=PublishRequest(
            version="1.0.0", changelog_md="Integration test publish."
        ),
    )
    assert job.status in ("succeeded", "queued", "completed"), job.status

    await db_session.refresh(persona_skill)
    assert persona_skill.status == SkillStatus.PUBLISHED

    # Assert persona_neurons count.
    res = await db_session.execute(
        select(PersonaNeuron).where(
            PersonaNeuron.persona_id == persona_skill_id
        )
    )
    join_rows = list(res.scalars().all())
    assert len(join_rows) == 3

    # Exactly one succeeded vault_build.
    res = await db_session.execute(
        select(VaultBuild).where(VaultBuild.skill_id == persona_skill_id)
    )
    builds = list(res.scalars().all())
    succeeded = [b for b in builds if b.status == VaultBuildStatus.SUCCEEDED]
    assert len(succeeded) == 1, (
        f"Expected exactly one succeeded vault_build; found {len(builds)} "
        f"({[b.status for b in builds]})"
    )


@pytest.mark.asyncio
async def test_persona_checkout_gate_without_parent_license(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """T-04 acceptance: buying a persona without the parent occupation
    license trips ``persona.requires_parent_occupation``.

    Driven via ``personas.service.check_persona_checkout_entitlement``
    — the same function the billing router calls before allowing a
    persona checkout to proceed.
    """
    parent_occ, _members = await _seed_published_occupation(
        db_session, memory_storage, handle="occ-gate", slug="gated-occ"
    )

    # Persona creator + persona row.
    persona_creator = await make_creator(
        db_session, email="gate@example.local", handle="gate-creator"
    )
    persona_read = await persona_service.create_persona(
        db_session,
        creator=persona_creator,
        payload=PersonaCreate(
            name="Gated Persona",
            slug="gated-persona",
            parent_occupation_id=parent_occ.id,
            pricing_model=PricingModel.FREE,
        ),
    )
    persona_skill = await db_session.get(Skill, persona_read.id)
    assert persona_skill is not None

    # Buyer with NO active occupation license.
    buyer = await make_buyer(db_session, email="buyer-without@example.local")

    gate = await persona_service.check_persona_checkout_entitlement(
        db_session, buyer=buyer, skill=persona_skill
    )
    assert gate.ok is False, (
        "Gate must reject when buyer does not hold the parent license — "
        "this is the 409 persona.requires_parent_occupation contract"
    )
    assert str(gate.parent_occupation_skill_id) == str(parent_occ.id)
    assert gate.parent_occupation_slug == parent_occ.slug
    assert gate.parent_occupation_handle == "occ-gate"
