"""Pydantic v2 schemas for users + creator profiles + API tokens."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.users.models import UserRole


class UserRead(BaseModel):
    """The shape of ``/v1/auth/me`` and similar."""

    id: uuid.UUID
    email: EmailStr
    display_name: str | None = None
    avatar_url: str | None = None
    role: UserRole
    is_creator_verified: bool
    is_admin: bool
    is_verified: bool
    is_active: bool
    stripe_customer_id: str | None = None
    stripe_connect_account_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Registration payload."""

    email: EmailStr
    password: str = Field(min_length=12, max_length=256)
    display_name: str | None = Field(default=None, max_length=120)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "jane@example.com",
                    "password": "correct horse battery staple",
                    "display_name": "Jane Doe",
                }
            ]
        }
    )


class UserUpdate(BaseModel):
    """PATCH /v1/auth/me payload."""

    display_name: str | None = Field(default=None, max_length=120)
    avatar_url: str | None = None


class CreatorProfileRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    handle: str
    bio: str | None = None
    website_url: str | None = None
    social: dict[str, Any] | None = None
    industries: list[str] | None = None
    payout_country: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BecomeCreatorRequest(BaseModel):
    """``POST /v1/auth/become-creator`` payload."""

    handle: str = Field(min_length=3, max_length=64, pattern=r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")
    payout_country: str = Field(min_length=2, max_length=2, pattern=r"^[A-Z]{2}$")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"handle": "janedoe", "payout_country": "US"}]
        }
    )


# ── API tokens ────────────────────────────────────────────────────────
class ApiTokenCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    scopes: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None


class ApiTokenRead(BaseModel):
    id: uuid.UUID
    name: str
    prefix: str
    scopes: list[str] | None
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ApiTokenCreated(ApiTokenRead):
    """One-time response containing the plaintext token."""

    token: str = Field(description="The plaintext token. Shown ONCE.")


# ── Public creator profile (Phase 1) ──────────────────────────────────
# See ``prompts/marketplace/02-skill-detail.md``.


class CreatorStats(BaseModel):
    total_skills: int = 0
    total_sales: int = 0
    rating_avg: float | None = None


class CreatorProfilePublic(BaseModel):
    """Public ``/v1/creators/{handle}`` payload."""

    handle: str
    display_name: str | None = None
    avatar_url: str | None = None
    bio_md: str | None = None
    website_url: str | None = None
    social: dict[str, Any] = Field(default_factory=dict)
    industries: list[str] = Field(default_factory=list)
    is_verified: bool = False
    stats: CreatorStats

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "ApiTokenCreate",
    "ApiTokenCreated",
    "ApiTokenRead",
    "BecomeCreatorRequest",
    "CreatorProfilePublic",
    "CreatorProfileRead",
    "CreatorStats",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]
