"""Router-level tests for the capture module.

T-05 acceptance bullet: every endpoint has a router-level test covering
the happy + auth-fail + validation-fail branches. The end-to-end create
→ extract → finalize flow lands here too (acceptance bullets 1 + 3).

Auth strategy: we override the auth deps via
``app.dependency_overrides`` per test (same pattern as the sibling
``personas/tests/test_router.py``) — no need to re-test the cookie/JWT
flow inside this module.
"""

from __future__ import annotations

import io
import uuid
from collections.abc import AsyncIterator
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
from src.capture import quota, service
from src.capture.models import CaptureSession, CaptureSessionStatus
from src.core.db import get_db
from src.occupations.models import Occupation
from src.personas.models import Persona
from src.skills.models import (
    PricingModel,
    Skill,
    SkillKind,
    SkillStatus,
)
from src.storage import s3 as storage_s3
from src.users.models import CreatorProfile, User, UserRole

# ── Local seed helpers ────────────────────────────────────────────────


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


async def _make_occupation(
    session: AsyncSession,
    *,
    creator: User,
    slug: str = "ai-devops-engineer",
) -> Skill:
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=slug.replace("-", " ").title(),
        tagline=None,
        description_md=None,
        category="engineering",
        tags=["devops"],
        status=SkillStatus.PUBLISHED,
        kind=SkillKind.OCCUPATION,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    session.add(
        Occupation(
            skill_id=skill.id,
            summary_md="x",
            domains=["ci-cd"],
            persona_count=0,
            recommended_persona_count=0,
        )
    )
    await session.flush()
    return skill


async def _make_persona(
    session: AsyncSession,
    *,
    creator: User,
    parent_skill_id: uuid.UUID,
    slug: str = "jane-devops",
) -> Skill:
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=slug.replace("-", " ").title(),
        tagline=None,
        description_md=None,
        category="engineering",
        tags=["persona"],
        status=SkillStatus.DRAFT,
        kind=SkillKind.PERSONA,
        pricing_model=PricingModel.FREE,
    )
    session.add(skill)
    await session.flush()
    session.add(
        Persona(
            skill_id=skill.id,
            parent_occupation_id=parent_skill_id,
            creator_intro_md=None,
            specialization=None,
            years_of_experience=None,
            neuron_count=0,
        )
    )
    await session.flush()
    return skill


# ── Auth-override client (matches sibling pattern) ───────────────────


@pytest_asyncio.fixture(scope="function")
async def auth_client(
    db_engine: Any,
    fake_redis: Any,
    in_memory_storage: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[tuple[AsyncClient, Any]]:
    """Yield (client, app) so tests can flip dependency overrides."""
    from src.capture.router import router as capture_router

    test_sessionmaker = async_sessionmaker(
        bind=db_engine, expire_on_commit=False, autoflush=False,
        class_=AsyncSession,
    )
    monkeypatch.setattr(core_db, "engine", db_engine)
    monkeypatch.setattr(core_db, "SessionLocal", test_sessionmaker)

    import src.auth.deps as auth_deps
    monkeypatch.setattr(auth_deps, "_redis", fake_redis)
    monkeypatch.setattr(auth_deps, "get_redis", lambda: fake_redis)
    import src.auth.router as auth_router
    monkeypatch.setattr(auth_router, "get_redis", lambda: fake_redis)

    from src.main import create_app

    app = create_app()
    app.include_router(capture_router)

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


async def _make_persona_for_creator(
    db_session: AsyncSession, creator: User,
) -> Skill:
    occ_creator = await _make_user(
        db_session, email="occ@example.com", handle="occ-creator",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    parent = await _make_occupation(db_session, creator=occ_creator)
    return await _make_persona(
        db_session, creator=creator, parent_skill_id=parent.id
    )


# ── POST /v1/capture/sessions ────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_session_happy_path(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    await db_session.commit()
    _login_as(app, creator)

    r = await client.post(
        "/v1/capture/sessions",
        json={
            "persona_id": str(persona.id),
            "title": "Flaky CI tests",
            "situation_md": "Tests broke.",
            "decision_md": "Fixed indexes.",
            "outcome_md": "Green again.",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["title"] == "Flaky CI tests"
    assert body["status"] == "draft"
    assert body["persona_id"] == str(persona.id)
    assert r.headers["Location"].startswith("/v1/capture/sessions/")


@pytest.mark.asyncio
async def test_create_session_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, _app = auth_client
    r = await client.post(
        "/v1/capture/sessions",
        json={"persona_id": str(uuid.uuid4()), "title": "X"},
    )
    assert r.status_code == 401, r.text


@pytest.mark.asyncio
async def test_create_session_rejects_buyer(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    buyer = await _make_user(
        db_session, email="buyer@example.com", role=UserRole.BUYER,
    )
    await db_session.commit()
    app.dependency_overrides[current_user] = lambda: buyer
    app.dependency_overrides[current_active_user] = lambda: buyer
    app.dependency_overrides[get_optional_user] = lambda: buyer
    r = await client.post(
        "/v1/capture/sessions",
        json={"persona_id": str(uuid.uuid4()), "title": "X"},
    )
    assert r.status_code == 403, r.text


@pytest.mark.asyncio
async def test_create_session_validation_rejects_empty_title(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/capture/sessions",
        json={"persona_id": str(uuid.uuid4()), "title": ""},
    )
    assert r.status_code == 422, r.text


# ── GET /v1/capture/sessions/{id} + list ─────────────────────────────


@pytest.mark.asyncio
async def test_get_session_happy_path(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/capture/sessions",
        json={"persona_id": str(persona.id), "title": "X"},
    )
    sid = r.json()["id"]
    r2 = await client.get(f"/v1/capture/sessions/{sid}")
    assert r2.status_code == 200, r2.text
    assert r2.json()["id"] == sid


@pytest.mark.asyncio
async def test_get_session_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, _app = auth_client
    r = await client.get(f"/v1/capture/sessions/{uuid.uuid4()}")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_session_404_for_intruder(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    intruder = await _make_user(
        db_session, email="intruder@example.com", handle="intruder",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/capture/sessions",
        json={"persona_id": str(persona.id), "title": "X"},
    )
    sid = r.json()["id"]
    _login_as(app, intruder)
    r2 = await client.get(f"/v1/capture/sessions/{sid}")
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_list_sessions_scoped_to_creator(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    await db_session.commit()
    _login_as(app, creator)
    for title in ("A", "B"):
        await client.post(
            "/v1/capture/sessions",
            json={"persona_id": str(persona.id), "title": title},
        )

    r = await client.get("/v1/capture/sessions")
    assert r.status_code == 200, r.text
    titles = sorted(it["title"] for it in r.json()["items"])
    assert titles == ["A", "B"]


@pytest.mark.asyncio
async def test_list_sessions_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, _app = auth_client
    r = await client.get("/v1/capture/sessions")
    assert r.status_code == 401


# ── PATCH /v1/capture/sessions/{id} ──────────────────────────────────


@pytest.mark.asyncio
async def test_patch_session_happy(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/capture/sessions",
        json={"persona_id": str(persona.id), "title": "X"},
    )
    sid = r.json()["id"]
    r2 = await client.patch(
        f"/v1/capture/sessions/{sid}",
        json={"title": "Y", "draft_md": "custom"},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["title"] == "Y"
    assert r2.json()["draft_md"] == "custom"


@pytest.mark.asyncio
async def test_patch_session_validation_rejects_extra_keys(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.patch(
        f"/v1/capture/sessions/{uuid.uuid4()}",
        json={"title": "Z", "bogus_extra": "no"},
    )
    assert r.status_code == 422, r.text


@pytest.mark.asyncio
async def test_patch_session_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, _app = auth_client
    r = await client.patch(
        f"/v1/capture/sessions/{uuid.uuid4()}",
        json={"title": "X"},
    )
    assert r.status_code == 401


# ── POST /v1/capture/sessions/{id}/extract ───────────────────────────


@pytest.mark.asyncio
async def test_extract_populates_draft_within_30s_via_stub(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    """T-05 acceptance bullet 1 — POST + extract + draft_md populated."""
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/capture/sessions",
        json={
            "persona_id": str(persona.id),
            "title": "Flaky CI tests",
            "situation_md": "Tests broke after Redis upgrade.",
            "decision_md": "Per-suite DB indexes.",
            "outcome_md": "Pass rate recovered.",
        },
    )
    sid = r.json()["id"]
    r2 = await client.post(f"/v1/capture/sessions/{sid}/extract")
    assert r2.status_code == 202, r2.text
    # Sync stub path → status is 'completed' immediately.
    body = r2.json()
    assert body["status"] in ("completed", "queued")
    # Polling the session reveals the populated draft.
    r3 = await client.get(f"/v1/capture/sessions/{sid}")
    assert r3.status_code == 200, r3.text
    body3 = r3.json()
    assert body3["status"] == "draft_ready"
    assert body3["draft_md"] is not None
    assert "memory_neuron" in body3["draft_md"]


@pytest.mark.asyncio
async def test_extract_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, _app = auth_client
    r = await client.post(f"/v1/capture/sessions/{uuid.uuid4()}/extract")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_extract_404_for_unknown_session(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(f"/v1/capture/sessions/{uuid.uuid4()}/extract")
    assert r.status_code == 404, r.text


# ── 11th extract → 429 (T-05 acceptance bullet 4) ────────────────────


@pytest.mark.asyncio
async def test_eleventh_extract_returns_429_with_quota_exceeded(
    auth_client: tuple[AsyncClient, Any],
    db_session: AsyncSession,
    fake_redis: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, app = auth_client
    # The conftest patches auth_deps.get_redis to point at fake_redis,
    # but the quota module calls get_redis() at call-time on each
    # reserve()/peek() — so once we ensure both binds are in place,
    # the same fake-redis instance is used.
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    await db_session.commit()
    _login_as(app, creator)

    sid_resp = await client.post(
        "/v1/capture/sessions",
        json={
            "persona_id": str(persona.id),
            "title": "Q",
            "situation_md": "a",
            "decision_md": "b",
            "outcome_md": "c",
        },
    )
    sid = sid_resp.json()["id"]
    # Burn 10 extracts.
    for i in range(10):
        r = await client.post(f"/v1/capture/sessions/{sid}/extract")
        assert r.status_code == 202, f"call {i}: {r.text}"
    # 11th → 429 capture.quota_exceeded.
    r11 = await client.post(f"/v1/capture/sessions/{sid}/extract")
    assert r11.status_code == 429, r11.text
    body = r11.json()
    assert body["error"]["code"] == "capture.quota_exceeded"


# ── POST /v1/capture/sessions/{id}/finalize ──────────────────────────


@pytest.mark.asyncio
async def test_finalize_creates_neuron_end_to_end(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    """T-05 acceptance bullet 3 — atomic skills+version+join in one tx."""
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/capture/sessions",
        json={
            "persona_id": str(persona.id),
            "title": "Flaky CI",
            "situation_md": "tests broke.",
            "decision_md": "fixed indexes.",
            "outcome_md": "green again.",
        },
    )
    sid = r.json()["id"]
    await client.post(f"/v1/capture/sessions/{sid}/extract")

    r_fin = await client.post(
        f"/v1/capture/sessions/{sid}/finalize",
        json={"neuron_slug": "flaky-ci-e2e", "neuron_version": "1.0.0"},
    )
    assert r_fin.status_code == 201, r_fin.text
    body = r_fin.json()
    assert body["neuron_version"] == "1.0.0"
    assert body["persona_id"] == str(persona.id)
    assert body["vault_path_hint"].endswith("flaky-ci-e2e.md")


@pytest.mark.asyncio
async def test_finalize_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, _app = auth_client
    r = await client.post(
        f"/v1/capture/sessions/{uuid.uuid4()}/finalize",
        json={"neuron_slug": "x"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_finalize_validation_rejects_bad_slug(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        f"/v1/capture/sessions/{uuid.uuid4()}/finalize",
        json={"neuron_slug": "Bad Slug With Spaces"},
    )
    assert r.status_code == 422, r.text


@pytest.mark.asyncio
async def test_finalize_409_when_draft_empty(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/capture/sessions",
        json={"persona_id": str(persona.id), "title": "X"},
    )
    sid = r.json()["id"]
    r2 = await client.post(
        f"/v1/capture/sessions/{sid}/finalize",
        json={"neuron_slug": "no-draft"},
    )
    assert r2.status_code == 409, r2.text
    assert r2.json()["error"]["code"] == "capture.draft_not_ready"


@pytest.mark.asyncio
async def test_finalize_422_when_pii_hardblock(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    """A hard-block secret in the draft rejects with capture.pii_blocked."""
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/capture/sessions",
        json={"persona_id": str(persona.id), "title": "X",
              "situation_md": "a", "decision_md": "b", "outcome_md": "c"},
    )
    sid = r.json()["id"]
    await client.post(f"/v1/capture/sessions/{sid}/extract")

    # Inject a credit card directly into the draft via PATCH.
    fetched = await client.get(f"/v1/capture/sessions/{sid}")
    draft = fetched.json()["draft_md"]
    poisoned = draft + "\n\nCard: 4111111111111111\n"
    await client.patch(
        f"/v1/capture/sessions/{sid}",
        json={"draft_md": poisoned},
    )

    r_fin = await client.post(
        f"/v1/capture/sessions/{sid}/finalize",
        json={"neuron_slug": "poisoned-draft"},
    )
    assert r_fin.status_code == 422, r_fin.text
    assert r_fin.json()["error"]["code"] == "capture.pii_blocked"


# ── POST /v1/capture/sessions/{id}/abandon ───────────────────────────


@pytest.mark.asyncio
async def test_abandon_marks_status(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/capture/sessions",
        json={"persona_id": str(persona.id), "title": "X"},
    )
    sid = r.json()["id"]
    r2 = await client.post(
        f"/v1/capture/sessions/{sid}/abandon",
        json={"reason": "changed mind"},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["status"] == "abandoned"
    assert r2.json()["abandoned_at"] is not None


@pytest.mark.asyncio
async def test_abandon_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, _app = auth_client
    r = await client.post(
        f"/v1/capture/sessions/{uuid.uuid4()}/abandon",
        json={"reason": None},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_abandon_validation_rejects_extra_keys(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        f"/v1/capture/sessions/{uuid.uuid4()}/abandon",
        json={"reason": "X", "bogus": "no"},
    )
    assert r.status_code == 422, r.text


# ── Attachments ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_attachment_upload_then_delete(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    persona = await _make_persona_for_creator(db_session, creator)
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(
        "/v1/capture/sessions",
        json={"persona_id": str(persona.id), "title": "X"},
    )
    sid = r.json()["id"]
    files = {"file": ("shot.png", io.BytesIO(b"pngbytes"), "image/png")}
    r2 = await client.post(
        f"/v1/capture/sessions/{sid}/attachments", files=files,
    )
    assert r2.status_code == 201, r2.text
    aid = r2.json()["id"]
    assert r2.json()["filename"] == "shot.png"

    r3 = await client.delete(
        f"/v1/capture/sessions/{sid}/attachments/{aid}",
    )
    assert r3.status_code == 204


@pytest.mark.asyncio
async def test_attachment_upload_requires_auth(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, _app = auth_client
    files = {"file": ("a.png", io.BytesIO(b"x"), "image/png")}
    r = await client.post(
        f"/v1/capture/sessions/{uuid.uuid4()}/attachments", files=files,
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_attachment_upload_validation_rejects_no_file(
    auth_client: tuple[AsyncClient, Any], db_session: AsyncSession,
) -> None:
    client, app = auth_client
    creator = await _make_user(
        db_session, email="jane@example.com", handle="janedoe",
        role=UserRole.CREATOR, is_creator_verified=True,
    )
    await db_session.commit()
    _login_as(app, creator)
    r = await client.post(f"/v1/capture/sessions/{uuid.uuid4()}/attachments")
    assert r.status_code == 422, r.text


# Silence linter on imports kept for parity with sibling modules.
_ = (CaptureSession, CaptureSessionStatus, storage_s3, service, quota)
