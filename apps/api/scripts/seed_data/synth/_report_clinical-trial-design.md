# Wave-3 Synthesis Report — Biotech: Clinical Trial Design

**Agent niche:** biotech — clinical trial design (protocol, statistical analysis plan, GCP, sample size)
**Date:** 2026-05-14
**Files produced:** 4 skills (.skills.md) + this report

## Files

- `D:\skillsgit\apps\api\scripts\seed_data\synth\biotech-clinical-protocol-author.skills.md`
- `D:\skillsgit\apps\api\scripts\seed_data\synth\biotech-sample-size-planner.skills.md`
- `D:\skillsgit\apps\api\scripts\seed_data\synth\biotech-statistical-analysis-plan-writer.skills.md`
- `D:\skillsgit\apps\api\scripts\seed_data\synth\biotech-clinical-protocol-amendment-reviewer.skills.md`

## Merge decision

No pre-existing biotech or clinical-trial-design skills in `synth/`. All four were authored fresh; nothing was edited or version-bumped.

## Source-thinness disclosure (mandatory for this niche)

The brief flagged that the clinical-trial-design niche is genuinely sparse on permissively-licensed GitHub content. This was confirmed by searching. The methodology software ecosystem for clinical trial design is dominated by:

- **R packages under GPL-2 / GPL-3 / LGPL-3** — rpact, simtrial, Mediana, trialr, adaptr, bayesCT, pwr, gsDesign-family packages. Excellent technical quality, but copyleft-licensed; **rejected** per the skill's MIT / Apache-2.0 / BSD / ISC / Unlicense-only policy.
- **Methodology guidelines under regulatory-body copyrights** — ICH E6, ICH E8, ICH E9, ICH E9(R1), SPIRIT 2025, CONSORT 2025, EMA scientific guidelines, FDA guidances. Not OSS, but referenced as URL-only public guidance.
- **Sponsor SOPs and CRO SOPs** — proprietary, not OSS at all.
- **EDC platforms** — REDCap is explicitly non-open-source; OpenClinica community edition exists but its current license status varies; LibreClinica is community-developed but mature open-source EDC is not the methodology core for this niche.

The accepted permissive sources therefore lean on the **pharmaverse Apache-2.0 ecosystem** (admiral, sdtm.oak, pharmaversesdtm, xportr) which addresses the *analysis-dataset and TFL-execution* side of clinical trial methodology rather than the protocol-and-SAP-authoring side; plus a few adjacent permissively-licensed repos (BayBE for DoE framing, simIDM for time-to-event illness-death structure, clinical_trial_risk for protocol-risk-scoring inversion to amendment-review framing, unbiased and olspow for narrow methodology cues). This is **disclosed in every skill's "Sources reviewed" section**.

The methodology prose is therefore original synthesis of public regulatory guidance (ICH, EMA, FDA, SPIRIT) and standard biostatistical practice. No copyrighted text is reproduced. The fidelity to the field rests on the regulatory-framework references plus the open-source pharmaverse ecosystem's data-side conventions.

## Sources reviewed (license-verified)

| Repo / Resource | License | Stars | ≥100? | Used for |
|---|---|---|---|---|
| pharmaverse/admiral | Apache-2.0 | ~298 | yes | Analysis-dataset (ADaM) conventions, derived-variable structure |
| pharmaverse/sdtm.oak | Apache-2.0 | ~72 | **sub-threshold** (disclosed) | SDTM transformation; data-management section framing |
| pharmaverse/pharmaversesdtm | Apache-2.0 | ~33 | **sub-threshold** (disclosed) | SDTM test-data structure |
| atorus-research/xportr | MIT | ~52 | **sub-threshold** (disclosed) | CDISC export conventions |
| insightsengineering/simIDM | Apache-2.0 | ~14 | **sub-threshold** (disclosed) | Time-to-event illness-death framing |
| emdgroup/baybe | Apache-2.0 | ~461 | yes | Design-of-experiments adjacent; sensitivity-analysis structure |
| fastdatascience/clinical_trial_risk | MIT | ~12 | **sub-threshold** (disclosed) | Risk-scoring inversion to protocol-author open-questions and amendment-review framing |
| ttscience/unbiased | MIT | ~12 | **sub-threshold** (disclosed) | Randomization-firewall framing |
| b-knight/olspow | MIT | ~3 | **sub-threshold** (disclosed) | OLS-adjusted power analysis; MMRM-versus-t-test mismatch caveat |
| ICH E9 / E9(R1) | Public regulatory guidance | n/a | n/a | Estimand framework, statistical principles |
| EMA scientific guidelines | Public regulatory guidance | n/a | n/a | Estimand addendum, design-family expectations |
| SPIRIT statement | Public methodology guidance | n/a | n/a | Protocol-item structure |

## Rejections (license incompatible)

These appeared in search but were **NOT** used as informing sources due to license incompatibility:

| Repo | License | Reason |
|---|---|---|
| Merck/simtrial | **GPL-3.0** | Copyleft; rejected per niche rules |
| gpaux/Mediana | **GPL-2** | Copyleft; rejected |
| brockk/trialr | **GPL (>=3)** | Copyleft; rejected |
| rpact-com/rpact | **LGPL-3** | Copyleft; rejected |
| thevaachandereng/bayesCT | **GPL-3** | Copyleft; rejected |
| INCEPTdk/adaptr | **GPL-3** | Copyleft; rejected |
| DarrenDahly/Clinical_trial_design_and_analysis | **CC-BY-NC-SA** | NonCommercial + ShareAlike; rejected |
| awconway/spiritR | License unverified | Skipped to keep source set clean |
| karlahemming/Cluster-RCT-Sample-Size-Calculator | License unspecified | Skipped |
| cdisc-org/sdtm-adam-pilot-project | License not specified (terms-of-use restrict) | Skipped for methodology informing |
| copperheadCrotch/BATS | GPL-3 | Rejected |
| TrialPhi/Trialphi-Protocol | URL 404 / not retrievable | Skipped |
| pwr (R package) | GPL (>=3) | Copyleft; rejected (named in brief) |

## Patterns observed across the field

1. **The pharmaverse Apache-2.0 ecosystem is the dominant permissively-licensed footprint** in clinical-trial methodology software. It addresses the analysis-dataset (ADaM) and SDTM-mapping side rather than the protocol/SAP-authoring side. The dominant *authoring-side* tooling lives in proprietary platforms (EAST, nQuery, PASS, ADDPLAN) or copyleft R packages (rpact, simtrial, Mediana, gsDesign). This is a structural feature of the field, not a temporary gap.

2. **The estimand framework (ICH E9(R1)) is now the methodology backbone.** Every protocol-authoring or SAP-authoring methodology references it. The five-attribute decomposition (population, treatment, variable, intercurrent-event strategy, summary) is the single most leverage-rich pre-specification choice in modern clinical-trial methodology. Each of the four skills here pivots on it.

3. **SPIRIT, ICH E6, and ICH E9 form the regulatory-protocol triangle.** SPIRIT governs structure of the protocol document; ICH E6 (GCP) governs conduct; ICH E9 governs statistical principles. The three are mostly compatible but emphasize different sections. SPIRIT 2025 added emphasis on open science, patient involvement, and harms description.

4. **Group-sequential and adaptive design has matured into regulatory-mainstream methodology.** Alpha-spending functions (O'Brien-Fleming, Pocock, Hwang-Shih-DeCani) and beta-spending for futility are now expected, not exotic. Sample-size re-estimation (blinded or unblinded) is regulator-accepted under pre-specified conditions. Master-protocol designs (basket, umbrella, platform) are still specialist territory.

5. **The trial-integrity-amendment risk axis is tightly coupled to (a) timing and (b) blinding.** An amendment that would be routine pre-enrollment becomes high-risk post-50% enrollment becomes potentially-disqualifying post-database-lock. Sponsor unblinding amplifies risk along every category. The amendment-reviewer skill makes this axis its primary lens.

6. **Missing-data methodology is the most-likely point of regulator-sponsor disagreement** after the effect-size assumption. Treatment-policy, hypothetical, composite, while-on-treatment, and principal-stratum strategies under E9(R1) all have legitimate use-cases; the choice has substantive analytic implications. Sensitivity analyses (tipping-point, control-based imputation) are now expected for any missing-data-sensitive primary analysis.

7. **CDISC SDTM/ADaM is now globally expected.** FDA and PMDA require it for submission; EMA expects it; many other regulators are moving that direction. The protocol-author and SAP-writer skills point at the data-management section as a place to bake in SDTM/ADaM alignment from the start.

## Disclaimers

Every skill body opens with the mandatory disclaimer in `## When to use`:

> "This skill produces methodology guidance, not regulatory advice or final clinical-trial documents. Every output must be reviewed by qualified clinical-research staff, biostatisticians, and regulatory counsel. No skill output may be submitted to a regulator or used to enroll a patient without sponsor sign-off."

The SAP-writer skill additionally emphasizes that the SAP must be **locked before unblinding** and signed by a qualified biostatistician. The sample-size planner skill emphasizes **validation against qualified software** (nQuery / PASS / EAST / rpact / similar) for any confirmatory trial. The protocol-amendment-reviewer skill emphasizes **regulator pre-discussion** for high-risk amendments and notes that the skill cannot independently verify data-independence claims.

## Frontmatter posture

- `category: biotech` on all four
- First tag `niche:clinical-trial-design` on all four
- 4–7 additional tags per skill
- `license_type: free`; only `currency: USD` and `support_included: false` set; no pricing populated
- No trademarks in names or descriptions (avoided product names such as REDCap, EAST, nQuery, PASS in trademark contexts; referred to only as exemplars of the tool category in the body where validation is recommended)
- All bodies fall within the 300–700-line target band

## Confidence

- **High** confidence: file structure, frontmatter validity, methodology fidelity to public regulatory practice (ICH E9, SPIRIT, GCP), license cleanliness of cited sources.
- **High** confidence: the estimand framework treatment in the SAP-writer skill, the four-axis amendment-impact treatment in the amendment-reviewer skill, the dropout-and-sensitivity treatment in the sample-size planner skill.
- **Medium** confidence: protocol-author skeleton's coverage of indication-specific endpoint conventions — the skill abstracts these intentionally (oncology, T2D, RA, depression, MS endpoints differ widely) and flags therapeutic-area expert review as essential.
- **Medium** confidence: sample-size formulas in the sample-size planner skill are textbook-canonical, but the closed-form expressions cannot substitute for qualified-software validation; the skill explicitly recommends validation in every output.
- **Lower** confidence: the source-thinness situation means more of the methodology rests on regulatory guidance (URL references) and original synthesis than is typical for other niches. The pharmaverse ecosystem provides analysis-dataset conventions but not protocol-or-SAP authoring conventions, so the protocol- and SAP-authoring skills synthesize from public regulatory frameworks more heavily than from OSS code. This is disclosed in every skill.

## Follow-ups (suggested for future waves)

1. **Master-protocol design skill** — basket / umbrella / platform trials, master-protocol-specific statistical analysis (Bayesian hierarchical, common-control comparators), Bayesian decision-rule pre-specification. Would complement the four skills here.
2. **Data Monitoring Committee charter author** — DMC composition, charter content, meeting cadence, decision rules, unblinding firewall, sponsor-DMC interaction conventions. Strong fit for the same niche.
3. **Clinical study report (CSR) drafter** — ICH E3-aligned CSR scaffold; companion to the SAP-writer skill that converts SAP-produced TFLs into a regulatory-grade CSR draft.
4. **Investigator's Brochure summarizer / risk-benefit reviewer** — IB summary and risk-benefit assessment scaffold; useful for protocol authoring and amendment review.
5. **Pharmacovigilance / safety signal review skill** — periodic safety report (DSUR / PSUR) scaffolding, signal detection, expedited reporting; adjacent but distinct from this wave's focus.
6. **Pediatric Investigation Plan (PIP) drafter** — EU regulation requires PIPs for most NDAs; structurally separate from the adult protocol. Would round out a biotech regulatory-pathway skill series.
7. Consider validation: run the 4 new files through `apps/api/src/skills/validator.py` before the integration pass; confirm all frontmatter fields parse cleanly and all required body sections (`## When to use`, `## How to apply`) are present.
