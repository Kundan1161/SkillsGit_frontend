# Dev diary — DevOps occupation vault, Cycle 1 Wave 3 (T-08)

**Owner:** Curation (Wave 3, T-08)
**Date:** 2026-05-26
**Status:** shipped (Layer-A demo artifact green)

---

## What shipped

### `apps/api/scripts/seed_data/devops/occupation.yaml` (new)

Occupation metadata for `skillsgit-curated/ai-devops-engineer`:

- 30 members across 7 domain folders (`ci-cd`, `observability`,
  `incident`, `iac`, `security`, `cost`, `platform`).
- Two substitutions vs the original 30 in `team/05-mvp-plan.md` (both
  ratified in `team/devops-occupation-slugs.md`):
  - slot 9: `alert-fatigue-reviewer` → `slo-designer` (CDS → SRE).
  - slot 23: `cross-platform-stack-chooser` → `instrumentation-coverage-reviewer`
    (mobile → observability triangle leg).
- Role tranches (per spec): 10 core / 12 supporting / 8 optional.
- Pricing: `free` (matches the platform-wide free phase the curated
  library currently uses; see `publish_curated.py` §`_infer_pricing`).
- Version 1.0.0, recommended_persona_count=2.

### `apps/api/scripts/seed_data/devops/cross-link-recipe.yaml` (new)

60 explicit cross-links across the 30 members, taken verbatim from
`team/devops-occupation-slugs.md` §Cross-link recipe seed. Relations
restricted to the LinkRelation enum's `applies`, `extends`, `see-also`
trio (no `contradicts`, no `recorded-instance-of` — the latter is
reserved for Wave-4 memory-neuron → base links).

Distribution:
- Hubs (≥4 in or out): `ci-pipeline-architect` (3/4),
  `observability-dashboard-architect` (3/4), `alert-policy-architect`
  (3/4), `cloud-cost-audit` (3/3), `k8s-manifest-reviewer` (4/4).
- Zero isolated nodes — every member has at least one outbound or
  inbound link.

### `apps/api/scripts/build_devops_vault.py` (new)

Orchestration script with deterministic, idempotent end-to-end pipeline.
Phases:

1. **Curated user** — calls `scripts.publish_curated._ensure_curated_user`
   (re-exported), so the script never duplicates the user-bootstrap
   logic that `publish_curated.py` already owns.
2. **Member resolution** — looks up every member `Skill` row by
   `(creator_id, slug)`. Errors loudly if any of the 30 is missing
   (with an instruction to run `publish_curated` first).
3. **Cross-link application** — for each member with ≥1 outbound link
   in the recipe, writes a *new patch* `SkillVersion` (`1.0.0 → 1.0.1`)
   carrying the recipe's `links[]` in frontmatter. The 1.0.0 release
   stays immutable per ADR-013. The patched body is re-validated with
   `validate_file()` before upload. Storage key is
   `skills/<id>/1.0.1.md`. Idempotent: if a 1.0.1 with the same
   `content_hash` already exists, no upload or row change. If the
   recipe drifted (different content_hash), the existing row's
   `content_hash` + `storage_url` are updated in place — the version
   string is owned by the curation pipeline, so reuse is legitimate.
4. **Occupation Skill row** — creates or updates
   `(creator_id, slug=ai-devops-engineer, kind=occupation)`. Idempotent
   on `(creator_id, slug)`.
5. **`occupation_skills`** — bulk-replace (DELETE + re-INSERT) matches
   `OccupationService.bulk_set_members` semantics. Deterministic
   `sort_order` from the YAML.
6. **Occupation SkillVersion** — creates `1.0.0` if missing. The
   storage object is a tiny JSON envelope (the actual content is the
   vault zip, not a markdown body — occupations don't have a
   single-file body the way base skills do).
7. **Publish + build** — sets `status=published` + `released_at`,
   then calls `src.vault.builder.build_occupation` directly. In dev
   there's no Arq worker, so calling the builder synchronously is the
   same code path the inline-test toggle uses. The builder is itself
   idempotent on `(skill_id, content_hash)`, but the orchestration
   script wraps that with a check on
   `(skill_id, skill_version_id, status='succeeded')` to handle the
   case where the polish step (next phase) has mutated the row's
   `content_hash` (see "Choices" below).
8. **`.obsidian/graph.json` polish (ADR-016 Q-6)** — post-build, the
   script downloads the zip, injects `.obsidian/graph.json` with
   color-by-tag for the 7 domain slugs, re-zips deterministically, and
   re-uploads to a *sibling* S3 key (same path prefix, new content
   hash). The `vault_builds` row's `storage_url` / `content_hash` /
   `file_count` / `total_bytes` are updated to point at the polished
   artifact. The original immutable artifact stays in S3 (ADR-013).
9. **`validate_vault()`** — runs against the final polished bytes.
   Build aborts with a clear message if it fails (it doesn't).
10. **Audit log + summary print** — writes
    `occupation.published` audit row, prints the summary block.

Command: `uv run python -m scripts.build_devops_vault`

### Domain colour palette for `.obsidian/graph.json`

Picked 7 hues from Tailwind v3 (50% sat band) for accessible distinct
colours — sky/emerald/amber/violet/red/green/pink mapped to
ci-cd / observability / incident / iac / security / cost / platform
respectively. Obsidian stores colour as a single 0xRRGGBB integer; the
script converts the hex strings into that form.

---

## Choices & decisions

### Cross-link strategy — patch SkillVersions vs `occupation_skills.links_json`

The brief gave two acceptable paths:

- (A) Write the cross-links into new patch `SkillVersion` rows
  (1.0.0 → 1.0.1). Original release stays immutable.
- (B) Extend `occupation_skills` with a `links_json` column.

**Chose (A).** Reading `apps/api/src/occupations/models.py` confirmed
the `occupation_skills` table has no `links_json` column today, and the
brief explicitly said "do NOT add migrations". (A) requires no schema
change, lets the vault builder consume the cross-links via the existing
`SkillVersion.storage_url → frontmatter.links[]` path (which it already
does — see `_link_entries_for_member` in `src/vault/builder.py`), and
keeps the cross-link semantics inside the canonical skill body. The
1.0.1 versions are valid published versions — they just happen to carry
metadata that the curator added on top of the original 1.0.0 author
work.

(A)'s downside is that downstream consumers of the bare member skill
(outside the occupation) now see two versions and might be surprised
the 1.0.1 has `links:` while 1.0.0 doesn't. That's fine — `links:` is
in the ADR-009 optional fields, and `SkillVersion.released_at` /
`is_yanked` semantics keep the listing UX clean.

### `publish_curated.py` strips `devops-` / `eng-` filename prefixes

The Curation-research verification in
`team/devops-occupation-slugs.md` used **filenames** (`devops-ci-pipeline-architect.skills.md`).
After running `publish_curated.py` and querying the DB, 7 of the
30 slugs came back missing. Inspecting the frontmatter `id:` field
showed why — the synthesis pipeline drops the `devops-` and `eng-`
prefix when it ships the slug, e.g.:

```
devops-ci-pipeline-architect.skills.md  → id: skillsgit-curated/ci-pipeline-architect
eng-chaos-experiment-planner.skills.md  → id: skillsgit-curated/chaos-experiment-planner
```

Both YAMLs were updated to use the **published** slug form. The
file-vs-id remapping is documented in the `occupation.yaml` header
comment. (Inventory follow-up for Wave 4: rename the 7 source files so
filename and slug match, or accept the remap as documented contract.)

### Orchestration calls `build_occupation` directly, not the Arq job façade

The vault jobs façade (`src/vault/jobs.py`) has three modes:
prod-enqueue-to-Arq, test-stub, test-inline. In `ENV=dev` the production
path runs (enqueue to Arq), but no worker is running, so the job sits
in Redis indefinitely. The cleanest path for a one-shot script is to
call the builder directly — same code path the inline-test mode uses
and the same path `dev-diary-vault-composer-wave3.md` §1 recommends for
T-13's demo CLI.

In production, a real Arq worker would be running and the
`publish_occupation` service path would queue this exact build via
the façade. The script is a thin "I'll just do it myself" wrapper for
the dev/curation workflow.

### Polish via sibling-key re-upload, not in-place mutation

ADR-013 says vault build artifacts are immutable in S3. The
`.obsidian/graph.json` polish breaks that property if applied to the
already-uploaded object. To keep the immutability invariant while
still getting the polish into the bytes the composer ships to buyers,
the script:

1. Reads the original `<hash>.zip` from S3.
2. Builds a polished copy in memory.
3. Uploads it as a sibling key
   `vaults/{skill_id}/{version}/{new_hash}.zip`.
4. Updates `vault_builds.storage_url` + `content_hash` to point at the
   polished one.
5. Leaves the original immutable artifact in place (technically
   orphaned in S3, but the cost is one ≈250 KB blob per occupation
   build and a fresh `aws s3 rm` once it ages out via lifecycle).

This keeps both the "build artifact is immutable" and "polish lands
on every download" invariants together.

### Build idempotency: belt + suspenders

The `build_occupation` function checks `(skill_id, content_hash)` for
idempotency. That works perfectly for re-running an *unmodified*
script. But the polish step in run 1 mutates the row's `content_hash`,
so run 2's `build_occupation` call no longer matches and would try to
INSERT a new row — tripping the partial unique on
`(skill_version_id) WHERE status='succeeded'`.

The orchestration script wraps the builder call with an explicit
`(skill_id, skill_version_id, status=succeeded)` lookup and reuses the
existing row when found. Belt + suspenders, but the script is the only
place this matters; the underlying `build_occupation` function is
unchanged.

---

## Verification

### Files created / modified

- `apps/api/scripts/seed_data/devops/occupation.yaml` (new)
- `apps/api/scripts/seed_data/devops/cross-link-recipe.yaml` (new)
- `apps/api/scripts/build_devops_vault.py` (new)
- `team/dev-diary-devops-vault-wave3.md` (this file)

No source files outside `scripts/` were touched. No alembic migrations
added. No edits to `src/main.py` or any module under `src/`.

### Member file existence (all 30 verified)

```
$ ls scripts/seed_data/synth/ | grep -E '^(devops|eng|ops|observability|alert|slo|cloud-cost|kubernetes|artifact|internal-platform|imported-alirezarezvani|cardinality|imported-google|instrumentation|spark-on-k|kafka|imported-voltagent)' | wc -l
30
```

All 30 source files exist as `*.skills.md`. After
`publish_curated.py`, 30 of 30 resolved as Skill rows in the DB once
the filename → published-slug remap was applied to the YAMLs.

### First run output (last 30 lines)

```
INFO curated: loading D:\skillsgit\apps\api\scripts\seed_data\devops\occupation.yaml
INFO curated: loading D:\skillsgit\apps\api\scripts\seed_data\devops\cross-link-recipe.yaml
INFO curated: spec: id=skillsgit-curated/ai-devops-engineer name=AI DevOps Engineer members=30 domains=7
INFO curated: recipe: 60 cross-links
INFO curated: curated user: curated@skillsgit.local (id=019e65aa-2de4-7821-9d76-9fcfbdf03e60)
INFO curated: resolved 30/30 member skill rows
INFO curated: patches: 30 new + 0 existing (or unchanged) — 0 skills with 0 outbound links
INFO curated: occupation skill row created (id=019e65b6-cbe4-7191-85c7-c075e1a1f7f4, new)
INFO curated: occupation_skills: 30 rows written (bulk-replaced)
INFO curated: occupation version row: id=019e65b6-cfc6-7473-b839-b6e67d6c81d0 version=1.0.0
INFO curated: build result: status=succeeded build_id=019e65b7-5923-7380-808b-d641d87b4fc7 content_hash=1d41567fb74a1710d9ebd55830e33f527ddc9005f2ba9c326e947280c4b2acd3
INFO curated: vault_build 019e65b7-5923-7380-808b-d641d87b4fc7 succeeded: content_hash=1d41567fb74a1710d9ebd55830e33f527ddc9005f2ba9c326e947280c4b2acd3 files=33 bytes=249895 storage=vaults/019e65b6-cbe4-7191-85c7-c075e1a1f7f4/1.0.0/1d41567fb74a1710d9ebd55830e33f527ddc9005f2ba9c326e947280c4b2acd3.zip
INFO curated: polished: injected .obsidian/graph.json; new content_hash=15be2c960792d198eef0c604e8c8538bc94a4db93ec2c479cfa286c0fb33dd0f bytes=250309
INFO curated: validate_vault: is_valid=True error_count=0

========================================================================
AI DevOps Engineer occupation vault — Wave 3 T-08 summary
========================================================================
  occupation skill_id : 019e65b6-cbe4-7191-85c7-c075e1a1f7f4
  occupation version  : 1.0.0
  vault_build.id      : 019e65b7-5923-7380-808b-d641d87b4fc7
  content_hash        : 15be2c960792d198eef0c604e8c8538bc94a4db93ec2c479cfa286c0fb33dd0f
  file_count          : 34
  total_bytes         : 250309
  storage_url         : vaults/019e65b6-cbe4-7191-85c7-c075e1a1f7f4/1.0.0/15be2c960792d198eef0c604e8c8538bc94a4db93ec2c479cfa286c0fb33dd0f.zip
  members             : 30 across 7 domains
  cross-links applied : 60
  obsidian polish     : injected
  validate_vault      : is_valid=True
========================================================================
```

### Second run output (last 10 lines — idempotent)

```
INFO curated: build result: REUSE existing succeeded build id=019e65b7-5923-7380-808b-d641d87b4fc7 content_hash=15be2c960792d198eef0c604e8c8538bc94a4db93ec2c479cfa286c0fb33dd0f
INFO curated: vault_build 019e65b7-5923-7380-808b-d641d87b4fc7 succeeded: content_hash=15be2c960792d198eef0c604e8c8538bc94a4db93ec2c479cfa286c0fb33dd0f files=34 bytes=250309 storage=vaults/019e65b6-cbe4-7191-85c7-c075e1a1f7f4/1.0.0/15be2c960792d198eef0c604e8c8538bc94a4db93ec2c479cfa286c0fb33dd0f.zip
INFO curated: polish: .obsidian/graph.json already present — no change
INFO curated: validate_vault: is_valid=True error_count=0

(summary block identical to run 1 — same build_id, same content_hash,
same storage_url, file_count=34, total_bytes=250309, polish reports
"already present", validate_vault green)
```

Run-2 logs explicitly show:
- `patches: 0 new + 30 existing (or unchanged)` — patch SkillVersions
  for the 30 members not re-uploaded (same content hash).
- `occupation skill row updated (existing)` — no duplicate Skill row.
- `occupation_skills: 30 rows written (bulk-replaced)` — same 30 rows.
- `build result: REUSE existing succeeded build` — no second
  vault_builds row.
- `polish: .obsidian/graph.json already present` — no re-upload.

### `validate_vault()` on the produced zip

```
is_valid:       True
error_count:    0
file_count:     34   (30 members + README.md + 00-index.md + vault.json + .obsidian/graph.json)
total_bytes:    250 309
content_hash:   15be2c960792d198eef0c604e8c8538bc94a4db93ec2c479cfa286c0fb33dd0f
```

### Vault zip layout

```
.obsidian/graph.json
00-index.md
README.md
domains/ci-cd/ci-pipeline-architect.md
domains/ci-cd/gha-workflow-optimizer.md
domains/ci-cd/imported-voltagent-cloudflare-workers-best-practices.md
domains/cost/cloud-cost-alert-designer.md
domains/cost/cloud-cost-audit.md
domains/cost/imported-google-skills-waf-cost.md
domains/cost/kubernetes-cost-optimizer.md
domains/iac/k8s-manifest-reviewer.md
domains/iac/terraform-module-reviewer.md
domains/incident/chaos-experiment-planner.md
domains/incident/imported-alirezarezvani-chaos-engineering.md
domains/incident/imported-google-skills-waf-reliability.md
domains/incident/ops-incident-commander.md
domains/incident/ops-runbook-generator.md
domains/observability/alert-policy-architect.md
domains/observability/cardinality-cost-reviewer.md
domains/observability/imported-google-skills-networking-observability.md
domains/observability/instrumentation-coverage-reviewer.md
domains/observability/observability-dashboard-architect.md
domains/observability/slo-designer.md
domains/platform/imported-voltagent-cloudflare-platform.md
domains/platform/internal-platform-strategy-author.md
domains/platform/kafka-consumer-pattern-picker.md
domains/platform/kafka-schema-evolution-architect.md
domains/platform/kafka-streams-pipeline-designer.md
domains/platform/kafka-topic-architect.md
domains/platform/spark-on-kubernetes-architect.md
domains/security/artifact-signing-and-verification-designer.md
domains/security/secrets-architecture-designer.md
domains/security/workload-identity-architect.md
vault.json
```

### DB row inventory after both runs

```
ai-devops-engineer Skill rows:     1   (idempotent, no dup)
occupation_skills rows:            30  (matches member count)
vault_builds rows (this occupation): 1   (idempotent, no dup)
SkillVersion v1.0.1 rows (member patches): 30
warnings count in vault.json:      0   (every link resolved)
.obsidian/graph.json colorGroups:  7   (one per domain)
```

### `.obsidian/graph.json` polish landed

**Yes** — injected in run 1, recognised as present in run 2.

The script's `_polish_vault_with_graph_json` opens the post-build zip,
adds `.obsidian/graph.json` with seven `colorGroups` (tag-keyed for
each domain slug, RGB ints derived from Tailwind palette steps), re-emits
the zip with deterministic `ZipInfo.date_time` to keep the determinism
guarantee, then re-uploads to a sibling S3 key. The `vault_builds`
row's `storage_url`, `content_hash`, `file_count`, and `total_bytes`
are patched in place to point at the polished bytes.

Stock Obsidian (no plugin) recognises `.obsidian/graph.json` and applies
the colour groups in Graph View immediately on first open.

---

## Open questions for Wave 4

1. **Filename ↔ slug drift on `devops-` and `eng-` prefixed files.**
   The Curation-research verification (Wave 1) listed slugs by
   filename; `publish_curated.py` strips the `devops-` / `eng-`
   prefix. Two paths to reconcile:
   - (a) Rename the 7 source files to match the published slug. Cost:
     a single curation commit, no schema or code change. Then
     `team/devops-occupation-slugs.md` and `team/05-mvp-plan.md` can
     keep their original verbose slugs as documentation.
   - (b) Document the remap as canonical (current state) and use
     published slugs in every downstream artefact (T-12, T-13, T-14
     fixtures). Lower churn. Recommend (b) — the file is the artifact's
     identity but the slug is the system's; mixing them is fine as long
     as it's documented.

2. **`alert-fatigue-reviewer` lingers in the library.** With the swap
   to `slo-designer`, the CDS skill stays in the curated library but
   isn't bundled. Listed for discoverability with no behavioural
   impact. Slot for Wave-4 review: either retag to `health` for clarity
   or rename to `clinical-alert-fatigue-reviewer` so its discovery
   filter is obvious. No action this wave.

3. **Persona vault path under composer.** The composer (T-07) expects
   each persona neuron's `frontmatter.links[].target` to start with
   `base/` when it references the parent occupation's members. Wave-4
   T-12 will need to author neuron links like
   `base/domains/observability/slo-designer` (note the `domains/`
   intermediate — that's what the vault builder emits, NOT just
   `base/slo-designer`). The vault builder's
   `_build_target_resolver_for_occupation` strips `.md` and matches
   exact path or bare slug — so `base/slo-designer` also works. T-12
   should standardise on the bare-slug form to keep neurons forward
   compatible with future folder reorgs.

4. **Recipe maintenance UX.** The 60-link recipe lives in a YAML file
   that's hand-edited. After Wave 4 lands the persona overlay, the
   total link count will grow (≥1 neuron → ≥1 base member link per
   ADR-005). A small linter would catch typos and dangling targets at
   recipe edit time, before they cause `unresolved_link` warnings at
   build time. Slot for QA / Docs (T-14).

5. **`vault_builds.storage_url` mutation by the polish step.** The
   `ADR-013` immutability invariant is upheld at the *object* level
   (the original zip stays in S3) but not at the *row* level
   (`vault_builds.storage_url` is mutated). The composer is fine — it
   reads `storage_url` and gets the polished bytes. But any future
   "verify my vault" tool that wants to compute the canonical
   `content_hash` from a `(skill_id, version)` lookup needs to be told
   that the row's `content_hash` is the post-polish hash, not the
   builder's pre-polish hash. The `build_log_json` doesn't currently
   carry both. If we want both, extend `vault_builds.build_log_json`
   with a `pre_polish_hash` field — out of scope this wave but
   trivially additive in Wave 5.

6. **T-12 piggybacks cleanly.** T-12 (sample persona seed neurons)
   will:
   - Create a *new* creator (`@jane-devops-demo` per ADR-016 Q-4) —
     reuses the `_ensure_curated_user` pattern but for a demo handle.
   - Reference the AI DevOps Engineer occupation by
     `parent_occupation_id` — the occupation skill row's UUID is
     deterministic now per the published artifact in `vault_builds`
     and `occupations`.
   - Build a persona vault via `enqueue_persona_build` —
     `apps/api/src/vault/builder.py:build_persona` already supports
     this code path (verified by `test_build_persona_happy_path_3_neurons`
     in Wave 3A).
   - At download time the composer (T-07) merges the occupation
     vault + the persona vault into a buyer-specific bundle. Wave 3A
     and 3B confirmed the composer handles cross-build links cleanly.

7. **The unused `vault_jobs` façade in dev.** The script bypasses the
   Arq queue because there's no worker in dev. For prod-mode parity,
   the curation team should either:
   - (a) start an Arq worker as a sidecar to `publish_curated` /
     `build_devops_vault`, or
   - (b) keep the direct-call pattern and document it as the canonical
     "curation script" approach. T-13 will face the same choice for the
     demo CLI; whatever it decides, the build script should mirror.

---

## What Wave 3 (Curation) inherits to Wave 4

- A published `skillsgit-curated/ai-devops-engineer` v1.0.0 occupation
  with 30 cross-linked members.
- A green `vault_builds` row at
  `vaults/{occupation_skill_id}/1.0.0/{hash}.zip` ready for the
  composer to merge personas into.
- A canonical `(creator_id, slug)` resolution pattern (used by
  `_resolve_member_skills`) that T-12 can copy verbatim for resolving
  neuron creators.
- A working `.obsidian/graph.json` colour palette + injection helper
  that T-12 can reuse if it wants the persona-merged bundle to keep
  the same colour scheme (just append persona-handle-keyed groups).
- Documented file-vs-slug remap for the 7 affected DevOps files.
