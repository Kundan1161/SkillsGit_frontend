# Team — Occupations & Personas build

> Active workstream for the **AI Occupation Personas** product layer. Charter, roles,
> communication protocol, and the index of every artifact this team produces.
>
> Distinct from:
> - `prompts/` — canonical original build spec for the marketplace
> - `context/` — curation audit trail for the 456-skill library

## Mission

Layer two new product types on top of the existing marketplace:

1. **Occupation** — a curated, graph-linked bundle of skills representing all
   methodology for a job role (MVP target: `AI DevOps Engineer`). Delivered as a
   downloadable Obsidian-compatible vault.
2. **Persona** — a composable add-on a real practitioner publishes. Memory neurons
   from recorded real-world situations, linked into a parent occupation. Buyers
   stack 1+ personas on top of the base occupation.

MVP demo at end of cycle 1: a working agent that loads `DevOps occupation + one
sample persona` and answers a DevOps prompt with attribution back to the neurons
it consulted.

## Decisions already locked (see `decisions.md`)

- **ADR-001** — Runtime delivery is vault bundle download. MCP server is Phase 2.
- **ADR-002** — Persona is a composable add-on (separate license, separate payout)
  to an occupation. Buyer holds 1 license per occupation + N licenses per persona.
- **ADR-003** — Architect drafts the spec; user approves; then the implementation
  team spawns.

## Roles

| Role | Owns | Tools |
|---|---|---|
| **Architect** | `team/00-architecture.md` through `team/06-open-questions.md`, `team/decisions.md`. Reviews proposals, breaks ties, owns the data-model contract. | Read, plan, write specs. No code. |
| **Backend** | `apps/api/src/{occupations,personas,capture}/` — models, schemas, services, routers, migrations, validator updates, vault build script. | Worktree-isolated. |
| **Frontend** | `apps/web-creator/app/{capture,personas}/` + marketplace vault-graph preview. | Worktree-isolated. |
| **Curation** | `apps/api/scripts/build_devops_vault.py` + DevOps source-list + cross-link recipe applied to existing 30+ DevOps skills in `seed_data/synth/`. | Worktree-isolated. |
| **QA / Docs** | `team/test-plan.md`, `team/dev-diary.md`, validator fixtures, smoke tests, end-of-cycle demo recording script. | Worktree-isolated. |

## Communication protocol

- **No chat.** All cross-role communication is markdown files in `team/`.
- Each role writes a `team/dev-diary-<role>.md` entry per work cycle: what they
  shipped, what they blocked on, what they need from another role.
- The Architect reads all diaries at end of cycle and writes the next cycle's
  plan into `team/cycle-N-plan.md`.
- **Open questions** for the user (Farzad) land in `team/06-open-questions.md`
  with: question, why it matters, options, recommended answer. The orchestrator
  (main Claude) surfaces them via `AskUserQuestion` and writes the answer back.

## Governance

- Architect signs off on data-model and API-surface changes. If two roles
  disagree on an interface, Architect breaks the tie in writing in `decisions.md`.
- User (Farzad) approves each cycle's plan before implementation agents spawn.
- Any change to `prompts/shared/skills-md-spec.md` is a user-gated decision.
- Worktrees: each implementation role runs in an isolated git worktree
  (`isolation: "worktree"`) so concurrent work cannot trample.

## Cadence

- **Cycle 0 (now):** Architect produces all 8 spec deliverables. User reviews.
- **Cycle 1:** Implementation team builds Layer A (DevOps occupation vault) +
  Layer B (one sample persona) + Layer C (demo).
- **Cycle 2:** Polish, second occupation, persona marketplace listing UX.

## File index (this folder)

| File | Owner | Purpose |
|---|---|---|
| `README.md` | Orchestrator | This file. Charter. |
| `decisions.md` | Architect | Architecture Decision Record (ADR) log. |
| `00-architecture.md` | Architect | System architecture + data flows. |
| `01-data-model-deltas.md` | Architect | New tables, columns, indexes, migrations plan. |
| `02-api-surface.md` | Architect | New endpoints with schemas. |
| `03-vault-generation.md` | Architect | Skill bundle → Obsidian vault spec. |
| `04-capture-flow.md` | Architect | Capture UX + situation → neuron pipeline. |
| `05-mvp-plan.md` | Architect | Cycle-1 task breakdown per role. |
| `06-open-questions.md` | Architect | Questions for user, with recommendations. |
| `cycle-N-plan.md` | Architect | Per-cycle work plan (created at each cycle boundary). |
| `dev-diary-<role>.md` | Each role | Per-cycle work log. |
| `test-plan.md` | QA | Test strategy + acceptance fixtures. |
| `dev-diary.md` | QA / Docs | Build journal (what shipped, what we learned). |
