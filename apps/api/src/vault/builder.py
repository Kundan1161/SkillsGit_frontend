"""Vault builder — produces an Obsidian-compatible zip per occupation/persona.

Spec: ``team/03-vault-generation.md`` §1, §2, §5, §7, §12.
ADR-010 (attribution comments), ADR-011 (ASCII-kebab filenames),
ADR-013 (immutable build artifacts).

Entry points:

* :func:`build_occupation` — assemble the ``base/`` tree + ``README.md``,
  ``00-index.md``, ``vault.json`` for an occupation's published members.
* :func:`build_persona` — assemble the ``personas/<handle>/<slug>/``
  subtree + a partial ``vault.json`` fragment for a single persona.

Both are idempotent: if a build with the same ``(skill_id, content_hash)``
already exists and ``force_rebuild=False`` we return the existing
:class:`~src.vault.models.VaultBuild` row without re-uploading.

The zip is deterministic — same inputs yield byte-identical output —
because we sort the filename list before writing and pin each
:class:`zipfile.ZipInfo` to ``EPOCH_TIMESTAMP``. The content_hash is
the SHA-256 of those zip bytes.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import re
import uuid
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Literal

from sqlalchemy import select

from src.occupations.models import Occupation, OccupationMemberRole, OccupationSkill
from src.personas.models import Persona, PersonaNeuron
from src.skills.models import Skill, SkillKind, SkillVersion
from src.skills.parser import split_frontmatter
from src.storage.s3 import get_storage
from src.users.models import CreatorProfile, User
from src.vault.manifest import (
    BuildBlock,
    FileEntry,
    ManifestLinkEntry,
    ManifestNeuronBlock,
    OccupationSummary,
    PersonaSummary,
    VaultManifest,
    Warning,  # noqa: A004 — this is the manifest's Warning shape, not Python's
    write_manifest,
)
from src.vault.models import VaultBuild, VaultBuildStatus

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


# ── Determinism constants ────────────────────────────────────────────


# Pinned timestamp used for every ZipInfo so re-builds with the same
# inputs produce byte-identical archives. The exact value is arbitrary;
# we use the cycle-1 reference date from the architect's brief.
EPOCH_TIMESTAMP: tuple[int, int, int, int, int, int] = (2026, 1, 1, 0, 0, 0)
EPOCH_DATETIME: datetime = datetime(*EPOCH_TIMESTAMP, tzinfo=UTC)

# ASCII-kebab filename rule from ADR-011 / 03-vault-generation.md §1.
_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Hard cap from 03-vault-generation.md §12.
MAX_VAULT_BYTES: int = 50 * 1024 * 1024

# Allowed link relations — mirror of LinkRelation enum, duplicated as a
# tuple here so the manifest layer doesn't need an import cycle.
_ALLOWED_RELATIONS = frozenset(
    {"applies", "extends", "contradicts", "see-also", "recorded-instance-of"}
)


# ── Errors ──────────────────────────────────────────────────────────


class VaultBuildError(Exception):
    """Raised when a build cannot proceed.

    Carries a stable ``code`` so the calling Arq job can write a
    structured error to ``vault_builds.error``.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


# ── Filename validation ─────────────────────────────────────────────


def _validate_slug(slug: str, *, what: str) -> None:
    if not slug or len(slug) > 80 or not _KEBAB_RE.match(slug):
        raise VaultBuildError(
            code="vault_build.invalid_filename",
            message=(
                f"{what} {slug!r} is not a valid ASCII kebab slug "
                "(≤80 chars, lowercase letters/digits/hyphens, no "
                "leading/trailing hyphens, no underscores)."
            ),
        )


# ── Loaded view of an occupation/persona ────────────────────────────


@dataclass
class _MemberFile:
    """One markdown file destined for the vault."""

    vault_path: str
    skill: Skill
    version: SkillVersion
    creator_handle: str
    body_bytes: bytes
    # Parsed lazily on first use.
    _frontmatter: dict[str, Any] | None = None
    _body_md: str | None = None

    def parsed(self) -> tuple[dict[str, Any], str]:
        if self._frontmatter is None:
            try:
                fm, body = split_frontmatter(self.body_bytes)
            except ValueError as exc:
                raise VaultBuildError(
                    code="vault_build.malformed_member",
                    message=(
                        f"Member file {self.vault_path} has malformed "
                        f"frontmatter: {exc}"
                    ),
                ) from exc
            self._frontmatter = fm
            self._body_md = body
        # Mypy needs the assertion since the field types are Optional.
        assert self._frontmatter is not None
        assert self._body_md is not None
        return self._frontmatter, self._body_md


# ── Loaders ──────────────────────────────────────────────────────────


async def _resolve_creator_handle(
    session: AsyncSession, *, user_id: uuid.UUID
) -> str:
    """Return the creator handle for a user, falling back to display_name."""
    res = await session.execute(
        select(CreatorProfile).where(CreatorProfile.user_id == user_id)
    )
    profile = res.scalar_one_or_none()
    if profile is not None:
        return profile.handle
    user = await session.get(User, user_id)
    if user is not None and user.display_name:
        return user.display_name
    return "unknown"


async def _load_skill_body(version: SkillVersion) -> bytes:
    """Fetch the canonical body bytes for a version from object storage.

    Raises :class:`VaultBuildError` with ``vault_build.member_missing``
    if the storage object is gone — that means the publish pipeline left
    the version row in an inconsistent state and we cannot build.
    """
    storage = get_storage()
    try:
        raw = await storage.get_object(version.storage_url)
    except Exception as exc:
        raise VaultBuildError(
            code="vault_build.member_missing",
            message=(
                f"Storage object {version.storage_url} for SkillVersion "
                f"{version.id} is missing or unreachable."
            ),
        ) from exc
    return raw


def _pick_version(
    skill: Skill, *, version: str | None
) -> SkillVersion | None:
    """Pick a version to bundle.

    If ``version`` is given, match by string; else pick the latest
    released non-yanked version, else the most recent any-state version.
    """
    if not skill.versions:
        return None
    if version is not None:
        for v in skill.versions:
            if v.version == version:
                return v
        return None
    # latest released first.
    released = [v for v in skill.versions if v.released_at is not None and not v.is_yanked]
    if released:
        released.sort(key=lambda v: v.released_at or datetime.min, reverse=True)
        return released[0]
    # fall back to the freshest row.
    fallback = sorted(skill.versions, key=lambda v: v.version, reverse=True)
    return fallback[0]


async def _load_occupation_files(
    session: AsyncSession, *, occupation_skill_id: uuid.UUID
) -> tuple[Skill, Occupation, list[tuple[OccupationSkill, _MemberFile]]]:
    """Load the parent occupation + every member's body bytes.

    Members are returned in (sort_order, slug) order so the resulting
    zip is deterministic.
    """
    skill = await session.get(Skill, occupation_skill_id)
    if skill is None or skill.kind != SkillKind.OCCUPATION:
        raise VaultBuildError(
            code="vault_build.not_found",
            message=f"Occupation skill {occupation_skill_id} not found.",
        )
    occupation = await session.get(Occupation, occupation_skill_id)
    if occupation is None:
        raise VaultBuildError(
            code="vault_build.not_found",
            message=f"Occupation side-table row for {occupation_skill_id} missing.",
        )

    members_res = await session.execute(
        select(OccupationSkill).where(
            OccupationSkill.occupation_id == occupation_skill_id
        )
    )
    membership_rows = list(members_res.scalars().all())
    if not membership_rows:
        raise VaultBuildError(
            code="vault_build.empty_membership",
            message=(
                f"Occupation {occupation_skill_id} has no members. "
                "Add at least one occupation_skills row before building."
            ),
        )

    out: list[tuple[OccupationSkill, _MemberFile]] = []
    for membership in membership_rows:
        member_skill = await session.get(Skill, membership.member_skill_id)
        if member_skill is None:
            raise VaultBuildError(
                code="vault_build.member_missing",
                message=(
                    f"Member skill {membership.member_skill_id} not found "
                    f"(occupation {occupation_skill_id})."
                ),
            )
        # Bundle only members that are kind=skill (per ADR-004 / occupation
        # service validation; defensive recheck at build time).
        if member_skill.kind != SkillKind.SKILL:
            raise VaultBuildError(
                code="vault_build.invalid_member_kind",
                message=(
                    f"Member {member_skill.id} has kind={member_skill.kind.value}; "
                    "occupations can only bundle kind='skill' members."
                ),
            )
        # Eager-load versions for this skill.
        await session.refresh(member_skill, attribute_names=["versions"])
        version = _pick_version(member_skill, version=None)
        if version is None:
            raise VaultBuildError(
                code="vault_build.no_published_version",
                message=(
                    f"Member {member_skill.slug} has no published version. "
                    "Publish a version before bundling."
                ),
            )
        body = await _load_skill_body(version)
        creator_handle = await _resolve_creator_handle(
            session, user_id=member_skill.creator_id
        )

        # Validate the slug — the publish pipeline already enforces this
        # but we recheck at the vault boundary per ADR-011.
        _validate_slug(member_skill.slug, what="member slug")
        domain = membership.domain or "uncategorised"
        _validate_slug(domain, what="domain slug")

        vault_path = f"domains/{domain}/{member_skill.slug}.md"
        out.append(
            (
                membership,
                _MemberFile(
                    vault_path=vault_path,
                    skill=member_skill,
                    version=version,
                    creator_handle=creator_handle,
                    body_bytes=body,
                ),
            )
        )

    out.sort(key=lambda pair: (pair[0].sort_order, pair[1].skill.slug))
    return skill, occupation, out


async def _load_persona_files(
    session: AsyncSession, *, persona_skill_id: uuid.UUID
) -> tuple[Skill, Persona, str, list[tuple[PersonaNeuron, _MemberFile]]]:
    """Load the parent persona + every neuron's body bytes."""
    skill = await session.get(Skill, persona_skill_id)
    if skill is None or skill.kind != SkillKind.PERSONA:
        raise VaultBuildError(
            code="vault_build.not_found",
            message=f"Persona skill {persona_skill_id} not found.",
        )
    persona = await session.get(Persona, persona_skill_id)
    if persona is None:
        raise VaultBuildError(
            code="vault_build.not_found",
            message=f"Persona side-table row for {persona_skill_id} missing.",
        )

    creator_handle = await _resolve_creator_handle(
        session, user_id=skill.creator_id
    )
    _validate_slug(creator_handle, what="creator handle")
    _validate_slug(skill.slug, what="persona slug")

    neurons_res = await session.execute(
        select(PersonaNeuron).where(PersonaNeuron.persona_id == persona_skill_id)
    )
    neuron_rows = list(neurons_res.scalars().all())
    if not neuron_rows:
        raise VaultBuildError(
            code="vault_build.no_neurons",
            message=(
                f"Persona {persona_skill_id} has zero neurons. Add at "
                "least one kind=memory_neuron via the capture flow first."
            ),
        )

    out: list[tuple[PersonaNeuron, _MemberFile]] = []
    for row in neuron_rows:
        neuron_skill = await session.get(Skill, row.neuron_skill_id)
        if neuron_skill is None:
            raise VaultBuildError(
                code="vault_build.member_missing",
                message=(
                    f"Neuron skill {row.neuron_skill_id} not found "
                    f"(persona {persona_skill_id})."
                ),
            )
        if neuron_skill.kind != SkillKind.MEMORY_NEURON:
            raise VaultBuildError(
                code="vault_build.invalid_member_kind",
                message=(
                    f"Persona member {neuron_skill.id} has kind="
                    f"{neuron_skill.kind.value}; expected memory_neuron."
                ),
            )
        await session.refresh(neuron_skill, attribute_names=["versions"])
        version = _pick_version(neuron_skill, version=None)
        if version is None:
            raise VaultBuildError(
                code="vault_build.no_published_version",
                message=(
                    f"Neuron {neuron_skill.slug} has no published version."
                ),
            )
        body = await _load_skill_body(version)
        _validate_slug(neuron_skill.slug, what="neuron slug")

        section = row.section
        if section is not None:
            _validate_slug(section, what="neuron section")
            vault_path = (
                f"personas/{creator_handle}/{skill.slug}/neurons/"
                f"{section}/{neuron_skill.slug}.md"
            )
        else:
            vault_path = (
                f"personas/{creator_handle}/{skill.slug}/neurons/"
                f"{neuron_skill.slug}.md"
            )
        out.append(
            (
                row,
                _MemberFile(
                    vault_path=vault_path,
                    skill=neuron_skill,
                    version=version,
                    creator_handle=creator_handle,
                    body_bytes=body,
                ),
            )
        )

    out.sort(key=lambda pair: (pair[0].sort_order, pair[1].skill.slug))
    return skill, persona, creator_handle, out


# ── File body emission ──────────────────────────────────────────────


def _emit_linked_notes_section(
    links: list[dict[str, Any]],
    *,
    target_resolver: Callable[[str], str] | None = None,
) -> str:
    """Render the auto-appended ``## Linked notes`` footer per spec §2."""
    if not links:
        return ""
    lines = ["## Linked notes", ""]
    for link in links:
        target = str(link.get("target") or "").strip()
        relation = str(link.get("relation") or "see-also")
        if relation not in _ALLOWED_RELATIONS:
            relation = "see-also"
        if not target:
            continue
        resolved = target_resolver(target) if target_resolver else target
        lines.append(f"- [[{resolved}]] — {relation}")
    lines.append("")
    return "\n".join(lines)


def _emit_attribution_comment(file_entry: FileEntry, built_at: datetime) -> str:
    """Build the trailing ``<!-- skg-attribution: ... -->`` block per ADR-010."""
    lines = [
        "<!-- skg-attribution:",
        f"  vault_path: {json.dumps(file_entry.vault_path)}",
        f"  skill_id: {json.dumps(file_entry.skill_id)}",
        f"  version: {json.dumps(file_entry.version)}",
        f"  kind: {json.dumps(file_entry.kind)}",
        f"  creator_handle: {json.dumps(file_entry.creator_handle)}",
        f"  content_hash: {json.dumps(file_entry.content_hash)}",
        f"  built_at: {json.dumps(built_at.isoformat().replace('+00:00', 'Z'))}",
        "-->",
    ]
    return "\n".join(lines) + "\n"


def _emit_file_body(
    member: _MemberFile,
    file_entry: FileEntry,
    built_at: datetime,
    *,
    target_resolver: Callable[[str], str] | None,
) -> bytes:
    """Build the final bytes for one member's .md file.

    Layout per ``03-vault-generation.md`` §7:

    1. ``---`` frontmatter ``---``
    2. body markdown
    3. ``## Linked notes`` section (auto-generated)
    4. ``<!-- skg-attribution: ... -->`` comment

    We pass the raw bytes through unchanged for the frontmatter+body so
    the canonical ``content_hash`` on ``SkillVersion`` still maps to a
    bytewise prefix of the emitted file. The Linked notes + attribution
    comment are appended.
    """
    raw_text = member.body_bytes.decode("utf-8")
    raw_text = raw_text.rstrip("\n")

    linked_notes = _emit_linked_notes_section(
        [link.model_dump() for link in file_entry.links],
        target_resolver=target_resolver,
    )
    attribution = _emit_attribution_comment(file_entry, built_at)

    parts: list[str] = [raw_text]
    if linked_notes:
        parts.append("")  # blank line between body and Linked notes
        parts.append(linked_notes.rstrip("\n"))
    parts.append("")
    parts.append(attribution.rstrip("\n"))
    parts.append("")
    out = "\n".join(parts)
    return out.encode("utf-8")


# ── README + index ──────────────────────────────────────────────────


def _emit_readme_occupation(
    skill: Skill,
    creator_handle: str,
    occupation: Occupation,
    members: list[tuple[OccupationSkill, _MemberFile]],
    *,
    built_at: datetime,
    version: str,
) -> bytes:
    domains = list(occupation.domains or [])
    summary = (occupation.summary_md or skill.description_md or "").strip()
    timestamp = built_at.isoformat().replace("+00:00", "Z")
    text = (
        f"# {skill.name} — v{version}\n\n"
        f"> A curated, graph-linked vault of methodology for the "
        f"{skill.name} role. Built by @{creator_handle}.\n\n"
        "## What's in this vault\n\n"
        f"- {len(members)} base methodology skills across "
        f"{len(domains) or 1} domain(s)"
        + (f" ({', '.join(domains)})" if domains else "")
        + ".\n"
        "- Compose with persona overlays for recorded situations and "
        "on-call decisions.\n\n"
    )
    if summary:
        text += f"## Summary\n\n{summary}\n\n"
    text += (
        "## How to use this vault\n\n"
        "1. Open the folder in **Obsidian** (no plugins required).\n"
        "2. Press `Ctrl-G` to view the graph.\n"
        "3. Start at `00-index.md`.\n"
        "4. Drop the vault folder into your AI agent's working directory; "
        "point your agent at `vault.json` for routing.\n\n"
        f"## Attribution\n\n"
        f"This vault was assembled at {timestamp} by Skills Git from:\n"
        f"- `@{creator_handle}/{skill.slug}` v{version}\n\n"
        f"See `vault.json` for the machine-readable manifest.\n\n"
        "## License\n\n"
        "Each file's license is governed by the buyer's purchase of the "
        "parent product. This bundle is per-buyer; the watermark in each "
        "file identifies the licensee. Redistribution is not permitted.\n"
    )
    return text.encode("utf-8")


def _emit_index_occupation(
    skill: Skill,
    occupation: Occupation,
    members: list[tuple[OccupationSkill, _MemberFile]],
) -> bytes:
    domains = list(occupation.domains or [])
    # Group by domain (membership.domain) then split by role.
    by_domain: dict[str, list[tuple[OccupationSkill, _MemberFile]]] = {}
    for membership, member in members:
        by_domain.setdefault(membership.domain or "uncategorised", []).append(
            (membership, member)
        )

    lines: list[str] = [f"# Index — {skill.name}", "", "## Base methodology", ""]
    ordered_domains: list[str] = []
    for d in domains:
        if d in by_domain:
            ordered_domains.append(d)
    extras = sorted(d for d in by_domain if d not in ordered_domains)
    ordered_domains.extend(extras)

    for domain in ordered_domains:
        domain_members = by_domain[domain]
        lines.append(f"### {domain}")
        lines.append("")
        # Split by role: core / supporting / optional.
        for role in (
            OccupationMemberRole.CORE,
            OccupationMemberRole.SUPPORTING,
            OccupationMemberRole.OPTIONAL,
        ):
            section = [m for m in domain_members if m[0].role == role]
            if not section:
                continue
            lines.append(f"**{role.value.capitalize()}**")
            lines.append("")
            for _membership, member in section:
                vault_link = member.vault_path.removesuffix(".md")
                lines.append(
                    f"- [[{vault_link}]] — {member.skill.tagline or member.skill.name}"
                )
            lines.append("")
        lines.append("")
    lines.append("## Personas")
    lines.append("")
    lines.append(
        "_None bundled in this base build. Composition adds personas at "
        "delivery time — see `vault.json` after composition._"
    )
    lines.append("")
    return "\n".join(lines).encode("utf-8")


def _emit_readme_persona(
    skill: Skill,
    persona: Persona,
    creator_handle: str,
    neurons: list[tuple[PersonaNeuron, _MemberFile]],
    *,
    built_at: datetime,
    version: str,
) -> bytes:
    intro = (persona.creator_intro_md or skill.description_md or "").strip()
    timestamp = built_at.isoformat().replace("+00:00", "Z")
    text = (
        f"# {skill.name} — v{version}\n\n"
        f"> A persona overlay by @{creator_handle}. "
        f"{persona.specialization or ''}\n\n"
        f"## What's in this overlay\n\n"
        f"- {len(neurons)} memory neuron(s) recording real situations, "
        "decisions, and outcomes.\n\n"
    )
    if intro:
        text += f"## About the practitioner\n\n{intro}\n\n"
    text += (
        f"## Attribution\n\n"
        f"This persona was assembled at {timestamp} by Skills Git.\n"
        f"- `@{creator_handle}/{skill.slug}` v{version}\n\n"
        "See `persona.json` for the machine-readable manifest fragment. "
        "Composition merges this overlay into the parent occupation vault "
        "at delivery time.\n"
    )
    return text.encode("utf-8")


# ── Zip writer ─────────────────────────────────────────────────────


def _write_zip(files: list[tuple[str, bytes]]) -> bytes:
    """Write a deterministic DEFLATE zip from sorted (path, bytes) pairs.

    Per ``03-vault-generation.md`` §12 we set every entry's timestamp to
    ``EPOCH_TIMESTAMP`` and use POSIX forward-slash paths. Two runs over
    the same content yield bytewise-identical zips.
    """
    # Defensive sort even though callers pre-sort.
    ordered = sorted(files, key=lambda pair: pair[0])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, data in ordered:
            info = zipfile.ZipInfo(filename=path, date_time=EPOCH_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)
    out = buf.getvalue()
    if len(out) > MAX_VAULT_BYTES:
        raise VaultBuildError(
            code="vault_build.too_large",
            message=(
                f"Vault exceeds {MAX_VAULT_BYTES // (1024 * 1024)} MB "
                f"hard cap (size={len(out)} bytes)."
            ),
        )
    return out


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _derive_vault_id(
    *,
    scope: Literal["occupation", "persona"],
    skill_id: str,
    version: str,
    file_entries: list[FileEntry],
) -> str:
    """Derive a stable UUID v4 string from build inputs.

    Two builds over the same inputs produce the same vault_id. The
    output is in canonical UUID format (with the version nibble set to
    4) so it serialises cleanly through the manifest's string field.
    """
    payload = json.dumps(
        {
            "scope": scope,
            "skill_id": skill_id,
            "version": version,
            "files": [
                {
                    "path": e.vault_path,
                    "skill_id": e.skill_id,
                    "version": e.version,
                    "content_hash": e.content_hash,
                    "links": [
                        {
                            "target": link.target,
                            "relation": link.relation,
                            "resolved": link.resolved,
                            "weight": link.weight,
                        }
                        for link in e.links
                    ],
                }
                for e in file_entries
            ],
        },
        sort_keys=True,
    ).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    # Stamp version-4 bits per RFC 4122 §4.4 for a syntactically-valid UUID.
    b = bytearray(digest[:16])
    b[6] = (b[6] & 0x0F) | 0x40  # version 4
    b[8] = (b[8] & 0x3F) | 0x80  # variant 10
    return str(uuid.UUID(bytes=bytes(b)))


# ── Manifest assembly helpers ───────────────────────────────────────


def _link_entries_for_member(
    member: _MemberFile,
    *,
    resolver: Callable[[str], str | None],
) -> tuple[list[ManifestLinkEntry], list[Warning]]:
    """Translate a member's raw ``links:`` frontmatter into manifest entries.

    Returns ``(entries, warnings)``. ``resolver(target)`` returns the
    final vault-relative path the link will reference (without the
    ``.md`` extension) or ``None`` if unresolved. Warnings are emitted
    for every dangling link so the manifest carries a complete diagnosis.
    """
    fm, _body = member.parsed()
    raw_links = fm.get("links") or []
    out: list[ManifestLinkEntry] = []
    warnings: list[Warning] = []
    if not isinstance(raw_links, list):
        return out, warnings
    for link in raw_links:
        if not isinstance(link, dict):
            continue
        target = str(link.get("target") or "").strip()
        if not target:
            continue
        relation_raw = str(link.get("relation") or "see-also")
        if relation_raw not in _ALLOWED_RELATIONS:
            relation_raw = "see-also"
        weight = link.get("weight")
        weight_val: float | None = None
        if isinstance(weight, (int, float)):
            try:
                w = float(weight)
                if 0.0 <= w <= 1.0:
                    weight_val = w
            except (TypeError, ValueError):
                weight_val = None
        resolved_path = resolver(target)
        resolved = resolved_path is not None
        if not resolved:
            warnings.append(
                Warning(
                    file=member.vault_path,
                    code="vault.unresolved_link",
                    unresolved_link=target,
                    message=(
                        f"Link target {target!r} did not resolve to a file "
                        f"in this build."
                    ),
                )
            )
        out.append(
            ManifestLinkEntry(
                target=resolved_path or target,
                relation=relation_raw,  # type: ignore[arg-type,unused-ignore]
                resolved=resolved,
                weight=weight_val,
            )
        )
    return out, warnings


def _build_target_resolver_for_occupation(
    members: list[tuple[OccupationSkill, _MemberFile]],
) -> Callable[[str], str | None]:
    """Return a callable that maps a frontmatter ``target`` to a vault path.

    Resolution order (see ``03-vault-generation.md`` §2):

    1. Exact vault-relative path (with or without ``.md`` suffix).
    2. Bare slug — matched against sibling member slugs.

    Returns ``None`` for unresolved targets so the caller can emit a
    warning.
    """
    by_slug: dict[str, str] = {}
    by_path: set[str] = set()
    for _, member in members:
        slug = member.skill.slug
        no_ext = member.vault_path.removesuffix(".md")
        by_slug[slug] = no_ext
        by_path.add(no_ext)

    def _resolve(target: str) -> str | None:
        cleaned = target.strip()
        no_ext = cleaned.removesuffix(".md")
        if no_ext in by_path:
            return no_ext
        if cleaned in by_slug:
            return by_slug[cleaned]
        return None

    return _resolve


def _build_target_resolver_for_persona(
    neurons: list[tuple[PersonaNeuron, _MemberFile]],
) -> Callable[[str], str | None]:
    """Resolver for a persona-only build.

    Resolves sibling neurons. Targets starting with ``base/`` are
    deliberately left unresolved here — the composer (T-07) re-runs link
    resolution against the merged tree where ``base/`` exists.
    """
    by_slug: dict[str, str] = {}
    by_path: set[str] = set()
    for _, member in neurons:
        slug = member.skill.slug
        no_ext = member.vault_path.removesuffix(".md")
        by_slug[slug] = no_ext
        by_path.add(no_ext)

    def _resolve(target: str) -> str | None:
        cleaned = target.strip()
        if cleaned.startswith("base/"):
            return None  # composer's job
        no_ext = cleaned.removesuffix(".md")
        if no_ext in by_path:
            return no_ext
        if cleaned in by_slug:
            return by_slug[cleaned]
        return None

    return _resolve


def _file_entry_for_member(
    member: _MemberFile,
    *,
    kind: Literal["skill", "occupation", "persona", "memory_neuron"],
    resolver: Callable[[str], str | None],
) -> tuple[FileEntry, list[Warning]]:
    fm, body = member.parsed()
    body_hash = _sha256(body.encode("utf-8"))
    tags = []
    raw_tags = fm.get("tags")
    if isinstance(raw_tags, list):
        tags = [str(t) for t in raw_tags if isinstance(t, (str, int, float))]
    neuron_block = fm.get("neuron")
    neuron: ManifestNeuronBlock | None = None
    if isinstance(neuron_block, dict) and {
        "situation",
        "decision",
        "outcome",
    }.issubset(neuron_block.keys()):
        try:
            neuron = ManifestNeuronBlock.model_validate(neuron_block)
        except Exception:
            neuron = None
    links, warnings = _link_entries_for_member(member, resolver=resolver)
    entry = FileEntry(
        vault_path=member.vault_path,
        skill_id=str(member.skill.id),
        version=member.version.version,
        kind=kind,
        creator_handle=member.creator_handle,
        content_hash=body_hash,
        tags=tags,
        links=links,
        links_resolved=all(link.resolved for link in links),
        neuron=neuron,
    )
    return entry, warnings


# ── Public entrypoints ──────────────────────────────────────────────


async def build_occupation(
    session: AsyncSession,
    occupation_skill_id: uuid.UUID,
    version: str,
    *,
    force_rebuild: bool = False,
) -> VaultBuild:
    """Build an occupation vault and upload the zip.

    Returns the :class:`VaultBuild` row. If ``force_rebuild=False`` and a
    build with the same ``(skill_id, content_hash)`` already exists, the
    existing row is returned without re-uploading.
    """
    skill, occupation, members = await _load_occupation_files(
        session, occupation_skill_id=occupation_skill_id
    )

    # Resolve the SkillVersion this build pins to.
    await session.refresh(skill, attribute_names=["versions"])
    target_version = _pick_version(skill, version=version)
    if target_version is None:
        raise VaultBuildError(
            code="vault_build.version_not_found",
            message=(
                f"Occupation {skill.slug} has no version {version!r}. "
                "Create the version row before building."
            ),
        )

    # Determinism: pin built_at to the epoch and derive vault_id from
    # the inputs so two builds over identical content produce the same
    # zip bytes (and therefore the same content_hash). Real wall-clock
    # provenance is captured on the ``vault_builds.created_at`` /
    # ``built_at`` columns instead.
    built_at = EPOCH_DATETIME
    creator_handle = await _resolve_creator_handle(
        session, user_id=skill.creator_id
    )
    _validate_slug(creator_handle, what="creator handle")
    _validate_slug(skill.slug, what="occupation slug")

    resolver = _build_target_resolver_for_occupation(members)

    # Build per-file manifest entries first; warnings accumulate.
    warnings: list[Warning] = []
    file_entries: list[FileEntry] = []
    for _, member in members:
        entry, member_warnings = _file_entry_for_member(
            member, kind="skill", resolver=resolver
        )
        file_entries.append(entry)
        warnings.extend(member_warnings)

    occupation_summary = OccupationSummary(
        skill_id=str(skill.id),
        name=skill.name,
        slug=skill.slug,
        creator_handle=creator_handle,
        version=target_version.version,
        # Will be back-filled with the final build hash; for now use the
        # version's stored content_hash so the summary is meaningful even
        # if the manifest is read in isolation.
        content_hash=target_version.content_hash,
        domains=list(occupation.domains or []),
    )

    vault_id = _derive_vault_id(
        scope="occupation",
        skill_id=str(skill.id),
        version=target_version.version,
        file_entries=file_entries,
    )

    manifest = VaultManifest(
        schema_version=1,
        vault_id=vault_id,
        occupation=occupation_summary,
        personas=[],
        files=file_entries,
        attribution_index={
            entry.skill_id: entry.vault_path for entry in file_entries
        },
        build=BuildBlock(
            occupation_build_id=None,
            occupation_build_hash=None,
            persona_build_ids=[],
            persona_build_hashes=[],
            composed_hash=None,
            built_at=built_at,
            composed_at=None,
        ),
        warnings=warnings,
    )

    # Assemble file payloads.
    files: list[tuple[str, bytes]] = []

    # Resolver for the Linked-notes section reuses the manifest-side closure
    # but returns a vault-relative path (no .md). Falls back to the raw
    # target if unresolved so Obsidian still renders the link as broken (the
    # user can see what was intended).
    def body_resolver(t: str) -> str:
        return resolver(t) or t.removesuffix(".md")

    for entry, (_, member) in zip(file_entries, members, strict=True):
        body_bytes = _emit_file_body(
            member, entry, built_at=built_at, target_resolver=body_resolver
        )
        files.append((entry.vault_path, body_bytes))

    # README, index, manifest.
    files.append(
        ("README.md", _emit_readme_occupation(
            skill, creator_handle, occupation, members,
            built_at=built_at, version=target_version.version,
        ))
    )
    files.append(
        ("00-index.md", _emit_index_occupation(skill, occupation, members))
    )
    files.append(("vault.json", write_manifest(manifest).encode("utf-8")))

    zip_bytes = _write_zip(files)
    content_hash = _sha256(zip_bytes)

    # Idempotency check.
    existing_res = await session.execute(
        select(VaultBuild).where(
            VaultBuild.skill_id == skill.id,
            VaultBuild.content_hash == content_hash,
        )
    )
    existing = existing_res.scalar_one_or_none()
    if existing is not None and not force_rebuild:
        return existing

    storage_url = (
        f"vaults/{skill.id}/{target_version.version}/{content_hash}.zip"
    )
    storage = get_storage()
    await storage.put_object(storage_url, zip_bytes, "application/zip")

    # When force_rebuild=True and an identical build already exists, the
    # only thing to do is re-upload the (bytewise identical) zip; we keep
    # the existing row so the unique (skill_id, content_hash) constraint
    # is preserved and downstream FKs (vault_downloads.occupation_build_id)
    # don't dangle.
    if existing is not None:
        return existing

    # Patch the manifest with the build hash + storage_url's content_hash
    # so the persisted JSON in the DB carries the same identifier as the
    # bytes on disk. Re-emit the json into the DB row but keep the zip's
    # vault.json as built (so we don't recompute the hash).
    manifest.build.occupation_build_hash = content_hash
    manifest.occupation = OccupationSummary(
        skill_id=occupation_summary.skill_id,
        name=occupation_summary.name,
        slug=occupation_summary.slug,
        creator_handle=occupation_summary.creator_handle,
        version=occupation_summary.version,
        content_hash=content_hash,
        domains=occupation_summary.domains,
    )

    build = VaultBuild(
        skill_id=skill.id,
        skill_version_id=target_version.id,
        content_hash=content_hash,
        storage_url=storage_url,
        manifest_json=json.loads(write_manifest(manifest)),
        file_count=len(files),
        total_bytes=len(zip_bytes),
        status=VaultBuildStatus.SUCCEEDED,
        error=None,
        build_log_json={
            "warning_count": len(warnings),
            "warnings": [w.model_dump() for w in warnings],
        },
        built_at=built_at,
        built_by=skill.creator_id,
    )
    session.add(build)
    await session.flush()

    # Patch the FK on the occupation side-table.
    occupation.latest_build_id = build.id
    await session.flush()

    return build


async def build_persona(
    session: AsyncSession,
    persona_skill_id: uuid.UUID,
    version: str,
    *,
    force_rebuild: bool = False,
) -> VaultBuild:
    """Build a persona vault (overlay only) and upload the zip.

    The build contains only the ``personas/<handle>/<slug>/`` subtree +
    a ``persona.json`` manifest fragment. The composer (T-07) merges
    this subtree into the parent occupation tree at delivery time.
    """
    skill, persona, creator_handle, neurons = await _load_persona_files(
        session, persona_skill_id=persona_skill_id
    )

    await session.refresh(skill, attribute_names=["versions"])
    target_version = _pick_version(skill, version=version)
    if target_version is None:
        raise VaultBuildError(
            code="vault_build.version_not_found",
            message=(
                f"Persona {skill.slug} has no version {version!r}. "
                "Create the version row before building."
            ),
        )

    # See ``build_occupation`` — built_at is pinned for determinism.
    built_at = EPOCH_DATETIME
    resolver = _build_target_resolver_for_persona(neurons)

    warnings: list[Warning] = []
    file_entries: list[FileEntry] = []
    for _, neuron in neurons:
        entry, member_warnings = _file_entry_for_member(
            neuron, kind="memory_neuron", resolver=resolver
        )
        file_entries.append(entry)
        warnings.extend(member_warnings)

    persona_summary = PersonaSummary(
        skill_id=str(skill.id),
        name=skill.name,
        slug=skill.slug,
        creator_handle=creator_handle,
        version=target_version.version,
        content_hash=target_version.content_hash,
        neuron_count=len(neurons),
        parent_occupation_id=(
            str(persona.parent_occupation_id)
            if persona.parent_occupation_id is not None
            else None
        ),
    )

    vault_id = _derive_vault_id(
        scope="persona",
        skill_id=str(skill.id),
        version=target_version.version,
        file_entries=file_entries,
    )

    manifest = VaultManifest(
        schema_version=1,
        vault_id=vault_id,
        occupation=None,
        personas=[persona_summary],
        files=file_entries,
        attribution_index={
            entry.skill_id: entry.vault_path for entry in file_entries
        },
        build=BuildBlock(
            occupation_build_id=None,
            occupation_build_hash=None,
            persona_build_ids=[],
            persona_build_hashes=[],
            composed_hash=None,
            built_at=built_at,
            composed_at=None,
        ),
        warnings=warnings,
    )

    files: list[tuple[str, bytes]] = []

    def body_resolver(t: str) -> str:
        return resolver(t) or t.removesuffix(".md")

    for entry, (_, neuron) in zip(file_entries, neurons, strict=True):
        body_bytes = _emit_file_body(
            neuron, entry, built_at=built_at, target_resolver=body_resolver
        )
        files.append((entry.vault_path, body_bytes))

    persona_root = f"personas/{creator_handle}/{skill.slug}"
    files.append(
        (
            f"{persona_root}/README.md",
            _emit_readme_persona(
                skill, persona, creator_handle, neurons,
                built_at=built_at, version=target_version.version,
            ),
        )
    )
    # Persona-only build writes ``persona.json`` (not ``vault.json``) per
    # 03-vault-generation.md §1 — composition produces the canonical
    # ``vault.json`` at delivery time.
    files.append(
        (
            f"{persona_root}/persona.json",
            write_manifest(manifest).encode("utf-8"),
        )
    )

    zip_bytes = _write_zip(files)
    content_hash = _sha256(zip_bytes)

    existing_res = await session.execute(
        select(VaultBuild).where(
            VaultBuild.skill_id == skill.id,
            VaultBuild.content_hash == content_hash,
        )
    )
    existing = existing_res.scalar_one_or_none()
    if existing is not None and not force_rebuild:
        return existing

    storage_url = (
        f"vaults/{skill.id}/{target_version.version}/{content_hash}.zip"
    )
    storage = get_storage()
    await storage.put_object(storage_url, zip_bytes, "application/zip")

    # See ``build_occupation``: force_rebuild=True with an identical hash
    # only re-uploads the (bytewise identical) zip; the existing row stays.
    if existing is not None:
        return existing

    # Patch the manifest's persona summary with the build hash now we
    # know it; persist the updated JSON into the DB row only.
    manifest.personas = [
        PersonaSummary(
            skill_id=persona_summary.skill_id,
            name=persona_summary.name,
            slug=persona_summary.slug,
            creator_handle=persona_summary.creator_handle,
            version=persona_summary.version,
            content_hash=content_hash,
            neuron_count=persona_summary.neuron_count,
            parent_occupation_id=persona_summary.parent_occupation_id,
        )
    ]

    build = VaultBuild(
        skill_id=skill.id,
        skill_version_id=target_version.id,
        content_hash=content_hash,
        storage_url=storage_url,
        manifest_json=json.loads(write_manifest(manifest)),
        file_count=len(files),
        total_bytes=len(zip_bytes),
        status=VaultBuildStatus.SUCCEEDED,
        error=None,
        build_log_json={
            "warning_count": len(warnings),
            "warnings": [w.model_dump() for w in warnings],
        },
        built_at=built_at,
        built_by=skill.creator_id,
    )
    session.add(build)
    await session.flush()

    persona.latest_build_id = build.id
    await session.flush()

    return build


__all__ = [
    "EPOCH_TIMESTAMP",
    "MAX_VAULT_BYTES",
    "VaultBuildError",
    "build_occupation",
    "build_persona",
]
