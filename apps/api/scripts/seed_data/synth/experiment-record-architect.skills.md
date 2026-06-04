---
id: skillsgit-curated/experiment-record-architect
version: 0.1.0
name: Experiment Record Architect
description: Design a complete experiment-record template covering objective, hypothesis, materials, methods, observations, results, deviations, conclusions, raw-data linkage, and signature blocks.
authors:
  - name: Wave-3 Synthesis Agent
    handle: synth-bio
    role: author
category: biotech
tags:
  - niche:lab-notebook-discipline
  - eln
  - experiment-record
  - reproducibility
  - glp
  - data-integrity
  - alcoa
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
  - experiment record
  - lab notebook entry
  - ELN template
  - electronic lab notebook
  - experimental record template
  - GLP record
  - ALCOA
  - witness signature
example_invocations:
  - "Design an experiment-record template for a Western blot."
  - "Build an ELN entry skeleton for a 96-well dose-response assay."
  - "Give me a notebook page structure for a tissue-culture passage experiment with raw-data linkage."
inputs:
  - name: experiment_type
    type: text
    required: true
    description: Short description of the experiment (assay, technique, biological system).
  - name: regulatory_context
    type: choice
    required: false
    description: Documentation tier expected.
    choices:
      - academic-discovery
      - internal-rd
      - glp-aligned
      - gxp-claim
  - name: data_modalities
    type: text
    required: false
    description: What raw-data files will be produced (e.g. plate-reader CSV, gel image TIFF, FCS, microscope ND2).
outputs:
  - name: experiment_record_template
    type: markdown
    description: Sectioned template ready to fill in, with field-level prompts, ALCOA-aligned discipline notes, and a signature block.
changelog:
  - version: 0.1.0
    date: 2026-05-14
    notes: Initial synthesis. Generic ELN-entry structure aligned with widely published ALCOA/ALCOA+ data-integrity conventions; no proprietary text reused.
---

# Experiment Record Architect

> **Mandatory disclaimer.** This skill produces methodology guidance for lab
> documentation practices. Regulated environments (GLP, GMP, FDA 21 CFR
> Part 11) impose specific record-keeping and electronic-signature
> requirements that this skill describes generically; compliance for any
> regulated workflow must be reviewed by qualified Quality and Regulatory
> staff.

## When to use

Use this skill when the user needs the **structure of an experiment
record** — a notebook page, an ELN entry, or a paper template they will
fill in by hand or paste into their notebook system. Typical asks:

- "What sections should my lab notebook entry have for X experiment?"
- "Design an ELN template for a new assay."
- "Build a reproducible experiment-record skeleton."
- "I need a notebook page that captures everything an auditor would look
  for."

Do **not** use this skill to:

- generate a finalized experimental record that will be relied upon as a
  legal or regulatory document (those records are authored
  contemporaneously by the scientist performing the work);
- produce GxP-compliant electronic signatures (those require a validated
  system, not generated text);
- substitute for a site SOP that prescribes the local record format —
  always defer to the SOP if one exists.

## How to apply

Produce a single markdown template with the **eleven fixed sections
below**. Every section has *field prompts* — short questions that tell the
scientist what to write — and *discipline notes* that explain why the
field exists. Do not invent values; the template is empty by design.

### Section 1 — Header

Field prompts:

- Notebook owner (name + handle/ORCID).
- Notebook ID and entry number (e.g. `LN-2026-014 / p.37`).
- Project / sub-project code.
- Experiment title (concise, scannable; not the hypothesis).
- Date started (YYYY-MM-DD, local timezone — be explicit).
- Linked previous entries (preceding experiment, training run, or
  procedure version).

Discipline note: **Attributable** and **Contemporaneous** data-integrity
principles require that every record name its author and its origin
moment. The header is the place that anchors them.

### Section 2 — Objective and hypothesis

Field prompts:

- Objective: one sentence — what question this single experiment will
  answer.
- Hypothesis: predictive form ("If X, then Y because Z"), with the
  measurable variable identified.
- Decision criterion: what observation would falsify the hypothesis (a
  specific threshold, fold-change, or qualitative outcome).
- Scope boundary: explicit statement of what this experiment will *not*
  conclude.

Discipline note: An experiment without a falsifiable criterion captured
*before* it runs is hard to audit and easy to motivated-reason after
the fact. Capturing the criterion here protects against that.

### Section 3 — Materials

For each material, a row with:

- Name (as on label).
- Vendor / source.
- Catalogue or part number.
- Lot or batch number (this is the ALCOA "Original" anchor).
- Storage condition and shelf-life date.
- Internal inventory ID (links to inventory system / freezer location).
- Quantity used (with units).

Include a sub-table for cells / strains / organisms with passage number
or generation, and a sub-table for plasmids / constructs with insert
identity and verification status (sequenced? gel-verified? date).

Discipline note: A reviewer should be able to reconstruct exactly which
tube of reagent was on the bench. Generic vendor names without lot
numbers fail this test.

### Section 4 — Equipment

For each instrument, capture:

- Instrument name (common name) and asset ID (institutional tag).
- Make / model.
- Software version (if it has one).
- Last calibration / qualification date.
- Configuration used (objective, filter set, gain, temperature
  setpoint — whatever is variable).
- Maintenance state at use (any open service issue, last cleaning, etc.).

Discipline note: Equipment IDs are the most common audit gap. The
template forces the field so it cannot be skipped silently.

### Section 5 — Method

Reference the **base protocol** by ID and version (`PROTO-WB-007 v2.3`).
Then capture only the **deltas** from base protocol — do not re-paste the
full method. Deltas to capture:

- Step variation (extended incubation, different temperature, alternate
  buffer).
- Substitution (different antibody clone, different blocking reagent).
- Skipped step (with reason).
- Added step (with reason).

If there is no base protocol, mark the entry as a **protocol-development
record** and write the full method inline, then capture the as-run
version as a separate protocol after the experiment concludes.

Discipline note: This separation prevents two failure modes — *silent
drift* (where the protocol on file no longer matches what people do) and
*re-paste rot* (where the inline method diverges from the canonical
protocol across many entries).

### Section 6 — Observations (raw, contemporaneous)

This is the **append-only, timestamped** section. Each line:

- Timestamp (HH:MM, local).
- Action or observation.
- Free-text remark.

Rules:

- No retroactive edits. Errors are struck through with a single line,
  initialled and dated; the original text remains readable.
- Tape-ins or attachments (printouts, photos) get a unique ID and are
  referenced here by ID, then physically taped (paper) or hash-linked
  (electronic) into the appropriate appendix.
- Deviations from the planned method are flagged here in-line as
  **DEV-n** and detailed in Section 9.

Discipline note: This section is the legal/scientific heart of the
record. It is what an auditor reads first. Treat it as immutable.

### Section 7 — Raw-data linkage

For every file or instrument export generated, capture:

- File name (as written by the instrument).
- File path or repository link (absolute path on instrument PC, plus
  archival path).
- Acquisition timestamp (instrument clock).
- File size and (recommended) SHA-256 hash of the raw file.
- Instrument that produced it (links to Section 4).
- Brief description ("plate 1, read 1, OD600").

Hash discipline: Computing a SHA-256 once and recording it in the
notebook is a low-cost ALCOA+ "Enduring" anchor — any later modification
of the file is provably detectable.

Discipline note: A record that says "see plate-reader output" without a
path, filename, and hash is unverifiable.

### Section 8 — Results and interpretation

- Processed-data summary: tables, plots, or numerical results.
- Analysis-code reference (commit hash + repo URL, or analysis-notebook
  ID + version).
- Analysis input → output map: which raw files (Section 7) produced this
  processed output, via which analysis version.
- Interpretation: what the data say about the hypothesis in Section 2,
  using the decision criterion stated there.
- Confidence and qualifications (n, replicates, biological vs.
  technical, known caveats).

Distinguish clearly between **what was observed** (Section 6, raw) and
**what is concluded** (Section 8, interpreted). Do not move conclusions
into the observation section.

### Section 9 — Deviations and issues

For each deviation tagged in Section 6:

- Tag (DEV-1, DEV-2, …).
- Description (what happened vs. what was planned).
- Impact assessment (on objective, on data interpretability).
- Action taken (continue, repeat, mark sample as suspect, discard).
- Required follow-up (root-cause, SOP update, retraining).

If no deviations: write *"No deviations recorded."* Do not leave the
section blank.

Discipline note: A record with no deviations across many entries is, in
the auditor's mind, suspicious. The honest record captures the small
ones too.

### Section 10 — Conclusions and next steps

- Conclusion stated against the Section 2 hypothesis: supported, refuted,
  inconclusive, with explicit reference to the decision criterion.
- Implications for the next experiment.
- Specific next-experiment hooks (link to the planned next entry by ID
  if available).
- Cross-reference to project plan or milestone.

Keep this section short. If it grows beyond a few paragraphs, the
project plan probably needs a separate review record.

### Section 11 — Signatures

- **Author**: signed and dated by the scientist who performed the work
  (electronic signature where the system supports it; ink on paper
  otherwise).
- **Witness / reviewer**: signed and dated by an independent colleague who
  has read the entry, examined the linked raw data, and confirms the
  record is complete and intelligible. The witness is not certifying the
  *scientific conclusion* — only the *record*.
- Date of witnessing must be after the date of authoring.
- For regulated work, the signature block must conform to the local
  electronic-signature SOP (21 CFR Part 11 in FDA-regulated contexts);
  this template names the field but does not produce a compliant
  signature.

Discipline note: Witnessing is the single highest-leverage practice for
notebook reliability. It catches missing fields, ambiguous notation,
and untraceable raw data before they harden into the historical record.

## Style rules

1. Past tense for what happened; future or imperative for what is planned.
2. ISO-8601 dates and 24-hour times throughout.
3. Units on every number, with explicit precision (`12.5 mL`, not `12.5`).
4. Reagent and equipment IDs are quoted verbatim from labels.
5. Never overwrite or erase — strike-through with initials and date.
6. Never antedate or postdate a contemporaneous entry. If a record is
   written later from notes, mark it `RECONSTRUCTED FROM NOTES` and
   include the notes as an appendix.
7. Acronyms expanded on first use within the entry.
8. No placeholder text in the final filled record. Empty fields read
   *"Not applicable — reason: …"* with the reason given.

## Inputs

- `experiment_type` — describes the experiment so the template can
  surface the right field prompts (e.g. flow-cytometry entries should
  prompt for compensation matrix; sequencing entries should prompt for
  library prep kit lot).
- `regulatory_context` — controls which discipline notes are emphasised
  (academic vs. GLP-aligned vs. GxP-claim).
- `data_modalities` — drives the Section 7 raw-data prompts (which file
  types, which hashing recommendation).

## Outputs

A single markdown template with the eleven sections above, fillable in
place. The footer must contain:

> *This template documents methodology only. Filled records produced
> using this template are not regulatory or audit deliverables until
> they have been reviewed against the site SOP, signed by the author,
> and witnessed per the local notebook policy. Compliance for regulated
> workflows must be confirmed by qualified Quality and Regulatory
> staff.*

## Examples

> **User**: "Design an experiment-record template for a Western blot in
> an academic discovery context. Data modalities: ChemiDoc image
> (.scn), densitometry CSV."
>
> **Assistant**: produces the eleven-section template; Section 3 prompts
> for primary and secondary antibody lots and dilutions; Section 4
> prompts for ChemiDoc asset ID, exposure setting, and software version;
> Section 5 references the base WB protocol and asks for deltas; Section
> 7 prompts for `.scn` filename, archival path, instrument acquisition
> time, and SHA-256; Section 11 contains author and witness signature
> blocks but does not claim 21 CFR Part 11 compliance.

## Limitations

This skill **does not**:

- author a filled experiment record (the scientist must write the
  contemporaneous observations themselves);
- produce a 21 CFR Part 11 compliant electronic-signature block (that
  requires a validated ELN system);
- replace a site SOP — when an SOP prescribes the format, the SOP wins;
- assess whether a particular experiment is sufficiently powered or
  controlled — that is a study-design question;
- coach on specific GLP claims — defer to QA for those.

## Sources

This methodology is synthesised from publicly available, URL-only
references. The open-source code ecosystem for ELN platforms under
permissive licences is **sparse** — the most widely adopted ELNs
(eLabFTW, SciNote, Chemotion, rspace-os) are AGPL and have been
deliberately **excluded** from this synthesis because the niche brief
restricts sources to MIT / Apache / BSD / ISC / Unlicense / CC0. The
permissive-licensed projects below provided structural inspiration for
notebook layout and entry hygiene; the regulatory-discipline content
derives from generic, widely published ALCOA / ALCOA+ guidance.

- https://github.com/tlnagy/jekyll-lab-notebook
- https://github.com/Inventree/InvenTree
- https://github.com/greenelab/lab-website-template
- https://github.com/benmarwick/rrtools
- https://github.com/jupyter-guide/jupyter-guide
- https://github.com/drivendataorg/cookiecutter-data-science
