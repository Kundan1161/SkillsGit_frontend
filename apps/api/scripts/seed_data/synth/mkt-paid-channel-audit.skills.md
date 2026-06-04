---
id: skillsgit-curated/paid-channel-audit
version: 1.0.0
name: Paid Channel Audit
description: Audit a paid-media program end-to-end — account hygiene, campaign structure, creative diversity, measurement integrity, and incrementality readiness — and produce a prioritized remediation plan.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [niche:paid-acquisition, google-ads, meta-ads, linkedin-ads, account-audit, utm, conversions-api, measurement, incrementality]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: [web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - paid audit
  - ads audit
  - google ads audit
  - meta ads audit
  - facebook ads audit
  - linkedin ads audit
  - account hygiene
  - campaign structure
  - utm audit
  - conversions api
  - capi
  - dedupe pixel
  - negative keywords
  - audience overlap
  - incrementality
example_invocations:
  - "Audit our Google Ads account and tell me what to fix first."
  - "Run a paid social hygiene check on our Meta Ads Manager."
  - "Review our UTM and CAPI setup for measurement integrity."
  - "We just inherited a paid program from an agency — give me a structured audit."
  - "What's wrong with our campaign structure if CPA is climbing every week?"
inputs:
  - name: account_context
    type: text
    required: true
    description: Which platforms are in scope (Google, Meta, LinkedIn, TikTok, etc.), monthly spend per platform, business model (B2B SaaS, ecommerce, app, lead-gen, marketplace), and primary conversion event.
  - name: access_evidence
    type: text
    required: false
    description: Screenshots, exports, or pasted summaries from the ad platforms — campaign list with naming, conversion settings, attribution windows, pixel/CAPI status, audience lists, recent QA findings. The more concrete, the sharper the audit.
  - name: known_issues
    type: text
    required: false
    description: Symptoms the team has already noticed (rising CPA, drop in reported conversions, audience saturation complaints, learning-phase loops, attribution disputes).
  - name: priorities
    type: choice
    required: false
    description: What the requester most wants the audit to surface.
    choices: [hygiene, structure, creative, measurement, incrementality, all]
outputs:
  - name: audit_report
    type: markdown
    description: A structured report covering hygiene, structure, creative diversity, measurement integrity, and incrementality readiness, with severity-rated findings and a prioritized fix list.
  - name: remediation_plan
    type: markdown
    description: A two-week and ninety-day remediation plan with owners, effort estimates, and expected impact for each item.
  - name: open_questions
    type: markdown
    description: Specific clarifying questions whose answers would materially change the recommendations.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when someone is responsible for a paid-media program — across Google Ads, Meta Ads, LinkedIn Ads, TikTok, or any combination — and wants a structured, opinionated audit rather than a checklist someone could buy on a freelancer marketplace. Typical situations:

- A new in-house marketer or agency inherits an account and needs to know what to fix first without spending three weeks "exploring."
- CPA or CAC has drifted up week-over-week and nobody can point at a single cause; the team needs a systematic look at hygiene, structure, creative, and measurement together.
- Reported conversions diverged from CRM-measured conversions after iOS, browser, or platform attribution changes, and finance has stopped trusting platform numbers.
- A team is about to invest in a creative testing program or an incrementality test and needs to confirm the foundation can support reliable signal.
- Leadership wants a defensible answer to "is our paid program actually working" before approving the next quarter's budget.

Do NOT use this skill for:

- One-off tactical questions (a single keyword bid, a single ad copy choice) — those are inside this work, not the work itself.
- Organic search audits — see the SEO Site Audit skill.
- Lifecycle email or in-product programs that do not buy paid impressions.
- A request to "predict" what spend should be — that is media planning, not auditing.

## How to apply

Work the five lenses in order. Hygiene first because broken plumbing distorts every downstream signal. Then structure (which the platform algorithms react to), then creative (which is what the user actually sees), then measurement (which is what the team will argue about), and finally incrementality readiness (which is the only honest answer to "did it work").

### Step 1 — Frame the program

Before touching the account, establish what "good" looks like for this business. Capture, in plain language:

- The single primary conversion event the program is paid to produce, and whether it is measured at the platform, the warehouse, or both.
- The maximum acceptable CPA or minimum acceptable ROAS, and whether the target is from CAC payback math or just an inherited rule of thumb.
- The attribution window the team currently uses and the one finance uses; record both even if they disagree.
- Geographic and language scope, regulatory constraints (financial services, health, restricted categories), and brand-safety constraints.

If any of these are missing, list them as open questions before continuing. Auditing against an undefined target produces opinions, not findings.

### Step 2 — Hygiene: naming and taxonomy

Pull or request the campaign and ad-group list across every active account. For each, check:

- **Naming convention.** Is there a stable, parseable pattern (e.g., `Channel | Country | Funnel-stage | Audience | Theme | Variant`)? Inconsistent names break reporting joins and force humans to remember context that should live in metadata. Flag any campaign whose name does not parse.
- **Funnel labelling.** Is each campaign tagged with a funnel stage (prospecting, retargeting, brand defense)? If not, the team cannot answer "what share of spend is on cold audiences" without manual sorting.
- **Sunset hygiene.** Are paused campaigns older than ninety days archived or clearly labelled `[DEPRECATED]`? Long pause lists silently affect "average CPA" math when someone reports at the account level.

### Step 3 — Hygiene: negatives, exclusions, and audience integrity

For Google Ads and other search/PMax-style platforms:

- Pull the search-terms report (or its equivalent) for the last 30–90 days. Sample the top 100 by impressions and the top 100 by spend with zero conversions. Flag any that obviously do not match intent.
- Confirm a centrally managed negative-keyword list is applied at the account level, with at least the brand-safety and irrelevant-vertical lists present.
- Check for self-competing campaigns: identical or near-identical keywords across multiple campaigns without explicit testing intent.

For Meta and other audience-driven platforms:

- Look at audience-overlap reports. Two prospecting audiences with >25% overlap are bidding against each other; one should be excluded from the other.
- Confirm retargeting audiences exclude existing customers and current trial users. The fastest way to embarrass a paid program is to retarget a paying customer with a "sign up" creative.
- Confirm exclusion lists (employees, do-not-market, churned-and-unreachable) are applied to prospecting campaigns.

### Step 4 — Hygiene: bidding, budgets, and learning phase

- Identify campaigns that have been in "learning" or unstable status for more than the platform's documented learning window. Frequent budget edits, frequent creative swaps, or repeated audience changes are the usual causes; record the trigger pattern.
- Flag CPA/ROAS targets that have been changed more than once in the last two weeks. Each change resets pacing math.
- For lead-gen and B2B, check whether the conversion event the platform is bidding to has at least the minimum weekly volume the platform documents as required for stable optimization. If not, recommend an earlier funnel event as the bid signal with the primary event tracked downstream.

### Step 5 — Structure: campaign and ad-group geometry

Score the structure on three axes:

- **Granularity.** Are ad groups themed tightly enough that one creative set can serve every keyword/audience in the group, or so loosely that the creative cannot speak to the intent? Both extremes are wrong; document the symptom.
- **Concurrency.** Are there enough live ad groups per campaign for the platform's optimization to do real work, but not so many that budget thins below the per-cell minimum needed for the bidder to learn?
- **Match-type discipline (search).** Is there a deliberate split between exact, phrase, and broad, with negatives ensuring lower-match-quality variants do not poach higher-intent queries? A pure-broad account is not always wrong — but it must be measured against an exact-match baseline.

For platforms that combine campaign types under one umbrella (Performance Max, Advantage+), record the share of spend that is in fully-automated campaigns vs manually-controlled, and whether brand search is included or excluded.

### Step 6 — Creative diversity

Pull the live ad set. For each campaign, record:

- **Format mix.** Static, video, carousel, collection, vertical, horizontal. Single-format prospecting campaigns are a red flag; the algorithm cannot route the impression to the user who responds best.
- **Concept count.** How many distinct creative concepts (not variants) are running? "Concept" means a different message or hook; recolouring a button is a variant, not a concept.
- **Refresh cadence.** When was the newest creative shipped? Programs that have not introduced a new concept in 60+ days will see fatigue regardless of headline copy.
- **Concept-to-funnel fit.** Cold-audience creative should not assume the viewer knows the product. Retargeting creative should acknowledge prior visit. Mismatches are the most common conversion-rate killer.

### Step 7 — Measurement integrity: tagging

Audit UTM tagging on every live destination URL. Required minimum: `utm_source`, `utm_medium`, `utm_campaign`. Recommended: `utm_content` (creative or ad), `utm_term` (keyword for search), and a stable internal campaign ID. Check that:

- Naming is consistent across platforms (Meta's `paid_social` and Google's `cpc` must follow one convention, not two).
- Auto-tagging (Google `gclid`, Meta `fbclid`) is enabled where supported, and downstream systems read them.
- Click-redirect tools do not strip parameters. Verify with a live click on a sample of ads.
- Landing pages preserve parameters across same-domain navigation and into form submissions.

### Step 8 — Measurement integrity: pixel and server-side

For each platform, confirm:

- The browser-side pixel fires once and only once for the primary conversion event. Duplicates inflate platform-reported conversions and corrupt bidder math.
- A server-side conversion source (Conversions API for Meta, Enhanced Conversions or offline conversion import for Google, Conversions API for LinkedIn) exists and is sending the same primary event with a stable `event_id` for deduplication.
- The dedupe key matches between the browser event and the server event. Mismatched keys silently double-count.
- Customer-information matching parameters (email, phone, name, address — hashed) are populated where the platform supports them; match quality is the single biggest lever on attribution recall under restricted-tracking regimes.
- Offline conversion uploads (for lead-gen) are running on a documented cadence and reach the platform within the model's lookback window. Late uploads are invisible to the bidder.

### Step 9 — Measurement integrity: cross-system reconciliation

Pick the trailing 14 or 28 days. For the primary conversion event, compare:

- Platform-reported conversions per channel.
- Web-analytics-reported conversions for the same channel.
- CRM- or warehouse-reported conversions, filtered to first-touch or last-touch on the same channel.

Document the ratios. A platform that reports 2× the warehouse is usually over-counting view-through or duplicating pixel+CAPI without dedupe. A platform that reports 0.5× is usually under-matching identity or losing the click ID. Either way, the team should not be making budget decisions on the higher number until reconciled.

### Step 10 — Attribution model sanity

For each platform, record the attribution model the bidder is using (last-click, data-driven, view-through window) and the attribution model the team is using to report performance externally. If they differ, document the divergence — it does not have to be the same model, but the team must know it is comparing two different things.

Flag if the bidder is being optimized against a model the team does not trust. The bidder will deliver against its own truth.

### Step 11 — Incrementality readiness

Ask three questions:

- Has an incrementality test ever been run on this program? If yes, when, with what method (geo holdout, conversion-lift study, PSA test), and what did it find?
- Is there a non-trivial holdout group anywhere — a set of users, geos, or hours where the program is not running and could serve as a control?
- For the largest spend channels, is the volume high enough to support a statistically powered geo or conversion-lift test in a reasonable window (typically 4–6 weeks)?

If the program has never been tested and the team is making channel-mix decisions on platform-reported ROAS alone, mark this as a critical finding even if every other lens is clean.

### Step 12 — Brand-versus-non-brand isolation (search)

If Google Ads or Bing Ads is in scope, isolate brand keyword spend. Mixing brand and non-brand in one ROAS number is the single most common reason a paid program looks healthier than it is. Report blended, brand-only, and non-brand-only CPA/ROAS separately even if the team historically has not.

### Step 13 — Frequency, fatigue, and audience saturation (paid social)

For each prospecting campaign older than four weeks:

- Pull frequency over the trailing 7, 14, and 28 days.
- Plot CTR and CPA against frequency.
- Identify the frequency point where CPA inflects upward. This is the campaign's practical ceiling, not a universal number.

For retargeting, frequency caps are almost always too loose. Recommend an explicit cap when none is set.

### Step 14 — Landing-page handoff

Sample five live ads per platform. For each, click through and check:

- The landing page matches the ad's promise (offer, audience, language).
- Page-load time on a throttled mobile connection is under three seconds to first meaningful paint.
- The primary CTA is visible without scrolling on a typical phone.
- The form (if any) does not ask for fields the conversion bidder does not need.

Bad post-click experience is invisible inside the ad platform but can account for half of CPA drift.

### Step 15 — Score and rank findings

For each finding, assign:

- **Severity** — Critical (compromises every decision the program is making), High (materially distorts CPA/ROAS), Medium (real but bounded impact), Low (hygiene, no immediate business risk).
- **Effort** — Hours, days, or weeks; honest, not aspirational.
- **Dependency** — does anything else have to ship first?

### Step 16 — Build a two-week plan

Take every Critical and the easiest two or three Highs. Sequence them into a fortnight with named owners. Do not pile a quarter of work into the two-week plan; the goal is to get the foundation honest before the team makes any more bets.

### Step 17 — Build a ninety-day plan

The ninety-day plan can include structural rebuilds, creative testing programs, the first incrementality test, and measurement upgrades that require engineering time (server-side tagging migration, CRM-to-platform conversion pipes). Sequence so that anything dependent on measurement integrity lands after the measurement fixes.

### Step 18 — Document the open questions

End with a short, specific list of questions whose answers would change the recommendations. Examples:

- "Is the team willing to lose brand-search ROAS on the report in exchange for an honest non-brand number?"
- "Is there warehouse access to run a geo holdout, or will the first incrementality test have to be a conversion-lift study inside Meta?"
- "Does finance accept seven-day click attribution, or is it still on last-click last-30-day?"

### Step 19 — Write the report

Lead with the three findings that, if nothing else changed, would most move the program. Then the lens-by-lens detail. Then the plan. Then the open questions. Keep the lens-by-lens detail to bullets; reserve prose for findings whose context matters.

### Step 20 — Calibrate confidence

End every report with a confidence section. Note the depth of evidence reviewed (full account access, screenshots only, verbal summary), the time window covered, and the assumptions you carried. Auditors who pretend they had everything they needed lose trust faster than auditors who name their blind spots.

## Inputs

- `account_context` (required): platforms, spend, business model, primary conversion event.
- `access_evidence` (optional but recommended): exports, screenshots, or pasted findings.
- `known_issues` (optional): symptoms the team has already noticed.
- `priorities` (optional): hygiene, structure, creative, measurement, incrementality, or all.

## Outputs

- `audit_report` — lens-by-lens findings with severity ratings.
- `remediation_plan` — a two-week and ninety-day plan with owners and effort.
- `open_questions` — clarifications that would change the plan if answered.

## Examples

**Example 1 — Inherited Meta + Google account, B2C ecommerce.**

Input: "$180k/month split roughly evenly Meta and Google. We just took over from an agency. CPA on Meta is up 40% in eight weeks, Google is flat. Pixel and CAPI both installed but we don't know if they're deduped."

Expected behavior:
- Hygiene pass uncovers three retargeting campaigns missing customer-exclusion lists and a prospecting campaign with 38% audience overlap.
- Structure pass shows Meta running Advantage+ Shopping campaigns alongside legacy ABO campaigns competing for the same audiences without exclusions.
- Measurement pass finds pixel and CAPI sending the same event without a shared `event_id`, so Meta is counting roughly 1.4× the warehouse number.
- Two-week plan: dedup CAPI, exclude customers from retargeting, exclude legacy ABO audiences from Advantage+. Estimated CPA recovery: 15–25% on Meta within four weeks.
- Ninety-day plan: rebuild the prospecting structure around audience archetypes, ship four new creative concepts, run a geo holdout on Meta in week ten.

**Example 2 — B2B SaaS LinkedIn-only program.**

Input: "$25k/month LinkedIn Ads, lead-gen objective, MQL-to-SQL has dropped from 30% to 12% over the quarter."

Expected behavior:
- Hygiene pass finds no offline conversion import to LinkedIn — the platform is optimizing on form-fills, not on SQLs.
- Structure pass shows three campaigns with eight ad groups each and average weekly conversion volume per ad group below the platform's documented optimization minimum.
- Creative pass finds one concept across all campaigns; refresh cadence is 90+ days.
- Findings: the SQL-rate drop is plausibly explained by the bidder optimizing for lead volume against a fatigued creative pool, not by audience or product issues.
- Two-week plan: enable offline-conversion import keyed to SQL stage, consolidate ad groups to three per campaign, ship two new concepts.

## Limitations

- This skill works from evidence the requester supplies. With no exports or screenshots, the audit becomes a generic checklist rather than a finding-by-finding report; flag this in the open questions.
- Platform-specific UI and feature names change frequently. The methodology is stable; the exact menu paths are not. Verify on the live platform.
- This skill does not generate ad copy, design creative, or write keyword lists. It points at what to test and rebuild; the doing is downstream.
- Incrementality test design beyond "is the program ready" is the scope of a separate skill (see the MMM/MTA Reviewer and the broader experimentation skills).
- The skill assumes English-speaking platforms and standard verticals. Restricted categories (gambling, certain financial products, certain health) impose constraints this skill flags but does not resolve.
- Output is opinionated. Where the evidence supports two reasonable interpretations, the skill names both and recommends the one with the larger expected-value if-wrong cost.

## Sources reviewed

- https://github.com/facebookexperimental/Robyn
- https://github.com/google/meridian
- https://github.com/pymc-labs/pymc-marketing
- https://github.com/facebookincubator/GeoLift
- https://github.com/google/trimmed_match
- https://github.com/segmentio/utm-params
- https://github.com/google/ads-account-structure-script
- https://github.com/CamDavidsonPilon/lifetimes
