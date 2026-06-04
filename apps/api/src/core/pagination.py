"""Cursor-based pagination.

Cursors are HMAC-signed base64 JSON blobs:
``base64url({"id": "<last-id>", "v": "<sort-tiebreaker>"}).<sig>``

See ``shared/api-conventions.md`` for the wire contract.
"""

from __future__ import annotations

import base64
import hmac
import json
from hashlib import sha256
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.errors import AppError

T = TypeVar("T")

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


class PageInfo(BaseModel):
    """Trailing ``page`` block of every list response."""

    next_cursor: str | None = None
    has_more: bool = False
    limit: int = DEFAULT_LIMIT

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"next_cursor": "eyJpZCI6Ii4uLiJ9.abc", "has_more": True, "limit": 20}
            ]
        }
    )


class Page(BaseModel, Generic[T]):
    """Generic paginated payload: ``{items, page}``."""

    items: list[T] = Field(default_factory=list)
    page: PageInfo


# ── Cursor codec ──────────────────────────────────────────────────────
def _hmac_sig(payload: bytes) -> str:
    key = settings.PLATFORM_HMAC_KEY.get_secret_value().encode("utf-8")
    return hmac.new(key, payload, sha256).hexdigest()[:16]


def encode_cursor(*, last_id: str, tiebreaker: str | None = None) -> str:
    """Encode a cursor pointing at the last row of a page."""
    payload_dict: dict[str, Any] = {"id": last_id}
    if tiebreaker is not None:
        payload_dict["v"] = tiebreaker
    payload = json.dumps(payload_dict, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    b64 = base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")
    return f"{b64}.{_hmac_sig(payload)}"


def decode_cursor(cursor: str) -> dict[str, Any]:
    """Decode and verify a cursor signature. Raises :class:`AppError` on tamper."""
    try:
        b64, sig = cursor.split(".", 1)
    except ValueError as exc:
        raise AppError(
            code="pagination.bad_cursor",
            message="Cursor is malformed.",
            status_code=400,
        ) from exc

    padding = "=" * (-len(b64) % 4)
    try:
        payload = base64.urlsafe_b64decode(b64 + padding)
    except Exception as exc:
        raise AppError(
            code="pagination.bad_cursor",
            message="Cursor is malformed.",
            status_code=400,
        ) from exc

    if not hmac.compare_digest(sig, _hmac_sig(payload)):
        raise AppError(
            code="pagination.bad_cursor_signature",
            message="Cursor signature does not match.",
            status_code=400,
        )

    try:
        return json.loads(payload)  # type: ignore[no-any-return]
    except json.JSONDecodeError as exc:
        raise AppError(
            code="pagination.bad_cursor",
            message="Cursor payload is not valid JSON.",
            status_code=400,
        ) from exc


def clamp_limit(limit: int | None) -> int:
    if limit is None:
        return DEFAULT_LIMIT
    if limit < 1:
        return 1
    if limit > MAX_LIMIT:
        return MAX_LIMIT
    return limit


async def paginate(
    session: AsyncSession,
    stmt: Select[Any],
    *,
    limit: int | None = None,
    cursor: str | None = None,
    id_column: str = "id",
) -> tuple[list[Any], PageInfo]:
    """Execute ``stmt`` paginated by primary key.

    Caller is responsible for ordering the statement (usually
    ``order_by(model.id)``). We over-fetch by one to detect ``has_more``.

    For Phase 0 this is intentionally minimal; richer
    (multi-column / direction-aware) cursors will land alongside the catalog
    module in Phase 1 — see ``prompts/marketplace/01-discovery.md``.
    """
    real_limit = clamp_limit(limit)
    fetched = await session.execute(stmt.limit(real_limit + 1))
    rows = list(fetched.scalars().all())
    has_more = len(rows) > real_limit
    if has_more:
        rows = rows[:real_limit]

    next_cursor: str | None = None
    if has_more and rows:
        last = rows[-1]
        last_id = getattr(last, id_column)
        next_cursor = encode_cursor(last_id=str(last_id))

    return rows, PageInfo(
        next_cursor=next_cursor, has_more=has_more, limit=real_limit
    )


__all__ = [
    "DEFAULT_LIMIT",
    "MAX_LIMIT",
    "Page",
    "PageInfo",
    "clamp_limit",
    "decode_cursor",
    "encode_cursor",
    "paginate",
]
