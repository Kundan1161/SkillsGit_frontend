"""Delivery service — license resolution + watermark pipeline.

Public entrypoints:

- :func:`entitled_version` — resolve which ``SkillVersion`` a license
  currently entitles the buyer to. See
  ``prompts/marketplace/04-licensing-and-delivery.md`` §
  *License resolution*.
- :class:`DeliveryService` — orchestrates the download path: validates
  ownership, fetches canonical body, applies the watermark, writes to a
  short-lived prefix, returns a presigned URL.
"""

from __future__ import annotations

import logging
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import and_, desc, select

from src.billing.models import License, LicenseStatus
from src.core.db import write_audit
from src.delivery.watermark import (
    build_delivery_payload,
    hash_ip,
    hash_ua,
)
from src.skills.models import Skill, SkillStatus, SkillVersion
from src.storage.s3 import get_storage

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)

# Tolerance for clock drift between Stripe and our server when a creator
# publishes a version moments before purchase. See spec § License resolution.
GRACE = timedelta(seconds=60)

# Download URLs are short-lived. The watermark generation is fresh per
# download, so a leak via the URL itself only exposes one buyer's copy.
DOWNLOAD_URL_TTL_SECONDS = 60


def _major(version: str) -> int:
    """Return the major component of a semver string (best-effort)."""
    try:
        return int(version.split(".", 1)[0])
    except (ValueError, IndexError):
        return 0


async def entitled_version(
    session: "AsyncSession", license_obj: License
) -> SkillVersion | None:
    """Return the most-recent :class:`SkillVersion` this license entitles to.

    Returns ``None`` if the license is inactive, the skill was removed, or
    no released version matches the license's constraints.
    """
    if license_obj.status != LicenseStatus.ACTIVE:
        return None

    # Cheap guard: if the parent skill is removed, no download is allowed.
    skill = await session.get(Skill, license_obj.skill_id)
    if skill is None or skill.status == SkillStatus.REMOVED:
        return None

    # A one-time / free license entitles to any non-yanked version within
    # the major cap — including versions released BEFORE the grant. Buying
    # today must give you the version current at purchase, even though
    # that row was authored months ago. Subscriptions pass max_version=None
    # and so resolve to the absolute latest non-yanked.
    stmt = (
        select(SkillVersion)
        .where(
            SkillVersion.skill_id == license_obj.skill_id,
            SkillVersion.released_at.is_not(None),
            SkillVersion.is_yanked.is_(False),
        )
        .order_by(desc(SkillVersion.released_at))
    )
    res = await session.execute(stmt)
    candidates = list(res.scalars().all())

    if license_obj.max_version:
        cap = _major(license_obj.max_version)
        candidates = [v for v in candidates if _major(v.version) <= cap]

    return candidates[0] if candidates else None


# ── Resolution by explicit version (for /download/{version}) ──────────────
async def resolve_explicit_version(
    session: "AsyncSession",
    license_obj: License,
    version: str,
) -> SkillVersion | None:
    """Validate that the license entitles to ``version`` and return it."""
    latest = await entitled_version(session, license_obj)
    if latest is None:
        return None
    if version == latest.version:
        return latest

    stmt = select(SkillVersion).where(
        and_(
            SkillVersion.skill_id == license_obj.skill_id,
            SkillVersion.version == version,
            SkillVersion.released_at.is_not(None),
            SkillVersion.is_yanked.is_(False),
            SkillVersion.released_at >= license_obj.granted_at - GRACE,
        )
    )
    res = await session.execute(stmt)
    candidate = res.scalar_one_or_none()
    if candidate is None:
        return None
    if license_obj.max_version and _major(candidate.version) > _major(
        license_obj.max_version
    ):
        return None
    return candidate


# ── DeliveryService ───────────────────────────────────────────────────────


@dataclass
class DeliveryResult:
    """Returned by :meth:`DeliveryService.prepare_download`."""

    download_url: str
    version: str
    content_hash: str
    expires_at: datetime
    body_bytes: bytes  # for ``format=raw``
    delivery_key: str


class DeliveryService:
    """Coordinator for the watermark + presigned-URL flow."""

    def __init__(self) -> None:
        # Lazily resolved on every call so tests can swap the storage
        # backend after the service singleton was constructed.
        pass

    @property
    def storage(self) -> Any:  # noqa: ANN401 — duck-typed S3 vs InMemory
        return get_storage()

    async def prepare_download(
        self,
        session: "AsyncSession",
        *,
        license_obj: License,
        explicit_version: str | None = None,
        user_agent: str | None = None,
        client_ip: str | None = None,
    ) -> DeliveryResult | None:
        if explicit_version:
            version = await resolve_explicit_version(
                session, license_obj, explicit_version
            )
        else:
            version = await entitled_version(session, license_obj)

        if version is None:
            return None

        canonical_bytes = await self.storage.get_object(version.storage_url)
        canonical_body = canonical_bytes.decode("utf-8")

        payload, _comment, content_hash = build_delivery_payload(
            canonical_body,
            license_id=license_obj.id,
            buyer_id=license_obj.buyer_id,
        )

        # Random suffix prevents URL guessability and keeps two downloads
        # from colliding when timestamps line up to the second.
        nonce = secrets.token_urlsafe(12)
        delivery_key = f"delivery/{license_obj.id}/{nonce}.md"
        await self.storage.put_object(delivery_key, payload, "text/markdown")

        download_url = await self.storage.presigned_url(
            delivery_key, expires_in_seconds=DOWNLOAD_URL_TTL_SECONDS
        )

        # Audit log entry. Caller is responsible for committing the session
        # — keep this side effect inside the request transaction so a
        # failure mid-flight doesn't drop the audit record.
        await write_audit(
            session,
            actor_id=license_obj.buyer_id,
            action="license.downloaded",
            target_type="license",
            target_id=license_obj.id,
            metadata={
                "skill_id": str(license_obj.skill_id),
                "version": version.version,
                "user_agent_hash": hash_ua(user_agent),
                "ip_hash": hash_ip(client_ip),
            },
        )

        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=DOWNLOAD_URL_TTL_SECONDS
        )
        return DeliveryResult(
            download_url=download_url,
            version=version.version,
            content_hash=content_hash,
            expires_at=expires_at,
            body_bytes=payload,
            delivery_key=delivery_key,
        )


_singleton: DeliveryService | None = None


def get_delivery_service() -> DeliveryService:
    global _singleton
    if _singleton is None:
        _singleton = DeliveryService()
    return _singleton


def reset_delivery_service() -> None:
    """Test helper — drops the cached singleton."""
    global _singleton
    _singleton = None


# ── License + skill summary for library list/detail ──────────────────────


async def get_license_for_user(
    session: "AsyncSession", license_id: uuid.UUID, user_id: uuid.UUID
) -> License | None:
    """Fetch a license iff the requester is the owner. Hide existence otherwise."""
    res = await session.execute(
        select(License).where(
            License.id == license_id, License.buyer_id == user_id
        )
    )
    return res.scalar_one_or_none()


__all__ = [
    "GRACE",
    "DeliveryResult",
    "DeliveryService",
    "entitled_version",
    "get_delivery_service",
    "get_license_for_user",
    "reset_delivery_service",
    "resolve_explicit_version",
]
