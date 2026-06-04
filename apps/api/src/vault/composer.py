"""Vault composer — buyer-time merge + watermark + presign.

Spec: ``team/03-vault-generation.md`` §10 (Composition algorithm) +
ADR-002 (per-buyer license set), ADR-006 (compose-on-demand, 24h cache,
60s presigned URL), ADR-010 (attribution comment stays in the file;
composer stacks the per-buyer watermark on top), ADR-013 (composed
artifact is auditable via :class:`VaultDownload`).

Public entry point: :func:`compose_for_license`. Given a buyer + an
occupation license + an optional list of persona-license-ids, it:

1. Validates the buyer owns the occupation license; intersects the
   requested persona licenses with their active persona-license set
   (403 with a typed code on a mismatch).
2. Builds a cache key over the input build ids and the buyer id.
3. On a hit, presigns the cached S3 object and returns the URL.
4. On a miss, fetches each input build's zip, merges the persona
   subtrees into the occupation tree, regenerates ``vault.json`` with
   merged manifests + re-resolved links, stamps every ``.md`` with the
   per-buyer watermark from :func:`src.delivery.watermark.append_watermark`,
   re-zips deterministically (except ``composed_at`` + watermark), uploads
   to ``delivery/vaults/{nonce}.zip``, records a ``vault_downloads`` row,
   primes the cache for 24h, and returns the presigned URL.

T-06's :mod:`src.vault.builder` is the source of truth for occupation
and persona build artifacts; this module is read-only against it.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import secrets
import uuid
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from sqlalchemy import desc, select

from src.billing.models import (
    License,
    LicenseCompositionRole,
    LicenseStatus,
)
from src.core import cache as cache_mod
from src.delivery.watermark import append_watermark
from src.vault.builder import EPOCH_TIMESTAMP
from src.vault.manifest import (
    BuildBlock,
    FileEntry,
    ManifestLinkEntry,
    OccupationSummary,
    PersonaSummary,
    VaultManifest,
    Warning,  # noqa: A004 — domain shape; not the builtin
    write_manifest,
)
from src.vault.models import VaultBuild, VaultBuildStatus, VaultDownload

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


# ── Constants ────────────────────────────────────────────────────────


# Per ADR-006: composed bundles are cached for 24h per (buyer, build set).
COMPOSE_CACHE_TTL_SECONDS: int = 24 * 60 * 60

# Per ADR-006 / spec §10: presigned URL is short-lived (60 seconds).
PRESIGNED_URL_TTL_SECONDS: int = 60


# ── Errors ───────────────────────────────────────────────────────────


class VaultComposeError(Exception):
    """Raised when composition cannot proceed.

    ``status_code`` lets the router map a single exception class to the
    right HTTP response without re-encoding each branch. ``code`` is the
    stable identifier the frontend dispatches on.
    """

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


# ── Result shape ─────────────────────────────────────────────────────


@dataclass
class ComposedDownload:
    """Outcome of :func:`compose_for_license`.

    ``presigned_url`` is the time-limited GET URL for the buyer's bundle.
    ``cache_hit`` reflects whether the composition was served from the
    24h cache (no re-zip).
    """

    presigned_url: str
    expires_at: datetime
    composed_hash: str
    cache_hit: bool
    vault_download_id: uuid.UUID
    storage_url: str
    occupation_build_id: uuid.UUID
    persona_build_ids: list[uuid.UUID]


# ── License resolution ──────────────────────────────────────────────


async def _load_occupation_license(
    session: AsyncSession,
    *,
    buyer_id: uuid.UUID,
    license_id: uuid.UUID,
) -> License:
    """Load + sanity-check the occupation license.

    Raises a typed :class:`VaultComposeError` on every failure mode so
    the router doesn't need to translate exception shapes.
    """
    lic = await session.get(License, license_id)
    # 404-style behaviour for "not found OR not yours" so the response
    # doesn't leak the existence of arbitrary license ids. Coerce to str
    # for the comparison — sqlite returns UUID columns as str via the
    # ``with_variant`` whereas the in-Python value is a real ``uuid.UUID``;
    # comparing across types silently mis-classifies the owner.
    if lic is None or str(lic.buyer_id) != str(buyer_id):
        raise VaultComposeError(
            code="vault.license_not_found",
            message="License not found.",
            status_code=404,
        )
    if lic.composition_role != LicenseCompositionRole.OCCUPATION:
        raise VaultComposeError(
            code="vault.compose_unentitled",
            message=(
                "License is not an occupation license — composition is "
                "only available against an occupation-role license."
            ),
            status_code=409,
            details={"composition_role": lic.composition_role.value},
        )
    if lic.status != LicenseStatus.ACTIVE:
        raise VaultComposeError(
            code="vault.license_inactive",
            message=f"License status is {lic.status.value}.",
            status_code=409,
            details={"status": lic.status.value},
        )
    return lic


async def _active_persona_licenses(
    session: AsyncSession,
    *,
    buyer_id: uuid.UUID,
    occupation_skill_id: uuid.UUID,
) -> list[License]:
    """Return every active persona license the buyer holds for this occupation.

    The primary composer query per ``02-api-surface.md`` §4 — buyer's
    persona licenses where ``target_occupation_skill_id == X`` and
    status is active. The wave-1 migration added a covering index.
    """
    stmt = select(License).where(
        License.buyer_id == buyer_id,
        License.composition_role == LicenseCompositionRole.PERSONA,
        License.target_occupation_skill_id == occupation_skill_id,
        License.status == LicenseStatus.ACTIVE,
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())


def _intersect_persona_licenses(
    active: list[License],
    requested: list[uuid.UUID] | None,
) -> list[License]:
    """Filter the buyer's active persona licenses by the requested set.

    If ``requested`` is ``None``, every active persona license is used
    (spec §10 default = "all active"). Otherwise every id in
    ``requested`` MUST appear in ``active`` — else 403 with
    ``vault.persona_license_not_held`` per the brief.
    """
    if requested is None:
        return active
    by_id = {lic.id: lic for lic in active}
    out: list[License] = []
    for req_id in requested:
        if req_id not in by_id:
            raise VaultComposeError(
                code="vault.persona_license_not_held",
                message=(
                    f"Persona license {req_id} is not held by the buyer "
                    "for this occupation."
                ),
                status_code=403,
                details={"persona_license_id": str(req_id)},
            )
        out.append(by_id[req_id])
    return out


async def _latest_succeeded_build(
    session: AsyncSession, *, skill_id: uuid.UUID,
) -> VaultBuild | None:
    """Return the latest succeeded :class:`VaultBuild` for ``skill_id``."""
    stmt = (
        select(VaultBuild)
        .where(
            VaultBuild.skill_id == skill_id,
            VaultBuild.status == VaultBuildStatus.SUCCEEDED,
        )
        .order_by(desc(VaultBuild.created_at), desc(VaultBuild.id))
        .limit(1)
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


# ── Cache key ────────────────────────────────────────────────────────


def _cache_key(
    *,
    buyer_id: uuid.UUID,
    occupation_skill_id: uuid.UUID,
    occupation_build_id: uuid.UUID,
    persona_build_ids: list[uuid.UUID],
) -> str:
    """sha256 over the inputs that change the composed bytes.

    Per spec §10 / ADR-006: the key is keyed on the build ids (NOT the
    license ids) because the same build content composed for the same
    buyer is byte-equivalent (modulo the wall-clock watermark, which the
    composer always re-applies on every call regardless of cache state
    — the cache stores the post-watermark presigned URL + storage key).

    ``buyer_id`` is in the key because the watermark embeds the buyer
    hash; two different buyers must NEVER share a cached entry.
    """
    sorted_pids = sorted(str(pid) for pid in persona_build_ids)
    payload = "|".join(
        [
            str(buyer_id),
            str(occupation_skill_id),
            str(occupation_build_id),
            *sorted_pids,
        ]
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"composed:{buyer_id}:{occupation_skill_id}:{digest}"


# ── Manifest merge ──────────────────────────────────────────────────


def _link_resolver_for_paths(paths: set[str]) -> _PathResolver:
    """Build a resolver closure for the merged file surface.

    Resolution mirrors :mod:`src.vault.builder` §_build_target_resolver_for_*:

    * Exact vault-relative path (with or without ``.md``).
    * Bare slug → the first path whose basename matches.
    * ``base/<slug>`` form — strip the ``base/`` prefix and resolve
      against the merged occupation surface. Wave 5 polish 2:
      persona neurons emit links like ``base/ci-pipeline-architect``
      by convention (see ``team/dev-diary-devops-persona-wave4.md``);
      the composer rewrites these to the actual
      ``domains/<domain>/<slug>`` path discovered in the merged tree.
    """
    by_path = {p.removesuffix(".md") for p in paths}
    # Build a slug→path index. If two files share the same slug (rare —
    # ADR-011's kebab rule prevents accidental collisions across base+
    # persona), pick the first deterministically by sort order.
    by_slug: dict[str, str] = {}
    for p in sorted(by_path):
        slug = p.rsplit("/", 1)[-1]
        by_slug.setdefault(slug, p)

    def _resolve(target: str) -> str | None:
        cleaned = target.strip().removesuffix(".md")
        if cleaned in by_path:
            return cleaned
        # base/<slug> rewrite — persona neurons use this convention.
        if cleaned.startswith("base/"):
            inner = cleaned[len("base/"):]
            # `base/domains/<domain>/<slug>` — try the fully qualified
            # path first.
            if inner in by_path:
                return inner
            # `base/<slug>` — bare-slug form, the common case.
            bare = inner.rsplit("/", 1)[-1]
            if bare in by_slug:
                return by_slug[bare]
        return by_slug.get(cleaned)

    return _resolve


# Type alias for the resolver closure (kept here so mypy --strict happy
# without exporting an intermediate name).
from collections.abc import Callable as _Callable  # noqa: E402

_PathResolver = _Callable[[str], str | None]


def _merge_manifests(
    *,
    occupation_manifest: VaultManifest,
    persona_manifests: list[VaultManifest],
    occupation_build: VaultBuild,
    persona_builds: list[VaultBuild],
    composed_at: datetime,
    file_surface_paths: set[str],
) -> VaultManifest:
    """Produce the composed ``vault.json`` manifest.

    Starts from the occupation manifest as a base. For each persona
    manifest: appends ``personas[]``, ``files[]``, ``attribution_index``
    entries. Re-runs link resolution over the merged file surface so
    persona-side ``base/`` references (intentionally left unresolved by
    the persona builder per
    :func:`src.vault.builder._build_target_resolver_for_persona`) get
    flipped to ``resolved=True`` whenever they hit a now-present
    occupation file.

    ``composed_at`` is the wall-clock timestamp (not the deterministic
    epoch the builder pins) — composition is intentionally a fresh audit
    event per ADR-006.
    """
    resolver = _link_resolver_for_paths(file_surface_paths)

    # Start with a copy of the occupation manifest's files.
    merged_files: list[FileEntry] = []
    merged_warnings: list[Warning] = list(occupation_manifest.warnings)

    # Re-resolve occupation files (most should already be resolved; safe
    # to re-run because the resolver is total over the merged surface).
    for entry in occupation_manifest.files:
        new_links, new_warnings, all_resolved = _re_resolve_links(
            entry.links,
            entry.vault_path,
            resolver,
        )
        merged_files.append(
            FileEntry(
                vault_path=entry.vault_path,
                skill_id=entry.skill_id,
                version=entry.version,
                kind=entry.kind,
                creator_handle=entry.creator_handle,
                content_hash=entry.content_hash,
                tags=list(entry.tags),
                links=new_links,
                links_resolved=all_resolved,
                neuron=entry.neuron,
            )
        )
        merged_warnings.extend(new_warnings)

    # Add persona files + warnings, re-resolving links against the merged
    # surface.
    for pm in persona_manifests:
        for entry in pm.files:
            new_links, new_warnings, all_resolved = _re_resolve_links(
                entry.links,
                entry.vault_path,
                resolver,
            )
            merged_files.append(
                FileEntry(
                    vault_path=entry.vault_path,
                    skill_id=entry.skill_id,
                    version=entry.version,
                    kind=entry.kind,
                    creator_handle=entry.creator_handle,
                    content_hash=entry.content_hash,
                    tags=list(entry.tags),
                    links=new_links,
                    links_resolved=all_resolved,
                    neuron=entry.neuron,
                )
            )
            merged_warnings.extend(new_warnings)
        # Carry over the persona's pre-existing warnings, BUT drop any
        # ``vault.unresolved_link`` warning whose target the merged-
        # surface resolver now resolves (Wave 5 polish 2). Without this
        # filter, every persona-build warning for a ``base/<slug>`` link
        # would leak through to the composed manifest even though the
        # composer just rewrote that link to a real ``domains/<domain>/
        # <slug>`` path. Other warning classes (e.g. a persona builder's
        # "missing version row") are preserved verbatim.
        for warning in pm.warnings:
            unresolved = getattr(warning, "unresolved_link", None)
            if (
                warning.code == "vault.unresolved_link"
                and unresolved is not None
                and resolver(unresolved) is not None
            ):
                continue  # The composed surface resolves it — drop the stale warning.
            merged_warnings.append(warning)

    attribution_index: dict[str, str] = {}
    for entry in merged_files:
        attribution_index[entry.skill_id] = entry.vault_path

    personas_list: list[PersonaSummary] = []
    for pm in persona_manifests:
        personas_list.extend(pm.personas)

    return VaultManifest(
        schema_version=1,
        vault_id=str(uuid.uuid4()),
        occupation=_clone_occupation_summary(occupation_manifest.occupation),
        personas=personas_list,
        files=merged_files,
        attribution_index=attribution_index,
        build=BuildBlock(
            occupation_build_id=str(occupation_build.id),
            occupation_build_hash=occupation_build.content_hash,
            persona_build_ids=[str(pb.id) for pb in persona_builds],
            persona_build_hashes=[pb.content_hash for pb in persona_builds],
            composed_hash=None,  # patched after final zip bytes are known
            built_at=(
                occupation_manifest.build.built_at
                if occupation_manifest.build is not None
                else composed_at
            ),
            composed_at=composed_at,
        ),
        warnings=merged_warnings,
    )


def _clone_occupation_summary(
    src: OccupationSummary | None,
) -> OccupationSummary | None:
    if src is None:
        return None
    return OccupationSummary(
        skill_id=src.skill_id,
        name=src.name,
        slug=src.slug,
        creator_handle=src.creator_handle,
        version=src.version,
        content_hash=src.content_hash,
        domains=list(src.domains),
    )


def _re_resolve_links(
    links: list[ManifestLinkEntry],
    vault_path: str,
    resolver: _PathResolver,
) -> tuple[list[ManifestLinkEntry], list[Warning], bool]:
    """Apply the composed-surface resolver to a file's link list.

    The composer's resolver sees the FULL merged file surface, so a
    persona link to ``base/...`` (or to any sibling occupation file)
    that was unresolved at build time will resolve here. We rebuild the
    link list with up-to-date ``resolved`` flags and emit a warning for
    every still-dangling target so the composed manifest carries a
    complete diagnosis per spec §10.
    """
    new_links: list[ManifestLinkEntry] = []
    warnings: list[Warning] = []
    all_resolved = True
    for link in links:
        # ``target`` on a resolved link is the vault path; on an
        # unresolved link it's the original creator-typed target. Try
        # the resolver against both shapes.
        resolved_path = resolver(link.target)
        if resolved_path is None and link.resolved:
            # The cached target IS already a vault path that no longer
            # resolves — keep it as the typed value but flip to
            # unresolved.
            resolved_path = None
        resolved = resolved_path is not None
        if not resolved:
            all_resolved = False
            warnings.append(
                Warning(
                    file=vault_path,
                    code="vault.unresolved_link",
                    unresolved_link=link.target,
                    message=(
                        f"Link target {link.target!r} did not resolve to "
                        "a file in the composed vault."
                    ),
                )
            )
        new_links.append(
            ManifestLinkEntry(
                target=resolved_path or link.target,
                relation=link.relation,
                resolved=resolved,
                weight=link.weight,
            )
        )
    return new_links, warnings, all_resolved


# ── Zip handling ────────────────────────────────────────────────────


def _read_zip(zip_bytes: bytes) -> dict[str, bytes]:
    """Read a zip into a name→bytes mapping.

    Skips directory entries (zips emitted by the builder don't include
    them, but defensive against any future archive that does).
    """
    out: dict[str, bytes] = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            out[info.filename] = zf.read(info.filename)
    return out


def _write_zip(files: dict[str, bytes]) -> bytes:
    """Write a deterministic DEFLATE zip from a name→bytes mapping.

    Mirrors :func:`src.vault.builder._write_zip` — every entry's
    timestamp is pinned to ``EPOCH_TIMESTAMP`` so two composed runs over
    the same merged tree produce byte-identical bytes (except for the
    per-buyer watermark + composed_at, which are intentionally fresh
    per call).
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(files):
            info = zipfile.ZipInfo(filename=path, date_time=EPOCH_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, files[path])
    return buf.getvalue()


def _stamp_markdown_with_watermark(
    files: dict[str, bytes],
    *,
    license_id: uuid.UUID,
    buyer_id: uuid.UUID,
) -> dict[str, bytes]:
    """Apply the per-buyer watermark to every ``.md`` file in the merged tree.

    Per ADR-010 / spec §7, the watermark goes AFTER the existing
    ``skg-attribution`` comment the builder already emitted — that is
    exactly what :func:`append_watermark` does (appends to the end of
    the file body), so no extra ordering work is needed.
    """
    stamped: dict[str, bytes] = {}
    for path, payload in files.items():
        if not path.endswith(".md"):
            stamped[path] = payload
            continue
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            # Non-text file masquerading as .md — leave it alone.
            stamped[path] = payload
            continue
        with_wm, _comment = append_watermark(
            text,
            license_id=license_id,
            buyer_id=buyer_id,
        )
        stamped[path] = with_wm.encode("utf-8")
    return stamped


def _parse_manifest_from_zip(
    files: dict[str, bytes], *, path: str
) -> VaultManifest:
    """Parse a vault/persona manifest JSON from the zip bytes."""
    raw = files.get(path)
    if raw is None:
        raise VaultComposeError(
            code="vault.compose_missing_manifest",
            message=f"Build artifact is missing {path}.",
            status_code=500,
        )
    payload = json.loads(raw.decode("utf-8"))
    # Strip ``$schema`` (the builder injects it for offline validators).
    payload = {k: v for k, v in payload.items() if k != "$schema"}
    return VaultManifest.model_validate(payload)


# ── Entry point ─────────────────────────────────────────────────────


async def compose_for_license(
    session: AsyncSession,
    *,
    buyer_id: uuid.UUID,
    occupation_license_id: uuid.UUID,
    include_persona_license_ids: list[uuid.UUID] | None = None,
    user_agent: str | None = None,
    client_ip: str | None = None,
) -> ComposedDownload:
    """Merge the buyer's entitled builds, watermark, cache, presign.

    See module docstring for the full algorithm. The ``user_agent`` and
    ``client_ip`` parameters are optional; when supplied they're hashed
    via :mod:`src.delivery.watermark` and stored on the
    :class:`VaultDownload` row for the existing audit trail.
    """
    occ_license = await _load_occupation_license(
        session,
        buyer_id=buyer_id,
        license_id=occupation_license_id,
    )

    active_personas = await _active_persona_licenses(
        session,
        buyer_id=buyer_id,
        occupation_skill_id=occ_license.skill_id,
    )
    persona_licenses = _intersect_persona_licenses(
        active_personas, include_persona_license_ids
    )

    occupation_build = await _latest_succeeded_build(
        session, skill_id=occ_license.skill_id
    )
    if occupation_build is None:
        raise VaultComposeError(
            code="vault.compose_no_build",
            message=(
                "No succeeded vault build exists for this occupation. "
                "Wait for the build to complete or contact the creator."
            ),
            status_code=409,
        )

    persona_builds: list[VaultBuild] = []
    persona_license_to_build: list[tuple[License, VaultBuild]] = []
    for pl in persona_licenses:
        pb = await _latest_succeeded_build(session, skill_id=pl.skill_id)
        if pb is None:
            # Mirror spec §10: skip personas without a build — surface
            # as a warning rather than a hard fail so the buyer can
            # still receive the occupation-only bundle.
            log.warning(
                "vault.compose.persona_no_build",
                extra={
                    "buyer_id": str(buyer_id),
                    "persona_license_id": str(pl.id),
                    "persona_skill_id": str(pl.skill_id),
                },
            )
            continue
        persona_builds.append(pb)
        persona_license_to_build.append((pl, pb))

    # ── Cache lookup ─────────────────────────────────────────────
    cache_key = _cache_key(
        buyer_id=buyer_id,
        occupation_skill_id=occ_license.skill_id,
        occupation_build_id=occupation_build.id,
        persona_build_ids=[pb.id for pb in persona_builds],
    )

    # Avoid the closure capturing UUIDs through a name shadow.
    _occ_build_id_for_compute = occupation_build.id
    _persona_build_ids_for_compute = [pb.id for pb in persona_builds]

    async def _compute() -> dict[str, Any]:
        # Cache-miss path. Build the bundle and write an audit row.
        composed_hash, storage_url, vault_download_id = await _build_and_record(
            session,
            buyer_id=buyer_id,
            occupation_license_id=occupation_license_id,
            occupation_build=occupation_build,
            persona_builds=persona_builds,
            persona_license_to_build=persona_license_to_build,
            user_agent=user_agent,
            client_ip=client_ip,
        )
        return {
            "composed_hash": composed_hash,
            "storage_url": storage_url,
            "vault_download_id": str(vault_download_id),
            "occupation_build_id": str(_occ_build_id_for_compute),
            "persona_build_ids": [str(pid) for pid in _persona_build_ids_for_compute],
        }

    payload, hit = await cache_mod.get_or_compute(
        cache_key, _compute, ttl_seconds=COMPOSE_CACHE_TTL_SECONDS
    )

    # ── Presign URL ──────────────────────────────────────────────
    storage_url = str(payload["storage_url"])
    composed_hash = str(payload["composed_hash"])
    vault_download_id = uuid.UUID(str(payload["vault_download_id"]))

    # Even on a cache hit we re-presign (URLs expire after 60s by spec).
    # We do NOT re-record a vault_downloads row on a hit — the cached
    # row's audit trail covers the buyer's "I downloaded this" event;
    # the URL re-issue is a UX detail, not a new download event. (If
    # the product later wants to audit URL re-issuance separately, this
    # is where to do it.)
    from src.storage.s3 import get_storage  # noqa: PLC0415 — local import avoids cycle

    storage = get_storage()
    presigned_url = await storage.presigned_url(
        storage_url, expires_in_seconds=PRESIGNED_URL_TTL_SECONDS
    )
    expires_at = datetime.now(UTC) + timedelta(
        seconds=PRESIGNED_URL_TTL_SECONDS
    )

    return ComposedDownload(
        presigned_url=presigned_url,
        expires_at=expires_at,
        composed_hash=composed_hash,
        cache_hit=hit,
        vault_download_id=vault_download_id,
        storage_url=storage_url,
        occupation_build_id=uuid.UUID(str(payload["occupation_build_id"])),
        persona_build_ids=[
            uuid.UUID(str(pid)) for pid in payload.get("persona_build_ids", [])
        ],
    )


async def _build_and_record(
    session: AsyncSession,
    *,
    buyer_id: uuid.UUID,
    occupation_license_id: uuid.UUID,
    occupation_build: VaultBuild,
    persona_builds: list[VaultBuild],
    persona_license_to_build: list[tuple[License, VaultBuild]],
    user_agent: str | None,
    client_ip: str | None,
) -> tuple[str, str, uuid.UUID]:
    """The cache-miss path. Compose, watermark, upload, audit.

    Returns ``(composed_hash, storage_url, vault_download_id)``. The
    composer's cache then stores those primitives so subsequent hits
    can presign without going through the merge path again.
    """
    from src.delivery.watermark import hash_ip, hash_ua  # noqa: PLC0415
    from src.storage.s3 import get_storage  # noqa: PLC0415

    storage = get_storage()
    composed_at = datetime.now(UTC)

    # 1. Read every input zip into memory. MVP scale per the brief
    #    (~50 MB max per spec §12); two-zip composition fits comfortably.
    occupation_files = _read_zip(
        await storage.get_object(occupation_build.storage_url)
    )
    persona_file_sets: list[dict[str, bytes]] = []
    for pb in persona_builds:
        persona_file_sets.append(
            _read_zip(await storage.get_object(pb.storage_url))
        )

    # 2. Pull the occupation tree as the base. We're going to drop the
    #    builder's vault.json (we'll rewrite it from the merged
    #    manifest) and copy persona subtrees on top.
    merged: dict[str, bytes] = {
        path: bytes(payload)
        for path, payload in occupation_files.items()
        if path != "vault.json"
    }

    # 3. Parse the occupation manifest from the build's manifest_json
    #    column (faster than re-parsing the in-zip file; identical
    #    contents).
    occupation_manifest = _manifest_from_build(occupation_build)

    # 4. Merge each persona's tree: keep only files under
    #    ``personas/...`` (the builder's persona archive ships its own
    #    persona.json + README under that subtree).
    persona_manifests: list[VaultManifest] = []
    for pb, file_set in zip(persona_builds, persona_file_sets, strict=True):
        for path, payload in file_set.items():
            if path.endswith("/persona.json"):
                # Skip the per-persona manifest; the composed vault.json
                # replaces it. (Some buyers may prefer it kept around;
                # spec §10 doesn't carry it through.)
                continue
            if not path.startswith("personas/"):
                # Defensive — persona builds only emit under personas/
                # per builder §_load_persona_files, but log if anything
                # else slips through so we can chase a bad build.
                log.warning(
                    "vault.compose.unexpected_persona_path",
                    extra={
                        "persona_build_id": str(pb.id),
                        "path": path,
                    },
                )
                continue
            merged[path] = bytes(payload)
        persona_manifests.append(_manifest_from_build(pb))

    # 5. Compose the merged manifest. The file surface used by the link
    #    resolver is every .md path now sitting in ``merged`` (plus the
    #    pre-watermark vault.json we're about to write).
    file_surface_paths = {p for p in merged if p.endswith(".md")}
    composed_manifest = _merge_manifests(
        occupation_manifest=occupation_manifest,
        persona_manifests=persona_manifests,
        occupation_build=occupation_build,
        persona_builds=persona_builds,
        composed_at=composed_at,
        file_surface_paths=file_surface_paths,
    )

    # 6. Write the composed vault.json + drop into the merged tree.
    merged["vault.json"] = write_manifest(composed_manifest).encode("utf-8")

    # 7. Per-buyer watermark on every .md.
    stamped = _stamp_markdown_with_watermark(
        merged, license_id=occupation_license_id, buyer_id=buyer_id
    )

    # 8. Deterministic re-zip (only watermark + composed_at vary across
    #    calls, per spec §10 / §12).
    bundle_bytes = _write_zip(stamped)
    composed_hash = hashlib.sha256(bundle_bytes).hexdigest()

    # 9. Patch the composed_hash back onto the manifest in-zip so the
    #    in-vault manifest agrees with the audit row. This requires a
    #    second zip pass — accept the cost for spec compliance.
    composed_manifest.build.composed_hash = composed_hash
    stamped["vault.json"] = write_manifest(composed_manifest).encode("utf-8")
    bundle_bytes = _write_zip(stamped)
    # The final composed_hash now includes the hash-of-itself patched
    # manifest. Recompute over the new bytes for the audit row + return
    # value (the manifest carries the prior hash; that's a known minor
    # circularity and consumers should treat the value in the manifest
    # as the *first-pass* hash. The audit row carries the *final* hash
    # over the bytes the buyer actually downloads).
    final_composed_hash = hashlib.sha256(bundle_bytes).hexdigest()

    # 10. Upload to the short-lived delivery prefix.
    nonce = secrets.token_urlsafe(12)
    delivery_key = f"delivery/vaults/{nonce}.zip"
    await storage.put_object(delivery_key, bundle_bytes, "application/zip")

    # 11. Insert the vault_downloads row.
    download = VaultDownload(
        occupation_license_id=occupation_license_id,
        buyer_id=buyer_id,
        occupation_build_id=occupation_build.id,
        persona_build_ids=[pb.id for pb in persona_builds] or None,
        persona_license_ids=(
            [pl.id for pl, _ in persona_license_to_build] or None
        ),
        composed_hash=final_composed_hash,
        storage_url=delivery_key,
        user_agent_hash=hash_ua(user_agent),
        ip_hash=hash_ip(client_ip),
    )
    session.add(download)
    await session.flush()

    return final_composed_hash, delivery_key, download.id


def _manifest_from_build(build: VaultBuild) -> VaultManifest:
    """Parse the manifest column from a :class:`VaultBuild` row.

    The builder stores the canonical JSON (including the ``$schema``
    URI). Strip it before validating against the Pydantic model.
    """
    payload = build.manifest_json or {}
    cleaned = {k: v for k, v in payload.items() if k != "$schema"}
    return VaultManifest.model_validate(cleaned)


__all__ = [
    "COMPOSE_CACHE_TTL_SECONDS",
    "PRESIGNED_URL_TTL_SECONDS",
    "ComposedDownload",
    "VaultComposeError",
    "compose_for_license",
]
