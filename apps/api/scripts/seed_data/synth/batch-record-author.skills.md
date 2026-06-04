---
id: skillsgit-curated/batch-record-author
version: 0.1.0
name: Batch Record Author
description: Produce a batch-production record skeleton for a lab process covering materials, equipment IDs, in-process checks, deviations, witness signatures, and attached-data linkage.
authors:
  - name: Wave-3 Synthesis Agent
    handle: synth-bio
    role: author
category: biotech
tags:
  - niche:lab-notebook-discipline
  - batch-record
  - production-record
  - in-process-control
  - deviations
  - witness-signature
  - data-linkage
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
  - batch record
  - batch production record
  - lab process record
  - in-process check
  - executed batch record
  - production batch
  - witness sign-off
example_invocations:
  - "Build a batch-record template for a 500 mL E. coli plasmid prep."
  - "Draft a lab batch record for a small-scale buffer preparation."
  - "I need a batch-production record structure for a research-scale protein purification."
inputs:
  - name: process_description
    type: text
    required: true
    description: One- or two-sentence description of the lab process being recorded (scale, product, intended use).
  - name: process_type
    type: choice
    required: false
    description: Category of process.
    choices:
      - reagent-preparation
      - cell-culture-passage
      - protein-purification
      - nucleic-acid-prep
      - small-molecule-synthesis
      - formulation
      - other
  - name: regulatory_context
    type: choice
    required: false
    description: Documentation tier expected.
    choices:
      - research-only
      - glp-aligned
      - gmp-claim
outputs:
  - name: batch_record_template
    type: markdown
    description: Sectioned, pre-printed batch-record skeleton with materials table, step-by-step execution lines, in-process check tables, deviation log, attached-data inventory, and signature block.
changelog:
  - version: 0.1.0
    date: 2026-05-14
    notes: Initial synthesis. Generic batch-record structure aligned with widely published BMR/EBR conventions and ALCOA+ data-integrity principles; no proprietary text reused.
---

# Batch Record Author

> **Mandatory disclaimer.** This skill produces methodology guidance for
> lab documentation practices. Regulated environments (GLP, GMP, FDA 21
> CFR Part 11) impose specific record-keeping and electronic-signature
> requirements that this skill describes generically; compliance for any
> regulated workflow must be reviewed by qualified Quality and Regulatory
> staff.

## When to use

Use this skill when the user needs a **batch-record skeleton** — a
pre-printed, fill-in document that someone will execute step-by-step
while running a lab process and producing a discrete output (a lot, a
batch, a preparation). Typical asks:

- "Build me a batch-record template for X process."
- "I need a fill-in form for a buffer preparation."
- "Design a batch sheet for our research-scale plasmid prep so we can
  trace every lot."
- "What should a lab batch record contain?"

This skill is for the **research and pre-clinical** end of the spectrum.
It deliberately uses the term "batch record" rather than "executed batch
record" (EBR) or "manufacturing batch record" (MBR), which are GMP terms
of art with regulator-specific format expectations.

Do **not** use this skill to:

- author a GMP-compliant master batch record (those derive from a
  validated master template controlled by your QA system);
- substitute for site SOPs or quality-system documents;
- generate executed records — the operator must complete the form
  contemporaneously while running the process.

## How to apply

Produce a single markdown template with the **ten fixed sections below**.
The template is designed to be printed (or pre-rendered in an electronic
batch-record system) and **completed by hand or with electronic
signature, line by line, during execution**.

### Section 1 — Identification block

A header table that appears on every page:

- Process name and version (`PROC-BUF-TBS-T v2.1`).
- Batch / lot number (assigned per the batch-numbering SOP, or
  pre-assigned and printed on the record).
- Scale (volume, mass, or count of units).
- Intended use (research aliquots, in-house assay, supply to other
  project — never claim therapeutic use here).
- Date of execution (start and finish; YYYY-MM-DD).
- Operator initials and reviewer initials boxes.
- Page X of Y.

Discipline note: The identification block must appear on every page so
loose pages remain attributable to the correct batch.

### Section 2 — Pre-execution checklist

Initial-and-date items that must be true *before* execution begins:

- All raw materials at the bench, with the lot numbers listed in
  Section 4 matching the labels.
- Equipment confirmed in calibration (or labelled `OOC` and excluded).
- Cleaning status of equipment verified (links to last cleaning record).
- Workspace cleared of materials from the previous batch (line clearance).
- Operator trained and signed-off on the current process version.
- Reviewer assigned for in-process verification.

Each item has an initial box and a timestamp box. The operator does not
proceed to Section 6 until every item is initialled.

Discipline note: Pre-execution checks catch the failure modes that
contaminate or cross-mix batches. They are also the easiest fields to
skip — pre-printing them forces the verification.

### Section 3 — Equipment in use

A pre-printed table:

| Equipment role | Asset ID | Make / model | Calibration valid through | Operator initial |
| --- | --- | --- | --- | --- |
| Analytical balance | (fill) | (fill) | YYYY-MM-DD | (init) |
| pH meter | … | … | … | … |
| Magnetic stirrer | … | … | … | … |
| Autoclave | … | … | … | … |

Any equipment not in calibration is listed as `OOC — NOT USED` and the
operator initials that line as confirmation it was excluded.

Discipline note: Asset IDs (institutional tags) are the unambiguous
anchor. Naming "the balance in the prep room" is not sufficient.

### Section 4 — Materials issued

A pre-printed table where the row count matches the bill of materials
for the process:

| Material | Vendor | Catalogue | Lot number | Expiry | Quantity required | Quantity dispensed | Issued by | Verified by | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Rules:

- Lot numbers are transcribed from the container label, character by
  character. They are not memorised or abbreviated.
- The *quantity required* is pre-printed from the process master.
- The *quantity dispensed* is recorded after weigh/measure.
- Two initials per row: one for the issuer (who weighed) and one for
  the verifier (who watched and confirmed). This is the **"witness at
  point of use"** pattern.

If a material is exhausted mid-batch and a second container is opened,
add a row for the second container with its own lot/expiry. Never
merge.

Discipline note: This is the single most-audited section of a batch
record. Missing lot numbers or single-signature dispenses are the
most common findings.

### Section 5 — Calculations

Pre-print every calculation in the process with the variables blanked
out:

```
Target final volume:  ______ mL
Target stock conc.:   ______ M
Working conc.:        ______ M
Volume of stock:      (target × final) / stock =  ______ mL
Volume of diluent:    final − stock =  ______ mL
Calculated by: _____  Verified by: _____  Time: _____
```

Rules:

- Every calculation is double-checked (calculator + independent
  recompute) and dual-signed.
- The pre-printed formula is part of the master; the operator does not
  re-derive it on the bench.
- Round only at the documented step; show intermediate values.

Discipline note: Free-form arithmetic on scratch paper is one of the
top sources of batch failure. Pre-printing the formula and dual-signing
the result protects against transcription and reasoning errors.

### Section 6 — Execution (step-by-step)

The body of the record. Each step is pre-printed as a numbered line
with:

- Step number and brief instruction (one sentence; refer to the master
  procedure for full instructions, do **not** copy the procedure body
  in full).
- Critical parameter target with tolerance (e.g. "Stir at 300 ± 50 rpm
  for 30 ± 5 min").
- Field for the recorded value (the actual measurement).
- Pass / fail box if there is a tolerance.
- Operator initial and timestamp.
- Reviewer initial (only for steps designated as **critical** — defined
  by the master).

Example step skeleton:

```
Step 6.04  Add NaCl per Section 4 to the buffer vessel; stir until dissolved.
           Critical parameter:   stir time ≥ 5 min
           Recorded stir time:   ______ min
           Pass / Fail:          [ ] Pass  [ ] Fail (raise DEV-n)
           Operator:  __  Time:  __:__
           Critical-step reviewer (if applicable):  __  Time:  __:__
```

Rules:

- Steps are executed and signed in order.
- A "Pass" requires the recorded value to be within the pre-printed
  tolerance.
- A "Fail" automatically opens a deviation in Section 8.

### Section 7 — In-process checks (IPCs)

Pre-printed table for measurements taken *during* execution that
condition the next step:

| IPC ID | Description | Specification | Result | Pass / Fail | Tested by | Verified by | Time |
| --- | --- | --- | --- | --- | --- | --- | --- |

Typical IPCs for lab-scale work: pH, conductivity, OD600 at induction,
A260/A280 ratio of a nucleic-acid prep, post-elution protein
concentration, sterility-filter integrity check.

Each IPC has a pre-printed specification (target ± tolerance) drawn from
the master procedure. The operator records the result; a separate
reviewer verifies.

### Section 8 — Deviations log

Pre-printed empty table for deviations that arise during execution:

| DEV-ID | Step ref | Description (what was planned vs. what happened) | Immediate action | Disposition (continue / repeat / scrap) | Raised by | Reviewed by | Time |
| --- | --- | --- | --- | --- | --- | --- | --- |

Rules:

- Deviations are tagged in-line in Section 6 or 7 as `DEV-n` and then
  fully described here.
- *Immediate action* is what the operator did at the bench (e.g.
  paused, added more diluent).
- *Disposition* requires a reviewer's signature — the operator alone
  cannot decide to continue after a deviation.
- Every deviation requires a follow-up investigation; the follow-up
  record is referenced by ID here but lives in a separate quality
  document.
- If no deviations: a single line *"No deviations during execution."*
  signed by operator and reviewer.

Discipline note: Honest deviation capture is the single best indicator
of a healthy lab. Records with no deviations across many batches are an
audit red flag.

### Section 9 — Attached data and outputs

For every file or printout produced during the batch:

| Attachment ID | Type | Source instrument | Filename / hash | Archival location | Time | Reviewed by |
| --- | --- | --- | --- | --- | --- | --- |

Typical attachments: pH meter printout, autoclave cycle chart, balance
weight printout, plate-reader CSV, gel image.

Rules:

- Physical printouts are taped to the back of the record and labelled
  with the attachment ID.
- Electronic files are archived to the long-term store; the path *and*
  the SHA-256 are captured.
- The reviewer's initial confirms the attachment was sighted.

Final output of the batch (the product itself):

- Final yield (mass, volume, or count of vials).
- Final QC results (concentration, A260/A280, endotoxin if applicable,
  visual inspection).
- Label text used for the final container, transcribed verbatim.

### Section 10 — Sign-off

Three signatures, each with a printed name, role, signature, and date:

- **Operator** — performed the work and prepared the record. Confirms
  the record is true, complete, and contemporaneous.
- **Independent reviewer** — has read every page, confirmed every
  required initial is present, every calculation is dual-signed, every
  deviation is closed (in this record or referenced to a separate
  investigation), and every attached datum is present. The reviewer is
  not certifying that the batch is *fit for use* — only that the
  record is *complete and intelligible*.
- **Disposition authority** — designates the batch as `Release for
  intended use`, `Quarantine pending follow-up`, or `Reject`. In a
  research context this may be the project lead; in a regulated
  context this role is held by QA.

Signatures must be after the date of the last execution step. For
regulated work, the signature block must conform to the local
electronic-signature SOP (21 CFR Part 11 in FDA-regulated contexts);
this template names the field but does not produce a compliant
signature.

## Style rules

1. ISO-8601 dates and 24-hour times throughout.
2. Initials are two- or three-character monograms attributable to a
   named signatory in Section 10.
3. No blank lines in a completed record — every line is initialled,
   marked `N/A` with a reason, or struck through with single-line strike
   plus initials and date.
4. Units on every measurement, with explicit precision.
5. Lot numbers and asset IDs are transcribed verbatim, not paraphrased.
6. "TBD" and "to be determined" are not allowed in a completed record;
   in a master template they are pre-printed blanks instead.
7. Strike-throughs preserve the original text legibly underneath.
8. Numerical results in IPC and execution tables are recorded *before*
   the pass/fail box is ticked — never the other way around.

## Inputs

- `process_description` — short description of the lab process.
- `process_type` — selects which Section 4 / 5 / 7 prompts apply (e.g.
  protein purification surfaces A280 IPCs; cell culture surfaces
  passage-number tracking).
- `regulatory_context` — research-only vs. GLP-aligned vs. GMP-claim;
  controls the emphasis of discipline notes and the explicit
  GMP-disclaimers.

## Outputs

A single markdown batch-record skeleton with the ten sections above.
The footer must contain:

> *This template documents methodology only. Completed records produced
> using this template are not GMP-compliant batch records and are not
> evidence of GMP manufacture. A GMP batch record derives from a
> validated master controlled by a quality system; compliance for
> regulated workflows must be confirmed by qualified Quality and
> Regulatory staff.*

## Examples

> **User**: "Build a batch-record template for a 500 mL TBS-T buffer
> preparation. Research-only context."
>
> **Assistant**: produces the ten-section template; Section 3 lists
> balance, pH meter, magnetic stirrer; Section 4 has rows for Tris base,
> NaCl, HCl, Tween-20, water, each with lot/expiry/issuer/verifier
> columns; Section 5 pre-prints the molarity calculation and the
> Tween-20 dilution; Section 6 enumerates the dissolve / pH / QS-to-
> volume / filter / aliquot steps; Section 7 captures pH (target 7.4 ±
> 0.1) and conductivity as IPCs; Section 9 captures the pH-meter
> printout as an attachment with SHA-256; the footer includes the
> "research-only, not a GMP record" disclaimer.

## Limitations

This skill **does not**:

- author an executed batch record (the operator must fill it
  contemporaneously);
- produce a GMP master batch record (those require a validated quality
  system and QA control);
- generate 21 CFR Part 11 compliant electronic signatures;
- determine the correct in-process specifications for a process — those
  derive from process development and validation;
- substitute for site SOPs governing batch numbering, cleaning records,
  or release authority.

## Sources

This methodology is synthesised from publicly available, URL-only
references. The open-source code ecosystem for batch-record systems
under permissive licences is **sparse** — the most widely deployed open
ELN/LIMS platforms are AGPL and have been **excluded** from this
synthesis per the niche brief. The permissive-licensed projects below
provided structural inspiration for materials tracking, asset ID
discipline, and form-driven workflows; the regulatory-discipline content
derives from generic, widely published ALCOA / ALCOA+ guidance.

- https://github.com/tlnagy/jekyll-lab-notebook
- https://github.com/Inventree/InvenTree
- https://github.com/benmarwick/rrtools
- https://github.com/jupyter-guide/jupyter-guide
- https://github.com/miguelarbesu/cookiecutter-reproducible-science
- https://github.com/drivendataorg/cookiecutter-data-science
