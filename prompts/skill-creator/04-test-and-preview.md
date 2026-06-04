# skill-creator — 04 Test & Preview

**Phase:** 3
**Depends on:** `skill-creator/00-overview.md`, `skill-creator/01-visual-builder.md`, `skill-creator/03-skill-config.md`, `shared/skills-md-spec.md`, `marketplace/05-trust-and-quality.md` (provider-key model)
**Parallel-safe with:** `02-import-from-projects.md`, `05-publish-to-marketplace.md`
**Status:** ready
**Owner:** _empty_

> A creator who can run their skill before publishing fixes bugs we'd otherwise see in refunds and bad reviews. The sandbox is their dress rehearsal.

---

## Scope

- The compiled skills.md preview page (`/skills/{id}/preview`).
- The sandbox runner page (`/skills/{id}/sandbox`).
- Sandbox runtime: model invocation, streaming output, run logs.
- Multi-model comparison (run the same input across required + compatible models).
- Cost & latency telemetry.

---

## Compiled preview (`/skills/{id}/preview`)

A read-only view of the compiled skills.md.

Layout:
- Top: a sticky bar with model targets, validation status, "Open builder" / "Open config" / "Open sandbox" / "Publish".
- Main: the rendered skills.md split into two views:
  - **Rendered** — markdown rendered as it'll appear on the marketplace listing's "What's inside" tab.
  - **Source** — the raw skills.md with syntax highlighting and copy-to-clipboard.
- Side: a tree-of-contents jumping to sections.
- Bottom: validation panel — list of warnings/errors with links into the builder or config to fix.

Pull from the server: `POST /v1/creator/skills/{id}/compile` returns `{ skills_md, valid, errors[] }`. Don't compile only client-side — server compile is the canonical result for publish.

---

## Sandbox (`/skills/{id}/sandbox`)

The sandbox simulates how a buyer's agent will use the skill: it feeds the compiled `## How to apply` instructions plus the inputs to a model and returns the model's response.

### Layout

```
┌────────────────────────┬────────────────────────────┐
│   Inputs (left)        │    Output stream (right)   │
│                        │                            │
│ Model: [claude-opus..▼]│  [streaming output here]   │
│ Provider key: [▼]      │                            │
│                        │  Tokens in: 1234           │
│ Input form:            │  Tokens out: 567           │
│ - name [text]          │  Latency: 4.2s             │
│ - file [upload]        │  Est. cost: $0.012         │
│ - choice [▼]           │                            │
│                        │                            │
│ [Run]  [Run on all reqd│  Saved runs: ▼             │
│         models]        │                            │
└────────────────────────┴────────────────────────────┘
```

### Inputs

- The form is **dynamically generated** from the skill's `frontmatter.inputs[]` (the parameter nodes from the builder).
- Each input type renders an appropriate control (text → Textarea, file → upload, choice → Select, etc.).
- Bulk paste: a "Paste raw JSON" toggle accepts a JSON object matching the input schema and fills the fields.

### Model picker

- Defaults to the first `required_models[]`.
- Switching models is instant — no re-compile (we're sending the same skill body, different model).
- "Run on all required models" button fans out: one streaming column per model (Phase 3 limit: 3 concurrent).

### Provider keys

- Re-use the `provider_keys` infrastructure from `marketplace/05-trust-and-quality.md`.
- A "Manage keys" link in the picker → opens a sheet for CRUD.
- Default keys per provider are remembered; switching models defaults to the most recent key for that provider.

### Running

- **`POST /v1/creator/skills/{id}/sandbox/runs`** body: `{ model_id, provider_key_id, inputs: {} }`. Returns `{ run_id, sse_url }` immediately (202).
- SSE endpoint streams: `{ type: "delta", text: "..." }` then `{ type: "done", tokens_in, tokens_out, finish_reason, duration_ms }` or `{ type: "error", code, message }`.
- Server proxies to the model provider's streaming endpoint. Use httpx async with sse_starlette to relay.
- Run rows persisted in `sandbox_runs(id, user_id, skill_id, draft_id, version_id?, model_id, status, started_at, finished_at, tokens_in, tokens_out, error)`. **Inputs and outputs are NOT stored** by default (privacy). Creator can opt-in to storing outputs for a specific run to come back to later.

### Saved runs

- Below the input form, a list of recent runs (latest 10) with timestamps, model, status, duration.
- Clicking re-loads inputs and re-displays the output (only if the creator opted to save it; otherwise placeholder).

### Cost & latency display

- Show tokens in/out per run.
- Estimated cost: derive from `models.py` allowlist (price per 1k tokens by provider). Use a static price table; refresh quarterly.
- p95 latency across recent runs (last 20) under the chart strip.

### Multi-model comparison

When "Run on all required models" is clicked:
- The UI splits the output panel into N columns (one per model).
- Each column streams independently.
- A final "Compare" tab summarizes: best/worst by duration, tokens, perceived quality (creator-rated thumbs).
- Saved as a `sandbox_comparisons` row referencing the underlying `sandbox_runs`.

### Quality checklist (creator self-eval)

A panel below the output: "Did the skill work as expected?" with thumbs up/down per output, plus a "Notes" field. Stored on the `sandbox_runs` row. Surfaces in publish wizard: "You've tested 5 times, 4 passed."

---

## Limitations

- The sandbox does NOT execute tools the skill claims (no real `web_search`, no real `code_execution` unless the model provider supports it natively in the call). If the skill relies on tool calls, the sandbox surfaces a warning: "This skill requires tools that we don't simulate yet. Test in a real agent before publishing."
- Cost shown is approximate. We disclose this in a footnote.

---

## API summary

- `POST /v1/creator/skills/{id}/compile` — server-side compile + validate.
- `POST /v1/creator/skills/{id}/sandbox/runs` — start a run.
- `GET  /v1/creator/skills/{id}/sandbox/runs/{run_id}/stream` — SSE stream.
- `GET  /v1/creator/skills/{id}/sandbox/runs?limit=10` — list recent runs.
- `PATCH /v1/creator/skills/{id}/sandbox/runs/{run_id}` — annotate with notes / outcome.
- `POST /v1/creator/skills/{id}/sandbox/runs/{run_id}/keep-output` — opt to persist output for this run.

---

## Provider integration

Server-side per-provider drivers:

```
apps/api/src/sandbox/
├── base.py          ProviderDriver interface
├── anthropic.py     Claude (Opus/Sonnet/Haiku 4.5+)
├── openai.py        GPT-4o / 4.1 / o-series
├── google.py        Gemini 1.5+ (Phase 3 best-effort)
└── runner.py        orchestrator + SSE relay
```

Each driver:
- `build_request(skill_body_md, inputs, model_id) -> ProviderRequest`
- `stream(request, key) -> AsyncIterator[Delta | Done | Error]`

Inputs are embedded into a runtime prompt template:

```
You are an AI assistant. The following skill describes the methodology to follow.

<skill>
{compiled_skill_body_md}
</skill>

<inputs>
{json of inputs}
</inputs>

Follow the skill's instructions exactly. Produce the outputs described.
```

This is the same template a buyer's agent could use; it's documented so buyers can replicate.

---

## Acceptance

- [ ] Sandbox runs against Claude (Anthropic provider) with a creator-supplied key.
- [ ] Sandbox runs against GPT-4o with an OpenAI key.
- [ ] SSE stream renders deltas live with no perceptible lag.
- [ ] Token counts + estimated cost appear after `done` event.
- [ ] Multi-model fan-out runs 2 models concurrently and shows side-by-side.
- [ ] Run history persists; opt-in output persistence works.
- [ ] Provider keys never log to disk; verified by audit-log scan in tests.
- [ ] Compiled preview shows rendered + source views with validation panel.
- [ ] E2E: creator opens sandbox → fills inputs → runs → sees streaming output → marks as passed.
