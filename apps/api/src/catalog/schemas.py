"""Pydantic v2 schemas for ``/v1/catalog`` and skill-detail/creator endpoints.

Phase 1 — see ``prompts/marketplace/01-discovery.md`` and
``prompts/marketplace/02-skill-detail.md``.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.core.pagination import PageInfo

# ── Shared sub-shapes ─────────────────────────────────────────────────


class CreatorChipPublic(BaseModel):
    """The creator chip shape embedded in every list/detail response."""

    handle: str
    display_name: str | None = None
    avatar_url: str | None = None
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class SkillCardItem(BaseModel):
    """Lean shape used in every catalog rail/grid (see 01-discovery.md §APIs)."""

    id: uuid.UUID
    slug: str
    name: str
    tagline: str | None = None
    cover_image_url: str | None = None
    category: str | None = None
    description_snippet: str | None = None
    tags: list[str] = Field(default_factory=list)
    pricing_model: str
    one_time_price_cents: int | None = None
    subscription_price_cents: int | None = None
    rating_avg: float | None = None
    rating_count: int = 0
    total_sales: int = 0
    creator: CreatorChipPublic
    latest_version: str | None = None
    released_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "01928f7a-...",
                    "slug": "dcf-valuation",
                    "name": "DCF Valuation Pro",
                    "tagline": "Build a defensible discounted cash flow model.",
                    "cover_image_url": "https://cdn/.../dcf.png",
                    "category": "finance",
                    "description_snippet": "This is a comprehensive DCF model...",
                    "tags": ["dcf", "valuation"],
                    "pricing_model": "one_time",
                    "one_time_price_cents": 1900,
                    "subscription_price_cents": None,
                    "rating_avg": 4.7,
                    "rating_count": 23,
                    "total_sales": 412,
                    "creator": {
                        "handle": "janedoe",
                        "display_name": "Jane Doe",
                        "avatar_url": None,
                        "is_verified": True,
                    },
                    "latest_version": "1.2.0",
                    "released_at": "2026-05-01T12:00:00Z",
                }
            ]
        },
    )


class SkillCardPage(BaseModel):
    """Standard paged list response shape (``items`` + ``page``)."""

    items: list[SkillCardItem] = Field(default_factory=list)
    page: PageInfo


# ── Catalog list params ───────────────────────────────────────────────


class CatalogSort(str, enum.Enum):
    RELEVANCE = "relevance"
    NEWEST = "newest"
    TOP_RATED = "top_rated"
    MOST_SOLD = "most_sold"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"


class CategoryItem(BaseModel):
    slug: str
    name: str
    description: str | None = None
    parent_slug: str | None = None
    display_order: int = 0
    skill_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CategoryList(BaseModel):
    items: list[CategoryItem] = Field(default_factory=list)


# ── Featured (editorial picks) ────────────────────────────────────────


class FeaturedItem(BaseModel):
    id: uuid.UUID
    slot: str | None = None
    sort_order: int = 0
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    skill: SkillCardItem

    model_config = ConfigDict(from_attributes=True)


class FeaturedList(BaseModel):
    items: list[FeaturedItem] = Field(default_factory=list)


class FeaturedCreate(BaseModel):
    """Admin: pin a skill into the featured rail."""

    skill_id: uuid.UUID
    slot: str | None = Field(default=None, max_length=64)
    sort_order: int = 0
    starts_at: datetime | None = None
    ends_at: datetime | None = None


# ── Search alerts ────────────────────────────────────────────────────


class SearchAlertCreate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    query: str | None = Field(default=None, max_length=200)
    filters: dict[str, Any] = Field(default_factory=dict)


class SearchAlertRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str | None
    query_json: dict[str, Any]
    created_at: datetime
    last_notified_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# ── Skill detail (02-skill-detail.md) ────────────────────────────────


class SkillPricing(BaseModel):
    model: str
    one_time_price_cents: int | None = None
    subscription_price_cents: int | None = None
    currency: str = "USD"
    support_included: bool = False
    freemium_paired_with: uuid.UUID | None = None


class AiRequirements(BaseModel):
    required_models: list[str] = Field(default_factory=list)
    compatible_models: list[str] = Field(default_factory=list)
    tools_required: list[str] = Field(default_factory=list)
    min_context_tokens: int | None = None
    estimated_tokens_per_invocation: int | None = None


class LatestVersionInfo(BaseModel):
    id: uuid.UUID
    version: str
    released_at: datetime | None = None
    changelog_md: str | None = None


class SkillStats(BaseModel):
    rating_avg: float | None = None
    rating_count: int = 0
    total_sales: int = 0


class SkillDetail(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    tagline: str | None = None
    description_md: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    cover_image_url: str | None = None
    screenshots: list[str] = Field(default_factory=list)
    faq_md: str | None = None
    status: str
    pricing: SkillPricing
    ai_requirements: AiRequirements
    latest_version: LatestVersionInfo | None = None
    stats: SkillStats
    creator: CreatorChipPublic
    preview_body_md: str | None = None
    inspired_by_urls: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class VersionItem(BaseModel):
    id: uuid.UUID
    version: str
    released_at: datetime | None = None
    changelog_md: str | None = None
    is_yanked: bool = False
    yank_reason: str | None = None

    model_config = ConfigDict(from_attributes=True)


class VersionList(BaseModel):
    items: list[VersionItem] = Field(default_factory=list)
    page: PageInfo


class VersionPreview(BaseModel):
    version: str
    preview_body_md: str


__all__ = [
    "AiRequirements",
    "CatalogSort",
    "CategoryItem",
    "CategoryList",
    "CreatorChipPublic",
    "FeaturedCreate",
    "FeaturedItem",
    "FeaturedList",
    "LatestVersionInfo",
    "SearchAlertCreate",
    "SearchAlertRead",
    "SkillCardItem",
    "SkillCardPage",
    "SkillDetail",
    "SkillPricing",
    "SkillStats",
    "VersionItem",
    "VersionList",
    "VersionPreview",
]
