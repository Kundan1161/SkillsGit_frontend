"""Liveness probe smoke test."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_healthz(client: AsyncClient) -> None:
    r = await client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "commit" in body
    # Trace id is set by middleware.
    assert "x-trace-id" in {k.lower() for k in r.headers}
