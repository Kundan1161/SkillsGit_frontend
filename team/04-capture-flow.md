# 04 — Capture UX + Pipeline

**Owner:** Architect
**Status:** Proposed
**Reads:** ADR-005, ADR-008, ADR-009, ADR-015, existing
`apps/web-creator/app/` route structure, `apps/api/src/storage/` for
attachment upload pattern.

This file defines how a practitioner records a situation in the web UI,
how the backend turns it into a draft memory-neuron skills.md, and
how the creator promotes the draft into a published neuron inside their
persona.

---

## 1. UI wireframe (added to `apps/web-creator/`)

Routes (existing `apps/web-creator/app/` already has `_design`, `import`,
`skills`, `templates`, `settings`, `sign-in/up`):

```
/personas                       persona list (new)
/personas/new                   create persona form (new)
/personas/[id]                  persona dashboard (new)
/personas/[id]/neurons          neuron list within persona (new)
/capture                        new capture session: pick or create persona (new)
/capture/[id]                   active capture session (review + finalize) (new)
```

### `/capture` — landing

```
┌──────────────────────────────────────────────────────────────────┐
│  Capture a situation                                             │
│                                                                  │
│  Which persona is this for?                                      │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ ▼ Jane's On-Call Brain  (parent: AI DevOps Engineer)         ││
│  │   The Cloud-Cost Cynic  (parent: AI DevOps Engineer)         ││
│  │   + Create new persona…                                       ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  [ Start capture → ]                                             │
└──────────────────────────────────────────────────────────────────┘
```

### `/capture/[id]` — recording form (immediately after creation)

```
┌──────────────────────────────────────────────────────────────────┐
│  Capture session · Jane's On-Call Brain · draft                  │
│                                                                  │
│  Title (one line)                                                │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ Flaky CI tests after Redis upgrade — Aug 2024                ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Situation — what happened? when? who was involved?              │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ Our checkout-service test suite started failing intermittent ││
│  │ ly the morning after we upgraded shared Redis from 6 → 7…    ││
│  │                                                              ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Decision — what did you choose to do and why?                   │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ I assigned each test suite a dedicated Redis logical DB inde ││
│  │ x (FLUSHDB on the per-suite index between tests)…             ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Outcome — what actually happened? would you do it again?         │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ Pass rate went 80% → 99.4% in 24 hours. Side note: a single ││
│  │ shared FLUSHALL would have been faster to ship but worse for ││
│  │ debuggability…                                                ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Context (optional) — anything else                              │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ Team of 8, ~200 backend tests, GitHub Actions matrix…        ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Attachments (drag-and-drop or click)                            │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  [+ ci-run-pre-fix.png]  [+ ci-run-post-fix.png]             ││
│  │  [+ redis-config.yaml]                                       ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  [ Generate draft → ]                                            │
└──────────────────────────────────────────────────────────────────┘
```

### `/capture/[id]` — draft review (after extract returns)

```
┌──────────────────────────────────────────────────────────────────┐
│  Draft neuron · status: draft_ready                              │
│                                                                  │
│  ┌─ Slug + version ─────────────────────────────────────────────┐│
│  │ Slug:    2024-08-flaky-tests-redis            [auto-suggested]││
│  │ Version: 1.0.0                                                ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─ Preview (rendered) ─────────────────────┐  ┌─ Markdown ────┐ │
│  │ # Flaky CI tests after Redis upgrade…    │  │ ---           │ │
│  │                                          │  │ id: jane-devo… │ │
│  │ ## When to use                           │  │ kind: memory_… │ │
│  │ Use this neuron when a test suite starts │  │ neuron:       │ │
│  │ failing intermittently after a backing-… │  │   situation:  │ │
│  │                                          │  │     "…"       │ │
│  │ ## How to apply                          │  │   decision:   │ │
│  │ 1. Reproduce locally with the post-upgr… │  │     "…"       │ │
│  │ …                                         │  │ ---           │ │
│  └──────────────────────────────────────────┘  └───────────────┘ │
│                                                                  │
│  Suggested links into base/                                       │
│  ☑ base/ci-cd/devops-ci-pipeline-architect — applies              │
│  ☑ base/observability/observability-dashboard-architect — see-also│
│  ☐ base/incident-response/ops-incident-commander — see-also       │
│  [+ Add link…]                                                    │
│                                                                  │
│  PII flags (review before publish)                                │
│  ⚠ "checkout-service" — internal service name, likely fine. [keep]│
│  ⚠ "Slack: #team-billing" — internal Slack channel.  [redact]    │
│                                                                  │
│  [ Re-run extraction ]   [ Save draft ]   [ Publish into persona ]│
└──────────────────────────────────────────────────────────────────┘
```

The "Publish into persona" button submits to
`POST /v1/capture/sessions/{id}/finalize`.

### `/personas/[id]/neurons` — neuron list

Standard CRUD table: title, recorded_at, status (draft|published|yanked),
section, sort_order, last updated, actions (reorder, view, edit metadata).

---

## 2. Backend pipeline

```
[ web-creator UI ]
       │
       │ POST /v1/capture/sessions  (form fields)
       ▼
[ capture/router.py: create_session ]
       │
       │ - inserts capture_sessions row (status=draft)
       │ - returns 201 + session id
       │ - enqueues Arq job: capture.extract_neuron(session_id)
       ▼
[ Arq worker: capture/jobs.py:extract_neuron ]
       │
       │ 1. load capture_sessions row, parent persona, parent occupation,
       │    occupation_skills list (for `links[]` suggestion candidates)
       │
       │ 2. call LLM (capture/llm.py:extract_draft)
       │    - prompt: structured template (see §3)
       │    - inputs: situation_md, decision_md, outcome_md, context_md,
       │              candidate slugs from occupation_skills
       │    - response format: JSON {frontmatter: {...},
       │                              body_sections: {...},
       │                              suggested_links: [...]}
       │    - tracks token_usage, model id
       │
       │ 3. assemble draft_md from the JSON:
       │    - frontmatter dict + body sections in canonical order
       │      (When to use, How to apply, Examples, Limitations)
       │    - frontmatter.kind = memory_neuron
       │    - frontmatter.neuron = {situation, decision, outcome,
       │                            recorded_at: today, confidence: 0.6}
       │    - frontmatter.parent_occupation_id = parent occupation slug
       │    - frontmatter.id = `{creator_handle}/{suggested_slug}`
       │
       │ 4. run validate_file(draft_md.encode())
       │    - on validation errors → fix the obvious (e.g. missing
       │      required section) or surface the errors in the UI for
       │      the creator to repair manually
       │
       │ 5. PII scan (see §4) → pii_flags_json
       │
       │ 6. write back: capture_sessions.draft_md, suggested_links_json,
       │    pii_flags_json, llm_model, token_usage_json, status=draft_ready
       │
       │ 7. notify the frontend (existing job-status endpoint poll)
       ▼
[ web-creator: render draft review UI ]
       │
       │ creator edits, accepts links, resolves PII
       │ creator clicks Publish into persona
       ▼
[ capture/router.py: finalize_session ]
       │
       │ 1. validate_file() one more time on edited draft_md
       │ 2. check pii_flags_json: any with severity=high and accepted=false → 422
       │ 3. inside a single DB transaction:
       │    a. INSERT skills (kind=memory_neuron, status=draft, slug,
       │                      creator_id, category=parent_occupation.category,
       │                      tags from the neuron's frontmatter)
       │    b. compute content_hash; INSERT skill_versions (1.0.0,
       │                      released_at = now, released_by = creator)
       │       (memory neurons publish into the persona's vault build at
       │       next build; they don't need their own marketplace flow)
       │    c. INSERT persona_neurons (persona_id, neuron_skill_id,
       │                      sort_order = max+1, section = …)
       │    d. UPDATE capture_sessions.finalized_at, finalized_neuron_skill_id
       │    e. write_audit (capture_session/finalized, skill/created,
       │                    skill_version/released, persona/neuron_added)
       │    f. copy attachments from capture_attachments S3 prefix to
       │       persona's attachments prefix (atomic via S3 copy)
       │ 4. return 201 with neuron_skill_id and a hint at the
       │    expected vault_path the next persona build will assign
       ▼
[ Frontend: redirect to /personas/[id]/neurons ]
```

---

## 3. LLM extraction prompt (ADR-008)

Model: platform-keyed Claude. Default `claude-sonnet-4-7`
(allowlist verified in `apps/api/src/skills/models.py`). The model
choice is overrideable per request for A/B but defaults are pinned in
`apps/api/src/capture/llm.py`.

System prompt (truncated representative):

```
You are an assistant that converts a practitioner's recorded situation,
decision, and outcome into a draft `skills.md` memory-neuron file for the
Skills Git marketplace.

You MUST output a JSON object with three top-level keys:
  - frontmatter: a YAML-compatible dict
  - body_sections: a dict with keys "when_to_use", "how_to_apply",
    "examples" (optional), "limitations" (optional). Each value is markdown.
  - suggested_links: a list of {target, relation, confidence} where target
    is one of the candidate slugs supplied by the caller. relation must be
    one of: applies, extends, contradicts, see-also, recorded-instance-of.
    Confidence is 0..1 (your own estimate).

CONSTRAINTS:
- The `kind` field MUST be `memory_neuron`.
- The `neuron` block MUST contain situation, decision, outcome (≤3
  sentences each, reusing the practitioner's wording where reasonable).
- `id` MUST be `{creator_handle}/{slug}` using a 2-5 word kebab slug.
- `name` MUST be ≤80 chars.
- `description` MUST be ≤280 chars, single line.
- Do NOT invent specifics not present in the input.
- Do NOT include real names, emails, phone numbers, ticket IDs, internal
  Slack channels, internal hostnames, customer names, or proprietary
  identifiers. If the input contains any, leave them out of the output
  (the caller will flag the input for redaction separately).
- Set `confidence` in the neuron block to 0.6 unless the practitioner
  explicitly says "I'm sure of this" (0.9) or "I'm guessing" (0.3).
- `tags` should be ≤5, kebab-case, drawn from the practitioner's wording.

CANDIDATE LINK TARGETS (parent occupation's skills):
[ "base/ci-cd/devops-ci-pipeline-architect",
  "base/observability/observability-dashboard-architect",
  ...
]

CREATOR HANDLE: {creator_handle}
PARENT OCCUPATION SLUG: {parent_occupation_slug}
RECORDED AT: {today}
```

User prompt: the four input fields concatenated with clear delimiters.

Output is parsed with `json.loads`; failures surface as
`capture.extract_parse_error` and the creator can re-run.

Token usage typical: ≤2k input, ≤1.5k output → ≈ $0.01 per capture
on Sonnet 4.7. The free-tier quota of 10 captures/month per creator
is ≤ $0.10 cost; the business case for paying it from platform key is
trivial for the MVP.

---

## 4. PII / redaction stance

The platform performs **detection** at extract time (post-LLM, on
`draft_md`); the creator performs **resolution** before finalize.

### Detector regex set

Reuses existing SECRET_PATTERNS from `skills/validator.py` (api keys,
SSN, credit cards) plus a new `pii_patterns` set:

| Type | Pattern (simplified) | Severity |
|---|---|---|
| email | `[\w.+-]+@[\w-]+\.[\w.-]+` | medium |
| phone (US) | `\(\d{3}\) \d{3}-\d{4}` and ISO equivalents | medium |
| ipv4 | `\b\d{1,3}(\.\d{1,3}){3}\b` (skip 0/127/192.168/10/172.16) | medium |
| internal-slack-channel | `#[\w-]+` followed by `slack` within 30 chars | low |
| jira-ticket | `\b[A-Z]{2,8}-\d{2,6}\b` | low |
| customer-name | none in MVP (TBD: a per-creator deny-list — Q-2) | — |

A high severity is currently a placeholder for future detector types
(driver licenses, medical record numbers). MVP severities are limited
to {low, medium}.

### Creator responsibility

Each flag in `pii_flags_json` has fields `{type, span_start, span_end,
severity, suggested_redaction, accepted: false}`. The creator can:
- **Keep** (set `accepted=true, action="keep"`).
- **Redact** (replace the span with `suggested_redaction`, default
  `[REDACTED]`; set `action="redact"`).
- **Edit** (manually rewrite the surrounding prose).

Finalize is blocked if any flag has `severity=high` AND `accepted=false`.
Medium and low are not blocking; the creator owns the decision.

### Platform enforcement

- The validator's existing SECRET_PATTERNS check ALWAYS hard-blocks
  finalize (an AWS access key in the draft is never published).
- The `pii_patterns` set is detection only; no patterns are mutated
  silently.
- We do NOT auto-redact. ADR rationale: a memory neuron loses
  meaning if names/timestamps are stripped without the author's
  judgment. Auto-redaction would create plausible-looking but useless
  artifacts.

---

## 5. Attachment storage

Reuses `apps/api/src/storage/` (existing S3 wrapper).

Upload path:
- During capture (draft): `s3://attachments/captures/{capture_session_id}/{sha256}.{ext}`.
- After finalize (permanent): `s3://attachments/personas/{persona_id}/{sha256}.{ext}`.

The finalize service issues an S3 server-side copy (no download +
re-upload). Old draft attachments expire via lifecycle policy after
30 days unless promoted.

Vault build behavior: attachments referenced from neuron body via
standard markdown image links (`![desc](attachments/{sha256-12}.png)`)
get copied into the vault `attachments/` folder by the persona vault
builder. The composer merges all persona attachments into the same
top-level `attachments/` (collisions impossible because of content
addressing).

References from the neuron body MUST use relative paths:
`![](../attachments/{sha256}.png)` resolves correctly when Obsidian
opens the vault.

Size cap per attachment: 5 MB MVP. Hard reject larger; advise the
creator to link off-vault.

---

## 6. AI-suggested links → creator confirms

The extract step (§2 step 2) produces `suggested_links` with
confidence scores. The UI shows each as a checkbox prefilled by
confidence ≥ 0.7. The creator can:
- Confirm a suggestion (no change).
- Reject (uncheck).
- Edit (change `relation` or replace `target` with a typeahead picker
  over the occupation's skill slugs and other personas the creator
  has published).
- Add new links the AI missed.

Only `accepted=true` links land in `frontmatter.links[]` at finalize
time.

Important: the AI MUST pick targets from the candidate list (§3
prompt) — it does not invent target slugs. This guarantees every
suggested link resolves at the parent occupation's current state.
After the creator confirms, the value is locked into the neuron's
frontmatter; if the occupation later renames a skill, the warning
will appear in the next persona rebuild's `manifest.warnings[]`.

---

## 7. Edit loop (re-extraction)

Creator can re-run extraction at any time before finalize:
`POST /v1/capture/sessions/{id}/extract`.

Semantics:
- The input fields (`situation_md`, `decision_md`, `outcome_md`,
  `context_md`) are taken from the current capture_sessions row (so
  PATCH the fields first if you want to change them).
- The output overwrites `draft_md`, `suggested_links_json`,
  `pii_flags_json`, `llm_model`, `token_usage_json`.
- Each extract counts against the monthly quota.
- The creator's manual edits to `draft_md` are lost on re-extract —
  the UI shows a confirmation dialog.

---

## 8. Failure modes

| Failure | Recovery |
|---|---|
| LLM returns invalid JSON | retry once with stricter prompt; on second failure, status=`draft_ready` with `draft_md=null`, surface error code `capture.extract_parse_error`. Creator can paste their own draft into the textarea instead. |
| LLM-produced frontmatter fails validate_file() | status=`draft_ready` with `draft_md` populated; the UI renders both the draft and the validator errors; creator edits to repair. |
| LLM-produced links target unknown slugs | filtered out before write (defense in depth — the prompt already constrains to candidate list). |
| Quota exceeded | 429 with `capture.quota_exceeded`; UI shows count + reset date. |
| Finalize hits a slug collision (`creator/slug` already used) | 409 with `skill.slug_taken`; UI suggests a numbered variant (`-2`). |
| Finalize finds `pii_flags_json[].severity=high && accepted=false` | 422 with the offending flag indexes. |
| Attachment upload exceeds 5 MB | 422 at upload time; doesn't block the session. |

---

## 9. Acceptance for the capture flow

- [ ] Creator can submit a 4-field form and reach a `draft_ready` state
      in ≤30s under normal load.
- [ ] AI-suggested `links[]` are always drawn from the parent
      occupation's skill slugs (verified in unit tests with seeded
      occupation data).
- [ ] PII detector catches the existing fixtures (email, phone, internal
      slack channel patterns) in QA's seeded `bad-capture-*.json` cases.
- [ ] Finalize creates exactly one `skills` row + one `skill_versions`
      row + one `persona_neurons` row inside a single transaction; on
      validate_file() failure the transaction rolls back.
- [ ] A finalized neuron does NOT appear in the public catalog
      (`GET /v1/skills?kind=skill` excludes it; `GET /v1/skills` with
      no filter still excludes it; only the persona owner sees it via
      `GET /v1/personas/{id}/neurons`).
- [ ] The persona's next vault build includes the new neuron as
      `personas/{handle}/neurons/{neuron-slug}.md`.

---

## 10. TBD

- **TBD:** Whether to allow voice or recorded-meeting inputs in MVP.
  Lean **no** — text-form-only keeps the LLM prompt simple and avoids
  speech-to-text infra. Voice is Q-4 in `06-open-questions.md`.
- **TBD:** Whether a creator can attach the same neuron to multiple
  personas (e.g. a generic "post-mortem template" neuron used in both
  "Jane's On-Call Brain" and "Cloud-Cost Cynic"). For MVP we allow this
  (the `persona_neurons` join supports it). The vault composer
  deduplicates by `vault_path`.
- **TBD:** A "private capture" mode (creator records but doesn't publish
  to a persona, just keeps in their own library). Defer — Q-3.

---
