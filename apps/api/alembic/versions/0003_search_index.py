"""search index + editorial picks + search alerts + faq_md

Revision ID: 0003_search_index
Revises: 0002_seed_categories
Create Date: 2026-05-14

Phase 1 catalog support:
- Add ``skills.faq_md`` (and ``skills.support_url`` — coordinating with
  Agent C's listing extensions).
- Add a stored generated ``skills.search_tsv`` ``tsvector`` column +
  GIN index for fast ranked search (per ``01-discovery.md``).
- Create ``editorial_picks`` and ``search_alerts`` tables.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "0003_search_index"
down_revision: Union[str, None] = "0002_seed_categories"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── faq_md + support_url on skills ────────────────────────────────
    op.add_column("skills", sa.Column("faq_md", sa.Text(), nullable=True))
    op.add_column("skills", sa.Column("support_url", sa.Text(), nullable=True))

    # ── skill_versions: yank_reason, rejection_reason, target_version ─
    op.add_column(
        "skill_versions",
        sa.Column("yank_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "skill_versions",
        sa.Column("rejection_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "skill_versions",
        sa.Column("target_version", sa.String(32), nullable=True),
    )

    # ── Stored tsvector for ranked FTS, maintained by trigger ─────────
    # GENERATED ALWAYS won't work here because to_tsvector('english', …)
    # is not IMMUTABLE (the regconfig is session-mutable). Trigger keeps
    # the column populated on INSERT/UPDATE; we backfill existing rows.
    op.execute("DROP INDEX IF EXISTS ix_skills_search;")
    op.execute("ALTER TABLE skills ADD COLUMN search_tsv tsvector;")
    op.execute(
        """
        CREATE OR REPLACE FUNCTION skills_search_tsv_refresh() RETURNS trigger AS $$
        BEGIN
            NEW.search_tsv :=
                setweight(to_tsvector('english', coalesce(NEW.name, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(NEW.tagline, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.description_md, '')), 'C') ||
                setweight(
                    to_tsvector('english', coalesce(array_to_string(NEW.tags, ' '), '')),
                    'B'
                );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER skills_search_tsv_trg
        BEFORE INSERT OR UPDATE OF name, tagline, description_md, tags
        ON skills
        FOR EACH ROW EXECUTE FUNCTION skills_search_tsv_refresh();
        """
    )
    # Backfill any existing rows (none on a fresh migration, but safe).
    op.execute("UPDATE skills SET search_tsv = search_tsv WHERE TRUE;")
    op.execute("CREATE INDEX ix_skills_search_tsv ON skills USING GIN (search_tsv);")
    op.execute("CREATE INDEX ix_skills_name_trgm ON skills USING GIN (name gin_trgm_ops);")

    # ── editorial_picks ───────────────────────────────────────────────
    op.create_table(
        "editorial_picks",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "skill_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("slot", sa.String(64), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_by",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_editorial_picks_skill_id", "editorial_picks", ["skill_id"])
    op.create_index("ix_editorial_picks_sort", "editorial_picks", ["sort_order"])

    # ── search_alerts ─────────────────────────────────────────────────
    op.create_table(
        "search_alerts",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(120), nullable=True),
        sa.Column(
            "query_json",
            pg.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("last_notified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_search_alerts_user_id", "search_alerts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_search_alerts_user_id", table_name="search_alerts")
    op.drop_table("search_alerts")
    op.drop_index("ix_editorial_picks_sort", table_name="editorial_picks")
    op.drop_index("ix_editorial_picks_skill_id", table_name="editorial_picks")
    op.drop_table("editorial_picks")
    op.execute("DROP INDEX IF EXISTS ix_skills_name_trgm;")
    op.execute("DROP INDEX IF EXISTS ix_skills_search_tsv;")
    op.execute("ALTER TABLE skills DROP COLUMN IF EXISTS search_tsv;")
    # Restore old functional index from 0001 for compatibility.
    op.execute(
        "CREATE INDEX ix_skills_search ON skills USING GIN ("
        "to_tsvector('english', coalesce(name,'') || ' ' || "
        "coalesce(tagline,'') || ' ' || coalesce(description_md,'')));"
    )
    op.drop_column("skill_versions", "target_version")
    op.drop_column("skill_versions", "rejection_reason")
    op.drop_column("skill_versions", "yank_reason")
    op.drop_column("skills", "support_url")
    op.drop_column("skills", "faq_md")
