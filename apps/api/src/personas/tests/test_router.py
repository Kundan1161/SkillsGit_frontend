"""Router-level tests for the personas module.

T-04 acceptance bullet: every endpoint has a router-level test covering
the happy + auth-fail + validation-fail branches.

These talk through HTTP via the ``auth_client`` fixture below. The
``_make_creator`` / ``_make_skill`` helpers seed the DB directly so we
can target specific authz scenarios without recreating the full
session-cookie flow for every test.

Authentication strategy: instead of running the auth flow (which would
double-test things outside this module), we override the auth
dependencies via ``app.dependency_overrides`` for each test. This
mirrors the sibling ``src/occupations/tests/test_router.py`` pattern.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
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
from src.core.db import get_db
from src.occupations.models import Occupation
from src.personas.models import Persona, PersonaNeuron
from src.skills.models import (
    PricingModel,
    Skill,
    SkillKind,
    SkillStatus,
    SkillVersion,
)
from src.users.models import CreatorProfile, User, UserRole

# ── Local seed helpers (duplicated so the test file is self-contained) ─


async def _make_user(
    session: AsyncSession,
    *,
    email: str,
    handle: str | None = None,
    role: UserRole = UserRole.BUYER,
    is_creator_verified: bool = False,
    is_admin: bool = False,
    payouts_enabled: bool = False,
    stripe_connect_account_id: str | None = None,
) -> User:
    user = User(
        email=email,
        hashed_password="x" * 32,
        display_name=(handle or email.split("@", maxsplit=1)[0]).title(),
        role=role,
        is_active=True,
        is_verified=True,
        is_creator_verified=is_creator_verified,
        is_admin=is_admin,
        payouts_enabled=payouts_enabled,
        stripe_connect_account_id=stripe_connect_account_id,
    )
    session.add(user)
    await session.flush()
    if handle is not None:
        session.add(
            CreatorProfile(user_id=user.id, handle=handle, payout_country="US")
        )
        await session.flush()
    return user


async def _make_skill(
    session: AsyncSession,
    *,
    creator: User,
    slug: str,
    name: str | None = None,
    kind: SkillKind = SkillKind.SKILL,
    status: SkillStatus = SkillStatus.PUBLISHED,
    pricing_model: PricingModel = PricingModel.FREE,
    one_time_price_cents: int | None = None,
) -> Skill:
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=name or slug.replace("-", " ").title(),
        tagline=f"Tagline for {slug}",
        description_md=f"# {slug}\n",
        category="engineering",
        tags=[slug.split("-", maxsplit=1)[0]],
        status=status,
        kind=kind,
        pricing_model=pricing_model,
        one_time_price_cents=one_time_price_cents,
    )
    session.add(skill)
    await session.flush()
    return skill


async def _make_occupation_row(
    session: AsyncSession,
    *,
    creator: User,
    slug: str = "ai-devops-engineer",
    status: SkillStatus = SkillStatus.PUBLISHED,
) -> Skill:
    skill = await _make_skill(
        session, creator=creator, slug=slug,
        kind=SkillKind.OCCUPATION, status=status,
    )
    session.add(
        Occupation(
            skill_id=skill.id,
            summary_md=f"Summary for {slug}",
            domains=["ci-cd", "observability"],
            persona_count=0,
            recommended_persona_count=2,
        )
    )
    await session.flush()
    return skill


async def _make_neuron_row(
    session: AsyncSession,
    *,
    creator: User,
    slug: str,
) -> Skill:
    return await _make_skill(
        session, creator=creator, slug=slug,
        kind=SkillKind.MEMORY_NEURON,
        status=SkillStatus.PUBLISHED,
    )


async def _attach_neuron(
    session: AsyncSession,
    *,
    persona_skill_id: uuid.UUID,
    neuron_skill_id: uuid.UUID,
    sort_order: int = 0,
) -> PersonaNeuron:
    row = PersonaNeuron(
        persona_id=persona_skill_id,
        neuron_skill_id=neuron_skill_id,
        sort_order=sort_order,
    )
    session.add(row)
    await session.flush()
    persona = await session.get(Persona, persona_skill_id)
    if persona is not None:
        persona.neuron_count += 1
        await session.flush()
    return row


async def _make_version(
    session: AsyncSession,
    *,
    skill: Skill,
    version: str = "1.0.0",
    released: bool = True,
) -> SkillVersion:
    v = SkillVersion(
        skill_id=skill.id,
        version=version,
        content_hash="a" * 64,
        storage_url=f"s3://test/{skill.slug}.md",
        ai_requirements={"required_models": ["claude-opus-4-7"]},
        changelog_md="## When to use\nNotes.\n\n## How to apply\n1. step",
        released_at=datetime.now(UTC) if released else None,
        released_by=skill.creator_id if released else None,
    )
    session.add(v)
    await session.flush()
    if released:
        skill.latest_version_id = v.id
        skill.status = SkillStatus.PUBLISHED
        await session.flush()
    return v


# ── Auth-override client builder ──────────────────────────────────────


@pytest_asyncio.fixture(scope="function")
async def auth_client(
    db_engine: Any, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[tuple[AsyncClient, Any]]:
    """Yield (client, app) so tests can flip dependency overrides."""
    from src.billing.router import router as billing_router
    from src.personas.router import router as personas_router

    test_sessionmaker = async_sessionmaker(
        bind=db_engine, expire_on_commit=False, autoflush=False,
        class_=AsyncSession,
    )
    monkeypatch.setattr(core_db, "engine", db_engine)
    monkeypatch.setattr(core_db, "SessionLocal", test_sessionmaker)

    from src.main import create_app

    app = create_app()
    app.include_router(personas_router)
    # Also mount billing so the 409-gate router-level test (T-04 bullet 2)
    # can drive a real POST /v1/checkout/sessions.
    app.include_router(billing_router)

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


def _logout(app: Any) -> None:
    app.dependency_overrides.pop(current_user, None)
    app.dependency_overrides.pop(current_active_user, None)
    app.dependency_overrides.pop(get_optional_user, None)
    app.dependency_overrides.pop(require_creator, None)


# ── POST /v1/personas ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_happy_path(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)

    r = await client.post(
        "/v1/personas",
        json={
            "name": "Jane the DevOps Lead",
            "slug": "jane-devops",
            "parent_occupation_id": str(parent.id),
            "creator_intro_md": "12 years on-call.",
            "specialization": "Fintech on-call lead",
            "years_of_experience": 12,
            "pricing_model": "free",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["slug"] == "jane-devops"
    assert body["kind"] == "persona"
    assert body["parent_occupation"]["slug"] == "ai-devops-engineer"
    assert r.headers["Location"].startswith("/v1/personas/")


@pytest.mark.asyncio
async def test_create_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.post(
        "/v1/personas",
        json={
            "name": "X", "slug": "x",
            "parent_occupation_id": str(uuid.uuid4()),
            "pricing_model": "free",
        },
    )
    assert r.status_code == 401, r.text


@pytest.mark.asyncio
async def test_create_rejects_buyer(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    buyer = await _make_user(
        db_session, email="buyer@example.com",
        role=UserRole.BUYER,
    )
    await db_session.commit()
    # Only override the buyer-style deps, NOT require_creator.
    app.dependency_overrides[current_user] = lambda: buyer
    app.dependency_overrides[current_active_user] = lambda: buyer
    app.dependency_overrides[get_optional_user] = lambda: buyer

    r = await client.post(
        "/v1/personas",
        json={
            "name": "X", "slug": "x",
            "parent_occupation_id": str(uuid.uuid4()),
            "pricing_model": "free",
        },
    )
    assert r.status_code == 403, r.text
    assert r.json()["error"]["code"] == "auth.not_a_creator"


@pytest.mark.asyncio
async def test_create_validation_fail_bad_slug(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)

    r = await client.post(
        "/v1/personas",
        json={
            "name": "Bad",
            "slug": "Bad Slug With Spaces",
            "parent_occupation_id": str(uuid.uuid4()),
            "pricing_model": "free",
        },
    )
    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "request.validation_failed"


@pytest.mark.asyncio
async def test_create_requires_verified_creator(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    unverified = await _make_user(
        db_session, email="anon@example.com", handle="anon",
        role=UserRole.CREATOR, is_creator_verified=False,
    )
    await db_session.commit()
    _login_as(app, unverified)

    r = await client.post(
        "/v1/personas",
        json={
            "name": "X", "slug": "x",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    assert r.status_code == 403, r.text
    assert r.json()["error"]["code"] == "persona.creator_not_verified"


@pytest.mark.asyncio
async def test_create_rejects_non_occupation_parent(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    """T-04 acceptance bullet 1 — parent must be a kind=occupation row."""
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    # Not an occupation — a plain skill.
    not_an_occ = await _make_skill(
        db_session, creator=occ_creator, slug="just-a-skill",
        kind=SkillKind.SKILL,
    )
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)

    r = await client.post(
        "/v1/personas",
        json={
            "name": "Jane", "slug": "jane",
            "parent_occupation_id": str(not_an_occ.id),
            "pricing_model": "free",
        },
    )
    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "persona.parent_occupation_invalid"


# ── PATCH /v1/personas/{id} ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_patch_happy_path(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)

    r = await client.post(
        "/v1/personas",
        json={
            "name": "Initial",
            "slug": "patchme",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    assert r.status_code == 201, r.text
    skill_id = r.json()["id"]

    r2 = await client.patch(
        f"/v1/personas/{skill_id}",
        json={"name": "Renamed", "specialization": "Updated"},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["name"] == "Renamed"
    assert r2.json()["specialization"] == "Updated"


@pytest.mark.asyncio
async def test_patch_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.patch(
        f"/v1/personas/{uuid.uuid4()}", json={"name": "X"}
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_patch_rejects_non_owner_404(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    owner = await _make_user(
        db_session, email="owner@example.com", handle="owner",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    intruder = await _make_user(
        db_session, email="intruder@example.com", handle="intruder",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()

    _login_as(app, owner)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "Owned", "slug": "owned",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]

    _login_as(app, intruder)
    r2 = await client.patch(
        f"/v1/personas/{skill_id}", json={"name": "Hacked"}
    )
    assert r2.status_code == 404, r2.text
    assert r2.json()["error"]["code"] == "persona.not_found"


@pytest.mark.asyncio
async def test_patch_validation_rejects_extra_keys(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "X", "slug": "x",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    r2 = await client.patch(
        f"/v1/personas/{skill_id}",
        json={"name": "Y", "bogus_extra_field": "no"},
    )
    assert r2.status_code == 422, r2.text


# ── Neuron membership endpoints ───────────────────────────────────────


@pytest.mark.asyncio
async def test_reorder_neurons_happy(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    n1 = await _make_neuron_row(db_session, creator=creator, slug="n1")
    n2 = await _make_neuron_row(db_session, creator=creator, slug="n2")
    await db_session.commit()
    _login_as(app, creator)

    r = await client.post(
        "/v1/personas",
        json={
            "name": "Jane", "slug": "jane",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    await _attach_neuron(
        db_session, persona_skill_id=uuid.UUID(skill_id),
        neuron_skill_id=n1.id, sort_order=0,
    )
    await _attach_neuron(
        db_session, persona_skill_id=uuid.UUID(skill_id),
        neuron_skill_id=n2.id, sort_order=1,
    )
    await db_session.commit()

    r2 = await client.post(
        f"/v1/personas/{skill_id}/neurons/order",
        json={
            "items": [
                {"neuron_skill_id": str(n2.id), "sort_order": 0},
                {"neuron_skill_id": str(n1.id), "sort_order": 1},
            ]
        },
    )
    assert r2.status_code == 200, r2.text
    by_slug = {n["neuron_slug"]: n for n in r2.json()["items"]}
    assert by_slug["n2"]["sort_order"] == 0
    assert by_slug["n1"]["sort_order"] == 1


@pytest.mark.asyncio
async def test_reorder_neurons_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.post(
        f"/v1/personas/{uuid.uuid4()}/neurons/order",
        json={"items": []},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_reorder_validation_rejects_extra_keys(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        f"/v1/personas/{uuid.uuid4()}/neurons/order",
        json={
            "items": [
                {
                    "neuron_skill_id": str(uuid.uuid4()),
                    "sort_order": 0,
                    "junk_extra": "no",
                }
            ]
        },
    )
    assert r.status_code == 422, r.text


@pytest.mark.asyncio
async def test_delete_neuron_happy(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    n1 = await _make_neuron_row(db_session, creator=creator, slug="n1")
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "Jane", "slug": "jane",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    await _attach_neuron(
        db_session, persona_skill_id=uuid.UUID(skill_id),
        neuron_skill_id=n1.id,
    )
    await db_session.commit()

    r2 = await client.delete(
        f"/v1/personas/{skill_id}/neurons/{n1.id}"
    )
    assert r2.status_code == 204, r2.text


@pytest.mark.asyncio
async def test_delete_neuron_missing_404(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "Jane", "slug": "jane",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    r2 = await client.delete(
        f"/v1/personas/{skill_id}/neurons/{uuid.uuid4()}"
    )
    assert r2.status_code == 404, r2.text


@pytest.mark.asyncio
async def test_delete_neuron_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.delete(
        f"/v1/personas/{uuid.uuid4()}/neurons/{uuid.uuid4()}"
    )
    assert r.status_code == 401


# ── Build / publish ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_build_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.post(
        f"/v1/personas/{uuid.uuid4()}/build",
        json={"version": "1.0.0"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_build_rejects_empty_neurons(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "Empty", "slug": "empty",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    parent_skill = await db_session.get(Skill, uuid.UUID(skill_id))
    assert parent_skill is not None
    await _make_version(db_session, skill=parent_skill, version="1.0.0", released=False)
    await db_session.commit()

    r2 = await client.post(
        f"/v1/personas/{skill_id}/build",
        json={"version": "1.0.0"},
    )
    assert r2.status_code == 422, r2.text
    assert r2.json()["error"]["code"] == "persona.no_neurons"


@pytest.mark.asyncio
async def test_build_validation_fail_bad_version(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        f"/v1/personas/{uuid.uuid4()}/build",
        json={"version": "not-a-semver"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_publish_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.post(
        f"/v1/personas/{uuid.uuid4()}/publish",
        json={"version": "1.0.0"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_publish_happy_path(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    n1 = await _make_neuron_row(db_session, creator=creator, slug="n1")
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "Jane", "slug": "jane",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    parent_skill = await db_session.get(Skill, uuid.UUID(skill_id))
    assert parent_skill is not None
    await _attach_neuron(
        db_session, persona_skill_id=uuid.UUID(skill_id),
        neuron_skill_id=n1.id,
    )
    await _make_version(db_session, skill=parent_skill, version="1.0.0", released=False)
    await db_session.commit()

    r2 = await client.post(
        f"/v1/personas/{skill_id}/publish",
        json={"version": "1.0.0", "changelog_md": "First."},
    )
    assert r2.status_code == 202, r2.text
    assert r2.json()["status"] == "queued"


# ── Public list ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_returns_published_only(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "Pub", "slug": "pub",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill = await db_session.get(Skill, uuid.UUID(r.json()["id"]))
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.commit()
    # Another draft.
    await client.post(
        "/v1/personas",
        json={
            "name": "Draft", "slug": "draft",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )

    _logout(app)
    r2 = await client.get("/v1/personas")
    assert r2.status_code == 200, r2.text
    slugs = [it["slug"] for it in r2.json()["items"]]
    assert "pub" in slugs
    assert "draft" not in slugs


@pytest.mark.asyncio
async def test_list_validation_rejects_bad_limit(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.get("/v1/personas?limit=9999")
    # FastAPI Query(le=100) → 422
    assert r.status_code == 422


# ── Public detail ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_by_handle_published(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "Detail", "slug": "detail-slug",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill = await db_session.get(Skill, uuid.UUID(r.json()["id"]))
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.commit()

    _logout(app)
    r2 = await client.get("/v1/personas/janedoe/detail-slug")
    assert r2.status_code == 200, r2.text
    assert r2.json()["slug"] == "detail-slug"


@pytest.mark.asyncio
async def test_get_by_handle_404_for_unknown(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.get("/v1/personas/janedoe/nope")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_by_id_404_for_random(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.get(f"/v1/personas/{uuid.uuid4()}")
    assert r.status_code == 404


# ── Neuron list (entitlement-gated) ───────────────────────────────────


@pytest.mark.asyncio
async def test_neurons_list_404_for_anon(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    """T-04 acceptance bullet 3 — non-entitled callers get 404."""
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "Jane", "slug": "jane",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    skill = await db_session.get(Skill, uuid.UUID(skill_id))
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    n1 = await _make_neuron_row(db_session, creator=creator, slug="n1")
    await _attach_neuron(
        db_session, persona_skill_id=uuid.UUID(skill_id),
        neuron_skill_id=n1.id,
    )
    await db_session.commit()

    _logout(app)
    r2 = await client.get(f"/v1/personas/{skill_id}/neurons")
    assert r2.status_code == 404, r2.text
    assert r2.json()["error"]["code"] == "persona.not_found"


@pytest.mark.asyncio
async def test_neurons_list_200_for_license_holder(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    """T-04 acceptance bullet 3 — license holders get full bodies."""
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    n1 = await _make_neuron_row(db_session, creator=creator, slug="n1")
    n2 = await _make_neuron_row(db_session, creator=creator, slug="n2")
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "Jane", "slug": "jane",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    skill = await db_session.get(Skill, uuid.UUID(skill_id))
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await _attach_neuron(
        db_session, persona_skill_id=uuid.UUID(skill_id),
        neuron_skill_id=n1.id, sort_order=0,
    )
    await _attach_neuron(
        db_session, persona_skill_id=uuid.UUID(skill_id),
        neuron_skill_id=n2.id, sort_order=1,
    )

    # Mint a license for a buyer.
    buyer = await _make_user(
        db_session, email="buyer@example.com",
        role=UserRole.BUYER,
    )
    lic = License(
        buyer_id=buyer.id,
        skill_id=uuid.UUID(skill_id),
        source=LicenseSource.ONE_TIME,
        source_id=uuid.uuid4(),
        granted_at=datetime.now(UTC),
        status=LicenseStatus.ACTIVE,
        support_tier=SupportTier.NONE,
        composition_role=LicenseCompositionRole.PERSONA,
        target_occupation_skill_id=parent.id,
    )
    db_session.add(lic)
    await db_session.commit()

    # Now log in as the buyer.
    app.dependency_overrides[current_user] = lambda: buyer
    app.dependency_overrides[current_active_user] = lambda: buyer
    app.dependency_overrides[get_optional_user] = lambda: buyer
    r2 = await client.get(f"/v1/personas/{skill_id}/neurons")
    assert r2.status_code == 200, r2.text
    slugs = {n["neuron_slug"] for n in r2.json()["items"]}
    assert slugs == {"n1", "n2"}


@pytest.mark.asyncio
async def test_neurons_list_200_for_creator_on_draft(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    """Creator can read own draft persona neurons even pre-publish."""
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    n1 = await _make_neuron_row(db_session, creator=creator, slug="n1")
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "Jane", "slug": "jane",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    await _attach_neuron(
        db_session, persona_skill_id=uuid.UUID(skill_id),
        neuron_skill_id=n1.id,
    )
    await db_session.commit()

    # The persona is still DRAFT — but creator can see bodies.
    r2 = await client.get(f"/v1/personas/{skill_id}/neurons")
    assert r2.status_code == 200, r2.text
    assert [n["neuron_slug"] for n in r2.json()["items"]] == ["n1"]


# ── Graph preview ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_graph_preview_404_for_random(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.get(f"/v1/personas/{uuid.uuid4()}/graph-preview")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_graph_preview_happy_empty_neurons(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/personas",
        json={
            "name": "G", "slug": "g",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "free",
        },
    )
    skill = await db_session.get(Skill, uuid.UUID(r.json()["id"]))
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.commit()

    _logout(app)
    r2 = await client.get(f"/v1/personas/{skill.id}/graph-preview")
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert body["persona_slug"] == "g"
    assert body["nodes"] == []
    assert body["edges"] == []
    assert body["truncated"] is False
    assert body["node_cap"] == 200


# ── T-04 acceptance bullet 2: persona checkout 409 gate ──────────────


@pytest.mark.asyncio
async def test_persona_checkout_409_without_parent_license(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    """T-04 acceptance bullet 2 — POST /v1/checkout/sessions on a persona
    SKU rejects with 409 ``persona.requires_parent_occupation`` and the
    parent occupation's slug in the error payload, when the buyer does
    not hold an active license on the parent occupation.
    """
    client, app = auth_client
    occ_creator = await _make_user(
        db_session,
        email="occ@example.com",
        handle="occ-creator",
        role=UserRole.CREATOR,
        is_creator_verified=True,
        stripe_connect_account_id="acct_for_occ",
        payouts_enabled=True,
    )
    parent = await _make_occupation_row(db_session, creator=occ_creator)
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
        stripe_connect_account_id="acct_for_jane",
        payouts_enabled=True,
    )
    # Build a *paid* persona so the checkout endpoint reaches the gate
    # instead of bouncing on "free skill not purchasable".
    _login_as(app, creator)
    persona_create = await client.post(
        "/v1/personas",
        json={
            "name": "Paid Persona",
            "slug": "paid-persona",
            "parent_occupation_id": str(parent.id),
            "pricing_model": "one_time",
            "one_time_price_cents": 2900,
        },
    )
    assert persona_create.status_code == 201, persona_create.text
    persona_skill_id = persona_create.json()["id"]

    # Bring the persona row to ``published`` + give it a released version
    # so a buyer can theoretically purchase.
    persona_skill = await db_session.get(Skill, uuid.UUID(persona_skill_id))
    assert persona_skill is not None
    persona_skill.status = SkillStatus.PUBLISHED
    await _make_version(db_session, skill=persona_skill, version="1.0.0")
    await db_session.commit()

    # Buyer with NO occupation license — should be rejected with the 409.
    buyer = await _make_user(
        db_session, email="buyer@example.com", role=UserRole.BUYER,
    )
    await db_session.commit()
    app.dependency_overrides[current_user] = lambda: buyer
    app.dependency_overrides[current_active_user] = lambda: buyer
    app.dependency_overrides[get_optional_user] = lambda: buyer

    r = await client.post(
        "/v1/checkout/sessions",
        json={"skill_id": persona_skill_id},
    )
    assert r.status_code == 409, r.text
    body = r.json()
    assert body["error"]["code"] == "persona.requires_parent_occupation"
    # The error message must mention the parent occupation's slug.
    details = body["error"]["details"]
    assert details is not None
    assert any(
        "ai-devops-engineer" in (d.get("message") or "") for d in details
    )
