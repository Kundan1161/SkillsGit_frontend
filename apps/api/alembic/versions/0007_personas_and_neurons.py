"""personas + persona_neurons

Revision ID: 0007_personas_and_neurons
Revises: 0006_occupations_and_kind
Create Date: 2026-05-26

Adds (per ``team/01-data-model-deltas.md`` §0007 and ADR-005):

- ``personas`` side table (1:1 with a ``kind=persona`` skill row).
  ``parent_occupation_id`` is non-null and references ``occupations``.
- ``persona_neurons`` join table — bundles ``kind=memory_neuron`` skill
  rows into a persona.

Membership rule "neuron.creator_id == persona.creator_id" is enforced
at the service layer (no FK can express it).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "0007_personas_and_neurons"
down_revision: Union[str, None] = "0006_occupations_and_kind"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── personas ──────────────────────────────────────────────────────
    op.create_table(
        "personas",
        sa.Column(
            "skill_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "parent_occupation_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("occupations.skill_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("creator_intro_md", sa.Text(), nullable=True),
        sa.Column("years_of_experience", sa.Integer(), nullable=True),
        sa.Column("specialization", sa.String(280), nullable=True),
        sa.Column(
            "neuron_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        # FK to vault_builds added in 0009; column nullable.
        sa.Column("latest_build_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_personas_parent_occupation_id",
        "personas",
        ["parent_occupation_id"],
    )

    # ── persona_neurons ───────────────────────────────────────────────
    op.create_table(
        "persona_neurons",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "persona_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("personas.skill_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "neuron_skill_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("section", sa.String(120), nullable=True),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "persona_id",
            "neuron_skill_id",
            name="uq_persona_neurons_persona_neuron",
        ),
    )
    op.create_index(
        "ix_persona_neurons_persona_sort",
        "persona_neurons",
        ["persona_id", "sort_order"],
    )
    op.create_index(
        "ix_persona_neurons_neuron_skill_id",
        "persona_neurons",
        ["neuron_skill_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_persona_neurons_neuron_skill_id",
        table_name="persona_neurons",
    )
    op.drop_index(
        "ix_persona_neurons_persona_sort",
        table_name="persona_neurons",
    )
    op.drop_table("persona_neurons")
    op.drop_index(
        "ix_personas_parent_occupation_id",
        table_name="personas",
    )
    op.drop_table("personas")
