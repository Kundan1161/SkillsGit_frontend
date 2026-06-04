---
id: skillsgit-curated/legal-vendor-security-review
version: 1.0.0
name: Vendor Security and Privacy Review
description: Evaluate a vendor's security and privacy posture before contract signing — review certifications, breach history, data flows, sub-processors, deletion guarantees, and contractual safeguards.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: legal
tags: [niche:privacy-compliance, vendor-review, third-party-risk, soc2, iso27001, dpa, sub-processors]
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
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - vendor security review
  - third party risk
  - vendor questionnaire
  - sub processor review
  - data processing agreement review
  - dpa review
  - soc 2 report review
  - iso 27001 vendor
  - vendor breach history
  - tprm
  - procurement security
  - subprocessor list
example_invocations:
  - "Review this SOC 2 Type II report excerpt and the vendor's security questionnaire — flag the gaps."
  - "We're about to sign with an analytics vendor that processes user events. Walk me through what to demand in the DPA."
  - "Build a vendor risk score for this AI sub-processor including breach history and data residency concerns."
inputs:
  - name: vendor_name
    type: text
    required: true
    description: Legal entity name of the vendor under review, plus trading name if different.
  - name: vendor_materials
    type: text
    required: false
    description: Pasted excerpts or summaries from the vendor — questionnaire answers, attestation reports (SOC 2, ISO 27001 certificate or Statement of Applicability summary), trust-center pages, sub-processor lists, breach disclosures, and any prior contracts.
  - name: data_in_scope
    type: text
    required: true
    description: What personal or business data the vendor will process — categories, sensitivity, volume, jurisdictions of data subjects, and whether special categories (health, children, biometric, financial, credentials) are involved.
  - name: integration_pattern
    type: choice
    required: false
    description: How the vendor will integrate with the controller's systems. Drives the data-flow review.
    choices: [saas_with_export, embedded_js_sdk, server_to_server_api, on_prem_software, browser_pixel, agent_in_environment, model_provider, other]
  - name: regulatory_anchor
    type: choice
    required: false
    description: Primary regime the buyer must satisfy through this vendor relationship.
    choices: [gdpr, ccpa_cpra, hipaa, pci_dss, soc2, iso27001, glba, ferpa, multi, none_specific]
outputs:
  - name: vendor_review_report
    type: markdown
    description: Structured review with executive summary, certification analysis, data-flow map narrative, sub-processor concerns, breach history findings, contractual recommendations, residual risk classification, and approval recommendation.
  - name: vendor_review_json
    type: json
    description: Structured fields for vendor inventory — vendor_name, data_categories, jurisdictions, attestations_held, attestations_validated, sub_processor_count, last_known_incident, residual_risk, required_contract_terms, conditions_of_approval, review_expiry.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Vendor Security and Privacy Review

> **Important — not legal advice.** This skill produces a procurement-stage risk review and a checklist of contractual safeguards. It is **not** legal advice and is not a substitute for review by qualified privacy, security, and procurement counsel in your jurisdiction. Contract clauses suggested here are starting positions for negotiation, not finished language, and they need to be reconciled with your master template, your insurance posture, and the specific regulatory exposure of the relationship. Where the skill recommends "require" or "do not sign without," read it as "raise this with counsel as a hard requirement and let counsel decide whether to hold the line." Vendors and buyers are advised to obtain independent legal review before executing any data processing agreement, sub-processing arrangement, or international data transfer mechanism.

## When to use

Reach for this skill at the moment a vendor is being seriously considered — usually after a security questionnaire has been requested or volunteered, after a trust-center URL has been shared, or when a paid procurement decision is days or weeks away. It is also the right tool for an annual review of an existing vendor, especially when the renewal would expand the data in scope or when the vendor has publicly disclosed an incident since the last review. Use it when a previously-fine vendor sub-contracts a new processor that needs to be reviewed. Use it when a privacy regulator inquiry causes you to retrospectively examine the safeguards in place for an existing vendor relationship.

The skill is not the right tool for a casual evaluation of a free developer tool that will not touch user data. It is also not the right tool for a one-time, low-volume engagement where the vendor receives no personal data at all — those belong in a lighter intake form. If the data in scope is exclusively business data (vendor financials, your own product roadmap) without personal data, parts of this workflow still apply but the privacy regime sections are out of place; the security and operational sections remain useful.

The skill assumes the buyer has at least some leverage. If the vendor is the only provider on the planet and the deal is already signed by an executive who did not ask first, the realistic posture is "document the residual risk and the compensating controls" rather than "demand new contract language." The output should still be honest about what is missing.

## How to apply

A defensible vendor review is a series of evidence-driven checks that produce a written record. The agent should never accept a verbal "yes we are compliant" — every claim worth recording is backed by a document the vendor produced, a third-party attestation, a public artifact, or an explicit warranty in the contract. Move through the stages below in order. Earlier stages constrain later ones; for instance, the data classification in stage one drives how strict the contractual stages need to be.

### 1. Classify the data in scope

Open with what the vendor will actually process. The agent should categorize along several axes: the categories of personal data (identifiers, contact, financial, content, behavioral, location, device), the sensitivity (special-category data under GDPR Article 9, sensitive personal information under CPRA, protected health information under HIPAA, cardholder data under PCI DSS, student records under FERPA), the volume (rough order of magnitude in subjects and records), the jurisdictions of the data subjects, and whether children are foreseeably in scope. Also classify the business data — credentials, internal financial figures, source code, model weights — that may be exposed through the integration.

Two cheap traps to avoid. The first is treating "we use anonymized data" as decisive; under GDPR and CCPA the anonymization standard is high and partial pseudonymization does not exit the regime. The second is treating "we only send aggregates" as decisive; if individual-level data ever transits the vendor, the relationship is in scope regardless of what is stored at rest.

### 2. Review attestations and certifications

Attestations are evidence, not magic. The agent's job is to read what the document actually says rather than to nod at the logo. For a SOC 2 report, the relevant document is a SOC 2 Type II report covering the trust service criteria appropriate to the engagement (Security always; Availability, Processing Integrity, Confidentiality, and Privacy as warranted) for a recent and adequate period — typically twelve months ending within the past year. Read the system description to confirm the report scope actually includes the product you are buying and not just the parent company's infrastructure. Read the auditor's opinion to confirm it is unqualified; a qualified opinion is not disqualifying but is a serious flag worth pursuing. Read the "exceptions noted" lists in the testing details; testing exceptions are the most informative part of a SOC 2 report and are often the only place a real control failure shows up.

For ISO/IEC 27001, the relevant evidence is a current certificate with a registered certification body, plus a Statement of Applicability (SoA) that lists which Annex A controls are implemented, which are excluded, and the rationale. A certificate without an SoA tells you the scheme; the SoA tells you what was actually scoped in. For ISO/IEC 27701 (privacy extension), expect the same artifacts plus the privacy-specific controls.

For HIPAA the analog is the Business Associate Agreement (BAA) plus the vendor's risk analysis documentation; HIPAA has no certification authority and any "HIPAA-certified" claim is a marketing artifact, not a regulatory one. For PCI DSS the analog is the Attestation of Compliance (AOC) for the relevant SAQ or Report on Compliance and the date of the assessing QSA's signature. For governmental regimes (FedRAMP, GovCloud, IRAP) the analog is the authorization letter plus the boundary diagram.

Always validate provenance. A PDF that arrives by email is a starting point, not proof. Cross-reference against the certification body's public register where one exists, look up the auditor's name against the relevant professional registry, and where the vendor offers an authenticated trust portal, prefer the trust portal as the source of truth.

### 3. Map the data flow

Sketch the path the data will take. The flow should answer: where does the data originate (browser, server, batch ETL), what intermediate processors does it touch, where does it land at rest, where does it replicate (regional replicas, backups, observability pipelines, customer support tooling, model-training feedback loops), and where does it ever leave the vendor's perimeter (sub-processors, support staff workstations, training data sets, sales-engineering demo environments).

The right artifact is a written paragraph that maps to a simple diagram. The agent should call out three failure modes specifically: silent replication into observability or analytics pipelines that the vendor's own privacy notice does not address, sub-processors that are not on the published list, and any path where a human at the vendor can access plaintext customer data without a customer-specific access ticket.

For international transfers, identify the transfer mechanism. Under GDPR a transfer of personal data to a third country requires an adequacy decision, Standard Contractual Clauses (SCCs) with a Transfer Impact Assessment, Binding Corporate Rules, or a derogation. Identify which is in use, when it was last updated, and whether the destination country has been the subject of recent adequacy controversy. The same logic applies to UK GDPR with the UK Addendum and to other regimes that have analogous transfer rules.

### 4. Inspect the sub-processor list

Modern vendors are layered. A typical SaaS uses a cloud provider, a CDN, an analytics processor, an email service provider, a payments processor, an observability stack, and increasingly an AI inference provider. Each of those is a sub-processor with its own data flow. Review the vendor's published sub-processor list — most regimes require one — and check whether it covers the integration in scope, whether it includes the cloud regions, whether it discloses material changes through a notification mechanism the buyer will actually see, and whether the buyer retains a right to object to new sub-processors with a reasonable opt-out (typically termination without penalty if objection is not resolved).

A short or absent sub-processor list is a flag in itself. Either the vendor is unusually vertically integrated, in which case ask how, or the list is incomplete, in which case probe. Where the vendor uses an AI inference provider, ensure the contract addresses whether prompts and responses are retained, whether they are used for training, and whether the vendor's downstream agreement is back-to-back with the assurances you need.

### 5. Probe breach history

Search for public disclosures, regulator actions, and class-action filings against the vendor and its known sub-processors over the past several years. Note the nature of each incident, the data affected, the remediation, and any pattern (repeated incidents in the same product area, repeated supply-chain compromises, delayed disclosures). A clean record is not necessarily a good signal; it may mean the vendor has had no incidents or it may mean the vendor does not disclose. A messy record is not necessarily a bad signal if remediation has been substantive and the controls have visibly matured.

Ask the vendor directly for a list of material security incidents in a defined recent period and for the post-incident reviews where they exist. A vendor that refuses to answer this question is making a choice. Record the refusal and weigh it.

### 6. Read the data processing agreement carefully

The DPA is where assurances become enforceable. The agent should check for the load-bearing clauses: processing instructions limited to the controller's documented purposes; confidentiality for personnel; an audit right that is actually exercisable (not just "a SOC 2 report on request"); a sub-processor notification mechanism with a meaningful objection right; a breach-notification timeline shorter than the regime's reporting deadline so the controller has time to assess; a deletion-or-return obligation at termination with a date-bound certification; cooperation with subject-rights requests; and an international transfer mechanism appropriate to the relationship.

Inspect liability and indemnity carefully. Vendors often cap data-breach liability at a small multiple of fees or even at fees paid in the prior twelve months. For a relationship where a breach could mean tens of millions in regulatory fines and remediation, this cap is the actual posture of the deal even if the security pages look impressive. Negotiate a super-cap or carve-out for data-protection failures and confirm the vendor's insurance backs it.

Look for the dark-pattern clauses that surface in DPAs: silent permission to use customer data for "improving the service" without a clear bound; a unilateral right to update the DPA itself with notice but without consent; a survival clause that does not include the deletion obligation; and any language that converts the vendor from processor to joint controller without acknowledging the regime change.

### 7. Operational hardening

Beyond paper, ask how the integration will be operated. Will the buyer use the vendor's strongest authentication option (SSO with the buyer's identity provider, SCIM provisioning, hardware-key MFA)? Will the buyer scope API credentials with least privilege and rotate them? Will the buyer enable encryption-in-transit features that are optional in the vendor's defaults? Will the buyer turn on the vendor's audit-log export so that an incident response would have evidence? Will the buyer scope the integration with allow-listed IP ranges where feasible? Every "yes" reduces residual risk independently of what the contract says.

### 8. Classify residual risk and write the recommendation

Produce a residual risk classification on a small scale (for example: low, moderate, elevated, high). Anchor it to the data classification from stage one, the attestation review, the breach history, and the contractual posture. State the recommendation in plain language: approve, approve with conditions, defer pending evidence, or decline. Where the recommendation is approve-with-conditions, the conditions are concrete: an updated DPA, a back-to-back sub-processor amendment, a remediation deadline, or a renewal-time recheck.

Schedule the next review. For low-residual-risk relationships, two years is a reasonable cadence. For moderate, annually. For elevated and high, every six months and at any material change. Record the review expiry in the structured output so a tracker can surface it.

## Inputs

The skill expects the vendor name and a description of the data in scope. Pasted excerpts from the vendor's questionnaire, attestation reports, trust center, and sub-processor list dramatically improve the quality of the output. The regulatory anchor and the integration pattern shape which sections are emphasized.

## Outputs

The Markdown report provides a structured review with executive summary, attestation analysis, data-flow narrative, sub-processor concerns, breach history findings, contractual recommendations, operational hardening list, residual risk classification, and an approval recommendation. The JSON output is suitable for piping into a vendor inventory or third-party risk system.

## Examples

A B2B SaaS controller is evaluating an analytics vendor that will receive product-event data including user identifiers from EU users. The skill classifies the data (identifiers, behavioral, EU subjects), reads the SOC 2 Type II excerpt to find that the Confidentiality criterion was scoped in but Privacy was not, flags the absence of SCCs in the draft DPA, notes a 2024 disclosed incident at a sub-processor, recommends approve-with-conditions, and lists the four contract amendments and two operational steps required before signature.

A health-tech buyer is evaluating an AI inference provider that will process patient-related text. The skill classifies the data as protected health information, requires a BAA before any data flows, demands a contractual prohibition on training-set retention of customer prompts, checks the vendor's published incident history, and recommends decline pending the BAA and a documented data-segregation commitment.

## Limitations

This skill produces a procurement-stage review, not a penetration test, not a forensic incident investigation, and not a legal opinion. It cannot verify claims the vendor makes outside the documents you supply. It assumes the buyer has access to the relevant documents under NDA or trust-portal access; absence of documents is a finding rather than a fault of the skill. The contract clauses suggested are starting positions and need lawyer review before they go into a redline. Regulator guidance and enforcement priorities shift; recheck against current authority guidance for the regime in scope.

## Sources reviewed

- https://github.com/strongdm/comply
- https://github.com/PehanIn/ISO-27001-2022-Toolkit
- https://github.com/ElNaboulsi/ISO-27001-2022-SoA-template
- https://github.com/ziyaadramdianee/ISO-IEC-27001-2022
- https://github.com/theopenlane/awesome-compliance
- https://github.com/ethyca/fides
