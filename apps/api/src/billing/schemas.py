"""Pydantic schemas for the billing module.

All money is integer cents. See ``02-data-model-core.md`` for canonical
field semantics and ``03-pricing-and-checkout.md`` for endpoint shapes.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ── Requests ──────────────────────────────────────────────────────────
class CreateCheckoutSessionRequest(BaseModel):
    skill_id: uuid.UUID
    # Optional in-body idempotency; the ``Idempotency-Key`` header is the
    # canonical mechanism per ``shared/api-conventions.md``. We accept the
    # body field for clients that can't easily set headers.
    idempotency_key: str | None = Field(default=None, max_length=64)


class StartOnboardingRequest(BaseModel):
    # ISO 3166-1 alpha-2 (e.g. ``US``, ``GB``).
    payout_country: str = Field(..., min_length=2, max_length=2)


class RefundRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


# ── Responses ─────────────────────────────────────────────────────────
class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_…",
                    "session_id": "cs_test_a1b2…",
                }
            ]
        }
    )


class FinalizeResponse(BaseModel):
    """UI-side polling response while the webhook lands."""

    session_id: str
    status: str  # ``open`` | ``complete`` | ``expired``
    order_id: uuid.UUID | None = None
    license_id: uuid.UUID | None = None


class OnboardingStartResponse(BaseModel):
    url: str
    account_id: str


class OnboardingStatusResponse(BaseModel):
    account_id: str | None
    details_submitted: bool
    payouts_enabled: bool
    charges_enabled: bool


class BillingPortalResponse(BaseModel):
    url: str


class PriceBreakdown(BaseModel):
    """Helper for the UI checkout summary card."""

    amount_cents: int
    platform_fee_cents: int
    creator_payout_cents: int
    currency: str = "USD"


class OrderItemRead(BaseModel):
    id: uuid.UUID
    skill_id: uuid.UUID
    skill_version_id: uuid.UUID
    price_cents: int
    platform_fee_cents: int
    creator_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    id: uuid.UUID
    buyer_id: uuid.UUID
    status: str
    subtotal_cents: int
    platform_fee_cents: int
    creator_payout_cents: int
    currency: str
    placed_at: datetime | None
    stripe_payment_intent_id: str | None
    items: list[OrderItemRead] = []

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    items: list[OrderRead]
    page: dict[str, int | str | bool | None]


class LicenseRead(BaseModel):
    id: uuid.UUID
    buyer_id: uuid.UUID
    skill_id: uuid.UUID
    source: str
    source_id: uuid.UUID
    granted_at: datetime
    expires_at: datetime | None
    max_version: str | None
    support_tier: str
    status: str

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "BillingPortalResponse",
    "CheckoutSessionResponse",
    "CreateCheckoutSessionRequest",
    "FinalizeResponse",
    "LicenseRead",
    "OnboardingStartResponse",
    "OnboardingStatusResponse",
    "OrderItemRead",
    "OrderListResponse",
    "OrderRead",
    "PriceBreakdown",
    "RefundRequest",
    "StartOnboardingRequest",
]
