# Cycle 1 — Wave Plan

**Owner:** Orchestrator
**Status:** Active
**Started:** 2026-05-26
**Reads:** `team/05-mvp-plan.md`, `team/decisions.md` (ADR-001 through ADR-018)

This file controls the spawn order of implementation agents. The MVP plan
defines what to build; this file defines when each task fires.

## Spawn waves

| Wave | Agents (parallel) | Tasks | Gating exit |
|---|---|---|---|
| 1 | Backend, QA-Docs, Curation-research | T-01 + T-02 + spec amendment; test-plan skeleton; verify 30 DevOps slugs exist | Migrations apply; 456 existing skills still validate; test-plan landed |
| 2 | Backend-A, Backend-B, Backend-C | T-03 Occupations; T-04 Personas; T-05 Capture | Three module routers exist with passing unit tests |
| 3 | Backend, Curation | T-06 + T-07 Vault builder + composer; T-08 DevOps vault assembly | A composed vault zip exists locally and opens in Obsidian |
| 4 | Curation, Backend, (optional) Frontend | T-12 sample persona neurons; T-13 demo CLI; T-09/T-10/T-11 if time | Demo CLI returns an attributed answer |
| 5 | QA, QA-Docs | T-14 integration tests; T-15 docs | `pytest` green; `docs/vault-format.md` + changelog landed |

Frontend tasks (T-09, T-10, T-11) are deferrable to Cycle 2 per the
"fastest path to Layer C" rule of thumb in `05-mvp-plan.md`. Decision
deferred until end of Wave 3.

## Worktree discipline

For Cycle 1 Wave 1, agents work in the **main tree** because:
- Wave 1 changes are additive (new files mostly + one new column).
- The user's WIP is on `apps/web-marketplace/` (frontend) — no overlap
  with Wave 1's API + spec changes.
- Worktree isolation requires re-bootstrapping `.venv` / `node_modules`,
  which adds ~5 min per agent. Cost > benefit at Wave 1 scale.

Starting at Wave 2, when three Backend modules are built concurrently
and may all touch `apps/api/src/main.py` (router mounting), worktrees
become net positive. Revisit then.

## Cross-wave conventions

- Each agent writes a `team/dev-diary-<role>-<wave>.md` entry with:
  what shipped, what blocked, what's needed from another role.
- Each Backend agent runs `pytest` for its module before reporting back.
  No agent reports "done" without test evidence.
- Each Backend agent runs `mypy --strict src/<new_module>` before reporting.
- All new files match the existing module pattern (`models.py`,
  `schemas.py`, `service.py`, `router.py`, `tests/`).
- Frontmatter additions to skills.md files use the field names from
  ADR-009 (`kind`, `links`, `parent_occupation_id`, `neuron`,
  `vault_path`) and nothing else.

## Inter-wave checkpoints

After each wave, the orchestrator:
1. Reads every `team/dev-diary-*` written during that wave.
2. Verifies acceptance criteria from `05-mvp-plan.md` for each task.
3. Surfaces any new open question to the user before the next wave.
4. Updates this file's wave-status table.

## Wave-status log

| Wave | State | Started | Completed | Notes |
|---|---|---|---|---|
| 1 | **done** | 2026-05-26 | 2026-05-26 | Backend T-01+T-02+spec ✓; QA-Docs scaffolding ✓; Curation-research inventory ✓. 2 small fixups carried into Wave 2 (drop `NeuronBlock.context`; verify `alembic upgrade head` on Postgres). |
| 2 | **done** | 2026-05-26 | 2026-05-26 | Occupations 55 ✓ + Personas 59 ✓ + Capture 77 ✓ = 191 module tests. 546 legacy tests still pass. Orchestrator mounted all three routers in `main.py`. NeuronBlock.context dropped; billing 409 gate active; alembic env.py fixed by Backend-A. |
| 3 | **done** | 2026-05-26 | 2026-05-26 | T-06 vault builder (31 tests) + T-07 composer (22 tests) + T-08 DevOps vault assembly (30-skill vault, 60 cross-links, 250 KB, validates green, opens in Obsidian). Vault router mounted in `main.py`. UUID cross-dialect bug fixed in composer. |
| 4 | **done** | 2026-05-26 | 2026-05-26 | T-12 (7 hand-authored persona neurons + idempotent build script) + T-13 (demo CLI with snapshot mode + live Claude path). Layers A+B+C functionally complete. 246 tests in module + integration suites. |
| 5 | **done** | 2026-05-26 | 2026-05-26 | T-14 (13 integration tests + 5 consulted-block unit tests + smoke CI workflow + 6 polish items closed) + T-15 (docs/vault-format.md 269 ln + docs/capture-howto.md 149 ln + changelog Cycle-1 entry + dev-diary close-out + retrospective). 809 tests passing. |

## Wave 2 conventions (delta from Wave 1)

- **Three parallel Backend agents, no worktree isolation.** Each owns one bounded
  context module (`occupations`, `personas`, `capture`). Risk of conflict is
  contained to `apps/api/src/main.py`, which **no Wave 2 agent edits** — the
  orchestrator mounts the three new routers after Wave 2 returns.
- Each agent verifies `alembic upgrade head` against a live Postgres
  (`docker compose -f infra/docker-compose.yml up -d postgres redis` if not
  running). The Postgres verification gap from Wave 1 closes here.
- Each agent runs `pytest` + `mypy --strict` on their module before reporting done.
- Each agent writes `team/dev-diary-{module}-wave2.md` with the standard sections.
