"""Occupation service layer.

Spec: ``team/02-api-surface.md`` §1, ``team/01-data-model-deltas.md``
§occupations, ADR-004.

A ``kind=occupation`` row is a thin specialisation of the existing
``skills`` row — every create/patch/publish writes the parent ``Skill``
row first and the ``occupations`` side-table row second in the same
transaction. Membership lives in ``occupation_skills`` and is rebuilt
atomically by the bulk endpoint.

No raw SQL. No business logic in routers. All exception paths use
:class:`OccupationError` so the router can map to typed error codes.
"""

from __future__ import annotations

import logging
import uuid  # noqa: TC003  (used at runtime via UUID args / Mapped[uuid.UUID])
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import String, cast, delete, func, literal, or_, select
from sqlalchemy.orm import selectinload

from src.core.db import write_audit
from src.core.errors import AppError, ErrorDetail
from src.core.pagination import PageInfo, clamp_limit, decode_cursor, encode_cursor
from src.occupations.models import Occupation, OccupationSkill
from src.occupations.schemas import (
    CreatorChip,
    GraphEdge,
    GraphNode,
    JobAccepted,
    OccupationCreate,
    OccupationDetailResponse,
    OccupationListItem,
    OccupationRead,
    OccupationSkillBulkItem,
    OccupationSkillGroup,
    OccupationSkillList,
    OccupationSkillRead,
    OccupationSkillUpsert,
    OccupationUpdate,
    VaultGraphPreview,
)
from src.skills.models import PricingModel, Skill, SkillKind, SkillStatus, SkillVersion
from src.skills.parser import split_frontmatter
from src.skills.validator import LinkRelation
from src.storage.s3 import get_storage
from src.users.models import CreatorProfile, User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


# ── Error envelope ────────────────────────────────────────────────────


class OccupationError(AppError):
    """Service-level error carrying a stable ``code`` for the router.

    Reuses :class:`src.core.errors.AppError` so the global FastAPI
    handler renders it via :class:`~src.core.errors.ErrorResponse`.
    """

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


# ── Listing filter helper ─────────────────────────────────────────────


@dataclass
class OccupationFilters:
    category: str | None = None
    domain: str | None = None
    q: str | None = None
    creator_handle: str | None = None
    order: str | None = None
    limit: int | None = None
    cursor: str | None = None
    include_non_public: bool = False
    creator_id: uuid.UUID | None = None


# ── Internal helpers ──────────────────────────────────────────────────


def _ownership_or_404(skill: Skill | None, user: User) -> Skill:
    if skill is None:
        raise OccupationError(
            code="occupation.not_found",
            message="Occupation not found.",
            status_code=404,
        )
    if skill.kind != SkillKind.OCCUPATION:
        # Don't leak the existence of a same-id non-occupation row.
        raise OccupationError(
            code="occupation.not_found",
            message="Occupation not found.",
            status_code=404,
        )
    # Cross-dialect: sqlite (tests) stores UUID as String(36), so a UUID
    # column compared to a UUID Python object can be string-vs-UUID. Cast
    # both sides to str for a dialect-agnostic check.
    if str(skill.creator_id) != str(user.id) and not user.is_admin:
        raise OccupationError(
            code="occupation.not_found",
            message="Occupation not found.",
            status_code=404,
        )
    return skill


def _to_list_item(
    skill: Skill,
    occupation: Occupation,
    user: User,
    profile: CreatorProfile | None,
    *,
    member_count: int,
) -> OccupationListItem:
    handle = profile.handle if profile is not None else (user.display_name or "anon")
    return OccupationListItem(
        id=skill.id,
        skill_id=skill.id,
        slug=skill.slug,
        name=skill.name,
        tagline=skill.tagline,
        summary_md=occupation.summary_md,
        description_md=skill.description_md,
        cover_image_url=skill.cover_image_url,
        category=skill.category,
        tags=list(skill.tags or []),
        domains=list(occupation.domains or []),
        kind=skill.kind,
        status=skill.status,
        pricing_model=skill.pricing_model,
        one_time_price_cents=skill.one_time_price_cents,
        subscription_price_cents=skill.subscription_price_cents,
        persona_count=occupation.persona_count,
        recommended_persona_count=occupation.recommended_persona_count,
        member_count=member_count,
        rating_avg=(
            float(skill.rating_avg) if skill.rating_avg is not None else None
        ),
        rating_count=skill.rating_count,
        total_sales=skill.total_sales,
        creator=CreatorChip(
            handle=handle,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            is_verified=user.is_creator_verified,
        ),
        latest_build_id=occupation.latest_build_id,
        created_at=skill.created_at,
        updated_at=skill.updated_at,
    )


def _to_skill_read(
    row: OccupationSkill,
    member_skill: Skill,
    member_profile: CreatorProfile | None,
    member_user: User | None,
) -> OccupationSkillRead:
    handle: str | None = None
    if member_profile is not None:
        handle = member_profile.handle
    elif member_user is not None and member_user.display_name:
        handle = member_user.display_name
    return OccupationSkillRead(
        id=row.id,
        occupation_id=row.occupation_id,
        member_skill_id=row.member_skill_id,
        member_slug=member_skill.slug,
        member_name=member_skill.name,
        member_tagline=member_skill.tagline,
        member_creator_handle=handle,
        domain=row.domain,
        role=row.role,
        sort_order=row.sort_order,
        pinned=row.pinned,
        notes_md=row.notes_md,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


async def _hydrate_member(
    session: AsyncSession, row: OccupationSkill
) -> OccupationSkillRead:
    # Force a refresh so server_default fields (created_at/updated_at) and
    # any pending expirations are loaded inside this async context — without
    # this, sqlite tests trip MissingGreenlet on a later attribute touch.
    await session.refresh(row)
    res = await session.execute(
        select(Skill, User, CreatorProfile)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .where(Skill.id == row.member_skill_id)
    )
    out = res.first()
    if out is None:  # pragma: no cover — FK guarantees this
        raise OccupationError(
            code="occupation.member_missing",
            message="Member skill row vanished during read.",
            status_code=500,
        )
    member_skill, member_user, member_profile = out
    return _to_skill_read(row, member_skill, member_profile, member_user)


def _validate_member_skill(
    member_skill: Skill | None,
    occupation: Occupation,
    domain: str | None,
) -> None:
    if member_skill is None:
        raise OccupationError(
            code="occupation.member_not_found",
            message="Member skill not found.",
            status_code=404,
        )
    if member_skill.kind != SkillKind.SKILL:
        raise OccupationError(
            code="occupation.invalid_member_kind",
            message=(
                f"Cannot add a {member_skill.kind.value} as an occupation "
                f"member; only kind='skill' rows are allowed."
            ),
            status_code=422,
            details=[
                ErrorDetail(
                    field="member_skill_id",
                    code="invalid_member_kind",
                    message=(
                        f"Skill id={member_skill.id} has kind="
                        f"{member_skill.kind.value}."
                    ),
                )
            ],
        )
    if domain is not None and (occupation.domains or []) and domain not in (
        occupation.domains or []
    ):
        raise OccupationError(
            code="occupation.domain_unknown",
            message=(
                f"Domain '{domain}' is not declared on this occupation. "
                f"Add it to the occupation's `domains` list first."
            ),
            status_code=422,
            details=[
                ErrorDetail(
                    field="domain",
                    code="domain_unknown",
                    message=f"Occupation domains: {list(occupation.domains or [])}.",
                )
            ],
        )


async def _refresh_member_count(
    session: AsyncSession, occupation_id: uuid.UUID
) -> int:
    res = await session.execute(
        select(func.count(OccupationSkill.id)).where(
            OccupationSkill.occupation_id == occupation_id
        )
    )
    return int(res.scalar() or 0)


async def _load_for_read(
    session: AsyncSession, skill_id: uuid.UUID
) -> tuple[Skill, Occupation, User, CreatorProfile | None] | None:
    res = await session.execute(
        select(Skill, Occupation, User, CreatorProfile)
        .join(Occupation, Occupation.skill_id == Skill.id)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .where(Skill.id == skill_id)
        .where(Skill.kind == SkillKind.OCCUPATION)
    )
    row = res.first()
    if row is None:
        return None
    return row[0], row[1], row[2], row[3]


# ── Creator-scoped operations ────────────────────────────────────────


async def create_occupation(
    session: AsyncSession,
    *,
    creator: User,
    payload: OccupationCreate,
) -> OccupationRead:
    """Create an occupation. Caller must be a verified creator (router-enforced)."""
    if not creator.is_creator_verified and not creator.is_admin:
        raise OccupationError(
            code="occupation.creator_not_verified",
            message=(
                "Publishing occupations requires a verified creator profile."
            ),
            status_code=403,
        )

    _validate_pricing(payload.pricing_model, payload.one_time_price_cents,
                      payload.subscription_price_cents)

    # Slug uniqueness within this creator.
    existing = await session.execute(
        select(Skill).where(
            Skill.creator_id == creator.id, Skill.slug == payload.slug
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise OccupationError(
            code="occupation.slug_conflict",
            message=f"You already have a skill with slug '{payload.slug}'.",
            status_code=409,
        )

    skill = Skill(
        creator_id=creator.id,
        slug=payload.slug,
        name=payload.name.strip()[:120],
        tagline=None,
        description_md=payload.description_md,
        category=payload.category,
        tags=payload.tags or None,
        status=SkillStatus.DRAFT,
        kind=SkillKind.OCCUPATION,
        pricing_model=payload.pricing_model,
        one_time_price_cents=payload.one_time_price_cents,
        subscription_price_cents=payload.subscription_price_cents,
    )
    session.add(skill)
    await session.flush()

    occupation = Occupation(
        skill_id=skill.id,
        summary_md=payload.summary_md,
        domains=payload.domains or None,
        persona_count=0,
        recommended_persona_count=payload.recommended_persona_count,
    )
    session.add(occupation)
    await session.flush()

    await write_audit(
        session,
        actor_id=creator.id,
        action="occupation.created",
        target_type="occupation",
        target_id=skill.id,
        metadata={"slug": skill.slug, "kind": "occupation"},
    )
    await session.flush()
    # Server-default columns (created_at/updated_at) only land on the in-
    # memory row after a refresh — required for sqlite tests where lazy
    # attribute reads would otherwise trip MissingGreenlet.
    await session.refresh(skill)
    await session.refresh(occupation)

    # Hydrate the read shape — for create the user/profile are the caller's.
    profile_res = await session.execute(
        select(CreatorProfile).where(CreatorProfile.user_id == creator.id)
    )
    profile = profile_res.scalar_one_or_none()
    return OccupationRead.model_validate(
        _to_list_item(skill, occupation, creator, profile, member_count=0)
    )


async def update_occupation(
    session: AsyncSession,
    *,
    creator: User,
    skill_id: uuid.UUID,
    patch: OccupationUpdate,
) -> OccupationRead:
    skill = await session.get(Skill, skill_id)
    skill = _ownership_or_404(skill, creator)
    occupation = await session.get(Occupation, skill_id)
    if occupation is None:  # pragma: no cover — FK CASCADE keeps them in sync
        raise OccupationError(
            code="occupation.not_found",
            message="Occupation not found.",
            status_code=404,
        )

    if patch.pricing_model is not None or patch.one_time_price_cents is not None \
            or patch.subscription_price_cents is not None:
        new_model = patch.pricing_model or skill.pricing_model
        new_ot = (
            patch.one_time_price_cents
            if patch.one_time_price_cents is not None
            else skill.one_time_price_cents
        )
        new_sub = (
            patch.subscription_price_cents
            if patch.subscription_price_cents is not None
            else skill.subscription_price_cents
        )
        _validate_pricing(new_model, new_ot, new_sub)

    # Apply Skill-side fields.
    if patch.name is not None:
        skill.name = patch.name.strip()[:120]
    if patch.description_md is not None:
        skill.description_md = patch.description_md
    if patch.category is not None:
        skill.category = patch.category
    if patch.tags is not None:
        skill.tags = patch.tags or None
    if patch.pricing_model is not None:
        skill.pricing_model = patch.pricing_model
    if patch.one_time_price_cents is not None:
        skill.one_time_price_cents = patch.one_time_price_cents
    if patch.subscription_price_cents is not None:
        skill.subscription_price_cents = patch.subscription_price_cents

    # Apply Occupation-side fields.
    if patch.summary_md is not None:
        occupation.summary_md = patch.summary_md
    if patch.domains is not None:
        occupation.domains = patch.domains or None
    if patch.recommended_persona_count is not None:
        occupation.recommended_persona_count = patch.recommended_persona_count

    await write_audit(
        session,
        actor_id=creator.id,
        action="occupation.updated",
        target_type="occupation",
        target_id=skill.id,
        metadata={
            "fields": [
                k for k, v in patch.model_dump(exclude_unset=True).items()
                if v is not None
            ]
        },
    )
    await session.flush()
    await session.refresh(skill)
    await session.refresh(occupation)

    profile_res = await session.execute(
        select(CreatorProfile).where(CreatorProfile.user_id == skill.creator_id)
    )
    profile = profile_res.scalar_one_or_none()
    user_res = await session.get(User, skill.creator_id)
    member_count = await _refresh_member_count(session, skill.id)
    return OccupationRead.model_validate(
        _to_list_item(
            skill,
            occupation,
            user_res or creator,
            profile,
            member_count=member_count,
        )
    )


def _validate_pricing(
    model: PricingModel,
    one_time: int | None,
    subscription: int | None,
) -> None:
    if model == PricingModel.ONE_TIME and one_time is None:
        raise OccupationError(
            code="occupation.pricing_required",
            message="one_time_price_cents is required when pricing_model=one_time.",
            status_code=422,
        )
    if model == PricingModel.SUBSCRIPTION and subscription is None:
        raise OccupationError(
            code="occupation.pricing_required",
            message=(
                "subscription_price_cents is required when "
                "pricing_model=subscription."
            ),
            status_code=422,
        )
    if model == PricingModel.FREE and (one_time is not None or subscription is not None):
        raise OccupationError(
            code="occupation.free_must_be_free",
            message="pricing_model=free must not set any price.",
            status_code=422,
        )


# ── Membership ───────────────────────────────────────────────────────


async def add_or_update_member(
    session: AsyncSession,
    *,
    creator: User,
    skill_id: uuid.UUID,
    member_skill_id: uuid.UUID,
    payload: OccupationSkillUpsert,
) -> OccupationSkillRead:
    """Add or update a single member skill.

    Idempotent: same ``(occupation_id, member_skill_id)`` upserts the
    metadata fields and bumps ``updated_at``.
    """
    parent = await session.get(Skill, skill_id)
    parent = _ownership_or_404(parent, creator)
    occupation = await session.get(Occupation, skill_id)
    if occupation is None:  # pragma: no cover
        raise OccupationError(
            code="occupation.not_found",
            message="Occupation not found.",
            status_code=404,
        )

    member = await session.get(Skill, member_skill_id)
    _validate_member_skill(member, occupation, payload.domain)
    assert member is not None  # narrowed by _validate_member_skill

    res = await session.execute(
        select(OccupationSkill)
        .where(OccupationSkill.occupation_id == skill_id)
        .where(OccupationSkill.member_skill_id == member_skill_id)
    )
    row = res.scalar_one_or_none()

    is_create = row is None
    if row is None:
        row = OccupationSkill(
            occupation_id=skill_id,
            member_skill_id=member_skill_id,
            domain=payload.domain,
            role=payload.role,
            sort_order=payload.sort_order,
            pinned=payload.pinned,
            notes_md=payload.notes_md,
        )
        session.add(row)
    else:
        row.domain = payload.domain
        row.role = payload.role
        row.sort_order = payload.sort_order
        row.pinned = payload.pinned
        row.notes_md = payload.notes_md

    await session.flush()

    await write_audit(
        session,
        actor_id=creator.id,
        action="occupation.members_set" if is_create else "occupation.updated",
        target_type="occupation",
        target_id=skill_id,
        metadata={
            "op": "member_upsert",
            "member_skill_id": str(member_skill_id),
            "role": payload.role.value,
            "domain": payload.domain,
        },
    )
    await session.flush()

    return await _hydrate_member(session, row)


async def bulk_set_members(
    session: AsyncSession,
    *,
    creator: User,
    skill_id: uuid.UUID,
    items: list[OccupationSkillBulkItem],
) -> OccupationSkillList:
    """Replace the entire membership set in one transaction.

    Validates every member is ``kind='skill'`` and every ``domain`` is
    declared on the occupation. Rejects with the first failing member's
    detail; the database state is unchanged on failure.
    """
    parent = await session.get(Skill, skill_id)
    parent = _ownership_or_404(parent, creator)
    occupation = await session.get(Occupation, skill_id)
    if occupation is None:  # pragma: no cover
        raise OccupationError(
            code="occupation.not_found",
            message="Occupation not found.",
            status_code=404,
        )

    # Reject duplicates up front.
    seen: set[uuid.UUID] = set()
    for item in items:
        if item.member_skill_id in seen:
            raise OccupationError(
                code="occupation.duplicate_member",
                message=(
                    f"member_skill_id {item.member_skill_id} appears "
                    f"more than once in items."
                ),
                status_code=422,
            )
        seen.add(item.member_skill_id)

    # Validate every member up front. Bulk-load the rows in one query.
    if items:
        member_ids = [i.member_skill_id for i in items]
        res = await session.execute(
            select(Skill).where(Skill.id.in_(member_ids))
        )
        # Key by string so dialect-coerced UUIDs round-trip cleanly.
        member_by_id: dict[str, Skill] = {
            str(m.id): m for m in res.scalars().all()
        }
        for item in items:
            _validate_member_skill(
                member_by_id.get(str(item.member_skill_id)),
                occupation,
                item.domain,
            )

    # Wipe existing membership and re-create.
    await session.execute(
        delete(OccupationSkill).where(
            OccupationSkill.occupation_id == skill_id
        )
    )

    new_rows: list[OccupationSkill] = []
    for item in items:
        row = OccupationSkill(
            occupation_id=skill_id,
            member_skill_id=item.member_skill_id,
            domain=item.domain,
            role=item.role,
            sort_order=item.sort_order,
            pinned=item.pinned,
            notes_md=item.notes_md,
        )
        session.add(row)
        # Flush each row separately to dodge SQLAlchemy's insertmany
        # sentinel-matching, which trips on sqlite where UUID round-trips
        # as String(36). Cost is small (≤ a few dozen rows per occupation)
        # and identical behaviour on Postgres.
        await session.flush([row])
        new_rows.append(row)

    await write_audit(
        session,
        actor_id=creator.id,
        action="occupation.members_set",
        target_type="occupation",
        target_id=skill_id,
        metadata={"count": len(items)},
    )
    await session.flush()

    hydrated = [await _hydrate_member(session, r) for r in new_rows]
    hydrated.sort(key=lambda r: (r.sort_order, r.member_slug))
    return OccupationSkillList(items=hydrated)


async def remove_member(
    session: AsyncSession,
    *,
    creator: User,
    skill_id: uuid.UUID,
    member_skill_id: uuid.UUID,
) -> None:
    parent = await session.get(Skill, skill_id)
    parent = _ownership_or_404(parent, creator)

    res = await session.execute(
        select(OccupationSkill)
        .where(OccupationSkill.occupation_id == skill_id)
        .where(OccupationSkill.member_skill_id == member_skill_id)
    )
    row = res.scalar_one_or_none()
    if row is None:
        raise OccupationError(
            code="occupation.member_not_found",
            message=(
                f"member_skill_id {member_skill_id} is not part of this "
                f"occupation."
            ),
            status_code=404,
        )
    await session.delete(row)
    await session.flush()

    await write_audit(
        session,
        actor_id=creator.id,
        action="occupation.members_set",
        target_type="occupation",
        target_id=skill_id,
        metadata={"op": "remove", "member_skill_id": str(member_skill_id)},
    )
    await session.flush()


async def reorder_members(
    session: AsyncSession,
    *,
    creator: User,
    skill_id: uuid.UUID,
    order: list[tuple[uuid.UUID, int]],
) -> OccupationSkillList:
    """Reorder members in place. Members not in ``order`` keep their existing
    ``sort_order``. Members in ``order`` but not in this occupation raise."""
    parent = await session.get(Skill, skill_id)
    parent = _ownership_or_404(parent, creator)

    if not order:
        # Nothing to reorder — return current set.
        return await _list_members(session, skill_id)

    member_ids = [m for (m, _) in order]
    if len(set(member_ids)) != len(member_ids):
        raise OccupationError(
            code="occupation.duplicate_member",
            message="Each member_skill_id may appear at most once in order.",
            status_code=422,
        )

    res = await session.execute(
        select(OccupationSkill)
        .where(OccupationSkill.occupation_id == skill_id)
        .where(OccupationSkill.member_skill_id.in_(member_ids))
    )
    # Key by str so dialect-coerced UUIDs (sqlite stores as String(36))
    # round-trip cleanly against the UUID-typed Pydantic body fields.
    rows_by_member: dict[str, OccupationSkill] = {
        str(r.member_skill_id): r for r in res.scalars().all()
    }
    missing = [m for m in member_ids if str(m) not in rows_by_member]
    if missing:
        raise OccupationError(
            code="occupation.member_not_found",
            message=(
                f"{len(missing)} member(s) not in this occupation: "
                f"{', '.join(str(m) for m in missing)}."
            ),
            status_code=404,
        )

    for member_id, sort_order in order:
        rows_by_member[str(member_id)].sort_order = sort_order
    await session.flush()

    await write_audit(
        session,
        actor_id=creator.id,
        action="occupation.members_set",
        target_type="occupation",
        target_id=skill_id,
        metadata={"op": "reorder", "count": len(order)},
    )
    await session.flush()

    return await _list_members(session, skill_id)


async def _list_members(
    session: AsyncSession, skill_id: uuid.UUID
) -> OccupationSkillList:
    res = await session.execute(
        select(OccupationSkill, Skill, User, CreatorProfile)
        .join(Skill, Skill.id == OccupationSkill.member_skill_id)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .where(OccupationSkill.occupation_id == skill_id)
        .order_by(OccupationSkill.sort_order.asc(), Skill.slug.asc())
    )
    items = [
        _to_skill_read(row, skill, profile, user)
        for (row, skill, user, profile) in res.all()
    ]
    return OccupationSkillList(items=items)


# ── Listing ──────────────────────────────────────────────────────────


async def list_occupations(  # noqa: PLR0912  (filters compose into one query)
    session: AsyncSession,
    filters: OccupationFilters,
) -> tuple[list[OccupationListItem], PageInfo]:
    """Paginated public list. By default returns published rows only."""
    dialect_name = (
        session.bind.dialect.name if session.bind is not None else "postgresql"
    )

    stmt = (
        select(Skill, Occupation, User, CreatorProfile)
        .join(Occupation, Occupation.skill_id == Skill.id)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .where(Skill.kind == SkillKind.OCCUPATION)
    )

    if not filters.include_non_public:
        stmt = stmt.where(Skill.status == SkillStatus.PUBLISHED)

    if filters.creator_id is not None:
        stmt = stmt.where(Skill.creator_id == filters.creator_id)
    if filters.category is not None:
        stmt = stmt.where(Skill.category == filters.category)
    if filters.creator_handle is not None:
        stmt = stmt.where(CreatorProfile.handle == filters.creator_handle)
    if filters.q:
        needle = f"%{filters.q.strip()}%"
        stmt = stmt.where(
            or_(
                Skill.name.ilike(needle),
                Skill.tagline.ilike(needle),
                Skill.description_md.ilike(needle),
                Occupation.summary_md.ilike(needle),
            )
        )
    if filters.domain is not None:
        # Cross-dialect: postgres ARRAY contains; sqlite JSON-blob LIKE.
        if dialect_name == "postgresql":
            stmt = stmt.where(Occupation.domains.op("@>")(literal([filters.domain])))
        else:
            text_col = cast(Occupation.domains, String)
            stmt = stmt.where(text_col.ilike(f'%"{filters.domain}"%'))

    # Order: newest first by default; ``order=oldest`` flips.
    if filters.order == "oldest":
        stmt = stmt.order_by(Skill.created_at.asc(), Skill.id.asc())
    else:
        stmt = stmt.order_by(Skill.created_at.desc(), Skill.id.desc())

    # Cursor: keyset by Skill.id (uuid7 is time-sortable).
    real_limit = clamp_limit(filters.limit)
    if filters.cursor:
        payload = decode_cursor(filters.cursor)
        last_id = payload.get("id")
        if last_id:
            if filters.order == "oldest":
                stmt = stmt.where(cast(Skill.id, String) > str(last_id))
            else:
                stmt = stmt.where(cast(Skill.id, String) < str(last_id))

    fetched = await session.execute(stmt.limit(real_limit + 1))
    rows = list(fetched.unique().all())
    has_more = len(rows) > real_limit
    if has_more:
        rows = rows[:real_limit]

    # Bulk-load member counts.
    skill_ids = [skill.id for (skill, _o, _u, _p) in rows]
    counts: dict[uuid.UUID, int] = {}
    if skill_ids:
        count_res = await session.execute(
            select(
                OccupationSkill.occupation_id,
                func.count(OccupationSkill.id),
            )
            .where(OccupationSkill.occupation_id.in_(skill_ids))
            .group_by(OccupationSkill.occupation_id)
        )
        counts = {row[0]: int(row[1]) for row in count_res.all()}

    items = [
        _to_list_item(
            skill,
            occupation,
            user,
            profile,
            member_count=counts.get(skill.id, 0),
        )
        for (skill, occupation, user, profile) in rows
    ]

    next_cursor: str | None = None
    if has_more and rows:
        last_skill = rows[-1][0]
        next_cursor = encode_cursor(last_id=str(last_skill.id))

    return items, PageInfo(
        next_cursor=next_cursor, has_more=has_more, limit=real_limit
    )


async def get_occupation_detail(
    session: AsyncSession,
    *,
    skill_id: uuid.UUID | None = None,
    handle: str | None = None,
    slug: str | None = None,
    include_non_public: bool = False,
) -> OccupationDetailResponse | None:
    """Fetch one occupation with member groupings.

    Lookup by UUID or by ``(handle, slug)`` (the public marketplace
    route). Returns ``None`` if not found.
    """
    stmt = (
        select(Skill, Occupation, User, CreatorProfile)
        .join(Occupation, Occupation.skill_id == Skill.id)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .where(Skill.kind == SkillKind.OCCUPATION)
    )
    if skill_id is not None:
        stmt = stmt.where(Skill.id == skill_id)
    elif handle is not None and slug is not None:
        stmt = stmt.where(CreatorProfile.handle == handle).where(Skill.slug == slug)
    else:
        return None
    if not include_non_public:
        stmt = stmt.where(Skill.status == SkillStatus.PUBLISHED)

    res = await session.execute(stmt)
    row = res.first()
    if row is None:
        return None
    skill, occupation, user, profile = row

    members = await _list_members(session, skill.id)
    grouped = _group_members(members.items, occupation.domains or [])

    base = _to_list_item(
        skill,
        occupation,
        user,
        profile,
        member_count=len(members.items),
    )
    return OccupationDetailResponse(
        **base.model_dump(),
        groups=grouped,
    )


def _group_members(
    members: list[OccupationSkillRead],
    declared_domains: list[str],
) -> list[OccupationSkillGroup]:
    """Group members by ``domain``, ordered by ``declared_domains`` then alpha.

    Members without a declared domain land in an ``other`` bucket at the
    end. Inside each group, members are already sorted by
    (sort_order, slug).
    """
    by_domain: dict[str | None, list[OccupationSkillRead]] = {}
    for m in members:
        by_domain.setdefault(m.domain, []).append(m)

    ordered_keys: list[str | None] = []
    for d in declared_domains:
        if d in by_domain:
            ordered_keys.append(d)
    # Trailing domains that aren't in the declared list (defensive — the
    # service rejects invalid domains on write, but reads stay tolerant).
    extras = sorted(
        k for k in by_domain if k is not None and k not in declared_domains
    )
    ordered_keys.extend(extras)
    if None in by_domain:
        ordered_keys.append(None)

    return [OccupationSkillGroup(domain=k, members=by_domain[k]) for k in ordered_keys]


# ── Graph preview (consumed by marketplace T-11) ─────────────────────


_ALLOWED_RELATIONS: frozenset[str] = frozenset(r.value for r in LinkRelation)


async def get_graph_preview(
    session: AsyncSession,
    *,
    skill_id: uuid.UUID,
    node_cap: int = 200,
    include_non_public: bool = False,
) -> VaultGraphPreview | None:
    """Compute the vault-graph preview for an occupation.

    Nodes are the occupation's member skills (up to ``node_cap``). Edges
    are read from the latest released ``SkillVersion`` body's frontmatter
    ``links:`` field for each member. Edges whose ``target`` is not a
    sibling node are *kept* — the marketplace renders dangling edges so
    the user sees the link's existence even if it points outside the
    bundle.
    """
    res = await session.execute(
        select(Skill, Occupation)
        .join(Occupation, Occupation.skill_id == Skill.id)
        .where(Skill.id == skill_id)
        .where(Skill.kind == SkillKind.OCCUPATION)
    )
    row = res.first()
    if row is None:
        return None
    skill, _occupation = row
    if not include_non_public and skill.status != SkillStatus.PUBLISHED:
        return None

    members_res = await session.execute(
        select(OccupationSkill, Skill)
        .join(Skill, Skill.id == OccupationSkill.member_skill_id)
        .options(selectinload(Skill.versions))
        .where(OccupationSkill.occupation_id == skill_id)
        .order_by(OccupationSkill.sort_order.asc(), Skill.slug.asc())
    )
    all_members = members_res.all()
    truncated = len(all_members) > node_cap
    kept = all_members[:node_cap]

    nodes: list[GraphNode] = []
    node_ids: set[str] = set()
    for membership, member in kept:
        node = GraphNode(
            id=member.slug,
            label=member.name,
            kind=member.kind,
            domain=membership.domain,
            role=membership.role,
            skill_id=member.id,
            pinned=membership.pinned,
        )
        nodes.append(node)
        node_ids.add(node.id)

    edges: list[GraphEdge] = []
    for _membership, member in kept:
        version = _pick_latest_released(member.versions)
        if version is None:
            continue
        try:
            links = await _read_links_from_storage(version)
        except Exception:  # pragma: no cover — storage flakes don't break preview
            log.exception("graph_preview.link_read_failed", extra={
                "skill_id": str(member.id),
                "version_id": str(version.id),
            })
            continue
        for link in links:
            relation = link.get("relation") or LinkRelation.SEE_ALSO.value
            if relation not in _ALLOWED_RELATIONS:
                relation = LinkRelation.SEE_ALSO.value
            target = link.get("target")
            if not target:
                continue
            weight = link.get("weight")
            edges.append(
                GraphEdge(
                    source=member.slug,
                    target=str(target),
                    relation=str(relation),
                    weight=float(weight) if isinstance(weight, (int, float)) else None,
                )
            )

    return VaultGraphPreview(
        occupation_id=skill.id,
        occupation_slug=skill.slug,
        node_cap=node_cap,
        truncated=truncated,
        nodes=nodes,
        edges=edges,
    )


def _pick_latest_released(versions: list[SkillVersion]) -> SkillVersion | None:
    candidates = [
        v for v in versions
        if v.released_at is not None and not v.is_yanked
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda v: v.released_at or datetime.min, reverse=True)
    return candidates[0]


async def _read_links_from_storage(
    version: SkillVersion,
) -> list[dict[str, Any]]:
    """Pull the ``links:`` array from a version's frontmatter.

    Returns an empty list if storage is missing the body or frontmatter
    is malformed — the preview is a best-effort view.
    """
    storage = get_storage()
    try:
        raw = await storage.get_object(version.storage_url)
    except Exception:
        return []
    try:
        fm, _body = split_frontmatter(raw)
    except ValueError:
        return []
    links_raw = fm.get("links") or []
    if not isinstance(links_raw, list):
        return []
    out: list[dict[str, Any]] = []
    for entry in links_raw:
        if isinstance(entry, dict):
            out.append(entry)
    return out


# ── Build / publish (Wave-2 stubs; Wave-3 wires the real Arq job) ────


async def trigger_build(
    session: AsyncSession,
    *,
    creator: User,
    skill_id: uuid.UUID,
    version: str,
) -> JobAccepted:
    """Enqueue a vault build for the named version.

    Wave 3 (T-06): wired to the real ``src.vault.jobs.enqueue_occupation_build``.
    In ``ENV=test`` the façade runs the builder inline on the caller's
    session so the build participates in the request's transaction; in
    production the façade dispatches to Arq and the worker runs the
    build in a fresh DB session.
    """
    parent = await session.get(Skill, skill_id)
    parent = _ownership_or_404(parent, creator)
    occupation = await session.get(Occupation, skill_id)
    if occupation is None:  # pragma: no cover
        raise OccupationError(
            code="occupation.not_found",
            message="Occupation not found.",
            status_code=404,
        )

    member_count = await _refresh_member_count(session, skill_id)
    if member_count == 0:
        raise OccupationError(
            code="occupation.empty_membership",
            message=(
                "Cannot build an occupation with zero member skills. Add at "
                "least one `kind=skill` member first."
            ),
            status_code=422,
        )

    version_res = await session.execute(
        select(SkillVersion)
        .where(SkillVersion.skill_id == skill_id)
        .where(SkillVersion.version == version)
    )
    target = version_res.scalar_one_or_none()
    if target is None:
        raise OccupationError(
            code="occupation.version_not_found",
            message=f"Version {version} not found on this occupation.",
            status_code=404,
        )

    # Local import to avoid an import cycle (vault.builder imports from
    # occupations.models; the service-side handle stays late-bound).
    from src.vault import jobs as vault_jobs  # noqa: PLC0415 — break circular import
    from src.vault.builder import VaultBuildError  # noqa: PLC0415  # circular import

    try:
        result = await vault_jobs.enqueue_occupation_build(
            session, skill_id=skill_id, version=version
        )
    except VaultBuildError as exc:
        raise OccupationError(
            code=exc.code,
            message=exc.message,
            status_code=422,
        ) from exc

    await write_audit(
        session,
        actor_id=creator.id,
        action="occupation.build_queued",
        target_type="occupation",
        target_id=skill_id,
        metadata={
            "version": version,
            "skill_version_id": str(target.id),
            "job_id": result.job_id,
            "build_id": str(result.build_id) if result.build_id else None,
            "member_count": member_count,
        },
    )
    await session.flush()
    return JobAccepted(
        job_id=result.job_id,
        build_id=result.build_id,
        status=result.status,
    )


async def publish_occupation(
    session: AsyncSession,
    *,
    creator: User,
    skill_id: uuid.UUID,
    payload: PublishRequest,
) -> JobAccepted:
    """Trigger a build and queue a publish.

    Wave 2: enqueues the build job stub and marks the version's
    ``released_at`` once the build job is run (Wave 3). For now we set
    ``released_at`` synchronously so creators can move forward against
    a stub vault build that lands in T-06.
    """
    job = await trigger_build(
        session,
        creator=creator,
        skill_id=skill_id,
        version=payload.version,
    )

    parent = await session.get(Skill, skill_id)
    assert parent is not None  # trigger_build raised if not
    version_res = await session.execute(
        select(SkillVersion)
        .where(SkillVersion.skill_id == skill_id)
        .where(SkillVersion.version == payload.version)
    )
    target = version_res.scalar_one_or_none()
    if target is None:  # pragma: no cover — guarded above
        raise OccupationError(
            code="occupation.version_not_found",
            message=f"Version {payload.version} not found on this occupation.",
            status_code=404,
        )
    if payload.changelog_md is not None:
        target.changelog_md = payload.changelog_md
    if target.released_at is None:
        target.released_at = datetime.now(UTC)
        target.released_by = creator.id
    parent.status = SkillStatus.PUBLISHED
    parent.latest_version_id = target.id

    await write_audit(
        session,
        actor_id=creator.id,
        action="occupation.published",
        target_type="occupation",
        target_id=skill_id,
        metadata={"version": payload.version, "job_id": job.job_id},
    )
    await session.flush()
    return job


# Re-export so the router's type hints stay tight.
from src.occupations.schemas import PublishRequest  # noqa: E402

__all__ = [
    "OccupationError",
    "OccupationFilters",
    "add_or_update_member",
    "bulk_set_members",
    "create_occupation",
    "get_graph_preview",
    "get_occupation_detail",
    "list_occupations",
    "publish_occupation",
    "remove_member",
    "reorder_members",
    "trigger_build",
    "update_occupation",
]
