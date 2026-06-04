"""Arq jobs for the vault builder.

Two MVP jobs:

* :func:`build_occupation_job` — wraps :func:`src.vault.builder.build_occupation`
  with persistence + structured logging.
* :func:`build_persona_job` — same for :func:`src.vault.builder.build_persona`.

The façade :func:`enqueue_occupation_build` / :func:`enqueue_persona_build`
is what service code calls. It dispatches to Arq when a real Redis
client is reachable; in CI / tests (``ENV=test``) we run the builder
in-process so the unit tests don't need a worker.

The composer (T-07) will share this module's worker process via
:class:`WorkerSettings`.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Any, ClassVar
from urllib.parse import urlparse

from arq import create_pool
from arq.connections import RedisSettings

from src.core.config import settings
from src.core.db import SessionLocal
from src.vault import builder

log = logging.getLogger(__name__)


# ── Façade return shape ──────────────────────────────────────────────


@dataclass
class EnqueueResult:
    """Outcome handed back to the service layer.

    ``job_id`` is the Arq-side identifier (or a synth in test mode).
    ``build_id`` is the :class:`~src.vault.models.VaultBuild` row id when
    the build ran in-process; ``None`` when the job was queued for the
    worker and has not yet executed.
    """

    job_id: str
    build_id: uuid.UUID | None
    status: str  # "queued" | "succeeded"


# ── Arq job entry-points ────────────────────────────────────────────


async def build_occupation_job(
    _ctx: dict[str, Any],
    occupation_skill_id: str,
    version: str,
    *,
    force_rebuild: bool = False,
) -> dict[str, Any]:
    """Run an occupation build in a fresh DB session.

    Returns a structured dict for worker logs; raises on failure so Arq's
    retry policy kicks in (capped by :attr:`WorkerSettings.max_tries`).
    """
    skill_uuid = uuid.UUID(occupation_skill_id)
    async with SessionLocal() as db:
        try:
            build = await builder.build_occupation(
                db,
                skill_uuid,
                version,
                force_rebuild=force_rebuild,
            )
            await db.commit()
            return {
                "ok": True,
                "build_id": str(build.id),
                "skill_id": occupation_skill_id,
                "version": version,
                "content_hash": build.content_hash,
                "total_bytes": build.total_bytes,
                "file_count": build.file_count,
            }
        except builder.VaultBuildError as exc:
            await db.rollback()
            log.error(
                "vault.build_occupation.failed",
                extra={
                    "skill_id": occupation_skill_id,
                    "version": version,
                    "code": exc.code,
                    "message": exc.message,
                },
            )
            raise
        except Exception:
            await db.rollback()
            log.exception(
                "vault.build_occupation.crashed",
                extra={"skill_id": occupation_skill_id, "version": version},
            )
            raise


async def build_persona_job(
    _ctx: dict[str, Any],
    persona_skill_id: str,
    version: str,
    *,
    force_rebuild: bool = False,
) -> dict[str, Any]:
    """Run a persona build in a fresh DB session (Arq entry-point)."""
    skill_uuid = uuid.UUID(persona_skill_id)
    async with SessionLocal() as db:
        try:
            build = await builder.build_persona(
                db,
                skill_uuid,
                version,
                force_rebuild=force_rebuild,
            )
            await db.commit()
            return {
                "ok": True,
                "build_id": str(build.id),
                "skill_id": persona_skill_id,
                "version": version,
                "content_hash": build.content_hash,
                "total_bytes": build.total_bytes,
                "file_count": build.file_count,
            }
        except builder.VaultBuildError as exc:
            await db.rollback()
            log.error(
                "vault.build_persona.failed",
                extra={
                    "skill_id": persona_skill_id,
                    "version": version,
                    "code": exc.code,
                    "message": exc.message,
                },
            )
            raise
        except Exception:
            await db.rollback()
            log.exception(
                "vault.build_persona.crashed",
                extra={"skill_id": persona_skill_id, "version": version},
            )
            raise


# ── Façade for the service layer ────────────────────────────────────


# Test-mode behaviour: by default the façade returns a synthesised
# "queued" result without invoking the real builder so the existing
# occupations/personas tests (which don't seed storage) don't trip the
# builder's storage-fetch path. The vault module's own tests flip this
# flag to ``True`` (via :func:`set_inline_builds_for_tests`) to exercise
# the real in-process path.
_INLINE_BUILDS_IN_TEST: bool = False


def set_inline_builds_for_tests(value: bool) -> None:
    """Toggle whether the façade runs the builder inline under ENV=test.

    Default behaviour in test mode is to return a synthesised queued
    result so seed-light occupations/personas tests don't accidentally
    trip the builder. The vault tests turn this on so they exercise the
    real path.
    """
    global _INLINE_BUILDS_IN_TEST  # noqa: PLW0603 — test-only flag flip is intentional
    _INLINE_BUILDS_IN_TEST = value


def _run_in_process() -> bool:
    """True when we should run the builder inline (not via Arq).

    Production never runs inline. In test mode the default is False (so
    legacy module tests keep the stub semantics they expect); vault
    tests opt in via :func:`set_inline_builds_for_tests`.
    """
    return settings.is_test and _INLINE_BUILDS_IN_TEST


def _synth_job_id(prefix: str, skill_id: uuid.UUID, version: str) -> str:
    """Synthesise a deterministic job id with a short random suffix.

    Matches the legacy stub's shape (``<prefix>:<skill>:<version>:<8hex>``)
    so test assertions on the prefix continue to pass.
    """
    suffix = uuid.uuid4().hex[:8]
    return f"{prefix}:{skill_id}:{version}:{suffix}"


async def enqueue_occupation_build(
    session: Any,
    *,
    skill_id: uuid.UUID,
    version: str,
    force_rebuild: bool = False,
) -> EnqueueResult:
    """Service-facing helper.

    Three modes:

    * Production (``ENV!=test``): submits an Arq job and returns a
      ``queued`` result; the worker re-loads the row in a fresh session
      and runs the build there.
    * Test (default): returns a synth ``queued`` result without invoking
      the builder. Legacy occupations/personas tests rely on this so a
      seed-light test (no SkillVersion + storage upload for members)
      doesn't trip on the builder's storage-fetch path.
    * Test (inline opt-in via :func:`set_inline_builds_for_tests`): runs
      the builder on the caller's session and returns ``succeeded``. Used
      by ``src/vault/tests/`` to exercise the real path.
    """
    if _run_in_process():
        try:
            build = await builder.build_occupation(
                session, skill_id, version, force_rebuild=force_rebuild
            )
        except builder.VaultBuildError as exc:
            log.error(
                "vault.enqueue_occupation.inline_failed",
                extra={
                    "skill_id": str(skill_id),
                    "version": version,
                    "code": exc.code,
                },
            )
            raise
        return EnqueueResult(
            job_id=f"vault:build_occupation:{skill_id}:{version}:{build.id.hex[:8]}",
            build_id=build.id,
            status="succeeded",
        )

    if settings.is_test:
        # Legacy compatibility — preserve the "occupations:build:..." prefix
        # the existing tests assert on.
        return EnqueueResult(
            job_id=_synth_job_id("occupations:build", skill_id, version),
            build_id=None,
            status="queued",
        )

    job_id = f"vault:build_occupation:{skill_id}:{version}"
    pool = await create_pool(_arq_redis_settings())
    try:
        await pool.enqueue_job(
            "build_occupation_job",
            str(skill_id),
            version,
            _job_id=job_id,
            force_rebuild=force_rebuild,
        )
    finally:
        await pool.close()
    return EnqueueResult(job_id=job_id, build_id=None, status="queued")


async def enqueue_persona_build(
    session: Any,
    *,
    skill_id: uuid.UUID,
    version: str,
    force_rebuild: bool = False,
) -> EnqueueResult:
    """Service-facing helper for persona builds.

    Mirrors :func:`enqueue_occupation_build` exactly: production
    enqueues an Arq job; test-mode default returns a synth queued
    result; test-mode inline opt-in runs the builder on the caller's
    session.
    """
    if _run_in_process():
        try:
            build = await builder.build_persona(
                session, skill_id, version, force_rebuild=force_rebuild
            )
        except builder.VaultBuildError as exc:
            log.error(
                "vault.enqueue_persona.inline_failed",
                extra={
                    "skill_id": str(skill_id),
                    "version": version,
                    "code": exc.code,
                },
            )
            raise
        return EnqueueResult(
            job_id=f"vault:build_persona:{skill_id}:{version}:{build.id.hex[:8]}",
            build_id=build.id,
            status="succeeded",
        )

    if settings.is_test:
        return EnqueueResult(
            job_id=_synth_job_id("personas:build", skill_id, version),
            build_id=None,
            status="queued",
        )

    job_id = f"vault:build_persona:{skill_id}:{version}"
    pool = await create_pool(_arq_redis_settings())
    try:
        await pool.enqueue_job(
            "build_persona_job",
            str(skill_id),
            version,
            _job_id=job_id,
            force_rebuild=force_rebuild,
        )
    finally:
        await pool.close()
    return EnqueueResult(job_id=job_id, build_id=None, status="queued")


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
    """Arq worker configuration for the vault module.

    Run with::

        uv run arq src.vault.jobs.WorkerSettings

    Retry policy: a vault build is deterministic given the same inputs,
    so a failure is almost always a transient storage/network issue —
    we allow ``max_tries=3``. ``job_timeout`` is generous because a
    50 MB vault zip can take a beat on slow object stores; tune down if
    operations show we're well below.
    """

    functions: ClassVar[list[Any]] = [build_occupation_job, build_persona_job]
    max_tries: ClassVar[int] = 3
    job_timeout: ClassVar[int] = 180
    keep_result: ClassVar[int] = 3600

    @staticmethod
    def redis_settings() -> RedisSettings:
        return _arq_redis_settings()


__all__ = [
    "EnqueueResult",
    "WorkerSettings",
    "build_occupation_job",
    "build_persona_job",
    "enqueue_occupation_build",
    "enqueue_persona_build",
]
