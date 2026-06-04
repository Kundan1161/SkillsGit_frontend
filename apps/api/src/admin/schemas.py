"""Pydantic shapes for the admin/moderation surface."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.core.pagination import PageInfo
from src.skills.models import SkillStatus


class ModerationQueueItem(BaseModel):
    """Row in the moderation queue list."""

    skill_id: uuid.UUID
    name: str
    slug: str
    status: SkillStatus
    creator_handle: str | None
    creator_display_name: str | None
    submitted_version: str | None = None
    submitted_at: datetime | None = None
    rejection_reason: str | None = None
    cover_image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ModerationQueueList(BaseModel):
    items: list[ModerationQueueItem] = Field(default_factory=list)
    page: PageInfo


class ApprovalResponse(BaseModel):
    skill_id: uuid.UUID
    status: SkillStatus
    version: str | None
    moderation_action_id: uuid.UUID


class RejectRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=2000)


class AdminUserSummary(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str | None = None
    is_active: bool
    is_admin: bool
    is_creator_verified: bool
    creator_handle: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserList(BaseModel):
    items: list[AdminUserSummary] = Field(default_factory=list)
    page: PageInfo


__all__ = [
    "AdminUserList",
    "AdminUserSummary",
    "ApprovalResponse",
    "ModerationQueueItem",
    "ModerationQueueList",
    "RejectRequest",
]
