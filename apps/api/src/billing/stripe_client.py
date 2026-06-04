"""Thin wrapper around the ``stripe`` SDK.

Why this module exists:
1. Centralizes API-key configuration (we read once from settings).
2. Lets tests inject a fake Stripe client via :func:`set_stripe_client`
   without monkey-patching the global ``stripe`` module everywhere.
3. Lets us add per-call logging / retries / timeouts in one place
   without leaking those concerns into the service layer.

Never log full request/response bodies — they can contain PII and PCI
data (PaymentIntent objects include card details). Log ids only.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

import stripe as _stripe

from src.core.config import settings

log = logging.getLogger(__name__)


class StripeClient(Protocol):
    """Minimal Stripe surface used by the billing module.

    Real implementation: a thin facade over the ``stripe`` module.
    Test implementation: see ``tests/test_checkout_flow.py`` for a fake.
    """

    # ── Checkout ─────────────────────────────────────────────────────
    def create_checkout_session(self, **params: Any) -> Any: ...

    def retrieve_checkout_session(self, session_id: str) -> Any: ...

    # ── PaymentIntents / refunds ─────────────────────────────────────
    def create_refund(self, **params: Any) -> Any: ...

    # ── Connect onboarding ───────────────────────────────────────────
    def create_account(self, **params: Any) -> Any: ...

    def create_account_link(self, **params: Any) -> Any: ...

    def retrieve_account(self, account_id: str) -> Any: ...

    # ── Customer portal (Phase 1 read-only billing UI) ───────────────
    def create_billing_portal_session(self, **params: Any) -> Any: ...

    # ── Webhook signature verification ───────────────────────────────
    def construct_webhook_event(
        self, payload: bytes, sig_header: str, secret: str
    ) -> Any: ...


class _LiveStripeClient:
    """Default impl that delegates to the real ``stripe`` SDK."""

    def __init__(self, api_key: str) -> None:
        # The Stripe SDK uses a module-level ``api_key``; setting it here
        # is enough for all subsequent calls in this process. We avoid
        # logging the key (it's a SecretStr value the caller already
        # unwrapped).
        _stripe.api_key = api_key

    def create_checkout_session(self, **params: Any) -> Any:
        return _stripe.checkout.Session.create(**params)

    def retrieve_checkout_session(self, session_id: str) -> Any:
        return _stripe.checkout.Session.retrieve(session_id)

    def create_refund(self, **params: Any) -> Any:
        return _stripe.Refund.create(**params)

    def create_account(self, **params: Any) -> Any:
        return _stripe.Account.create(**params)

    def create_account_link(self, **params: Any) -> Any:
        return _stripe.AccountLink.create(**params)

    def retrieve_account(self, account_id: str) -> Any:
        return _stripe.Account.retrieve(account_id)

    def create_billing_portal_session(self, **params: Any) -> Any:
        return _stripe.billing_portal.Session.create(**params)

    def construct_webhook_event(
        self, payload: bytes, sig_header: str, secret: str
    ) -> Any:
        # Raises stripe.error.SignatureVerificationError on bad sig.
        return _stripe.Webhook.construct_event(payload, sig_header, secret)


# ── Module-level singleton (overridable for tests) ────────────────────
_client: StripeClient | None = None


def get_stripe_client() -> StripeClient:
    """Return the active Stripe client (constructing the default lazily)."""
    global _client
    if _client is None:
        _client = _LiveStripeClient(
            api_key=settings.STRIPE_SECRET_KEY.get_secret_value()
        )
    return _client


def set_stripe_client(client: StripeClient | None) -> None:
    """Inject a fake Stripe client (or reset to default with ``None``)."""
    global _client
    _client = client


# Re-export the SDK's exception classes so callers can catch them by
# name without importing ``stripe`` directly. Keeps the abstraction
# leaky in only one well-defined direction.
StripeError = _stripe.error.StripeError
SignatureVerificationError = _stripe.error.SignatureVerificationError
InvalidRequestError = _stripe.error.InvalidRequestError


__all__ = [
    "InvalidRequestError",
    "SignatureVerificationError",
    "StripeClient",
    "StripeError",
    "get_stripe_client",
    "set_stripe_client",
]
