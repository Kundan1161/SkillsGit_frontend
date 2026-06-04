"""Skill / version services.

Phase 0 only — most CRUD (publish flows, version pinning, etc.) is deferred
to ``prompts/marketplace/04-licensing-and-delivery.md`` and the
creator-side prompts. This file currently exposes basic readers used by
the validator and future routers — plus the Phase 1 creator upload path
appended below.
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from src.core.db import write_audit
from src.delivery.watermark import compute_content_hash, inject_distribution_block
from src.skills.models import (
    ALLOWED_AI_MODELS,  # noqa: F401 — re-exported by callers
    Category,
    PricingModel,
    Skill,
    SkillStatus,
    SkillVersion,
)
from src.skills.parser import split_frontmatter
from src.skills.validator import ValidationResult, validate_file
from src.storage.s3 import get_storage

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.users.models import User

log = logging.getLogger(__name__)

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[\w.]+)?$")

# Daily publish-rate cap per `05-trust-and-quality.md`.
PUBLISH_COOLDOWN_PER_DAY = 5


async def get_skill_by_id(session: "AsyncSession", skill_id: uuid.UUID) -> Skill | None:
    res = await session.execute(select(Skill).where(Skill.id == skill_id))
    return res.scalar_one_or_none()


async def list_categories(session: "AsyncSession") -> list[Category]:
    res = await session.execute(
        select(Category).order_by(Category.display_order, Category.slug)
    )
    return list(res.scalars().all())


# ── Creator upload path ──────────────────────────────────────────────────


class CreatorError(Exception):
    """Raised by service methods so the router can map to a typed error."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
        details: list[Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def _skill_storage_key(skill_id: uuid.UUID, version: str) -> str:
    return f"skills/{skill_id}/{version}.md"


def _cover_storage_key(skill_id: uuid.UUID, extension: str) -> str:
    ext = extension.lstrip(".") or "bin"
    return f"covers/{skill_id}.{ext}"


def parse_frontmatter_fields(
    content: bytes,
) -> tuple[dict[str, Any], str]:
    """Validator-less split — used to extract id/version after validation."""
    return split_frontmatter(content)


async def upload_skill_body(skill_id: uuid.UUID, version: str, content: bytes) -> str:
    """Persist the canonical body to object storage, return the storage key."""
    storage = get_storage()
    key = _skill_storage_key(skill_id, version)
    # Inject distribution block on upload so the canonical copy on S3 is
    # already signed. The watermarking pipeline re-signs at delivery time
    # (with a fresh signed_at) but having the block now keeps the file
    # spec-compliant from the moment it lands.
    text = content.decode("utf-8")
    stamped = inject_distribution_block(text)
    await storage.put_object(key, stamped.encode("utf-8"), "text/markdown")
    return key


async def upload_cover_image(
    skill_id: uuid.UUID, filename: str, content: bytes, content_type: str
) -> str:
    storage = get_storage()
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    key = _cover_storage_key(skill_id, ext)
    await storage.put_object(key, content, content_type)
    return key


async def _validate_or_raise(content: bytes) -> ValidationResult:
    result = validate_file(content)
    if not result.is_valid:
        raise CreatorError(
            code="skill.publish_validation_failed",
            message="skills.md failed validation; see details.",
            status_code=422,
        )
    return result


async def create_skill_from_upload(
    session: "AsyncSession",
    *,
    creator: "User",
    name: str,
    tagline: str | None,
    category: str | None,
    tags: list[str] | None,
    pricing_model: PricingModel,
    one_time_price_cents: int | None,
    support_url: str | None,
    cover_filename: str | None,
    cover_bytes: bytes | None,
    cover_content_type: str | None,
    skills_md_bytes: bytes,
) -> tuple[Skill, SkillVersion, ValidationResult]:
    """Create a new draft Skill + first (unreleased) SkillVersion.

    Validates the uploaded skills.md, persists the body to S3, and writes
    the DB rows. Raises :class:`CreatorError` on validation failure (422)
    or business-rule conflicts.
    """
    if not name.strip():
        raise CreatorError(
            code="skill.invalid_name",
            message="name is required.",
            status_code=422,
        )

    # 1. Schema validation.
    result = validate_file(skills_md_bytes)
    if not result.is_valid:
        from src.core.errors import ErrorDetail

        details = [
            ErrorDetail(field=e.field, code=e.code, message=e.message)
            for e in result.errors
        ]
        raise _detailed_error(
            "skill.publish_validation_failed",
            "skills.md failed validation; see details.",
            details=details,
        )

    fm_dict, _body = split_frontmatter(skills_md_bytes)
    creator_handle, slug = str(fm_dict["id"]).split("/", 1)
    version_str = str(fm_dict["version"])

    # 2. Ownership: creator handle in `id` must match this creator's handle.
    profile = creator.creator_profile if hasattr(creator, "creator_profile") else None
    actual_handle: str | None = None
    if profile is not None:
        actual_handle = profile.handle
    if actual_handle and actual_handle.lower() != creator_handle.lower():
        raise CreatorError(
            code="skill.handle_mismatch",
            message=(
                f"frontmatter id '{creator_handle}/...' does not match your "
                f"handle '{actual_handle}'."
            ),
            status_code=422,
        )

    # 3. Slug uniqueness within this creator.
    existing = await session.execute(
        select(Skill).where(Skill.creator_id == creator.id, Skill.slug == slug)
    )
    if existing.scalar_one_or_none() is not None:
        raise CreatorError(
            code="skill.slug_conflict",
            message=f"You already have a skill with slug '{slug}'.",
            status_code=409,
        )

    # 4. Build rows.
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=name.strip()[:120],
        tagline=(tagline or None) and tagline.strip()[:140],
        category=category,
        tags=tags or None,
        status=SkillStatus.DRAFT,
        pricing_model=pricing_model,
        one_time_price_cents=one_time_price_cents,
        support_url=support_url,
    )
    session.add(skill)
    await session.flush()  # gets skill.id

    # 5. Upload body to S3.
    storage_key = await upload_skill_body(skill.id, version_str, skills_md_bytes)

    # 6. Cover.
    if cover_bytes is not None and cover_filename:
        cover_key = await upload_cover_image(
            skill.id,
            cover_filename,
            cover_bytes,
            cover_content_type or "application/octet-stream",
        )
        skill.cover_image_url = cover_key

    # 7. First version row — released_at stays None until publish.
    content_hash = compute_content_hash(skills_md_bytes.decode("utf-8"))
    version = SkillVersion(
        skill_id=skill.id,
        version=version_str,
        content_hash=content_hash,
        storage_url=storage_key,
        ai_requirements=fm_dict.get("ai"),
        changelog_md=None,
        released_at=None,
        is_yanked=False,
        target_version=version_str,
    )
    session.add(version)
    await session.flush()

    await write_audit(
        session,
        actor_id=creator.id,
        action="skill.created",
        target_type="skill",
        target_id=skill.id,
        metadata={"slug": slug, "version": version_str},
    )
    await session.flush()

    return skill, version, result


def _detailed_error(code: str, message: str, *, details: list[Any]) -> CreatorError:
    return CreatorError(
        code=code, message=message, status_code=422, details=details
    )


async def add_skill_version(
    session: "AsyncSession",
    *,
    creator: "User",
    skill: Skill,
    skills_md_bytes: bytes,
    changelog_md: str | None,
    target_version: str | None,
) -> SkillVersion:
    """Create a new (unreleased) SkillVersion for an existing skill."""
    if skill.creator_id != creator.id and not creator.is_admin:
        raise CreatorError(
            code="skill.forbidden",
            message="You do not own this skill.",
            status_code=403,
        )

    result = validate_file(skills_md_bytes)
    if not result.is_valid:
        from src.core.errors import ErrorDetail

        details = [
            ErrorDetail(field=e.field, code=e.code, message=e.message)
            for e in result.errors
        ]
        raise _detailed_error(
            "skill.publish_validation_failed",
            "skills.md failed validation; see details.",
            details=details,
        )

    fm_dict, _body = split_frontmatter(skills_md_bytes)
    version_str = target_version or str(fm_dict["version"])
    if not SEMVER_RE.match(version_str):
        raise CreatorError(
            code="skill.bad_version",
            message=f"'{version_str}' is not a valid semver.",
            status_code=422,
        )

    existing = await session.execute(
        select(SkillVersion).where(
            SkillVersion.skill_id == skill.id,
            SkillVersion.version == version_str,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise CreatorError(
            code="skill.version_exists",
            message=f"Version {version_str} already exists on this skill.",
            status_code=409,
        )

    storage_key = await upload_skill_body(skill.id, version_str, skills_md_bytes)
    content_hash = compute_content_hash(skills_md_bytes.decode("utf-8"))
    version = SkillVersion(
        skill_id=skill.id,
        version=version_str,
        content_hash=content_hash,
        storage_url=storage_key,
        ai_requirements=fm_dict.get("ai"),
        changelog_md=changelog_md,
        released_at=None,
        is_yanked=False,
        target_version=version_str,
    )
    session.add(version)
    await session.flush()

    await write_audit(
        session,
        actor_id=creator.id,
        action="skill.version_submitted",
        target_type="skill_version",
        target_id=version.id,
        metadata={"skill_id": str(skill.id), "version": version_str},
    )
    await session.flush()
    return version


async def publish_skill(
    session: "AsyncSession",
    *,
    creator: "User",
    skill: Skill,
) -> Skill:
    """Transition the skill from ``draft`` to ``pending_review`` (or
    ``published`` if the creator is fast-tracked)."""
    if skill.creator_id != creator.id and not creator.is_admin:
        raise CreatorError(
            code="skill.forbidden",
            message="You do not own this skill.",
            status_code=403,
        )

    if skill.status == SkillStatus.PUBLISHED:
        raise CreatorError(
            code="skill.already_published",
            message="Skill is already published.",
            status_code=409,
        )

    # Find the most recent unreleased version.
    res = await session.execute(
        select(SkillVersion)
        .where(SkillVersion.skill_id == skill.id, SkillVersion.released_at.is_(None))
        .order_by(SkillVersion.version.desc())
    )
    pending = res.scalar_one_or_none()
    if pending is None:
        raise CreatorError(
            code="skill.no_pending_version",
            message="No draft version is pending publish.",
            status_code=409,
        )

    fast_track = bool(creator.is_creator_verified) and await _has_zero_pending_publishes(
        session, creator_id=creator.id, exclude_skill=skill.id
    )

    if fast_track:
        pending.released_at = datetime.now(timezone.utc)
        pending.released_by = creator.id
        skill.status = SkillStatus.PUBLISHED
        skill.latest_version_id = pending.id
        await write_audit(
            session,
            actor_id=creator.id,
            action="skill.published",
            target_type="skill",
            target_id=skill.id,
            metadata={"version": pending.version, "fast_track": True},
        )
    else:
        skill.status = SkillStatus.PENDING_REVIEW
        pending.rejection_reason = None  # clear any previous rejection
        await write_audit(
            session,
            actor_id=creator.id,
            action="skill.submitted_for_review",
            target_type="skill",
            target_id=skill.id,
            metadata={"version": pending.version},
        )

    return skill


async def _has_zero_pending_publishes(
    session: "AsyncSession", *, creator_id: uuid.UUID, exclude_skill: uuid.UUID
) -> bool:
    res = await session.execute(
        select(Skill).where(
            Skill.creator_id == creator_id,
            Skill.status == SkillStatus.PENDING_REVIEW,
            Skill.id != exclude_skill,
        )
    )
    return res.scalar_one_or_none() is None


async def yank_version(
    session: "AsyncSession",
    *,
    creator: "User",
    skill: Skill,
    version_str: str,
    reason: str | None,
) -> SkillVersion:
    if skill.creator_id != creator.id and not creator.is_admin:
        raise CreatorError(
            code="skill.forbidden",
            message="You do not own this skill.",
            status_code=403,
        )
    res = await session.execute(
        select(SkillVersion).where(
            SkillVersion.skill_id == skill.id, SkillVersion.version == version_str
        )
    )
    version = res.scalar_one_or_none()
    if version is None:
        raise CreatorError(
            code="skill.version_not_found",
            message=f"Version {version_str} not found.",
            status_code=404,
        )

    version.is_yanked = True
    version.yank_reason = reason

    # If the yanked version was latest, point latest_version_id at the
    # next-best (most recent released, unyanked) version.
    if skill.latest_version_id == version.id:
        latest_res = await session.execute(
            select(SkillVersion)
            .where(
                SkillVersion.skill_id == skill.id,
                SkillVersion.id != version.id,
                SkillVersion.released_at.is_not(None),
                SkillVersion.is_yanked.is_(False),
            )
            .order_by(SkillVersion.released_at.desc())
        )
        replacement = latest_res.scalar_one_or_none()
        skill.latest_version_id = replacement.id if replacement else None

    await write_audit(
        session,
        actor_id=creator.id,
        action="skill.yanked",
        target_type="skill_version",
        target_id=version.id,
        metadata={"skill_id": str(skill.id), "version": version_str, "reason": reason},
    )
    return version


async def soft_remove_skill(
    session: "AsyncSession", *, creator: "User", skill: Skill
) -> Skill:
    if skill.creator_id != creator.id and not creator.is_admin:
        raise CreatorError(
            code="skill.forbidden",
            message="You do not own this skill.",
            status_code=403,
        )
    skill.status = SkillStatus.REMOVED
    skill.deleted_at = datetime.now(timezone.utc)
    await write_audit(
        session,
        actor_id=creator.id,
        action="skill.unlisted",
        target_type="skill",
        target_id=skill.id,
        metadata={"reason": "soft_remove"},
    )
    return skill


async def update_listing(
    session: "AsyncSession",
    *,
    creator: "User",
    skill: Skill,
    patch: dict[str, Any],
) -> Skill:
    if skill.creator_id != creator.id and not creator.is_admin:
        raise CreatorError(
            code="skill.forbidden",
            message="You do not own this skill.",
            status_code=403,
        )
    allowed = {
        "name",
        "tagline",
        "description_md",
        "category",
        "tags",
        "cover_image_url",
        "screenshots",
        "support_url",
        "faq_md",
    }
    for key, value in patch.items():
        if key not in allowed:
            continue
        setattr(skill, key, value)
    await write_audit(
        session,
        actor_id=creator.id,
        action="skill.updated",
        target_type="skill",
        target_id=skill.id,
        metadata={"fields": list(k for k in patch.keys() if k in allowed)},
    )
    return skill


__all__ = [
    "CreatorError",
    "add_skill_version",
    "create_skill_from_upload",
    "get_skill_by_id",
    "list_categories",
    "publish_skill",
    "soft_remove_skill",
    "update_listing",
    "yank_version",
]
