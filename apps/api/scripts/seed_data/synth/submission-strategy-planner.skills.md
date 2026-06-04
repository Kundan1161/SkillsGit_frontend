---
id: skillsgit-curated/submission-strategy-planner
version: 1.0.0
name: Regulatory Submission Strategy Planner
description: Assess a biotech or medical-device product against FDA, EMA, and ICH pathways, recommend the best regulatory route, and produce a milestone-based submission plan.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: biotech
tags: [niche:regulatory-submission, fda, ema, 510k, ind, ectd, strategy, planning]
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
  - regulatory strategy
  - submission pathway
  - which pathway 510k or de novo
  - ind versus iind
  - pma vs 510k
  - regulatory plan
  - ectd plan
  - fda submission strategy
  - ema submission plan
  - regulatory roadmap
  - pre-submission strategy
  - q-sub planning
example_invocations:
  - "Help me choose between a 510(k), De Novo, and PMA for our continuous glucose monitor accessory."
  - "Draft a milestone plan for an IND submission for a Phase 1 oncology candidate."
  - "Compare the FDA and EMA pathways for our digital therapeutic and recommend which to lead with."
inputs:
  - name: product_description
    type: text
    required: true
    description: A plain-language description of the product, including intended use, target population, mechanism of action or operating principle, and any combination-product aspects (device + drug, device + biologic).
  - name: product_type
    type: choice
    required: true
    description: High-level product class. Drives which pathway tree the agent walks.
    choices: [medical_device, drug_small_molecule, biologic, combination_product, digital_therapeutic, in_vitro_diagnostic, unknown]
  - name: target_regions
    type: text
    required: false
    description: Comma-separated list of regulator regions of interest (e.g. "FDA, EMA, Health Canada"). Defaults to FDA-only if omitted.
  - name: risk_signals
    type: text
    required: false
    description: Known safety, novelty, or technology-risk flags (e.g. "novel mechanism, no predicate, pediatric population, AI/ML-enabled, implantable, life-supporting"). Used to escalate or de-escalate the pathway recommendation.
  - name: known_predicates_or_precedents
    type: text
    required: false
    description: Any known cleared or approved predicate devices, listed drugs, or precedent submissions the sponsor has already identified.
  - name: program_phase
    type: choice
    required: false
    description: Where the program currently sits. Affects what milestones are still in scope.
    choices: [discovery, preclinical, ind_enabling, phase_1, phase_2, phase_3, design_freeze, verification_complete, preparing_filing, unknown]
outputs:
  - name: strategy_report
    type: markdown
    description: Narrative report with the recommended pathway, rationale, alternative pathways considered and rejected, key risks, and a milestone table.
  - name: strategy_json
    type: json
    description: Machine-readable structure — recommended_pathway, alternatives_considered (with rejection reasons), risk_flags, milestones (array of {name, target_offset_months, predecessors, owner_role}), pre_submission_recommended (bool), confidence (float).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Regulatory Submission Strategy Planner

## When to use

**Mandatory disclaimer.** This skill produces methodology guidance only. Outputs are not regulatory submissions. Real submissions must be authored, reviewed, and signed by qualified regulatory affairs staff and may require external counsel. No output may be filed with any regulator without sponsor authorization.

Invoke this skill at the front end of a regulatory program — typically the moment a sponsor is converging on a product definition and asking "which pathway, in which order, on what timeline?" Typical entry points: a startup CTO whose device is months away from design freeze and needs to know whether the regulatory team is sized for a 510(k) or a PMA; a clinical lead at a small biotech who needs to draft an IND timeline to a target first-in-human date; a product owner at a digital-health company who is uncertain whether their software is a regulated device at all, much less which pathway applies; a regulatory affairs manager pulling together a region-by-region launch plan for a combination product and trying to sequence FDA, EMA, Health Canada, and PMDA filings sensibly.

The skill is appropriate for *pre-decision* planning. It is **not** appropriate as the final word on a pathway selection; that decision must be made by a qualified regulatory affairs professional, with input from clinical, quality, and legal, and ideally pre-validated with the relevant agency through a pre-submission meeting (FDA Q-Sub, EMA Scientific Advice, etc.). The skill's job is to compress weeks of strategic scoping into a defensible first draft that a human team can pressure-test and refine.

Do not use this skill for:

- Already-submitted programs where the question is "should I respond to this deficiency letter?" — that is a different skill (`submission-gap-reviewer` is closer).
- Products that the sponsor knows fall outside FDA/EMA jurisdiction — e.g., pure wellness apps with no medical claims, general-purpose lab reagents marketed as research-use-only. The skill will still produce output but the recommendation will be "out of scope; confirm with counsel."
- Programs where the strategy question is a corporate-development question (e.g., "should we partner with a CRO?") rather than a regulatory one.

The skill is intentionally biased toward suggesting a pre-submission meeting with the agency at any meaningful inflection point. Agency feedback is the cheapest insurance available in this space, and the methodology treats a missed pre-sub as a planning defect.

## How to apply

Regulatory strategy is, fundamentally, a classification problem followed by a sequencing problem. The classification problem is "what is this product, in the regulator's taxonomy, and what does that taxonomy demand?" The sequencing problem is "given those demands, what work must happen in what order, and where can parallel work cut the timeline without creating rework?"

1. **Classify the product against the regulator's taxonomy before anything else.** The same physical product can be a Class I device, a Class II device, a Class III device, a drug, a biologic, or a combination product depending on its claims and mechanism. Do not let the sponsor's marketing label decide. Walk through:
   - **Intended use claims.** What does the product *claim* to do, in regulator-relevant language? "Aids in diagnosis of X" is a different claim from "supports clinician decisions about X" is a different claim from "monitors Y in patients with Z." The most consequential claim is usually the most aggressive one in the sponsor's marketing.
   - **Mechanism.** Is the principal mode of action achieved through chemical action (drug), biologic action (biologic), or physical/mechanical/computational action (device)? For combination products, identify the primary mode of action (PMOA) — this determines the lead center at FDA (CDER, CBER, or CDRH) and parallel jurisdiction at EMA.
   - **Risk class.** For devices: Class I (general controls), Class II (special controls, typically 510(k)), Class III (PMA). For drugs and biologics: New Molecular Entity vs. follow-on (505(b)(1) vs. 505(b)(2) vs. ANDA; BLA vs. biosimilar 351(k)). For IVDs: traditional vs. high-complexity vs. companion diagnostic.

2. **Look hard for a predicate or precedent before assuming a high-burden pathway.** Many sponsors default to the most rigorous pathway out of caution; this can add years and millions of dollars to a program unnecessarily. Specifically:
   - **For devices**, search the FDA 510(k) database for substantially equivalent cleared devices in the same product code. A legitimate predicate enables a 510(k); a novel device without a predicate may be a De Novo candidate (often faster than a PMA); only the highest-risk truly novel devices need a PMA.
   - **For drugs**, examine whether 505(b)(2) is available — i.e., whether the sponsor can reference published literature or FDA's prior findings of safety/efficacy for a listed drug. This can collapse a five-to-seven-year NDA timeline into a meaningfully shorter program.
   - **For digital therapeutics and software**, examine whether the product fits within the Software as a Medical Device (SaMD) framework, the Clinical Decision Support exemption (under the 21st Century Cures Act), or the Digital Health Pre-Cert pilot signals — and whether it qualifies as a non-device under FDA's evolving software guidance.

3. **Map the work product backwards from the submission contents.** Rather than starting from "what should we do next," start from "what does the submission have to contain, and what work product feeds each section?" For an eCTD-format submission:
   - **Module 1** — regional administrative information (cover letter, application forms, agent appointments). Cheap to produce but cannot start until the dossier is shaped.
   - **Module 2** — summaries (Quality Overall Summary, Nonclinical Overview, Clinical Overview). These are derivative; they cannot be finished until 3-5 are stable.
   - **Module 3** — quality / CMC. Usually the longest pole for a small-molecule NDA; tightly coupled to manufacturing-process freeze.
   - **Module 4** — nonclinical study reports. Driven by the IND-enabling tox package.
   - **Module 5** — clinical study reports and integrated summaries (ISS, ISE). Driven by the clinical program.
   For a 510(k), the structure is different but the same backward-mapping discipline applies: indications for use, device description, substantial equivalence comparison, performance testing (bench, animal, clinical if needed), labeling, and the eSTAR forms.

4. **Identify the rate-limiting work stream.** In almost every program, one work stream sets the critical path:
   - For a first-in-human small molecule, it is usually the IND-enabling tox package (typically 9-15 months from candidate selection to IND-ready, depending on whether non-rodent species and chronic-tox studies are needed).
   - For a Class II device, it is usually performance testing (bench + biocompatibility + EMC/electrical-safety + cybersecurity for connected devices) plus the clinical evidence package if the predicate path requires one.
   - For a biologic, it is usually CMC — process development, comparability, and stability often dictate when the BLA can file.
   - For a digital therapeutic, it is usually clinical evidence generation plus the QMS maturity needed to convince the agency the software-development process is auditable.
   Flag the rate-limiting stream explicitly. The rest of the plan should be scheduled around it.

5. **Schedule pre-submission interactions deliberately.** Every regulator offers low-cost feedback channels: FDA Pre-Submission (Q-Sub) meetings, EMA Scientific Advice, EMA Innovation Task Force briefings, Health Canada presubmission meetings, PMDA face-to-face consultations, NMPA pre-clinical communication. The methodology treats these as planning rocks, not optional polish:
   - **Pre-IND** (drugs/biologics) — typically two to four months before the planned IND filing. Used to align on the tox package adequacy and the Phase 1 design.
   - **Q-Sub** (devices) — most useful when the predicate strategy is uncertain, the test methodology is novel, or the indications-for-use language is being shaped. Plan for one to three Q-Subs across a Class II device program; more for a novel-technology Class II or a De Novo.
   - **End-of-Phase 2** (drugs/biologics) — gating the Phase 3 design.
   - **Pre-NDA / Pre-BLA / Pre-Submission** — gating the marketing application.
   - **Type C / Type D ad hoc meetings** — for narrowly-scoped questions that come up between major milestones.
   Schedule each meeting with at least three months of buffer for the briefing-document drafting and FDA's response window. Treat the briefing package as the deliverable, not the meeting itself.

6. **Construct the milestone table in dependency order.** Each milestone should have: a name, a target offset in months from "today" (or from a named anchor like "candidate selection"), an explicit predecessor list, and an owner role (Regulatory Affairs, Clinical, CMC, Quality, Safety, Project Management). Avoid attaching milestones to calendar dates in the first draft — use offsets so the plan is robust to slip.

7. **Surface region-by-region divergence rather than papering over it.** FDA, EMA, Health Canada, PMDA, NMPA, MHRA, and the rest have meaningful methodological differences (e.g., EMA places more weight on quality-of-life endpoints in some therapeutic areas; PMDA may require ethnically Japanese clinical data; NMPA has its own technical review queue with distinct timing). A "global" plan that pretends the regions are identical will fail. Either (a) lead with one region and stage the others sequentially, accepting the launch lag, or (b) parallel-track but explicitly call out which evidence package needs to be designed for cross-region acceptance (typically by aligning to ICH guidelines: ICH E6 for GCP, ICH M4 for the CTD format, ICH E8/E9 for trial design, ICH Q-series for CMC).

8. **Make the risk-flag register explicit.** For each significant risk, name (a) the risk, (b) the regulator-facing consequence, and (c) the proposed mitigation. Common high-leverage risks:
   - **Novel mechanism with no predicate** → consequence: pathway uncertainty, possible De Novo or PMA → mitigation: early Q-Sub on classification.
   - **Pediatric indication** → consequence: PREA/PIP obligations, additional safety review → mitigation: pediatric study plan in the IND.
   - **AI/ML-enabled functionality** → consequence: predetermined change-control plan (PCCP) expectations, possible cybersecurity submission requirements → mitigation: design the PCCP early and reference FDA's good machine-learning practice principles in design controls.
   - **Combination product** → consequence: jurisdictional ambiguity, RFD potentially needed → mitigation: Request for Designation early if PMOA is unclear.
   - **First-in-class biologic** → consequence: heavy CMC scrutiny, comparability concerns for process changes → mitigation: lock the manufacturing process early; over-invest in characterization.

9. **Surface the cost-of-change profile.** Some decisions are cheap to revise early and ruinously expensive late: indications-for-use language, primary endpoint selection, the manufacturing site location, the comparator in a pivotal trial. The plan should call out which decisions are still reversible and which become locked at each milestone, so the sponsor can prioritize where to push back hardest before that gate closes.

10. **Recommend, do not decide.** End the report with a clear, single-sentence recommendation ("Recommend a 510(k) via predicate K201234 with one Q-Sub on the human-factors test design"), followed by the alternatives considered and the explicit reason each was rejected. Use must/should/may language deliberately — "should pursue" is a recommendation, "must obtain" should be reserved for statutorily required steps.

11. **Self-check before returning.** Confirm: (a) the recommended pathway maps to a real, current regulator pathway (no inventing categories); (b) every milestone has a predecessor or is anchored to "today"; (c) every risk flag has a mitigation; (d) the disclaimer is present; (e) the rate-limiting work stream is explicitly named. If the input is too sparse to make a defensible recommendation, say so and ask for the specific missing inputs rather than producing a confident-but-shaky plan.

12. **Calibrate confidence honestly.** Confidence below 0.6 should trigger an explicit "this needs a regulatory consultant before any commitments are made" note. Common low-confidence drivers: combination product with unclear PMOA, software whose device-status is ambiguous, novel biologic with no comparable approval history, multi-region plan with conflicting evidence requirements.

## Inputs

- `product_description` (required, text) — narrative product description. The richer the better; sparse inputs produce sparse outputs.
- `product_type` (required, choice) — anchors the pathway tree. If `unknown`, the agent should start by asking diagnostic questions rather than guessing.
- `target_regions` (optional, text) — comma-separated. Default FDA only.
- `risk_signals` (optional, text) — anything the sponsor flags as a known risk or novelty.
- `known_predicates_or_precedents` (optional, text) — predicates, listed drugs, or precedent products the sponsor has already identified.
- `program_phase` (optional, choice) — where the program is today; trims out-of-scope milestones.

## Outputs

- `strategy_report` (markdown) — opens with the recommendation in one sentence; followed by classification analysis; pathway comparison with rejection reasons for alternatives; milestone table; risk register with mitigations; pre-submission interaction plan; explicit limitations and assumptions.
- `strategy_json` (JSON) — `recommended_pathway`, `alternatives_considered` (array of `{pathway, rejection_reason}`), `milestones` (array of `{name, target_offset_months, predecessors, owner_role}`), `risk_flags` (array of `{risk, consequence, mitigation}`), `pre_submission_recommended` (bool), `regions` (array), `confidence` (float 0-1), `confidence_reason`, `disclaimer_acknowledged` (bool, always true).

## Examples

### Example 1 — Class II connected medical device

**Input product_description (excerpt):** A wearable continuous glucose monitor accessory that pairs over Bluetooth Low Energy with a primary CGM device, runs a proprietary smoothing algorithm, and displays trend arrows to the patient. No insulin dosing claims.

**Input product_type:** `medical_device`. **risk_signals:** "AI/ML smoothing, BLE-connected, OTC adult use, no pediatric." **known_predicates_or_precedents:** "K20XXXX (named predicate accessory)."

**Output strategy_report (excerpt):**

> **Recommendation: pursue a 510(k) referencing K20XXXX as the primary predicate, with one Q-Sub before the cybersecurity test plan locks.**
>
> Pathway alternatives considered:
> - **De Novo** — rejected because a substantively similar accessory has already been cleared; substantial-equivalence argument is available.
> - **PMA** — rejected because risk class is II, not III, and the device does not make insulin-dosing claims.
> - **Non-device wellness app** — rejected because the device interprets a medical signal and conveys clinical-decision-relevant trend information.
>
> Rate-limiting work stream: cybersecurity and connected-device testing (FDA's premarket cybersecurity expectations have hardened; SBOM is now mandatory and the threat model is gated by the system architecture).
>
> Suggested pre-submission interaction: one Q-Sub at design-freeze minus three months to validate the cybersecurity testing approach, the human-factors protocol, and the PCCP for the smoothing algorithm.

### Example 2 — First-in-human small molecule

**Input product_description (excerpt):** A novel small-molecule inhibitor of a previously undrugged target, intended initially for advanced refractory solid tumors. Candidate selected; non-GLP tox suggests acceptable margin.

**Input product_type:** `drug_small_molecule`. **program_phase:** `preclinical`. **risk_signals:** "novel target, oncology, no precedent in class."

**Output strategy_report (excerpt):**

> **Recommendation: file a traditional IND for a Phase 1a dose-escalation in advanced refractory solid tumors, anchored by a single Pre-IND meeting four months before IND submission.**
>
> Rate-limiting work stream: the IND-enabling tox package (28-day GLP tox in two species, genotoxicity battery, safety pharmacology core battery). At the current preclinical stage, IND filing is approximately 12-15 months out depending on chronic-tox sequencing.
>
> Pre-IND focus areas: (a) adequacy of the tox package for the planned starting dose and escalation scheme; (b) alignment on the Phase 1 design including the dose-escalation rule (mTPI vs. 3+3 vs. BOIN); (c) CMC adequacy at IND stage for first-in-human supply.

### Example 3 — Digital therapeutic with ambiguous device status

**Input product_description (excerpt):** A mobile app delivering cognitive behavioral therapy for insomnia (CBT-I) to adults, with a structured 8-week protocol. No connection to physical sensors. Markets as a "treatment for chronic insomnia."

**Input product_type:** `digital_therapeutic`. **risk_signals:** "first-in-class digital therapeutic for the sponsor."

**Output strategy_report (excerpt):**

> **Recommendation: pursue a 510(k) referencing K17XXXX (a previously cleared CBT-I digital therapeutic) under the Software as a Medical Device framework. Confirm the path with a Q-Sub before locking the pivotal study design.**
>
> The treatment claim places the product squarely inside the device definition (intended to treat a disease), excluding the Clinical Decision Support exemption and the general-wellness carve-out. The existence of a cleared predicate enables 510(k) rather than De Novo.
>
> Rate-limiting work stream: the pivotal clinical evidence package. The predicate cleared on a randomized controlled trial against a sleep-hygiene control; the methodology should be confirmed in the Q-Sub.
>
> Confidence: 0.65 — the predicate strategy is sound but the indication language deserves agency confirmation before the protocol locks.

## Limitations

- **Not regulatory advice.** Every output is a structured methodology draft. Real submission decisions must be made by qualified regulatory affairs professionals.
- **Agency policy changes faster than this skill.** Guidances are revised; new pilots open and close; classifications shift. Treat any specific pathway citation as a starting point for verification against current agency websites, not as a current-state assertion.
- **No real-time agency database access.** The skill does not query the FDA 510(k) database, the Drugs@FDA database, or the EMA EPAR repository in real time. If a sponsor provides predicate numbers, the skill takes them on input; it does not verify they are real, current, or appropriate.
- **Region coverage is biased toward FDA.** EMA, Health Canada, PMDA, NMPA, MHRA, TGA coverage is competent but not exhaustive. For programs led from a non-US region, treat the recommendation as a draft to validate with local regulatory counsel.
- **Combination-product PMOA calls are genuinely hard.** When the product is a true combination (e.g., drug-eluting stent, prefilled drug-device combination, digital-plus-drug regimen), the agent will recommend the Request for Designation pathway rather than pretend to know the PMOA call.
- **Timelines are planning estimates, not commitments.** Tox programs slip, sites slip, agencies slip. The milestone offsets are reasonable medians, not P50 guarantees.
- **No financial modeling.** The skill does not estimate study costs, CMO costs, or CRO costs. Pair with an internal finance model.

## Sources reviewed

The methodology below was informed by reviewing publicly available, permissively-licensed regulatory tooling and documentation repositories on GitHub, plus regulator-public-domain guidance documents. No source content was reproduced. **Honest disclosure of source thinness:** open-source regulatory-submission tooling is unusually sparse under MIT/Apache/BSD/ISC/Unlicense terms. The most prominent industry templates (OpenRegulatory ISO/IEC compliance templates) are released under CC BY-NC-SA and were therefore excluded from primary sourcing. The methodology leans on a small set of MIT-licensed tooling repositories plus official regulator URLs (FDA, EMA, ICH) used as references only — never copied. Sponsors should treat regulator websites as authoritative; this skill paraphrases enduring methodology, not current guidance text.

- https://github.com/innolitics/rdm (MIT license — regulatory documentation manager methodology for medical-device software)
- https://github.com/rlwadh/fda-predicate-finder (MIT license — predicate device discovery methodology)
- https://github.com/arnaud-dg/fda-510k (MIT license — 510(k) knowledge-base methodology)
- https://github.com/tsbischof/fda (BSD-2-Clause — FDA 510(k) data aggregation methodology)
- https://www.fda.gov/regulatory-information/search-fda-guidance-documents (FDA public-domain guidance index — reference only, not a source repo)
- https://www.ema.europa.eu/en/human-regulatory-overview (EMA human-medicines regulatory overview — reference only, not a source repo)
- https://www.ich.org/page/efficacy-guidelines (ICH efficacy guideline index — reference only, not a source repo)
