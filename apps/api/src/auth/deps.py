"""FastAPI dependencies for resolving the current user.

Order of precedence:
1. ``Authorization: Bearer skg_…`` API token header.
2. ``session`` httpOnly cookie carrying a JWT.

If neither is present the dependency raises 401.
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select

from src.auth.service import pwd_context
from src.auth.tokens import decode_token, is_revoked
from src.core.config import settings
from src.core.db import get_db
from src.users.models import ApiToken, User, UserRole

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)

SESSION_COOKIE_NAME = "skillsgit_session"


# Redis is a module-level singleton because we only ever need one connection
# pool per process. Tests can monkey-patch this.
_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def _user_from_jwt(session: "AsyncSession", token: str, redis: Redis) -> User | None:
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        return None
    if payload.get("purpose") != "session":
        return None
    jti = payload.get("jti")
    if jti and await is_revoked(redis, jti):
        return None
    sub = payload.get("sub")
    if not sub:
        return None
    try:
        user_id = uuid.UUID(sub)
    except (TypeError, ValueError):
        return None
    res = await session.execute(select(User).where(User.id == user_id))
    return res.scalar_one_or_none()


async def _user_from_api_token(
    session: "AsyncSession", plaintext: str
) -> User | None:
    prefix = plaintext[:12]
    res = await session.execute(
        select(ApiToken).where(ApiToken.prefix == prefix, ApiToken.revoked_at.is_(None))
    )
    candidate = res.scalar_one_or_none()
    if candidate is None:
        return None
    try:
        if not pwd_context.verify(plaintext, candidate.token_hash):
            return None
    except Exception:
        return None
    res2 = await session.execute(select(User).where(User.id == candidate.user_id))
    return res2.scalar_one_or_none()


async def get_optional_user(
    session: "AsyncSession" = Depends(get_db),
    session_cookie: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    authorization: str | None = Header(default=None),
) -> User | None:
    """Returns the current user or ``None``. Use when auth is optional."""
    redis = get_redis()

    # API token wins so server-to-server scripts can pass through even if a
    # stale cookie is hanging around.
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        if token.startswith(("skg_live_", "skg_test_")):
            user = await _user_from_api_token(session, token)
            if user is not None:
                return user
        else:
            # Bearer JWT (used by some clients that don't manage cookies).
            user = await _user_from_jwt(session, token, redis)
            if user is not None:
                return user

    if session_cookie:
        user = await _user_from_jwt(session, session_cookie, redis)
        if user is not None:
            return user

    return None


async def current_user(
    user: User | None = Depends(get_optional_user),
) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "auth.unauthorized", "message": "Not authenticated."},
        )
    return user


async def current_active_user(
    user: User = Depends(current_user),
) -> User:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "auth.inactive", "message": "Account is inactive."},
        )
    return user


async def require_verified(
    user: User = Depends(current_active_user),
) -> User:
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "auth.email_unverified",
                "message": "Verify your email to perform this action.",
            },
        )
    return user


async def require_admin(
    user: User = Depends(current_active_user),
) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "auth.forbidden", "message": "Admin only."},
        )
    return user


async def require_creator(
    user: User = Depends(current_active_user),
) -> User:
    if user.role not in (UserRole.CREATOR, UserRole.ADMIN) and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "auth.not_a_creator",
                "message": "Creator profile required.",
            },
        )
    return user


__all__ = [
    "SESSION_COOKIE_NAME",
    "current_active_user",
    "current_user",
    "get_optional_user",
    "get_redis",
    "require_admin",
    "require_creator",
    "require_verified",
]
