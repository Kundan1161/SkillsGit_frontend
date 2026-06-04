---
id: skillsgit-curated/ops-rfp-author
version: 1.0.0
name: RFP Author
description: Drafts a focused Request for Proposal — scope, evaluation criteria, timeline, response format, technical and security sections, and scoring transparency — that gets useful comparable answers from vendors instead of a wall of unstructured marketing prose.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: operations
tags: [niche:vendor-management, procurement, rfp, sourcing, rfx, rfi, vendor-evaluation, contracts]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - rfp
  - request for proposal
  - rfp template
  - rfx
  - rfi
  - request for information
  - rfq
  - sourcing
  - vendor proposal
  - bid request
  - procurement
  - solicitation
example_invocations:
  - "Draft an RFP for a managed SOC service for our 800-person company."
  - "Write the RFP for replacing our HRIS — we have three vendors invited."
  - "Help me turn this draft scope into a proper RFP with evaluation criteria."
inputs:
  - name: scope_summary
    type: text
    required: true
    description: What is being procured — the problem to solve, the rough scale, the must-haves, the timing, and any vendors already in mind or already excluded.
  - name: organization_context
    type: text
    required: false
    description: Industry, size, geography, regulatory regime, existing stack, and the buying entity's signing authority and procurement process.
  - name: evaluation_criteria
    type: text
    required: false
    description: Pre-agreed criteria and weights — typically the output of the vendor-selection-scorecard skill. The RFP echoes these so vendors know how they will be judged.
  - name: timeline_constraints
    type: text
    required: false
    description: Hard dates — board approval, fiscal-year close, regulatory deadline, contract renewal, project go-live.
outputs:
  - name: rfp_document
    type: markdown
    description: A complete RFP with cover page, instructions to respondents, scope, technical and security requirements, response format, evaluation methodology, timeline, and commercial terms.
  - name: response_template
    type: markdown
    description: A structured response template vendors fill out, designed so answers are comparable side-by-side.
  - name: evaluator_brief
    type: markdown
    description: Internal-only brief explaining how the team will read responses, what good and bad answers look like, and how scoring rolls up.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when the team has decided to formally invite proposals from multiple vendors and needs a document that produces comparable answers. The threshold for "merits an RFP" varies by organization, but typical triggers are: spend above a defined approval threshold (commonly $100k+ annual or $250k+ total), a regulated buy (financial services, healthcare, public sector) where a documented selection process is required, or a strategic purchase where the team wants the rigor of comparing three to five vendors against a single specification.

The skill is not the right tool for an RFI (Request for Information — a broader market scan to see what is even available; lighter document, no scoring). It is also not the right tool for an RFQ (Request for Quotation — when the spec is fully defined and the only open variable is price; much shorter document). It is the right tool for an RFP, where the spec is partially defined, the team is open to different solution approaches, and the choice will depend on a multi-factor evaluation.

A good RFP is shorter than most teams expect. The dominant failure mode of an RFP project is the document bloats to 80+ pages, vendors invest minimal effort because the response burden is high and the signal-to-noise looks bad, and the team gets a stack of partially-completed responses that take weeks to compare. The skill targets a length where serious vendors will engage fully and the team can read every response in a day — typically 15 to 30 pages including appendices, with a response template that produces apples-to-apples comparisons rather than free-form essays.

## How to apply

1. **State the problem before stating the solution.** The first page of the RFP describes the business problem the team is trying to solve, not the product category. "We process 2 million customer interactions per month across web and call center, and we cannot currently identify the same customer across the two channels in under 24 hours, which is hurting our retention efforts" is a problem statement. "We are buying a CDP" is a category. Vendors respond more usefully to problem statements because they can propose approaches the team has not preconceived. The category goes in the second paragraph as the team's current best guess.

2. **Define scope with what is in and what is explicitly out.** A scope without explicit exclusions invites scope creep in proposals — vendors propose everything they sell, hoping something sticks. The "out of scope" subsection prevents that: "out of scope for this RFP: replacing the data warehouse, redesigning the analytics layer, professional services engagements above $50k." Excluding professional services explicitly is particularly useful because it surfaces vendors who can only deliver via heavy services.

3. **List must-haves up front as eligibility criteria.** Same logic as the scorecard's gate: a vendor that cannot meet must-haves should not invest in a response and the team should not invest in reading one. Phrase must-haves as concrete contractual statements ("Vendor must hold SOC 2 Type 2 dated within the last 12 months and provide a copy under NDA upon request"), not as marketing language ("vendor must be secure"). Add a single yes/no question for each must-have at the top of the response template; a no anywhere is an automatic decline.

4. **Publish the evaluation criteria and weights — actually publish them.** Vendors who know how they will be scored give better-targeted answers. Teams worry that publishing weights "lets vendors game the response." That is precisely the point: a vendor who games their response by putting effort into the highest-weighted areas is allocating their proposal-writing budget the same way the team is allocating its evaluation budget. The team has done a service by aligning incentives. Hide weights only when the team is not confident in them — in which case fix the weights, do not hide them.

5. **Force structured responses with a response template, not a freeform Word document.** The response template is a fillable structure: each criterion has a heading, a required answer field with a stated character limit (200 to 500 words per criterion is plenty), a "supporting evidence" field for documentation references, and a yes/no/partial field for binary requirements. Two RFP responses returned in this format can be diffed in a spreadsheet. Two RFP responses returned as freeform 60-page Word documents cannot be compared without four days of work per evaluator. The template format is the single highest-leverage choice in RFP design.

6. **Write the technical section as questions the vendor must answer, not requirements they must check.** "Does the vendor support SSO?" is a checkbox; every vendor will say yes. "Describe how SSO is implemented in your product — protocols supported, how user provisioning works, what happens when an SSO provider is unavailable, and provide a link to your public SSO documentation" gets a comparable substantive answer. Phrase each technical line item as an open question with bounded length. Twenty good open questions beat 200 checkboxes.

7. **Build the security section from a recognized framework.** Do not invent the security questionnaire; reuse a recognized one (CAIQ, SIG, or a subset of NIST 800-53 or ISO 27001 controls relevant to the buy). Vendors recognize standard questionnaires and have answer libraries; their responses will be faster and more accurate. The skill outputs a curated subset rather than the full 300-question CAIQ, because a vendor asked 300 generic security questions returns boilerplate. Curate 25 to 50 that matter for the specific buy.

8. **Make commercials transparent and require a standard pricing layout.** Pricing comparisons across vendors are the most frequently distorted part of an RFP — one vendor quotes by user, another by event, another by seat with tiers. The RFP requires every vendor to fill the same pricing table: list price per unit, projected volume from the scope, year-1 cost, year-2 cost, year-3 cost, implementation cost, ongoing professional services estimate, total 3-year commitment. Add a free-form box for the vendor to propose an alternative pricing model, but the standard table is mandatory. Vendors will resist; the team can hold the line because non-comparable pricing is the team's problem, not the vendor's.

9. **Specify the timeline with dates, not durations.** "Responses due in 3 weeks" forces vendors to do timezone math. "Responses due by 5pm UTC on Friday 12 June 2026" is unambiguous. The timeline section names dates for: RFP issued, written-question deadline, written-question answers published, response due, shortlist notification, demo days, reference-call window, decision communicated, contract negotiation, target signature date. Vendors who cannot fit the timeline self-select out, which is a useful filter.

10. **Run a written-question window and publish the answers to all vendors.** Every serious RFP allows vendors to submit clarifying questions in writing during a defined window. The team consolidates the questions, removes vendor identifiers, answers them, and publishes the full set to all invited vendors. This prevents one vendor from getting an information advantage and reduces the number of bad responses driven by ambiguity. It also surfaces ambiguities in the RFP itself that the team did not see — vendor questions are free QA on the document.

11. **Name the contract terms that are non-negotiable up front.** Vendors invest more in RFP responses when they know which contract terms will be in the final paper. Include a one-page summary of the team's standard terms — DPA without redlines on a named list of clauses, mutual indemnification, audit rights, SLA structure, termination for convenience after year one with a stated notice period, exit-assistance terms. This is not the contract; it is a directional statement so vendors know what they are signing up to. Vendors who flag a deal-breaker now save the team six weeks of negotiation that would end at impasse.

12. **Specify how scoring will be communicated to non-winning vendors.** The RFP closes with a short section on the team's debrief commitment: shortlist notification by date X, non-winners receive a one-page summary of their score and the score gap to the winner, and an offer of a 30-minute call to discuss. Vendors invest more when they expect honest feedback. The cost is one hour per non-winner; the benefit is that those vendors return better proposals next time and the team's reputation in the vendor community improves, which improves the next RFP's response quality.

### Standard RFP layout

The output document uses these sections in this order:

1. `# Request for Proposal: <subject>`
2. `## 1. Problem statement` — business problem first, category second.
3. `## 2. Scope` — in scope, out of scope.
4. `## 3. Eligibility / Must-haves` — pass/fail gate.
5. `## 4. Organization context` — size, industry, geography, existing stack.
6. `## 5. Functional requirements` — open questions, grouped by capability area.
7. `## 6. Technical requirements` — architecture, integration, scale.
8. `## 7. Security and compliance` — curated questionnaire (25–50 items).
9. `## 8. Implementation and onboarding` — expected timeline, resourcing, training.
10. `## 9. Commercial requirements` — standard pricing table, term, payment.
11. `## 10. Contract terms summary` — non-negotiable clauses.
12. `## 11. Evaluation methodology` — criteria, weights, scoring scale, decision-makers.
13. `## 12. Process and timeline` — dated milestones.
14. `## 13. Submission instructions` — format, channel, contact, late submission rule.
15. `## 14. Appendices` — response template, sample data shapes, current-state diagrams, glossary.

### Composition rules

- **Under 30 pages total, with appendices.** A longer RFP gets shallower responses.
- **Every requirement maps to a scoring criterion.** A requirement no one will score is decoration.
- **One question per question.** "Describe your SSO and audit logging" is two questions. Split.
- **Bounded response lengths.** 200–500 words per open question is the sweet spot.
- **No "describe your company culture" questions.** They cannot be scored consistently and they waste vendor effort.
- **The team commits to the timeline.** Slipping the team's milestones (extending the response window, missing the shortlist notification date) damages the response quality of the next RFP because vendors notice.

## Inputs

- **Scope summary (required, text).** What is being bought, scale, must-haves, timing, any known vendor pool.
- **Organization context (optional, text).** Industry, size, geography, regulatory regime, existing tooling, signing-authority structure.
- **Evaluation criteria (optional, text).** Pre-agreed criteria and weights — feed the output of the vendor-selection-scorecard skill in here for consistency.
- **Timeline constraints (optional, text).** Hard dates that anchor the process.

## Outputs

A complete RFP document, a separate response template structured so answers are comparable, and an internal-only evaluator brief explaining what good and bad answers look like for each section. The evaluator brief is not shared with vendors; it is the calibration document for the team.

## Examples

### Worked example: managed SOC service

**Input scope summary:** "Managed Security Operations Center service for our 800-person company. We currently have a small internal security team and need 24x7 monitoring of our cloud workloads (AWS), endpoints (~1,500 devices), and SaaS app logs (~30 critical apps). Target go-live in 90 days. Must integrate with our existing SIEM (Splunk Cloud). Three vendors invited based on prior RFI."

**Input organization context:** "Mid-market SaaS, US headquartered, primary data in us-east-1 and eu-west-1. SOC 2 Type 2 required by our customers. Signing authority for >$250k is the CISO with CFO co-sign. Procurement process requires written-question Q&A window of 5 business days."

**Input evaluation criteria:** "From the scorecard skill: Fit-to-need 40%, Implementation 15%, Operability 20% (detection quality, alert handling), Cost 10%, Security/risk 15%. Five-point scale, anti-bias rules from the scorecard skill."

**Input timeline constraints:** "Decision needed by August 15 to align with budget cycle. Service must be operational by October 31."

**Expected output (excerpted):**

> # Request for Proposal: Managed SOC Service
>
> **Issued by:** [Company]
> **Date issued:** 2026-05-14
> **Response due:** 2026-06-13 at 17:00 UTC
> **Contact:** rfp-soc@[company].com — all questions in writing to this address only
>
> ## 1. Problem statement
>
> Our internal security team of four operates business hours only, while our customer-facing services run 24x7 globally. We need eyes on the security telemetry — cloud workload alerts, endpoint detections, SaaS audit logs — at all hours, with the response speed our customer commitments require. We are not buying a tool replacement; we already operate Splunk Cloud as our SIEM. We are buying a service team that monitors our existing tooling, triages alerts to a documented playbook, and escalates to our team for in-scope incidents.
>
> ## 2. Scope
>
> **In scope:**
> - 24x7x365 monitoring of alerts ingested into our Splunk Cloud instance
> - Triage to a jointly-maintained playbook with documented escalation criteria
> - Phone and pager-tool escalation to our on-call within stated SLAs
> - Monthly metrics review and quarterly playbook tuning
> - Threat intelligence enrichment for triaged alerts
>
> **Out of scope:**
> - Replacing or relocating our SIEM
> - Endpoint detection product replacement (we run [vendor] EDR; the MSSP consumes its alerts)
> - Incident response retainer services (we have a separate retainer)
> - Vulnerability management or pen testing
> - Compliance consulting
>
> ## 3. Eligibility (pass/fail)
>
> Respond yes/no to each on the response template's first page. Any "no" results in a decline.
>
> 1. Vendor holds SOC 2 Type 2 dated within the last 12 months and will provide a copy under NDA before contract signature.
> 2. Vendor's primary SOC operates 24x7 with no follow-the-sun handoff gaps documented in their availability SLA.
> 3. Vendor supports Splunk Cloud as a primary SIEM (not a workaround integration).
> 4. Vendor will sign our standard DPA with the sub-processor and audit clauses unmodified, or will commit in writing to do so before contract.
> 5. Vendor can be operational on our environment within 90 days of contract signature.
>
> ## 4. Organization context
>
> - 800 employees globally; security team of four; engineering team of approximately 200
> - AWS primary, with workloads in us-east-1 (primary) and eu-west-1
> - Approximately 1,500 managed endpoints across Mac (60%) and Windows (40%)
> - SIEM: Splunk Cloud, retention 90 days hot, 12 months cold
> - EDR: [Vendor]
> - Identity: Okta
> - Communications/ticketing: Slack and PagerDuty
>
> ## 5. Functional requirements
>
> Respond in the response template, 200–500 words per item, with documentation links.
>
> **5.1 Triage methodology.** Describe how your team triages an alert from arrival to disposition. Include role structure (tier 1, tier 2, named senior analysts), the playbook authoring model (vendor-owned, joint, customer-owned), and the median and 95th-percentile time-to-triage you commit to contractually.
>
> **5.2 Splunk Cloud integration.** Describe the specific integration approach with Splunk Cloud — does your team work inside our instance with named accounts, does data egress to your platform, or both? Address audit-log visibility on your team's queries inside our environment.
>
> **5.3 Escalation to our on-call.** Describe your escalation mechanism to our PagerDuty. What information accompanies an escalation? What feedback loop closes from our on-call back to your tier-1 about whether the escalation was useful? How do you tune false-positive rates over time?
>
> **5.4 Tuning cadence.** Describe your detection-tuning rhythm — frequency, who attends, what gets measured (precision/recall, time-to-triage, false-positive rate). What does the first 90 days of tuning look like for a new customer?
>
> [...continued, 12 functional requirement items total]
>
> ## 6. Technical requirements
>
> **6.1 Splunk Cloud access architecture.** Describe authentication, authorization, audit logging, and data residency for your team's Splunk access. We require named accounts with our SSO; service accounts are not acceptable for human access.
>
> **6.2 Data egress.** If any of our telemetry leaves Splunk Cloud for processing in your environment, describe what data, where it is processed, retention, and the data-classification controls.
>
> [...continued, 8 technical items]
>
> ## 7. Security and compliance
>
> Curated 30-item subset of CAIQ v4 plus 6 service-specific questions covering analyst vetting, separation of duties between customers, audit rights, and breach notification SLAs. (See Appendix C for the full list and response format.)
>
> ## 8. Implementation and onboarding
>
> **8.1 Day-1 to operational timeline.** Provide a week-by-week implementation plan for the 90-day window. Identify dependencies on our team and the FTE-hours expected from us per week.
>
> **8.2 Playbook authoring.** Provide a sample initial playbook (one detection scenario) you would propose for us based on Section 4 context. We will use this as a quality signal.
>
> **8.3 Knowledge handover from your team to ours.** If we ever exit this relationship, describe the handover process — runbooks, tuning history, open-case state.
>
> ## 9. Commercial requirements
>
> Complete the pricing table in Appendix A. The table covers:
> - Year 1 base service fee (annual)
> - Year 2 base service fee (committed cap)
> - Year 3 base service fee (committed cap)
> - One-time implementation fee
> - Per-incident charges (if any) — flat fee, hourly, or none
> - Per-additional-endpoint or per-additional-app charges as we grow
> - Optional services pricing (threat intel uplift, etc.)
>
> Pricing is fixed in the response. Alternative pricing models may be proposed in a separate text box but the standard table must be completed.
>
> ## 10. Contract terms summary
>
> The following terms are non-negotiable. Flag any deal-breakers in your response.
>
> - Our standard DPA, unmodified on sub-processor (with notification) and audit-rights clauses
> - Mutual indemnification with stated caps
> - Termination for convenience after month 13, with 90 days notice
> - 30 days of transition-assistance hours included at no incremental cost on termination
> - SLA structure: time-to-triage with service credits; not lump-sum availability
> - Annual audit right exercisable on 30 days notice
>
> ## 11. Evaluation methodology
>
> Responses are scored on a 5-point scale, criteria weights as below:
>
> | Category | Weight |
> |---|---|
> | Fit-to-need (functional + technical sections) | 40 |
> | Implementation feasibility | 15 |
> | Operability (detection quality, alert handling) | 20 |
> | 3-year total cost | 10 |
> | Security and risk posture | 15 |
>
> Each evaluator scores independently before group calibration. Tie-break: lower 3-year TCO. Decision-maker: CISO with CFO sign-off.
>
> Three vendors are invited. Two will be shortlisted for demos and references. One will be selected.
>
> ## 12. Process and timeline
>
> | Milestone | Date | Notes |
> |---|---|---|
> | RFP issued | 2026-05-14 | |
> | Written-question deadline | 2026-05-22 17:00 UTC | Email to rfp-soc@... |
> | Q&A published to all vendors | 2026-05-27 | Anonymized |
> | Response due | 2026-06-13 17:00 UTC | Late = not accepted |
> | Shortlist notification | 2026-06-23 | All three notified |
> | Demos | 2026-07-06 to 2026-07-10 | 90-minute slots |
> | Reference calls | 2026-07-13 to 2026-07-17 | 3 refs per shortlisted vendor |
> | Decision communicated | 2026-08-04 | Winner + non-winner debriefs |
> | Target contract signature | 2026-08-25 | |
> | Service operational | 2026-10-31 | |
>
> ## 13. Submission instructions
>
> - One PDF of the response template, plus appendices as separate files
> - Email to rfp-soc@... with subject `[VENDOR NAME] SOC RFP Response`
> - Total response size under 50 MB
> - Late submissions are not accepted; if your team needs an extension, request it in the written-question window
> - Non-winners will receive a one-page score summary and an offer of a 30-minute debrief call within 10 business days of decision
>
> ## 14. Appendices
>
> - **A.** Response template (structured Word/markdown form, fillable)
> - **B.** Standard pricing table
> - **C.** Curated security questionnaire (30 + 6 items, with response format)
> - **D.** Current-state architecture diagram (Splunk Cloud, EDR, AWS log sources)
> - **E.** Glossary

## Limitations

- The RFP is a procurement instrument, not a contract. A vendor commitment in an RFP response is not legally binding unless it is referenced and incorporated into the signed agreement. The skill outputs the document; the team must make sure key vendor commitments are pulled into the final contract.
- A high-quality RFP can still produce a bad decision if the evaluation step is run badly. The skill pairs with the vendor-selection-scorecard skill (for the criteria and scoring discipline) and the vendor-tco-modeler skill (for the financial comparison). An RFP issued without an evaluation framework set in advance is process for its own sake.
- The skill cannot predict the regulatory or organization-specific procurement rules the team operates under. Public-sector procurement, regulated financial services, and some healthcare buyers have prescribed RFP formats and legal review steps that override sections of this template. Run the output past the internal procurement and legal teams before issuing.
- Vendors will partially answer the RFP. The response template enforces structure; it does not enforce quality. Plan for a clarification round after responses arrive — a one-week window where the team can ask three to five clarifying questions of each respondent. Build that window into the timeline.
- The skill is opinionated toward shorter, structured RFPs. Some teams (and some vendors) expect 80-page RFPs with extensive narrative. The shorter format works better, but a team operating in an environment that expects the longer form should adjust expectations with stakeholders before issuing this template's output.
- A no-bid response is signal, not noise. If an invited vendor declines to bid, ask why in writing. The reasons — timeline too short, scope mismatch, a must-have they cannot meet — often expose flaws in the RFP that the bidding vendors are quietly working around.

## Sources reviewed

- https://github.com/SalesforceLabs/ProposalForce
- https://github.com/tractorjuice/arc-kit
- https://github.com/mgifford/open-source-contracting
- https://github.com/makegov/awesome-procurement-data
- https://github.com/Funkmyster/awesome-supply-chain
- https://github.com/accordproject/template-archive
- https://github.com/open-agreements/open-agreements
