"""``moderation_actions`` table.

Spec: ``prompts/marketplace/05-trust-and-quality.md`` § Action log.
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
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base, uuid7

_UUID = PG_UUID(as_uuid=True).with_variant(String(36), "sqlite")
_JSONB = JSON().with_variant(JSONB, "postgresql")


class ModerationAction(Base):
    """Moderator-friendly mirror of ``audit_log`` for trust-and-quality decisions."""

    __tablename__ = "moderation_actions"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    actor_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(_UUID, nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        _JSONB, nullable=True, name="metadata"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_moderation_actions_target", "target_type", "target_id"),
        Index("ix_moderation_actions_action", "action"),
    )


__all__ = ["ModerationAction"]
