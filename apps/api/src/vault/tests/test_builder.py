"""Unit tests for :mod:`src.vault.builder`.

Covers:

* :func:`build_occupation` happy path: 5 member skills, zip is well-formed,
  validate_vault passes, every member file carries the attribution comment.
* Idempotency: a second call with the same inputs returns the existing row.
* ``force_rebuild=True`` skips the cache.
* :func:`build_persona` happy path: 3 neurons, persona-only subtree.
* VaultBuildError surfaces with the right code on empty membership,
  unknown version, missing storage object, invalid member kind.
* The link resolver renders Linked notes correctly + emits warnings for
  dangling targets.
* The zip is deterministic — two back-to-back builds with the same content
  yield identical content_hash values.
"""

from __future__ import annotations

import io
import textwrap
import zipfile
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.occupations.models import Occupation, OccupationMemberRole, OccupationSkill
from src.personas.models import Persona, PersonaNeuron
from src.skills.models import (
    PricingModel,
    Skill,
    SkillKind,
    SkillStatus,
    SkillVersion,
)
from src.storage.s3 import InMemoryStorage
from src.users.models import CreatorProfile, User, UserRole
from src.vault import builder
from src.vault.manifest import VaultManifest
from src.vault.models import VaultBuild
from src.vault.validator import validate_vault

# ── Seed helpers ────────────────────────────────────────────────────


async def _make_creator(
    session: AsyncSession,
    *,
    email: str,
    handle: str,
) -> User:
    user = User(
        email=email,
        hashed_password="x" * 32,
        display_name=handle.title(),
        role=UserRole.CREATOR,
        is_active=True,
        is_verified=True,
        is_creator_verified=True,
    )
    session.add(user)
    await session.flush()
    session.add(CreatorProfile(user_id=user.id, handle=handle, payout_country="US"))
    await session.flush()
    return user


def _skill_md(
    *,
    creator_handle: str,
    slug: str,
    name: str,
    kind: str = "skill",
    links: list[dict[str, str]] | None = None,
    neuron_block: dict[str, str] | None = None,
    parent_occupation_id: str | None = None,
    tags: list[str] | None = None,
) -> bytes:
    """Build a minimal but valid skills.md body."""
    yaml_lines = [
        f"id: {creator_handle}/{slug}",
        "version: 1.0.0",
        f"name: {name}",
        f"description: A test skill describing {name}.",
        "category: engineering",
        f"tags: {tags or [slug.split('-', maxsplit=1)[0]]}",
        "license_type: free",
        "ai:",
        "  required_models:",
        "    - claude-sonnet-4-7",
        f"kind: {kind}",
    ]
    if parent_occupation_id is not None:
        yaml_lines.append(f"parent_occupation_id: {parent_occupation_id}")
    if links:
        yaml_lines.append("links:")
        for link in links:
            yaml_lines.append(f"  - target: {link['target']}")
            yaml_lines.append(f"    relation: {link.get('relation', 'see-also')}")
    if neuron_block is not None:
        yaml_lines.append("neuron:")
        for key, val in neuron_block.items():
            yaml_lines.append(f"  {key}: {val!r}")

    body = textwrap.dedent(
        f"""
        ## When to use

        Use this skill when {name} applies.

        ## How to apply

        1. Read the spec.
        2. Apply it.
        """
    ).strip()
    return ("---\n" + "\n".join(yaml_lines) + "\n---\n\n" + body + "\n").encode("utf-8")


async def _add_skill_with_body(
    session: AsyncSession,
    *,
    storage: InMemoryStorage,
    creator: User,
    creator_handle: str,
    slug: str,
    name: str,
    kind: SkillKind = SkillKind.SKILL,
    links: list[dict[str, str]] | None = None,
    neuron_block: dict[str, str] | None = None,
    parent_occupation_id: str | None = None,
) -> tuple[Skill, SkillVersion]:
    body_bytes = _skill_md(
        creator_handle=creator_handle,
        slug=slug,
        name=name,
        kind=kind.value,
        links=links,
        neuron_block=neuron_block,
        parent_occupation_id=parent_occupation_id,
    )
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=name,
        tagline=name,
        description_md=name,
        category="engineering",
        tags=[slug.split("-", maxsplit=1)[0]],
        status=SkillStatus.PUBLISHED,
        kind=kind,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    await storage.put_object(
        f"skills/{skill.id}/1.0.0.md", body_bytes, "text/markdown"
    )

    version = SkillVersion(
        skill_id=skill.id,
        version="1.0.0",
        content_hash="a" * 64,
        storage_url=f"skills/{skill.id}/1.0.0.md",
        ai_requirements={"required_models": ["claude-sonnet-4-7"]},
        changelog_md="initial",
        released_at=datetime.now(UTC),
        released_by=creator.id,
        is_yanked=False,
    )
    session.add(version)
    await session.flush()
    skill.latest_version_id = version.id
    skill.status = SkillStatus.PUBLISHED
    await session.flush()
    return skill, version


async def _make_occupation(
    session: AsyncSession,
    *,
    creator: User,
    slug: str,
    name: str,
    domains: list[str],
) -> tuple[Skill, Occupation, SkillVersion]:
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=name,
        tagline=name,
        description_md=name,
        category="occupations",
        tags=["devops"],
        status=SkillStatus.DRAFT,
        kind=SkillKind.OCCUPATION,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    occ = Occupation(
        skill_id=skill.id,
        summary_md=f"Summary for {name}",
        domains=domains,
        persona_count=0,
        recommended_persona_count=0,
    )
    session.add(occ)
    await session.flush()
    version = SkillVersion(
        skill_id=skill.id,
        version="1.0.0",
        content_hash="b" * 64,
        storage_url=f"occupations/{skill.id}/1.0.0.placeholder",
        ai_requirements=None,
        changelog_md="initial",
        released_at=datetime.now(UTC),
        released_by=creator.id,
        is_yanked=False,
    )
    session.add(version)
    await session.flush()
    return skill, occ, version


async def _make_persona(
    session: AsyncSession,
    *,
    creator: User,
    slug: str,
    name: str,
    parent_occupation_skill: Skill,
) -> tuple[Skill, Persona, SkillVersion]:
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=name,
        tagline=name,
        description_md=name,
        category="personas",
        tags=["devops"],
        status=SkillStatus.DRAFT,
        kind=SkillKind.PERSONA,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    persona = Persona(
        skill_id=skill.id,
        parent_occupation_id=parent_occupation_skill.id,
        creator_intro_md=f"Hi I'm {creator.display_name}.",
        years_of_experience=10,
        specialization="DevOps on-call",
        neuron_count=0,
    )
    session.add(persona)
    await session.flush()
    version = SkillVersion(
        skill_id=skill.id,
        version="1.0.0",
        content_hash="c" * 64,
        storage_url=f"personas/{skill.id}/1.0.0.placeholder",
        ai_requirements=None,
        changelog_md="initial",
        released_at=datetime.now(UTC),
        released_by=creator.id,
        is_yanked=False,
    )
    session.add(version)
    await session.flush()
    return skill, persona, version


async def _add_member(
    session: AsyncSession,
    *,
    occupation: Skill,
    member: Skill,
    domain: str,
    role: OccupationMemberRole = OccupationMemberRole.CORE,
    sort_order: int = 0,
) -> OccupationSkill:
    row = OccupationSkill(
        occupation_id=occupation.id,
        member_skill_id=member.id,
        domain=domain,
        role=role,
        sort_order=sort_order,
        pinned=False,
        notes_md=None,
    )
    session.add(row)
    await session.flush()
    return row


async def _add_neuron(
    session: AsyncSession,
    *,
    persona: Skill,
    neuron: Skill,
    section: str | None = None,
    sort_order: int = 0,
) -> PersonaNeuron:
    row = PersonaNeuron(
        persona_id=persona.id,
        neuron_skill_id=neuron.id,
        sort_order=sort_order,
        section=section,
    )
    session.add(row)
    await session.flush()
    return row


# ── Occupation builder tests ────────────────────────────────────────


@pytest.mark.asyncio
async def test_build_occupation_happy_path_5_members(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Spec: T-06 acceptance bullet 1 — 5 members + validate_vault passes."""
    creator = await _make_creator(
        db_session, email="curator@example.com", handle="skillsgit-curated"
    )
    occ_skill, _occ, _version = await _make_occupation(
        db_session, creator=creator,
        slug="ai-devops-engineer",
        name="AI DevOps Engineer",
        domains=["ci-cd", "observability", "incident-response"],
    )
    member_skills: list[Skill] = []
    for i, slug in enumerate(
        [
            "devops-ci-pipeline-architect",
            "devops-gha-workflow-optimizer",
            "observability-dashboard-architect",
            "alert-policy-architect",
            "ops-incident-commander",
        ]
    ):
        skill, _v = await _add_skill_with_body(
            db_session,
            storage=memory_storage,
            creator=creator,
            creator_handle="skillsgit-curated",
            slug=slug,
            name=slug.replace("-", " ").title(),
            links=(
                [{"target": "ops-incident-commander", "relation": "applies"}]
                if i == 0
                else []
            ),
        )
        member_skills.append(skill)

    # Three domains: 2 ci-cd, 2 observability, 1 incident-response.
    domains = ["ci-cd", "ci-cd", "observability", "observability", "incident-response"]
    for i, member in enumerate(member_skills):
        await _add_member(
            db_session, occupation=occ_skill, member=member,
            domain=domains[i], sort_order=i,
        )

    build = await builder.build_occupation(
        db_session, occ_skill.id, "1.0.0"
    )
    assert build is not None
    assert build.status.value == "succeeded"
    assert build.file_count >= 8  # 5 members + README + index + manifest
    assert build.content_hash
    assert len(build.content_hash) == 64

    # Fetch the uploaded zip and verify.
    zip_bytes = await memory_storage.get_object(build.storage_url)
    result = validate_vault(zip_bytes)
    assert result.is_valid, [(e.field, e.code, e.message) for e in result.errors]

    # Spot-check zip layout.
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        names = set(zf.namelist())
        assert "README.md" in names
        assert "00-index.md" in names
        assert "vault.json" in names
        assert "domains/ci-cd/devops-ci-pipeline-architect.md" in names

        # Every member .md carries the attribution comment.
        for member in member_skills:
            paths = [n for n in names if n.endswith(f"{member.slug}.md")]
            assert paths
            content = zf.read(paths[0]).decode("utf-8")
            assert "skg-attribution" in content
            assert "skillsgit-curated" in content


@pytest.mark.asyncio
async def test_build_occupation_writes_vault_builds_row(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    creator = await _make_creator(
        db_session, email="curator@example.com", handle="skillsgit-curated"
    )
    occ_skill, _occ, _version = await _make_occupation(
        db_session, creator=creator,
        slug="oc", name="OC", domains=["x"],
    )
    member, _v = await _add_skill_with_body(
        db_session, storage=memory_storage, creator=creator,
        creator_handle="skillsgit-curated", slug="one", name="One",
    )
    await _add_member(db_session, occupation=occ_skill, member=member, domain="x")

    build = await builder.build_occupation(db_session, occ_skill.id, "1.0.0")

    # The row is in the session, query by id.
    from sqlalchemy import select
    res = await db_session.execute(
        select(VaultBuild).where(VaultBuild.id == build.id)
    )
    row = res.scalar_one()
    assert row.skill_id == occ_skill.id
    assert row.status.value == "succeeded"
    assert row.storage_url.startswith(f"vaults/{occ_skill.id}/1.0.0/")
    assert row.storage_url.endswith(".zip")
    assert isinstance(row.manifest_json, dict)
    assert row.manifest_json["schema_version"] == 1
    assert row.manifest_json["occupation"]["slug"] == "oc"


@pytest.mark.asyncio
async def test_build_occupation_is_idempotent(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    creator = await _make_creator(
        db_session, email="curator@example.com", handle="skillsgit-curated"
    )
    occ_skill, _occ, _version = await _make_occupation(
        db_session, creator=creator,
        slug="oc", name="OC", domains=["x"],
    )
    member, _v = await _add_skill_with_body(
        db_session, storage=memory_storage, creator=creator,
        creator_handle="skillsgit-curated", slug="one", name="One",
    )
    await _add_member(db_session, occupation=occ_skill, member=member, domain="x")

    first = await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    second = await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    # Same row returned — same id, same content_hash.
    # sqlite stores UUID as String(36), so the in-session row's id may
    # come back as UUID while the queried-fresh row comes back as str.
    # Coerce both sides for a dialect-agnostic check.
    assert str(first.id) == str(second.id)
    assert first.content_hash == second.content_hash


@pytest.mark.asyncio
async def test_build_occupation_empty_membership_raises(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    creator = await _make_creator(
        db_session, email="c@example.com", handle="cur"
    )
    occ_skill, _occ, _v = await _make_occupation(
        db_session, creator=creator, slug="empty", name="Empty",
        domains=["x"],
    )
    with pytest.raises(builder.VaultBuildError) as exc:
        await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    assert exc.value.code == "vault_build.empty_membership"


@pytest.mark.asyncio
async def test_build_occupation_unknown_version_raises(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    creator = await _make_creator(
        db_session, email="c@example.com", handle="cur"
    )
    occ_skill, _occ, _v = await _make_occupation(
        db_session, creator=creator, slug="oc", name="OC", domains=["x"],
    )
    member, _vm = await _add_skill_with_body(
        db_session, storage=memory_storage, creator=creator,
        creator_handle="cur", slug="m", name="M",
    )
    await _add_member(db_session, occupation=occ_skill, member=member, domain="x")
    with pytest.raises(builder.VaultBuildError) as exc:
        await builder.build_occupation(db_session, occ_skill.id, "2.0.0")
    assert exc.value.code == "vault_build.version_not_found"


@pytest.mark.asyncio
async def test_build_occupation_rejects_non_skill_member(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Defence in depth: the service rejects this at the API boundary but the
    builder should not silently bundle a wrong-kind member if a DB-level
    inconsistency creeps in."""
    creator = await _make_creator(
        db_session, email="c@example.com", handle="cur"
    )
    occ_skill, _occ, _v = await _make_occupation(
        db_session, creator=creator, slug="oc", name="OC", domains=["x"],
    )
    # Manually craft a kind=occupation row and shove it in as a "member"
    # (bypasses the service's invalid_member_kind check on purpose).
    bad_member = Skill(
        creator_id=creator.id,
        slug="another-occ",
        name="Another Occ",
        tagline="t",
        description_md="d",
        category="x",
        tags=["x"],
        status=SkillStatus.PUBLISHED,
        kind=SkillKind.OCCUPATION,
        pricing_model=PricingModel.FREE,
    )
    db_session.add(bad_member)
    await db_session.flush()
    bad_version = SkillVersion(
        skill_id=bad_member.id, version="1.0.0", content_hash="d" * 64,
        storage_url="skills/another-occ/1.0.0.md",
        ai_requirements=None, changelog_md="x",
        released_at=datetime.now(UTC), released_by=creator.id,
        is_yanked=False,
    )
    db_session.add(bad_version)
    await db_session.flush()
    bad_member.latest_version_id = bad_version.id
    await db_session.flush()
    await _add_member(db_session, occupation=occ_skill, member=bad_member, domain="x")

    with pytest.raises(builder.VaultBuildError) as exc:
        await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    assert exc.value.code == "vault_build.invalid_member_kind"


@pytest.mark.asyncio
async def test_build_occupation_manifest_attribution_index(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """attribution_index should map skill_id → vault_path for every member."""
    creator = await _make_creator(
        db_session, email="curator@example.com", handle="skillsgit-curated"
    )
    occ_skill, _occ, _v = await _make_occupation(
        db_session, creator=creator, slug="oc", name="OC",
        domains=["ci-cd", "observability"],
    )
    members: list[Skill] = []
    for slug, domain in [
        ("alpha", "ci-cd"),
        ("beta", "observability"),
        ("gamma", "ci-cd"),
    ]:
        m, _v = await _add_skill_with_body(
            db_session, storage=memory_storage, creator=creator,
            creator_handle="skillsgit-curated", slug=slug, name=slug.title(),
        )
        members.append(m)
        await _add_member(
            db_session, occupation=occ_skill, member=m, domain=domain,
        )

    build = await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    assert build.manifest_json is not None
    manifest = VaultManifest.model_validate(
        {k: v for k, v in build.manifest_json.items() if k != "$schema"}
    )
    assert len(manifest.files) == 3
    assert set(manifest.attribution_index.keys()) == {str(m.id) for m in members}
    # Every value points at a file in files[].
    file_paths = {f.vault_path for f in manifest.files}
    for path in manifest.attribution_index.values():
        assert path in file_paths


# ── Persona builder tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_build_persona_happy_path_3_neurons(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Spec: T-06 acceptance bullet 4 — persona with 3 neurons."""
    curator = await _make_creator(
        db_session, email="curator@example.com", handle="skillsgit-curated"
    )
    practitioner = await _make_creator(
        db_session, email="jane@example.com", handle="jane-devops"
    )

    parent_skill, _occ, _v = await _make_occupation(
        db_session, creator=curator,
        slug="ai-devops-engineer", name="AI DevOps Engineer",
        domains=["ci-cd"],
    )
    persona_skill, _p, _pv = await _make_persona(
        db_session, creator=practitioner,
        slug="jane-on-call", name="Jane's On-Call Brain",
        parent_occupation_skill=parent_skill,
    )

    neurons = []
    for slug, sit in [
        ("2024-08-flaky-tests", "Flaky tests in CI"),
        ("2024-10-blue-green-rollback", "Blue/green rollback at 3am"),
        ("2025-01-secret-rotation", "Secret rotation under load"),
    ]:
        skill, _v = await _add_skill_with_body(
            db_session, storage=memory_storage, creator=practitioner,
            creator_handle="jane-devops", slug=slug, name=slug,
            kind=SkillKind.MEMORY_NEURON,
            parent_occupation_id=str(parent_skill.id),
            neuron_block={
                "situation": sit,
                "decision": "Picked a sane default.",
                "outcome": "Worked out fine.",
            },
        )
        neurons.append(skill)
        await _add_neuron(
            db_session, persona=persona_skill, neuron=skill,
            sort_order=len(neurons),
        )

    build = await builder.build_persona(db_session, persona_skill.id, "1.0.0")
    assert build is not None
    assert build.status.value == "succeeded"

    zip_bytes = await memory_storage.get_object(build.storage_url)
    result = validate_vault(zip_bytes)
    assert result.is_valid, [(e.field, e.code, e.message) for e in result.errors]

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        names = set(zf.namelist())
        # Only the persona subtree — NO base/ folder, NO vault.json.
        assert any(n.startswith("personas/jane-devops/jane-on-call/") for n in names)
        assert "personas/jane-devops/jane-on-call/persona.json" in names
        assert "personas/jane-devops/jane-on-call/README.md" in names
        assert "vault.json" not in names
        assert not any(n.startswith("domains/") for n in names)
        # Every neuron file has the attribution comment.
        for n in neurons:
            paths = [p for p in names if p.endswith(f"{n.slug}.md")]
            assert paths
            content = zf.read(paths[0]).decode("utf-8")
            assert "skg-attribution" in content


@pytest.mark.asyncio
async def test_build_persona_no_neurons_raises(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    curator = await _make_creator(
        db_session, email="curator@example.com", handle="cur"
    )
    practitioner = await _make_creator(
        db_session, email="p@example.com", handle="prac-tit"
    )
    parent, _o, _v = await _make_occupation(
        db_session, creator=curator, slug="oc", name="OC",
        domains=["x"],
    )
    persona, _p, _pv = await _make_persona(
        db_session, creator=practitioner,
        slug="p", name="P", parent_occupation_skill=parent,
    )
    with pytest.raises(builder.VaultBuildError) as exc:
        await builder.build_persona(db_session, persona.id, "1.0.0")
    assert exc.value.code == "vault_build.no_neurons"


# ── Deterministic zip ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_zip_is_deterministic_across_two_builds(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Same inputs → identical zip bytes (per 03-vault-generation.md §12)."""
    creator = await _make_creator(
        db_session, email="c@example.com", handle="cur"
    )
    occ_skill, _occ, _v = await _make_occupation(
        db_session, creator=creator, slug="oc", name="OC",
        domains=["x"],
    )
    member, _vm = await _add_skill_with_body(
        db_session, storage=memory_storage, creator=creator,
        creator_handle="cur", slug="alpha", name="Alpha",
    )
    await _add_member(db_session, occupation=occ_skill, member=member, domain="x")

    first = await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    # Capture the bytes
    first_bytes = await memory_storage.get_object(first.storage_url)

    # Force a rebuild (force_rebuild=True bypasses the (skill, hash) cache).
    second = await builder.build_occupation(
        db_session, occ_skill.id, "1.0.0", force_rebuild=True
    )
    second_bytes = await memory_storage.get_object(second.storage_url)

    # Both content_hash values should match (same inputs).
    assert first.content_hash == second.content_hash
    assert first_bytes == second_bytes


# ── Linked notes section / link resolution ─────────────────────────


@pytest.mark.asyncio
async def test_linked_notes_renders_resolved_links(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """A link pointing at a sibling member resolves to a full vault path."""
    creator = await _make_creator(
        db_session, email="c@example.com", handle="cur"
    )
    occ_skill, _occ, _v = await _make_occupation(
        db_session, creator=creator, slug="oc", name="OC",
        domains=["x", "y"],
    )
    source, _vs = await _add_skill_with_body(
        db_session, storage=memory_storage, creator=creator,
        creator_handle="cur", slug="alpha", name="Alpha",
        links=[{"target": "beta", "relation": "applies"}],
    )
    target, _vt = await _add_skill_with_body(
        db_session, storage=memory_storage, creator=creator,
        creator_handle="cur", slug="beta", name="Beta",
    )
    await _add_member(db_session, occupation=occ_skill, member=source, domain="x", sort_order=0)
    await _add_member(db_session, occupation=occ_skill, member=target, domain="y", sort_order=1)

    build = await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    zip_bytes = await memory_storage.get_object(build.storage_url)

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        body = zf.read("domains/x/alpha.md").decode("utf-8")
    assert "## Linked notes" in body
    assert "[[domains/y/beta]]" in body
    assert "applies" in body

    # And the manifest entry records the link as resolved.
    assert build.manifest_json is not None
    manifest = VaultManifest.model_validate(
        {k: v for k, v in build.manifest_json.items() if k != "$schema"}
    )
    alpha_entry = next(f for f in manifest.files if f.vault_path == "domains/x/alpha.md")
    assert alpha_entry.links_resolved
    assert any(
        link.target == "domains/y/beta" and link.resolved
        for link in alpha_entry.links
    )


@pytest.mark.asyncio
async def test_unresolved_link_emits_warning_but_does_not_fail(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Dangling links surface as manifest warnings, not build failures."""
    creator = await _make_creator(
        db_session, email="c@example.com", handle="cur"
    )
    occ_skill, _occ, _v = await _make_occupation(
        db_session, creator=creator, slug="oc", name="OC",
        domains=["x"],
    )
    member, _vm = await _add_skill_with_body(
        db_session, storage=memory_storage, creator=creator,
        creator_handle="cur", slug="alpha", name="Alpha",
        links=[{"target": "this-does-not-exist", "relation": "see-also"}],
    )
    await _add_member(db_session, occupation=occ_skill, member=member, domain="x")

    build = await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    assert build.manifest_json is not None
    manifest = VaultManifest.model_validate(
        {k: v for k, v in build.manifest_json.items() if k != "$schema"}
    )
    assert any(
        w.unresolved_link == "this-does-not-exist" for w in manifest.warnings
    )
    alpha_entry = next(f for f in manifest.files if f.vault_path == "domains/x/alpha.md")
    assert not alpha_entry.links_resolved


# ── Storage-missing path ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_missing_storage_object_raises_member_missing(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """If the source skill's body bytes are gone, build fails loudly."""
    creator = await _make_creator(
        db_session, email="c@example.com", handle="cur"
    )
    occ_skill, _occ, _v = await _make_occupation(
        db_session, creator=creator, slug="oc", name="OC",
        domains=["x"],
    )
    # Create the row but DON'T upload to storage.
    skill = Skill(
        creator_id=creator.id,
        slug="ghost",
        name="Ghost",
        tagline="ghost",
        description_md="ghost",
        category="x",
        tags=["x"],
        status=SkillStatus.PUBLISHED,
        kind=SkillKind.SKILL,
        pricing_model=PricingModel.FREE,
    )
    db_session.add(skill)
    await db_session.flush()
    version = SkillVersion(
        skill_id=skill.id, version="1.0.0",
        content_hash="e" * 64,
        storage_url=f"skills/{skill.id}/1.0.0.md",
        ai_requirements=None, changelog_md="x",
        released_at=datetime.now(UTC), released_by=creator.id,
        is_yanked=False,
    )
    db_session.add(version)
    await db_session.flush()
    skill.latest_version_id = version.id
    await db_session.flush()
    await _add_member(db_session, occupation=occ_skill, member=skill, domain="x")

    with pytest.raises(builder.VaultBuildError) as exc:
        await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    assert exc.value.code == "vault_build.member_missing"
