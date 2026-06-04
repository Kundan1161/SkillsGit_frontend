"""``/v1/webhooks/stripe`` — inbound Stripe webhook endpoint.

This router is intentionally thin: parse → verify signature → persist →
dispatch. All business logic lives in :mod:`src.webhooks.service`.

Spec: ``prompts/marketplace/03-pricing-and-checkout.md`` "Webhooks".
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.stripe_client import (
    SignatureVerificationError,
    get_stripe_client,
)
from src.core.config import settings
from src.core.db import get_db
from src.core.errors import AppError, error_responses
from src.webhooks import service as webhook_service

log = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post(
    "/stripe",
    status_code=status.HTTP_200_OK,
    summary="Inbound Stripe webhook receiver",
    responses=error_responses(400, 401),
)
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    session: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """Receive a Stripe webhook event.

    - Verifies the ``Stripe-Signature`` header against
      ``STRIPE_WEBHOOK_SECRET`` (or skips verification when running
      under ``ENV=test`` so unit tests can post raw JSON).
    - Persists every event in ``webhook_events`` keyed on Stripe's
      ``event.id``; re-deliveries are a no-op.
    - Dispatches to :func:`src.webhooks.service.process_event`.

    Always returns 200 once the event is persisted, even if a handler
    encountered a recoverable error — Stripe's retry policy will replay
    based on 5xx, not on handler-level errors.
    """
    payload = await request.body()

    # Parse the event. In tests we accept raw JSON; in prod we always
    # verify the signature first via the Stripe SDK.
    event: dict[str, object]
    if settings.is_test:
        try:
            event = json.loads(payload.decode() or "{}")
        except json.JSONDecodeError as exc:
            raise AppError(
                code="webhooks.invalid_payload",
                message="Webhook payload was not valid JSON.",
                status_code=400,
            ) from exc
    else:
        if not stripe_signature:
            raise AppError(
                code="webhooks.missing_signature",
                message="Stripe-Signature header is required.",
                status_code=400,
            )
        try:
            verified = get_stripe_client().construct_webhook_event(
                payload,
                stripe_signature,
                settings.STRIPE_WEBHOOK_SECRET.get_secret_value(),
            )
        except SignatureVerificationError as exc:
            # Don't log the signature or the raw payload — both are sensitive.
            log.warning("stripe webhook signature verification failed")
            raise AppError(
                code="webhooks.invalid_signature",
                message="Webhook signature could not be verified.",
                status_code=401,
            ) from exc
        except Exception as exc:  # noqa: BLE001
            log.warning("stripe webhook parse failed: %s", type(exc).__name__)
            raise AppError(
                code="webhooks.invalid_payload",
                message="Webhook payload was malformed.",
                status_code=400,
            ) from exc
        # Stripe events are dict-like; coerce to native dict for the handler.
        event = json.loads(json.dumps(verified, default=str)) if not isinstance(verified, dict) else verified

    if not event or "id" not in event:
        raise AppError(
            code="webhooks.invalid_payload",
            message="Event payload is missing 'id'.",
            status_code=400,
        )

    try:
        result = await webhook_service.process_event(session, event)
        await session.commit()
    except Exception as exc:  # noqa: BLE001
        # The service already persisted a ``webhook_events`` row with
        # status=failed before re-raising. Roll back any in-progress
        # business-side writes, then commit just the failure log.
        await session.rollback()
        try:
            await _persist_failure(session, event, exc)
            await session.commit()
        except Exception:  # pragma: no cover
            log.exception("could not persist webhook failure row")
        log.exception("webhook handler raised")
        raise AppError(
            code="webhooks.handler_error",
            message="Webhook handler failed; will be retried.",
            status_code=500,
        ) from exc
    return result


async def _persist_failure(
    session: AsyncSession, event: dict[str, object], exc: Exception
) -> None:
    """Persist a ``webhook_events`` row marking the failure.

    Called after the main session was rolled back, so this commit only
    writes the audit row. Uses INSERT-or-UPDATE semantics: if the row
    already exists (e.g. from a prior partial success), updates the
    status only.
    """
    from datetime import datetime, timezone

    from src.billing.models import WebhookEvent, WebhookEventStatus

    event_id = str(event.get("id", ""))
    if not event_id:
        return
    existing = await session.get(WebhookEvent, event_id)
    if existing is None:
        row = WebhookEvent(
            id=event_id,
            type=str(event.get("type", "unknown")),
            payload_json=event,  # type: ignore[arg-type]
            received_at=datetime.now(timezone.utc),
            status=WebhookEventStatus.FAILED,
            error=type(exc).__name__,
        )
        session.add(row)
    else:
        existing.status = WebhookEventStatus.FAILED
        existing.error = type(exc).__name__
        session.add(existing)
