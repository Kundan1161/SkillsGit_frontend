# 08 — Infrastructure

Diagrams of the Skills Git infrastructure — what's running locally,
how config flows from disk to runtime, what CI executes per PR and
nightly, and the production deployment target that has not yet been
provisioned.

Source: `infra/docker-compose.yml`, `apps/api/.env.example`,
`apps/api/src/core/config.py`, and every workflow under
`.github/workflows/` — all read directly. Production deploy targets
come from `prompts/01-tech-stack-and-repo.md §Infra` and are marked
`<<target>>` throughout — none of the prod stack is live yet.

## Files

### [`docker-compose-stack.drawio`](docker-compose-stack.drawio) — local dev stack

The four sidecar services in `infra/docker-compose.yml` —
`postgres:16-alpine` (5433→5432 to avoid clashing with a local
Postgres install), `redis:7-alpine` (6379), `minio/minio`
(9000 + 9001 console), `mailhog/mailhog` (1025 SMTP + 8025 UI) —
plus the four host-side processes (`apps/api` FastAPI, the Arq
worker, `web-marketplace`, `web-creator`) that dial them via the
published host ports. Includes per-service healthchecks, named
volumes (`pgdata`, `miniodata`), and the single `skillsgit` bridge
network they all share.

### [`env-config-flow.drawio`](env-config-flow.drawio) — `.env` → runtime

How a `.env` value becomes a runtime injection: `.env.example`
(tracked) → developer copy to `.env` (gitignored) → Pydantic
Settings `BaseSettings` in `core/config.py` (with `env_file='.env'`,
`case_sensitive=False`, `extra='ignore'`) → `@lru_cache` singleton
exported as `settings` → consumed by every module that needs config.
Lists every key env var grouped by purpose (DB, Redis, S3, Stripe,
secrets, fees, SMTP, CORS, OAuth, AI, capture-LLM) and the runtime
consumer that reads each. Also covers the test override path
(`ENV=test`, `SKG_CAPTURE_LLM_STUB=1`, `InMemoryStorage` swap,
in-memory cache).

### [`ci-pipeline.drawio`](ci-pipeline.drawio) — GitHub Actions workflows

Both shipped workflows in detail:

- **`ci.yml`** (existing, per-PR): `lint-and-test` (pnpm install →
  uv sync → typecheck → lint → test) followed by `build` (per-app
  Next.js production build). Triggered on `push` and `pull_request`
  to `main`.
- **`team-smoke.yml`** (Cycle-1 addition): nightly cron
  (`'17 3 * * *'` UTC), manual `workflow_dispatch`, and a
  path-filtered `pull_request` trigger. Spins up
  `postgres:16-alpine` + `redis:7-alpine` as sidecar services,
  runs `alembic upgrade head`, then the full
  `tests/integration/` suite. Env injects `SKG_CAPTURE_LLM_STUB=1`
  and `ANTHROPIC_API_KEY=""` so the demo CLI runs in snapshot-only
  mode.

Includes the pnpm-store + uv caches and a `<<deferred>>` section
listing what's NOT in CI yet (mypy, ruff, deploy step, MinIO sidecar,
live Anthropic test).

### [`deployment-target.drawio`](deployment-target.drawio) — production target

Every box in this diagram is `<<target>>` — nothing here is live.
Production-target stack per `prompts/01-tech-stack-and-repo.md`:
backend on Fly.io OR Railway, frontends on Vercel, Postgres on
Neon, Redis on Upstash, object store on Cloudflare R2, Stripe +
Anthropic live keys. The spec's "don't bake in cloud-specific
bindings" principle is illustrated — every external dep is wired
through a URL/endpoint env var, so the four managed services are
replaceable without code changes. Cycle 2 will add the actual
`flyctl deploy` (or `railway up`) GitHub Actions step plus a
secrets manager (Doppler / Infisical / cloud-native).

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
| Local dev compose stack | `infra/docker-compose.yml` |
| `.env` template | `apps/api/.env.example` |
| Pydantic Settings | `apps/api/src/core/config.py` |
| FastAPI app + middleware | `apps/api/src/main.py` |
| DB engine + session | `apps/api/src/core/db.py` |
| Redis cache façade | `apps/api/src/core/cache.py` |
| Redis dependency for routes | `apps/api/src/auth/deps.py:get_redis` |
| S3 / MinIO / R2 wrapper | `apps/api/src/storage/s3.py` |
| Capture LLM (stub swap) | `apps/api/src/capture/llm.py` |
| Per-PR CI workflow | `.github/workflows/ci.yml` |
| Nightly integration smoke | `.github/workflows/team-smoke.yml` |
| Infra spec (prod target) | `prompts/01-tech-stack-and-repo.md` §Infra (target) |
| Tech stack spec | `prompts/01-tech-stack-and-repo.md` (full file) |

## What's NOT shown

- **Vercel project config** — lives outside the repo; no
  `vercel.json` is needed for the current Next.js apps. Cycle-2.
- **Container Dockerfile** — `apps/api` does not yet ship a
  Dockerfile. The first deploy will add one (Python 3.12-slim base,
  uv-managed venv, uvicorn entry).
- **Alembic migrations** — covered in `03-data-model/` (the migration
  list + per-rev contents). This folder only shows the CI step that
  runs them.
- **Frontend route trees + component hierarchy** — covered in
  `01-web-frontend/`.
