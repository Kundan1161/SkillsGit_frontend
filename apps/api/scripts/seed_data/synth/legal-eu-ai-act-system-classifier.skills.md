---
id: skillsgit-curated/legal-eu-ai-act-system-classifier
version: 1.0.0
name: EU AI Act System Classifier
description: Classify an AI system under EU AI Act tiers (prohibited, high-risk, limited-risk, minimal), trigger appropriate obligations (conformity assessment, FRIA, transparency), and flag general-purpose AI provider duties.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: legal
tags: [niche:eu-ai-act-compliance, eu-ai-act, ai-governance, high-risk, fria, conformity-assessment, gpai]
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
  estimated_tokens_per_invocation: 10000
trigger_keywords:
  - eu ai act
  - ai act
  - ai system classification
  - high-risk ai
  - prohibited ai
  - conformity assessment
  - fundamental rights impact assessment
  - fria
  - annex iii
  - article 5 prohibited
  - article 6 high-risk
  - gpai
  - general purpose ai
  - systemic risk model
  - ai transparency
example_invocations:
  - "Classify our resume-screening tool under the EU AI Act and produce the obligations checklist for the role we play."
  - "We are integrating a third-party GPAI model into a customer-facing assistant in the EU. Map our deployer obligations and the upstream provider obligations."
  - "We built an emotion-recognition feature for retail analytics. Is it prohibited, high-risk, or limited-risk under the AI Act, and what changes that classification?"
inputs:
  - name: system_description
    type: text
    required: true
    description: Plain-language description of the AI system — what it does, who uses it, what data it consumes, what decisions or outputs it produces, in what sector, and the geographic footprint of users and affected persons.
  - name: role_in_value_chain
    type: choice
    required: false
    description: Whether the organization acts as provider (puts the system on the EU market or into service in its name), deployer (uses an AI system under its authority), importer, distributor, or product manufacturer that integrates AI into a product.
    choices: [provider, deployer, importer, distributor, product_manufacturer, multiple, unsure]
  - name: model_type
    type: choice
    required: false
    description: Whether the system is or includes a general-purpose AI model, and whether it is suspected to meet the systemic-risk threshold; relevant for upstream provider duties.
    choices: [no_gpai, gpai_standard, gpai_systemic_risk, fine_tuned_gpai, unsure]
  - name: sector_overlays
    type: text
    required: false
    description: Sector-specific regulatory regimes that may apply in parallel (medical device, machinery, automotive, aviation, financial services, employment, education, law enforcement, migration, justice, biometrics, critical infrastructure).
outputs:
  - name: classification_report
    type: markdown
    description: A full classification memo with role analysis, tier determination, obligations checklist, FRIA and DPIA triggers, conformity-assessment route (where applicable), GPAI provider duties (where applicable), and an open-questions log for counsel review.
  - name: classification_json
    type: json
    description: Structured fields — role, tier (prohibited / high_risk / limited_risk / minimal / gpai), legal_basis (article and annex references), obligations (per-item with owner_role and trigger_date), open_questions, next_review_event.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# EU AI Act System Classifier

> **Important — not legal advice and not a compliance determination.** This skill produces methodology guidance only. Compliance determinations require qualified counsel and, for regulated entities, formal program ownership (Privacy Officer, Security Officer, Compliance Officer, or equivalent). No skill output constitutes legal advice, satisfies a regulator's evidence requirement on its own, or substitutes for jurisdiction-specific analysis. Real submissions and notices must be authored, reviewed, and signed by qualified staff before any external action. EU AI Act classification is fact-sensitive, often turns on national supervisory authority interpretation, intersects with the GDPR, the Digital Services Act, sectoral product regulation, and Member State implementing law, and continues to evolve through delegated acts and standards work. Treat every output as a draft analysis to be reviewed by qualified EU counsel and the organization's AI governance owner before any external commitment or product change.

## When to use

Invoke this skill when an organization needs to classify a specific AI system or system component under the Regulation establishing harmonised rules on artificial intelligence ("AI Act") and to derive the obligations that follow from that classification. The right moments are: the design or procurement review of a new AI feature that will reach EU users or affected persons; the inventory and triage phase of an enterprise AI governance program where dozens or hundreds of systems are being placed on a classification map; the diligence phase of an acquisition or partnership involving AI; the response to a customer or partner questionnaire that asks for a classification position; the planning phase ahead of an AI Act compliance milestone (the staged application dates mean some obligations bind earlier than others); and the post-incident review where an AI behavior raised a regulator-facing concern.

Do not use this skill in isolation where parallel regimes do most of the work. A medical device with AI components remains regulated as a medical device, with the AI Act adding obligations on top. A consumer credit scoring system already regulated under sectoral financial services and consumer law remains so regulated; the AI Act layers additional obligations. Employment monitoring intersects with national labor law that is often more protective than the AI Act baseline. Treat the AI Act analysis as additive, not substitutive, and route to the right sectoral specialist where the parallel regime is dispositive.

Do not use this skill to authorize deployment in jurisdictions outside the EU on the assumption that AI Act compliance is sufficient. The UK, U.S. states, and other regimes have their own emerging AI laws that classify and regulate differently. The skill output is bounded to the AI Act and to its direct intersections with the GDPR and major EU instruments.

## How to apply

Classification under the AI Act is structurally a decision tree with four primary tiers — prohibited, high-risk, limited-risk (subject to transparency obligations), and minimal — plus a parallel regime for general-purpose AI models. Work the tree in order. At each branch, capture the factual basis for the determination, because the AI Act expects providers and deployers to justify their classification choices and to revisit them when the system changes.

### Stage 1: Establish the role in the value chain

The same AI system imposes different duties on different actors. The provider is the natural or legal person that develops or has developed an AI system or general-purpose AI model and places it on the market or puts it into service under its own name or trademark. The deployer is the natural or legal person using an AI system under its authority, except where the use is in the course of a personal non-professional activity. Importers and distributors play their conventional product-regulation roles. A product manufacturer that integrates an AI system into a product placed on the market under the manufacturer's name carries the provider's duties for the integrated system, with some sectoral nuance.

The role determination is the gate to every other field. A SaaS vendor that builds a high-risk AI system is a provider with the full provider obligations. The same SaaS vendor's enterprise customer is a deployer with a narrower but still meaningful set of obligations. A consultancy that fine-tunes an upstream foundation model and ships it embedded in a customer-facing feature may carry provider duties for the fine-tuned variant, even though it is a deployer of the underlying foundation model. Resolve role first.

A single organization is frequently multiple roles for the same system in different contexts. Capture each role and produce the obligations checklist for each.

### Stage 2: Screen for prohibited practices (Article 5)

Article 5 prohibits a specific list of AI practices that the regulation deems unacceptable risks to fundamental rights. The categories include: certain manipulative or deceptive techniques that materially distort behavior in ways causing significant harm; exploitation of vulnerabilities due to age, disability, or socio-economic situation; social scoring by public authorities or on their behalf where it leads to detrimental treatment in unrelated contexts; certain individual criminal-risk assessments based solely on profiling or personality traits; untargeted scraping of facial images from the internet or CCTV for facial recognition databases; emotion recognition in workplaces and educational institutions, with narrow safety/medical exceptions; biometric categorization to infer sensitive attributes (race, political opinions, trade union membership, religion, sex life, sexual orientation) with narrow exceptions; and real-time remote biometric identification in publicly accessible spaces for law enforcement purposes outside narrow authorized cases.

Screen the system against each category. A few classification heuristics: emotion recognition that the team described as "engagement detection" or "tone-of-voice analysis" still implicates the workplace and education prohibition when deployed there; biometric categorization that infers protected attributes from non-biometric inputs may still fall within the spirit of the prohibition, and supervisory authority guidance is the controlling source; "social scoring" is not just a public-sector phenomenon, and private-sector behavior that effectively reproduces public-sector social scoring against a population can attract scrutiny even outside the literal letter.

A prohibited determination is fatal: the system cannot be placed on the market or put into service in the EU. Do not classify a system as prohibited without senior counsel sign-off, and do not classify a system as not-prohibited without an explicit reasoning trail that survives audit.

### Stage 3: Screen for high-risk (Article 6 and Annex III)

High-risk classification proceeds along two tracks. The first track captures AI systems intended to be used as a safety component of a product, or that are themselves a product, covered by Union harmonisation legislation listed in Annex I (medical devices, machinery, toys, lifts, civil aviation security, automotive, marine equipment, and others) where the product is required to undergo a third-party conformity assessment. The second track captures AI systems listed in Annex III, which enumerates eight domains in their current form: biometrics outside the prohibited cases; critical infrastructure (road traffic, water, gas, heating, electricity); education and vocational training; employment, workers management, and access to self-employment; access to and enjoyment of essential private services and essential public services and benefits (including credit scoring and life and health insurance risk assessment, with carve-outs); law enforcement; migration, asylum, and border control management; and administration of justice and democratic processes.

The Annex III analysis is the engine room of high-risk classification for most non-product AI deployed by industry. Work the categories with care. Recruitment AI, performance evaluation AI, and AI used for task allocation in employment fall in Annex III. Credit scoring and insurance underwriting hit the essential-services category subject to carve-outs. Biometric identification — even outside the prohibited cases — is high-risk where it is used for biometric verification or categorization in ways that touch protected categories, again subject to nuance.

The AI Act adds a derogation from high-risk classification where an Annex III system does not pose a significant risk of harm to health, safety, or fundamental rights, because of specific narrow conditions in Article 6(3). This derogation is narrow and providers that rely on it must register their assessment in the EU database. Do not rely on the derogation without explicit reasoning and senior review.

### Stage 4: If high-risk, derive provider obligations

A high-risk AI system imposes a substantial obligation set on the provider. Capture each as a line item in the obligations checklist with an owner role and a target date.

Risk management system covering the entire lifecycle, with iterative identification, evaluation, and mitigation of risks.

Data and data governance practices for training, validation, and test data — relevance, representativeness, freedom from errors, examination of biases, and contextual statistical properties.

Technical documentation covering the elements in Annex IV — the most detailed disclosure obligation in the regime.

Record-keeping and automatic logging.

Transparency and provision of information to deployers — instructions for use sufficient for deployers to operate the system in compliance with their own obligations.

Human oversight measures appropriate to the risk.

Accuracy, robustness, and cybersecurity appropriate to the intended purpose.

Quality management system covering the provider's organization.

Conformity assessment via the appropriate route (internal control for most Annex III systems; notified-body involvement for product-related systems and for certain biometrics cases).

CE marking, EU declaration of conformity, and registration in the EU database where required.

Post-market monitoring system and serious-incident reporting.

### Stage 5: If high-risk, derive deployer obligations

Deployer obligations are narrower but real. Capture: assignment of human oversight to natural persons with the necessary competence, training, and authority; relevant input data control where the deployer controls input data; monitoring of operation and pausing or stopping where significant risks emerge; record-keeping of automatically generated logs to the extent within the deployer's control; informing affected workers and their representatives in employment contexts; informing affected natural persons in certain Annex III contexts; cooperation with competent authorities; and — critically — a Fundamental Rights Impact Assessment (FRIA) for deployers that are bodies governed by public law, private operators providing public services, or deployers of certain credit and insurance use cases before first use.

The FRIA is the most distinctly AI-Act-flavored deployer artifact. It documents the processes in which the system will be used, the period and frequency of use, the categories of natural persons likely to be affected, the specific risks of harm to those persons, the human oversight measures, and the measures to take in case of materialization of those risks. The FRIA is separate from but complementary to the GDPR DPIA; in practice the two documents share evidence and should be developed in coordination.

### Stage 6: If limited-risk, derive transparency duties

Certain AI systems trigger transparency obligations regardless of broader classification. Capture each that applies: AI systems intended to interact directly with natural persons must inform those persons that they are interacting with an AI system (with narrow exceptions for obvious cases and law-enforcement exceptions); emotion-recognition and biometric-categorization systems outside the prohibitions must inform affected persons; AI systems that generate synthetic audio, image, video, or text content must mark outputs as artificially generated or manipulated in machine-readable form; deployers of AI-generated or manipulated deep-fake content must disclose that the content is artificial; deployers of AI-generated text published to inform the public on matters of public interest must disclose that the text is artificially generated.

### Stage 7: Run the general-purpose AI overlay

The AI Act regulates providers of general-purpose AI models separately from the system-level tiering. A general-purpose AI model is a model trained with a large amount of data using self-supervision at scale that displays significant generality and is capable of competently performing a wide range of distinct tasks regardless of the way the model is placed on the market. Providers of these models carry duties to maintain technical documentation, to make information and documentation available to downstream providers integrating the model, to put in place a policy to respect Union copyright law, and to publish a sufficiently detailed summary of the content used for training. Providers of models with systemic risk — judged by capability thresholds in the regulation and by Commission designation — carry additional duties including model evaluation with adversarial testing, systemic-risk assessment and mitigation, serious-incident reporting, and cybersecurity protection.

When the system being classified integrates a third-party general-purpose model, capture the upstream provider's duties as a dependency and capture the downstream provider's duties for the integrated system as the primary obligations set. Where the organization fine-tunes a general-purpose model and ships it under its own name, route the question of whether the fine-tuned variant is itself a general-purpose model (and whether the organization is now a GPAI provider) to counsel.

### Stage 8: Cross-cut with the GDPR and the AI office position

Run two cross-cutting checks before issuing the classification.

GDPR alignment. Most high-risk systems also trigger DPIA obligations. The FRIA and the DPIA overlap; the AI Act explicitly contemplates coordination. Where the organization is processing special-category data, automated decision-making with legal or similarly significant effects (Article 22), or large-scale monitoring, capture the GDPR obligations alongside the AI Act obligations and merge the assessments where the regulation allows.

Standards and codes-of-practice alignment. The AI Act relies on harmonised European standards (drafted by CEN-CENELEC) and on codes of practice (especially for GPAI). The classification report should reference the standards landscape current at the time of the analysis, recognizing that the standards work is moving. Where a relevant standard is in draft, capture both the current best-practice baseline and the expected future requirement, so the program builds toward the future state.

### Stage 9: Produce the obligations checklist and the open-questions log

Produce a per-actor obligations checklist with owner role, evidence, and target date keyed to the staged application dates. Produce an open-questions log capturing the determinations that depend on facts the team has not yet verified, the determinations that depend on supervisory authority guidance that is not yet published, and the determinations that depend on contractual language with upstream or downstream parties that has not yet been negotiated. Route the open-questions log to qualified counsel and to the AI governance owner before publication.

## Inputs

A plain-language system description; an optional role declaration covering all the roles the organization plays for this system; an optional GPAI model overlay; and an optional list of sector-specific regimes that intersect with the system.

## Outputs

A markdown classification memo with role analysis, tier determination with reasoning, the obligations checklist scoped to each role the organization plays, the FRIA and DPIA triggers, the conformity-assessment route where applicable, the GPAI overlay where applicable, and the open-questions log. A parallel JSON object captures the same structured fields for tracking.

## Examples

A SaaS HR platform is preparing to launch an automated resume-screening feature for EU employers. The skill positions the SaaS as the provider; the feature falls in Annex III (employment) and is high-risk; the SaaS therefore picks up the full provider obligation set, including a Quality Management System, technical documentation against Annex IV, post-market monitoring, and registration. Customers are deployers and inherit deployer obligations, including affected-worker information and the FRIA where they are public-sector. The skill produces both checklists and flags the GDPR Article 22 overlap.

A retail operator wants to deploy emotion-recognition cameras at points of sale to optimize staffing. The skill identifies that emotion recognition in retail is not within the workplace prohibition but is within the limited-risk transparency obligation and may be high-risk depending on use; biometric categorization risks are flagged; the GDPR overlay is significant given the biometric data involved. The skill routes the matter to counsel before any deployment.

An AI-native startup fine-tunes an open-weights general-purpose model and ships it as part of a developer SDK to EU customers. The skill captures the dual question of whether the startup is now a GPAI provider for the fine-tuned variant and what the integrated-system tier is downstream. Both branches generate open questions for counsel and for the AI office contact.

## Limitations

The skill cannot make the determination. Classification under the AI Act is fact-sensitive, depends on the precise way the system is described to a regulator, intersects with national implementing law, and continues to evolve through delegated acts, standards, and supervisory authority guidance. The skill cannot evaluate conformity-assessment evidence; that is a notified-body or internal-quality-system function. The skill cannot replace the FRIA or the DPIA themselves; it identifies their triggers and structures the inputs. Where the regulation has been amended since the date of this skill or where the Commission has issued delegated or implementing acts that change classifications, the skill defers to current authority.

## Sources reviewed

- https://github.com/Hiepler/EuConform — MIT and EUPL-1.2; the dual-license, Annex-aware classification structure illustrates a working approach to tiering Article 5, Article 6, and Annex III in code.
- https://github.com/ark-forge/mcp-eu-ai-act — MIT; the prompt-driven tier classification against Article 5, Annex III, Article 52, and minimal-risk illustrates a deployer-facing self-classification flow.
- https://github.com/GenAI-Gurus/awesome-eu-ai-act — CC0-1.0; the curated landscape of official sources, standards, FRIA templates, and conformity-assessment tools shaped the source map used in this skill.
- https://github.com/kanad13/EU-AI-Act — MIT; a teaching-oriented walk-through of the AI Act with practical examples and an implementation timeline.
- https://artificialintelligenceact.eu/ — public-policy publication of the regulation text and a community compliance checker; the regulation text itself is the primary source.
