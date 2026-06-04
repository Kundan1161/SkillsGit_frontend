"""Router-level tests for the occupations module.

T-03 acceptance bullet: every endpoint has a router-level test covering
the happy + auth-fail + validation-fail branches.

These talk through HTTP via the ``client`` fixture from the local
``conftest.py``. The :func:`_make_creator`/``_make_skill`` helpers seed
the DB directly so we can target specific authz scenarios without
recreating the full session-cookie flow for every test.

Authentication strategy: instead of running the auth flow (which would
double-test things outside this module), we override the auth
dependencies via ``app.dependency_overrides`` for each test.
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
from src.core.db import get_db
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
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    return skill


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
    """Yield (client, app) so individual tests can flip dependency overrides
    to simulate logged-in / anonymous callers cleanly.

    Mirrors the ``client`` fixture in ``conftest.py`` but exposes the app
    so tests can assign to ``app.dependency_overrides`` mid-test.
    """
    from src.occupations.router import router as occupations_router

    test_sessionmaker = async_sessionmaker(
        bind=db_engine, expire_on_commit=False, autoflush=False,
        class_=AsyncSession,
    )
    monkeypatch.setattr(core_db, "engine", db_engine)
    monkeypatch.setattr(core_db, "SessionLocal", test_sessionmaker)

    from src.main import create_app

    app = create_app()
    app.include_router(occupations_router)

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


# ── POST /v1/occupations ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_happy_path(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)

    r = await client.post(
        "/v1/occupations",
        json={
            "name": "AI DevOps Engineer",
            "slug": "ai-devops-engineer",
            "summary_md": "Playbook.",
            "domains": ["ci-cd", "observability"],
            "tags": ["devops"],
            "pricing_model": "free",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["slug"] == "ai-devops-engineer"
    assert body["kind"] == "occupation"
    assert r.headers["Location"].startswith("/v1/occupations/")


@pytest.mark.asyncio
async def test_create_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "X", "slug": "x",
            "domains": ["x"],
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
        "/v1/occupations",
        json={
            "name": "X", "slug": "x",
            "domains": ["x"],
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
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)

    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Bad",
            "slug": "Bad Slug With Spaces",
            "domains": ["x"],
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
    unverified = await _make_user(
        db_session,
        email="anon@example.com",
        handle="anon",
        role=UserRole.CREATOR,
        is_creator_verified=False,
    )
    await db_session.commit()
    _login_as(app, unverified)

    r = await client.post(
        "/v1/occupations",
        json={
            "name": "X", "slug": "x",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    assert r.status_code == 403, r.text
    assert r.json()["error"]["code"] == "occupation.creator_not_verified"


# ── PATCH /v1/occupations/{id} ────────────────────────────────────────


@pytest.mark.asyncio
async def test_patch_happy_path(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)

    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Initial",
            "slug": "patchme",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]

    r2 = await client.patch(
        f"/v1/occupations/{skill_id}",
        json={"name": "Renamed", "domains": ["x", "y"]},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["name"] == "Renamed"
    assert r2.json()["domains"] == ["x", "y"]


@pytest.mark.asyncio
async def test_patch_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.patch(
        f"/v1/occupations/{uuid.uuid4()}", json={"name": "X"}
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_patch_rejects_non_owner_404(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
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
        "/v1/occupations",
        json={
            "name": "Owned", "slug": "owned",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]

    _login_as(app, intruder)
    r2 = await client.patch(
        f"/v1/occupations/{skill_id}", json={"name": "Hacked"}
    )
    assert r2.status_code == 404, r2.text
    assert r2.json()["error"]["code"] == "occupation.not_found"


@pytest.mark.asyncio
async def test_patch_validation_fail_bad_domain(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "X", "slug": "x",
            "domains": ["ci-cd"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    r2 = await client.patch(
        f"/v1/occupations/{skill_id}",
        json={"domains": ["Invalid With Spaces"]},
    )
    assert r2.status_code == 422


# ── Membership endpoints ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_bulk_set_members_happy(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    s1 = await _make_skill(db_session, creator=creator, slug="s1")
    s2 = await _make_skill(db_session, creator=creator, slug="s2")
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Occ", "slug": "occ",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]

    r2 = await client.post(
        f"/v1/occupations/{skill_id}/skills",
        json={
            "items": [
                {"member_skill_id": str(s1.id), "domain": "x"},
                {"member_skill_id": str(s2.id), "domain": "x", "sort_order": 1},
            ]
        },
    )
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert {m["member_slug"] for m in body["items"]} == {"s1", "s2"}


@pytest.mark.asyncio
async def test_bulk_set_rejects_invalid_member_kind(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    persona = await _make_skill(
        db_session, creator=creator, slug="some-persona",
        kind=SkillKind.PERSONA,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Occ", "slug": "occ",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    r2 = await client.post(
        f"/v1/occupations/{skill_id}/skills",
        json={"items": [{"member_skill_id": str(persona.id), "domain": "x"}]},
    )
    assert r2.status_code == 422, r2.text
    assert r2.json()["error"]["code"] == "occupation.invalid_member_kind"


@pytest.mark.asyncio
async def test_bulk_set_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.post(
        f"/v1/occupations/{uuid.uuid4()}/skills", json={"items": []}
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_upsert_member_happy(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    member = await _make_skill(db_session, creator=creator, slug="m")
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Occ", "slug": "occ",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    r2 = await client.post(
        f"/v1/occupations/{skill_id}/skills/{member.id}",
        json={"domain": "x", "role": "core"},
    )
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert body["member_skill_id"] == str(member.id)
    assert body["role"] == "core"


@pytest.mark.asyncio
async def test_upsert_member_unknown_domain_422(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    member = await _make_skill(db_session, creator=creator, slug="m")
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Occ", "slug": "occ",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    r2 = await client.post(
        f"/v1/occupations/{skill_id}/skills/{member.id}",
        json={"domain": "not-declared"},
    )
    assert r2.status_code == 422, r2.text
    assert r2.json()["error"]["code"] == "occupation.domain_unknown"


@pytest.mark.asyncio
async def test_upsert_member_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.post(
        f"/v1/occupations/{uuid.uuid4()}/skills/{uuid.uuid4()}", json={}
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_delete_member_happy(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    member = await _make_skill(db_session, creator=creator, slug="m")
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Occ", "slug": "occ",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    await client.post(
        f"/v1/occupations/{skill_id}/skills/{member.id}",
        json={"domain": "x"},
    )

    r2 = await client.delete(
        f"/v1/occupations/{skill_id}/skills/{member.id}"
    )
    assert r2.status_code == 204, r2.text


@pytest.mark.asyncio
async def test_delete_member_missing_404(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Occ", "slug": "occ",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    r2 = await client.delete(
        f"/v1/occupations/{skill_id}/skills/{uuid.uuid4()}"
    )
    assert r2.status_code == 404, r2.text


@pytest.mark.asyncio
async def test_delete_member_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.delete(
        f"/v1/occupations/{uuid.uuid4()}/skills/{uuid.uuid4()}"
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_reorder_members_happy(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    s1 = await _make_skill(db_session, creator=creator, slug="s1")
    s2 = await _make_skill(db_session, creator=creator, slug="s2")
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Occ", "slug": "occ",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    await client.post(
        f"/v1/occupations/{skill_id}/skills",
        json={
            "items": [
                {"member_skill_id": str(s1.id), "domain": "x", "sort_order": 0},
                {"member_skill_id": str(s2.id), "domain": "x", "sort_order": 1},
            ]
        },
    )
    r2 = await client.patch(
        f"/v1/occupations/{skill_id}/skills/order",
        json={
            "items": [
                {"member_skill_id": str(s2.id), "sort_order": 0},
                {"member_skill_id": str(s1.id), "sort_order": 1},
            ]
        },
    )
    assert r2.status_code == 200, r2.text
    by_slug = {m["member_slug"]: m for m in r2.json()["items"]}
    assert by_slug["s2"]["sort_order"] == 0
    assert by_slug["s1"]["sort_order"] == 1


@pytest.mark.asyncio
async def test_reorder_members_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.patch(
        f"/v1/occupations/{uuid.uuid4()}/skills/order",
        json={"items": []},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_reorder_validation_rejects_extra_keys(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Occ", "slug": "occ",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    r2 = await client.patch(
        f"/v1/occupations/{skill_id}/skills/order",
        json={
            "items": [
                {
                    "member_skill_id": str(uuid.uuid4()),
                    "sort_order": 0,
                    "junk": "no",
                }
            ]
        },
    )
    assert r2.status_code == 422, r2.text


# ── Build / publish ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_build_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.post(
        f"/v1/occupations/{uuid.uuid4()}/build",
        json={"version": "1.0.0"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_build_rejects_empty_membership(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Empty", "slug": "empty",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    # Seed a version row so the trigger validator gets past version lookup.
    parent = await db_session.get(Skill, uuid.UUID(skill_id))
    assert parent is not None
    await _make_version(db_session, skill=parent, version="1.0.0", released=False)
    await db_session.commit()

    r2 = await client.post(
        f"/v1/occupations/{skill_id}/build",
        json={"version": "1.0.0"},
    )
    assert r2.status_code == 422, r2.text
    assert r2.json()["error"]["code"] == "occupation.empty_membership"


@pytest.mark.asyncio
async def test_build_validation_fail_bad_version(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "X", "slug": "x",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    r2 = await client.post(
        f"/v1/occupations/{skill_id}/build",
        json={"version": "not-a-semver"},
    )
    assert r2.status_code == 422


@pytest.mark.asyncio
async def test_publish_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.post(
        f"/v1/occupations/{uuid.uuid4()}/publish",
        json={"version": "1.0.0"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_publish_happy_path(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    member = await _make_skill(db_session, creator=creator, slug="m")
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Occ", "slug": "occ",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    parent = await db_session.get(Skill, uuid.UUID(skill_id))
    assert parent is not None
    await _make_version(db_session, skill=parent, version="1.0.0", released=False)
    await db_session.commit()

    await client.post(
        f"/v1/occupations/{skill_id}/skills/{member.id}",
        json={"domain": "x"},
    )
    r2 = await client.post(
        f"/v1/occupations/{skill_id}/publish",
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
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Pub", "slug": "pub",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    # Force published status via DB.
    skill = await db_session.get(Skill, uuid.UUID(r.json()["id"]))
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.commit()
    # Another draft.
    await client.post(
        "/v1/occupations",
        json={
            "name": "Draft", "slug": "draft",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )

    _logout(app)
    r2 = await client.get("/v1/occupations")
    assert r2.status_code == 200, r2.text
    slugs = [it["slug"] for it in r2.json()["items"]]
    assert "pub" in slugs
    assert "draft" not in slugs


@pytest.mark.asyncio
async def test_list_validation_rejects_bad_limit(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.get("/v1/occupations?limit=9999")
    # FastAPI Query(le=100) → 422
    assert r.status_code == 422


# ── Public detail ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_by_handle_published(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "Detail", "slug": "detail-slug",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill = await db_session.get(Skill, uuid.UUID(r.json()["id"]))
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.commit()

    _logout(app)
    r2 = await client.get("/v1/occupations/janedoe/detail-slug")
    assert r2.status_code == 200, r2.text
    assert r2.json()["slug"] == "detail-slug"


@pytest.mark.asyncio
async def test_get_by_handle_404_for_unknown(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.get("/v1/occupations/janedoe/nope")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_by_id_404_for_random(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.get(f"/v1/occupations/{uuid.uuid4()}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_by_id_validation_rejects_bad_uuid(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    # Note: "{handle}/{slug}" route catches multi-segment paths first;
    # a non-uuid single segment goes to the by-id route which rejects.
    r = await client.get("/v1/occupations/not-a-uuid-or-handleslug")
    # FastAPI parses path param as UUID → 422.
    assert r.status_code == 422


# ── Graph preview ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_graph_preview_404_for_random(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, _app = auth_client
    r = await client.get(f"/v1/occupations/{uuid.uuid4()}/graph-preview")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_graph_preview_happy_empty_membership(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "G", "slug": "g",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill = await db_session.get(Skill, uuid.UUID(r.json()["id"]))
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.commit()

    _logout(app)
    r2 = await client.get(f"/v1/occupations/{skill.id}/graph-preview")
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert body["occupation_slug"] == "g"
    assert body["nodes"] == []
    assert body["edges"] == []
    assert body["truncated"] is False
    assert body["node_cap"] == 200


@pytest.mark.asyncio
async def test_graph_preview_with_members(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession
) -> None:
    """Members appear as nodes; missing storage just yields no edges."""
    client, app = auth_client
    creator = await _make_user(
        db_session,
        email="jane@example.com",
        handle="janedoe",
        role=UserRole.CREATOR,
        is_creator_verified=True,
    )
    s1 = await _make_skill(db_session, creator=creator, slug="m1")
    s2 = await _make_skill(db_session, creator=creator, slug="m2")
    await db_session.commit()

    _login_as(app, creator)
    r = await client.post(
        "/v1/occupations",
        json={
            "name": "G", "slug": "g",
            "domains": ["x"],
            "pricing_model": "free",
        },
    )
    skill_id = r.json()["id"]
    skill = await db_session.get(Skill, uuid.UUID(skill_id))
    assert skill is not None
    skill.status = SkillStatus.PUBLISHED
    await db_session.commit()

    await client.post(
        f"/v1/occupations/{skill_id}/skills",
        json={
            "items": [
                {"member_skill_id": str(s1.id), "domain": "x"},
                {"member_skill_id": str(s2.id), "domain": "x"},
            ]
        },
    )

    _logout(app)
    r2 = await client.get(f"/v1/occupations/{skill_id}/graph-preview")
    assert r2.status_code == 200, r2.text
    body = r2.json()
    ids = {n["id"] for n in body["nodes"]}
    assert ids == {"m1", "m2"}
