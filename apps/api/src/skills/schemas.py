"""Pydantic schemas for skill listings, versions, categories.

Phase 0 keeps these read-only and minimal. CRUD schemas (publish payloads,
draft updates) land alongside the catalog/creator routers in later phases.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from src.skills.models import PricingModel, SkillStatus


class CategoryRead(BaseModel):
    slug: str
    name: str
    description: str | None = None
    parent_slug: str | None = None
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class SkillRead(BaseModel):
    id: uuid.UUID
    creator_id: uuid.UUID
    slug: str
    name: str
    tagline: str | None = None
    description_md: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    cover_image_url: str | None = None
    screenshots: list[str] | None = None
    status: SkillStatus
    latest_version_id: uuid.UUID | None = None
    pricing_model: PricingModel
    one_time_price_cents: int | None = None
    subscription_price_cents: int | None = None
    support_included: bool
    total_sales: int
    rating_avg: Decimal | None = None
    rating_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillVersionRead(BaseModel):
    id: uuid.UUID
    skill_id: uuid.UUID
    version: str
    content_hash: str
    storage_url: str
    changelog_md: str | None
    released_at: datetime | None
    is_yanked: bool

    model_config = ConfigDict(from_attributes=True)


__all__ = ["CategoryRead", "SkillRead", "SkillVersionRead"]
