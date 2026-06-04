"""Tests for :mod:`src.capture.quota`.

T-05 acceptance bullet 4 (11th extract in a calendar month returns 429
with ``capture.quota_exceeded``) is exercised end-to-end here; the
router-level run lives in :mod:`test_router.py`.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.capture import quota

# ── Key + reset-at helpers ───────────────────────────────────────────


def test_quota_key_uses_creator_id_and_yyyy_mm() -> None:
    creator_id = uuid.uuid4()
    now = datetime(2026, 5, 26, tzinfo=UTC)
    key = quota.quota_key(creator_id, now=now)
    assert key == f"capture:quota:{creator_id}:2026-05"


def test_quota_key_rolls_over_at_month_boundary() -> None:
    creator_id = uuid.uuid4()
    jan = datetime(2026, 1, 31, 23, 59, 59, tzinfo=UTC)
    feb = datetime(2026, 2, 1, 0, 0, 0, tzinfo=UTC)
    assert quota.quota_key(creator_id, now=jan).endswith("2026-01")
    assert quota.quota_key(creator_id, now=feb).endswith("2026-02")


# ── Reserve happy path ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reserve_increments_counter() -> None:
    from src.capture.tests.conftest import _FakeRedis

    creator_id = uuid.uuid4()
    redis = _FakeRedis()
    used = await quota.reserve(creator_id, redis=redis)
    assert used == 1
    used2 = await quota.reserve(creator_id, redis=redis)
    assert used2 == 2


@pytest.mark.asyncio
async def test_peek_does_not_mutate_counter() -> None:
    from src.capture.tests.conftest import _FakeRedis

    creator_id = uuid.uuid4()
    redis = _FakeRedis()
    used, cap = await quota.peek(creator_id, redis=redis)
    assert used == 0
    assert cap == 10  # default cap from .env.example
    await quota.reserve(creator_id, redis=redis)
    used2, cap2 = await quota.peek(creator_id, redis=redis)
    assert used2 == 1
    assert cap2 == cap


# ── Reserve denies past the cap ──────────────────────────────────────


@pytest.mark.asyncio
async def test_reserve_blocks_eleventh_attempt() -> None:
    """T-05 acceptance bullet 4 — service-layer 429 on the 11th call."""
    from src.capture.tests.conftest import _FakeRedis

    creator_id = uuid.uuid4()
    redis = _FakeRedis()
    for _ in range(10):
        await quota.reserve(creator_id, redis=redis)

    with pytest.raises(quota.CaptureQuotaExceededError) as exc:
        await quota.reserve(creator_id, redis=redis)
    assert exc.value.code == "capture.quota_exceeded"
    assert exc.value.status_code == 429


@pytest.mark.asyncio
async def test_reserve_decrement_after_block_keeps_counter_at_cap() -> None:
    """A blocked attempt does NOT permanently bump the counter past cap."""
    from src.capture.tests.conftest import _FakeRedis

    creator_id = uuid.uuid4()
    redis = _FakeRedis()
    for _ in range(10):
        await quota.reserve(creator_id, redis=redis)
    with pytest.raises(quota.CaptureQuotaExceededError):
        await quota.reserve(creator_id, redis=redis)

    used, cap = await quota.peek(creator_id, redis=redis)
    assert used == cap == 10  # the failed attempt was refunded.


# ── Refund ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_refund_decrements_counter() -> None:
    from src.capture.tests.conftest import _FakeRedis

    creator_id = uuid.uuid4()
    redis = _FakeRedis()
    await quota.reserve(creator_id, redis=redis)
    await quota.reserve(creator_id, redis=redis)
    remaining = await quota.refund(creator_id, redis=redis)
    assert remaining == 1


@pytest.mark.asyncio
async def test_refund_floors_at_zero() -> None:
    from src.capture.tests.conftest import _FakeRedis

    creator_id = uuid.uuid4()
    redis = _FakeRedis()
    remaining = await quota.refund(creator_id, redis=redis)
    assert remaining == 0
    # Still zero — should not have gone negative.
    used, _cap = await quota.peek(creator_id, redis=redis)
    assert used == 0


# ── Per-creator isolation ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_two_creators_get_independent_buckets() -> None:
    from src.capture.tests.conftest import _FakeRedis

    a = uuid.uuid4()
    b = uuid.uuid4()
    redis = _FakeRedis()
    for _ in range(10):
        await quota.reserve(a, redis=redis)
    # B is still fresh.
    used_b, _cap = await quota.peek(b, redis=redis)
    assert used_b == 0
    # Reserving B's first slot doesn't trip A's cap.
    n = await quota.reserve(b, redis=redis)
    assert n == 1


@pytest.mark.asyncio
async def test_month_rollover_independent_buckets() -> None:
    from src.capture.tests.conftest import _FakeRedis

    creator_id = uuid.uuid4()
    redis = _FakeRedis()
    jan = datetime(2026, 1, 15, tzinfo=UTC)
    feb = datetime(2026, 2, 1, tzinfo=UTC)
    # Burn January's cap.
    for _ in range(10):
        await quota.reserve(creator_id, redis=redis, now=jan)
    with pytest.raises(quota.CaptureQuotaExceededError):
        await quota.reserve(creator_id, redis=redis, now=jan)
    # February starts fresh.
    n = await quota.reserve(creator_id, redis=redis, now=feb)
    assert n == 1
