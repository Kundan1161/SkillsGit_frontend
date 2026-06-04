"""``vault.json`` manifest model + serializer.

Spec: ``team/03-vault-generation.md`` §5. The manifest is a stable
machine-readable index used by:

* The Layer-C demo agent (`scripts/demo_devops_agent.py`) to map a
  ``skill_id`` → ``vault_path`` for attribution citations.
* The composer (T-07) when merging an occupation build with persona
  builds at delivery time.
* The validator (`src/vault/validator.py`) to assert vault integrity.

Schema lives at :file:`src/vault/schema/vault-manifest-v1.json` and is
versioned via the top-level ``schema_version`` integer. Bumping the
field is a major version change.
"""

from __future__ import annotations

import json
from datetime import datetime  # noqa: TC003
from importlib import resources
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ── Sub-shapes ───────────────────────────────────────────────────────


class OccupationSummary(BaseModel):
    """Top-level summary for the occupation that anchors the vault."""

    skill_id: str
    name: str
    slug: str
    creator_handle: str
    version: str
    content_hash: str
    domains: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class PersonaSummary(BaseModel):
    """Top-level summary for a persona overlay merged into the vault."""

    skill_id: str
    name: str
    slug: str
    creator_handle: str
    version: str
    content_hash: str
    neuron_count: int = 0
    parent_occupation_id: str | None = None

    model_config = ConfigDict(extra="forbid")


class ManifestLinkEntry(BaseModel):
    """An outbound link emitted inside the manifest, with resolution flag.

    Mirrors the ``links:`` frontmatter shape on the source file but adds
    ``resolved`` so the composer can mark dangling links without
    rewriting the file.
    """

    target: str = Field(min_length=1)
    relation: Literal[
        "applies", "extends", "contradicts", "see-also", "recorded-instance-of"
    ] = "see-also"
    resolved: bool = False
    weight: float | None = Field(default=None, ge=0.0, le=1.0)

    model_config = ConfigDict(extra="forbid")


class ManifestNeuronBlock(BaseModel):
    """Neuron block mirrored into the manifest for fast read.

    Carries the same shape as :class:`~src.skills.validator.NeuronBlock`
    so consumers don't have to load the source markdown to read the
    situation/decision/outcome triplet.
    """

    situation: str
    decision: str
    outcome: str
    recorded_at: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    model_config = ConfigDict(extra="forbid")


class FileEntry(BaseModel):
    """One file's metadata inside the vault."""

    vault_path: str
    skill_id: str
    version: str
    kind: Literal["skill", "occupation", "persona", "memory_neuron"]
    creator_handle: str
    content_hash: str
    tags: list[str] = Field(default_factory=list)
    links: list[ManifestLinkEntry] = Field(default_factory=list)
    links_resolved: bool = True
    neuron: ManifestNeuronBlock | None = None

    model_config = ConfigDict(extra="forbid")


class BuildBlock(BaseModel):
    """Build/composition metadata.

    For an occupation build, ``occupation_build_id`` + ``occupation_build_hash``
    are set and ``persona_build_ids`` is empty. For a persona build,
    ``persona_build_ids`` contains exactly one entry and the occupation
    fields are null. The composer (T-07) fills both halves and computes
    ``composed_hash`` over the merged bytes.
    """

    occupation_build_id: str | None = None
    occupation_build_hash: str | None = None
    persona_build_ids: list[str] = Field(default_factory=list)
    persona_build_hashes: list[str] = Field(default_factory=list)
    composed_hash: str | None = None
    built_at: datetime
    composed_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class Warning(BaseModel):  # noqa: A001 — domain shape; spec calls it `warnings[]`
    """A non-blocking issue surfaced by the builder or composer.

    ``code`` is a stable identifier (e.g. ``vault.unresolved_link``);
    ``unresolved_link`` is populated when the warning concerns a missing
    link target.
    """

    file: str
    code: str | None = None
    unresolved_link: str | None = None
    message: str | None = None

    model_config = ConfigDict(extra="allow")


# ── Root manifest ────────────────────────────────────────────────────


class VaultManifest(BaseModel):
    """Root ``vault.json`` document.

    Always serialises with ``schema_version=1``; bumping the field is a
    major version change per ``team/03-vault-generation.md`` §13.
    """

    schema_version: Literal[1] = 1
    vault_id: str
    occupation: OccupationSummary | None = None
    personas: list[PersonaSummary] = Field(default_factory=list)
    files: list[FileEntry] = Field(default_factory=list)
    attribution_index: dict[str, str] = Field(default_factory=dict)
    build: BuildBlock
    warnings: list[Warning] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    def to_json(self) -> str:
        """Serialise to a deterministic JSON string.

        ``sort_keys=False`` keeps the field order author-meaningful (the
        schema is the source of truth). ``ensure_ascii=False`` lets
        non-ASCII characters round-trip verbatim. The output is suitable
        for direct write to ``vault.json`` inside the zip.
        """
        # Use ``mode='json'`` so datetimes serialise as ISO 8601 strings
        # rather than Python ``datetime`` objects.
        payload = self.model_dump(mode="json", exclude_none=False)
        # Inject the canonical ``$schema`` URI so consumers can validate
        # offline against the bundled JSON Schema.
        payload = {"$schema": SCHEMA_URI, **payload}
        return json.dumps(
            payload,
            indent=2,
            sort_keys=False,
            ensure_ascii=False,
        ) + "\n"


# ── Schema loading helpers ────────────────────────────────────────────


SCHEMA_URI = "https://skillsgit.com/schema/vault-manifest-v1.json"
SCHEMA_FILENAME = "vault-manifest-v1.json"


def load_schema() -> dict[str, Any]:
    """Load the bundled JSON Schema as a dict.

    Used by :mod:`src.vault.validator` to validate a built manifest at
    test time. The schema is shipped as a sibling JSON file so it can be
    copied to the ``packages/skills-schema/`` package unchanged.
    """
    pkg = resources.files("src.vault.schema")
    raw = (pkg / SCHEMA_FILENAME).read_text(encoding="utf-8")
    schema: dict[str, Any] = json.loads(raw)
    return schema


# ── Public entrypoint ────────────────────────────────────────────────


def write_manifest(manifest: VaultManifest) -> str:
    """Serialise a manifest to the canonical ``vault.json`` string.

    Thin wrapper around :meth:`VaultManifest.to_json` kept as a free
    function so the builder calls a stable name and the model can be
    refactored without touching every call-site.
    """
    return manifest.to_json()


__all__ = [
    "SCHEMA_FILENAME",
    "SCHEMA_URI",
    "BuildBlock",
    "FileEntry",
    "ManifestLinkEntry",
    "ManifestNeuronBlock",
    "OccupationSummary",
    "PersonaSummary",
    "VaultManifest",
    "Warning",
    "load_schema",
    "write_manifest",
]
