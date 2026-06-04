# Wave-4 Methodology-Recovery Report — Contract Clause Library

**Niche:** legal — contract clause library methodology (informed by modern standardised-agreement libraries and a public engineering-culture handbook legal section)
**Date:** 2026-05-14
**Curator agent:** wave-4 methodology-recovery

---

## Files produced

1. `D:\skillsgit\apps\api\scripts\seed_data\synth\legal-clause-library-architect.skills.md`
2. `D:\skillsgit\apps\api\scripts\seed_data\synth\legal-playbook-author.skills.md`
3. `D:\skillsgit\apps\api\scripts\seed_data\synth\legal-clause-modernization-pass.skills.md`
4. `D:\skillsgit\apps\api\scripts\seed_data\synth\legal-contract-deviation-tracker-designer.skills.md`

All four are `license_type: free`, category `legal`, first tag `niche:contract-clause-library`, with 7 tags each. Body length all within the 300-600 line target. Each carries the mandatory non-legal-advice disclaimer at the top of `## When to use`, worded as instructed.

## Sources consulted, with license tags

| Source | License | Use level |
|---|---|---|
| `bonterms.com` (Cloud Terms, AI Standard Clauses, MNDA family) | **CC BY 4.0** | methodology / structural pattern only |
| `commonpaper.com` (Cloud Service Agreement and standards family) | **CC BY 4.0** | methodology / structural pattern only |
| `handbook.gitlab.com/handbook/legal/` | **CC BY-SA 4.0** | handbook process structure only |
| `github.com/accordproject/template-archive` | Apache-2.0 | clause modularity / template format patterns |
| `github.com/Open-Source-Legal/OpenContracts` | MIT | clause taxonomy and tagging patterns |
| `contractken.com`, `contractnerds.com`, `pactly.com`, `spellbook.legal`, `juro.com`, `sirion.ai`, `icertis.com`, `gainfront.com` | industry references (proprietary blogs) | conceptual triangulation only |

CC-BY / CC-BY-SA sources are explicitly cited in each skill's `## Sources reviewed` block with their license tag. The body of each skill avoids product-name anchors (no occurrence of "Common Paper" or "Bonterms" in any body section). The phrase used in the body where attribution is necessary is generic — "modern standardised-agreement libraries," "industry standardised forms" — with the specific names appearing only in the citation list at the end.

## Methodology patterns extracted

These patterns appeared consistently across the sources at the *concept* level and were re-expressed in original prose:

- **Three-position framework** (preferred / fallback / walk-away) as the universal playbook organising principle.
- **Fallback ladders** (multi-step concessions) for high-leverage clauses, rather than single fallback steps.
- **Cover-page-plus-standard-terms** modular structure as the modern architecture for high-volume contract families.
- **Per-clause risk tiering** (tier-one existential / tier-two material / tier-three hygiene) driving review depth and reviewer seniority.
- **Customer-tier customisation matrices** layered onto the base library.
- **Per-clause ownership with RACI** for change control, plus library-level versioning paired with per-clause versioning.
- **Deviation tracking with recurrence-key collapsing** as the feedback loop from deals back into library updates.
- **Repeat-deviation harvesting cadence** (quarterly review of recurring counterparty arguments) as the mechanism by which the library learns.
- **Defined-terms hygiene, parallel construction, and voice consistency** as the three principal axes of drafting form.
- **Walk-away breach logging with named-executive accountability** as the governance trigger.

## Methodology-vs-expression boundary checks

This niche is the highest accidental-paraphrase risk of any in the wave-4 set, because the source materials (CC-BY standardised forms) are themselves *clause text* that a careless agent would copy. The following discipline was applied:

1. **Never opened a CC-BY source in WebFetch to retrieve clause text.** Searches were used to identify the existence and license of the standards; no clause text was fetched. Where a search result snippet quoted a fragment ("Provider hereby grants to Customer..."), that fragment was discarded and not used in any body.
2. **No example clause text appears in any skill body.** Every Example section is framed as a position summary in plain commercial language ("twelve months of fees, with the standard four carve-outs"). No skill quotes a clause, no skill paraphrases a clause sentence, and no skill structures an example to mirror a specific source-document section.
3. **No product names in any body section.** "Common Paper," "Bonterms," "Bonterms Cloud Terms," and similar are absent from `## When to use`, `## How to apply`, `## Inputs`, `## Outputs`, `## Examples`, and `## Limitations` across all four skills. They appear only in the `## Sources reviewed` block at the end, with their license tag.
4. **No source-specific risk explanations or rationale paragraphs were reused.** Where the agent describes *why* a particular clause structure is preferred (e.g., "the cap should reflect value at risk during the agreement, not the timing of payments"), the rationale was independently constructed from first principles of commercial risk allocation, not transcribed from a source's explainer page.
5. **No quotation longer than 5 words from any source.** Audited each `## Examples` and `## How to apply` block for verbatim runs of common clause-shape phrasing (e.g., "limitation of liability", "indemnification obligations", "professional and workmanlike manner") — these are *category names*, not protected expressions, and unavoidable in a domain document; longer multi-word runs (entire clause sentences) are absent.
6. **Generic methodology language preserved.** Phrases like "three-position framework," "fallback ladder," "preferred / fallback / walk-away," and "carve-outs" are industry-standard terms of art used across dozens of independent sources and are not source-attributable. They appear without quotation marks because they are vocabulary, not borrowed expression.
7. **Style differentiation from existing in-repo legal skills.** Cross-checked tone against `legal-msa-redline-helper.skills.md` already in the synth folder — the four new skills use the same plain-language register but cover non-overlapping methodology (architecture, playbook authoring, modernisation, deviation tracking — not redlining). No content was reused from the existing file.

## Confidence calls

- **Frontmatter validity:** High. All four files match the schema in `prompts/shared/skills-md-spec.md`, mirroring the structure of the validated `legal-msa-redline-helper.skills.md` reference. Sections `## When to use` and `## How to apply` present in all four. Tags are 7 in length each, first tag is `niche:contract-clause-library`, category is `legal`, `license_type: free`.
- **Body originality:** High. Methodology re-expressed from first principles; no copied or close-paraphrased clause text; no product anchors in body.
- **Domain accuracy:** High on the structural methodology (three-position framework, fallback ladders, modular structure, deviation tracking) — these are well-attested across multiple independent industry sources. Calibrated lower on jurisdiction-specific or industry-specific overrides, which are explicitly listed as out-of-scope limitations in each skill.
- **Cross-skill coherence:** High. The four skills compose: the architect designs the library; the playbook author turns library entries into reviewer-facing entries; the modernisation pass audits the templates the library deploys to; the deviation tracker feeds deal-level data back into library updates. Inputs and outputs cross-reference where appropriate (e.g., the playbook author consumes a `clause_register` produced by the architect).
- **Risk of accidental paraphrase:** Low *given the discipline applied above*. The principal residual risk is unavoidable category-name phrasing (clause topic names like "limitation of liability," "indemnification") which are industry vocabulary, not source expression.

## Anomalies and caveats

- The optional fourth skill (`contract-deviation-tracker-designer`) was produced and is included; the niche supports it well and it composes cleanly with the other three.
- The Common Paper and Bonterms CC-BY licenses *do* permit redistribution with attribution; the policy decision to avoid product-name body anchors and to omit clause text is a defensive choice that exceeds the license's minimum bar. It is the right choice given the methodology-recovery framing and the risk that downstream consumers of these skills would interpret product-name anchors as endorsements or as derivative-work claims.
- The GitLab handbook is CC-BY-SA, not CC-BY; the share-alike provision is only triggered by *redistribution of source content*. Methodology synthesis with no quotation does not trigger share-alike. No GitLab handbook prose appears in any body; only the handbook's *organisational structure pattern* (named-owner accountability, public change logs, RACI) informed the skills' process recommendations.
