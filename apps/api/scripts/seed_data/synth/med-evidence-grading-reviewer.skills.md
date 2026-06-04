---
id: skillsgit-curated/med-evidence-grading-reviewer
version: 1.0.0
name: Medical Evidence Grading Reviewer
description: Apply a structured certainty-of-evidence assessment to a body of medical studies — covering risk of bias, consistency, directness, precision, and publication bias — and produce a summary-of-findings table.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: healthcare
tags: [niche:medical-literature-review, evidence-synthesis, certainty-of-evidence, summary-of-findings, risk-of-bias, evidence-quality]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  tools_optional: [web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 10000
trigger_keywords:
  - grade the evidence
  - certainty of evidence
  - quality of evidence
  - summary of findings
  - downgrade for imprecision
  - downgrade for inconsistency
  - downgrade for indirectness
  - publication bias assessment
  - evidence profile
  - rate the body of evidence
example_invocations:
  - "Rate the certainty of evidence for SGLT2 inhibitors on cardiovascular mortality in HFpEF."
  - "Build a summary-of-findings table from these 12 included trials of digital CBT for adolescent depression."
  - "Help me decide whether to downgrade for indirectness when the population is older than our target."
inputs:
  - name: outcome_data
    type: text
    required: true
    description: Per-outcome summary of the evidence base — number of studies, designs, total participants, pooled effect estimate with CI, heterogeneity, and any risk-of-bias judgments already made.
  - name: comparison_context
    type: text
    required: true
    description: The clinical question this body of evidence informs (population, intervention, comparator, outcome, time horizon) and any anticipated absolute baseline risks for the summary-of-findings table.
  - name: design_mix
    type: text
    required: false
    description: Description of the predominant study designs and any non-randomized evidence relevant to the outcome.
  - name: known_concerns
    type: text
    required: false
    description: Specific concerns the team has already flagged (a high-risk-of-bias study, a heterogeneity signal, an out-of-range population subgroup).
outputs:
  - name: certainty_assessment_markdown
    type: markdown
    description: Per-outcome certainty rating with explicit reasoning for each consideration and the final overall rating.
  - name: summary_of_findings_table
    type: markdown
    description: A reader-facing table with relative effect, anticipated absolute effects at low and high baseline risk, number of participants and studies, certainty rating, and a plain-language summary.
  - name: open_questions
    type: markdown
    description: Items the methodology lead must confirm before the certainty ratings are finalized.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Medical Evidence Grading Reviewer

## When to use

Use this skill once the synthesis stage of a review has produced per-outcome estimates and the team needs to translate those estimates into a defensible certainty-of-evidence rating for each outcome. The certainty rating is what readers — clinicians, guideline panels, patients, payers — actually use to decide how confident to be in the result. A pooled hazard ratio without a certainty rating is half a finding.

This skill produces methodology guidance for literature reviews. Outputs are not clinical decisions or care recommendations. Every output must be reviewed by qualified clinical/research staff. Conclusions about treatment efficacy or safety must be confirmed against current clinical practice guidelines and primary literature.

Typical triggers:

- A review draft has pooled estimates and risk-of-bias ratings; the team needs the certainty column for the summary-of-findings table.
- A guideline panel is preparing recommendations and needs explicit certainty ratings for each critical outcome.
- A health-technology-assessment report needs an evidence profile section.
- A peer reviewer has asked the authors to make their certainty reasoning explicit, including the considerations they downgraded or upgraded for.

Do not use this skill for:

- Single-study appraisal — risk-of-bias judgments for one study at a time are an upstream activity. This skill consumes the per-study ratings; it does not produce them.
- Producing the pooled estimates — that is the synthesis stage.
- Writing clinical recommendations — the certainty rating informs but does not become the recommendation. A separate process weighs benefits, harms, values, preferences, resource use, equity, and acceptability.

## Inputs

- `outcome_data` (required) — Per outcome, the methodology lead should provide: number of studies, study designs, total participants, the pooled effect estimate and confidence interval (or, for narrative synthesis, a structured summary), the heterogeneity statistics, and any risk-of-bias rating already made (typically per study and overall for the outcome).
- `comparison_context` (required) — The structured question framing the body of evidence and the anticipated absolute baseline risks (often two — a representative low-risk and high-risk population for the summary-of-findings table).
- `design_mix` — Detail on the design types and any non-randomized evidence informing the outcome. Different starting points are appropriate for randomized vs. non-randomized evidence.
- `known_concerns` — Specific items the team has already flagged. The skill should explicitly address each in its reasoning, even if it ends up disagreeing with the team's first impression.

## How to apply

Apply the steps per outcome, in order. The output is one short reasoning block per consideration plus an overall rating. Where evidence is too thin to judge a consideration, mark it explicitly rather than defaulting to "no concerns".

### 1. Set the starting certainty

1.1. For an outcome informed predominantly by **randomized trials**, the starting certainty is **high**.

1.2. For an outcome informed predominantly by **non-randomized studies of interventions** (cohort, case-control, registry-based), the starting certainty is **low**.

1.3. For an outcome where both designs contribute substantively, set the start based on the design that drives the pooled estimate. State the choice explicitly so a reader can see the assumption.

1.4. Special cases: case series and case reports rarely support a certainty rating above very low for therapy questions. For diagnostic-accuracy questions, the starting certainty is typically high if the studies are cross-sectional with adequate reference standards.

### 2. Assess study limitations (risk of bias across the body)

2.1. Summarize the per-study risk-of-bias judgments for this outcome. The unit of analysis is the body of evidence for the specific outcome, not the studies as wholes — a study can be at low risk for one outcome and high risk for another.

2.2. Identify the **leverage-weighted risk of bias** — which studies contribute most weight to the pooled estimate, and what are their risk-of-bias profiles? A small low-risk-of-bias signal next to a large high-risk signal does not save the body.

2.3. Decide: no concerns, serious limitations (downgrade one level), or very serious limitations (downgrade two levels). Document the dominant domain (e.g., concealment, blinding, attrition, selective reporting).

2.4. A sensitivity analysis that excludes high-risk-of-bias studies and yields a materially different estimate is strong evidence of bias-driven distortion; mention the result of the sensitivity analysis in the reasoning.

### 3. Assess consistency (heterogeneity across studies)

3.1. Inspect the pooled estimate's heterogeneity:
   - Visual: does the forest plot show overlapping confidence intervals, or do studies cluster in different directions?
   - Statistical: heterogeneity statistic (I-squared, tau-squared, Q-test). Any single statistic is a partial signal; combine the visual and the numbers.
   - Direction of effect: are study point estimates on the same side of the null?

3.2. Decide: no concerns, serious inconsistency (downgrade one), or very serious inconsistency (downgrade two).

3.3. Pre-specified subgroup analyses that explain heterogeneity are a reason to present subgroup-specific ratings rather than downgrade the overall body. Document the pre-specified subgroup that explained heterogeneity and rate that subgroup separately.

3.4. Two-study comparisons cannot reliably be assessed for inconsistency; note this limitation explicitly and lean on the direction of effect rather than statistical tests.

### 4. Assess directness (population, intervention, comparator, outcome match)

4.1. For each of population, intervention, comparator, and outcome, check whether the included studies match the review question or differ in ways that affect applicability.

4.2. **Population directness** — were the trial participants the population the review aims to inform? An evidence base in younger adults applied to older adults with multimorbidity is indirect.

4.3. **Intervention directness** — was the dosing, route, and duration consistent with how the intervention would be used in the review's target setting?

4.4. **Comparator directness** — was the comparator the alternative the reader will face, or a different one?

4.5. **Outcome directness** — was the measured outcome the one that matters to the reader, or a surrogate? A surrogate that does not reliably translate to the patient-important outcome is indirect; a surrogate with a strong validated relationship to the outcome may be defensible but should be flagged.

4.6. **Indirect comparison** — if the body of evidence is informed by indirect comparisons (e.g., A vs. C and B vs. C, used to infer A vs. B), state this explicitly and consider whether to downgrade.

4.7. Decide: no concerns, serious indirectness (downgrade one), or very serious indirectness (downgrade two).

### 5. Assess precision

5.1. Examine the pooled estimate's confidence interval against the **decision threshold** that would change clinical action. A confidence interval that crosses the threshold of clinical importance is imprecise even if it excludes the null.

5.2. Use the **optimal information size** as a rough check — the number of participants and events the comparison would need to detect a minimally important effect. Bodies of evidence well below the optimal information size are likely imprecise.

5.3. For rare outcomes, a small number of events is the dominant precision concern; with fewer than (typically) 300 events for binary outcomes or 400 participants per arm for continuous outcomes, downgrade for imprecision unless the effect is large and the CI is tight.

5.4. Decide: no concerns, serious imprecision (downgrade one), or very serious imprecision (downgrade two).

### 6. Assess publication and reporting bias

6.1. Use the protocol-specified small-study-effects analysis (funnel plot inspection and statistical test where the number of studies permits) and the team's knowledge of unreported trials.

6.2. Cross-check against trial registries: are there registered trials that did not produce a publication or for which results were not reported? Persistent gaps between registration and publication are signals of selective reporting.

6.3. Decide: undetected (most common in small bodies of evidence), strongly suspected (downgrade one), or detected (downgrade two). When data are too sparse to detect, do not falsely conclude absence; note the limitation explicitly.

### 7. Consider reasons to upgrade

7.1. For non-randomized bodies of evidence, three reasons can justify upgrading: a large effect, a dose-response gradient, and plausible confounders that would reduce a demonstrated effect (making the observed effect a conservative estimate).

7.2. Apply upgrades sparingly and only when each reason is genuinely supported. A large effect for a marginal absolute difference is not the same as a large relative effect for a meaningful absolute difference.

7.3. Document upgrades with at least as much rigor as downgrades.

### 8. Combine into the overall certainty

8.1. Net the downgrades and upgrades. Floor the rating at **very low** and cap at **high**. Possible values are: high, moderate, low, very low.

8.2. Write a one-paragraph **summary statement** per outcome capturing the rating and the dominant reasons.

8.3. State the **implication** of the rating in plain language. The four-level vocabulary maps roughly to: high — further research very unlikely to change the estimate; moderate — further research likely to have an important impact; low — further research very likely to have an important impact and may change the estimate; very low — any estimate is very uncertain.

### 9. Build the summary-of-findings table

9.1. One row per outcome. Columns: outcome and time horizon, anticipated absolute effects (with intervention and with comparator) at the low-risk baseline, anticipated absolute effects at the high-risk baseline, relative effect (with 95% CI), number of participants and studies, certainty rating, and a plain-language comment.

9.2. **Anticipated absolute effects** combine the relative effect from the meta-analysis with assumed baseline risks taken from a credible source named in the table footnote (a representative trial control arm, a registry, or a guideline assumption). Report both as risk per 1,000 (or other natural-frequency unit) and as the difference.

9.3. **Number of participants and studies** comes from the synthesis stage.

9.4. **Comment** is one sentence summarizing the practical meaning: "Probably reduces all-cause mortality by about 30 deaths per 1,000 over one year."

9.5. Format the table to be read in isolation. A reader who sees only the table should be able to act on the result — the table is the public face of the review.

### 10. Validate the assessment against an internal checklist

Before emitting, verify:

- Each outcome has explicit reasoning for each of the five considerations.
- The starting certainty is justified by design type.
- Downgrades cite the specific evidence (risk-of-bias domain, heterogeneity result, threshold-crossing CI, etc.).
- Upgrades, if applied, are documented with at least the same rigor.
- The overall rating is consistent with the per-consideration narrative; surprises are explained.
- The plain-language implication uses the four-level vocabulary correctly.
- The summary-of-findings table has both relative and absolute effects, with sources for the baseline risk.
- No outcome is rated without considering all five domains; "no concerns" is a judgment, not a default.

### 11. Emit the certainty assessment and the summary-of-findings table

The certainty assessment is one section per outcome with sub-headings for each consideration and an overall rating. The summary-of-findings table is a single reader-facing table covering all critical and important outcomes.

### Decision rules and heuristics

- **Per outcome, not per review.** A review almost never has a single certainty rating; it has one per critical and important outcome. Resist the urge to summarize.
- **Downgrade once for a clear reason, not partly for several.** Half-downgrades invite gaming. If a consideration has a real problem, downgrade fully; if not, do not.
- **Two-level downgrades are rare.** Very serious limitations are the exception, not a way to express strong disagreement.
- **Apply considerations independently.** Risk of bias and inconsistency can both be present and both downgrade; one does not preclude the other.
- **Trust the body's leverage.** A single high-leverage study at high risk of bias can drive the body's rating; do not be reassured by many small, low-leverage low-risk studies.
- **Threshold-crossing matters more than null-crossing.** A CI that excludes the null but still crosses the threshold of clinical importance is imprecise; say so.
- **Upgrades for non-randomized evidence rarely reach high.** Most well-conducted upgrades land at moderate.
- **The plain-language sentence is the part the reader keeps.** Write it carefully and check it for honesty.

### Edge cases

- **Body of evidence with only one study.** Inconsistency cannot be assessed. Imprecision and publication bias should be assessed conservatively. State the single-study limitation explicitly.
- **Conflicting pooled estimates from different models.** When fixed-effect and random-effects estimates differ materially, present both and rate based on the random-effects estimate while noting the divergence.
- **Body with a published meta-analysis and new individual trials.** Either re-pool with the new data or rate the existing meta-analysis with a note about new evidence; do not mix without re-analysis.
- **Indirect comparison via network meta-analysis.** Add a consideration for the network assumptions (transitivity, consistency) and assess whether they hold for this outcome.
- **Outcome with no quantitative pool — narrative synthesis only.** Rate using the same five considerations applied to the narrative summary; note that precision and inconsistency must be judged qualitatively, with care.
- **Outcome where one study dominates by sample size.** Examine that study's risk of bias carefully; the body's rating may be effectively the rating of that one study.
- **Sub-group rating differs from overall rating.** Report both, name the pre-specified subgroup, and explain why the subgroup is more credible if so.
- **Mixed direction across critical outcomes.** Present the certainty per outcome and let the recommendation process — not the rating — weigh the trade-offs.

## Outputs

- `certainty_assessment_markdown` — One section per outcome with per-consideration reasoning and an overall rating. Includes the dominant reasons for each downgrade or upgrade.
- `summary_of_findings_table` — Reader-facing single table covering all critical and important outcomes, with relative and absolute effects, certainty rating, and a plain-language comment.
- `open_questions` — Items needing methodology-lead confirmation before the assessment is finalized.

## Examples

### Worked example (abbreviated)

Input:

> Outcome: composite cardiovascular death + HF hospitalization at 12 months.
> Pooled risk ratio: 0.79 (95% CI 0.72-0.87) from 4 RCTs, ~14,000 participants total.
> Heterogeneity: I-squared 18%, all studies on the same side of the null.
> Risk-of-bias judgments per outcome: 3 trials low risk, 1 with some concerns (open-label design,
>   no blinded outcome adjudication).
> Anticipated baseline risks: 100 events/1000/year (low-risk cohort), 200 events/1000/year (high-risk cohort).

Expected certainty assessment (abbreviated):

```
Outcome: composite CV death + HF hospitalization at 12 months

Starting certainty: high (predominantly RCTs)

Risk of bias: 3 of 4 trials low risk; 1 trial with some concerns due to open-label design
  with no blinded adjudication of the composite. The study contributes ~20% weight.
  Sensitivity analysis excluding the study moves the pooled estimate from 0.79 to 0.78 —
  not material. No downgrade.

Inconsistency: I-squared 18%, all point estimates on the same side, CIs overlap heavily.
  No downgrade.

Indirectness: included trials predominantly enrolled adults with LVEF >= 45% in outpatient
  settings; the target population is LVEF >= 50% (HFpEF). The 45-50% sub-band represents
  ~25% of pooled participants. Pre-specified subgroup analysis by LVEF cutoff did not show
  effect modification. No downgrade; flag for the discussion.

Imprecision: ~14,000 participants and ~1,400 events; CI excludes the null and excludes
  a 10% relative reduction (the team's pre-specified decision threshold). No downgrade.

Publication bias: 4 studies — too few for a reliable funnel-plot assessment. No registered
  trials with unreported results identified. Status: undetected; note limitation.

Overall: high certainty.

Plain-language implication: SGLT2 inhibitors probably reduce the composite of CV death
  and HF hospitalization at 12 months compared with placebo in adults with HFpEF without
  diabetes; further research is very unlikely to change this estimate.
```

Expected `summary_of_findings_table` (abbreviated):

```
| Outcome                | Anticipated absolute effects per 1000 over 12 months  | Relative effect    | Participants (studies) | Certainty | Comment                                                |
|------------------------|--------------------------------------------------------|--------------------|------------------------|-----------|--------------------------------------------------------|
|                        | Placebo  | Intervention | Difference                       | (95% CI)           |                        |           |                                                        |
| CV death or HF hosp.   |          |              |                                  | RR 0.79 (0.72-0.87)| ~14,000 (4 RCTs)       | High      | Probably reduces by 21 (low risk) to 42 (high risk) events per 1000 |
|   Low-risk baseline    | 100      | 79           | 21 fewer (13 fewer to 28 fewer)  |                    |                        |           |                                                        |
|   High-risk baseline   | 200      | 158          | 42 fewer (26 fewer to 56 fewer)  |                    |                        |           |                                                        |
| All-cause mortality    | ...      | ...          | ...                              | ...                | ...                    | Moderate  | ...                                                    |
| Serious adverse events | ...      | ...          | ...                              | ...                | ...                    | Moderate  | ...                                                    |
```

`open_questions` example output:

```
- Confirm the pre-specified decision threshold (currently 10% relative reduction) used for
  the imprecision judgment.
- Confirm the source for baseline risks in the table footnote (proposed: trial control arms
  weighted by sample size). The guideline panel may prefer a registry source.
- Confirm whether the 45-49% LVEF sub-band should produce a separate certainty rating for
  the strict HFpEF subgroup.
- Confirm reviewer agreement on the "some concerns" rating for the open-label trial; one
  reviewer initially rated high.
```

## Limitations

- Certainty ratings are judgments. Two qualified reviewers can defensibly reach different ratings on the same body of evidence; the value is in the reasoning, not in mechanical scoring.
- The skill consumes the synthesis output and the risk-of-bias ratings; it does not produce them. Garbage in, downgrade out.
- Plain-language implications use a four-level vocabulary that readers may interpret loosely; pair the rating with the absolute-effect numbers wherever the rating appears.
- The skill does not produce recommendations. A recommendation requires weighing benefits, harms, values, preferences, resource use, equity, and acceptability — separate processes beyond certainty rating.
- The summary-of-findings table uses anticipated absolute effects derived from assumed baseline risks; the table footnote must declare the assumed baseline source so readers can adjust to their own setting.

## Sources reviewed

- https://github.com/prisma-flowdiagram/PRISMA2020
- https://github.com/neurostuff/PyMARE
- https://github.com/neurostuff/NiMARE
- https://github.com/mcguinlu/robvis
- https://github.com/asreview/asreview
- https://www.gradeworkinggroup.org/
- https://training.cochrane.org/handbook
