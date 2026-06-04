"""Persona service layer.

Spec: ``team/02-api-surface.md`` §2, ``team/01-data-model-deltas.md``
§personas, ADR-002, ADR-004, ADR-005.

A ``kind=persona`` row is a thin specialisation of the existing
``skills`` row — every create/patch/publish writes the parent ``Skill``
row first and the ``personas`` side-table row second in the same
transaction. Neuron membership lives in ``persona_neurons`` and is
appended only via the capture-finalize path (Wave 3, T-05); this Wave-2
service handles reorder + remove + read.

No raw SQL. No business logic in routers. All exception paths use
:class:`PersonaError` so the router can map to typed error codes.

Persona checkout enforcement (T-04 acceptance bullet 2) — the
:func:`check_persona_checkout_entitlement` helper is the single source
of truth; ``src/billing/service.py`` (the checkout flow) imports it.
"""

from __future__ import annotations

import logging
import uuid  # noqa: TC003  (used at runtime via UUID args / Mapped[uuid.UUID])
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import selectinload

from src.billing.models import License, LicenseCompositionRole, LicenseStatus
from src.core.db import write_audit
from src.core.errors import AppError, ErrorDetail
from src.core.pagination import PageInfo, clamp_limit, decode_cursor, encode_cursor
from src.occupations.models import Occupation
from src.personas.models import Persona, PersonaNeuron
from src.personas.schemas import (
    CreatorChip,
    GraphEdge,
    GraphNode,
    JobAccepted,
    NeuronOrderItem,
    ParentOccupationChip,
    PersonaCreate,
    PersonaDetailResponse,
    PersonaListItem,
    PersonaNeuronList,
    PersonaNeuronRead,
    PersonaRead,
    PersonaUpdate,
    PublishRequest,
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


class PersonaError(AppError):
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
class PersonaFilters:
    parent_occupation_id: uuid.UUID | None = None
    creator_handle: str | None = None
    q: str | None = None
    order: str | None = None
    limit: int | None = None
    cursor: str | None = None
    include_non_public: bool = False
    creator_id: uuid.UUID | None = None


# ── Internal helpers ──────────────────────────────────────────────────


def _ownership_or_404(skill: Skill | None, user: User) -> Skill:
    if skill is None:
        raise PersonaError(
            code="persona.not_found",
            message="Persona not found.",
            status_code=404,
        )
    if skill.kind != SkillKind.PERSONA:
        # Don't leak the existence of a same-id non-persona row.
        raise PersonaError(
            code="persona.not_found",
            message="Persona not found.",
            status_code=404,
        )
    # Cross-dialect: sqlite (tests) stores UUID as String(36), so a UUID
    # column compared to a UUID Python object can be string-vs-UUID. Cast
    # both sides to str for a dialect-agnostic check.
    if str(skill.creator_id) != str(user.id) and not user.is_admin:
        raise PersonaError(
            code="persona.not_found",
            message="Persona not found.",
            status_code=404,
        )
    return skill


async def _resolve_parent_occupation(
    session: AsyncSession,
    *,
    parent_id: uuid.UUID,
) -> tuple[Skill, Occupation, User, CreatorProfile | None]:
    """Load the parent occupation triple; raise if not a kind=occupation row."""
    res = await session.execute(
        select(Skill, Occupation, User, CreatorProfile)
        .join(Occupation, Occupation.skill_id == Skill.id)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .where(Skill.id == parent_id)
    )
    row = res.first()
    if row is None:
        raise PersonaError(
            code="persona.parent_occupation_invalid",
            message=(
                "parent_occupation_id must reference an existing "
                "kind=occupation skill row."
            ),
            status_code=422,
            details=[
                ErrorDetail(
                    field="parent_occupation_id",
                    code="parent_not_found",
                    message=f"No occupation row with id={parent_id}.",
                )
            ],
        )
    parent_skill, parent_occ, parent_user, parent_profile = row
    if parent_skill.kind != SkillKind.OCCUPATION:
        raise PersonaError(
            code="persona.parent_occupation_invalid",
            message=(
                f"Skill {parent_id} has kind={parent_skill.kind.value}, "
                "not 'occupation'."
            ),
            status_code=422,
            details=[
                ErrorDetail(
                    field="parent_occupation_id",
                    code="parent_not_occupation",
                    message=(
                        f"Expected kind='occupation', got "
                        f"'{parent_skill.kind.value}'."
                    ),
                )
            ],
        )
    return parent_skill, parent_occ, parent_user, parent_profile


def _parent_chip(
    parent_skill: Skill,
    parent_profile: CreatorProfile | None,
    parent_user: User | None,
) -> ParentOccupationChip:
    handle: str | None = None
    if parent_profile is not None:
        handle = parent_profile.handle
    elif parent_user is not None and parent_user.display_name:
        handle = parent_user.display_name
    return ParentOccupationChip(
        skill_id=parent_skill.id,
        slug=parent_skill.slug,
        name=parent_skill.name,
        handle=handle,
    )


def _to_list_item(
    skill: Skill,
    persona: Persona,
    user: User,
    profile: CreatorProfile | None,
    parent_chip: ParentOccupationChip,
    *,
    neuron_count: int | None = None,
) -> PersonaListItem:
    handle = profile.handle if profile is not None else (user.display_name or "anon")
    return PersonaListItem(
        id=skill.id,
        skill_id=skill.id,
        slug=skill.slug,
        name=skill.name,
        tagline=skill.tagline,
        description_md=skill.description_md,
        cover_image_url=skill.cover_image_url,
        category=skill.category,
        tags=list(skill.tags or []),
        kind=skill.kind,
        status=skill.status,
        pricing_model=skill.pricing_model,
        one_time_price_cents=skill.one_time_price_cents,
        subscription_price_cents=skill.subscription_price_cents,
        creator_intro_md=persona.creator_intro_md,
        specialization=persona.specialization,
        years_of_experience=persona.years_of_experience,
        neuron_count=neuron_count if neuron_count is not None else persona.neuron_count,
        parent_occupation=parent_chip,
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
        latest_build_id=persona.latest_build_id,
        created_at=skill.created_at,
        updated_at=skill.updated_at,
    )


def _to_neuron_read(
    row: PersonaNeuron,
    neuron_skill: Skill,
    neuron_profile: CreatorProfile | None,
    neuron_user: User | None,
) -> PersonaNeuronRead:
    handle: str | None = None
    if neuron_profile is not None:
        handle = neuron_profile.handle
    elif neuron_user is not None and neuron_user.display_name:
        handle = neuron_user.display_name
    return PersonaNeuronRead(
        id=row.id,
        persona_id=row.persona_id,
        neuron_skill_id=row.neuron_skill_id,
        neuron_slug=neuron_skill.slug,
        neuron_name=neuron_skill.name,
        neuron_tagline=neuron_skill.tagline,
        neuron_description_md=neuron_skill.description_md,
        creator_handle=handle,
        section=row.section,
        sort_order=row.sort_order,
        added_at=row.added_at,
    )


async def _refresh_neuron_count(
    session: AsyncSession, persona_id: uuid.UUID
) -> int:
    res = await session.execute(
        select(func.count(PersonaNeuron.id)).where(
            PersonaNeuron.persona_id == persona_id
        )
    )
    return int(res.scalar() or 0)


async def _list_neurons(
    session: AsyncSession, persona_id: uuid.UUID
) -> PersonaNeuronList:
    res = await session.execute(
        select(PersonaNeuron, Skill, User, CreatorProfile)
        .join(Skill, Skill.id == PersonaNeuron.neuron_skill_id)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .where(PersonaNeuron.persona_id == persona_id)
        .order_by(PersonaNeuron.sort_order.asc(), Skill.slug.asc())
    )
    items = [
        _to_neuron_read(row, skill, profile, user)
        for (row, skill, user, profile) in res.all()
    ]
    return PersonaNeuronList(items=items)


async def _load_for_read(
    session: AsyncSession, skill_id: uuid.UUID
) -> tuple[Skill, Persona, User, CreatorProfile | None] | None:
    res = await session.execute(
        select(Skill, Persona, User, CreatorProfile)
        .join(Persona, Persona.skill_id == Skill.id)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .where(Skill.id == skill_id)
        .where(Skill.kind == SkillKind.PERSONA)
    )
    row = res.first()
    if row is None:
        return None
    return row[0], row[1], row[2], row[3]


def _validate_pricing(
    model: PricingModel,
    one_time: int | None,
    subscription: int | None,
) -> None:
    if model == PricingModel.ONE_TIME and one_time is None:
        raise PersonaError(
            code="persona.pricing_required",
            message="one_time_price_cents is required when pricing_model=one_time.",
            status_code=422,
        )
    if model == PricingModel.SUBSCRIPTION and subscription is None:
        raise PersonaError(
            code="persona.pricing_required",
            message=(
                "subscription_price_cents is required when "
                "pricing_model=subscription."
            ),
            status_code=422,
        )
    if model == PricingModel.FREE and (one_time is not None or subscription is not None):
        raise PersonaError(
            code="persona.free_must_be_free",
            message="pricing_model=free must not set any price.",
            status_code=422,
        )


# ── Creator-scoped operations ────────────────────────────────────────


async def create_persona(
    session: AsyncSession,
    *,
    creator: User,
    payload: PersonaCreate,
) -> PersonaRead:
    """Create a persona. Caller must be a verified creator (router-enforced).

    Validates ``parent_occupation_id`` points at a real ``kind=occupation``
    row (rejects with ``persona.parent_occupation_invalid`` otherwise) per
    T-04 acceptance.
    """
    if not creator.is_creator_verified and not creator.is_admin:
        raise PersonaError(
            code="persona.creator_not_verified",
            message=(
                "Publishing personas requires a verified creator profile."
            ),
            status_code=403,
        )

    _validate_pricing(
        payload.pricing_model,
        payload.one_time_price_cents,
        payload.subscription_price_cents,
    )

    parent_skill, _parent_occ, parent_user, parent_profile = (
        await _resolve_parent_occupation(
            session, parent_id=payload.parent_occupation_id
        )
    )

    # Slug uniqueness within this creator.
    existing = await session.execute(
        select(Skill).where(
            Skill.creator_id == creator.id, Skill.slug == payload.slug
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise PersonaError(
            code="persona.slug_conflict",
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
        kind=SkillKind.PERSONA,
        pricing_model=payload.pricing_model,
        one_time_price_cents=payload.one_time_price_cents,
        subscription_price_cents=payload.subscription_price_cents,
    )
    session.add(skill)
    await session.flush()

    persona = Persona(
        skill_id=skill.id,
        parent_occupation_id=parent_skill.id,
        creator_intro_md=payload.creator_intro_md,
        specialization=payload.specialization,
        years_of_experience=payload.years_of_experience,
        neuron_count=0,
    )
    session.add(persona)
    await session.flush()

    await write_audit(
        session,
        actor_id=creator.id,
        action="persona.created",
        target_type="persona",
        target_id=skill.id,
        metadata={
            "slug": skill.slug,
            "kind": "persona",
            "parent_occupation_id": str(parent_skill.id),
        },
    )
    await session.flush()
    # Server-default columns (created_at/updated_at) only land on the in-
    # memory row after a refresh — required for sqlite tests where lazy
    # attribute reads would otherwise trip MissingGreenlet.
    await session.refresh(skill)
    await session.refresh(persona)

    profile_res = await session.execute(
        select(CreatorProfile).where(CreatorProfile.user_id == creator.id)
    )
    profile = profile_res.scalar_one_or_none()
    parent_chip = _parent_chip(parent_skill, parent_profile, parent_user)
    return PersonaRead.model_validate(
        _to_list_item(skill, persona, creator, profile, parent_chip, neuron_count=0)
    )


async def update_persona(  # noqa: PLR0912  (one branch per optional field)
    session: AsyncSession,
    *,
    creator: User,
    skill_id: uuid.UUID,
    patch: PersonaUpdate,
) -> PersonaRead:
    """Patch a persona.

    Per ``02-api-surface.md`` §2, ``slug`` and ``parent_occupation_id``
    are immutable after first publish. The slug isn't in
    :class:`PersonaUpdate` at all, so we only need to gate parent
    reparenting on publish state — both rejections share the
    ``persona.published_lock`` error code.
    """
    skill = await session.get(Skill, skill_id)
    skill = _ownership_or_404(skill, creator)
    persona = await session.get(Persona, skill_id)
    if persona is None:  # pragma: no cover — FK CASCADE keeps them in sync
        raise PersonaError(
            code="persona.not_found",
            message="Persona not found.",
            status_code=404,
        )

    if (
        patch.parent_occupation_id is not None
        and str(patch.parent_occupation_id) != str(persona.parent_occupation_id)
        and skill.status == SkillStatus.PUBLISHED
    ):
        raise PersonaError(
            code="persona.published_lock",
            message=(
                "parent_occupation_id cannot change after the persona is "
                "published. Yank the listing first if you need to re-parent."
            ),
            status_code=409,
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

    # Resolve the parent — even when unchanged, we need its chip for the response.
    parent_id_to_use = (
        patch.parent_occupation_id
        if patch.parent_occupation_id is not None
        else persona.parent_occupation_id
    )
    parent_skill, _parent_occ, parent_user, parent_profile = (
        await _resolve_parent_occupation(session, parent_id=parent_id_to_use)
    )

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

    # Apply Persona-side fields.
    if patch.parent_occupation_id is not None:
        persona.parent_occupation_id = parent_skill.id
    if patch.creator_intro_md is not None:
        persona.creator_intro_md = patch.creator_intro_md
    if patch.specialization is not None:
        persona.specialization = patch.specialization
    if patch.years_of_experience is not None:
        persona.years_of_experience = patch.years_of_experience

    await write_audit(
        session,
        actor_id=creator.id,
        action="persona.updated",
        target_type="persona",
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
    await session.refresh(persona)

    profile_res = await session.execute(
        select(CreatorProfile).where(CreatorProfile.user_id == skill.creator_id)
    )
    profile = profile_res.scalar_one_or_none()
    user_res = await session.get(User, skill.creator_id)
    neuron_count = await _refresh_neuron_count(session, skill.id)
    parent_chip = _parent_chip(parent_skill, parent_profile, parent_user)
    return PersonaRead.model_validate(
        _to_list_item(
            skill,
            persona,
            user_res or creator,
            profile,
            parent_chip,
            neuron_count=neuron_count,
        )
    )


# ── Neuron membership ────────────────────────────────────────────────


async def reorder_neurons(
    session: AsyncSession,
    *,
    creator: User,
    skill_id: uuid.UUID,
    items: list[NeuronOrderItem],
) -> PersonaNeuronList:
    """Reorder existing neurons. Never adds.

    Per ``02-api-surface.md`` §2, neurons may also be assigned a
    ``section`` here to relocate them in the vault folder layout.
    Members in ``items`` but not in this persona raise
    ``persona.neuron_not_found``.
    """
    parent = await session.get(Skill, skill_id)
    parent = _ownership_or_404(parent, creator)

    if not items:
        return await _list_neurons(session, skill_id)

    neuron_ids = [i.neuron_skill_id for i in items]
    if len(set(neuron_ids)) != len(neuron_ids):
        raise PersonaError(
            code="persona.duplicate_neuron",
            message="Each neuron_skill_id may appear at most once in items.",
            status_code=422,
        )

    res = await session.execute(
        select(PersonaNeuron)
        .where(PersonaNeuron.persona_id == skill_id)
        .where(PersonaNeuron.neuron_skill_id.in_(neuron_ids))
    )
    # Key by str so dialect-coerced UUIDs (sqlite stores as String(36))
    # round-trip cleanly against the UUID-typed Pydantic body fields.
    rows_by_neuron: dict[str, PersonaNeuron] = {
        str(r.neuron_skill_id): r for r in res.scalars().all()
    }
    missing = [n for n in neuron_ids if str(n) not in rows_by_neuron]
    if missing:
        raise PersonaError(
            code="persona.neuron_not_found",
            message=(
                f"{len(missing)} neuron(s) not in this persona: "
                f"{', '.join(str(n) for n in missing)}."
            ),
            status_code=404,
        )

    for item in items:
        row = rows_by_neuron[str(item.neuron_skill_id)]
        row.sort_order = item.sort_order
        if item.section is not None:
            row.section = item.section
    await session.flush()

    await write_audit(
        session,
        actor_id=creator.id,
        action="persona.neuron_added",  # reorder is a member-set change
        target_type="persona",
        target_id=skill_id,
        metadata={"op": "reorder", "count": len(items)},
    )
    await session.flush()

    return await _list_neurons(session, skill_id)


async def remove_neuron(
    session: AsyncSession,
    *,
    creator: User,
    skill_id: uuid.UUID,
    neuron_skill_id: uuid.UUID,
) -> None:
    """Remove a neuron from a persona.

    Per ``02-api-surface.md`` §2: removes the join row. The neuron row
    itself is soft-deleted only if no other persona references it
    (Phase-2 cleanup job — not in MVP).
    """
    parent = await session.get(Skill, skill_id)
    parent = _ownership_or_404(parent, creator)

    res = await session.execute(
        select(PersonaNeuron)
        .where(PersonaNeuron.persona_id == skill_id)
        .where(PersonaNeuron.neuron_skill_id == neuron_skill_id)
    )
    row = res.scalar_one_or_none()
    if row is None:
        raise PersonaError(
            code="persona.neuron_not_found",
            message=(
                f"neuron_skill_id {neuron_skill_id} is not part of this "
                f"persona."
            ),
            status_code=404,
        )
    await session.delete(row)
    await session.flush()

    # Refresh denormalized count on the persona row.
    persona = await session.get(Persona, skill_id)
    if persona is not None:
        persona.neuron_count = await _refresh_neuron_count(session, skill_id)
        await session.flush()

    await write_audit(
        session,
        actor_id=creator.id,
        action="persona.neuron_removed",
        target_type="persona",
        target_id=skill_id,
        metadata={"neuron_skill_id": str(neuron_skill_id)},
    )
    await session.flush()


# ── Listing ──────────────────────────────────────────────────────────


async def list_personas(  # noqa: PLR0912  (filters compose into one query)
    session: AsyncSession,
    filters: PersonaFilters,
) -> tuple[list[PersonaListItem], PageInfo]:
    """Paginated public list. By default returns published rows only."""
    stmt = (
        select(Skill, Persona, User, CreatorProfile)
        .join(Persona, Persona.skill_id == Skill.id)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .where(Skill.kind == SkillKind.PERSONA)
    )

    if not filters.include_non_public:
        stmt = stmt.where(Skill.status == SkillStatus.PUBLISHED)

    if filters.creator_id is not None:
        stmt = stmt.where(Skill.creator_id == filters.creator_id)
    if filters.parent_occupation_id is not None:
        stmt = stmt.where(Persona.parent_occupation_id == filters.parent_occupation_id)
    if filters.creator_handle is not None:
        stmt = stmt.where(CreatorProfile.handle == filters.creator_handle)
    if filters.q:
        needle = f"%{filters.q.strip()}%"
        stmt = stmt.where(
            or_(
                Skill.name.ilike(needle),
                Skill.tagline.ilike(needle),
                Skill.description_md.ilike(needle),
                Persona.creator_intro_md.ilike(needle),
                Persona.specialization.ilike(needle),
            )
        )

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

    # Bulk-load neuron counts.
    skill_ids = [skill.id for (skill, _p, _u, _pr) in rows]
    counts: dict[uuid.UUID, int] = {}
    if skill_ids:
        count_res = await session.execute(
            select(
                PersonaNeuron.persona_id,
                func.count(PersonaNeuron.id),
            )
            .where(PersonaNeuron.persona_id.in_(skill_ids))
            .group_by(PersonaNeuron.persona_id)
        )
        counts = {row[0]: int(row[1]) for row in count_res.all()}

    # Bulk-load parent occupations for all rows.
    parent_ids = list({p.parent_occupation_id for (_s, p, _u, _pr) in rows})
    parent_chips: dict[uuid.UUID, ParentOccupationChip] = {}
    if parent_ids:
        parent_res = await session.execute(
            select(Skill, CreatorProfile, User)
            .join(User, User.id == Skill.creator_id)
            .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
            .where(Skill.id.in_(parent_ids))
        )
        for parent_skill, parent_profile, parent_user in parent_res.all():
            parent_chips[parent_skill.id] = _parent_chip(
                parent_skill, parent_profile, parent_user
            )

    items: list[PersonaListItem] = []
    for skill, persona, user, profile in rows:
        chip = parent_chips.get(
            persona.parent_occupation_id,
            ParentOccupationChip(
                skill_id=persona.parent_occupation_id,
                slug="unknown",
                name="(missing parent)",
            ),
        )
        items.append(
            _to_list_item(
                skill,
                persona,
                user,
                profile,
                chip,
                neuron_count=counts.get(skill.id, persona.neuron_count),
            )
        )

    next_cursor: str | None = None
    if has_more and rows:
        last_skill = rows[-1][0]
        next_cursor = encode_cursor(last_id=str(last_skill.id))

    return items, PageInfo(
        next_cursor=next_cursor, has_more=has_more, limit=real_limit
    )


async def get_persona_detail(
    session: AsyncSession,
    *,
    skill_id: uuid.UUID | None = None,
    handle: str | None = None,
    slug: str | None = None,
    include_non_public: bool = False,
    caller_id: uuid.UUID | None = None,
) -> PersonaDetailResponse | None:
    """Fetch one persona with neuron summary titles.

    Lookup by UUID or by ``(handle, slug)`` (the public marketplace
    route). Returns ``None`` if not found.

    ``caller_is_entitled`` is computed from the buyer's license set —
    True if ``caller_id`` holds an active license on this persona or is
    the creator/admin.
    """
    stmt = (
        select(Skill, Persona, User, CreatorProfile)
        .join(Persona, Persona.skill_id == Skill.id)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .where(Skill.kind == SkillKind.PERSONA)
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
    skill, persona, user, profile = row

    parent_skill_data = await _safe_load_parent(
        session, persona.parent_occupation_id
    )
    parent_chip = (
        _parent_chip(parent_skill_data[0], parent_skill_data[2], parent_skill_data[1])
        if parent_skill_data is not None
        else ParentOccupationChip(
            skill_id=persona.parent_occupation_id,
            slug="unknown",
            name="(missing parent)",
        )
    )

    neurons = await _list_neurons(session, skill.id)
    sample_titles = [n.neuron_name for n in neurons.items[:5]]

    entitled = await _caller_holds_persona_license(
        session, caller_id=caller_id, persona_skill=skill
    )

    base = _to_list_item(
        skill,
        persona,
        user,
        profile,
        parent_chip,
        neuron_count=len(neurons.items),
    )
    return PersonaDetailResponse(
        **base.model_dump(),
        sample_neuron_titles=sample_titles,
        caller_is_entitled=entitled,
    )


async def _safe_load_parent(
    session: AsyncSession, parent_id: uuid.UUID
) -> tuple[Skill, User, CreatorProfile | None] | None:
    """Load the parent occupation triple, tolerant of dangling FK refs."""
    res = await session.execute(
        select(Skill, User, CreatorProfile)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .where(Skill.id == parent_id)
    )
    row = res.first()
    if row is None:
        return None
    return row[0], row[1], row[2]


async def _caller_holds_persona_license(
    session: AsyncSession,
    *,
    caller_id: uuid.UUID | None,
    persona_skill: Skill,
) -> bool:
    """True if the caller is the creator/admin OR holds an active license."""
    if caller_id is None:
        return False
    # Creator/admin always "entitled" to read their own persona's bodies.
    if str(persona_skill.creator_id) == str(caller_id):
        return True
    user = await session.get(User, caller_id)
    if user is not None and user.is_admin:
        return True
    res = await session.execute(
        select(License).where(
            License.buyer_id == caller_id,
            License.skill_id == persona_skill.id,
            License.status == LicenseStatus.ACTIVE,
        )
    )
    return res.scalar_one_or_none() is not None


# ── Neuron read endpoint (entitlement gated) ─────────────────────────


async def list_persona_neurons(
    session: AsyncSession,
    *,
    skill_id: uuid.UUID,
    caller_id: uuid.UUID | None,
    section: str | None = None,
    limit: int | None = None,
    cursor: str | None = None,
) -> PersonaNeuronList | None:
    """Return the full neuron list for an entitled caller, or ``None``.

    Per ``02-api-surface.md`` §2: non-entitled callers get 404 (the
    router maps ``None`` → 404 to avoid existence leak). The creator and
    admins are always entitled to read their own personas' neurons.
    """
    skill = await session.get(Skill, skill_id)
    if skill is None or skill.kind != SkillKind.PERSONA:
        return None
    # Only published personas are visible to non-creator callers; creators
    # / admins see draft personas.
    is_owner_or_admin = False
    if caller_id is not None:
        if str(skill.creator_id) == str(caller_id):
            is_owner_or_admin = True
        else:
            user = await session.get(User, caller_id)
            if user is not None and user.is_admin:
                is_owner_or_admin = True
    if skill.status != SkillStatus.PUBLISHED and not is_owner_or_admin:
        return None
    entitled = await _caller_holds_persona_license(
        session, caller_id=caller_id, persona_skill=skill
    )
    if not entitled:
        return None

    # Note: section + limit + cursor accepted for API parity with the
    # spec; with current persona scale (≤10 neurons per persona at MVP),
    # we pull the full list and filter in Python. A real cursor lands
    # alongside the discovery refactor in Wave 4.
    full = await _list_neurons(session, skill_id)
    items = full.items
    if section is not None:
        items = [n for n in items if n.section == section]
    if limit is not None:
        items = items[:clamp_limit(limit)]
    return PersonaNeuronList(items=items)


# ── Persona checkout entitlement (T-04 acceptance bullet 2) ──────────


@dataclass
class PersonaCheckoutGate:
    """Outcome of :func:`check_persona_checkout_entitlement`.

    ``ok=True`` means the buyer holds an active occupation license on the
    persona's parent and the checkout may proceed. ``ok=False`` means the
    caller should respond ``409 persona.requires_parent_occupation`` with
    ``parent_occupation_skill_id`` + ``parent_occupation_slug`` in the
    error details.
    """

    ok: bool
    parent_occupation_skill_id: uuid.UUID | None = None
    parent_occupation_slug: str | None = None
    parent_occupation_handle: str | None = None


async def check_persona_checkout_entitlement(
    session: AsyncSession,
    *,
    buyer: User,
    skill: Skill,
) -> PersonaCheckoutGate:
    """Validate persona purchase prerequisites per ADR-002 / T-04.

    Returns a :class:`PersonaCheckoutGate` describing the parent
    occupation; the billing router wraps a falsey result into the 409
    error body documented in ``02-api-surface.md`` §2.

    Non-persona SKUs pass through with ``ok=True`` so this function is
    safe to call unconditionally from the checkout flow.
    """
    if skill.kind != SkillKind.PERSONA:
        return PersonaCheckoutGate(ok=True)

    persona = await session.get(Persona, skill.id)
    if persona is None:
        # The FK constraint on personas.skill_id → skills.id makes this
        # unreachable in practice, but the type narrowing matters for
        # mypy --strict. Treat as "missing parent" and let the router
        # render the canonical 409.
        return PersonaCheckoutGate(
            ok=False,
            parent_occupation_skill_id=None,
            parent_occupation_slug=None,
            parent_occupation_handle=None,
        )

    parent = await session.get(Skill, persona.parent_occupation_id)
    parent_slug = parent.slug if parent is not None else None
    parent_handle: str | None = None
    if parent is not None:
        profile_res = await session.execute(
            select(CreatorProfile).where(CreatorProfile.user_id == parent.creator_id)
        )
        profile = profile_res.scalar_one_or_none()
        if profile is not None:
            parent_handle = profile.handle

    # Per ADR-002 / 01-data-model-deltas §licenses additions: the relevant
    # license is the buyer's *occupation* license on persona.parent_occupation_id.
    res = await session.execute(
        select(License).where(
            License.buyer_id == buyer.id,
            License.skill_id == persona.parent_occupation_id,
            License.status == LicenseStatus.ACTIVE,
        )
    )
    active_license = res.scalar_one_or_none()
    # The composition_role is set to ``standalone`` on legacy licenses
    # and ``occupation`` on the licenses minted by an occupation
    # purchase. Either is acceptable as the anchor — the spec language
    # is "active license on the parent occupation". A
    # composition_role='persona' license should never be the anchor
    # (those snapshot the parent in ``target_occupation_skill_id`` and
    # are layered on top, not anchors themselves).
    if active_license is None:
        return PersonaCheckoutGate(
            ok=False,
            parent_occupation_skill_id=persona.parent_occupation_id,
            parent_occupation_slug=parent_slug,
            parent_occupation_handle=parent_handle,
        )
    if active_license.composition_role == LicenseCompositionRole.PERSONA:
        return PersonaCheckoutGate(
            ok=False,
            parent_occupation_skill_id=persona.parent_occupation_id,
            parent_occupation_slug=parent_slug,
            parent_occupation_handle=parent_handle,
        )
    return PersonaCheckoutGate(
        ok=True,
        parent_occupation_skill_id=persona.parent_occupation_id,
        parent_occupation_slug=parent_slug,
        parent_occupation_handle=parent_handle,
    )


# ── Graph preview (consumed by marketplace T-11) ─────────────────────


_ALLOWED_RELATIONS: frozenset[str] = frozenset(r.value for r in LinkRelation)


async def get_graph_preview(
    session: AsyncSession,
    *,
    skill_id: uuid.UUID,
    node_cap: int = 200,
    include_non_public: bool = False,
) -> VaultGraphPreview | None:
    """Compute the persona vault-graph preview.

    Nodes are the persona's neurons (up to ``node_cap``). Edges are read
    from the latest released ``SkillVersion`` body's frontmatter
    ``links:`` field for each neuron. Where a link's ``target`` resolves
    to a sibling neuron, it stays within the persona; where it points at
    a parent-occupation skill, the target node carries ``from_base=True``.
    """
    res = await session.execute(
        select(Skill, Persona)
        .join(Persona, Persona.skill_id == Skill.id)
        .where(Skill.id == skill_id)
        .where(Skill.kind == SkillKind.PERSONA)
    )
    row = res.first()
    if row is None:
        return None
    skill, _persona = row
    if not include_non_public and skill.status != SkillStatus.PUBLISHED:
        return None

    neurons_res = await session.execute(
        select(PersonaNeuron, Skill)
        .join(Skill, Skill.id == PersonaNeuron.neuron_skill_id)
        .options(selectinload(Skill.versions))
        .where(PersonaNeuron.persona_id == skill_id)
        .order_by(PersonaNeuron.sort_order.asc(), Skill.slug.asc())
    )
    all_neurons = neurons_res.all()
    truncated = len(all_neurons) > node_cap
    kept = all_neurons[:node_cap]

    nodes: list[GraphNode] = []
    node_ids: set[str] = set()
    for membership, neuron in kept:
        node = GraphNode(
            id=neuron.slug,
            label=neuron.name,
            kind=neuron.kind,
            section=membership.section,
            skill_id=neuron.id,
            from_base=False,
        )
        nodes.append(node)
        node_ids.add(node.id)

    edges: list[GraphEdge] = []
    base_targets: set[str] = set()
    for _membership, neuron in kept:
        version = _pick_latest_released(neuron.versions)
        if version is None:
            continue
        try:
            links = await _read_links_from_storage(version)
        except Exception:  # pragma: no cover — storage flakes don't break preview
            log.exception("graph_preview.link_read_failed", extra={
                "skill_id": str(neuron.id),
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
            target_str = str(target)
            # ``base/<slug>`` is the spec's convention for cross-vault refs.
            if target_str.startswith("base/") and target_str not in node_ids:
                base_targets.add(target_str)
            edges.append(
                GraphEdge(
                    source=neuron.slug,
                    target=target_str,
                    relation=str(relation),
                    weight=float(weight) if isinstance(weight, (int, float)) else None,
                )
            )

    for target in sorted(base_targets):
        nodes.append(
            GraphNode(
                id=target,
                label=target.split("/", 1)[-1],
                kind=SkillKind.SKILL,
                section=None,
                skill_id=None,
                from_base=True,
            )
        )

    return VaultGraphPreview(
        persona_id=skill.id,
        persona_slug=skill.slug,
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

    Wave 3 (T-06): wired to ``src.vault.jobs.enqueue_persona_build``.
    In ``ENV=test`` the façade runs the builder inline on the caller's
    session so the build is part of the request's transaction; in
    production the façade dispatches to Arq and the worker runs the
    build in a fresh DB session.
    """
    parent = await session.get(Skill, skill_id)
    parent = _ownership_or_404(parent, creator)
    persona = await session.get(Persona, skill_id)
    if persona is None:  # pragma: no cover
        raise PersonaError(
            code="persona.not_found",
            message="Persona not found.",
            status_code=404,
        )

    neuron_count = await _refresh_neuron_count(session, skill_id)
    if neuron_count == 0:
        raise PersonaError(
            code="persona.no_neurons",
            message=(
                "Cannot build a persona with zero neurons. Add at least one "
                "kind=memory_neuron via the capture flow first."
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
        raise PersonaError(
            code="persona.version_not_found",
            message=f"Version {version} not found on this persona.",
            status_code=404,
        )

    # Local import to avoid an import cycle (vault.builder imports from
    # personas.models; service-side handle stays late-bound).
    from src.vault import jobs as vault_jobs  # noqa: PLC0415 — break circular import
    from src.vault.builder import VaultBuildError  # noqa: PLC0415  # circular import

    try:
        result = await vault_jobs.enqueue_persona_build(
            session, skill_id=skill_id, version=version
        )
    except VaultBuildError as exc:
        raise PersonaError(
            code=exc.code,
            message=exc.message,
            status_code=422,
        ) from exc

    await write_audit(
        session,
        actor_id=creator.id,
        action="persona.build_queued",
        target_type="persona",
        target_id=skill_id,
        metadata={
            "version": version,
            "skill_version_id": str(target.id),
            "job_id": result.job_id,
            "build_id": str(result.build_id) if result.build_id else None,
            "neuron_count": neuron_count,
        },
    )
    await session.flush()
    return JobAccepted(
        job_id=result.job_id,
        build_id=result.build_id,
        status=result.status,
    )


async def publish_persona(
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
        raise PersonaError(
            code="persona.version_not_found",
            message=f"Version {payload.version} not found on this persona.",
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
        action="persona.published",
        target_type="persona",
        target_id=skill_id,
        metadata={"version": payload.version, "job_id": job.job_id},
    )
    await session.flush()
    return job


__all__ = [
    "PersonaCheckoutGate",
    "PersonaError",
    "PersonaFilters",
    "check_persona_checkout_entitlement",
    "create_persona",
    "get_graph_preview",
    "get_persona_detail",
    "list_persona_neurons",
    "list_personas",
    "publish_persona",
    "remove_neuron",
    "reorder_neurons",
    "trigger_build",
    "update_persona",
]
