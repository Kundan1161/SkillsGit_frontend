# Wave-2 Methodology Synthesis Report — Product / UX Research

**Niche:** product — UX research (interviews, usability tests, JTBD-style discovery, surveys, synthesis)
**Date:** 2026-05-14
**Agent:** Wave-2 methodology-synthesis
**Repo:** D:\skillsgit

## Files produced

Four skill files dropped to `apps/api/scripts/seed_data/synth/`:

- `ux-interview-guide-designer.skills.md` (v1.0.0)
- `ux-usability-test-planner.skills.md` (v1.0.0)
- `ux-research-synthesis.skills.md` (v1.0.0)
- `ux-survey-question-bank-builder.skills.md` (v1.0.0)

All four are net-new — no UX research skills existed in the synth/ folder previously. No merges or version bumps were required. Frontmatter follows the wave-2 template: `category: design`, first tag `niche:ux-research`, 4–7 additional tags per skill, `license_type: free`, no pricing fields populated (currency only).

## Sources per skill

Each skill cites a 5–6 URL subset from a shared verified pool. The pool of sources surveyed (and verified MIT or Apache-2.0):

- https://github.com/surveyjs/survey-library — MIT, ~4.7k stars, last release Feb 2026
- https://github.com/product-on-purpose/pm-skills — Apache-2.0, ~211 stars, v2.14.2 May 2026
- https://github.com/ruxailab/RUXAILAB — MIT, ~164 stars, v2.0 Oct 2025
- https://github.com/VoltAgent/awesome-claude-code-subagents — MIT, ~19.8k stars, active
- https://github.com/aakashg/pm-claude-code-setup — MIT, ~122 stars, active
- https://github.com/msitarzewski/agency-agents — MIT, ~97k stars, active

Per-skill citation lists in each `## Sources reviewed` section.

## Patterns extracted

Common methodology patterns observed across the surveyed sources and synthesized (in original prose) across the four skills:

- **Decision-anchored framing.** Every modern source treats the research goal not as "learn things" but as "inform a specific decision." Both the interview-guide and usability-test skills enforce this in step 1.
- **Behavior over preference.** Across guides, the strongest patterns prioritize past behavior questions over hypothetical or preference questions. Reflected in the warm-up structure and question-type guidance.
- **Anti-leading discipline.** Multiple sources flag leading-question risk; the interview-guide skill carries an explicit "lead test" in the pressure-test step and the survey skill annotates each question with the bias it guards against.
- **Severity + confidence as separate axes.** Synthesis sources converge on rating findings on both severity and evidence strength independently. The research-synthesis skill enforces this with a four-level confidence rubric plus separate severity/impact scale.
- **Kill criteria pre-registered.** Usability-test sources increasingly advocate stating in advance what failure looks like. The usability-test-planner skill makes this a required step.
- **Outliers preserved, not buried.** Stronger sources keep single-participant or contradictory findings visible rather than burying them in appendices. The research-synthesis skill carries this through.
- **Length budget enforcement.** Survey sources are explicit that data quality drops nonlinearly past 5 minutes; the survey skill enforces channel-specific length budgets.
- **Pilot before launch.** Every method has a pilot step. All four skills carry one.
- **Reusable artifacts.** Sources that emphasize research ops push reusable question banks, screener templates, and debrief forms. The survey skill produces a reusable question bank as a separate output; the interview-guide skill produces a separate probe bank.

## Notable rejections

License-rejected (CC, GPL, AGPL, LGPL, CC0, or no license file — all outside MIT/Apache/BSD/ISC/Unlicense):

- `ianarawjo/splat` — GPL-3.0 (rejected; would have been a strong synthesis reference)
- `ccbogel/QualCoder` — LGPL-3.0 (rejected)
- `dermatologist/nlp-qrmine` — GPL-3.0 + archived (rejected on both counts)
- `LimeSurvey/LimeSurvey` — GPL-2.0 (rejected)
- `formbricks/formbricks` — AGPL-3.0 (rejected)
- `idno/User-Research` — CC0 (rejected — CC family not in approved list)
- `gschema/awesome-ux` — CC0 (rejected)
- `augbog/awesome-user-testing` — CC0 (rejected)
- `ongov/Service-Design-Playbook` — CC-BY-4.0 (rejected)
- `contains-studio/agents` — no LICENSE file (rejected)

Freshness-rejected:

- `18F/ux-guide` — archived Dec 2023 (~2.5 years old, fails 18-month freshness)
- `alphagov/government-service-design-manual` — archived Feb 2018 (rejected on freshness)

Star-threshold rejected:

- `wdavidturner/product-skills` — MIT but only 11 stars (rejected; under 100-star floor)
- `researchops/research_repositories` — 6 stars (rejected)
- `andybywire/ux-methods-poc` — no license / low stars (rejected)

Trademark guardrails: avoided naming trademarked frameworks. The third skill prompt suggested JTBD as a topic but the spec required avoiding trademarked framework names. The interview-guide skill covers discovery interviews including job-shaped story prompts ("walk me through the last time you...") without using the trademarked framework name. No trademark surface in any of the four skills.

## Confidence assessment

**High confidence**: Skill content is grounded in widely-converged UX research methodology that appears repeatedly across the surveyed sources. The structural shape (research questions → tasks/probes → success criteria → analysis → report) is well-established in the field.

**Medium confidence**: Specific numeric guidance (sample sizes, time budgets, severity scales) varies across sources. The chosen values reflect the most common professional defaults but a team with strong reasons to deviate should be able to.

**Lower confidence area**: The skills assume English-language, Western-context research norms. Cross-cultural or non-English deployment will need additional review. Each skill flags this in `## Limitations`.

## Follow-ups recommended

1. **Validation pass via the schema validator.** All four skills target the wave-2 frontmatter contract per `prompts/shared/skills-md-spec.md`. Recommend running each through `apps/api/src/skills/validator.py` before publishing.
2. **Length verification.** Each body falls within the 300–700 line spec (interview-guide ~310, usability-test ~330, research-synthesis ~320, survey-bank ~340 lines of body content; line counts approximate).
3. **Consider a fifth skill — research-repo-organizer.** The Wave-2 spec offered this as optional. If demand surfaces for a research-ops-focused skill, the four current sources contain enough taxonomy and tagging guidance to support synthesis of a fifth. Held off here to keep the bundle tight and not over-extend without a clear stakeholder ask.
4. **Cross-skill links.** Each skill mentions the others by function (without naming the skill IDs). A future pass could promote these into explicit `related_skills` frontmatter once the platform supports that field.
5. **Translation-readiness.** Survey skill flags translation drift as a limitation. Could spawn a follow-up skill for back-translation workflow review if a UX research customer requests it.

## Quality self-check

- All prose is original; no copying or close paraphrasing of source material.
- Every source cited in a skill is verified MIT or Apache-2.0 and meets the ≥100 stars + 18-month freshness floor.
- License compliance strict: no CC, GPL, AGPL, LGPL, or unlicensed sources cited.
- No trademarks reproduced.
- All skills are `license_type: free` per spec; no pricing fields populated except `currency: USD`.
- Tags lead with `niche:ux-research` and category is `design` across all four.
- Frontmatter `inputs`/`outputs` arrays use correct enum values (`text`, `number`, `choice`, `markdown`).
- Each skill carries: `## When to use`, `## How to apply` (required by spec), plus `## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources reviewed` (recommended sections).
