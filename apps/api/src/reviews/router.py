"""``/v1/reviews`` router — Phase 0 stub.

TODO Phase 2: ``prompts/marketplace/05-trust-and-quality.md``.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.core.errors import error_responses

router = APIRouter(prefix="/v1/reviews", tags=["reviews"])


@router.get(
    "/",
    status_code=501,
    responses=error_responses(501),
    summary="List reviews (Phase 2)",
)
async def list_reviews() -> dict[str, str]:
    # TODO Phase 2: prompts/marketplace/05-trust-and-quality.md
    raise HTTPException(
        status_code=501,
        detail={
            "code": "reviews.list_not_implemented",
            "message": "Reviews land in Phase 2.",
        },
    )
