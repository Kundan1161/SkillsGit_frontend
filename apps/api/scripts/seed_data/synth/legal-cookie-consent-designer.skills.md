---
id: skillsgit-curated/legal-cookie-consent-designer
version: 1.0.0
name: Cookie Banner and Consent Stack Designer
description: Design a compliant consent stack — categorization, default state, granularity, withdrawal, record retention — calibrated to GDPR, CCPA/CPRA, and ePrivacy.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: legal
tags: [niche:privacy-compliance, consent, cookies, gdpr, ccpa, eprivacy, cmp]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  tools_optional: [web_search]
  min_context_tokens: 16000
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - cookie banner
  - consent management
  - consent stack
  - cmp design
  - cookie categories
  - opt in opt out
  - gpc signal
  - global privacy control
  - eprivacy
  - tcf
  - consent withdrawal
  - dark pattern banner
example_invocations:
  - "Design a cookie banner for an EU and California audience — categories, defaults, withdrawal, and record retention."
  - "Audit this cookie banner for dark patterns and compliance gaps."
  - "We have a TCF vendor list and want to add a US opt-out — propose the integrated consent stack."
inputs:
  - name: site_context
    type: text
    required: true
    description: Description of the site or product — what trackers run today (analytics, advertising, session replay, marketing automation, A/B testing, embedded social), the geographic audience, and the current consent state.
  - name: audience_regions
    type: choice
    required: false
    description: Which regulatory regimes the consent stack must serve.
    choices: [eu_only, eu_and_uk, us_only, eu_and_us, global, unsure]
  - name: business_model
    type: choice
    required: false
    description: Influences which tracker categories are likely material and which dark patterns are tempting.
    choices: [saas_b2b, saas_b2c, ecommerce, publisher_advertising, content_subscription, government_public_sector, healthcare_regulated, other]
  - name: current_banner_text
    type: text
    required: false
    description: Optional — paste the current banner text and choices for audit purposes.
outputs:
  - name: consent_design
    type: markdown
    description: A complete consent-stack design with category model, default-state recommendation per regime, banner copy, granular preference UI outline, withdrawal flow, record retention plan, and integration notes for analytics and ad tech.
  - name: consent_design_json
    type: json
    description: Structured fields — regimes_served, category_model, default_state_per_region, banner_copy_variants, withdrawal_path, signals_honored (e.g., GPC), record_retention_days, audit_log_fields, vendor_inventory_required.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Cookie Banner and Consent Stack Designer

> **Important — not legal advice.** This skill produces a design for a consent stack that aims at compliance with current GDPR, ePrivacy Directive, UK PECR, and CCPA/CPRA expectations as commonly enforced. It is **not** legal advice, and consent law is one of the most actively litigated and re-interpreted areas of digital regulation. Supervisory authorities (CNIL, ICO, AEPD, Garante, the EDPB, and California's CPPA among others) publish guidance and enforcement decisions that materially affect what passes. New US state privacy laws are landing on a rolling schedule and each has small but important differences. Have qualified counsel review the final design before launch and on a recurring basis. Where the skill recommends "default off" or "do not load until consent," treat it as a starting position that your counsel should sign off on against the most recent authority guidance for the regions you serve.

## When to use

The right moment for this skill is the first launch of a site or product that places trackers on a user's device, the rollout of a new tracker category (advertising pixels, session replay, AI experimentation tools) that wasn't in the original design, the expansion of the audience into a region with stricter consent law than the home region (commonly: a US company adding EU traffic), and the periodic audit that should follow material enforcement decisions or new regulator guidance. Also use it when an enforcement letter, a customer complaint, or an internal review surfaces a likely problem in the current banner; the skill produces both new designs and audits of existing ones.

It is also worth invoking during major product redesigns. Consent UI is one of the few places where the law has strong opinions about UI affordances, and a redesign that ignores those opinions has tendency to ship the same regulator-flagged patterns as the prior design but in new colors. The skill catches the recurring pitfalls — unequal button prominence, opaque "manage preferences" paths, withdrawal flows hidden behind several clicks — that show up regardless of visual style.

Do not use this skill as a substitute for a Consent Management Platform (CMP) implementation. A CMP is the runtime system that loads or blocks scripts according to the user's choices, persists records, signals downstream vendors, and provides audit trails. The skill produces the design that a CMP enforces; it does not implement the runtime. Where a CMP is already in place, the skill is useful for configuring it.

Avoid using the skill for in-product permission flows that look like consent but are governed by different rules. The microphone permission for a video meeting, the camera permission for a document scanner, the OS-level App Tracking Transparency prompt — these have their own legal and platform regimes and a generic cookie-consent design does not transfer. Native mobile SDK consent is closer to but not identical to web consent and should be designed in conjunction with the platform's own rules.

## How to apply

A well-designed consent stack is a small system with five components: a category model that maps to the trackers actually in use; a default state per region; a banner UI that meets the legal standard for unambiguous, informed, freely-given action; a granular preferences UI that lets users pick at the category level; and a withdrawal-and-record subsystem that lets users change their mind and lets the controller prove what was chosen. The agent should produce all five components and explain how they fit together.

### 1. Inventory the trackers

Before designing the consent stack, list every tracker actually loaded by the site or product. Categorize each by purpose (strictly necessary, functionality, analytics, advertising, social, session replay, marketing automation, experimentation, AI/ML observability) and by who controls it (first-party scripts the controller owns, third-party scripts the controller embeds, fourth-party tags that load through a tag manager or a sub-processor's bundle). The inventory is the diagnostic — banners that describe categories the site does not actually use, or that omit categories it does use, fail both regulator review and consumer-trust review.

A useful pattern is the "load test": load the site in a clean browser, capture network requests, and confirm the list matches the inventory. Trackers that show up in the load test but not in the inventory are unknown unknowns and should be tracked back to the responsible vendor.

### 2. Choose the category model

Three category models recur in current practice. The narrowest is the binary model — strictly necessary versus everything else — which is the legal floor in some jurisdictions but a poor user experience and a regulator-disfavored design where granularity is feasible. The middle is the four-category model — strictly necessary, functionality/preferences, analytics/performance, marketing/advertising — which matches most regulator guidance and most user expectations. The widest is the IAB Transparency and Consent Framework (TCF) purposes-and-vendors model, which is appropriate where the site participates in programmatic advertising ecosystems and inappropriate where it does not (it is overcomplicated for sites that do not need it).

The agent should default to the four-category model unless the inputs justify wider or narrower granularity. The granularity should be at the category level, not at the per-vendor level for general use; per-vendor granularity is sometimes required for TCF participation but adding per-vendor toggles to a banner that does not need them is a user-experience harm that regulators have called out.

### 3. Default-state design per region

Under GDPR and ePrivacy, non-strictly-necessary trackers must be off by default until the user gives unambiguous, informed, freely-given consent through a clear affirmative action. Pre-ticked boxes are not consent; bundled consents that mix necessary and non-necessary categories are not consent; "by continuing to use this site you consent" banners are not consent. The legal standard is high, the regulator practice has been consistent, and the agent should not propose anything weaker for EU traffic.

Under CCPA/CPRA, the model is opt-out rather than opt-in for most processing; the user has a right to opt out of sale or sharing and the site must honor the Global Privacy Control (GPC) signal as a valid opt-out from a browser-level mechanism. Sensitive personal information has additional limits the user can invoke. The "Do Not Sell or Share My Personal Information" link is a contemporary requirement for in-scope businesses serving California consumers.

Where a single site serves both regions, two practical options exist. The first is "EU-strict everywhere" — apply opt-in defaults globally — which is the simplest design and the easiest to defend to regulators, at the cost of analytics coverage in regions where opt-in is not required. The second is "region-aware" — detect the user's region (typically by IP geolocation, with a fallback) and serve a banner appropriate to the inferred regime. Region-aware designs have to handle edge cases honestly (the user behind a VPN, the user crossing regions on different visits) and should err on the side of the stricter regime when in doubt.

The agent should recommend the design appropriate to the inputs and call out the trade-offs explicitly.

### 4. Banner copy and UI

The banner is a small piece of copy that has to do a lot of work. It needs to: tell the user what is happening in plain language, name the categories of trackers and the purposes they serve, offer a clear way to accept, a clear way to reject, and a path to granular preferences. Several recurring regulator-favored UI principles apply:

The "accept" and "reject" actions should have equal prominence. A bright "Accept" button next to a muted "Manage preferences" link with no visible "Reject" is one of the most-cited dark patterns in enforcement decisions. The fix is a "Reject" button visually equivalent to "Accept" — same size, same prominence, same number of clicks to use.

The granular preferences UI should not require more clicks than the accept-all path. Asymmetric friction is itself a regulator concern: a user who has to wade through a five-screen vendor list to reject is being nudged toward acceptance, and regulators read that as invalid consent.

The categories should be described in plain language at the surface of the UI, not in a "more info" expansion that the user has to discover. The plain-language description should name the purposes and roughly the vendors; a single sentence per category is the goal, and a link to the full notice is the supporting detail.

The banner should not block the substantive content of the page in ways that pressure consent. The page is allowed to load with strictly necessary trackers and present the consent UI without holding the user hostage. Some sites do block non-necessary content behind consent — the so-called "consent wall" — and the regulator posture on this varies; the agent should flag the design as elevated-risk and require counsel sign-off.

### 5. Withdrawal and re-prompting

Consent must be as easy to withdraw as to give. The practical implementation is a persistent re-entry point — a link in the footer, a button in account settings, or both — that re-opens the preferences UI. The withdrawal does not require justification, does not penalize the user, and does not degrade the parts of the service that do not legitimately depend on the trackers in question.

Re-prompting is a delicate area. A site may re-ask for consent when material new trackers are introduced, when a long period has elapsed since the last decision, or when the user signals confusion. A site that re-asks daily until the user gives in is in dark-pattern territory; the agent should recommend a re-prompt cadence of at least six to twelve months for renewal purposes, with immediate re-prompts only for material changes that the user is entitled to know about.

### 6. Honor browser signals

The Global Privacy Control is a browser-level signal that the user does not consent to sale or sharing under CCPA/CPRA. California's CPPA has been explicit that compliant businesses must honor it as a valid opt-out. The Do Not Track header is older and has weaker support in current law but should still be honored where feasible. The agent should design the consent stack to read these signals on the first request, apply the equivalent opt-out, and persist the choice; a user with GPC enabled should not see a banner that pretends the signal is not there.

### 7. Record what was chosen

Every consent decision should be logged with: a stable user or session identifier, the categories accepted or rejected, the banner version (linked to the copy and the vendor inventory at that moment), the timestamp, the originating jurisdiction (inferred or stated), the mechanism (banner click, GPC signal, in-product preferences page), and any IP-and-user-agent context required to defend the record. The records should persist long enough to demonstrate accountability in a regulator inquiry — typically a few years, calibrated to the relevant limitation periods and audit cycles in your jurisdiction.

The records are themselves personal data and should be retained with appropriate security and minimization. Do not retain them indefinitely; do not link them to advertising profiles; do not export them to processors who do not need them.

### 8. Integration with downstream systems

The consent decision is not a UI artifact; it is a signal that has to propagate. Analytics SDKs should not load until the relevant category is accepted, and should be configured to honor consent revocation if the user later opts out. Advertising vendors should receive the appropriate signal (TCF strings where applicable, GPC headers where applicable, vendor-specific consent flags otherwise). Tag-management systems should be configured to gate scripts on category, not to load all scripts and then attempt to silence them post hoc; silencing post hoc has been a regulator finding in multiple recent enforcement decisions.

Server-side or hybrid tracking patterns deserve specific attention. A first-party endpoint that proxies to a third-party processor is still subject to consent rules; the architecture does not change the analysis. Document the server-side flows explicitly and confirm consent is being checked at the gate.

## Inputs

The skill expects a description of the site, the trackers, and the audience regions. Pasting the current banner text and the current tracker inventory dramatically improves the quality of an audit. If the audience regions are unknown, the agent should default to "EU and US" and recommend the design that satisfies the stricter regime as the floor.

## Outputs

The Markdown deliverable is a complete consent-stack design: category model, default-state recommendation per regime, banner copy variants, granular preferences UI outline, withdrawal flow, signal handling for GPC, record retention plan, and integration notes for analytics and ad tech. The JSON output gives a structured summary suitable for piping into a CMP configuration or a compliance program tracker.

## Examples

A B2C subscription content site with EU and California audiences runs analytics, advertising, and session replay. The skill proposes the four-category model, opt-in defaults globally with region-aware withdrawal links, banner copy with equal-prominence Accept and Reject buttons, a one-screen granular preferences UI, honor of GPC at first request, a Do Not Sell or Share link in the footer for California, and a twelve-month re-prompt cadence with a record schema retained for two years.

A SaaS B2B site with EU traffic but no advertising still loads analytics and a session replay tool. The skill proposes a simplified three-category model (necessary, functionality, analytics), opt-in defaults under GDPR, banner copy that explains the session replay scope honestly (because session replay frequently captures content typed into forms before submission), and a settings page in the authenticated product for withdrawal once logged in.

## Limitations

This skill produces a design and an audit; it does not implement runtime consent enforcement and does not configure a specific CMP product. It does not perform the legal interpretation of a specific enforcement decision against a specific site. New US state privacy laws are landing frequently and the skill's general posture is calibrated to the regimes named in this document; expansion to other states requires per-state review. The TCF model evolves on its own version cadence and the agent's recommendations should be re-checked against the current TCF version where TCF participation applies.

## Sources reviewed

- https://github.com/orestbida/cookieconsent
- https://github.com/ethyca/fides
- https://github.com/theopenlane/awesome-compliance
- https://github.com/paulveillard/cybersecurity-gdpr-compliance
- https://github.com/strongdm/comply
