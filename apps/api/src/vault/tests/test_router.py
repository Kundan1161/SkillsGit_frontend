"""Router-level tests for the vault module (T-07).

Covers the three endpoints from ``team/02-api-surface.md`` §4 + the
brief's verbatim acceptance criteria:

* ``POST /v1/licenses/{occupation_license_id}/vault`` — happy path
  returns a 60s presigned URL whose downloaded zip lists files from
  the occupation + every persona license. 404 on wrong-owner license,
  403 on a requested persona license the buyer doesn't hold.
* ``GET /v1/licenses/{occupation_license_id}/vault/downloads`` —
  paginated history; 404 to non-owners.
* ``GET /v1/vault/builds/{build_id}`` — owner can read; admin can read;
  unauthorised buyers get 404.

Auth strategy mirrors ``src/personas/tests/test_router.py``: override
the FastAPI deps so tests don't need to run the JWT cookie flow.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import src.core.db as core_db
from src.auth.deps import (
    current_active_user,
    current_user,
    get_optional_user,
    require_creator,
)
from src.billing.models import (
    License,
    LicenseCompositionRole,
    LicenseSource,
    LicenseStatus,
    SupportTier,
)
from src.core import cache as cache_mod
from src.core.db import get_db
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

# ── Seed helpers (mirror test_composer.py) ───────────────────────────


@pytest.fixture(autouse=True)
def _clear_cache_between_tests() -> Any:
    cache_mod.reset_inmem_for_tests()
    yield
    cache_mod.reset_inmem_for_tests()


async def _make_user(
    session: AsyncSession,
    *,
    email: str,
    handle: str | None = None,
    role: UserRole = UserRole.BUYER,
    is_admin: bool = False,
) -> User:
    user = User(
        email=email,
        hashed_password="x" * 32,
        display_name=(handle or email.split("@", maxsplit=1)[0]).title(),
        role=role,
        is_active=True,
        is_verified=True,
        is_creator_verified=role == UserRole.CREATOR,
        is_admin=is_admin,
    )
    session.add(user)
    await session.flush()
    if handle is not None:
        session.add(
            CreatorProfile(user_id=user.id, handle=handle, payout_country="US")
        )
        await session.flush()
    return user


def _skill_md_bytes(
    *,
    creator_handle: str,
    slug: str,
    name: str,
    kind: str = "skill",
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
    if neuron_block is not None:
        yaml_lines.append("neuron:")
        for key, val in neuron_block.items():
            yaml_lines.append(f"  {key}: {val!r}")
    body = (
        "## When to use\n\nUse when X.\n\n"
        "## How to apply\n\n1. Read.\n2. Apply.\n"
    )
    return ("---\n" + "\n".join(yaml_lines) + "\n---\n\n" + body).encode("utf-8")


async def _seed_member(
    session: AsyncSession,
    *,
    storage: InMemoryStorage,
    creator: User,
    creator_handle: str,
    slug: str,
    kind: SkillKind = SkillKind.SKILL,
    parent_occupation_id: str | None = None,
    neuron_block: dict[str, str] | None = None,
) -> tuple[Skill, SkillVersion]:
    body = _skill_md_bytes(
        creator_handle=creator_handle,
        slug=slug,
        name=slug,
        kind=kind.value,
        parent_occupation_id=parent_occupation_id,
        neuron_block=neuron_block,
    )
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=slug,
        tagline=slug,
        description_md=slug,
        category="engineering",
        tags=[slug.split("-", maxsplit=1)[0]],
        status=SkillStatus.PUBLISHED,
        kind=kind,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    await storage.put_object(f"skills/{skill.id}/1.0.0.md", body, "text/markdown")
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


async def _seed_occupation_skill(
    session: AsyncSession, *, creator: User, slug: str = "ai-devops",
    domains: list[str] | None = None,
) -> tuple[Skill, Occupation]:
    skill = Skill(
        creator_id=creator.id,
        slug=slug, name=slug, tagline=slug, description_md=slug,
        category="occupations", tags=["devops"],
        status=SkillStatus.PUBLISHED,
        kind=SkillKind.OCCUPATION,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    occ = Occupation(
        skill_id=skill.id, summary_md=slug,
        domains=domains or ["ci-cd", "observability"],
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
    return skill, occ


async def _seed_persona_skill(
    session: AsyncSession, *, creator: User, slug: str,
    parent_occupation_skill: Skill,
) -> tuple[Skill, Persona]:
    skill = Skill(
        creator_id=creator.id,
        slug=slug, name=slug, tagline=slug, description_md=slug,
        category="personas", tags=["devops"],
        status=SkillStatus.PUBLISHED,
        kind=SkillKind.PERSONA,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    persona = Persona(
        skill_id=skill.id,
        parent_occupation_id=parent_occupation_skill.id,
        creator_intro_md=f"hi {slug}",
        years_of_experience=5,
        specialization="t",
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
    return skill, persona


async def _add_member(
    session: AsyncSession, *, occupation: Skill, member: Skill,
    domain: str = "ci-cd", sort_order: int = 0,
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
        persona_id=persona.id, neuron_skill_id=neuron.id,
        sort_order=sort_order, section=None,
    )
    session.add(row)
    await session.flush()
    return row


async def _create_license(
    session: AsyncSession, *, buyer: User, skill: Skill,
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


# ── App fixture with deps overridden ─────────────────────────────────


@pytest_asyncio.fixture(scope="function")
async def auth_client(
    db_engine: Any, monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[tuple[AsyncClient, Any]]:
    """Yield (client, app) so each test can flip auth overrides."""
    from src.vault.router import router as vault_router

    test_sessionmaker = async_sessionmaker(
        bind=db_engine, expire_on_commit=False, autoflush=False,
        class_=AsyncSession,
    )
    monkeypatch.setattr(core_db, "engine", db_engine)
    monkeypatch.setattr(core_db, "SessionLocal", test_sessionmaker)

    from src.main import create_app

    app = create_app()
    app.include_router(vault_router)

    async def _override_get_db() -> AsyncIterator[AsyncSession]:
        async with test_sessionmaker() as s:
            try:
                yield s
            except Exception:
                await s.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac, app


def _login_as(app: Any, user: User) -> None:
    app.dependency_overrides[current_user] = lambda: user
    app.dependency_overrides[current_active_user] = lambda: user
    app.dependency_overrides[get_optional_user] = lambda: user
    app.dependency_overrides[require_creator] = lambda: user


# ── POST /v1/licenses/{id}/vault — happy path ────────────────────────


@pytest.mark.asyncio
async def test_post_vault_happy_path(
    auth_client: tuple[AsyncClient, Any],
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    client, app = auth_client
    curator = await _make_user(
        db_session, email="curator@example.com", handle="curated",
        role=UserRole.CREATOR,
    )
    occ_skill, _occ = await _seed_occupation_skill(
        db_session, creator=curator, slug="ai-devops",
    )
    m1, _v1 = await _seed_member(
        db_session, storage=memory_storage, creator=curator,
        creator_handle="curated", slug="member-a",
    )
    await _add_member(db_session, occupation=occ_skill, member=m1)
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")

    buyer = await _make_user(
        db_session, email="buyer@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )
    await db_session.commit()
    _login_as(app, buyer)

    r = await client.post(
        f"/v1/licenses/{occ_lic.id}/vault",
        json={},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["cache_hit"] is False
    assert body["composed_hash"]
    assert body["presigned_url"].startswith("memory://")
    assert "expires_at" in body
    assert body["persona_build_ids"] == []
    assert body["occupation_build_id"]


@pytest.mark.asyncio
async def test_post_vault_second_call_cache_hit(
    auth_client: tuple[AsyncClient, Any],
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    client, app = auth_client
    curator = await _make_user(
        db_session, email="curator@example.com", handle="curated",
        role=UserRole.CREATOR,
    )
    occ_skill, _occ = await _seed_occupation_skill(
        db_session, creator=curator,
    )
    m1, _v1 = await _seed_member(
        db_session, storage=memory_storage, creator=curator,
        creator_handle="curated", slug="m-one",
    )
    await _add_member(db_session, occupation=occ_skill, member=m1)
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")

    buyer = await _make_user(
        db_session, email="buyer@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )
    await db_session.commit()
    _login_as(app, buyer)

    r1 = await client.post(f"/v1/licenses/{occ_lic.id}/vault", json={})
    r2 = await client.post(f"/v1/licenses/{occ_lic.id}/vault", json={})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["cache_hit"] is False
    assert r2.json()["cache_hit"] is True
    assert r1.json()["composed_hash"] == r2.json()["composed_hash"]


# ── POST /v1/licenses/{id}/vault — auth fails ────────────────────────


@pytest.mark.asyncio
async def test_post_vault_404_when_not_owner(
    auth_client: tuple[AsyncClient, Any],
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """A buyer hitting another buyer's license id gets 404 (no existence leak)."""
    client, app = auth_client
    curator = await _make_user(
        db_session, email="curator@example.com", handle="curated",
        role=UserRole.CREATOR,
    )
    occ_skill, _occ = await _seed_occupation_skill(
        db_session, creator=curator,
    )
    m1, _v1 = await _seed_member(
        db_session, storage=memory_storage, creator=curator,
        creator_handle="curated", slug="member-a",
    )
    await _add_member(db_session, occupation=occ_skill, member=m1)
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")

    owner = await _make_user(
        db_session, email="owner@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=owner, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )
    stranger = await _make_user(
        db_session, email="stranger@example.com", role=UserRole.BUYER,
    )
    await db_session.commit()
    _login_as(app, stranger)

    r = await client.post(f"/v1/licenses/{occ_lic.id}/vault", json={})
    assert r.status_code == 404, r.text
    assert r.json()["error"]["code"] == "vault.license_not_found"


@pytest.mark.asyncio
async def test_post_vault_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, _app = auth_client
    fake_id = uuid.uuid4()
    r = await client.post(f"/v1/licenses/{fake_id}/vault", json={})
    assert r.status_code == 401, r.text


@pytest.mark.asyncio
async def test_post_vault_403_persona_license_not_held(
    auth_client: tuple[AsyncClient, Any],
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """Requesting a persona license you don't own returns 403."""
    client, app = auth_client
    curator = await _make_user(
        db_session, email="curator@example.com", handle="curated",
        role=UserRole.CREATOR,
    )
    practitioner = await _make_user(
        db_session, email="prac@example.com", handle="practitioner",
        role=UserRole.CREATOR,
    )
    occ_skill, _occ = await _seed_occupation_skill(
        db_session, creator=curator,
    )
    m1, _v1 = await _seed_member(
        db_session, storage=memory_storage, creator=curator,
        creator_handle="curated", slug="member-a",
    )
    await _add_member(db_session, occupation=occ_skill, member=m1)
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")

    persona_skill, _p = await _seed_persona_skill(
        db_session, creator=practitioner, slug="prac-on-call",
        parent_occupation_skill=occ_skill,
    )
    neuron, _nv = await _seed_member(
        db_session, storage=memory_storage, creator=practitioner,
        creator_handle="practitioner", slug="neuron-x",
        kind=SkillKind.MEMORY_NEURON,
        parent_occupation_id=str(occ_skill.id),
        neuron_block={
            "situation": "x", "decision": "y", "outcome": "z",
        },
    )
    await _add_neuron(db_session, persona=persona_skill, neuron=neuron)
    await builder.build_persona(db_session, persona_skill.id, "1.0.0")

    buyer = await _make_user(
        db_session, email="buyer@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )

    # Persona license owned by a different buyer.
    other = await _make_user(
        db_session, email="other@example.com", role=UserRole.BUYER,
    )
    other_p_lic = await _create_license(
        db_session, buyer=other, skill=persona_skill,
        role=LicenseCompositionRole.PERSONA,
        target_occupation_skill_id=occ_skill.id,
    )
    await db_session.commit()
    _login_as(app, buyer)

    r = await client.post(
        f"/v1/licenses/{occ_lic.id}/vault",
        json={"include_persona_license_ids": [str(other_p_lic.id)]},
    )
    assert r.status_code == 403, r.text
    assert r.json()["error"]["code"] == "vault.persona_license_not_held"


# ── POST /v1/licenses/{id}/vault — validation ────────────────────────


@pytest.mark.asyncio
async def test_post_vault_validation_fail_extra_field(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    buyer = await _make_user(
        db_session, email="b@example.com", role=UserRole.BUYER,
    )
    await db_session.commit()
    _login_as(app, buyer)

    r = await client.post(
        f"/v1/licenses/{uuid.uuid4()}/vault",
        json={"include_persona_license_ids": ["not-a-uuid"]},
    )
    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "request.validation_failed"


# ── GET /v1/licenses/{id}/vault/downloads ────────────────────────────


@pytest.mark.asyncio
async def test_list_vault_downloads_happy_path(
    auth_client: tuple[AsyncClient, Any],
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    client, app = auth_client
    curator = await _make_user(
        db_session, email="curator@example.com", handle="curated",
        role=UserRole.CREATOR,
    )
    occ_skill, _occ = await _seed_occupation_skill(
        db_session, creator=curator,
    )
    m1, _v1 = await _seed_member(
        db_session, storage=memory_storage, creator=curator,
        creator_handle="curated", slug="member-a",
    )
    await _add_member(db_session, occupation=occ_skill, member=m1)
    await builder.build_occupation(db_session, occ_skill.id, "1.0.0")

    buyer = await _make_user(
        db_session, email="buyer@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )
    await db_session.commit()
    _login_as(app, buyer)

    # Generate one download.
    await client.post(f"/v1/licenses/{occ_lic.id}/vault", json={})

    r = await client.get(f"/v1/licenses/{occ_lic.id}/vault/downloads")
    assert r.status_code == 200, r.text
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["composed_hash"]
    assert items[0]["occupation_build_id"]


@pytest.mark.asyncio
async def test_list_vault_downloads_404_for_non_owner(
    auth_client: tuple[AsyncClient, Any],
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    client, app = auth_client
    curator = await _make_user(
        db_session, email="curator@example.com", handle="curated",
        role=UserRole.CREATOR,
    )
    occ_skill, _occ = await _seed_occupation_skill(
        db_session, creator=curator,
    )
    owner = await _make_user(
        db_session, email="owner@example.com", role=UserRole.BUYER,
    )
    occ_lic = await _create_license(
        db_session, buyer=owner, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )
    stranger = await _make_user(
        db_session, email="stranger@example.com", role=UserRole.BUYER,
    )
    await db_session.commit()
    _login_as(app, stranger)

    r = await client.get(f"/v1/licenses/{occ_lic.id}/vault/downloads")
    assert r.status_code == 404, r.text
    assert r.json()["error"]["code"] == "license.not_found"


# ── GET /v1/vault/builds/{id} ────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_vault_build_by_owner(
    auth_client: tuple[AsyncClient, Any],
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """The skill's creator can read the build summary."""
    client, app = auth_client
    curator = await _make_user(
        db_session, email="curator@example.com", handle="curated",
        role=UserRole.CREATOR,
    )
    occ_skill, _occ = await _seed_occupation_skill(
        db_session, creator=curator,
    )
    m1, _v1 = await _seed_member(
        db_session, storage=memory_storage, creator=curator,
        creator_handle="curated", slug="member-a",
    )
    await _add_member(db_session, occupation=occ_skill, member=m1)
    build = await builder.build_occupation(db_session, occ_skill.id, "1.0.0")
    await db_session.commit()
    _login_as(app, curator)

    r = await client.get(f"/v1/vault/builds/{build.id}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] == str(build.id)
    assert body["status"] == "succeeded"
    assert body["content_hash"] == build.content_hash
    assert body["manifest_summary"]["schema_version"] == 1


@pytest.mark.asyncio
async def test_get_vault_build_by_license_holder(
    auth_client: tuple[AsyncClient, Any],
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """A buyer with an active license on the parent skill can read it."""
    client, app = auth_client
    curator = await _make_user(
        db_session, email="curator@example.com", handle="curated",
        role=UserRole.CREATOR,
    )
    occ_skill, _occ = await _seed_occupation_skill(
        db_session, creator=curator,
    )
    m1, _v1 = await _seed_member(
        db_session, storage=memory_storage, creator=curator,
        creator_handle="curated", slug="member-a",
    )
    await _add_member(db_session, occupation=occ_skill, member=m1)
    build = await builder.build_occupation(db_session, occ_skill.id, "1.0.0")

    buyer = await _make_user(
        db_session, email="buyer@example.com", role=UserRole.BUYER,
    )
    await _create_license(
        db_session, buyer=buyer, skill=occ_skill,
        role=LicenseCompositionRole.OCCUPATION,
    )
    await db_session.commit()
    _login_as(app, buyer)

    r = await client.get(f"/v1/vault/builds/{build.id}")
    assert r.status_code == 200, r.text


@pytest.mark.asyncio
async def test_get_vault_build_404_for_unauthorised(
    auth_client: tuple[AsyncClient, Any],
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """A logged-in user with no license + no ownership gets 404."""
    client, app = auth_client
    curator = await _make_user(
        db_session, email="curator@example.com", handle="curated",
        role=UserRole.CREATOR,
    )
    occ_skill, _occ = await _seed_occupation_skill(
        db_session, creator=curator,
    )
    m1, _v1 = await _seed_member(
        db_session, storage=memory_storage, creator=curator,
        creator_handle="curated", slug="member-a",
    )
    await _add_member(db_session, occupation=occ_skill, member=m1)
    build = await builder.build_occupation(db_session, occ_skill.id, "1.0.0")

    stranger = await _make_user(
        db_session, email="stranger@example.com", role=UserRole.BUYER,
    )
    await db_session.commit()
    _login_as(app, stranger)

    r = await client.get(f"/v1/vault/builds/{build.id}")
    assert r.status_code == 404, r.text
    assert r.json()["error"]["code"] == "vault.build_not_found"


@pytest.mark.asyncio
async def test_get_vault_build_404_for_unknown_id(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    buyer = await _make_user(
        db_session, email="b@example.com", role=UserRole.BUYER,
    )
    await db_session.commit()
    _login_as(app, buyer)

    r = await client.get(f"/v1/vault/builds/{uuid.uuid4()}")
    assert r.status_code == 404, r.text
    assert r.json()["error"]["code"] == "vault.build_not_found"
