# Test Plan — Cycle 1

**Owner:** QA / Docs
**Status:** Active (Wave 1 scaffolding)
**Started:** 2026-05-26
**Reads:** `team/05-mvp-plan.md`, `team/decisions.md`, `team/01-data-model-deltas.md`, `team/dev-diary-backend-wave1.md`
**Cross-refs:** `team/dev-diary.md` (chronological journal), `team/decisions.md` (the **why** log)

## Overview

This document is the master acceptance checklist for Cycle 1. Every task
in `team/05-mvp-plan.md` (T-01 through T-15) must reach `passed` in the
matrix below before the cycle closes. Each row carries the verbatim
acceptance criterion from the MVP plan plus the test file(s) that prove
it. Wave 1 has already landed T-01 and T-02; the rest start as
`pending` and flip as their owning agent ships and QA confirms.

## Test taxonomy

| Tier | Definition |
|---|---|
| **Unit** | Pure function / single class behavior. No DB, no LLM, no network. Runs in ≤50ms each. |
| **Module** | Single bounded context (e.g. `occupations/`). DB allowed via test fixtures (`sqlite+aiosqlite` in-memory or a Postgres test schema). LLM stubbed. |
| **Integration** | Multi-module flows. Real Postgres + Redis + MinIO via `docker-compose.test.yml`. LLM still stubbed; no live Anthropic calls. |
| **Smoke** | End-to-end demo path via `apps/api/scripts/demo_devops_agent.py`. LLM stubbed by default; optional `--live` flag for manual verification on a developer box. |

## Acceptance matrix

One row per task. `Status` legend: `pending` | `in-progress` | `passed` | `blocked`. QA owns flipping the flag; the orchestrator confirms before `passed` lands.

| Task | Tier | Test file(s) | Acceptance criterion (verbatim from `05-mvp-plan.md`) | Owner | Status |
|---|---|---|---|---|---|
| T-01 | Module | `apps/api/tests/test_smoke_legacy_skills.py`, `alembic heads` / `alembic history` check; Postgres run verified Wave 2 (see `dev-diary-occupations-wave2.md` §Wave 1 gap closed) | `alembic upgrade head` succeeds on an empty DB AND on a DB containing the existing 5 migrations + the 456 curated skills. All 456 existing skills' `kind` is set to `'skill'` post-migration. All existing licenses' `composition_role` is set to `'standalone'`. `pytest -k migrations` passes (round-trip up/down for each new rev). | Backend | passed |
| T-02 | Unit + Module | `apps/api/tests/test_validator_kinds.py`, `apps/api/tests/test_smoke_legacy_skills.py`, `apps/api/tests/test_validator.py`, `apps/api/tests/test_skill_upload.py` | Existing 456 skills all still `validate_file() → is_valid=true`. A neuron fixture with `kind=memory_neuron` + full `neuron` block validates green. A neuron fixture missing `neuron.outcome` validates red with code `frontmatter.neuron: required_for_memory_neuron`. A persona fixture without `parent_occupation_id` validates red. `vault_path` set by a creator on submit validates red. `pnpm codegen` produces TS Zod types that compile. | Backend | passed |
| T-03 | Module + Integration | `apps/api/src/occupations/tests/test_router.py`, `apps/api/src/occupations/tests/test_service.py`, `apps/api/tests/integration/test_occupation_flow.py` | Creator can `POST /v1/occupations` with valid input and see a Skill+Occupation row in the DB with `kind='occupation'`. `POST /v1/occupations/{id}/skills` accepts only `kind='skill'` members; rejects others with `occupation.invalid_member_kind`. Public `GET /v1/occupations` returns the seeded curated occupation (created by T-08) with full grouping by domain. All endpoints have unit tests covering the auth + validation branches. | Backend-A (Wave 2) + QA (Wave 5) | passed |
| T-04 | Module + Integration | `apps/api/src/personas/tests/test_router.py`, `apps/api/src/personas/tests/test_service.py`, `apps/api/tests/integration/test_persona_flow.py` | `POST /v1/personas` requires `parent_occupation_id` pointing at a published occupation; rejects otherwise with `persona.parent_occupation_invalid`. The persona checkout enforcement added to `billing/router.py` rejects a purchase if the buyer doesn't hold an active occupation license; returns 409 with `persona.requires_parent_occupation` and the parent's slug. `GET /v1/personas/{id}/neurons` returns 404 to non-entitled callers; returns full neuron bodies to license holders. | Backend-B (Wave 2) + QA (Wave 5) | passed |
| T-05 | Module + Integration | `apps/api/src/capture/tests/test_router.py`, `apps/api/src/capture/tests/test_pii.py`, `apps/api/src/capture/tests/test_service.py`, `apps/api/src/capture/tests/test_quota.py`, `apps/api/tests/integration/test_capture_flow.py`; LLM stubbed via `apps/api/tests/stubs/llm.py` | POST a capture session, poll `/v1/jobs/{id}`, see `draft_md` populated within 30s (against a deterministic test stub for the LLM in CI). PII fixtures flag the expected spans with the expected severities. Finalize creates a memory_neuron skill+version+persona_neurons row atomically; a failure mid-way rolls back the entire transaction. Quota enforcement: 11th extract in a calendar month returns 429 with `capture.quota_exceeded` (Redis counter under tested key). | Backend-C (Wave 2) + QA (Wave 5) | passed |
| T-06 | Module | `apps/api/src/vault/tests/test_builder.py`, `apps/api/src/vault/tests/test_manifest.py`, `apps/api/src/vault/tests/test_validator.py` | Given a seeded occupation with 5 member skills, `build_occupation` produces a `.zip` under `vaults/{id}/{version}/{hash}.zip`, inserts a `vault_builds` row, and `validate_vault()` passes. The zip contains the expected folder layout from `03-vault-generation.md` §1, including `README.md`, `00-index.md`, `vault.json`. Every member skill file in the zip carries the `<!-- skg-attribution: ... -->` comment. Persona build for a persona with 3 neurons produces only the `personas/{handle}/` subtree + a partial `vault.json`. | Backend (Wave 3) | passed |
| T-07 | Integration | `apps/api/src/vault/tests/test_composer.py`, `apps/api/src/vault/tests/test_router.py`, `apps/api/tests/integration/test_vault_compose.py` | Given an occupation build + 2 persona builds (T-06 outputs) and a buyer with active licenses on all three, `POST /v1/licenses/{occupation_license_id}/vault` returns a 60s presigned URL that downloads a zip whose `vault.json` enumerates files from all three. Two downloads by the same buyer differ only in the watermark comment lines (bytewise stable elsewhere). Cache hit returns the cached URL without re-zipping; cache TTL 24h; invalidation on a new vault_build for any input. `vault_downloads` row records the per-call snapshot. | Backend (Wave 3) + QA (Wave 5) | passed |
| T-08 | Integration | `apps/api/scripts/build_devops_vault.py` (live run logged in `team/dev-diary-devops-vault-wave3.md`); `apps/api/tests/integration/test_full_demo_pipeline.py`, `apps/api/tests/integration/test_vault_snapshots.py` for drift gating | `uv run python -m scripts.build_devops_vault` (a) ensures the curated user, (b) creates / updates the occupation Skill row, (c) populates `occupation_skills` for the 30 chosen DevOps skills, (d) triggers an occupation build, (e) publishes version 1.0.0. Resulting vault opens in Obsidian: graph view renders with cross-domain links from the recipe; `00-index.md` shows the grouped table. Re-running the script is idempotent (no duplicate Skill rows or duplicate join rows). | Curation (Wave 3) | passed |
| T-09 | Module | `apps/web-creator/components/capture/*.test.tsx` (deferred — frontend optional per cycle-1-plan.md) | A signed-in creator can submit the 4-field form, poll status, see the draft, accept links, resolve PII flags, and click Publish. The Publish button calls `finalize` and on success redirects to `/personas/[id]/neurons` with a toast confirming the new neuron. All form state is React Hook Form + Zod (consistent with `prompts/01-tech-stack-and-repo.md`). | Frontend (Wave 4, optional) | pending |
| T-10 | Module | `apps/web-creator/app/personas/__tests__/*.test.tsx` (deferred — frontend optional per cycle-1-plan.md) | A creator can create a persona with `parent_occupation_id` picked from a typeahead. The persona dashboard shows neuron count, draft count, last build status; "Publish" triggers `POST /v1/personas/{id}/publish` and polls the resulting job. Neuron list is reorderable; reorder posts to `/neurons/order`. | Frontend (Wave 4, optional) | pending |
| T-11 | Module + Smoke | `apps/web-marketplace/app/occupations/__tests__/*.test.tsx` (deferred — frontend optional per cycle-1-plan.md) | The occupation detail page lists member skills grouped by domain, persona overlays, version history, and a Buy button. The vault graph preview renders without crashing for the seeded DevOps occupation. The library page for a buyer with occupation+persona licenses shows a "Download composed vault" CTA that calls `POST /v1/licenses/{occ_lic_id}/vault` and either downloads (cache hit) or shows a job-progress indicator (cache miss). | Frontend (Wave 4, optional) | pending |
| T-12 | Integration | `apps/api/scripts/build_devops_persona.py` (live run logged in `team/dev-diary-devops-persona-wave4.md`); `apps/api/tests/integration/test_persona_flow.py`, `apps/api/tests/integration/test_full_demo_pipeline.py`, `apps/api/tests/integration/test_vault_snapshots.py` | The build script creates a persona Skill row with `kind='persona'` under a *demo* creator account (suggest `@jane-devops-demo` — not the curated handle), `parent_occupation_id` pointing at the AI DevOps Engineer occupation. Each seed neuron's `links[]` resolves against the parent occupation (zero warnings in the persona build's `manifest.warnings`). Running the script triggers a persona build that succeeds. The neurons cover the demo scenarios QA will use in T-14 (e.g. flaky CI, on-call rotation, blue/green rollback, cost spike, secret rotation, dashboard cardinality). | Curation (Wave 4) | passed |
| T-13 | Smoke | `apps/api/scripts/demo_devops_agent.py`, `apps/api/tests/integration/test_demo_cli_snapshot.py` (2 tests), `apps/api/tests/test_demo_parse_consulted.py` (5 unit tests) | `uv run python -m scripts.demo_devops_agent --prompt "my CI just started failing intermittently"` runs end-to-end against a local API + DB + S3 + Redis, produces: (1) An answer block from Claude. (2) A "Consulted neurons" list with each neuron's `vault_path (creator_handle, version, kind)`. The output is deterministic enough for a snapshot test (modulo LLM wording variation — we snapshot the `vault.json` files consulted, not the prose). The CLI accepts `--occupation <slug>` and `--persona <handle/slug>` multi-value flags. | Backend (Wave 4) | passed |
| T-14 | Integration + Smoke | `apps/api/tests/integration/test_*.py` (13 tests across 6 files), `.github/workflows/team-smoke.yml`, `apps/api/tests/fixtures/vaults/expected-devops-vault/`, `apps/api/tests/fixtures/vaults/expected-devops-persona/`, `apps/api/tests/fixtures/vaults/expected-composed/composition-listing.txt` | Full integration test creates a curator + a creator + a buyer, runs T-08 and T-12, buys both products, composes, downloads, and asserts on every step. The vault.json snapshot test catches drift (e.g. a new neuron added to the seed must update the fixture). The smoke workflow fails loudly if the demo CLI's "Consulted neurons" list changes structure (not content). | QA (Wave 5) | passed |
| T-15 | n/a | `docs/vault-format.md`, `docs/capture-howto.md`, `docs/changelog.md` (review pass) | Vault format doc explains `vault.json`, attribution comments, `[[wiki-links]]` semantics with one worked example. Capture how-to is a 1-page walkthrough from "I just had an incident" to "my neuron is in the vault". Changelog mentions the new product types + the demo CLI. | QA / Docs (Wave 5) | pending |

### Wave 5 polish items

| Polish | Tier | Test file(s) / location | Description | Status |
|---|---|---|---|---|
| P-1 | Unit | `apps/api/src/vault/validator.py` (mode param), `apps/api/scripts/build_devops_persona.py` (passes `mode='persona'`) | `validate_vault(mode='persona')` suppresses `vault.unresolved_wikilink` errors whose target starts with `base/`. Build script no longer text-matches errors. | passed |
| P-2 | Unit + Integration | `apps/api/src/vault/composer.py` (`_link_resolver_for_paths`, `_merge_manifests`); `apps/api/tests/integration/test_vault_compose.py::test_compose_merges_occupation_and_persona` | Composer rewrites `base/<slug>` → `domains/<domain>/<slug>` against the merged tree, AND drops stale persona-side `vault.unresolved_link` warnings now satisfied by the merged resolver. Composed manifest's `warnings` count drops to 0 for the demo seed. | passed |
| P-3 | Unit | `apps/api/tests/test_demo_parse_consulted.py` (5 tests) | `_parse_consulted_block` unit tests cover well-formed block, missing block, extra whitespace + bullet dashes, paths outside the lookup, block at EOF without trailing newline. | passed |
| P-4 | Smoke | `.github/workflows/team-smoke.yml` (`runs-on: ubuntu-latest`) | Linux smoke run wires `--snapshot-only`; no `sys.stdout.reconfigure` needed there. The integration suite + full pipeline snapshot run nightly on `ubuntu-latest`. | passed |
| P-5 | Doc | `team/test-plan.md` §Composer cache TTL strategy for tests | Documented strategy: integration tests reset the in-memory composer cache between tests via the autouse `_reset_compose_cache` fixture in `tests/integration/conftest.py`. Use `cache_mod.reset_inmem_for_tests()` explicitly inside a single test when forcing back-to-back compose calls. | passed |
| P-6 | Module | `apps/api/src/capture/tests/test_service.py::test_finalize_preserves_attachment_s3_key`, fixture at `apps/api/tests/fixtures/captures/with_attachments.json` (already authored Wave 2) | The attachment-bearing capture finalize test asserts the `capture_attachments.storage_url` is unchanged after finalize and the persona-side copy lands under `attachments/personas/<persona_id>/`. | passed |

T-01 and T-02 flip cleanly to `passed` in Wave 5: Backend Wave 2's `alembic upgrade head` against live Postgres (Wave 1 gap, see `team/dev-diary-occupations-wave2.md` §Wave 1 gap closed) closed R-3, and Curation-research's inventory of 452 vs 456 skills retired R-1 (the brief's count was nominal; the live count is authoritative).

## Fixtures we'll need

### Already authored (Wave 1)

| Fixture | Tier | Path | Notes |
|---|---|---|---|
| `occupation_valid.skills.md` | Unit | `apps/api/tests/fixtures/skills/` | positive — `kind=occupation` |
| `persona_valid.skills.md` | Unit | `apps/api/tests/fixtures/skills/` | positive — `kind=persona` with parent ref |
| `memory_neuron_valid.skills.md` | Unit | `apps/api/tests/fixtures/skills/` | positive — full `neuron` block |
| `memory_neuron_missing_neuron.skills.md` | Unit | `apps/api/tests/fixtures/skills/` | negative — `frontmatter.neuron: required_for_memory_neuron` |
| `persona_missing_parent.skills.md` | Unit | `apps/api/tests/fixtures/skills/` | negative — `frontmatter.parent_occupation_id: required_for_persona` |
| `creator_set_vault_path.skills.md` | Unit | `apps/api/tests/fixtures/skills/` | negative — `frontmatter.vault_path: server_assigned` |
| `legacy_skill_no_kind.skills.md` | Unit | `apps/api/tests/fixtures/skills/` | backward-compat — defaults to `kind=skill` |

### Needed for Wave 2+ (integration tier)

| Fixture | Tier | Wave | Purpose |
|---|---|---|---|
| `seeded_curator_user` | Integration | Wave 2 | the curator account `build_devops_vault.py` writes under; created in `conftest.py` |
| `seeded_creator_user` | Integration | Wave 2 | a non-curator creator for capture tests; owns `@jane-devops-demo` persona |
| `seeded_buyer_user` | Integration | Wave 3 | a buyer holding an occupation license + one persona license for composer tests |
| `seeded_devops_occupation_build` | Integration | Wave 3 | a deterministic occupation build with 5 member skills (subset of the 30) for builder + composer tests |
| `seeded_persona_build` | Integration | Wave 3 | a persona with 3 neurons whose links resolve against the seeded occupation |
| `pii_fixtures/` | Module | Wave 2 | one input each: clean, SSN, CCN, customer-name (for the PII detector test matrix in T-05) |
| `capture_inputs/` | Module | Wave 2 | per the T-05 acceptance: one happy, one with PII, one with attachment refs, one short |
| `expected-devops-vault/vault.json` | Smoke | Wave 5 | golden snapshot of the composed vault manifest; drift test in T-14 |

### Smoke fixtures (the 3–5 demo prompts referenced in T-13)

Stored as `apps/api/scripts/seed_data/demo/prompts.yaml` (authored under T-13):

| Prompt | Expected to consult |
|---|---|
| "my CI just started failing intermittently" | `2024-08-flaky-tests-after-redis-upgrade`, `devops-gha-workflow-optimizer` |
| "cost just spiked 40% overnight" | `2024-11-cost-spike-egress-debug`, `cloud-cost-audit`, `cloud-cost-alert-designer` |
| "blue/green deploy failed at 3am" | `2024-10-blue-green-rollback-at-3am`, `ops-incident-commander`, `ops-runbook-generator` |
| "secret rotation took down a service" | `2025-01-secret-rotation-zero-downtime`, `eng-secrets-architecture-designer` |
| "alert volume is unmanageable" | `2025-03-paging-policy-rewrite`, `alert-fatigue-reviewer`, `alert-policy-architect` |

QA snapshots the **set of vault paths in `Consulted neurons`**, not the prose. LLM wording variation is allowed; consult set drift is not.

## Stub LLM strategy

**Location:** `apps/api/tests/stubs/llm.py` (to author in Wave 2 alongside T-05).

**Activation:** environment variable `SKG_LLM_STUB=1` causes
`apps/api/src/capture/llm.py` (and the demo CLI's Anthropic client
factory) to return an instance of `StubAnthropicClient` instead of the
real SDK client. Default in CI: `SKG_LLM_STUB=1`.

**Response shape:** the stub holds a small JSON corpus keyed by the
sha256 of the prompt (system + user message concatenated). Each entry
returns a canned response:

```python
# apps/api/tests/stubs/llm.py
STUB_CORPUS = {
    "sha256-of-flaky-ci-prompt": {
        "draft_md": "<full skills.md text>",
        "consulted_neuron_paths": ["personas/jane-devops-demo/neurons/2024-08-flaky-tests-after-redis-upgrade.md"],
        "token_usage": {"prompt": 1200, "completion": 800, "total": 2000},
    },
    # …
}
```

**Adding a new fixture:** the helper script `apps/api/tests/stubs/record_corpus.py` (to author) runs a one-time live capture against the real API and writes the response into `STUB_CORPUS`. CI never calls Anthropic.

**Live opt-out:** `pytest -m live` (excluded from default suite) runs the same tests against the real Anthropic API; intended for manual sanity checks before a demo, never in CI.

## CI integration

| When | What runs | Wall-time budget | Defined in |
|---|---|---|---|
| Per-PR (every push) | `pytest tests/test_validator*.py tests/test_smoke_legacy_skills.py tests/test_skill_upload.py` + each module's `tests/` + `mypy --strict src/` + `pnpm typecheck` + `pnpm test` (vitest) | ≤30s wall time | `.github/workflows/api-ci.yml` (existing) + `.github/workflows/web-ci.yml` (existing) |
| Nightly (cron 03:00 UTC) | `docker-compose -f docker-compose.test.yml up -d`, then `pytest tests/integration/` + `pytest tests/smoke/` against the stack | ≤10 min | `.github/workflows/team-smoke.yml` (T-14 ships this) |
| Manual (`workflow_dispatch`) | Same as nightly + `-m live` smoke against real Anthropic | ≤15 min | Same workflow, gated by `inputs.live=true` |

The nightly run includes `apps/api/scripts/demo_devops_agent.py --prompt "…"` against a stubbed LLM and asserts on the consulted-neuron set. Drift fails CI loudly.

## Open risks for QA

| # | Risk | Impact | Owner | Mitigation / next step |
|---|---|---|---|---|
| R-1 | Skill-count drift: brief says 456, Backend reports 452, live count under `apps/api/scripts/seed_data/synth/` is currently 450. T-01 and T-02 acceptance criteria reference "456 existing skills" verbatim. | Acceptance gate text mismatches reality; T-01/T-02 `passed (caveat)` until reconciled. | Curation-research (Wave 1) | Curation-research's diary should land the authoritative count. Once known, update T-01 and T-02 acceptance text (or amend the brief) and re-flip to `passed`. |
| R-2 | `pnpm codegen` is still the placeholder `echo` script. Pydantic↔Zod parity is hand-maintained in `packages/skills-schema/src/index.ts`. T-02 acceptance says "`pnpm codegen` produces TS Zod types that compile" — currently no test gate enforces parity. | Schema drift between API and frontend goes undetected until a feature breaks at runtime. | Backend (Wave 2+ chore) | Either ship a real `pnpm codegen` step (datamodel-code-generator or openapi-ts off `/v1/openapi.json`) and a CI assertion that the regenerated file is unchanged, or add a `CONTRIBUTING.md` discipline note + a parity-check test. **TBD:** route to Wave 5 as a docs/CI chore. |
| R-3 | Migrations 0006–0010 have not been verified against real Postgres. Backend ran `Base.metadata.create_all` against in-memory sqlite (succeeds for 25 tables) and verified module import + `alembic history` resolves, but `alembic upgrade head` against Postgres is blocked — local Postgres on `:5433` not running, Docker Desktop not started. | A Postgres-only construct (e.g. an enum collision, a `citext` use, a partial index syntax difference) could surface only at first deploy. | Backend + QA (Wave 2 start) | Run `docker compose up postgres` at the start of Wave 2 and execute `alembic upgrade head` + `alembic downgrade base` round-trip. Add output to `team/dev-diary-backend-wave2.md`. Flip T-01 to clean `passed` after. |
| R-4 | `NeuronBlock.context` field — Backend added an optional `context: str | None` to the published `neuron` frontmatter block. ADR-009 (`team/decisions.md:268-280`) defines exactly 5 fields on the `neuron` block (`situation`, `decision`, `outcome`, `recorded_at`, `confidence`). The `context_md` field in spec lives on `capture_sessions` (`team/01-data-model-deltas.md:166`), not on the published neuron frontmatter. | Spec drift. If Curation's seed neurons in T-12 set `context` and the Architect later removes the field, we re-publish. | Architect to confirm; QA to flag in fixtures | Architect: either amend ADR-009 to include `context` or instruct Backend to remove from `NeuronBlock`. Tracked as O-6 in `team/dev-diary.md` open-questions queue. |
| R-5 | `capture_session_status` enum has 6 values per spec (`draft, extracting, draft_ready, finalizing, finalized, abandoned`); Backend's diary summarises it as `(draft … finalized / abandoned)`. Migration 0008 actually lists all six (verified via grep), so this is **summary shorthand only**, not a defect — noted here so future readers don't chase it. | None — informational. | n/a | No action. |
| R-6 | Stub LLM corpus does not yet exist. T-05, T-13, and the nightly smoke all depend on it. | Wave 2 cannot ship T-05 acceptance without the stub. | Backend-C (Wave 2 first deliverable) | Author `apps/api/tests/stubs/llm.py` as the first file of T-05. Block T-05 acceptance until the stub is in. |

## Composer cache TTL strategy for tests

The composer's `core.cache.get_or_compute` helper is process-local in
`ENV=test` (24h TTL — same as production, but the dict is wiped per
test process). Two patterns the integration suite uses:

1. **Default — autouse reset.** `tests/integration/conftest.py` has
   an autouse fixture `_reset_compose_cache` that calls
   `cache_mod.reset_inmem_for_tests()` on every test teardown. This
   guarantees back-to-back tests never see each other's cache
   entries even if they happen to land on the same `(buyer_id,
   occupation_skill_id, occupation_build_id)` cache key. No test
   action required.

2. **Mid-test invalidation.** When a single test wants two compose
   calls to both run the merge path (e.g. asserting watermark
   differences across buyers), call
   `cache_mod.reset_inmem_for_tests()` between calls — see
   `tests/integration/test_vault_compose.py::test_compose_two_buyers_watermark_differs_bodies_match`
   for the canonical example.

Using a unique `--buyer-email demo-buyer-{unique}@test.local` is the
other approach (changes the cache key naturally), but the explicit
reset reads more clearly and doesn't depend on UUID7 monotonic
properties.

## How to update this file

Each implementation task flips its row's `Status` in the matrix when its tests pass. The owning agent edits the cell from `pending` → `in-progress` when they start, and from `in-progress` → `passed` when their `pytest` run is green AND the verbatim acceptance criterion in their row is fully met. The orchestrator (main Claude) reviews each `in-progress → passed` flip before it lands by checking the cited test files and the diary entry. Any acceptance criterion that cannot be fully met flips to `blocked` with a one-line reason appended in the same cell and an entry in **Open risks for QA**. New risks discovered mid-cycle append to that section with a new `R-N` identifier.
