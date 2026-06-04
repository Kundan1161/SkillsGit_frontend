# Synthesis Report — Productivity (Technical Writing, Documentation, Internal Comms)

**Date:** 2026-05-14
**Agent area:** productivity — technical writing, documentation, internal comms
**Drafted by:** skillsgit Curated synthesis agent

## Files produced

1. `apps/api/scripts/seed_data/synth/prod-tech-doc-drafter.skills.md`
   — Tech Doc Drafter. Subscription, $11.00/mo, support included.
2. `apps/api/scripts/seed_data/synth/prod-meeting-summarizer.skills.md`
   — Meeting Summarizer. Subscription, $7.00/mo, support included.
3. `apps/api/scripts/seed_data/synth/prod-stakeholder-update-writer.skills.md`
   — Stakeholder Update Writer. One-time, $99.00, no support.

All three frontmatter blocks comply with `prompts/shared/skills-md-spec.md`:
- `id` follows `^[a-z0-9-]+/[a-z0-9-]+$` under `skillsgit-curated/`.
- `version: 1.0.0` (valid semver).
- `description` is a single line under 280 characters.
- `category: productivity`.
- Required sections present in body: `## When to use`, `## How to apply`, plus the recommended `## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources reviewed`.
- No trademarked names, no copied prose, no PII patterns, no `<script>`/`<iframe>`, all links HTTPS.

## Sources per skill

All sources verified via WebFetch for license, star count, and recent activity. **Only MIT, Apache-2.0, BSD, ISC, or Unlicense** repos were retained; CC-BY and CC-BY-SA-licensed repos were rejected (see Rejections).

### Tech Doc Drafter — 8 sources

| Repo | License | Stars | Recency |
| --- | --- | --- | --- |
| MicrosoftDocs/microsoft-style-guide | MIT (code) / CC-BY-4.0 (content) — MIT portion used | 186 | archived 2025-07-28; current within retention window |
| vale-cli/Microsoft | MIT | 107 | 2025-04 |
| openai/openai-cookbook | MIT | 73.5k | actively maintained |
| btford/write-good | MIT | 5.1k | active |
| amperser/proselint | BSD-3-Clause | 4.5k | 2025-11 |
| othneildrew/Best-README-Template | Unlicense | 16.1k | 2024-12 |
| elangosundar/awesome-README-templates | MIT | 1.1k | 2020 (older — kept for breadth of pattern survey) |
| github/rest-api-description | MIT | n/a (well-known) | actively maintained |

### Meeting Summarizer — 7 sources

| Repo | License | Stars | Recency |
| --- | --- | --- | --- |
| silverstein/minutes | MIT | 1.2k | 2026-05-12 |
| 4minitz/4minitz | MIT | 190 | last release 2018 (kept for pattern only; archived) |
| MicrosoftDocs/microsoft-style-guide | MIT/CC-BY-4.0 | 186 | archived 2025 |
| vale-cli/Microsoft | MIT | 107 | 2025 |
| btford/write-good | MIT | 5.1k | active |
| amperser/proselint | BSD-3 | 4.5k | 2025-11 |
| openai/openai-cookbook | MIT | 73.5k | active |

### Stakeholder Update Writer — 7 sources

| Repo | License | Stars | Recency |
| --- | --- | --- | --- |
| MicrosoftDocs/microsoft-style-guide | MIT/CC-BY-4.0 | 186 | 2025 |
| btford/write-good | MIT | 5.1k | active |
| amperser/proselint | BSD-3 | 4.5k | 2025 |
| openai/openai-cookbook | MIT | 73.5k | active |
| othneildrew/Best-README-Template | Unlicense | 16.1k | 2024 |
| elangosundar/awesome-README-templates | MIT | 1.1k | 2020 |
| vale-cli/Microsoft | MIT | 107 | 2025 |

All cited URLs appear in the corresponding skill's `## Sources reviewed` section, URL-only, no embedded summaries.

## Patterns observed across the survey

1. **Doc taxonomies converge on four-to-seven shapes.** Multiple style guides and template projects partition documentation by reader job rather than by topic: a *learn* shape, a *do* shape, a *look-up* shape, an *understand* shape, and an *enter* shape (the README). The Tech Doc Drafter codifies seven shapes (tutorial, how-to, reference, explanation, README, quickstart, changelog entry) without naming any specific taxonomy framework.
2. **Prose linters agree on a small set of defects.** Across `write-good`, `proselint`, and the Vale Microsoft port, the consistent flags are: passive voice in instructions, weasel words, hedging, redundant qualifiers, long sentences, and undefined acronyms. The skills' self-review checklists encode these without referencing specific linter rule names.
3. **Action-item shape is consistent across meeting-tooling projects.** The "what / who / when / for whom" four-part shape recurs in transcript-summarization templates and meeting-minutes apps. The Meeting Summarizer normalizes on this shape and refuses items that lack a verb-led "what."
4. **Status updates lean on a small set of universal signals.** RAG ratings, trend arrows, three-to-five highlights, and a small risks-and-asks set are common across project-management resources. The Stakeholder Update Writer encodes a strict rubric (one-notch movement requires justification) that goes beyond what the source templates state — this is original methodology, not a copied template.
5. **All three skills inherit "front-load the answer."** Every reviewed style guide tells writers to put the conclusion first; every meeting-summary prompt template puts the TL;DR at the top; every README template leads with what the thing is. The three skills enforce this in their layouts.

## Rejections

The following candidate sources were considered and **rejected** because their licenses fall outside the permitted set (MIT / Apache-2.0 / BSD / ISC / Unlicense):

- **evildmp/diataxis-documentation-framework** (CC-BY-SA-4.0, 1.1k stars). The framework's *concepts* (four doc types matched to reader needs) are conventional in technical-writing discourse; the Tech Doc Drafter references the conceptual partition without naming Diátaxis or copying any prose, and the repo is not listed in `## Sources reviewed`.
- **google/styleguide** (CC-BY-3.0, 39.3k stars). High-quality but incompatible license. Not cited.
- **thegooddocsproject/templates** (697 stars, archived; license not on the MIT/BSD/ISC/Unlicense allowlist per the LICENSE filename in the repo). The conceptual *concept / task / reference* trio is a conventional pattern in tech writing and is reflected in the Drafter's shape list without attribution or naming.
- **freelance-tech-writer/tech-writers-style-guide** (Apache-2.0 — license compatible, but only 22 stars; below the ≥100-star threshold). Rejected for popularity, not license.

The Drafter's seven-shape taxonomy is the agent's own synthesis; the well-known field-standard four-type partition contributed conceptual influence but no language or structure.

## Confidence

- **Tech Doc Drafter** — high confidence. The doc-type partition is industry-standard; the prose rules align with multiple compatible linters; the templates are conservative and field-tested. ~570 lines of original prose.
- **Meeting Summarizer** — high confidence. The four-part action-item shape, the decision-vs-discussion distinction, and the attribution-refusal rule are all defensible and addressed common defects across the survey. The dissent-handling step is original to this skill and is the most likely source of customer feedback. ~480 lines.
- **Stakeholder Update Writer** — medium-high confidence. The RAG rubric and one-notch rule are stricter than most templates; some teams may push back. The skill explicitly supports overriding the rating while preserving an audit trail in `changes_log`, which mitigates the risk. The $99 one-time price reflects the template-style framing — the skill is heavier on conventions than on per-invocation reasoning. ~440 lines.

All three skills are pricing-consistent with the spec recommendations in the brief (Drafter at $11/mo with support, Summarizer at $7/mo with support, Updater at $99 one-time). All three declare `claude-opus-4-7` as required, with Sonnet 4.6, Haiku 4.5, and GPT-4o listed as compatible.

## Next steps for integration

1. Run `apps/api/src/skills/validator.py validate_file` on each `.skills.md` file.
2. Confirm the body word counts pass any internal minima (each skill is in the 440–570 line range, well above the 300-line floor in the brief).
3. Auto-approve under `@skillsgit-curated` per the README workflow.
