"""Redis-backed monthly capture-extraction quota.

ADR-008 + ``team/02-api-surface.md`` §Capture quota: the platform-key
Claude budget is bounded per creator per calendar month. The default
cap is 10 captures/month; deferred-paid tiers are Phase 2.

Key layout: ``capture:quota:{creator_id}:{YYYY-MM}`` (the calendar
month is the UTC month — bumps over at the first of the month UTC).
TTL is 32 days so old keys evict naturally; we never need to GC.

Lifecycle:
- :func:`reserve` is the gate. Atomically incr the counter; if the
  post-incr value exceeds the cap, decrement and raise
  ``CaptureQuotaExceededError``.
- :func:`peek` is read-only for the UI (status header).
- :func:`refund` rolls back a reservation when the downstream extract
  fails after the reservation was already taken (network blip, parse
  error). Implementation: decrement, with a floor of 0.

The Redis client is fetched via :func:`src.auth.deps.get_redis` so
tests' fake-Redis swap works uniformly. The fake-Redis used in the
sibling occupations/personas tests covers ``incr/expire/decr/get``,
which is all we need here.
"""

from __future__ import annotations

import logging
import uuid  # noqa: TC003  (UUID is used at runtime via function args)
from datetime import UTC, datetime
from typing import Any, Protocol

from src.auth.deps import get_redis
from src.core.config import settings
from src.core.errors import AppError, ErrorDetail

log = logging.getLogger(__name__)

# 32 days — comfortably outlasts a calendar month so the natural rollover
# at the first of the next month doesn't need explicit cleanup.
_TTL_SECONDS: int = 32 * 24 * 3600


class CaptureQuotaExceededError(AppError):
    """Raised when a creator hits the monthly cap.

    Renders as 429 with ``capture.quota_exceeded`` per
    ``team/04-capture-flow.md`` §Failure modes.
    """

    def __init__(self, *, used: int, cap: int, reset_at_iso: str) -> None:
        super().__init__(
            code="capture.quota_exceeded",
            message=(
                f"Monthly capture quota exceeded ({used}/{cap}). "
                f"Resets on {reset_at_iso}."
            ),
            status_code=429,
            details=[
                ErrorDetail(
                    field="creator_id",
                    code="quota_exceeded",
                    message=(
                        f"You've used {used} of {cap} captures this month. "
                        "Wait for the monthly rollover or contact support "
                        "about a higher tier."
                    ),
                )
            ],
        )


# ── Redis-protocol surface we actually use ───────────────────────────


class _RedisLike(Protocol):
    async def incr(self, key: str) -> int: ...
    async def expire(self, key: str, ttl: int) -> Any: ...
    async def get(self, key: str) -> Any: ...
    async def decr(self, key: str) -> Any: ...


# ── Key helpers ──────────────────────────────────────────────────────


def _bucket_for(now: datetime) -> str:
    return now.strftime("%Y-%m")


def quota_key(creator_id: uuid.UUID, *, now: datetime | None = None) -> str:
    """Compute the Redis key for ``creator_id`` in ``now``'s UTC month."""
    if now is None:
        now = datetime.now(UTC)
    return f"capture:quota:{creator_id}:{_bucket_for(now)}"


def _cap() -> int:
    """Resolve the active monthly cap from settings.

    Re-read on each call so test overrides via env vars + cache clears
    take effect without restarting the process.
    """
    return int(settings.SKG_CAPTURE_QUOTA_PER_MONTH)


def _reset_at_iso(now: datetime) -> str:
    """First-of-next-month UTC midnight ISO 8601."""
    if now.month == 12:
        next_month = now.replace(
            year=now.year + 1, month=1, day=1,
            hour=0, minute=0, second=0, microsecond=0,
        )
    else:
        next_month = now.replace(
            month=now.month + 1, day=1,
            hour=0, minute=0, second=0, microsecond=0,
        )
    return next_month.isoformat()


# ── Public API ───────────────────────────────────────────────────────


async def peek(
    creator_id: uuid.UUID,
    *,
    redis: _RedisLike | None = None,
    now: datetime | None = None,
) -> tuple[int, int]:
    """Return ``(used, cap)`` without mutating the counter.

    ``used`` is 0 when no quota has been consumed this month (the key
    doesn't exist yet).
    """
    r = redis or get_redis()
    now = now or datetime.now(UTC)
    raw = await r.get(quota_key(creator_id, now=now))
    used = int(raw) if raw is not None else 0
    return used, _cap()


async def reserve(
    creator_id: uuid.UUID,
    *,
    redis: _RedisLike | None = None,
    now: datetime | None = None,
) -> int:
    """Atomically reserve one quota unit.

    Returns the post-incr count when accepted; raises
    :class:`CaptureQuotaExceededError` when the cap is exceeded (and
    decrements the counter so the failed attempt doesn't permanently
    burn a slot).
    """
    r = redis or get_redis()
    now = now or datetime.now(UTC)
    key = quota_key(creator_id, now=now)
    new_count = int(await r.incr(key))
    # Set TTL on first write — INCR's expire-on-miss semantics differ
    # between real Redis (no auto-expire) and fakes. Cheap to set every
    # time; Redis EXPIRE is O(1).
    await r.expire(key, _TTL_SECONDS)

    cap = _cap()
    if new_count > cap:
        # Refund the failed reservation so a flood of 429s doesn't
        # cement the over-cap state for the rest of the month.
        try:
            await r.decr(key)
        except Exception:  # pragma: no cover — best effort
            log.exception("quota.refund_failed", extra={"creator_id": str(creator_id)})
        raise CaptureQuotaExceededError(
            used=new_count,
            cap=cap,
            reset_at_iso=_reset_at_iso(now),
        )
    return new_count


async def refund(
    creator_id: uuid.UUID,
    *,
    redis: _RedisLike | None = None,
    now: datetime | None = None,
) -> int:
    """Roll back a previously-reserved quota unit.

    Used when a reserved extraction fails downstream (e.g. parse error
    on the LLM response): the creator should not pay for a slot that
    never produced a draft. The floor is 0; we never go negative.
    """
    r = redis or get_redis()
    now = now or datetime.now(UTC)
    key = quota_key(creator_id, now=now)
    raw = await r.get(key)
    current = int(raw) if raw is not None else 0
    if current <= 0:
        return 0
    await r.decr(key)
    return current - 1


__all__ = [
    "CaptureQuotaExceededError",
    "peek",
    "quota_key",
    "refund",
    "reserve",
]
