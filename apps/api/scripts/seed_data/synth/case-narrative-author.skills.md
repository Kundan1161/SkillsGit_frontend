---
id: skillsgit-curated/case-narrative-author
version: 0.1.0
name: ICSR Case Narrative Author
description: Draft a structured individual case safety report narrative covering demographics, treatment, event, dechallenge/rechallenge, causality, and action taken.
authors:
  - name: Wave-3 Synthesis Agent
    handle: synth-pv
    role: author
category: healthcare
tags:
  - niche:pharmacovigilance
  - icsr
  - case-narrative
  - adverse-event
  - causality
  - meddra
  - drug-safety
license_type: free
ai:
  required_models:
    - claude-opus-4-7
  compatible_models:
    - claude-sonnet-4-6
    - gpt-4o
  min_context_tokens: 30000
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - case narrative
  - ICSR
  - individual case safety report
  - adverse event narrative
  - CIOMS narrative
  - dechallenge
  - rechallenge
  - causality assessment
example_invocations:
  - "Draft a case narrative from these de-identified notes about a patient who developed rash on Day 7 of treatment."
  - "Help me structure a training-only ICSR narrative for a hepatic injury case."
  - "Outline the dechallenge/rechallenge and causality paragraphs for a sample case."
inputs:
  - name: case_facts
    type: text
    required: true
    description: De-identified, training-only case facts (demographics in bands, medical history, drug therapy, event timing, lab values, dechallenge, outcome).
  - name: source_type
    type: choice
    required: false
    description: Origin of the report.
    choices:
      - spontaneous-hcp
      - spontaneous-consumer
      - clinical-trial
      - literature
      - regulatory-authority
  - name: causality_framework
    type: choice
    required: false
    description: Which assessment framework to apply.
    choices:
      - WHO-UMC
      - Naranjo
      - both
outputs:
  - name: case_narrative_draft
    type: markdown
    description: Sectioned ICSR-style narrative draft (training/planning use only), ready for review by a qualified PV professional.
changelog:
  - version: 0.1.0
    date: 2026-05-14
    notes: Initial synthesis. Generic ICSR-narrative structure aligned with widely published CIOMS and ICH E2B(R3) conventions; no proprietary text reused.
---

# ICSR Case Narrative Author

> **Mandatory disclaimer.** This skill produces methodology guidance for
> pharmacovigilance workflows. Outputs are not regulatory safety reports and
> have no role in real-time individual case safety reporting (which has
> statutory deadlines requiring qualified PV staff). Use only as a
> planning/training aid; every real PV decision must be authorized by a
> qualified PV professional and signed off by the EU-QPPV or equivalent.

## When to use

Use this skill when the user wants help **structuring** an individual case
safety report (ICSR) narrative — for training, internal review prep, SOP
authoring, mock-audit exercises, or learning the conventional shape of a
CIOMS-style narrative.

Do **not** use this skill to:

- generate a narrative that will be submitted to a regulator;
- produce text for E2B(R3) gateway transmission;
- meet a 15-day expedited deadline (those reports must be written and
  released by qualified PV staff against your safety-database SOP);
- handle real patient-identifiable data — only de-identified, training
  inputs are appropriate.

## How to apply

Follow this fixed seven-section structure. Each section is mandatory; if the
case facts are silent, mark the section *"Information not provided in source
documents"* rather than inventing detail. Never fabricate lab values, dates,
batch numbers, or causality outcomes.

### Section 1 — Patient and reporter

- Demographics in **bands**, never exact values: age band (e.g. 60–69),
  sex, country.
- Relevant medical history (chronic conditions, allergies).
- Concomitant medications at event onset, with indication.
- Reporter type (HCP, consumer, study investigator, literature) and
  qualification when known.
- Source of report (spontaneous, solicited, study, literature citation).

Write this section in plain past tense, third person, no patient
identifiers.

### Section 2 — Suspect product(s) and treatment

For each suspect product:

- Active substance and product name as reported.
- Indication for use **in this patient**.
- Dose, route, frequency, formulation.
- Start date (or relative day, e.g. "Day 0"), stop date.
- Batch / lot number if provided.
- Time-to-onset from start of suspect product to event onset (calendar days
  or hours; use whichever the source provides).

Include concomitant products that are **not** suspect in Section 1, and
distinguish them clearly here.

### Section 3 — Event description

- Preferred MedDRA term (PT) for each event, plus the verbatim reporter
  term in quotes.
- Date or relative day of onset.
- Seriousness criteria met (any of: death, life-threatening,
  hospitalisation / prolongation, persistent or significant
  disability/incapacity, congenital anomaly, other medically important).
- Severity in clinical terms when given (mild / moderate / severe — distinct
  from "serious").
- Clinical course in chronological order: onset → progression → peak →
  resolution.
- Supporting investigations: relevant labs (values with units and reference
  ranges *only if provided in source*), imaging, biopsy, ECG.

### Section 4 — Dechallenge and rechallenge

Dechallenge — what happened when the suspect product was withdrawn or dose
reduced:

- Action taken with suspect drug (withdrawn, dose reduced, dose increased,
  unchanged, unknown).
- Outcome after action: recovered, recovering, not recovered, recovered with
  sequelae, fatal, unknown.
- Time from action to outcome change.

Rechallenge — only if the source documents a deliberate or accidental
re-exposure:

- Re-exposure date and dose.
- Recurrence of event (yes / no / unknown), with time-to-recurrence.

If no rechallenge occurred, state *"Rechallenge: not performed."* Do not
speculate about what would have happened.

### Section 5 — Relevant differential and confounders

- Alternative aetiologies considered (concomitant disease, other drugs,
  diet, environmental exposure).
- Why each is or is not supported by the case facts.
- Whether the event is consistent with the underlying indication or
  comorbidity ("disease progression vs. drug-induced").
- Confounding by indication, channeling, or protopathic bias if relevant.

### Section 6 — Causality assessment

Apply the framework chosen in the `causality_framework` input. Show your
reasoning step-by-step; never assert a category without justification.

**WHO-UMC categories**: certain, probable/likely, possible, unlikely,
conditional/unclassified, unassessable/unclassifiable. Map the case to one
category and quote the criteria met.

**Naranjo algorithm** (ten items, score):
- ≥ 9: definite
- 5–8: probable
- 1–4: possible
- ≤ 0: doubtful

Always state separately:
- Reporter causality (as stated by the reporter).
- Company / investigator causality (per your training-time SOP).
- Any disagreement and why.

### Section 7 — Action taken and outcome

- Action taken with the suspect product (already captured in Section 4 —
  restate concisely).
- Treatment given for the event itself.
- Final outcome at the latest follow-up.
- Date of last follow-up and whether further follow-up is planned.
- Note any required regulatory action (e.g. label review, RMP update,
  signal review trigger) — **flag only**, do not initiate.

## Style rules

1. Past tense, third person, no quotation of patient identifiers.
2. Use *patient* (singular) — never *the patient's name* or initials.
3. Use ISO-style relative timing ("Day 0", "Day 7") unless absolute dates
   were provided in the source.
4. Quote the reporter's verbatim event description in quotation marks
   exactly once, alongside the MedDRA PT.
5. Numerical values: include units (mg, mg/kg, mmol/L) and reference range
   when source provides it.
6. No marketing language. No adjectives like *unfortunate* or *severe* unless
   the source uses them.
7. Never fabricate batch numbers, lot numbers, dates, lab values, or
   reporter contact details.
8. If a section is unsupported by the source, write *"Information not
   provided in source documents."*

## Inputs

- `case_facts` — de-identified case description.
- `source_type` — origin of report (optional).
- `causality_framework` — WHO-UMC / Naranjo / both (optional, default
  WHO-UMC).

## Outputs

A seven-section markdown narrative draft. The footer must contain:

> *This narrative is a training/planning draft. It must be reviewed,
> edited, and approved by a qualified pharmacovigilance professional, and
> the qualified person responsible for pharmacovigilance (EU-QPPV or
> equivalent) retains final responsibility, before any use in a regulated
> process or transmission to a regulator.*

## Examples

> **User**: "Draft a training-only narrative. Patient 60s, female, EU.
> Started medication X 50 mg daily for hypertension on Day 0. On Day 12
> developed maculopapular rash on torso, no fever. Drug stopped Day 12;
> rash resolved by Day 19. No rechallenge. HCP-reported. Concomitant
> simvastatin and metformin."
>
> **Assistant**: produces seven sections, MedDRA PT = "Rash maculo-papular",
> seriousness = non-serious, time-to-onset = 12 days, positive dechallenge,
> WHO-UMC = *probable* with justification, action taken = drug withdrawn,
> outcome = recovered, follow-up = none planned.

## Worked micro-example

A training case fact pattern: *"60s, female, EU; metformin 1000 mg BID for
T2DM started 3 years ago; atorvastatin 40 mg started Day -180; on Day 0
started co-trimoxazole for UTI; Day 4 facial swelling, urticaria, dyspnoea
requiring ED visit; co-trimoxazole stopped Day 4; IV antihistamine and
corticosteroid given; full resolution Day 5; no rechallenge."*

The expected narrative shape:

- **Section 1.** Patient: 60s, female, EU. History: T2DM. Concomitants:
  metformin, atorvastatin (with indications). Reporter: HCP.
- **Section 2.** Suspect: co-trimoxazole (active substances stated),
  oral, started Day 0 for UTI. Time-to-onset 4 days.
- **Section 3.** Events: facial swelling (MedDRA PT *Face oedema*),
  urticaria (PT *Urticaria*), dyspnoea (PT *Dyspnoea*); seriousness met
  (medically important / ED visit); clinical course described.
- **Section 4.** Dechallenge: co-trimoxazole stopped Day 4 → events
  resolved Day 5 → **positive dechallenge**. Rechallenge: not performed.
- **Section 5.** Differential: not metformin (years of stable use); not
  atorvastatin (180 days of stable use); timing strongly supports co-
  trimoxazole.
- **Section 6.** WHO-UMC: **probable/likely** (reasonable time
  relationship, known reaction to product, dechallenge positive, no
  rechallenge, alternative cause unlikely). If Naranjo also requested,
  score ~6–7 (probable).
- **Section 7.** Action: drug withdrawn; symptomatic treatment given;
  outcome recovered. Follow-up: none planned. Regulatory flag: event
  is already labelled — close case.

## Common mistakes to avoid

1. **Restating the patient verbatim from a foreign report without de-
   identification.** Reject and re-request de-identified facts.
2. **Inventing a batch / lot number.** If the source does not provide
   one, mark *unknown*.
3. **Implying causality through adjectives** ("clearly caused by")
   instead of applying the chosen framework.
4. **Conflating seriousness and severity.** *Serious* is a regulatory
   criterion; *severe* is a clinical descriptor. They are independent.
5. **Forgetting concomitants.** Concomitant medications must appear in
   Section 1 with indication; their omission is a frequent QA finding.
6. **Skipping the dechallenge outcome timing.** Time-from-stop to
   resolution is the strongest causality clue available; never omit it
   when the source provides it.
7. **Auto-coding MedDRA.** Suggest a likely PT but state explicitly that
   final coding is a qualified-coder task.
8. **Drafting follow-up questions inside the narrative.** Follow-up
   queries belong in the case file, not in the narrative body.

## Required follow-up checklist

Before any human reviewer signs off the narrative, confirm:

- All seven sections are present.
- No patient identifiers anywhere in the text.
- Every numeric value has a unit and a source.
- Every MedDRA PT suggestion is flagged "candidate term — confirm with
  coder".
- Both reporter and company causality are stated separately.
- The footer disclaimer is intact and unedited.

## Limitations

This skill **does not**:

- code MedDRA terms (it suggests likely PT but coding is a qualified-coder
  task);
- generate E2B(R3) XML;
- determine seriousness — it transcribes what the source states and flags
  if multiple criteria appear met;
- substitute for the company case-processing SOP;
- handle identifiable patient data — refuse and ask for de-identified
  input if names, dates of birth, or contact details are provided.

## Differences across source types

The base structure is constant; the emphasis shifts with `source_type`:

- **spontaneous-hcp.** Emphasise reporter qualification, completeness of
  clinical detail, and any HCP-stated causality.
- **spontaneous-consumer.** Note that medical history is often less
  reliable; flag missing labs explicitly; consider follow-up by the
  company to a treating HCP (recommend, do not perform).
- **clinical-trial.** Anchor to study ID, treatment arm (blinded or
  unblinded as the source allows), protocol-defined adverse-event
  collection windows, and relatedness as the investigator stated.
- **literature.** Cite the literature reference; flag whether the case is
  identifiable enough to require reporting under the relevant jurisdiction
  rules.
- **regulatory-authority.** Mention the originating authority and any
  request for follow-up.

## How this skill differs from a regulatory narrative writer

A regulatory narrative writer is a qualified human who knows the
company's SOPs, the safety database conventions, and the controlled
vocabulary in use. This skill produces a **shape** the writer can fill
in and adapt. The skill does not:

- access the safety database;
- assign a case number;
- determine 15-day expedited status;
- finalise MedDRA coding;
- approve transmission.

## Sources

This methodology is synthesised from publicly available, URL-only references.
The open-source code ecosystem for ICSR narrative authoring is essentially
nonexistent under permissive licences — disclosed honestly. The structural
conventions follow widely published CIOMS / ICH-E2B norms.

- https://github.com/InfOmics/TEDAR
- https://github.com/WangLabCSU/faers
- https://github.com/ngiangre/openFDA_drug_event_parsing
- https://www.who.int/publications/m/item/WHO-causality-assessment
- https://www.ema.europa.eu/en/human-regulatory-overview/post-authorisation/pharmacovigilance-post-authorisation/periodic-safety-update-reports-psurs
