"""Pydantic shapes returned by the delivery router."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.billing.models import LicenseSource, LicenseStatus, SupportTier
from src.core.pagination import PageInfo


class LicenseVersionInfo(BaseModel):
    """Snapshot of the version a license currently entitles the buyer to."""

    id: uuid.UUID
    version: str
    released_at: datetime | None
    is_yanked: bool

    model_config = ConfigDict(from_attributes=True)


class LicenseSkillInfo(BaseModel):
    """Minimal skill summary embedded in a license response."""

    id: uuid.UUID
    name: str
    slug: str
    creator_handle: str | None = None
    creator_display_name: str | None = None
    cover_image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LicenseRead(BaseModel):
    """Library list/detail entry."""

    id: uuid.UUID
    skill: LicenseSkillInfo
    source: LicenseSource
    status: LicenseStatus
    support_tier: SupportTier
    granted_at: datetime
    expires_at: datetime | None = None
    max_version: str | None = None
    current_version: LicenseVersionInfo | None = None
    last_downloaded_at: datetime | None = None
    download_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class LicenseList(BaseModel):
    items: list[LicenseRead] = Field(default_factory=list)
    page: PageInfo


class DownloadResponse(BaseModel):
    """``GET /v1/licenses/{id}/download`` payload."""

    download_url: str
    version: str
    expires_at: datetime
    content_hash: str


__all__ = [
    "DownloadResponse",
    "LicenseList",
    "LicenseRead",
    "LicenseSkillInfo",
    "LicenseVersionInfo",
]
