"""User / creator profile services.

Phase 0: only the bits needed by ``/v1/auth/become-creator`` and ``/me``
edits. Listing creators, public profiles, etc. come in Phase 1.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from src.core.errors import AppError
from src.users.models import CreatorProfile, User, UserRole

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_by_id(session: "AsyncSession", user_id: uuid.UUID) -> User | None:
    res = await session.execute(select(User).where(User.id == user_id))
    return res.scalar_one_or_none()


async def get_creator_profile(
    session: "AsyncSession", user_id: uuid.UUID
) -> CreatorProfile | None:
    res = await session.execute(
        select(CreatorProfile).where(CreatorProfile.user_id == user_id)
    )
    return res.scalar_one_or_none()


async def handle_taken(session: "AsyncSession", handle: str) -> bool:
    res = await session.execute(
        select(CreatorProfile.id).where(CreatorProfile.handle == handle)
    )
    return res.scalar_one_or_none() is not None


async def create_creator_profile(
    session: "AsyncSession",
    *,
    user: User,
    handle: str,
    payout_country: str,
) -> CreatorProfile:
    """Create a creator profile and bump the user's primary role.

    Stripe Connect onboarding is intentionally not started here — that lands
    in Phase 1 via ``prompts/marketplace/03-pricing-and-checkout.md``.
    """
    if await get_creator_profile(session, user.id) is not None:
        raise AppError(
            code="creator.already_exists",
            message="Creator profile already exists for this user.",
            status_code=409,
        )
    if await handle_taken(session, handle):
        raise AppError(
            code="creator.handle_taken",
            message="That handle is already in use.",
            status_code=409,
        )

    profile = CreatorProfile(
        user_id=user.id,
        handle=handle,
        payout_country=payout_country.upper(),
    )
    session.add(profile)

    # Promote the primary role; users keep buyer capabilities.
    if user.role == UserRole.BUYER:
        user.role = UserRole.CREATOR

    await session.flush()
    return profile


__all__ = [
    "create_creator_profile",
    "get_creator_profile",
    "get_user_by_id",
    "handle_taken",
]
