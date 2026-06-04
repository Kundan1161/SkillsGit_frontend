"""Admin/moderation service logic.

Approval/rejection of pending publishes, user suspension, creator
verification grants.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import select

from src.admin.models import ModerationAction
from src.auth.email import send_email
from src.core.db import write_audit
from src.skills.models import Skill, SkillStatus, SkillVersion
from src.users.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


async def approve_skill(
    session: "AsyncSession",
    *,
    admin: User,
    skill: Skill,
) -> tuple[Skill, SkillVersion | None, ModerationAction]:
    if skill.status != SkillStatus.PENDING_REVIEW:
        from src.skills.service import CreatorError

        raise CreatorError(
            code="skill.not_pending",
            message="Only pending_review skills can be approved.",
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
        from src.skills.service import CreatorError

        raise CreatorError(
            code="skill.no_pending_version",
            message="No pending version found.",
            status_code=409,
        )

    now = datetime.now(timezone.utc)
    pending.released_at = now
    pending.released_by = admin.id
    skill.status = SkillStatus.PUBLISHED
    skill.latest_version_id = pending.id

    action = ModerationAction(
        actor_admin_id=admin.id,
        target_type="skill",
        target_id=skill.id,
        action="approved",
        reason=None,
        action_metadata={"version": pending.version},
    )
    session.add(action)
    await session.flush()

    await write_audit(
        session,
        actor_id=admin.id,
        action="moderation.approved",
        target_type="skill",
        target_id=skill.id,
        metadata={"version": pending.version},
    )
    await session.flush()
    # Audit log alias the spec calls out: skill.published.
    await write_audit(
        session,
        actor_id=admin.id,
        action="skill.published",
        target_type="skill",
        target_id=skill.id,
        metadata={"version": pending.version, "approved_by_admin": True},
    )
    await session.flush()

    # Notify the creator.
    creator = await session.get(User, skill.creator_id)
    if creator is not None:
        await send_email(
            to=creator.email,
            subject=f"Your skill '{skill.name}' is live",
            body=(
                "Good news — your skill has been approved and is now live on "
                "the marketplace.\n\n"
                f"Version: {pending.version}\n"
                "You can view it in your dashboard.\n"
            ),
        )

    return skill, pending, action


async def reject_skill(
    session: "AsyncSession",
    *,
    admin: User,
    skill: Skill,
    reason: str,
) -> tuple[Skill, SkillVersion | None, ModerationAction]:
    if skill.status != SkillStatus.PENDING_REVIEW:
        from src.skills.service import CreatorError

        raise CreatorError(
            code="skill.not_pending",
            message="Only pending_review skills can be rejected.",
            status_code=409,
        )

    res = await session.execute(
        select(SkillVersion)
        .where(SkillVersion.skill_id == skill.id, SkillVersion.released_at.is_(None))
        .order_by(SkillVersion.version.desc())
    )
    pending = res.scalar_one_or_none()
    if pending is not None:
        pending.rejection_reason = reason

    # Per spec: stays pending_review, the version carries the rejection_reason.
    action = ModerationAction(
        actor_admin_id=admin.id,
        target_type="skill",
        target_id=skill.id,
        action="rejected",
        reason=reason,
        action_metadata={"version": pending.version if pending else None},
    )
    session.add(action)
    await session.flush()

    await write_audit(
        session,
        actor_id=admin.id,
        action="moderation.rejected",
        target_type="skill",
        target_id=skill.id,
        metadata={"version": pending.version if pending else None, "reason": reason},
    )
    await session.flush()

    creator = await session.get(User, skill.creator_id)
    if creator is not None:
        await send_email(
            to=creator.email,
            subject=f"Your skill '{skill.name}' needs changes",
            body=(
                "An admin reviewed your skill submission and asked for changes "
                "before it goes live.\n\n"
                f"Reason: {reason}\n\n"
                "Resubmit a new version once you've addressed the feedback.\n"
            ),
        )

    return skill, pending, action


async def verify_creator(
    session: "AsyncSession", *, admin: User, target_user: User
) -> User:
    target_user.is_creator_verified = True
    action = ModerationAction(
        actor_admin_id=admin.id,
        target_type="user",
        target_id=target_user.id,
        action="creator_verified",
    )
    session.add(action)
    await write_audit(
        session,
        actor_id=admin.id,
        action="user.creator_verified",
        target_type="user",
        target_id=target_user.id,
    )
    return target_user


async def suspend_user(
    session: "AsyncSession", *, admin: User, target_user: User, reason: str | None
) -> User:
    target_user.is_active = False
    action = ModerationAction(
        actor_admin_id=admin.id,
        target_type="user",
        target_id=target_user.id,
        action="suspended",
        reason=reason,
    )
    session.add(action)
    await write_audit(
        session,
        actor_id=admin.id,
        action="user.suspended",
        target_type="user",
        target_id=target_user.id,
        metadata={"reason": reason},
    )

    # Also unlist all this creator's skills.
    res = await session.execute(
        select(Skill).where(
            Skill.creator_id == target_user.id, Skill.status == SkillStatus.PUBLISHED
        )
    )
    for skill in res.scalars().all():
        skill.status = SkillStatus.UNLISTED
        await write_audit(
            session,
            actor_id=admin.id,
            action="skill.unlisted",
            target_type="skill",
            target_id=skill.id,
            metadata={"reason": "user_suspended"},
        )
    return target_user


async def list_pending_skills(
    session: "AsyncSession",
    *,
    limit: int,
    cursor_id: uuid.UUID | None = None,
) -> tuple[list[Skill], bool]:
    stmt = (
        select(Skill)
        .where(Skill.status == SkillStatus.PENDING_REVIEW)
        .order_by(Skill.updated_at.desc(), Skill.id.desc())
    )
    if cursor_id is not None:
        stmt = stmt.where(Skill.id < cursor_id)
    res = await session.execute(stmt.limit(limit + 1))
    rows = list(res.scalars().all())
    has_more = len(rows) > limit
    return rows[:limit], has_more


async def latest_pending_version(
    session: "AsyncSession", skill: Skill
) -> SkillVersion | None:
    res = await session.execute(
        select(SkillVersion)
        .where(SkillVersion.skill_id == skill.id, SkillVersion.released_at.is_(None))
        .order_by(SkillVersion.version.desc())
    )
    return res.scalar_one_or_none()


__all__ = [
    "approve_skill",
    "latest_pending_version",
    "list_pending_skills",
    "reject_skill",
    "suspend_user",
    "verify_creator",
]
