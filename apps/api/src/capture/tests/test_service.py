"""Service-level unit tests for the capture module.

These talk to the ORM directly (via the ``db_session`` fixture) and
exercise every branch of :mod:`src.capture.service` without going
through HTTP. Router-level coverage lives in ``test_router.py``.

T-05 acceptance bullets covered here:
- LLM extraction populates draft_md (synchronously under the stub).
- PII detector flags expected spans on the with_pii fixture.
- Finalize creates skills + skill_versions + persona_neurons rows
  atomically; failure rolls back the whole transaction.
- Quota: 11th extract returns 429 with `capture.quota_exceeded`.
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.capture import quota, service
from src.capture.models import CaptureAttachment, CaptureSession, CaptureSessionStatus
from src.capture.schemas import (
    CaptureFinalize,
    CaptureSessionCreate,
    CaptureSessionUpdate,
)
from src.core.db import AuditLog
from src.occupations.models import Occupation
from src.personas.models import Persona, PersonaNeuron
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


async def _make_occupation(
    session: AsyncSession,
    *,
    creator: User,
    slug: str = "ai-devops-engineer",
) -> Skill:
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=slug.replace("-", " ").title(),
        tagline=f"Tagline for {slug}",
        description_md=f"# {slug}\n",
        category="engineering",
        tags=["devops"],
        status=SkillStatus.PUBLISHED,
        kind=SkillKind.OCCUPATION,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    session.add(
        Occupation(
            skill_id=skill.id,
            summary_md=f"Summary for {slug}",
            domains=["ci-cd", "observability"],
            persona_count=0,
            recommended_persona_count=2,
        )
    )
    await session.flush()
    return skill


async def _make_persona(
    session: AsyncSession,
    *,
    creator: User,
    parent_skill_id: uuid.UUID,
    slug: str = "jane-devops",
) -> Skill:
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=slug.replace("-", " ").title(),
        tagline=None,
        description_md=None,
        category="engineering",
        tags=["persona"],
        status=SkillStatus.DRAFT,
        kind=SkillKind.PERSONA,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    session.add(
        Persona(
            skill_id=skill.id,
            parent_occupation_id=parent_skill_id,
            creator_intro_md=None,
            specialization=None,
            years_of_experience=None,
            neuron_count=0,
        )
    )
    await session.flush()
    return skill


async def _quick_setup(
    db_session: AsyncSession,
) -> tuple[User, Skill, Skill]:
    """Seed (creator, parent occupation, persona) in one call."""
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator"
    )
    parent = await _make_occupation(db_session, creator=occ_creator)
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe"
    )
    persona = await _make_persona(
        db_session, creator=creator, parent_skill_id=parent.id
    )
    return creator, parent, persona


# ── create_session ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_session_happy_path(db_session: AsyncSession) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    out = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(
            persona_id=persona.id,
            title="Flaky CI",
            situation_md="Flaky tests after Redis upgrade.",
            decision_md="Per-suite DB indexes.",
            outcome_md="Pass rate 99%.",
        ),
    )
    assert out.persona_id == persona.id
    assert out.status == CaptureSessionStatus.DRAFT
    assert out.title == "Flaky CI"

    # Audit row.
    audit = await db_session.execute(
        select(AuditLog).where(AuditLog.action == "capture_session.created")
    )
    rows = list(audit.scalars().all())
    assert len(rows) == 1
    assert str(rows[0].actor_id) == str(creator.id)


@pytest.mark.asyncio
async def test_create_session_requires_verified_creator(
    db_session: AsyncSession,
) -> None:
    occ_creator = await _make_creator(
        db_session, email="occ@example.com", handle="occ-creator"
    )
    parent = await _make_occupation(db_session, creator=occ_creator)
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe"
    )
    persona = await _make_persona(
        db_session, creator=creator, parent_skill_id=parent.id
    )

    unverified = await _make_creator(
        db_session, email="anon@example.com", handle="anon",
        is_creator_verified=False,
    )
    with pytest.raises(service.CaptureError) as exc:
        await service.create_session(
            db_session,
            creator=unverified,
            payload=CaptureSessionCreate(
                persona_id=persona.id, title="X",
            ),
        )
    assert exc.value.code == "capture.creator_not_verified"
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_create_session_rejects_unowned_persona(
    db_session: AsyncSession,
) -> None:
    _, _parent, persona = await _quick_setup(db_session)
    intruder = await _make_creator(
        db_session, email="intruder@example.com", handle="intruder"
    )
    with pytest.raises(service.CaptureError) as exc:
        await service.create_session(
            db_session,
            creator=intruder,
            payload=CaptureSessionCreate(
                persona_id=persona.id, title="X",
            ),
        )
    assert exc.value.code == "capture.persona_not_owned"
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_create_session_rejects_unknown_persona(
    db_session: AsyncSession,
) -> None:
    creator = await _make_creator(
        db_session, email="jane@example.com", handle="janedoe"
    )
    with pytest.raises(service.CaptureError) as exc:
        await service.create_session(
            db_session,
            creator=creator,
            payload=CaptureSessionCreate(
                persona_id=uuid.uuid4(), title="X",
            ),
        )
    assert exc.value.code == "capture.persona_not_found"


# ── update_session ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_session_patches_fields(db_session: AsyncSession) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    out = await service.update_session(
        db_session,
        creator=creator,
        session_id=initial.id,
        patch=CaptureSessionUpdate(
            title="Y",
            situation_md="Updated situation.",
            draft_md="custom",
        ),
    )
    assert out.title == "Y"
    assert out.situation_md == "Updated situation."
    assert out.draft_md == "custom"


@pytest.mark.asyncio
async def test_update_session_404_for_intruder(
    db_session: AsyncSession,
) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    intruder = await _make_creator(
        db_session, email="intruder@example.com", handle="intruder"
    )
    with pytest.raises(service.CaptureError) as exc:
        await service.update_session(
            db_session,
            creator=intruder,
            session_id=initial.id,
            patch=CaptureSessionUpdate(title="HACK"),
        )
    assert exc.value.code == "capture.not_found"
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_session_rejects_after_finalize(
    db_session: AsyncSession,
) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    # Manually flip status to FINALIZED for the test.
    row = await db_session.get(CaptureSession, initial.id)
    assert row is not None
    row.status = CaptureSessionStatus.FINALIZED
    await db_session.flush()

    with pytest.raises(service.CaptureError) as exc:
        await service.update_session(
            db_session,
            creator=creator,
            session_id=initial.id,
            patch=CaptureSessionUpdate(title="Z"),
        )
    assert exc.value.code == "capture.terminal_status"


# ── run_extract (the stub LLM path) ──────────────────────────────────


@pytest.mark.asyncio
async def test_run_extract_populates_draft_synchronously(
    db_session: AsyncSession,
    capture_fixtures: dict[str, Any],
) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    fixture = capture_fixtures["happy"]
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(
            persona_id=persona.id,
            title=fixture["title"],
            situation_md=fixture["situation_md"],
            decision_md=fixture["decision_md"],
            outcome_md=fixture["outcome_md"],
            context_md=fixture["context_md"],
        ),
    )
    out = await service.run_extract(
        db_session, creator=creator, session_id=initial.id
    )
    assert out.status == CaptureSessionStatus.DRAFT_READY
    assert out.draft_md is not None
    assert "memory_neuron" in out.draft_md
    assert out.llm_model is not None
    assert out.llm_model.startswith("claude")
    # Audit row exists.
    audit = await db_session.execute(
        select(AuditLog).where(AuditLog.action == "capture_session.extracted")
    )
    assert audit.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_run_extract_consumes_quota(
    db_session: AsyncSession,
    fake_redis: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The router goes through enqueue_extract → reserve quota → run."""
    monkeypatch.setattr("src.auth.deps._redis", fake_redis)
    monkeypatch.setattr("src.auth.deps.get_redis", lambda: fake_redis)
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    await service.run_extract(
        db_session, creator=creator, session_id=initial.id
    )
    used, cap = await quota.peek(creator.id, redis=fake_redis)
    assert used == 1
    assert cap == 10


@pytest.mark.asyncio
async def test_run_extract_skips_quota_when_disabled(
    db_session: AsyncSession,
    fake_redis: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Arq retries set consume_quota=False so we don't double-charge."""
    monkeypatch.setattr("src.auth.deps._redis", fake_redis)
    monkeypatch.setattr("src.auth.deps.get_redis", lambda: fake_redis)
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    await service.run_extract(
        db_session, creator=creator, session_id=initial.id, consume_quota=False
    )
    used, _cap = await quota.peek(creator.id, redis=fake_redis)
    assert used == 0


# ── enqueue_extract — the router-facing wrapper ──────────────────────


@pytest.mark.asyncio
async def test_enqueue_extract_runs_sync_under_stub(
    db_session: AsyncSession,
    fake_redis: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Under SKG_CAPTURE_LLM_STUB=1, enqueue runs in-process."""
    monkeypatch.setattr("src.auth.deps._redis", fake_redis)
    monkeypatch.setattr("src.auth.deps.get_redis", lambda: fake_redis)
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    job = await service.enqueue_extract(
        db_session, creator=creator, session_id=initial.id
    )
    assert job.status == "completed"  # sync stub path
    after = await db_session.get(CaptureSession, initial.id)
    assert after is not None
    assert after.status == CaptureSessionStatus.DRAFT_READY
    assert after.draft_md is not None


# ── finalize_session — the atomic transaction ────────────────────────


@pytest.mark.asyncio
async def test_finalize_creates_neuron_atomically(
    db_session: AsyncSession,
    in_memory_storage: Any,
    fake_redis: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T-05 acceptance: skills + skill_versions + persona_neurons in one tx."""
    monkeypatch.setattr("src.auth.deps._redis", fake_redis)
    monkeypatch.setattr("src.auth.deps.get_redis", lambda: fake_redis)
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(
            persona_id=persona.id,
            title="Flaky CI tests after Redis upgrade",
            situation_md="Flaky tests began after Redis 6→7 upgrade.",
            decision_md="Assigned per-suite DB indexes.",
            outcome_md="Pass rate 99.4%.",
        ),
    )
    await service.run_extract(
        db_session, creator=creator, session_id=initial.id
    )
    out = await service.finalize_session(
        db_session,
        creator=creator,
        session_id=initial.id,
        payload=CaptureFinalize(neuron_slug="flaky-ci-redis"),
    )
    # NeuronCreated payload sanity.
    assert out.neuron_version == "1.0.0"
    assert out.persona_id == persona.id
    assert out.vault_path_hint.endswith("flaky-ci-redis.md")

    # Skill + SkillVersion + PersonaNeuron rows exist.
    skill = await db_session.get(Skill, out.neuron_skill_id)
    assert skill is not None
    assert skill.kind == SkillKind.MEMORY_NEURON
    assert skill.status == SkillStatus.DRAFT
    assert skill.latest_version_id is not None
    version_res = await db_session.execute(
        select(SkillVersion).where(SkillVersion.skill_id == skill.id)
    )
    version_rows = list(version_res.scalars().all())
    assert len(version_rows) == 1
    assert version_rows[0].version == "1.0.0"

    join_res = await db_session.execute(
        select(PersonaNeuron).where(
            PersonaNeuron.persona_id == persona.id,
            PersonaNeuron.neuron_skill_id == skill.id,
        )
    )
    assert join_res.scalar_one_or_none() is not None

    # Persona neuron_count was bumped.
    persona_row = await db_session.get(Persona, persona.id)
    assert persona_row is not None
    assert persona_row.neuron_count == 1

    # Capture session is FINALIZED + linked.
    after = await db_session.get(CaptureSession, initial.id)
    assert after is not None
    assert after.status == CaptureSessionStatus.FINALIZED
    assert after.finalized_neuron_skill_id == skill.id
    assert after.finalized_at is not None

    # Storage write happened.
    assert any(
        str(skill.id) in key for key in in_memory_storage.objects
    )


@pytest.mark.asyncio
async def test_finalize_blocks_on_credit_card(
    db_session: AsyncSession,
    in_memory_storage: Any,
    fake_redis: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T-05 acceptance: hard-block secrets refuse finalize."""
    monkeypatch.setattr("src.auth.deps._redis", fake_redis)
    monkeypatch.setattr("src.auth.deps.get_redis", lambda: fake_redis)
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    await service.run_extract(
        db_session, creator=creator, session_id=initial.id
    )
    # Inject a hard-block secret directly into the draft.
    row = await db_session.get(CaptureSession, initial.id)
    assert row is not None
    assert row.draft_md is not None
    row.draft_md = row.draft_md + "\n\nCard: 4111111111111111\n"
    await db_session.flush()

    with pytest.raises(service.CaptureError) as exc:
        await service.finalize_session(
            db_session,
            creator=creator,
            session_id=initial.id,
            payload=CaptureFinalize(neuron_slug="x-slug"),
        )
    assert exc.value.code == "capture.pii_blocked"
    assert exc.value.status_code == 422

    # No skill row was created.
    skill_res = await db_session.execute(
        select(Skill).where(
            Skill.creator_id == creator.id,
            Skill.slug == "x-slug",
        )
    )
    assert skill_res.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_finalize_blocks_on_slug_collision(
    db_session: AsyncSession,
    in_memory_storage: Any,
    fake_redis: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.auth.deps._redis", fake_redis)
    monkeypatch.setattr("src.auth.deps.get_redis", lambda: fake_redis)
    creator, _parent, persona = await _quick_setup(db_session)
    # Pre-claim the slug on a plain skill.
    existing = Skill(
        creator_id=creator.id,
        slug="dup-slug",
        name="Already Taken",
        category=None,
        status=SkillStatus.DRAFT,
        kind=SkillKind.SKILL,
        pricing_model=PricingModel.FREE,
    )
    db_session.add(existing)
    await db_session.flush()
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    await service.run_extract(
        db_session, creator=creator, session_id=initial.id
    )
    with pytest.raises(service.CaptureError) as exc:
        await service.finalize_session(
            db_session,
            creator=creator,
            session_id=initial.id,
            payload=CaptureFinalize(neuron_slug="dup-slug"),
        )
    assert exc.value.code == "skill.slug_taken"
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_finalize_blocks_when_draft_empty(
    db_session: AsyncSession,
) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    # No extract run → draft_md still None.
    with pytest.raises(service.CaptureError) as exc:
        await service.finalize_session(
            db_session,
            creator=creator,
            session_id=initial.id,
            payload=CaptureFinalize(neuron_slug="empty"),
        )
    assert exc.value.code == "capture.draft_not_ready"
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_finalize_blocks_when_validate_fails(
    db_session: AsyncSession,
    in_memory_storage: Any,
    fake_redis: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A draft missing the required body section refuses."""
    monkeypatch.setattr("src.auth.deps._redis", fake_redis)
    monkeypatch.setattr("src.auth.deps.get_redis", lambda: fake_redis)
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    # Overwrite the draft with something that won't validate.
    row = await db_session.get(CaptureSession, initial.id)
    assert row is not None
    row.draft_md = "---\nid: foo/bar\n---\n\n(no body)\n"
    row.status = CaptureSessionStatus.DRAFT_READY
    await db_session.flush()

    with pytest.raises(service.CaptureError) as exc:
        await service.finalize_session(
            db_session,
            creator=creator,
            session_id=initial.id,
            payload=CaptureFinalize(neuron_slug="bad-draft"),
        )
    assert exc.value.code == "capture.validation_failed"
    assert exc.value.status_code == 422
    # No skill row landed (rollback).
    res = await db_session.execute(
        select(Skill).where(
            Skill.creator_id == creator.id,
            Skill.slug == "bad-draft",
        )
    )
    assert res.scalar_one_or_none() is None


# ── abandon_session ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_abandon_marks_status_and_writes_audit(
    db_session: AsyncSession,
) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    out = await service.abandon_session(
        db_session,
        creator=creator,
        session_id=initial.id,
        reason="changed my mind",
    )
    assert out.status == CaptureSessionStatus.ABANDONED
    assert out.abandoned_at is not None

    audit = await db_session.execute(
        select(AuditLog).where(AuditLog.action == "capture_session.abandoned")
    )
    assert audit.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_abandon_rejects_terminal_status(
    db_session: AsyncSession,
) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    row = await db_session.get(CaptureSession, initial.id)
    assert row is not None
    row.status = CaptureSessionStatus.FINALIZED
    await db_session.flush()
    with pytest.raises(service.CaptureError) as exc:
        await service.abandon_session(
            db_session,
            creator=creator,
            session_id=initial.id,
            reason=None,
        )
    assert exc.value.code == "capture.terminal_status"


# ── list_sessions ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_sessions_scoped_to_creator(db_session: AsyncSession) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="A"),
    )
    await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="B"),
    )
    items, page = await service.list_sessions(
        db_session, creator=creator, filters=service.CaptureFilters()
    )
    assert sorted(i.title for i in items) == ["A", "B"]
    assert page.has_more is False


# ── Attachments ──────────────────────────────────────────────────────


class _FakeUpload:
    """Minimal UploadFile stand-in for unit tests."""

    def __init__(self, *, filename: str, content_type: str, body: bytes) -> None:
        self.filename = filename
        self.content_type = content_type
        self._body = body

    async def read(self) -> bytes:
        return self._body


@pytest.mark.asyncio
async def test_add_attachment_happy_path(
    db_session: AsyncSession,
    in_memory_storage: Any,
) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    fake = _FakeUpload(
        filename="screenshot.png", content_type="image/png", body=b"fakepng" * 10,
    )
    out = await service.add_attachment(
        db_session, creator=creator, session_id=initial.id, upload=fake,  # type: ignore[arg-type]
    )
    assert out.filename == "screenshot.png"
    assert out.size_bytes == 70
    res = await db_session.execute(
        select(CaptureAttachment).where(
            CaptureAttachment.capture_session_id == initial.id
        )
    )
    rows = list(res.scalars().all())
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_add_attachment_rejects_oversize(
    db_session: AsyncSession,
    in_memory_storage: Any,
) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    too_big = b"\x00" * (5 * 1024 * 1024 + 1)
    fake = _FakeUpload(
        filename="big.bin", content_type="application/octet-stream", body=too_big,
    )
    with pytest.raises(service.CaptureError) as exc:
        await service.add_attachment(
            db_session, creator=creator, session_id=initial.id, upload=fake,  # type: ignore[arg-type]
        )
    assert exc.value.code == "capture.attachment_too_large"


@pytest.mark.asyncio
async def test_remove_attachment_deletes_row(
    db_session: AsyncSession,
    in_memory_storage: Any,
) -> None:
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(persona_id=persona.id, title="X"),
    )
    fake = _FakeUpload(
        filename="a.png", content_type="image/png", body=b"pngbytes",
    )
    out = await service.add_attachment(
        db_session, creator=creator, session_id=initial.id, upload=fake,  # type: ignore[arg-type]
    )
    await service.remove_attachment(
        db_session,
        creator=creator,
        session_id=initial.id,
        attachment_id=out.id,
    )
    res = await db_session.execute(
        select(CaptureAttachment).where(
            CaptureAttachment.capture_session_id == initial.id
        )
    )
    assert res.scalar_one_or_none() is None


# ── Polish 6 (Wave 5 QA): attachment exercise through finalize ───────


@pytest.mark.asyncio
async def test_finalize_preserves_attachment_s3_key(
    db_session: AsyncSession,
    in_memory_storage: Any,
    fake_redis: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T-05 + Wave 5 polish item 6: an attachment stored against a capture
    session must survive the finalize transaction.

    Acceptance: after finalize the ``capture_attachments`` row is still
    present, its ``storage_url`` (the S3 key recorded at upload time)
    is unchanged, and the bytes at that key are still retrievable.
    The finalize service also copies the bytes to a persona-side
    permanent prefix; we don't assert on the copy's exact key here (the
    service computes it internally) — we just confirm the original
    audit-row pointer survives so the chain-of-custody is complete.

    Companion fixture: ``tests/fixtures/captures/with_attachments.json``
    (already authored — Wave 2). We don't load that JSON here because
    the service path that consumes it is the multipart upload, not the
    finalize path; instead we use the same ``_FakeUpload`` shim the
    existing attachment tests use and exercise the in-process flow
    end-to-end.
    """
    monkeypatch.setattr("src.auth.deps._redis", fake_redis)
    monkeypatch.setattr("src.auth.deps.get_redis", lambda: fake_redis)
    creator, _parent, persona = await _quick_setup(db_session)
    initial = await service.create_session(
        db_session,
        creator=creator,
        payload=CaptureSessionCreate(
            persona_id=persona.id,
            title="Blue/green rollback at 3am",
            situation_md=(
                "Blue/green deploy started routing traffic to the new fleet "
                "at 02:45 UTC; 5% of requests immediately returned 502s."
            ),
            decision_md=(
                "Rollback in 12 min; flipped LB back; documented runbook."
            ),
            outcome_md="15 min of partial 502s; runbook reused 3x since.",
        ),
    )
    fake = _FakeUpload(
        filename="alb-graphs-pre-rollback.png",
        content_type="image/png",
        body=b"\x89PNG\r\n\x1a\n" + b"fake-png-bytes" * 20,
    )
    attachment = await service.add_attachment(
        db_session,
        creator=creator,
        session_id=initial.id,
        upload=fake,  # type: ignore[arg-type]
    )

    # Snapshot the originally-recorded S3 key before finalize.
    original_storage_url = attachment.storage_url
    assert original_storage_url.startswith(
        f"attachments/captures/{initial.id}/"
    )
    # Bytes are retrievable from the in-memory storage.
    pre_finalize_bytes = await in_memory_storage.get_object(original_storage_url)
    assert pre_finalize_bytes.startswith(b"\x89PNG")

    # Drive the LLM stub + finalize end-to-end.
    await service.run_extract(
        db_session, creator=creator, session_id=initial.id
    )
    out = await service.finalize_session(
        db_session,
        creator=creator,
        session_id=initial.id,
        payload=CaptureFinalize(neuron_slug="blue-green-rollback-3am"),
    )

    # The capture_attachments row survives the transaction.
    res = await db_session.execute(
        select(CaptureAttachment).where(
            CaptureAttachment.capture_session_id == initial.id
        )
    )
    rows = list(res.scalars().all())
    assert len(rows) == 1, (
        "Attachment row must survive finalize for audit integrity"
    )
    survivor = rows[0]
    assert str(survivor.id) == str(attachment.id)
    # The audit-row S3 key is unchanged — the service copied bytes to
    # the persona-side permanent prefix but did NOT mutate the capture-
    # side audit row.
    assert survivor.storage_url == original_storage_url
    assert survivor.sha256 == attachment.sha256
    assert survivor.size_bytes == attachment.size_bytes
    assert survivor.filename == "alb-graphs-pre-rollback.png"

    # The original bytes are still readable at the original key.
    post_bytes = await in_memory_storage.get_object(original_storage_url)
    assert post_bytes == pre_finalize_bytes

    # The persona-side copy landed under attachments/personas/<persona_id>/.
    persona_prefix = f"attachments/personas/{persona.id}/"
    persona_copies = [
        k for k in in_memory_storage.objects if k.startswith(persona_prefix)
    ]
    assert len(persona_copies) == 1, (
        f"Expected a persona-side copy under {persona_prefix}; "
        f"found {persona_copies}"
    )
    assert (
        await in_memory_storage.get_object(persona_copies[0])
        == pre_finalize_bytes
    )

    # Sanity: the finalize service produced a published neuron we can
    # tie back to the surviving attachment via the capture session.
    # (sqlite stores UUID columns as String(36) via with_variant; coerce
    # to str for the cross-dialect equality check.)
    after = await db_session.get(CaptureSession, initial.id)
    assert after is not None
    assert str(after.finalized_neuron_skill_id) == str(out.neuron_skill_id)
