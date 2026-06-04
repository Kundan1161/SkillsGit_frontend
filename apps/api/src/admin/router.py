"""``/v1/admin`` router — moderation + user management.

Every endpoint is gated on ``users.is_admin`` via
:func:`src.auth.deps.require_admin`. Spec:
``prompts/marketplace/05-trust-and-quality.md``.
"""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin.schemas import (
    AdminUserList,
    AdminUserSummary,
    ApprovalResponse,
    ModerationQueueItem,
    ModerationQueueList,
    RejectRequest,
)
from src.admin.service import (
    approve_skill,
    latest_pending_version,
    list_pending_skills,
    reject_skill,
    suspend_user,
    verify_creator,
)
from src.auth.deps import require_admin
from src.core.db import get_db
from src.core.errors import error_responses
from src.core.pagination import PageInfo, clamp_limit, decode_cursor, encode_cursor
from src.skills.models import Skill
from src.skills.service import CreatorError
from src.users.models import CreatorProfile, User

log = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin", tags=["admin"])


def _raise_creator_error(exc: CreatorError) -> None:
    detail: dict[str, Any] = {"code": exc.code, "message": exc.message}
    if exc.details:
        detail["details"] = exc.details
    raise HTTPException(status_code=exc.status_code, detail=detail)


@router.get(
    "/moderation",
    response_model=ModerationQueueList,
    summary="List skills pending review",
    responses=error_responses(401, 403),
)
async def moderation_queue(
    _admin: Annotated[User, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: int | None = Query(default=None, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> ModerationQueueList:
    real_limit = clamp_limit(limit)
    cursor_id: uuid.UUID | None = None
    if cursor:
        payload = decode_cursor(cursor)
        cursor_id = uuid.UUID(str(payload["id"]))

    rows, has_more = await list_pending_skills(
        session, limit=real_limit, cursor_id=cursor_id
    )

    items: list[ModerationQueueItem] = []
    for skill in rows:
        version = await latest_pending_version(session, skill)
        cp_res = await session.execute(
            select(CreatorProfile).where(CreatorProfile.user_id == skill.creator_id)
        )
        cp = cp_res.scalar_one_or_none()
        creator = await session.get(User, skill.creator_id)
        items.append(
            ModerationQueueItem(
                skill_id=skill.id,
                name=skill.name,
                slug=skill.slug,
                status=skill.status,
                creator_handle=cp.handle if cp else None,
                creator_display_name=creator.display_name if creator else None,
                submitted_version=version.version if version else None,
                submitted_at=skill.updated_at,
                rejection_reason=version.rejection_reason if version else None,
                cover_image_url=skill.cover_image_url,
            )
        )

    next_cursor: str | None = None
    if has_more and rows:
        next_cursor = encode_cursor(last_id=str(rows[-1].id))

    return ModerationQueueList(
        items=items,
        page=PageInfo(next_cursor=next_cursor, has_more=has_more, limit=real_limit),
    )


@router.post(
    "/skills/{skill_id}/approve",
    response_model=ApprovalResponse,
    summary="Approve a pending skill",
    responses=error_responses(401, 403, 404, 409),
)
async def approve(
    skill_id: uuid.UUID,
    admin: Annotated[User, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ApprovalResponse:
    skill = await session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    try:
        skill, version, action = await approve_skill(session, admin=admin, skill=skill)
    except CreatorError as exc:
        _raise_creator_error(exc)
        raise
    await session.commit()
    return ApprovalResponse(
        skill_id=skill.id,
        status=skill.status,
        version=version.version if version else None,
        moderation_action_id=action.id,
    )


@router.post(
    "/skills/{skill_id}/reject",
    response_model=ApprovalResponse,
    summary="Reject a pending skill (with reason)",
    responses=error_responses(401, 403, 404, 409, 422),
)
async def reject(
    skill_id: uuid.UUID,
    body: RejectRequest,
    admin: Annotated[User, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ApprovalResponse:
    skill = await session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    try:
        skill, version, action = await reject_skill(
            session, admin=admin, skill=skill, reason=body.reason
        )
    except CreatorError as exc:
        _raise_creator_error(exc)
        raise
    await session.commit()
    return ApprovalResponse(
        skill_id=skill.id,
        status=skill.status,
        version=version.version if version else None,
        moderation_action_id=action.id,
    )


# ── Users ─────────────────────────────────────────────────────────────


def _summarise_user(
    user: User, profile: CreatorProfile | None
) -> AdminUserSummary:
    return AdminUserSummary(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_creator_verified=user.is_creator_verified,
        creator_handle=profile.handle if profile else None,
        created_at=user.created_at,
    )


@router.get(
    "/users",
    response_model=AdminUserList,
    summary="Search/filter users",
    responses=error_responses(401, 403),
)
async def list_users(
    _admin: Annotated[User, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> AdminUserList:
    real_limit = clamp_limit(limit)
    stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                User.email.ilike(like),
                User.display_name.ilike(like),
            )
        )
    if cursor:
        payload = decode_cursor(cursor)
        cursor_id = uuid.UUID(str(payload["id"]))
        stmt = stmt.where(User.id < cursor_id)

    res = await session.execute(stmt.limit(real_limit + 1))
    rows = list(res.scalars().all())
    has_more = len(rows) > real_limit
    rows = rows[:real_limit]

    items: list[AdminUserSummary] = []
    for u in rows:
        cp = await session.execute(
            select(CreatorProfile).where(CreatorProfile.user_id == u.id)
        )
        items.append(_summarise_user(u, cp.scalar_one_or_none()))

    next_cursor: str | None = None
    if has_more and rows:
        next_cursor = encode_cursor(last_id=str(rows[-1].id))

    return AdminUserList(
        items=items,
        page=PageInfo(next_cursor=next_cursor, has_more=has_more, limit=real_limit),
    )


@router.post(
    "/users/{user_id}/verify-creator",
    response_model=AdminUserSummary,
    summary="Grant the verified-creator badge",
    responses=error_responses(401, 403, 404),
)
async def verify_creator_endpoint(
    user_id: uuid.UUID,
    admin: Annotated[User, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AdminUserSummary:
    target = await session.get(User, user_id)
    if target is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "user.not_found", "message": "User not found."},
        )
    target = await verify_creator(session, admin=admin, target_user=target)
    await session.commit()
    cp = await session.execute(
        select(CreatorProfile).where(CreatorProfile.user_id == target.id)
    )
    return _summarise_user(target, cp.scalar_one_or_none())


@router.post(
    "/users/{user_id}/suspend",
    response_model=AdminUserSummary,
    summary="Suspend (deactivate) a user account",
    responses=error_responses(401, 403, 404),
)
async def suspend(
    user_id: uuid.UUID,
    admin: Annotated[User, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
    body: dict[str, Any] | None = None,
) -> AdminUserSummary:
    target = await session.get(User, user_id)
    if target is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "user.not_found", "message": "User not found."},
        )
    reason = (body or {}).get("reason") if isinstance(body, dict) else None
    target = await suspend_user(
        session, admin=admin, target_user=target, reason=reason
    )
    await session.commit()
    cp = await session.execute(
        select(CreatorProfile).where(CreatorProfile.user_id == target.id)
    )
    return _summarise_user(target, cp.scalar_one_or_none())


__all__ = ["router"]
