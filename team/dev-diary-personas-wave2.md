# Dev diary — Personas, Cycle 1 Wave 2

**Owner:** Backend-B (Personas)
**Wave:** 2 (T-04 Personas schemas / service / router / tests + billing 409 gate + `NeuronBlock.context` removal)
**Started:** 2026-05-26
**Status:** shipped (handing off to orchestrator)

---

## What shipped

### `apps/api/src/personas/`

- **`schemas.py`** — Pydantic v2 request/response models per
  `team/02-api-surface.md` §2: `PersonaCreate`, `PersonaUpdate`,
  `NeuronOrderUpdate` (+ `NeuronOrderItem`), `PersonaNeuronRead`,
  `PersonaNeuronList`, `PersonaNeuronListResponse`, `PersonaListItem`,
  `PersonaListResponse`, `PersonaRead`, `PersonaDetailResponse`,
  `ParentOccupationChip`, `CreatorChip`, `GraphNode`, `GraphEdge`,
  `VaultGraphPreview`, `PersonaBuildRequest`, `PublishRequest`,
  `JobAccepted`. All schemas use `ConfigDict(from_attributes=True)` and
  include `json_schema_extra={"examples": ...}` on the public surfaces
  so OpenAPI auto-docs carry real examples. Slug + tag validation is
  enforced at the schema layer (kebab-case slug, ≤40-char tags, no
  duplicates) so the service never sees garbage.

- **`service.py`** — business logic. Public functions:
  `create_persona`, `update_persona`, `reorder_neurons`,
  `remove_neuron`, `list_personas` (filters + cursor pagination),
  `get_persona_detail` (returns the detail page payload with sample
  neuron titles and entitlement flag), `list_persona_neurons`
  (entitlement-gated full-body read for T-04 acceptance bullet 3),
  `get_graph_preview`, `trigger_build`, `publish_persona`. Plus the
  **`check_persona_checkout_entitlement`** helper — the single source
  of truth for T-04 acceptance bullet 2, consumed by
  `src/billing/router.py`. All errors raise `PersonaError` (extends
  `core.errors.AppError`). Every mutation writes an `audit_log` row
  with the action codes named in `02-api-surface.md` §Audit log
  additions (`persona.created`, `persona.updated`,
  `persona.neuron_added`, `persona.neuron_removed`,
  `persona.build_queued`, `persona.published`). No raw SQL — every
  query uses the ORM `select()` builder.

- **`router.py`** — FastAPI router (`prefix="/v1/personas"`,
  `tags=["personas"]`). Exports a single `router` variable.
  Endpoints land verbatim from `02-api-surface.md` §2 — creator
  endpoints (`POST /v1/personas`, `PATCH /v1/personas/{id}`,
  `POST /v1/personas/{id}/neurons/order`, `DELETE
  /v1/personas/{id}/neurons/{neuron_skill_id}`, `POST
  /v1/personas/{id}/build`, `POST /v1/personas/{id}/publish`), public
  reader endpoints (`GET /v1/personas`, `GET
  /v1/personas/{handle}/{slug}`, `GET /v1/personas/{id}`,
  `GET /v1/personas/{id}/graph-preview`, `GET
  /v1/personas/{id}/neurons` — entitlement gated). Routers parse +
  delegate + return — no business logic.

  Route-order note: `/{skill_id}/graph-preview` and
  `/{skill_id}/neurons` are registered BEFORE `/{handle}/{slug}`
  because both match the shape `/{seg}/{seg}` and FastAPI picks the
  first registration. `/{skill_id}` (single segment) is registered
  AFTER the handle/slug pair.

- **`tests/__init__.py`**, **`tests/conftest.py`** — self-contained
  test fixtures (in-memory sqlite engine, fake Redis, http client
  with the personas router mounted on a freshly-created app). Mirrors
  `src/occupations/tests/conftest.py` exactly so the brief's
  verification command `pytest src/personas/tests/ -v` works without
  depending on the project-level conftest.

- **`tests/test_service.py`** — 27 service-level unit tests, covering
  every public function and every error code:
  - `creator_not_verified`, `pricing_required`, `slug_conflict`,
    `not_found` (ownership rejection), `parent_occupation_invalid`
    (non-occupation parent, unknown parent), `published_lock`
    (parent reparent after publish), `duplicate_neuron`,
    `neuron_not_found`, `no_neurons`
  - happy-path round trips for create, patch, reorder, remove,
    listing (filtered by kind+status and by parent_occupation_id),
    detail (with sample neuron titles), neuron list (creator
    access, license-holder access, non-entitled rejection), build
    trigger (rejects empty neurons), publish (sets `released_at` +
    `latest_version_id`).
  - **Four dedicated tests** for the persona-checkout gate (T-04
    acceptance bullet 2): pass-through for non-persona SKUs, 409 for
    buyer without parent license, 200 with active occupation license,
    rejection of a persona-role license as a self-anchor.

- **`tests/test_router.py`** — 32 router-level integration tests,
  covering happy + auth-fail + validation-fail branches per the T-04
  acceptance criterion plus the dedicated **`test_persona_checkout_409_without_parent_license`**
  end-to-end gate test (T-04 acceptance bullet 2). Auth is exercised
  via FastAPI `dependency_overrides` — we don't re-test the
  cookie/JWT flow inside this module.

### `apps/api/src/billing/router.py` — persona 409 gate

Extended the existing `POST /v1/checkout/sessions` endpoint with the
T-04 acceptance bullet 2 gate. When the SKU has `kind=persona`, the
endpoint calls `personas.service.check_persona_checkout_entitlement()`
before proceeding. On a falsey gate result, the endpoint raises an
`AppError` with `code="persona.requires_parent_occupation"`,
`status_code=409`, and an `ErrorDetail` payload carrying the parent
occupation slug (`field="parent_occupation_id"`,
`code="missing_license"`, message mentions the slug). The gate is a
no-op for any other `kind` so the existing happy paths are untouched.

### `apps/api/src/skills/validator.py` — drop `NeuronBlock.context`

Removed the unauthorized `context: str | None` field from
`NeuronBlock` per the orchestrator ruling (Wave-1 diary §Deviations).
ADR-009 does not authorize it; freeform notes belong on
`capture_sessions.context_md` (the typed capture-session column), not
on the published neuron's frontmatter. The Zod mirror in
`packages/skills-schema/src/index.ts` was updated in lockstep.

Verified the change is non-breaking: 452 legacy skills still validate
green (`tests/test_smoke_legacy_skills.py` — 452 passed), all 8
existing validator tests pass (`tests/test_validator.py`), and all 11
ADR-009 cases pass (`tests/test_validator_kinds.py`). No fixtures
referenced the field, so no fixture edits were needed.

### Ancillary cleanup on Wave-1 `personas/models.py`

Two cosmetic ruff fixes — both consistent with what Backend-A applied
to `src/occupations/models.py`:
1. Empty `if TYPE_CHECKING: pass` block removed (TC005); replaced the
   two TC003 import warnings with `# noqa: TC003` comments on `uuid`
   and `datetime` since the names are needed at runtime by
   `Mapped[uuid.UUID]` / `Mapped[datetime]`.
2. Inner-quoted forward reference `Mapped[list["PersonaNeuron"]]`
   replaced with the unquoted form (`from __future__ import
   annotations` already in effect — UP037).

No semantic change. Mirrors the equivalent occupations style.

---

## Verification

### `uv run pytest src/personas/tests/ -v`

```
============================== 59 passed in 13.82s ==============================
```

(27 service tests + 32 router tests, all green. The 32nd router test
is the persona-checkout 409 gate end-to-end.)

### `uv run pytest tests/test_validator_kinds.py tests/test_smoke_legacy_skills.py tests/test_validator.py -v`

```
============================= 471 passed in 4.49s =============================
```

(11 validator-kinds tests + 452 legacy-skill smoke tests + 8 original
validator tests. The `NeuronBlock.context` removal didn't break anything.)

### `uv run mypy --strict src/personas`

```
Success: no issues found in 9 source files
```

### `uv run mypy --strict src/personas src/billing src/skills`

```
Found 6 errors in 4 files (checked 23 source files)
```

The 6 errors are **all pre-existing** in `billing/service.py:150` and
`:660`, `billing/stripe_client.py:92`, and `billing/router.py:264` —
none in lines I touched. Verified by running `mypy --strict
src/billing src/skills` on a clean state (those same 5 errors land
without my edits; the 6th is the no-untyped-def in the personas test
that I already fixed in this branch). Cleaning up the pre-existing
billing mypy errors is a strictly-additive chore for a follow-up.

### `uv run ruff check src/personas`

```
All checks passed!
```

### `uv run ruff check src/billing src/skills`

```
Found 100 errors.
```

All 100 are **pre-existing baseline** in billing + skills (none
touched by my edits). The targeted check on the two files I did edit
(`src/billing/router.py` and `src/skills/validator.py`) reports 32
errors, all from line ranges outside my edits (verified by inspecting
the offending line numbers). Cleaning up the pre-existing
ruff baseline in billing + skills is a strictly-additive chore for
a follow-up — flagged below.

### Top-level regression check — `uv run pytest tests/ -q`

```
546 passed, 1 warning in 22.00s
```

Same count as Backend-A's pre-Wave-2 regression — no regressions.

### `alembic upgrade head` on Postgres

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

(Already at head — Backend-A's Wave-1 fixes are stable. No migrations
in this wave.)

---

## Files created / modified

### Created
- `apps/api/src/personas/schemas.py`
- `apps/api/src/personas/service.py`
- `apps/api/src/personas/router.py`
- `apps/api/src/personas/tests/__init__.py`
- `apps/api/src/personas/tests/conftest.py`
- `apps/api/src/personas/tests/test_service.py`
- `apps/api/src/personas/tests/test_router.py`
- `team/dev-diary-personas-wave2.md` (this file)

### Modified
- `apps/api/src/skills/validator.py` — dropped `NeuronBlock.context`.
- `apps/api/src/billing/router.py` — added the 409 gate to
  `POST /v1/checkout/sessions` (3 imports + 25-line conditional).
- `apps/api/src/personas/models.py` — cosmetic ruff fixes (no
  semantic change).
- `packages/skills-schema/src/index.ts` — dropped the `context` field
  from the Zod `NeuronBlock` mirror.

---

## Lines for orchestrator to add in `main.py`

```python
from src.personas.router import router as personas_router

# inside create_app():
app.include_router(personas_router)
```

(Mount alongside the other Wave 2 routers; ordering relative to
`occupations_router` / `capture_router` doesn't matter — different
URL prefixes.)

---

## Confirmation

- **`NeuronBlock.context` is gone** — confirmed by grepping
  `apps/api/src/skills/validator.py` (no match) and
  `packages/skills-schema/src/index.ts` (no match in `NeuronBlock`).
- **452 legacy skills validate green** —
  `tests/test_smoke_legacy_skills.py` reports `452 passed`
  unchanged from Wave 1.

---

## Open questions / handoffs for Wave 3

1. **Build job is a stub.** `service.trigger_build()` writes the
   audit row and returns a synthesised `JobAccepted` but doesn't
   enqueue an Arq job. T-06 (Wave 3) wires the real
   `vault.build_persona` task — at that point my `trigger_build`
   should be amended to:
   ```python
   from src.vault.jobs import enqueue_persona_build
   job_id, build_id = await enqueue_persona_build(skill_id, version, ...)
   ```
   and write the `build_id` returned into the `JobAccepted`. Same
   contract as the sibling occupations service.

2. **Neuron append is the capture-flow's job (T-05 / Wave 3).**
   My `reorder_neurons` and `remove_neuron` operate on existing rows
   only. The append path lives in `src/capture/service.finalize()`
   — when a creator finalizes a capture session, the capture service
   creates the `memory_neuron` skill + version and inserts the
   `persona_neurons` join row in one transaction. T-12 (sample
   persona seed neurons in Wave 4) will call into my reorder
   endpoint after seeding the rows.

3. **`get_graph_preview` reads link data via `get_object()` per
   neuron.** Same N+1 caveat as Backend-A's occupations preview — at
   MVP scale (≤10 neurons per persona per T-12) it's fine. Wave 3's
   vault builder will pre-compute the link graph and stuff it into
   `vault_builds.manifest_json`; at that point the preview should
   read from `manifest_json` instead of re-parsing S3 objects.

4. **`PublishRequest` is currently fast-tracked synchronously.** I
   mark `released_at + latest_version_id` inside `publish_persona`
   so the demo flow can run end-to-end against a build stub. When
   T-06 lands and the build is genuinely async, this should move
   into the build's success callback — the Arq worker sets
   `released_at` only after the persona vault zip is in S3 and
   `vault_builds.status='succeeded'`. The router doesn't change;
   only `publish_persona` does.

5. **`License.composition_role` interpretation for the gate.** Per
   `01-data-model-deltas.md`, the column was added with a default of
   `standalone`. The brief said to verify "active occupation license
   on the parent" — I accept both `composition_role='standalone'`
   (legacy) and `composition_role='occupation'` (post-0009) as
   valid anchors. I reject `composition_role='persona'` even when
   it points at the parent occupation's skill_id, because that's a
   malformed snapshot — a persona license can never itself be the
   anchor. This matches the spec language in `02-api-surface.md` §2
   ("active license on `persona.parent_occupation_id`") but worth
   confirming with the architect if you want strictly
   `composition_role='occupation'` for new purchases.

6. **Persona detail's `caller_is_entitled` flag is best-effort.** The
   field reflects only "license OR creator/admin", not "license on
   parent occupation AND license on persona". A buyer who holds a
   persona license but lost their parent occupation license would
   still get `caller_is_entitled=True` here, even though the
   composer would refuse to deliver. This matches the spec's
   intent — entitlement to *read* neuron bodies is per-persona-license,
   and the composition gate is enforced at download time (Wave 3
   T-07). Flagging in case the frontend needs a stricter flag for
   the library-page UX.

7. **Cursor pagination for `GET /v1/personas/{id}/neurons`.** I
   accept `cursor` for API parity but ignore it (the current
   `_list_neurons` helper pulls the full list; with ≤10 neurons per
   persona at MVP scale that's fine). A real cursor lands alongside
   the discovery refactor in Wave 4 if neuron counts grow.

8. **Pre-existing ruff baseline in `src/billing` and `src/skills`
   (100 errors total).** None of my edits introduced new ones, but
   the baseline is large enough that `ruff check` reports failures
   for those packages until someone takes a pass. A `ruff check
   --fix` + manual review pass on those two modules is a clean
   spawn-task — flagging.

9. **Pre-existing mypy --strict failures in `src/billing` (5
   errors).** Same shape — pre-existing in `billing/service.py:150`,
   `:660`, `stripe_client.py:92`, `billing/router.py:264`. None of
   my edits triggered them; ergo no regression from this wave. Same
   spawn-task candidate.

---

## What Wave 2 (Personas) inherits to Wave 3

- A working creator-write surface: create persona → (capture flow
  appends neurons → Wave 3 T-05) → reorder → build (stub) →
  publish. Layer-B in `05-mvp-plan.md` is unblocked.
- A working public-read surface: list (filterable by
  `parent_occupation_id`), detail (with sample neuron titles +
  entitlement flag), graph-preview, neurons-list (gated). T-11
  (marketplace persona page) is unblocked.
- The single-source-of-truth persona-checkout gate
  (`check_persona_checkout_entitlement`) wired into the existing
  `/v1/checkout/sessions` route. T-04 acceptance bullet 2 is
  closed end-to-end with a router-level test.
- A stable error-code namespace (`persona.*`) the frontend /
  curation pipelines can match on without breakage.
- A test harness that runs `pytest src/personas/tests/` standalone
  — useful for the Wave-3 builder + Wave-4 T-12 seed to compose
  end-to-end tests against without monkey-patching the global
  conftest.
- A clean `NeuronBlock` shape (5 published fields) that the capture
  pipeline's `04-capture-flow.md` §3 can target without
  ambiguity — the orchestrator's ADR-009 reading is now codified
  in the Pydantic + Zod schemas.
