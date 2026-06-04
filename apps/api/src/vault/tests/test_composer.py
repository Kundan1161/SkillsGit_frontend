"""Unit tests for :mod:`src.vault.composer` (T-07).

Covers (minimum 8 per the wave-3B brief):

1. Cache miss + cache hit.
2. Occupation-only compose (no personas in the buyer's library).
3. Occupation + 1 persona compose.
4. Occupation + 2 personas compose.
5. Two downloads by the same buyer differ ONLY in the watermark
   comment lines (bytewise stable elsewhere).
6. Link-warning surface — a persona linking to ``base/<unknown>`` lands
   the warning on the composed manifest.
7. 403 / 404 when the buyer doesn't own the occupation license.
8. 403 ``vault.persona_license_not_held`` when a requested persona
   license isn't held by the buyer.
9. Cache invalidation on a new vault_build (a fresh build_id changes
   the cache key so cache_hit goes back to False).

The conftest's autouse ``_inline_builds_in_vault_tests`` fixture is
sufficient: composer doesn't need the Arq façade flip because it never
enqueues builds; it reads existing :class:`VaultBuild` rows seeded by
the builder.
"""

from __future__ import annotations

import hashlib
import io
import re
import uuid
import zipfile
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.models import (
    License,
    LicenseCompositionRole,
    LicenseSource,
    LicenseStatus,
    SupportTier,
)
from src.core import cache as cache_mod
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
from src.vault import builder, composer
from src.vault.models import VaultDownload

# ── Seed helpers (mirrors test_builder.py — kept local for isolation) ─


@pytest.fixture(autouse=True)
def _clear_cache_between_tests() -> Any:
    """Composer cache is process-local in tests — reset between cases."""
    cache_mod.reset_inmem_for_tests()
    yield
    cache_mod.reset_inmem_for_tests()


async def _make_user(
    session: AsyncSession,
    *,
    email: str,
    handle: str | None = None,
    role: UserRole = UserRole.BUYER,
) -> User:
    user = User(
        email=email,
        hashed_password="x" * 32,
        display_name=(handle or email.split("@", maxsplit=1)[0]).title(),
        role=role,
        is_active=True,
        is_verified=True,
        is_creator_verified=role == UserRole.CREATOR,
    )
    session.add(user)
    await session.flush()
    if handle is not None:
        session.add(
            CreatorProfile(user_id=user.id, handle=handle, payout_country="US")
        )
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
) -> bytes:
    yaml_lines = [
        f"id: {creator_handle}/{slug}",
        "version: 1.0.0",
        f"name: {name}",
        f"description: Skill {name}.",
        "category: engineering",
        f"tags: ['{slug.split('-', maxsplit=1)[0]}']",
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
    body = (
        "## When to use\n\n"
        f"Use when {name}.\n\n"
        "## How to apply\n\n"
        "1. Read.\n2. Apply.\n"
    )
    return ("---\n" + "\n".join(yaml_lines) + "\n---\n\n" + body).encode("utf-8")


async def _add_member_skill(
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
    body = _skill_md(
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
        f"skills/{skill.id}/1.0.0.md", body, "text/markdown"
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
    await session.flush()
    return skill, version


async def _make_occupation(
    session: AsyncSession, *, creator: User, slug: str, name: str,
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
        status=SkillStatus.PUBLISHED,
        kind=SkillKind.OCCUPATION,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    occ = Occupation(
        skill_id=skill.id, summary_md=name, domains=domains,
        persona_count=0, recommended_persona_count=0,
    )
    session.add(occ)
    await session.flush()
    version = SkillVersion(
        skill_id=skill.id, version="1.0.0", content_hash="b" * 64,
        storage_url=f"occupations/{skill.id}/1.0.0.placeholder",
        ai_requirements=None, changelog_md="initial",
        released_at=datetime.now(UTC), released_by=creator.id,
        is_yanked=False,
    )
    session.add(version)
    await session.flush()
    skill.latest_version_id = version.id
    await session.flush()
    return skill, occ, version


async def _make_persona(
    session: AsyncSession, *, creator: User, slug: str, name: str,
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
        status=SkillStatus.PUBLISHED,
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
        skill_id=skill.id, version="1.0.0", content_hash="c" * 64,
        storage_url=f"personas/{skill.id}/1.0.0.placeholder",
        ai_requirements=None, changelog_md="initial",
        released_at=datetime.now(UTC), released_by=creator.id,
        is_yanked=False,
    )
    session.add(version)
    await session.flush()
    skill.latest_version_id = version.id
    await session.flush()
    return skill, persona, version


async def _add_member(
    session: AsyncSession, *, occupation: Skill, member: Skill, domain: str,
    sort_order: int = 0,
) -> OccupationSkill:
    row = OccupationSkill(
        occupation_id=occupation.id,
        member_skill_id=member.id,
        domain=domain,
        role=OccupationMemberRole.CORE,
        sort_order=sort_order,
        pinned=False,
        notes_md=None,
    )
    session.add(row)
    await session.flush()
    return row


async def _add_neuron(
    session: AsyncSession, *, persona: Skill, neuron: Skill,
    sort_order: int = 0,
) -> PersonaNeuron:
    row = PersonaNeuron(
        persona_id=persona.id,
        neuron_skill_id=neuron.id,
        sort_order=sort_order,
        section=None,
    )
    session.add(row)
    await session.flush()
    return row


async def _create_license(
    session: AsyncSession,
    *,
    buyer: User,
    skill: Skill,
    role: LicenseCompositionRole,
    target_occupation_skill_id: uuid.UUID | None = None,
) -> License:
    lic = License(
        buyer_id=buyer.id,
        skill_id=skill.id,
        source=LicenseSource.FREE,
        source_id=uuid.uuid4(),
        granted_at=datetime.now(UTC) - timedelta(minutes=5),
        max_version=None,
        support_tier=SupportTier.NONE,
        status=LicenseStatus.ACTIVE,
        composition_role=role,
        target_occupation_skill_id=target_occupation_skill_id,
    )
    session.add(lic)
    await session.flush()
    return lic


# ── Seed scenarios — common test setup ───────────────────────────────


async def _seed_occupation_with_n_members(
    session: AsyncSession,
    *,
    storage: InMemoryStorage,
    n_members: int = 2,
    occupation_slug: str = "ai-devops-engineer",
) -> tuple[User, Skill, list[Skill]]:
    """Returns (curator, occupation_skill, member_skills)."""
    curator = await _make_user(
        session, email="curator@example.com", handle="skillsgit-curated",
        role=UserRole.CREATOR,
    )
    occ_skill, _occ, _v = await _make_occupation(
        session, creator=curator,
        slug=occupation_slug, name="AI DevOps Engineer",
        domains=["ci-cd", "observability"],
    )
    member_skills: list[Skill] = []
    for i in range(n_members):
        slug = f"skill-{chr(ord('a') + i)}"
        skill, _v = await _add_member_skill(
            session, storage=storage, creator=curator,
            creator_handle="skillsgit-curated", slug=slug, name=slug.upper(),
            links=None,
        )
        member_skills.append(skill)
        await _add_member(
            session, occupation=occ_skill, member=skill,
            domain=("ci-cd" if i % 2 == 0 else "observability"),
            sort_order=i,
        )
    return curator, occ_skill, member_skills


async def _seed_persona(
    session: AsyncSession,
    *,
    storage: InMemoryStorage,
    parent_skill: Skill,
    handle: str,
    slug: str,
    n_neurons: int = 2,
    neuron_links_to_base: list[str] | None = None,
) -> tuple[User, Skill, list[Skill]]:
    """Returns (practitioner, persona_skill, neuron_skills)."""
    practitioner = await _make_user(
        session, email=f"{handle}@example.com", handle=handle,
        role=UserRole.CREATOR,
    )
    persona_skill, _p, _pv = await _make_persona(
        session, creator=practitioner, slug=slug, name=slug.title(),
        parent_occupation_skill=parent_skill,
    )
    neurons: list[Skill] = []
    for i in range(n_neurons):
        neuron_slug = f"{handle}-incident-{i + 1}"
        skill, _v = await _add_member_skill(
            session, storage=storage, creator=practitioner,
            creator_handle=handle, slug=neuron_slug,
            name=f"Incident {i + 1}",
            kind=SkillKind.MEMORY_NEURON,
            parent_occupation_id=str(parent_skill.id),
            neuron_block={
                "situation": "Things broke.",
                "decision": "Did the thing.",
                "outcome": "Worked.",
            },
            links=(
                [{"target": t, "relation": "applies"} for t in (neuron_links_to_base or [])]
                if i == 0 and neuron_links_to_base
                else None
            ),
        )
        neurons.append(skill)
        await _add_neuron(
            session, persona=persona_skill, neuron=skill, sort_order=i + 1,
        )
    return practitioner, persona_skill, neurons


# ── 1 + 3: occupation-only happy path + cache miss/hit ───────────────


@pytest.mark.asyncio
async def test_compose_occupation_only_cache_miss(
    db_session: AsyncSession, memory_storage: InMemoryStorage,
) -> None:
    """First call is a cache miss; result downloads + parses correctly."""
    _curator, occ_skill, _members = await _seed_occupation_with_n_members(
        db_session, storage=memory_storage, n_members=2,
    )
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    buyer = await _make_user(
        db_session, email="buyer@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )

    result = await composer.compose_for_license(
        db_session, buyer_id=buyer.id,
        occupation_license_id=occ_lic.id,
    )
    assert result.cache_hit is False
    assert result.composed_hash
    assert len(result.composed_hash) == 64
    assert result.presigned_url.startswith("memory://")
    assert result.expires_at > datetime.now(UTC)
    assert result.persona_build_ids == []

    # Download the bundle and confirm vault.json + readme are present.
    zip_bytes = await memory_storage.get_object(result.storage_url)
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        names = set(zf.namelist())
        assert "vault.json" in names
        assert "README.md" in names
        assert "00-index.md" in names
        # member files are under domains/
        assert any(n.startswith("domains/") for n in names)


@pytest.mark.asyncio
async def test_compose_cache_hit_returns_same_storage_url(
    db_session: AsyncSession, memory_storage: InMemoryStorage,
) -> None:
    """Second call within TTL hits the cache and skips re-zipping."""
    _curator, occ_skill, _members = await _seed_occupation_with_n_members(
        db_session, storage=memory_storage, n_members=2,
    )
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    buyer = await _make_user(
        db_session, email="buyer@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )

    first = await composer.compose_for_license(
        db_session, buyer_id=buyer.id, occupation_license_id=occ_lic.id,
    )
    second = await composer.compose_for_license(
        db_session, buyer_id=buyer.id, occupation_license_id=occ_lic.id,
    )

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert first.storage_url == second.storage_url
    assert first.composed_hash == second.composed_hash
    # vault_downloads row is recorded only on the miss, so the cached
    # download_id is returned verbatim from the cache payload.
    assert first.vault_download_id == second.vault_download_id


# ── 4: occupation + 1 persona ────────────────────────────────────────


@pytest.mark.asyncio
async def test_compose_with_one_persona(
    db_session: AsyncSession, memory_storage: InMemoryStorage,
) -> None:
    """Composition merges a persona's neurons into the vault."""
    _curator, occ_skill, _members = await _seed_occupation_with_n_members(
        db_session, storage=memory_storage, n_members=2,
    )
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    _prac, persona_skill, _neurons = await _seed_persona(
        db_session, storage=memory_storage,
        parent_skill=occ_skill, handle="jane-devops", slug="jane-on-call",
        n_neurons=2,
    )
    await builder.build_persona(db_session, persona_skill.id, "1.0.0")

    buyer = await _make_user(
        db_session, email="buyer@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )
    p_lic = await _create_license(
        db_session, buyer=buyer, skill=persona_skill,
        role=LicenseCompositionRole.PERSONA,
        target_occupation_skill_id=occ_skill.id,
    )

    result = await composer.compose_for_license(
        db_session, buyer_id=buyer.id, occupation_license_id=occ_lic.id,
    )
    assert result.cache_hit is False
    assert len(result.persona_build_ids) == 1

    zip_bytes = await memory_storage.get_object(result.storage_url)
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        names = set(zf.namelist())
        # The persona subtree is merged on top of the occupation tree.
        assert any(n.startswith("personas/jane-devops/jane-on-call/") for n in names)
        # And vault.json lists files from BOTH.
        import json as _json
        vault_json = _json.loads(zf.read("vault.json").decode("utf-8"))
        paths = {f["vault_path"] for f in vault_json["files"]}
        assert any(p.startswith("domains/") for p in paths)
        assert any(p.startswith("personas/jane-devops/") for p in paths)

    # vault_downloads row recorded the persona license id too.
    download = await db_session.get(VaultDownload, result.vault_download_id)
    assert download is not None
    # sqlite stores ARRAY-of-UUID as JSON; coerce both sides.
    assert download.persona_license_ids is not None
    assert str(p_lic.id) in [str(x) for x in download.persona_license_ids]


# ── 5: occupation + 2 personas ───────────────────────────────────────


@pytest.mark.asyncio
async def test_compose_with_two_personas(
    db_session: AsyncSession, memory_storage: InMemoryStorage,
) -> None:
    """Composing two personas merges both subtrees + both manifests."""
    _curator, occ_skill, _members = await _seed_occupation_with_n_members(
        db_session, storage=memory_storage, n_members=2,
    )
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")

    _p1, persona_a, _n1 = await _seed_persona(
        db_session, storage=memory_storage,
        parent_skill=occ_skill, handle="practa", slug="persona-a",
        n_neurons=2,
    )
    await builder.build_persona(db_session, persona_a.id, "1.0.0")

    _p2, persona_b, _n2 = await _seed_persona(
        db_session, storage=memory_storage,
        parent_skill=occ_skill, handle="practb", slug="persona-b",
        n_neurons=1,
    )
    await builder.build_persona(db_session, persona_b.id, "1.0.0")

    buyer = await _make_user(
        db_session, email="b@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )
    await _create_license(
        db_session, buyer=buyer, skill=persona_a,
        role=LicenseCompositionRole.PERSONA,
        target_occupation_skill_id=occ_skill.id,
    )
    await _create_license(
        db_session, buyer=buyer, skill=persona_b,
        role=LicenseCompositionRole.PERSONA,
        target_occupation_skill_id=occ_skill.id,
    )

    result = await composer.compose_for_license(
        db_session, buyer_id=buyer.id, occupation_license_id=occ_lic.id,
    )
    assert len(result.persona_build_ids) == 2

    zip_bytes = await memory_storage.get_object(result.storage_url)
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        names = set(zf.namelist())
        assert any(n.startswith("personas/practa/persona-a/") for n in names)
        assert any(n.startswith("personas/practb/persona-b/") for n in names)
        import json as _json
        vault_json = _json.loads(zf.read("vault.json").decode("utf-8"))
        # The manifest's personas[] carries both summaries.
        assert len(vault_json["personas"]) == 2


# ── 6: watermark bytewise stability ──────────────────────────────────


@pytest.mark.asyncio
async def test_two_downloads_differ_only_in_watermark(
    db_session: AsyncSession, memory_storage: InMemoryStorage,
) -> None:
    """Two downloads by the same buyer must differ only in the watermark.

    Approach: bypass the cache by deleting the cache entry between
    calls (otherwise the second hit returns the same storage_url and
    the test would be trivially true). We compare the post-zip bytes
    by md-file diff — every difference must be inside the watermark
    comment line, with the rest of the body identical.
    """
    _curator, occ_skill, _members = await _seed_occupation_with_n_members(
        db_session, storage=memory_storage, n_members=2,
    )
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    buyer = await _make_user(
        db_session, email="b@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )

    first = await composer.compose_for_license(
        db_session, buyer_id=buyer.id, occupation_license_id=occ_lic.id,
    )
    first_zip = await memory_storage.get_object(first.storage_url)

    # Wipe the cache so the next call goes through the compose path
    # (otherwise we'd just get the same bundle back).
    cache_mod.reset_inmem_for_tests()

    second = await composer.compose_for_license(
        db_session, buyer_id=buyer.id, occupation_license_id=occ_lic.id,
    )
    second_zip = await memory_storage.get_object(second.storage_url)

    # The composed bytes differ overall (watermark + composed_at).
    assert first_zip != second_zip

    # But: every .md file should differ ONLY inside the watermark
    # comment line emitted by ``delivery.watermark.append_watermark``.
    watermark_re = re.compile(
        r"<!--\s*license:[0-9a-f]+\s+buyer:[0-9a-f]+\s+ts:[^>]+-->",
        re.MULTILINE,
    )
    with zipfile.ZipFile(io.BytesIO(first_zip), "r") as a, zipfile.ZipFile(
        io.BytesIO(second_zip), "r"
    ) as b:
        names = sorted(n for n in a.namelist() if n.endswith(".md"))
        assert names  # sanity — there is at least one .md
        for n in names:
            body_a = a.read(n).decode("utf-8")
            body_b = b.read(n).decode("utf-8")
            stripped_a = watermark_re.sub("", body_a).rstrip()
            stripped_b = watermark_re.sub("", body_b).rstrip()
            assert stripped_a == stripped_b, f"file {n} diverges outside the watermark"
            # And there MUST be a watermark in both.
            assert watermark_re.search(body_a)
            assert watermark_re.search(body_b)


# ── 7: persona-link warning surfaces in composed manifest ────────────


@pytest.mark.asyncio
async def test_persona_unresolved_base_link_surfaces_warning(
    db_session: AsyncSession, memory_storage: InMemoryStorage,
) -> None:
    """A persona neuron linking to base/<missing> emits a warning."""
    _curator, occ_skill, _members = await _seed_occupation_with_n_members(
        db_session, storage=memory_storage, n_members=2,
    )
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")

    # Persona neuron #1 links to a base slug that doesn't exist in the
    # occupation members (skill-a, skill-b).
    _p, persona_skill, _neurons = await _seed_persona(
        db_session, storage=memory_storage,
        parent_skill=occ_skill, handle="jane", slug="jane-on-call",
        n_neurons=1,
        neuron_links_to_base=["domains/ci-cd/this-doesnt-exist"],
    )
    await builder.build_persona(db_session, persona_skill.id, "1.0.0")

    buyer = await _make_user(
        db_session, email="b@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )
    await _create_license(
        db_session, buyer=buyer, skill=persona_skill,
        role=LicenseCompositionRole.PERSONA,
        target_occupation_skill_id=occ_skill.id,
    )

    result = await composer.compose_for_license(
        db_session, buyer_id=buyer.id, occupation_license_id=occ_lic.id,
    )
    zip_bytes = await memory_storage.get_object(result.storage_url)
    import json as _json
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        vault_json = _json.loads(zf.read("vault.json").decode("utf-8"))
    warnings = vault_json.get("warnings", [])
    assert any(
        w.get("unresolved_link") == "domains/ci-cd/this-doesnt-exist"
        for w in warnings
    )


# ── 8: auth — buyer doesn't own the occupation license ───────────────


@pytest.mark.asyncio
async def test_compose_404_when_buyer_doesnt_own_occupation_license(
    db_session: AsyncSession, memory_storage: InMemoryStorage,
) -> None:
    """404 with ``vault.license_not_found`` for a license held by a different buyer."""
    _curator, occ_skill, _members = await _seed_occupation_with_n_members(
        db_session, storage=memory_storage, n_members=2,
    )
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")

    other_buyer = await _make_user(
        db_session, email="other@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=other_buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )

    not_the_owner = await _make_user(
        db_session, email="random@example.com", role=UserRole.BUYER,
    )
    with pytest.raises(composer.VaultComposeError) as exc:
        await composer.compose_for_license(
            db_session,
            buyer_id=not_the_owner.id,
            occupation_license_id=occ_lic.id,
        )
    assert exc.value.code == "vault.license_not_found"
    assert exc.value.status_code == 404


# ── 9: persona-license-not-held → 403 ────────────────────────────────


@pytest.mark.asyncio
async def test_compose_403_when_requested_persona_license_not_held(
    db_session: AsyncSession, memory_storage: InMemoryStorage,
) -> None:
    """403 ``vault.persona_license_not_held`` for a persona id the buyer doesn't own."""
    _curator, occ_skill, _members = await _seed_occupation_with_n_members(
        db_session, storage=memory_storage, n_members=2,
    )
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    _p, persona_skill, _neurons = await _seed_persona(
        db_session, storage=memory_storage,
        parent_skill=occ_skill, handle="practitioner-x", slug="x-on-call",
        n_neurons=1,
    )
    await builder.build_persona(db_session, persona_skill.id, "1.0.0")

    # Buyer has the occupation license but NOT the persona license.
    buyer = await _make_user(
        db_session, email="b@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )

    # A persona license held by a DIFFERENT buyer — we'll pretend our
    # buyer is requesting its id.
    other_buyer = await _make_user(
        db_session, email="other@example.com", role=UserRole.BUYER,
    )
    other_persona_lic = await _create_license(
        db_session, buyer=other_buyer, skill=persona_skill,
        role=LicenseCompositionRole.PERSONA,
        target_occupation_skill_id=occ_skill.id,
    )

    with pytest.raises(composer.VaultComposeError) as exc:
        await composer.compose_for_license(
            db_session, buyer_id=buyer.id,
            occupation_license_id=occ_lic.id,
            include_persona_license_ids=[other_persona_lic.id],
        )
    assert exc.value.code == "vault.persona_license_not_held"
    assert exc.value.status_code == 403


# ── 10: cache invalidation on a new vault_build ──────────────────────


@pytest.mark.asyncio
async def test_new_vault_build_invalidates_cache_via_keyed_build_id(
    db_session: AsyncSession, memory_storage: InMemoryStorage,
) -> None:
    """A new occupation build → fresh cache key → cache_hit=False on next call."""
    _curator, occ_skill, members = await _seed_occupation_with_n_members(
        db_session, storage=memory_storage, n_members=1,
    )
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    buyer = await _make_user(
        db_session, email="b@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )

    first = await composer.compose_for_license(
        db_session, buyer_id=buyer.id, occupation_license_id=occ_lic.id,
    )
    second = await composer.compose_for_license(
        db_session, buyer_id=buyer.id, occupation_license_id=occ_lic.id,
    )
    assert first.cache_hit is False
    assert second.cache_hit is True
    first_build_id = first.occupation_build_id

    # Simulate a new build by inserting a fresh VaultBuild row with
    # different content_hash (e.g. a new member appeared).
    new_member, _v = await _add_member_skill(
        db_session, storage=memory_storage,
        creator=members[0].creator_id and await db_session.get(User, members[0].creator_id),  # type: ignore[arg-type]
        creator_handle="skillsgit-curated", slug="skill-extra", name="Extra",
    )
    await _add_member(
        db_session, occupation=occ_skill, member=new_member, domain="ci-cd",
        sort_order=2,
    )
    new_build = await builder.build_occupation(
        db_session, occ_skill.id, "1.0.0", force_rebuild=True
    )
    # The builder is idempotent on identical content_hash — force a
    # NEW build by altering inputs (we just added a member, so the new
    # zip bytes WILL differ from the previous build's content_hash).
    assert new_build.id != first_build_id or new_build.content_hash != first.composed_hash

    third = await composer.compose_for_license(
        db_session, buyer_id=buyer.id, occupation_license_id=occ_lic.id,
    )
    # New build_id → new cache_key → cache miss again.
    assert third.cache_hit is False
    assert third.occupation_build_id != first_build_id


# ── 11: composed_hash on download row matches actual zip bytes ───────


@pytest.mark.asyncio
async def test_vault_downloads_row_records_hash_matching_bytes(
    db_session: AsyncSession, memory_storage: InMemoryStorage,
) -> None:
    """Audit row's composed_hash is sha256 over the actual delivered bytes."""
    _curator, occ_skill, _members = await _seed_occupation_with_n_members(
        db_session, storage=memory_storage, n_members=2,
    )
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    buyer = await _make_user(
        db_session, email="b@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )

    result = await composer.compose_for_license(
        db_session, buyer_id=buyer.id, occupation_license_id=occ_lic.id,
    )
    zip_bytes = await memory_storage.get_object(result.storage_url)
    actual_hash = hashlib.sha256(zip_bytes).hexdigest()
    assert actual_hash == result.composed_hash

    download = await db_session.get(VaultDownload, result.vault_download_id)
    assert download is not None
    assert download.composed_hash == actual_hash
    assert download.storage_url == result.storage_url
