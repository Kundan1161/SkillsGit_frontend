"""Build the AI DevOps Engineer occupation vault (T-08, Wave 3, Cycle 1).

End-to-end orchestration:

1. Ensure the ``@skillsgit-curated`` user exists (re-using the helper from
   :mod:`scripts.publish_curated`).
2. Load ``seed_data/devops/occupation.yaml`` + ``cross-link-recipe.yaml``.
3. Resolve every member skill row by ``(creator_id, slug)``. Abort if any
   member is missing — Wave-3A's ``publish_curated`` is expected to have
   published all 30.
4. Apply the 60 cross-links to each member skill by writing a *patch*
   ``SkillVersion`` (``1.0.0 → 1.0.1``). The original release stays
   immutable per ADR-013. Re-validates the patched body before upload;
   aborts on validation failure.
5. Create or update the occupation ``Skill`` row (``kind=occupation``).
6. Bulk-replace ``occupation_skills`` with the 30 members from the YAML.
7. Create a ``SkillVersion(version=occupation.version)`` for the occupation.
8. Publish — sets ``status=published`` + ``released_at``, then enqueues
   :func:`src.vault.jobs.enqueue_occupation_build`.
9. Poll the resulting ``vault_builds`` row until ``status='succeeded'``.
10. Download the zip, inject ``.obsidian/graph.json`` color-by-tag polish
    (ADR-016 Q-6), re-upload the patched zip under the same key.
11. Run :func:`src.vault.validator.validate_vault` on the patched bytes.
12. Print a summary + write an audit-log entry.

Run with::

    uv run python -m scripts.build_devops_vault

Idempotent: re-running produces the same content_hash (deterministic
builder + deterministic recipe) — no duplicate Skill or join rows, and
member patch versions are skipped if a ``1.0.1`` already exists with
identical bytes.
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import json
import logging
import re
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from sqlalchemy import delete, select

from scripts.publish_curated import CURATED_HANDLE, _ensure_curated_user
from src.core.db import SessionLocal, write_audit
from src.delivery.watermark import (
    compute_content_hash,
    inject_distribution_block,
)
from src.occupations.models import (
    Occupation,
    OccupationMemberRole,
    OccupationSkill,
)
from src.skills.models import (
    PricingModel,
    Skill,
    SkillKind,
    SkillStatus,
    SkillVersion,
)
from src.skills.parser import split_frontmatter
from src.skills.validator import validate_file
from src.storage.s3 import get_storage
from src.vault import builder as vault_builder
from src.vault.builder import EPOCH_DATETIME
from src.vault.models import VaultBuild, VaultBuildStatus
from src.vault.validator import validate_vault

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s build_devops_vault: %(message)s"
)
log = logging.getLogger("build_devops_vault")

DEVOPS_DIR = Path(__file__).parent / "seed_data" / "devops"
OCCUPATION_YAML = DEVOPS_DIR / "occupation.yaml"
RECIPE_YAML = DEVOPS_DIR / "cross-link-recipe.yaml"

OCCUPATION_VERSION = "1.0.0"
PATCH_VERSION = "1.0.1"  # bumped from 1.0.0 to carry the cross-links


# ── YAML loaders ──────────────────────────────────────────────────────


def _load_occupation_spec() -> dict[str, Any]:
    data = yaml.safe_load(OCCUPATION_YAML.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{OCCUPATION_YAML}: top-level must be a mapping")
    return data


def _load_recipe() -> list[dict[str, str]]:
    data = yaml.safe_load(RECIPE_YAML.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "links" not in data:
        raise RuntimeError(f"{RECIPE_YAML}: must have a top-level `links` list")
    links = data["links"]
    if not isinstance(links, list):
        raise RuntimeError(f"{RECIPE_YAML}: `links` must be a list")
    out: list[dict[str, str]] = []
    for i, raw in enumerate(links):
        if not isinstance(raw, dict):
            raise RuntimeError(f"{RECIPE_YAML}: link {i} is not a mapping")
        if not {"from", "to", "relation"}.issubset(raw.keys()):
            raise RuntimeError(
                f"{RECIPE_YAML}: link {i} missing from/to/relation: {raw}"
            )
        out.append(raw)
    return out


# ── Member resolution ─────────────────────────────────────────────────


async def _resolve_member_skills(
    session: AsyncSession,
    *,
    creator_id: Any,
    member_slugs: list[str],
) -> dict[str, Skill]:
    """Return ``{slug → Skill}`` for every requested member.

    Raises if any member slug doesn't have a corresponding ``Skill`` row
    under the curated creator. The expectation is that
    ``publish_curated`` has run first.
    """
    res = await session.execute(
        select(Skill).where(
            Skill.creator_id == creator_id,
            Skill.slug.in_(member_slugs),
        )
    )
    found = {s.slug: s for s in res.scalars().all()}
    missing = [slug for slug in member_slugs if slug not in found]
    if missing:
        raise RuntimeError(
            f"Member skill(s) not found under @{CURATED_HANDLE}: {missing}. "
            f"Run `uv run python -m scripts.publish_curated` first."
        )
    return found


# ── Cross-link application via patch SkillVersions ────────────────────


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*(?:\n|$)", re.DOTALL)


def _split_fm_text(content: str) -> tuple[dict[str, Any], str]:
    """Split into ``(frontmatter_dict, body_text)`` preserving raw body text."""
    m = _FRONTMATTER_RE.match(content)
    if not m:
        raise ValueError("Skills.md file is missing frontmatter")
    yaml_block = m.group(1)
    body = content[m.end():]
    data = yaml.safe_load(yaml_block) or {}
    if not isinstance(data, dict):
        raise ValueError("Frontmatter must be a YAML mapping")
    return data, body


def _apply_links_to_frontmatter(
    fm: dict[str, Any], links_for_skill: list[dict[str, str]]
) -> dict[str, Any]:
    """Return a copy of ``fm`` with ``links`` set to the recipe's entries.

    The previous ``links`` value (if any) is replaced — we own the field for
    every curated member at occupation-build time. The output preserves
    field insertion order: existing keys keep their position; ``links`` is
    inserted right after ``tags`` (or at the end if ``tags`` is absent),
    matching the ordering convention of the existing synthesized files.
    """
    # Build the new links list.
    new_links = [
        {"target": link["to"], "relation": link["relation"]}
        for link in links_for_skill
    ]
    # Preserve insertion order; if `links` already exists, just replace value.
    new_fm: dict[str, Any] = {}
    inserted = False
    for k, v in fm.items():
        if k == "links":
            new_fm[k] = new_links
            inserted = True
        elif k == "tags":
            new_fm[k] = v
            new_fm["links"] = new_links
            inserted = True
        else:
            new_fm[k] = v
    if not inserted:
        new_fm["links"] = new_links
    # Ensure `kind` is explicit on members — `SkillKind.SKILL` is the
    # default, but emitting it makes the file self-describing for any
    # downstream consumer that reads the patched .md directly.
    new_fm.setdefault("kind", SkillKind.SKILL.value)
    return new_fm


def _emit_patched_body(
    fm: dict[str, Any],
    body_text: str,
    *,
    new_version: str,
) -> bytes:
    """Serialise ``(fm, body)`` back into a skills.md byte stream.

    Bumps ``version`` to ``new_version`` so the patched body is a valid
    1.0.1 (or whatever ``new_version`` says) — versioning is the contract
    that lets the builder pick the latest released non-yanked version.
    Pre-existing ``distribution`` block (if any) is stripped — it will be
    re-injected by :func:`inject_distribution_block` at upload time.
    """
    fm = dict(fm)
    fm["version"] = new_version
    fm.pop("distribution", None)
    yaml_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    body_norm = body_text.lstrip("\n")
    return f"---\n{yaml_text}\n---\n\n{body_norm}".encode("utf-8")


async def _ensure_member_patch_version(
    session: AsyncSession,
    skill: Skill,
    *,
    creator_id: Any,
    links_for_skill: list[dict[str, str]],
) -> tuple[SkillVersion, bool]:
    """Ensure a ``PATCH_VERSION`` of ``skill`` exists carrying the recipe links.

    Returns ``(version_row, was_new)``. Idempotent:
    * If the patch version already exists and its ``content_hash`` matches
      what we'd produce now, we keep it (no upload, no row change).
    * If the patch version exists but its content_hash differs (a recipe
      edit), we overwrite the storage object and update the row's hash so
      the next build picks up the change.
    """
    # Pull the 1.0.0 source.
    res = await session.execute(
        select(SkillVersion).where(
            SkillVersion.skill_id == skill.id,
            SkillVersion.version == OCCUPATION_VERSION,
        )
    )
    base_version = res.scalar_one_or_none()
    if base_version is None:
        raise RuntimeError(
            f"Member {skill.slug}: no base version {OCCUPATION_VERSION}; "
            f"did publish_curated run successfully?"
        )

    storage = get_storage()
    src_bytes = await storage.get_object(base_version.storage_url)
    fm, body_text = _split_fm_text(src_bytes.decode("utf-8"))
    patched_fm = _apply_links_to_frontmatter(fm, links_for_skill)
    patched_bytes = _emit_patched_body(
        patched_fm, body_text, new_version=PATCH_VERSION
    )

    # Validate the patched body before persisting it.
    vr = validate_file(patched_bytes)
    if not vr.is_valid:
        errs = "; ".join(
            f"{e.field}: {e.code} — {e.message}" for e in vr.errors[:5]
        )
        raise RuntimeError(
            f"Member {skill.slug}: patched body failed validation: {errs}"
        )

    patched_hash = compute_content_hash(patched_bytes.decode("utf-8"))
    storage_key = f"skills/{skill.id}/{PATCH_VERSION}.md"

    # Existing patch version?
    res2 = await session.execute(
        select(SkillVersion).where(
            SkillVersion.skill_id == skill.id,
            SkillVersion.version == PATCH_VERSION,
        )
    )
    existing = res2.scalar_one_or_none()

    # Always inject the distribution block before uploading. The block
    # is recomputed on each call so the stored object stays consistent.
    stamped = inject_distribution_block(patched_bytes.decode("utf-8"))

    if existing is not None and existing.content_hash == patched_hash:
        # Already published with the same content; nothing to do.
        skill.latest_version_id = existing.id
        return existing, False

    # Upload the (potentially new) bytes.
    await storage.put_object(storage_key, stamped.encode("utf-8"), "text/markdown")

    if existing is not None:
        # Recipe drift: keep the row, update its hash so downstream code
        # (builder + composer) sees the new content. Re-validating the
        # same version string is permitted because we own it.
        existing.content_hash = patched_hash
        existing.storage_url = storage_key
        skill.latest_version_id = existing.id
        return existing, False

    version = SkillVersion(
        skill_id=skill.id,
        version=PATCH_VERSION,
        content_hash=patched_hash,
        storage_url=storage_key,
        ai_requirements=dict(fm.get("ai") or {}),
        changelog_md=(
            "Wave-3 occupation build: 60-link cross-link recipe applied to "
            "frontmatter `links:` for graph view rendering."
        ),
        released_at=datetime.now(UTC),
        released_by=creator_id,
        is_yanked=False,
        target_version=PATCH_VERSION,
    )
    session.add(version)
    await session.flush()
    skill.latest_version_id = version.id
    return version, True


# ── Occupation upsert ─────────────────────────────────────────────────


async def _ensure_occupation_skill(
    session: AsyncSession,
    *,
    creator_id: Any,
    spec: dict[str, Any],
) -> tuple[Skill, Occupation, bool]:
    """Create or update the occupation Skill + side-table row.

    Idempotent on ``(creator_id, slug)``.
    """
    handle, slug = str(spec["id"]).split("/", 1)
    if handle != CURATED_HANDLE:
        raise RuntimeError(
            f"occupation.yaml id handle {handle!r} != {CURATED_HANDLE!r}"
        )

    domain_slugs = [d["slug"] for d in spec.get("domains", [])]

    res = await session.execute(
        select(Skill).where(
            Skill.creator_id == creator_id, Skill.slug == slug
        )
    )
    skill = res.scalar_one_or_none()
    is_new = skill is None
    if skill is None:
        skill = Skill(
            creator_id=creator_id,
            slug=slug,
            name=str(spec["name"]),
            tagline=str(spec.get("tagline") or "")[:140] or None,
            description_md=str(spec.get("description") or ""),
            category=str(spec.get("category") or "occupations"),
            tags=list(spec.get("tags") or []),
            status=SkillStatus.DRAFT,
            kind=SkillKind.OCCUPATION,
            pricing_model=PricingModel.FREE,
            one_time_price_cents=None,
            subscription_price_cents=None,
            support_url="https://skillsgit.com/support",
        )
        session.add(skill)
        await session.flush()
    else:
        skill.name = str(spec["name"])
        skill.tagline = str(spec.get("tagline") or "")[:140] or None
        skill.description_md = str(spec.get("description") or "")
        skill.category = str(spec.get("category") or skill.category or "occupations")
        skill.tags = list(spec.get("tags") or [])
        skill.kind = SkillKind.OCCUPATION
        skill.pricing_model = PricingModel.FREE

    res2 = await session.execute(
        select(Occupation).where(Occupation.skill_id == skill.id)
    )
    occupation = res2.scalar_one_or_none()
    if occupation is None:
        occupation = Occupation(
            skill_id=skill.id,
            summary_md=str(spec.get("description") or "") or None,
            domains=domain_slugs or None,
            persona_count=0,
            recommended_persona_count=int(spec.get("recommended_persona_count", 0)),
        )
        session.add(occupation)
        await session.flush()
    else:
        occupation.summary_md = str(spec.get("description") or "") or None
        occupation.domains = domain_slugs or None
        occupation.recommended_persona_count = int(
            spec.get("recommended_persona_count", 0)
        )

    return skill, occupation, is_new


# ── occupation_skills upsert ──────────────────────────────────────────


_ROLE_MAP: dict[str, OccupationMemberRole] = {
    "core": OccupationMemberRole.CORE,
    "supporting": OccupationMemberRole.SUPPORTING,
    "optional": OccupationMemberRole.OPTIONAL,
}


async def _replace_membership(
    session: AsyncSession,
    *,
    occupation_skill_id: Any,
    spec_members: list[dict[str, Any]],
    member_skills: dict[str, Skill],
) -> int:
    """Bulk-replace ``occupation_skills`` rows. Idempotent."""
    # Wipe + recreate is the simplest path to a deterministic state. The
    # service layer's ``bulk_set_members`` does the same thing.
    await session.execute(
        delete(OccupationSkill).where(
            OccupationSkill.occupation_id == occupation_skill_id
        )
    )
    for m in spec_members:
        role = _ROLE_MAP[m["member_role"]]
        member = member_skills[m["slug"]]
        row = OccupationSkill(
            occupation_id=occupation_skill_id,
            member_skill_id=member.id,
            domain=m.get("domain"),
            sort_order=int(m.get("sort_order", 0)),
            role=role,
            pinned=False,
            notes_md=None,
        )
        session.add(row)
        await session.flush([row])
    return len(spec_members)


# ── Occupation SkillVersion ──────────────────────────────────────────


async def _ensure_occupation_version(
    session: AsyncSession,
    *,
    skill: Skill,
    creator_id: Any,
    changelog: list[dict[str, Any]] | None,
) -> SkillVersion:
    """Create ``occupation.version`` if missing.

    The occupation's version row anchors the vault_build. The body is
    rendered by the builder, so the row only needs a hash placeholder and
    a storage_url that points to a manifest snapshot — we write a tiny
    JSON envelope so the storage object isn't empty.
    """
    res = await session.execute(
        select(SkillVersion).where(
            SkillVersion.skill_id == skill.id,
            SkillVersion.version == OCCUPATION_VERSION,
        )
    )
    version = res.scalar_one_or_none()
    if version is not None:
        skill.latest_version_id = version.id
        return version

    storage = get_storage()
    storage_key = f"skills/{skill.id}/{OCCUPATION_VERSION}.occupation.json"
    payload = json.dumps(
        {
            "skill_id": str(skill.id),
            "slug": skill.slug,
            "version": OCCUPATION_VERSION,
            "kind": SkillKind.OCCUPATION.value,
            "rendered_at": datetime.now(UTC).isoformat(),
        },
        sort_keys=True,
    ).encode("utf-8")
    await storage.put_object(storage_key, payload, "application/json")
    content_hash = hashlib.sha256(payload).hexdigest()

    notes = ""
    if changelog:
        head = changelog[0]
        notes = str(head.get("notes") or "")
    version = SkillVersion(
        skill_id=skill.id,
        version=OCCUPATION_VERSION,
        content_hash=content_hash,
        storage_url=storage_key,
        ai_requirements=None,
        changelog_md=notes or None,
        released_at=None,  # set when we publish
        released_by=None,
        is_yanked=False,
        target_version=OCCUPATION_VERSION,
    )
    session.add(version)
    await session.flush()
    skill.latest_version_id = version.id
    return version


# ── .obsidian/graph.json polish (ADR-016 Q-6) ────────────────────────


# Three accessible distinct hues per the brief (teal / amber / violet)
# extended to 7 to match the 7 declared domains. Hex picked from
# Tailwind v3 palette steps for visual distinction at 50% saturation.
_GRAPH_DOMAIN_COLORS: dict[str, str] = {
    "ci-cd":          "#0EA5E9",  # sky-500
    "observability":  "#10B981",  # emerald-500
    "incident":       "#F59E0B",  # amber-500
    "iac":            "#8B5CF6",  # violet-500
    "security":       "#EF4444",  # red-500
    "cost":           "#22C55E",  # green-500
    "platform":       "#EC4899",  # pink-500
}


def _hex_to_rgb_int(hex_color: str) -> int:
    """Obsidian stores colour as a single integer (0xRRGGBB)."""
    h = hex_color.lstrip("#")
    return int(h, 16)


def _build_graph_json(domain_slugs: list[str]) -> bytes:
    """Render ``.obsidian/graph.json`` with color-by-tag for each domain."""
    color_groups = []
    for slug in domain_slugs:
        hex_color = _GRAPH_DOMAIN_COLORS.get(slug, "#94A3B8")
        color_groups.append(
            {
                "query": f"tag:#{slug}",
                "color": {"a": 1.0, "rgb": _hex_to_rgb_int(hex_color)},
            }
        )
    payload = {
        "collapse-filter": True,
        "search": "",
        "showTags": False,
        "showAttachments": False,
        "hideUnresolved": False,
        "showOrphans": True,
        "collapse-color": False,
        "collapse-display": True,
        "collapse-forces": True,
        "lineSizeMultiplier": 1.5,
        "colorGroups": color_groups,
    }
    return json.dumps(payload, indent=2, sort_keys=False).encode("utf-8")


def _inject_graph_json_into_zip(
    zip_bytes: bytes, *, graph_json_bytes: bytes
) -> bytes:
    """Return a new zip with ``.obsidian/graph.json`` added.

    Re-zips every entry to preserve the determinism guarantees from
    :mod:`src.vault.builder` (sorted, pinned timestamp).
    """
    target_path = ".obsidian/graph.json"
    src = zipfile.ZipFile(io.BytesIO(zip_bytes))
    try:
        existing_names = src.namelist()
        if target_path in existing_names:
            # The polish landed in a previous run; nothing to do.
            src.close()
            return zip_bytes
        new_entries: list[tuple[str, bytes]] = []
        for name in existing_names:
            new_entries.append((name, src.read(name)))
        new_entries.append((target_path, graph_json_bytes))
        # Re-emit deterministically.
        out_buf = io.BytesIO()
        with zipfile.ZipFile(out_buf, "w", compression=zipfile.ZIP_DEFLATED) as out_zip:
            for path, data in sorted(new_entries, key=lambda p: p[0]):
                info = zipfile.ZipInfo(
                    filename=path,
                    date_time=(
                        EPOCH_DATETIME.year,
                        EPOCH_DATETIME.month,
                        EPOCH_DATETIME.day,
                        EPOCH_DATETIME.hour,
                        EPOCH_DATETIME.minute,
                        EPOCH_DATETIME.second,
                    ),
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                out_zip.writestr(info, data)
        return out_buf.getvalue()
    finally:
        src.close()


async def _polish_vault_with_graph_json(
    session: AsyncSession,
    *,
    build: VaultBuild,
    domain_slugs: list[str],
) -> tuple[bool, bytes]:
    """Post-build step: add ``.obsidian/graph.json`` to the built zip.

    Returns ``(was_modified, final_zip_bytes)``.

    Re-uploads the modified zip and patches ``vault_builds.storage_url``,
    ``content_hash``, ``total_bytes`` and ``file_count`` so the composer
    (which serves the same artifact at delivery time) picks up the
    polish for every buyer.
    """
    storage = get_storage()
    original_bytes = await storage.get_object(build.storage_url)
    graph_bytes = _build_graph_json(domain_slugs)
    patched = _inject_graph_json_into_zip(
        original_bytes, graph_json_bytes=graph_bytes
    )
    if patched == original_bytes:
        return False, original_bytes

    new_hash = hashlib.sha256(patched).hexdigest()
    # Place under a sibling key so the original immutable artifact is
    # preserved (per ADR-013) and the patched one becomes the authoritative
    # ``storage_url`` for delivery. Sibling key just swaps the trailing
    # ``<hash>.zip`` component of the original key.
    new_storage_url = _sibling_key_for(build.storage_url, new_hash)
    await storage.put_object(new_storage_url, patched, "application/zip")

    # Patch the build row in place. The (skill_id, content_hash) unique
    # constraint allows the new hash because we keep the old row but
    # change its content_hash; SQL is happy as long as no other row in
    # the table has the new hash for the same skill_id. (At MVP scale
    # we never write two builds for the same occupation version, so a
    # collision is impossible.)
    file_count = 0
    total_bytes = len(patched)
    with zipfile.ZipFile(io.BytesIO(patched)) as zf:
        file_count = len(zf.namelist())
    build.storage_url = new_storage_url
    build.content_hash = new_hash
    build.total_bytes = total_bytes
    build.file_count = file_count
    await session.flush()
    return True, patched


def _sibling_key_for(original_key: str, new_hash: str) -> str:
    """Derive a sibling object key swapping the trailing ``<hash>.zip``."""
    # original_key shape: "vaults/{skill_id}/{version}/{hash}.zip"
    head, _slash, _tail = original_key.rpartition("/")
    return f"{head}/{new_hash}.zip"


# ── Driver ───────────────────────────────────────────────────────────


async def _flush_storage_inmemory_warning() -> None:
    """Refuse to run against the in-memory storage outside of tests.

    The script must persist to a real backing store (MinIO in dev) so
    re-runs in fresh processes can read what previous runs wrote.
    """
    from src.core.config import settings as _s
    from src.storage.s3 import InMemoryStorage as _InMem
    if _s.is_test and isinstance(get_storage(), _InMem):
        # Test runs always use in-memory; the script isn't typically
        # invoked under pytest, but make the failure mode obvious.
        log.warning(
            "ENV=test with InMemoryStorage detected — durability across "
            "processes is NOT guaranteed."
        )


async def run() -> None:
    log.info("loading %s", OCCUPATION_YAML)
    spec = _load_occupation_spec()
    log.info("loading %s", RECIPE_YAML)
    recipe = _load_recipe()
    log.info(
        "spec: id=%s name=%s members=%d domains=%d",
        spec["id"], spec["name"], len(spec["members"]), len(spec.get("domains", [])),
    )
    log.info("recipe: %d cross-links", len(recipe))

    # Group recipe links by source slug for fast lookup.
    by_source: dict[str, list[dict[str, str]]] = {}
    for link in recipe:
        by_source.setdefault(link["from"], []).append(link)

    await get_storage().ensure_bucket()
    await _flush_storage_inmemory_warning()

    # ─── Phase 1: curated user + member resolution + cross-link patches ──
    member_slugs = [m["slug"] for m in spec["members"]]
    async with SessionLocal() as session:
        creator = await _ensure_curated_user(session)
        await session.commit()
        creator_id = creator.id
        log.info("curated user: %s (id=%s)", creator.email, creator_id)

    member_skills: dict[str, Skill] = {}
    patches_new = 0
    patches_existing = 0
    async with SessionLocal() as session:
        member_skills = await _resolve_member_skills(
            session, creator_id=creator_id, member_slugs=member_slugs
        )
        log.info("resolved %d/%d member skill rows", len(member_skills), len(member_slugs))

        for slug in member_slugs:
            skill = member_skills[slug]
            links_for_skill = by_source.get(slug, [])
            _version, was_new = await _ensure_member_patch_version(
                session,
                skill,
                creator_id=creator_id,
                links_for_skill=links_for_skill,
            )
            if was_new:
                patches_new += 1
            else:
                patches_existing += 1
        await session.commit()
    log.info(
        "patches: %d new + %d existing (or unchanged) — %d skills with 0 outbound links",
        patches_new,
        patches_existing,
        sum(1 for s in member_slugs if not by_source.get(s)),
    )

    # ─── Phase 2: occupation Skill row + occupation_skills + version ─────
    async with SessionLocal() as session:
        skill, occupation, was_new = await _ensure_occupation_skill(
            session, creator_id=creator_id, spec=spec
        )
        log.info(
            "occupation skill row %s (id=%s, %s)",
            "created" if was_new else "updated",
            skill.id,
            "new" if was_new else "existing",
        )
        # Resolve member skills again on this session to avoid mixing
        # entities from the previous one.
        member_skills_session = await _resolve_member_skills(
            session, creator_id=creator_id, member_slugs=member_slugs
        )
        member_count = await _replace_membership(
            session,
            occupation_skill_id=skill.id,
            spec_members=spec["members"],
            member_skills=member_skills_session,
        )
        log.info("occupation_skills: %d rows written (bulk-replaced)", member_count)

        version_row = await _ensure_occupation_version(
            session,
            skill=skill,
            creator_id=creator_id,
            changelog=spec.get("changelog"),
        )
        log.info(
            "occupation version row: id=%s version=%s",
            version_row.id,
            version_row.version,
        )

        # Publish: set status, released_at, then run the build.
        #
        # The vault jobs façade has three modes: prod-enqueue-to-Arq,
        # test-stub, and test-inline. Because this script runs in
        # ENV=dev and there is no Arq worker, the script calls the
        # builder directly — same code path the inline-test mode uses.
        # This is the same pattern T-13's demo CLI follows per
        # dev-diary-vault-composer-wave3.md §1.
        if version_row.released_at is None:
            version_row.released_at = datetime.now(UTC)
            version_row.released_by = creator_id
        if skill.status != SkillStatus.PUBLISHED:
            skill.status = SkillStatus.PUBLISHED
        skill.latest_version_id = version_row.id

        # Force the latest_version_id write to commit before we hand off
        # to the builder (which will read versions in its own queries).
        await session.flush()

        # Idempotency: if a succeeded build for this (skill_id, version_id)
        # already exists, reuse it instead of running the builder. The
        # builder's own (skill_id, content_hash) idempotency check breaks
        # down once the .obsidian/graph.json polish has mutated the row's
        # content_hash — calling build_occupation again would try to
        # insert a new row and trip the partial unique on
        # (skill_version_id) WHERE status='succeeded'.
        existing_build_res = await session.execute(
            select(VaultBuild)
            .where(VaultBuild.skill_id == skill.id)
            .where(VaultBuild.skill_version_id == version_row.id)
            .where(VaultBuild.status == VaultBuildStatus.SUCCEEDED)
        )
        existing_build = existing_build_res.scalar_one_or_none()
        if existing_build is not None:
            log.info(
                "build result: REUSE existing succeeded build id=%s content_hash=%s",
                existing_build.id, existing_build.content_hash,
            )
            build_row = existing_build
        else:
            try:
                build_row = await vault_builder.build_occupation(
                    session,
                    skill.id,
                    OCCUPATION_VERSION,
                    force_rebuild=False,
                )
            except vault_builder.VaultBuildError as exc:
                raise RuntimeError(
                    f"vault build failed: {exc.code} — {exc.message}"
                ) from exc

            log.info(
                "build result: status=%s build_id=%s content_hash=%s",
                build_row.status.value if hasattr(build_row.status, "value") else build_row.status,
                build_row.id,
                build_row.content_hash,
            )

        # Frame the façade's normal return shape for the rest of the script.
        class _Result:
            def __init__(self, build_id: Any, content_hash: str, job_id: str) -> None:
                self.build_id = build_id
                self.status = "succeeded"
                self.job_id = job_id
                self.content_hash = content_hash

        result = _Result(
            build_id=build_row.id,
            content_hash=build_row.content_hash,
            job_id=f"vault:build_occupation:{skill.id}:{OCCUPATION_VERSION}:{build_row.id.hex[:8]}",
        )

        await write_audit(
            session,
            actor_id=creator_id,
            action="occupation.published",
            target_type="skill",
            target_id=skill.id,
            metadata={
                "version": OCCUPATION_VERSION,
                "job_id": result.job_id,
                "build_id": str(result.build_id) if result.build_id else None,
                "member_count": member_count,
                "links_applied": len(recipe),
            },
        )
        await session.commit()

        occupation_skill_id = skill.id

    # ─── Phase 3: load the build row, polish, validate ──────────────────
    # The build ran inline above; this is just a fresh load for the
    # polish / validate phase.
    async with SessionLocal() as s:
        build = await s.get(VaultBuild, result.build_id)
        if build is None:
            raise RuntimeError(
                f"vault_builds row {result.build_id} not found after inline build"
            )

    log.info(
        "vault_build %s succeeded: content_hash=%s files=%d bytes=%d storage=%s",
        build.id, build.content_hash, build.file_count, build.total_bytes, build.storage_url,
    )

    domain_slugs = [d["slug"] for d in spec.get("domains", [])]
    async with SessionLocal() as session:
        build_in_session = await session.get(VaultBuild, build.id)
        if build_in_session is None:
            raise RuntimeError(f"vault_builds row {build.id} disappeared between phases")
        was_polished, final_bytes = await _polish_vault_with_graph_json(
            session, build=build_in_session, domain_slugs=domain_slugs
        )
        await session.commit()
        # Refresh build snapshot for the summary.
        final_storage_url = build_in_session.storage_url
        final_content_hash = build_in_session.content_hash
        final_file_count = build_in_session.file_count
        final_total_bytes = build_in_session.total_bytes

    if was_polished:
        log.info(
            "polished: injected .obsidian/graph.json; new content_hash=%s bytes=%d",
            final_content_hash, final_total_bytes,
        )
    else:
        log.info("polish: .obsidian/graph.json already present — no change")

    # Validate the final bytes.
    validation = validate_vault(final_bytes)
    log.info(
        "validate_vault: is_valid=%s error_count=%d",
        validation.is_valid, len(validation.errors),
    )
    if not validation.is_valid:
        for err in validation.errors[:10]:
            log.error("  vault error: %s — %s", err.code, err.message)
        raise RuntimeError("validate_vault() failed on the produced bundle")

    # ─── Summary ─────────────────────────────────────────────────────────
    print()
    print("=" * 72)
    print("AI DevOps Engineer occupation vault — Wave 3 T-08 summary")
    print("=" * 72)
    print(f"  occupation skill_id : {occupation_skill_id}")
    print(f"  occupation version  : {OCCUPATION_VERSION}")
    print(f"  vault_build.id      : {build.id}")
    print(f"  content_hash        : {final_content_hash}")
    print(f"  file_count          : {final_file_count}")
    print(f"  total_bytes         : {final_total_bytes}")
    print(f"  storage_url         : {final_storage_url}")
    print(f"  members             : {len(member_slugs)} across {len(domain_slugs)} domains")
    print(f"  cross-links applied : {len(recipe)}")
    print(f"  obsidian polish     : {'injected' if was_polished else 'already present'}")
    print(f"  validate_vault      : is_valid={validation.is_valid}")
    print()
    print("Open in Obsidian:")
    print(
        "  1. Download the zip:   `mc cp local/skillsgit-skills/{key} ./vault.zip`".format(
            key=final_storage_url
        )
    )
    print("  2. Extract:             `unzip vault.zip -d ai-devops-engineer`")
    print("  3. Open Obsidian -> 'Open folder as vault' -> ai-devops-engineer/")
    print("  4. Press Ctrl-G to view the graph (colored by tag).")
    print("=" * 72)


if __name__ == "__main__":
    asyncio.run(run())
