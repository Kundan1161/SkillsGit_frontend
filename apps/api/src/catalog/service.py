"""Catalog query layer.

Centralises the SQL builders for the list endpoints so the router stays
thin. Search uses Postgres full-text on prod and a simple ILIKE fallback on
sqlite (tests) — see ``_apply_search`` below.

Spec: ``prompts/marketplace/01-discovery.md`` and
``prompts/marketplace/02-skill-detail.md``.
"""

from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import (
    Select,
    String,
    case,
    cast,
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.models import EditorialPick
from src.catalog.schemas import (
    AiRequirements,
    CatalogSort,
    CategoryItem,
    CreatorChipPublic,
    LatestVersionInfo,
    SkillCardItem,
    SkillDetail,
    SkillPricing,
    SkillStats,
    VersionItem,
)
from src.core.pagination import PageInfo, clamp_limit, decode_cursor, encode_cursor
from src.skills.models import Category, Skill, SkillStatus, SkillVersion
from src.skills.parser import split_frontmatter
from src.storage.s3 import get_storage
from src.users.models import CreatorProfile, User

# ── In-memory TTL cache for read-heavy endpoints ─────────────────────


@dataclass
class _Cache:
    value: Any
    expires_at: float


_cache: dict[str, _Cache] = {}


def _cache_get(key: str) -> Any | None:
    entry = _cache.get(key)
    if entry is None:
        return None
    if entry.expires_at < time.monotonic():
        _cache.pop(key, None)
        return None
    return entry.value


def _cache_set(key: str, value: Any, ttl_seconds: float) -> None:
    _cache[key] = _Cache(value=value, expires_at=time.monotonic() + ttl_seconds)


# ── Helpers ──────────────────────────────────────────────────────────


def _csv_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _array_contains_any(column: Any, values: list[str], dialect_name: str) -> Any:
    """Cross-dialect ARRAY/json contains-any check.

    Postgres uses the ``&&`` overlap operator; sqlite stores arrays as JSON
    blobs so we fall back to a substring LIKE per value (good enough for tests).
    """
    if dialect_name == "postgresql":
        # ``column.overlap(values)`` would require typed ARRAY; we hand-roll
        # the operator to keep this dialect-agnostic. ``literal()`` boxes the
        # Python list so SQLAlchemy / mypy accept it as a clause element.
        from sqlalchemy import literal

        return column.op("&&")(literal(values))
    # sqlite: JSON list — naïve LIKE per value, OR-combined.
    if not values:
        return func.lower("1") == "0"  # always-false sentinel
    text_col = cast(column, String)
    clauses = [text_col.ilike(f'%"{v}"%') for v in values]
    return or_(*clauses)


def _apply_search(stmt: Select[Any], q: str, dialect_name: str) -> Select[Any]:
    """Attach search filter + relevance order. Returns the augmented stmt."""
    q_norm = q.strip()
    if not q_norm:
        return stmt
    if dialect_name == "postgresql":
        # websearch_to_tsquery is forgiving — accepts quoted phrases, OR, etc.
        # Combine FTS relevance with trigram similarity for typo tolerance,
        # then add a logarithmic popularity boost (see 01-discovery.md §Search).
        tsv = func.to_tsvector(
            "english",
            func.coalesce(Skill.name, "")
            + " "
            + func.coalesce(Skill.tagline, "")
            + " "
            + func.coalesce(Skill.description_md, ""),
        )
        tsq = func.websearch_to_tsquery("english", q_norm)
        rank = func.ts_rank_cd(tsv, tsq)
        sim = func.similarity(Skill.name, q_norm)
        popularity = 0.1 * func.ln(1 + Skill.total_sales)
        score = (rank * 0.7) + (sim * 0.3) + popularity
        stmt = stmt.where(or_(tsv.op("@@")(tsq), sim > 0.3))
        return stmt.order_by(score.desc(), Skill.id.desc())
    # sqlite / generic fallback: ILIKE across name + tagline + description.
    needle = f"%{q_norm}%"
    stmt = stmt.where(
        or_(
            Skill.name.ilike(needle),
            Skill.tagline.ilike(needle),
            Skill.description_md.ilike(needle),
        )
    )
    # Best-effort relevance: name match first, then tagline.
    score = case(
        (Skill.name.ilike(needle), 3),
        (Skill.tagline.ilike(needle), 2),
        else_=1,
    ) + (Skill.total_sales / 1000.0)
    return stmt.order_by(score.desc(), Skill.id.desc())


def _apply_sort(stmt: Select[Any], sort: CatalogSort, dialect_name: str) -> Select[Any]:
    if sort == CatalogSort.NEWEST:
        return stmt.order_by(SkillVersion.released_at.desc().nulls_last(), Skill.id.desc())
    if sort == CatalogSort.TOP_RATED:
        return stmt.where(Skill.rating_count >= 5).order_by(
            Skill.rating_avg.desc().nulls_last(), Skill.id.desc()
        )
    if sort == CatalogSort.MOST_SOLD:
        return stmt.order_by(Skill.total_sales.desc(), Skill.id.desc())
    if sort == CatalogSort.PRICE_ASC:
        # Coalesce free → 0 so freebies sort first.
        price = func.coalesce(Skill.one_time_price_cents, Skill.subscription_price_cents, 0)
        return stmt.order_by(price.asc(), Skill.id.desc())
    if sort == CatalogSort.PRICE_DESC:
        price = func.coalesce(Skill.one_time_price_cents, Skill.subscription_price_cents, 0)
        return stmt.order_by(price.desc(), Skill.id.desc())
    # RELEVANCE is handled inside _apply_search; if no q is set fall through
    # to a stable id-desc order so cursor pagination is well-defined.
    return stmt.order_by(Skill.id.desc())


# ── Public list query ────────────────────────────────────────────────


@dataclass
class CatalogFilters:
    q: str | None = None
    categories: list[str] | None = None
    pricing_models: list[str] | None = None
    min_price_cents: int | None = None
    max_price_cents: int | None = None
    required_models: list[str] | None = None
    tags: list[str] | None = None
    min_rating: float | None = None
    creator_handle: str | None = None
    creator_id: uuid.UUID | None = None
    sort: CatalogSort = CatalogSort.RELEVANCE
    limit: int | None = None
    cursor: str | None = None


async def list_skills(
    session: AsyncSession, filters: CatalogFilters
) -> tuple[list[SkillCardItem], PageInfo]:
    """Run the workhorse catalog query and return card items + page info."""
    dialect_name = session.bind.dialect.name if session.bind is not None else "postgresql"

    # We join SkillVersion (latest) + User (creator) + CreatorProfile (handle).
    # ``isouter`` so skills without a published version (edge) still flow.
    stmt: Select[Any] = (
        select(
            Skill,
            SkillVersion,
            User,
            CreatorProfile,
        )
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .join(SkillVersion, SkillVersion.id == Skill.latest_version_id, isouter=True)
        .where(Skill.status == SkillStatus.PUBLISHED)
    )

    if filters.categories:
        stmt = stmt.where(Skill.category.in_(filters.categories))
    if filters.pricing_models:
        stmt = stmt.where(Skill.pricing_model.in_(filters.pricing_models))
    if filters.min_price_cents is not None:
        stmt = stmt.where(
            func.coalesce(
                Skill.one_time_price_cents, Skill.subscription_price_cents, 0
            )
            >= filters.min_price_cents
        )
    if filters.max_price_cents is not None:
        stmt = stmt.where(
            func.coalesce(
                Skill.one_time_price_cents, Skill.subscription_price_cents, 0
            )
            <= filters.max_price_cents
        )
    if filters.min_rating is not None:
        stmt = stmt.where(Skill.rating_avg >= filters.min_rating)
    if filters.creator_id is not None:
        stmt = stmt.where(Skill.creator_id == filters.creator_id)
    if filters.creator_handle:
        stmt = stmt.where(CreatorProfile.handle == filters.creator_handle)
    if filters.tags:
        stmt = stmt.where(_array_contains_any(Skill.tags, filters.tags, dialect_name))
    if filters.required_models:
        # ai_requirements is JSONB on the *version* row. Use a JSON path query
        # on postgres; on sqlite degrade to a textual contains check.
        if dialect_name == "postgresql":
            from sqlalchemy import literal as _literal

            stmt = stmt.where(
                SkillVersion.ai_requirements["required_models"].op("?|")(
                    _literal(filters.required_models)
                )
            )
        else:
            text_col = cast(SkillVersion.ai_requirements, String)
            stmt = stmt.where(
                or_(*[text_col.ilike(f'%"{m}"%') for m in filters.required_models])
            )

    # Ordering — search-first if q is set; otherwise the requested sort.
    if filters.q and filters.sort == CatalogSort.RELEVANCE:
        stmt = _apply_search(stmt, filters.q, dialect_name)
    elif filters.q:
        # Search filter still applies, but order takes the explicit sort.
        # Apply text predicate without the relevance order:
        q_norm = filters.q.strip()
        needle = f"%{q_norm}%"
        if dialect_name == "postgresql":
            tsv = func.to_tsvector(
                "english",
                func.coalesce(Skill.name, "")
                + " "
                + func.coalesce(Skill.tagline, "")
                + " "
                + func.coalesce(Skill.description_md, ""),
            )
            tsq = func.websearch_to_tsquery("english", q_norm)
            stmt = stmt.where(
                or_(
                    tsv.op("@@")(tsq),
                    func.similarity(Skill.name, q_norm) > 0.3,
                )
            )
        else:
            stmt = stmt.where(
                or_(
                    Skill.name.ilike(needle),
                    Skill.tagline.ilike(needle),
                    Skill.description_md.ilike(needle),
                )
            )
        stmt = _apply_sort(stmt, filters.sort, dialect_name)
    else:
        stmt = _apply_sort(stmt, filters.sort, dialect_name)

    real_limit = clamp_limit(filters.limit)

    # Cursor — keyset by Skill.id (uuid7 is time-sortable so id-desc gives a
    # stable, well-defined "next" relative to whichever sort we picked).
    if filters.cursor:
        payload = decode_cursor(filters.cursor)
        last_id = payload.get("id")
        if last_id:
            stmt = stmt.where(cast(Skill.id, String) < str(last_id))

    fetched = await session.execute(stmt.limit(real_limit + 1))
    rows = list(fetched.unique().all())
    has_more = len(rows) > real_limit
    if has_more:
        rows = rows[:real_limit]

    items = [
        _row_to_card(skill, version, user, profile) for (skill, version, user, profile) in rows
    ]

    next_cursor: str | None = None
    if has_more and rows:
        last_skill = rows[-1][0]
        next_cursor = encode_cursor(last_id=str(last_skill.id))

    return items, PageInfo(
        next_cursor=next_cursor, has_more=has_more, limit=real_limit
    )


def _row_to_card(
    skill: Skill,
    version: SkillVersion | None,
    user: User,
    profile: CreatorProfile | None,
) -> SkillCardItem:
    desc_snippet = None
    if skill.description_md:
        import re
        clean_text = re.sub(r'#+\s*', '', skill.description_md)
        clean_text = clean_text.replace('\n', ' ').strip()
        desc_snippet = clean_text[:120] + ('...' if len(clean_text) > 120 else '')

    return SkillCardItem(
        id=skill.id,
        slug=skill.slug,
        name=skill.name,
        tagline=skill.tagline,
        cover_image_url=skill.cover_image_url,
        category=skill.category,
        description_snippet=desc_snippet,
        tags=list(skill.tags or []),
        pricing_model=(
            skill.pricing_model.value
            if hasattr(skill.pricing_model, "value")
            else str(skill.pricing_model)
        ),
        one_time_price_cents=skill.one_time_price_cents,
        subscription_price_cents=skill.subscription_price_cents,
        rating_avg=float(skill.rating_avg) if skill.rating_avg is not None else None,
        rating_count=skill.rating_count,
        total_sales=skill.total_sales,
        creator=CreatorChipPublic(
            handle=profile.handle if profile is not None else (user.display_name or "anon"),
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            is_verified=user.is_creator_verified,
        ),
        latest_version=version.version if version is not None else None,
        released_at=version.released_at if version is not None else None,
    )


# ── Categories ───────────────────────────────────────────────────────


async def list_categories(session: AsyncSession) -> list[CategoryItem]:
    cached = _cache_get("categories")
    if cached is not None:
        return list(cached)

    # Count published skills per category in one pass.
    counts_stmt = (
        select(Skill.category, func.count(Skill.id))
        .where(Skill.status == SkillStatus.PUBLISHED)
        .group_by(Skill.category)
    )
    counts_rows = await session.execute(counts_stmt)
    counts: dict[str | None, int] = {row[0]: int(row[1]) for row in counts_rows}

    cats_stmt = select(Category).order_by(Category.display_order, Category.slug)
    res = await session.execute(cats_stmt)
    categories = list(res.scalars().all())

    items = [
        CategoryItem(
            slug=c.slug,
            name=c.name,
            description=c.description,
            parent_slug=c.parent_slug,
            display_order=c.display_order,
            skill_count=counts.get(c.slug, 0),
        )
        for c in categories
    ]
    _cache_set("categories", items, ttl_seconds=60.0)
    return items


# ── Featured ─────────────────────────────────────────────────────────


async def list_featured(session: AsyncSession) -> list[tuple[EditorialPick, SkillCardItem]]:
    """Active editorial picks joined with their skill card data."""
    now = datetime.now(UTC)
    stmt = (
        select(EditorialPick, Skill, SkillVersion, User, CreatorProfile)
        .join(Skill, Skill.id == EditorialPick.skill_id)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
        .join(SkillVersion, SkillVersion.id == Skill.latest_version_id, isouter=True)
        .where(Skill.status == SkillStatus.PUBLISHED)
        .where(
            or_(EditorialPick.starts_at.is_(None), EditorialPick.starts_at <= now)
        )
        .where(or_(EditorialPick.ends_at.is_(None), EditorialPick.ends_at >= now))
        .order_by(EditorialPick.sort_order.asc(), EditorialPick.created_at.desc())
    )
    res = await session.execute(stmt)
    out: list[tuple[EditorialPick, SkillCardItem]] = []
    for pick, skill, version, user, profile in res.all():
        out.append((pick, _row_to_card(skill, version, user, profile)))
    return out


# ── Skill detail ─────────────────────────────────────────────────────


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
_URL_RE = re.compile(r"https?://[^\s<>()\]]+")
_GIT_HOSTS = frozenset(
    {"github.com", "www.github.com", "gitlab.com", "www.gitlab.com"}
)


def _extract_section(body_md: str, *, heading_prefix: str) -> str:
    """Return the body of the first heading matching ``heading_prefix``."""
    lines = body_md.splitlines(keepends=False)
    out: list[str] = []
    capture_level: int | None = None

    for line in lines:
        match = _HEADING_RE.match(line)
        if match:
            level = len(match.group(1))
            heading = match.group(2).strip().lower()
            if capture_level is not None and level <= capture_level:
                break
            if capture_level is None and heading.startswith(heading_prefix):
                capture_level = level
                continue
        if capture_level is not None:
            out.append(line)

    return "\n".join(out).strip()


def extract_inspired_by_urls(body_md: str | None) -> list[str]:
    """Extract Git-hosted source URLs from the ``Sources reviewed`` section."""
    if not body_md:
        return []

    sources_section = _extract_section(body_md, heading_prefix="sources reviewed")
    if not sources_section:
        return []

    seen: set[str] = set()
    urls: list[str] = []
    for match in _URL_RE.findall(sources_section):
        url = match.rstrip(".,)")
        hostname = urlparse(url).netloc.lower()
        if hostname not in _GIT_HOSTS:
            continue
        canonical = url.rstrip("/")
        if canonical in seen:
            continue
        seen.add(canonical)
        urls.append(canonical)
    return urls


async def _load_skill_body_from_storage(version: SkillVersion | None) -> str | None:
    if version is None:
        return None

    try:
        raw = await get_storage().get_object(version.storage_url)
    except Exception:
        return None

    try:
        _frontmatter, body_md = split_frontmatter(raw)
        return body_md
    except ValueError:
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return None


def compute_preview_body(body_md: str | None) -> str:
    """Strip "How to apply" and clip "Examples" to 1, per 02-skill-detail.md."""
    if not body_md:
        return ""
    # Walk top-level (## or #) sections; keep all but "How to apply", trim
    # Examples to the first sub-example.
    lines = body_md.splitlines(keepends=False)
    out: list[str] = []
    i = 0
    n = len(lines)
    skip_section_level: int | None = None
    in_examples: bool = False
    examples_first_kept = False
    while i < n:
        line = lines[i]
        match = _HEADING_RE.match(line)
        if match:
            level = len(match.group(1))
            heading = match.group(2).strip().lower()
            # Reset state when we cross a heading at or below tracked level.
            if skip_section_level is not None and level <= skip_section_level:
                skip_section_level = None
            if in_examples and level <= 2:
                in_examples = False
                examples_first_kept = False
            if heading == "how to apply" or heading.startswith("sources reviewed"):
                skip_section_level = level
                i += 1
                continue
            if heading == "examples":
                in_examples = True
                examples_first_kept = False
                out.append(line)
                i += 1
                continue
        if skip_section_level is not None:
            i += 1
            continue
        if in_examples:
            sub = _HEADING_RE.match(line) if line else None
            if sub:
                sub_level = len(sub.group(1))
                if sub_level == 3:
                    # First ### under Examples — keep, then drop subsequent.
                    if not examples_first_kept:
                        examples_first_kept = True
                        out.append(line)
                        i += 1
                        continue
                    # Skip until next ### or ## boundary.
                    j = i + 1
                    while j < n:
                        line2 = lines[j]
                        m2 = _HEADING_RE.match(line2)
                        if m2 and len(m2.group(1)) <= 3:
                            break
                        j += 1
                    i = j
                    continue
            out.append(line)
            i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out).rstrip() + "\n"


async def fetch_skill_detail(
    session: AsyncSession,
    *,
    skill_id: uuid.UUID | None = None,
    handle: str | None = None,
    slug: str | None = None,
    include_non_public: bool = False,
) -> SkillDetail | None:
    stmt = (
        select(Skill, User, CreatorProfile)
        .join(User, User.id == Skill.creator_id)
        .join(CreatorProfile, CreatorProfile.user_id == User.id, isouter=True)
    )
    if skill_id is not None:
        stmt = stmt.where(Skill.id == skill_id)
    elif handle is not None and slug is not None:
        stmt = stmt.where(CreatorProfile.handle == handle).where(Skill.slug == slug)
    else:
        return None

    if not include_non_public:
        stmt = stmt.where(
            Skill.status.in_([SkillStatus.PUBLISHED, SkillStatus.UNLISTED])
        )

    res = await session.execute(stmt)
    row = res.first()
    if row is None:
        return None
    skill, user, profile = row

    # Latest non-yanked version.
    version_stmt = (
        select(SkillVersion)
        .where(SkillVersion.skill_id == skill.id)
        .where(SkillVersion.is_yanked.is_(False))
        .order_by(SkillVersion.released_at.desc().nulls_last())
        .limit(1)
    )
    version_res = await session.execute(version_stmt)
    version: SkillVersion | None = version_res.scalar_one_or_none()

    ai_req_blob: dict[str, Any] = (
        dict(version.ai_requirements) if version and version.ai_requirements else {}
    )
    ai_req = AiRequirements(
        required_models=list(ai_req_blob.get("required_models", []) or []),
        compatible_models=list(ai_req_blob.get("compatible_models", []) or []),
        tools_required=list(ai_req_blob.get("tools_required", []) or []),
        min_context_tokens=ai_req_blob.get("min_context_tokens"),
        estimated_tokens_per_invocation=ai_req_blob.get(
            "estimated_tokens_per_invocation"
        ),
    )

    body_md = await _load_skill_body_from_storage(version)
    preview_source_md = body_md if body_md else (version.changelog_md if version else None)
    preview_md = compute_preview_body(preview_source_md)
    inspired_by_urls = extract_inspired_by_urls(body_md)

    return SkillDetail(
        id=skill.id,
        slug=skill.slug,
        name=skill.name,
        tagline=skill.tagline,
        description_md=skill.description_md,
        category=skill.category,
        tags=list(skill.tags or []),
        cover_image_url=skill.cover_image_url,
        screenshots=list(skill.screenshots or []),
        faq_md=skill.faq_md,
        status=skill.status.value if hasattr(skill.status, "value") else str(skill.status),
        pricing=SkillPricing(
            model=(
                skill.pricing_model.value
                if hasattr(skill.pricing_model, "value")
                else str(skill.pricing_model)
            ),
            one_time_price_cents=skill.one_time_price_cents,
            subscription_price_cents=skill.subscription_price_cents,
            currency="USD",
            support_included=skill.support_included,
            freemium_paired_with=None,
        ),
        ai_requirements=ai_req,
        latest_version=(
            LatestVersionInfo(
                id=version.id,
                version=version.version,
                released_at=version.released_at,
                changelog_md=version.changelog_md,
            )
            if version is not None
            else None
        ),
        stats=SkillStats(
            rating_avg=float(skill.rating_avg) if skill.rating_avg is not None else None,
            rating_count=skill.rating_count,
            total_sales=skill.total_sales,
        ),
        creator=CreatorChipPublic(
            handle=profile.handle if profile is not None else "anon",
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            is_verified=user.is_creator_verified,
        ),
        preview_body_md=preview_md,
        inspired_by_urls=inspired_by_urls,
    )


async def list_versions(
    session: AsyncSession,
    skill_id: uuid.UUID,
    *,
    limit: int | None = None,
    cursor: str | None = None,
) -> tuple[list[VersionItem], PageInfo]:
    real_limit = clamp_limit(limit)
    stmt = (
        select(SkillVersion)
        .where(SkillVersion.skill_id == skill_id)
        .order_by(SkillVersion.released_at.desc().nulls_last(), SkillVersion.id.desc())
    )
    if cursor:
        payload = decode_cursor(cursor)
        last_id = payload.get("id")
        if last_id:
            stmt = stmt.where(cast(SkillVersion.id, String) < str(last_id))
    res = await session.execute(stmt.limit(real_limit + 1))
    rows = list(res.scalars().all())
    has_more = len(rows) > real_limit
    if has_more:
        rows = rows[:real_limit]
    items = [
        VersionItem(
            id=v.id,
            version=v.version,
            released_at=v.released_at,
            changelog_md=v.changelog_md,
            is_yanked=v.is_yanked,
            yank_reason=getattr(v, "yank_reason", None),
        )
        for v in rows
    ]
    next_cursor = encode_cursor(last_id=str(rows[-1].id)) if has_more and rows else None
    return items, PageInfo(next_cursor=next_cursor, has_more=has_more, limit=real_limit)


async def fetch_version(
    session: AsyncSession, skill_id: uuid.UUID, version: str
) -> SkillVersion | None:
    res = await session.execute(
        select(SkillVersion)
        .where(SkillVersion.skill_id == skill_id)
        .where(SkillVersion.version == version)
    )
    return res.scalar_one_or_none()


# ── Creator profile stats (compute-on-read for Phase 1) ──────────────


async def creator_stats(session: AsyncSession, user_id: uuid.UUID) -> dict[str, Any]:
    """Aggregate quick stats for a creator's public profile."""
    skills_stmt = select(
        func.count(Skill.id),
        func.coalesce(func.sum(Skill.total_sales), 0),
        func.avg(Skill.rating_avg),
    ).where(Skill.creator_id == user_id).where(Skill.status == SkillStatus.PUBLISHED)
    res = await session.execute(skills_stmt)
    total_skills, total_sales, rating_avg = res.one()
    return {
        "total_skills": int(total_skills or 0),
        "total_sales": int(total_sales or 0),
        "rating_avg": float(rating_avg) if rating_avg is not None else None,
    }


__all__ = [
    "CatalogFilters",
    "compute_preview_body",
    "creator_stats",
    "fetch_skill_detail",
    "fetch_version",
    "list_categories",
    "list_featured",
    "list_skills",
    "list_versions",
]
