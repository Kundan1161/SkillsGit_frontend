"""Persona + PersonaNeuron ORM models.

Per ``team/01-data-model-deltas.md`` §0007. Side tables for ``kind=persona``
and the persona-to-neuron membership join. The neuron rows themselves
are ``kind=memory_neuron`` skills in the existing ``skills`` table — no
new neuron table.
"""

from __future__ import annotations

import uuid  # noqa: TC003  (used at runtime via Mapped[uuid.UUID])
from datetime import datetime  # noqa: TC003  (used at runtime via Mapped[datetime])

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base, TimestampMixin, uuid7

_UUID = PG_UUID(as_uuid=True).with_variant(String(36), "sqlite")


class Persona(Base, TimestampMixin):
    """Side table for ``kind=persona`` skill rows.

    Identity, pricing, and listing fields live on the parent ``skills``
    row. ``parent_occupation_id`` is non-null: every persona stacks on
    exactly one occupation. Deleting the parent is rejected (RESTRICT)
    with a clear service-layer message; the operator must reparent or
    yank the personas first.
    """

    __tablename__ = "personas"

    skill_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    parent_occupation_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("occupations.skill_id", ondelete="RESTRICT"),
        nullable=False,
    )
    creator_intro_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    years_of_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(280), nullable=True)
    neuron_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # FK to vault_builds added in migration 0009.
    latest_build_id: Mapped[uuid.UUID | None] = mapped_column(
        _UUID, nullable=True
    )

    neurons: Mapped[list[PersonaNeuron]] = relationship(
        back_populates="persona",
        cascade="all, delete-orphan",
        foreign_keys="PersonaNeuron.persona_id",
    )

    __table_args__ = (
        Index("ix_personas_parent_occupation_id", "parent_occupation_id"),
    )


class PersonaNeuron(Base):
    """Membership row: a memory_neuron skill bundled into a persona.

    Per ADR-005, the neuron is itself a ``skills`` row with
    ``kind=memory_neuron``. The application-level rule (enforced in the
    service when this row is inserted) is that the neuron's
    ``creator_id`` must equal the persona's ``creator_id`` — a creator
    cannot bundle someone else's neurons into their own persona.
    """

    __tablename__ = "persona_neurons"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    persona_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("personas.skill_id", ondelete="CASCADE"),
        nullable=False,
    )
    neuron_skill_id: Mapped[uuid.UUID] = mapped_column(
        _UUID,
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Optional sub-folder name under ``personas/{handle}/`` in the vault.
    section: Mapped[str | None] = mapped_column(String(120), nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    persona: Mapped[Persona] = relationship(
        back_populates="neurons",
        foreign_keys=[persona_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "persona_id",
            "neuron_skill_id",
            name="uq_persona_neurons_persona_neuron",
        ),
        Index(
            "ix_persona_neurons_persona_sort",
            "persona_id",
            "sort_order",
        ),
        Index("ix_persona_neurons_neuron_skill_id", "neuron_skill_id"),
    )


__all__ = [
    "Persona",
    "PersonaNeuron",
]
