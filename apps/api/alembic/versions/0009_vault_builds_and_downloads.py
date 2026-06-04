"""vault_builds + vault_downloads + licenses composition

Revision ID: 0009_vault_builds_and_downloads
Revises: 0008_capture
Create Date: 2026-05-26

Adds (per ``team/01-data-model-deltas.md`` §0009, ADR-002, ADR-013):

- ``vault_build_status`` enum.
- ``vault_builds`` — addressable immutable build records keyed by
  ``(skill_id, content_hash)``; ``(skill_version_id)`` partial-unique
  where ``status='succeeded'``.
- Deferred FKs from ``occupations.latest_build_id`` and
  ``personas.latest_build_id`` to ``vault_builds.id`` (added now that
  the target table exists).
- ``vault_downloads`` — per-call composition record (delivery-side
  audit).
- ``license_composition_role`` enum + ``licenses.composition_role`` +
  ``licenses.target_occupation_skill_id`` with backfill.
- ``ix_licenses_buyer_target_occupation_status`` index for the
  composer's primary "buyer's persona licenses for occupation X" query.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "0009_vault_builds_and_downloads"
down_revision: Union[str, None] = "0008_capture"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── enums ─────────────────────────────────────────────────────────
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE vault_build_status AS ENUM ("
        "    'queued', 'running', 'succeeded', 'failed'"
        "  ); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$;"
    )
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE license_composition_role AS ENUM ("
        "    'occupation', 'persona', 'standalone'"
        "  ); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$;"
    )
    vault_build_status = pg.ENUM(name="vault_build_status", create_type=False)
    license_composition_role = pg.ENUM(
        name="license_composition_role", create_type=False
    )

    # ── vault_builds ──────────────────────────────────────────────────
    op.create_table(
        "vault_builds",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "skill_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "skill_version_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("skill_versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content_hash", sa.CHAR(64), nullable=False),
        sa.Column("storage_url", sa.Text(), nullable=False),
        sa.Column("manifest_json", pg.JSONB(), nullable=True),
        sa.Column(
            "file_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "total_bytes",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "status",
            vault_build_status,
            nullable=False,
            server_default="queued",
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("build_log_json", pg.JSONB(), nullable=True),
        sa.Column("built_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "built_by",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
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
            "skill_id",
            "content_hash",
            name="uq_vault_builds_skill_content_hash",
        ),
    )
    op.create_index(
        "ix_vault_builds_skill_status_built_at",
        "vault_builds",
        ["skill_id", "status", "built_at"],
    )
    # Partial unique: at most one authoritative succeeded build per
    # version. Postgres-only syntax via op.execute.
    op.execute(
        "CREATE UNIQUE INDEX uq_vault_builds_skill_version_succeeded "
        "ON vault_builds (skill_version_id) WHERE status = 'succeeded';"
    )

    # ── deferred FKs from occupations / personas → vault_builds ──────
    op.create_foreign_key(
        "fk_occupations_latest_build_id_vault_builds",
        "occupations",
        "vault_builds",
        ["latest_build_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_personas_latest_build_id_vault_builds",
        "personas",
        "vault_builds",
        ["latest_build_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ── vault_downloads ───────────────────────────────────────────────
    op.create_table(
        "vault_downloads",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "occupation_license_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("licenses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "buyer_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "occupation_build_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("vault_builds.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "persona_build_ids",
            pg.ARRAY(pg.UUID(as_uuid=True)),
            nullable=True,
        ),
        sa.Column(
            "persona_license_ids",
            pg.ARRAY(pg.UUID(as_uuid=True)),
            nullable=True,
        ),
        sa.Column("composed_hash", sa.CHAR(64), nullable=False),
        sa.Column("storage_url", sa.Text(), nullable=False),
        sa.Column("user_agent_hash", sa.String(64), nullable=True),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_vault_downloads_buyer_created",
        "vault_downloads",
        ["buyer_id", "created_at"],
    )
    op.create_index(
        "ix_vault_downloads_occupation_license_created",
        "vault_downloads",
        ["occupation_license_id", "created_at"],
    )

    # ── licenses additions ────────────────────────────────────────────
    op.add_column(
        "licenses",
        sa.Column(
            "composition_role",
            license_composition_role,
            nullable=True,
            server_default="standalone",
        ),
    )
    op.add_column(
        "licenses",
        sa.Column(
            "target_occupation_skill_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )
    # Backfill every existing license to standalone, then enforce NOT NULL.
    op.execute(
        "UPDATE licenses SET composition_role = 'standalone' "
        "WHERE composition_role IS NULL;"
    )
    op.alter_column("licenses", "composition_role", nullable=False)
    op.create_index(
        "ix_licenses_buyer_target_occupation_status",
        "licenses",
        ["buyer_id", "target_occupation_skill_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_licenses_buyer_target_occupation_status",
        table_name="licenses",
    )
    op.drop_column("licenses", "target_occupation_skill_id")
    op.drop_column("licenses", "composition_role")

    op.drop_index(
        "ix_vault_downloads_occupation_license_created",
        table_name="vault_downloads",
    )
    op.drop_index(
        "ix_vault_downloads_buyer_created",
        table_name="vault_downloads",
    )
    op.drop_table("vault_downloads")

    op.drop_constraint(
        "fk_personas_latest_build_id_vault_builds",
        "personas",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_occupations_latest_build_id_vault_builds",
        "occupations",
        type_="foreignkey",
    )

    op.execute("DROP INDEX IF EXISTS uq_vault_builds_skill_version_succeeded;")
    op.drop_index(
        "ix_vault_builds_skill_status_built_at",
        table_name="vault_builds",
    )
    op.drop_table("vault_builds")

    bind = op.get_bind()
    sa.Enum(name="license_composition_role").drop(bind, checkfirst=True)
    sa.Enum(name="vault_build_status").drop(bind, checkfirst=True)
