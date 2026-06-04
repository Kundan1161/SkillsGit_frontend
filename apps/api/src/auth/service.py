"""Auth service: password hashing, user creation, login, email/reset flows,
API token issuance.

This layer is the only place that touches argon2/passlib. Routers stay thin.
"""

from __future__ import annotations

import logging
import secrets
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from passlib.context import CryptContext
from sqlalchemy import select

from src.auth.tokens import make_purpose_token
from src.core.db import write_audit
from src.core.errors import AppError
from src.users.models import ApiToken, User, UserRole

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)

# Argon2id tuned per shared/auth.md: mem=64MB, iterations=3, parallelism=4.
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MiB
    argon2__time_cost=3,
    argon2__parallelism=4,
)

# Token plaintext prefix (production tokens use _live_, test tokens _test_).
TOKEN_PREFIX_LIVE = "skg_live_"
TOKEN_PREFIX_TEST = "skg_test_"

# A pre-computed argon2id hash of a dummy password, used by ``authenticate``
# to keep timing constant when the email doesn't exist. Generated at import
# time once; the value itself is not a real password.
_DUMMY_HASH: str = pwd_context.hash("dummy-password-for-timing-defense")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # type: ignore[no-any-return]


def verify_password(password: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(password, hashed)  # type: ignore[no-any-return]
    except Exception:
        return False


# ── Password strength (lightweight; zxcvbn would land in Phase 1) ────
def password_is_strong_enough(password: str) -> tuple[bool, str | None]:
    if len(password) < 12:
        return False, "Password must be at least 12 characters."
    # Reject the most-obvious bad ones; a real zxcvbn check is Phase 1.
    too_easy = {"password", "passwordpassword", "qwertyqwerty", "letmeinletmein"}
    if password.lower() in too_easy:
        return False, "Password is too common."
    return True, None


# ── User CRUD ─────────────────────────────────────────────────────────


async def get_user_by_email(session: "AsyncSession", email: str) -> User | None:
    res = await session.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()


async def create_user(
    session: "AsyncSession",
    *,
    email: str,
    password: str,
    display_name: str | None = None,
) -> User:
    ok, reason = password_is_strong_enough(password)
    if not ok:
        raise AppError(
            code="auth.weak_password",
            message=reason or "Password is too weak.",
            status_code=422,
        )

    existing = await get_user_by_email(session, email)
    if existing is not None:
        raise AppError(
            code="auth.email_taken",
            message="An account with that email already exists.",
            status_code=409,
        )

    user = User(
        email=email,
        hashed_password=hash_password(password),
        display_name=display_name,
        role=UserRole.BUYER,
        is_active=True,
        is_verified=False,
        is_admin=False,
    )
    session.add(user)
    await session.flush()  # populates user.id
    await write_audit(
        session,
        actor_id=user.id,
        action="auth.register",
        target_type="user",
        target_id=user.id,
    )
    return user


async def authenticate(
    session: "AsyncSession", *, email: str, password: str
) -> User | None:
    user = await get_user_by_email(session, email)
    if user is None or not user.is_active or user.hashed_password is None:
        # Run a verify anyway against a known-bad hash to avoid timing oracles.
        # The cost is dominated by argon2 work, identical to the real path.
        try:
            pwd_context.verify(password, _DUMMY_HASH)
        except Exception:
            pass
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ── Email verification / password reset ──────────────────────────────


async def make_verification_token(user: User) -> str:
    return make_purpose_token(user_id=user.id, purpose="verify_email")


async def make_password_reset_token(user: User) -> str:
    return make_purpose_token(user_id=user.id, purpose="password_reset")


async def mark_email_verified(
    session: "AsyncSession", user: User
) -> None:
    user.is_verified = True
    await write_audit(
        session,
        actor_id=user.id,
        action="auth.email_verified",
        target_type="user",
        target_id=user.id,
    )


async def reset_password(
    session: "AsyncSession", user: User, new_password: str
) -> None:
    ok, reason = password_is_strong_enough(new_password)
    if not ok:
        raise AppError(
            code="auth.weak_password",
            message=reason or "Password is too weak.",
            status_code=422,
        )
    user.hashed_password = hash_password(new_password)
    await write_audit(
        session,
        actor_id=user.id,
        action="auth.password_reset",
        target_type="user",
        target_id=user.id,
    )


# ── API tokens ────────────────────────────────────────────────────────


def _generate_plaintext_token(env: str) -> str:
    prefix = TOKEN_PREFIX_LIVE if env == "prod" else TOKEN_PREFIX_TEST
    return prefix + secrets.token_urlsafe(32)


async def issue_api_token(
    session: "AsyncSession",
    *,
    user: User,
    name: str,
    scopes: list[str],
    expires_at: datetime | None,
    env: str,
) -> tuple[ApiToken, str]:
    """Create an API token row, return ``(row, plaintext_token)``.

    The plaintext is only returned here — never stored.
    """
    plaintext = _generate_plaintext_token(env)
    row = ApiToken(
        user_id=user.id,
        name=name,
        token_hash=hash_password(plaintext),
        prefix=plaintext[:12],  # e.g. "skg_live_AB"
        scopes=scopes or [],
        expires_at=expires_at,
    )
    session.add(row)
    await session.flush()
    await write_audit(
        session,
        actor_id=user.id,
        action="auth.token_issued",
        target_type="api_token",
        target_id=row.id,
        metadata={"name": name, "scopes": scopes},
    )
    return row, plaintext


async def revoke_api_token(
    session: "AsyncSession",
    *,
    user: User,
    token_id: uuid.UUID,
) -> None:
    res = await session.execute(
        select(ApiToken).where(ApiToken.id == token_id, ApiToken.user_id == user.id)
    )
    row = res.scalar_one_or_none()
    if row is None:
        raise AppError(
            code="auth.token_not_found",
            message="API token not found.",
            status_code=404,
        )
    row.revoked_at = datetime.now(timezone.utc)
    await write_audit(
        session,
        actor_id=user.id,
        action="auth.token_revoked",
        target_type="api_token",
        target_id=row.id,
    )


async def list_api_tokens(
    session: "AsyncSession", *, user: User
) -> list[ApiToken]:
    res = await session.execute(
        select(ApiToken).where(ApiToken.user_id == user.id).order_by(ApiToken.created_at.desc())
    )
    return list(res.scalars().all())


__all__ = [
    "authenticate",
    "create_user",
    "get_user_by_email",
    "hash_password",
    "issue_api_token",
    "list_api_tokens",
    "make_password_reset_token",
    "make_verification_token",
    "mark_email_verified",
    "password_is_strong_enough",
    "reset_password",
    "revoke_api_token",
    "verify_password",
]
