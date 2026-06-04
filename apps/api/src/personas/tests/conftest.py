"""Test fixtures for ``src/personas/tests/``.

Wave 2 ships the personas router but does NOT mount it in
``apps/api/src/main.py`` (the orchestrator does that after Wave 2
returns). The verification command in the brief is::

    uv run pytest src/personas/tests/ -v

…which means pytest's conftest discovery does NOT pick up
``apps/api/tests/conftest.py``. This file therefore re-implements the
necessary fixtures (test env, in-memory sqlite, fake Redis, http client
with the personas router mounted) self-contained — mirroring the
sibling ``src/occupations/tests/conftest.py``.
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
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import src.auth.deps as auth_deps
import src.core.db as core_db
from src.core.config import get_settings
from src.core.db import Base, get_db

# Reset settings cache so the test-env vars take effect.
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


@pytest_asyncio.fixture(scope="function")
async def client(
    db_engine: Any, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[AsyncClient]:
    """Test client with the personas router mounted on a fresh app."""
    from src.personas.router import router as personas_router

    test_sessionmaker = async_sessionmaker(
        bind=db_engine,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )
    monkeypatch.setattr(core_db, "engine", db_engine)
    monkeypatch.setattr(core_db, "SessionLocal", test_sessionmaker)

    fake = _FakeRedis()
    monkeypatch.setattr(auth_deps, "_redis", fake)
    monkeypatch.setattr(auth_deps, "get_redis", lambda: fake)
    import src.auth.router as auth_router
    monkeypatch.setattr(auth_router, "get_redis", lambda: fake)

    from src.main import create_app

    app = create_app()
    app.include_router(personas_router)

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


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> None:
    try:
        from src.core.rate_limits import limiter

        if hasattr(limiter, "_storage"):
            try:
                limiter._storage.reset()
            except Exception:
                pass
        if hasattr(limiter, "reset"):
            try:
                limiter.reset()
            except Exception:
                pass
    except Exception:
        pass
