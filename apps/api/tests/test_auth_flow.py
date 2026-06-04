"""Register / login / /me / logout flow."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_then_login_me_logout(client: AsyncClient) -> None:
    payload = {
        "email": "jane@example.com",
        "password": "correct horse battery staple",
        "display_name": "Jane Doe",
    }
    r = await client.post("/v1/auth/register", json=payload)
    assert r.status_code == 201, r.text
    user = r.json()
    assert user["email"] == "jane@example.com"
    assert user["role"] == "buyer"
    assert user["is_verified"] is False

    # /me works because register set the cookie.
    r = await client.get("/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == "jane@example.com"

    # Logout clears the cookie.
    r = await client.post("/v1/auth/logout")
    assert r.status_code == 204

    # /me after logout is 401.
    r = await client.get("/v1/auth/me")
    assert r.status_code == 401

    # Login again with the credentials.
    r = await client.post(
        "/v1/auth/login",
        json={"email": "jane@example.com", "password": "correct horse battery staple"},
    )
    assert r.status_code == 200, r.text

    r = await client.get("/v1/auth/me")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client: AsyncClient) -> None:
    payload = {
        "email": "dup@example.com",
        "password": "correct horse battery staple",
    }
    r = await client.post("/v1/auth/register", json=payload)
    assert r.status_code == 201

    r = await client.post("/v1/auth/register", json=payload)
    assert r.status_code == 409
    body = r.json()
    assert body["error"]["code"] == "auth.email_taken"


@pytest.mark.asyncio
async def test_login_bad_credentials_returns_401(client: AsyncClient) -> None:
    # Pre-register.
    await client.post(
        "/v1/auth/register",
        json={"email": "bob@example.com", "password": "correct horse battery staple"},
    )
    await client.post("/v1/auth/logout")

    r = await client.post(
        "/v1/auth/login",
        json={"email": "bob@example.com", "password": "WRONG password 1234"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.invalid_credentials"


@pytest.mark.asyncio
async def test_register_weak_password_rejected(client: AsyncClient) -> None:
    r = await client.post(
        "/v1/auth/register",
        json={"email": "weak@example.com", "password": "short"},
    )
    # Pydantic min_length triggers a 422 here.
    assert r.status_code in (400, 422)
