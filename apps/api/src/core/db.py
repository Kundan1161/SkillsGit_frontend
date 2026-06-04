"""Database engine, session, base model, and shared SQLAlchemy primitives.

All models inherit from :class:`Base` (declarative). Mixins for timestamps
and soft deletion live here so feature modules need only import them.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

import uuid_utils
from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.config import settings

# ── Naming convention ──────────────────────────────────────────────────
# Postgres prefers explicit constraint names; pick one and stick to it so
# Alembic generates stable migration names.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


def uuid7() -> uuid.UUID:
    """Generate a UUID v7 (time-ordered).

    Uses ``uuid_utils`` for the actual generation; coerces to stdlib UUID so
    SQLAlchemy / Pydantic round-trip cleanly.
    """
    return uuid.UUID(str(uuid_utils.uuid7()))


class Base(AsyncAttrs, DeclarativeBase):
    """Declarative base. All models inherit from this."""

    metadata = metadata


class TimestampMixin:
    """``created_at`` / ``updated_at``. All timestamps are UTC ``timestamptz``."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class SoftDeleteMixin:
    """``deleted_at`` for soft-deletes. NULL means active."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


# ── Engine / session ───────────────────────────────────────────────────
def _build_engine() -> AsyncEngine:
    # ``echo`` only in dev to avoid log noise.
    return create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        future=True,
    )


engine: AsyncEngine = _build_engine()

SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yields an async session and ensures cleanup."""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# ── Audit log table ───────────────────────────────────────────────────
# Defined here because it has no natural owning feature module (it logs
# events across modules). See 02-data-model-core.md `audit_log`.
from sqlalchemy import JSON, ForeignKey, Index, String  # noqa: E402
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID  # noqa: E402


class AuditLog(Base):
    """Append-only log for security-relevant actions.

    See 02-data-model-core.md → ``audit_log``.
    """

    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=uuid7,
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    target_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        nullable=True,
    )
    audit_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        # Use JSON for sqlite test compatibility; JSONB on Postgres via variant.
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
        name="metadata",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_audit_log_actor_id", "actor_id"),
        Index("ix_audit_log_action", "action"),
        Index("ix_audit_log_target", "target_type", "target_id"),
    )


async def write_audit(
    session: AsyncSession,
    *,
    actor_id: uuid.UUID | None,
    action: str,
    target_type: str | None = None,
    target_id: uuid.UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Append an audit log entry. Caller is responsible for committing."""
    entry = AuditLog(
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        audit_metadata=metadata,
    )
    session.add(entry)
