"""Occupation + OccupationSkill ORM models.

Per ``team/01-data-model-deltas.md`` §0006 and ADR-004 in
``team/decisions.md``. Side tables only — the parent ``skills`` row
carries identity, pricing, status, and version history. The 1:1
relationship to ``skills.id`` is enforced by making ``skill_id`` both
the primary key and a foreign key (no separate ``id`` column).
"""

from __future__ import annotations

import enum
import uuid  # noqa: TC003  (used at runtime via Mapped[uuid.UUID])

from sqlalchemy import (
    JSON,
    Boolean,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base, TimestampMixin, uuid7

_UUID = PG_UUID(as_uuid=True).with_variant(String(36), "sqlite")
_STR_ARRAY = PG_ARRAY(String).with_variant(JSON(), "sqlite")


# `(str, enum.Enum)` matches the project-wide enum pattern in
# `src/skills/models.py`, `src/billing/models.py`, etc. Keeping it for
# consistency; switching to enum.StrEnum is a project-wide cleanup, not
# a Wave-2 scope item.
class OccupationMemberRole(str, enum.Enum):  # noqa: UP042
    """How a member skill is positioned inside the occupation vault."""

    CORE = "core"
    SUPPORTING = "supporting"
    OPTIONAL = "optional"


class Occupation(Base, TimestampMixin):
    """Side table for ``kind=occupation`` skill rows.

    Identity, billing, status, and versioning live on the parent
    ``skills`` row. This row only carries occupation-specific metadata:
    long-form summary, domain folders for the vault, and aggregates.
    """

    __tablename__ = "occupations"

    skill_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    summary_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Top-level groupings used as folder names in the vault.
    domains: Mapped[list[str] | None] = mapped_column(_STR_ARRAY, nullable=True)
    # Denormalized counts — kept in sync by the personas/vault services.
    persona_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommended_persona_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    # FK to vault_builds; the constraint itself is added in migration 0009
    # (vault_builds doesn't exist when occupations is first created).
    latest_build_id: Mapped[uuid.UUID | None] = mapped_column(
        _UUID, nullable=True
    )

    members: Mapped[list[OccupationSkill]] = relationship(
        back_populates="occupation",
        cascade="all, delete-orphan",
        foreign_keys="OccupationSkill.occupation_id",
    )


class OccupationSkill(Base, TimestampMixin):
    """Join row: a member skill inside an occupation.

    ``member_skill_id`` must reference a ``skills`` row with
    ``kind=skill``. The constraint is enforced at the service layer
    (see ADR-004 consequences) because referential SQL can't check the
    parent's discriminator across the FK.
    """

    __tablename__ = "occupation_skills"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    occupation_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("occupations.skill_id", ondelete="CASCADE"),
        nullable=False,
    )
    member_skill_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False,
    )
    domain: Mapped[str | None] = mapped_column(String(120), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    role: Mapped[OccupationMemberRole] = mapped_column(
        Enum(
            OccupationMemberRole,
            name="occupation_member_role",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=OccupationMemberRole.CORE,
    )
    pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes_md: Mapped[str | None] = mapped_column(Text, nullable=True)

    occupation: Mapped[Occupation] = relationship(
        back_populates="members",
        foreign_keys=[occupation_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "occupation_id",
            "member_skill_id",
            name="uq_occupation_skills_occupation_member",
        ),
        Index(
            "ix_occupation_skills_occupation_sort",
            "occupation_id",
            "sort_order",
        ),
        Index("ix_occupation_skills_member_skill_id", "member_skill_id"),
    )


__all__ = [
    "Occupation",
    "OccupationMemberRole",
    "OccupationSkill",
]
