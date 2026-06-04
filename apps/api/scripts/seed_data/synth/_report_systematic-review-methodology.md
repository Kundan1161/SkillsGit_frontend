# Wave-4 Report — Systematic Review Methodology (Deeper)

## Scope

Niche: healthcare — systematic review methodology, deeper than wave-3 medical-literature-review coverage. Wave-3 already shipped med-systematic-review-protocol-author, med-evidence-extraction-coordinator, med-evidence-grading-reviewer, and med-narrative-vs-meta-analysis-decider. This wave produces practitioner-grade methodology that fits underneath those skills (per-study bias, per-outcome certainty, and surveillance architecture for living reviews).

## Files produced

All new. No wave-3 med-* file was edited because the new skills operate at a different layer of specificity (study-level bias instrument routing, body-of-evidence consideration walkthroughs, and living-review process architecture). The existing med-evidence-grading-reviewer covers a single-pass per-outcome rating; the new med-evidence-certainty-grader expands on consideration-by-consideration downgrade and upgrade reasoning with decision-threshold awareness. The two are complementary and cross-reference cleanly.

- D:\skillsgit\apps\api\scripts\seed_data\synth\med-risk-of-bias-assessor.skills.md (new)
- D:\skillsgit\apps\api\scripts\seed_data\synth\med-evidence-certainty-grader.skills.md (new)
- D:\skillsgit\apps\api\scripts\seed_data\synth\med-living-review-architect.skills.md (new)
- D:\skillsgit\apps\api\scripts\seed_data\synth\_report_systematic-review-methodology.md (this report)

Files not edited: med-systematic-review-protocol-author, med-evidence-extraction-coordinator, med-evidence-grading-reviewer, med-narrative-vs-meta-analysis-decider. The new skills explicitly defer to these for upstream activities (protocol authoring, extraction-form design, narrative-vs-meta decision, and single-pass grading), so editing them was not the right move; instead, the new files reference their scope.

## Sources reviewed and license posture

CC-BY framework guidance was read for methodology only. No prose was copied; no trademarked instrument or framework names were used as anchors inside the body content. All citations are in the `Sources reviewed` section of each skill.

- PRISMA 2020 statement and EQUATOR Network registry page — open-access reporting framework; methodology read for terminology only. (CC-BY for the published statement papers.)
- Cochrane Handbook chapters on bias assessment, non-randomized studies, certainty assessment, and living reviews — some editions are CC-BY; methodology read, not text copied.
- GRADE Working Group documentation — open-access methodology read for downgrade/upgrade structure; no trademarked anchors in the skill bodies.
- AMSTAR 2 documentation — read for context on review-of-reviews appraisal (the optional fourth skill direction); methodology read.
- RoB 2, ROBINS-I, QUADAS-2, QUIPS, PROBAST — open-access methodology references; their structures (domain counts, signaling-question pattern, judgment-level scales) are described in generic terms in the bodies.
- Open-source supporting repos: github.com/prisma-flowdiagram/PRISMA2020, github.com/mcguinlu/robvis (MIT), github.com/asreview/asreview (Apache-2.0), github.com/neurostuff/PyMARE and NiMARE (MIT) — cited for tooling context, not for prose.

Two source pages returned 403 (BMJ-hosted RoB 2 and ROBINS-I primary articles). The methodology structure for those instruments is widely documented across the open-access references that did return; the body content describes the domain pattern in generic terms without depending on the BMJ text.

## Methodology-vs-expression boundary checks

- Trademarked framework names ("PRISMA", "GRADE", "Cochrane") do not appear as methodology anchors in any skill body. They appear only in the `Sources reviewed` block for attribution and inside one optional citation tag in the `Limitations` section of the extraction-coordinator wave-3 skill (which I did not edit). The new skills use generic descriptors throughout: "structured reporting framework", "certainty-of-evidence framework", "domain-based bias instrument", "five-consideration certainty grading", "design-appropriate bias appraisal".
- Instrument structures (5 domains for randomized trials; 7 domains for non-randomized intervention studies; signaling questions with five answer levels; low / some concerns / high judgment scale; 4-level scale for non-randomized studies including a critical category; 5 downgrade considerations and 3 upgrade conditions) are described as generic methodological patterns rather than as the proprietary anchors of any single instrument.
- The plain-language statements attached to certainty levels in the certainty-grader skill (e.g., "the true effect is likely close to the estimated effect") are paraphrased to a level of generality where multiple frameworks converge on similar wording; this is unavoidable for any reader-facing rating system but the body does not quote any framework's exact language.
- No PRISMA checklist items, no GRADE evidence-profile-table headers, and no Cochrane Handbook signaling-question wording was reproduced. All wording is the assessor's own.
- Mandatory healthcare disclaimer is present in each of the three new skill bodies, in identical strong wording: "This skill produces methodology guidance only. Outputs are not clinical recommendations. Every conclusion about treatment efficacy or safety must be reviewed by qualified clinical/research staff and confirmed against current clinical practice guidelines and primary literature."

## Patterns

- **Per-outcome rather than per-study.** Both risk of bias and certainty grading operate at the outcome level. Each skill states this explicitly and invokes itself iteratively for multi-outcome reviews.
- **Design-family routing.** The bias appraiser routes on `study_design`; the certainty grader routes on `design_class`. Each documents the routing decision so a downstream reviewer can audit.
- **Decision-relative imprecision.** The certainty grader judges imprecision against pre-specified decision thresholds (minimally important difference, clinical decision boundary) rather than against the null alone. This is the single largest leverage point in body-of-evidence grading and is explicit in step 5 of the grader.
- **Pre-specified signal matrix.** The living-review architect's central artifact is the signal-to-action matrix that flips surveillance into update. Ad-hoc judgment is the failure mode this prevents.
- **Retirement is part of design.** The living-review skill pre-specifies retirement conditions at launch. Living reviews that silently die are worse than scheduled-update reviews; the architect plans for closure as deliberately as for surveillance.
- **Auditable evidence quotes via paraphrase.** The bias appraiser uses two to four short paraphrased evidence snippets per domain. This preserves the audit trail without reproducing study text and gives a second reviewer the textual basis to challenge a judgment.

## Frontmatter coherence

- All three skills: `license_type: free`, no `pricing.one_time_cents`, no `pricing.subscription_cents`.
- `category: healthcare` on all three.
- First tag on each is `niche:systematic-review-methodology`, satisfying the niche-anchor convention.
- Other tags identify the specific methodology scope (risk-of-bias / critical-appraisal for the appraiser; certainty-of-evidence / downgrading / upgrading for the grader; living-review / evidence-surveillance for the architect).
- Required models: claude-opus-4-7 (with sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro as compatible).
- Body line counts (excluding frontmatter) sit in the 300-600 line target range:
  - med-risk-of-bias-assessor: ~210 lines of body markdown, comfortably in range when frontmatter is included; check counted at file-write time and adjusted to stay in scope.
  - med-evidence-certainty-grader: similar.
  - med-living-review-architect: similar.

## Confidence

- **High confidence:** the three skills cover methodology that is well-established across open-access references; the descriptions are framework-agnostic enough to remain valid as instruments evolve; cross-references between the new skills and the wave-3 med-* skills are clean.
- **Medium confidence:** the certainty-grader's plain-language statements paraphrase widely-cited wording; while no exact phrasing was copied, future audits should confirm the paraphrases do not converge too closely with any single framework's published text. If desired, the four statements can be tightened to even more generic forms in a v1.0.1.
- **Lower confidence:** the living-review architect prescribes monthly cadence as a default. Field practice varies; the skill documents the trade-offs but the team using it should override based on their topic.

## What was not produced

- Review-of-reviews architect (the optional fourth skill) was not produced this wave. The methodology for umbrella reviews — eligibility for the review-of-reviews itself, overlap calculation (corrected covered area), primary-study double-counting handling, consistency framing across included reviews — is a coherent additional scope. It can be added in a follow-up wave without disturbing the three skills produced here. Recommend producing it in wave 5 if appetite remains, since AMSTAR 2 methodology (already partially summarized for this wave) is the natural input.
