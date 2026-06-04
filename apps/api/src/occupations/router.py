"""``/v1/occupations`` router — creator + public endpoints.

Per ``team/02-api-surface.md`` §1 and T-03 acceptance in
``team/05-mvp-plan.md``. Routers parse + delegate + return; all business
logic lives in :mod:`src.occupations.service`.

The orchestrator mounts this router in ``apps/api/src/main.py`` after
Wave 2 returns (do not touch ``main.py`` from this module).
"""

from __future__ import annotations

import logging
import uuid  # noqa: TC003  (FastAPI needs the type at runtime for path params)
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select as sa_select
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002  (FastAPI dep)

from src.auth.deps import get_optional_user, require_creator
from src.core.db import get_db
from src.core.errors import error_responses
from src.occupations import service
from src.occupations.schemas import (
    JobAccepted,
    OccupationBuildRequest,
    OccupationCreate,
    OccupationDetailResponse,
    OccupationListResponse,
    OccupationRead,
    OccupationSkillList,
    OccupationSkillRead,
    OccupationSkillsBulkSet,
    OccupationSkillUpsert,
    OccupationUpdate,
    PublishRequest,
    VaultGraphPreview,
)
from src.skills.models import Skill
from src.users.models import User  # noqa: TC001  (FastAPI dep)

log = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/occupations", tags=["occupations"])


# ── Inline body shape for the reorder endpoint ────────────────────────


class _ReorderItem(BaseModel):
    member_skill_id: uuid.UUID
    sort_order: int = Field(ge=0)

    model_config = ConfigDict(extra="forbid")


class _ReorderRequest(BaseModel):
    items: list[_ReorderItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


# ── Creator endpoints ─────────────────────────────────────────────────


@router.post(
    "",
    response_model=OccupationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an occupation",
    responses=error_responses(401, 403, 409, 422),
)
async def create_occupation_endpoint(
    payload: OccupationCreate,
    response: Response,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OccupationRead:
    out = await service.create_occupation(
        session, creator=creator, payload=payload
    )
    await session.commit()
    response.headers["Location"] = f"/v1/occupations/{out.id}"
    return out


@router.patch(
    "/{skill_id}",
    response_model=OccupationRead,
    summary="Update an occupation listing or metadata",
    responses=error_responses(401, 403, 404, 422),
)
async def patch_occupation(
    skill_id: uuid.UUID,
    payload: OccupationUpdate,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OccupationRead:
    out = await service.update_occupation(
        session, creator=creator, skill_id=skill_id, patch=payload
    )
    await session.commit()
    return out


@router.post(
    "/{skill_id}/skills",
    response_model=OccupationSkillList,
    summary="Bulk-set the membership of an occupation",
    responses=error_responses(401, 403, 404, 422),
)
async def bulk_set_members_endpoint(
    skill_id: uuid.UUID,
    payload: OccupationSkillsBulkSet,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OccupationSkillList:
    out = await service.bulk_set_members(
        session, creator=creator, skill_id=skill_id, items=payload.items
    )
    await session.commit()
    return out


@router.post(
    "/{skill_id}/skills/{member_skill_id}",
    response_model=OccupationSkillRead,
    summary="Add or update a single member skill",
    responses=error_responses(401, 403, 404, 422),
)
async def upsert_member_endpoint(
    skill_id: uuid.UUID,
    member_skill_id: uuid.UUID,
    payload: OccupationSkillUpsert,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OccupationSkillRead:
    out = await service.add_or_update_member(
        session,
        creator=creator,
        skill_id=skill_id,
        member_skill_id=member_skill_id,
        payload=payload,
    )
    await session.commit()
    return out


@router.delete(
    "/{skill_id}/skills/{member_skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a member skill from an occupation",
    responses=error_responses(401, 403, 404),
)
async def remove_member_endpoint(
    skill_id: uuid.UUID,
    member_skill_id: uuid.UUID,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await service.remove_member(
        session,
        creator=creator,
        skill_id=skill_id,
        member_skill_id=member_skill_id,
    )
    await session.commit()


@router.patch(
    "/{skill_id}/skills/order",
    response_model=OccupationSkillList,
    summary="Reorder member skills",
    responses=error_responses(401, 403, 404, 422),
)
async def reorder_members_endpoint(
    skill_id: uuid.UUID,
    payload: _ReorderRequest,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OccupationSkillList:
    order = [(i.member_skill_id, i.sort_order) for i in payload.items]
    out = await service.reorder_members(
        session, creator=creator, skill_id=skill_id, order=order
    )
    await session.commit()
    return out


@router.post(
    "/{skill_id}/build",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueue a vault build for this occupation",
    responses=error_responses(401, 403, 404, 422),
)
async def build_occupation_endpoint(
    skill_id: uuid.UUID,
    payload: OccupationBuildRequest,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobAccepted:
    out = await service.trigger_build(
        session, creator=creator, skill_id=skill_id, version=payload.version
    )
    await session.commit()
    return out


@router.post(
    "/{skill_id}/publish",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Publish an occupation (queues a build and marks released)",
    responses=error_responses(401, 403, 404, 422),
)
async def publish_occupation_endpoint(
    skill_id: uuid.UUID,
    payload: PublishRequest,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobAccepted:
    out = await service.publish_occupation(
        session, creator=creator, skill_id=skill_id, payload=payload
    )
    await session.commit()
    return out


# ── Public reader endpoints ───────────────────────────────────────────


@router.get(
    "",
    response_model=OccupationListResponse,
    summary="List published occupations",
    responses=error_responses(400, 422),
)
async def list_occupations_endpoint(
    session: Annotated[AsyncSession, Depends(get_db)],
    category: str | None = Query(default=None, max_length=64),
    domain: str | None = Query(default=None, max_length=120),
    q: str | None = Query(default=None, max_length=200),
    creator_handle: str | None = Query(default=None, max_length=64),
    order: str | None = Query(
        default=None, description="Sort: 'newest' (default) or 'oldest'."
    ),
    limit: int | None = Query(default=None, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> OccupationListResponse:
    filters = service.OccupationFilters(
        category=category,
        domain=domain,
        q=q,
        creator_handle=creator_handle,
        order=order,
        limit=limit,
        cursor=cursor,
    )
    items, page = await service.list_occupations(session, filters)
    return OccupationListResponse(items=items, page=page)


# NOTE on route ordering: the more-specific two-segment routes
# (`/{skill_id}/graph-preview`, `/{skill_id}/builds`, etc.) MUST be
# declared before `/{handle}/{slug}` — both match the shape
# `/{seg1}/{seg2}` and FastAPI picks the first registration. Single-
# segment id lookup is registered after the handle/slug pair so a path
# like `/{handle}/{slug}` (two segments) doesn't shadow it.


@router.get(
    "/{skill_id}/graph-preview",
    response_model=VaultGraphPreview,
    summary="Vault-graph preview for the marketplace detail page",
    responses=error_responses(404),
)
async def graph_preview_endpoint(
    skill_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_user)],
) -> VaultGraphPreview:
    preview = await service.get_graph_preview(session, skill_id=skill_id)
    if preview is None and user is not None:
        # Owner / admin: include the draft graph.
        row = (
            await session.execute(sa_select(Skill).where(Skill.id == skill_id))
        ).scalar_one_or_none()
        if row is not None and (
            str(row.creator_id) == str(user.id) or user.is_admin
        ):
            preview = await service.get_graph_preview(
                session, skill_id=skill_id, include_non_public=True
            )
    if preview is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "occupation.not_found",
                "message": "Occupation not found.",
            },
        )
    return preview


@router.get(
    "/{handle}/{slug}",
    response_model=OccupationDetailResponse,
    summary="Get an occupation by {handle}/{slug}",
    responses=error_responses(404),
)
async def get_occupation_by_handle(
    handle: str,
    slug: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_user)],
) -> OccupationDetailResponse:
    # Owners + admins see drafts; everyone else only sees published.
    include_non_public = user is not None and user.is_admin
    detail = await service.get_occupation_detail(
        session,
        handle=handle,
        slug=slug,
        include_non_public=include_non_public,
    )
    if detail is None and user is not None:
        # Try as owner — handle may belong to caller.
        candidate = await service.get_occupation_detail(
            session,
            handle=handle,
            slug=slug,
            include_non_public=True,
        )
        if candidate is not None:
            row = (
                await session.execute(
                    sa_select(Skill).where(Skill.id == candidate.skill_id)
                )
            ).scalar_one_or_none()
            if row is not None and (
                str(row.creator_id) == str(user.id) or user.is_admin
            ):
                detail = candidate

    if detail is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "occupation.not_found",
                "message": "Occupation not found.",
            },
        )
    return detail


@router.get(
    "/{skill_id}",
    response_model=OccupationDetailResponse,
    summary="Get an occupation by id",
    responses=error_responses(404),
)
async def get_occupation_by_id(
    skill_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_user)],
) -> OccupationDetailResponse:
    # First try the public path. If that misses and the caller owns the
    # row, return the draft.
    detail = await service.get_occupation_detail(session, skill_id=skill_id)
    if detail is None and user is not None:
        candidate = await service.get_occupation_detail(
            session, skill_id=skill_id, include_non_public=True
        )
        if candidate is not None:
            row = (
                await session.execute(sa_select(Skill).where(Skill.id == skill_id))
            ).scalar_one_or_none()
            if row is not None and (
                str(row.creator_id) == str(user.id) or user.is_admin
            ):
                detail = candidate

    if detail is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "occupation.not_found",
                "message": "Occupation not found.",
            },
        )
    return detail


__all__ = ["router"]
