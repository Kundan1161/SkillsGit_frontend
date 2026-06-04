"""``/v1`` router — vault build read endpoints + composed downloads.

Per ``team/02-api-surface.md`` §4. Mounts under no prefix because the
spec spreads vault routes across two namespaces:

* ``/v1/licenses/{occupation_license_id}/vault`` — the buyer's
  composed-download endpoint (POSTed against the occupation license
  the buyer owns).
* ``/v1/licenses/{occupation_license_id}/vault/downloads`` — the
  buyer's per-license download history.
* ``/v1/vault/builds/{build_id}`` — admin/owner read of a single
  vault_builds row (a thin alias for the same data the
  ``vault_builds`` audit endpoints expose; the brief asks for it
  under ``/v1/vault/...`` for cleanliness).

The orchestrator mounts this router in ``apps/api/src/main.py`` after
T-07 returns (do not touch ``main.py`` from this module). The mount
line is recorded in ``team/dev-diary-vault-composer-wave3.md``.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime  # noqa: TC003 — FastAPI runtime needs the type
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002  (FastAPI dep)

from src.auth.deps import current_active_user
from src.billing.models import License, LicenseCompositionRole
from src.core.db import get_db, write_audit
from src.core.errors import error_responses
from src.core.pagination import PageInfo, clamp_limit, decode_cursor, encode_cursor
from src.users.models import User  # noqa: TC001  (FastAPI dep)
from src.vault import composer as composer_mod
from src.vault.models import VaultBuild, VaultDownload

log = logging.getLogger(__name__)

router = APIRouter(tags=["vault"])


# ── Request / response shapes ────────────────────────────────────────


class VaultDownloadRequest(BaseModel):
    """Body for ``POST /v1/licenses/{id}/vault``."""

    include_persona_license_ids: list[uuid.UUID] | None = Field(
        default=None,
        description=(
            "Subset of the buyer's active persona licenses to include. "
            "When omitted, every active persona license for this "
            "occupation is included by default."
        ),
    )

    model_config = ConfigDict(extra="forbid")


class VaultDownloadResponse(BaseModel):
    """Payload returned by ``POST /v1/licenses/{id}/vault``."""

    presigned_url: str
    expires_at: datetime
    composed_hash: str
    cache_hit: bool
    vault_download_id: uuid.UUID
    occupation_build_id: uuid.UUID
    persona_build_ids: list[uuid.UUID] = Field(default_factory=list)


class VaultDownloadHistoryEntry(BaseModel):
    """One row in the buyer's vault-download history."""

    id: uuid.UUID
    composed_hash: str
    occupation_build_id: uuid.UUID
    persona_build_ids: list[uuid.UUID] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VaultDownloadHistory(BaseModel):
    items: list[VaultDownloadHistoryEntry] = Field(default_factory=list)
    page: PageInfo


class VaultBuildSummary(BaseModel):
    """Lightweight :class:`VaultBuild` projection.

    The brief asks for ``GET /v1/vault/builds/{build_id}`` — a thin
    read for buyers/owners. We return the same shape as the existing
    creator-side build endpoint (``GET /v1/vault-builds/{id}``) without
    the full manifest body (which can be hundreds of KB) — instead a
    compact summary so the page can render quickly.
    """

    id: uuid.UUID
    skill_id: uuid.UUID
    skill_version_id: uuid.UUID
    status: str
    content_hash: str
    storage_url: str
    file_count: int
    total_bytes: int
    built_at: datetime | None = None
    manifest_summary: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)


# ── Helpers ──────────────────────────────────────────────────────────


def _client_ip(request: Request) -> str | None:
    """Reuses delivery router's convention for X-Forwarded-For."""
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return None


def _persona_build_ids_as_uuid_list(value: Any) -> list[uuid.UUID]:
    """Coerce the JSON/ARRAY column to a list of UUIDs.

    The persona_build_ids column is ``UUID[]`` on Postgres and JSON on
    sqlite; both end up as a Python list of strings or UUIDs. Normalise
    to ``list[UUID]`` so downstream serialisers don't choke.
    """
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        return []
    out: list[uuid.UUID] = []
    for item in value:
        if isinstance(item, uuid.UUID):
            out.append(item)
        else:
            try:
                out.append(uuid.UUID(str(item)))
            except (TypeError, ValueError):
                continue
    return out


def _compose_error_to_http(exc: composer_mod.VaultComposeError) -> HTTPException:
    """Translate a typed composer exception into FastAPI's HTTPException."""
    detail: dict[str, Any] = {"code": exc.code, "message": exc.message}
    if exc.details:
        detail["details"] = [
            {"field": k, "code": exc.code, "message": str(v)}
            for k, v in exc.details.items()
        ]
    return HTTPException(status_code=exc.status_code, detail=detail)


# ── Endpoints ────────────────────────────────────────────────────────


@router.post(
    "/v1/licenses/{occupation_license_id}/vault",
    response_model=VaultDownloadResponse,
    status_code=status.HTTP_200_OK,
    summary="Compose + download the buyer's vault bundle",
    responses=error_responses(401, 403, 404, 409, 422),
)
async def compose_vault_endpoint(
    occupation_license_id: uuid.UUID,
    payload: VaultDownloadRequest,
    request: Request,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> VaultDownloadResponse:
    """Request a composed vault bundle for ``occupation_license_id``.

    The composer:

    * Verifies the buyer owns the occupation license (404 otherwise).
    * Verifies any requested persona-license-ids are also held by the
      buyer (403 ``vault.persona_license_not_held`` otherwise).
    * On cache hit (Redis, 24h TTL per ADR-006), returns the cached
      bundle's presigned URL without re-zipping.
    * On miss, merges occupation + persona builds, watermarks per
      buyer, writes a ``vault_downloads`` audit row, and returns a 60s
      presigned URL per ADR-006.
    """
    try:
        result = await composer_mod.compose_for_license(
            session,
            buyer_id=user.id,
            occupation_license_id=occupation_license_id,
            include_persona_license_ids=payload.include_persona_license_ids,
            user_agent=request.headers.get("user-agent"),
            client_ip=_client_ip(request),
        )
    except composer_mod.VaultComposeError as exc:
        # Roll back any partial DB work before surfacing the error.
        await session.rollback()
        raise _compose_error_to_http(exc) from exc

    # Audit the download event on the occupation license (mirrors the
    # existing single-skill delivery flow's audit row).
    await write_audit(
        session,
        actor_id=user.id,
        action="license.vault_downloaded",
        target_type="license",
        target_id=occupation_license_id,
        metadata={
            "vault_download_id": str(result.vault_download_id),
            "composed_hash": result.composed_hash,
            "cache_hit": result.cache_hit,
            "occupation_build_id": str(result.occupation_build_id),
            "persona_build_ids": [str(p) for p in result.persona_build_ids],
        },
    )
    await session.commit()

    return VaultDownloadResponse(
        presigned_url=result.presigned_url,
        expires_at=result.expires_at,
        composed_hash=result.composed_hash,
        cache_hit=result.cache_hit,
        vault_download_id=result.vault_download_id,
        occupation_build_id=result.occupation_build_id,
        persona_build_ids=result.persona_build_ids,
    )


@router.get(
    "/v1/licenses/{occupation_license_id}/vault/downloads",
    response_model=VaultDownloadHistory,
    summary="List past composed downloads for this license",
    responses=error_responses(401, 404),
)
async def list_vault_downloads_endpoint(
    occupation_license_id: uuid.UUID,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: int | None = Query(default=None, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> VaultDownloadHistory:
    """Return the buyer's :class:`VaultDownload` rows for this license.

    Only the license owner (or an admin) can read this — non-owners get
    a 404 to avoid existence leaks.
    """
    lic = await session.get(License, occupation_license_id)
    if lic is None or (
        str(lic.buyer_id) != str(user.id) and not user.is_admin
    ):
        raise HTTPException(
            status_code=404,
            detail={
                "code": "license.not_found",
                "message": "License not found.",
            },
        )

    real_limit = clamp_limit(limit)
    stmt = (
        select(VaultDownload)
        .where(VaultDownload.occupation_license_id == occupation_license_id)
        .order_by(desc(VaultDownload.created_at), desc(VaultDownload.id))
    )
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
        stmt = stmt.where(VaultDownload.id < last_id)

    res = await session.execute(stmt.limit(real_limit + 1))
    rows = list(res.scalars().all())
    has_more = len(rows) > real_limit
    rows = rows[:real_limit]

    items = [
        VaultDownloadHistoryEntry(
            id=row.id,
            composed_hash=row.composed_hash,
            occupation_build_id=row.occupation_build_id,
            persona_build_ids=_persona_build_ids_as_uuid_list(
                row.persona_build_ids
            ),
            created_at=row.created_at,
        )
        for row in rows
    ]

    next_cursor: str | None = None
    if has_more and rows:
        next_cursor = encode_cursor(last_id=str(rows[-1].id))

    return VaultDownloadHistory(
        items=items,
        page=PageInfo(next_cursor=next_cursor, has_more=has_more, limit=real_limit),
    )


@router.get(
    "/v1/vault/builds/{build_id}",
    response_model=VaultBuildSummary,
    summary="Read a single vault build by id",
    responses=error_responses(401, 403, 404),
)
async def get_vault_build_endpoint(
    build_id: uuid.UUID,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> VaultBuildSummary:
    """Return summary data for a single :class:`VaultBuild`.

    Authorisation: the caller must hold an active license that covers
    the build's parent skill (either the occupation directly or a
    persona that lists the buyer's parent_occupation_id). Admins can
    read any build.
    """
    build = await session.get(VaultBuild, build_id)
    if build is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "vault.build_not_found",
                "message": "Vault build not found.",
            },
        )

    if not user.is_admin:
        # Owner of the parent skill? Allowed.
        from src.skills.models import Skill  # noqa: PLC0415 — local import avoids cycle

        skill = await session.get(Skill, build.skill_id)
        is_owner = skill is not None and str(skill.creator_id) == str(user.id)
        if not is_owner:
            # Or hold a license that covers it (occupation, persona, or
            # standalone — any active license on the same skill_id).
            stmt = select(License).where(
                License.buyer_id == user.id,
                License.skill_id == build.skill_id,
            )
            res = await session.execute(stmt)
            licensed = res.scalar_one_or_none()
            if licensed is None:
                # Or hold an occupation license for which this build is
                # a persona overlay (target_occupation_skill_id ==
                # parent occupation of the persona).
                if skill is not None:
                    from src.personas.models import Persona  # noqa: PLC0415

                    persona = await session.get(Persona, skill.id)
                    if persona is not None and persona.parent_occupation_id is not None:
                        stmt2 = select(License).where(
                            License.buyer_id == user.id,
                            License.skill_id == persona.parent_occupation_id,
                            License.composition_role
                            == LicenseCompositionRole.OCCUPATION,
                        )
                        res2 = await session.execute(stmt2)
                        licensed = res2.scalar_one_or_none()
                if licensed is None:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "code": "vault.build_not_found",
                            "message": "Vault build not found.",
                        },
                    )

    # Pluck a small summary from the manifest_json to keep the response
    # under a couple of KB (the full manifest can be very large).
    manifest_summary: dict[str, Any] | None = None
    if isinstance(build.manifest_json, dict):
        files = build.manifest_json.get("files") or []
        manifest_summary = {
            "schema_version": build.manifest_json.get("schema_version"),
            "vault_id": build.manifest_json.get("vault_id"),
            "file_count": len(files) if isinstance(files, list) else 0,
            "warning_count": len(build.manifest_json.get("warnings") or []),
        }

    return VaultBuildSummary(
        id=build.id,
        skill_id=build.skill_id,
        skill_version_id=build.skill_version_id,
        status=build.status.value,
        content_hash=build.content_hash,
        storage_url=build.storage_url,
        file_count=build.file_count,
        total_bytes=build.total_bytes,
        built_at=build.built_at,
        manifest_summary=manifest_summary,
    )


__all__ = ["router"]
