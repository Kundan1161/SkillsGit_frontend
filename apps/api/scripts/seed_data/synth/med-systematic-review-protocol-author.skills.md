---
id: skillsgit-curated/med-systematic-review-protocol-author
version: 1.0.0
name: Medical Systematic Review Protocol Author
description: Draft a pre-registrable protocol for a medical literature review — structured question, eligibility rules, source list, per-database search strings, risk-of-bias plan, and synthesis approach.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: healthcare
tags: [niche:medical-literature-review, evidence-synthesis, protocol, pico, search-strategy, risk-of-bias, pre-registration]
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
  estimated_tokens_per_invocation: 12000
trigger_keywords:
  - write a review protocol
  - draft a systematic review protocol
  - register a review
  - pico question
  - picos
  - eligibility criteria
  - search strategy for medline
  - search strategy for embase
  - inclusion exclusion criteria
  - prospero registration
  - scoping review protocol
  - rapid review plan
  - methodology for literature review
example_invocations:
  - "Draft a protocol for a review of SGLT2 inhibitors in non-diabetic heart failure patients."
  - "We need a pre-registrable plan for a scoping review of digital therapeutics for adolescent depression."
  - "Help me build a search strategy across MEDLINE, Embase, and CENTRAL for inhaled corticosteroid step-down in mild asthma."
inputs:
  - name: review_topic
    type: text
    required: true
    description: A free-text description of the clinical question, what is already known, why a review is needed, and the intended audience (clinicians, guideline developers, patients, payers).
  - name: review_type
    type: choice
    required: false
    description: Type of evidence synthesis the protocol should cover. Defaults to systematic_review.
    choices: [systematic_review, scoping_review, rapid_review, living_review, overview_of_reviews]
  - name: time_window
    type: text
    required: false
    description: Date limits for included studies and any rationale (e.g., post-approval date of a drug, year a guideline was last updated).
  - name: team_constraints
    type: text
    required: false
    description: Practical constraints — number of reviewers, language skills, statistical capacity, deadline.
  - name: existing_reviews
    type: text
    required: false
    description: References to prior reviews on the topic. Used to justify scope and gap.
outputs:
  - name: protocol_markdown
    type: markdown
    description: A pre-registrable protocol document with all required sections.
  - name: search_strategy_blocks
    type: markdown
    description: Per-database search strings (MEDLINE/Ovid, Embase, CENTRAL, CINAHL, etc.) with line-by-line logic and translation notes.
  - name: open_questions
    type: markdown
    description: Items the clinical lead must decide before the protocol can be registered.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Medical Systematic Review Protocol Author

## When to use

Use this skill when a clinical team is about to start a structured literature review and needs a defensible written plan before screening begins. The protocol is the contract the review team signs with itself: what question is being asked, which studies count, where to look, how to judge quality, and how to combine results. Writing the protocol after screening has already started introduces a well-known source of bias and undermines any later claim that the review followed an a-priori plan.

This skill produces methodology guidance for literature reviews. Outputs are not clinical decisions or care recommendations. Every output must be reviewed by qualified clinical/research staff. Conclusions about treatment efficacy or safety must be confirmed against current clinical practice guidelines and primary literature.

Typical triggers:

- A grant proposal, dissertation chapter, guideline update, or health-technology-assessment task is starting and needs a protocol on file.
- A clinical question keeps surfacing in journal club and the team wants a structured answer rather than a narrative impression.
- A drug or device has new outcomes data and the existing reviews are out of date.
- A funder or registry (PROSPERO, OSF) requires pre-registration before screening.
- A team is preparing a scoping review to map a heterogeneous evidence base before committing to a full systematic review.

Do not use this skill for:

- Single-paper appraisals — those are critical-appraisal tasks, not protocols.
- Clinical decision support — protocols describe how evidence will be summarized, not what to do at the bedside.
- Bench science literature surveys with no clinical question — the framing here assumes a patient-centered question.

## Inputs

- `review_topic` (required) — Free-text describing the clinical scenario. The more detail, the better: who the patients are, what is being compared to what, what outcomes matter to patients and clinicians, and why a fresh review is justified now. Vague topics (e.g., "diabetes") get pushed back as `open_questions` for the user to refine.
- `review_type` — Selects the methodological flavor:
  - `systematic_review` — narrow question, comprehensive search, formal risk-of-bias and quantitative synthesis where feasible.
  - `scoping_review` — broader question, focus on mapping evidence types, less emphasis on quality appraisal.
  - `rapid_review` — accelerated methods with documented shortcuts (single-reviewer screening, limited databases) and explicit acknowledgement of the trade-offs.
  - `living_review` — periodic re-runs of the search with a defined trigger for incorporating new evidence.
  - `overview_of_reviews` — synthesis of existing reviews rather than primary studies; includes an overlap analysis plan.
- `time_window` — Inclusion date range and justification.
- `team_constraints` — Number of independent screeners, statistical capability (none / descriptive / random-effects modeling / network meta-analysis), and timeline.
- `existing_reviews` — References to prior reviews, including any that are out of date or methodologically limited; used to justify scope.

## How to apply

Apply the steps in order. Where input is missing, write a placeholder enclosed in `<TODO: ...>` and list each placeholder in `open_questions` rather than inventing details. A protocol with honest gaps is more useful than one with confident guesses.

### 1. Sharpen the question into a structured form

1.1. Restate `review_topic` as a structured question with these slots: **Population**, **Intervention** (or Exposure), **Comparator**, **Outcomes**, and **Study designs**. For prognostic or diagnostic questions, swap the slots appropriately (e.g., Index test, Reference standard, Target condition).

1.2. Population: specify clinical condition, severity, setting (primary care, ICU, community), age band, and any pre-specified subgroups. "Adults with type 2 diabetes and stage 3 CKD treated in outpatient endocrinology" is a usable population definition; "diabetics" is not.

1.3. Intervention: name the agent, class, dose range, duration, route, and any constraints (e.g., "as add-on to standard therapy" or "as monotherapy"). For complex interventions, describe the active components and the comparator condition explicitly.

1.4. Comparator: state what the intervention is being compared against — placebo, active comparator, usual care, or another intervention class. "No comparison" is allowed for single-arm prognostic questions and should be noted as such.

1.5. Outcomes: split into **critical outcomes** (patient-important, used to drive conclusions) and **important outcomes** (informative but not decision-driving). For each outcome, specify the measurement instrument, the time horizon, and whether absolute or relative effect is the primary metric. Patient-reported outcomes and harms deserve at least as much space as efficacy endpoints.

1.6. Study designs: specify which designs are eligible and why. For therapy questions, randomized trials usually dominate; for harms, observational designs may be necessary; for prognosis, cohort studies; for diagnostic accuracy, cross-sectional or cohort designs with a defined reference standard.

1.7. If the question cannot be put in a structured slot form without distortion, the question is too broad. Surface this in `open_questions` and propose two or three narrower sub-questions.

### 2. Write the background and justification

2.1. Two or three paragraphs: clinical importance of the condition, current uncertainty, what existing reviews have found and where they fall short, and what the new review will add. Anchor every quantitative claim to a citation.

2.2. State the explicit gap: a new molecule entered the market, a guideline group needs evidence by a deadline, prior reviews used different outcomes, prior reviews are stale, prior reviews disagreed.

2.3. Avoid marketing language. The background should read as a fair-minded statement of what is known and unknown, not as a sales pitch for the review.

### 3. Lock the eligibility criteria

3.1. Restate population, intervention, comparator, outcomes, and study designs as inclusion criteria. Then write the **exclusion criteria** as a parallel list — what would force a study out even if it superficially matches inclusion.

3.2. Be explicit about: language restrictions (and the reason — translation capacity, not a quality claim), publication status (peer-reviewed, conference abstracts, preprints, theses), study size minimum, follow-up minimum, and any setting restrictions.

3.3. Pre-specify the rules for handling **mixed-population studies** (subgroup data available vs. not), **multi-arm trials** (which comparisons are eligible), and **multiple publications of the same study** (which to count as the primary report).

3.4. Eligibility criteria must be testable. A criterion like "high-quality study" is not testable — replace with the specific risk-of-bias domains that will be assessed.

### 4. Design the search

4.1. List the databases. For a clinical question, a defensible baseline is: a major biomedical database, a European biomedical database with broader pharmaceutical and conference coverage, a trial-specific register, a discipline-specific database where relevant (nursing, psychology, rehabilitation), and a grey-literature/clinical-trial-registry pair. The exact databases depend on the question; justify each choice.

4.2. For each database, build a **search strategy block** with three layers:
   - **Concept block A** — the population (controlled vocabulary terms + free-text synonyms).
   - **Concept block B** — the intervention or exposure (controlled vocabulary terms + free-text synonyms + brand and generic names).
   - **Concept block C** — the study design filter, if any (validated filters for randomized trials, observational designs, diagnostic accuracy).

4.3. Combine the blocks with the database's Boolean operators. Translate the strategy for each database — vocabulary, field tags, and truncation differ across platforms. Note translation decisions explicitly so a reviewer can audit them.

4.4. Pre-specify supplementary searches: forward and backward citation chasing of included studies and prior reviews, hand-searching of a small number of high-yield journals if relevant, and contact with subject experts. Each adds breadth but must be planned in advance to avoid post-hoc cherry-picking.

4.5. Validate the strategy against a **seed set** — three to five known-relevant articles the team can name in advance. If the strategy fails to retrieve any seed, iterate. Document the iterations in the protocol so future readers see how the strategy evolved.

4.6. Set the **date the search will be executed** and the rule for re-running before publication if the protocol-to-submission gap exceeds (typically) 12 months.

### 5. Plan the selection and de-duplication workflow

5.1. Describe the citation-management tool, the de-duplication approach (automatic + manual check on near-duplicates), and the screening tool (active-learning-assisted screeners are acceptable if their use is pre-specified and reported).

5.2. Specify **dual independent screening** at title-abstract and full-text stages, with the conflict-resolution rule (third-reviewer adjudication, consensus discussion). For rapid reviews, single-reviewer screening with a calibration step is acceptable if explicitly noted as a deviation.

5.3. Set a **pilot calibration** — the first 50–100 records screened by all reviewers, with disagreements discussed before independent screening continues. Record the inter-rater agreement metric used.

5.4. Define the **reason-for-exclusion taxonomy** at the full-text stage. A taxonomy with five to eight categories (wrong population, wrong intervention, wrong comparator, wrong outcomes, wrong design, no full text available, other) supports the reviewer flow diagram and gives the team a structured way to disagree.

5.5. Describe how the **flow of studies** through identification, screening, eligibility, and inclusion will be reported numerically, with sources of records named at each stage.

### 6. Design the data extraction

6.1. List the variables to extract per study, grouped into: study identification (authors, year, country, funding), design (randomization, blinding, follow-up), population (sample size, age, sex, comorbidity, condition severity), intervention (agent, dose, duration), comparator, outcomes (measurement, time point, summary statistic, dispersion, n at follow-up), and notes (early stopping, protocol deviations).

6.2. Pre-specify **dual independent extraction** for outcome data and a single-reviewer-with-check approach for study-identification fields. State the conflict-resolution rule.

6.3. Plan for **missing data**: contacting authors, imputation rules for standard deviations from confidence intervals or standard errors, and the cutoff at which a study with too much missing data is excluded from the quantitative synthesis but retained in the narrative summary.

6.4. Design the extraction form before screening starts. Pilot it on three to five included studies; revise; freeze. Note that any post-pilot changes must be logged with a justification.

### 7. Plan the risk-of-bias assessment

7.1. Choose an assessment instrument appropriate to the predominant study design — a domain-based tool for randomized trials, an analogous one for non-randomized studies of interventions, a tailored instrument for diagnostic-accuracy studies, prognostic studies, or qualitative studies.

7.2. For each domain, specify the **judgment categories** (typically low / some concerns / high, or low / moderate / high / unclear) and the rules for combining domain judgments into an overall study judgment.

7.3. Specify **dual independent rating** with a calibration set and a conflict-resolution rule. Record both the per-domain and overall judgments in the extraction form.

7.4. Plan how risk of bias will feed into the synthesis: sensitivity analyses excluding high-risk studies, subgroup analyses by risk-of-bias category, or as a downgrading criterion in the overall certainty-of-evidence rating.

### 8. Plan the synthesis

8.1. Specify in advance whether a **quantitative pooled estimate** is the primary goal or whether **structured narrative synthesis** is more appropriate. The decision rule rests on clinical and methodological similarity across studies, availability of a common effect metric, and the number of studies per comparison.

8.2. If quantitative pooling is planned: state the effect metric per outcome (risk ratio, odds ratio, mean difference, standardized mean difference, hazard ratio), the model family (fixed-effect vs. random-effects, with the estimator), and the heterogeneity statistics to be reported.

8.3. Pre-specify **subgroup analyses** and **sensitivity analyses** with clinical rationale for each. Post-hoc subgroups are allowed but must be flagged as exploratory in the final report.

8.4. Pre-specify the assessment for **small-study effects and publication bias** — visual funnel-plot inspection, statistical tests when the comparison includes a sufficient number of studies, and any planned correction methods. Note their limitations.

8.5. If narrative synthesis is planned: describe the structuring framework (by population, by intervention, by outcome), the tabulation approach, and how vote-counting will be avoided or, if used, justified.

8.6. Plan an **overall certainty-of-evidence rating** per outcome that explicitly considers study limitations, consistency across studies, directness to the question, precision of the estimate, and risk of publication bias. State whether and how upgrades for large effects or dose-response gradients will be considered.

### 9. Plan reporting and dissemination

9.1. Specify the reporting checklist the final report will follow (named explicitly so reviewers can audit).

9.2. State where the protocol will be registered and the registration identifier once obtained.

9.3. Describe deviations process: any change to the protocol after registration must be documented with a date, reason, and impact assessment.

9.4. Plan the public-facing summary — a plain-language abstract for patients and clinicians, separate from the technical abstract.

### 10. Plan ethics, funding, and conflict-of-interest declarations

10.1. Note whether ethics approval is needed (typically not for reviews of already-published studies, but check institutional policy).

10.2. State the funding source and whether the funder had a role in the protocol.

10.3. Declare any reviewer conflicts of interest, including financial, intellectual, and personal. Specify how conflicts are managed (e.g., a reviewer with intellectual investment in one option does not screen or extract for that comparison).

### 11. Validate the draft against an internal checklist

Before emitting, verify:

- Structured question is complete (all slots filled or explicitly marked not applicable).
- Eligibility criteria are testable; no quality-laden wording.
- Search strategy includes at least one biomedical, one European biomedical, one trial register, and one grey-literature source — or a written justification for any omission.
- Search strategy retrieves the seed set, with iteration log.
- Selection workflow specifies dual independent screening and conflict resolution.
- Extraction form is pre-specified with dual extraction for outcome data.
- Risk-of-bias instrument is appropriate to the study designs.
- Synthesis plan distinguishes quantitative from narrative paths with an explicit decision rule.
- Subgroup and sensitivity analyses are pre-specified with rationale.
- Certainty-of-evidence framework is named with five core considerations.
- Reporting checklist, registration, and deviation process are named.
- Ethics, funding, and conflict-of-interest declarations are present.

### 12. Emit the protocol

Combine the sections into a protocol document with these headings, in order: Title, Authors and Roles, Background and Justification, Objectives and Structured Question, Eligibility Criteria, Information Sources, Search Strategy (with per-database blocks), Selection Process, Data Extraction, Risk-of-Bias Assessment, Synthesis Methods, Certainty-of-Evidence Assessment, Reporting Plan, Ethics and Funding, Deviations Process, References. Append the search-strategy blocks as `search_strategy_blocks` for separate use.

### Decision rules and heuristics

- **One question per protocol.** Multiple-question reviews invite scope drift. Split into linked protocols if needed.
- **Pre-specify, do not pre-decide.** Pre-specifying analyses is not the same as pre-deciding conclusions. Stay open to what the evidence shows.
- **Patient-important outcomes lead.** If the primary outcome is a surrogate, justify it explicitly and pair it with a downstream patient-important outcome whenever possible.
- **Harms are not optional.** A review of efficacy without harms is half a review. Reserve real space in eligibility and extraction for harms data.
- **Symmetry between intervention and comparator.** The same outcomes, time horizons, and definitions apply to both arms; do not let the protocol favor one side by definition.
- **Document the seed set.** Naming three to five known-relevant papers in advance gives the search a falsification test.
- **Conflict of interest is a method, not a confession.** Manage it through reviewer assignment, not through silence.

### Edge cases

- **Living review.** The protocol must define the trigger condition for re-running the search (calendar interval, new high-quality study published, or both) and the threshold at which the conclusions are updated.
- **Network meta-analysis.** Eligibility must specify the network connectivity assumption, the transitivity assumption, and the planned consistency assessment. Surface these in the synthesis section.
- **Diagnostic-accuracy review.** Eligibility includes the reference standard; extraction includes 2x2 tables; synthesis uses bivariate or hierarchical models; risk of bias uses a tool designed for diagnostic studies.
- **Prognostic-model review.** Eligibility addresses model development vs. validation; extraction captures predictors, outcomes, and discrimination/calibration metrics; risk of bias uses a tool tailored to prognostic studies.
- **Qualitative or mixed-methods review.** Eligibility addresses study designs that include qualitative data; synthesis uses a thematic or framework method; risk of bias uses an instrument designed for qualitative studies.
- **Conflict-laden topic.** If a reviewer has financial ties to one intervention, exclude them from screening and extraction for that comparison and document the exclusion.
- **Insufficient seed set.** If the team cannot name even three known-relevant articles, the question may be too novel for a systematic review; recommend a scoping review first.

## Outputs

- `protocol_markdown` — Complete protocol document ready for internal review and registration.
- `search_strategy_blocks` — Per-database search strings with line-by-line logic and translation notes; suitable for an appendix.
- `open_questions` — Items the clinical lead must decide before registration. Each item names the affected section and a recommended default.

## Examples

### Worked example (abbreviated)

Input:

> Topic: SGLT2 inhibitors in adults with heart failure with preserved ejection fraction (HFpEF) without diabetes. Existing reviews predate the recent dedicated HFpEF trials. We want to inform a guideline update due in nine months. Team: two clinical reviewers, one methodologist, statistical support available. Time window: trials reported from 2010 onward. Languages: English and Spanish.

Expected protocol structure (abbreviated):

```
Title: SGLT2 inhibitors versus placebo in adults with HFpEF without diabetes: a systematic review and meta-analysis

Structured question:
  Population: adults with HFpEF (LVEF >= 50%) without diabetes; outpatient and post-discharge settings
  Intervention: any SGLT2 inhibitor at approved doses
  Comparator: placebo
  Outcomes (critical): composite cardiovascular death + HF hospitalization; all-cause mortality; serious adverse events
  Outcomes (important): KCCQ change at 12 months; eGFR slope; volume-related adverse events
  Study designs: parallel-group randomized trials with >= 12 weeks follow-up

Eligibility:
  Include: trials from 2010 onward; adults; HFpEF as inclusion criterion; placebo control; outcomes measured
  Exclude: trials limited to diabetic populations; trials of < 12 weeks follow-up; trials reported only as abstracts without enough data to extract

Information sources:
  MEDLINE (Ovid), Embase (Elsevier), CENTRAL, ClinicalTrials.gov, WHO ICTRP, hand-search of one guideline society's congress abstracts

Search strategy:
  Concept block A: heart failure, HFpEF, preserved ejection fraction, diastolic heart failure (MeSH + free text)
  Concept block B: SGLT2 inhibitors as a class + each generic name
  Concept block C: randomized trial filter (validated)
  Combined A AND B AND C; date 2010-present; English/Spanish

Selection: dual independent screening at title-abstract and full-text; third-reviewer adjudication;
  pilot of 100 records before independent screening
Extraction: pre-piloted form; dual extraction for outcome data
Risk of bias: domain-based tool for randomized trials, dual rating, calibration set
Synthesis:
  Primary: random-effects meta-analysis for the composite cardiovascular outcome using risk ratio
  Subgroups (pre-specified): by age band, by baseline eGFR, by baseline natriuretic peptide
  Sensitivity: excluding studies at high risk of bias in the main outcome domain
  Small-study effects: funnel plot if >= 10 studies, with an explicit caution about test power
Certainty-of-evidence: per outcome, five-consideration rating
Reporting: standard reporting checklist for systematic reviews with meta-analyses; protocol pre-registered
```

`search_strategy_blocks` example (MEDLINE/Ovid, abbreviated):

```
1  exp Heart Failure/
2  (HFpEF or "heart failure with preserved" or "diastolic heart failure").ti,ab,kw.
3  1 or 2
4  exp Sodium-Glucose Transporter 2 Inhibitors/
5  (SGLT2 or "sodium-glucose cotransporter 2" or empagliflozin or dapagliflozin or
   canagliflozin or ertugliflozin or sotagliflozin).ti,ab,kw.
6  4 or 5
7  randomized controlled trial.pt.
8  controlled clinical trial.pt.
9  randomi?ed.ti,ab.
10 placebo.ti,ab.
11 7 or 8 or 9 or 10
12 3 and 6 and 11
13 limit 12 to yr="2010 -Current"
14 limit 13 to (english or spanish)
```

`open_questions` example output:

```
- Define HFpEF cutoff precisely (LVEF >= 50% vs. >= 45%); both definitions exist in trials. Decision affects eligibility.
- Decide a-priori threshold for adding network meta-analysis if multiple SGLT2 inhibitors are pooled separately.
- Confirm whether congress abstracts with full data tables are eligible or excluded; current draft excludes.
- Identify the seed set of 3-5 known-relevant trials and run the search against it before freezing the strategy.
- Confirm reviewer conflicts of interest; one reviewer has a research grant from an SGLT2 manufacturer.
```

## Limitations

- The protocol records intent; the value depends on the team executing it faithfully. Deviations not logged become hidden flexibility.
- Search strategies are starting points. A qualified information specialist should review and refine the per-database translations before the search is run.
- The skill does not run the search. It produces strings ready to paste into the database interface.
- The skill assumes a clinical question with patient-important outcomes. Bench-science questions need a different framing.
- Quantitative synthesis decisions are pre-specified at the protocol stage but may need revisiting once the included-studies set is known; the protocol-deviation process is the channel for that.
- The skill does not replace pre-registration; it produces the document that gets registered. Registration must be completed in the chosen registry by the team.

## Sources reviewed

- https://github.com/prisma-flowdiagram/PRISMA2020
- https://github.com/neurostuff/PyMARE
- https://github.com/neurostuff/NiMARE
- https://github.com/mcguinlu/robvis
- https://github.com/asreview/asreview
- https://www.prisma-statement.org/prisma-2020-flow-diagram
- https://www.equator-network.org/
- https://training.cochrane.org/handbook
