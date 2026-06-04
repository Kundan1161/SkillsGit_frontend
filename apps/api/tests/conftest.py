"""Shared test fixtures.

Tests run against an in-memory SQLite database (via aiosqlite) for speed.
Production uses Postgres + asyncpg; the models use ``with_variant`` to
support both dialects. The Redis client is replaced by a tiny in-memory
fake so the auth flow doesn't need an external service.

Set ``ENV=test`` so :mod:`src.core.rate_limits` skips Redis and uses an
in-memory limiter.
"""

from __future__ import annotations

import os
import sqlite3
import uuid

# Register sqlite adapters so cross-dialect models that store uuid.UUID
# values can round-trip through aiosqlite. Production uses Postgres which
# handles UUID natively; sqlite needs explicit string coercion.
sqlite3.register_adapter(uuid.UUID, lambda u: str(u))

# MUST be set before importing src — Settings reads env at import time.
os.environ.setdefault("ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-which-is-32+chars-ok-ok")
os.environ.setdefault(
    "PLATFORM_HMAC_KEY", "test-hmac-key-which-is-32+chars-ok-ok-ok"
)

import asyncio
from collections.abc import AsyncIterator, Iterator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import src.core.db as core_db  # noqa: E402
from src.auth import deps as auth_deps  # noqa: E402
from src.core.config import get_settings  # noqa: E402
from src.core.db import Base, get_db  # noqa: E402

# Force every test module-level import to refresh settings cache.
get_settings.cache_clear()


# ── In-memory fake Redis (covers the surface the auth code touches) ──
class _FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def incr(self, key: str) -> int:
        n = int(self.store.get(key, "0")) + 1
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


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncIterator[Any]:
    """Per-test in-memory sqlite engine. Each test starts fresh."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

    # Import all models so metadata is fully populated.
    import src.users.models  # noqa: F401
    import src.skills.models  # noqa: F401
    import src.billing.models  # noqa: F401
    import src.reviews.models  # noqa: F401
    import src.catalog.models  # noqa: F401
    import src.admin.models  # noqa: F401
    import src.occupations.models  # noqa: F401
    import src.personas.models  # noqa: F401
    import src.capture.models  # noqa: F401
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
        bind=db_engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_engine: Any, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[AsyncClient]:
    """Test client wired to the in-memory db + fake Redis."""
    # Swap the module-level engine + session factory so any code path that
    # imports SessionLocal directly hits the test DB.
    test_sessionmaker = async_sessionmaker(
        bind=db_engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
    )
    monkeypatch.setattr(core_db, "engine", db_engine)
    monkeypatch.setattr(core_db, "SessionLocal", test_sessionmaker)

    # Fake Redis singleton.
    fake = _FakeRedis()
    monkeypatch.setattr(auth_deps, "_redis", fake)
    monkeypatch.setattr(auth_deps, "get_redis", lambda: fake)

    # Patch get_redis in tokens / router / service uses via the auth_deps export.
    import src.auth.router as auth_router
    monkeypatch.setattr(auth_router, "get_redis", lambda: fake)

    # Build the app *after* the patches so dependency overrides resolve fresh.
    from src.main import create_app

    app = create_app()

    # Override the get_db dep to use our test sessionmaker.
    async def _override_get_db() -> AsyncIterator[AsyncSession]:
        async with test_sessionmaker() as s:
            try:
                yield s
            except Exception:
                await s.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture()
def fixtures_dir() -> str:
    import os.path

    return os.path.join(os.path.dirname(__file__), "fixtures", "skills")


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> None:
    """Clear the in-memory slowapi limiter between tests so back-to-back
    ``/v1/auth/register`` calls don't trip the per-IP cap."""
    try:
        from src.core.rate_limits import limiter

        if hasattr(limiter, "_storage"):
            try:
                limiter._storage.reset()  # type: ignore[attr-defined]
            except Exception:
                pass
        if hasattr(limiter, "reset"):
            try:
                limiter.reset()
            except Exception:
                pass
    except Exception:
        pass
