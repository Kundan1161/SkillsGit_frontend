---
id: skillsgit-curated/periodic-safety-report-architect
version: 0.1.0
name: Periodic Safety Report Architect
description: Outline a generic PBRER/PSUR structure covering exposure, ongoing safety profile, signal status, benefit-risk, and conclusions.
authors:
  - name: Wave-3 Synthesis Agent
    handle: synth-pv
    role: author
category: healthcare
tags:
  - niche:pharmacovigilance
  - psur
  - pbrer
  - benefit-risk
  - periodic-report
  - drug-safety
  - methodology
license_type: free
ai:
  required_models:
    - claude-opus-4-7
  compatible_models:
    - claude-sonnet-4-6
    - gpt-4o
  min_context_tokens: 50000
  estimated_tokens_per_invocation: 9500
trigger_keywords:
  - PSUR
  - PBRER
  - periodic safety update
  - benefit-risk evaluation
  - periodic benefit risk
  - DLP
  - data lock point
  - reference safety information
example_invocations:
  - "Outline a PBRER for a product with two indications and one DLP six months away."
  - "Architect the signal and risk sections of our next PSUR."
  - "Give me a structured PBRER skeleton with placeholder content so the medical writer can fill it in."
inputs:
  - name: product_profile
    type: text
    required: true
    description: Active substance, indication(s), authorisation history, regions of authorisation, reporting period type (6-monthly, 12-monthly, etc.).
  - name: data_lock_point
    type: text
    required: true
    description: The intended data lock point and the reporting interval covered.
  - name: known_risks_and_signals
    type: text
    required: false
    description: Important identified risks, important potential risks, and any signals currently under evaluation.
  - name: regions
    type: text
    required: false
    description: Regulatory regions for which the report is intended (EU, US, UK, ICH region, global).
outputs:
  - name: report_outline
    type: markdown
    description: A sectioned generic outline of a PBRER/PSUR with explanatory guidance under each section — not a final regulatory document.
changelog:
  - version: 0.1.0
    date: 2026-05-14
    notes: Initial synthesis. Generic structure aligned with publicly published ICH-E2C(R2) headings; no proprietary text reused.
---

# Periodic Safety Report Architect

> **Mandatory disclaimer.** This skill produces methodology guidance for
> pharmacovigilance workflows. Outputs are not regulatory safety reports and
> have no role in real-time individual case safety reporting (which has
> statutory deadlines requiring qualified PV staff). Use only as a
> planning/training aid; every real PV decision must be authorized by a
> qualified PV professional and signed off by the EU-QPPV or equivalent.

## When to use

Use this skill when a pharmacovigilance, medical writing, or regulatory
affairs team wants a **generic structural outline** for a Periodic Benefit-
Risk Evaluation Report (PBRER) or Periodic Safety Update Report (PSUR) —
typically for:

- planning the table of contents and section ownership;
- training new medical writers on the canonical PBRER/PSUR shape;
- preparing internal kickoff documents before content authoring begins;
- mapping which datasets and signal-evaluation outputs each section needs.

Do **not** use this skill to:

- generate the actual content submitted to a regulator;
- produce final benefit-risk conclusions;
- replace the company's PV system master file, signal-management SOP, or
  EU-QPPV oversight;
- bypass the qualified writer / qualified PV scientist / QPPV signoff chain.

## How to apply

Generate the outline below as a single markdown document. Each top-level
section is mandatory; sub-bullets are guidance for the human author and
should remain in the output as instructions to fill in. Do **not** invent
benefit-risk conclusions, exposure figures, signal outcomes, or label
recommendations.

### 1. Introduction

- International Birth Date (IBD) and the reporting interval.
- Data lock point.
- Authorisation status by region (brief table placeholder).
- Whether the product is single-source or multi-source.
- Reporting authority context (EU PSUR Single Assessment, US PADER /
  PBRER, ICH region, etc.).

### 2. Worldwide marketing authorisation status

A table with one row per region containing:

- region;
- indication(s) authorised in that region;
- date of first authorisation;
- proprietary name;
- prescription status;
- any current regulatory action (suspension, withdrawal, label restriction).

### 3. Actions taken in the reporting interval for safety reasons

List, with dates and triggers, every regulatory or company-initiated action
that touched the safety of the product, including:

- label changes (any region);
- DHPC / Dear Healthcare Provider Letter;
- safety-related variations;
- clinical-trial pauses or holds;
- batch withdrawals;
- marketing suspensions or restrictions;
- changes to the Risk Management Plan (RMP).

If no actions occurred, state explicitly: *"No actions taken in the
reporting interval for safety reasons."*

### 4. Changes to reference safety information

- Version of the Company Core Data Sheet (CCDS) / Core Safety Information
  (CSI) at the start and end of the interval.
- Diff summary: new adverse drug reactions added, frequency category
  changes, new contraindications, new warnings.
- Cross-reference to which signal evaluation drove each change.

### 5. Estimated exposure and use patterns

Two subsections.

**5.1 Cumulative subject exposure from clinical trials.**

- Number of subjects exposed by indication, dose range, duration.
- Exposure in special populations (paediatric, elderly, renal/hepatic
  impaired, pregnant — explicitly flagged).

**5.2 Cumulative and interval patient exposure from marketing experience.**

- Method of estimation (sales-based, prescriptions, patient-days, defined
  daily doses).
- Caveat: post-marketing exposure is an estimate; spontaneous-report
  denominators are weak.
- Breakdown by region and by indication when feasible.

### 6. Data in summary tabulations

- Cumulative serious adverse events from clinical trials by MedDRA SOC.
- Cumulative and interval ICSRs from post-marketing by SOC and seriousness.
- Vaccination products: report by region per VAERS/EudraVigilance/national
  equivalent.
- Note: tabulations are descriptive, not analytic.

### 7. Summaries of significant findings from clinical trials

For each ongoing or completed study in the interval:

- Study identifier, design, population.
- Safety findings of note: new or changed adverse drug reactions, deaths,
  serious unexpected events.
- Cross-link to the relevant clinical study report or DSUR.

### 8. Findings from non-interventional studies, other clinical trials and sources

Include:

- Post-authorisation safety studies (PASS).
- Registry data.
- Compassionate-use programmes.
- Literature reports (with citation list).
- Solicited reports (patient-support programmes, market research).

### 9. Other periodic reports

- Linkage to the most recent Development Safety Update Report (DSUR) if
  the product is also in development.
- Linkage to the previous PBRER/PSUR.
- Reconciliation note: any discrepancy between this and the previous report
  must be explained.

### 10. Lack of efficacy in controlled clinical trials

Report any controlled clinical trial data in the interval suggesting lack
of efficacy where this could have a clinically significant impact on the
benefit-risk balance.

### 11. Late-breaking information

Information that arrived **after** the data lock point but before
report finalisation and which is relevant to benefit-risk.

### 12. Overview of signals: new, ongoing, or closed

The core section. For each signal handled in the interval:

- Source (disproportionality analysis, case-series review, literature,
  regulator query, company review).
- Date opened.
- Current status: under evaluation, closed-refuted, closed-confirmed
  (becomes an identified or potential risk), validated.
- Summary of evaluation including methods, key cases, conclusion.
- Required follow-up: label change, RMP update, additional study, no
  further action.
- Cross-reference the *Signal Detection Planner* output where applicable.

### 13. Signal and risk evaluation

Three subsections.

**13.1 Summaries of safety concerns.** Important identified risks,
important potential risks, and missing information — copied forward from
the RMP and updated.

**13.2 Signal evaluation.** Method, data sources, results, and
conclusions for each signal closed in the interval.

**13.3 Evaluation of risks and new information.** Evaluation of any new
information on previously characterised risks (e.g. dose-response, time-
to-onset, reversibility, risk factors).

### 14. Characterisation of risks

For each important identified risk and important potential risk:

- Frequency.
- Mechanism if known.
- Severity, reversibility, outcome.
- Risk factors and risk groups.
- Preventability and current minimisation measures.

### 15. Effectiveness of risk minimisation

For products with additional risk minimisation measures (educational
material, controlled-access programmes, pregnancy-prevention programmes):

- Description of measure.
- Effectiveness indicator data.
- Conclusion: effective, partially effective, requires revision.

### 16. Benefit evaluation

- Important baseline efficacy/effectiveness information from the
  authorisation dossier.
- Newly identified information on efficacy or effectiveness from the
  interval.
- Characterisation of benefits: magnitude, duration, generalisability.

### 17. Integrated benefit-risk analysis

The qualitative integration step. Do **not** auto-generate a conclusion.
The skill output must reserve this section for the qualified author and
include the following placeholder structure:

- Benefit-risk context (intended use, severity of indication, alternatives).
- Benefit-risk analysis evaluation: integrate benefits (Section 16) and
  risks (Section 14).
- Sources of uncertainty.

### 18. Conclusions and actions

State explicitly that conclusions and any proposed actions are to be
drafted by the qualified safety physician and approved by the QPPV /
equivalent — this skill *must not* draft them.

### 19. Appendices

A standard appendix list:

- Reference Safety Information valid at the data lock point.
- Cumulative and interval line listings of ICSRs.
- List of ongoing and completed clinical studies.
- List of signals opened, ongoing, and closed.
- List of regulatory actions for safety reasons.

## Ownership and review matrix

Provide a small RACI placeholder so the team can assign owners:

| Section | Author | Reviewer | Approver |
|---|---|---|---|
| 1–4 | Regulatory | Medical writer | QPPV |
| 5–8 | Medical writer | Safety scientist | QPPV |
| 12–13 | Safety scientist | Signal-management lead | QPPV |
| 14–18 | Safety physician | QPPV | QPPV |

## Inputs

- `product_profile` — active substance, indications, authorisation
  history, regions, reporting cadence.
- `data_lock_point` — DLP date and interval covered.
- `known_risks_and_signals` — important identified / potential risks and
  open signals.
- `regions` — intended regulatory regions.

## Outputs

A markdown outline with the 19 sections above plus the ownership matrix.
Each section contains guidance bullets but **no fabricated content**. The
output is a skeleton, not a finished report.

## Examples

> **User**: "Outline a PBRER for our PARP inhibitor — one EU and one US
> indication, IBD 4 years ago, next DLP 30 June, 6-monthly reporting."
>
> **Assistant**: produces a 19-section skeleton, populates section 1 with
> the IBD and DLP, section 2 with a two-row authorisation placeholder
> table, section 12 with empty rows for any open signals the user lists,
> and explicitly leaves sections 17 and 18 as author-only.

## Limitations

This skill **does not**:

- write benefit-risk conclusions;
- calculate exposure denominators;
- produce final RMP updates;
- generate line listings of cases;
- substitute for the company SOP on periodic reporting;
- handle final QPPV signoff — that responsibility cannot be delegated to
  this skill or any AI.

A regulatory submission produced from this skeleton without qualified human
authorship and QPPV oversight would be non-compliant with ICH-E2C(R2) and
EU GVP Module VII expectations.

## Common pitfalls when using a skeleton like this

1. **Treating the skeleton as content.** The skeleton is *structural*; it
   contains no facts. A reviewer should be able to tell from one glance
   that nothing has been filled in yet.
2. **Letting the assistant draft the benefit-risk conclusion.** Section 17
   and Section 18 are intentionally left for the qualified author. Do not
   bypass.
3. **Omitting the late-breaking section** because nothing arrived. State
   *"No late-breaking information."* explicitly — silence is not the same
   as nil.
4. **Re-using last cycle's wording.** The PBRER is a fresh evaluation; the
   skeleton must not import prior cycle conclusions verbatim.
5. **Mixing the EU-only and US-only formats in one document.** If two
   regions are intended, plan two reports or one PBRER-aligned document
   with a regional addendum.
6. **Forgetting the appendices.** Line listings and the RSI version at
   DLP are mandatory and must be cross-referenced from the body.

## Cadence and project plan placeholder

Include a small timeline placeholder in the output so the team can fit
the report into the regulatory deadline:

- DLP minus 90 days: outline frozen, ownership assigned.
- DLP minus 60 days: data extracts from the safety database.
- DLP minus 30 days: signal evaluations closed.
- DLP: lock data.
- DLP plus 30 days: full draft for medical review.
- DLP plus 45 days: QPPV review.
- DLP plus 70 days (EU 6-monthly): submission.
- (Adapt the actual day-offsets to the relevant procedure — this is a
  generic placeholder, not regulatory deadlines.)

## How this skill differs from a real PBRER authoring workflow

A real PBRER workflow involves: a controlled medical-writing template, a
locked safety database, signed-off signal evaluations, QPPV oversight,
the company core data sheet at the data lock point, and a publishing
pipeline. This skill produces a **structural skeleton only**. It does
not:

- pull data from any system;
- compute exposure;
- evaluate signals;
- characterise risks;
- write the benefit-risk integration;
- decide submission timing.

A PBRER produced from this skeleton without the full qualified workflow
would be non-compliant. The skeleton is a planning artefact, useful for
medical-writer onboarding, internal kickoff meetings, and SOP training.

## Sources

Synthesis is based on publicly available, URL-only references. Open-source
code for periodic-safety-report authoring under permissive licences is
genuinely nonexistent — disclosed honestly. The structural conventions
follow the publicly published ICH-E2C(R2) and EMA GVP Module VII headings.

- https://github.com/InfOmics/TEDAR
- https://github.com/WangLabCSU/faers
- https://github.com/ltscomputingllc/faersdbstats
- https://github.com/ngiangre/openFDA_drug_event_parsing
- https://www.ema.europa.eu/en/human-regulatory-overview/post-authorisation/pharmacovigilance-post-authorisation/periodic-safety-update-reports-psurs
- https://www.who.int/publications/m/item/WHO-causality-assessment
