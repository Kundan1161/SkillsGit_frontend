---
id: skillsgit-curated/legal-soc2-readiness-assessor
version: 1.0.0
name: SOC 2 Readiness Assessor
description: Gap-analyze a company against SOC 2 Trust Service Criteria and produce a remediation plan with controls to design, evidence to collect, and period requirements.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: legal
tags: [niche:privacy-compliance, soc2, trust-services-criteria, readiness, controls, evidence, audit-prep]
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
  - soc 2 readiness
  - soc 2 gap analysis
  - trust service criteria
  - tsc gap
  - soc 2 controls
  - type 1 readiness
  - type 2 readiness
  - audit evidence
  - control narrative
  - readiness assessment
  - policy library
  - soc 2 remediation
example_invocations:
  - "Run a SOC 2 readiness assessment for our 40-person SaaS — Security, Availability, and Confidentiality criteria."
  - "We have eight weeks until a Type I audit window. Build a gap list and a remediation plan with owners and dates."
  - "Walk us through what evidence to start collecting now to make a Type II observation period clean."
inputs:
  - name: company_profile
    type: text
    required: true
    description: Plain-language description of the company — product type, team size, cloud architecture summary, customer segment, current security maturity, prior audit history if any.
  - name: scope_criteria
    type: choice
    required: false
    description: Which Trust Service Criteria categories are in scope. Security is mandatory; the others are added based on customer requirements.
    choices: [security_only, security_availability, security_availability_confidentiality, security_processing_integrity, security_privacy, all_five]
  - name: audit_type
    type: choice
    required: false
    description: Target audit type. Type I is point-in-time design; Type II is operating effectiveness over a period (typically 3-12 months).
    choices: [type_1, type_2_short_period, type_2_full_period, undecided]
  - name: target_window
    type: text
    required: false
    description: Approximate target audit window — for example, "Type I in 10 weeks" or "Type II observation period starting Q3."
  - name: current_artifacts
    type: text
    required: false
    description: Inventory of policies, controls, evidence sources already in place — even rough lists help calibrate the gap.
outputs:
  - name: readiness_report
    type: markdown
    description: A structured readiness report with scope analysis, control-by-control gap assessment, prioritized remediation plan with owners and dates, evidence collection schedule, and audit-window recommendation.
  - name: readiness_json
    type: json
    description: Structured fields — tsc_in_scope, audit_type, gap_count_by_category, top_remediation_items, evidence_streams_required, observation_period_recommendation, estimated_weeks_to_readiness.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# SOC 2 Readiness Assessor

> **Important — not legal advice and not an audit.** This skill produces a readiness assessment intended to surface gaps before an independent CPA firm conducts the SOC 2 examination. It is **not** a SOC 2 audit, does not produce a SOC 2 report, and is not a substitute for an examination by a licensed CPA in accordance with AICPA attestation standards. Only a licensed CPA firm can issue a SOC 2 report. The criteria, control activities, and points of focus referenced here are framed in general terms — your auditor's interpretation of any criterion governs your engagement, and your engagement letter and management assertion are the operative documents. Consult qualified counsel and your selected auditor for binding decisions on scope, criteria, and acceptable evidence. Where this skill says "design this control" or "collect this evidence," treat it as preparatory guidance to discuss with your auditor before relying on it.

## When to use

The natural entry points for this skill are the moment a sales conversation reveals that a SOC 2 report is a prerequisite for a deal, the moment leadership decides that SOC 2 is a strategic milestone for the next funding round or enterprise tier, the moment a customer's security review escalates the request from "willing to sign an NDA and review a policy" to "send the SOC 2 report," and the rough quarterly cadence of an internal program manager who is keeping a readiness program alive between audit windows. The earlier in this lifecycle the assessment is done, the cheaper the remediation. A team that begins readiness work six months before the desired audit will spend a fraction of what a team three weeks out spends, because the latter is buying its way out of evidence-window problems.

Use this skill for a fresh readiness check before any audit engagement, for a mid-program reset when a control owner leaves or a major architectural change is shipped, and for an annual recheck where prior-year posture is the baseline. Use it where the company is considering a switch between Type I and Type II, because that decision drives an evidence-collection program that materially differs in cost and lead time.

Do not use this skill in place of the auditor's planning. Once an engagement letter is signed, the auditor's request list and sampling approach take precedence over any general framework. The skill is useful for getting ready and for staying ready between audits; it is not a substitute for the auditor's work and should not be marketed internally as such.

A second important caution: do not use the skill to prepare a SOC 2 report. Only a licensed CPA firm performing an examination under AICPA attestation standards (specifically AT-C section 205 for SOC 2 engagements) may issue a SOC 2 report. Any artifact this skill produces is a readiness document, not an attestation.

## How to apply

A useful readiness exercise treats SOC 2 as a system rather than a checklist. The system has four moving parts: the criteria you commit to, the controls you design to satisfy them, the evidence those controls produce, and the period over which the evidence accumulates. The agent's job is to make those parts coherent. Move through the stages in order; the scoping decisions early on shape everything downstream.

### 1. Decide the scope of criteria

The Trust Services Criteria (TSC) are organized into five categories: Security (mandatory, often referred to as the common criteria), Availability, Processing Integrity, Confidentiality, and Privacy. Most first-time examinations cover Security alone, sometimes plus Confidentiality. Adding Availability is common for infrastructure-heavy services where customers care about uptime contractually. Processing Integrity is selected by services where the correctness of automated processing is the customer's primary concern (payments, data pipelines, supply chain). Privacy is selected where the service positions itself on consumer privacy — and adopting Privacy commits you to the AICPA privacy criteria, which overlap with but are distinct from GDPR or CCPA obligations.

Each added category brings additional criteria, additional control design, and additional evidence. The agent's recommendation should reflect the customer-driven reason for adding each category, not a desire for a more impressive report. Customers rarely read past the cover page, and the right answer is "the smallest scope that wins your deals."

### 2. Decide Type I or Type II

A Type I report attests that controls were suitably designed at a point in time. A Type II report attests that controls operated effectively over a period of time — typically three to twelve months. Customers increasingly want Type II, but a clean Type I is often the right first step because it forces the design work and produces a deliverable in a few months rather than most of a year.

The strategic move many teams make is "Type I first, then Type II starting the day after Type I." That sequence gives a customer-facing report quickly while the Type II observation period accrues evidence. The risk is that the Type II auditor will look more critically at controls the Type I auditor designed; a control that passed Type I as designed may fail Type II as operated.

### 3. Map controls to criteria

The auditor will work from the criteria, but the team works from controls. A control is a discrete activity — "access reviews are performed quarterly for production systems" or "vulnerability scans are run weekly against all internet-facing assets" — that contributes to one or more criteria. A useful exercise is to write the controls in plain language first, then map each to the criteria it serves. Controls that map to no criteria are still good practice but not in scope. Criteria that have no controls mapped to them are the gaps the agent must surface.

The auditor's framework will reference specific control activities and points of focus published by the AICPA. The agent should not pretend to memorize that framework verbatim; instead, the agent's job is to produce a list of plain-language controls that cover the substantive categories — governance, risk management, vendor management, access management, change management, system operations, monitoring, incident response, business continuity, vulnerability management, data classification, encryption, secure development, employee management, and physical security where applicable. Each plain-language control maps to one or more criteria categories. The auditor will translate to their framework during the examination.

### 4. Build the evidence catalog

For each control, identify the evidence stream — the artifact that demonstrates the control operated. Evidence categories common in modern SOC 2 engagements include: ticket-system tickets for change management and incident response, identity-provider logs for access management, code-review records for secure development, training-platform completion records for security awareness, vendor inventories with evidence-of-review timestamps, vulnerability scan reports, penetration test reports, business continuity test results, backup verification logs, employee onboarding and offboarding checklists, and policy acknowledgment records.

Two failure modes are common at this stage. The first is evidence that exists in principle but cannot be retrieved efficiently — "we do access reviews" but the records live in a private spreadsheet that the reviewer leaves behind on their personal drive. The auditor's request list will fail on this, even though the control is real. The second is evidence with gaps in the observation period — a quarterly review that happened in month one and month nine but not in months four through six. A Type II auditor will flag the gap and the report's exception will reduce its commercial value.

The agent should propose a centralized evidence catalog with a single owner per stream, a documented retention period, and a quarterly self-test where the evidence is pulled as if the auditor had asked.

### 5. Run the gap assessment

For each control area, score the readiness on a small scale (for example: designed and operating, designed but inconsistent, partially designed, missing). Anchor scores to specific observations rather than to opinions. "Designed but inconsistent" means the policy exists, the control owner can name what they do, but evidence shows the cadence has slipped. "Missing" means there is no control, no evidence, and no owner.

Produce a gap list that is prioritized. The priority order is not "do the easy ones first" but "do the controls that block the audit." A missing security incident response capability blocks the audit; a missing physical security control for a fully remote company is sometimes a non-issue depending on scope and the auditor's interpretation. The skill should rank gaps by audit-blocking severity, by effort, and by dependencies, and propose a sequence that ends with all blocking gaps closed before the desired audit window.

### 6. Remediation plan with owners and dates

Each gap becomes a remediation item with an owner, a target completion date, a verification step, and a dependency list. The agent should be honest about effort. Drafting a policy is a week. Implementing a centralized identity provider with SCIM and conditional access where there isn't one is months. Getting a vendor inventory cleaned up enough to pass auditor scrutiny is weeks of cross-functional time, not days. A remediation plan whose schedule shows "policy drafting" and "control implementation" running in parallel with the same person owning both is fiction.

The agent should also flag remediations that have lead-time floors regardless of effort. Penetration testing requires a vendor engagement that is rarely possible within two weeks. Background-check programs need a vendor and a privacy review. Insurance reviews need broker involvement. The plan should put these on the critical path.

### 7. Observation period strategy (Type II)

For a Type II engagement, the observation period is itself a deliverable to plan. Common periods are three months for a first Type II, six months for a subsequent one, and twelve months for the steady state. A clean observation period means every control operated as designed throughout, with evidence preserved.

The strategy question is when to start the observation period. Starting it before the design work is complete guarantees exceptions. Starting it after the design work is complete plus a stabilization buffer (typically two to four weeks of "test runs" where the team operates the controls and finds the breakages) produces a cleaner report. The agent should propose an observation-period start date that follows the close of the highest-priority gaps with a stabilization buffer, and an end date that aligns with the desired audit window.

### 8. Pre-audit dress rehearsal

Two to four weeks before the audit window, run a dress rehearsal: pull the evidence catalog as if the auditor had asked, walk through each control with its owner, look for the embarrassing gaps that only show up under pressure. Fix what can be fixed; document what cannot. The dress rehearsal is the difference between an audit that produces no exceptions and an audit whose report has a paragraph the sales team has to explain on every call for a year.

## Inputs

The skill expects a profile of the company and is materially improved by an inventory of existing artifacts. The scope of criteria and the audit type drive depth; if undecided, the skill should default to "Security only, Type I in approximately twelve weeks" and let the user override.

## Outputs

The Markdown report contains scope analysis, gap assessment by control area, prioritized remediation plan with owners and dates, evidence catalog and collection schedule, observation-period recommendation, and a dress-rehearsal plan. The JSON output is suitable for piping into a program-management tool — criteria in scope, audit type, gap count by category, top remediation items, evidence streams required, observation-period recommendation, and estimated weeks to readiness.

## Examples

A fifty-person SaaS company wants Security and Confidentiality, Type I in ten weeks, with Type II observation starting immediately after. The skill scopes the criteria, identifies the access-management and change-management controls as the most expensive remediations, recommends an identity-provider rollout on the critical path, builds an eight-week remediation schedule with a two-week buffer before audit fieldwork, and proposes a six-month Type II observation starting at audit close.

A series-A startup with a remote-only team wants the lightest credible SOC 2. The skill recommends Security-only Type I, defers Privacy and Processing Integrity, identifies a missing vendor inventory and an inconsistent code-review record as the priority gaps, and recommends starting the observation period for a future Type II only after the next round of customer-driven scope expansion forces it.

## Limitations

This skill prepares a company for an audit; it does not perform one and does not produce a SOC 2 report. Auditor interpretation varies, and the controls and evidence acceptable to one CPA firm may be insufficient for another. The criteria evolve; the AICPA periodically updates Trust Services Criteria and points of focus. Local engagement decisions — sampling, materiality thresholds, the precise wording of management's assertion — are auditor-led and out of scope here. Vendor and tool recommendations are out of scope; the skill describes what is needed, not what to buy.

## Sources reviewed

- https://github.com/strongdm/comply
- https://github.com/PehanIn/ISO-27001-2022-Toolkit
- https://github.com/ElNaboulsi/ISO-27001-2022-SoA-template
- https://github.com/theopenlane/awesome-compliance
- https://github.com/ethyca/fides
