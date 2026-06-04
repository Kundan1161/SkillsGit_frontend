"""``/v1`` router — license listing + license-gated downloads.

The router exposes two endpoint families:

- ``/v1/me/licenses`` — buyer's library list.
- ``/v1/licenses/{id}`` — license detail + download endpoints.

See ``prompts/marketplace/04-licensing-and-delivery.md``.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.deps import current_active_user
from src.billing.models import License
from src.core.db import AuditLog, get_db
from src.core.errors import error_responses
from src.core.pagination import PageInfo, clamp_limit, decode_cursor, encode_cursor
from src.delivery.schemas import (
    DownloadResponse,
    LicenseList,
    LicenseRead,
    LicenseSkillInfo,
    LicenseVersionInfo,
)
from src.delivery.service import (
    entitled_version,
    get_delivery_service,
    get_license_for_user,
)
from src.skills.models import Skill
from src.users.models import CreatorProfile, User

log = logging.getLogger(__name__)

router = APIRouter(tags=["delivery"])


def _client_ip(request: Request) -> str | None:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return None


async def _summarise_license(
    session: AsyncSession, lic: License
) -> LicenseRead:
    skill = await session.get(Skill, lic.skill_id)
    assert skill is not None, "license refers to a missing skill"
    creator_handle: str | None = None
    creator_display_name: str | None = None
    if skill.creator_id is not None:
        prof = await session.execute(
            select(CreatorProfile).where(CreatorProfile.user_id == skill.creator_id)
        )
        cp = prof.scalar_one_or_none()
        if cp is not None:
            creator_handle = cp.handle
        user = await session.get(User, skill.creator_id)
        if user is not None:
            creator_display_name = user.display_name

    version = await entitled_version(session, lic)
    cv: LicenseVersionInfo | None = None
    if version is not None:
        cv = LicenseVersionInfo(
            id=version.id,
            version=version.version,
            released_at=version.released_at,
            is_yanked=version.is_yanked,
        )

    # Download stats from the audit log.
    stats = await session.execute(
        select(
            func.count(AuditLog.id),
            func.max(AuditLog.created_at),
        ).where(
            AuditLog.action == "license.downloaded",
            AuditLog.target_id == lic.id,
        )
    )
    dl_count, last_dl = stats.one()

    return LicenseRead(
        id=lic.id,
        skill=LicenseSkillInfo(
            id=skill.id,
            name=skill.name,
            slug=skill.slug,
            creator_handle=creator_handle,
            creator_display_name=creator_display_name,
            cover_image_url=skill.cover_image_url,
        ),
        source=lic.source,
        status=lic.status,
        support_tier=lic.support_tier,
        granted_at=lic.granted_at,
        expires_at=lic.expires_at,
        max_version=lic.max_version,
        current_version=cv,
        last_downloaded_at=last_dl,
        download_count=int(dl_count or 0),
    )


# ── List endpoints ─────────────────────────────────────────────────────


@router.get(
    "/v1/me/licenses",
    response_model=LicenseList,
    summary="List my licenses",
    responses=error_responses(401),
)
async def list_my_licenses(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: int | None = Query(default=None, ge=1, le=100),
    cursor: str | None = Query(default=None),
    source: str | None = Query(default=None, description="Filter by license source."),
) -> LicenseList:
    real_limit = clamp_limit(limit)
    stmt = select(License).where(License.buyer_id == user.id).order_by(
        desc(License.granted_at), desc(License.id)
    )
    if source:
        from src.billing.models import LicenseSource as Src

        try:
            stmt = stmt.where(License.source == Src(source))
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "license.bad_filter",
                    "message": f"Unknown license source '{source}'.",
                },
            ) from exc

    if cursor:
        payload = decode_cursor(cursor)
        try:
            last_id = uuid.UUID(str(payload["id"]))
        except (KeyError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "pagination.bad_cursor",
                    "message": "Cursor missing id.",
                },
            ) from exc
        stmt = stmt.where(License.id < last_id)

    res = await session.execute(stmt.limit(real_limit + 1))
    rows = list(res.scalars().all())
    has_more = len(rows) > real_limit
    rows = rows[:real_limit]

    items = [await _summarise_license(session, lic) for lic in rows]
    next_cursor: str | None = None
    if has_more and rows:
        next_cursor = encode_cursor(last_id=str(rows[-1].id))

    return LicenseList(
        items=items,
        page=PageInfo(next_cursor=next_cursor, has_more=has_more, limit=real_limit),
    )


@router.get(
    "/v1/licenses/{license_id}",
    response_model=LicenseRead,
    summary="License detail",
    responses=error_responses(401, 403, 404),
)
async def get_license(
    license_id: uuid.UUID,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> LicenseRead:
    lic = await session.get(License, license_id)
    if lic is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "license.not_found",
                "message": "License not found.",
            },
        )
    if lic.buyer_id != user.id and not user.is_admin:
        # 404 to avoid leaking existence to non-owners (spec convention).
        raise HTTPException(
            status_code=404,
            detail={
                "code": "license.not_found",
                "message": "License not found.",
            },
        )
    return await _summarise_license(session, lic)


# ── Download endpoints ────────────────────────────────────────────────


async def _download(
    *,
    license_id: uuid.UUID,
    user: User,
    session: AsyncSession,
    request: Request,
    explicit_version: str | None,
    raw: bool,
) -> Any:
    lic = await get_license_for_user(session, license_id, user.id)
    if lic is None and not user.is_admin:
        raise HTTPException(
            status_code=404,
            detail={"code": "license.not_found", "message": "License not found."},
        )
    if lic is None:
        lic = await session.get(License, license_id)
        if lic is None:
            raise HTTPException(
                status_code=404,
                detail={"code": "license.not_found", "message": "License not found."},
            )

    svc = get_delivery_service()
    result = await svc.prepare_download(
        session,
        license_obj=lic,
        explicit_version=explicit_version,
        user_agent=request.headers.get("user-agent"),
        client_ip=_client_ip(request),
    )
    if result is None:
        await session.commit()
        raise HTTPException(
            status_code=409,
            detail={
                "code": "license.not_entitled",
                "message": (
                    "No released version is currently available for this "
                    "license — it may be revoked, expired, or the skill yanked."
                ),
            },
        )

    await session.commit()

    if raw:
        return PlainTextResponse(
            content=result.body_bytes.decode("utf-8"),
            media_type="text/markdown; charset=utf-8",
            headers={
                "X-Skill-Version": result.version,
                "X-Content-Hash": result.content_hash,
            },
        )

    return DownloadResponse(
        download_url=result.download_url,
        version=result.version,
        expires_at=result.expires_at,
        content_hash=result.content_hash,
    )


@router.get(
    "/v1/licenses/{license_id}/download",
    summary="Download (signed URL or raw body)",
    response_model=DownloadResponse,
    responses=error_responses(401, 403, 404, 409),
)
async def download_license(
    license_id: uuid.UUID,
    request: Request,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    format: str | None = Query(default=None, description="Use 'raw' to stream."),
) -> Any:
    return await _download(
        license_id=license_id,
        user=user,
        session=session,
        request=request,
        explicit_version=None,
        raw=format == "raw",
    )


@router.get(
    "/v1/licenses/{license_id}/download/{version}",
    summary="Download a specific entitled version",
    response_model=DownloadResponse,
    responses=error_responses(401, 403, 404, 409),
)
async def download_license_version(
    license_id: uuid.UUID,
    version: str,
    request: Request,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    format: str | None = Query(default=None),
) -> Any:
    return await _download(
        license_id=license_id,
        user=user,
        session=session,
        request=request,
        explicit_version=version,
        raw=format == "raw",
    )


__all__ = ["router"]


# Silence unused symbols flagged by ruff on imports we keep for type narrowing.
_ = (Header, Response, datetime, status)
