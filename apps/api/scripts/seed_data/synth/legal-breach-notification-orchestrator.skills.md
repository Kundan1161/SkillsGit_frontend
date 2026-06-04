---
id: skillsgit-curated/legal-breach-notification-orchestrator
version: 1.0.0
name: Breach Notification Orchestrator
description: Orchestrate a data-breach response — clock start, severity assessment, regulator notification timing per jurisdiction, individual notification triggers, and communications scaffolds.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: legal
tags: [niche:breach-notification, breach, incident-response, gdpr-article-33, hipaa-breach-rule, regulator-notification, individual-notice]
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
  estimated_tokens_per_invocation: 11000
trigger_keywords:
  - data breach
  - breach notification
  - article 33
  - article 34
  - hipaa breach rule
  - 72 hour notification
  - 60 day notification
  - personal data breach
  - ephi breach
  - dpa notification
  - individual notice
  - state breach notification
  - regulator notification
  - breach risk assessment
example_invocations:
  - "We had an incident — unauthorized access to a customer support inbox containing EU customer tickets. Walk through whether notification is required and on what clock."
  - "An employee laptop with unencrypted ePHI was stolen. Produce the HIPAA breach assessment and the notification plan."
  - "Triage this incident across GDPR, HIPAA, and US state breach notification laws — give me the deadline matrix and the draft notices for counsel."
inputs:
  - name: incident_description
    type: text
    required: true
    description: Plain-language description of the incident — what happened, when it was discovered, how it was discovered, what systems and data are involved, the scale, the affected populations, the containment status, and any current evidence of misuse.
  - name: regimes_in_scope
    type: choice
    required: false
    description: The regulatory regimes likely to apply; if unsure, choose multi and let the skill triage.
    choices: [gdpr_only, hipaa_only, us_state_breach, gdpr_and_hipaa, multi, unsure]
  - name: organization_role
    type: choice
    required: false
    description: Whether the organization is the controller/covered entity, the processor/business associate, or both, for the affected data.
    choices: [controller, processor, covered_entity, business_associate, joint, multiple]
  - name: incident_status
    type: choice
    required: false
    description: Where in the incident lifecycle the response sits when the skill is invoked.
    choices: [suspected, confirmed_unconfirmed_scope, scoped, contained_and_assessing, ready_to_notify, post_notification]
outputs:
  - name: breach_response_plan
    type: markdown
    description: A full breach response plan with clock-start determination, severity and risk assessment, regulator notification matrix, individual notification trigger analysis, draft communications scaffolds, decision log, and post-incident review prompts.
  - name: breach_response_json
    type: json
    description: Structured fields — discovered_at, clock_start, applicable_regimes, severity, regulator_notifications (per regulator with deadline and content checklist), individual_notification_required, comms_owners, decisions, open_questions.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Breach Notification Orchestrator

> **Important — not legal advice and not a compliance determination. Especially heavy disclaimer in this domain.** This skill produces methodology guidance only. Compliance determinations require qualified counsel and, for regulated entities, formal program ownership (Privacy Officer, Security Officer, Compliance Officer, or equivalent). No skill output constitutes legal advice, satisfies a regulator's evidence requirement on its own, or substitutes for jurisdiction-specific analysis. Real submissions and notices must be authored, reviewed, and signed by qualified staff before any external action. Breach notification is among the most consequential and time-sensitive areas of privacy and security law. A misjudged notification — too early, too late, too narrow, too broad, wrongly addressed, or wrongly framed — creates regulator-facing risk that exceeds the original incident. Every clock in this skill is to be cross-checked against the version of the law in force on the date of the incident in the jurisdiction at issue. Every notice draft is a scaffold for qualified counsel to redraft. Treat the skill output as a triage and decision-support aid; do not transmit any draft to a regulator, partner, or affected individual without sign-off from in-house or outside counsel and the designated incident response authority.

## When to use

Invoke this skill the moment an event is reported that may meet the definition of a personal data breach, a breach of unsecured protected health information, or a "security breach" under a U.S. state or foreign breach notification law. The right moments include: the first hour after the security or privacy team accepts an incident report and confirms there is plausible exposure of personal data; the early hours of a vendor-reported incident where the organization is the controller or covered entity and a processor or business associate has notified upstream; the recovery phase of an incident where containment has held but the exposure-assessment work has not yet been done; the post-mortem of a near-miss where the question is whether notification is still required (often the answer is yes for a defined subset of "encrypted laptop stolen" cases); and the response to a regulator inquiry that arrives without a prior internal incident — a real and increasing pattern in the GDPR era.

Do not use this skill before the incident is real enough to assess. A vague rumor of unauthorized access without supporting facts triggers an incident response, not a breach response. Run the security team's incident response first; reach this skill once there is enough fact to evaluate the four breach questions below. Conversely, do not delay this skill while waiting for "complete" facts. The GDPR clock starts on awareness, not on completeness; the U.S. state clocks vary; HIPAA presumes a breach absent a documented low-probability-of-compromise determination. Run the skill on incomplete facts and document what is unknown — that documentation is itself part of the regulator-facing record.

Do not use this skill for incidents that are not personal data breaches. Cybersecurity incidents without personal data exposure may trigger SEC disclosure, NIS2 reporting, contractual notification, and other regimes that this skill does not cover. A wire fraud incident is not a personal data breach unless personal data was incidentally exposed. Vendor outages without data exposure are not breaches. Run the regime screen carefully at the threshold so that the breach machinery does not engage in cases it is not designed for.

## How to apply

Treat the breach response as a sequence of distinct decisions, each with a documented basis, each with a named owner. The mistake the skill is designed to prevent is the conflation of distinct decisions into a single panicked call: when notification is required, to which regulators, by when, to which individuals, with what content, in what language, through what channel, and with what evidence trail. Each decision has its own answer and its own clock.

### Stage 1: Define the incident and the asset

Capture the incident in a one-paragraph factual description: what happened, when it started, when it was discovered, how, by whom, the containment state, and the systems and data implicated. Beneath the paragraph maintain a structured timeline that grows during the response — every material fact gets an entry with a timestamp and a source. The timeline is the spine of the regulator-facing record.

Capture the asset inventory affected: which systems, which data classes, which data subjects, which geographies. Distinguish data the organization controls from data the organization processes on behalf of others — the notification duties and the recipients differ. For health data, identify protected health information specifically; for EU/UK data, identify the categories of personal data and whether special-category data is in scope; for U.S. state law purposes, identify the specific data elements (Social Security number, driver's license number, financial account number, health information, biometric data, online credentials with security information, and the rest of the modern state breach element set) because the state laws are element-driven.

### Stage 2: Identify the clock starts

The clock-start determination is the single most consequential output of the early response.

Under the GDPR, the controller's clock to notify the competent supervisory authority is seventy-two hours from awareness of the personal data breach. "Awareness" attaches when the controller has a reasonable degree of certainty that a security incident has occurred that has led to personal data being compromised; this is earlier than complete forensics. A processor must notify the controller "without undue delay" after becoming aware; that intra-pipeline clock pressures the controller's own seventy-two-hour clock and is the most common cause of late notifications in practice. Note both clocks.

Under HIPAA, the covered entity has up to sixty days from discovery of a breach of unsecured PHI to notify affected individuals, with parallel obligations to notify HHS (immediately if 500 or more individuals affected; in the annual summary report if fewer) and, for breaches of 500 or more residents of a state or jurisdiction, prominent media in that state. A business associate has up to sixty days from discovery to notify the covered entity. "Discovery" under HIPAA is the first day the breach is known, or by exercising reasonable diligence would have been known, by any person other than the person committing the breach who is a workforce member or agent. The discovery clock is broader than many teams realize and is a common audit finding.

Under U.S. state breach notification laws, each state runs its own clock and its own threshold. Many states require notification "in the most expedient time possible and without unreasonable delay," sometimes capped at thirty, forty-five, or sixty days. Several states require attorney general notification at population thresholds, and the consumer reporting agencies must be notified at higher thresholds. The state-by-state matrix changes meaningfully each legislative cycle; the skill output is a starting matrix that counsel must reconcile against the current state of each state's law.

Sectoral overlays may add clocks. Financial services regulators, communications regulators, critical infrastructure regulators, and trust-services regulators each carry their own breach notification expectations. Contractual obligations to enterprise customers — often forty-eight to seventy-two hours — frequently bind faster than statutory ones; capture these alongside the statutory clocks because in practice they drive the early-hour workflow.

Pick the earliest clock as the operating deadline. Document the slower clocks separately for completeness.

### Stage 3: Run the breach-or-not assessment per regime

The breach-or-not determination is different under each regime.

Under the GDPR, a personal data breach is a breach of security leading to the accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to, personal data transmitted, stored, or otherwise processed. Note: confidentiality, integrity, and availability all count — a ransomware event that encrypted personal data and made it unavailable is a personal data breach even if no exfiltration occurred. The notification to the supervisory authority is not required where the breach is unlikely to result in a risk to the rights and freedoms of natural persons; the determination is fact-sensitive and must be documented. Individual notification under Article 34 is required where the breach is likely to result in a high risk to rights and freedoms, subject to specific exceptions (appropriate technical and organizational protection measures applied to the affected data, such that the personal data are rendered unintelligible to unauthorized persons; subsequent measures that ensure the high risk is no longer likely; or notification would involve disproportionate effort, in which case a public communication or equivalent measure is required instead).

Under HIPAA, a breach is presumed when there is an acquisition, access, use, or disclosure of protected health information in a manner not permitted under the Privacy Rule that compromises the security or privacy of the PHI. The presumption can be rebutted with a documented four-factor risk assessment showing a low probability that the PHI has been compromised, looking at the nature and extent of the PHI involved including identifiers and likelihood of re-identification, the unauthorized person who used the PHI or to whom the disclosure was made, whether the PHI was actually acquired or viewed, and the extent to which the risk has been mitigated. A low-probability-of-compromise determination must be documented contemporaneously; many enforcement actions involve organizations that asserted no breach but did not document the assessment.

Under U.S. state laws, the test is element-driven and state-specific. Several states apply a "risk of harm" filter; others apply a strict element-exposure test; the encrypted-data safe harbor exists in most states but with varying definitions of "encrypted" and varying requirements about whether the encryption key was also compromised. Run the state-by-state screen with current law.

For each regime, capture the determination, the reasoning, and the evidence the determination depends on. Where two regimes apply and reach different determinations, follow the stricter — but capture both analyses.

### Stage 4: Severity and risk assessment

Move from breach-or-not to severity-and-risk. The factors are partially common across regimes: the nature of the personal data (special-category, health, financial, credentials, children's data weigh heavier); the volume and identifiability of the affected individuals; the ease of identification from the affected data; the severity of the consequences (financial loss, identity theft, discrimination, reputational damage, loss of confidentiality of professionally privileged data, unauthorized reversal of pseudonymization, loss of control over data); the special characteristics of the individuals (vulnerability, employment context); the special characteristics of the data controller (public authority, healthcare provider); and the number of affected individuals.

The output of this stage is a structured severity score (typical practice: low / medium / high / very high) with a one-paragraph rationale, used as the input to the individual-notification trigger and the regulator-notification content.

### Stage 5: Notification matrix

Produce a notification matrix listing every regulator, partner, and individual population that must be notified, the deadline for each, the content required by each, and the owner. Typical entries:

Supervisory authority(ies) under the GDPR — the lead supervisory authority for the controller's main establishment, and the supervisory authorities in each Member State where data subjects are likely to be substantially affected, in cross-border cases. Content requirements include the nature of the breach, the categories and approximate number of data subjects and data records concerned, the DPO's name and contact, the likely consequences, the measures taken or proposed to address the breach, and any measures to mitigate possible adverse effects. Where information cannot be provided at the same time, it may be provided in phases without undue further delay — a critical and underused provision when the seventy-two-hour clock is approaching.

HHS Office for Civil Rights for HIPAA breaches — the larger-breach immediate notification through the HHS portal, or the annual log for smaller breaches.

Affected individuals — under the GDPR where the high-risk threshold is met, under HIPAA in nearly all breach cases by first-class mail or by alternative methods where contact information is insufficient, and under state law where the state thresholds are met. The content checklist varies by regime; HIPAA's content requirements are explicit and the state laws layer additional content (toll-free numbers, identity-theft monitoring offers, credit reporting agency information).

State attorneys general, state regulators, and consumer reporting agencies — at the state thresholds.

Contractual partners — enterprise customers under the data processing agreement, large customers under custom contracts, business associates upstream of covered entities, and counterparties to other sectoral agreements.

Media — under HIPAA at the 500-resident threshold, under sectoral regulators in some cases, and under voluntary disclosure considerations in others.

Internal — board, executive team, audit committee, customer-success, communications, finance for cyber-insurance carrier notification, and the privacy and security organizations.

### Stage 6: Draft scaffolds

Produce draft scaffolds for each notification. The scaffolds are explicitly skeletons for counsel to redraft. They include the regulator notice, the individual notice with the regime-specific content blocks, a brief partner notice for enterprise customers, an internal stakeholder update, and a public-facing statement template where the incident warrants public communication. Every draft carries a header noting that it is a scaffold, that counsel must redraft and approve, that all factual claims must be verified against the live incident record, and that no draft is to be transmitted without sign-off.

Plain language is mandatory in individual notices; clarity beats legalese and is also what the regulator expects. The notice answers four questions a reasonable affected individual would ask: what happened, what information of mine was involved, what is the organization doing about it, and what can I do to protect myself. Build each draft around those four questions and let counsel layer the regime-specific content blocks on top.

### Stage 7: Decision log and post-incident review

Maintain a decision log throughout. Each decision — what regime applies, when the clock started, whether notification is required, who is the lead supervisory authority, whether to invoke the disproportionate-effort exception, whether to mass-mail or to publish, whether to offer identity-theft monitoring, whether to invite media inquiries — is logged with timestamp, decision-maker role, factual basis, and reasoning. The decision log is the artifact the regulator will ask for after the fact.

Schedule the post-incident review at a deliberate distance from the incident — typically two to four weeks after notification — so the team has perspective. The review covers detection time, response time, decision quality, evidence quality, and the gaps that the incident exposed in the underlying privacy and security program. Feed findings into the risk analysis, the RoPA where new flows or recipients were exposed, the vendor risk program where a processor or business associate contributed to the incident, and the training program where workforce behavior contributed.

## Inputs

Provide the incident description, the suspected regimes, the organization's role for the affected data, and the current incident-lifecycle stage. The skill works on incomplete information by design; what is unknown is captured rather than blocking the response.

## Outputs

A markdown breach response plan with clock-start determination, breach-or-not analyses per regime, severity and risk assessment, notification matrix, draft scaffolds, decision log, and post-incident review prompts. A parallel JSON object captures the same content in a form an incident-management platform can ingest.

## Examples

A SaaS vendor experiences unauthorized access to a customer support inbox containing EU customers' tickets. The skill confirms the SaaS is a processor for ticket content; the seventy-two-hour notification clock is not the SaaS's direct obligation, but the without-undue-delay notification to controllers is. The skill produces the controller-notification scaffold, the deadline matrix, the severity assessment (medium, given the categories of data and absence of special-category data), and the internal communications plan. Counsel reviews; the controller notifications go out within twelve hours; supervisory authority notifications are the controllers' to make.

A clinic discovers a stolen laptop containing unencrypted ePHI for approximately 1,800 patients. The skill identifies HIPAA as the primary regime; notes that the encryption safe harbor does not apply because the device was unencrypted; runs the four-factor risk assessment and concludes that the presumption of breach is not rebutted; produces the individual-notification timeline (within sixty days), the HHS notification timeline (immediate, given the 500-individual threshold), the media notification analysis (the state in question is the only state in scope), and the state attorney general overlay. Counsel and the privacy officer adopt the plan, with adjustments.

## Limitations

This is the most fact-sensitive and regime-dependent skill in the legal collection, and the limitations are commensurate. The skill cannot make the breach determination — that is counsel's call. The skill cannot guarantee that every applicable regime has been identified; cross-border, cross-sector, and multi-state incidents routinely trigger regimes that surface only in counsel review. The skill cannot validate that a draft notice complies with the specific content requirements of a specific state in a specific year; the state laws drift faster than any general checklist can track. The skill cannot replace the cyber-insurance carrier's panel counsel and forensic firm, which the policy may require to be engaged at the earliest hour. Use the skill to structure the response and to enforce the discipline of distinct decisions; let qualified counsel make and own the decisions.

## Sources reviewed

- https://github.com/counteractive/incident-response-plan-template — Apache-2.0; the structure of a free incident response plan, particularly the decision-log discipline and the playbook-per-scenario pattern.
- https://github.com/aws-samples/aws-incident-response-playbooks — MIT-0; the staged playbook structure (preparation, detection, analysis, containment, eradication, recovery, post-incident) informs the breach-response sequencing.
- https://github.com/austinsonger/Incident-Playbook — MIT; the MITRE-aligned playbook collection illustrates the granular per-scenario decision tree pattern.
- https://github.com/awslabs/aws-config-rules — Apache-2.0; the HIPAA Security conformance pack is a reminder that ePHI exposure cases are routinely covered by Security Rule gaps that the breach response then surfaces.
- https://gdpr-info.eu/art-33-gdpr/ and https://gdpr-info.eu/art-34-gdpr/ — public regulation text; primary source for the GDPR clocks and content requirements.
