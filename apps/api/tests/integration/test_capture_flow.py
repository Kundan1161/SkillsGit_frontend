"""End-to-end capture flow (T-14, Wave 5).

T-05 acceptance translated into integration coverage:

1. Create a capture session.
2. Enqueue extract (LLM stub returns synchronously under
   ``SKG_CAPTURE_LLM_STUB=1``).
3. Poll the session — draft_md populated.
4. Finalize — assert a new ``kind=memory_neuron`` Skill + Version +
   persona_neurons row exists; capture session is marked finalized.

PII variant: a session whose draft contains a credit-card number must
hard-block at finalize with ``capture.pii_blocked``.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.capture import service as capture_service
from src.capture.models import CaptureSession, CaptureSessionStatus
from src.capture.schemas import (
    CaptureFinalize,
    CaptureSessionCreate,
)
from src.personas.models import Persona, PersonaNeuron
from src.skills.models import (
    Skill,
    SkillKind,
    SkillVersion,
)
from src.storage.s3 import InMemoryStorage

from tests.integration._seed_helpers import (
    add_skill_with_body,
    attach_occupation_member,
    make_creator,
    make_occupation_skill,
)


async def _seed_persona_for_capture(
    db: AsyncSession,
    storage: InMemoryStorage,
) -> tuple[Persona, Skill]:
    """Seed (creator + parent occupation + persona) for a capture session.

    Returns ``(persona_row, persona_skill)`` — the persona's ``skill_id``
    is what the capture session references.
    """
    occ_creator = await make_creator(
        db, email="occ-cap@x.local", handle="occ-cap"
    )
    parent_member, _ = await add_skill_with_body(
        db,
        storage=storage,
        creator=occ_creator,
        creator_handle="occ-cap",
        slug="ops-incident-commander",
        name="Ops Incident Commander",
    )
    parent_occ, _occ_row, _ = await make_occupation_skill(
        db,
        creator=occ_creator,
        slug="ai-devops-engineer-cap",
        name="AI DevOps Engineer (capture)",
        domains=["incident"],
    )
    await attach_occupation_member(
        db,
        occupation_skill=parent_occ,
        member_skill=parent_member,
        domain="incident",
        sort_order=0,
    )

    # Persona creator + persona skill.
    persona_creator = await make_creator(
        db, email="cap-creator@x.local", handle="cap-creator"
    )
    persona_skill = Skill(
        creator_id=persona_creator.id,
        slug="cap-test-persona",
        name="Capture Test Persona",
        tagline="Persona for capture integration test",
        description_md="x",
        category="personas",
        tags=["persona"],
        status="draft",  # str OK — column accepts the enum value
        kind=SkillKind.PERSONA,
        pricing_model="free",
    )
    db.add(persona_skill)
    await db.flush()
    persona = Persona(
        skill_id=persona_skill.id,
        parent_occupation_id=parent_occ.id,
        creator_intro_md=None,
        specialization=None,
        years_of_experience=None,
        neuron_count=0,
    )
    db.add(persona)
    await db.flush()
    # Return both — tests reuse ``persona_creator`` from the persona_skill.
    return persona, persona_skill


@pytest.mark.asyncio
async def test_capture_create_extract_finalize_happy_path(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
    fake_redis: object,
) -> None:
    """Full capture lifecycle: create → extract → finalize → neuron."""
    _persona, persona_skill = await _seed_persona_for_capture(
        db_session, memory_storage
    )
    from src.users.models import User

    creator = await db_session.get(User, persona_skill.creator_id)
    assert creator is not None

    # 1. Create the session.
    session_read = await capture_service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(
            persona_id=persona_skill.id,
            title="Integration capture",
            situation_md="A small integration scenario for the LLM stub.",
            decision_md="We chose option X.",
            outcome_md="Pass rate restored.",
            context_md="Test harness only.",
        ),
    )
    assert session_read.status == CaptureSessionStatus.DRAFT

    # 2. Enqueue extract — stub runs synchronously and populates draft_md.
    job = await capture_service.enqueue_extract(
        db_session, creator=creator, session_id=session_read.id
    )
    assert job.status in ("completed", "queued")

    # 3. Poll — draft is ready.
    polled = await capture_service.get_session(
        db_session, creator=creator, session_id=session_read.id
    )
    assert polled.status == CaptureSessionStatus.DRAFT_READY
    assert polled.draft_md, "stub LLM should have populated draft_md"

    # 4. Finalize.
    result = await capture_service.finalize_session(
        db_session,
        creator=creator,
        session_id=session_read.id,
        payload=CaptureFinalize(neuron_slug="capture-integration"),
    )
    assert result.neuron_version == "1.0.0"

    # Neuron Skill + SkillVersion + persona_neurons row exist.
    neuron_skill = await db_session.get(Skill, result.neuron_skill_id)
    assert neuron_skill is not None
    assert neuron_skill.kind == SkillKind.MEMORY_NEURON
    versions = await db_session.execute(
        select(SkillVersion).where(SkillVersion.skill_id == neuron_skill.id)
    )
    assert len(list(versions.scalars().all())) == 1

    join = await db_session.execute(
        select(PersonaNeuron).where(
            PersonaNeuron.persona_id == persona_skill.id,
            PersonaNeuron.neuron_skill_id == neuron_skill.id,
        )
    )
    assert join.scalar_one_or_none() is not None

    # Capture session is FINALIZED + linked.
    after = await db_session.get(CaptureSession, session_read.id)
    assert after is not None
    assert after.status == CaptureSessionStatus.FINALIZED
    assert after.finalized_at is not None
    assert str(after.finalized_neuron_skill_id) == str(neuron_skill.id)

    # Persona neuron_count bumped — the service updated the row but the
    # cached identity-map row might be stale; refresh before asserting.
    persona_after = await db_session.get(Persona, persona_skill.id)
    assert persona_after is not None
    await db_session.refresh(persona_after)
    assert persona_after.neuron_count == 1


@pytest.mark.asyncio
async def test_capture_pii_credit_card_hard_blocks_finalize(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
    fake_redis: object,
) -> None:
    """T-05 acceptance: a CCN in the draft hard-blocks finalize with
    ``capture.pii_blocked``.

    We inject the CCN into the draft post-extract so we don't depend on
    the LLM stub generating one — the production behaviour is the same:
    the PII gate fires on whatever ``draft_md`` is at finalize time.
    """
    _persona, persona_skill = await _seed_persona_for_capture(
        db_session, memory_storage
    )
    from src.users.models import User

    creator = await db_session.get(User, persona_skill.creator_id)
    assert creator is not None

    session_read = await capture_service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(
            persona_id=persona_skill.id,
            title="PII capture",
            situation_md="Production CCN appeared in logs.",
            decision_md="Filtered + rotated.",
            outcome_md="No exposure.",
        ),
    )
    await capture_service.enqueue_extract(
        db_session, creator=creator, session_id=session_read.id
    )

    # Splice a hard-block secret into the draft directly. Mirrors the
    # existing capture/tests/test_service.py::test_finalize_blocks_on_credit_card
    # pattern.
    row = await db_session.get(CaptureSession, session_read.id)
    assert row is not None
    assert row.draft_md
    row.draft_md = row.draft_md + "\n\nCard: 4111111111111111\n"
    await db_session.flush([row])

    with pytest.raises(capture_service.CaptureError) as exc:
        await capture_service.finalize_session(
            db_session,
            creator=creator,
            session_id=session_read.id,
            payload=CaptureFinalize(neuron_slug="pii-blocked"),
        )
    assert exc.value.code == "capture.pii_blocked"

    # Capture session must NOT be finalized — the transaction is gated
    # before any skill row insertion.
    after = await db_session.get(CaptureSession, session_read.id)
    assert after is not None
    assert after.status != CaptureSessionStatus.FINALIZED
    assert after.finalized_neuron_skill_id is None
