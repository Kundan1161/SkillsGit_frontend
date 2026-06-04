"""Unit tests for :mod:`src.vault.manifest`.

Covers:

* Round-trip: build a :class:`VaultManifest`, serialise, parse, assert equal.
* :func:`write_manifest` output validates against the bundled JSON Schema.
* The schema file is loadable and at version 1.
* Bad inputs (unknown link relation, malformed file entry) are rejected
  at the Pydantic boundary.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import jsonschema
import pytest
from pydantic import ValidationError

from src.vault.manifest import (
    SCHEMA_URI,
    BuildBlock,
    FileEntry,
    ManifestLinkEntry,
    ManifestNeuronBlock,
    OccupationSummary,
    PersonaSummary,
    VaultManifest,
    Warning,  # noqa: A004 — domain shape; spec calls it `warnings[]`
    load_schema,
    write_manifest,
)

# ── Fixtures (Python-side) ──────────────────────────────────────────


def _occupation() -> OccupationSummary:
    return OccupationSummary(
        skill_id="018f0000-0000-7000-8000-000000000001",
        name="AI DevOps Engineer",
        slug="ai-devops-engineer",
        creator_handle="skillsgit-curated",
        version="1.0.0",
        content_hash="a" * 64,
        domains=["ci-cd", "observability"],
    )


def _file(*, path: str, kind: str = "skill") -> FileEntry:
    return FileEntry(
        vault_path=path,
        skill_id="018f0000-0000-7000-8000-000000000002",
        version="1.0.0",
        kind=kind,  # type: ignore[arg-type,unused-ignore]
        creator_handle="skillsgit-curated",
        content_hash="b" * 64,
        tags=["ci-cd"],
        links=[],
        links_resolved=True,
        neuron=None,
    )


def _build_block() -> BuildBlock:
    return BuildBlock(
        occupation_build_id="018f0000-0000-7000-8000-00000000000a",
        occupation_build_hash="c" * 64,
        persona_build_ids=[],
        persona_build_hashes=[],
        composed_hash=None,
        built_at=datetime(2026, 5, 26, 12, 0, 0, tzinfo=UTC),
        composed_at=None,
    )


# ── Round-trip ──────────────────────────────────────────────────────


def test_manifest_roundtrips_through_json() -> None:
    """The model serialises and re-parses without loss."""
    manifest = VaultManifest(
        schema_version=1,
        vault_id="018f0000-0000-7000-8000-deadbeefcafe",
        occupation=_occupation(),
        personas=[],
        files=[
            _file(path="domains/ci-cd/devops-ci-pipeline-architect.md"),
            _file(path="domains/observability/observability-dashboard-architect.md"),
        ],
        attribution_index={
            "018f0000-0000-7000-8000-000000000002":
                "domains/ci-cd/devops-ci-pipeline-architect.md",
        },
        build=_build_block(),
        warnings=[],
    )
    serialised = write_manifest(manifest)
    payload = json.loads(serialised)
    assert payload["$schema"] == SCHEMA_URI
    # Strip $schema before round-trip (the Pydantic model doesn't carry it).
    payload.pop("$schema")
    reparsed = VaultManifest.model_validate(payload)
    assert reparsed.schema_version == 1
    assert reparsed.occupation is not None
    assert reparsed.occupation.slug == "ai-devops-engineer"
    assert len(reparsed.files) == 2


def test_manifest_serialised_matches_json_schema() -> None:
    """Output of write_manifest() validates against the bundled schema."""
    manifest = VaultManifest(
        schema_version=1,
        vault_id="018f0000-0000-7000-8000-deadbeefcafe",
        occupation=_occupation(),
        personas=[
            PersonaSummary(
                skill_id="018f0000-0000-7000-8000-000000000003",
                name="Jane's On-Call Brain",
                slug="jane-on-call",
                creator_handle="jane-devops",
                version="1.0.0",
                content_hash="d" * 64,
                neuron_count=12,
                parent_occupation_id="018f0000-0000-7000-8000-000000000001",
            )
        ],
        files=[
            _file(path="domains/ci-cd/devops-ci-pipeline-architect.md"),
            FileEntry(
                vault_path=(
                    "personas/jane-devops/jane-on-call/neurons/"
                    "2024-08-flaky-tests.md"
                ),
                skill_id="018f0000-0000-7000-8000-000000000004",
                version="1.0.0",
                kind="memory_neuron",
                creator_handle="jane-devops",
                content_hash="e" * 64,
                tags=["incident", "flaky-tests"],
                links=[
                    ManifestLinkEntry(
                        target=(
                            "domains/ci-cd/devops-ci-pipeline-architect"
                        ),
                        relation="applies",
                        resolved=True,
                        weight=0.9,
                    )
                ],
                links_resolved=True,
                neuron=ManifestNeuronBlock(
                    situation="CI started failing intermittently",
                    decision="Pinned the upstream redis-py to 5.0.3",
                    outcome="Pipelines green within 20 minutes",
                    recorded_at="2024-08-12",
                    confidence=0.8,
                ),
            ),
        ],
        attribution_index={
            "018f0000-0000-7000-8000-000000000002":
                "domains/ci-cd/devops-ci-pipeline-architect.md",
            "018f0000-0000-7000-8000-000000000004": (
                "personas/jane-devops/jane-on-call/neurons/"
                "2024-08-flaky-tests.md"
            ),
        },
        build=_build_block(),
        warnings=[
            Warning(
                file="personas/jane-devops/jane-on-call/neurons/2024-08-flaky-tests.md",
                code="vault.unresolved_link",
                unresolved_link="missing-target",
                message="Link target did not resolve.",
            )
        ],
    )
    payload = json.loads(write_manifest(manifest))
    schema = load_schema()
    jsonschema.Draft7Validator(schema).validate(payload)


def test_schema_is_loadable_and_versioned() -> None:
    schema = load_schema()
    assert schema["title"] == "Vault Manifest v1"
    assert schema["properties"]["schema_version"]["const"] == 1
    # The two top-level required types are present.
    assert "OccupationSummary" in schema["$defs"]
    assert "PersonaSummary" in schema["$defs"]


# ── Pydantic rejects malformed inputs ──────────────────────────────


def test_link_entry_rejects_unknown_relation() -> None:
    with pytest.raises(ValidationError):
        ManifestLinkEntry(
            target="foo",
            relation="not-a-real-relation",  # type: ignore[arg-type,unused-ignore]
            resolved=False,
        )


def test_file_entry_requires_kind_in_enum() -> None:
    with pytest.raises(ValidationError):
        FileEntry(
            vault_path="x.md",
            skill_id="018f...",
            version="1.0.0",
            kind="nonsense",  # type: ignore[arg-type,unused-ignore]
            creator_handle="cur",
            content_hash="a" * 64,
        )


def test_link_entry_weight_must_be_between_0_and_1() -> None:
    with pytest.raises(ValidationError):
        ManifestLinkEntry(target="t", relation="see-also", resolved=False, weight=2.0)


def test_manifest_persona_only_build_has_no_occupation() -> None:
    """A persona-only build sets occupation=None and personas=[summary]."""
    manifest = VaultManifest(
        schema_version=1,
        vault_id="018f0000-0000-7000-8000-deadbeefcafe",
        occupation=None,
        personas=[
            PersonaSummary(
                skill_id="018f0000-0000-7000-8000-000000000003",
                name="Jane's On-Call Brain",
                slug="jane-on-call",
                creator_handle="jane-devops",
                version="1.0.0",
                content_hash="d" * 64,
                neuron_count=3,
            )
        ],
        files=[
            FileEntry(
                vault_path=(
                    "personas/jane-devops/jane-on-call/neurons/n1.md"
                ),
                skill_id="018f0000-0000-7000-8000-000000000004",
                version="1.0.0",
                kind="memory_neuron",
                creator_handle="jane-devops",
                content_hash="e" * 64,
                tags=[],
                links=[],
                neuron=ManifestNeuronBlock(
                    situation="x", decision="y", outcome="z",
                ),
            ),
        ],
        attribution_index={},
        build=_build_block(),
        warnings=[],
    )
    payload = json.loads(write_manifest(manifest))
    assert payload["occupation"] is None
    assert len(payload["personas"]) == 1
    schema = load_schema()
    jsonschema.Draft7Validator(schema).validate(payload)
