"""Full demo pipeline (T-14 marquee, Wave 5).

The end-to-end check the brief describes: from "no DB" to "composed
vault listing matches a recorded fixture" via the same code paths the
real demo CLI exercises. The shape:

1. Seed a minimal subset (3 occupation members + 2 persona neurons)
   in an in-memory SQLite DB through the same service-layer surface
   the curation scripts use.
2. Build the occupation + persona vaults via ``vault.builder``.
3. Grant the demo buyer free licenses on both.
4. Compose for the buyer via ``vault.composer.compose_for_license``.
5. Extract a deterministic ``vault_path|kind|creator|version`` listing
   from the composed manifest and assert it matches the fixture at
   ``tests/fixtures/vaults/expected-composed/composition-listing.txt``.

When the seed legitimately changes, the fixture is regenerated via
``--update-fixture`` (the test prints the new listing on a diff so
the regen is trivially "copy from CI log + paste"). Until then any
drift in the curation/build/compose pipeline fails CI with a single
deterministic diff.

Why not subprocess-shell out to ``scripts.build_devops_vault``?
Because that script wants the full dev stack (Postgres + Redis +
MinIO). The nightly ``team-smoke.yml`` workflow runs the existing
``tests/integration/test_demo_cli_snapshot.py`` against that stack;
this test gates the *same drift contract* in the unit-CI loop.
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
from src.vault import builder, composer

from tests.integration._seed_helpers import (
    add_skill_with_body,
    attach_occupation_member,
    attach_persona_neuron,
    make_buyer,
    make_creator,
    make_occupation_skill,
    make_persona_skill,
    mint_occupation_license,
    mint_persona_license,
)

# Mini fixture: 3 occupation members in 2 domains.
_MEMBER_SPECS = [
    ("ci-pipeline-architect", "CI Pipeline Architect", "ci-cd"),
    ("ops-runbook-generator", "Ops Runbook Generator", "incident"),
    ("alert-policy-architect", "Alert Policy Architect", "observability"),
]
# 2 persona neurons — each links to a base/ member.
_NEURON_SPECS = [
    ("flaky-tests-demo", "Flaky tests demo", "base/ci-pipeline-architect"),
    ("rollback-demo", "Rollback demo", "base/ops-runbook-generator"),
]


_FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "vaults"
    / "expected-composed"
    / "composition-listing.txt"
)


def _render_listing(rows: list[tuple[str, str, str, str]]) -> str:
    """Render the listing rows in the canonical pipe-delimited form.

    Sorted alphabetically by vault_path so a re-generation produces a
    deterministic diff against the fixture.
    """
    lines = [
        "# Composed vault listing — full demo pipeline snapshot (Wave 5)",
        "# One row per file: vault_path|kind|creator_handle|version",
        "",
    ]
    for path, kind, creator, version in sorted(rows):
        lines.append(f"{path}|{kind}|{creator}|{version}")
    return "\n".join(lines) + "\n"


def _parse_listing(text: str) -> list[tuple[str, str, str, str]]:
    """Reverse of :func:`_render_listing` — drops `#`-prefixed and blank lines."""
    out: list[tuple[str, str, str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) != 4:
            raise AssertionError(
                f"fixture {_FIXTURE_PATH.name}: malformed row {line!r}; "
                "expected 4 pipe-delimited fields"
            )
        out.append((parts[0], parts[1], parts[2], parts[3]))
    return out


async def _build_minimal_pipeline(
    db: AsyncSession,
    storage: InMemoryStorage,
) -> str:
    """Run the equivalent of publish_curated → build_devops_vault →
    build_devops_persona → compose against the minimal fixture set.

    Returns the storage URL of the composed zip.
    """
    # 1. Curated user + 3 published member skills (the
    #    publish_curated equivalent for our 3-skill subset).
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

    # 2. Occupation Skill + members + build (the build_devops_vault
    #    equivalent, minus the cross-link recipe + obsidian polish).
    occ_skill, _occ_row, occ_version = await make_occupation_skill(
        db, creator=curator, slug="ai-devops-engineer",
        name="AI DevOps Engineer (demo)",
        domains=["ci-cd", "incident", "observability"],
    )
    for i, (member, (_, _, domain)) in enumerate(zip(members, _MEMBER_SPECS, strict=True)):
        await attach_occupation_member(
            db, occupation_skill=occ_skill, member_skill=member,
            domain=domain, sort_order=i,
        )
    occ_build = await builder.build_occupation(
        db, occ_skill.id, occ_version.version
    )
    assert occ_build.content_hash

    # 3. Persona creator + 2 neurons + persona build (the
    #    build_devops_persona equivalent).
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
    await builder.build_persona(
        db, persona_skill.id, persona_version.version
    )

    # 4. Buyer + free licenses (the demo CLI's _ensure_demo_buyer +
    #    _ensure_free_license equivalent).
    buyer = await make_buyer(db, email="demo-buyer@skillsgit.local")
    occ_lic = await mint_occupation_license(
        db, buyer=buyer, occupation_skill=occ_skill,
    )
    await mint_persona_license(
        db, buyer=buyer, persona_skill=persona_skill,
        target_occupation_skill_id=occ_skill.id,
    )

    # 5. Compose for the buyer (the demo CLI's _compose_and_load
    #    equivalent).
    result = await composer.compose_for_license(
        db, buyer_id=uuid.UUID(str(buyer.id)),
        occupation_license_id=uuid.UUID(str(occ_lic.id)),
    )
    return result.storage_url


def _listing_from_zip(zip_bytes: bytes) -> list[tuple[str, str, str, str]]:
    """Extract the demo-CLI-shaped listing from a composed zip's manifest."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        manifest = json.loads(zf.read("vault.json").decode("utf-8"))
    rows: list[tuple[str, str, str, str]] = []
    for entry in manifest.get("files", []):
        rows.append(
            (
                entry["vault_path"],
                entry["kind"],
                entry["creator_handle"],
                entry["version"],
            )
        )
    return rows


@pytest.mark.asyncio
async def test_full_demo_pipeline_listing_matches_fixture(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Marquee test: every step of the demo pipeline runs and the final
    listing matches the recorded fixture. Drift in the curation /
    build / compose pipeline fails this test loudly with one
    deterministic diff.
    """
    storage_url = await _build_minimal_pipeline(db_session, memory_storage)
    zip_bytes = await memory_storage.get_object(storage_url)
    actual = _listing_from_zip(zip_bytes)
    assert actual, "composed zip should yield at least one file row"

    # Allow ``UPDATE_DEMO_PIPELINE_FIXTURE=1`` to regenerate the file
    # in a single explicit step. Without that env var, drift fails the
    # test with a copy-pasteable diff.
    if os.environ.get("UPDATE_DEMO_PIPELINE_FIXTURE") == "1":
        _FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _FIXTURE_PATH.write_text(_render_listing(actual), encoding="utf-8")
        return

    if not _FIXTURE_PATH.exists():
        pytest.fail(
            f"Fixture missing at {_FIXTURE_PATH}. Regenerate via "
            f"UPDATE_DEMO_PIPELINE_FIXTURE=1 uv run pytest "
            f"tests/integration/test_full_demo_pipeline.py and commit "
            f"the file."
        )

    expected = _parse_listing(_FIXTURE_PATH.read_text(encoding="utf-8"))
    assert sorted(actual) == sorted(expected), (
        f"Composed vault listing drifted from fixture.\n"
        f"actual rows: {len(actual)}\n"
        f"expected rows: {len(expected)}\n"
        f"only-in-actual (first 3): "
        f"{sorted(set(actual) - set(expected))[:3]}\n"
        f"only-in-expected (first 3): "
        f"{sorted(set(expected) - set(actual))[:3]}\n"
        f"Regenerate via UPDATE_DEMO_PIPELINE_FIXTURE=1 once you've "
        f"verified the new state is intentional."
    )
