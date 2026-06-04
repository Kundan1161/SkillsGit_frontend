"""``users`` and ``creator_profiles`` tables.

See ``02-data-model-core.md`` for the canonical schema.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    CHAR,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import (
    ARRAY as PG_ARRAY,
    CITEXT,
    JSONB,
    UUID as PG_UUID,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base, SoftDeleteMixin, TimestampMixin, uuid7

if TYPE_CHECKING:
    from src.skills.models import Skill


class UserRole(str, enum.Enum):
    """Primary role for UX defaults. Authorization is capability-based."""

    BUYER = "buyer"
    CREATOR = "creator"
    ADMIN = "admin"


# Cross-dialect helpers ────────────────────────────────────────────────
# Tests run on sqlite (aiosqlite); production on postgres. ``citext`` and
# ``ARRAY`` are postgres-only — fall back to plain types on sqlite via
# ``with_variant`` so models import in both engines.
_UUID = PG_UUID(as_uuid=True).with_variant(String(36), "sqlite")
_CITEXT = CITEXT().with_variant(String(255), "sqlite")
_STR_ARRAY = PG_ARRAY(String).with_variant(JSON(), "sqlite")


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)

    # fastapi-users baseline columns
    email: Mapped[str] = mapped_column(_CITEXT, nullable=False, unique=True)
    hashed_password: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Application-specific
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.BUYER,
    )
    is_creator_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    stripe_customer_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    stripe_connect_account_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    # Cached from Stripe's ``account.payouts_enabled``; refreshed on
    # ``account.updated`` webhook + when the creator hits the status endpoint.
    # Gated by ``billing.checkout`` — paid skills can't be listed without it.
    payouts_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Relationships
    creator_profile: Mapped["CreatorProfile | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    api_tokens: Mapped[list["ApiToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    skills: Mapped[list["Skill"]] = relationship(
        back_populates="creator",
        cascade="all, delete-orphan",
        foreign_keys="Skill.creator_id",
    )

    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
        Index("ix_users_role", "role"),
    )


class CreatorProfile(Base, TimestampMixin):
    __tablename__ = "creator_profiles"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    handle: Mapped[str] = mapped_column(_CITEXT, nullable=False, unique=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    website_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    social: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    industries: Mapped[list[str] | None] = mapped_column(_STR_ARRAY, nullable=True)
    payout_country: Mapped[str | None] = mapped_column(CHAR(2), nullable=True)

    user: Mapped[User] = relationship(back_populates="creator_profile")

    __table_args__ = (
        Index("ix_creator_profiles_handle", "handle", unique=True),
    )


class ApiToken(Base):
    """Issued from the creator dashboard for programmatic access.

    Spec: ``shared/auth.md`` → ``api_tokens`` table.
    """

    __tablename__ = "api_tokens"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(1024), nullable=False)
    prefix: Mapped[str] = mapped_column(String(32), nullable=False)
    scopes: Mapped[list[str] | None] = mapped_column(_STR_ARRAY, nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="api_tokens")

    __table_args__ = (
        Index("ix_api_tokens_user_id", "user_id"),
        Index("ix_api_tokens_prefix", "prefix"),
        UniqueConstraint("prefix", name="uq_api_tokens_prefix"),
    )


__all__ = ["ApiToken", "CreatorProfile", "User", "UserRole"]
