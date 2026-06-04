"""capture_sessions + capture_attachments

Revision ID: 0008_capture
Revises: 0007_personas_and_neurons
Create Date: 2026-05-26

Adds (per ``team/01-data-model-deltas.md`` §0008 and ADR-015):

- ``capture_session_status`` enum.
- ``capture_sessions`` — draft holding pen for in-flight LLM
  extractions; never reaches ``skills`` until finalize.
- ``capture_attachments`` — uploads attached to a session.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "0008_capture"
down_revision: Union[str, None] = "0007_personas_and_neurons"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── enum ──────────────────────────────────────────────────────────
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE capture_session_status AS ENUM ("
        "    'draft', 'extracting', 'draft_ready', "
        "    'finalizing', 'finalized', 'abandoned'"
        "  ); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$;"
    )
    capture_session_status = pg.ENUM(
        name="capture_session_status", create_type=False
    )

    # ── capture_sessions ──────────────────────────────────────────────
    op.create_table(
        "capture_sessions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "creator_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "persona_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("personas.skill_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(140), nullable=False),
        sa.Column("situation_md", sa.Text(), nullable=True),
        sa.Column("decision_md", sa.Text(), nullable=True),
        sa.Column("outcome_md", sa.Text(), nullable=True),
        sa.Column("context_md", sa.Text(), nullable=True),
        sa.Column("suggested_links_json", pg.JSONB(), nullable=True),
        sa.Column("draft_md", sa.Text(), nullable=True),
        sa.Column(
            "status",
            capture_session_status,
            nullable=False,
            server_default="draft",
        ),
        sa.Column("llm_model", sa.String(120), nullable=True),
        sa.Column("token_usage_json", pg.JSONB(), nullable=True),
        sa.Column("pii_flags_json", pg.JSONB(), nullable=True),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "finalized_neuron_skill_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("abandoned_at", sa.DateTime(timezone=True), nullable=True),
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
        "ix_capture_sessions_creator_status_updated",
        "capture_sessions",
        ["creator_id", "status", "updated_at"],
    )
    op.create_index(
        "ix_capture_sessions_persona_id",
        "capture_sessions",
        ["persona_id"],
    )

    # ── capture_attachments ───────────────────────────────────────────
    op.create_table(
        "capture_attachments",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "capture_session_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("capture_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("storage_url", sa.Text(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(120), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.CHAR(64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_capture_attachments_capture_session_id",
        "capture_attachments",
        ["capture_session_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_capture_attachments_capture_session_id",
        table_name="capture_attachments",
    )
    op.drop_table("capture_attachments")
    op.drop_index(
        "ix_capture_sessions_persona_id",
        table_name="capture_sessions",
    )
    op.drop_index(
        "ix_capture_sessions_creator_status_updated",
        table_name="capture_sessions",
    )
    op.drop_table("capture_sessions")

    bind = op.get_bind()
    sa.Enum(name="capture_session_status").drop(bind, checkfirst=True)
