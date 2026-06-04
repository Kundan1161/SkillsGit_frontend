"""Seed the database with demo skills, creators, and a buyer.

Run with::

    uv run python -m scripts.seed_skills

Idempotent: deletes the prior seed rows (by email/handle) and re-creates.
A and B depend on this data — see ``prompts/marketplace/04-licensing-and-delivery.md``
acceptance section.

What this produces:

- 3 seed creators: ``janedoe`` (finance, verified), ``marcoart`` (design,
  verified), ``samdata`` (data, not verified).
- 6 published skills across categories (see ``scripts/seed_data/*.skills.md``).
- 1 admin user (``admin@example.com``).
- 1 buyer user (``buyer@example.com``) with a granted license to
  ``janedoe/dcf-valuation-pro`` so download flows can be demoed.
"""

from __future__ import annotations

import asyncio
import logging
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from passlib.context import CryptContext
from sqlalchemy import delete, select

from src.billing.models import (
    License,
    LicenseSource,
    LicenseStatus,
    Order,
    OrderItem,
    OrderStatus,
    SupportTier,
)
from src.core.db import SessionLocal, write_audit
from src.delivery.watermark import compute_content_hash, inject_distribution_block
from src.skills.models import PricingModel, Skill, SkillStatus, SkillVersion
from src.skills.parser import split_frontmatter
from src.skills.validator import validate_file
from src.storage.s3 import get_storage
from src.users.models import CreatorProfile, User, UserRole

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO, format="%(levelname)s seed: %(message)s")
log = logging.getLogger("seed_skills")

SEED_DIR = Path(__file__).parent / "seed_data"

pwd = CryptContext(schemes=["argon2"], deprecated="auto")
SEED_PASSWORD = "Seed-password-1234"

# (file, pricing_model, one_time_cents, total_sales, rating_avg, rating_count)
SKILL_SEEDS: list[tuple[str, PricingModel, int | None, int, float, int]] = [
    ("janedoe-dcf-valuation-pro.skills.md", PricingModel.ONE_TIME, 1900, 412, 4.8, 67),
    ("janedoe-lbo-modeling.skills.md", PricingModel.ONE_TIME, 2900, 188, 4.6, 32),
    ("marcoart-design-critique-rubric.skills.md", PricingModel.ONE_TIME, 900, 503, 4.9, 84),
    ("marcoart-brand-system-builder.skills.md", PricingModel.FREE, None, 821, 4.4, 55),
    ("samdata-schema-architect.skills.md", PricingModel.ONE_TIME, 3900, 96, 4.7, 22),
    ("samdata-etl-pipeline-design.skills.md", PricingModel.ONE_TIME, 2400, 64, 4.2, 14),
]

CREATORS: list[dict[str, object]] = [
    {
        "email": "janedoe@example.com",
        "handle": "janedoe",
        "display_name": "Jane Doe",
        "bio": "20 years on Wall Street; now teaching the modelling I wish I'd had in year one.",
        "industries": ["finance", "investing"],
        "payout_country": "US",
        "is_creator_verified": True,
        "stripe_connect_account_id": "acct_seed_janedoe",
    },
    {
        "email": "marcoart@example.com",
        "handle": "marcoart",
        "display_name": "Marco Art",
        "bio": "Design systems for fintechs and design-first SaaS.",
        "industries": ["design", "branding"],
        "payout_country": "IT",
        "is_creator_verified": True,
        "stripe_connect_account_id": "acct_seed_marcoart",
    },
    {
        "email": "samdata@example.com",
        "handle": "samdata",
        "display_name": "Sam Data",
        "bio": "Data engineer; building pipelines since the Hadoop era.",
        "industries": ["data", "engineering"],
        "payout_country": "GB",
        "is_creator_verified": False,
        "stripe_connect_account_id": None,
    },
]

SEED_EMAILS = {c["email"] for c in CREATORS} | {
    "admin@example.com",
    "buyer@example.com",
}


# ── Helpers ───────────────────────────────────────────────────────────


async def _purge_existing(session: "AsyncSession") -> None:
    """Best-effort cleanup so re-runs are idempotent."""
    res = await session.execute(
        select(User).where(User.email.in_(list(SEED_EMAILS)))
    )
    users = list(res.scalars().all())
    for u in users:
        # Skills.cascade deletes versions.
        sk = await session.execute(select(Skill).where(Skill.creator_id == u.id))
        for skill in sk.scalars().all():
            # Drop FK from skill -> latest_version_id first to break the cycle.
            skill.latest_version_id = None
        await session.flush()
        for skill in sk.scalars().all():  # iterator already consumed; harmless no-op
            pass

    # Delete licenses + orders for buyer/users in scope.
    for u in users:
        await session.execute(delete(License).where(License.buyer_id == u.id))
        await session.execute(delete(OrderItem).where(OrderItem.creator_id == u.id))
        await session.execute(delete(Order).where(Order.buyer_id == u.id))

    # Delete skills by creator_id.
    for u in users:
        await session.execute(delete(Skill).where(Skill.creator_id == u.id))

    # Delete creator profiles + users.
    for u in users:
        await session.execute(
            delete(CreatorProfile).where(CreatorProfile.user_id == u.id)
        )
    await session.execute(delete(User).where(User.email.in_(list(SEED_EMAILS))))
    await session.flush()


async def _create_user(
    session: "AsyncSession",
    *,
    email: str,
    display_name: str,
    role: UserRole = UserRole.BUYER,
    is_admin: bool = False,
    is_creator_verified: bool = False,
    stripe_connect_account_id: str | None = None,
) -> User:
    user = User(
        email=email,
        hashed_password=pwd.hash(SEED_PASSWORD),
        display_name=display_name,
        role=role,
        is_active=True,
        is_verified=True,
        is_admin=is_admin,
        is_creator_verified=is_creator_verified,
        stripe_connect_account_id=stripe_connect_account_id,
    )
    session.add(user)
    await session.flush()
    return user


async def _create_creator(session: "AsyncSession", data: dict[str, object]) -> User:
    user = await _create_user(
        session,
        email=str(data["email"]),
        display_name=str(data["display_name"]),
        role=UserRole.CREATOR,
        is_creator_verified=bool(data["is_creator_verified"]),
        stripe_connect_account_id=(
            str(data["stripe_connect_account_id"])
            if data["stripe_connect_account_id"]
            else None
        ),
    )
    profile = CreatorProfile(
        user_id=user.id,
        handle=str(data["handle"]),
        bio=str(data["bio"]),
        industries=list(data["industries"]),  # type: ignore[arg-type]
        payout_country=str(data["payout_country"]),
    )
    session.add(profile)
    await session.flush()
    return user


async def _upload_and_create_skill(
    session: "AsyncSession",
    *,
    creator: User,
    handle: str,
    file_path: Path,
    pricing_model: PricingModel,
    one_time_price_cents: int | None,
    total_sales: int,
    rating_avg: float,
    rating_count: int,
) -> tuple[Skill, SkillVersion]:
    raw = file_path.read_bytes()

    result = validate_file(raw)
    if not result.is_valid:
        raise RuntimeError(
            f"Seed file {file_path.name} failed validation: {result.errors}"
        )

    fm, _body = split_frontmatter(raw)
    creator_handle, slug = str(fm["id"]).split("/", 1)
    assert creator_handle == handle, f"handle mismatch in {file_path.name}"
    version_str = str(fm["version"])

    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=str(fm["name"]),
        tagline=str(fm["description"])[:140],
        description_md=str(fm["description"]),
        category=str(fm.get("category") or "other"),
        tags=list(fm.get("tags") or []),
        status=SkillStatus.PUBLISHED,
        pricing_model=pricing_model,
        one_time_price_cents=one_time_price_cents,
        total_sales=total_sales,
        rating_avg=rating_avg,
        rating_count=rating_count,
        support_url=f"https://example.com/{handle}/support",
    )
    session.add(skill)
    await session.flush()

    storage = get_storage()
    storage_key = f"skills/{skill.id}/{version_str}.md"
    stamped = inject_distribution_block(raw.decode("utf-8"))
    await storage.put_object(storage_key, stamped.encode("utf-8"), "text/markdown")

    version = SkillVersion(
        skill_id=skill.id,
        version=version_str,
        content_hash=compute_content_hash(raw.decode("utf-8")),
        storage_url=storage_key,
        ai_requirements=dict(fm.get("ai") or {}),
        changelog_md=None,
        released_at=datetime.now(timezone.utc) - timedelta(days=random.randint(7, 60)),
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
        metadata={"version": version_str, "seed": True},
    )
    return skill, version


# ── Main entry ────────────────────────────────────────────────────────


async def run() -> None:
    await get_storage().ensure_bucket()

    async with SessionLocal() as session:
        await _purge_existing(session)

        # Admin + buyer.
        admin = await _create_user(
            session,
            email="admin@example.com",
            display_name="Skills Admin",
            role=UserRole.ADMIN,
            is_admin=True,
        )
        buyer = await _create_user(
            session,
            email="buyer@example.com",
            display_name="Test Buyer",
            role=UserRole.BUYER,
        )

        # Creators by handle.
        creators_by_handle: dict[str, User] = {}
        for data in CREATORS:
            cu = await _create_creator(session, data)
            creators_by_handle[str(data["handle"])] = cu

        # Skills.
        first_skill_for_buyer: Skill | None = None
        first_version_for_buyer: SkillVersion | None = None
        for filename, pm, price, sales, rating, rcount in SKILL_SEEDS:
            handle = filename.split("-", 1)[0]
            file_path = SEED_DIR / filename
            skill, version = await _upload_and_create_skill(
                session,
                creator=creators_by_handle[handle],
                handle=handle,
                file_path=file_path,
                pricing_model=pm,
                one_time_price_cents=price,
                total_sales=sales,
                rating_avg=rating,
                rating_count=rcount,
            )
            log.info(
                "created %s/%s (%s) %s sales", handle, skill.slug, version.version, sales
            )
            if first_skill_for_buyer is None and pm == PricingModel.ONE_TIME:
                first_skill_for_buyer = skill
                first_version_for_buyer = version

        # Grant the buyer one license against the first one_time skill so the
        # download path is demoable end-to-end.
        if first_skill_for_buyer is not None and first_version_for_buyer is not None:
            order = Order(
                buyer_id=buyer.id,
                subtotal_cents=first_skill_for_buyer.one_time_price_cents or 0,
                platform_fee_cents=int(
                    (first_skill_for_buyer.one_time_price_cents or 0) * 0.2
                ),
                creator_payout_cents=int(
                    (first_skill_for_buyer.one_time_price_cents or 0) * 0.8
                ),
                status=OrderStatus.PAID,
                placed_at=datetime.now(timezone.utc),
            )
            session.add(order)
            await session.flush()

            item = OrderItem(
                order_id=order.id,
                skill_id=first_skill_for_buyer.id,
                skill_version_id=first_version_for_buyer.id,
                creator_id=first_skill_for_buyer.creator_id,
                price_cents=first_skill_for_buyer.one_time_price_cents or 0,
                platform_fee_cents=int(
                    (first_skill_for_buyer.one_time_price_cents or 0) * 0.2
                ),
            )
            session.add(item)
            await session.flush()

            lic = License(
                buyer_id=buyer.id,
                skill_id=first_skill_for_buyer.id,
                source=LicenseSource.ONE_TIME,
                source_id=item.id,
                granted_at=datetime.now(timezone.utc),
                max_version=f"{first_version_for_buyer.version.split('.')[0]}.x",
                support_tier=SupportTier.NONE,
                status=LicenseStatus.ACTIVE,
            )
            session.add(lic)
            await write_audit(
                session,
                actor_id=admin.id,
                action="license.granted",
                target_type="license",
                target_id=lic.id,
                metadata={
                    "skill_id": str(first_skill_for_buyer.id),
                    "source": "seed",
                },
            )

        await session.commit()
        log.info("seed complete")
        log.info("  admin login: admin@example.com / %s", SEED_PASSWORD)
        log.info("  buyer login: buyer@example.com / %s", SEED_PASSWORD)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
