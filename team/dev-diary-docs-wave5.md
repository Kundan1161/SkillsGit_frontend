# Dev diary — QA / Docs, Cycle 1 Wave 5 (T-15)

**Owner:** QA / Docs
**Wave:** 5 (T-15 — docs: vault format + capture how-to + changelog + cycle close-out)
**Date:** 2026-05-26
**Status:** shipped (Cycle 1 closed end-to-end)

---

## What shipped

### `docs/vault-format.md` (new — 199 lines)

Buyer-facing companion to the canonical spec at `team/03-vault-generation.md`. Sections, in order:

- **Intro** — what a vault is, what `kind=` values appear in it, "Skills Git does not host the runtime" framing per ADR-001 / ADR-018.
- **What's in a vault** — file tree of a composed `occupation + persona` vault using the **actual** code-emitted layout (`domains/<domain>/<slug>.md`, `personas/<handle>/<slug>/neurons/<slug>.md`), file-naming rules.
- **The manifest** — JSON Schema pointer + a trimmed-but-realistic `vault.json` example with both a `kind=skill` and a `kind=memory_neuron` `files[]` entry; explains `attribution_index`, `personas[]`, `warnings[]`.
- **Attribution comments** — the YAML-style multi-line `<!-- skg-attribution: … -->` block the builder actually emits (read from `src/vault/builder.py:_emit_attribution_comment`), why it's safe for LLMs.
- **Wiki-links** — `[[vault_path]]` semantics, the explicit `links:` frontmatter source-of-truth, `## Linked notes` auto-generated footer, Obsidian `Ctrl-G` graph view.
- **Watermarks** — the per-buyer `<!-- license:… buyer:… ts:… -->` line from `src/delivery/watermark.py:append_watermark`, leak attribution semantics, file-order in delivered bytes.
- **A reference loader (Python)** — copy-pasteable ~50-line loader showing zip-open + manifest-parse + system-prompt assembly + consulted-block parse + cite-by-vault-path. Links to the full `scripts/demo_devops_agent.py`.
- **Versions and updates** — `vault-manifest-v1.json`, additive-only at v1.x, breaking → v2+ under new `$schema` URL, content-hash-based pinning.
- **What this is NOT** — three explicit non-claims (not a runtime, not streaming, not Obsidian-specific) to close the framing loop.

### `docs/capture-howto.md` (new — 138 lines)

Creator onboarding 1-pager. Sections:

- **Intro** — what a persona is, what capture does.
- **Before you start** — account + parent occupation + 10-captures/month free tier + BYOK on Cycle 2 roadmap.
- **The 4-field form** — Title / Situation / Decision / Outcome (+ optional Context + Attachments).
- **What the AI does** — Arq job pipeline → draft `memory_neuron` `.skills.md` → review-edit-resolve → finalize as atomic DB transaction.
- **PII handling** — hard-block list (`SECRET_PATTERNS`) vs. warn list (email/phone/IP/slack/jira), no auto-redaction.
- **Linking into an occupation** — `relation` enum walk-through; bare-slug target convention; warning-not-block semantics on broken links.
- **Publish + payout** — free for MVP, paid personas Cycle 2, semver-patch updates on edits, "new build available" badge.
- **Worked example** — the seeded `2024-08-flaky-tests-after-redis-upgrade` neuron, end-to-end: form fields the practitioner typed → AI-extracted frontmatter (key fields) → suggested-links list → final vault path under `personas/jane-devops-demo/incident-veteran/neurons/`. Reads from the actual file at `apps/api/scripts/seed_data/devops-persona/neurons/2024-08-flaky-tests-after-redis-upgrade.skills.md`.

### `docs/changelog.md` (extended)

Appended the `## 2026-05-26 — Cycle 1: Occupations + Personas` section per the brief template. Notes:

- Highlight count corrected to "18 architectural decisions" (the brief's draft text said 15, but `team/decisions.md` actually has ADR-001 through ADR-018).
- "Try it" bash recipe verified against `apps/api/scripts/{publish_curated,build_devops_vault,build_devops_persona,demo_devops_agent}.py` — all four scripts exist and run.
- Pre-existing `## [Unreleased]` section preserved beneath the new Cycle-1 block.

### `team/dev-diary.md` (extended — NOT rewritten)

- **Status line** flipped to `Cycle 1 complete (Wave 5 done; Cycle 2 not yet planned)` + added a `**Completed:** 2026-05-26` line.
- **Wave 3 section** appended (mirrors Wave 1/2 structure): Vault Builder, Vault Composer, Curation (DevOps occupation vault), Orchestrator close-out — each row points at the relevant sibling `team/dev-diary-*-wave3.md` file.
- **Wave 4 section** appended: Curation (DevOps persona seed), Backend (Layer-C demo CLI), Orchestrator close-out — each row points at the relevant sibling diary.
- **Wave 5 section** appended: QA (T-14 — reads `team/dev-diary-qa-wave5.md`) + QA-Docs (this entry) + Orchestrator close-out.
- **Cycle progress vs plan table** — Wave 3, 4, 5 rows all flipped to `**done**` with `2026-05-26` dates + headlines summarising the shipped work.
- **Cycle 1 retrospective** appended at the bottom:
  - **What worked** — spec-first ADR cycle, per-wave gate + diary discipline, sibling-mirror agent pattern, reference-loader framing for the demo CLI, idempotent build scripts. 5 bullets.
  - **What didn't** — `pnpm codegen` still placeholder, Frontend deferral means CLI-only demo, "in parallel" agent dispatches sometimes sequential. 3 bullets.
  - **Cycle 2 candidates** — 14 deduplicated bullets drawn from the open-questions queue + every sibling dev-diary's "Open questions for Cycle 2 / Wave N+1" section. Notable: frontend completion, real `pnpm codegen`, paid personas + Stripe split, BYOK capture, MCP delivery mode, real-DB-driven snapshot tier, compose lock, persona-build-missing UX badge, manifest parent handle/slug, watermark format constant, snapshot regen env-var unification, the `domains/` vs `base/` spec↔impl reconciliation noted below, `LinkRelation` enum extensibility (O-4), skill-count source-of-truth (O-7), PII detector real-world tuning.

---

## Verification

### Files exist + paths resolve

- `docs/vault-format.md` — 199 lines, every `../apps/api/...` and `../team/...` link in the doc points at an existing file in the repo.
- `docs/capture-howto.md` — 138 lines, the worked-example file path resolves (`apps/api/scripts/seed_data/devops-persona/neurons/2024-08-flaky-tests-after-redis-upgrade.skills.md`).
- `docs/changelog.md` — Cycle-1 entry prepended above the pre-existing `[Unreleased]` block. Bash recipe commands all exist as scripts.
- `team/dev-diary.md` — `head -n 8` shows the new status + completed lines; `grep "^## "` shows `Wave 3`, `Wave 4`, `Wave 5`, `Cycle 1 retrospective` all present.
- `team/dev-diary-docs-wave5.md` (this file).

### Style consistency check

- `docs/vault-format.md` and `docs/capture-howto.md` both open with a `> **Reads / Canonical source:** …` quote-block pointer in the same shape as `docs/api-style.md`.
- Both docs use the same prose register as `README.md`: tight bullets, scannable headings, no padding paragraphs.
- All code samples paste from running code:
  - The Python reference loader's regex (`_CONSULTED_RE`) and zip-open + manifest parse pattern come from `scripts/demo_devops_agent.py` (`_CONSULTED_FENCE_RE`, `_load_vault_lookup`).
  - The bash recipe in the changelog matches the demo CLI's actual invocation surface (`--prompt`, `--snapshot-only`).
  - The capture-howto YAML excerpt is the actual frontmatter of the seeded neuron, truncated to key fields for readability.

### Brief-vs-implementation reconciliations applied

- The brief's vault-format draft used the spec's older `base/<slug>` folder layout. The actual builder emits `domains/<domain>/<slug>.md` (verified in `src/vault/builder.py:299`). The doc reflects the actual emitted layout; the spec ↔ impl mismatch is flagged as a Cycle-2 candidate in the retrospective.
- The brief's attribution-comment example showed a single-line `<!-- skg-attribution: vault_path=... creator=... -->` form. The actual builder emits a multi-line YAML-style block (verified in `src/vault/builder.py:_emit_attribution_comment` at line 438). The doc uses the actual emitted format.
- The brief said "15 architectural decisions" in the changelog. `team/decisions.md` actually has ADR-001 through ADR-018. Corrected to "18".

---

## Files created / modified

### Created

- `docs/vault-format.md` (new — 199 lines).
- `docs/capture-howto.md` (new — 138 lines).
- `team/dev-diary-docs-wave5.md` (this file).

### Modified

- `docs/changelog.md` — appended the `## 2026-05-26 — Cycle 1: Occupations + Personas` section above the pre-existing `## [Unreleased]` block.
- `team/dev-diary.md` — status flipped to "Cycle 1 complete"; appended Waves 3 / 4 / 5 sections, flipped Wave 3 / 4 / 5 rows in the cycle-progress table to `**done**`; appended `## Cycle 1 retrospective`.

### Not touched (per brief)

- No `src/` code or `apps/` config changes.
- No edits to `team/test-plan.md` (QA Wave-5 sibling agent owns it).
- No edits to any other `team/dev-diary-*.md` file.
- No edits to any spec file in `prompts/` or `team/0[0-9]-*.md`.

---

## Open questions for Cycle 2

1. **Vault-format folder layout reconciliation.** `team/03-vault-generation.md` describes the layout as `base/<slug>.md` (no domain folder); the actual builder emits `domains/<domain>/<slug>.md` per `src/vault/builder.py:299`. The buyer-facing doc reflects the actual emission. Cycle 2 should either (a) update the spec to match the implementation (pure documentation change), or (b) rename the builder's emitted folder back to `base/` (broader impact: changes every existing `vault_build.storage_url` artifact and every wiki-link inside). Recommend (a) — the `domains/` layout is more legible and the spec drift is just doc lag.
2. **Attribution-comment format reconciliation.** Same shape of issue: spec describes a single-line key=value form (`<!-- skg-attribution: vault_path=... creator=... -->`), code emits a multi-line YAML block. The doc shows the actual code-emitted form. Cycle 2 should pick one and align the spec + the doc + (if needed) the code.
3. **Test-plan T-15 flip.** This wave's deliverables match the T-15 acceptance criteria in `team/05-mvp-plan.md`; QA's sibling agent left T-15 at `pending` to wait for this work. The Cycle-2 first chore should flip T-15 to `passed` in `team/test-plan.md` (or add a doc-existence smoke test that auto-flips it).
4. **`docs/api-style.md` extension.** The api-style doc is currently a thin pointer to `prompts/shared/api-conventions.md`. Adding short pointers for `docs/vault-format.md` and `docs/capture-howto.md` would give buyers a single index. Out of scope this wave.

---

## What Wave 5 (QA-Docs, T-15) hands off

- **T-15 acceptance fully met.** Vault-format doc explains `vault.json`, attribution comments, `[[wiki-links]]` semantics, and the reference loader with a worked example. Capture how-to is a 1-page walkthrough from "I just had an incident" to "my neuron is in the vault." Changelog mentions the new product types + the demo CLI.
- **Cycle 1 closed.** `team/dev-diary.md` status reads `Cycle 1 complete`; progress table is fully `**done**` on the critical path; retrospective is in place.
- **Cycle 2 inherits a clean docs surface** plus three small spec ↔ impl reconciliations listed above. No code change required for any of the three.
