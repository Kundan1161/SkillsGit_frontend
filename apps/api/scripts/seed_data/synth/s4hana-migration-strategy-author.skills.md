---
id: skillsgit-curated/s4hana-migration-strategy-author
version: 0.1.0
name: S/4HANA Migration Strategy Author
description: Outline a brownfield, greenfield, or selective approach to S/4HANA with phasing, custom code, master data, and cutover plan.
authors:
  - name: Wave-3 Synthesis Agent
    handle: wave3synth
    role: author
category: enterprise-software
tags:
  - niche:sap-integration
  - s4hana
  - migration
  - brownfield
  - greenfield
  - selective-data-transition
  - custom-code
  - cutover
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
    - gpt-4.1
  min_context_tokens: 50000
  tools_required: []
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - s/4hana migration
  - s4 migration
  - ecc to s4
  - brownfield vs greenfield
  - selective data transition
  - custom code migration
  - rise with sap
  - s/4 cutover
example_invocations:
  - "Outline an S/4HANA migration plan for a 15-year-old ECC 6.0 EhP8 system in pharma."
  - "Brownfield or greenfield for our multi-country roll-out? Pros and cons."
  - "Build a custom-code remediation plan with phasing for our Z-heavy ECC."
  - "Draft a cutover plan and master-data harmonisation plan for an S/4 conversion."
inputs:
  - name: context
    type: text
    required: true
    description: Free-text profile of the source landscape, business drivers, constraints, and known pain points.
  - name: preferred_path
    type: choice
    required: false
    description: Hypothesised migration path; the skill will challenge it if the context disagrees.
    choices:
      - undecided
      - brownfield
      - greenfield
      - selective-data-transition
  - name: target
    type: choice
    required: false
    description: Target S/4HANA deployment.
    choices:
      - s4-on-premise
      - s4-private-cloud
      - s4-public-cloud
      - rise-with-sap
  - name: timeline_months
    type: number
    required: false
    description: Target programme length in months; the skill scales the phasing to fit.
outputs:
  - name: strategy_brief
    type: markdown
    description: Recommended path, rationale, phasing, work-streams, RACI sketch, risks.
  - name: cutover_outline
    type: markdown
    description: Pre-cutover, cutover-weekend, hypercare timeline with go/no-go checkpoints.
changelog:
  - version: 0.1.0
    date: 2026-05-14
    notes: Initial release. Synthesised from SAP custom-code migration workshops, CAP samples, abapGit, and Clean ABAP/Code Review styleguides.
---

# S/4HANA Migration Strategy Author

## When to use

Use this skill at the start of an S/4HANA programme to produce a written strategy document that a steering committee, CIO, or transformation lead can react to. Typical triggers:

- An ECC 6.0 estate is approaching the 2027 / 2030 maintenance horizon and leadership wants a recommendation.
- A board is weighing brownfield system conversion vs greenfield re-implementation vs selective data transition (SDT, also called "shell conversion" in some shops).
- A pre-existing programme stalled and needs a re-baselined plan.
- A merger or carve-out forces a re-design of the SAP landscape.

Do **not** use it for:

- Running the conversion itself (use SAP's Software Update Manager / DMO, Migration Cockpit, Custom Code Migration Fiori app).
- Estimating licence cost (commercial conversation with SAP and partners).
- Producing the cutover runbook at task-level granularity (it produces an outline; the runbook is the cutover team's deliverable).

## How to apply

Produce a strategy brief in seven sections, in this order. Reviewers will hunt for the path recommendation and the cutover; everything else supports those two.

### Section 1 - Source-landscape baseline

Capture and restate, asking the user only for missing items:

- Current release and SP / EhP, database, OS, kernel.
- Modules in scope (FI, CO, MM, SD, PP, WM/EWM, PM, QM, HR/HCM, CRM if embedded).
- Industry add-ons (IS-U, IS-Retail, IS-Oil, etc.) - they often dictate the path.
- Customisations: number of Z-objects, BAdI / user-exit implementations, modifications to standard, copies of standard programs.
- Master-data quality issues: known duplicate customers / vendors, multi-source product master, plant code clashes, chart-of-accounts diversity.
- Integration inventory: IDoc partners, RFC destinations, SOAP / OData consumers, file interfaces, third-party middleware in flight.
- Non-functional: data volume (DB size, top tables), peak transaction rate, uptime SLAs, regulatory regimes (GxP, SOX, HIPAA, GDPR).
- Organisational: number of countries / legal entities, language requirements, business-process owners in place, change-management appetite.

### Section 2 - Drivers and constraints

Translate the business goals into evaluation weights. Typical drivers:

- **Maintenance-deadline driven.** Just get to S/4 with minimum disruption. Bias to **brownfield**.
- **Process-transformation driven.** Standardise on SAP Best Practices, retire bespoke. Bias to **greenfield**.
- **Selective scope.** Keep historical data in one or two entities, redesign the rest. Bias to **selective data transition**.
- **Carve-out or merger.** Source system is shared and cannot be converted in place. Often forces **SDT** or **greenfield**.
- **Risk-averse / regulated.** Validation cost dominates; prefer the path with the smallest delta to "what we have today".

Constraints that act as tie-breakers: industry solution availability on the target stack, language / country localisations, the Customer Vendor Integration (CVI) and Business Partner readiness of the source system, whether the source has already moved to a Unicode kernel and HANA.

### Section 3 - Path recommendation

Pick one and justify it. The default heuristics:

**Brownfield (system conversion / in-place)**

- Best when: the existing system is healthy and largely fit-for-purpose, customisations are sane, business wants minimum disruption, deadline pressure is real, data history is precious.
- Avoid when: organisations are mid-merger, the source has accumulated 20+ years of debt with no business owner left, the target needs a substantially different organisational structure, or industry add-ons block conversion.
- Phasing - typically 12-24 months: preparation, system conversion (DMO + SUM), custom-code adaptation, functional testing, integration testing, cutover, hypercare.

**Greenfield (new implementation)**

- Best when: the business genuinely wants to re-engineer processes, the source is unsalvageable, multiple regional systems are being consolidated, the target is S/4 public cloud (which mandates Best Practices alignment).
- Avoid when: there is no appetite for change management, master data cannot be cleansed in time, historical reporting needs cannot be solved with a data warehouse.
- Phasing - typically 18-36 months: explore / fit-to-standard, realise, deploy by wave (country, region, business unit), hypercare per wave.

**Selective data transition (SDT)**

- Best when: a hybrid is needed - retain selected historical data and configuration but redesign the rest; carve-outs and mergers; landscape consolidation.
- Avoid when: the team has no SDT delivery experience and the partner offering is unproven; the data scope cannot be drawn cleanly.
- Phasing - typically 18-30 months: feasibility study, scope definition (entities, time slices), shell build, iterative data loads, parallel runs.

If `preferred_path` was supplied and the context disagrees, **say so explicitly** with a one-paragraph rebuttal and recommend the alternative.

### Section 4 - Work-stream plan

Produce a numbered list of work-streams. Every S/4 programme needs at least:

1. **Programme governance.** Steering committee, RACI, change-control board, integration architecture board.
2. **Functional design.** Per module: process owner, fit-to-standard workshops, configuration delta log.
3. **Custom-code remediation.** See section 5 - it gets its own treatment.
4. **Data migration / harmonisation.** Master data cleansing, deduplication, business-partner consolidation (CVI), chart-of-accounts harmonisation, plant / company-code mapping.
5. **Integration redesign.** Catalogue every interface; mark each as keep / replace / retire; map IDoc / RFC interfaces to OData / event mesh where the target stack requires it (especially for S/4 public cloud or RISE).
6. **Authorisations and security.** Re-derive PFCG roles against new and Fiori tcode catalogue; address SoD findings as part of the cut-over, not after.
7. **Reporting and analytics.** Move from BW on Hana to BW/4HANA or SAP Datasphere; embedded analytics via CDS views.
8. **Testing.** Unit, system, integration, regression, performance, user-acceptance, cutover dress rehearsals.
9. **Training and change management.** Fiori UX is the visible shock; under-investing here is the most common cause of post-go-live grief.
10. **Cutover and hypercare.** See section 7.

For each work-stream, list: lead role, key deliverables, dependencies, and the earliest start.

### Section 5 - Custom-code remediation plan

This is the work-stream that breaks more programmes than any other. Treat it as a mini-plan-within-the-plan.

1. **Inventory.** Use ABAP Call Monitor (SCMON) and Usage and Procedure Logging (SUSG) on the source for 3-6 months to find what is actually used. The number of "live" Z-objects is usually 30-60% of the catalogue.
2. **Categorise.** Each surviving Z-object is one of: keep-as-is, adapt for S/4, replace with standard / Fiori, replace with side-by-side BTP extension, retire.
3. **Analyse.** Run remote ATC checks from the future S/4 system using the Simplification Database. The ATC produces findings categorised by the simplification item; group them by responsible team.
4. **Decide on extensibility model per object.** In-app key-user extensibility (Fiori-based) for small things; classic ABAP enhancements for in-stack logic that must run inside the kernel; side-by-side on BTP for any logic that wants to be released-independent or run in S/4 public cloud where in-stack ABAP is restricted.
5. **Schedule remediation in waves.** Wave 1: blockers (will not activate). Wave 2: simplification-database functional adaptations. Wave 3: performance and Fiori-UX adaptations. Wave 4: optional clean-ABAP / RAP refactors.
6. **Track in transports tied to the conversion.** Use abapGit / gCTS so the remediation work is version-controlled outside the cutover transport queue.
7. **Set quality gates.** No new Z-objects without an ATC clean run. Code review by the two-eyes principle. The S/4 styleguide for in-stack code, the BTP Cloud SDK for side-by-side.

### Section 6 - Master-data harmonisation

Pre-conversion or pre-cutover work that is non-negotiable for brownfield and SDT.

- **Customer / Vendor / Contact -> Business Partner (CVI).** Source system must be CVI-active before conversion; this often takes months of cleansing.
- **Chart of accounts.** Multiple charts must be reconciled; mapping rules approved by Finance.
- **Material master.** Material number length, type catalogue, classification redesign for the new product hierarchy.
- **Plants, storage locations, sales orgs, purchasing orgs.** Lock the org-unit structure early; changes after cutover are painful.
- **Pricing conditions and output determination.** Notorious for drift between countries; align in the harmonisation phase, not during cutover weekend.
- **Historical postings.** Define how far back FI documents must be carried forward; archive the rest before conversion to shrink the SUM downtime.

### Section 7 - Cutover and hypercare outline

Produce a calendar with these checkpoints (the depth depends on `timeline_months`):

**T minus 6 months.** Mock conversion #1 on a sandbox copy: time the SUM/DMO runtime, measure the system-downtime window, validate the custom-code adaptations.

**T minus 3 months.** Mock conversion #2 with full data volume. Lock the cutover-weekend runbook. Communicate the freeze window for transports and master-data changes.

**T minus 1 month.** Mock conversion #3 - the dress rehearsal. Every cutover task must have an owner, a predecessor, an expected duration, and a rollback. Confirm hypercare staffing.

**Cutover weekend.** Sequence:

1. Functional freeze on source.
2. Final delta data export (open items, in-flight documents).
3. Source backup and DMO downtime window begins.
4. Technical conversion (kernel, DB, content).
5. Post-conversion automation (CVI activation, simplification-database adaptations, custom-code transports).
6. Smoke tests (logon, top-20 tcodes / apps, top integrations end-to-end).
7. Reconciliation (FI balances, open POs, open SOs, inventory).
8. Business sign-off go / no-go at a pre-published checkpoint time.
9. Open to users.

**Hypercare** (4-8 weeks): a war-room with module leads and developers on rotation, daily triage, a freeze on non-critical change, and a clear exit checklist (defect burn-down rate, SLA compliance, business KPI parity).

### Section 8 - Risks and mitigations

Always include a list of the top 6-10 risks. The recurring ones:

- CVI conversion blocked by un-cleansed business partners.
- Custom-code remediation slips, dragging the cutover.
- Integration consumers (downstream non-SAP) not retested.
- BW / analytics behind schedule, leaving the business without numbers post-go-live.
- Authorisations re-built late, producing access-denied storms on day 1.
- Master-data harmonisation incomplete, producing reconciliation errors at cutover.
- Hypercare staffing thin during European / Asian / US holidays.
- Vendor (system integrator) ramp-down too aggressive, leaving the client without support.

For each risk, supply a likelihood / impact / mitigation triple.

## Inputs

- `context` - required free-text describing the source landscape, drivers, and pain points. Encourage the user to paste anything they have - audit reports, prior assessments, current pain inventory.
- `preferred_path` - optional. The skill will challenge it if the context disagrees.
- `target` - optional; constrains the path (public cloud excludes most in-stack custom code).
- `timeline_months` - optional; scales the phasing.

## Outputs

- `strategy_brief` - the seven sections above, in markdown, with the path recommendation prominent at the top.
- `cutover_outline` - a markdown timeline of pre-cutover, cutover weekend, and hypercare with go/no-go checkpoints.

## Examples

> Context: ECC 6.0 EhP8 on HANA, 2.4 TB DB, FI/CO/MM/SD/PP, three legal entities, light Z (about 600 active Z-objects, 90% in MM and SD), no industry add-on. Driver: 2030 maintenance deadline. Risk appetite: low. No appetite for re-engineering.

Recommendation (abridged): **Brownfield system conversion to S/4HANA private cloud edition (RISE).** Rationale: healthy source, modest customisation, low transformation appetite, deadline-driven driver. Phasing 16 months. Custom-code remediation in three waves. Cutover after two full-volume mock runs.

> Context: ECC 6.0 on Oracle, EhP7, 8 TB DB, IS-Retail, 14 countries on 14 local templates, post-merger consolidation in progress, executive sponsorship for process standardisation.

Recommendation (abridged): **Greenfield on S/4HANA public cloud with a multi-wave country roll-out.** Rationale: consolidation goal, executive sponsorship, divergent local templates that brownfield would preserve. Risk: change-management load. Mitigation: wave by region with a pilot country first.

## Limitations

- The brief is a starting point, not a contract. A real programme requires a paid scoping engagement with SAP or an experienced partner.
- Effort and timeline estimates are heuristics; they scale linearly with the inputs the user supplied and do not model team productivity, contention with other initiatives, or freeze windows in the calendar.
- The skill does not know your licence position. Public cloud and RISE come with very different commercial shapes; the technical recommendation may be over-ruled commercially.
- It cannot audit the source system; it relies on what the user reports. Garbage-in / garbage-out.
- Industry add-ons (especially IS-U, IS-Retail older releases, banking) carry hard constraints that the generic recommendation may miss; if the context mentions an add-on, the brief flags it for specialist review and does not pretend to resolve it.

## Sources synthesised (all permissive)

- `SAP-samples/abap-platform-ccm-workshops` - Apache-2.0; the canonical workflow (SCMON / SUSG, Simplification Database, ATC, Custom Code Migration Fiori app, remediation waves).
- `SAP/styleguides` (Clean ABAP, ABAP Code Review) - Creative Commons; code-quality bar applied to the remediation work-stream.
- `SAP-samples/abap-cheat-sheets` - Apache-2.0; idioms used in the post-conversion code refactors.
- `SAP-samples/cloud-cap-samples-java`, `cap-sflight`, `btp-cap-demo-usecases` - Apache-2.0; side-by-side BTP extensibility option.
- `SAP-samples/cloud-abap-event-mesh-api`, `btp-event-driven-multi-tenant-architecture` - Apache-2.0; event-mesh option for replacing legacy IDoc fan-out during the integration redesign.
- `abapGit/abapGit`, `SAP/abap-file-formats` - MIT; version-control posture for custom-code remediation.

## Source-thinness disclosure

Permissively licensed open-source SAP methodology material is genuinely scarce. The most authoritative resources on S/4HANA migration are SAP-proprietary documents (Activate methodology, Custom Code Migration guides, simplification list PDFs) and partner playbooks that are not redistributable. This skill draws only on the permissively licensed sources listed above; it does not paraphrase SAP-proprietary text. Treat the resulting brief as a structural starting point that must be reconciled against your tenant's simplification list and your partner's delivery playbook.
