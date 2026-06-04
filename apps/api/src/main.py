"""FastAPI application entrypoint.

Mounts all module routers under ``/v1/<module>``; installs global exception
handlers and middleware (CORS, trace id, rate limiting).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.billing.router import router as billing_router
from src.capture.router import router as capture_router
from src.catalog.router import router as catalog_router
from src.catalog.skill_detail_router import router as skill_detail_router
from src.core.config import settings
from src.core.errors import install_exception_handlers
from src.core.logging import TraceIdMiddleware, configure_logging
from src.core.rate_limits import RateLimitExceeded, limiter, rate_limit_exceeded_handler
from src.creator.router import router as creator_router
from src.delivery.router import router as delivery_router
from src.occupations.router import router as occupations_router
from src.personas.router import router as personas_router
from src.vault.router import router as vault_router
from src.reviews.router import router as reviews_router
from src.admin.router import router as admin_router
from src.skills.router import (
    creator_skills_router,
    router as skills_router,
)
from src.users.router import creators_router, router as users_router
from src.webhooks.router import router as webhooks_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Skillsgit API",
        version="0.1.0",
        openapi_url="/v1/openapi.json",
        docs_url="/v1/docs",
        redoc_url="/v1/redoc",
        lifespan=lifespan,
    )

    # ── Middleware (order matters; outermost first) ──────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Trace-Id"],
    )
    app.add_middleware(TraceIdMiddleware)

    # ── Rate limiting ────────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # ── Global exception handlers ────────────────────────────────────
    install_exception_handlers(app)

    # ── Routers ──────────────────────────────────────────────────────
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(creators_router)
    app.include_router(skills_router)
    app.include_router(creator_skills_router)
    app.include_router(admin_router)
    app.include_router(skill_detail_router)
    app.include_router(catalog_router)
    app.include_router(billing_router)
    app.include_router(delivery_router)
    app.include_router(reviews_router)
    app.include_router(creator_router)
    app.include_router(webhooks_router)
    # ── Wave-2 modules ───────────────────────────────────────────────
    app.include_router(occupations_router)
    app.include_router(personas_router)
    app.include_router(capture_router)
    # ── Wave-3 modules ───────────────────────────────────────────────
    app.include_router(vault_router)

    # ── Health ────────────────────────────────────────────────────────
    @app.get("/healthz", tags=["meta"], summary="Liveness probe")
    async def healthz() -> dict[str, str]:
        return {"status": "ok", "commit": settings.GIT_COMMIT}

    return app


app = create_app()
