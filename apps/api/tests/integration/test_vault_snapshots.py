"""Vault snapshot fixtures (T-14 §B, Wave 5).

Asserts the live builds match these recorded artifacts:

* ``fixtures/vaults/expected-devops-vault/vault.json`` — the full
  occupation-manifest JSON produced by the integration-seed pipeline.
* ``fixtures/vaults/expected-devops-vault/file-listing.txt`` — sorted
  list of every file path in the produced zip.
* ``fixtures/vaults/expected-devops-persona/persona.json`` — same for
  the persona build.

The fixtures here use the same minimal seed as
:mod:`test_full_demo_pipeline` (3 occupation members + 2 persona
neurons + 1 buyer composing). When a curator legitimately changes the
seed, ``UPDATE_VAULT_SNAPSHOTS=1`` regenerates every fixture in one
pass and the test passes. Until then any drift fails CI noisily with
a deterministic diff per fixture.

Why a seed instead of the real 30-skill build? Because the snapshot
test runs in the unit-CI loop (no Postgres / MinIO required). The
full 30-skill build's snapshot lives at
``tests/fixtures/demo/expected-vault-listing.txt`` and is covered by
``tests/integration/test_demo_cli_snapshot.py`` against the live dev
stack — that's the "real" drift gate.
"""

from __future__ import annotations

import io
import json
import os
import uuid
import zipfile
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.skills.models import SkillKind
from src.storage.s3 import InMemoryStorage
from src.vault import builder

from tests.integration._seed_helpers import (
    add_skill_with_body,
    attach_occupation_member,
    attach_persona_neuron,
    make_creator,
    make_occupation_skill,
    make_persona_skill,
)

_FIXTURES_ROOT = (
    Path(__file__).resolve().parent.parent / "fixtures" / "vaults"
)
_OCC_DIR = _FIXTURES_ROOT / "expected-devops-vault"
_PER_DIR = _FIXTURES_ROOT / "expected-devops-persona"

# Same fixture skills as test_full_demo_pipeline so the snapshots
# capture the same minimal recipe (drift in one ↔ drift in the other).
_MEMBER_SPECS = [
    ("ci-pipeline-architect", "CI Pipeline Architect", "ci-cd"),
    ("ops-runbook-generator", "Ops Runbook Generator", "incident"),
    ("alert-policy-architect", "Alert Policy Architect", "observability"),
]
_NEURON_SPECS = [
    ("flaky-tests-demo", "Flaky tests demo", "base/ci-pipeline-architect"),
    ("rollback-demo", "Rollback demo", "base/ops-runbook-generator"),
]


# ── JSON normalization ──────────────────────────────────────────────


# Manifest fields whose values vary across runs (UUIDs, hashes,
# timestamps). We replace them with stable sentinels before snapshot
# comparison; the regenerator strips them too so the fixture stays
# canonical.
_VOLATILE_TOP_FIELDS = ("vault_id",)


def _normalize_manifest(manifest: dict) -> dict:
    """Strip volatile fields so the fixture diff is meaningful."""
    out = dict(manifest)

    # Strip $schema (offline URI) for stable comparison.
    out.pop("$schema", None)

    # Replace volatile top-level fields.
    for k in _VOLATILE_TOP_FIELDS:
        if k in out:
            out[k] = "<volatile>"

    # build.* — every id/hash/timestamp varies across runs.
    if "build" in out and isinstance(out["build"], dict):
        build = dict(out["build"])
        for field in (
            "occupation_build_id",
            "occupation_build_hash",
            "persona_build_ids",
            "persona_build_hashes",
            "composed_hash",
            "built_at",
            "composed_at",
        ):
            if field in build:
                build[field] = "<volatile>"
        out["build"] = build

    # files[].skill_id, content_hash, version (since version is fixed
    # at 1.0.0 we keep it; but skill_id is row-bound).
    if "files" in out and isinstance(out["files"], list):
        files = []
        for entry in out["files"]:
            if isinstance(entry, dict):
                e = dict(entry)
                if "skill_id" in e:
                    e["skill_id"] = "<volatile>"
                if "content_hash" in e:
                    e["content_hash"] = "<volatile>"
                files.append(e)
            else:
                files.append(entry)
        out["files"] = files

    # attribution_index — keys are skill_ids (volatile); the values
    # are vault_paths (stable). Rebuild keyed by vault_path order.
    if "attribution_index" in out and isinstance(out["attribution_index"], dict):
        out["attribution_index"] = {
            "<volatile-skill-id>": v
            for v in sorted(out["attribution_index"].values())
        }

    # occupation / personas — strip skill_id + content_hash.
    if "occupation" in out and isinstance(out["occupation"], dict):
        occ = dict(out["occupation"])
        for k in ("skill_id", "content_hash"):
            if k in occ:
                occ[k] = "<volatile>"
        out["occupation"] = occ
    if "personas" in out and isinstance(out["personas"], list):
        personas = []
        for p in out["personas"]:
            if isinstance(p, dict):
                pp = dict(p)
                for k in ("skill_id", "content_hash", "parent_occupation_id"):
                    if k in pp:
                        pp[k] = "<volatile>"
                personas.append(pp)
            else:
                personas.append(p)
        out["personas"] = personas

    return out


def _dump_canonical(payload: dict) -> str:
    """Pretty JSON with sorted keys so a fixture diff stays tight."""
    return json.dumps(payload, sort_keys=True, indent=2) + "\n"


# ── Seed builders ──────────────────────────────────────────────────


async def _build_occupation_seed(
    db: AsyncSession, storage: InMemoryStorage,
) -> tuple[bytes, dict]:
    """Run the occupation portion of the seed pipeline.

    Returns ``(zip_bytes, manifest_json_dict)``.
    """
    curator = await make_creator(
        db, email="curated@skillsgit.local", handle="skillsgit-curated",
    )
    members = []
    for slug, name, _domain in _MEMBER_SPECS:
        skill, _ = await add_skill_with_body(
            db, storage=storage, creator=curator,
            creator_handle="skillsgit-curated",
            slug=slug, name=name,
        )
        members.append(skill)
    occ_skill, _, occ_version = await make_occupation_skill(
        db, creator=curator, slug="ai-devops-engineer",
        name="AI DevOps Engineer (demo)",
        domains=["ci-cd", "incident", "observability"],
    )
    for i, (member, (_, _, domain)) in enumerate(zip(members, _MEMBER_SPECS, strict=True)):
        await attach_occupation_member(
            db, occupation_skill=occ_skill, member_skill=member,
            domain=domain, sort_order=i,
        )
    build = await builder.build_occupation(db, occ_skill.id, occ_version.version)
    zip_bytes = await storage.get_object(build.storage_url)
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        manifest = json.loads(zf.read("vault.json").decode("utf-8"))
    return zip_bytes, manifest


async def _build_persona_seed(
    db: AsyncSession, storage: InMemoryStorage,
) -> tuple[bytes, dict]:
    """Run the persona portion of the seed pipeline.

    Returns ``(zip_bytes, persona_manifest_json_dict)``. Uses the same
    fixture occupation so the persona's ``parent_occupation_id`` resolves.
    """
    curator = await make_creator(
        db, email="curated@skillsgit.local", handle="skillsgit-curated",
    )
    for slug, name, _ in _MEMBER_SPECS:
        await add_skill_with_body(
            db, storage=storage, creator=curator,
            creator_handle="skillsgit-curated", slug=slug, name=name,
        )
    occ_skill, _, _ = await make_occupation_skill(
        db, creator=curator, slug="ai-devops-engineer",
        name="AI DevOps Engineer (demo)",
        domains=["ci-cd", "incident", "observability"],
    )

    persona_creator = await make_creator(
        db, email="jane-devops-demo@skillsgit.local",
        handle="jane-devops-demo",
    )
    persona_skill, persona_row, persona_version = await make_persona_skill(
        db, creator=persona_creator, slug="incident-veteran",
        name="Incident Veteran (demo)",
        parent_occupation_skill_id=occ_skill.id,
    )
    neuron_block = {
        "situation": "Demo situation.",
        "decision": "Demo decision.",
        "outcome": "Demo outcome.",
        "recorded_at": "2024-10-15",
        "confidence": "high",
    }
    for i, (slug, name, link_target) in enumerate(_NEURON_SPECS):
        neuron_skill, _ = await add_skill_with_body(
            db, storage=storage, creator=persona_creator,
            creator_handle="jane-devops-demo",
            slug=slug, name=name,
            kind=SkillKind.MEMORY_NEURON,
            links=[{"target": link_target, "relation": "applies"}],
            neuron_block=neuron_block,
            parent_occupation_id="skillsgit-curated/ai-devops-engineer",
        )
        await attach_persona_neuron(
            db, persona=persona_row, neuron_skill=neuron_skill,
            sort_order=i,
        )
    build = await builder.build_persona(db, persona_skill.id, persona_version.version)
    zip_bytes = await storage.get_object(build.storage_url)
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        persona_jsons = [
            n for n in zf.namelist() if n.endswith("/persona.json")
        ]
        assert len(persona_jsons) == 1, persona_jsons
        manifest = json.loads(zf.read(persona_jsons[0]).decode("utf-8"))
    return zip_bytes, manifest


def _file_listing(zip_bytes: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        names = sorted(n for n in zf.namelist() if not n.endswith("/"))
    return "\n".join(names) + "\n"


def _maybe_write(path: Path, content: str) -> bool:
    """Write only when the env opt-in is set. Returns True if written."""
    if os.environ.get("UPDATE_VAULT_SNAPSHOTS") != "1":
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


# ── Tests ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_occupation_vault_snapshot_matches_fixture(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Snapshot the occupation build's vault.json + file listing."""
    zip_bytes, manifest = await _build_occupation_seed(
        db_session, memory_storage
    )
    normalized = _normalize_manifest(manifest)
    actual_manifest_text = _dump_canonical(normalized)
    actual_listing = _file_listing(zip_bytes)

    manifest_fixture = _OCC_DIR / "vault.json"
    listing_fixture = _OCC_DIR / "file-listing.txt"

    if _maybe_write(manifest_fixture, actual_manifest_text):
        _maybe_write(listing_fixture, actual_listing)
        return

    if not manifest_fixture.exists() or not listing_fixture.exists():
        pytest.fail(
            f"Fixture(s) missing under {_OCC_DIR}. Regenerate via "
            f"UPDATE_VAULT_SNAPSHOTS=1 uv run pytest "
            f"tests/integration/test_vault_snapshots.py and commit."
        )

    expected_manifest = manifest_fixture.read_text(encoding="utf-8")
    expected_listing = listing_fixture.read_text(encoding="utf-8")

    assert actual_manifest_text == expected_manifest, (
        "Occupation vault.json drift detected. "
        "Diff between live build and fixture above; regenerate with "
        "UPDATE_VAULT_SNAPSHOTS=1 once you've verified the new state "
        "is intentional."
    )
    assert actual_listing == expected_listing, (
        "Occupation file listing drift detected. Regenerate with "
        "UPDATE_VAULT_SNAPSHOTS=1 once verified."
    )


@pytest.mark.asyncio
async def test_persona_vault_snapshot_matches_fixture(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Snapshot the persona build's persona.json."""
    _zip_bytes, manifest = await _build_persona_seed(
        db_session, memory_storage
    )
    normalized = _normalize_manifest(manifest)
    actual_manifest_text = _dump_canonical(normalized)

    manifest_fixture = _PER_DIR / "persona.json"
    if _maybe_write(manifest_fixture, actual_manifest_text):
        return

    if not manifest_fixture.exists():
        pytest.fail(
            f"Fixture missing at {manifest_fixture}. Regenerate via "
            f"UPDATE_VAULT_SNAPSHOTS=1 uv run pytest "
            f"tests/integration/test_vault_snapshots.py and commit."
        )

    expected_manifest = manifest_fixture.read_text(encoding="utf-8")
    assert actual_manifest_text == expected_manifest, (
        "Persona persona.json drift detected. Regenerate with "
        "UPDATE_VAULT_SNAPSHOTS=1 once verified."
    )


# Silence unused-import warning for ``uuid`` when type-checkers run on
# this file (it's imported above to keep mypy happy if a future
# regenerator wants UUID coercion).
_ = uuid
