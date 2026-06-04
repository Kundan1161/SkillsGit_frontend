# Dev diary — Curation, Cycle 1 Wave 1

**Owner:** Curation
**Wave:** 1 (inventory + DevOps-occupation slug verification; no code)
**Started:** 2026-05-26
**Status:** shipped (handing off to Wave 3 for T-08)

This wave was inventory + planning, not curation authoring. The 30-skill DevOps set Wave-3 needs to ingest into the vault builder is now verified and the cross-link recipe is sketched, so T-08 can start the moment the vault builder (T-06) lands.

## What I shipped

1. **`team/inventory-synth.md`** — definitive count + per-domain bucket of `apps/api/scripts/seed_data/synth/`. Reconciles the 456 / 452 / 450 drift in the prior docs (it's three counts of the same library under different conventions; no skill files were added or deleted between Backend's run and now).

2. **`team/devops-occupation-slugs.md`** — verification of all 30 spec'd DevOps slugs (T-08 lines 244–279), per-slug fit assessment, two substitutions flagged with rationale, suggested `base/<domain>/` folder grouping per `03-vault-generation.md` §1, and a first-draft cross-link recipe with 60 links across 30 skills.

3. **This diary (`team/dev-diary-curation-wave1.md`)** — the hand-off doc QA-Docs is waiting on.

No code was touched. No `seed_data/devops/` directory was created — that's T-08's job under the vault-builder's API.

## What I broke / deferred

Nothing broken. Two decisions deferred to Wave 3 (or to a user-gated answer on `team/06-open-questions.md`):

1. **`alert-fatigue-reviewer` (Core slot 9) is not a DevOps skill.** The slug existed; the file is `category: healthcare`, `niche:clinical-decision-support` — a CDS alert-fatigue audit for EHR alert portfolios, not a Prometheus/Alertmanager fatigue review. I recommend substituting `slo-designer` (Core), which also closes the SLO → alert-policy → incident chain. **Wave 3 needs to accept or reject the substitution.**

2. **`cross-platform-stack-chooser` (Optional slot 23) is a mobile-dev skill.** The slug sounds platform-y; the body picks React Native vs Flutter vs Kotlin Multiplatform. The MVP plan's brief explicitly says "Curation may swap any optional slot if a better candidate exists" so I'm proposing the swap unilaterally to `instrumentation-coverage-reviewer` (it's the missing leg of the observability triangle). If Wave-3 / QA prefer to keep the mobile skill in the optional bucket, the fixture in `tests/fixtures/vaults/expected-devops-vault/` will need to assert the slug it actually chose.

Both substitutes already exist in `synth/` — no new authoring is required. See `team/devops-occupation-slugs.md` §Why the two substitutions for details.

Beyond the two substitutions, I deferred (intentionally) anything that requires Backend interfaces I can't ground-truth yet:

- The actual `cross-link-recipe.yaml` file is *sketched* in `devops-occupation-slugs.md`, not written to `apps/api/scripts/seed_data/devops/` — that path doesn't exist yet and is T-08's deliverable. Writing it now would let it drift before Wave 3 picks it up.
- The `occupation.yaml` (name, summary, domains, member roles) for the DevOps occupation is also T-08's. I provided a suggested `base/<domain>/` member grouping in `devops-occupation-slugs.md` §Final 30 to make that file mostly mechanical.

## Hand-off to Wave 3 (T-08)

The Curation agent that runs in Wave 3 to build `apps/api/scripts/build_devops_vault.py` should:

1. **Treat the 30-slug list in `team/devops-occupation-slugs.md` §Final 30 as canonical.** All 30 files exist as-is in `apps/api/scripts/seed_data/synth/{slug}.skills.md` — no missing files to author. Two slugs are substitutions from the original spec; if QA / Architect rejects the swaps, restore the original spec slugs and accept that slot 9 (alert-fatigue) will carry CDS content that's tonally off for a DevOps occupation.

2. **Adopt the cross-link recipe seed in `team/devops-occupation-slugs.md` §Cross-link recipe seed as the v1 file.** It's 60 links across the 30 skills using only the three relations Backend shipped (`applies`, `extends`, `see-also`). It compiles against the validator's `LinkEntry` model out of the box. Edit freely — it's a starting point. The reasoning behind each cluster (CI/CD axis, IaC axis, observability triangle, etc.) is documented in the section.

3. **For `occupation.yaml`,** the suggested folder grouping in `team/devops-occupation-slugs.md` §Final 30 → "Domain grouping for the vault's `base/` folder layout" maps each of the 30 slugs to one of the five domain folders called out in `03-vault-generation.md` §1 (`ci-cd`, `observability`, `infra-as-code`, `incident-response`, `platform`). The data-platform optional cluster (Spark + 4 Kafka) lands under `platform/` for now; if Wave-3 wants a sixth folder, that needs `03-vault-generation.md` §1 amended (Architect call).

4. **Frontmatter `kind` field on member skills:** none of the 30 member files currently set `kind:` in frontmatter — they default to `kind: skill` per the Backend Wave-1 validator extension. The vault builder (T-06) should not mutate the source files to set `kind` — it should rely on the default. Only the *occupation* itself (the new top-level Skill row T-08 creates) gets `kind: occupation`.

5. **`vault_path` is server-assigned.** The Backend Wave-1 validator rejects creator-set `vault_path` with code `frontmatter.vault_path: server_assigned`. T-08 must NOT write `vault_path:` into the source `.skills.md` files. T-06 (vault builder) sets it when emitting each file into the bundle. Per the data-flow in `03-vault-generation.md` §6, the value is `"base/<domain>/<slug>.md"`.

6. **Cross-link recipe relations beyond what's shipped:** if Wave-3 wants `requires` / `supersedes` / `depends_on`, file an entry in `team/06-open-questions.md` and ping Backend Wave-2. Backend already flagged this as their O-4 in `dev-diary-backend-wave1.md` §Open questions item 4. Without `requires`, some links in the recipe seed are slightly loose (`slo-designer → alert-policy-architect` is `extends`; arguably it's `requires`).

7. **Re-running the script must be idempotent** per T-08 acceptance criterion. The slug list is fixed; the recipe is data; the occupation row uses `INSERT … ON CONFLICT (creator_handle, slug) DO UPDATE` (mirrors `publish_curated.py` discipline). I confirmed no slug in the 30 collides with the demo creators' slugs in `apps/api/scripts/seed_data/*.skills.md`.

8. **Watch out for the off-domain frontmatter on the two substituted slugs' originals:**
   - `alert-fatigue-reviewer` will still be in the published library after T-08 runs (T-08 doesn't yank it, just doesn't bundle it). Buyers will find it via search but it'll be a CDS skill, not a DevOps one. That's fine — it's accurate; the slug just shouldn't be in this occupation's member list.
   - Same for `cross-platform-stack-chooser` if it's left out.

9. **What's NOT in the inventory (so Wave-3 doesn't go hunting):** 6 demo seed files live one folder up at `apps/api/scripts/seed_data/*.skills.md` (the `janedoe-*`, `marcoart-*`, `samdata-*` files) and are NOT part of `@skillsgit-curated`. They are not candidates for the DevOps occupation. Validator test fixtures at `apps/api/tests/fixtures/skills/*.skills.md` are also not candidates.

10. **For QA-Docs (T-14) downstream:** the expected-vault fixture should be derived from the final 30-slug list above. If you regenerate the fixture from a Wave-3 vault build, the snapshot's `files[]` array should contain exactly these 30 `vault_path` entries (sorted by `vault_path` for stable diffs). The two substituted slugs (`slo-designer`, `instrumentation-coverage-reviewer`) replace the two spec'd slugs (`alert-fatigue-reviewer`, `cross-platform-stack-chooser`) — update the test_occupation_flow assertion accordingly.

## Verification

Counts confirmed via `Glob` + PowerShell `Get-ChildItem` on `apps/api/scripts/seed_data/synth/`:
- 450 `*.skills.md`
- 79 `_report_*.md`
- 1 other (`README.md`)
- Total: 530 entries.

All 30 spec'd DevOps slugs exist as files (Test-Path = True for each) — no missing files. The two slugs flagged for substitution exist; their frontmatter `category:` and `niche:*` tags don't match the DevOps occupation's intent. The two proposed substitutes (`slo-designer`, `instrumentation-coverage-reviewer`) also exist and have DevOps-aligned frontmatter from the same Wave-3 observability-SRE batch as several other Core members, so voice/rubric consistency is preserved.

Wave totals from `git log --oneline -- apps/api/scripts/seed_data/synth/` reconcile to 450:
```
W1=30 + W2=89 + W3=90 + W4=37 + W5=36 + W5c+W6+W7=168 = 450 ✓
```
Plus 6 seed (third-party creator simulation files at `seed_data/*.skills.md`) = 456 total published. Matches what `context/README.md` reports.
