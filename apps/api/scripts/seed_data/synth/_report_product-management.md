# Wave-2 Synthesis Report — Product (PM Frameworks)

**Niche:** product — PM frameworks (PRDs, OKRs, prioritization, roadmaps)
**Agent run date:** 2026-05-14
**Skills produced:** 5

## Skills

1. `prod-prd-drafter.skills.md` — PRD Drafter
2. `prod-prioritization-frame-picker.skills.md` — Prioritization Frame Picker (RICE / value-effort / opportunity scoring / MoSCoW / ICE / WSJF / Kano)
3. `prod-okr-set-reviewer.skills.md` — OKR Set Reviewer
4. `prod-quarterly-planning-facilitator.skills.md` — Quarterly Planning Facilitator
5. `prod-feature-spec-audit.skills.md` — Feature Spec Audit (kickoff readiness)

All five are new (no overlap with existing synth files, which under `prod-*` were productivity/writing — meeting summarizer, stakeholder update writer, tech doc drafter). No merges performed; all skills versioned 1.0.0.

## Sources approved (≥100 stars, ≤18 months freshness, permissive license)

- https://github.com/phuryn/pm-skills — MIT, 11.2k stars
- https://github.com/product-on-purpose/pm-skills — Apache-2.0, 211 stars, last release May 11 2026
- https://github.com/anombyte93/prd-taskmaster — MIT, 417 stars, v3.0.0 Feb 12 2026
- https://github.com/github/spec-kit — MIT, 99.4k stars, v0.8.10 May 14 2026
- https://github.com/ploi/roadmap — MIT, 560 stars, v4.21 March 23 2026

Each skill cites all five. Total = 5 unique sources, within the 5-10 band.

## Sources rejected (and why)

- **domenicosolazzo/awesome-okr** — CC0-1.0. Not in allowlist (MIT/Apache-2.0/BSD/ISC/Unlicense). 1.8k stars but cannot be used.
- **joelparkerhenderson/objectives-and-key-results** — License could not be verified after multiple attempts (LICENSE file returned 404 on both master and main branches; no badge visible). Joel Parker Henderson's repos historically vary; rejected on inability to confirm permissive license.
- **deanpeters/Product-Manager-Skills** — CC BY-NC-SA 4.0 (non-commercial). Not allowed.
- **ProductHired/open-product-management** — Public Domain Mark 1.0. Not in strict allowlist; rejected on principle of conservative interpretation.
- **opulo-inc/prd-template** — CC BY-SA 4.0. Not allowed.
- **AlekOmOm/PRD_TEMPLATE** — MIT but 0 stars, fails ≥100 threshold.
- **AnandChowdhary/okrs** — Mixed: code MIT but the OKR *content* (which is the load-bearing part) is CC BY 4.0. Rejected.
- **dend/awesome-product-management** — CC0. Not allowed.
- **eyaltoledano/claude-task-master** — MIT *with Commons Clause*. The Commons Clause adds a non-compete restriction that makes the license non-OSI-permissive in the relevant sense. Rejected conservatively.

## Patterns observed across approved sources

- **Skill-style instructional artifacts are the dominant new format.** Both pm-skills repos (phuryn, product-on-purpose) ship template + workflow + example trios per skill. Common contract: a name, a "when to use," a numbered procedure, and example output. The synth skills here adopt the same shape but write original prose.
- **PRDs converge on a stable section spine.** TL;DR / problem / goals / non-goals / users / requirements / metrics / risks / rollout / open questions appears in slightly varied form across every PRD-adjacent source. The PRD Drafter skill commits to this spine and adds the "open-questions register" as an explicit auxiliary output.
- **Spec-driven development is gaining ground.** github/spec-kit and the agent-skills ecosystem push hard on user-story-with-acceptance-criteria format and traceable requirements. The Feature Spec Audit skill mirrors this completeness bar and adds operational concerns (observability, kill switch, rollback) that pure spec-driven workflows under-emphasize.
- **Prioritization framework choice is undertaught.** Most sources teach a single framework. The Prioritization Frame Picker skill explicitly addresses which-framework-when, which is the most common confusion in the wild.
- **OKR review is rarer than OKR setting.** Almost all sources describe how to write OKRs; few describe how to critique a draft. The OKR Set Reviewer fills this gap with a structured per-objective / per-KR / per-set evaluation.
- **Capacity math is universally hand-waved.** Quarterly Planning Facilitator codifies a defensible default (60-70% productive time, subtract committed work, reserve 10-20% buffer).

## Frontmatter notes

- All 5 skills use `category: productivity` (the closest seeded category to PM).
- First tag on every skill is `niche:product-management`.
- `license_type: free`, no pricing, per brief.
- `id` namespaced under `skillsgit-curated/`.
- All `required_models: [claude-opus-4-7]` with the standard compatible-models fallback list.

## Confidence

- **PRD Drafter** — high. Field is well-trodden; sources strongly converged on structure.
- **Prioritization Frame Picker** — high. Each framework is well-documented; the synthesis is in the *picker* logic, which is the skill's original contribution.
- **OKR Set Reviewer** — medium-high. The critique criteria are widely cited; calibration of stretch versus sandbag is judgment-shaped and the skill is explicit about that.
- **Quarterly Planning Facilitator** — medium-high. Strong agenda structure; capacity defaults are informed estimates and clearly flagged as such.
- **Feature Spec Audit** — high. The checklist is comprehensive and surface-area-aware; spec-kit conventions provided strong calibration.

## Follow-ups recommended

- **More PM sources.** This wave was constrained by the permissive-license requirement; CC0 and CC BY-SA dominate the PM-template space (Anthropic, awesome-okr, awesome-product-management, opulo-inc, AnandChowdhary). A v1.1 pass could revisit license terms or expand the allowlist to include CC0 for *templates* (vs code) if the platform decides that is acceptable.
- **Sibling skills not produced this wave.** Candidates for future waves: discovery-interview-guide-builder, north-star-metric-tree-designer, opportunity-solution-tree-walker, kano-survey-designer, launch-readiness-checklist, product-postmortem-writer (different from incident postmortem), customer-feedback-synthesizer, JTBD-statement-writer.
- **Cross-skill orchestration.** PRD Drafter → Feature Spec Audit is a natural pipeline. Prioritization Frame Picker → Quarterly Planning Facilitator is another. Consider explicit handoff annotations in a v1.1.
- **OKR cascade tooling.** The OKR Set Reviewer asks the user to paste `parent_okrs`; a future enhancement could integrate with an OKR-tracking tool (none of the approved sources offer a permissively-licensed runtime).
- **Localization.** All five skills default to English/Western conventions. International product teams (especially in Japan, where Kano is native; or in DACH where Scrum/SAFe conventions differ) may need calibration notes.

## Validation

- All 5 files conform to `prompts/shared/skills-md-spec.md` frontmatter schema (id, version, name, description, authors, category, tags, license_type, ai, trigger_keywords, example_invocations, inputs, outputs, changelog).
- Required body sections present in each: `## When to use`, `## How to apply`, `## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources reviewed`.
- No copied prose; methodology is synthesized from cross-source patterns and original writing.
- No secrets, no trademarks, no external scripts.
- File line counts: 204-230 each — in line with existing synth files (215-360 range observed in the folder).
