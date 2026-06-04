# 02 — Backend API

Diagrams of the FastAPI backend in `apps/api/`. Source: actual router
files and module imports — not the `team/02-api-surface.md` spec — so
small drifts between spec and code are captured truthfully.

## Files

### [`module-graph.drawio`](module-graph.drawio) — module file map

Every bounded context under `apps/api/src/` is one subgraph, with its
real files listed inside (e.g. `vault/` shows `builder.py`,
`composer.py`, `manifest.py`, `validator.py`, `jobs.py`, `router.py`,
`models.py`). Arrows are real import / runtime dependencies pulled
from the service-layer code: `capture → personas/skills/storage/anthropic`,
`vault.composer → vault.builder + cache + billing + occupations + personas`,
`billing.router → personas.models` for the persona-checkout 409 gate.
Cycle-1 subgraphs carry the `<<new>>` stereotype.

### [`request-pipeline.drawio`](request-pipeline.drawio) — request lifecycle

End-to-end sequence for `GET /v1/catalog/skills?q=devops`. Walks
through CORS → `TraceIdMiddleware` (sets `X-Trace-Id` and the
`_trace_id_var` contextvar) → slowapi `Limiter` (`LIMIT_DEFAULT =
120/minute`, keyed by user id or IP) → router parses `Query()` params
→ service runs the SQLAlchemy 2.x async query → Postgres → response
serialised by Pydantic → response headers include the trace id.
Branches show what happens for rate-limit overflows and how
`AppError` / `HTTPException` / `RequestValidationError` / uncaught
exceptions all funnel through `_render()` into the canonical
`ErrorResponse` shape.

### [`auth-flow.drawio`](auth-flow.drawio) — registration + login + request auth

Three phases in one sequence. **Register:** `POST /v1/auth/register`
runs `password_is_strong_enough()`, hashes with argon2id (mem=64 MiB,
t=3, p=4), inserts the user + audit row, fires a verification email
(Mailhog in dev), and auto-issues a session cookie. **Login:**
`POST /v1/auth/login` consults the Redis lockout counter, runs
`authenticate()` (timing-safe — verifies against `_DUMMY_HASH` on
unknown email), resets the failed-login counter on success, issues
the JWT, and writes the `auth.login` audit row. **Subsequent
request:** `auth.deps.get_optional_user` tries the
`Authorization: Bearer skg_…` API token first, falls back to the
session JWT in the `skillsgit_session` cookie, checks the Redis
`jti` denylist, and resolves the `User`. `current_active_user`
enforces `is_active`; `require_creator` / `require_admin` layer on
top.

### [`api-surface.drawio`](api-surface.drawio) — every `/v1/*` endpoint

Grouped by router file. Each node is `METHOD path · auth-scope ·
notes` where auth-scope is `pub` / `user` / `creator` / `admin` (as
seen in the actual `Depends(...)` annotations). Cycle-1 routers are
marked `<<new>>`. Highlights faithful to the source rather than the
spec:

- `/v1/skills/` (existing skills router) is a `501` stub —
  `catalog/router.py` and `skill_detail_router.py` own listing and
  detail.
- `vault/router.py` mounts at the **root** (no prefix); its endpoints
  live under `/v1/licenses/{id}/vault*` and `/v1/vault/builds/{id}`
  rather than `/v1/vault/…`.
- `billing.router` adds the 409 `persona.requires_parent_occupation`
  gate inline on `POST /v1/checkout/sessions` — no new endpoint.
- `personas` `GET /{id}/neurons` returns 404 (not 403) to non-entitled
  callers to avoid existence leaks.
- All Cycle-1 build/publish endpoints return 202 `JobAccepted`; the
  real work runs in `vault.jobs` / `capture.jobs` (Arq).

## How to view

Every file in this folder is a `.drawio` file. Open it in the draw.io
desktop app or at [app.diagrams.net](https://app.diagrams.net), or
render it inline in VS Code with the
[Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)
extension. See [`docs/diagrams/README.md`](../README.md#how-to-view-these-diagrams)
for the full guide and the two flavours of `.drawio` in this repo
(native mxgraph vs Mermaid-embedded).

## Source pointers

| Topic | File |
|---|---|
| Router mounts | `apps/api/src/main.py` |
| CORS + trace id + rate-limit middleware | `apps/api/src/main.py` + `core/logging.py` + `core/rate_limits.py` |
| Global exception handlers | `apps/api/src/core/errors.py` |
| Auth dependencies | `apps/api/src/auth/deps.py` |
| JWT mint / decode / denylist | `apps/api/src/auth/tokens.py` |
| Password hashing | `apps/api/src/auth/service.py` (`pwd_context`, `_DUMMY_HASH`) |
| Persona-checkout 409 gate | `apps/api/src/billing/router.py` lines ~99-123 |
| Vault composer + cache | `apps/api/src/vault/composer.py` |
