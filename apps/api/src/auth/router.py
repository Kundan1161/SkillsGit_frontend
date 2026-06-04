"""``/v1/auth`` router.

All endpoints from ``shared/auth.md``. OAuth start/callback are scaffolded
— they return 501 unless OAuth credentials are configured. Real OAuth
wiring (``fastapi-users[oauth]``) lands in Phase 1.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.deps import (
    SESSION_COOKIE_NAME,
    current_active_user,
    get_redis,
)
from src.auth.email import (
    password_reset_template,
    send_email,
    verify_email_template,
)
from src.auth.schemas import (
    ForgotRequest,
    LoginRequest,
    LoginResponse,
    ResetRequest,
    VerifyResendRequest,
)
from src.auth.service import (
    authenticate,
    create_user,
    get_user_by_email,
    issue_api_token,
    list_api_tokens,
    make_password_reset_token,
    make_verification_token,
    mark_email_verified,
    reset_password,
    revoke_api_token,
)
from src.auth.tokens import (
    DEFAULT_LIFETIME,
    decode_token,
    is_locked_out,
    make_session_token,
    record_failed_login,
    reset_failed_login,
    revoke_jti,
)
from src.core.config import settings
from src.core.db import get_db, write_audit
from src.core.errors import AppError, error_responses
from src.core.rate_limits import (
    LIMIT_API_TOKENS,
    LIMIT_FORGOT,
    LIMIT_LOGIN,
    LIMIT_REGISTER,
    LIMIT_VERIFY_RESEND,
    limiter,
)
from src.users.models import User
from src.users.schemas import (
    ApiTokenCreate,
    ApiTokenCreated,
    ApiTokenRead,
    BecomeCreatorRequest,
    CreatorProfileRead,
    UserCreate,
    UserRead,
    UserUpdate,
)
from src.users.service import create_creator_profile

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/auth", tags=["auth"])


# ── Helpers ───────────────────────────────────────────────────────────
def _set_session_cookie(response: Response, token: str, max_age_seconds: int) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=max_age_seconds,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


# ── Register / Login / Logout ─────────────────────────────────────────
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead,
    summary="Register a new user",
    responses=error_responses(409, 422, 429),
)
@limiter.limit(LIMIT_REGISTER)
async def register(
    request: Request,
    payload: UserCreate,
    response: Response,
    session: AsyncSession = Depends(get_db),
) -> UserRead:
    user = await create_user(
        session,
        email=str(payload.email),
        password=payload.password,
        display_name=payload.display_name,
    )

    # Send verification email (best-effort).
    token = await make_verification_token(user)
    subject, body = verify_email_template(
        verify_url=f"https://app.skillsgit.local/verify?token={token}"
    )
    await send_email(to=user.email, subject=subject, body=body)

    # Auto-login on register.
    jwt_token, jti, expires_at = make_session_token(
        user_id=user.id, email_verified=user.is_verified, is_admin=user.is_admin
    )
    _set_session_cookie(response, jwt_token, int(DEFAULT_LIFETIME.total_seconds()))

    await session.commit()
    response.headers["Location"] = f"/v1/users/{user.id}"
    return UserRead.model_validate(user)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Sign in (sets session cookie)",
    responses=error_responses(401, 423, 429),
)
@limiter.limit(LIMIT_LOGIN)
async def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_db),
) -> LoginResponse:
    redis = get_redis()

    # Lockout check.
    try:
        if await is_locked_out(redis, str(payload.email)):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail={
                    "code": "auth.account_locked",
                    "message": (
                        "Too many failed attempts. Try again in a few minutes."
                    ),
                },
            )
    except HTTPException:
        raise
    except Exception:
        # Redis unavailable — fail open on the lockout check; login itself
        # still requires a valid password.
        log.warning("redis lockout check failed; proceeding without it")

    user = await authenticate(
        session, email=str(payload.email), password=payload.password
    )
    if user is None:
        try:
            await record_failed_login(redis, str(payload.email))
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "auth.invalid_credentials",
                "message": "Email or password is incorrect.",
            },
        )

    try:
        await reset_failed_login(redis, str(payload.email))
    except Exception:
        pass

    jwt_token, jti, _expires = make_session_token(
        user_id=user.id, email_verified=user.is_verified, is_admin=user.is_admin
    )
    _set_session_cookie(response, jwt_token, int(DEFAULT_LIFETIME.total_seconds()))

    await write_audit(
        session,
        actor_id=user.id,
        action="auth.login",
        target_type="user",
        target_id=user.id,
    )
    await session.commit()
    return LoginResponse(ok=True)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sign out",
)
async def logout(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
) -> Response:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    user_id: uuid.UUID | None = None
    if token:
        try:
            payload = decode_token(token)
            jti = payload.get("jti")
            sub = payload.get("sub")
            exp = int(payload.get("exp", 0))
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = max(1, exp - now)
            if jti:
                try:
                    await revoke_jti(get_redis(), jti, ttl_seconds=ttl)
                except Exception:
                    log.warning("failed to add jti to denylist; continuing")
            if sub:
                try:
                    user_id = uuid.UUID(sub)
                except (TypeError, ValueError):
                    user_id = None
        except jwt.PyJWTError:
            pass

    _clear_session_cookie(response)
    if user_id is not None:
        await write_audit(
            session,
            actor_id=user_id,
            action="auth.logout",
            target_type="user",
            target_id=user_id,
        )
        await session.commit()
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


# ── /me ───────────────────────────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current user",
    responses=error_responses(401),
)
async def get_me(user: User = Depends(current_active_user)) -> UserRead:
    return UserRead.model_validate(user)


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Update profile fields",
    responses=error_responses(401, 422),
)
async def patch_me(
    payload: UserUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
) -> UserRead:
    if payload.display_name is not None:
        user.display_name = payload.display_name
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


# ── Forgot / reset ────────────────────────────────────────────────────
@router.post(
    "/forgot",
    status_code=status.HTTP_200_OK,
    summary="Request a password reset",
    responses=error_responses(429),
)
@limiter.limit(LIMIT_FORGOT)
async def forgot(
    request: Request,
    payload: ForgotRequest,
    session: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    # Always return 200 — never leak whether the email exists.
    user = await get_user_by_email(session, str(payload.email))
    if user is not None:
        token = await make_password_reset_token(user)
        subject, body = password_reset_template(
            reset_url=f"https://app.skillsgit.local/reset?token={token}"
        )
        await send_email(to=user.email, subject=subject, body=body)
        await write_audit(
            session,
            actor_id=user.id,
            action="auth.password_reset_requested",
            target_type="user",
            target_id=user.id,
        )
        await session.commit()
    return {"ok": True}


@router.post(
    "/reset",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reset password using a token",
    responses=error_responses(400, 422),
)
async def reset(
    payload: ResetRequest,
    session: AsyncSession = Depends(get_db),
) -> Response:
    try:
        data = decode_token(payload.token)
    except jwt.PyJWTError as exc:
        raise AppError(
            code="auth.invalid_reset_token",
            message="Reset token is invalid or expired.",
            status_code=400,
        ) from exc
    if data.get("purpose") != "password_reset":
        raise AppError(
            code="auth.invalid_reset_token",
            message="Token is not a password reset token.",
            status_code=400,
        )
    try:
        user_id = uuid.UUID(data["sub"])
    except (KeyError, ValueError) as exc:
        raise AppError(
            code="auth.invalid_reset_token",
            message="Token payload is malformed.",
            status_code=400,
        ) from exc
    from sqlalchemy import select

    res = await session.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if user is None:
        raise AppError(
            code="auth.invalid_reset_token",
            message="Reset token refers to an unknown user.",
            status_code=400,
        )
    await reset_password(session, user, payload.new_password)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Verify ────────────────────────────────────────────────────────────
@router.get(
    "/verify",
    summary="Verify email via signed link",
    responses=error_responses(400),
)
async def verify(
    token: str,
    session: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    try:
        data = decode_token(token)
    except jwt.PyJWTError as exc:
        raise AppError(
            code="auth.invalid_verify_token",
            message="Verification token is invalid or expired.",
            status_code=400,
        ) from exc
    if data.get("purpose") != "verify_email":
        raise AppError(
            code="auth.invalid_verify_token",
            message="Token is not a verification token.",
            status_code=400,
        )
    try:
        user_id = uuid.UUID(data["sub"])
    except (KeyError, ValueError) as exc:
        raise AppError(
            code="auth.invalid_verify_token",
            message="Token payload is malformed.",
            status_code=400,
        ) from exc
    from sqlalchemy import select

    res = await session.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if user is None:
        raise AppError(
            code="auth.invalid_verify_token",
            message="Verification token refers to an unknown user.",
            status_code=400,
        )
    if not user.is_verified:
        await mark_email_verified(session, user)
        await session.commit()
    return {"ok": True}


@router.post(
    "/verify/resend",
    status_code=status.HTTP_200_OK,
    summary="Resend the verification email",
    responses=error_responses(429),
)
@limiter.limit(LIMIT_VERIFY_RESEND)
async def verify_resend(
    request: Request,
    payload: VerifyResendRequest,
    session: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    user = await get_user_by_email(session, str(payload.email))
    if user is not None and not user.is_verified:
        token = await make_verification_token(user)
        subject, body = verify_email_template(
            verify_url=f"https://app.skillsgit.local/verify?token={token}"
        )
        await send_email(to=user.email, subject=subject, body=body)
    return {"ok": True}


# ── Become creator ────────────────────────────────────────────────────
@router.post(
    "/become-creator",
    status_code=status.HTTP_201_CREATED,
    response_model=CreatorProfileRead,
    summary="Create a creator profile",
    responses=error_responses(401, 409, 422),
)
async def become_creator(
    payload: BecomeCreatorRequest,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
) -> CreatorProfileRead:
    profile = await create_creator_profile(
        session,
        user=user,
        handle=payload.handle,
        payout_country=payload.payout_country,
    )
    await write_audit(
        session,
        actor_id=user.id,
        action="auth.become_creator",
        target_type="creator_profile",
        target_id=profile.id,
        metadata={"handle": payload.handle},
    )
    await session.commit()
    await session.refresh(profile)
    # TODO Phase 1: kick off Stripe Connect onboarding here.
    # See prompts/marketplace/03-pricing-and-checkout.md
    return CreatorProfileRead.model_validate(profile)


# ── API tokens ────────────────────────────────────────────────────────
@router.get(
    "/tokens",
    response_model=list[ApiTokenRead],
    summary="List API tokens",
    responses=error_responses(401),
)
@limiter.limit(LIMIT_API_TOKENS)
async def list_tokens(
    request: Request,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
) -> list[ApiTokenRead]:
    rows = await list_api_tokens(session, user=user)
    return [ApiTokenRead.model_validate(r) for r in rows]


@router.post(
    "/tokens",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiTokenCreated,
    summary="Issue an API token (returns plaintext ONCE)",
    responses=error_responses(401, 422),
)
@limiter.limit(LIMIT_API_TOKENS)
async def create_token(
    request: Request,
    payload: ApiTokenCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ApiTokenCreated:
    row, plaintext = await issue_api_token(
        session,
        user=user,
        name=payload.name,
        scopes=payload.scopes,
        expires_at=payload.expires_at,
        env=settings.ENV,
    )
    await session.commit()
    await session.refresh(row)
    data: dict[str, Any] = ApiTokenRead.model_validate(row).model_dump()
    data["token"] = plaintext
    return ApiTokenCreated.model_validate(data)


@router.delete(
    "/tokens/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke an API token",
    responses=error_responses(401, 404),
)
@limiter.limit(LIMIT_API_TOKENS)
async def delete_token(
    request: Request,
    token_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    await revoke_api_token(session, user=user, token_id=token_id)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── OAuth scaffold ────────────────────────────────────────────────────
@router.get(
    "/oauth/{provider}/start",
    summary="Begin OAuth flow (Phase 1)",
    responses=error_responses(501),
)
async def oauth_start(provider: str) -> dict[str, str]:
    # TODO Phase 1: wire fastapi-users[oauth] for google + github.
    if provider == "google" and not settings.GOOGLE_OAUTH_CLIENT_ID:
        raise HTTPException(
            status_code=501,
            detail={
                "code": "auth.oauth_not_configured",
                "message": "Google OAuth credentials are not configured.",
            },
        )
    if provider == "github" and not settings.GITHUB_OAUTH_CLIENT_ID:
        raise HTTPException(
            status_code=501,
            detail={
                "code": "auth.oauth_not_configured",
                "message": "GitHub OAuth credentials are not configured.",
            },
        )
    raise HTTPException(
        status_code=501,
        detail={
            "code": "auth.oauth_not_implemented",
            "message": f"OAuth provider '{provider}' is scaffolded but not wired in Phase 0.",
        },
    )


@router.get(
    "/oauth/{provider}/callback",
    summary="OAuth callback (Phase 1)",
    responses=error_responses(501),
)
async def oauth_callback(provider: str) -> dict[str, str]:
    raise HTTPException(
        status_code=501,
        detail={
            "code": "auth.oauth_not_implemented",
            "message": f"OAuth callback for '{provider}' not implemented in Phase 0.",
        },
    )
