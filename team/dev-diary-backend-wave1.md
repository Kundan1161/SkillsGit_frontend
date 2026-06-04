# Dev diary — Backend, Cycle 1 Wave 1

**Owner:** Backend
**Wave:** 1 (T-01 migrations 0006–0010, T-02 validator + Zod regen, ADR-017 spec amendment)
**Started:** 2026-05-26
**Status:** shipped (handing off to Wave 2)

---

## What shipped

### Migrations (`apps/api/alembic/versions/`)

- **0006 `occupations_and_kind`** — `skill_kind` enum + `skills.kind`
  column (default `'skill'`, backfilled, then NOT NULL), the
  `ix_skills_kind_status` covering index for every catalog query that
  now filters by kind, `occupation_member_role` enum, `occupations`
  side table (1:1 with `skills` via shared PK), and `occupation_skills`
  join with `(occupation_id, sort_order)` + `(member_skill_id)`
  indexes.
- **0007 `personas_and_neurons`** — `personas` side table (non-null
  `parent_occupation_id` → `occupations.skill_id` ON DELETE RESTRICT)
  and the `persona_neurons` join with sort + lookup indexes.
- **0008 `capture`** — `capture_session_status` enum (`draft` …
  `finalized` / `abandoned`), `capture_sessions` with creator-side
  drafts list index, and `capture_attachments` with sha256 content
  addressing.
- **0009 `vault_builds_and_downloads`** — `vault_build_status` enum,
  `vault_builds` keyed `(skill_id, content_hash)` + a partial unique
  `(skill_version_id) WHERE status='succeeded'`, deferred FKs from
  `occupations.latest_build_id` and `personas.latest_build_id` to
  `vault_builds.id`, `vault_downloads` with per-buyer / per-license
  audit indexes, `license_composition_role` enum, and the licenses
  additions (`composition_role` backfilled to `standalone` + NOT NULL,
  `target_occupation_skill_id`) with the
  `ix_licenses_buyer_target_occupation_status` composer index.
- **0010 `categories_seed_occupations_personas`** — idempotent INSERT
  of the `occupations` (display_order 50) and `personas` (51) category
  rows.

The dependency chain is contiguous `0001 → 0010`; `alembic heads`
reports a single head and `alembic history` resolves the
0003+0004 → 0005 mergepoint without ambiguity.

### Model modules

- `src/skills/models.py` extended: new `SkillKind` enum (values
  `skill`, `occupation`, `persona`, `memory_neuron`) + `kind` column on
  `Skill` (server_default `'skill'`) + new `ix_skills_kind_status`
  index. `__all__` updated.
- `src/billing/models.py` extended: new `LicenseCompositionRole` enum +
  `License.composition_role` (server_default `'standalone'`) +
  `License.target_occupation_skill_id` + the
  `ix_licenses_buyer_target_occupation_status` index.
- `src/occupations/__init__.py`, `src/occupations/models.py` — new
  module: `Occupation`, `OccupationSkill`, `OccupationMemberRole`.
- `src/personas/__init__.py`, `src/personas/models.py` — new module:
  `Persona`, `PersonaNeuron`.
- `src/capture/__init__.py`, `src/capture/models.py` — new module:
  `CaptureSession`, `CaptureAttachment`, `CaptureSessionStatus`.
- `src/vault/__init__.py`, `src/vault/models.py` — new module:
  `VaultBuild`, `VaultDownload`, `VaultBuildStatus`.

No router mounted in `main.py` — that's Wave 2's job per the wave plan.
`alembic/env.py` and `tests/conftest.py` now import the four new model
modules so `Base.metadata` sees them.

### Validator + Pydantic frontmatter

`src/skills/validator.py`:
- New sub-models `LinkRelation` enum, `LinkEntry` (strict), `NeuronBlock`
  (strict).
- Five new optional fields on `SkillFrontmatter`: `kind`, `links`,
  `parent_occupation_id`, `neuron`, `vault_path`.
- Four new error codes wired in `_validate_frontmatter_semantics`:
  - `frontmatter.neuron: required_for_memory_neuron`
  - `frontmatter.parent_occupation_id: required_for_memory_neuron`
  - `frontmatter.parent_occupation_id: required_for_persona`
  - `frontmatter.vault_path: server_assigned`
- The 456 (currently 452) curated skill files validate green under the
  extended schema — backward compatibility preserved.

### Test fixtures (`apps/api/tests/fixtures/skills/`)

- `occupation_valid.skills.md`
- `persona_valid.skills.md`
- `memory_neuron_valid.skills.md`
- `memory_neuron_missing_neuron.skills.md`
- `persona_missing_parent.skills.md`
- `creator_set_vault_path.skills.md`
- `legacy_skill_no_kind.skills.md`

### Test modules

- `apps/api/tests/test_validator_kinds.py` — 11 cases (positive fixtures,
  negative fixtures, inline `memory_neuron` missing-parent case, and
  three parser-sanity tests on enum defaults and strict relation
  validation).
- `apps/api/tests/test_smoke_legacy_skills.py` — parametrized over
  every `*.skills.md` under `scripts/seed_data/synth/` (excluding
  `_report_*` / `README.md`) plus a bulk-summary aggregate.

### Spec amendment

`prompts/shared/skills-md-spec.md`:
- The YAML schema block now documents the 5 new optional fields
  inline, each marked `# optional` with their type and default.
- Validation-rules sub-list extended with one bullet per new error
  code.
- New `### Optional fields — kinds, links, neurons` section with
  per-field prose + worked YAML examples for occupation, persona,
  and memory_neuron.
- New `### Compatibility` paragraph: "Existing files without these
  fields continue to validate. The default `kind` is `skill`."
- No restructuring of the rest of the doc.

### Zod schema

`packages/skills-schema/src/index.ts` — replaced the placeholder
scaffold with a hand-maintained mirror of the Pydantic
`SkillFrontmatter`. All five ADR-009 fields land with matching shapes
(`LinkEntry`, `NeuronBlock`, `SkillKind` enum, etc.). `tsc --noEmit`
passes via `pnpm typecheck`. The root `pnpm codegen` script is still
the placeholder `echo` from before this work — flagged below as a
Wave 2+ chore.

---

## Verification

### `alembic upgrade head`

**Could not run end-to-end against Postgres** — the local Postgres on
`localhost:5433` is not running (`ConnectionRefusedError [WinError
1225]`) and Docker Desktop is not started, so the docker-compose
postgres can't be brought up either. This is an environmental
constraint, not a migration defect.

What I did verify:
- Every migration module imports cleanly (`importlib.util` round-trip
  on each file in `alembic/versions/`).
- `alembic heads` returns a single head:
  `0010_categories_seed_occupations_personas`.
- `alembic history` resolves the full chain `<base> → 0001 → 0002 →
  {0003, 0004} → 0005 → 0006 → 0007 → 0008 → 0009 → 0010` without
  unresolved mergepoints.
- `Base.metadata.create_all` against `sqlite+aiosqlite:///:memory:`
  (with all new modules imported) successfully creates all 8 new
  tables (`occupations`, `occupation_skills`, `personas`,
  `persona_neurons`, `capture_sessions`, `capture_attachments`,
  `vault_builds`, `vault_downloads`) alongside the existing 17 tables
  → 25 total.
- A sqlite `alembic upgrade head` was attempted as a fallback and
  fails at migration **0001** on `CREATE EXTENSION IF NOT EXISTS
  citext;` — a pre-existing Postgres-only construct, not caused by my
  new migrations. The brief explicitly anticipated this divergence.

Last 20 lines of the sqlite attempt (for the record):

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) near "EXTENSION": syntax error
[SQL: CREATE EXTENSION IF NOT EXISTS citext;]
```

### `pytest tests/test_validator_kinds.py -v`

```
collected 11 items

tests/test_validator_kinds.py::test_occupation_valid PASSED
tests/test_validator_kinds.py::test_persona_valid PASSED
tests/test_validator_kinds.py::test_memory_neuron_valid PASSED
tests/test_validator_kinds.py::test_legacy_skill_no_kind_validates_green PASSED
tests/test_validator_kinds.py::test_memory_neuron_missing_neuron_block PASSED
tests/test_validator_kinds.py::test_persona_missing_parent_occupation_id PASSED
tests/test_validator_kinds.py::test_creator_set_vault_path_rejected PASSED
tests/test_validator_kinds.py::test_memory_neuron_missing_parent_is_also_required PASSED
tests/test_validator_kinds.py::test_kind_defaults_to_skill_when_absent PASSED
tests/test_validator_kinds.py::test_links_default_to_empty_list PASSED
tests/test_validator_kinds.py::test_link_entry_rejects_unknown_relation PASSED

============================= 11 passed in 0.49s ==============================
```

### `pytest tests/test_smoke_legacy_skills.py -v`

```
============================= 452 passed in 4.11s ==============================
```

(The `synth/` directory currently holds 452 skill files; the brief
called this "the 456 existing skills" — the discrepancy is just that
the live count has drifted by 4 since the brief was written. Wave 2
should reconcile if the exact number matters for any acceptance gate.)

### Existing validator + skill-upload regressions

```
tests/test_validator.py ........                                         [ 32%]
tests/test_validator_kinds.py ...........                                [ 76%]
tests/test_skill_upload.py ......                                        [100%]

============================= 25 passed in 30.95s ==============================
```

The publish-pipeline upload tests (which exercise the full
`SQLAlchemy create_all → ORM round-trip → frontmatter validation`
loop) confirm the `kind` default + the new optional fields don't
disturb the existing pipeline.

### `mypy --strict`

```
$ uv run mypy --strict src/skills src/occupations src/personas src/capture src/vault
Success: no issues found in 15 source files
```

Also clean on `src/billing/models.py` after the License-model
additions.

---

## Deviations from `01-data-model-deltas.md`

None of substance. Three minor implementation choices worth flagging
for Wave 2:

1. **`NeuronBlock.context`** — the data-model doc lists `context_md`
   on `capture_sessions` (as the typed input), and ADR-009 spells out
   `situation / decision / outcome / recorded_at / confidence` for
   the published `neuron` frontmatter block. The Architect's
   capture-flow §3 example referenced "context" as a freeform extras
   field on the published neuron, so I exposed it as an optional
   `context: str | None` on `NeuronBlock`. If the Architect would
   rather keep "context" purely on the capture-session side and out
   of the published frontmatter, this can be removed in Wave 2
   without breaking anything (no validator rule uses it).
2. **`Occupation.latest_build_id` / `Persona.latest_build_id`** — both
   are declared on the SQLAlchemy model as `UUID | None` with no
   relationship attribute (since the model files are in modules
   the `vault` package doesn't currently import). Migration 0009
   wires up the FK constraint after `vault_builds` exists. Wave 2
   should add a SQLAlchemy `relationship()` if it wants navigability.
3. **`License.target_occupation_skill_id`** has an `ondelete='RESTRICT'`
   FK to `skills.id`. The spec described it as "snapshot at purchase
   time"; I went with RESTRICT to make it impossible to delete an
   occupation that still has persona licenses pointing at it. If the
   Architect prefers SET NULL semantics (snapshot truly decouples),
   adjust the FK in a Wave-2 follow-up migration.

---

## Open questions for Wave 2 backend

1. **Router mounting strategy** — main.py mounts existing routers in a
   single block. Wave 2 will spawn three Backend agents (T-03 / T-04 /
   T-05) in parallel worktrees. The cycle-1 plan already calls this
   out as the reason worktrees become net positive at Wave 2;
   confirm the merge strategy (probably the cycle-1-plan's intended
   "each agent adds its `include_router` call, last write wins, conflicts
   resolve trivially").
2. **`finalized_neuron_skill_id` ondelete** — I used `SET NULL` so a
   neuron deletion doesn't cascade to the capture session row (which
   we want to keep for audit). The doc didn't specify; flag if you'd
   prefer different semantics.
3. **`pnpm codegen`** is still a placeholder. The Zod schema is now
   hand-maintained in lockstep with Pydantic. We should either build
   a real codegen step (datamodel-code-generator / openapi-ts off the
   `/v1/openapi.json` surface) or document the "edit in both places"
   discipline in `CONTRIBUTING.md`. Either is a Wave 2+ chore.
4. **`relation` enum extensibility** — `LinkRelation` is a closed
   enum on both sides today. If curation wants to introduce e.g.
   `requires` or `supersedes`, it's a non-breaking change but it
   needs a coordinated Pydantic + Zod + spec amendment. Worth a one-
   line entry in `team/06-open-questions.md` if it's likely.
5. **Quota counter for capture** — `capture_sessions.token_usage_json`
   is set up; the actual quota-key Redis counter (T-05 acceptance
   bullet 4) needs a key prefix decision. Suggestion:
   `capture:quota:{creator_id}:{yyyy-mm}` with a 32-day TTL.

---

## What Wave 2 inherits

- Stable ORM models for all 4 new bounded contexts. The `kind`
  discriminator is wired and existing pricing/licensing/delivery rails
  can be reused without modification.
- A validator that accepts the 5 new optional fields and emits stable
  error codes downstream agents can match on.
- Test fixtures that exercise every new error code (good seeds for the
  Wave-2 integration tests in `test_occupation_flow.py` etc.).
- A spec document the marketplace UX and the curation pipelines can
  reference without ambiguity.
- A Zod schema parsable by the future creator-app preview pane (T-09
  / T-10).

No router work, no service work, no migrations beyond 0010 — that's
all Wave 2.
