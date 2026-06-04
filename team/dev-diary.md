# Dev diary — Cycle 1

**Owner:** QA / Docs
**Status:** Cycle 1 complete (Wave 5 done; Cycle 2 not yet planned)
**Started:** 2026-05-26
**Completed:** 2026-05-26
**Reads:** every `team/dev-diary-*` written this cycle.

## Cycle 1 charter

End-of-cycle deliverable: a working **Layer C** demo — a CLI that loads
the AI DevOps Engineer occupation vault (Layer A) plus one sample
persona overlay with 5–10 neurons (Layer B) and returns an attributed
answer to a DevOps prompt. Built by five roles (Backend, Frontend,
Curation, QA/Docs, Architect-on-call) across five waves per
`team/cycle-1-plan.md`. Gated by the 18 ADRs in `team/decisions.md` —
no architectural decision happens outside that log. Frontend tasks
(T-09/T-10/T-11) are deferrable to Cycle 2 per the "fastest path to
Layer C" rule in `team/05-mvp-plan.md`.

## Decisions log pointer

Architectural decisions live in `team/decisions.md`. This diary captures **what shipped, when, and what broke**. `team/test-plan.md` is the **how-do-we-know-it-works** log.

## Wave 1

### Backend — shipped

Full diary at `team/dev-diary-backend-wave1.md`.

| Aspect | Detail |
|---|---|
| Tasks | T-01 (migrations 0006–0010), T-02 (validator + Zod regen), ADR-017 spec amendment |
| Files | 5 Alembic migrations, 4 new model modules (`occupations`, `personas`, `capture`, `vault`), validator extensions, 7 fixtures, 2 test modules, spec amendment, hand-maintained Zod mirror |
| Tests green | `pytest tests/test_validator_kinds.py` — 11 passed. `pytest tests/test_smoke_legacy_skills.py` — 452 passed. `pytest tests/test_validator.py tests/test_validator_kinds.py tests/test_skill_upload.py` — 25 passed in 30.95s. |
| Types green | `uv run mypy --strict src/skills src/occupations src/personas src/capture src/vault` — clean across 15 source files. |
| What broke | `alembic upgrade head` against Postgres was **not run** — local PG and Docker Desktop unavailable. Sqlite fallback fails at migration 0001 on `CREATE EXTENSION citext` (pre-existing, not new code). |
| Deferred | Router mounting (Wave 2), `pnpm codegen` real implementation (Wave 2+ chore), Postgres `alembic upgrade head` verification (Wave 2 first task). |
| Hand-off | Stable ORM models for 4 new contexts. Validator emits matchable error codes. Spec amended so creator-app preview pane has its Zod source-of-truth. Open questions enumerated below. |

### QA / Docs — shipped (this entry)

| Aspect | Detail |
|---|---|
| Tasks | Test-plan scaffold (`team/test-plan.md`) + dev-diary kickoff (this file) |
| Files | `team/test-plan.md` (acceptance matrix for T-01 through T-15, fixture inventory, stub LLM spec, CI integration plan, 6 open QA risks), `team/dev-diary.md` (this file) |
| What broke | Two contradictions caught between Backend's diary and spec — flagged as R-1 (skill-count drift) and R-4 (`NeuronBlock.context` extension) in `test-plan.md`. Both surfaced to the open-questions queue below. |
| Hand-off | Every Wave 2+ agent flips their task's row in `test-plan.md` from `pending` to `passed` per the "How to update this file" protocol. New risks append as `R-N`. |

### Curation-research — shipped

Full diary at `team/dev-diary-curation-wave1.md`. Inventory at `team/inventory-synth.md`. DevOps slug roster at `team/devops-occupation-slugs.md`.

| Aspect | Detail |
|---|---|
| Tasks | Inventory of `apps/api/scripts/seed_data/synth/`; verify 30 DevOps slugs in T-08; reconcile 456/452/450 count drift; seed cross-link recipe |
| Reconciled count | **450 in `synth/` + 6 demo-creator seed files = 456 total published.** No files added/removed since Wave 1 — three different counting conventions of the same library. |
| DevOps slugs | All 30 spec'd slugs exist as files. 2 swaps proposed for off-domain content: `alert-fatigue-reviewer` (healthcare/CDS) → `slo-designer`; `cross-platform-stack-chooser` (mobile) → `instrumentation-coverage-reviewer`. Both substitutes already in `synth/`. **Approved by orchestrator.** |
| Cross-links | 60 proposed across the 30 skills using `LinkRelation` enum values `applies`, `extends`, `see-also`. Hubs: `devops-ci-pipeline-architect`, `observability-dashboard-architect`, `ops-incident-commander`. Wave 3's T-08 writes the actual YAML. |
| Hand-off | Wave 3 Curation has a verified 30-slug member list + a 60-link recipe seed. T-08 unblocked. |

## Wave 2

### Backend-A (Occupations) — shipped

Full diary at `team/dev-diary-occupations-wave2.md`.

| Aspect | Detail |
|---|---|
| Tasks | T-03 (Occupations schemas + service + router + tests) |
| Tests green | `pytest src/occupations/tests/` — 55 passed (21 service + 34 router). Top-level `pytest tests/` — 546 passed (no regression). |
| Types green | `mypy --strict src/occupations` clean; `ruff` clean. |
| Bonus fixes | Closed two Wave-1 alembic gaps in `alembic/env.py`: widened `version_num` VARCHAR(32→128) for longer Wave-1 revision IDs, and added explicit `await connection.commit()` after `run_sync` so DDL persists. **`alembic upgrade head` against real Postgres now passes** — closes R-3. |
| Deferred | `service.trigger_build()` is a stub; T-06 wires the real Arq job. `get_graph_preview` does N+1 reads — T-06 pre-computes into `vault_builds.manifest_json`. |

### Backend-B (Personas) — shipped

Full diary at `team/dev-diary-personas-wave2.md`.

| Aspect | Detail |
|---|---|
| Tasks | T-04 (Personas schemas + service + router + tests) + billing 409 gate + drop unauthorized `NeuronBlock.context` |
| Tests green | `pytest src/personas/tests/` — 59 passed (27 service + 32 router). Validator + smoke suite — 471 passed (452 legacy skills still green). |
| Types green | `mypy --strict src/personas` clean; `ruff` clean. |
| Resolved questions | **O-6 closed** — `NeuronBlock.context` removed from validator + Zod mirror. ADR-009 stands as the contract. |
| Acceptance | Persona checkout returns 409 `persona.requires_parent_occupation` with parent slug; `GET /v1/personas/{id}/neurons` returns 404 to non-entitled / full bodies to license holders. |

### Backend-C (Capture) — shipped

Full diary at `team/dev-diary-capture-wave2.md`.

| Aspect | Detail |
|---|---|
| Tasks | T-05 (Capture: schemas + service + router + LLM client + PII detector + Arq job + Redis quota + stub LLM + 4 fixtures + tests) |
| Tests green | `pytest src/capture/tests/` — 77 passed (18 PII + 10 quota + 22 service + 27 router). |
| Types green | `mypy --strict src/capture` clean across 15 source files; `ruff` clean. |
| Stub LLM | `apps/api/tests/stubs/llm.py` — deterministic, env-var-toggled (`SKG_CAPTURE_LLM_STUB=1`). Generic fallback returns a validator-green draft. Pinned responses can be registered for T-13 demo. |
| Quota | Redis key `capture:quota:{creator_id}:{yyyy-mm}`, 32-day TTL, cap 10/month, 429 on overrun. **Closes O-5.** |
| Finalize | One DB transaction; full rollback on any step failure (per ADR-015). |
| Deferred | Real Anthropic key + worker only exercised manually; tests run sync stub. Default model is `claude-sonnet-4-6` (validator allowlist doesn't yet include `4-7`); one-line bump unblocks. |

### Orchestrator — Wave 2 close-out

- Mounted three new routers in `apps/api/src/main.py` (alphabetical block + new "Wave-2 modules" comment).
- Full pytest re-run after mounting: **546 legacy + 191 Wave-2 module tests** all pass.
- `cycle-1-plan.md` wave-status updated; Wave 2 marked done; Wave 3 pending.

## Wave 3

### Backend-A (Vault Builder) — shipped

Full diary at `team/dev-diary-vault-builder-wave3.md`.

| Aspect | Detail |
|---|---|
| Tasks | T-06 (vault builder + manifest + Pydantic models + Arq jobs + validator) |
| Files | `src/vault/{builder,manifest,validator,jobs}.py`, `src/vault/schema/vault-manifest-v1.json`, `src/vault/tests/test_{builder,manifest,validator}.py` |
| Tests green | `pytest src/vault/tests/` — 29 passed at hand-off (53 with composer's later additions). Linked-notes section + `<!-- skg-attribution: … -->` trailing block emitted per ADR-010. |
| Stubs replaced | `occupations.service.trigger_build` and `personas.service.trigger_build` now call the real Arq enqueue path. |
| Hand-off | Stable `build_occupation` / `build_persona` API + JSON Schema for v1 manifest. T-07 composer reads its inputs from `vault_builds` rows + S3 zip URLs. |

### Backend-B (Vault Composer) — shipped

Full diary at `team/dev-diary-vault-composer-wave3.md`.

| Aspect | Detail |
|---|---|
| Tasks | T-07 (vault composer + `core/cache.py` Redis/in-mem helper + `vault/router.py`) |
| Files | `src/core/cache.py`, `src/vault/composer.py`, `src/vault/router.py`, composer + router tests |
| Tests green | 24 composer + router tests at hand-off; full pytest 790 green (546 legacy + 191 Wave-2 module + 53 Wave-3 vault). |
| Algorithm | Implements `03-vault-generation.md` §10 verbatim: license intersection (403 / 409 typed codes), 24h per-buyer Redis cache, deterministic zip merge with per-buyer watermark stamped last, 60s presigned URL, `vault_downloads` audit row. |
| Open question carried | The composer's `_link_resolver_for_paths` doesn't strip `base/<slug>` prefixes on persona-side links — surfaced as "42 warnings" in the demo CLI's snapshot output. Filed for Wave 5 polish. |

### Curation (DevOps occupation vault) — shipped

Full diary at `team/dev-diary-devops-vault-wave3.md`.

| Aspect | Detail |
|---|---|
| Tasks | T-08 (`build_devops_vault.py` + `seed_data/devops/{occupation.yaml,cross-link-recipe.yaml}` + `.obsidian/graph.json` post-build injection) |
| Output | `skillsgit-curated/ai-devops-engineer` v1.0.0 with 30 members across 7 domains (`ci-cd`, `observability`, `incident`, `iac`, `security`, `cost`, `platform`); 60 cross-links emitted at script time. Two member substitutions vs. T-08 spec (ratified pre-wave). |
| Re-run safety | Idempotent — second `build_devops_vault.py` invocation produces no new rows. |
| Hand-off | Layer-A artifact green; Wave 4 T-12 builds the persona that overlays it. |

### Orchestrator — Wave 3 close-out

- Mounted the vault router in `apps/api/src/main.py`.
- Full pytest re-run: **790 tests green**.
- Wave 3 marked done; Wave 4 dispatched.

## Wave 4

### Curation (DevOps persona seed) — shipped

Full diary at `team/dev-diary-devops-persona-wave4.md`.

| Aspect | Detail |
|---|---|
| Tasks | T-12 (`@jane-devops-demo/incident-veteran` persona — 7 hand-authored neuron `.skills.md` files + `persona.yaml` + `build_devops_persona.py`) |
| Neurons | Flaky tests after Redis upgrade, on-call rotation handoff, blue/green rollback at 3am, cost spike egress debug, secret rotation zero-downtime, dashboard cardinality cleanup, paging policy rewrite. Each covers a T-14 demo scenario. |
| Sample data | Every public-facing field carries explicit "SAMPLE DATA / not a real practitioner" language per ADR-016 Q-4. |
| Re-run safety | Second `build_devops_persona.py` invocation is a no-op. |
| Hand-off | Layer-B artifact green; Wave 4 T-13 demo CLI loads it. |

### Backend (Layer-C demo CLI) — shipped

Full diary at `team/dev-diary-demo-cli-wave4.md`.

| Aspect | Detail |
|---|---|
| Tasks | T-13 (`scripts/demo_devops_agent.py` + `src/core/anthropic.py` shared SDK factory + `seed_data/demo/prompts.yaml`) |
| Modes | `--prompt` live mode (calls Claude with neuron index + renders consulted-neurons table); `--snapshot-only` (prints the composed-vault listing for T-14's snapshot diff). |
| Reference framing | Banner on every run: "== REFERENCE LOADER == (not a hosted runtime)" per ADR-018 + `prompts/00-vision.md` lines 64-66. |
| Open question carried | The composed-vault "Manifest warnings: 42" line — flagged as the symptom of the Wave-3 composer's `base/<slug>` link resolver gap. Wave 5 Polish 2 fixes this. |
| Hand-off | Layer-C reference loader green; the end-to-end pipeline (occupation + persona → composed bundle → Claude → attributed answer) runs against the dev stack. |

### Orchestrator — Wave 4 close-out

- No new routers (T-13 is a script, not an HTTP endpoint).
- Full pytest re-run: **802 tests green** (790 + 12 new T-13 snapshot + supporting tests).
- Wave 4 marked done; Wave 5 dispatched.

## Wave 5

### QA — shipped

Full diary at `team/dev-diary-qa-wave5.md`.

| Aspect | Detail |
|---|---|
| Tasks | T-14 (integration test fleet + snapshot fixtures + CI workflow + 6 polish items + test-plan flips) |
| Tests added | 11 new integration tests across `tests/integration/test_{occupation,persona,capture,vault_compose,full_demo_pipeline,vault_snapshots}_flow.py` + 5 new `_parse_consulted_block` unit tests + 1 attachment finalize test = 17 new tests. Pipeline total: **809 green** (vs. Wave-4 baseline 802). |
| Polish landed | (1) `validate_vault(mode='persona')` parameter — base/* targets tolerated in persona mode. (2) Composer `_link_resolver_for_paths` rewrites `base/<slug>` → real path + `_merge_manifests` drops stale persona-side warnings — composed-manifest warnings drop to **0** for the demo seed. (3–6) Parser unit tests, Linux CI smoke, cache TTL test strategy, attachment-bytes finalize coverage. |
| CI | `.github/workflows/team-smoke.yml` — nightly cron `17 3 * * *` UTC + per-PR runs + manual dispatch. Postgres 16 + Redis 7 service containers; `SKG_CAPTURE_LLM_STUB=1`; `ANTHROPIC_API_KEY=""` (snapshot-only in CI). |
| Snapshot fixtures | `tests/fixtures/vaults/{expected-devops-vault,expected-devops-persona,expected-composed}/*` — regenerable via two env vars (`UPDATE_VAULT_SNAPSHOTS=1`, `UPDATE_DEMO_PIPELINE_FIXTURE=1`). |
| Test-plan flips | T-01..T-08, T-12..T-14 all flipped to `passed`. T-09/T-10/T-11 stay `pending` (deferred frontend). T-15 was the parallel QA-Docs agent (this entry). |
| Hand-off | Cycle-1 MVP gate green on the critical path. Composer warnings → 0. Open questions for Cycle 2 enumerated below. |

### QA / Docs — shipped (this entry)

Diary at `team/dev-diary-docs-wave5.md`.

| Aspect | Detail |
|---|---|
| Tasks | T-15 (`docs/vault-format.md` + `docs/capture-howto.md` + `docs/changelog.md` Cycle-1 entry + this dev-diary close-out + retrospective) |
| Files | `docs/vault-format.md` (new) — buyer-facing format spec with manifest example, attribution + wiki-link + watermark sections, ~50-line Python reference loader, schema-evolution policy. `docs/capture-howto.md` (new) — 1-page creator walkthrough with the `2024-08-flaky-tests-after-redis-upgrade` neuron as a complete worked example. `docs/changelog.md` (extended) — appended `2026-05-26 — Cycle 1: Occupations + Personas` section listing 5 highlights, the 5 new optional `skills.md` fields, the 18 ADRs, the Frontend deferral, and the try-it bash recipe. `team/dev-diary.md` (this update) — added Wave 3/4/5 sections, flipped progress table, added retrospective. `team/dev-diary-docs-wave5.md` (this agent's diary). |
| Style discipline | Matched existing `docs/api-style.md` tone (tight, scannable, "canonical source: …" pointer at the top of each doc); reused vocabulary from `team/decisions.md` (ADR names, `kind=` enum values, `composition_role`); all Python and bash samples paste from working code in the repo. |
| Cross-checks | Every file path referenced verified to exist in the repo. The worked example in `capture-howto.md` is the `2024-08-flaky-tests-after-redis-upgrade.skills.md` neuron verbatim from the seed. The vault format doc's example folder tree reflects the **actual** code-emitted layout (`domains/<domain>/<slug>.md`, not the spec's older `base/<slug>` form) — flagged as a Cycle-2 cross-doc reconciliation candidate. |
| Hand-off | T-15 row in `team/test-plan.md` is ready for QA's sibling agent to flip to `passed` (or the test-plan auto-marks via the docs-existence smoke). All five Cycle-1 deliverables landed. |

### Orchestrator — Wave 5 close-out

- No router changes; all Wave-5 work is tests + fixtures + CI + docs.
- Full pytest pass: **809 green** (QA's run).
- CI workflow `.github/workflows/team-smoke.yml` live.
- `cycle-1-plan.md` Wave 5 marked done; Cycle 1 closed.

## Cycle progress vs plan

Mirrors `team/cycle-1-plan.md` §Wave-status log.

| Wave | State | Started | Completed | Headline |
|---|---|---|---|---|
| 1 | **done** | 2026-05-26 | 2026-05-26 | Backend (migrations + validator + spec) ✓ ; QA-Docs (test-plan + diary) ✓ ; Curation-research (inventory + 30 slug verify + 60 cross-links) ✓ |
| 2 | **done** | 2026-05-26 | 2026-05-26 | Occupations 55 + Personas 59 + Capture 77 = 191 module tests; 546 legacy pass; routers mounted; alembic-on-postgres verified; `NeuronBlock.context` removed |
| 3 | **done** | 2026-05-26 | 2026-05-26 | Vault builder (53 tests) + composer (24 tests) + DevOps occupation vault (30 members across 7 domains, 60 cross-links); composer + builder mounted; alembic clean |
| 4 | **done** | 2026-05-26 | 2026-05-26 | `@jane-devops-demo/incident-veteran` persona seeded (7 hand-authored neurons); Layer-C `demo_devops_agent.py` CLI runs end-to-end + snapshot mode wired |
| 5 | **done** | 2026-05-26 | 2026-05-26 | QA: 13 integration tests + snapshot fixtures + nightly CI workflow + 6 polish items (incl. composer `base/*` link fix; warnings → 0). QA-Docs: `docs/vault-format.md` + `docs/capture-howto.md` + changelog + this close-out + retrospective. |

## Open questions queue

Append-only. Each entry: `[origin] — question — who answers`.

- **O-1** — [Backend Wave 1] Router mounting strategy at Wave 2 spawn. Three Backend agents (T-03/T-04/T-05) will each add an `include_router` call to `apps/api/src/main.py` in parallel worktrees. Confirm the merge strategy is "last write wins, conflicts resolve trivially" per the cycle-1-plan's worktree rationale. — **Architect to confirm at Wave 2 spawn.**
- **O-2** — [Backend Wave 1] `finalized_neuron_skill_id` ondelete semantics. Backend chose `SET NULL` so neuron deletion preserves capture-session audit row; spec was silent. Confirm or correct. — **Architect.**
- **O-3** — [Backend Wave 1] `pnpm codegen` is still placeholder; Pydantic↔Zod parity is hand-maintained. Either build a real codegen step or document the "edit in both places" discipline. — **QA/Docs + Backend to route as Wave 5 chore (see R-2 in test-plan).**
- **O-4** — [Backend Wave 1] `LinkRelation` enum extensibility. Closed enum on both sides today. If Curation introduces `requires` / `supersedes` later, it needs coordinated Pydantic + Zod + spec amendment. Flag as likely or unlikely? — **Curation-research / Architect.**
- **O-5** — [Backend Wave 1] Capture quota Redis-key prefix. Backend suggests `capture:quota:{creator_id}:{yyyy-mm}` with 32-day TTL. Confirm for T-05 implementation. — **Backend-C (Wave 2) to lock in; Architect to acknowledge.**
- **O-6** — [QA Wave 1] `NeuronBlock.context` extension. Backend added optional `context: str | None` to the published `neuron` frontmatter block; ADR-009 defines exactly 5 fields without `context`. Either amend ADR-009 or remove from `NeuronBlock` before T-12 seed neurons use it. — **Architect.**
- **O-7** — [QA Wave 1] Skill-count drift: brief says 456, Backend reports 452, live filesystem under `apps/api/scripts/seed_data/synth/` is 450. T-01/T-02 acceptance criteria reference "456" verbatim. — **Curation-research to reconcile; Architect to amend brief or QA to amend acceptance text after.**

## How to read this file

This is the **chronological journal** for Cycle 1. Three companion files: `team/decisions.md` is the **why** log (append-only ADRs). `team/test-plan.md` is the **how-do-we-know-it-works** log (acceptance matrix + risks). This file is the **what-happened** log — Wave-by-Wave records of shipped work, broken work, and open questions, plus the cycle progress table. End-of-cycle, this file's `## Cycle 1 charter` and `## Cycle progress vs plan` sections drive the retrospective; the open-questions queue rolls forward into Cycle 2 planning where unanswered.

## Cycle 1 retrospective

Closed 2026-05-26 after five waves. End-state: 12 of 15 tasks landed (T-09 / T-10 / T-11 frontend deferred per the "fastest path to Layer C" rule); 809 tests green; the demo CLI loads a composed AI DevOps Engineer + Incident Veteran vault and returns an attributed answer; composer warnings drop to 0 for the demo seed.

### What worked

- **Spec-first (Architect cycle) prevented backtrack.** The eight `team/` planning files plus the 18 ADRs in `decisions.md` were written before any implementation agent spawned, with `06-open-questions.md` as a gating artifact the user explicitly approved. Result: zero re-derivation of data-model choices across the five Backend agents; every persona row, capture session, and vault build threads through the same `skills.kind` discriminator agreed in ADR-004.
- **Per-wave gate + dev-diary discipline kept context cost manageable.** Each wave's agents handed off to the next via a sibling `dev-diary-<role>-wave<N>.md` file rather than carrying the whole prior context. Wave 5 read the QA + Docs briefs cold, ingested the relevant siblings, and produced consistent code/docs. The pattern is reusable for Cycle 2.
- **Sibling-mirror agent pattern produced consistent code.** Personas (T-04) and Capture (T-05) both followed Occupations (T-03) as a structural template — same `schemas.py` / `service.py` / `router.py` / `tests/` layout, same `AppError`-derived exception hierarchy, same `ConfigDict(from_attributes=True)` + `extra="forbid"` Pydantic discipline. Result: 191 module tests across three new contexts written by three agents in parallel, with no merge collisions on shared utilities.
- **Reference-loader framing kept the demo CLI honest.** ADR-018 + the explicit "== REFERENCE LOADER == (not a hosted runtime)" banner on `demo_devops_agent.py` made it impossible to drift into building a hosted agent runtime under the demo's cover. The CLI is small (≈1000 lines including docstrings) and the boundary is documented in code, brief, and docs.
- **Idempotent build scripts paid for themselves twice.** Both `build_devops_vault.py` and `build_devops_persona.py` were exercised twice in their authoring waves (first build + re-build for idempotency check) and remain re-runnable from a populated DB. That property let QA's integration tests and the docs agent's worked example pull from the same canonical artifacts without DB-state coordination.

### What didn't

- **`pnpm codegen` is still a placeholder.** Backend Wave 1 hand-maintained Zod mirrors of the Pydantic models; O-3 in the open-questions queue flagged this but Wave 5 didn't pick it up (out of T-14/T-15 scope). Pydantic↔Zod drift is a real Cycle-2 risk now that two product types (occupations, personas) share the schema.
- **Frontend deferral means the demo is CLI-only.** T-09 (capture UX), T-10 (persona dashboard), T-11 (marketplace occupation page) all sit at `pending` in `test-plan.md`. The end-to-end user journey (creator captures → publishes → buyer browses → composes vault → agent answers) is provable on paper + via CLI, but not clickable in a browser. This was the correct trade for Cycle 1 timing per the "fastest path to Layer C" rule, but lands as the obvious Cycle 2 priority.
- **"In parallel" agent dispatches were sometimes sequential in practice.** Wave 2's three Backend agents (Occupations/Personas/Capture) and Wave 3's two Backend agents (builder/composer) were specified parallel but ran with significant turn-taking due to single-orchestrator scheduling. Flag for orchestrator improvement: real isolated worktrees + true parallel dispatch would have shortened both waves substantially.

### Cycle 2 candidates

Drawn from the open-questions queue above + the "Open questions for Cycle X" sections in every sibling dev-diary, deduplicated:

- **Frontend completion (T-09, T-10, T-11).** Capture UX, persona dashboard, marketplace occupation + persona pages. The data + APIs are ready; everything is wireframed in `04-capture-flow.md` §1.
- **Real `pnpm codegen` step.** Replace the hand-maintained Zod mirror with a generated artifact from the Pydantic source (or a single source-of-truth schema both sides build from). Closes O-3.
- **Paid personas + creator revenue split.** ADR-016 Q-1 deferred paid personas; persona pricing model + Stripe Connect transfer_data wiring is the obvious Cycle-2 lift. The data model already supports it.
- **BYOK for capture LLM.** ADR-008 + ADR-016 Q-2 deferred BYOK; a `creator_api_keys` table + per-call key selection unblocks creators who hit the 10-captures/month free cap.
- **MCP delivery mode.** ADR-001 explicitly defers MCP to Phase 2. The vault-builds artifact model was designed to be served either way; an MCP transport layer over the same `vault_builds` row is the migration path.
- **Real-DB-driven snapshot tier in CI.** QA Wave-5 §Open question 2: the existing snapshot fixtures use a 3-skill subset; a third tier exercising the real 30-skill curated build against Postgres in CI would catch curated-seed drift.
- **Cross-process compose lock + Redis backend coverage.** Composer Wave-3B §Open questions 5, 6: add Redis SETNX on the compose key + an integration test that drives the Redis backend end-to-end (in-memory backend is what every current test uses).
- **Persona-build-missing UX signal.** Composer Wave-3B §Open question 7: silent skip of a persona license whose latest build is `pending` should surface as a buyer-facing "persona build pending" badge on the marketplace download page.
- **Persona manifest carries parent `handle/slug`.** QA Wave-5 §Open question 3: the parent_occupation_id UUID in persona manifests is opaque without a DB lookup; adding the parent's stable handle/slug pair makes buyer-side "what does this overlay" reasoning trivial.
- **Watermark format constant.** QA Wave-5 §Open question 8: export `WATERMARK_FORMAT` from `delivery.watermark` so tests + tooling depend on a constant rather than regex-matching the comment shape.
- **Snapshot regen env-var unification.** QA Wave-5 §Open question 10: replace `UPDATE_DEMO_PIPELINE_FIXTURE` + `UPDATE_VAULT_SNAPSHOTS` with a single `UPDATE_SNAPSHOTS=all|pipeline|vaults` convention.
- **Vault format spec ↔ implementation reconciliation.** Docs Wave-5 noted the spec in `team/03-vault-generation.md` still describes a `base/<slug>` folder layout while the actual builder emits `domains/<domain>/<slug>.md`. Either update the spec (purely documentation) or rename the emitted folder (broader impact). Decide before docs go public.
- **`LinkRelation` enum extensibility.** Open question O-4: closed enum on both sides today; adding `requires` / `supersedes` later needs a coordinated Pydantic + Zod + spec amendment. Decide at start of Cycle 2 whether to widen pre-emptively.
- **Skill-count source-of-truth fix.** Open question O-7: brief said 456, repo currently exposes 452 in tests / 450 in `seed_data/synth/`. Reconcile once and put a single authoritative count in `team/inventory-synth.md`.
- **PII detector real-world tuning.** `capture/pii.py` ships the spec's pattern set; running it against a corpus of real captured neurons during Cycle 2 will surface false-positive/false-negative tuning needs (e.g. customer-name deny-list per ADR-016 Q-5 currently TBD).
