"""Centralised rate-limit definitions.

We use ``slowapi`` as the limiter backend; limits are keyed off client IP
(or user id when authenticated). Centralising the strings here lets us audit
limits without grepping routers.

See ``shared/auth.md`` for the canonical starting values.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.config import settings

if TYPE_CHECKING:
    from fastapi import Request
    from starlette.responses import Response

# ── Limit strings (slowapi format) ────────────────────────────────────
LIMIT_LOGIN = "10/minute;50/hour"
LIMIT_FORGOT = "10/minute;50/hour"
LIMIT_REGISTER = "5/hour"
LIMIT_VERIFY_RESEND = "5/hour"
LIMIT_API_TOKENS = "60/minute"
LIMIT_DEFAULT = "120/minute"


def _key_func(request: "Request") -> str:
    """Key by authenticated user when available, else by IP."""
    user = getattr(request.state, "user", None)
    if user is not None:
        return f"user:{user.id}"
    return get_remote_address(request)


# Use Redis when not in test/dev-without-redis; slowapi will fall back to
# in-memory if the URI is empty. For dev/test we still point at Redis from
# settings — tests should set ``REDIS_URL`` to ``memory://`` if no Redis.
def _storage_uri() -> str:
    if settings.is_test:
        return "memory://"
    return settings.REDIS_URL


limiter: Limiter = Limiter(
    key_func=_key_func,
    storage_uri=_storage_uri(),
    default_limits=[LIMIT_DEFAULT],
    headers_enabled=True,
)


# Re-export so routers don't import slowapi directly.
RateLimitExceeded: type[Exception]
rate_limit_exceeded_handler: Callable[..., Awaitable["Response"]]
try:  # pragma: no cover - import side effects
    from slowapi.errors import RateLimitExceeded as _RLE
    from slowapi import _rate_limit_exceeded_handler

    RateLimitExceeded = _RLE
    rate_limit_exceeded_handler = _rate_limit_exceeded_handler  # type: ignore[assignment]
except Exception:  # pragma: no cover
    # Should never happen at runtime; the imports above guard against the
    # case where slowapi internals shift.
    RateLimitExceeded = Exception

    async def rate_limit_exceeded_handler(*args: object, **kwargs: object) -> "Response":  # type: ignore[empty-body]
        raise NotImplementedError


__all__ = [
    "LIMIT_API_TOKENS",
    "LIMIT_DEFAULT",
    "LIMIT_FORGOT",
    "LIMIT_LOGIN",
    "LIMIT_REGISTER",
    "LIMIT_VERIFY_RESEND",
    "RateLimitExceeded",
    "limiter",
    "rate_limit_exceeded_handler",
]
