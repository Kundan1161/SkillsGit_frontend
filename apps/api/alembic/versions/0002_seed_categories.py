"""seed categories

Revision ID: 0002_seed_categories
Revises: 0001_initial
Create Date: 2026-05-14
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from sqlalchemy import column, table
from sqlalchemy.dialects.postgresql import CITEXT

revision: str = "0002_seed_categories"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Seed list per 02-data-model-core.md.
CATEGORIES: list[dict[str, str | int]] = [
    {"slug": "finance",          "name": "Finance",          "display_order": 10},
    {"slug": "design",           "name": "Design",           "display_order": 20},
    {"slug": "data",             "name": "Data",             "display_order": 30},
    {"slug": "marketing",        "name": "Marketing",        "display_order": 40},
    {"slug": "sales",            "name": "Sales",            "display_order": 50},
    {"slug": "legal",            "name": "Legal",            "display_order": 60},
    {"slug": "operations",       "name": "Operations",       "display_order": 70},
    {"slug": "engineering",      "name": "Engineering",      "display_order": 80},
    {"slug": "customer-support", "name": "Customer Support", "display_order": 90},
    {"slug": "productivity",     "name": "Productivity",     "display_order": 100},
    {"slug": "creative",         "name": "Creative",         "display_order": 110},
    {"slug": "research",         "name": "Research",         "display_order": 120},
    {"slug": "other",            "name": "Other",            "display_order": 999},
]


def upgrade() -> None:
    import sqlalchemy as sa

    categories_t = table(
        "categories",
        column("slug", CITEXT()),
        column("name", sa.String()),
        column("description", sa.String()),
        column("display_order", sa.Integer()),
    )
    op.bulk_insert(categories_t, CATEGORIES)


def downgrade() -> None:
    slugs = ", ".join(f"'{c['slug']}'" for c in CATEGORIES)
    op.execute(f"DELETE FROM categories WHERE slug IN ({slugs});")
