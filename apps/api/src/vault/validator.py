"""Vault-zip validator — post-build integrity check.

Spec: ``team/03-vault-generation.md`` §6 (manifest binding rules) +
ADR-010 (attribution comment in every emitted file). Exposed as
:func:`validate_vault` and called by:

* T-06 tests (this wave) — assert the builder's zip is well-formed.
* Future buyer-side "verify my vault" CLI (Phase 2 — not in MVP scope
  but the API surface is stable so we don't have to refactor).

Returns :class:`ValidationResult` with a boolean ``is_valid`` and a
list of :class:`ValidationError` rows so the caller can surface every
problem in one pass.
"""

from __future__ import annotations

import io
import json
import re
import zipfile
from typing import Literal

import jsonschema
from pydantic import BaseModel, Field

from src.vault.manifest import VaultManifest, load_schema

# Validation mode for :func:`validate_vault`. ``occupation`` is the
# default and matches the canonical merged-vault contract. ``persona``
# tolerates ``vault.unresolved_wikilink`` errors whose target starts
# with ``base/`` — by design the persona-only builder leaves those
# unresolved so the composer can resolve them at delivery time. See
# ``team/dev-diary-devops-persona-wave4.md`` §Open question 1 for the
# rationale; the polish landed in Wave 5 (this file).
ValidateMode = Literal["occupation", "persona", "composed"]

# Match the attribution comment per ADR-010.
_ATTRIBUTION_RE = re.compile(
    r"<!--\s*skg-attribution:\s*\n(?:.*\n)*?\s*-->", re.MULTILINE
)
# Match a Linked-notes wiki target inside the auto-emitted footer. We
# only look at lines starting with `- [[`.
_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


class ValidationError(BaseModel):
    """One machine-actionable problem with the built vault."""

    field: str = Field(
        description="Vault-relative path or ``manifest``/``zip`` for global issues."
    )
    code: str = Field(description="Stable error code.")
    message: str


class ValidationResult(BaseModel):
    """Outcome of :func:`validate_vault`."""

    is_valid: bool
    errors: list[ValidationError] = Field(default_factory=list)


# ── Internals ────────────────────────────────────────────────────────


def _load_manifest(
    zf: zipfile.ZipFile,
    manifest_path: str,
) -> tuple[VaultManifest | None, list[ValidationError]]:
    """Parse ``vault.json`` (or ``persona.json``) into a :class:`VaultManifest`."""
    errors: list[ValidationError] = []
    try:
        raw = zf.read(manifest_path)
    except KeyError:
        errors.append(
            ValidationError(
                field="manifest",
                code="vault.missing_manifest",
                message=f"{manifest_path} is absent from the vault zip.",
            )
        )
        return None, errors
    # JSON Schema check first (catches structural problems with a
    # clearer error than Pydantic's coerce attempt).
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(
            ValidationError(
                field="manifest",
                code="vault.malformed_manifest_json",
                message=f"Failed to parse {manifest_path}: {exc}",
            )
        )
        return None, errors

    schema = load_schema()
    validator = jsonschema.Draft7Validator(schema)
    schema_errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    for err in schema_errors:
        path = ".".join(str(p) for p in err.path) or "manifest"
        errors.append(
            ValidationError(
                field=f"manifest.{path}",
                code="vault.schema_violation",
                message=err.message,
            )
        )

    # Even with schema warnings, try the Pydantic model so callers get a
    # parsed view for downstream checks. Errors are collected, not raised.
    try:
        # Pydantic accepts the manifest with the ``$schema`` key too.
        cleaned = {k: v for k, v in payload.items() if k != "$schema"}
        manifest = VaultManifest.model_validate(cleaned)
    except Exception as exc:  # collect everything
        errors.append(
            ValidationError(
                field="manifest",
                code="vault.manifest_pydantic_error",
                message=str(exc),
            )
        )
        return None, errors
    return manifest, errors


def _check_attribution_comments(
    zf: zipfile.ZipFile,
    manifest: VaultManifest,
) -> list[ValidationError]:
    """Per ADR-010: every emitted .md file carries an ``skg-attribution`` comment."""
    errors: list[ValidationError] = []
    for entry in manifest.files:
        try:
            body = zf.read(entry.vault_path).decode("utf-8")
        except KeyError:
            errors.append(
                ValidationError(
                    field=entry.vault_path,
                    code="vault.manifest_file_missing",
                    message=(
                        f"vault.json lists {entry.vault_path!r} but the "
                        "file is absent from the zip."
                    ),
                )
            )
            continue
        if not _ATTRIBUTION_RE.search(body):
            errors.append(
                ValidationError(
                    field=entry.vault_path,
                    code="vault.missing_attribution",
                    message=(
                        f"{entry.vault_path} is missing the trailing "
                        "<!-- skg-attribution: ... --> comment (ADR-010)."
                    ),
                )
            )
    return errors


def _check_link_resolution(
    zf: zipfile.ZipFile,
    manifest: VaultManifest,
    *,
    mode: ValidateMode = "occupation",
) -> list[ValidationError]:
    """Every ``[[wiki-link]]`` in the Linked notes footer resolves to a file.

    When ``mode='persona'`` we suppress any unresolved-link error whose
    target starts with ``base/`` — the persona-only builder
    deliberately leaves those targets unresolved so the composer can
    resolve them against the merged occupation+persona surface at
    delivery time. See
    :func:`src.vault.builder._build_target_resolver_for_persona` for
    the documented contract.
    """
    errors: list[ValidationError] = []
    available_paths = {info.filename.removesuffix(".md") for info in zf.infolist()}
    for entry in manifest.files:
        try:
            body = zf.read(entry.vault_path).decode("utf-8")
        except KeyError:
            continue  # already flagged above.
        # Restrict the scan to the Linked notes footer (the spec's
        # canonical link surface). Inline links elsewhere are allowed to
        # dangle per the spec.
        marker = "## Linked notes"
        idx = body.find(marker)
        if idx == -1:
            continue
        footer = body[idx:]
        for match in _WIKILINK_RE.finditer(footer):
            raw = match.group(1).split("|")[0].strip()
            # Strip optional .md extension and any trailing #anchor.
            cleaned = raw.split("#", 1)[0].removesuffix(".md").strip()
            if not cleaned:
                continue
            # Resolution: full vault path (no .md) OR bare slug found.
            if cleaned in available_paths:
                continue
            # Bare slug — search any file whose basename matches.
            slug_matches = [p for p in available_paths if p.endswith("/" + cleaned)]
            if slug_matches:
                continue
            # Persona-mode tolerance: ``base/<slug>`` targets are
            # expected to fail in a persona-only build — they resolve
            # at compose time. Skip them here.
            if mode == "persona" and cleaned.startswith("base/"):
                continue
            errors.append(
                ValidationError(
                    field=entry.vault_path,
                    code="vault.unresolved_wikilink",
                    message=(
                        f"{entry.vault_path} references [[{raw}]] which does "
                        "not resolve to a file in the vault."
                    ),
                )
            )
    return errors


def _check_attribution_index(
    manifest: VaultManifest,
) -> list[ValidationError]:
    """Every entry in attribution_index points at a real ``files[]`` row."""
    errors: list[ValidationError] = []
    files_by_path = {entry.vault_path: entry for entry in manifest.files}
    for skill_id, vault_path in manifest.attribution_index.items():
        if vault_path not in files_by_path:
            errors.append(
                ValidationError(
                    field=f"manifest.attribution_index.{skill_id}",
                    code="vault.attribution_dangles",
                    message=(
                        f"attribution_index[{skill_id!r}] points at "
                        f"{vault_path!r} which is not in files[]."
                    ),
                )
            )
    return errors


def _check_neuron_blocks(manifest: VaultManifest) -> list[ValidationError]:
    """Every ``kind=memory_neuron`` file carries a neuron block."""
    errors: list[ValidationError] = []
    for entry in manifest.files:
        if entry.kind == "memory_neuron" and entry.neuron is None:
            errors.append(
                ValidationError(
                    field=f"manifest.files.{entry.vault_path}",
                    code="vault.neuron_block_missing",
                    message=(
                        f"{entry.vault_path} has kind=memory_neuron but no "
                        "neuron block in the manifest."
                    ),
                )
            )
    return errors


# ── Public entrypoint ───────────────────────────────────────────────


def validate_vault(
    zip_bytes: bytes,
    *,
    mode: ValidateMode = "occupation",
) -> ValidationResult:
    """Validate a built vault zip end-to-end.

    Catches:

    * Missing ``00-index.md``, ``README.md``, or ``vault.json`` (occupation builds).
    * Missing ``persona.json`` in a persona-only build.
    * Manifest schema violations (against ``vault-manifest-v1.json``).
    * Files listed in the manifest but not in the zip.
    * Files in the zip missing the ``skg-attribution`` comment.
    * Linked-notes wiki links that don't resolve to a file in this vault.
    * ``attribution_index`` entries pointing at non-existent files.
    * ``kind=memory_neuron`` files missing the neuron block.

    The validator never raises; problems are accumulated into
    :class:`ValidationResult.errors`.

    ``mode`` toggles the link-resolution rule:

    * ``occupation`` (default) — strict: every ``[[...]]`` must resolve.
    * ``persona`` — tolerates ``[[base/...]]`` links left unresolved
      by the persona-only builder; they resolve at compose time.
    * ``composed`` — same strictness as ``occupation``; composed
      bundles should have every link resolvable on the merged surface.
    """
    errors: list[ValidationError] = []

    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes), "r")
    except zipfile.BadZipFile as exc:
        return ValidationResult(
            is_valid=False,
            errors=[
                ValidationError(
                    field="zip",
                    code="vault.bad_zip",
                    message=f"Not a valid zip file: {exc}",
                )
            ],
        )

    with zf:
        names = set(zf.namelist())

        # Decide manifest path: occupation builds use ``vault.json`` at root;
        # persona builds use ``personas/<handle>/<slug>/persona.json``.
        manifest_path: str | None = None
        if "vault.json" in names:
            manifest_path = "vault.json"
            # Required root files for the occupation build.
            for required in ("README.md", "00-index.md"):
                if required not in names:
                    errors.append(
                        ValidationError(
                            field=required,
                            code="vault.required_file_missing",
                            message=f"Occupation build is missing {required}.",
                        )
                    )
        else:
            # Look for a persona.json under personas/.../.
            persona_jsons = [n for n in names if n.endswith("/persona.json")]
            if len(persona_jsons) == 1:
                manifest_path = persona_jsons[0]
                persona_root = manifest_path[: -len("/persona.json")]
                readme_path = f"{persona_root}/README.md"
                if readme_path not in names:
                    errors.append(
                        ValidationError(
                            field=readme_path,
                            code="vault.required_file_missing",
                            message=f"Persona build is missing {readme_path}.",
                        )
                    )
            else:
                errors.append(
                    ValidationError(
                        field="manifest",
                        code="vault.missing_manifest",
                        message=(
                            "Zip is missing both ``vault.json`` (occupation "
                            "build) and a single ``personas/.../persona.json`` "
                            "(persona build)."
                        ),
                    )
                )

        if manifest_path is None:
            return ValidationResult(is_valid=False, errors=errors)

        manifest, manifest_errors = _load_manifest(zf, manifest_path)
        errors.extend(manifest_errors)
        if manifest is None:
            return ValidationResult(is_valid=False, errors=errors)

        errors.extend(_check_attribution_comments(zf, manifest))
        errors.extend(_check_link_resolution(zf, manifest, mode=mode))
        errors.extend(_check_attribution_index(manifest))
        errors.extend(_check_neuron_blocks(manifest))

    return ValidationResult(is_valid=not errors, errors=errors)


__all__ = ["ValidateMode", "ValidationError", "ValidationResult", "validate_vault"]
