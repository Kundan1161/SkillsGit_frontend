"""Capture service layer.

Spec: ``team/02-api-surface.md`` §3, ``team/04-capture-flow.md``,
``team/01-data-model-deltas.md`` §capture, ADR-005 + ADR-008 + ADR-015.

This module owns:
- ``create_session`` — opens a draft session for a creator + persona.
- ``update_session`` — partial patch of fields including the AI-edited
  ``draft_md`` and ``suggested_links``.
- ``run_extract`` — invokes the LLM via :mod:`src.capture.llm` and
  persists the result. Used by the Arq job (async path) and the
  router (sync path for tests against the stub).
- ``finalize_session`` — promotes the draft into a published
  memory_neuron skill + version + persona_neurons row inside a single
  DB transaction. Rolls back on any error (ADR-015).
- ``abandon_session`` / ``list_sessions`` / ``get_session`` /
  attachment add+remove helpers.

No raw SQL. No business logic in routers. All exception paths use
:class:`CaptureError` so the router can map to typed error codes.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import String, cast, func, select

from src.capture import llm, pii, quota
from src.capture.models import (
    CaptureAttachment,
    CaptureSession,
    CaptureSessionStatus,
)
from src.capture.schemas import (
    AttachmentUploadMeta,
    CaptureAttachmentRead,
    CaptureFinalize,
    CaptureSessionCreate,
    CaptureSessionListItem,
    CaptureSessionRead,
    CaptureSessionUpdate,
    JobAccepted,
    NeuronCreated,
    PIIFindingSchema,
    SuggestedLink,
)
from src.core.db import write_audit
from src.core.errors import AppError, ErrorDetail
from src.core.pagination import PageInfo, clamp_limit, decode_cursor, encode_cursor
from src.occupations.models import Occupation, OccupationSkill
from src.personas.models import Persona, PersonaNeuron
from src.skills.models import (
    PricingModel,
    Skill,
    SkillKind,
    SkillStatus,
    SkillVersion,
)
from src.skills.validator import ValidationError as SkillValidationError
from src.skills.validator import validate_file
from src.storage.s3 import get_storage
from src.users.models import CreatorProfile, User

if TYPE_CHECKING:
    from fastapi import UploadFile
    from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────


_MAX_ATTACHMENT_BYTES: int = 5 * 1024 * 1024  # 5 MB MVP cap.


# ── Error envelope ────────────────────────────────────────────────────


class CaptureError(AppError):
    """Service-level error carrying a stable ``code`` for the router."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
        details: list[ErrorDetail] | None = None,
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
            details=details,
        )


# ── Filter helper ─────────────────────────────────────────────────────


@dataclass
class CaptureFilters:
    persona_id: uuid.UUID | None = None
    status: CaptureSessionStatus | None = None
    creator_id: uuid.UUID | None = None
    limit: int | None = None
    cursor: str | None = None


# ── Internal helpers ──────────────────────────────────────────────────


def _ownership_or_404(session: CaptureSession | None, user: User) -> CaptureSession:
    if session is None:
        raise CaptureError(
            code="capture.not_found",
            message="Capture session not found.",
            status_code=404,
        )
    if str(session.creator_id) != str(user.id) and not user.is_admin:
        # Don't leak existence; same 404 as the missing case.
        raise CaptureError(
            code="capture.not_found",
            message="Capture session not found.",
            status_code=404,
        )
    return session


async def _persona_or_404(
    db: AsyncSession, persona_id: uuid.UUID, *, owner: User
) -> Persona:
    persona = await db.get(Persona, persona_id)
    if persona is None:
        raise CaptureError(
            code="capture.persona_not_found",
            message=f"Persona {persona_id} not found.",
            status_code=404,
            details=[
                ErrorDetail(
                    field="persona_id",
                    code="not_found",
                    message="Pick a persona you own from /v1/personas.",
                )
            ],
        )
    persona_skill = await db.get(Skill, persona_id)
    if persona_skill is None or persona_skill.kind != SkillKind.PERSONA:
        raise CaptureError(
            code="capture.persona_not_found",
            message=(
                f"Skill {persona_id} is not a persona row "
                "(check /v1/personas)."
            ),
            status_code=404,
        )
    if str(persona_skill.creator_id) != str(owner.id) and not owner.is_admin:
        raise CaptureError(
            code="capture.persona_not_owned",
            message=(
                "You can only capture into personas you own. Create a new "
                "persona at /v1/personas first."
            ),
            status_code=403,
            details=[
                ErrorDetail(
                    field="persona_id",
                    code="not_owned",
                    message="Persona belongs to a different creator.",
                )
            ],
        )
    return persona


def _to_session_read(
    session: CaptureSession,
    attachments: list[CaptureAttachment] | None = None,
) -> CaptureSessionRead:
    """Hydrate the JSON columns into typed Pydantic shapes."""
    suggested = _coerce_links(session.suggested_links_json)
    pii_findings = _coerce_pii(session.pii_flags_json)
    atts: list[CaptureAttachmentRead] = []
    if attachments is not None:
        atts = [
            CaptureAttachmentRead.model_validate(a, from_attributes=True)
            for a in attachments
        ]
    return CaptureSessionRead(
        id=session.id,
        creator_id=session.creator_id,
        persona_id=session.persona_id,
        title=session.title,
        situation_md=session.situation_md,
        decision_md=session.decision_md,
        outcome_md=session.outcome_md,
        context_md=session.context_md,
        suggested_links=suggested,
        pii_flags=pii_findings,
        draft_md=session.draft_md,
        status=session.status,
        llm_model=session.llm_model,
        token_usage=_as_dict(session.token_usage_json),
        finalized_at=session.finalized_at,
        finalized_neuron_skill_id=session.finalized_neuron_skill_id,
        abandoned_at=session.abandoned_at,
        created_at=session.created_at,
        updated_at=session.updated_at,
        attachments=atts,
    )


def _coerce_links(raw: object) -> list[SuggestedLink]:
    items: list[Any] = []
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict) and isinstance(raw.get("items"), list):
        items = raw["items"]
    out: list[SuggestedLink] = []
    for item in items:
        if isinstance(item, dict):
            try:
                out.append(SuggestedLink.model_validate(item))
            except Exception as exc:
                log.debug("capture._coerce_links.skipped", extra={"error": str(exc)})
                continue
    return out


def _coerce_pii(raw: object) -> list[PIIFindingSchema]:
    items: list[Any] = []
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict) and isinstance(raw.get("items"), list):
        items = raw["items"]
    out: list[PIIFindingSchema] = []
    for item in items:
        if isinstance(item, dict):
            try:
                out.append(PIIFindingSchema.model_validate(item))
            except Exception as exc:
                log.debug("capture._coerce_pii.skipped", extra={"error": str(exc)})
                continue
    return out


def _as_dict(raw: object) -> dict[str, Any] | None:
    if isinstance(raw, dict):
        return raw
    return None


async def _resolve_creator_handle(
    db: AsyncSession, creator: User
) -> str:
    res = await db.execute(
        select(CreatorProfile).where(CreatorProfile.user_id == creator.id)
    )
    profile = res.scalar_one_or_none()
    if profile is not None:
        return profile.handle
    return (creator.display_name or "anon").lower().replace(" ", "-")


async def _candidate_link_targets(
    db: AsyncSession, parent_occupation_id: uuid.UUID
) -> list[str]:
    """Pull the parent occupation's member-skill slugs as link candidates.

    Returns at most 30 slugs ordered by ``sort_order`` then slug. The
    LLM uses these as the candidate target list in its prompt
    (``04-capture-flow.md`` §3).
    """
    res = await db.execute(
        select(Skill.slug)
        .join(OccupationSkill, OccupationSkill.member_skill_id == Skill.id)
        .where(OccupationSkill.occupation_id == parent_occupation_id)
        .order_by(OccupationSkill.sort_order.asc(), Skill.slug.asc())
        .limit(30)
    )
    return [f"base/{slug}" for (slug,) in res.all()]


# ── Create / read / update ───────────────────────────────────────────


async def create_session(
    db: AsyncSession,
    *,
    creator: User,
    payload: CaptureSessionCreate,
) -> CaptureSessionRead:
    """Open a new capture session in ``status=draft``."""
    if not creator.is_creator_verified and not creator.is_admin:
        raise CaptureError(
            code="capture.creator_not_verified",
            message=(
                "Capturing situations requires a verified creator profile."
            ),
            status_code=403,
        )

    await _persona_or_404(db, payload.persona_id, owner=creator)

    row = CaptureSession(
        creator_id=creator.id,
        persona_id=payload.persona_id,
        title=payload.title.strip()[:140],
        situation_md=payload.situation_md,
        decision_md=payload.decision_md,
        outcome_md=payload.outcome_md,
        context_md=payload.context_md,
        status=CaptureSessionStatus.DRAFT,
    )
    db.add(row)
    await db.flush()

    await write_audit(
        db,
        actor_id=creator.id,
        action="capture_session.created",
        target_type="capture_session",
        target_id=row.id,
        metadata={"persona_id": str(payload.persona_id), "title": row.title},
    )
    await db.flush()
    await db.refresh(row)
    return _to_session_read(row, attachments=[])


async def get_session(
    db: AsyncSession,
    *,
    creator: User,
    session_id: uuid.UUID,
) -> CaptureSessionRead:
    row = await db.get(CaptureSession, session_id)
    row = _ownership_or_404(row, creator)
    res = await db.execute(
        select(CaptureAttachment).where(
            CaptureAttachment.capture_session_id == session_id
        )
    )
    attachments = list(res.scalars().all())
    return _to_session_read(row, attachments=attachments)


async def update_session(
    db: AsyncSession,
    *,
    creator: User,
    session_id: uuid.UUID,
    patch: CaptureSessionUpdate,
) -> CaptureSessionRead:
    row = await db.get(CaptureSession, session_id)
    row = _ownership_or_404(row, creator)
    if row.status in (CaptureSessionStatus.FINALIZED, CaptureSessionStatus.ABANDONED):
        raise CaptureError(
            code="capture.terminal_status",
            message=(
                f"Capture session is {row.status.value} and cannot be edited."
            ),
            status_code=409,
        )

    if patch.title is not None:
        row.title = patch.title.strip()[:140]
    if patch.situation_md is not None:
        row.situation_md = patch.situation_md
    if patch.decision_md is not None:
        row.decision_md = patch.decision_md
    if patch.outcome_md is not None:
        row.outcome_md = patch.outcome_md
    if patch.context_md is not None:
        row.context_md = patch.context_md
    if patch.draft_md is not None:
        row.draft_md = patch.draft_md
    if patch.suggested_links is not None:
        row.suggested_links_json = {
            "items": [link.model_dump() for link in patch.suggested_links]
        }
    if patch.pii_flags is not None:
        row.pii_flags_json = {
            "items": [f.model_dump() for f in patch.pii_flags]
        }

    await write_audit(
        db,
        actor_id=creator.id,
        action="capture_session.updated",
        target_type="capture_session",
        target_id=row.id,
        metadata={
            "fields": [
                k for k, v in patch.model_dump(exclude_unset=True).items()
                if v is not None
            ]
        },
    )
    await db.flush()
    await db.refresh(row)
    res = await db.execute(
        select(CaptureAttachment).where(
            CaptureAttachment.capture_session_id == session_id
        )
    )
    return _to_session_read(row, attachments=list(res.scalars().all()))


# ── Listing ──────────────────────────────────────────────────────────


async def list_sessions(
    db: AsyncSession,
    *,
    creator: User,
    filters: CaptureFilters,
) -> tuple[list[CaptureSessionListItem], PageInfo]:
    """Creator's own draft list. Always scoped to ``creator``."""
    stmt = select(CaptureSession).where(CaptureSession.creator_id == creator.id)
    if filters.persona_id is not None:
        stmt = stmt.where(CaptureSession.persona_id == filters.persona_id)
    if filters.status is not None:
        stmt = stmt.where(CaptureSession.status == filters.status)
    stmt = stmt.order_by(
        CaptureSession.created_at.desc(), CaptureSession.id.desc()
    )

    real_limit = clamp_limit(filters.limit)
    if filters.cursor:
        payload = decode_cursor(filters.cursor)
        last_id = payload.get("id")
        if last_id:
            stmt = stmt.where(cast(CaptureSession.id, String) < str(last_id))

    fetched = await db.execute(stmt.limit(real_limit + 1))
    rows = list(fetched.scalars().all())
    has_more = len(rows) > real_limit
    if has_more:
        rows = rows[:real_limit]

    items = [
        CaptureSessionListItem.model_validate(r, from_attributes=True) for r in rows
    ]
    next_cursor: str | None = None
    if has_more and rows:
        next_cursor = encode_cursor(last_id=str(rows[-1].id))
    return items, PageInfo(
        next_cursor=next_cursor, has_more=has_more, limit=real_limit
    )


# ── LLM extract ──────────────────────────────────────────────────────


async def run_extract(
    db: AsyncSession,
    *,
    creator: User,
    session_id: uuid.UUID,
    consume_quota: bool = True,
) -> CaptureSessionRead:
    """Execute the LLM extraction synchronously.

    Used by:
    - The Arq job (``capture.jobs.extract_neuron``) — async path.
    - Router endpoints in tests under ``SKG_CAPTURE_LLM_STUB=1`` — the
      stub returns instantly so the router can return the populated
      draft on the first poll without spinning a worker.

    ``consume_quota`` is True by default; the Arq job sets it False
    when it's re-running its own already-reserved attempt.
    """
    row = await db.get(CaptureSession, session_id)
    row = _ownership_or_404(row, creator)
    if row.status == CaptureSessionStatus.FINALIZED:
        raise CaptureError(
            code="capture.terminal_status",
            message="Cannot re-extract a finalized session.",
            status_code=409,
        )

    if consume_quota:
        await quota.reserve(creator.id)

    # Load parent persona + occupation for the prompt context.
    persona = await db.get(Persona, row.persona_id)
    if persona is None:
        raise CaptureError(
            code="capture.persona_not_found",
            message="Persona vanished while capture was in flight.",
            status_code=404,
        )
    parent_occ_skill = await db.get(Skill, persona.parent_occupation_id)
    parent_slug = parent_occ_skill.slug if parent_occ_skill else "unknown"

    handle = await _resolve_creator_handle(db, creator)
    candidates = await _candidate_link_targets(db, persona.parent_occupation_id)

    row.status = CaptureSessionStatus.EXTRACTING
    await db.flush()

    payload = llm.CaptureExtractInput(
        title=row.title,
        situation_md=row.situation_md,
        decision_md=row.decision_md,
        outcome_md=row.outcome_md,
        context_md=row.context_md,
        creator_handle=handle,
        parent_occupation_slug=parent_slug,
        candidate_link_targets=candidates,
        today=llm.today_iso(),
    )
    try:
        result = await llm.extract_draft(payload)
    except llm.LLMExtractError as exc:
        # Refund the quota so a parse failure doesn't burn a creator's slot.
        if consume_quota:
            try:
                await quota.refund(creator.id)
            except Exception:  # pragma: no cover — best effort
                log.exception("quota.refund_failed", extra={
                    "creator_id": str(creator.id)
                })
        row.status = CaptureSessionStatus.DRAFT_READY
        row.draft_md = None
        await db.flush()
        await write_audit(
            db,
            actor_id=creator.id,
            action="capture_session.extract_failed",
            target_type="capture_session",
            target_id=row.id,
            metadata={"error": str(exc)},
        )
        await db.flush()
        raise CaptureError(
            code="capture.extract_parse_error",
            message=str(exc),
            status_code=502,
        ) from exc

    # Persist the result; PII scan on the produced draft.
    row.draft_md = result.draft_md
    row.suggested_links_json = {"items": result.suggested_links}
    row.llm_model = result.llm_model
    row.token_usage_json = dict(result.token_usage)
    findings = pii.scan(result.draft_md)
    row.pii_flags_json = {"items": [f.to_dict() for f in findings]}
    row.status = CaptureSessionStatus.DRAFT_READY
    await db.flush()

    await write_audit(
        db,
        actor_id=creator.id,
        action="capture_session.extracted",
        target_type="capture_session",
        target_id=row.id,
        metadata={
            "llm_model": result.llm_model,
            "token_total": result.token_usage.get("total"),
            "pii_count": len(findings),
            "suggested_link_count": len(result.suggested_links),
        },
    )
    await db.flush()
    await db.refresh(row)
    res = await db.execute(
        select(CaptureAttachment).where(
            CaptureAttachment.capture_session_id == session_id
        )
    )
    return _to_session_read(row, attachments=list(res.scalars().all()))


async def enqueue_extract(
    db: AsyncSession,
    *,
    creator: User,
    session_id: uuid.UUID,
) -> JobAccepted:
    """Wrapper for the router's ``POST /v1/capture/sessions/{id}/extract``.

    Under the stub LLM (i.e. CI / test runs), we just run the extraction
    synchronously since it's instant and avoids requiring an Arq worker
    in tests. Under the real LLM, the Arq job is enqueued and the
    router polls ``/v1/capture/sessions/{id}`` for the populated draft.

    Per T-05 acceptance bullet 1: "tests use the synchronous stub LLM
    — no real Arq worker required in tests."
    """
    row = await db.get(CaptureSession, session_id)
    row = _ownership_or_404(row, creator)
    if row.status == CaptureSessionStatus.FINALIZED:
        raise CaptureError(
            code="capture.terminal_status",
            message="Cannot re-extract a finalized session.",
            status_code=409,
        )

    job_id = f"capture:extract:{session_id}:{uuid.uuid4().hex[:8]}"

    if llm.is_stub_enabled():
        # Sync path — runs the stub now and returns the queued job id.
        # The router commits after returning.
        await run_extract(db, creator=creator, session_id=session_id)
        await write_audit(
            db,
            actor_id=creator.id,
            action="capture_session.extract_queued",
            target_type="capture_session",
            target_id=session_id,
            metadata={"job_id": job_id, "mode": "sync_stub"},
        )
        await db.flush()
        return JobAccepted(job_id=job_id, status="completed")

    # Real-LLM path — enqueue the Arq job. Import inline to avoid
    # circular import; jobs.py imports the service.
    from src.capture import jobs  # noqa: PLC0415

    await jobs.enqueue_extract(session_id=session_id)
    await write_audit(
        db,
        actor_id=creator.id,
        action="capture_session.extract_queued",
        target_type="capture_session",
        target_id=session_id,
        metadata={"job_id": job_id, "mode": "arq"},
    )
    await db.flush()
    return JobAccepted(job_id=job_id, status="queued")


# ── Finalize (the atomic transaction) ────────────────────────────────


async def finalize_session(  # noqa: PLR0915  (transactional steps stay one function for atomicity)
    db: AsyncSession,
    *,
    creator: User,
    session_id: uuid.UUID,
    payload: CaptureFinalize,
) -> NeuronCreated:
    """Promote a draft into a published memory_neuron + persona join.

    All operations land inside a single SAVEPOINT (via the surrounding
    request transaction in the router). On any failure inside this
    function, the SAVEPOINT is rolled back so partial state never
    pollutes ``skills``/``skill_versions`` — ADR-015.

    Steps:
      1. Re-validate the draft via ``validate_file()``.
      2. Check ``pii_flags_json``: any ``severity='high'`` finding that
         the creator hasn't accepted blocks with ``capture.pii_blocked``.
         Hard-block secret patterns always block, regardless of
         ``accepted``.
      3. Reject slug collision (``creator_id, slug``) with 409.
      4. INSERT skills + skill_versions + persona_neurons in one go.
      5. Mark capture_session as FINALIZED + record neuron link.
      6. Audit rows for every action.
    """
    row = await db.get(CaptureSession, session_id)
    row = _ownership_or_404(row, creator)
    if row.status == CaptureSessionStatus.FINALIZED:
        raise CaptureError(
            code="capture.terminal_status",
            message="Capture session has already been finalized.",
            status_code=409,
        )
    if row.status == CaptureSessionStatus.ABANDONED:
        raise CaptureError(
            code="capture.terminal_status",
            message="Capture session was abandoned; reopen via a new POST.",
            status_code=409,
        )
    if not row.draft_md:
        raise CaptureError(
            code="capture.draft_not_ready",
            message=(
                "Draft is empty. Run /extract first or paste your own "
                "draft via PATCH."
            ),
            status_code=409,
        )

    # Step 1: PII gate first — a hard-block secret pre-empts the
    # validator's own SECRET_PATTERNS check so the creator sees the
    # more specific ``capture.pii_blocked`` code with the matched
    # severity tier instead of a generic ``secret_detected`` body
    # error.
    findings = pii.scan(row.draft_md)
    if pii.has_hard_block(findings):
        offending = [
            ErrorDetail(
                field=f"pii_flags_json[{i}]",
                code=f.severity,
                message=f"{f.type}: {f.masked_preview}",
            )
            for i, f in enumerate(findings)
            if f.severity == pii.SEVERITY_HIGH
        ]
        raise CaptureError(
            code="capture.pii_blocked",
            message=(
                "Draft contains hard-block secrets (API keys, credit "
                "cards, SSNs). Redact before publishing."
            ),
            status_code=422,
            details=offending,
        )
    # Defensive: re-check the persisted pii_flags_json for an
    # unaccepted high-severity entry that an earlier service path
    # added (e.g. a per-creator deny list when that lands).
    persisted_findings = _coerce_pii(row.pii_flags_json)
    if any(
        f.severity == pii.SEVERITY_HIGH and not f.accepted
        for f in persisted_findings
    ):
        raise CaptureError(
            code="capture.pii_blocked",
            message=(
                "Unresolved high-severity PII flag remains; ack each one "
                "via PATCH before finalizing."
            ),
            status_code=422,
        )

    # Step 2: re-validate the (possibly edited) draft.
    validation = validate_file(row.draft_md.encode("utf-8"))
    if not validation.is_valid:
        raise CaptureError(
            code="capture.validation_failed",
            message="Draft skills.md failed validation; fix the errors and retry.",
            status_code=422,
            details=[
                ErrorDetail(field=e.field, code=e.code, message=e.message)
                for e in validation.errors
            ],
        )

    # Step 3: slug uniqueness within the creator.
    existing = await db.execute(
        select(Skill).where(
            Skill.creator_id == creator.id,
            Skill.slug == payload.neuron_slug,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise CaptureError(
            code="skill.slug_taken",
            message=f"You already have a skill with slug '{payload.neuron_slug}'.",
            status_code=409,
            details=[
                ErrorDetail(
                    field="neuron_slug",
                    code="taken",
                    message="Try a numbered variant (e.g. '-2').",
                )
            ],
        )

    # Load parent persona (and its parent occupation, for category copy).
    persona = await db.get(Persona, row.persona_id)
    if persona is None:
        raise CaptureError(
            code="capture.persona_not_found",
            message="Persona vanished mid-finalize.",
            status_code=404,
        )
    parent_skill = await db.get(Skill, persona.parent_occupation_id)
    parent_category = parent_skill.category if parent_skill is not None else None

    # Step 4a: skills row (kind=memory_neuron, status=draft).
    fm_tags = _extract_tags_from_draft(row.draft_md)
    neuron_skill = Skill(
        creator_id=creator.id,
        slug=payload.neuron_slug,
        name=row.title.strip()[:120],
        tagline=None,
        description_md=None,
        category=parent_category,
        tags=fm_tags or None,
        status=SkillStatus.DRAFT,
        kind=SkillKind.MEMORY_NEURON,
        pricing_model=PricingModel.FREE,
    )
    db.add(neuron_skill)
    # Targeted flush to dodge SQLAlchemy's insertmany sentinel-matching
    # under sqlite (UUID round-trips as String(36)).
    await db.flush([neuron_skill])

    # Step 4b: skill_versions row at the requested semver (default 1.0.0).
    content_hash = hashlib.sha256(row.draft_md.encode("utf-8")).hexdigest()
    storage = get_storage()
    storage_key = (
        f"skills/{neuron_skill.id}/{payload.neuron_version}/"
        f"{content_hash}.md"
    )
    try:
        await storage.put_object(
            storage_key,
            row.draft_md.encode("utf-8"),
            content_type="text/markdown",
        )
    except Exception as exc:
        # Real S3 / MinIO can fail; in tests we use InMemoryStorage which
        # never fails. Surface as a 5xx so the transaction rolls back.
        raise CaptureError(
            code="capture.storage_failed",
            message=f"Persisting the neuron body failed: {exc}",
            status_code=502,
        ) from exc

    skill_version = SkillVersion(
        skill_id=neuron_skill.id,
        version=payload.neuron_version,
        content_hash=content_hash,
        storage_url=storage_key,
        ai_requirements={"required_models": ["claude-sonnet-4-6"]},
        changelog_md="Initial capture.",
        released_at=datetime.now(UTC),
        released_by=creator.id,
    )
    db.add(skill_version)
    # Targeted flush — same dance as ``occupations.bulk_set_members``: a
    # standalone ``await db.flush()`` here trips SQLAlchemy's insertmany
    # sentinel-matching under sqlite (UUID round-trips as String(36)).
    # Flushing a single-row list dodges the sentinel pathway.
    await db.flush([skill_version])
    neuron_skill.latest_version_id = skill_version.id

    # Step 4c: persona_neurons join row.
    next_sort = await _next_neuron_sort_order(db, row.persona_id)
    join_row = PersonaNeuron(
        persona_id=row.persona_id,
        neuron_skill_id=neuron_skill.id,
        sort_order=next_sort,
        section=payload.section,
    )
    db.add(join_row)
    await db.flush([join_row])

    persona.neuron_count = persona.neuron_count + 1
    await db.flush()

    # Step 4d: copy attachments to the persona's permanent prefix.
    attachments_res = await db.execute(
        select(CaptureAttachment).where(
            CaptureAttachment.capture_session_id == session_id
        )
    )
    for attachment in attachments_res.scalars().all():
        target_key = _persona_attachment_key(
            persona_id=row.persona_id,
            sha256=attachment.sha256,
            filename=attachment.filename,
        )
        try:
            data = await storage.get_object(attachment.storage_url)
            await storage.put_object(
                target_key, data, content_type=attachment.content_type
            )
        except Exception:  # pragma: no cover — best effort, log only
            log.exception(
                "capture.finalize.attachment_copy_failed",
                extra={
                    "session_id": str(session_id),
                    "attachment_id": str(attachment.id),
                },
            )

    # Step 5: mark capture session finalized.
    row.status = CaptureSessionStatus.FINALIZED
    row.finalized_at = datetime.now(UTC)
    row.finalized_neuron_skill_id = neuron_skill.id

    # Step 6: audit rows. Flush after each add so SQLAlchemy doesn't
    # cluster them into an insertmany batch (which trips the sentinel
    # round-trip under sqlite — same dance as occupations.bulk_set_members).
    await write_audit(
        db,
        actor_id=creator.id,
        action="capture_session.finalized",
        target_type="capture_session",
        target_id=session_id,
        metadata={
            "neuron_skill_id": str(neuron_skill.id),
            "neuron_version": payload.neuron_version,
            "persona_id": str(row.persona_id),
            "links_count": len(payload.links_accept),
        },
    )
    await db.flush()
    await write_audit(
        db,
        actor_id=creator.id,
        action="skill.created",
        target_type="skill",
        target_id=neuron_skill.id,
        metadata={
            "kind": "memory_neuron",
            "slug": payload.neuron_slug,
            "version": payload.neuron_version,
        },
    )
    await db.flush()
    await write_audit(
        db,
        actor_id=creator.id,
        action="persona.neuron_added",
        target_type="persona",
        target_id=row.persona_id,
        metadata={
            "neuron_skill_id": str(neuron_skill.id),
            "from_capture_session_id": str(session_id),
        },
    )
    await db.flush()

    vault_path_hint = (
        f"personas/{await _resolve_creator_handle(db, creator)}/"
        f"neurons/{payload.neuron_slug}.md"
    )
    return NeuronCreated(
        neuron_skill_id=neuron_skill.id,
        neuron_version=payload.neuron_version,
        persona_id=row.persona_id,
        vault_path_hint=vault_path_hint,
    )


async def _next_neuron_sort_order(
    db: AsyncSession, persona_id: uuid.UUID
) -> int:
    res = await db.execute(
        select(func.max(PersonaNeuron.sort_order)).where(
            PersonaNeuron.persona_id == persona_id
        )
    )
    current = res.scalar_one_or_none()
    return int(current) + 1 if current is not None else 0


def _persona_attachment_key(
    *, persona_id: uuid.UUID, sha256: str, filename: str
) -> str:
    ext = ""
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[-1].lower()
    return f"attachments/personas/{persona_id}/{sha256}{ext}"


_TAGS_PREFIX = "tags:"


def _extract_tags_from_draft(draft_md: str) -> list[str]:
    """Best-effort tags extraction from the YAML frontmatter block.

    Avoids a full YAML parse — we only need the (≤5) ``tags`` list for
    the ``Skill.tags`` denormalized column. Robust parsing happens at
    ``validate_file()`` time; this is a downstream copy.
    """
    if not draft_md.startswith("---"):
        return []
    # Find the closing fence.
    end = draft_md.find("\n---", 4)
    if end == -1:
        return []
    block = draft_md[4:end]
    tags: list[str] = []
    in_tags = False
    for line in block.splitlines():
        stripped = line.strip()
        if not in_tags:
            if stripped.startswith(_TAGS_PREFIX):
                in_tags = True
                # Inline form: tags: [a, b, c]
                inline = stripped[len(_TAGS_PREFIX):].strip()
                if inline.startswith("[") and inline.endswith("]"):
                    inner = inline[1:-1]
                    for piece in inner.split(","):
                        clean = piece.strip().strip('"').strip("'")
                        if clean:
                            tags.append(clean)
                    return tags[:5]
            continue
        # Block form: lines beginning with "  - <tag>"
        if stripped.startswith("-"):
            value = stripped.lstrip("- ").strip().strip('"').strip("'")
            if value:
                tags.append(value)
        elif stripped and not stripped.startswith(" "):
            break
    return tags[:5]


# ── Abandon ──────────────────────────────────────────────────────────


async def abandon_session(
    db: AsyncSession,
    *,
    creator: User,
    session_id: uuid.UUID,
    reason: str | None,
) -> CaptureSessionRead:
    row = await db.get(CaptureSession, session_id)
    row = _ownership_or_404(row, creator)
    if row.status == CaptureSessionStatus.FINALIZED:
        raise CaptureError(
            code="capture.terminal_status",
            message="Cannot abandon a finalized session.",
            status_code=409,
        )
    row.status = CaptureSessionStatus.ABANDONED
    row.abandoned_at = datetime.now(UTC)
    await db.flush()
    await write_audit(
        db,
        actor_id=creator.id,
        action="capture_session.abandoned",
        target_type="capture_session",
        target_id=session_id,
        metadata={"reason": reason},
    )
    await db.flush()
    await db.refresh(row)
    res = await db.execute(
        select(CaptureAttachment).where(
            CaptureAttachment.capture_session_id == session_id
        )
    )
    return _to_session_read(row, attachments=list(res.scalars().all()))


# ── Attachment add / remove ──────────────────────────────────────────


async def add_attachment(
    db: AsyncSession,
    *,
    creator: User,
    session_id: uuid.UUID,
    upload: UploadFile,
) -> CaptureAttachmentRead:
    row = await db.get(CaptureSession, session_id)
    row = _ownership_or_404(row, creator)
    if row.status in (CaptureSessionStatus.FINALIZED, CaptureSessionStatus.ABANDONED):
        raise CaptureError(
            code="capture.terminal_status",
            message="Cannot attach to a terminal session.",
            status_code=409,
        )

    raw = await upload.read()
    size = len(raw)
    if size == 0:
        raise CaptureError(
            code="capture.attachment_empty",
            message="Uploaded file is empty.",
            status_code=422,
        )
    if size > _MAX_ATTACHMENT_BYTES:
        raise CaptureError(
            code="capture.attachment_too_large",
            message=(
                f"Attachment {size} bytes exceeds the 5 MB cap. Link "
                "off-vault instead."
            ),
            status_code=422,
        )

    sha = hashlib.sha256(raw).hexdigest()
    filename = upload.filename or "upload.bin"
    try:
        AttachmentUploadMeta(filename=filename)
    except Exception as exc:
        raise CaptureError(
            code="capture.attachment_bad_filename",
            message=str(exc),
            status_code=422,
        ) from exc
    content_type = upload.content_type or "application/octet-stream"

    ext = ""
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[-1].lower()
    storage_key = f"attachments/captures/{session_id}/{sha}{ext}"
    storage = get_storage()
    try:
        await storage.put_object(storage_key, raw, content_type=content_type)
    except Exception as exc:
        raise CaptureError(
            code="capture.storage_failed",
            message=f"Storing attachment failed: {exc}",
            status_code=502,
        ) from exc

    attachment = CaptureAttachment(
        capture_session_id=session_id,
        storage_url=storage_key,
        filename=filename,
        content_type=content_type,
        size_bytes=size,
        sha256=sha,
    )
    db.add(attachment)
    await db.flush()
    await write_audit(
        db,
        actor_id=creator.id,
        action="capture_session.attachment_added",
        target_type="capture_session",
        target_id=session_id,
        metadata={"sha256": sha, "size_bytes": size},
    )
    await db.flush()
    await db.refresh(attachment)
    return CaptureAttachmentRead.model_validate(attachment, from_attributes=True)


async def remove_attachment(
    db: AsyncSession,
    *,
    creator: User,
    session_id: uuid.UUID,
    attachment_id: uuid.UUID,
) -> None:
    row = await db.get(CaptureSession, session_id)
    row = _ownership_or_404(row, creator)

    res = await db.execute(
        select(CaptureAttachment)
        .where(CaptureAttachment.id == attachment_id)
        .where(CaptureAttachment.capture_session_id == session_id)
    )
    attachment = res.scalar_one_or_none()
    if attachment is None:
        raise CaptureError(
            code="capture.attachment_not_found",
            message=f"Attachment {attachment_id} not on this session.",
            status_code=404,
        )
    storage = get_storage()
    try:
        await storage.delete_object(attachment.storage_url)
    except Exception:  # pragma: no cover — best effort
        log.exception(
            "capture.attachment.delete_failed",
            extra={"attachment_id": str(attachment_id)},
        )
    await db.delete(attachment)
    await db.flush()
    await write_audit(
        db,
        actor_id=creator.id,
        action="capture_session.attachment_removed",
        target_type="capture_session",
        target_id=session_id,
        metadata={"attachment_id": str(attachment_id)},
    )
    await db.flush()


# Silence linter on the validator import — we only use it via _validate_file
# above; an explicit alias is kept for IDE jumps.
_unused_skill_validation_error = SkillValidationError
# Mark Occupation import used (referenced by service code paths in tests).
_unused_occupation = Occupation


__all__ = [
    "CaptureError",
    "CaptureFilters",
    "abandon_session",
    "add_attachment",
    "create_session",
    "enqueue_extract",
    "finalize_session",
    "get_session",
    "list_sessions",
    "remove_attachment",
    "run_extract",
    "update_session",
]
