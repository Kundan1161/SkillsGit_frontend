"""Shared fixtures for ``apps/api/tests/integration/``.

The integration suite (T-14, Wave 5) exercises end-to-end flows
through the real service layer using an in-memory SQLite engine and
:class:`InMemoryStorage`. Tests run fast (each in <1s) and stay
hermetic; production parity is enforced by the nightly
``team-smoke.yml`` workflow which runs the same fleet against
Postgres + Redis + MinIO.

This conftest is intentionally self-contained — pytest's conftest
discovery does NOT pull in the project-level ``apps/api/tests/conftest.py``
when collecting ``tests/integration/test_*.py`` because the integration
tests need an inline-build vault façade and storage override that the
unit suite doesn't want.
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
os.environ["SKG_CAPTURE_LLM_STUB"] = "1"
os.environ["SKG_LLM_STUB"] = "1"
os.environ.setdefault("SKG_CACHE_INMEM", "1")

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
    """Per-test in-memory sqlite engine with every model loaded."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

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
    """Inject a fresh :class:`InMemoryStorage` for each integration test."""
    storage = InMemoryStorage(bucket="test-integration-bucket")
    set_storage(storage)
    yield storage
    # Reset back to the default lazy singleton so unrelated tests
    # don't see stale objects.
    set_storage(InMemoryStorage(bucket="test-integration-bucket"))


@pytest.fixture(autouse=True)
def _inline_builds_in_integration_tests() -> Iterator[None]:
    """Force the jobs façade to run builds inline for integration tests."""
    from src.vault import jobs as vault_jobs

    vault_jobs.set_inline_builds_for_tests(True)
    try:
        yield
    finally:
        vault_jobs.set_inline_builds_for_tests(False)


@pytest.fixture(autouse=True)
def _reset_compose_cache() -> Iterator[None]:
    """Wipe the composer's in-memory cache between tests.

    Without this every test's composed bundle is keyed on the previous
    test's buyer_id/build_id sha — which can yield a false `cache_hit=True`
    when test setup happens to produce identical primitive ids (rare under
    UUID7 but the cost of being defensive is one dict.clear()).
    """
    yield
    try:
        from src.core import cache as cache_mod

        cache_mod.reset_inmem_for_tests()
    except Exception:
        pass


# ── Fake Redis shared with quota + auth code paths ───────────────────


class _FakeRedis:
    """In-memory Redis-protocol fake covering capture.quota +
    auth/session surfaces. Mirrors the per-module conftests in
    ``src/capture/tests/`` and ``src/occupations/tests/``.
    """

    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def incr(self, key: str) -> int:
        n = int(self.store.get(key, "0")) + 1
        self.store[key] = str(n)
        return n

    async def decr(self, key: str) -> int:
        n = max(0, int(self.store.get(key, "0")) - 1)
        self.store[key] = str(n)
        return n

    async def expire(self, _key: str, _ttl: int) -> bool:
        return True

    async def setex(self, key: str, _ttl: int, value: str) -> bool:
        self.store[key] = value
        return True

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def delete(self, key: str) -> int:
        return 1 if self.store.pop(key, None) is not None else 0

    async def exists(self, key: str) -> int:
        return 1 if key in self.store else 0


@pytest_asyncio.fixture(scope="function")
async def fake_redis(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[_FakeRedis]:
    """Fake Redis swapped into the auth-deps singleton.

    Capture quota imports ``get_redis`` from ``src.auth.deps`` at
    call time, so monkeypatching the module-level singleton + getter
    both reaches the quota path.
    """
    import src.auth.deps as auth_deps

    fake = _FakeRedis()
    monkeypatch.setattr(auth_deps, "_redis", fake)
    monkeypatch.setattr(auth_deps, "get_redis", lambda: fake)
    yield fake
