# Dev diary — Occupations, Cycle 1 Wave 2

**Owner:** Backend-A (Occupations)
**Wave:** 2 (T-03 Occupations schemas / service / router / tests)
**Started:** 2026-05-26
**Status:** shipped (handing off to orchestrator)

---

## What shipped

### `apps/api/src/occupations/`

- **`schemas.py`** — Pydantic v2 request/response models per
  `team/02-api-surface.md` §1: `OccupationCreate`, `OccupationUpdate`,
  `OccupationSkillsBulkSet` (+ `OccupationSkillBulkItem`),
  `OccupationSkillUpsert`, `OccupationSkillRead`, `OccupationSkillList`,
  `OccupationSkillGroup`, `OccupationListItem`, `OccupationListResponse`,
  `OccupationRead`, `OccupationDetailResponse`, `GraphNode`,
  `GraphEdge`, `VaultGraphPreview`, `OccupationBuildRequest`,
  `PublishRequest`, `JobAccepted`, plus a private `CreatorChip` for
  embedded creator chips. All schemas use `ConfigDict(from_attributes=True)`
  and include `json_schema_extra={"examples": ...}` on the public
  surfaces so OpenAPI auto-docs carry real examples. Slug + domain
  validation is enforced at the schema layer (kebab-case, ≤80 chars,
  no duplicates) so the service never sees garbage.

- **`service.py`** — business logic. Public functions:
  `create_occupation`, `update_occupation`, `add_or_update_member`,
  `bulk_set_members`, `remove_member`, `reorder_members`,
  `list_occupations` (filters + cursor pagination),
  `get_occupation_detail` (returns the domain-grouped view consumed by
  the detail page), `get_graph_preview` (nodes from membership + edges
  from each member's `links:` frontmatter — capped at 200 nodes per
  `02-api-surface.md`), `trigger_build`, `publish_occupation`.
  All errors raise `OccupationError` (extends `core.errors.AppError`
  for FastAPI handler reuse). Every mutation writes an `audit_log` row
  with the action codes named in `02-api-surface.md` §Audit log
  additions (`occupation.created`, `occupation.updated`,
  `occupation.members_set`, `occupation.build_queued`,
  `occupation.published`). No raw SQL — every query uses the ORM
  `select()` builder.

- **`router.py`** — FastAPI router (`prefix="/v1/occupations"`,
  `tags=["occupations"]`). Exports a single `router` variable.
  Endpoints land verbatim from `02-api-surface.md` §1 plus the
  `PATCH /v1/occupations/{id}/skills/order` reorder endpoint required
  by T-03 acceptance bullet 5. Public detail accepts both
  `/v1/occupations/{handle}/{slug}` and `/v1/occupations/{id}`.
  Routers parse + delegate + return — no business logic.

  Route-order note: `/{skill_id}/graph-preview` is registered BEFORE
  `/{handle}/{slug}` because both match the shape `/{seg}/{seg}` and
  FastAPI picks the first registration. Same reason
  `/{skill_id}` (single segment) is registered AFTER the handle/slug
  pair so two-segment paths don't shadow it.

- **`tests/__init__.py`**, **`tests/conftest.py`** — self-contained
  test fixtures (in-memory sqlite engine, fake Redis, http client with
  the occupations router mounted on a freshly-created app). Mirrors
  the patterns in `apps/api/tests/conftest.py` so the brief's
  verification command `pytest src/occupations/tests/ -v` works
  without depending on the project-level conftest (pytest's conftest
  discovery would not pick it up across sibling trees).

- **`tests/test_service.py`** — 21 service-level unit tests, covering
  every public function and every error code:
  - `creator_not_verified`, `pricing_required`, `slug_conflict`
  - `not_found` (ownership rejection),
  - `invalid_member_kind`, `domain_unknown`, `member_not_found`,
    `duplicate_member`
  - happy-path round trips for upsert, bulk-replace, remove, reorder,
    listing (filtered by kind+status), detail (with domain grouping),
    build trigger (rejects empty membership), publish (sets
    `released_at` + `latest_version_id`).

- **`tests/test_router.py`** — 34 router-level integration tests,
  covering happy + auth-fail + validation-fail branches per the T-03
  acceptance criterion. Auth is exercised via FastAPI
  `dependency_overrides` (we don't re-test the cookie/JWT flow inside
  this module — that's already covered by `tests/test_auth_flow.py`).

### Wave 1 gap closed: `alembic upgrade head` against Postgres

The Wave 1 diary flagged that `alembic upgrade head` had not been
verified against a real Postgres (Docker was not running at the time).
I started Docker Desktop, brought up `infra/docker-compose.yml`'s
`postgres + redis`, and ran the migration chain. Two real bugs
surfaced and were fixed in `apps/api/alembic/env.py`:

1. The default Alembic `alembic_version.version_num` column is
   `VARCHAR(32)`, which truncates revision identifiers like
   `0010_categories_seed_occupations_personas` (43 chars). The migration
   would complete the table writes but fail to UPDATE the version row,
   leaving the DB in a stale state. Fix: ensure the table exists with a
   `VARCHAR(128)` column at the start of every migration run via
   `CREATE TABLE IF NOT EXISTS … + ALTER COLUMN … TYPE`. Pure config —
   not a new migration.

2. The async engine pattern `async with connectable.connect() as
   connection: await connection.run_sync(do_run_migrations)` opens an
   implicit transaction on the asyncpg connection. SQLAlchemy's
   `run_sync` wraps Alembic's per-migration begin/commit, but the outer
   asyncpg transaction was never closed, so on `dispose()` the
   connection rolled back. Every "Running upgrade …" INFO line printed
   but the DDL never landed in the DB. Fix: add `await
   connection.commit()` after `run_sync`.

After both fixes, a clean Postgres takes all 10 migrations
(`<base> → 0001 → 0002 → {0003, 0004} → 0005 → 0006 → 0007 → 0008 →
0009 → 0010`) and ends with 26 tables in the public schema, including
all 8 new ones from Wave 1 (`occupations`, `occupation_skills`,
`personas`, `persona_neurons`, `capture_sessions`,
`capture_attachments`, `vault_builds`, `vault_downloads`).

### Ancillary `pyproject.toml` change

Added `"src/*/tests/**/*"` to `[tool.ruff.lint.per-file-ignores]` so
per-module tests get the same dispensations as the top-level
`tests/` (plus a few extras for integration-style test code:
`PLC0415` for late-bound fixture imports, `E402`/`SIM105`/`S110`
for the standard test-bootstrap pattern, `TC*` for in-test
type annotations). Mirrors what already applied to `tests/**/*`.

---

## Verification

### Verification commands from the brief

```powershell
# From apps/api/
$ uv run pytest src/occupations/tests/ -v
$ uv run mypy --strict src/occupations
$ uv run ruff check src/occupations
```

### `uv run pytest src/occupations/tests/ -v`

```
============================== 55 passed in 12.66s ==============================
```

(21 service tests + 34 router tests, all green.)

### `uv run mypy --strict src/occupations`

```
Success: no issues found in 9 source files
```

### `uv run ruff check src/occupations`

```
All checks passed!
```

### Regression check — existing tests untouched

```
$ uv run pytest tests/ -q
546 passed, 1 warning in 23.26s
```

### Postgres migration end-to-end

```
$ uv run alembic upgrade head
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_initial, initial schema
INFO  [alembic.runtime.migration] Running upgrade 0001_initial -> 0002_seed_categories, seed categories
INFO  [alembic.runtime.migration] Running upgrade 0002_seed_categories -> 0003_search_index, search index + editorial picks + search alerts + faq_md
INFO  [alembic.runtime.migration] Running upgrade 0002_seed_categories -> 0004_billing_phase1, billing phase 1: webhook_events + users.payouts_enabled
INFO  [alembic.runtime.migration] Running upgrade 0003_search_index, 0004_billing_phase1 -> 0005_delivery_and_moderation, delivery + moderation phase 1
INFO  [alembic.runtime.migration] Running upgrade 0005_delivery_and_moderation -> 0006_occupations_and_kind, occupations + skills.kind discriminator
INFO  [alembic.runtime.migration] Running upgrade 0006_occupations_and_kind -> 0007_personas_and_neurons, personas + persona_neurons
INFO  [alembic.runtime.migration] Running upgrade 0007_personas_and_neurons -> 0008_capture, capture_sessions + capture_attachments
INFO  [alembic.runtime.migration] Running upgrade 0008_capture -> 0009_vault_builds_and_downloads, vault_builds + vault_downloads + licenses composition
INFO  [alembic.runtime.migration] Running upgrade 0009_vault_builds_and_downloads -> 0010_categories_seed_occupations_personas, seed occupations + personas categories
```

26 tables present in `public` post-migration including
`occupations`, `occupation_skills`, `personas`, `persona_neurons`,
`capture_sessions`, `capture_attachments`, `vault_builds`,
`vault_downloads`.

---

## Line for orchestrator to add in `main.py`

```python
from src.occupations.router import router as occupations_router

# inside create_app():
app.include_router(occupations_router)
```

(Mount alongside the other Wave 2 routers; ordering relative to
`personas_router` / `capture_router` doesn't matter — different
URL prefixes.)

---

## Open questions / handoffs

1. **Build job is a stub.** `service.trigger_build()` writes the
   audit row and returns a synthesised `JobAccepted` but doesn't
   enqueue an Arq job. T-06 (Wave 3) wires the real
   `vault.build_occupation` task — at that point my `trigger_build`
   should be amended to:
   ```python
   from src.vault.jobs import enqueue_occupation_build
   job_id = await enqueue_occupation_build(skill_id, version, ...)
   ```
   and write the `build_id` returned into the `JobAccepted`. I left
   the function shape so Wave 3 can swap it without touching the
   router or the OpenAPI surface.

2. **`get_graph_preview` reads link data via `get_object()` per
   member.** That's N+1 if there are 200 members — at MVP scale
   (~30-50 members per occupation per `05-mvp-plan.md` T-08) it's
   fine. Wave 3's vault builder will pre-compute the link graph and
   stuff it into `vault_builds.manifest_json` — at that point the
   preview should read from `manifest_json` instead of re-parsing
   the S3 objects. I left the loop tolerant of missing storage so
   the preview never fatals on a partial vault.

3. **`PublishRequest` is currently fast-tracked synchronously.** I
   mark `released_at + latest_version_id` inside `publish_occupation`
   so the demo flow (T-13) can run end-to-end against a build stub.
   When T-06 lands and the build is genuinely async, this should
   move into the build's success callback — i.e. the Arq worker
   sets `released_at` only after the vault zip is in S3 and
   `vault_builds.status='succeeded'`. The router doesn't change;
   only `publish_occupation` does.

4. **Domain validation on member upsert is strict.** If the
   occupation declares `domains=["ci-cd","obs"]`, you cannot add a
   member with `domain="incident-response"` — the service rejects
   with `occupation.domain_unknown`. Curation (T-08
   `build_devops_vault.py`) must order operations correctly:
   declare every domain first, then assign members. This is
   already documented inline in the service error message.

5. **Spawned dependency: `personas` service will need
   `get_occupation_summary(skill_id)`.** When Backend-B builds
   `POST /v1/personas { parent_occupation_id }`, they need to
   validate the parent is a published occupation. I left
   `service.get_occupation_detail(session, skill_id=…)` public for
   that — the persona module can call it and check
   `.status == published` + `.kind == occupation`. If they want a
   lighter lookup, an explicit helper is trivial to add and is a
   strictly-additive change.

6. **Wave 3 / T-06 vault builder.** The vault builder will read
   `OccupationSkill` ordered by `(sort_order, slug)` (matching what
   `_list_members` does today). The `role` enum
   (`core / supporting / optional`) drives the `00-index.md`
   sectioning. The `domain` field maps 1:1 to a folder name in the
   vault zip. None of those contracts change — the builder is the
   only consumer of these fields besides the marketplace
   preview.

---

## What Wave 2 (Occupations) inherits to Wave 3

- A working creator-write surface: create → bulk-set membership →
  build (stub) → publish. Layer-A in `05-mvp-plan.md` is unblocked.
- A working public-read surface: list, detail (with domain
  grouping), graph-preview. Layer-A and T-11 (marketplace
  occupation page) are both unblocked.
- A stable error-code namespace (`occupation.*`) the
  frontend/curation pipelines can match on without breakage.
- A test harness that runs `pytest src/occupations/tests/` standalone
  — useful for the Wave-3 builder to compose end-to-end tests
  against without monkey-patching the global conftest.
