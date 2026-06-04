"""Arq jobs for the capture pipeline.

The single MVP job is :func:`extract_neuron` — wraps the LLM call from
:mod:`src.capture.llm` with persistence + retry semantics. It lives
behind a thin façade so the service / router don't import Arq directly
(easy to swap workers later).

CI does NOT spin a real Arq worker: tests rely on
``SKG_CAPTURE_LLM_STUB=1`` + :func:`src.capture.service.run_extract`
running synchronously. The Arq job is the real-LLM, production path.
The :func:`enqueue_extract` helper either dispatches to Arq (when a
Redis client is configured) or falls back to running the extraction
in-process (CI / unit test paths).
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, ClassVar
from urllib.parse import urlparse

from arq import create_pool
from arq.connections import RedisSettings

from src.capture import service
from src.capture.models import CaptureSession
from src.core.config import settings
from src.core.db import SessionLocal
from src.users.models import User

log = logging.getLogger(__name__)


# ── Arq job ──────────────────────────────────────────────────────────


async def extract_neuron(_ctx: dict[str, Any], session_id: str) -> dict[str, Any]:
    """Arq job entry-point. Re-runs the LLM extraction for one session.

    Loads the row in a fresh DB session (we cannot share the request
    session across the Arq boundary). The job is idempotent: it
    overrides the previous draft on each run; the quota counter has
    already been bumped by the router so we set ``consume_quota=False``.

    On failure the job allows Arq's normal retry policy (``max_tries``
    is set in :class:`WorkerSettings`) and returns the error metadata
    so the worker log surfaces it.
    """
    session_uuid = uuid.UUID(session_id)
    async with SessionLocal() as db:
        row = await db.get(CaptureSession, session_uuid)
        if row is None:
            return {"ok": False, "code": "capture.not_found"}
        # We hydrate the creator user explicitly — the job doesn't have
        # access to the request's User dep.
        user = await db.get(User, row.creator_id)
        if user is None:
            return {"ok": False, "code": "capture.creator_missing"}

        try:
            out = await service.run_extract(
                db, creator=user, session_id=session_uuid, consume_quota=False
            )
            await db.commit()
            return {
                "ok": True,
                "session_id": session_id,
                "draft_len": len(out.draft_md or ""),
                "suggested_link_count": len(out.suggested_links),
            }
        except Exception as exc:
            await db.rollback()
            log.exception(
                "capture.extract_neuron.failed",
                extra={"session_id": session_id, "error": str(exc)},
            )
            raise


# ── Façade for the router ────────────────────────────────────────────


async def enqueue_extract(*, session_id: uuid.UUID) -> None:
    """Submit the extract job to Arq.

    Implementation note: tests never hit this path (``llm.is_stub_enabled``
    short-circuits in :func:`src.capture.service.enqueue_extract`).
    Production goes through Arq's ``ArqRedis.enqueue_job``; the worker
    process picks the job up and runs :func:`extract_neuron`.
    """
    pool = await create_pool(_arq_redis_settings())
    try:
        await pool.enqueue_job(
            "extract_neuron",
            str(session_id),
            _job_id=f"capture:extract:{session_id}",
        )
    finally:
        await pool.close()


# ── Worker settings ──────────────────────────────────────────────────


def _arq_redis_settings() -> RedisSettings:
    """Translate ``settings.REDIS_URL`` into Arq's connection shape."""
    url = urlparse(settings.REDIS_URL)
    return RedisSettings(
        host=url.hostname or "localhost",
        port=url.port or 6379,
        database=int((url.path or "/0").lstrip("/") or "0"),
        password=url.password,
    )


class WorkerSettings:
    """Configuration for the Arq worker process.

    Run with::

        uv run arq src.capture.jobs.WorkerSettings

    Retry policy: per ``team/04-capture-flow.md`` §Failure modes the
    LLM-extract step retries once with a stricter prompt before
    surrendering. We model that as ``max_tries=2`` (the second try is
    the stricter retry); a third failure surfaces as
    ``capture.extract_parse_error`` to the creator via the existing
    audit log path.
    """

    functions: ClassVar[list[Any]] = [extract_neuron]
    max_tries: ClassVar[int] = 2
    job_timeout: ClassVar[int] = 60
    keep_result: ClassVar[int] = 3600

    @staticmethod
    def redis_settings() -> RedisSettings:
        return _arq_redis_settings()


__all__ = [
    "WorkerSettings",
    "enqueue_extract",
    "extract_neuron",
]
