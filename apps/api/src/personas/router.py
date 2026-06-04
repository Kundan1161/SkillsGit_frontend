"""``/v1/personas`` router — creator + public endpoints.

Per ``team/02-api-surface.md`` §2 and T-04 acceptance in
``team/05-mvp-plan.md``. Routers parse + delegate + return; all business
logic lives in :mod:`src.personas.service`.

The orchestrator mounts this router in ``apps/api/src/main.py`` after
Wave 2 returns (do not touch ``main.py`` from this module).
"""

from __future__ import annotations

import logging
import uuid  # noqa: TC003  (FastAPI needs the type at runtime for path params)
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select as sa_select
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002  (FastAPI dep)

from src.auth.deps import get_optional_user, require_creator
from src.core.db import get_db
from src.core.errors import error_responses
from src.personas import service
from src.personas.schemas import (
    JobAccepted,
    NeuronOrderUpdate,
    PersonaBuildRequest,
    PersonaCreate,
    PersonaDetailResponse,
    PersonaListResponse,
    PersonaNeuronList,
    PersonaRead,
    PersonaUpdate,
    PublishRequest,
    VaultGraphPreview,
)
from src.skills.models import Skill
from src.users.models import User  # noqa: TC001  (FastAPI dep)

log = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/personas", tags=["personas"])


# ── Creator endpoints ─────────────────────────────────────────────────


@router.post(
    "",
    response_model=PersonaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a persona",
    responses=error_responses(401, 403, 409, 422),
)
async def create_persona_endpoint(
    payload: PersonaCreate,
    response: Response,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> PersonaRead:
    out = await service.create_persona(
        session, creator=creator, payload=payload
    )
    await session.commit()
    response.headers["Location"] = f"/v1/personas/{out.id}"
    return out


@router.patch(
    "/{skill_id}",
    response_model=PersonaRead,
    summary="Update a persona listing or metadata",
    responses=error_responses(401, 403, 404, 409, 422),
)
async def patch_persona(
    skill_id: uuid.UUID,
    payload: PersonaUpdate,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> PersonaRead:
    out = await service.update_persona(
        session, creator=creator, skill_id=skill_id, patch=payload
    )
    await session.commit()
    return out


@router.post(
    "/{skill_id}/neurons/order",
    response_model=PersonaNeuronList,
    summary="Reorder a persona's neurons",
    responses=error_responses(401, 403, 404, 422),
)
async def reorder_neurons_endpoint(
    skill_id: uuid.UUID,
    payload: NeuronOrderUpdate,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> PersonaNeuronList:
    out = await service.reorder_neurons(
        session, creator=creator, skill_id=skill_id, items=payload.items
    )
    await session.commit()
    return out


@router.delete(
    "/{skill_id}/neurons/{neuron_skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a neuron from a persona",
    responses=error_responses(401, 403, 404),
)
async def remove_neuron_endpoint(
    skill_id: uuid.UUID,
    neuron_skill_id: uuid.UUID,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await service.remove_neuron(
        session,
        creator=creator,
        skill_id=skill_id,
        neuron_skill_id=neuron_skill_id,
    )
    await session.commit()


@router.post(
    "/{skill_id}/build",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueue a vault build for this persona",
    responses=error_responses(401, 403, 404, 422),
)
async def build_persona_endpoint(
    skill_id: uuid.UUID,
    payload: PersonaBuildRequest,
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
    summary="Publish a persona (queues a build and marks released)",
    responses=error_responses(401, 403, 404, 422),
)
async def publish_persona_endpoint(
    skill_id: uuid.UUID,
    payload: PublishRequest,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobAccepted:
    out = await service.publish_persona(
        session, creator=creator, skill_id=skill_id, payload=payload
    )
    await session.commit()
    return out


# ── Public reader endpoints ───────────────────────────────────────────


@router.get(
    "",
    response_model=PersonaListResponse,
    summary="List published personas",
    responses=error_responses(400, 422),
)
async def list_personas_endpoint(
    session: Annotated[AsyncSession, Depends(get_db)],
    parent_occupation_id: Annotated[
        uuid.UUID | None,
        Query(description="Filter to personas with this parent occupation."),
    ] = None,
    creator_handle: str | None = Query(default=None, max_length=64),
    q: str | None = Query(default=None, max_length=200),
    order: str | None = Query(
        default=None, description="Sort: 'newest' (default) or 'oldest'."
    ),
    limit: int | None = Query(default=None, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> PersonaListResponse:
    filters = service.PersonaFilters(
        parent_occupation_id=parent_occupation_id,
        creator_handle=creator_handle,
        q=q,
        order=order,
        limit=limit,
        cursor=cursor,
    )
    items, page = await service.list_personas(session, filters)
    return PersonaListResponse(items=items, page=page)


# NOTE on route ordering: the more-specific two-segment routes
# (`/{skill_id}/graph-preview`, `/{skill_id}/neurons`, etc.) MUST be
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
                "code": "persona.not_found",
                "message": "Persona not found.",
            },
        )
    return preview


@router.get(
    "/{skill_id}/neurons",
    response_model=PersonaNeuronList,
    summary="List a persona's neurons (entitlement-gated)",
    responses=error_responses(404),
)
async def list_neurons_endpoint(
    skill_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_user)],
    section: str | None = Query(default=None, max_length=120),
    limit: int | None = Query(default=None, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> PersonaNeuronList:
    """Return full neuron bodies for license-holders.

    Per ``02-api-surface.md`` §2: non-entitled callers get 404 (not 403)
    to avoid existence leak. The service returns ``None`` for both
    "persona doesn't exist" and "caller not entitled" — both render as
    the same 404 body here.

    ``cursor`` accepted for API parity; the current persona scale (≤10
    neurons per persona at MVP) does not page. A real cursor lands
    alongside the discovery refactor in Wave 4.
    """
    del cursor  # accepted for API parity; not implemented at MVP scale.
    caller_id = user.id if user is not None else None
    out = await service.list_persona_neurons(
        session,
        skill_id=skill_id,
        caller_id=caller_id,
        section=section,
        limit=limit,
    )
    if out is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "persona.not_found",
                "message": "Persona not found.",
            },
        )
    return out


@router.get(
    "/{handle}/{slug}",
    response_model=PersonaDetailResponse,
    summary="Get a persona by {handle}/{slug}",
    responses=error_responses(404),
)
async def get_persona_by_handle(
    handle: str,
    slug: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_user)],
) -> PersonaDetailResponse:
    # Owners + admins see drafts; everyone else only sees published.
    include_non_public = user is not None and user.is_admin
    caller_id = user.id if user is not None else None
    detail = await service.get_persona_detail(
        session,
        handle=handle,
        slug=slug,
        include_non_public=include_non_public,
        caller_id=caller_id,
    )
    if detail is None and user is not None:
        # Try as owner — handle may belong to caller.
        candidate = await service.get_persona_detail(
            session,
            handle=handle,
            slug=slug,
            include_non_public=True,
            caller_id=caller_id,
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
                "code": "persona.not_found",
                "message": "Persona not found.",
            },
        )
    return detail


@router.get(
    "/{skill_id}",
    response_model=PersonaDetailResponse,
    summary="Get a persona by id",
    responses=error_responses(404),
)
async def get_persona_by_id(
    skill_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User | None, Depends(get_optional_user)],
) -> PersonaDetailResponse:
    caller_id = user.id if user is not None else None
    # First try the public path. If that misses and the caller owns the
    # row, return the draft.
    detail = await service.get_persona_detail(
        session, skill_id=skill_id, caller_id=caller_id
    )
    if detail is None and user is not None:
        candidate = await service.get_persona_detail(
            session,
            skill_id=skill_id,
            include_non_public=True,
            caller_id=caller_id,
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
                "code": "persona.not_found",
                "message": "Persona not found.",
            },
        )
    return detail


__all__ = ["router"]
