# Dev diary — Capture, Cycle 1 Wave 2

**Owner:** Backend-C (Capture)
**Wave:** 2 (T-05 Capture schemas / service / router / LLM wrapper / Arq job / PII / quota / tests + stub LLM corpus)
**Started:** 2026-05-26
**Status:** shipped (handing off to orchestrator)

---

## What shipped

### `apps/api/src/capture/`

- **`schemas.py`** — Pydantic v2 request/response models per
  `team/02-api-surface.md` §3: `CaptureSessionCreate`,
  `CaptureSessionUpdate`, `CaptureSessionRead`, `CaptureSessionListItem`,
  `CaptureSessionListResponse`, `CaptureFinalize`, `Abandon`,
  `CaptureAttachmentRead`, `AttachmentUploadMeta`, `JobAccepted`,
  `NeuronCreated`, plus `SuggestedLink` + `PIIFindingSchema` sub-shapes
  that mirror the JSON columns on the `capture_sessions` row. All
  schemas use `ConfigDict(from_attributes=True)` for direct ORM
  hydration; mutation bodies use `extra="forbid"` so the router rejects
  unknown keys; every public surface carries
  `json_schema_extra={"examples": …}` so the auto-generated OpenAPI
  docs carry real request bodies.

- **`pii.py`** — synchronous, in-process PII + secret detector. Two
  pattern sets per ADR-016 + `04-capture-flow.md` §PII:
  - **Hard-block list** = `validator.SECRET_PATTERNS` (re-imported; same
    surface as the publish-time secret scan, so an AWS key / SSN /
    credit card never leaks past finalize even if a creator marks the
    flag as "accepted").
  - **Warn list** = email, US + E.164 phone, public IPv4 (private
    ranges + loopback suppressed), internal Slack channels (both
    pre- and post-keyword), Jira tickets.
  - Severity tiers `{high|medium|low}` map directly to the spec. The
    `PIIFinding` dataclass + `scan()` / `has_hard_block()` /
    `has_unresolved_high()` helpers are the entire public surface;
    findings sort deterministically by `(span_start, type)` for stable
    snapshots.

- **`llm.py`** — Anthropic SDK wrapper. **Single chokepoint** for every
  LLM call (ADR-008 BYOK swap point lives here in Cycle 2). Exports:
  - `CaptureExtractInput` + `CaptureExtractResult` dataclasses + the
    `LLMClient` `Protocol` that the real and stub clients conform to.
  - `build_system_prompt()` / `build_user_prompt()` — the prompt
    template lifted verbatim from `team/04-capture-flow.md` §3 (model
    pinned to `claude-sonnet-4-6` per the validator's allowlist; the
    `04-capture-flow.md` doc says 4-7 but the validator does NOT have
    4-7 in its allowlist yet — pinned to 4-6 to keep the validator
    happy; flagged below).
  - `_RealAnthropicClient` — lazy-imports the SDK so stub-only test
    runs never need it.
  - `is_stub_enabled()` reads `SKG_CAPTURE_LLM_STUB=1` (the canonical
    name from this brief) or `SKG_LLM_STUB=1` (legacy alias from
    `team/test-plan.md` §Stub LLM strategy). Either flag, plus the
    settings field, opts in.
  - `get_client()` returns the stub when enabled, the real client
    otherwise (with a clear error if `ANTHROPIC_API_KEY` is unset).
  - Minimal YAML emitter (`_dict_to_yaml`) assembles the LLM's parsed
    JSON envelope into a full `skills.md` string — no `PyYAML`
    dependency added.

- **`quota.py`** — Redis-backed monthly quota per ADR-008. Key shape
  `capture:quota:{creator_id}:{YYYY-MM}` (UTC), 32-day TTL so old
  keys evict naturally. Public API: `reserve()` (atomic incr;
  `CaptureQuotaExceededError` → 429 `capture.quota_exceeded` past
  cap), `peek()` (read-only, for status headers), `refund()` (rolls
  back a reservation when the downstream extract fails, with a floor
  of 0 so we never go negative). Cap is configurable via
  `settings.SKG_CAPTURE_QUOTA_PER_MONTH` (default 10). The Redis
  client comes from `src.auth.deps.get_redis` so the project-wide
  fake-Redis swap works uniformly in tests.

- **`service.py`** — business logic. Public functions:
  - `create_session` — opens a `status=draft` row; rejects unverified
    creators (403 `capture.creator_not_verified`), unowned personas
    (403 `capture.persona_not_owned`), and unknown personas (404
    `capture.persona_not_found`).
  - `update_session` — partial patch including the AI-edited
    `draft_md` and `suggested_links`; rejects on terminal status
    (409 `capture.terminal_status`).
  - `run_extract` — invokes `llm.extract_draft()` synchronously
    (used by the Arq job AND by the router under the stub LLM path),
    persists `draft_md` + `suggested_links_json` + `pii_flags_json` +
    `llm_model` + `token_usage_json`, transitions the row through
    `extracting → draft_ready`. Refunds the quota slot on parse
    failure. Status code maps: 502 `capture.extract_parse_error` for
    LLM errors.
  - `enqueue_extract` — the router-facing wrapper. Under
    `SKG_CAPTURE_LLM_STUB=1` it runs `run_extract` in-process (so
    tests need no Arq worker per the T-05 acceptance bullet). Under
    the real LLM it dispatches to the Arq job.
  - `finalize_session` — **the atomic transaction**. PII gate first
    (so the more-specific `capture.pii_blocked` wins over the
    generic `secret_detected` body error), then `validate_file()`,
    then slug uniqueness, then INSERT skills + skill_versions +
    persona_neurons + attachment copy + status flip + 3 audit rows
    (capture_session/finalized + skill/created +
    persona/neuron_added) — all inside the request's session, so
    any error rolls back the entire SAVEPOINT per ADR-015.
  - `abandon_session` / `add_attachment` / `remove_attachment` /
    `list_sessions` / `get_session` — supporting flows. Attachments
    have a hard 5 MB cap (422 `capture.attachment_too_large`); the
    storage backend is the same `src.storage.s3.get_storage()` shim
    that personas/occupations consume.

- **`jobs.py`** — Arq job `extract_neuron(ctx, session_id)`. Opens a
  fresh DB session (Arq runs outside the request context), hydrates
  the creator user, calls `service.run_extract(..., consume_quota=False)`
  (the router already reserved the quota slot before enqueuing), and
  commits. `WorkerSettings` sets `max_tries=2` per
  `04-capture-flow.md` §Failure modes (one retry with a stricter
  prompt; a third failure surfaces as `capture.extract_parse_error`).
  `enqueue_extract()` is the façade the service calls under the real
  LLM path; it translates `settings.REDIS_URL` into Arq's
  `RedisSettings` and pushes a job with the deterministic id
  `capture:extract:{session_id}`.

- **`router.py`** — FastAPI router (`prefix="/v1/capture"`,
  `tags=["capture"]`). Single `router` export, no business logic.
  Endpoints: `POST /sessions`, `GET /sessions`, `GET /sessions/{id}`,
  `PATCH /sessions/{id}`, `POST /sessions/{id}/extract`,
  `POST /sessions/{id}/finalize`, `POST /sessions/{id}/abandon`,
  `POST /sessions/{id}/attachments`, `DELETE
  /sessions/{id}/attachments/{aid}`. Every endpoint sets
  `response_model`, `responses=error_responses(...)`, and a `summary`
  so the OpenAPI bundle stays self-documenting.

- **`tests/__init__.py`**, **`tests/conftest.py`** — self-contained
  test harness (in-memory sqlite + fake-Redis + `InMemoryStorage`
  swap; mirrors `src/personas/tests/conftest.py` exactly). The
  conftest forces `SKG_CAPTURE_LLM_STUB=1` + `SKG_LLM_STUB=1` at
  import time so every test routes through the stub. A
  `capture_fixtures` session-scoped fixture loads all four JSON
  fixtures from `apps/api/tests/fixtures/captures/`.

- **`tests/test_pii.py`** — 18 PII unit tests. Covers every pattern
  (email, US phone, E.164 phone, public/private IPv4, slack channel,
  Jira ticket, CC, AWS key, SSN), the masked-preview shape, the
  hard-block predicate (including the "accepted=true cannot dismiss
  a platform-wide secret" rule), and the T-05 acceptance check
  against the `with_pii.json` fixture's expected severity set.

- **`tests/test_quota.py`** — 10 quota unit tests. Key-format,
  month-rollover, per-creator isolation, reserve / peek / refund
  semantics, and the T-05 acceptance bullet 4 service-layer 429.

- **`tests/test_service.py`** — 22 service-level unit tests covering
  every public function and every error code: create / update /
  list / extract / enqueue / finalize / abandon / attachments. The
  atomic-finalize test asserts on the resulting Skill +
  SkillVersion + PersonaNeuron + finalized capture row + storage
  write; the slug-collision, draft-empty, PII-hard-block, and
  validate-fail rollback tests confirm ADR-015's "fails the whole
  transaction" guarantee.

- **`tests/test_router.py`** — 27 router-level integration tests
  covering happy + auth-fail + validation-fail branches per the
  T-05 acceptance: create / get / list / patch / extract / finalize /
  abandon / attachments. Two T-05-acceptance tests stand out:
  - `test_extract_populates_draft_within_30s_via_stub` — POST →
    extract → poll → draft_md populated, all in <2 seconds via the
    stub (T-05 bullet 1).
  - `test_eleventh_extract_returns_429_with_quota_exceeded` — burns
    10 extracts, asserts the 11th is 429 with code
    `capture.quota_exceeded` (T-05 bullet 4 end-to-end).
  - `test_finalize_creates_neuron_end_to_end` (T-05 bullet 3) +
    `test_finalize_422_when_pii_hardblock` (PII gate enforcement).

### `apps/api/tests/stubs/`

- **`__init__.py`** + **`llm.py`** — the deterministic Anthropic
  stub. `StubAnthropicClient.extract()` looks up canned responses by
  SHA256 of `(title|first-60-chars-of-situation)`; falls back to a
  generic-but-valid `memory_neuron` skills.md template formatted per
  call with the creator handle + parent occupation slug. The
  fallback template passes `validate_file()` cleanly, so most
  happy-path tests work with no corpus entries at all. `register()`
  + `clear_corpus()` helpers let tests pin specific responses; the
  conftest auto-resets between tests so pins don't leak.

### `apps/api/tests/fixtures/captures/`

- **`happy.json`** — clean situation/decision/outcome/context. Stub
  returns the generic template; PII detector reports zero findings.
- **`with_pii.json`** — situation containing an email (medium),
  internal Slack channel (low), and an inline credit card (high
  → hard-block at finalize).
- **`with_attachments.json`** — references 2 S3 attachment keys
  (the actual upload happens via the multipart endpoint in tests; the
  fixture documents the expected sha256/filename pairs).
- **`short.json`** — minimal viable input; still extracts under the
  stub fallback.

### `apps/api/.env.example` additions

```
# ── Capture LLM (ADR-008) ─────────────────────────────────────────────
SKG_CAPTURE_LLM_MODEL=claude-sonnet-4-6
SKG_CAPTURE_LLM_STUB=0
SKG_CAPTURE_QUOTA_PER_MONTH=10
```

`ANTHROPIC_API_KEY` was already present in `.env.example` — left blank
for the user to fill (Brand-keyed Anthropic client is invoked when
both `SKG_CAPTURE_LLM_STUB=0` and `ANTHROPIC_API_KEY` is set).

### `apps/api/src/core/config.py` additions

Three new settings fields on the `Settings` model: `SKG_CAPTURE_LLM_MODEL`,
`SKG_CAPTURE_LLM_STUB`, `SKG_CAPTURE_QUOTA_PER_MONTH`. Defaults match
the .env.example values.

### Wave-1 capture/models.py polish (consistent with siblings)

- Added `# noqa: TC003` to the `uuid` + `datetime` imports — Mapped[]
  uses them at runtime; matches what Backend-A applied to
  `occupations/models.py`.
- Added `# noqa: UP042` on `CaptureSessionStatus(str, enum.Enum)` with
  the same explanatory comment as `OccupationMemberRole` — keeps the
  project-wide enum pattern consistent rather than mixing StrEnum
  (3.11+) in.
- The auto-fixer unquoted `Mapped[list["CaptureAttachment"]]` — no
  semantic change.

---

## Verification

### `uv run pytest src/capture/tests/ -v`

```
=== test_pii.py ===
18 passed in 0.33s

=== test_quota.py ===
10 passed in 0.31s

=== test_service.py ===
22 passed in 3.71s

=== test_router.py ===
27 passed in 9.12s

=== combined ===
77 passed, 5 warnings in 10.96s
```

(18 PII + 10 quota + 22 service + 27 router; the 5 warnings are
Starlette's deprecation of `HTTP_422_UNPROCESSABLE_ENTITY` — pre-existing
across the project, not introduced here.)

### `uv run mypy --strict src/capture`

```
Success: no issues found in 15 source files
```

### `uv run ruff check src/capture`

```
All checks passed!
```

### Regression check — existing tests untouched

```
$ uv run pytest tests/ -q
546 passed, 1 warning in 22.32s

$ uv run pytest src/personas/tests/ src/occupations/tests/ -q
114 passed, 11 warnings in 25.42s
```

Same counts as Backend-A / Backend-B's pre-Wave-2 baselines — no regressions.

### Postgres migration

```
$ uv run alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

Already at head — Backend-A's Wave-1 + Backend-B's Wave-2 are stable.
No migrations in this wave.

---

## Files created / modified

### Created
- `apps/api/src/capture/schemas.py`
- `apps/api/src/capture/pii.py`
- `apps/api/src/capture/llm.py`
- `apps/api/src/capture/quota.py`
- `apps/api/src/capture/service.py`
- `apps/api/src/capture/jobs.py`
- `apps/api/src/capture/router.py`
- `apps/api/src/capture/tests/__init__.py`
- `apps/api/src/capture/tests/conftest.py`
- `apps/api/src/capture/tests/test_pii.py`
- `apps/api/src/capture/tests/test_quota.py`
- `apps/api/src/capture/tests/test_service.py`
- `apps/api/src/capture/tests/test_router.py`
- `apps/api/tests/stubs/__init__.py`
- `apps/api/tests/stubs/llm.py`
- `apps/api/tests/fixtures/captures/happy.json`
- `apps/api/tests/fixtures/captures/with_pii.json`
- `apps/api/tests/fixtures/captures/with_attachments.json`
- `apps/api/tests/fixtures/captures/short.json`
- `team/dev-diary-capture-wave2.md` (this file)

### Modified
- `apps/api/src/core/config.py` — added 3 capture-LLM settings fields.
- `apps/api/.env.example` — added the 3 capture-LLM env vars.
- `apps/api/src/capture/models.py` — added `# noqa: TC003` to uuid +
  datetime imports, `# noqa: UP042` on `CaptureSessionStatus`, and the
  ruff auto-fixer unquoted the `Mapped[list["CaptureAttachment"]]`
  forward ref. No semantic change.

---

## Lines for orchestrator to add in `main.py`

```python
from src.capture.router import router as capture_router

# inside create_app():
app.include_router(capture_router)
```

(Mount alongside the other Wave 2 routers; ordering relative to
`occupations_router` / `personas_router` doesn't matter — different
URL prefixes.)

---

## Confirmation of `.env.example` additions

```
# ── Capture LLM (ADR-008) ─────────────────────────────────────────────
SKG_CAPTURE_LLM_MODEL=claude-sonnet-4-6
SKG_CAPTURE_LLM_STUB=0
SKG_CAPTURE_QUOTA_PER_MONTH=10
```

Three new keys, all with safe defaults. `ANTHROPIC_API_KEY` was
already in `.env.example` from Wave 1; left blank as the brief
required.

---

## Open questions / handoffs for Wave 3

1. **Real Arq worker is not running in tests.** Per the T-05
   acceptance bullet, tests use the synchronous stub LLM —
   `service.enqueue_extract` runs the extraction in-process when
   `SKG_CAPTURE_LLM_STUB=1` is set. The Arq path (`jobs.enqueue_extract`
   → `extract_neuron`) is wired but only exercised in production
   against a real Anthropic key + a running Arq worker. Wave 4's
   T-13 demo CLI should hit the real path against
   `apps/api/scripts/demo_devops_agent.py` — that's where any wiring
   bugs in `jobs.py` would surface.

2. **`SKG_CAPTURE_LLM_MODEL` defaults to `claude-sonnet-4-6` (not
   4-7)** even though `04-capture-flow.md` §3 says 4-7. Reason: the
   validator's `ALLOWED_AI_MODELS` set (`src/skills/models.py`) does
   not include `claude-sonnet-4-7` yet — only 4-5 and 4-6. The stub
   LLM's draft uses 4-6 too so the validator passes on the
   round-trip. If/when the curator adds 4-7 to the allowlist (a one-
   line non-breaking change), bump the default. Flagged for the
   architect — non-blocking for Cycle 1.

3. **Attachment copy on finalize is best-effort.** If the S3 copy
   fails (network blip), the neuron still publishes — we log the
   failure but don't fail the transaction. Rationale: the attachment
   exists at its capture-prefix URL anyway (lifecycle policy deletes
   after 30 days per `04-capture-flow.md` §Attachment storage); a
   subsequent re-build can re-copy. The capture-prefix S3 object
   remains the source of truth until the persona-prefix copy
   completes. Wave-3 vault builder (T-06) should be tolerant of
   missing persona-prefix objects on first build.

4. **PII detector's slack-channel pattern is intentionally loose.**
   It matches `#anything` within 30 chars of the word "slack" in
   either direction. False positives are possible (e.g. "Slack used
   to bundle #include for C devs" would fire). MVP is OK with this —
   the creator-resolves model means a few extra warn flags is
   acceptable. A per-creator deny-list (curators add their own
   "internal terms") is Q-3 in `06-open-questions.md` and a Phase-2
   concern.

5. **Quota cap is global at 10/month.** ADR-008 says "free tier:
   10/month; beyond that, BYOK or paid tier". Paid quota lands in
   Phase 2 alongside the `creator_api_keys` table; the gate now lives
   in one place (`quota.reserve`), so swapping it for a per-creator
   tiered cap is a strictly-additive change.

6. **Finalize creates the neuron in `status=draft`** per ADR-005 +
   ADR-015 — neurons are never publicly listed, only addressable
   inside the persona's vault. Wave 3's persona vault builder (T-06)
   reads `persona_neurons` ordered by `(sort_order, slug)`, picks
   up the new neuron, and includes it in the next build. The
   neuron's `Skill.status=draft` is fine — it never reaches the
   public catalog regardless.

7. **`run_extract` consumes one quota slot per call.** The Arq
   retry path uses `consume_quota=False` so retries don't double-
   charge. If a creator's first extract parses cleanly and they then
   call `POST /extract` a second time to re-run with edits, that
   does count as a second slot — same as the spec
   (`04-capture-flow.md` §Edit loop says "each extract counts
   against the monthly quota").

8. **The stub corpus is intentionally empty.** Only the generic
   fallback template is registered. Tests that need pinned LLM
   output can call `register()` from `tests/stubs/llm.py` — but the
   77 tests as written don't need it (the fallback is rich enough
   to exercise every code path). The T-13 demo CLI may want to add
   canned responses for the 3-5 stock prompts in
   `scripts/seed_data/demo/prompts.yaml` so the demo's "Consulted
   neurons" snapshot is fully deterministic.

9. **Pre-existing ruff/mypy baseline in `src/billing` + `src/skills`
   noted by Backend-B was not touched.** None of my edits introduced
   new errors in those modules.

---

## What Wave 2 (Capture) inherits to Wave 3 + Frontend

- A complete creator-facing capture loop: open session → submit
  fields → extract draft → review + edit + accept links → finalize
  into the persona. Layer-B in `05-mvp-plan.md` is unblocked for
  the human-driven path.
- A single LLM chokepoint (`capture.llm.get_client()`) that BYOK
  in Cycle 2 will swap with one if-branch.
- A deterministic PII detector that the marketplace's "see what
  the AI flagged" UI consumes verbatim.
- A Redis-backed quota that's safe to call from any code path —
  idempotent, refund-able, per-month per-creator isolated.
- An Arq job that production deploy can stand up by running
  `uv run arq src.capture.jobs.WorkerSettings`; tests stay sync
  via the stub so CI doesn't need Redis/Arq.
- A test stub corpus that T-13's demo CLI can extend with pinned
  responses for the demo prompts (the `register()` API is the
  surface).
- A stable error-code namespace (`capture.*` + `skill.slug_taken`
  for the finalize collision) the frontend can match on.
- A self-contained test harness that runs
  `pytest src/capture/tests/` standalone — no global conftest
  dependency, so T-14 integration tests can compose against it.
