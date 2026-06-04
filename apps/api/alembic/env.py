"""Alembic environment — async, reads ``DATABASE_URL`` from settings.

Uses ``run_async`` to run migrations inside an asyncio context. Imports all
models so Alembic's autogenerate can see them.

The ``alembic_version.version_num`` column is widened beyond the Alembic
default (32 chars) so the longer revision identifiers introduced in Wave 1
(e.g. ``0010_categories_seed_occupations_personas``) fit. This is a
configuration setting — not a migration — and applies on every connect.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.core.config import settings
from src.core.db import Base

# Import every module's models so Base.metadata is fully populated.
import src.core.db  # noqa: F401  (AuditLog)
import src.users.models  # noqa: F401
import src.skills.models  # noqa: F401
import src.billing.models  # noqa: F401
import src.reviews.models  # noqa: F401
import src.occupations.models  # noqa: F401
import src.personas.models  # noqa: F401
import src.capture.models  # noqa: F401
import src.vault.models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    # Ensure alembic_version.version_num is wide enough for the longer
    # revision identifiers shipped in Wave 1 (the Alembic default of 32
    # is too short for e.g. "0010_categories_seed_occupations_personas").
    # Safe to run on every connect — creates the table if absent, widens
    # if already present.
    connection.execute(
        text(
            "CREATE TABLE IF NOT EXISTS alembic_version "
            "(version_num VARCHAR(128) NOT NULL, "
            "CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"
        )
    )
    connection.execute(
        text("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(128)")
    )
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        future=True,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
        # ``run_sync`` runs Alembic's own begin/commit per migration, but the
        # outer asyncpg connection still holds an open transaction that
        # SQLAlchemy expects us to close explicitly. Without this commit the
        # CREATE TABLE statements above are written to the connection but
        # rolled back when ``dispose()`` returns. (Async migrations gap from
        # Wave 1.)
        await connection.commit()
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
