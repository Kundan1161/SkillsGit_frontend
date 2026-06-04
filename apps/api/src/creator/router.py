"""``/v1/creator`` router — Phase 0 stub.

TODO Phase 3: visual builder persistence, importers, sandbox.
See ``prompts/skill-creator/*``.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.core.errors import error_responses

router = APIRouter(prefix="/v1/creator", tags=["creator"])


@router.get(
    "/drafts",
    status_code=501,
    responses=error_responses(501),
    summary="List builder drafts (Phase 3)",
)
async def list_drafts() -> dict[str, str]:
    # TODO Phase 3: prompts/skill-creator/01-visual-builder.md
    raise HTTPException(
        status_code=501,
        detail={
            "code": "creator.drafts_not_implemented",
            "message": "Creator drafts land in Phase 3.",
        },
    )
