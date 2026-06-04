---
id: skillsgit-curated/alert-fatigue-reviewer
version: 0.1.0
name: CDS Alert Fatigue Reviewer
description: Audit an existing portfolio of clinical decision support alerts for fatigue risk — firing rate, override rate, time-to-action, false-positive rate, redundancy — and recommend retirements and refinements.
authors:
  - name: Wave-3 Synthesis Agent
    handle: synth-cds
    role: author
category: healthcare
tags:
  - niche:clinical-decision-support
  - alert-fatigue
  - cds-governance
  - ehr-alerts
  - override-analysis
  - clinical-informatics
  - quality-improvement
license_type: free
ai:
  required_models:
    - claude-opus-4-7
  compatible_models:
    - claude-sonnet-4-6
    - gpt-4o
  min_context_tokens: 40000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - alert fatigue
  - alert audit
  - CDS audit
  - override rate
  - alert tuning
  - alert retirement
  - alert governance
  - BPA review
  - alert burden
example_invocations:
  - "Help me audit our top 20 alerts by override rate and propose a retire/refine/keep decision for each."
  - "Walk me through a fatigue-risk framework I can present to the CDS governance committee."
  - "Draft a tuning plan for an alert with a 92% override rate."
inputs:
  - name: alert_inventory_summary
    type: text
    required: true
    description: De-identified summary of the alert(s) under review — name, intent, target role, firing rate, override rate, override-reason distribution, top suppressors. No PHI.
  - name: review_scope
    type: choice
    required: false
    description: How wide the audit is.
    choices:
      - single-alert
      - alert-family
      - top-N-by-volume
      - top-N-by-override-rate
      - full-portfolio
  - name: governance_context
    type: choice
    required: false
    description: The committee or process this audit will feed into.
    choices:
      - cds-governance-committee
      - p-and-t-committee
      - quality-and-safety
      - informatics-internal-review
      - vendor-package-tuning
outputs:
  - name: alert_audit_report
    type: markdown
    description: A structured audit report with per-alert fatigue-risk classification, retire/refine/keep recommendation, and a portfolio-level summary (planning use only, governance-committee draft).
changelog:
  - version: 0.1.0
    date: 2026-05-14
    notes: Initial synthesis. Generic alert-fatigue audit scaffold drawn from widely published informatics literature on alert override analysis and the "Five Rights of CDS" framework; no proprietary alert text or clinic content reused.
---

# CDS Alert Fatigue Reviewer

> **Mandatory disclaimer.** This skill describes methodology for
> DESIGNING and auditing clinical decision support systems. It is not
> itself a CDS, does not diagnose, and does not recommend treatment.
> CDS deployments in real clinical settings require qualified clinical
> informatics staff, formal validation against clinical reference
> standards, regulatory clearance where applicable (e.g., FDA Software
> as a Medical Device), and ongoing post-deployment surveillance. **No
> skill output may be deployed in care delivery without that full
> process.** Treat every artifact this skill produces as a draft for
> governance-committee review — not as a configuration export, not as
> a retirement order, not as a vendor change request.

## When to use

Use this skill when a clinical informatics team wants to systematically
review existing CDS alerts (interruptive Best-Practice Advisories,
order-entry warnings, drug–drug interaction alerts, dose alerts, etc.)
for **fatigue risk** and decide which to **retire, refine, or keep**.
Common prompts:

- "We have a portfolio of 600 interruptive alerts. Help us frame an
  audit we can actually finish this quarter."
- "Our top-volume alert has a 95% override rate. What questions
  should we ask before retiring it?"
- "Draft the per-alert section template we will use for our
  governance committee."
- "Help us classify the override reasons we are seeing on this
  alert family."

Do **not** use this skill to:

- Issue actual retirement orders for live alerts.
- Recommend specific clinical thresholds, drug doses, or
  contraindication overrides.
- Replace a CDS governance committee, pharmacist-informaticist
  review, or patient-safety review.
- Determine whether a given alert is a regulated medical-device
  function.

## How to apply

The audit is a five-stage funnel. Earlier stages are cheap and ruthless;
later stages are expensive and careful.

### Stage 1 — Scope the audit

Pick the unit of analysis:

- **Single alert** — usually because of a complaint, a near-miss, or a
  vendor change.
- **Alert family** — related rules (e.g. all opioid-prescribing
  alerts, all drug–allergy alerts).
- **Top-N by volume** — the alerts users see most.
- **Top-N by override rate** — the alerts users dismiss most.
- **Full portfolio** — usually only feasible once per year, with
  staged execution.

Document, for each alert in scope:

- Internal alert id and name.
- One-line clinical intent.
- Target user role.
- Surface (interruptive modal, non-interruptive banner, order
  default, CDS Hooks card).
- Date created and date last reviewed.
- Owner of clinical content. **An alert with no named owner is a
  Stage 1 fail; recommend retirement or re-assignment of ownership
  before any further analysis.**

### Stage 2 — Pull the fatigue-risk metrics

For each in-scope alert, gather the following (the skill assumes the
team has access to EHR audit logs; it does not query them):

| Metric                       | What it tells you                                                |
|------------------------------|------------------------------------------------------------------|
| Firing rate                  | Volume per 1,000 eligible encounters or per user-day             |
| Acceptance rate              | % of fires where the recommended action was taken                |
| Override rate                | % of fires overridden                                            |
| Override-reason distribution | How often each reason is selected (concentration vs. spread)     |
| Time-to-action               | Median seconds from fire to user action                          |
| Same-user repeat rate        | % of fires on patients the same user already saw today           |
| Same-patient repeat rate     | Fires per patient-encounter                                      |
| Redundancy index             | Co-occurrence with other alerts within N seconds                 |
| Equity slice                 | All metrics stratified by relevant subgroups                     |
| False-positive estimate      | Where calculable, from chart review or registry comparison       |

Two important caveats:

1. **Acceptance rate is not the same as benefit.** A user can accept
   a recommendation that is wrong, or override a recommendation that
   is right. The audit must not assume otherwise.
2. **Override rate without override-reason analysis is not
   actionable.** A 95% override rate where 95% of overrides are
   "already addressed" is a different problem than a 95% override
   rate where 95% are "alert not relevant."

### Stage 3 — Classify fatigue risk

For each alert, assign a fatigue-risk tier using this rubric. The
thresholds are **placeholders** for governance-committee tuning —
the skill cannot set them for a specific organization.

| Tier        | Pattern                                                                                    |
|-------------|--------------------------------------------------------------------------------------------|
| **Red**     | Very high firing rate AND very high override rate AND no concentration of override reasons |
| **Orange**  | High override rate with concentrated override reasons suggesting clear refinement target   |
| **Yellow**  | Moderate override rate with workflow friction (long time-to-action, repeat fires)          |
| **Green**   | Override rate low, time-to-action short, acceptance pattern stable, equity slice clean     |
| **Unknown** | Metrics unavailable or owner unknown                                                       |

For each alert, also tag any of the following modifiers:

- `safety-floor` — alert exists to enforce a non-negotiable safety
  rule (e.g. contraindicated combination). Safety-floor alerts are
  reviewed for **precision**, not for retirement.
- `regulatory-required` — alert exists because a regulator or
  accreditor requires it. Retirement requires a regulatory analysis,
  not just an override-rate analysis.
- `patient-facing` — alert surfaces to a patient or caregiver, not a
  clinician. Different fatigue dynamics apply.
- `vendor-default` — alert ships from the EHR or content vendor.
  Local tuning may be limited; recommendation may be to escalate to
  vendor rather than retire.
- `recently-deployed` — alert deployed within last 90 days. Metrics
  are not yet stable; defer classification.

### Stage 4 — Recommend an action per alert

For each in-scope alert, write a one-paragraph recommendation in one of
five buckets:

1. **Retire.** The alert is firing too often, being overridden too
   often, has no concentrated refinement signal, is not a safety
   floor, and is not regulatory-required. Recommend retirement with
   a 30-day shadow window before full removal so the team can
   confirm no unexpected dependency.
2. **Refine — tighten eligibility.** Override reasons concentrate on
   "patient not eligible" or "already addressed." Propose specific
   suppression rules (e.g. suppress if existing order, suppress if
   already on care plan, suppress if recent acknowledgment).
3. **Refine — change surface.** Override reasons concentrate on
   "interrupted at wrong time." Propose moving from interruptive
   modal to non-interruptive banner, infobutton, or order-set
   default.
4. **Refine — change payload.** Acceptance is moderate but
   time-to-action is long. Propose simplifying title, reducing
   options to one primary action, or moving evidence link below the
   fold.
5. **Keep.** Tier is Green or the alert is a safety floor performing
   within target.

Every recommendation must specify:

- The **expected change** in firing rate, override rate, or
  time-to-action.
- A **re-audit window** (typically 60–180 days).
- A **roll-back trigger** if the refinement worsens metrics or
  produces new safety events.

### Stage 5 — Portfolio-level synthesis

Roll up the per-alert recommendations into a portfolio view:

- **Retirement candidates** with estimated reduction in
  alert-impressions per user-day.
- **Refinement candidates** grouped by refinement type (eligibility,
  surface, payload).
- **Safety floors and regulatory-required alerts** confirmed kept,
  with their owners.
- **Unknown / orphan alerts** flagged for ownership re-assignment.
- **Equity findings** — alerts where the override rate or firing
  rate differs materially across patient subgroups, escalated to
  health-equity review.
- **Vendor-package issues** — alerts where the recommendation
  requires a vendor change rather than local tuning.

Close with a one-page summary suitable for a governance-committee
meeting: number of alerts reviewed, number recommended for retirement,
expected reduction in alert burden per user-day (as a range, not a
point estimate), and the highest-priority safety considerations.

## Inputs

- `alert_inventory_summary` — de-identified summary of the alert(s)
  under review.
- `review_scope` — single alert, family, top-N, or full portfolio.
- `governance_context` — receiving committee.

## Outputs

- `alert_audit_report` — a markdown audit report containing the
  five-stage analysis, per-alert classification, recommendations,
  and a portfolio-level summary.

## Worked example (placeholder data)

> **Alert under review.** `<INTERNAL-ID>` — "Consider `<INTERVENTION
> CLASS>` for `<RISK CONDITION>` if eligible." Target user:
> `<clinician role>`. Surface: interruptive modal at order-sign.
> Owner: `<NAME, ROLE>`. Last reviewed: `<YYYY-MM>`.
>
> **Metrics (de-identified, last 90 days).**
>
> - Firing rate: `<N>` per 1,000 eligible encounters.
> - Override rate: `<87%>`.
> - Override-reason distribution: 62% "already on order," 19%
>   "contraindicated," 11% "patient declined," 8% other.
> - Median time-to-action: `<22s>`.
> - Same-patient repeat rate: `<3.4>` fires per encounter.
> - Equity slice: override rate `<+9 percentage points>` on
>   `<subgroup>` vs. portfolio average.
>
> **Classification.** Orange (high override, concentrated reasons,
> clear refinement target). Modifiers: not a safety floor; not
> regulatory-required; not vendor-default.
>
> **Recommendation.** Refine — tighten eligibility. Add suppression
> rules: (1) suppress if `<intervention class>` already on active
> medication list; (2) suppress if contraindication documented in
> `Condition` or `AllergyIntolerance`; (3) suppress if previously
> acknowledged within `<window>` for same encounter.
>
> Expected impact: firing rate down ~`<60–70%>`, override rate down
> to ~`<50%>` range, time-to-action improved as cognitive load drops.
> Re-audit at `<90 days>`. Roll-back trigger: any new patient-safety
> event linked to the alert, or override rate worsens.
>
> **Equity flag.** Subgroup gap requires separate review — the
> refinement above may or may not narrow it, and a health-equity
> reviewer should look at the eligibility logic for upstream bias.
>
> **Reviews required before action.** CDS governance committee,
> clinical owner, P&T if related to medication, equity reviewer.

All values in angle brackets are placeholders. **The skill does not
recommend specific clinical thresholds, drugs, or doses.**

## Limitations

- The skill works from **summary statistics** the team provides. It
  does not query EHR audit logs, does not access patient records, and
  cannot validate the metrics it is given.
- Override-reason analysis is only as good as the override-reason
  picklist on the alert. A free-text override field collapses to
  "other" and the audit will recommend re-design before retirement.
- The skill cannot assess clinical appropriateness of individual
  alert content. That requires the clinical owner and, where
  relevant, P&T review.
- The skill cannot determine regulatory status of an alert.
- The skill cannot replace human chart review for false-positive
  estimation; it can only structure the question.
- Patient-facing alert dynamics differ substantially from
  clinician-facing dynamics; coverage here is clinician-facing first.
- Equity findings require a qualified reviewer and dedicated
  follow-up; the skill surfaces them, it does not resolve them.

## Sources (URL-only, license-verified permissive)

- https://github.com/cds-hooks/sandbox-cds-services (Apache-2.0) —
  pattern reference for CDS card structure and indicator levels,
  used here for thinking about payload and surface.
- https://github.com/HL7/cds-hooks (Apache-2.0 for code) — pattern
  reference for hook taxonomy used in scoping the audit by trigger
  type.
- https://github.com/cds-hooks/cds-validator (MIT) — pattern
  reference for the shape of a valid CDS response, used
  conceptually when discussing payload tightness.
- https://github.com/hapifhir/hapi-fhir (Apache-2.0) — pattern
  reference for FHIR resource names cited in suppression-rule
  examples.
- https://github.com/mitre/fhir-server (Apache-2.0) — pattern
  reference for FHIR server shape, supporting the eligibility-rule
  discussion.

**Source-thinness disclosure.** Permissively licensed (MIT / Apache /
BSD / ISC / Unlicense) repositories specifically about alert-fatigue
*audit methodology* are essentially absent on public GitHub —
override-rate analytics live inside EHR vendors and academic
informatics groups, not in open repos. The sources above are
infrastructure-level references whose existence and shape inform the
vocabulary used here. No proprietary alert text, no copyrighted
override picklist, and no clinic-specific configuration is reused.

## Mandatory disclaimer (repeated)

This skill describes methodology for DESIGNING and auditing clinical
decision support systems. It is not itself a CDS, does not diagnose,
and does not recommend treatment. CDS deployments in real clinical
settings require qualified clinical informatics staff, formal
validation against clinical reference standards, regulatory clearance
where applicable (e.g., FDA Software as a Medical Device), and ongoing
post-deployment surveillance. **No skill output may be deployed in
care delivery without that full process.**
