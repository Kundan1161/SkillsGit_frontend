"""VaultBuild + VaultDownload ORM models.

Per ``team/01-data-model-deltas.md`` §0009.

A ``vault_build`` is keyed by ``(skill_id, skill_version_id,
content_hash)`` and points at an immutable S3 zip artifact. The composer
(Wave 3) reads ``manifest_json`` and merges multiple builds into a
per-buyer bundle whose metadata lands in ``vault_downloads``.
"""

from __future__ import annotations

import enum
import uuid  # noqa: TC003  (used at runtime via Mapped[uuid.UUID])
from datetime import datetime  # noqa: TC003  (used at runtime via Mapped[datetime])
from typing import Any

from sqlalchemy import (
    CHAR,
    JSON,
    BigInteger,
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
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base, TimestampMixin, uuid7

_UUID = PG_UUID(as_uuid=True).with_variant(String(36), "sqlite")
_JSONB = JSON().with_variant(JSONB, "postgresql")
_UUID_ARRAY = PG_ARRAY(PG_UUID(as_uuid=True)).with_variant(JSON(), "sqlite")


class VaultBuildStatus(str, enum.Enum):  # noqa: UP042 — matches project-wide enum pattern
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class VaultBuild(Base, TimestampMixin):
    """Immutable build artifact for an occupation or persona version."""

    __tablename__ = "vault_builds"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    skill_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_version_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("skill_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    content_hash: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    storage_url: Mapped[str] = mapped_column(Text, nullable=False)
    manifest_json: Mapped[dict[str, Any] | None] = mapped_column(
        _JSONB, nullable=True
    )
    file_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    status: Mapped[VaultBuildStatus] = mapped_column(
        Enum(
            VaultBuildStatus,
            name="vault_build_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=VaultBuildStatus.QUEUED,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    build_log_json: Mapped[dict[str, Any] | None] = mapped_column(
        _JSONB, nullable=True
    )
    built_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    built_by: Mapped[uuid.UUID | None] = mapped_column(
        _UUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        # Same content under same skill = same build (idempotent rebuilds).
        UniqueConstraint(
            "skill_id", "content_hash", name="uq_vault_builds_skill_content_hash"
        ),
        # Note: ``UNIQUE(skill_version_id) WHERE status='succeeded'`` is a
        # partial unique index created in the migration via ``op.execute``
        # — SQLAlchemy can model it but the migration is the source of
        # truth for partial indexes that need Postgres-specific syntax.
        Index(
            "ix_vault_builds_skill_status_built_at",
            "skill_id",
            "status",
            "built_at",
        ),
    )


class VaultDownload(Base):
    """Per-call composition record (delivery-side audit).

    The composed zip itself lives under ``delivery/vaults/{nonce}.zip``
    with a 1h lifecycle policy; this row is permanent.
    """

    __tablename__ = "vault_downloads"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    occupation_license_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("licenses.id", ondelete="CASCADE"),
        nullable=False,
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    occupation_build_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("vault_builds.id", ondelete="RESTRICT"),
        nullable=False,
    )
    # Persona builds + persona licenses are snapshots — once recorded,
    # later persona-side changes don't rewrite the audit row.
    persona_build_ids: Mapped[list[uuid.UUID] | None] = mapped_column(
        _UUID_ARRAY, nullable=True
    )
    persona_license_ids: Mapped[list[uuid.UUID] | None] = mapped_column(
        _UUID_ARRAY, nullable=True
    )
    composed_hash: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    storage_url: Mapped[str] = mapped_column(Text, nullable=False)
    user_agent_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index(
            "ix_vault_downloads_buyer_created",
            "buyer_id",
            "created_at",
        ),
        Index(
            "ix_vault_downloads_occupation_license_created",
            "occupation_license_id",
            "created_at",
        ),
    )


__all__ = [
    "VaultBuild",
    "VaultBuildStatus",
    "VaultDownload",
]
