---
id: skillsgit-curated/legal-dsar-handler
version: 1.0.0
name: Data Subject Access Request Handler
description: Run a Data Subject Access Request end-to-end — intake, identity verification, scope, discovery, redaction, response packaging, deadline tracking, and exception logging.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: legal
tags: [niche:privacy-compliance, dsar, gdpr, ccpa, subject-rights, deadlines, redaction]
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
  - dsar
  - data subject access request
  - sar workflow
  - subject rights request
  - right to access
  - right to deletion
  - article 15 request
  - ccpa right to know
  - privacy request intake
  - data subject deadline
  - redact response
  - identity verification privacy
example_invocations:
  - "Handle this DSAR — intake email is pasted below, draft the verification step and the 30-day plan."
  - "We received a deletion request from a former employee. Walk me through the workflow including exceptions."
  - "Build a discovery list for a CCPA right-to-know request across our CRM, support, billing, and product analytics."
inputs:
  - name: request_text
    type: text
    required: true
    description: The raw inbound request — email, web form submission, postal letter transcription, or in-app message. Include the requester's stated identity, the claimed jurisdiction, and the rights they invoke.
  - name: organization_context
    type: json
    required: false
    description: Company name, jurisdictions of operation, applicable regimes (GDPR/UK GDPR/CCPA/CPRA/LGPD/HIPAA/other), data systems inventory at a high level (CRM, marketing, billing, product, support, HR, backups, third-party processors). Improves discovery and exceptions.
  - name: requester_profile
    type: json
    required: false
    description: Optional verified attributes from the controller side (account ID, email-on-file, last login, account type — customer, employee, prospect, child).
  - name: regime
    type: choice
    required: false
    description: Primary legal regime to anchor the workflow.
    choices: [gdpr, uk_gdpr, ccpa_cpra, lgpd, pipeda, multi, unknown]
  - name: requested_rights
    type: choice
    required: false
    description: Type(s) of right exercised. If multiple, pass "multiple" and list them in request_text.
    choices: [access, deletion, correction, portability, restriction, objection, opt_out_sale_share, multiple, unspecified]
outputs:
  - name: dsar_plan
    type: markdown
    description: A staged workflow with deadlines, verification approach, discovery checklist, redaction guidance, response package outline, draft acknowledgment, and exceptions log entries.
  - name: dsar_json
    type: json
    description: Structured fields for case management — case_id placeholder, regime, rights, deadline_iso, identity_status, scope, system_targets, exemptions_claimed, status, next_action, next_action_due.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Data Subject Access Request Handler

> **Important — not legal advice.** This skill produces an operational workflow and drafting aid for handling privacy rights requests. It is **not** legal advice, does not establish an attorney-client relationship, and is not a substitute for review by qualified counsel in your jurisdiction. Regulatory regimes change, supervisory authorities publish guidance that supersedes general templates, and edge cases (children's data, deceased persons, criminal records, joint controllers, journalistic exemptions, employer-employee context) frequently demand legal judgment. Always have a lawyer or qualified privacy officer review consequential decisions — particularly denials, partial responses, deadline extensions, and any response to a regulator. Where this skill says "you may," read it as "you may, if your counsel agrees."

## When to use

Invoke this skill the moment a request to exercise a data subject right enters the organization — typically a fresh email to a `privacy@`, `dpo@`, or generic support inbox, a submission via an in-product privacy portal, a postal letter that someone has scanned, a request that arrived to a sales rep's personal address, a forwarded screenshot from a community channel, or a fax in a regulated industry. The skill is appropriate for any of the rights granted under modern privacy regimes — access, deletion, correction, portability, restriction, objection, and the CCPA/CPRA-flavored rights to know, delete, correct, and opt out of sale or sharing. It is also appropriate for the related-but-distinct workflows that frequently piggyback on a DSAR, such as a parent invoking rights on behalf of a child, an authorized agent acting under power of attorney, or a former employee requesting an HR file under an employment-law regime that happens to overlap with privacy law.

Do not invoke this skill for adjacent intake that looks similar but is procedurally different. Sale opt-outs via a Global Privacy Control signal are best handled by an automated cookie-and-consent layer, not a manual workflow. A breach notification requirement triggered by your own incident is an incident-response process, not a subject-rights process. A subpoena, civil discovery request, or law-enforcement preservation letter is a legal process matter — funnel it to counsel rather than treating it as a DSAR. Press inquiries dressed up as access requests are media relations problems. If you are unsure, default to opening a case in this workflow and flagging the ambiguity for human review; opening a case is cheap, and the deadline clock is forgiving of a few hours of confusion but not of weeks of inaction.

A second class of correct invocation is the backlog catch-up. Some teams discover, often during a SOC 2 audit or a CCPA enforcement letter, that they have months of unprocessed requests sitting in shared inboxes. This skill scales to that situation: run each request through the pipeline, mark the deadline as already missed where it is, and produce a triage queue that orders by jurisdictional risk, deadline overrun, and apparent requester sensitivity. Catching up is better than continuing to ignore, but the agent should be honest about the missed-deadline status in the case record and in any tolling discussion with counsel.

## How to apply

Treat a DSAR as a small case file that opens, moves through stages with strict deadlines, and closes with a packaged response and a logged decision. Each stage is a checkpoint with a human-readable artifact. Move sequentially; do not skip ahead because earlier stages create the evidence later stages depend on.

### 1. Open the case and start the clock

Record the date and time of receipt to the minute. Under GDPR (Articles 12 and 15) the controller has one month from receipt of a verified request, extendable by two further months for complexity, with the extension communicated to the subject within the first month. Under CCPA/CPRA the controller has forty-five days from receipt, extendable by another forty-five days with notice. Under LGPD the default is fifteen days for access requests with some flexibility. Under PIPEDA the response window is thirty days, extendable by a further thirty with notice. These figures are general planning anchors, not authoritative pronouncements for your specific case — confirm them against current regulator guidance and your counsel's reading.

Begin the deadline arithmetic immediately, even before you know whether the request is verified. The clock generally starts on receipt, not on verification, and a tribunal that has to choose between a controller-friendly and a subject-friendly reading of when "receipt" happened tends to choose the subject-friendly one. Record the worst-case interpretation in the case file, and present the controller-friendly interpretation as a secondary date that counsel can argue for if necessary.

### 2. Acknowledge receipt within a short window

Draft an acknowledgment to send within a few business days. The acknowledgment confirms receipt, states the relevant deadline, explains identity verification, lists what the subject can do to speed verification, names the controller's point of contact, and references the supervisory authority the subject may complain to. The tone is plain and human. Do not promise a specific scope of response — you have not done discovery yet. Do not deny the request in the acknowledgment; denial is a substantive decision that comes later and requires a documented basis.

### 3. Verify identity proportionate to the request

The principle is proportionality: ask for only as much identity evidence as is reasonable given the sensitivity of what would be disclosed. For an access request from someone who is already authenticated in your product (recent valid session, account in good standing, request submitted from in-app), the existing authentication is usually sufficient and demanding more is itself a privacy harm. For an out-of-band request from an email address that matches the account on file, a confirmation link to that address is generally enough. For a request where the requester's identity is uncertain or the data is highly sensitive (health, finance, children, employment records), step up the verification — government-ID photo with selfie, a knowledge-based check against existing record fields the requester should know, or a signed statement under penalty of perjury where the regime supports it.

Be alert to two failure modes. The first is over-asking: demanding a passport scan from an authenticated user to slow down a deletion request is a documented dark pattern and a regulator-favored complaint. The second is under-asking: handing over the wrong person's data because the requester guessed an email address and you replied to the address-on-file is a breach. The right balance is "what would a reasonable privacy officer ask for, given who the requester appears to be and what they are asking for?" Document the verification step in the case file with the basis for the decision.

For authorized-agent requests (CCPA permits these explicitly), require evidence of the agent's authority — usually a written authorization signed by the consumer, plus the consumer's own verification through the controller's normal channels. Children's requests vary by regime; under most regimes a parent or guardian acts on behalf of a child below the regime's age threshold, with the same verification logic applied to the parent.

### 4. Scope the request

Translate the request into a discovery brief. What categories of data are in scope? Which time period? Which products, services, and operating entities? Are there carve-outs the regime allows (privileged communications, trade secrets, third-party data interleaved with the subject's data, ongoing investigations)? Are there standing exemptions in the regime (the GDPR's "manifestly unfounded or excessive" carve-out at Article 12(5), the CCPA's exceptions for security and fraud prevention)?

Scope honestly. A request phrased as "all my data" generally means all personal data the controller and its processors hold about the data subject, not a literal export of every database row that touched their session. A pragmatic scope captures the user-relevant artifacts — profile, communications, content created, billing records, support history, identifiers, derived attributes — and references the categories of data that are out of scope with a clear rationale. The Article 15 right of access in GDPR also has informational components beyond the data itself: categories of recipients, sources, retention periods, and the existence of automated decision-making.

### 5. Discover the data

Run a structured sweep across the systems inventory. For each system in scope, log what was searched, what identifiers were used, who ran the search, when, and what was returned. A defensible discovery is one where, if a regulator later asks "how do you know you found everything you held about this person," you can answer with a per-system log rather than a wave of the hand.

The agent should produce a discovery checklist tailored to the organization-context input. A reasonable default list for a typical SaaS controller includes: the production application database, the customer relationship management system, the marketing automation platform, the support and ticketing system, the billing and payments system, the product analytics platform, the email service provider, internal communications archives that mention the subject by name or identifier, file storage that may hold attachments, log retention systems, sub-processor stores reached via documented data export endpoints, and backup systems with their retention windows. For each, identify the identifier to search by — usually email, but sometimes account ID, phone number, or device identifier — and confirm whether the system supports an export.

Resist the temptation to skip backups. The position favored by most regulators is that backups are in scope for access (with caveats about format and partial retrieval) but receive a softer treatment for deletion provided the controller can demonstrate that restored backups will not re-introduce the deleted record. Document the backup posture in the case file rather than ignoring it.

### 6. Apply exemptions deliberately

Where the regime permits withholding or redacting, do so deliberately and on the record. Common bases include third-party data interleaved with the subject's data (redact the third party), trade-secret algorithms behind a derived attribute (disclose the existence and broad purpose, withhold the implementation), legal privilege over attorney communications, and ongoing-investigation exceptions where the regime supports them. A claim of "manifestly unfounded or excessive" is allowed but rare — use it only with counsel's review, because regulators are sceptical of it and may invert the burden.

Redaction is a craft, not a sed-script. Names of internal staff are personal data of those staff and are routinely redacted in third-party access responses, but the requester is often entitled to know the category of recipient ("data exported to a US-based analytics processor under SCCs") even when the specific individual is redacted. Make a redaction log that pairs each redaction with a basis; do not redact silently.

### 7. Package the response

The deliverable to the subject usually has two parts. The first is a narrative cover letter that summarizes what was found, what was withheld and why, the categories of recipients and sources of the data, retention rules, whether automated decision-making affected the subject, and the route for complaint to the supervisory authority. The second is the data itself, in a format the regime allows — for portability rights this is typically a structured, commonly used, machine-readable format such as JSON, CSV, or XML. For access rights the format is more flexible, but the deliverable should be intelligible to a lay reader and complete relative to the scope.

Avoid two common pitfalls. The first is dumping raw database exports that contain internal field names a layperson cannot interpret; this technically discloses the data and substantively fails the access right. The second is producing a curated summary that omits the underlying records; the subject is entitled to the data, not your gloss on it. The right answer is a curated narrative pointing into a complete export.

Encrypt the package in transit and at rest. A secure download portal with single-use access is preferable to an emailed ZIP. Where postal is required, registered mail with delivery confirmation. The package itself should not become a new breach surface.

### 8. Close the case and log the decision

A closed case includes: the request artifact, the verification record, the scope memo, the per-system discovery logs, the redaction log, the response package, the cover letter, proof of delivery, and any extension notices sent. The exceptions log records any right denied or partially denied, the basis, the regulator-pointer text included in the response, and the human approver. Retain the case file under the controller's own retention rule — long enough to defend against a regulator inquiry (often two or more years) but not indefinitely.

If the request is denied or modified, the response must give reasons and inform the subject of their right to complain to the supervisory authority and to seek a judicial remedy. Do not bury this text — it is a regulator-favored signal and its absence is a common citation in enforcement decisions.

## Inputs

The skill expects the inbound request text and benefits from organization context describing systems, regimes, and any pre-verified attributes about the requester. If regime is left unspecified, the agent should infer from the requester's stated jurisdiction and the controller's footprint, and call out the inference.

## Outputs

The primary output is a staged Markdown workflow with deadline arithmetic, draft acknowledgment, verification approach, discovery checklist, redaction guidance, response package outline, and exceptions log entries. The structured JSON output is suitable for piping into a case-management system and includes the deadline, identity status, scope summary, system targets, exemptions claimed, current status, and next action with a due date.

## Examples

A SaaS controller in the EU receives an email to `privacy@` from a former trial user asking for "all my data" and stating they live in Berlin. The skill opens a case under GDPR, sets the deadline at one month from receipt, drafts an acknowledgment explaining a confirmation-link verification, lists the eight systems to sweep based on the company's inventory, flags that the support inbox contains messages from this user about a third-party complaint (third-party-data redaction), and produces a delivery plan that closes with a download portal and a regulator-pointer paragraph.

A US-based retailer receives a postal letter forwarded by counsel claiming the right to know under CCPA on behalf of a California resident, signed by an authorized agent. The skill opens a case under CCPA, sets a forty-five-day deadline, branches verification into "verify the consumer" and "verify the agent's authority," scopes the response to the prior twelve months as the regime permits, calls out the "categories of sources and recipients" disclosure obligation, and produces a structured export plus a cover narrative.

## Limitations

This skill is procedural scaffolding. It does not determine whether a specific exemption applies in a specific jurisdiction, does not draft a denial letter that will withstand regulator scrutiny without counsel review, and does not know your organization's data inventory unless you supply it. It treats the regimes it lists at a planning level appropriate for an operational workflow; precise figures, recent regulator guidance, and case-by-case judgment require legal review. It assumes good-faith requesters and good-faith controllers; adversarial scenarios (litigation discovery dressed as a DSAR, requests intended to harass, requests from individuals attempting to exfiltrate a third party's data) need human judgment from the start.

## Sources reviewed

- https://github.com/strongdm/comply
- https://github.com/ethyca/fides
- https://github.com/opengdpr/OpenDSR
- https://github.com/open-privacy/dsrhub
- https://github.com/theopenlane/awesome-compliance
- https://github.com/paulveillard/cybersecurity-gdpr-compliance
