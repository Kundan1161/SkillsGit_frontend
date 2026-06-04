"""CaptureSession + CaptureAttachment ORM models.

Per ``team/01-data-model-deltas.md`` §0008. Drafts live here, never
in ``skills`` — see ADR-015 in ``team/decisions.md``.
"""

from __future__ import annotations

import enum
import uuid  # noqa: TC003  (used at runtime via Mapped[uuid.UUID])
from datetime import datetime  # noqa: TC003  (Mapped[datetime] runtime use)
from typing import Any

from sqlalchemy import (
    CHAR,
    JSON,
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base, TimestampMixin, uuid7

_UUID = PG_UUID(as_uuid=True).with_variant(String(36), "sqlite")
_JSONB = JSON().with_variant(JSONB, "postgresql")


# `(str, enum.Enum)` matches the project-wide enum pattern in
# ``src/skills/models.py``; UP042 would have us use StrEnum (3.11+) but
# we keep the historical shape for consistency across modules.
class CaptureSessionStatus(str, enum.Enum):  # noqa: UP042
    """Lifecycle of a capture session.

    ``draft`` — creator is typing.
    ``extracting`` — LLM job is in flight.
    ``draft_ready`` — ``draft_md`` populated, awaiting human review.
    ``finalizing`` — promote-to-neuron transaction is running.
    ``finalized`` — neuron row created; ``finalized_neuron_skill_id`` set.
    ``abandoned`` — creator gave up; nothing reaches ``skills``.
    """

    DRAFT = "draft"
    EXTRACTING = "extracting"
    DRAFT_READY = "draft_ready"
    FINALIZING = "finalizing"
    FINALIZED = "finalized"
    ABANDONED = "abandoned"


class CaptureSession(Base, TimestampMixin):
    __tablename__ = "capture_sessions"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    persona_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("personas.skill_id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(140), nullable=False)
    situation_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    context_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_links_json: Mapped[dict[str, Any] | None] = mapped_column(
        _JSONB, nullable=True
    )
    draft_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CaptureSessionStatus] = mapped_column(
        Enum(
            CaptureSessionStatus,
            name="capture_session_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=CaptureSessionStatus.DRAFT,
    )
    llm_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    token_usage_json: Mapped[dict[str, Any] | None] = mapped_column(
        _JSONB, nullable=True
    )
    pii_flags_json: Mapped[dict[str, Any] | None] = mapped_column(
        _JSONB, nullable=True
    )
    finalized_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finalized_neuron_skill_id: Mapped[uuid.UUID | None] = mapped_column(
        _UUID,
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
    )
    abandoned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    attachments: Mapped[list[CaptureAttachment]] = relationship(
        back_populates="capture_session",
        cascade="all, delete-orphan",
        foreign_keys="CaptureAttachment.capture_session_id",
    )

    __table_args__ = (
        Index(
            "ix_capture_sessions_creator_status_updated",
            "creator_id",
            "status",
            "updated_at",
        ),
        Index("ix_capture_sessions_persona_id", "persona_id"),
    )


class CaptureAttachment(Base):
    """Uploads attached to a capture session.

    On finalize the service copies these to a permanent prefix and
    rewrites references in the body. The row is preserved for audit but
    its ``storage_url`` may be invalidated.
    """

    __tablename__ = "capture_attachments"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    capture_session_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("capture_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    storage_url: Mapped[str] = mapped_column(Text, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    capture_session: Mapped[CaptureSession] = relationship(
        back_populates="attachments",
        foreign_keys=[capture_session_id],
    )

    __table_args__ = (
        Index("ix_capture_attachments_capture_session_id", "capture_session_id"),
    )


__all__ = [
    "CaptureAttachment",
    "CaptureSession",
    "CaptureSessionStatus",
]
