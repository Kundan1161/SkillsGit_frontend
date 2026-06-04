"""occupations + skills.kind discriminator

Revision ID: 0006_occupations_and_kind
Revises: 0005_delivery_and_moderation
Create Date: 2026-05-26

Adds (per ``team/01-data-model-deltas.md`` §0006 and ADR-004):

- ``skill_kind`` enum + ``skills.kind`` column with default ``'skill'``,
  backfill existing rows, then SET NOT NULL.
- ``ix_skills_kind_status`` covering index — every catalog query now
  filters by ``kind``.
- ``occupation_member_role`` enum.
- ``occupations`` side table (1:1 with ``skills`` via shared PK).
- ``occupation_skills`` join table with unique + sort indexes.

Owned by Backend / Wave 1 of Cycle 1 (Occupations & Personas).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "0006_occupations_and_kind"
down_revision: Union[str, None] = "0005_delivery_and_moderation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── enums ─────────────────────────────────────────────────────────
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE skill_kind AS ENUM ('skill', 'occupation', 'persona', 'memory_neuron'); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$;"
    )
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE occupation_member_role AS ENUM ('core', 'supporting', 'optional'); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$;"
    )
    skill_kind = pg.ENUM(name="skill_kind", create_type=False)
    occupation_member_role = pg.ENUM(name="occupation_member_role", create_type=False)

    # ── skills.kind ───────────────────────────────────────────────────
    # Add nullable first so the table-rewrite is fast on large tables;
    # then backfill to 'skill' and finally enforce NOT NULL.
    op.add_column(
        "skills",
        sa.Column("kind", skill_kind, nullable=True, server_default="skill"),
    )
    op.execute("UPDATE skills SET kind = 'skill' WHERE kind IS NULL;")
    op.alter_column("skills", "kind", nullable=False)

    op.create_index(
        "ix_skills_kind_status",
        "skills",
        ["kind", "status"],
    )

    # ── occupations ───────────────────────────────────────────────────
    op.create_table(
        "occupations",
        sa.Column(
            "skill_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("summary_md", sa.Text(), nullable=True),
        sa.Column("domains", pg.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "persona_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "recommended_persona_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        # FK constraint to vault_builds added in 0009 (the target table
        # doesn't exist yet). The column is nullable so we just record
        # the UUID for now.
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

    # ── occupation_skills ─────────────────────────────────────────────
    op.create_table(
        "occupation_skills",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "occupation_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("occupations.skill_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "member_skill_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("domain", sa.String(120), nullable=True),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "role",
            occupation_member_role,
            nullable=False,
            server_default="core",
        ),
        sa.Column(
            "pinned",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("notes_md", sa.Text(), nullable=True),
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
        sa.UniqueConstraint(
            "occupation_id",
            "member_skill_id",
            name="uq_occupation_skills_occupation_member",
        ),
    )
    op.create_index(
        "ix_occupation_skills_occupation_sort",
        "occupation_skills",
        ["occupation_id", "sort_order"],
    )
    op.create_index(
        "ix_occupation_skills_member_skill_id",
        "occupation_skills",
        ["member_skill_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_occupation_skills_member_skill_id",
        table_name="occupation_skills",
    )
    op.drop_index(
        "ix_occupation_skills_occupation_sort",
        table_name="occupation_skills",
    )
    op.drop_table("occupation_skills")
    op.drop_table("occupations")
    op.drop_index("ix_skills_kind_status", table_name="skills")
    op.drop_column("skills", "kind")

    bind = op.get_bind()
    sa.Enum(name="occupation_member_role").drop(bind, checkfirst=True)
    sa.Enum(name="skill_kind").drop(bind, checkfirst=True)
