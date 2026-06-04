"""FastAPI dependency helpers.

Capability-based authz checks per ``shared/auth.md``. The auth module wires
the actual ``current_user`` resolver against fastapi-users; this module
re-exports thin wrappers so feature routers don't need to know about the
auth library directly.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from fastapi import Depends, HTTPException, status

from src.core.db import get_db

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.users.models import User


# Re-export db session dep under a stable name.
async def db_session() -> AsyncIterator["AsyncSession"]:
    async for s in get_db():
        yield s


def require_admin(user: "User" = Depends(lambda: None)) -> "User":
    # NOTE: actual current_user dep is wired in src.auth.deps to avoid an
    # import cycle. Tests / Phase 1 callers should import from src.auth.deps.
    if user is None or not getattr(user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "auth.forbidden", "message": "Admin required."},
        )
    return user


__all__ = ["db_session", "require_admin"]
