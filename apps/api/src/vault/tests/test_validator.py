"""Unit tests for :mod:`src.vault.validator`.

The validator opens a built zip and asserts the integrity rules in
``team/03-vault-generation.md`` §6 + ADR-010. These tests build minimal
valid + invalid zips by hand so the tests run without the full builder.
"""

from __future__ import annotations

import io
import json
import zipfile
from datetime import UTC, datetime

from src.vault.manifest import (
    BuildBlock,
    FileEntry,
    ManifestLinkEntry,
    ManifestNeuronBlock,
    OccupationSummary,
    PersonaSummary,
    VaultManifest,
    write_manifest,
)
from src.vault.validator import validate_vault

# ── Helpers ─────────────────────────────────────────────────────────


def _build_block() -> BuildBlock:
    return BuildBlock(
        built_at=datetime(2026, 5, 26, 12, 0, 0, tzinfo=UTC),
    )


def _occupation() -> OccupationSummary:
    return OccupationSummary(
        skill_id="018f0000-0000-7000-8000-000000000001",
        name="AI DevOps Engineer",
        slug="ai-devops-engineer",
        creator_handle="skillsgit-curated",
        version="1.0.0",
        content_hash="a" * 64,
        domains=["ci-cd"],
    )


def _attribution_comment(*, vault_path: str, skill_id: str = "00000000-0000-0000-0000-000000000001") -> str:
    return (
        "<!-- skg-attribution:\n"
        f"  vault_path: {json.dumps(vault_path)}\n"
        f"  skill_id: {json.dumps(skill_id)}\n"
        '  version: "1.0.0"\n'
        '  kind: "skill"\n'
        '  creator_handle: "skillsgit-curated"\n'
        '  content_hash: "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"\n'
        '  built_at: "2026-05-26T12:00:00Z"\n'
        "-->\n"
    )


def _skill_md(vault_path: str, *, with_attribution: bool = True, link_target: str | None = None) -> str:
    body = (
        "---\n"
        f"id: skillsgit-curated/{vault_path.rsplit('/', maxsplit=1)[-1].removesuffix('.md')}\n"
        "version: 1.0.0\n"
        "name: T\n"
        "description: t\n"
        "category: x\n"
        "tags: [x]\n"
        "license_type: free\n"
        "ai:\n"
        "  required_models: [claude-sonnet-4-7]\n"
        "---\n\n"
        "## When to use\nUse it.\n\n"
        "## How to apply\nDo it.\n"
    )
    if link_target is not None:
        body += f"\n## Linked notes\n\n- [[{link_target}]] — see-also\n"
    if with_attribution:
        body += "\n" + _attribution_comment(vault_path=vault_path) + "\n"
    return body


def _build_zip(files: list[tuple[str, bytes]]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, data in sorted(files, key=lambda p: p[0]):
            zf.writestr(path, data)
    return buf.getvalue()


def _file_entry(*, path: str, skill_id: str, kind: str = "skill", links: list[ManifestLinkEntry] | None = None, neuron: ManifestNeuronBlock | None = None) -> FileEntry:
    return FileEntry(
        vault_path=path,
        skill_id=skill_id,
        version="1.0.0",
        kind=kind,  # type: ignore[arg-type,unused-ignore]
        creator_handle="skillsgit-curated",
        content_hash="f" * 64,
        tags=["x"],
        links=links or [],
        links_resolved=all(link.resolved for link in (links or [])),
        neuron=neuron,
    )


# ── Happy paths ─────────────────────────────────────────────────────


def test_validate_minimal_occupation_zip_passes() -> None:
    """Occupation build with README + index + manifest + 1 file → valid."""
    manifest = VaultManifest(
        schema_version=1,
        vault_id="018f0000-0000-7000-8000-deadbeefcafe",
        occupation=_occupation(),
        personas=[],
        files=[
            _file_entry(
                path="domains/ci-cd/devops-ci-pipeline-architect.md",
                skill_id="018f0000-0000-7000-8000-000000000002",
            )
        ],
        attribution_index={
            "018f0000-0000-7000-8000-000000000002":
                "domains/ci-cd/devops-ci-pipeline-architect.md",
        },
        build=_build_block(),
        warnings=[],
    )
    zip_bytes = _build_zip(
        [
            ("README.md", b"# Test"),
            ("00-index.md", b"# Index"),
            ("vault.json", write_manifest(manifest).encode("utf-8")),
            (
                "domains/ci-cd/devops-ci-pipeline-architect.md",
                _skill_md("domains/ci-cd/devops-ci-pipeline-architect.md").encode(
                    "utf-8"
                ),
            ),
        ]
    )
    result = validate_vault(zip_bytes)
    assert result.is_valid, [(e.field, e.code, e.message) for e in result.errors]


def test_validate_minimal_persona_zip_passes() -> None:
    """Persona-only build with persona.json + README + 1 neuron → valid."""
    persona = PersonaSummary(
        skill_id="018f0000-0000-7000-8000-000000000003",
        name="Jane's On-Call Brain",
        slug="jane-on-call",
        creator_handle="jane-devops",
        version="1.0.0",
        content_hash="b" * 64,
        neuron_count=1,
    )
    neuron_path = "personas/jane-devops/jane-on-call/neurons/2024-08-flaky-tests.md"
    manifest = VaultManifest(
        schema_version=1,
        vault_id="018f0000-0000-7000-8000-deadbeefcafe",
        occupation=None,
        personas=[persona],
        files=[
            _file_entry(
                path=neuron_path,
                skill_id="018f0000-0000-7000-8000-000000000004",
                kind="memory_neuron",
                neuron=ManifestNeuronBlock(
                    situation="x", decision="y", outcome="z",
                ),
            )
        ],
        attribution_index={
            "018f0000-0000-7000-8000-000000000004": neuron_path,
        },
        build=_build_block(),
        warnings=[],
    )
    persona_root = "personas/jane-devops/jane-on-call"
    zip_bytes = _build_zip(
        [
            (f"{persona_root}/README.md", b"# README"),
            (
                f"{persona_root}/persona.json",
                write_manifest(manifest).encode("utf-8"),
            ),
            (neuron_path, _skill_md(neuron_path).encode("utf-8")),
        ]
    )
    result = validate_vault(zip_bytes)
    assert result.is_valid, [(e.field, e.code, e.message) for e in result.errors]


# ── Failure modes ───────────────────────────────────────────────────


def test_validate_rejects_non_zip() -> None:
    result = validate_vault(b"not a zip")
    assert not result.is_valid
    assert any(e.code == "vault.bad_zip" for e in result.errors)


def test_validate_missing_manifest() -> None:
    zip_bytes = _build_zip(
        [
            ("README.md", b"# Test"),
            ("00-index.md", b"# Index"),
        ]
    )
    result = validate_vault(zip_bytes)
    assert not result.is_valid
    assert any(e.code == "vault.missing_manifest" for e in result.errors)


def test_validate_missing_readme_for_occupation_build() -> None:
    manifest = VaultManifest(
        schema_version=1,
        vault_id="x",
        occupation=_occupation(),
        files=[
            _file_entry(
                path="domains/x/a.md",
                skill_id="018f0000-0000-7000-8000-000000000002",
            )
        ],
        attribution_index={
            "018f0000-0000-7000-8000-000000000002": "domains/x/a.md",
        },
        build=_build_block(),
    )
    zip_bytes = _build_zip(
        [
            # README.md missing on purpose.
            ("00-index.md", b"# Index"),
            ("vault.json", write_manifest(manifest).encode("utf-8")),
            ("domains/x/a.md", _skill_md("domains/x/a.md").encode("utf-8")),
        ]
    )
    result = validate_vault(zip_bytes)
    assert not result.is_valid
    assert any(
        e.code == "vault.required_file_missing" and e.field == "README.md"
        for e in result.errors
    )


def test_validate_file_listed_in_manifest_but_missing_from_zip() -> None:
    manifest = VaultManifest(
        schema_version=1,
        vault_id="x",
        occupation=_occupation(),
        files=[
            _file_entry(
                path="domains/x/ghost.md",
                skill_id="018f0000-0000-7000-8000-000000000002",
            )
        ],
        attribution_index={
            "018f0000-0000-7000-8000-000000000002": "domains/x/ghost.md",
        },
        build=_build_block(),
    )
    zip_bytes = _build_zip(
        [
            ("README.md", b"# Test"),
            ("00-index.md", b"# Index"),
            ("vault.json", write_manifest(manifest).encode("utf-8")),
            # The ghost file is NOT in the zip.
        ]
    )
    result = validate_vault(zip_bytes)
    assert not result.is_valid
    assert any(
        e.code == "vault.manifest_file_missing" for e in result.errors
    )


def test_validate_missing_attribution_comment_in_file() -> None:
    manifest = VaultManifest(
        schema_version=1,
        vault_id="x",
        occupation=_occupation(),
        files=[
            _file_entry(
                path="domains/x/a.md",
                skill_id="018f0000-0000-7000-8000-000000000002",
            )
        ],
        attribution_index={
            "018f0000-0000-7000-8000-000000000002": "domains/x/a.md",
        },
        build=_build_block(),
    )
    body_without_comment = _skill_md("domains/x/a.md", with_attribution=False)
    zip_bytes = _build_zip(
        [
            ("README.md", b"# Test"),
            ("00-index.md", b"# Index"),
            ("vault.json", write_manifest(manifest).encode("utf-8")),
            ("domains/x/a.md", body_without_comment.encode("utf-8")),
        ]
    )
    result = validate_vault(zip_bytes)
    assert not result.is_valid
    assert any(
        e.code == "vault.missing_attribution" and e.field == "domains/x/a.md"
        for e in result.errors
    )


def test_validate_unresolved_wiki_link_in_linked_notes() -> None:
    """Linked-notes section pointing at a missing file → unresolved_wikilink."""
    manifest = VaultManifest(
        schema_version=1,
        vault_id="x",
        occupation=_occupation(),
        files=[
            _file_entry(
                path="domains/x/a.md",
                skill_id="018f0000-0000-7000-8000-000000000002",
            )
        ],
        attribution_index={
            "018f0000-0000-7000-8000-000000000002": "domains/x/a.md",
        },
        build=_build_block(),
    )
    body = _skill_md(
        "domains/x/a.md",
        with_attribution=True,
        link_target="domains/x/missing",
    )
    zip_bytes = _build_zip(
        [
            ("README.md", b"# Test"),
            ("00-index.md", b"# Index"),
            ("vault.json", write_manifest(manifest).encode("utf-8")),
            ("domains/x/a.md", body.encode("utf-8")),
        ]
    )
    result = validate_vault(zip_bytes)
    assert not result.is_valid
    assert any(
        e.code == "vault.unresolved_wikilink" for e in result.errors
    )


def test_validate_attribution_index_dangles() -> None:
    """An attribution_index entry pointing at a non-files[] path is flagged."""
    manifest = VaultManifest(
        schema_version=1,
        vault_id="x",
        occupation=_occupation(),
        files=[
            _file_entry(
                path="domains/x/a.md",
                skill_id="018f0000-0000-7000-8000-000000000002",
            )
        ],
        attribution_index={
            # Points at a path not in files[].
            "018f0000-0000-7000-8000-000000000099": "domains/x/ghost.md",
            "018f0000-0000-7000-8000-000000000002": "domains/x/a.md",
        },
        build=_build_block(),
    )
    zip_bytes = _build_zip(
        [
            ("README.md", b"# Test"),
            ("00-index.md", b"# Index"),
            ("vault.json", write_manifest(manifest).encode("utf-8")),
            ("domains/x/a.md", _skill_md("domains/x/a.md").encode("utf-8")),
        ]
    )
    result = validate_vault(zip_bytes)
    assert not result.is_valid
    assert any(
        e.code == "vault.attribution_dangles" for e in result.errors
    )


def test_validate_memory_neuron_must_have_neuron_block() -> None:
    """kind=memory_neuron files require a neuron block in the manifest."""
    manifest = VaultManifest(
        schema_version=1,
        vault_id="x",
        occupation=None,
        personas=[
            PersonaSummary(
                skill_id="018f0000-0000-7000-8000-000000000003",
                name="P", slug="p", creator_handle="cur",
                version="1.0.0", content_hash="b" * 64, neuron_count=1,
            )
        ],
        files=[
            _file_entry(
                path="personas/cur/p/neurons/n1.md",
                skill_id="018f0000-0000-7000-8000-000000000004",
                kind="memory_neuron",
                neuron=None,
            )
        ],
        attribution_index={
            "018f0000-0000-7000-8000-000000000004":
                "personas/cur/p/neurons/n1.md",
        },
        build=_build_block(),
    )
    persona_root = "personas/cur/p"
    zip_bytes = _build_zip(
        [
            (f"{persona_root}/README.md", b"# R"),
            (
                f"{persona_root}/persona.json",
                write_manifest(manifest).encode("utf-8"),
            ),
            (
                "personas/cur/p/neurons/n1.md",
                _skill_md("personas/cur/p/neurons/n1.md").encode("utf-8"),
            ),
        ]
    )
    result = validate_vault(zip_bytes)
    assert not result.is_valid
    assert any(
        e.code == "vault.neuron_block_missing" for e in result.errors
    )


def test_validate_malformed_manifest_json() -> None:
    """Garbage in vault.json → ``vault.malformed_manifest_json``."""
    zip_bytes = _build_zip(
        [
            ("README.md", b"# Test"),
            ("00-index.md", b"# Index"),
            ("vault.json", b"this is { not ] valid json"),
        ]
    )
    result = validate_vault(zip_bytes)
    assert not result.is_valid
    assert any(
        e.code == "vault.malformed_manifest_json" for e in result.errors
    )
