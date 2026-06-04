"""Public read-only ``/v1/skills/{...}`` endpoints (detail + versions).

Owned by the catalog module so Agent C's write endpoints in
``src/skills/router.py`` stay isolated. Mounted under ``/v1/skills`` with
the same tag so OpenAPI shows them together.

Spec: ``prompts/marketplace/02-skill-detail.md``.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog import service
from src.catalog.schemas import (
    SkillDetail,
    VersionList,
    VersionPreview,
)
from src.core.db import get_db
from src.core.errors import error_responses
from src.skills.models import Skill, SkillStatus

router = APIRouter(prefix="/v1/skills", tags=["skills"])


def _split_handle_slug(id_or_slug: str) -> tuple[str, str] | None:
    """``{handle}/{slug}`` or URL-encoded variant."""
    raw = id_or_slug.replace("%2F", "/").replace("%2f", "/")
    if "/" not in raw:
        return None
    parts = raw.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None
    return parts[0], parts[1]


@router.get(
    "/by-handle/{handle}/{slug}",
    response_model=SkillDetail,
    summary="Get a skill by {handle}/{slug}",
    responses=error_responses(404),
)
async def get_skill_by_handle(
    handle: str,
    slug: str,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SkillDetail:
    detail = await service.fetch_skill_detail(session, handle=handle, slug=slug)
    if detail is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    if detail.status == SkillStatus.UNLISTED.value:
        response.headers["X-Robots-Tag"] = "noindex"
    return detail


@router.get(
    "/{id_or_slug}",
    response_model=SkillDetail,
    summary="Get a skill by UUID or URL-encoded {handle}/{slug}",
    responses=error_responses(404),
)
async def get_skill(
    id_or_slug: str,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SkillDetail:
    # Try UUID first.
    detail: SkillDetail | None = None
    try:
        skill_id = uuid.UUID(id_or_slug)
        detail = await service.fetch_skill_detail(session, skill_id=skill_id)
    except ValueError:
        pair = _split_handle_slug(id_or_slug)
        if pair is None:
            raise HTTPException(
                status_code=404,
                detail={"code": "skill.not_found", "message": "Skill not found."},
            ) from None
        handle, slug = pair
        detail = await service.fetch_skill_detail(session, handle=handle, slug=slug)

    if detail is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    # Unlisted skills are reachable by direct URL but not indexable.
    if detail.status == SkillStatus.UNLISTED.value:
        response.headers["X-Robots-Tag"] = "noindex"
    return detail


@router.get(
    "/{skill_id}/versions",
    response_model=VersionList,
    summary="List versions for a skill (newest first)",
    responses=error_responses(404),
)
async def list_skill_versions(
    skill_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: int | None = Query(default=None, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> VersionList:
    # Ensure the skill exists and is public.
    res = await session.execute(
        select(Skill).where(Skill.id == skill_id).where(
            Skill.status.in_([SkillStatus.PUBLISHED, SkillStatus.UNLISTED])
        )
    )
    if res.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    items, page = await service.list_versions(
        session, skill_id, limit=limit, cursor=cursor
    )
    return VersionList(items=items, page=page)


@router.get(
    "/{skill_id}/versions/{version}/preview",
    response_model=VersionPreview,
    summary="Get the public preview body for a specific version",
    responses=error_responses(404),
)
async def get_version_preview(
    skill_id: uuid.UUID,
    version: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> VersionPreview:
    # Skill must be public.
    res = await session.execute(
        select(Skill).where(Skill.id == skill_id).where(
            Skill.status.in_([SkillStatus.PUBLISHED, SkillStatus.UNLISTED])
        )
    )
    if res.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    version_row = await service.fetch_version(session, skill_id, version)
    if version_row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "skill_version.not_found", "message": "Version not found."},
        )
    preview = service.compute_preview_body(version_row.changelog_md or "")
    return VersionPreview(version=version, preview_body_md=preview)


__all__ = ["router"]
