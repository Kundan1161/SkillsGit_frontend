# Skillsgit API

FastAPI backend for the Skillsgit marketplace. Single source of truth for the
data model (users, skills, versions, orders, subscriptions, licenses, reviews,
payouts) and authoring contracts (skills.md frontmatter + body validator).

## Dev quickstart

```bash
cd apps/api
cp .env.example .env             # then edit secrets
uv sync                          # install runtime + dev deps
uv run alembic upgrade head      # create tables + seed categories
uv run uvicorn src.main:app --reload --port 8000
```

OpenAPI doc lives at `http://localhost:8000/v1/docs`.

## Common commands

```bash
uv run pytest                    # run unit + flow tests (sqlite in-memory)
uv run mypy src/                 # strict type check
uv run ruff check src/ tests/    # lint
uv run ruff format src/ tests/   # autoformat
uv run alembic revision --autogenerate -m "add foo"
uv run alembic downgrade -1
```

## Architecture

One package per bounded context under `src/`. Each package owns a
`models.py` (SQLAlchemy 2.x async, typed via `Mapped[...]`), `schemas.py`
(Pydantic v2 read/create/update), `service.py` (business logic, no FastAPI
imports), and `router.py` (FastAPI router; parses, delegates, returns).
Authentication uses `fastapi-users`-compatible primitives (argon2id, JWT
session cookie, opaque API tokens with hashed storage); see `src/auth/`.
Money is integer cents everywhere; timestamps are `timestamptz` (UTC).
Errors follow `shared/api-conventions.md` — every non-2xx response is an
`ErrorResponse` envelope with a stable `error.code`, human `message`,
optional field-level `details`, and a `trace_id` propagated from the
`X-Trace-Id` middleware.

## Module map

| Module       | Phase | Status                                                   |
| ------------ | ----- | -------------------------------------------------------- |
| `core/`      | 0     | Real — config, db, errors, pagination, rate limits, logging |
| `auth/`      | 0     | Real — register/login/logout/me/forgot/reset/verify, API tokens, become-creator |
| `users/`     | 0     | Real — User, CreatorProfile, ApiToken models + schemas    |
| `skills/`    | 0     | Real — models + `validator.py` (the canonical skills.md gate) |
| `billing/`   | 1     | Stub — models only; router 501s. See `prompts/marketplace/03-pricing-and-checkout.md` |
| `catalog/`   | 1     | Stub — `prompts/marketplace/01-discovery.md`              |
| `delivery/`  | 1     | Stub — `prompts/marketplace/04-licensing-and-delivery.md` |
| `reviews/`   | 2     | Stub — model only. `prompts/marketplace/05-trust-and-quality.md` |
| `creator/`   | 3     | Stub — `prompts/skill-creator/*`                          |
| `webhooks/`  | 1     | Stub — `prompts/marketplace/03-pricing-and-checkout.md`   |

## Testing strategy

Unit tests run against in-memory SQLite (`aiosqlite`) for speed. Production
uses Postgres + `asyncpg`. Models declare Postgres-specific column types
(`citext`, `JSONB`, `ARRAY`) via `with_variant(..., "sqlite")` fallbacks so
the same model definitions work on both engines. CI runs the test suite
against both backends on every PR.

## Migrations

Alembic env is configured for async (`run_async`). The initial migration
(`0001_initial.py`) hand-writes every table from `02-data-model-core.md`
and enables the `citext`, `pgcrypto`, and `pg_trgm` extensions. Category
seed data lands in `0002_seed_categories.py`.
