# 05 — Cycle-1 MVP Plan

**Owner:** Architect
**Status:** Proposed
**Reads:** every prior `team/` file.
**Cross-refs:** `team/README.md` for role definitions.

This is the task graph that turns the spec into a working
end-of-cycle-1 demo: a curated AI DevOps Engineer occupation vault
(Layer A), one sample persona overlay with 5–10 neurons (Layer B), and
a CLI demo that loads `base + persona` and returns an attributed
answer (Layer C).

Roles (from `team/README.md`):
- **Backend** — `apps/api/src/{occupations,personas,capture,vault}/`,
  migrations, validator extensions.
- **Frontend** — `apps/web-creator/app/{capture,personas}/`, plus a
  small vault-graph preview added to `apps/web-marketplace/`.
- **Curation** — `apps/api/scripts/build_devops_vault.py`, the
  cross-link recipe, the sample persona's seed neurons.
- **QA / Docs** — `team/test-plan.md`, fixtures, the demo script.

Effort scale (rough Claude-day equivalents on one focused agent):
- S = ≤ 1 day
- M = 1–3 days
- L = 3–6 days

The graph is topologically ordered below. Parallel tasks at the same
"layer level" are marked.

---

## Task graph at a glance

```
                ┌──────────────────────────────────────┐
                │ T-01 (Backend) migrations 0006-0010  │  M
                │ T-02 (Backend) validator extensions  │  S    parallel
                └──────────┬───────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   T-03 Occupations    T-04 Personas      T-05 Capture
   API + service (M)   API + service (M)  API + jobs (M)
        │                  │                  │
        └────────┬─────────┴─────────┬────────┘
                 ▼                   ▼
            T-06 Vault builder    T-07 Vault composer
            (Backend, L)          (Backend, M)
                 │                   │
                 └────────┬──────────┘
                          ▼
            T-08 Curation: build_devops_vault.py (Curation, M)
                          │
              ┌───────────┼───────────────┐
              ▼           ▼               ▼
         T-09 Capture  T-10 Persona   T-11 Marketplace
         web UI       admin UI       occupation page
         (Frontend M) (Frontend M)   (Frontend M)   parallel
              │           │               │
              └─────┬─────┴───────────────┘
                    ▼
              T-12 Sample persona seed neurons (Curation, S)
                    │
                    ▼
              T-13 Layer-C demo CLI (Backend, S)
                    │
                    ▼
              T-14 QA smoke + fixtures + test plan (QA, M)
                    │
                    ▼
              T-15 Docs: vault format, capture how-to (QA/Docs, S)
```

Critical path: **T-01 → T-06 → T-07 → T-08 → T-13**. Everything else
hangs off branches.

---

## T-01 — Migrations 0006 through 0010
- **Owner:** Backend
- **Files touched:**
  - `apps/api/alembic/versions/0006_occupations_and_kind.py` (new)
  - `apps/api/alembic/versions/0007_personas_and_neurons.py` (new)
  - `apps/api/alembic/versions/0008_capture.py` (new)
  - `apps/api/alembic/versions/0009_vault_builds_and_downloads.py` (new)
  - `apps/api/alembic/versions/0010_categories_seed_occupations_personas.py` (new)
  - `apps/api/src/skills/models.py` (add `kind` column + `SkillKind` enum)
  - `apps/api/src/billing/models.py` (add `composition_role`, `target_occupation_skill_id`)
  - new model modules: `apps/api/src/occupations/models.py`,
    `apps/api/src/personas/models.py`, `apps/api/src/capture/models.py`,
    `apps/api/src/vault/models.py`
- **Depends on:** none
- **Acceptance:**
  - `alembic upgrade head` succeeds on an empty DB AND on a DB
    containing the existing 5 migrations + the 456 curated skills.
  - All 456 existing skills' `kind` is set to `'skill'` post-migration.
  - All existing licenses' `composition_role` is set to `'standalone'`.
  - `pytest -k migrations` passes (round-trip up/down for each new rev).
- **Estimated effort:** M

## T-02 — Validator extensions for new optional frontmatter
- **Owner:** Backend
- **Files touched:**
  - `apps/api/src/skills/validator.py` (extend `SkillFrontmatter`)
  - `apps/api/tests/fixtures/skills/*` (new positive + negative fixtures)
  - `packages/skills-schema/` (regenerate Zod from updated Pydantic — `pnpm codegen`)
- **Depends on:** none (parallel with T-01)
- **Acceptance:**
  - Existing 456 skills all still `validate_file() → is_valid=true`.
  - A neuron fixture with `kind=memory_neuron` + full `neuron` block
    validates green.
  - A neuron fixture missing `neuron.outcome` validates red with code
    `frontmatter.neuron: required_for_memory_neuron`.
  - A persona fixture without `parent_occupation_id` validates red.
  - `vault_path` set by a creator on submit validates red.
  - `pnpm codegen` produces TS Zod types that compile.
- **Estimated effort:** S

## T-03 — Occupations module: models, schemas, service, router
- **Owner:** Backend
- **Files touched:**
  - `apps/api/src/occupations/` — new module (`__init__.py`, `models.py`
    [partial, side table only — main `Skill` model lives in skills/],
    `schemas.py`, `service.py`, `router.py`, `tests/`)
  - `apps/api/src/main.py` (mount the new router)
- **Depends on:** T-01
- **Acceptance:**
  - Creator can `POST /v1/occupations` with valid input and see a
    Skill+Occupation row in the DB with `kind='occupation'`.
  - `POST /v1/occupations/{id}/skills` accepts only `kind='skill'`
    members; rejects others with `occupation.invalid_member_kind`.
  - Public `GET /v1/occupations` returns the seeded curated occupation
    (created by T-08) with full grouping by domain.
  - All endpoints have unit tests covering the auth + validation
    branches.
- **Estimated effort:** M

## T-04 — Personas module: models, schemas, service, router
- **Owner:** Backend
- **Files touched:** mirror of T-03 under `apps/api/src/personas/`
- **Depends on:** T-01 (model only; the publish path uses T-06)
- **Acceptance:**
  - `POST /v1/personas` requires `parent_occupation_id` pointing at a
    published occupation; rejects otherwise with
    `persona.parent_occupation_invalid`.
  - The persona checkout enforcement added to `billing/router.py`
    rejects a purchase if the buyer doesn't hold an active occupation
    license; returns 409 with `persona.requires_parent_occupation` and
    the parent's slug.
  - `GET /v1/personas/{id}/neurons` returns 404 to non-entitled
    callers; returns full neuron bodies to license holders.
- **Estimated effort:** M

## T-05 — Capture module: models, schemas, service, router, Arq jobs, LLM client
- **Owner:** Backend
- **Files touched:**
  - `apps/api/src/capture/` — new module
  - `apps/api/src/capture/llm.py` — Anthropic SDK wrapper with prompt
    template from `04-capture-flow.md` §3
  - `apps/api/src/capture/jobs.py` — Arq job `extract_neuron`
  - `apps/api/src/capture/pii.py` — the PII detector set
  - `apps/api/tests/fixtures/captures/*` — at least 4 input fixtures
    (one happy, one with PII, one with attachment refs, one short)
- **Depends on:** T-01, T-02
- **Acceptance:**
  - POST a capture session, poll `/v1/jobs/{id}`, see `draft_md` populated
    within 30s (against a deterministic test stub for the LLM in CI).
  - PII fixtures flag the expected spans with the expected severities.
  - Finalize creates a memory_neuron skill+version+persona_neurons row
    atomically; a failure mid-way rolls back the entire transaction.
  - Quota enforcement: 11th extract in a calendar month returns 429 with
    `capture.quota_exceeded` (Redis counter under tested key).
- **Estimated effort:** M

## T-06 — Vault builder (single skill bundle producer)
- **Owner:** Backend
- **Files touched:**
  - `apps/api/src/vault/builder.py` (new) — `build_occupation`,
    `build_persona`
  - `apps/api/src/vault/manifest.py` (new) — `vault.json` writer +
    schema in `apps/api/src/vault/schema/vault-manifest-v1.json`
  - `apps/api/src/vault/jobs.py` (new) — Arq job wrappers
  - `apps/api/src/vault/validator.py` (new) — post-build vault integrity
    check
  - `apps/api/tests/vault/test_builder.py`
- **Depends on:** T-03, T-04
- **Acceptance:**
  - Given a seeded occupation with 5 member skills, `build_occupation`
    produces a `.zip` under `vaults/{id}/{version}/{hash}.zip`,
    inserts a `vault_builds` row, and `validate_vault()` passes.
  - The zip contains the expected folder layout from
    `03-vault-generation.md` §1, including `README.md`, `00-index.md`,
    `vault.json`.
  - Every member skill file in the zip carries the
    `<!-- skg-attribution: ... -->` comment.
  - Persona build for a persona with 3 neurons produces only the
    `personas/{handle}/` subtree + a partial `vault.json`.
- **Estimated effort:** L

## T-07 — Vault composer (delivery-time merge + watermarking + presign)
- **Owner:** Backend
- **Files touched:**
  - `apps/api/src/vault/composer.py` (new)
  - `apps/api/src/vault/router.py` (new) — endpoints listed in §02
  - `apps/api/src/delivery/watermark.py` (reuse `append_watermark`)
  - Redis caching helpers in `apps/api/src/core/cache.py` (probably
    a small new helper; otherwise inline)
- **Depends on:** T-06
- **Acceptance:**
  - Given an occupation build + 2 persona builds (T-06 outputs) and a
    buyer with active licenses on all three, `POST /v1/licenses/{occupation_license_id}/vault`
    returns a 60s presigned URL that downloads a zip whose
    `vault.json` enumerates files from all three.
  - Two downloads by the same buyer differ only in the watermark
    comment lines (bytewise stable elsewhere).
  - Cache hit returns the cached URL without re-zipping; cache TTL
    24h; invalidation on a new vault_build for any input.
  - `vault_downloads` row records the per-call snapshot.
- **Estimated effort:** M

## T-08 — Curation: `build_devops_vault.py`
- **Owner:** Curation
- **Files touched:**
  - `apps/api/scripts/build_devops_vault.py` (new)
  - `apps/api/scripts/seed_data/devops/cross-link-recipe.yaml` (new) —
    explicit `links[]` to add to each member skill at build time
  - `apps/api/scripts/seed_data/devops/occupation.yaml` (new) —
    occupation metadata (name, summary, domains, member roles)
- **Depends on:** T-03, T-06
- **Acceptance:**
  - `uv run python -m scripts.build_devops_vault` (a) ensures the
    curated user, (b) creates / updates the occupation Skill row,
    (c) populates `occupation_skills` for the 30 chosen DevOps skills,
    (d) triggers an occupation build, (e) publishes version 1.0.0.
  - Resulting vault opens in Obsidian: graph view renders with
    cross-domain links from the recipe; `00-index.md` shows the
    grouped table.
  - Re-running the script is idempotent (no duplicate Skill rows or
    duplicate join rows).

The 30 starter member skills (from the DevOps inventory in
`seed_data/synth/`):

Core (10):
- `devops-ci-pipeline-architect`
- `devops-gha-workflow-optimizer`
- `devops-k8s-manifest-reviewer`
- `devops-terraform-module-reviewer`
- `ops-incident-commander`
- `ops-runbook-generator`
- `observability-dashboard-architect`
- `alert-policy-architect`
- `alert-fatigue-reviewer`
- `eng-chaos-experiment-planner`

Supporting (12):
- `cloud-cost-audit`
- `cloud-cost-alert-designer`
- `kubernetes-cost-optimizer`
- `eng-secrets-architecture-designer`
- `eng-workload-identity-architect`
- `artifact-signing-and-verification-designer`
- `internal-platform-strategy-author`
- `imported-alirezarezvani-chaos-engineering`
- `cardinality-cost-reviewer`
- `imported-google-skills-waf-reliability`
- `imported-google-skills-waf-cost`
- `imported-google-skills-networking-observability`

Optional (8):
- `cross-platform-stack-chooser`
- `spark-on-kubernetes-architect`
- `kafka-topic-architect`
- `kafka-consumer-pattern-picker`
- `kafka-streams-pipeline-designer`
- `kafka-schema-evolution-architect`
- `imported-voltagent-cloudflare-platform`
- `imported-voltagent-cloudflare-workers-best-practices`

These 30 slugs are sourced from listings already present in
`apps/api/scripts/seed_data/synth/`. Curation may swap any optional
slot if a better candidate exists; do not change the count without
updating QA's fixtures.

- **Estimated effort:** M

## T-09 — Frontend: capture UX (web-creator)
- **Owner:** Frontend
- **Files touched:**
  - `apps/web-creator/app/capture/page.tsx` (new — landing)
  - `apps/web-creator/app/capture/[id]/page.tsx` (new — session UI)
  - `apps/web-creator/components/capture/` (form, draft-preview,
    link-picker, pii-flag-list)
  - `apps/web-creator/lib/api/capture.ts` (typed wrapper over generated
    api-client)
  - `apps/web-creator/components/capture/*.test.tsx` (vitest snapshots)
- **Depends on:** T-05
- **Acceptance:**
  - A signed-in creator can submit the 4-field form, poll status, see
    the draft, accept links, resolve PII flags, and click Publish.
  - The Publish button calls `finalize` and on success redirects to
    `/personas/[id]/neurons` with a toast confirming the new neuron.
  - All form state is React Hook Form + Zod (consistent with
    `prompts/01-tech-stack-and-repo.md`).
- **Estimated effort:** M

## T-10 — Frontend: persona admin UI (web-creator)
- **Owner:** Frontend
- **Files touched:**
  - `apps/web-creator/app/personas/page.tsx` (new — list)
  - `apps/web-creator/app/personas/new/page.tsx` (new — create form)
  - `apps/web-creator/app/personas/[id]/page.tsx` (new — dashboard
    with neuron list, publish button)
  - `apps/web-creator/app/personas/[id]/neurons/page.tsx` (new —
    sortable neuron list)
- **Depends on:** T-04, T-09
- **Acceptance:**
  - A creator can create a persona with `parent_occupation_id` picked
    from a typeahead.
  - The persona dashboard shows neuron count, draft count, last build
    status; "Publish" triggers `POST /v1/personas/{id}/publish` and
    polls the resulting job.
  - Neuron list is reorderable; reorder posts to `/neurons/order`.
- **Estimated effort:** M

## T-11 — Frontend: marketplace occupation + persona pages
- **Owner:** Frontend
- **Files touched:**
  - `apps/web-marketplace/app/occupations/[handle]/[slug]/page.tsx` (new)
  - `apps/web-marketplace/app/personas/[handle]/[slug]/page.tsx` (new)
  - `apps/web-marketplace/components/discovery/OccupationCard.tsx` (new)
  - `apps/web-marketplace/components/discovery/PersonaCard.tsx` (new)
  - `apps/web-marketplace/components/discovery/VaultGraphPreview.tsx`
    (new — a minimal React Flow or D3 force-directed render of
    `GET /v1/occupations/{id}/graph-preview`)
  - `apps/web-marketplace/app/library/[id]/vault/page.tsx` (new —
    composed download page with persona checklist)
  - additions to `apps/web-marketplace/app/page.tsx` (home rail
    showing occupations)
- **Depends on:** T-03, T-07
- **Acceptance:**
  - The occupation detail page lists member skills grouped by domain,
    persona overlays, version history, and a Buy button.
  - The vault graph preview renders without crashing for the seeded
    DevOps occupation.
  - The library page for a buyer with occupation+persona licenses
    shows a "Download composed vault" CTA that calls
    `POST /v1/licenses/{occ_lic_id}/vault` and either downloads
    (cache hit) or shows a job-progress indicator (cache miss).
- **Estimated effort:** M

## T-12 — Sample persona seed neurons
- **Owner:** Curation
- **Files touched:**
  - `apps/api/scripts/seed_data/devops-persona/persona.yaml` (new) —
    persona metadata
  - `apps/api/scripts/seed_data/devops-persona/neurons/*.skills.md` (5–10
    new files following the memory_neuron spec)
  - `apps/api/scripts/build_devops_persona.py` (new — mirrors
    `build_devops_vault.py` but for the persona)
- **Depends on:** T-08
- **Acceptance:**
  - The build script creates a persona Skill row with `kind='persona'`
    under a *demo* creator account (suggest `@jane-devops-demo` —
    not the curated handle), `parent_occupation_id` pointing at the
    AI DevOps Engineer occupation.
  - Each seed neuron's `links[]` resolves against the parent occupation
    (zero warnings in the persona build's `manifest.warnings`).
  - Running the script triggers a persona build that succeeds.
  - The neurons cover the demo scenarios QA will use in T-14
    (e.g. flaky CI, on-call rotation, blue/green rollback, cost spike,
    secret rotation, dashboard cardinality).

Sample neurons (≥5, ≤10):
1. `2024-08-flaky-tests-after-redis-upgrade`
2. `2024-09-on-call-rotation-handoff-template`
3. `2024-10-blue-green-rollback-at-3am`
4. `2024-11-cost-spike-egress-debug`
5. `2025-01-secret-rotation-zero-downtime`
6. `2025-02-dashboard-cardinality-cleanup`
7. `2025-03-paging-policy-rewrite`

- **Estimated effort:** S

## T-13 — Layer-C demo CLI
- **Owner:** Backend
- **Files touched:**
  - `apps/api/scripts/demo_devops_agent.py` (new)
  - `apps/api/scripts/seed_data/demo/prompts.yaml` (3–5 stock prompts
    for the demo to chew on; e.g. "my CI is flaky", "cost just
    spiked 40%", "blue/green failed at 3am")
- **Depends on:** T-07, T-08, T-12
- **Acceptance:**
  - `uv run python -m scripts.demo_devops_agent --prompt "my CI just
    started failing intermittently"` runs end-to-end against a local
    API + DB + S3 + Redis, produces:
    1. An answer block from Claude.
    2. A "Consulted neurons" list with each neuron's
       `vault_path (creator_handle, version, kind)`.
  - The output is deterministic enough for a snapshot test (modulo
    LLM wording variation — we snapshot the `vault.json` files
    consulted, not the prose).
  - The CLI accepts `--occupation <slug>` and `--persona <handle/slug>`
    multi-value flags.
- **Estimated effort:** S

## T-14 — QA: smoke tests, fixtures, test plan
- **Owner:** QA / Docs
- **Files touched:**
  - `team/test-plan.md` (new — formal end-to-end checklist)
  - `apps/api/tests/integration/test_occupation_flow.py` (new)
  - `apps/api/tests/integration/test_persona_flow.py` (new)
  - `apps/api/tests/integration/test_capture_flow.py` (new)
  - `apps/api/tests/integration/test_vault_compose.py` (new)
  - `apps/api/tests/fixtures/vaults/expected-devops-vault/` —
    snapshot of expected `vault.json` from a deterministic build
  - `.github/workflows/team-smoke.yml` — nightly run of
    `demo_devops_agent.py` with a stubbed LLM
- **Depends on:** all of T-01 through T-13
- **Acceptance:**
  - Full integration test creates a curator + a creator + a buyer,
    runs T-08 and T-12, buys both products, composes, downloads, and
    asserts on every step.
  - The vault.json snapshot test catches drift (e.g. a new neuron added
    to the seed must update the fixture).
  - The smoke workflow fails loudly if the demo CLI's "Consulted
    neurons" list changes structure (not content).
- **Estimated effort:** M

## T-15 — Docs
- **Owner:** QA / Docs
- **Files touched:**
  - `docs/vault-format.md` (new) — for downstream agent authors
  - `docs/capture-howto.md` (new) — for creator onboarding
  - `docs/changelog.md` — append cycle-1 entry
  - `team/dev-diary.md` — end-of-cycle journal
- **Depends on:** T-14
- **Acceptance:**
  - Vault format doc explains `vault.json`, attribution comments,
    `[[wiki-links]]` semantics with one worked example.
  - Capture how-to is a 1-page walkthrough from "I just had an incident"
    to "my neuron is in the vault".
  - Changelog mentions the new product types + the demo CLI.
- **Estimated effort:** S

---

## Parallelism windows

After T-01 and T-02 land, the following can run concurrently in
isolated worktrees:

- Group A (Backend): T-03, T-04, T-05.
- Group B (Frontend, blocked on API readiness): T-09 starts after T-05
  router has stable schemas (mock-data first); T-10 follows T-04; T-11
  follows T-03 + T-07.
- Group C (Curation): T-08 starts as soon as T-06 schemas land; T-12
  follows T-08.

Critical-path estimate (sequential through the longest chain):
T-01 (M) → T-06 (L) → T-07 (M) → T-08 (M) → T-13 (S) → T-14 (M) ≈
13 focused agent-days. With Frontend running concurrently the wall
time is the same (Frontend is parallel work, not a serial blocker for
Layer C since the demo is CLI).

---

## Layer-by-layer mapping

| Layer | Tasks |
|---|---|
| **A** — DevOps occupation vault | T-01, T-02, T-03, T-06, T-08 |
| **B** — Sample persona overlay | T-04, T-05, T-06, T-12 (+ T-09, T-10 for the human-driven capture flow if Curation goes through the UI) |
| **C** — Demo agent with attribution | T-07, T-13 |

Frontend tasks T-09, T-10, T-11 are *demo polish* — they make the
flow inspectable in a browser. Layer C ships without them by going
through the CLI.

---

## Sequencing rule of thumb for the user

If the user wants the absolute fastest path to a working demo
(Layer C only), the cycle-1 critical path is **T-01 → T-02 → T-03 →
T-04 → T-05 (stub LLM call) → T-06 → T-07 → T-08 → T-12 (hand-author
the 5 sample neurons as files rather than via UI) → T-13 → T-14**.
That ships the demo without any frontend work. Frontend tasks
(T-09, T-10, T-11) become Cycle 2 if time pressure is real.

---
