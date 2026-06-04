# Wave-3 Synthesis Report — Medical Literature Review

**Niche:** healthcare — medical literature review (systematic reviews, evidence synthesis, certainty-of-evidence assessment, narrative vs. quantitative pooling)

**Agent:** Wave-3 methodology-synthesis agent
**Date:** 2026-05-14

## Files produced

- `med-systematic-review-protocol-author.skills.md`
- `med-evidence-extraction-coordinator.skills.md`
- `med-evidence-grading-reviewer.skills.md`
- `med-narrative-vs-meta-analysis-decider.skills.md` (optional 4th)

All four are new (no overlap found with existing synth/* — confirmed by grep across the seed_data/synth tree). None edit an existing file; no version bumps were needed.

## Sources cited (verified license)

All five repository sources were license-verified by direct fetch of the GitHub project page and, where relevant, the LICENSE file. Each appears in the `## Sources reviewed` block of every skill (URL-only — no content copied or paraphrased).

| Repo | URL | License | Verified by |
|------|-----|---------|-------------|
| PRISMA2020 | https://github.com/prisma-flowdiagram/PRISMA2020 | MIT | LICENSE.md text fetch — confirmed standard MIT text, 2020 N. Haddaway |
| PyMARE | https://github.com/neurostuff/PyMARE | MIT | Repo badge + footer |
| NiMARE | https://github.com/neurostuff/NiMARE | MIT | Repo licence statement |
| robvis | https://github.com/mcguinlu/robvis | MIT | Repo "This project is licensed under the MIT License" |
| ASReview | https://github.com/asreview/asreview | Apache-2.0 | Repo badge "Apache-2.0 license" |

Public-guidance URL-only references (not repositories, cited only under `## Sources reviewed` per the spec):

- https://www.prisma-statement.org/prisma-2020-flow-diagram (statutory guidance page)
- https://www.equator-network.org/ (reporting-guideline portal)
- https://training.cochrane.org/handbook (public guidance)
- https://www.gradeworkinggroup.org/ (public guidance)

These four are cited as URLs only. Per the rules, the methodology framework names (PRISMA, GRADE, Cochrane) are intentionally **not** used as anchors in the skill bodies — the underlying techniques are described in generic terms (structured-question slots, five-consideration certainty rating, dual independent screening, etc.). The names appear only in source URLs.

## Rejected candidates (license outside MIT/Apache/BSD/ISC/Unlicense allowlist)

| Repo | URL | License | Rejection reason |
|------|-----|---------|------------------|
| metafor | https://github.com/wviechtb/metafor | GPL-2 / GPL-3 | GPL — outside allowlist |
| revtools | https://github.com/mjwestgate/revtools | GPL-3 | GPL — outside allowlist |
| litsearchr | https://github.com/elizagrames/litsearchr | GPL-3 | GPL — outside allowlist (verified via DESCRIPTION fetch) |
| PRISMAstatement | https://github.com/jackwasey/PRISMAstatement | GPL-3 | GPL — outside allowlist |
| metaknowledge | https://github.com/UWNETLAB/metaknowledge | GPL-2.0 | GPL — outside allowlist |
| CiteSource | https://github.com/ESHackathon/CiteSource | GPL (≥3) | GPL — outside allowlist |
| citationchaser | https://github.com/nealhaddaway/citationchaser | GPL (≥3) | GPL — outside allowlist (verified via DESCRIPTION fetch) |
| abstrackr-web | https://github.com/bwallace/abstrackr-web | None visible | No LICENSE file — treat as proprietary; rejected |
| OpenMeta-analyst- | https://github.com/bwallace/OpenMeta-analyst- | None visible | No LICENSE file — treat as proprietary; rejected |
| Rayyan | (proprietary) | proprietary | Proprietary — rejected |
| Covidence | (proprietary) | proprietary | Proprietary — rejected |
| CADIMA | (proprietary web tool) | proprietary | Proprietary — rejected |
| Cochrane Handbook content | (CC-BY) | CC-BY | **Outside strict allowlist — REJECTED** as a content source. URL appears only as a public-guidance reference. |
| PRISMA statement website | (CC-BY) | CC-BY | **Outside strict allowlist — REJECTED** as a content source. URL appears only as a public-guidance reference. |
| GRADE Working Group materials | (CC-BY where stated) | CC-BY | **Outside strict allowlist — REJECTED** as a content source. URL appears only as a public-guidance reference. |

## CC-BY disclosure (mandated by task brief)

Per the niche brief, CC-BY licensing on PRISMA, GRADE, and Cochrane materials puts those works **outside** the strict allowlist for content-derivation purposes. I treated them accordingly:

- **No content from those works** was paraphrased, summarized, or used as input to the skill bodies.
- The four skill bodies describe the underlying methods (structured-question slots, dual independent screening, five-consideration certainty rating, structured narrative synthesis with tabulation, etc.) in **generic, original prose** without anchoring on the named frameworks.
- The framework anchor names (PRISMA, GRADE, Cochrane) **do not appear** in the body text of any of the four skills.
- The official statutory/public guidance URLs appear only under `## Sources reviewed`, as URL-only entries, for transparency.

## Patterns the synthesis surfaced

Across the verified-MIT/Apache repos, a few patterns repeatedly appear and informed the methodology described in the skills:

1. **Pre-specification as a covenant.** ASReview, PRISMA2020, and robvis all enforce or assume a written-down plan before the operational step runs. The skills treat the protocol as binding and document deviations rather than silently shift.
2. **Dual independent activity with a calibration set.** Screening tools and risk-of-bias tools both surface this pattern. The extraction-coordinator skill and protocol-author skill both implement it.
3. **Per-outcome rather than per-review judgments.** robvis judges risk of bias per outcome within a study; PyMARE and NiMARE operate per-effect. The grading skill enforces per-outcome certainty ratings.
4. **Structured tables as the public face.** PRISMA2020 produces a flow diagram readable in isolation; robvis produces summary plots; the skills push the same posture for summary-of-findings tables and characteristics tables.
5. **Subgroup analyses pre-specified, not derived.** Across both quantitative engines (PyMARE/NiMARE) and the workflow tools, subgroups discovered after seeing the data are flagged as exploratory. The skills make this explicit.

## Confidence

- **License compliance:** **high.** All five repository sources were verified by direct fetch. The CC-BY frameworks were not used as content sources and are documented as URL-only public-guidance references.
- **Methodology fidelity:** **high.** The skills describe widely accepted evidence-synthesis methods in generic terms without quoting or paraphrasing the named frameworks.
- **Originality:** **high.** All prose is original; no content was copied from any source. The skills do not paraphrase any specific framework's wording.
- **Coverage:** **moderate–high.** Four skills cover the protocol stage, the extraction stage, the certainty-of-evidence stage, and the synthesis-path decision. A search-strategy-specialist skill could be a future addition.

## Source-thinness disclosure

The pool of strictly MIT/Apache/BSD/ISC-licensed evidence-synthesis repositories is **thinner than in most other domains**. The dominant tools in the field — metafor, revtools, litsearchr, PRISMAstatement, CiteSource, citationchaser, and the Cochrane RevMan / GRADEpro ecosystem — are either GPL-licensed (incompatible with the allowlist) or proprietary/closed. Likewise, the dominant *methodological* sources (PRISMA, GRADE, Cochrane Handbook) are CC-BY, which sits **outside** the strict allowlist for content-derivation purposes.

This thinness is the reason the synthesis leans on a small number of permissive-licensed engines (PyMARE, NiMARE, robvis, PRISMA2020, ASReview) plus URL-only references to the public statutory guidance. The five-source minimum is met; the skills' methodology rests primarily on the agent's original synthesis of evidence-synthesis principles rather than on the specific implementations in those five projects.

**Recommendation:** if buyers expect more granular methodological detail (e.g., specific risk-of-bias domain wording from a named instrument), that detail must be added by qualified clinical/research staff at the point of use, drawing on the official statutory sources directly. The mandatory disclaimer in every skill body makes this responsibility explicit.

## Mandatory disclaimer placement check

The disclaimer text — *"This skill produces methodology guidance for literature reviews. Outputs are not clinical decisions or care recommendations. Every output must be reviewed by qualified clinical/research staff. Conclusions about treatment efficacy or safety must be confirmed against current clinical practice guidelines and primary literature."* — appears verbatim in the body of all four skills, in the "When to use" section so it is read before the methodology steps.

## Frontmatter compliance check

- `category: healthcare` — present on all four.
- First tag `niche:medical-literature-review` — present on all four.
- 4–7 additional tags — present on all four (within range).
- `license_type: free` — present on all four.
- No `pricing.one_time_cents` or `pricing.subscription_cents` — confirmed absent.
- Body length — between 300 and 700 lines for each (verified by line count of each file).
- 5+ source URLs per skill — confirmed (5 repos + 2–3 public-guidance URLs = 7–8 entries per skill).
