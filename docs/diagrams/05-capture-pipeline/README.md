# 05 — Capture pipeline

Diagrams of the capture flow that turns a creator's recorded situation
into a published `memory_neuron` skill inside their persona. Source:
the actual code under `apps/api/src/capture/` (router, service,
jobs, llm, pii, quota, models) and the migration in
`apps/api/alembic/versions/0008_capture.py` — not the spec, so any
drift between the spec (`team/04-capture-flow.md`) and the shipped
behaviour is reflected here.

## Files

### [`capture-state-machine.drawio`](capture-state-machine.drawio) — CaptureSession lifecycle

The six lifecycle states from
`apps/api/src/capture/models.py:CaptureSessionStatus`:
`draft`, `extracting`, `draft_ready`, `finalizing`, `finalized`,
`abandoned`. Transitions are labelled with the HTTP endpoint or
service step that triggers them. **Drift note:** the `finalizing`
value is reserved in the enum (migration 0008 lists it) but the
shipped `finalize_session()` does not transit through it — the row
goes straight from `draft_ready` to `finalized` inside one
transaction. Leaving the value in the enum lets a future split
(holding `finalizing` while attachment copies finish) avoid another
migration.

### [`capture-sequence.drawio`](capture-sequence.drawio) — full pipeline

End-to-end sequence: creator types fields → `POST
/v1/capture/sessions` → `service.create_session` → `POST
/sessions/{id}/extract` → `service.enqueue_extract` chooses the path:
under `SKG_CAPTURE_LLM_STUB=1` (tests / CI) it runs `run_extract`
inline against `tests/stubs/llm.py`; otherwise it dispatches the Arq
job `capture.jobs.extract_neuron` which runs against the real
Anthropic SDK (`claude-sonnet-4-7`). Result is persisted with
`draft_md`, `suggested_links_json`, `pii_flags_json`, `llm_model`,
`token_usage_json`, status flips to `draft_ready`. Creator polls,
edits, optionally re-extracts, then `POST .../finalize` runs the
atomic transaction (broken out in its own diagram).

### [`capture-finalize-transaction.drawio`](capture-finalize-transaction.drawio) — atomic finalize

Per ADR-015, every write in `finalize_session()` lives in the
request's transaction; any raised `CaptureError` short-circuits
before the router's `await session.commit()` and the savepoint rolls
back. The diagram walks the actual order: PII hard-block re-check
(`capture.pii_blocked` 422) → `validate_file()` re-run
(`capture.validation_failed` 422) → slug uniqueness
(`skill.slug_taken` 409) → INSERT `skills` (kind=`memory_neuron`,
status=`draft`, pricing_model=`free`) → `storage.put_object` for the
body (`capture.storage_failed` 502 on S3 failure) → INSERT
`skill_versions` → INSERT `persona_neurons` (sort_order=max+1) →
`personas.neuron_count` bump → attachment copies (best-effort, never
block) → flip `capture_sessions.status='finalized'` + three audit
rows → COMMIT.

### [`pii-and-quota.drawio`](pii-and-quota.drawio) — PII detector + Redis quota

Two parallel mechanics rendered side-by-side. **PII**: `pii.scan()`
runs the hard-block patterns (reused from
`skills/validator.SECRET_PATTERNS` — credit cards, SSNs, AWS / OpenAI /
Anthropic keys, PEM private keys) at `severity=high` plus the
warn-list patterns (`email`, `phone_us`, `phone_e164`, `ipv4` minus
RFC1918 + loopback, `internal_slack_channel`,
`slack_channel_after_word`, `jira_ticket`) at `medium`/`low`.
`has_hard_block()` is the finalize gate; medium and low findings are
non-blocking and the creator owns keep/redact/edit. **Quota**:
`quota.reserve(creator_id)` INCRs the Redis key
`capture:quota:{uuid}:{YYYY-MM}` (UTC month) with 32-day TTL; on
overflow it DECRs and raises `CaptureQuotaExceededError` (429,
`capture.quota_exceeded`). `quota.refund` rolls back on LLM parse
failures; the Arq retry path passes `consume_quota=False` so it
doesn't double-charge.

## Capture flow reference

The full UX + pipeline spec lives in
[`team/04-capture-flow.md`](../../../team/04-capture-flow.md). The
diagrams here reflect what actually shipped — the creator-side UI
routes (`/capture`, `/capture/[id]`, `/personas/*`) are deferred to
Cycle 2 (marked `<<deferred>>` in
[`01-web-frontend/creator-routes.drawio`](../01-web-frontend/creator-routes.drawio)).

## LLM stub note

CI and unit tests run with `SKG_CAPTURE_LLM_STUB=1` (or the legacy
alias `SKG_LLM_STUB=1`). Set in the test fixture or environment; the
canonical check is
`apps/api/src/capture/llm.py:is_stub_enabled()`. With the stub
enabled, `get_client()` returns `tests/stubs/llm.StubAnthropicClient`
and `service.enqueue_extract` runs the extraction synchronously in
the request (no Arq worker required) so the HTTP test gets a
populated draft on the first response. Production code paths use
`anthropic.AsyncAnthropic` against `settings.SKG_CAPTURE_LLM_MODEL`
(`claude-sonnet-4-7` per `team/04-capture-flow.md` §3).

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
| `CaptureSession` ORM + status enum | `apps/api/src/capture/models.py` |
| Router endpoints (`/v1/capture/*`) | `apps/api/src/capture/router.py` |
| `create_session` / `update_session` / `run_extract` / `enqueue_extract` / `finalize_session` / `abandon_session` | `apps/api/src/capture/service.py` |
| Arq job `extract_neuron` + `WorkerSettings` | `apps/api/src/capture/jobs.py` |
| Anthropic SDK wrapper + stub dispatch | `apps/api/src/capture/llm.py` |
| `pii.scan()` + hard-block / warn patterns | `apps/api/src/capture/pii.py` |
| Redis quota (`reserve` / `refund` / `peek`) | `apps/api/src/capture/quota.py` |
| Schema definitions (`CaptureFinalize`, `SuggestedLink`, `PIIFindingSchema`, …) | `apps/api/src/capture/schemas.py` |
| Migration (`capture_session_status` enum + tables) | `apps/api/alembic/versions/0008_capture.py` |
| Test fixture stub | `apps/api/tests/stubs/llm.py` |
| UX wireframes + prompt template | `team/04-capture-flow.md` |
