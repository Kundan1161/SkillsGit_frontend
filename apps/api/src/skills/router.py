"""``/v1/skills`` + ``/v1/creator/skills`` routers.

Phase 0 only exposed the validator. Phase 1 adds the creator upload path
documented in ``prompts/marketplace/07-creator-dashboard.md`` §
``/dashboard/skills/new`` and the version submission flow under
``POST /v1/creator/skills/{id}/versions``.

The catalog (public discovery, public detail, /v1/skills/{id}) is owned
by Agent A.
"""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.deps import current_active_user
from src.core.db import get_db
from src.core.errors import error_responses
from src.skills.models import PricingModel, Skill, SkillStatus, SkillVersion
from src.skills.schemas import SkillRead, SkillVersionRead
from src.skills.service import (
    CreatorError,
    add_skill_version,
    create_skill_from_upload,
    publish_skill,
    soft_remove_skill,
    update_listing,
    yank_version,
)
from src.skills.validator import ValidationResult, validate_file
from src.users.models import User

log = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/skills", tags=["skills"])


@router.post(
    "/validate",
    summary="Validate a skills.md file",
    description=(
        "Runs the full skills.md validator (frontmatter + body). Returns "
        "structured per-field errors. Does not persist anything."
    ),
    response_model=ValidationResult,
    responses=error_responses(400, 422),
)
async def validate_skill_file(
    file: UploadFile = File(..., description="A skills.md upload."),
) -> ValidationResult:
    content = await file.read()
    return validate_file(content)


@router.get(
    "/",
    summary="List published skills (Phase 1 stub — Agent A owns this)",
    status_code=501,
    responses=error_responses(501),
)
async def list_skills() -> dict[str, str]:
    # Catalog/discovery is owned by Agent A — see prompts/marketplace/01-discovery.md
    raise HTTPException(
        status_code=501,
        detail={
            "code": "skills.list_not_implemented",
            "message": "Skill discovery is implemented by the catalog router.",
        },
    )


# ── Creator-side endpoints ─────────────────────────────────────────────
# Mounted as a separate router so the prefix splits cleanly. Mounted from
# the bottom of this module so it shares import context.

creator_skills_router = APIRouter(
    prefix="/v1/creator/skills", tags=["creator-skills"]
)


def _raise_creator_error(exc: CreatorError) -> None:
    detail: dict[str, Any] = {"code": exc.code, "message": exc.message}
    if exc.details:
        detail["details"] = exc.details
    raise HTTPException(status_code=exc.status_code, detail=detail)


def _to_pricing_model(value: str | None) -> PricingModel:
    if not value:
        return PricingModel.FREE
    try:
        return PricingModel(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "skill.bad_pricing_model",
                "message": f"Unknown pricing model '{value}'.",
            },
        ) from exc


@creator_skills_router.get(
    "/",
    response_model=list[SkillRead],
    summary="List my skills (creator)",
    responses=error_responses(401, 403),
)
async def list_my_skills(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[Skill]:
    res = await session.execute(
        select(Skill)
        .where(Skill.creator_id == user.id, Skill.status != SkillStatus.REMOVED)
        .order_by(Skill.created_at.desc())
    )
    return list(res.scalars().all())


@creator_skills_router.post(
    "/",
    response_model=SkillRead,
    status_code=201,
    summary="Create a draft skill from an uploaded skills.md",
    responses=error_responses(401, 403, 409, 422),
)
async def create_skill(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    skills_md: UploadFile = File(..., description="A skills.md upload."),
    name: str = Form(..., description="Listing display name."),
    tagline: str | None = Form(default=None),
    category: str | None = Form(default=None),
    tags: str | None = Form(
        default=None, description="Comma-separated tags."
    ),
    pricing_model: str | None = Form(default="free"),
    one_time_price_cents: int | None = Form(default=None),
    support_url: str | None = Form(default=None),
    cover_image: UploadFile | None = File(default=None),
) -> Skill:
    skills_md_bytes = await skills_md.read()
    cover_bytes: bytes | None = None
    cover_filename: str | None = None
    cover_content_type: str | None = None
    if cover_image is not None and cover_image.filename:
        cover_bytes = await cover_image.read()
        cover_filename = cover_image.filename
        cover_content_type = cover_image.content_type

    tag_list = (
        [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    )

    # Hydrate creator profile so the service can compare handle.
    res = await session.execute(
        select(User)
        .options(selectinload(User.creator_profile))
        .where(User.id == user.id)
    )
    full_user = res.scalar_one()

    try:
        skill, _version, _validation = await create_skill_from_upload(
            session,
            creator=full_user,
            name=name,
            tagline=tagline,
            category=category,
            tags=tag_list,
            pricing_model=_to_pricing_model(pricing_model),
            one_time_price_cents=one_time_price_cents,
            support_url=support_url,
            cover_filename=cover_filename,
            cover_bytes=cover_bytes,
            cover_content_type=cover_content_type,
            skills_md_bytes=skills_md_bytes,
        )
    except CreatorError as exc:
        _raise_creator_error(exc)
        raise  # unreachable, makes type-checker happy

    await session.commit()
    await session.refresh(skill)
    return skill


@creator_skills_router.patch(
    "/{skill_id}",
    response_model=SkillRead,
    summary="Update listing metadata",
    responses=error_responses(401, 403, 404),
)
async def patch_skill(
    skill_id: uuid.UUID,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    body: dict[str, Any] | None = None,
) -> Skill:
    skill = await session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    if skill.creator_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    try:
        updated = await update_listing(
            session, creator=user, skill=skill, patch=body or {}
        )
    except CreatorError as exc:
        _raise_creator_error(exc)
        raise
    await session.commit()
    await session.refresh(updated)
    return updated


@creator_skills_router.post(
    "/{skill_id}/versions",
    response_model=SkillVersionRead,
    status_code=201,
    summary="Submit a new version of an existing skill",
    responses=error_responses(401, 403, 404, 409, 422),
)
async def submit_version(
    skill_id: uuid.UUID,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    skills_md: UploadFile = File(...),
    changelog_md: str | None = Form(default=None),
    target_version: str | None = Form(default=None),
) -> SkillVersion:
    skill = await session.get(Skill, skill_id)
    if skill is None or (skill.creator_id != user.id and not user.is_admin):
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    body = await skills_md.read()
    try:
        version = await add_skill_version(
            session,
            creator=user,
            skill=skill,
            skills_md_bytes=body,
            changelog_md=changelog_md,
            target_version=target_version,
        )
    except CreatorError as exc:
        _raise_creator_error(exc)
        raise
    await session.commit()
    return version


@creator_skills_router.post(
    "/{skill_id}/publish",
    response_model=SkillRead,
    summary="Submit the skill for review (or fast-track to published)",
    responses=error_responses(401, 403, 404, 409),
)
async def publish(
    skill_id: uuid.UUID,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Skill:
    skill = await session.get(Skill, skill_id)
    if skill is None or (skill.creator_id != user.id and not user.is_admin):
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    try:
        updated = await publish_skill(session, creator=user, skill=skill)
    except CreatorError as exc:
        _raise_creator_error(exc)
        raise
    await session.commit()
    await session.refresh(updated)
    return updated


@creator_skills_router.post(
    "/{skill_id}/versions/{version}/yank",
    response_model=SkillVersionRead,
    summary="Yank a published version",
    responses=error_responses(401, 403, 404),
)
async def yank(
    skill_id: uuid.UUID,
    version: str,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    body: dict[str, Any] | None = None,
) -> SkillVersion:
    skill = await session.get(Skill, skill_id)
    if skill is None or (skill.creator_id != user.id and not user.is_admin):
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    reason = (body or {}).get("reason") if isinstance(body, dict) else None
    try:
        v = await yank_version(
            session, creator=user, skill=skill, version_str=version, reason=reason
        )
    except CreatorError as exc:
        _raise_creator_error(exc)
        raise
    await session.commit()
    return v


@creator_skills_router.delete(
    "/{skill_id}",
    status_code=204,
    summary="Soft-remove a skill",
    responses=error_responses(401, 403, 404),
)
async def remove_skill(
    skill_id: uuid.UUID,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    skill = await session.get(Skill, skill_id)
    if skill is None or (skill.creator_id != user.id and not user.is_admin):
        raise HTTPException(
            status_code=404,
            detail={"code": "skill.not_found", "message": "Skill not found."},
        )
    try:
        await soft_remove_skill(session, creator=user, skill=skill)
    except CreatorError as exc:
        _raise_creator_error(exc)
        raise
    await session.commit()
    return None
