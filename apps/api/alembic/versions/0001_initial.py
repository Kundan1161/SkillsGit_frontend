"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-14

Creates every table in ``02-data-model-core.md`` plus the ``api_tokens``
table from ``shared/auth.md`` and the generic ``audit_log``.

Extensions:
- ``citext`` — case-insensitive text (emails, slugs, handles).
- ``pgcrypto`` — primarily for gen_random_uuid as a safety net even though
  the application generates UUID v7 client-side.

Indexes that Postgres alone supports (functional / GIN on tsvector or
``ARRAY`` columns) are created via ``op.execute(...)``.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Extensions ─────────────────────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS citext;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # ── Enum types ─────────────────────────────────────────────────────
    # Raw DO-block CREATE TYPE for each enum, idempotent via EXCEPTION.
    # Column types below use postgresql.ENUM(name=..., create_type=False)
    # so create_table won't try to re-issue CREATE TYPE.
    for enum_name, enum_values in (
        ("user_role", ("buyer", "creator", "admin")),
        ("skill_status", ("draft", "pending_review", "published", "unlisted", "removed")),
        ("pricing_model", ("free", "one_time", "subscription", "freemium")),
        ("order_status", ("pending", "paid", "refunded", "partially_refunded", "failed")),
        ("subscription_status", ("active", "past_due", "canceled", "paused")),
        ("license_source", ("one_time", "subscription", "free", "freemium", "grant")),
        ("license_status", ("active", "expired", "revoked")),
        ("support_tier", ("none", "basic", "priority")),
        ("payout_status", ("pending", "paid", "failed")),
        ("review_status", ("visible", "hidden", "flagged")),
    ):
        values_sql = ", ".join(f"'{v}'" for v in enum_values)
        op.execute(
            f"DO $$ BEGIN "
            f"  CREATE TYPE {enum_name} AS ENUM ({values_sql}); "
            f"EXCEPTION WHEN duplicate_object THEN null; END $$;"
        )

    user_role = pg.ENUM(name="user_role", create_type=False)
    skill_status = pg.ENUM(name="skill_status", create_type=False)
    pricing_model = pg.ENUM(name="pricing_model", create_type=False)
    order_status = pg.ENUM(name="order_status", create_type=False)
    subscription_status = pg.ENUM(name="subscription_status", create_type=False)
    license_source = pg.ENUM(name="license_source", create_type=False)
    license_status = pg.ENUM(name="license_status", create_type=False)
    support_tier = pg.ENUM(name="support_tier", create_type=False)
    payout_status = pg.ENUM(name="payout_status", create_type=False)
    review_status = pg.ENUM(name="review_status", create_type=False)

    # ── users ──────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", pg.CITEXT(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("display_name", sa.String(120), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("role", user_role, nullable=False, server_default="buyer"),
        sa.Column("is_creator_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("stripe_customer_id", sa.String(64), nullable=True),
        sa.Column("stripe_connect_account_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])

    # ── creator_profiles ───────────────────────────────────────────────
    op.create_table(
        "creator_profiles",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("handle", pg.CITEXT(), nullable=False, unique=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("website_url", sa.Text(), nullable=True),
        sa.Column("social", pg.JSONB(), nullable=True),
        sa.Column("industries", pg.ARRAY(sa.String()), nullable=True),
        sa.Column("payout_country", sa.CHAR(2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_creator_profiles_handle", "creator_profiles", ["handle"], unique=True)

    # ── api_tokens ─────────────────────────────────────────────────────
    op.create_table(
        "api_tokens",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("token_hash", sa.String(1024), nullable=False),
        sa.Column("prefix", sa.String(32), nullable=False, unique=True),
        sa.Column("scopes", pg.ARRAY(sa.String()), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_api_tokens_user_id", "api_tokens", ["user_id"])
    op.create_index("ix_api_tokens_prefix", "api_tokens", ["prefix"])

    # ── categories ─────────────────────────────────────────────────────
    op.create_table(
        "categories",
        sa.Column("slug", pg.CITEXT(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_slug", pg.CITEXT(), sa.ForeignKey("categories.slug", ondelete="SET NULL"), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )

    # ── skills ─────────────────────────────────────────────────────────
    op.create_table(
        "skills",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("creator_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slug", pg.CITEXT(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("tagline", sa.String(140), nullable=True),
        sa.Column("description_md", sa.Text(), nullable=True),
        sa.Column("category", pg.CITEXT(), sa.ForeignKey("categories.slug", ondelete="SET NULL"), nullable=True),
        sa.Column("tags", pg.ARRAY(sa.String()), nullable=True),
        sa.Column("cover_image_url", sa.Text(), nullable=True),
        sa.Column("screenshots", pg.ARRAY(sa.String()), nullable=True),
        sa.Column("status", skill_status, nullable=False, server_default="draft"),
        # latest_version_id FK added after skill_versions exists (circular).
        sa.Column("latest_version_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column("pricing_model", pricing_model, nullable=False, server_default="free"),
        sa.Column("one_time_price_cents", sa.Integer(), nullable=True),
        sa.Column("subscription_price_cents", sa.Integer(), nullable=True),
        sa.Column("support_included", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("total_sales", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rating_avg", sa.Numeric(3, 2), nullable=True),
        sa.Column("rating_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("creator_id", "slug", name="uq_skills_creator_slug"),
    )
    op.create_index("ix_skills_status_category", "skills", ["status", "category"])
    op.create_index("ix_skills_creator_id", "skills", ["creator_id"])
    op.execute(
        "CREATE INDEX ix_skills_search ON skills USING GIN ("
        "to_tsvector('english', coalesce(name,'') || ' ' || coalesce(tagline,'') || ' ' || coalesce(description_md,''))"
        ");"
    )
    op.execute("CREATE INDEX ix_skills_tags ON skills USING GIN (tags);")

    # ── skill_versions ─────────────────────────────────────────────────
    op.create_table(
        "skill_versions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("skill_id", pg.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("content_hash", sa.CHAR(64), nullable=False),
        sa.Column("storage_url", sa.Text(), nullable=False),
        sa.Column("ai_requirements", pg.JSONB(), nullable=True),
        sa.Column("changelog_md", sa.Text(), nullable=True),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("released_by", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_yanked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.UniqueConstraint("skill_id", "version", name="uq_skill_versions_skill_version"),
    )
    op.create_index("ix_skill_versions_skill_id", "skill_versions", ["skill_id"])
    op.create_foreign_key(
        "fk_skills_latest_version_id_skill_versions",
        "skills", "skill_versions",
        ["latest_version_id"], ["id"],
        ondelete="SET NULL",
    )

    # ── orders ─────────────────────────────────────────────────────────
    op.create_table(
        "orders",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("buyer_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("stripe_payment_intent_id", sa.String(128), nullable=True, unique=True),
        sa.Column("subtotal_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("platform_fee_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("creator_payout_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.CHAR(3), nullable=False, server_default="USD"),
        sa.Column("status", order_status, nullable=False, server_default="pending"),
        sa.Column("placed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_orders_buyer_id", "orders", ["buyer_id"])

    # ── order_items ────────────────────────────────────────────────────
    op.create_table(
        "order_items",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", pg.UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", pg.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("skill_version_id", pg.UUID(as_uuid=True), sa.ForeignKey("skill_versions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("platform_fee_cents", sa.Integer(), nullable=False),
        sa.Column("creator_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_order_items_creator_id", "order_items", ["creator_id"])
    op.create_index("ix_order_items_skill_id", "order_items", ["skill_id"])

    # ── subscriptions ──────────────────────────────────────────────────
    op.create_table(
        "subscriptions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("buyer_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("skill_id", pg.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("stripe_subscription_id", sa.String(128), nullable=True, unique=True),
        sa.Column("status", subscription_status, nullable=False, server_default="active"),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("buyer_id", "skill_id", name="uq_subscriptions_buyer_skill"),
    )
    op.create_index("ix_subscriptions_buyer_id", "subscriptions", ["buyer_id"])
    op.create_index("ix_subscriptions_skill_id", "subscriptions", ["skill_id"])

    # ── licenses ───────────────────────────────────────────────────────
    op.create_table(
        "licenses",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("buyer_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("skill_id", pg.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("source", license_source, nullable=False),
        sa.Column("source_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("max_version", sa.String(32), nullable=True),
        sa.Column("support_tier", support_tier, nullable=False, server_default="none"),
        sa.Column("status", license_status, nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_licenses_buyer_skill_status", "licenses", ["buyer_id", "skill_id", "status"])
    op.create_index("ix_licenses_skill_id", "licenses", ["skill_id"])

    # ── payouts ────────────────────────────────────────────────────────
    op.create_table(
        "payouts",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("creator_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("stripe_transfer_id", sa.String(128), nullable=True, unique=True),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.CHAR(3), nullable=False, server_default="USD"),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", payout_status, nullable=False, server_default="pending"),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_payouts_creator_id", "payouts", ["creator_id"])

    # ── reviews ────────────────────────────────────────────────────────
    op.create_table(
        "reviews",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("skill_id", pg.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("license_id", pg.UUID(as_uuid=True), sa.ForeignKey("licenses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(160), nullable=True),
        sa.Column("body_md", sa.Text(), nullable=True),
        sa.Column("status", review_status, nullable=False, server_default="visible"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("skill_id", "author_id", name="uq_reviews_skill_author"),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_range"),
    )
    op.create_index("ix_reviews_skill_status_created", "reviews", ["skill_id", "status", "created_at"])

    # ── audit_log ──────────────────────────────────────────────────────
    op.create_table(
        "audit_log",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("target_type", sa.String(64), nullable=True),
        sa.Column("target_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", pg.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_log_actor_id", "audit_log", ["actor_id"])
    op.create_index("ix_audit_log_action", "audit_log", ["action"])
    op.create_index("ix_audit_log_target", "audit_log", ["target_type", "target_id"])


def downgrade() -> None:
    # Drop in reverse dependency order.
    op.drop_table("audit_log")
    op.drop_table("reviews")
    op.drop_table("payouts")
    op.drop_table("licenses")
    op.drop_table("subscriptions")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_constraint("fk_skills_latest_version_id_skill_versions", "skills", type_="foreignkey")
    op.drop_table("skill_versions")
    op.execute("DROP INDEX IF EXISTS ix_skills_search;")
    op.execute("DROP INDEX IF EXISTS ix_skills_tags;")
    op.drop_table("skills")
    op.drop_table("categories")
    op.drop_table("api_tokens")
    op.drop_table("creator_profiles")
    op.drop_table("users")

    bind = op.get_bind()
    for name in (
        "review_status", "payout_status", "support_tier", "license_status",
        "license_source", "subscription_status", "order_status",
        "pricing_model", "skill_status", "user_role",
    ):
        sa.Enum(name=name).drop(bind, checkfirst=True)
