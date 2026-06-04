"""``/v1/capture`` router — creator-scoped capture endpoints.

Per ``team/02-api-surface.md`` §3 and T-05 acceptance in
``team/05-mvp-plan.md``. Routers parse + delegate + return; all
business logic lives in :mod:`src.capture.service`.

The orchestrator mounts this router in ``apps/api/src/main.py`` after
Wave 2 returns (do not touch ``main.py`` from this module).
"""

from __future__ import annotations

import logging
import uuid  # noqa: TC003  (FastAPI needs the type at runtime for path params)
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002  (FastAPI dep)

from src.auth.deps import require_creator
from src.capture import service
from src.capture.models import CaptureSessionStatus  # noqa: TC001  (Query param type at runtime)
from src.capture.schemas import (
    Abandon,
    CaptureAttachmentRead,
    CaptureFinalize,
    CaptureSessionCreate,
    CaptureSessionListResponse,
    CaptureSessionRead,
    CaptureSessionUpdate,
    JobAccepted,
    NeuronCreated,
)
from src.core.db import get_db
from src.core.errors import error_responses
from src.users.models import User  # noqa: TC001  (FastAPI dep)

log = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/capture", tags=["capture"])


# ── Creator endpoints ─────────────────────────────────────────────────


@router.post(
    "/sessions",
    response_model=CaptureSessionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Open a capture session",
    responses=error_responses(401, 403, 404, 422),
)
async def create_session_endpoint(
    payload: CaptureSessionCreate,
    response: Response,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CaptureSessionRead:
    out = await service.create_session(session, creator=creator, payload=payload)
    await session.commit()
    response.headers["Location"] = f"/v1/capture/sessions/{out.id}"
    return out


@router.get(
    "/sessions",
    response_model=CaptureSessionListResponse,
    summary="List the creator's own capture sessions",
    responses=error_responses(401, 403),
)
async def list_sessions_endpoint(
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
    persona_id: Annotated[
        uuid.UUID | None,
        Query(description="Filter to a single persona."),
    ] = None,
    status_filter: Annotated[
        CaptureSessionStatus | None,
        Query(alias="status", description="Filter by lifecycle status."),
    ] = None,
    limit: int | None = Query(default=None, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> CaptureSessionListResponse:
    items, page = await service.list_sessions(
        session,
        creator=creator,
        filters=service.CaptureFilters(
            persona_id=persona_id,
            status=status_filter,
            limit=limit,
            cursor=cursor,
        ),
    )
    return CaptureSessionListResponse(items=items, page=page)


@router.get(
    "/sessions/{session_id}",
    response_model=CaptureSessionRead,
    summary="Read a capture session",
    responses=error_responses(401, 403, 404),
)
async def get_session_endpoint(
    session_id: uuid.UUID,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CaptureSessionRead:
    return await service.get_session(session, creator=creator, session_id=session_id)


@router.patch(
    "/sessions/{session_id}",
    response_model=CaptureSessionRead,
    summary="Patch a capture session (including the AI draft)",
    responses=error_responses(401, 403, 404, 409, 422),
)
async def patch_session_endpoint(
    session_id: uuid.UUID,
    payload: CaptureSessionUpdate,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CaptureSessionRead:
    out = await service.update_session(
        session, creator=creator, session_id=session_id, patch=payload
    )
    await session.commit()
    return out


@router.post(
    "/sessions/{session_id}/extract",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run the LLM extraction (queues an Arq job; runs sync under stub)",
    responses=error_responses(401, 403, 404, 409, 422, 429, 502),
)
async def extract_endpoint(
    session_id: uuid.UUID,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobAccepted:
    out = await service.enqueue_extract(
        session, creator=creator, session_id=session_id
    )
    await session.commit()
    return out


@router.post(
    "/sessions/{session_id}/finalize",
    response_model=NeuronCreated,
    status_code=status.HTTP_201_CREATED,
    summary="Publish the draft into the persona (atomic)",
    responses=error_responses(401, 403, 404, 409, 422, 502),
)
async def finalize_endpoint(
    session_id: uuid.UUID,
    payload: CaptureFinalize,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> NeuronCreated:
    out = await service.finalize_session(
        session, creator=creator, session_id=session_id, payload=payload
    )
    await session.commit()
    return out


@router.post(
    "/sessions/{session_id}/abandon",
    response_model=CaptureSessionRead,
    summary="Abandon a capture session",
    responses=error_responses(401, 403, 404, 409),
)
async def abandon_endpoint(
    session_id: uuid.UUID,
    payload: Abandon,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CaptureSessionRead:
    out = await service.abandon_session(
        session,
        creator=creator,
        session_id=session_id,
        reason=payload.reason,
    )
    await session.commit()
    return out


# ── Attachments ──────────────────────────────────────────────────────


@router.post(
    "/sessions/{session_id}/attachments",
    response_model=CaptureAttachmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a capture attachment",
    responses=error_responses(401, 403, 404, 409, 422, 502),
)
async def add_attachment_endpoint(
    session_id: uuid.UUID,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
    file: Annotated[UploadFile, File(...)],
) -> CaptureAttachmentRead:
    out = await service.add_attachment(
        session, creator=creator, session_id=session_id, upload=file
    )
    await session.commit()
    return out


@router.delete(
    "/sessions/{session_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a capture attachment",
    responses=error_responses(401, 403, 404),
)
async def remove_attachment_endpoint(
    session_id: uuid.UUID,
    attachment_id: uuid.UUID,
    creator: Annotated[User, Depends(require_creator)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await service.remove_attachment(
        session,
        creator=creator,
        session_id=session_id,
        attachment_id=attachment_id,
    )
    await session.commit()


__all__ = ["router"]
