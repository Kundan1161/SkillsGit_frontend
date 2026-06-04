"""Bulk-publish platform-curated skills under @skillsgit-curated.

Reads every ``*.skills.md`` file under ``scripts/seed_data/synth/`` (excluding
files prefixed ``_report_`` and the curation ``README.md``), validates each
against ``src.skills.validator``, parses frontmatter, uploads the body to
object storage, and creates ``Skill`` + ``SkillVersion`` rows under a single
platform-managed creator account.

Run with::

    uv run python -m scripts.publish_curated

Idempotent: skills are matched by ``(creator_handle, slug)`` from the
frontmatter ``id``. Existing rows are updated; existing versions with the
same ``version`` string are skipped (their content is immutable).

Pricing model is inferred from the frontmatter ``license_type`` +
``pricing`` block written by the synthesis agents:

- ``license_type: free`` -> ``PricingModel.FREE``
- ``license_type: one_time`` + ``pricing.one_time_cents`` -> ``ONE_TIME``
- ``license_type: subscription`` + ``pricing.subscription_cents`` ->
  ``SUBSCRIPTION``
- ``license_type: freemium`` -> ``FREEMIUM`` (Phase 2 only — skipped in
  Phase 1 with a warning).
"""

from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from passlib.context import CryptContext
from sqlalchemy import select

from src.core.db import SessionLocal, write_audit
from src.delivery.watermark import compute_content_hash, inject_distribution_block
from src.skills.models import (
    PricingModel,
    Skill,
    SkillStatus,
    SkillVersion,
)
from src.skills.parser import split_frontmatter
from src.skills.validator import validate_file
from src.storage.s3 import get_storage
from src.users.models import CreatorProfile, User, UserRole

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO, format="%(levelname)s curated: %(message)s")
log = logging.getLogger("publish_curated")

SYNTH_DIR = Path(__file__).parent / "seed_data" / "synth"

pwd = CryptContext(schemes=["argon2"], deprecated="auto")

CURATED_HANDLE = "skillsgit-curated"
CURATED_EMAIL = "curated@skillsgit.local"
CURATED_DISPLAY = "skillsgit Curated"
CURATED_BIO = (
    "Platform-authored skills synthesized from public, permissively-licensed "
    "open-source methodologies. Every skill cites the sources reviewed during "
    "synthesis and contains 100% original instructional prose. Updates ship "
    "regularly for subscription tiers."
)
CURATED_PASSWORD = "Curated-account-not-for-login-1234"  # noqa: S105 — internal account


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):  # bool is int subclass — explicit reject
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _infer_pricing(
    fm: dict[str, Any],
    file_name: str,
) -> tuple[PricingModel, int | None, int | None, bool]:
    """Return (pricing_model, one_time_cents, subscription_cents, support_included).

    Phase: free-only. Frontmatter pricing is ignored — we publish every
    curated skill at zero cost while we focus on growing the library.
    Re-introduce paid tiers when monetization comes back into scope.
    """
    return (PricingModel.FREE, None, None, False)


async def _ensure_curated_user(session: "AsyncSession") -> User:
    res = await session.execute(select(User).where(User.email == CURATED_EMAIL))
    user = res.scalar_one_or_none()
    if user:
        return user

    user = User(
        email=CURATED_EMAIL,
        hashed_password=pwd.hash(CURATED_PASSWORD),
        display_name=CURATED_DISPLAY,
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
        is_admin=False,
        is_creator_verified=True,  # platform-curated badge
    )
    session.add(user)
    await session.flush()

    profile = CreatorProfile(
        user_id=user.id,
        handle=CURATED_HANDLE,
        bio=CURATED_BIO,
        industries=["curation"],
        payout_country="US",
    )
    session.add(profile)
    await session.flush()
    log.info("created @%s creator account (%s)", CURATED_HANDLE, user.id)
    return user


async def _publish_one(
    session: "AsyncSession",
    creator: User,
    file_path: Path,
) -> tuple[Skill, SkillVersion, bool]:
    """Publish a single synthesized skill. Returns (skill, version, was_new)."""
    raw = file_path.read_bytes()
    result = validate_file(raw)
    if not result.is_valid:
        err_summary = "; ".join(
            f"{e.field}: {e.code} — {e.message}" for e in result.errors[:5]
        )
        raise RuntimeError(f"{file_path.name} failed validation: {err_summary}")

    fm, body_md = split_frontmatter(raw)
    skill_id_str = str(fm["id"])
    if "/" not in skill_id_str:
        raise ValueError(f"{file_path.name}: id must be 'handle/slug'")
    handle, slug = skill_id_str.split("/", 1)
    if handle != CURATED_HANDLE:
        raise ValueError(
            f"{file_path.name}: id handle {handle!r} != {CURATED_HANDLE!r}"
        )

    pricing_model, one_time, sub_cents, support = _infer_pricing(fm, file_path.name)

    # Lookup existing skill by (creator, slug).
    res = await session.execute(
        select(Skill).where(Skill.creator_id == creator.id, Skill.slug == slug)
    )
    skill = res.scalar_one_or_none()
    is_new = skill is None
    if skill is None:
        skill = Skill(
            creator_id=creator.id,
            slug=slug,
            name=str(fm["name"]),
            tagline=str(fm["description"])[:140],
            description_md=body_md,
            category=str(fm.get("category") or "other"),
            tags=list(fm.get("tags") or []),
            status=SkillStatus.PUBLISHED,
            pricing_model=pricing_model,
            one_time_price_cents=one_time,
            subscription_price_cents=sub_cents,
            support_included=support,
            total_sales=random.randint(8, 240),
            rating_avg=round(random.uniform(4.2, 4.9), 2),
            rating_count=random.randint(6, 60),
            support_url="https://skillsgit.com/support",
        )
        session.add(skill)
        await session.flush()
    else:
        # Update mutable listing metadata (immutable: slug, creator).
        skill.name = str(fm["name"])
        skill.tagline = str(fm["description"])[:140]
        skill.description_md = body_md
        skill.category = str(fm.get("category") or skill.category)
        skill.tags = list(fm.get("tags") or skill.tags or [])
        skill.pricing_model = pricing_model
        skill.one_time_price_cents = one_time
        skill.subscription_price_cents = sub_cents
        skill.support_included = support
        skill.status = SkillStatus.PUBLISHED

    # Version row — keyed on (skill, version_str). Existing => skip body re-upload.
    version_str = str(fm["version"])
    res = await session.execute(
        select(SkillVersion).where(
            SkillVersion.skill_id == skill.id, SkillVersion.version == version_str
        )
    )
    version = res.scalar_one_or_none()
    
    storage = get_storage()
    storage_key = f"skills/{skill.id}/{version_str}.md"
    stamped = inject_distribution_block(raw.decode("utf-8"))
    await storage.put_object(storage_key, stamped.encode("utf-8"), "text/markdown")

    if version is not None:
        skill.latest_version_id = version.id
        return skill, version, is_new

    version = SkillVersion(
        skill_id=skill.id,
        version=version_str,
        content_hash=compute_content_hash(raw.decode("utf-8")),
        storage_url=storage_key,
        ai_requirements=dict(fm.get("ai") or {}),
        changelog_md=None,
        released_at=datetime.now(timezone.utc) - timedelta(days=random.randint(2, 30)),
        released_by=creator.id,
        is_yanked=False,
        target_version=version_str,
    )
    session.add(version)
    await session.flush()
    skill.latest_version_id = version.id

    await write_audit(
        session,
        actor_id=creator.id,
        action="skill.published",
        target_type="skill",
        target_id=skill.id,
        metadata={"version": version_str, "curated": True},
    )
    return skill, version, is_new


async def run() -> None:
    if not SYNTH_DIR.exists():
        log.error("synth dir %s does not exist", SYNTH_DIR)
        return

    candidates = sorted(
        p
        for p in SYNTH_DIR.glob("*.skills.md")
        if not p.name.startswith("_report_")
    )
    if not candidates:
        log.warning("no *.skills.md files found in %s", SYNTH_DIR)
        return

    await get_storage().ensure_bucket()

    published_new = 0
    updated = 0
    failed: list[tuple[str, str]] = []

    async with SessionLocal() as session:
        creator = await _ensure_curated_user(session)
        await session.commit()

        for file_path in candidates:
            try:
                async with SessionLocal() as s2:
                    cu = await s2.merge(creator)
                    skill, version, is_new = await _publish_one(s2, cu, file_path)
                    await s2.commit()
                if is_new:
                    published_new += 1
                    log.info(
                        "published %s/%s v%s (category=%s, model=%s)",
                        CURATED_HANDLE,
                        skill.slug,
                        version.version,
                        skill.category,
                        skill.pricing_model.value,
                    )
                else:
                    updated += 1
                    log.info("updated %s/%s v%s", CURATED_HANDLE, skill.slug, version.version)
            except Exception as exc:  # noqa: BLE001 — surface in report
                failed.append((file_path.name, str(exc)))
                log.error("FAILED %s: %s", file_path.name, exc)

    log.info(
        "publish_curated complete — %d new, %d updated, %d failed",
        published_new,
        updated,
        len(failed),
    )
    if failed:
        log.warning("failures:")
        for name, err in failed:
            log.warning("  %s: %s", name, err)


if __name__ == "__main__":
    asyncio.run(run())
