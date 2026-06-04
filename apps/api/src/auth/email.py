"""Outbound transactional email.

Targets mailhog locally (SMTP on ``settings.SMTP_HOST:SMTP_PORT``). Templates
are inline strings for Phase 0 — Resend/SES wire-up + Jinja templates land
when we ship the marketplace UI in Phase 1.
"""

from __future__ import annotations

import logging
from email.message import EmailMessage

import aiosmtplib

from src.core.config import settings

log = logging.getLogger(__name__)


async def send_email(*, to: str, subject: str, body: str) -> None:
    """Send a plaintext email via SMTP.

    Errors are swallowed and logged: bouncing on email-send during sign-up
    is a worse failure mode than the user not getting the message. The
    audit log records the attempt regardless.
    """
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=False,
        )
    except Exception:  # noqa: BLE001 — see docstring
        log.warning("send_email failed", extra={"to": to, "subject": subject})


def verify_email_template(*, verify_url: str) -> tuple[str, str]:
    subject = "Verify your Skillsgit email"
    body = (
        "Welcome to Skillsgit.\n\n"
        f"Click to verify your email: {verify_url}\n\n"
        "This link expires in 24 hours.\n"
    )
    return subject, body


def password_reset_template(*, reset_url: str) -> tuple[str, str]:
    subject = "Reset your Skillsgit password"
    body = (
        "We received a password reset request.\n\n"
        f"Reset link: {reset_url}\n\n"
        "If you didn't ask for this, ignore this email.\n"
    )
    return subject, body


__all__ = ["password_reset_template", "send_email", "verify_email_template"]
