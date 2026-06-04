"""``skills``, ``skill_versions``, and ``categories`` tables.

Includes the static AI-model allowlist consumed by the validator
(per ``shared/skills-md-spec.md``).
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CHAR,
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
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
    from src.users.models import User


_UUID = PG_UUID(as_uuid=True).with_variant(String(36), "sqlite")
_CITEXT = CITEXT().with_variant(String(255), "sqlite")
_STR_ARRAY = PG_ARRAY(String).with_variant(JSON(), "sqlite")
_JSONB = JSON().with_variant(JSONB, "postgresql")


class SkillStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    UNLISTED = "unlisted"
    REMOVED = "removed"


class PricingModel(str, enum.Enum):
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    FREEMIUM = "freemium"


class SkillKind(str, enum.Enum):
    """Discriminator on the ``skills`` row per ADR-004.

    The existing 456 curated rows are ``skill``; ``occupation`` and
    ``persona`` carry their own side-table metadata; ``memory_neuron``
    rows are addressable inside a persona vault and never appear in
    the public marketplace listings.
    """

    SKILL = "skill"
    OCCUPATION = "occupation"
    PERSONA = "persona"
    MEMORY_NEURON = "memory_neuron"


# ── AI model allowlist ────────────────────────────────────────────────
# Referenced from ``shared/skills-md-spec.md`` — the validator rejects
# ``ai.required_models`` entries not in this set. Update conservatively;
# adding a new model is a non-breaking change.
ALLOWED_AI_MODELS: frozenset[str] = frozenset(
    {
        # Anthropic Claude
        "claude-opus-4-7",
        "claude-opus-4-6",
        "claude-opus-4-5",
        "claude-sonnet-4-7",
        "claude-sonnet-4-6",
        "claude-sonnet-4-5",
        "claude-haiku-4-7",
        "claude-haiku-4-6",
        "claude-haiku-4-5",
        # OpenAI
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-5",
        "o1",
        "o3",
        # Google
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-2.0-pro",
        "gemini-2.0-flash",
    }
)


class Category(Base):
    __tablename__ = "categories"

    slug: Mapped[str] = mapped_column(_CITEXT, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_slug: Mapped[str | None] = mapped_column(
        _CITEXT,
        ForeignKey("categories.slug", ondelete="SET NULL"),
        nullable=True,
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Skill(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    slug: Mapped[str] = mapped_column(_CITEXT, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    tagline: Mapped[str | None] = mapped_column(String(140), nullable=True)
    description_md: Mapped[str | None] = mapped_column(Text, nullable=True)

    category: Mapped[str | None] = mapped_column(
        _CITEXT,
        ForeignKey("categories.slug", ondelete="SET NULL"),
        nullable=True,
    )
    tags: Mapped[list[str] | None] = mapped_column(_STR_ARRAY, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    screenshots: Mapped[list[str] | None] = mapped_column(_STR_ARRAY, nullable=True)

    status: Mapped[SkillStatus] = mapped_column(
        Enum(SkillStatus, name="skill_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=SkillStatus.DRAFT,
    )
    # ADR-004 — discriminator added in migration 0006.
    kind: Mapped[SkillKind] = mapped_column(
        Enum(SkillKind, name="skill_kind", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=SkillKind.SKILL,
        server_default=SkillKind.SKILL.value,
    )
    latest_version_id: Mapped[uuid.UUID | None] = mapped_column(
        _UUID,
        ForeignKey(
            "skill_versions.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_skills_latest_version_id_skill_versions",
        ),
        nullable=True,
    )

    pricing_model: Mapped[PricingModel] = mapped_column(
        Enum(PricingModel, name="pricing_model", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PricingModel.FREE,
    )
    one_time_price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subscription_price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    support_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    total_sales: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rating_avg: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Phase 1 listing extensions — see 04-licensing-and-delivery.md (Support)
    # and 07-creator-dashboard.md (Listing tab).
    support_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    faq_md: Mapped[str | None] = mapped_column(Text, nullable=True)

    creator: Mapped["User"] = relationship(
        back_populates="skills", foreign_keys=[creator_id]
    )
    versions: Mapped[list["SkillVersion"]] = relationship(
        back_populates="skill",
        cascade="all, delete-orphan",
        foreign_keys="SkillVersion.skill_id",
    )

    __table_args__ = (
        UniqueConstraint("creator_id", "slug", name="uq_skills_creator_slug"),
        Index("ix_skills_status_category", "status", "category"),
        Index("ix_skills_creator_id", "creator_id"),
        # ADR-004 — every catalog query filters by kind; added in 0006.
        Index("ix_skills_kind_status", "kind", "status"),
        # FT search GIN index on (name || tagline || description_md) and tags
        # are created in the Alembic migration via ``op.execute(...)`` since
        # SQLAlchemy doesn't model functional GIN indexes natively.
    )


class SkillVersion(Base):
    __tablename__ = "skill_versions"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    skill_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    content_hash: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    storage_url: Mapped[str] = mapped_column(Text, nullable=False)
    ai_requirements: Mapped[dict[str, Any] | None] = mapped_column(_JSONB, nullable=True)
    changelog_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    released_by: Mapped[uuid.UUID | None] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    is_yanked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    yank_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Set when an admin rejects this version; clears on resubmission.
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_version: Mapped[str | None] = mapped_column(String(32), nullable=True)

    skill: Mapped[Skill] = relationship(
        back_populates="versions", foreign_keys=[skill_id]
    )

    __table_args__ = (
        UniqueConstraint("skill_id", "version", name="uq_skill_versions_skill_version"),
        Index("ix_skill_versions_skill_id", "skill_id"),
    )


__all__ = [
    "ALLOWED_AI_MODELS",
    "Category",
    "PricingModel",
    "Skill",
    "SkillKind",
    "SkillStatus",
    "SkillVersion",
]
