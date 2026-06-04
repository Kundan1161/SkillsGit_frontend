"""``editorial_picks`` and ``search_alerts`` tables.

Phase 1 — see ``prompts/marketplace/01-discovery.md``. Both tables are
catalog-owned (no other module reads or writes them).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base, uuid7

_UUID = PG_UUID(as_uuid=True).with_variant(String(36), "sqlite")
_JSONB = JSON().with_variant(JSONB, "postgresql")


class EditorialPick(Base):
    """Admin-curated featured rail (per 01-discovery.md §Pages → Home)."""

    __tablename__ = "editorial_picks"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    skill_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    slot: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        Index("ix_editorial_picks_skill_id", "skill_id"),
        Index("ix_editorial_picks_sort", "sort_order"),
    )


class SearchAlert(Base):
    """Saved-search row consumed by a nightly cron (Phase 1 persists only)."""

    __tablename__ = "search_alerts"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    query_json: Mapped[dict[str, Any]] = mapped_column(
        _JSONB, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (Index("ix_search_alerts_user_id", "user_id"),)


__all__ = ["EditorialPick", "SearchAlert"]
