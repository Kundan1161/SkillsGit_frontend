"""Platform-fee math.

All amounts in **integer cents**. Never floats — see
``prompts/marketplace/03-pricing-and-checkout.md`` for the rule.

``PLATFORM_FEE_PERCENT`` is configurable via env. Banker's rounding
(half-to-even) is used to avoid systematic round-up drift across many
small transactions.
"""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal
from typing import TypedDict

from src.core.config import settings


class FeeBreakdown(TypedDict):
    platform_fee_cents: int
    creator_payout_cents: int


def _percent_to_decimal(percent: float | int | Decimal) -> Decimal:
    """Coerce a percent like ``20.0`` to ``Decimal('0.20')`` exactly."""
    # Going through ``str`` avoids float-binary surprises (20.0 → 20.0 exact).
    return (Decimal(str(percent)) / Decimal(100)).normalize()


def compute_fee(amount_cents: int, percent: float | None = None) -> int:
    """Compute the platform fee for ``amount_cents``.

    Banker's rounding (ROUND_HALF_EVEN) ensures fairness across many
    transactions.

    Args:
        amount_cents: Sale price in **integer cents**.
        percent: Override the platform percent. ``None`` uses
            ``settings.PLATFORM_FEE_PERCENT``.

    Returns:
        Platform fee in **integer cents** (always ``0 <= fee <= amount``).
    """
    if amount_cents < 0:
        raise ValueError("amount_cents must be non-negative")
    if amount_cents == 0:
        return 0

    pct = percent if percent is not None else settings.PLATFORM_FEE_PERCENT
    if pct < 0 or pct > 100:
        raise ValueError("percent must be in [0, 100]")

    raw = Decimal(amount_cents) * _percent_to_decimal(pct)
    # Quantize to whole cents using banker's rounding.
    fee_cents = int(raw.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))
    # Defensive clamp; rounding can never produce a negative but be safe.
    return max(0, min(amount_cents, fee_cents))


def breakdown(
    amount_cents: int, percent: float | None = None
) -> FeeBreakdown:
    """Return ``{platform_fee_cents, creator_payout_cents}``.

    Sum is exactly ``amount_cents`` (we don't lose pennies to rounding —
    the remainder always goes to the creator).
    """
    fee = compute_fee(amount_cents, percent)
    return {
        "platform_fee_cents": fee,
        "creator_payout_cents": amount_cents - fee,
    }


__all__ = ["FeeBreakdown", "breakdown", "compute_fee"]
