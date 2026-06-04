---
id: skillsgit-curated/biotech-sample-size-planner
version: 1.0.0
name: Clinical Trial Sample Size Planner
description: Compute sample size for common clinical-trial designs — two-arm RCT, non-inferiority, group-sequential, adaptive — with documented assumptions, sensitivity ranges, dropout adjustment, and missing-data buffer.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: biotech
tags: [niche:clinical-trial-design, sample-size, power-analysis, non-inferiority, group-sequential, adaptive, rct, biostatistics]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: [code_execution, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 12000
trigger_keywords:
  - sample size calculation
  - power analysis clinical trial
  - non-inferiority sample size
  - group sequential sample size
  - adaptive trial sample size
  - rct sample size
  - sample size with dropout
  - cluster randomized sample size
  - sample size sensitivity
  - sample size justification
example_invocations:
  - "Compute sample size for a two-arm parallel RCT with a continuous primary endpoint and dropout."
  - "Plan a non-inferiority sample size with a hazard-ratio margin and 1:1 allocation."
  - "What sample size do I need for a group-sequential design with one interim analysis using O'Brien-Fleming?"
inputs:
  - name: endpoint_type
    type: choice
    required: true
    description: The statistical type of the primary endpoint. The methodology branches sharply by type.
    choices: [continuous, binary, time_to_event, count, ordinal, repeated_measures_continuous]
  - name: design_family
    type: choice
    required: true
    description: The high-level design. The skill computes per-arm and total sample sizes for each.
    choices: [superiority_two_arm_parallel, non_inferiority_two_arm, equivalence_two_arm, superiority_multi_arm, group_sequential, sample_size_re_estimation_adaptive, crossover_two_period, cluster_randomized_parallel, stepped_wedge, single_arm_against_historical, dose_response]
  - name: effect_assumptions
    type: json
    required: true
    description: Numeric assumptions specific to the endpoint type. For continuous- minimum clinically important difference (delta) and standard deviation. For binary- control rate and treatment rate (or relative risk / odds ratio). For time-to-event- hazard ratio or median survival, accrual period, follow-up period, dropout per unit time. For non-inferiority- the margin.
  - name: alpha
    type: number
    required: false
    description: Type I error rate (one-sided or two-sided as specified). Default 0.05 two-sided. For non-inferiority, the convention is one-sided 0.025.
  - name: power
    type: number
    required: false
    description: Target statistical power (1 - type II error). Default 0.80. For confirmatory Phase 3 trials, 0.90 is often used.
  - name: allocation_ratio
    type: text
    required: false
    description: Treatment-to-control allocation ratio (e.g. "1:1", "2:1", "3:1"). Default 1:1.
  - name: dropout_rate
    type: number
    required: false
    description: Fraction expected to drop out before the primary endpoint is measured (0 to 1). Default 0.10 unless specified.
  - name: intracluster_correlation
    type: number
    required: false
    description: For cluster-randomized designs, the intracluster correlation coefficient (ICC). Drives the design-effect inflation.
  - name: cluster_size
    type: number
    required: false
    description: Average number of participants per cluster (for cluster-randomized designs).
  - name: interim_analyses
    type: json
    required: false
    description: For group-sequential and adaptive designs- number, timing (information fractions), alpha-spending function (OBrien-Fleming, Pocock, Hwang-Shih-DeCani), beta-spending function, and futility boundary type.
outputs:
  - name: sample_size_report
    type: markdown
    description: A structured report with the computed sample size per arm and total, the formula used, assumptions table, a sensitivity-analysis table varying each assumption, dropout adjustment, and explicit caveats.
  - name: sample_size_json
    type: json
    description: Machine-readable fields including per_arm_evaluable, per_arm_enrolled, total_evaluable, total_enrolled, formula_id, assumptions, sensitivity, dropout_adjustment, missing_data_buffer, design_effect (if applicable), confidence, recommended_validation_path.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Clinical Trial Sample Size Planner

## When to use

**This skill produces methodology guidance, not regulatory advice or final clinical-trial documents. Every output must be reviewed by qualified clinical-research staff, biostatisticians, and regulatory counsel. No skill output may be submitted to a regulator or used to enroll a patient without sponsor sign-off.**

Sample-size planning is the operation that turns a clinical question and a set of assumptions into a number — how many people must be enrolled. The number cascades into budget, timeline, site count, monitoring plan, regulatory commitments, and ethics-committee review. A trial under-powered by 30% may be unable to detect a real effect; a trial over-enrolled by 30% wastes patient exposure and money. The arithmetic is straightforward; the *assumptions* are where the entire planning exercise lives, and the assumptions are where most disagreements with regulators and methodology reviewers happen.

Use this skill when a protocol author or biostatistician has:

- A primary endpoint defined to the level of an estimand (variable, timepoint, intercurrent-event strategy).
- A target effect size and a variability assumption that the sponsor team is willing to defend.
- A design family (parallel, non-inferiority, group-sequential, adaptive, cluster, crossover).
- A desired type I error rate and power.

Typical entry points: a protocol team finalizing the statistical considerations section; a sponsor team building a regulatory briefing-book sample-size justification; a grant writer responding to an NIH or equivalent reviewer's "how did you arrive at N" question; a biostatistician needing a structured sensitivity-analysis table for an investigator advisory board.

Do **not** use this skill as the sole basis for the sample size that ends up in a regulatory protocol. The output is a structured, opinionated computation aligned with the textbook formulas and the regulatory norms. A qualified biostatistician must validate the computation using qualified software (e.g., the sponsor's validated nQuery, PASS, EAST, ADDPLAN, or a validated R simulation), confirm the assumptions against the investigator's brochure and the literature, and sign off on the regulatory submission. The skill flags the path to validation explicitly in every output.

Out of scope: complex master-protocol sample sizing (basket / umbrella / platform) that requires simulation-based operating-characteristic studies; sample sizing under model-averaging or Bayesian decision-theoretic frameworks that need bespoke priors; sample sizing for rare-disease trials where the effective population caps the achievable N (these need feasibility analysis, not power analysis); diagnostic-accuracy studies (different formulas — sensitivity/specificity and ROC AUC); equivalence trials of bioequivalence for generic approval (use the 80/125 bioequivalence rules and the right software).

## How to apply

Treat sample-size planning as a four-stage operation: (1) state the estimand and assumption set explicitly; (2) compute the base sample size using the appropriate formula or simulation; (3) inflate for dropout and design-effect considerations; (4) build a sensitivity table that varies each assumption and shows how robust the plan is. Refuse to return a single number without the surrounding assumption documentation — a sample size without assumptions is a hazard.

1. **Confirm the endpoint type and estimand framing.** Continuous endpoints (e.g., HbA1c change, FEV1, MADRS score) use mean-difference formulas. Binary endpoints (e.g., response rate, mortality at fixed time) use proportion-difference, relative-risk, or odds-ratio formulas. Time-to-event endpoints (e.g., progression-free survival, time-to-discontinuation) use hazard-ratio formulas based on event counts and require accrual and follow-up assumptions to translate events into participants. Count endpoints use Poisson or negative-binomial formulas with overdispersion. Ordinal endpoints often use proportional-odds rank-based methods or, more commonly, are dichotomized into responders versus non-responders at the cost of efficiency. Repeated-measures continuous endpoints can use mixed-model-for-repeated-measures (MMRM) assumptions with correlation structure or be reduced to a single-timepoint analysis. Match the formula to the actual analysis specified in the SAP — mismatch between sample-size formula and analysis method is a common reviewer finding.

2. **State alpha, power, and sided-ness.** The defaults are 0.05 two-sided alpha and 0.80 power. Confirmatory Phase 3 trials often use 0.90 power. Non-inferiority and equivalence trials conventionally use one-sided alpha 0.025. Multi-primary-endpoint trials need a multiplicity-adjusted alpha (Bonferroni, Hochberg, hierarchical, gatekeeping, or a graphical procedure). Trials with one interim analysis use an alpha-spending function (O'Brien-Fleming, Pocock, Hwang-Shih-DeCani) that fractionally allocates the alpha across the interim and final looks. State the sided-ness explicitly — one-sided versus two-sided is a frequent source of confusion in protocol reviews.

3. **Compute the base sample size for the chosen design.**

   **Two-arm parallel superiority, continuous endpoint.** The textbook expression for per-arm sample size is approximately `n_per_arm = 2 * (z_{1-α/2} + z_{1-β})^2 * σ^2 / δ^2` where δ is the minimum clinically important difference, σ is the within-arm standard deviation, and z denotes the standard-normal quantile. Adjust for allocation ratio by computing `n_total = (1 + k) * n_per_arm` and re-deriving the per-arm n where k is the allocation ratio.

   **Two-arm parallel superiority, binary endpoint.** Use the normal-approximation difference-of-proportions formula or the exact Fisher's-exact-based approach for small expected counts. For relative-risk or odds-ratio targeting, transform the control rate and effect into a target treatment rate and apply the difference formula. Distinguish per-arm sample size based on the expected event rate from per-arm sample size based on absolute counts.

   **Two-arm parallel superiority, time-to-event endpoint.** Use Schoenfeld's formula: required event count `E ≈ (z_{1-α/2} + z_{1-β})^2 / (p_1 * p_2 * (ln HR)^2)` where HR is the hazard ratio and p_1, p_2 are the allocation proportions. Then translate events into participants given the accrual period, accrual pattern, follow-up period, and dropout-per-unit-time. State the accrual model (uniform, ramp-up, calendar-time-driven) and the censoring model explicitly. Time-to-event sample sizing is event-count driven, not participant-count driven — the protocol-level sample size is the participant count required to *produce* the events within the trial timeline.

   **Non-inferiority and equivalence.** The non-inferiority margin Δ is the maximum tolerable inferior performance — a value the sponsor and regulators have agreed upon based on historical effect of the active comparator. The formula structure mirrors superiority but with the alternative hypothesis at the boundary of equivalence rather than at the assumed effect; the test is one-sided. Sample size is typically larger than the corresponding superiority study, especially when the assumed true effect is at-or-near the margin. Equivalence trials are two-one-sided-tests (TOST); sample size is typically 1.5–2× the superiority equivalent.

   **Multi-arm superiority.** A k-arm trial with a control arm uses pairwise sample-size computation per active-versus-control pair, with multiplicity adjustment if more than one comparison is in the primary family. The Dunnett procedure is common for comparing multiple actives to one control; the critical value is smaller than the Bonferroni-corrected value because Dunnett accounts for correlation. Dose-response trials may use trend tests (Williams, Cochran-Armitage), MCP-Mod, or the proportional-hazards equivalent — each has its own sample-size formula and operating characteristics.

   **Group-sequential.** A trial with one or more interim analyses uses an alpha-spending function to allocate the type-I error across looks. O'Brien-Fleming spends very little alpha early and most at the final analysis, which means the maximum sample size is similar to the fixed-design sample size but the trial may stop early for overwhelming efficacy. Pocock spends alpha more evenly, with a smaller maximum sample size but a larger expected sample size. Hwang-Shih-DeCani is a flexible family parameterized between the two. The reported sample size for a group-sequential design should include: maximum sample size (under the null), expected sample size under the alternative, expected sample size under the null, and the boundaries at each look. Beta-spending (for futility) further reduces expected sample size under the null at the cost of a small power penalty.

   **Sample-size re-estimation adaptive.** A blinded or unblinded SSR design plans an initial sample size based on prudent assumptions; at a pre-specified information fraction, the assumption (typically the nuisance parameter — variance for continuous, control rate for binary) is re-estimated and the final sample size is adjusted within pre-specified bounds. Blinded SSR (re-estimating the variance using pooled data) is widely regulatory-accepted and requires minimal alpha adjustment. Unblinded SSR (re-estimating the effect size) is more controversial and typically requires a combination-test or conditional-power approach with careful adjustment.

   **Cluster-randomized parallel.** Sample size is the corresponding individual-randomized sample size inflated by the design effect `DE = 1 + (m - 1) * ICC` where m is the average cluster size and ICC is the intracluster correlation. Stepped-wedge designs use a different design-effect formula incorporating the number of steps; consult a stepped-wedge specialist resource. Cluster-randomized trials typically also need a larger number of clusters rather than larger clusters — a small number of large clusters has poor effective sample size.

   **Crossover.** For a two-period crossover continuous endpoint, sample size uses the within-subject standard deviation of the period-difference and is typically much smaller than a parallel design — but the crossover assumption (no carryover, no period-treatment interaction) must hold. Carryover-adjusted designs need a washout period and possibly additional sample size.

   **Single-arm against a historical control.** Use a one-sample test against a fixed null value, with sample size driven by the difference between the assumed treatment response and the historical control. State the historical control source and acknowledge the substantial bias risk; consider performing a Bayesian dynamic borrowing analysis if a contemporary control is available but small.

4. **Adjust for dropout.** The base sample size is the *evaluable* sample size — the number of participants who contribute a primary-endpoint observation. To enroll, divide by `(1 − dropout_rate)`. A 10% dropout assumption with a base evaluable n of 200 per arm requires enrolling approximately 222 per arm. For time-to-event endpoints, dropout is modeled as censoring and incorporated into the event-count computation; an additional buffer for non-administrative dropout may still be prudent. State the dropout assumption explicitly with citation to comparable trials and the operational mitigations planned to reduce dropout.

5. **Adjust for missing data.** Even with no overt dropout, missing data accumulates at every visit. Modern analytic approaches (mixed-model-for-repeated-measures, multiple imputation, control-based imputation) handle missing data under their assumptions, but the assumption-set must be stated in advance. If the SAP specifies a treatment-policy estimand under which post-discontinuation observations are still collected and analyzed, missing-data inflation is smaller than under a hypothetical estimand where post-discontinuation observations are missing-by-design. The sample-size plan should state the missing-data analytic strategy and any further buffer (typically a small additional inflation if the estimand-and-analysis choice does not eliminate missing-data inflation).

6. **Build a sensitivity table.** For each assumption (effect size, variance, control rate, hazard ratio, dropout, allocation ratio, accrual period, follow-up period), vary the assumption across a plausible range and report the resulting sample size. The table reveals which assumptions the plan is most sensitive to. For typical RCTs, the sample size is most sensitive to the effect-size assumption and the variance/control-rate assumption; less sensitive to alpha/power and to allocation ratio. A sample-size plan that produces wildly different N values across plausible assumption ranges is a planning risk, not a planning answer.

7. **Confirm the formula matches the planned analysis.** A sample size computed under a t-test formula but analyzed with MMRM, or computed under a normal-approximation formula but analyzed with Fisher's exact, has a mismatch that can move power by a few percentage points. For confirmatory trials, simulation-based sample sizing using the exact planned analysis is the highest-fidelity approach; closed-form computation is the planning-stage approximation that simulation confirms. The output should name the formula (or simulation procedure) and recommend a simulation validation pass for confirmatory studies.

8. **Document feasibility considerations.** The computed sample size meets the statistical objective; whether it can be achieved within the planned timeline is a separate question. Feasibility variables include: estimated eligible-population size in the target geographies, expected screen-fail rate, expected enrollment rate per site per month, planned site count, and competing trials. The skill flags these without computing them; the operations team owns the feasibility analysis.

9. **Address regulatory expectations.** For an FDA or EMA confirmatory submission, the sample size and its justification will be reviewed against the statistical-analysis-plan-equivalent in the protocol. Expect challenges on: the effect-size assumption (regulators may push for a smaller assumed effect); the variance assumption (regulators may push for a larger assumed variance); the multiplicity-adjusted alpha for multi-arm or multi-endpoint trials; the interim-analysis structure for group-sequential designs; and the appropriateness of the chosen formula for the planned analysis. Build the rationale to survive each.

10. **State validation requirements.** Every computed sample size in the report should be accompanied by a recommended validation path: "validate using [tool] under [version]; confirm with simulation if [condition applies]." This is not optional — for confirmatory trials, qualified-software validation is the regulatory expectation.

11. **Self-check before returning.** Confirm: the formula matches the endpoint type and design family; alpha, power, and sided-ness are explicit; the effect-size assumption is identified as a sponsor decision when not already validated against the IB or prior trials; dropout inflation is applied; sensitivity table is non-trivial; the recommendation to validate using qualified software is explicit.

## Inputs

- `endpoint_type` (required) — continuous, binary, time-to-event, count, ordinal, repeated-measures.
- `design_family` (required) — superiority parallel, non-inferiority, group-sequential, adaptive, cluster, crossover, etc.
- `effect_assumptions` (required, JSON) — numeric assumptions for the chosen endpoint and design.
- `alpha` (optional, default 0.05 two-sided) — type I error rate.
- `power` (optional, default 0.80) — target power.
- `allocation_ratio` (optional, default 1:1) — treatment-to-control ratio.
- `dropout_rate` (optional, default 0.10) — expected dropout before primary endpoint.
- `intracluster_correlation`, `cluster_size` (optional) — for cluster designs.
- `interim_analyses` (optional, JSON) — for group-sequential and adaptive designs.

## Outputs

- `sample_size_report` (markdown) — computed n per arm and total, formula identifier, assumption table, sensitivity table varying each assumption, dropout adjustment, missing-data buffer, design-effect application (if applicable), and an explicit recommendation to validate using qualified software.
- `sample_size_json` (JSON) — per_arm_evaluable, per_arm_enrolled, total_evaluable, total_enrolled, formula_id, assumptions, sensitivity, dropout_adjustment, missing_data_buffer, design_effect, confidence, recommended_validation_path.

## Examples

### Example 1 — Two-arm superiority, continuous endpoint

**Inputs:**
- `endpoint_type`: continuous
- `design_family`: superiority_two_arm_parallel
- `effect_assumptions`: `{"delta": 0.5, "sd": 1.5, "endpoint_unit": "HbA1c percent change"}`
- `alpha`: 0.05 (two-sided)
- `power`: 0.80
- `allocation_ratio`: 1:1
- `dropout_rate`: 0.15

**Output sample_size_report (excerpt):**

> **Formula:** two-sample t-test approximation for continuous endpoint, equal variance.
>
> **Computation.** `n_per_arm = 2 * (z_{0.975} + z_{0.80})^2 * σ^2 / δ^2 = 2 * (1.96 + 0.84)^2 * 1.5^2 / 0.5^2 ≈ 142` evaluable per arm.
>
> **Dropout adjustment.** 15% expected dropout → enroll `142 / (1 − 0.15) ≈ 168` per arm. **Total enrolled ≈ 336.**
>
> **Sensitivity table (per-arm evaluable):**
>
> | δ | σ=1.2 | σ=1.5 | σ=1.8 |
> |---|---|---|---|
> | 0.3 | 252 | 393 | 565 |
> | 0.5 | 91  | 142  | 204  |
> | 0.7 | 47  | 73   | 105  |
>
> **Caveats.** The base formula assumes a t-test analysis. If the planned analysis is MMRM with covariate adjustment, the effective sample size is higher than the t-test n at the same power; consider re-deriving under MMRM. The variance assumption is critical: a variance 20% higher than assumed inflates n by ~44%. Confirm σ against IB and prior-trial data.
>
> **Validation recommendation.** Validate using sponsor-qualified nQuery, PASS, EAST, or a validated R simulation; required before protocol finalization for a confirmatory trial.

### Example 2 — Time-to-event, hazard ratio, group-sequential

**Inputs:**
- `endpoint_type`: time_to_event
- `design_family`: group_sequential
- `effect_assumptions`: `{"hr": 0.75, "median_control_months": 12, "accrual_months": 24, "followup_months": 18, "annual_dropout": 0.05}`
- `alpha`: 0.05 two-sided
- `power`: 0.90
- `allocation_ratio`: 1:1
- `interim_analyses`: `{"count": 1, "info_fraction": 0.6, "alpha_spending": "OBrien-Fleming", "futility": "non-binding_HSD_gamma_-2"}`

**Output (excerpt):**
> **Event count required (fixed design equivalent):** approximately 508 events for HR=0.75 at α=0.05 two-sided, 90% power.
>
> **Group-sequential adjustment.** One interim at 60% information using OBrien-Fleming alpha-spending (critical Z ≈ 2.67 at interim, ≈ 1.99 at final). Maximum event count under stopping ≈ 514. Expected event count under the alternative ≈ 460 (10% reduction). Non-binding futility (HSD γ=−2) further reduces expected event count under the null with negligible power penalty (<1%).
>
> **Participant translation.** Given 12-month median control survival (exponential approximation, λ ≈ 0.0577 monthly hazard), 24-month accrual, 18-month minimum follow-up, 5% annual dropout, approximately 720 participants randomized 1:1 are required to produce the maximum event count within the trial timeline. **Total enrolled ≈ 720.**
>
> **Caveats.** Exponential survival is an approximation; if proportional hazards is plausible but the survival distribution is Weibull or piecewise, simulate. Schoenfeld's formula assumes a single fixed effect across follow-up; for non-proportional hazards (delayed effect, crossing hazards), it can be biased — flag and simulate.
>
> **Validation recommendation.** Validate using EAST or rpact (or a sponsor-qualified equivalent) with the specified spending function and futility boundary. Simulate under non-proportional-hazard scenarios if biologically plausible.

## Limitations

- **Methodology, not validation.** The skill is not qualified software. Regulatory submissions require sample-size validation using sponsor-qualified tools.
- **Assumptions are sponsor decisions.** The skill computes correctly under the assumptions provided but does not validate those assumptions against the investigator's brochure or the literature.
- **Closed-form versus simulation.** The skill leans on closed-form formulas with simulation recommendations for complex cases. Truly bespoke designs (master protocols, biomarker-adaptive enrichment, response-adaptive randomization, hierarchical multi-endpoint gatekeeping with correlated tests) require purpose-built simulations that the skill cannot substitute for.
- **Non-proportional-hazards** time-to-event scenarios (crossing hazards, delayed effect, cured fraction) are flagged but not solved; consult a survival-analysis specialist.
- **Bayesian designs.** The skill is frequentist by default. Bayesian designs with predictive-probability-of-success or expected-utility metrics need Bayesian sample-size machinery that the skill flags but does not implement.
- **Cluster designs** require a credible ICC; the skill uses provided ICC at face value. Underestimated ICC is a common cause of under-powered cluster trials.
- **Stepped-wedge** sample sizing is complex; the skill provides a high-level scaffold but recommends specialist software.
- **Rare-disease and pediatric trials** often hit feasibility ceilings before statistical ceilings. The skill flags but does not resolve the feasibility-versus-power trade-off.
- **No regulatory negotiation.** Sample-size negotiations with regulators are a separate exercise. The skill produces a defensible starting point; the regulatory affairs team owns the negotiation.

## Sources reviewed

The methodology synthesized here is informed by reviewing permissively-licensed open-source sample-size and trial-simulation repositories on GitHub, augmented by reference to public regulatory and methodology guidance. **Source-thinness disclosure:** the dominant clinical-trial sample-size R packages — rpact (LGPL-3), simtrial (GPL-3), Mediana (GPL-2), trialr (GPL ≥ 3), adaptr (GPL-3), bayesCT (GPL-3), pwr (GPL ≥ 3) — are under copyleft licenses that this skill rejects per its MIT/Apache/BSD/ISC/Unlicense-only policy, so they were not used as informing sources. The accepted sources cover the analysis-dataset side (pharmaverse) and adjacent design-of-experiments tooling (BayBE); methodology guidance is supplemented by public ICH and EMA references. Sub-threshold (< 100 stars) repos are disclosed.

- https://github.com/pharmaverse/admiral (Apache-2.0, ~298 stars)
- https://github.com/emdgroup/baybe (Apache-2.0, ~461 stars; design-of-experiments adjacent; used for methodology framing on sensitivity-analysis structure)
- https://github.com/insightsengineering/simIDM (Apache-2.0, ~14 stars; sub-threshold; informs the time-to-event illness-death framing in survival sample sizing)
- https://github.com/b-knight/olspow (MIT, ~3 stars; sub-threshold; OLS-adjusted power analysis under covariate adjustment; informs the MMRM-versus-t-test mismatch caveat)
- https://github.com/pharmaverse/sdtm.oak (Apache-2.0, ~72 stars; sub-threshold; informs the analysis-dataset-aware sample-size framing)
- https://database.ich.org/sites/default/files/E9_Guideline.pdf (ICH E9 — Statistical Principles)
- https://www.ema.europa.eu/en/ich-e9-statistical-principles-clinical-trials-scientific-guideline (EMA E9 and E9(R1) addendum guidance)
- https://www.fda.gov/regulatory-information/search-fda-guidance-documents (FDA guidance index for endpoint and design-family expectations)
