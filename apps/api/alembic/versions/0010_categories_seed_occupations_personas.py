"""seed occupations + personas categories

Revision ID: 0010_categories_seed_occupations_personas
Revises: 0009_vault_builds_and_downloads
Create Date: 2026-05-26

Appends two listing-surface category slugs (per
``team/01-data-model-deltas.md`` §0010). These are display-side
concessions so the marketplace can filter ``category='occupations'``
without surfacing the ``skills.kind`` discriminator in the top nav.

Idempotent ``INSERT … ON CONFLICT DO NOTHING`` matches the seed pattern
established in ``0002_seed_categories``.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0010_categories_seed_occupations_personas"
down_revision: Union[str, None] = "0009_vault_builds_and_downloads"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SEED_CATEGORIES: list[tuple[str, str, str, int]] = [
    (
        "occupations",
        "Occupations",
        "Job-role playbooks built from curated skill bundles.",
        50,
    ),
    (
        "personas",
        "Personas",
        "Practitioner overlays — recorded situations layered onto an occupation.",
        51,
    ),
]


def upgrade() -> None:
    for slug, name, description, display_order in SEED_CATEGORIES:
        # ON CONFLICT DO NOTHING — re-running this migration on an env
        # that already has the rows must be a no-op.
        op.execute(
            "INSERT INTO categories (slug, name, description, display_order) "
            f"VALUES ('{slug}', '{name}', '{description}', {display_order}) "
            "ON CONFLICT (slug) DO NOTHING;"
        )


def downgrade() -> None:
    slugs = ", ".join(f"'{slug}'" for slug, *_ in SEED_CATEGORIES)
    op.execute(f"DELETE FROM categories WHERE slug IN ({slugs});")
