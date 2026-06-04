---
id: skillsgit-curated/clinical-evidence-narrative
version: 1.0.0
name: Clinical Evidence Section Narrative Drafter
description: Draft the clinical-evidence narrative for a regulatory submission — study design fit, endpoint relevance, statistical power, and gap analysis against the label or indications claim.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: biotech
tags: [niche:regulatory-submission, clinical-evidence, ich-e9, ind, 510k, ectd, endpoints, statistical-power]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  tools_optional: [web_search, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - clinical evidence section
  - clinical study report
  - endpoint adequacy
  - statistical power
  - clinical evidence narrative
  - module 5 clinical
  - clinical study summary
  - pivotal trial fit
  - label support
  - clinical evidence gap analysis
  - spirit checklist
  - efficacy narrative
example_invocations:
  - "Draft the clinical-evidence narrative for our Module 2.5 Clinical Overview supporting the proposed indication."
  - "Assess whether our Phase 3 endpoint suite supports the label claim and flag any gaps."
  - "Write the clinical-evidence section for the 510(k) based on this pivotal study summary."
inputs:
  - name: proposed_label_or_indication
    type: text
    required: true
    description: The exact proposed indication-for-use language or proposed label claim that the clinical evidence is meant to support. The agent will work backward from this to assess fit.
  - name: study_descriptions
    type: text
    required: true
    description: Description of the clinical studies in the program — design (RCT, single-arm, registry, prospective cohort), population (inclusion/exclusion summary), comparator if any, sample size, primary endpoint, key secondary endpoints, follow-up duration, results summary with effect sizes and confidence intervals where available.
  - name: submission_type
    type: choice
    required: true
    description: Which submission this evidence supports. Drives section structure and expectations.
    choices: [510k, de_novo, pma, ind, nda, bla, ce_marking, other]
  - name: regulatory_region
    type: choice
    required: false
    description: Primary regulator. FDA and EMA have different conventions on clinical evidence narrative structure.
    choices: [fda, ema, health_canada, pmda, nmpa, mhra, tga, global, unknown]
  - name: known_evidence_gaps
    type: text
    required: false
    description: Gaps the sponsor already recognizes (e.g., "no head-to-head against standard of care," "pediatric subgroup small"). Helps the agent prioritize gap-bridging in the draft.
outputs:
  - name: evidence_narrative
    type: markdown
    description: Structured clinical-evidence narrative draft with sections for study design adequacy, endpoint relevance, statistical power and effect-size interpretation, subgroup and sensitivity analyses, safety summary, and an explicit gap-analysis-vs-claim section.
  - name: evidence_json
    type: json
    description: Machine-readable structure — design_adequacy (object), endpoint_relevance (array of {endpoint, claim_supported, rationale}), power_assessment (object), gaps_vs_claim (array of {gap, severity, mitigation}), label_supportability (full_support | partial_support | unsupported), confidence (float).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Clinical Evidence Section Narrative Drafter

## When to use

**Mandatory disclaimer.** This skill produces methodology guidance only. Outputs are not regulatory submissions. Real submissions must be authored, reviewed, and signed by qualified regulatory affairs staff and may require external counsel. No output may be filed with any regulator without sponsor authorization.

Invoke this skill when a sponsor needs to translate a clinical study program — one trial or several — into the clinical-evidence narrative that anchors a regulatory submission. Typical entry points: a medical writer drafting the Clinical Overview (Module 2.5) of an NDA or BLA; a regulatory affairs lead drafting the clinical-evidence section of a 510(k); a clinical lead assessing whether the pivotal study endpoints actually support the proposed label; a biostatistician reviewing whether the achieved power and effect size let the program claim what marketing wants to claim; a consultant preparing a clinical-evidence briefing for a Type B meeting with FDA.

Do not use this skill for:

- **De novo statistical analysis.** This is a narrative-drafting skill, not a biostatistical analysis tool. It works from study results the sponsor provides; it does not re-analyze raw data, recalculate p-values, or perform meta-analyses on study-level summaries.
- **Protocol drafting.** Writing or critiquing a study protocol prospectively is a different skill (SPIRIT-checklist-driven). This skill operates after studies are complete, when the question is "does what we have support what we want to claim."
- **Regulatory adjudication.** Whether a particular endpoint is "acceptable" to a regulator is a regulator-specific, sponsor-specific judgment. The skill flags risks but does not pre-adjudicate.

The skill is appropriate for an honest gap analysis as much as a flattering write-up. A clinical-evidence section that overpromises is more damaging than one that scopes claims carefully — overpromising invites deficiency letters, label restrictions, and post-approval commitments. The methodology defaults to the most conservative supportable claim, then explicitly surfaces what additional evidence would let the sponsor expand the claim.

## How to apply

The methodology rests on one structural insight: the clinical-evidence narrative is not a chronological account of what the sponsor did. It is an argument that *this evidence* supports *this claim* on *this population* with *this confidence*. Every section of the narrative has to be traceable to the proposed label or indications language. Anything else is a study report, not a regulatory narrative.

1. **Anchor on the proposed claim before describing the studies.** Reverse the temptation to "describe the data and let it speak." Pin the proposed indication or label claim at the top of the narrative, in regulator-grade language. Every subsequent section should be readable as evidence for or against this specific claim. If the proposed claim has not been finalized, surface that as the highest-priority input gap and produce a provisional narrative tagged with the assumed claim.

2. **Frame study-design adequacy against the claim, not in the abstract.** A randomized double-blind placebo-controlled trial is the gold standard for many claims and overkill for others; a single-arm trial against a historical control may be entirely appropriate for a rare-disease claim or for a 510(k) where bench data does most of the work. For each pivotal study, ask:
   - **Design class** — is the design appropriate for the type of claim? (RCT for efficacy claims involving a comparator; single-arm against a robust historical control for rare disease or where equipoise is absent; observational/registry for rare-event safety claims; pragmatic trial for real-world-effectiveness claims.)
   - **Comparator choice** — is the comparator the right one for the claim? "Better than placebo" supports a different label than "non-inferior to standard of care." A trial against an inappropriately easy comparator does not support a competitive label.
   - **Population fit** — does the enrolled population match the proposed indicated population? Population narrower than the claim is fixable by narrowing the claim; population broader than the claim is unusually rare; population *mismatched* (e.g., trial enrolled mild-to-moderate disease, label claims all severities) is a defect that the narrative must address explicitly.
   - **Blinding and bias controls** — adequate randomization, allocation concealment, blinding of patients/clinicians/outcome assessors as appropriate, intention-to-treat principle for the primary analysis.

3. **Audit endpoint relevance against the claim.** An endpoint is "fit-for-claim" only if (a) it measures what the claim says it measures, (b) it has a clinically meaningful threshold for the effect size, and (c) the regulator's prior expectations for the disease area are met. Common endpoint failure modes to surface:
   - **Surrogate endpoints used to support a hard-outcome claim.** Surrogates are acceptable when the regulator has accepted them in the indication (e.g., HbA1c for type 2 diabetes glycemic control; viral load for HIV; LDL cholesterol for cardiovascular event reduction in many contexts) and not otherwise. Claiming "reduced cardiovascular events" from an LDL-cholesterol endpoint requires the surrogate-to-outcome pathway to be accepted in the specific indication and population.
   - **Composite endpoints with one driver.** A composite endpoint that is driven primarily by its softest component (e.g., a major adverse cardiac events composite driven entirely by reductions in unstable angina hospitalizations) does not support a claim on the harder components.
   - **Patient-reported outcomes without an instrument with regulatory pedigree.** A PRO endpoint that uses a non-validated instrument is fragile. For US filings, FDA's PRO guidance establishes the evidentiary expectations for instrument development and content validity.
   - **Endpoints measured at the wrong time.** A 12-week endpoint cannot support a claim about durable effect; a 6-month follow-up cannot support a "chronic" claim. Time horizon must match claim duration.

4. **Assess statistical power and effect-size interpretation honestly.** An underpowered study that still hits its endpoint can be a regulator's gift (a positive trial despite headwinds) or a hostage (a fragile effect that may not replicate). The narrative should report:
   - **Pre-specified power assumptions** — what effect size was the trial powered to detect, at what alpha and beta? Was the analysis pre-specified or post-hoc?
   - **Observed effect size with confidence interval** — point estimate, two-sided 95% CI, and explicit comparison of the lower CI bound to the clinically meaningful threshold. A statistically significant result whose lower 95% CI includes a clinically negligible effect should be flagged.
   - **Multiplicity adjustments** — if multiple primary or key-secondary endpoints were tested, was the family-wise error rate controlled? An "as-tested" p-value that does not account for multiplicity is suspect.
   - **Sensitivity analyses** — primary analysis robustness across reasonable alternative analyses (per-protocol vs. ITT, multiple imputation for missing data, exclusion of protocol deviators). If the primary effect collapses under reasonable sensitivity analyses, the narrative must acknowledge this.

5. **Map subgroup and sensitivity analyses to the claim's scope.** Regulators read subgroup forest plots looking for two patterns: (a) heterogeneity that should narrow the indication (e.g., effect concentrated in one subgroup, absent in another); (b) directional reversal in a subgroup (the "harm in some" red flag that triggers an FDA Advisory Committee or an EMA Scientific Advisory Group). Surface both patterns explicitly. The narrative should not silently support a broad indication when subgroup data argue for narrowing.

6. **Integrate safety into the evidence narrative rather than ghettoizing it.** A common defect in clinical-evidence narratives is treating safety as a separate appendix. For regulator-readable narrative purposes:
   - **Common adverse events** — incidence and exposure-adjusted rates vs. comparator. Anything more frequent than comparator deserves narrative discussion, not just a table.
   - **Serious adverse events** — adjudicated where appropriate; integrated incidence across the program.
   - **Adverse events of special interest (AESIs)** — class-effect events the regulator expects to see characterized (e.g., hepatotoxicity for many drugs, infections for immunosuppressants, suicidality for CNS-acting drugs).
   - **Deaths, treatment discontinuations, dose modifications** — must be reported and contextualized against the proposed indication's benefit profile.

7. **Surface the gap between claim and evidence explicitly.** The most valuable section of the narrative is the gap analysis. For each component of the claim, ask: "Is this directly supported by the study evidence, partially supported, or unsupported?" Use three buckets:
   - **Fully supported** — pre-specified endpoint, adequately powered, robust to sensitivity analyses, consistent across subgroups, with safety profile compatible with the benefit.
   - **Partially supported** — the evidence is consistent with the claim but has a recognizable gap (e.g., insufficient long-term follow-up; subgroup limitation; surrogate-only endpoint).
   - **Unsupported** — the evidence does not address the claim, or the data argue against it.
   For each partial or unsupported component, propose either (a) a narrowed claim that *is* supported, or (b) the specific additional evidence (post-approval study, real-world evidence commitment, pediatric extension) that would close the gap. Never paper over a gap with verbal scaffolding; reviewers notice.

8. **Match the structural conventions of the submission type and region.** Different submissions and regions expect different narrative shapes:
   - **NDA / BLA Module 2.5 (Clinical Overview)** — concise integrated narrative across the clinical program; benefit-risk synthesis; references to detailed CSRs in Module 5. ICH M4E gives the formal structure.
   - **NDA / BLA Module 2.7 (Clinical Summary)** — detailed summary by topic (biopharmaceutics, clinical pharmacology, clinical efficacy, clinical safety, literature).
   - **510(k) clinical-evidence section** — short, anchored to the substantial-equivalence argument. Clinical data is required only when bench/animal data cannot adequately address the SE question; the narrative should be tight on the specific equivalence point the data supports.
   - **De Novo clinical-evidence section** — independent demonstration of safety and effectiveness for the proposed special-controls. More substantive than 510(k); less rigid than PMA.
   - **PMA clinical-evidence section** — full demonstration of safety and effectiveness. Comparable in rigor to NDA/BLA for the device's risk profile.
   - **IND** — supports the safety and rationale for initiating clinical investigation, not yet a label-claim narrative. The methodology here applies more to later-stage program reviews.
   - **CE marking / MDR clinical-evaluation report** — EU expectation is a structured Clinical Evaluation Plan (CEP) and Clinical Evaluation Report (CER) per MDR Annex XIV, with explicit literature, equivalence, and clinical-investigation pathways.

9. **Write to the reviewer who has read a hundred of these.** Reviewers skim for signal. Strong narrative habits:
   - State the conclusion of each subsection in the first sentence.
   - Use specific numbers with confidence intervals rather than directional words.
   - Acknowledge weaknesses before the reviewer flags them; pre-emptive acknowledgment is read as credibility.
   - Avoid promotional language ("breakthrough," "best-in-class," "rapid onset"); regulators read promotional tone as a signal that the evidence is being oversold.
   - Cite ICH guidelines, agency guidances, and disease-area expert consensus where the claim depends on shared methodology rather than novel argument.

10. **Recommend pre-submission interaction when the gap analysis surfaces material risk.** If the gap analysis flags partial or unsupported components, a Type B / Type C meeting (FDA), Scientific Advice (EMA), or pre-submission meeting (Health Canada) is almost always worth the cost. The cheapest fix is a regulator pre-aligned on a narrowed claim; the most expensive is a Complete Response Letter or a Major Objection asking for additional studies.

11. **Self-check before returning.** Confirm: (a) the proposed claim is restated verbatim at the top; (b) every claim component appears in the gap-analysis section with a fully/partially/unsupported determination; (c) every "partially supported" or "unsupported" finding has an explicit mitigation or scoped-claim recommendation; (d) statistical-power statements use confidence intervals, not just p-values; (e) safety is integrated, not appended; (f) the disclaimer is present; (g) the narrative does not use promotional language.

12. **When the evidence does not support the proposed claim, recommend a narrowed claim plainly.** A draft that scopes the indication to what the evidence actually supports is more valuable than one that overstates. The narrative should propose specific narrower language with the rationale. The sponsor's commercial team will push back; the regulatory team has a documented basis to defend.

## Inputs

- `proposed_label_or_indication` (required, text) — verbatim claim language. The entire narrative anchors on this.
- `study_descriptions` (required, text) — design, population, comparator, sample size, primary endpoint, key secondaries, follow-up, results with effect sizes and CIs.
- `submission_type` (required, choice) — drives structural conventions.
- `regulatory_region` (optional, choice) — drives regional structural and methodological conventions.
- `known_evidence_gaps` (optional, text) — sponsor-acknowledged gaps. The agent will prioritize mitigation discussion.

## Outputs

- `evidence_narrative` (markdown) — proposed claim restated; per-study design adequacy assessment; endpoint-relevance assessment; statistical-power and effect-size interpretation; subgroup and sensitivity analyses; integrated safety summary; gap-analysis-vs-claim section with fully/partially/unsupported determinations and mitigations; pre-submission recommendation if warranted; structural notes for the target submission section.
- `evidence_json` (JSON) — `proposed_claim`, `design_adequacy` (per study), `endpoint_relevance` (array), `power_assessment`, `gaps_vs_claim` (array of {gap, severity, mitigation}), `label_supportability` (full | partial | unsupported), `recommended_claim_revision` (string, if applicable), `pre_submission_recommended` (bool), `confidence` (float), `confidence_reason`.

## Examples

### Example 1 — straightforward NDA Clinical Overview support

**Input proposed_label_or_indication:** "Indicated for the treatment of moderate-to-severe plaque psoriasis in adults who are candidates for systemic therapy or phototherapy."

**Input study_descriptions (excerpt):** Two pivotal Phase 3 RCTs, randomized 2:1 active vs. placebo, 12-week primary endpoint of PASI 75 response and IGA 0/1 response. N=720 across the two studies. Primary endpoints met with PASI 75 responses of 78% and 81% vs. placebo 6% and 5% (p<0.001 each; multiplicity-controlled gatekeeping hierarchy pre-specified). Safety profile: most common AEs nasopharyngitis and injection-site reactions; serious infections similar to placebo.

**Input submission_type:** `nda`. **regulatory_region:** `fda`.

**Output evidence_narrative (excerpt):**

> **Proposed indication.** "Indicated for the treatment of moderate-to-severe plaque psoriasis in adults who are candidates for systemic therapy or phototherapy."
>
> **Design adequacy.** Two adequate-and-well-controlled Phase 3 RCTs against placebo, 2:1 randomization, double-blind, pre-specified gatekeeping multiplicity strategy. Population matches the proposed indication (moderate-to-severe; adults; candidates for systemic therapy or phototherapy per the standard enrollment criteria for the indication). Design class is appropriate for the indication and consistent with the regulatory precedent set by prior approvals in plaque psoriasis.
>
> **Endpoint relevance.** PASI 75 and IGA 0/1 at 12 weeks are accepted clinical endpoints in plaque psoriasis with extensive regulatory precedent. Both endpoints support the proposed indication directly.
>
> **Power and effect.** Effect sizes (78%/6% and 81%/5%) are large, with non-overlapping 95% CIs. Lower CI bound of the treatment-effect difference is well above the clinically meaningful threshold of 15 percentage points used in prior psoriasis trials.
>
> **Safety integration.** Common AEs and serious infections in line with prior approvals in this class; benefit-risk supports the proposed indication.
>
> **Gap analysis vs. claim.** **Fully supported.** Both efficacy and safety evidence directly support the proposed indication language without modification.
>
> **Label supportability:** full. **Confidence:** 0.85.

### Example 2 — claim-evidence mismatch demanding a narrower indication

**Input proposed_label_or_indication:** "Indicated for the prevention of major adverse cardiovascular events in adults with elevated LDL cholesterol."

**Input study_descriptions (excerpt):** One 18-month Phase 3 RCT, N=420, primary endpoint LDL-C percent reduction. LDL-C reduced 55% vs. placebo, statistically significant. Adjudicated MACE events 12 vs. 14 — exploratory analysis, study not powered for cardiovascular outcomes.

**Output evidence_narrative (excerpt):**

> **Gap analysis vs. claim.**
> - **MACE prevention claim — unsupported.** The trial was powered for an LDL-C endpoint, not a cardiovascular outcome. Observed MACE counts (12 vs. 14) are small and the trial was not designed or powered to detect a difference. The cardiovascular-outcome surrogate-to-claim path requires either a powered cardiovascular outcomes trial or reliance on FDA's accepted surrogate framework for LDL-C-to-MACE — which itself requires demonstrating expected effect-size and consistency with prior accepted agents.
> - **LDL-C reduction — fully supported.** A 55% LDL-C reduction is robust and clinically meaningful.
>
> **Recommended claim revision.** "Indicated as an adjunct to diet, alone or in combination with other LDL-cholesterol-lowering therapies, in adults with primary hyperlipidemia to reduce low-density lipoprotein cholesterol (LDL-C)." A cardiovascular-outcomes claim should be supported by a separately powered cardiovascular outcomes trial (CVOT) as a post-approval commitment.
>
> **Label supportability:** partial — supportable as an LDL-C-lowering indication; not supportable as a MACE-prevention indication with current evidence.
>
> **Pre-submission strongly recommended** to align with FDA on the surrogate-to-outcome pathway and the post-approval CVOT design.

### Example 3 — 510(k) clinical evidence section

**Input proposed_label_or_indication:** "Indicated for non-invasive measurement of functional oxygen saturation (SpO2) in adults in hospital settings."

**Input study_descriptions (excerpt):** One controlled desaturation study per ISO 80601-2-61, N=12 healthy adult subjects, SpO2 range 70-100%, accuracy 1.8% Arms across the range. Comparison against arterial blood gas reference.

**Input submission_type:** `510k`. **regulatory_region:** `fda`.

**Output evidence_narrative (excerpt):**

> **Submission context.** Clinical evidence for this 510(k) is anchored to the substantial-equivalence argument vs. predicate K20XXXX. The clinical study addresses the accuracy specification, which is the principal technological difference from the predicate.
>
> **Design adequacy.** Controlled desaturation study per ISO 80601-2-61 is the standard methodology for pulse-oximeter accuracy claims. Sample size, demographic distribution, and reference method follow the consensus standard.
>
> **Endpoint relevance.** Accuracy expressed as Arms across the indicated SpO2 range is the consensus performance metric, directly supports the accuracy specification, and is consistent with the predicate's accuracy claim.
>
> **Gap analysis vs. claim.** **Fully supported** for the proposed indication. No additional clinical evidence required for the SE argument as drafted.
>
> **Label supportability:** full. **Confidence:** 0.80.

## Limitations

- **Not regulatory advice.** Outputs are methodology drafts. Qualified regulatory affairs and biostatistical professionals must verify all claims, statistical interpretations, and gap analyses.
- **Not a biostatistical engine.** The skill does not perform statistical analyses, recalculate p-values, fit models, or run simulations. It works from results the sponsor provides.
- **Disease-area precedent matters more than the skill can fully encode.** What "counts" as adequate evidence is heavily disease-specific. The skill applies durable methodology principles and flags when disease-specific expertise is needed.
- **PRO and surrogate-endpoint judgments are regulator-specific.** Acceptance of a particular PRO instrument or surrogate endpoint requires a current regulator-specific review, which the skill does not perform.
- **Real-world evidence (RWE) handling is light.** The skill recognizes RWE as a possible gap-bridging strategy but does not draft the RWE methodology in depth.
- **Pediatric, geriatric, and rare-disease nuances are flagged but not exhaustively handled.** Pediatric study plans, breakthrough designations, orphan designations, and accelerated approval frameworks may require additional specialist input beyond what this skill produces.
- **Regional adaptations are sketched, not deep.** EMA, PMDA, NMPA, and Health Canada conventions differ from FDA in meaningful ways that this skill identifies but does not fully encode.
- **Cannot read CSRs.** If raw clinical study reports (CSRs) are the only input, the agent will produce a degraded narrative; sponsors should pre-summarize.

## Sources reviewed

The methodology below was informed by reviewing publicly available, permissively-licensed clinical-trial and regulatory tooling repositories on GitHub, plus regulator-public-domain and ICH-guideline references. No source content was reproduced. **Honest disclosure of source thinness:** clinical-evidence drafting tooling under MIT/Apache/BSD/ISC/Unlicense terms on GitHub is sparse; the most widely-used reporting frameworks (SPIRIT, CONSORT) are CC-licensed and were used as URL references only, not as primary methodology sources. Methodology rests on a small set of MIT-licensed tooling repositories plus regulator and ICH guideline URLs used as references only.

- https://github.com/awconway/spiritR (MIT — SPIRIT-checklist-aligned clinical-trial protocol template structure, used only as a tooling reference)
- https://github.com/innolitics/rdm (MIT — regulatory documentation manager methodology, applicable to clinical evidence sections for software devices)
- https://github.com/rlwadh/fda-predicate-finder (MIT — predicate context for clinical-evidence requirements in 510(k))
- https://github.com/tsbischof/fda (BSD-2-Clause — FDA 510(k) data tooling, contextual reference for clinical-evidence-section conventions)
- https://www.ich.org/page/efficacy-guidelines (ICH efficacy guidelines index, including E6, E8, E9, E10 — reference only, not a source repo)
- https://www.fda.gov/regulatory-information/search-fda-guidance-documents (FDA guidance index — reference only, not a source repo)
- https://www.ema.europa.eu/en/human-regulatory-overview/research-and-development/scientific-guidelines (EMA scientific guidelines — reference only, not a source repo)
