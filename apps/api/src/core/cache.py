"""Lightweight Redis caching helper with an in-memory test façade.

The composer (T-07) caches per-buyer composed vault descriptors for 24h
per ADR-006 §Composition cache. To keep the test suite hermetic — and to
avoid forcing every vault unit test to spin up a real Redis pool — the
helper resolves its backend at call time:

* Production / dev (``settings.is_test`` is ``False``): the helper goes
  through the project's ``redis.asyncio`` client.
* Tests (``settings.is_test`` is ``True``) OR when ``SKG_CACHE_INMEM=1``:
  the helper uses a process-local dict. The dict honours TTL expiry on
  read so a stale entry behaves the same as a real Redis miss.

The public surface is intentionally tiny — only the two operations the
composer needs:

* :func:`get_or_compute` — atomic-from-the-caller's-perspective cache
  lookup that runs ``compute_fn`` on a miss and stores the result.
* :func:`invalidate` — drop a key (test-only, or for future creator-side
  rebuild webhooks).

Values are JSON-encoded on write so the helper plays nicely with both
backends (Redis stores strings, dicts store the same).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import TYPE_CHECKING, Any, TypeVar

from redis.asyncio import Redis

from src.core.config import settings

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

log = logging.getLogger(__name__)

T = TypeVar("T")


# ── Backend selection ────────────────────────────────────────────────


def _use_inmem() -> bool:
    """Return True when the in-memory store should be used.

    Two trigger paths:

    1. ``ENV=test`` (the project's standard test-mode signal).
    2. ``SKG_CACHE_INMEM=1`` env var — for ad-hoc scripts that want the
       helper to behave like tests without flipping the whole env.
    """
    if settings.is_test:
        return True
    return os.environ.get("SKG_CACHE_INMEM", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


# ── In-memory store ──────────────────────────────────────────────────


# (value_json, expires_at_monotonic_seconds | None)
_InMemEntry = tuple[str, float | None]
_inmem_store: dict[str, _InMemEntry] = {}
_inmem_lock = asyncio.Lock()


def reset_inmem_for_tests() -> None:
    """Drop every entry from the in-memory store.

    Tests call this between cases so cached results don't leak across
    fixtures.
    """
    _inmem_store.clear()


def _now() -> float:
    return time.monotonic()


async def _inmem_get(key: str) -> str | None:
    async with _inmem_lock:
        entry = _inmem_store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at is not None and _now() > expires_at:
            _inmem_store.pop(key, None)
            return None
        return value


async def _inmem_set(key: str, value: str, *, ttl_seconds: int | None) -> None:
    async with _inmem_lock:
        expires_at = _now() + ttl_seconds if ttl_seconds else None
        _inmem_store[key] = (value, expires_at)


async def _inmem_delete(key: str) -> None:
    async with _inmem_lock:
        _inmem_store.pop(key, None)


# ── Redis backend ────────────────────────────────────────────────────


_redis_client: Redis | None = None


def _redis() -> Redis:
    """Return a process-wide Redis client.

    The composer's caller (a FastAPI request handler) sees this client
    once per process — connection pooling lives inside redis-py.
    """
    global _redis_client  # noqa: PLW0603 — module-level lazy singleton
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def set_redis_client_for_tests(client: Redis | None) -> None:
    """Inject a custom Redis client (or ``None`` to reset).

    Used by the integration tests that want to talk to a real Redis
    container while the rest of the suite runs against the in-memory
    backend.
    """
    global _redis_client  # noqa: PLW0603 — test-only singleton swap
    _redis_client = client


# ── Public API ───────────────────────────────────────────────────────


async def get_or_compute(
    key: str,
    compute_fn: Callable[[], Awaitable[Any]],
    *,
    ttl_seconds: int,
) -> tuple[Any, bool]:
    """Return the cached value at ``key`` or compute + store one.

    Returns ``(value, cache_hit)``. The value is a JSON-decoded Python
    object — ``compute_fn`` must return something JSON-serialisable.

    On a hit, the cached value is returned and ``compute_fn`` is NOT
    called. On a miss, ``compute_fn`` runs once and its result is stored
    with the given TTL before being returned.

    The function does not provide cross-process locking — two parallel
    requests for the same key may both compute. That's acceptable for
    the composer because:

    * Computation is idempotent given the same inputs.
    * The two writers will produce the same payload (composer's
      cache_key already encodes occupation_build_id + persona_build_ids).
    * One winner's ``set`` clobbers the other harmlessly.
    """
    raw = await _read(key)
    if raw is not None:
        try:
            return json.loads(raw), True
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
            log.warning(
                "cache.deserialise_failed",
                extra={"key": key, "error": str(exc)},
            )
            # Treat a corrupted entry as a miss and overwrite below.

    value = await compute_fn()
    payload = json.dumps(value, default=str, sort_keys=True)
    await _write(key, payload, ttl_seconds=ttl_seconds)
    return value, False


async def invalidate(key: str) -> None:
    """Drop ``key`` from the cache.

    Used by composer cache invalidation logic when a new vault_build
    succeeds — though in practice the build_id is part of the cache key
    so a new build naturally generates a new key and the stale one ages
    out at its TTL.
    """
    await _delete(key)


# ── Backend dispatch ─────────────────────────────────────────────────


async def _read(key: str) -> str | None:
    if _use_inmem():
        return await _inmem_get(key)
    client = _redis()
    val = await client.get(key)
    if val is None:
        return None
    if isinstance(val, bytes):
        return val.decode("utf-8")
    return str(val)


async def _write(key: str, value: str, *, ttl_seconds: int) -> None:
    if _use_inmem():
        await _inmem_set(key, value, ttl_seconds=ttl_seconds)
        return
    client = _redis()
    if ttl_seconds > 0:
        await client.set(key, value, ex=ttl_seconds)
    else:
        await client.set(key, value)


async def _delete(key: str) -> None:
    if _use_inmem():
        await _inmem_delete(key)
        return
    client = _redis()
    await client.delete(key)


__all__ = [
    "get_or_compute",
    "invalidate",
    "reset_inmem_for_tests",
    "set_redis_client_for_tests",
]
