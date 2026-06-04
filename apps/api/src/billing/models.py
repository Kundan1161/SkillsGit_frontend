"""Billing-side tables: orders, order_items, subscriptions, licenses, payouts.

See ``02-data-model-core.md`` for the canonical schema. Money is always
``Integer`` cents; timestamps always ``timestamptz``.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from typing import Any

from sqlalchemy import (
    CHAR,
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base, TimestampMixin, uuid7

_UUID = PG_UUID(as_uuid=True).with_variant(String(36), "sqlite")


# ── Enums ─────────────────────────────────────────────────────────────
class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    FAILED = "failed"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    PAUSED = "paused"


class LicenseSource(str, enum.Enum):
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    FREE = "free"
    FREEMIUM = "freemium"
    GRANT = "grant"


class LicenseStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class LicenseCompositionRole(str, enum.Enum):
    """How a license participates in vault composition (ADR-002, ADR-006).

    - ``standalone`` — legacy, single-skill download. Every license
      created before 0009 backfills to this.
    - ``occupation`` — anchor license; the buyer downloads a composed
      vault keyed off this license id.
    - ``persona`` — overlay; must be paired with an active occupation
      license to compose. ``target_occupation_skill_id`` is a snapshot
      of the persona's parent at purchase time.
    """

    OCCUPATION = "occupation"
    PERSONA = "persona"
    STANDALONE = "standalone"


class SupportTier(str, enum.Enum):
    NONE = "none"
    BASIC = "basic"
    PRIORITY = "priority"


class PayoutStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


class WebhookEventStatus(str, enum.Enum):
    """Lifecycle of an inbound Stripe webhook event."""

    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"


# ── Tables ────────────────────────────────────────────────────────────
class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True, unique=True
    )
    subtotal_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    platform_fee_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    creator_payout_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False, default="USD")
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=OrderStatus.PENDING,
    )
    placed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_orders_buyer_id", "buyer_id"),)


class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    order_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False
    )
    skill_version_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("skill_versions.id", ondelete="RESTRICT"), nullable=False
    )
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    platform_fee_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    order: Mapped[Order] = relationship(back_populates="items")

    __table_args__ = (
        Index("ix_order_items_creator_id", "creator_id"),
        Index("ix_order_items_skill_id", "skill_id"),
    )


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False
    )
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True, unique=True
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, name="subscription_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=SubscriptionStatus.ACTIVE,
    )
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_subscriptions_buyer_id", "buyer_id"),
        Index("ix_subscriptions_skill_id", "skill_id"),
        UniqueConstraint(
            "buyer_id", "skill_id", name="uq_subscriptions_buyer_skill"
        ),
    )


class License(Base, TimestampMixin):
    __tablename__ = "licenses"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False
    )
    source: Mapped[LicenseSource] = mapped_column(
        Enum(LicenseSource, name="license_source", values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    # FK kept logical (no DB constraint) because source_id can point at either
    # order_items.id or subscriptions.id depending on source.
    source_id: Mapped[uuid.UUID] = mapped_column(_UUID, nullable=False)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    max_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    support_tier: Mapped[SupportTier] = mapped_column(
        Enum(SupportTier, name="support_tier", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=SupportTier.NONE,
    )
    status: Mapped[LicenseStatus] = mapped_column(
        Enum(LicenseStatus, name="license_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=LicenseStatus.ACTIVE,
    )

    # ADR-002 — composition role added in migration 0009. Default
    # ``standalone`` preserves existing single-skill download semantics.
    composition_role: Mapped[LicenseCompositionRole] = mapped_column(
        Enum(
            LicenseCompositionRole,
            name="license_composition_role",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=LicenseCompositionRole.STANDALONE,
        server_default=LicenseCompositionRole.STANDALONE.value,
    )
    # Snapshot of the persona's parent occupation at purchase time so a
    # creator changing parents post-sale doesn't invalidate the license.
    # NULL for ``occupation`` and ``standalone`` rows.
    target_occupation_skill_id: Mapped[uuid.UUID | None] = mapped_column(
        _UUID,
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_licenses_buyer_skill_status", "buyer_id", "skill_id", "status"),
        Index("ix_licenses_skill_id", "skill_id"),
        # Primary composer query: "buyer's persona licenses for occupation X".
        Index(
            "ix_licenses_buyer_target_occupation_status",
            "buyer_id",
            "target_occupation_skill_id",
            "status",
        ),
    )


class Payout(Base, TimestampMixin):
    __tablename__ = "payouts"

    id: Mapped[uuid.UUID] = mapped_column(_UUID, primary_key=True, default=uuid7)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        _UUID, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    stripe_transfer_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True, unique=True
    )
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False, default="USD")
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[PayoutStatus] = mapped_column(
        Enum(PayoutStatus, name="payout_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PayoutStatus.PENDING,
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (Index("ix_payouts_creator_id", "creator_id"),)


class WebhookEvent(Base):
    """Persistent log of inbound Stripe webhook events.

    Primary key is Stripe's ``event.id`` so re-deliveries are naturally
    deduped — see ``prompts/marketplace/03-pricing-and-checkout.md``
    "Webhooks" section.
    """

    __tablename__ = "webhook_events"

    # Stripe event ids look like ``evt_1NJ...`` — bounded char count.
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    type: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[WebhookEventStatus] = mapped_column(
        Enum(
            WebhookEventStatus,
            name="webhook_event_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=WebhookEventStatus.RECEIVED,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_webhook_events_type", "type"),
        Index("ix_webhook_events_status", "status"),
    )


__all__ = [
    "License",
    "LicenseCompositionRole",
    "LicenseSource",
    "LicenseStatus",
    "Order",
    "OrderItem",
    "OrderStatus",
    "Payout",
    "PayoutStatus",
    "Subscription",
    "SubscriptionStatus",
    "SupportTier",
    "WebhookEvent",
    "WebhookEventStatus",
]
