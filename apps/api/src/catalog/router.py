"""``/v1/catalog`` router — discovery, browse, search, featured.

Spec: ``prompts/marketplace/01-discovery.md``.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.deps import current_active_user, require_admin
from src.catalog import service
from src.catalog.models import EditorialPick, SearchAlert
from src.catalog.schemas import (
    CatalogSort,
    CategoryList,
    FeaturedCreate,
    FeaturedItem,
    FeaturedList,
    SearchAlertCreate,
    SearchAlertRead,
    SkillCardPage,
)
from src.core.db import get_db
from src.core.errors import error_responses
from src.users.models import User

router = APIRouter(prefix="/v1/catalog", tags=["catalog"])


# ── List / browse / search ───────────────────────────────────────────


@router.get(
    "/skills",
    response_model=SkillCardPage,
    summary="List published skills with filters, search, and sort",
    responses=error_responses(400, 422),
)
async def list_catalog_skills(
    session: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = Query(default=None, max_length=200, description="Free-text search."),
    categories: str | None = Query(default=None, description="CSV of category slugs."),
    pricing_models: str | None = Query(
        default=None,
        description="CSV of: free,one_time,subscription,freemium",
    ),
    min_price_cents: int | None = Query(default=None, ge=0),
    max_price_cents: int | None = Query(default=None, ge=0),
    required_models: str | None = Query(default=None, description="CSV of model IDs."),
    tags: str | None = Query(default=None, description="CSV of tags."),
    min_rating: float | None = Query(default=None, ge=0, le=5),
    creator_handle: str | None = Query(default=None, max_length=64),
    sort: CatalogSort = Query(default=CatalogSort.RELEVANCE),
    limit: int | None = Query(default=None, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> SkillCardPage:
    filters = service.CatalogFilters(
        q=q,
        categories=service._csv_list(categories),
        pricing_models=service._csv_list(pricing_models),
        min_price_cents=min_price_cents,
        max_price_cents=max_price_cents,
        required_models=service._csv_list(required_models),
        tags=service._csv_list(tags),
        min_rating=min_rating,
        creator_handle=creator_handle,
        sort=sort,
        limit=limit,
        cursor=cursor,
    )
    items, page = await service.list_skills(session, filters)
    return SkillCardPage(items=items, page=page)


# ── Categories ───────────────────────────────────────────────────────


@router.get(
    "/categories",
    response_model=CategoryList,
    summary="List categories with skill counts",
)
async def list_categories(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryList:
    items = await service.list_categories(session)
    return CategoryList(items=items)


# ── Featured ─────────────────────────────────────────────────────────


@router.get(
    "/featured",
    response_model=FeaturedList,
    summary="Editorial featured rail",
)
async def list_featured(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> FeaturedList:
    rows = await service.list_featured(session)
    items = [
        FeaturedItem(
            id=pick.id,
            slot=pick.slot,
            sort_order=pick.sort_order,
            starts_at=pick.starts_at,
            ends_at=pick.ends_at,
            skill=card,
        )
        for pick, card in rows
    ]
    return FeaturedList(items=items)


@router.post(
    "/featured",
    status_code=status.HTTP_201_CREATED,
    summary="Pin a skill into the featured rail (admin)",
    responses=error_responses(401, 403, 404),
)
async def create_featured(
    payload: FeaturedCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
) -> FeaturedItem:
    # Validate the skill exists.
    from src.skills.models import Skill

    res = await session.execute(select(Skill).where(Skill.id == payload.skill_id))
    skill = res.scalar_one_or_none()
    if skill is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    pick = EditorialPick(
        skill_id=payload.skill_id,
        slot=payload.slot,
        sort_order=payload.sort_order,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        created_by=_admin.id,
    )
    session.add(pick)
    await session.commit()
    await session.refresh(pick)
    # Invalidate the categories cache when featured changes too — same key.
    service._cache.pop("featured", None)
    # Build the embedded card.
    rows = await service.list_featured(session)
    card = next((c for (p, c) in rows if p.id == pick.id), None)
    if card is None:
        # Shouldn't happen; fall back to a minimal lookup
        raise HTTPException(
            status_code=500,
            detail={"code": "catalog.featured_assembly_failed", "message": "Failed to assemble featured item."},
        )
    return FeaturedItem(
        id=pick.id,
        slot=pick.slot,
        sort_order=pick.sort_order,
        starts_at=pick.starts_at,
        ends_at=pick.ends_at,
        skill=card,
    )


@router.delete(
    "/featured/{pick_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a featured pin (admin)",
    responses=error_responses(401, 403, 404),
)
async def delete_featured(
    pick_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
) -> None:
    res = await session.execute(select(EditorialPick).where(EditorialPick.id == pick_id))
    pick = res.scalar_one_or_none()
    if pick is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "featured.not_found", "message": "Featured pin not found."},
        )
    await session.delete(pick)
    await session.commit()


# ── Search alerts ────────────────────────────────────────────────────


@router.post(
    "/search-alerts",
    response_model=SearchAlertRead,
    status_code=status.HTTP_201_CREATED,
    summary="Save a search to receive future-match notifications",
    responses=error_responses(401, 422),
)
async def create_search_alert(
    payload: SearchAlertCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(current_active_user)],
) -> SearchAlertRead:
    query_json: dict[str, object] = dict(payload.filters)
    if payload.query:
        query_json["q"] = payload.query
    alert = SearchAlert(
        user_id=user.id, name=payload.name, query_json=query_json
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return SearchAlertRead.model_validate(alert)


__all__ = ["router"]
