"""``reviews`` table.

See ``02-data-model-core.md``. Unique constraint on ``(skill_id, author_id)``
keeps the "one-review-per-buyer-per-skill" invariant.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base, uuid7

_UUID = PG_UUID(as_uuid=True).with_variant(String(36), "sqlite")


class ReviewStatus(str, enum.Enum):
    VISIBLE = "visible"
    HIDDEN = "hidden"
    FLAGGED = "flagged"


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    skill_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    license_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("licenses.id", ondelete="RESTRICT"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    body_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="review_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ReviewStatus.VISIBLE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("skill_id", "author_id", name="uq_reviews_skill_author"),
        Index("ix_reviews_skill_status_created", "skill_id", "status", "created_at"),
    )


__all__ = ["Review", "ReviewStatus"]
