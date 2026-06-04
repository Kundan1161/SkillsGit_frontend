# 01 — Tech Stack & Repo Layout

**Phase:** 0 (shared context)
**Depends on:** `00-vision.md`
**Parallel-safe with:** all
**Status:** ready

> Every agent must respect these decisions. If a decision is wrong, raise it explicitly — do not silently substitute.

---

## Stack

### Backend
- **Language:** Python 3.12+
- **Framework:** FastAPI (async)
- **ORM:** SQLAlchemy 2.x (async, typed)
- **Migrations:** Alembic
- **Schemas:** Pydantic v2 (request/response models, no separate DTO layer)
- **Auth:** FastAPI Users + JWT (httpOnly cookie for web, bearer token for API)
- **Background jobs:** Arq (Redis-backed) for billing webhooks, email, search indexing
- **Search:** Postgres full-text + `pg_trgm` for v1; reassess Meilisearch when listings > 5k
- **Storage:** S3-compatible (Cloudflare R2 in production) for skills.md files and screenshots
- **Payments:** Stripe (Stripe Connect Express for creator payouts, Stripe Billing for subscriptions)

### Frontend
- **Framework:** Next.js 15 (App Router, RSC where it pays off)
- **Language:** TypeScript (`"strict": true`)
- **Styling:** Tailwind CSS v4 + shadcn/ui
- **State:** React Server Components for data, TanStack Query for client mutations, Zustand for builder-canvas state
- **Forms:** React Hook Form + Zod
- **Visual builder:** React Flow (xyflow) for the node canvas (skill-creator only)
- **Markdown:** `unified` + `remark` + `remark-frontmatter` for parsing/rendering skills.md previews

### Data
- **Primary DB:** Postgres 16
- **Cache / queue broker:** Redis 7
- **Object store:** S3-compatible (R2)

### Infra (target)
- **Local dev:** Docker Compose (postgres, redis, minio, mailhog)
- **Production:** containerized — backend on Fly.io or Railway, frontend on Vercel, Postgres on Neon, Redis on Upstash. Don't bake in cloud-specific bindings; the deploy target is replaceable.

### Tooling
- **Python:** `uv` for env management, `ruff` for lint+format, `mypy --strict` for types, `pytest` + `pytest-asyncio` + `httpx` for tests
- **TS:** `pnpm`, `eslint` (next config), `prettier`, `vitest` for unit, `playwright` for E2E
- **Pre-commit:** `pre-commit` runs ruff, mypy, eslint, prettier on staged files

---

## Monorepo layout

```
skillsgit/
├── apps/
│   ├── api/                      FastAPI backend (the single source of truth)
│   │   ├── src/
│   │   │   ├── auth/
│   │   │   ├── billing/          Stripe Connect, subscriptions, payouts
│   │   │   ├── catalog/          listings, search, categories
│   │   │   ├── delivery/         license issuance, download URLs
│   │   │   ├── reviews/
│   │   │   ├── skills/           Skill, SkillVersion CRUD + skills.md validation
│   │   │   ├── creator/          builder persistence, import pipelines
│   │   │   ├── users/
│   │   │   ├── webhooks/         Stripe webhooks
│   │   │   ├── core/             config, db, deps, errors, logging
│   │   │   └── main.py
│   │   ├── alembic/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   ├── web-marketplace/          Next.js — public marketplace + buyer UX
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── package.json
│   │
│   └── web-creator/              Next.js — authoring app (visual builder)
│       ├── app/
│       ├── components/
│       │   └── builder/          React Flow canvas, node palette, inspector
│       ├── lib/
│       └── package.json
│
├── packages/
│   ├── skills-schema/            TS types + Zod schemas for skills.md frontmatter
│   │                             (auto-generated from Pydantic models via openapi-ts)
│   ├── api-client/               typed fetch client generated from FastAPI OpenAPI
│   └── ui/                       shared shadcn components used by both web apps
│
├── infra/
│   ├── docker-compose.yml        local dev
│   └── seed/                     fixture data for local development
│
├── prompts/                      ← this folder
├── docs/                         human-readable specs derived from prompts
├── .github/workflows/            CI: lint, type, test, build per app
├── pnpm-workspace.yaml
├── package.json                  workspace root, scripts: dev, build, test
└── README.md
```

### Why two frontends?
The marketplace is content-heavy and benefits from SSR/SEO; the creator is interactive and stays mostly client-side. Splitting them avoids leaking heavy builder code into landing-page bundles. They share `packages/ui` and `packages/api-client`.

### Why a single backend?
Skills, billing, delivery, and authoring all touch the same data. A single API with clear module boundaries is simpler than microservices at this scale. If a module needs to scale independently later (search, sandbox runtime), extract it then — not preemptively.

---

## Conventions

### Backend
- **One package per bounded context** under `src/`. Each package owns: `models.py` (SQLAlchemy), `schemas.py` (Pydantic), `service.py` (business logic), `router.py` (FastAPI router), `tests/`.
- **No business logic in routers.** Routers parse, delegate, return.
- **No raw SQL in routers or services** unless explicitly justified. Use the ORM.
- **All money in cents (int).** Never floats for currency.
- **All timestamps in UTC.** Postgres `timestamptz`. Serialize as ISO 8601 with `Z`.
- **All IDs are UUID v7** (time-ordered) — implement with `uuid_v7` package.

### Frontend
- **Server Components by default.** `"use client"` only when you need interactivity.
- **No fetch in components.** Use TanStack Query hooks in client components, async functions on the server.
- **Forms use React Hook Form + Zod.** No uncontrolled state spaghetti.
- **Styling: Tailwind utility classes + shadcn primitives.** No CSS-in-JS, no global stylesheets beyond `globals.css`.

### Shared
- **API contracts live in OpenAPI.** Generated by FastAPI, consumed by `packages/api-client` via `openapi-typescript-codegen`. Frontend never hand-writes types for API responses.
- **Skill files (skills.md) validate identically on both sides** using a shared JSON Schema generated from the Pydantic frontmatter model.

---

## Out of scope for v1

- Multi-tenant orgs / team workspaces (single-user creator accounts only).
- Self-hosted deployments for buyers.
- Mobile apps.
- i18n. English only at launch; keep strings extractable.

---

## Acceptance for "stack is set up"

- [ ] `docker compose up` brings up postgres + redis + minio + mailhog locally.
- [ ] `pnpm dev` starts all three apps (api on :8000, marketplace on :3000, creator on :3001).
- [ ] `pnpm typecheck && pnpm lint && pnpm test` passes on a clean checkout.
- [ ] CI runs the same on push to `main` and PRs.
- [ ] `api-client` and `skills-schema` regenerate cleanly from a single `pnpm codegen` script.
