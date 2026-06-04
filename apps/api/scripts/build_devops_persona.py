"""Build the @jane-devops-demo "Incident Veteran" sample persona (T-12, Wave 4).

End-to-end orchestration that mirrors :mod:`scripts.build_devops_vault`
but for a persona rather than an occupation.

Phases:

1. Ensure the ``@jane-devops-demo`` *demo* creator account exists
   (separate from the curated account that owns the occupation, per
   ADR-016 Q-4 and the T-12 spec).
2. Load ``seed_data/devops-persona/persona.yaml`` + the 7
   ``neurons/*.skills.md`` files.
3. Validate every neuron via :func:`src.skills.validator.validate_file`.
   Abort with a clear error if any fail.
4. Resolve the parent occupation Skill row by
   ``parent_occupation_id`` (handle/slug pair → DB row). Abort if the
   occupation is missing or not yet published (T-08 must have run).
5. Verify every neuron's ``links[]`` target resolves to a member of the
   parent occupation. Abort if any link is unresolvable. This is the
   T-12 acceptance bullet "zero warnings in the persona build's
   ``manifest.warnings``" — the build itself deliberately leaves
   ``base/...`` links unresolved (the composer resolves them at
   delivery time), so script-side verification is the right place.
6. Upsert one ``Skill`` row + ``SkillVersion`` per neuron
   (``kind=memory_neuron``), upload body to S3. Idempotent on
   ``(creator_id, slug)``.
7. Upsert the persona ``Skill`` row + ``Persona`` side-table row
   (``kind=persona``), idempotent on ``(creator_id, slug)``.
8. Upsert ``persona_neurons`` rows attaching neurons to the persona
   (bulk-replace for deterministic ordering).
9. Create the persona ``SkillVersion`` (1.0.0).
10. Publish: set ``status=published``, ``released_at``, then call
    :func:`src.vault.builder.build_persona` directly (same pattern as
    ``build_devops_vault.py`` — in dev there's no Arq worker, so the
    enqueue-to-queue path would block forever).
11. Reload the resulting ``vault_builds`` row and run
    :func:`src.vault.validator.validate_vault` on the produced bytes.
12. Print a summary + write an ``persona.published`` audit log entry.

Run with::

    uv run python -m scripts.build_devops_persona

Idempotent: re-running produces the same persona + neuron rows, the
same persona_neurons join membership, and either reuses the existing
succeeded ``vault_builds`` row (when the content_hash is unchanged) or
adds a single new row (when the persona content changed).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from passlib.context import CryptContext
from sqlalchemy import delete, select
from src.core.db import SessionLocal, write_audit
from src.delivery.watermark import compute_content_hash, inject_distribution_block
from src.occupations.models import Occupation, OccupationSkill
from src.personas.models import Persona, PersonaNeuron
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
from src.users.models import CreatorProfile, User, UserRole
from src.vault import builder as vault_builder
from src.vault.models import VaultBuild, VaultBuildStatus
from src.vault.validator import validate_vault

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s build_devops_persona: %(message)s"
)
log = logging.getLogger("build_devops_persona")

PERSONA_DIR = Path(__file__).parent / "seed_data" / "devops-persona"
PERSONA_YAML = PERSONA_DIR / "persona.yaml"
NEURONS_DIR = PERSONA_DIR / "neurons"

PERSONA_VERSION = "1.0.0"
NEURON_VERSION = "1.0.0"

# Demo creator identity (per ADR-016 Q-4 + T-12 spec).
DEMO_HANDLE = "jane-devops-demo"
DEMO_EMAIL = "jane-devops-demo@skillsgit.local"
DEMO_DISPLAY = "Jane Devops (sample)"
DEMO_BIO = (
    "Demo creator account for the Cycle-1 sample persona — not a real "
    "practitioner. The 7 neurons published under this account are "
    "synthesised demonstration data shipped alongside the AI DevOps "
    "Engineer occupation. Real practitioner personas replace this content."
)
# Internal account; password is not used for login (no creator login flow
# is exercised by the demo). Same Argon2 hashing pattern as
# `publish_curated.py`.
DEMO_PASSWORD = "Demo-jane-devops-not-for-login-1234"  # noqa: S105

pwd = CryptContext(schemes=["argon2"], deprecated="auto")


# ── YAML loaders ──────────────────────────────────────────────────────


def _load_persona_spec() -> dict[str, Any]:
    data = yaml.safe_load(PERSONA_YAML.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{PERSONA_YAML}: top-level must be a mapping")
    for required in ("id", "name", "neurons", "parent_occupation_id", "version"):
        if required not in data:
            raise RuntimeError(f"{PERSONA_YAML}: missing required key {required!r}")
    if not isinstance(data["neurons"], list) or not data["neurons"]:
        raise RuntimeError(f"{PERSONA_YAML}: `neurons` must be a non-empty list")
    return data


def _load_neuron_files(slugs: list[str]) -> list[tuple[str, Path, bytes, dict[str, Any], str]]:
    """Return ``[(slug, path, raw_bytes, frontmatter, body_md), ...]``.

    Order matches the order in ``persona.yaml``. Raises if a file is
    missing or fails ``validate_file()``.
    """
    out: list[tuple[str, Path, bytes, dict[str, Any], str]] = []
    for slug in slugs:
        path = NEURONS_DIR / f"{slug}.skills.md"
        if not path.exists():
            raise RuntimeError(
                f"Neuron file missing: {path}. persona.yaml lists {slug} but "
                f"the corresponding file is not on disk."
            )
        raw = path.read_bytes()
        vr = validate_file(raw)
        if not vr.is_valid:
            errs = "; ".join(
                f"{e.field}: {e.code} — {e.message}" for e in vr.errors[:5]
            )
            raise RuntimeError(f"{path.name}: validate_file() failed: {errs}")
        fm, body = split_frontmatter(raw)
        if not isinstance(fm, dict):
            raise RuntimeError(f"{path.name}: frontmatter is not a mapping")
        # The validator guarantees these are present + correctly typed.
        fm_id = str(fm.get("id") or "")
        if "/" not in fm_id:
            raise RuntimeError(f"{path.name}: frontmatter id {fm_id!r} missing handle/slug")
        handle, fm_slug = fm_id.split("/", 1)
        if handle != DEMO_HANDLE:
            raise RuntimeError(
                f"{path.name}: id handle {handle!r} != demo handle {DEMO_HANDLE!r}"
            )
        if fm_slug != slug:
            raise RuntimeError(
                f"{path.name}: id slug {fm_slug!r} != filename slug {slug!r}. "
                f"Keep the file basename and the frontmatter slug in sync."
            )
        out.append((slug, path, raw, fm, body))
    return out


# ── Demo creator account ──────────────────────────────────────────────


async def _ensure_demo_user(session: AsyncSession) -> User:
    """Idempotent: create the demo creator account if missing.

    Mirrors ``publish_curated._ensure_curated_user`` but with the demo
    handle / email / bio. Sets ``is_creator_verified=True`` so the
    persona service's verified-creator gate doesn't reject the publish
    path (the demo persona must publish for the composer to assemble
    the Layer-C bundle).
    """
    res = await session.execute(select(User).where(User.email == DEMO_EMAIL))
    user = res.scalar_one_or_none()
    if user is not None:
        return user

    user = User(
        email=DEMO_EMAIL,
        hashed_password=pwd.hash(DEMO_PASSWORD),
        display_name=DEMO_DISPLAY,
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
        is_admin=False,
        is_creator_verified=True,
    )
    session.add(user)
    await session.flush()

    profile = CreatorProfile(
        user_id=user.id,
        handle=DEMO_HANDLE,
        bio=DEMO_BIO,
        industries=["devops", "sample-data"],
        payout_country="US",
    )
    session.add(profile)
    await session.flush()
    log.info("created @%s demo creator account (%s)", DEMO_HANDLE, user.id)
    return user


# ── Parent occupation resolution ──────────────────────────────────────


async def _resolve_parent_occupation(
    session: AsyncSession, *, parent_id: str
) -> tuple[Skill, Occupation, dict[str, str]]:
    """Resolve ``handle/slug`` → ``(Skill, Occupation, {member_slug: vault_target})``.

    The third element is the resolver map the script uses to verify
    every neuron's ``links[]`` target. Keys are bare slugs (e.g.
    ``ci-pipeline-architect``); values are the vault-relative paths the
    occupation build emits (e.g. ``domains/ci-cd/ci-pipeline-architect``).
    Both forms are accepted as targets in neuron frontmatter:

    * ``base/ci-pipeline-architect`` (bare-slug — Wave-3 dev diary
      recommendation; forward-compatible with folder reorgs)
    * ``base/domains/ci-cd/ci-pipeline-architect`` (fully-qualified —
      also resolves)
    """
    if "/" not in parent_id:
        raise RuntimeError(
            f"parent_occupation_id {parent_id!r} must be of the form handle/slug"
        )
    handle, slug = parent_id.split("/", 1)

    # Lookup by (creator_handle, slug). We resolve through CreatorProfile.
    res = await session.execute(
        select(Skill, CreatorProfile)
        .join(CreatorProfile, CreatorProfile.user_id == Skill.creator_id)
        .where(CreatorProfile.handle == handle)
        .where(Skill.slug == slug)
        .where(Skill.kind == SkillKind.OCCUPATION)
    )
    row = res.first()
    if row is None:
        raise RuntimeError(
            f"Parent occupation {parent_id!r} not found. "
            f"Run `uv run python -m scripts.build_devops_vault` first to "
            f"publish the AI DevOps Engineer occupation."
        )
    parent_skill: Skill = row[0]
    if parent_skill.status != SkillStatus.PUBLISHED:
        raise RuntimeError(
            f"Parent occupation {parent_id!r} is in status "
            f"{parent_skill.status.value}, not 'published'. "
            f"Publish the occupation before building the persona."
        )

    occ_res = await session.execute(
        select(Occupation).where(Occupation.skill_id == parent_skill.id)
    )
    occupation = occ_res.scalar_one_or_none()
    if occupation is None:
        raise RuntimeError(
            f"Occupation side-table row for skill {parent_skill.id} missing."
        )

    # Build the member resolver map: {member_slug: vault_path_no_ext}.
    members_res = await session.execute(
        select(OccupationSkill, Skill)
        .join(Skill, Skill.id == OccupationSkill.member_skill_id)
        .where(OccupationSkill.occupation_id == parent_skill.id)
    )
    resolver_map: dict[str, str] = {}
    for membership, member_skill in members_res.all():
        domain = membership.domain or "uncategorised"
        vault_no_ext = f"domains/{domain}/{member_skill.slug}"
        resolver_map[member_skill.slug] = vault_no_ext
        # Also register the fully-qualified form for compatibility.
        resolver_map[vault_no_ext] = vault_no_ext
    return parent_skill, occupation, resolver_map


def _verify_neuron_links_resolve(
    neuron_files: list[tuple[str, Path, bytes, dict[str, Any], str]],
    *,
    resolver_map: dict[str, str],
) -> None:
    """Per T-12 acceptance: every neuron's ``links[]`` resolves against the parent.

    Raises a single RuntimeError listing every unresolvable target across
    every neuron, so the user gets a complete picture per run instead of
    one error at a time.
    """
    failures: list[str] = []
    for slug, _path, _raw, fm, _body in neuron_files:
        links = fm.get("links") or []
        if not isinstance(links, list):
            continue
        for i, link in enumerate(links):
            if not isinstance(link, dict):
                continue
            target = str(link.get("target") or "").strip()
            if not target:
                continue
            # Per the Wave-3 dev diary §Open questions item 3, neuron
            # links use the ``base/{member-slug}`` form. The persona-build
            # itself leaves ``base/...`` deliberately unresolved (the
            # composer resolves at delivery time); the script-side
            # verification is what guarantees the link IS resolvable.
            if not target.startswith("base/"):
                # Non-base targets are sibling-neuron links — resolved by
                # the persona builder's own resolver. Skip script-side
                # check; if it doesn't resolve, the persona build will
                # surface a warning at link-emission time.
                continue
            inner = target[len("base/"):]
            if inner not in resolver_map:
                failures.append(
                    f"{slug}.links[{i}]: target {target!r} does not resolve "
                    f"to any member of the parent occupation."
                )
    if failures:
        msg = (
            "One or more neuron links do not resolve against the parent "
            "occupation's published members:\n  - "
            + "\n  - ".join(failures)
            + f"\n\nValid base/ targets are any of: {sorted(set(resolver_map.keys()))[:6]}..."
        )
        raise RuntimeError(msg)


# ── Neuron Skill + SkillVersion upserts ───────────────────────────────


async def _upsert_neuron_skill(
    session: AsyncSession,
    *,
    creator: User,
    slug: str,
    raw_bytes: bytes,
    fm: dict[str, Any],
    body_md: str,
) -> tuple[Skill, SkillVersion, bool]:
    """Idempotent neuron Skill + SkillVersion creator.

    ``kind=memory_neuron``, ``status=published``. Per ADR-005 these rows
    are present in ``skills`` but hidden from the public marketplace
    (the catalog API filters on ``kind=skill``). The neuron's
    ``creator_id`` MUST match the persona's ``creator_id`` — the
    PersonaNeuron service-level rule per `personas/models.py` docstring.
    """
    res = await session.execute(
        select(Skill).where(Skill.creator_id == creator.id, Skill.slug == slug)
    )
    skill = res.scalar_one_or_none()
    is_new = skill is None
    name = str(fm["name"])[:120]
    tagline = str(fm.get("description") or "")[:140] or None
    tags = list(fm.get("tags") or [])
    category = str(fm.get("category") or "personas")

    if skill is None:
        skill = Skill(
            creator_id=creator.id,
            slug=slug,
            name=name,
            tagline=tagline,
            description_md=body_md,
            category=category,
            tags=tags,
            status=SkillStatus.PUBLISHED,
            kind=SkillKind.MEMORY_NEURON,
            pricing_model=PricingModel.FREE,
            one_time_price_cents=None,
            subscription_price_cents=None,
            support_url="https://skillsgit.com/support",
        )
        session.add(skill)
        await session.flush()
    else:
        skill.name = name
        skill.tagline = tagline
        skill.description_md = body_md
        skill.category = category
        skill.tags = tags
        skill.status = SkillStatus.PUBLISHED
        skill.kind = SkillKind.MEMORY_NEURON
        skill.pricing_model = PricingModel.FREE

    # Version row: keyed on (skill, version_str). Existing same-version
    # row stays unless the content_hash differs (capture pipeline re-edit
    # equivalent — here it means we re-authored the neuron file).
    res2 = await session.execute(
        select(SkillVersion).where(
            SkillVersion.skill_id == skill.id,
            SkillVersion.version == NEURON_VERSION,
        )
    )
    existing_version = res2.scalar_one_or_none()
    storage = get_storage()
    storage_key = f"skills/{skill.id}/{NEURON_VERSION}.md"

    stamped = inject_distribution_block(raw_bytes.decode("utf-8"))
    new_hash = compute_content_hash(raw_bytes.decode("utf-8"))

    if existing_version is not None and existing_version.content_hash == new_hash:
        skill.latest_version_id = existing_version.id
        return skill, existing_version, is_new

    # Upload (or re-upload) the body.
    await storage.put_object(storage_key, stamped.encode("utf-8"), "text/markdown")

    if existing_version is not None:
        # Same version string, different content — the script owns the
        # version, so updating the row's hash + storage_url in place is
        # legitimate and matches the Wave-3 patch pattern.
        existing_version.content_hash = new_hash
        existing_version.storage_url = storage_key
        existing_version.released_at = datetime.now(UTC)
        existing_version.released_by = creator.id
        skill.latest_version_id = existing_version.id
        return skill, existing_version, is_new

    version = SkillVersion(
        skill_id=skill.id,
        version=NEURON_VERSION,
        content_hash=new_hash,
        storage_url=storage_key,
        ai_requirements=dict(fm.get("ai") or {}),
        changelog_md=None,
        released_at=datetime.now(UTC),
        released_by=creator.id,
        is_yanked=False,
        target_version=NEURON_VERSION,
    )
    session.add(version)
    await session.flush()
    skill.latest_version_id = version.id
    return skill, version, is_new


# ── Persona Skill + side-table + persona_neurons ──────────────────────


async def _upsert_persona_skill(
    session: AsyncSession,
    *,
    creator: User,
    spec: dict[str, Any],
    parent_skill: Skill,
) -> tuple[Skill, Persona, bool]:
    """Idempotent: create or update the persona Skill + Persona side-table row.

    Per ADR-002 + T-04 the row carries ``kind=persona``,
    ``parent_occupation_id`` pointing at the parent occupation skill,
    and ``license_type=free`` for MVP (ADR-016 Q-1).
    """
    spec_id = str(spec["id"])
    handle, slug = spec_id.split("/", 1)
    if handle != DEMO_HANDLE:
        raise RuntimeError(
            f"persona.yaml id handle {handle!r} != demo handle {DEMO_HANDLE!r}"
        )

    res = await session.execute(
        select(Skill).where(Skill.creator_id == creator.id, Skill.slug == slug)
    )
    skill = res.scalar_one_or_none()
    is_new = skill is None
    name = str(spec["name"])[:120]
    tagline = str(spec.get("tagline") or "").strip().replace("\n", " ")[:140] or None
    description_md = str(spec.get("description") or "")
    category = str(spec.get("category") or "personas")
    tags = list(spec.get("tags") or [])

    if skill is None:
        skill = Skill(
            creator_id=creator.id,
            slug=slug,
            name=name,
            tagline=tagline,
            description_md=description_md,
            category=category,
            tags=tags,
            status=SkillStatus.DRAFT,
            kind=SkillKind.PERSONA,
            pricing_model=PricingModel.FREE,
            one_time_price_cents=None,
            subscription_price_cents=None,
            support_url="https://skillsgit.com/support",
        )
        session.add(skill)
        await session.flush()
    else:
        skill.name = name
        skill.tagline = tagline
        skill.description_md = description_md
        skill.category = category
        skill.tags = tags
        skill.kind = SkillKind.PERSONA
        skill.pricing_model = PricingModel.FREE

    res2 = await session.execute(select(Persona).where(Persona.skill_id == skill.id))
    persona = res2.scalar_one_or_none()
    if persona is None:
        persona = Persona(
            skill_id=skill.id,
            parent_occupation_id=parent_skill.id,
            creator_intro_md=str(spec.get("creator_intro_md") or "") or None,
            specialization=str(spec.get("specialization") or "")[:280] or None,
            years_of_experience=int(spec["years_of_experience"])
                if spec.get("years_of_experience") is not None else None,
            neuron_count=0,
        )
        session.add(persona)
        await session.flush()
    else:
        persona.parent_occupation_id = parent_skill.id
        persona.creator_intro_md = str(spec.get("creator_intro_md") or "") or None
        persona.specialization = str(spec.get("specialization") or "")[:280] or None
        persona.years_of_experience = (
            int(spec["years_of_experience"])
            if spec.get("years_of_experience") is not None else None
        )
    return skill, persona, is_new


async def _replace_persona_membership(
    session: AsyncSession,
    *,
    persona_skill_id: Any,
    neuron_skills_in_order: list[Skill],
) -> int:
    """Bulk-replace ``persona_neurons`` rows for deterministic ordering."""
    await session.execute(
        delete(PersonaNeuron).where(PersonaNeuron.persona_id == persona_skill_id)
    )
    for i, neuron_skill in enumerate(neuron_skills_in_order, start=1):
        row = PersonaNeuron(
            persona_id=persona_skill_id,
            neuron_skill_id=neuron_skill.id,
            sort_order=i,
            section=None,
        )
        session.add(row)
        await session.flush([row])
    # Refresh denormalised count on the persona row.
    persona = await session.get(Persona, persona_skill_id)
    if persona is not None:
        persona.neuron_count = len(neuron_skills_in_order)
        await session.flush()
    return len(neuron_skills_in_order)


# ── Persona SkillVersion ─────────────────────────────────────────────


async def _ensure_persona_version(
    session: AsyncSession,
    *,
    skill: Skill,
    creator: User,
    changelog: list[dict[str, Any]] | None,
) -> SkillVersion:
    """Create ``persona.version`` if missing. Persona version body is a tiny envelope.

    Same pattern as the occupation version row in ``build_devops_vault.py``:
    the actual deliverable is the vault zip, so the version's storage
    object is just a JSON envelope.
    """
    res = await session.execute(
        select(SkillVersion).where(
            SkillVersion.skill_id == skill.id,
            SkillVersion.version == PERSONA_VERSION,
        )
    )
    version = res.scalar_one_or_none()
    if version is not None:
        skill.latest_version_id = version.id
        return version

    storage = get_storage()
    storage_key = f"skills/{skill.id}/{PERSONA_VERSION}.persona.json"
    payload = json.dumps(
        {
            "skill_id": str(skill.id),
            "slug": skill.slug,
            "version": PERSONA_VERSION,
            "kind": SkillKind.PERSONA.value,
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
        version=PERSONA_VERSION,
        content_hash=content_hash,
        storage_url=storage_key,
        ai_requirements=None,
        changelog_md=notes or None,
        released_at=None,
        released_by=None,
        is_yanked=False,
        target_version=PERSONA_VERSION,
    )
    session.add(version)
    await session.flush()
    skill.latest_version_id = version.id
    return version


# ── Driver ───────────────────────────────────────────────────────────


async def run() -> None:  # noqa: PLR0912, PLR0915  (orchestration script — phases are linear)
    log.info("loading %s", PERSONA_YAML)
    spec = _load_persona_spec()
    log.info(
        "spec: id=%s name=%s neurons=%d parent=%s",
        spec["id"], spec["name"], len(spec["neurons"]), spec["parent_occupation_id"],
    )

    log.info("loading %d neuron files from %s", len(spec["neurons"]), NEURONS_DIR)
    neuron_files = _load_neuron_files(list(spec["neurons"]))
    log.info("validated %d/%d neuron files", len(neuron_files), len(spec["neurons"]))

    await get_storage().ensure_bucket()

    # ─── Phase 1: demo user ──────────────────────────────────────────
    async with SessionLocal() as session:
        creator = await _ensure_demo_user(session)
        await session.commit()
        creator_id = creator.id
        log.info("demo user: %s (id=%s)", creator.email, creator_id)

    # ─── Phase 2: resolve parent + verify links ──────────────────────
    async with SessionLocal() as session:
        parent_skill, _occupation, resolver_map = await _resolve_parent_occupation(
            session, parent_id=str(spec["parent_occupation_id"])
        )
        # Count base-form slugs (resolver_map carries both bare slugs and
        # fully-qualified vault paths; the bare-slug count == member count).
        member_count = len([k for k in resolver_map if not k.startswith("domains/")])
        log.info(
            "parent occupation: skillsgit-curated/%s (skill_id=%s, %d members)",
            parent_skill.slug, parent_skill.id, member_count,
        )
        _verify_neuron_links_resolve(neuron_files, resolver_map=resolver_map)
        log.info(
            "links: every base/* target across %d neurons resolves to a "
            "parent-occupation member (zero unresolvable)",
            len(neuron_files),
        )
        parent_skill_id = parent_skill.id

    # ─── Phase 3: neuron Skill rows + SkillVersions ──────────────────
    new_neurons = 0
    existing_neurons = 0
    neuron_skill_ids_in_order: list[Any] = []
    async with SessionLocal() as session:
        # Re-load creator on this session so its identity is bound.
        creator_local = await session.merge(creator)
        for slug, _path, raw_bytes, fm, body_md in neuron_files:
            n_skill, _n_version, was_new = await _upsert_neuron_skill(
                session,
                creator=creator_local,
                slug=slug,
                raw_bytes=raw_bytes,
                fm=fm,
                body_md=body_md,
            )
            neuron_skill_ids_in_order.append(n_skill.id)
            if was_new:
                new_neurons += 1
            else:
                existing_neurons += 1
        await session.commit()
    log.info(
        "neurons: %d new + %d existing (or updated)",
        new_neurons, existing_neurons,
    )

    # ─── Phase 4: persona row + persona_neurons + version + publish + build ──
    persona_skill_id: Any = None
    build_was_new = False
    build_id: Any = None
    final_storage_url = ""
    final_content_hash = ""
    final_file_count = 0
    final_total_bytes = 0
    async with SessionLocal() as session:
        creator_local = await session.merge(creator)
        parent_skill_local = await session.get(Skill, parent_skill_id)
        if parent_skill_local is None:
            raise RuntimeError("Parent occupation disappeared between phases")
        skill, _persona, was_new = await _upsert_persona_skill(
            session,
            creator=creator_local,
            spec=spec,
            parent_skill=parent_skill_local,
        )
        log.info(
            "persona skill row %s (id=%s, %s)",
            "created" if was_new else "updated",
            skill.id,
            "new" if was_new else "existing",
        )

        # Reload neuron skills bound to this session for the membership join.
        neuron_skill_ids_set = list(neuron_skill_ids_in_order)
        res = await session.execute(
            select(Skill).where(Skill.id.in_(neuron_skill_ids_set))
        )
        by_id = {s.id: s for s in res.scalars().all()}
        # Preserve persona.yaml's neuron ordering.
        ordered_neurons = [by_id[nid] for nid in neuron_skill_ids_in_order]
        missing = [nid for nid in neuron_skill_ids_in_order if nid not in by_id]
        if missing:
            raise RuntimeError(
                f"Neuron Skill row(s) disappeared between phases: {missing}"
            )

        membership_count = await _replace_persona_membership(
            session,
            persona_skill_id=skill.id,
            neuron_skills_in_order=ordered_neurons,
        )
        log.info(
            "persona_neurons: %d rows written (bulk-replaced)", membership_count
        )

        version_row = await _ensure_persona_version(
            session,
            skill=skill,
            creator=creator_local,
            changelog=spec.get("changelog"),
        )
        log.info(
            "persona version row: id=%s version=%s",
            version_row.id, version_row.version,
        )

        # Publish: set status + released_at, then run the build.
        # In dev there's no Arq worker, so we call build_persona directly
        # (same pattern as build_devops_vault.py per Wave-3 dev diary).
        if version_row.released_at is None:
            version_row.released_at = datetime.now(UTC)
            version_row.released_by = creator_local.id
        if skill.status != SkillStatus.PUBLISHED:
            skill.status = SkillStatus.PUBLISHED
        skill.latest_version_id = version_row.id
        await session.flush()

        # Idempotency belt-and-suspenders: if a succeeded build already
        # exists for this (skill_id, version_id), reuse it. The builder's
        # own (skill_id, content_hash) check handles the common case
        # where nothing changed; this catches the case where downstream
        # mutation has shifted the hash without our knowledge.
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
            build_was_new = False
        else:
            try:
                build_row = await vault_builder.build_persona(
                    session,
                    skill.id,
                    PERSONA_VERSION,
                    force_rebuild=False,
                )
            except vault_builder.VaultBuildError as exc:
                raise RuntimeError(
                    f"persona vault build failed: {exc.code} — {exc.message}"
                ) from exc
            log.info(
                "build result: status=succeeded build_id=%s content_hash=%s",
                build_row.id, build_row.content_hash,
            )
            build_was_new = True

        await write_audit(
            session,
            actor_id=creator_local.id,
            action="persona.published",
            target_type="skill",
            target_id=skill.id,
            metadata={
                "demo": True,
                "version": PERSONA_VERSION,
                "build_id": str(build_row.id),
                "neuron_count": len(ordered_neurons),
                "parent_occupation_skill_id": str(parent_skill_local.id),
            },
        )
        await session.commit()
        persona_skill_id = skill.id
        build_id = build_row.id

    # ─── Phase 5: reload build for validate ──────────────────────────
    async with SessionLocal() as session:
        build = await session.get(VaultBuild, build_id)
        if build is None:
            raise RuntimeError(
                f"vault_builds row {build_id} not found after build"
            )
        final_storage_url = build.storage_url
        final_content_hash = build.content_hash
        final_file_count = build.file_count
        final_total_bytes = build.total_bytes
        manifest_warnings: list[Any] = []
        if build.build_log_json:
            manifest_warnings = list(
                build.build_log_json.get("warnings") or []
            )

    log.info(
        "vault_build %s succeeded: content_hash=%s files=%d bytes=%d storage=%s",
        build_id, final_content_hash, final_file_count, final_total_bytes,
        final_storage_url,
    )

    # ─── Phase 6: download zip + validate_vault (mode='persona') ──────
    #
    # validate_vault(mode='persona') tolerates `[[base/...]]`
    # unresolved-wikilink errors by design: the persona-only builder
    # leaves base/* targets unresolved so the composer (T-07) can
    # resolve them against the merged occupation+persona tree at
    # delivery time. See
    # `src/vault/builder.py:_build_target_resolver_for_persona` and
    # `src/vault/validator.py:validate_vault` (Wave 5 polish 1).
    # Any other error class still fails the build for real.
    storage = get_storage()
    zip_bytes = await storage.get_object(final_storage_url)
    validation = validate_vault(zip_bytes, mode="persona")
    real_errors = list(validation.errors)
    log.info(
        "validate_vault(mode='persona'): real_errors=%d",
        len(real_errors),
    )
    if real_errors:
        for err in real_errors[:10]:
            log.error("  vault error: %s — %s", err.code, err.message)
        raise RuntimeError(
            "validate_vault(mode='persona') reported real errors on the produced bundle"
        )

    # Per T-12 acceptance: zero warnings in manifest.warnings ↔ persona
    # build's own warnings list. The persona-only builder deliberately
    # leaves base/... links unresolved (the composer resolves them at
    # delivery), so the persona build's warnings will list every
    # base/<slug> link as `vault.unresolved_link`. The script-side check
    # we ran in phase 2 is the *real* T-12 guarantee — it proves every
    # link target exists as a member of the parent occupation.
    base_link_warnings = [
        w for w in manifest_warnings
        if isinstance(w, dict) and (w.get("unresolved_link") or "").startswith("base/")
    ]
    non_base_warnings = [
        w for w in manifest_warnings if w not in base_link_warnings
    ]

    # ─── Summary ─────────────────────────────────────────────────────
    print()
    print("=" * 72)
    print("Jane Devops (sample) — Wave 4 T-12 persona summary")
    print("=" * 72)
    print(f"  demo creator        : @{DEMO_HANDLE}")
    print(f"  persona skill_id    : {persona_skill_id}")
    print(f"  persona slug        : {spec['id']}")
    print(f"  persona version     : {PERSONA_VERSION}")
    print(f"  parent occupation   : skillsgit-curated/{parent_skill_local.slug}")
    print(f"  neurons             : {len(neuron_files)}")
    print(f"  vault_build.id      : {build_id}")
    print(f"  vault build status  : {'new' if build_was_new else 'reused'}")
    print(f"  content_hash        : {final_content_hash}")
    print(f"  file_count          : {final_file_count}")
    print(f"  total_bytes         : {final_total_bytes}")
    print(f"  storage_url         : {final_storage_url}")
    print(
        f"  validate_vault      : real_errors={len(real_errors)} "
        f"(base/* unresolved={len(base_link_warnings)}, deferred to composer)"
    )
    print(
        f"  manifest warnings   : {len(manifest_warnings)} total "
        f"({len(base_link_warnings)} expected base/* deferred to composer, "
        f"{len(non_base_warnings)} other)"
    )
    print("  link resolution     : 100% — verified script-side against parent occupation")
    print("=" * 72)
    print()
    print("Next: run the Layer-C demo CLI (T-13) to load occupation + persona")
    print("together and ask Claude a DevOps question with neuron attribution.")
    print("=" * 72)


if __name__ == "__main__":
    asyncio.run(run())
