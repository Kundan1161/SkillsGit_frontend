"""Public ``/v1/users`` router.

Phase 0 keeps this minimal — auth handles ``/me``. Public creator profile
pages and creator listings land in Phase 1 alongside the catalog module.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.errors import error_responses

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.get(
    "/health",
    summary="Users module health (Phase 0 placeholder)",
    responses=error_responses(501),
)
async def users_health() -> dict[str, str]:
    """TODO Phase 1: public creator profile endpoints.

    See ``prompts/marketplace/02-skill-detail.md`` and
    ``prompts/marketplace/07-creator-dashboard.md``.
    """
    return {"status": "ok"}


# Placeholder endpoint to demonstrate the 501 stub pattern used elsewhere.
@router.get(
    "/{handle}",
    summary="Public creator profile (legacy users path — prefer /v1/creators)",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses=error_responses(501),
)
async def get_public_profile(handle: str) -> dict[str, str]:
    # Kept as a 501 stub for backward-compatibility; the canonical endpoint
    # lives at /v1/creators/{handle}. See ``creators_router`` below.
    raise HTTPException(
        status_code=501,
        detail={
            "code": "users.public_profile_moved",
            "message": "Use GET /v1/creators/{handle} instead.",
        },
    )


# ── /v1/creators — public profile + skills ────────────────────────────
# Spec: prompts/marketplace/02-skill-detail.md.
#
# Mounted as a separate router so the URL surface follows the spec
# (``/v1/creators/...``) without refactoring the existing /v1/users routes.

from src.catalog import service as _catalog_service  # noqa: E402
from src.catalog.schemas import CatalogSort, SkillCardPage  # noqa: E402
from src.users.models import CreatorProfile, User  # noqa: E402
from src.users.schemas import CreatorProfilePublic, CreatorStats  # noqa: E402

creators_router = APIRouter(prefix="/v1/creators", tags=["creators"])


async def _load_creator(
    session: AsyncSession, handle: str
) -> tuple[User, CreatorProfile]:
    stmt = (
        select(User, CreatorProfile)
        .join(CreatorProfile, CreatorProfile.user_id == User.id)
        .where(CreatorProfile.handle == handle)
    )
    res = await session.execute(stmt)
    row = res.first()
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "creator.not_found", "message": "Creator not found."},
        )
    user_obj, profile_obj = row
    return user_obj, profile_obj


@creators_router.get(
    "/{handle}",
    response_model=CreatorProfilePublic,
    summary="Public creator profile by handle",
    responses=error_responses(404),
)
async def get_creator_profile(
    handle: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CreatorProfilePublic:
    user, profile = await _load_creator(session, handle)
    stats_d = await _catalog_service.creator_stats(session, user.id)
    return CreatorProfilePublic(
        handle=profile.handle,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        bio_md=profile.bio,
        website_url=profile.website_url,
        social=profile.social or {},
        industries=list(profile.industries or []),
        is_verified=user.is_creator_verified,
        stats=CreatorStats(
            total_skills=stats_d["total_skills"],
            total_sales=stats_d["total_sales"],
            rating_avg=stats_d["rating_avg"],
        ),
    )


@creators_router.get(
    "/{handle}/skills",
    response_model=SkillCardPage,
    summary="Published skills for a creator (paginated)",
    responses=error_responses(404),
)
async def list_creator_skills(
    handle: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: int | None = Query(default=None, ge=1, le=100),
    cursor: str | None = Query(default=None),
    sort: CatalogSort = Query(default=CatalogSort.MOST_SOLD),
) -> SkillCardPage:
    user, _profile = await _load_creator(session, handle)
    filters = _catalog_service.CatalogFilters(
        creator_id=user.id,
        creator_handle=handle,
        sort=sort,
        limit=limit,
        cursor=cursor,
    )
    items, page = await _catalog_service.list_skills(session, filters)
    return SkillCardPage(items=items, page=page)
