"""billing phase 1: webhook_events + users.payouts_enabled

Revision ID: 0004_billing_phase1
Revises: 0002_seed_categories
Create Date: 2026-05-14

Adds:
- ``users.payouts_enabled`` (bool, default false) — cached from
  Stripe Connect ``account.payouts_enabled``; refreshed by webhook.
- ``webhook_events`` table — inbound Stripe webhook event log. Primary
  key is Stripe's ``event.id`` so re-delivery is a no-op via INSERT
  ... ON CONFLICT.
- ``webhook_event_status`` enum.

Owned by Phase-1 Agent B (billing). Agent A is using ``0003`` for
catalog-side migrations.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "0004_billing_phase1"
down_revision: Union[str, None] = "0002_seed_categories"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users.payouts_enabled ──────────────────────────────────────────
    op.add_column(
        "users",
        sa.Column(
            "payouts_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # ── webhook_event_status enum ──────────────────────────────────────
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE webhook_event_status AS ENUM ('received', 'processed', 'failed'); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$;"
    )
    webhook_event_status = pg.ENUM(name="webhook_event_status", create_type=False)

    # ── webhook_events ─────────────────────────────────────────────────
    op.create_table(
        "webhook_events",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("type", sa.String(128), nullable=False),
        sa.Column("payload_json", pg.JSONB(), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            webhook_event_status,
            nullable=False,
            server_default="received",
        ),
        sa.Column("error", sa.Text(), nullable=True),
    )
    op.create_index("ix_webhook_events_type", "webhook_events", ["type"])
    op.create_index("ix_webhook_events_status", "webhook_events", ["status"])


def downgrade() -> None:
    op.drop_index("ix_webhook_events_status", table_name="webhook_events")
    op.drop_index("ix_webhook_events_type", table_name="webhook_events")
    op.drop_table("webhook_events")

    bind = op.get_bind()
    sa.Enum(name="webhook_event_status").drop(bind, checkfirst=True)

    op.drop_column("users", "payouts_enabled")
