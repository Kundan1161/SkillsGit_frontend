"""JWT session tokens + Redis-backed jti denylist + email-purpose tokens.

We don't depend on ``fastapi-users``' JWT strategy at this layer — that
makes testing and middleware composition simpler. The format below matches
``shared/auth.md`` exactly so swapping in fastapi-users later is mechanical.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import jwt
from redis.asyncio import Redis

from src.core.config import settings

ALGORITHM = "HS256"
DEFAULT_LIFETIME = timedelta(days=7)
MAX_LIFETIME = timedelta(days=30)

TokenPurpose = Literal["session", "verify_email", "password_reset"]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _secret() -> str:
    return settings.JWT_SECRET.get_secret_value()


def make_session_token(
    *,
    user_id: uuid.UUID,
    email_verified: bool,
    is_admin: bool,
    lifetime: timedelta = DEFAULT_LIFETIME,
) -> tuple[str, str, datetime]:
    """Issue a fresh session JWT. Returns ``(token, jti, expires_at)``."""
    jti = uuid.uuid4().hex
    expires_at = _now() + lifetime
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email_verified": email_verified,
        "is_admin": is_admin,
        "iat": int(_now().timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": jti,
        "purpose": "session",
    }
    token = jwt.encode(payload, _secret(), algorithm=ALGORITHM)
    return token, jti, expires_at


def make_purpose_token(
    *,
    user_id: uuid.UUID,
    purpose: TokenPurpose,
    lifetime: timedelta = timedelta(hours=24),
) -> str:
    """Issue a single-purpose token (email verify, password reset)."""
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "iat": int(_now().timestamp()),
        "exp": int((_now() + lifetime).timestamp()),
        "purpose": purpose,
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode + verify signature/expiry. Raises ``jwt.PyJWTError`` on failure."""
    return jwt.decode(  # type: ignore[no-any-return]
        token,
        _secret(),
        algorithms=[ALGORITHM],
        options={"require": ["exp", "sub", "purpose"]},
    )


# ── Redis denylist (jti) ──────────────────────────────────────────────
_DENYLIST_PREFIX = "auth:deny:"


async def revoke_jti(redis: Redis, jti: str, *, ttl_seconds: int) -> None:
    await redis.setex(_DENYLIST_PREFIX + jti, max(1, ttl_seconds), "1")


async def is_revoked(redis: Redis, jti: str) -> bool:
    return await redis.exists(_DENYLIST_PREFIX + jti) > 0


# ── Failed-login throttle (per-account) ───────────────────────────────
_FAIL_PREFIX = "auth:fail:"
LOCKOUT_THRESHOLD = 10
LOCKOUT_WINDOW_SECS = 600  # 10 minutes


async def record_failed_login(redis: Redis, email: str) -> int:
    key = _FAIL_PREFIX + email.lower()
    n = await redis.incr(key)
    if n == 1:
        await redis.expire(key, LOCKOUT_WINDOW_SECS)
    return int(n)


async def reset_failed_login(redis: Redis, email: str) -> None:
    await redis.delete(_FAIL_PREFIX + email.lower())


async def is_locked_out(redis: Redis, email: str) -> bool:
    n = await redis.get(_FAIL_PREFIX + email.lower())
    if n is None:
        return False
    try:
        return int(n) >= LOCKOUT_THRESHOLD
    except (TypeError, ValueError):
        return False


__all__ = [
    "ALGORITHM",
    "DEFAULT_LIFETIME",
    "LOCKOUT_THRESHOLD",
    "LOCKOUT_WINDOW_SECS",
    "MAX_LIFETIME",
    "TokenPurpose",
    "decode_token",
    "is_locked_out",
    "is_revoked",
    "make_purpose_token",
    "make_session_token",
    "record_failed_login",
    "reset_failed_login",
    "revoke_jti",
]
