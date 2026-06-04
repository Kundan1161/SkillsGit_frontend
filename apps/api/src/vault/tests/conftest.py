"""Test fixtures for ``src/vault/tests/``.

The vault module is not mounted in ``apps/api/src/main.py`` (T-07
mounts the future vault router); these fixtures stand alone so the
brief's verification command::

    uv run pytest src/vault/tests/ -v

…works without depending on the project-level conftest. Mirrors the
sibling ``src/occupations/tests/conftest.py`` plus an in-memory storage
override so the builder can put + get objects without S3.
"""

from __future__ import annotations

import asyncio
import os
import sqlite3
import uuid
from collections.abc import AsyncIterator, Iterator
from typing import Any

# Set env BEFORE importing src.* so `Settings` reads the test values.
os.environ.setdefault("ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-which-is-32+chars-ok-ok")
os.environ.setdefault(
    "PLATFORM_HMAC_KEY", "test-hmac-key-which-is-32+chars-ok-ok-ok"
)

# UUID adapter for sqlite (cross-dialect tests).
sqlite3.register_adapter(uuid.UUID, str)

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import get_settings
from src.core.db import Base
from src.storage.s3 import InMemoryStorage, set_storage

# Reset settings cache so the test-env vars take effect.
get_settings.cache_clear()


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncIterator[Any]:
    """Per-test in-memory sqlite engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

    # Force import of every model module so Base.metadata is fully populated.
    import src.admin.models
    import src.billing.models
    import src.capture.models
    import src.catalog.models
    import src.occupations.models
    import src.personas.models
    import src.reviews.models
    import src.skills.models
    import src.users.models
    import src.vault.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine: Any) -> AsyncIterator[AsyncSession]:
    session_factory = async_sessionmaker(
        bind=db_engine,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
def memory_storage() -> Iterator[InMemoryStorage]:
    """Inject a fresh :class:`InMemoryStorage` for each test.

    The builder calls :func:`src.storage.s3.get_storage` to read source
    skill bodies and to put the final zip. Tests pre-populate the
    storage with ``put_object`` calls inside test bodies; the fixture
    handles reset between tests.
    """
    storage = InMemoryStorage(bucket="test-vault-bucket")
    set_storage(storage)
    yield storage
    # Reset back to the default (lazy) singleton so unrelated tests
    # don't see stale objects.
    set_storage(InMemoryStorage(bucket="test-vault-bucket"))


@pytest.fixture(autouse=True)
def _inline_builds_in_vault_tests() -> Iterator[None]:
    """Force the jobs façade to run builds inline for vault tests.

    The default test-mode behaviour is to short-circuit to a synth
    "queued" result so the legacy occupations/personas tests (which
    don't seed storage) don't trip on the builder's storage fetch.
    Vault tests need the real path — flip the flag here, restore on
    teardown.
    """
    from src.vault import jobs as vault_jobs

    vault_jobs.set_inline_builds_for_tests(True)
    try:
        yield
    finally:
        vault_jobs.set_inline_builds_for_tests(False)
