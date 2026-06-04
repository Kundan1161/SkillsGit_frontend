"""delivery + moderation phase 1

Revision ID: 0005_delivery_and_moderation
Revises: 0003_search_index, 0004_billing_phase1
Create Date: 2026-05-14

Owned by Phase-1 Agent C (licensing + delivery + admin).

Adds:
- ``skill_versions.yank_reason`` — set when a creator yanks a version.
- ``skill_versions.rejection_reason`` — set by an admin during moderation
  rejection; cleared on resubmission.
- ``skill_versions.target_version`` — the semver the creator declared at
  submit-time (immutable record of the version label).
- ``moderation_actions`` table — moderator-friendly action log per
  ``prompts/marketplace/05-trust-and-quality.md`` § Action log.

This is a merge of Agent A's catalog branch (0003) and Agent B's billing
branch (0004) — by depending on both, alembic picks the linear order
implicitly.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "0005_delivery_and_moderation"
down_revision: Union[str, Sequence[str], None] = (
    "0003_search_index",
    "0004_billing_phase1",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── skill_versions extensions ─────────────────────────────────────
    # Columns yank_reason, rejection_reason, target_version are already
    # added by 0003_search_index (one of this revision's parents).
    # Backfill target_version with the canonical version label for any
    # rows present at upgrade time.
    op.execute(
        "UPDATE skill_versions SET target_version = version "
        "WHERE target_version IS NULL;"
    )

    # ── moderation_actions table ──────────────────────────────────────
    op.create_table(
        "moderation_actions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "actor_admin_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("target_type", sa.String(32), nullable=False),
        sa.Column("target_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("metadata", pg.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_moderation_actions_target",
        "moderation_actions",
        ["target_type", "target_id"],
    )
    op.create_index(
        "ix_moderation_actions_action", "moderation_actions", ["action"]
    )


def downgrade() -> None:
    op.drop_index("ix_moderation_actions_action", table_name="moderation_actions")
    op.drop_index("ix_moderation_actions_target", table_name="moderation_actions")
    op.drop_table("moderation_actions")
    # skill_versions column drops belong to 0003_search_index's downgrade.

    with op.batch_alter_table("skill_versions") as batch:
        batch.drop_column("target_version")
        batch.drop_column("rejection_reason")
        batch.drop_column("yank_reason")
