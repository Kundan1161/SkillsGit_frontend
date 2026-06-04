"""End-to-end vault composition (T-14, Wave 5).

Asserts the T-07 acceptance criteria in an integration setting that
mirrors the demo CLI's compose path:

1. Seed: curator + occupation with 3 member skills, persona creator +
   persona with 2 neurons (each linking to a base member).
2. Build the occupation + the persona via the real builder.
3. Mint buyer + free occupation + free persona license.
4. Compose for the buyer.
5. Assert: presigned URL works; composed zip contains both occupation
   files and persona files; manifest has zero real warnings (Polish 2
   from this wave fixed the ``base/*`` resolver); two consecutive
   downloads after a cache invalidate differ only in the watermark
   comment lines (bytewise stable elsewhere).
"""

from __future__ import annotations

import io
import re
import zipfile

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core import cache as cache_mod
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

# Match the watermark comment append_watermark emits.
_WATERMARK_RE = re.compile(
    r"<!--\s*license:.*?ts:.*?-->", re.DOTALL
)


def _strip_watermarks(text: str) -> str:
    """Remove every watermark comment so two buyers' .md content can be
    compared apples-to-apples."""
    return _WATERMARK_RE.sub("<!-- WATERMARK -->", text)


async def _seed_full_stack(
    db: AsyncSession,
    storage: InMemoryStorage,
    *,
    buyer_email: str = "buyer-compose@x.local",
) -> tuple[
    object,  # occ skill
    object,  # persona skill
    object,  # occupation license
    object,  # persona license
    object,  # buyer
]:
    """Seed the full occupation + persona + buyer stack used by every
    test in this module."""
    occ_creator = await make_creator(
        db, email="occ@x.local", handle="occ-compose"
    )
    member_a, _ = await add_skill_with_body(
        db, storage=storage, creator=occ_creator,
        creator_handle="occ-compose", slug="ops-runbook-generator",
        name="Ops Runbook Generator",
    )
    member_b, _ = await add_skill_with_body(
        db, storage=storage, creator=occ_creator,
        creator_handle="occ-compose", slug="ops-incident-commander",
        name="Ops Incident Commander",
    )
    member_c, _ = await add_skill_with_body(
        db, storage=storage, creator=occ_creator,
        creator_handle="occ-compose", slug="alert-policy-architect",
        name="Alert Policy Architect",
    )

    occ_skill, _occ_row, occ_version = await make_occupation_skill(
        db, creator=occ_creator, slug="ai-devops-compose",
        name="AI DevOps (compose)",
        domains=["incident", "observability"],
    )
    await attach_occupation_member(
        db, occupation_skill=occ_skill, member_skill=member_a,
        domain="incident", sort_order=0,
    )
    await attach_occupation_member(
        db, occupation_skill=occ_skill, member_skill=member_b,
        domain="incident", sort_order=1,
    )
    await attach_occupation_member(
        db, occupation_skill=occ_skill, member_skill=member_c,
        domain="observability", sort_order=2,
    )

    # Build the occupation vault.
    occ_build = await builder.build_occupation(
        db, occ_skill.id, occ_version.version
    )
    assert occ_build.content_hash, "occupation build must produce a hash"

    # Persona creator + 2 neurons (each links to a base/<member> slug).
    persona_creator = await make_creator(
        db, email="jane@x.local", handle="jane-compose"
    )
    persona_skill, persona_row, persona_version = await make_persona_skill(
        db, creator=persona_creator, slug="jane-incident-compose",
        name="Jane Incident (compose)",
        parent_occupation_skill_id=occ_skill.id,
    )
    neuron_block = {
        "situation": "Pager fired at 3am.",
        "decision": "Followed the rollback runbook.",
        "outcome": "10-min impact; no escalation.",
        "recorded_at": "2024-10-15",
        "confidence": "high",
    }
    from src.skills.models import SkillKind

    neuron_1, _ = await add_skill_with_body(
        db, storage=storage, creator=persona_creator,
        creator_handle="jane-compose", slug="jane-neuron-rollback",
        name="Jane rollback at 3am",
        kind=SkillKind.MEMORY_NEURON,
        links=[{"target": "base/ops-runbook-generator", "relation": "applies"}],
        neuron_block=neuron_block,
        parent_occupation_id="occ-compose/ai-devops-compose",
    )
    neuron_2, _ = await add_skill_with_body(
        db, storage=storage, creator=persona_creator,
        creator_handle="jane-compose", slug="jane-neuron-pager-tune",
        name="Jane pager tune",
        kind=SkillKind.MEMORY_NEURON,
        links=[{"target": "base/alert-policy-architect", "relation": "applies"}],
        neuron_block=neuron_block,
        parent_occupation_id="occ-compose/ai-devops-compose",
    )
    await attach_persona_neuron(
        db, persona=persona_row, neuron_skill=neuron_1, sort_order=0,
    )
    await attach_persona_neuron(
        db, persona=persona_row, neuron_skill=neuron_2, sort_order=1,
    )

    persona_build = await builder.build_persona(
        db, persona_skill.id, persona_version.version
    )
    assert persona_build.content_hash, "persona build must produce a hash"

    # Buyer + free licenses.
    buyer = await make_buyer(db, email=buyer_email)
    occ_lic = await mint_occupation_license(
        db, buyer=buyer, occupation_skill=occ_skill
    )
    persona_lic = await mint_persona_license(
        db, buyer=buyer, persona_skill=persona_skill,
        target_occupation_skill_id=occ_skill.id,
    )

    return occ_skill, persona_skill, occ_lic, persona_lic, buyer


@pytest.mark.asyncio
async def test_compose_merges_occupation_and_persona(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Compose returns a presigned URL; the bundle contains files from
    both the occupation and the persona; the manifest reports zero
    real warnings (Polish 2: composer rewrites ``base/<slug>`` →
    ``domains/<domain>/<slug>``)."""
    _occ_skill, _persona_skill, occ_lic, _persona_lic, buyer = await _seed_full_stack(
        db_session, memory_storage
    )

    # Omit include_persona_license_ids — composer auto-includes every
    # active persona license the buyer holds for this occupation. That
    # path round-trips cleanly through the sqlite UUID-as-string variant
    # without needing the test to manually coerce.
    import uuid

    occ_lic_uuid = uuid.UUID(str(occ_lic.id))
    buyer_uuid = uuid.UUID(str(buyer.id))

    result = await composer.compose_for_license(
        db_session,
        buyer_id=buyer_uuid,
        occupation_license_id=occ_lic_uuid,
    )
    assert result.cache_hit is False
    assert result.composed_hash
    assert len(result.composed_hash) == 64
    assert result.presigned_url

    zip_bytes = await memory_storage.get_object(result.storage_url)
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        names = set(zf.namelist())
        # Occupation tree.
        assert "vault.json" in names
        assert "README.md" in names
        assert "00-index.md" in names
        domain_files = [n for n in names if n.startswith("domains/") and n.endswith(".md")]
        assert len(domain_files) == 3, (
            f"Expected 3 occupation member .md files; found {len(domain_files)}"
        )
        # Persona tree.
        neuron_paths = [
            n for n in names
            if n.startswith("personas/jane-compose/")
            and "/neurons/" in n
            and n.endswith(".md")
        ]
        assert len(neuron_paths) == 2, (
            f"Expected 2 persona neuron .md files; found {len(neuron_paths)}"
        )
        # Each persona file carries the watermark.
        for path in neuron_paths:
            body = zf.read(path).decode("utf-8")
            assert _WATERMARK_RE.search(body), (
                f"Persona file {path} missing watermark"
            )
        # Composed vault.json — zero "real" warnings. The composer's
        # Polish 2 base/* rewrite means every persona-side link should
        # resolve to a domains/<domain>/<slug> path; any remaining
        # warnings would surface a real broken link.
        import json
        vault_json = json.loads(zf.read("vault.json").decode("utf-8"))
        warnings = vault_json.get("warnings", [])
        assert warnings == [], (
            f"Composed manifest should have zero warnings after Polish 2 "
            f"base/* rewrite; got {len(warnings)}: {warnings[:3]}"
        )


@pytest.mark.asyncio
async def test_compose_two_buyers_watermark_differs_bodies_match(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Two compose runs for two buyers differ only in the per-buyer
    watermark; the rest of the .md bodies are byte-identical (modulo
    the watermark line)."""
    import uuid

    # Buyer 1.
    occ_skill, _persona_skill, occ_lic_1, _persona_lic_1, buyer_1 = await _seed_full_stack(
        db_session, memory_storage, buyer_email="alice@x.local",
    )
    result_1 = await composer.compose_for_license(
        db_session, buyer_id=uuid.UUID(str(buyer_1.id)),
        occupation_license_id=uuid.UUID(str(occ_lic_1.id)),
    )
    zip_1 = await memory_storage.get_object(result_1.storage_url)

    # Buyer 2 — second buyer purchases the same occupation + persona.
    buyer_2 = await make_buyer(db_session, email="bob@x.local")
    occ_lic_2 = await mint_occupation_license(
        db_session, buyer=buyer_2, occupation_skill=occ_skill,
    )
    _ = await mint_persona_license(
        db_session, buyer=buyer_2, persona_skill=_persona_skill,
        target_occupation_skill_id=occ_skill.id,
    )
    # Reset the cache between buyers so the second compose actually
    # runs the merge path (avoids a cache-hit short-circuit).
    cache_mod.reset_inmem_for_tests()

    result_2 = await composer.compose_for_license(
        db_session, buyer_id=uuid.UUID(str(buyer_2.id)),
        occupation_license_id=uuid.UUID(str(occ_lic_2.id)),
    )
    zip_2 = await memory_storage.get_object(result_2.storage_url)

    # Composed hashes differ because watermarks differ.
    assert result_1.composed_hash != result_2.composed_hash

    # Every .md body is byte-identical once the watermark line is
    # normalised away.
    with zipfile.ZipFile(io.BytesIO(zip_1), "r") as zf1, \
            zipfile.ZipFile(io.BytesIO(zip_2), "r") as zf2:
        names_1 = sorted(n for n in zf1.namelist() if n.endswith(".md"))
        names_2 = sorted(n for n in zf2.namelist() if n.endswith(".md"))
        assert names_1 == names_2
        # Pick one file from each tree and confirm the bodies match
        # modulo the watermark.
        for name in names_1:
            body_1 = zf1.read(name).decode("utf-8")
            body_2 = zf2.read(name).decode("utf-8")
            stripped_1 = _strip_watermarks(body_1)
            stripped_2 = _strip_watermarks(body_2)
            assert stripped_1 == stripped_2, (
                f"File {name} differs beyond the watermark — bodies should "
                f"be byte-identical otherwise"
            )
