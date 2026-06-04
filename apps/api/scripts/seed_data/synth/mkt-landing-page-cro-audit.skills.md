---
id: skillsgit-curated/landing-page-cro-audit
version: 1.0.0
name: Landing Page CRO Audit
description: Audit a landing page or funnel for conversion friction and clarity, then return a prioritized backlog of fixes and tests ranked by expected lift, confidence, and effort.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [niche:conversion-rate-optimization, cro-audit, landing-page, funnel, prioritization, mobile, page-speed, social-proof]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: [web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9500
trigger_keywords:
  - cro audit
  - conversion audit
  - landing page audit
  - funnel audit
  - friction audit
  - conversion rate optimization
  - test prioritization
  - lift estimate
  - page speed conversion
  - mobile conversion
  - form optimization
  - cta audit
  - social proof audit
  - clarity audit
example_invocations:
  - "Audit our pricing page for conversion issues and give me a prioritized test backlog."
  - "Walk through our signup funnel from ad click to first session — where are we losing people?"
  - "Review this landing page and rank the top 10 fixes by impact and effort."
  - "What should we test first on our homepage if we have only enough traffic for two tests this quarter?"
  - "Audit our checkout for mobile friction."
inputs:
  - name: page_url_or_description
    type: text
    required: true
    description: The page or funnel under audit. A URL, a written description, copied content, or a stack of screenshots — whichever the requester can provide.
  - name: audience
    type: text
    required: true
    description: Who arrives on this page and where they came from (paid search, organic, email, referral, in-product, returning user). Audience and source drive the audit lens.
  - name: conversion_goal
    type: text
    required: true
    description: The single action the page is trying to drive (signup, demo request, purchase, download, waitlist join). One page, one goal.
  - name: current_metrics
    type: text
    required: false
    description: Current conversion rate, bounce rate, time on page, mobile share, traffic volume, any heatmap or session-replay observations the requester has on hand.
  - name: prior_tests
    type: text
    required: false
    description: Tests already run on the page (win, loss, inconclusive) and any findings or rules of thumb the team has learned.
  - name: constraints
    type: text
    required: false
    description: Brand or legal rules, design system limits, technical debt, freeze windows, or strict accessibility requirements that constrain the backlog.
outputs:
  - name: audit_findings
    type: markdown
    description: A structured audit organized by section (above the fold, value props, social proof, friction, mobile, performance, form, CTA, trust) with specific observations and the why behind each.
  - name: prioritized_backlog
    type: markdown
    description: A ranked test and fix backlog scored by expected lift, confidence, and effort, with the recommended next three tests and the reasoning for each.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Landing Page CRO Audit

## When to use

Use this skill when a team owns a landing page or a multi-step funnel, is unhappy with the conversion rate, and needs an opinion on what to fix first. Typical surfaces are marketing-site homepages, product feature pages, paid-search landing pages, signup flows, checkout flows, pricing pages, app-store equivalents (web app onboarding), and post-click sequences from an ad or email. The skill is most useful when traffic is large enough to support testing but small enough that the team has to pick — three tests will run this quarter, not thirty, and choosing the wrong three wastes a quarter.

The audit applies whether the requester gives a live URL the agent can review, screenshots, copied content, or a prose description. It does not require analytics access; if metrics are absent it produces a qualitative audit and explicitly flags the hypotheses that need data to confirm. Skip this skill when the page has no goal (use a different audit), when traffic is too low to support any test in a reasonable window (recommend qualitative research instead), or when the request is for copy generation rather than diagnosis (use a landing-page copy skill instead).

## How to apply

1. **Open with the conversion contract.** State in one sentence who the page is for, what they wanted before they arrived, what the page asks them to do, and what they get if they do it. If the requester did not supply this, derive it from the inputs and present it back as the first finding — alignment on the contract is the foundation of the audit. Misaligned contracts are the most common root cause of "the page does not convert" and the cheapest to fix.
2. **Identify the visitor's awareness rung.** A visitor from a Google search for "best CRM for small business" is solution-aware; a visitor from a retargeting ad for a named product is most-aware; a visitor from a generic display ad about "growing your business" may be problem-aware. The audit's expectations of headline, proof, and CTA aggressiveness shift with awareness. Mismatch between awareness and copy is a structural defect, not a tactical tweak.
3. **Run the five-second test on the hero.** From the hero alone, can a visitor say what the product is, who it is for, and what to do next? Score each of the three with a yes, a partial, or a no, and quote the specific words that produced the score. The first finding lives or dies here — if the hero fails, no later section will save the page.
4. **Inspect the headline against three failure modes.** (a) Vague verbs: "transform," "empower," "unlock" — these survive a swap with the competitor's product, so they communicate nothing. (b) Inside-out framing: "we are a platform that…" instead of an outcome the visitor cares about. (c) Buzzword density: "AI-powered, end-to-end, intelligent, holistic" — flag any string of three or more buzzwords back-to-back. Quote the headline and rewrite it as a directional fix to demonstrate the issue, not to ship the copy.
5. **Inspect the subheadline against the headline.** The subheadline should answer the obvious "okay, but how?" or "okay, but for whom?" without restating the headline. Flag restatement, flag missing answers, flag length over two lines.
6. **Score the primary CTA.** Three checks: is there exactly one primary CTA in the hero region (not two of equal weight); does the label name the action and the outcome (not "Submit"); is the friction of the action matched to the awareness rung (most-aware → "Buy now $29"; solution-aware → "Start free, no credit card"; problem-aware → "Get the report"). Two primary CTAs in the hero is one of the most common defects and one of the easiest fixes.
7. **Audit the social proof.** Look for specificity, recency, and relevance. Specificity: a named logo bar beats "trusted by leading companies." A number with a unit beats a number alone. A quote with a named human at a named company beats a quote with no attribution. Recency: a "G2 leader 2022" badge is stale if the year is wrong. Relevance: customer logos in the wrong segment for the audience (enterprise logos on a small-business page) are negative signal, not positive. Flag missing proof, flag fabricated-sounding proof, flag misplaced proof.
8. **Map the visitor's question sequence.** Imagine the visitor reading the page top to bottom and list the questions a real visitor would have, in order: "what is this," "who is it for," "what does it do," "why is it different," "what does it cost," "what could go wrong," "what do I do next." Then walk the page and mark which section answers which question. Gaps are findings. Sections that do not answer any question are candidates for cutting.
9. **Inspect the value-prop block.** Three to four payoffs is the convergent default across modern SaaS templates. Each payoff is a verb-led or noun phrase with a one- or two-sentence body. Flag: more than five payoffs (visitors stop counting); non-parallel structure (one is a verb, the next is a noun, the third is a question); body copy that lists features instead of payoffs ("Includes SSO" instead of "Your security team will not be paged at 2 a.m.").
10. **Inspect the proof of mechanism.** Modern SaaS pages typically include a "how it works" or product visualization. If absent on a page where the visitor is solution-aware or earlier, the page is asking for trust the visitor has not granted. If present but generic (a flowchart of three boxes that could describe any tool), the section is taking space without doing work. Flag both.
11. **Inspect the objection-handling section.** List the four to seven objections the audience would have for this offer, in the order frequency suggests: segment fit, price, security or compliance, switching cost, vendor risk, time to value, reversibility. Walk the page and mark which objections are answered, which are answered weakly, and which are silent. Silent objections are leaks; weakly answered objections are noise. The audit recommendation here is usually structural: add an FAQ or inline mini-sections, not a tweak to existing copy.
12. **Audit pricing as a conversion surface, not a reference.** If the page includes pricing, check whether the unit is named (per seat, per project, per usage), whether plan identities help self-selection ("for solo builders" vs. "for teams of 5+"), whether inclusions are written as benefits, whether the "talk to sales" plan has a trigger sentence, and whether the page handles the inevitable "but what does it really cost" anxiety. Pricing pages where the prices are accurate but the copy around them is silent leak conversions.
13. **Audit forms with friction first.** For any form on the page (signup, demo request, contact, waitlist): count required fields and judge each by whether the data is needed at this step (work email, yes; company size, maybe; how did you hear about us, almost never). Flag every field that is collected for marketing convenience rather than required to fulfill the next step. Flag every required field whose error message is generic ("invalid input") rather than instructive ("we need a work email, not a personal one"). Flag the absence of a one-line trust statement near a sensitive field. Recommend specific field removals with the recovered conversion estimate.
14. **Audit the CTA hierarchy across the page.** Count primary buttons (should be one per fold, three to five on the page, all leading to the same action). Count secondary CTAs (should be a small set with clear secondary purpose — see pricing, watch demo, read docs). Flag any link that competes with the primary CTA for the visitor's attention (a "learn more" link near the hero that pulls visitors deeper into the site is a leak). Flag exit-intent popups, intrusive chat widgets, and second-page CTAs that distract from the conversion path.
15. **Run a mobile audit even if the desktop audit ran first.** Modern landing-page traffic is majority mobile for most direct-response channels. On mobile, the audit shifts: hero is one paragraph, not two; primary CTA is sticky or thumb-reachable, not in a buried right rail; tap targets are at least 44 by 44 CSS pixels; modal forms collapse cleanly; long-press menus do not block CTA access; iOS Safari and Android Chrome render the hero without horizontal scroll. Flag any desktop-first decisions that surface mobile defects, and recommend mobile-specific variants.
16. **Estimate page speed without a live load.** From the inputs and known patterns, predict the heaviest assets: hero video or large image, web fonts above three weights, autoplay carousel, embedded chat widget, marketing tag stack. Each is a candidate for a load-time finding. Recommend specific lift-bearing fixes: convert hero video to lightweight format or static image with a "play" affordance, defer chat widget until after the largest contentful paint, prune marketing tags by audit, lazy-load below-the-fold images, ship a small critical-CSS file. If the requester supplied a real Lighthouse score, anchor the recommendations to it.
17. **Audit copy density and reading effort.** Long paragraphs and visual walls of text are friction. A landing page is read at a 9th-grade reading level by default; technical pages addressing senior engineers can climb a few rungs, but never to academic prose. Flag sentences over 25 words, paragraphs over four sentences, jargon used before it has been defined for the audience that will not have seen it.
18. **Audit the trust signals.** Trust signals are not the same as social proof. Trust includes: visible security and privacy posture (SOC 2, ISO badges with a link to a real attestation, a privacy policy that is up to date), a real human team page if the buyer is consultative, named investors if relevant, status page link, refund or cancellation policy stated near the buy button. Flag every claim that is unverifiable from the page itself ("bank-grade security" without a cert; "loved by teams worldwide" without specifics).
19. **Look for clarity defects in microcopy.** Microcopy is the small text that does outsized work: form labels, help text, button labels, error messages, empty-state hints, confirmation lines. Audit the microcopy near the CTA most aggressively — these few words are the last thing the visitor reads before deciding. "We will never spam you" is a classic clarity defect that needs replacing with the actual policy ("One email per week, unsubscribe in one click").
20. **Identify funnel-stage leaks.** If the input is a multi-step funnel, audit each step against the same lens: does each step have a clear job, a single primary action, no surprise required fields, a way back without losing state, and a sensible mobile rendering? Find the step with the largest absolute drop-off and prioritize fixes there before fixes earlier or later. Earlier-step fixes return less than late-step fixes when late-step conversion is the bottleneck.
21. **Distinguish defects from preferences.** A finding is a defect when it violates a tested principle of clarity, friction, or trust (a hero with no clear product description, two primary CTAs of equal weight, a required field that is not needed). A finding is a preference when reasonable practitioners disagree (warm vs. direct tone, image style, color palette). Mark each finding clearly; preferences belong in the rationale, not the backlog.
22. **Score each finding for prioritization.** Use three axes. (a) Expected lift: a directional estimate based on the size of the issue (a vague hero is "high"; a missing FAQ entry is "low"). (b) Confidence: how sure the auditor is that the fix produces the lift (a tested CTA-label change is "high"; a new social-proof section in an untested category is "medium"). (c) Effort: design and engineering and copy hours to ship (a copy change is "small"; a new section with images and engineering is "medium"; a structural redesign is "large"). Combine into a simple priority: high-lift, high-confidence, small-effort items go first. Show the math even when it is back-of-envelope; opaque scoring loses stakeholder trust.
23. **Recommend the next three tests.** From the prioritized backlog, name the three tests the team should run first. For each, write a single-sentence hypothesis, the primary metric to move, the expected lift band, the confidence band, the rough effort, and the rationale. Three is the default because most teams have throughput for two to four tests per quarter; if the requester named a different cadence, match it.
24. **Recommend the fixes that should ship without a test.** Not every fix is a test. Typo corrections, broken links, accessibility defects, factual errors, stale dates, missing alt text, and misaligned CTAs that violate basic UX should ship as bugs, not as treatments. The audit explicitly lists these as "ship now, no test" items so they do not sit in the test backlog consuming attention.
25. **Honor what is already known.** If the inputs included prior tests, do not recommend retesting recent losses without a new theory of the case, and do not propose changes that contradict a confirmed win. Cite the prior test in the recommendation when its result is relevant.
26. **Return two artifacts.** The audit findings document is organized by page section and includes one observation per finding, the why behind it, and the kind of fix it warrants (copy, structure, design, engineering, content). The prioritized backlog document is a sortable list with lift, confidence, effort, and priority columns plus the recommended next three tests with their hypotheses. Designers and copywriters consume the findings; the experiment owner consumes the backlog.

## Inputs

- `page_url_or_description` — URL, screenshots, copied content, or written description.
- `audience` — who arrives and where they came from.
- `conversion_goal` — the single action the page is meant to drive.
- `current_metrics` (optional) — conversion rate, bounce, time on page, mobile share, traffic.
- `prior_tests` (optional) — past wins, losses, and learnings.
- `constraints` (optional) — brand, legal, design system, accessibility, freeze windows.

## Outputs

- A structured audit organized by section (above the fold, value props, social proof, friction, mobile, performance, forms, CTA, trust) with specific observations and the why behind each.
- A prioritized test and fix backlog scored by lift, confidence, and effort, with the recommended next three tests and the bugs to ship now without a test.

## Examples

**Example 1: SaaS pricing-page audit, paid-search traffic.**

*Input* — page: pricing page for a project-management tool, hero is a four-line paragraph above a three-plan table, two primary CTAs (`Start free trial` and `Talk to sales`) of equal visual weight, no logos, no testimonials, FAQ section at the bottom; audience: SMB owners arriving from a Google search for "project management for small teams"; goal: paid-trial start; current rate: 1.8% paid-trial-start per pricing-page visitor.

*Audit sketch* — Hero fails the five-second test on "what is this" (the paragraph leads with company values, not product). Two primary CTAs split visitor attention; the data shows about half the demo requests turn out to be SMBs who should have self-served, suggesting label hierarchy is wrong. Social proof is entirely absent on a high-intent page — primary defect. FAQ is correctly placed but skips the "is this for our size" objection and the "how is this different from the free spreadsheet we already use" objection. Pricing plans are unnamed by identity ("Basic / Pro / Business" with no "for solo builders / for small teams / for growing companies" framing). Mobile: hero paragraph wraps to 12 lines on iPhone, pushing the price below the fold.

*Backlog sketch* — Tests, ranked: (1) replace hero paragraph with a three-line outcome-led headline and a sub-line, single primary CTA, secondary "Talk to sales" as a text link below — high lift, high confidence, small effort; (2) add a five-logo social proof bar with one line of context above the plans — medium-high lift, high confidence, small effort; (3) reframe plan identities with "for X" labels — medium lift, medium confidence, small effort. Ship-now bugs: stale "2023" award badge, alt text missing on logo bar, password-strength help text on signup form is confusing.

**Example 2: Mobile checkout audit, DTC consumer.**

*Input* — page: a three-step mobile checkout (cart → shipping → payment); audience: returning email subscribers and paid-social traffic; goal: complete purchase; current rate: 64% completion from step 1 to confirmation, with the largest drop-off between shipping and payment.

*Audit sketch* — Step-2 (shipping) is where the leak concentrates. Shipping form has 11 required fields including phone number and "how did you hear about us." Address autocomplete is missing on mobile. Apple Pay and Google Pay are offered only on step 3, not in the cart — moving them earlier reduces friction. Order summary is collapsed on mobile, hiding total until step 3, which violates the principle of cost transparency before commitment. Trust microcopy is absent near payment ("Secure checkout" badge but no statement of refund policy or what happens after submit).

*Backlog sketch* — (1) Move Apple Pay and Google Pay to step 1 cart — high lift on returning shoppers, high confidence, small effort; (2) remove phone-number and "how did you hear" from required, make optional — medium-high lift, high confidence, small effort; (3) add an inline order-summary line at every step showing total and shipping cost — medium lift, medium confidence, small effort. Ship-now: tap targets on "Edit address" link are 32px high, below the 44px minimum.

**Example 3: B2B demo-request page, content-marketing traffic.**

*Input* — page: a long-form demo-request page for a compliance-automation tool; audience: security and compliance leads arriving from a blog post; goal: demo booked; current rate: 2.4% demo-request rate per page visitor; prior tests: video hero lost to static image in a Q4 test; "see pricing" link removed from the page in Q3.

*Audit sketch* — Hero is now a static image (honoring the Q4 result). Primary CTA "Request a demo" is correctly the only above-fold CTA. Social proof bar is strong (eight named SOC 2-era logos). Mid-page features a long video that competes with the form for attention — leak. Form has nine required fields including "annual revenue" and "expected purchase timeline," which signal a sales-handling page rather than a customer-serving page — recommend reducing to four and moving the rest to the demo-call itself. FAQ is thorough; objection handling for "do we need to rip and replace" is missing. Pricing is absent from the page entirely (honoring the Q3 decision) but the lack of any price signal pushes a known share of mid-funnel visitors out of the funnel — recommend a "starting at" range without committing to the prior decision being reversed.

*Backlog sketch* — (1) reduce form to four fields — high lift, high confidence, small effort; (2) remove mid-page video or move below FAQ — medium lift, medium confidence, small effort; (3) add a "starting at" pricing line — medium lift, medium confidence, small effort, but stage carefully against the Q3 decision. Ship-now: broken link in footer to docs.

## Limitations

- The audit produces hypotheses, not certainties; expected-lift estimates are directional and must be confirmed by real tests.
- Without analytics access, the audit cannot rank by observed drop-off; recommendations may overweight surface defects and underweight invisible analytics issues.
- Brand and legal constraints can override audit recommendations; the prioritized backlog flags conflicts but does not resolve them.
- The audit assumes a Western, English-speaking audience by default; non-English pages require a localization pass with native review.
- Pages whose conversion rate is structurally low (highly considered B2B purchases, regulated industries) may resist short-cycle tests; the audit may recommend qualitative research as the next step instead of an A/B test.
- The audit does not produce production-ready copy; pair it with a landing-page copy skill for the rewrite step.
- The audit does not run page-speed tools; if the requester has Lighthouse or Core Web Vitals data, the speed recommendations are anchored to it, otherwise they are pattern-based.

## Sources reviewed

- https://github.com/growthbook/growthbook
- https://github.com/PostHog/posthog
- https://github.com/PaulleDemon/awesome-landing-pages
- https://github.com/leoMirandaa/shadcn-landing-page
- https://github.com/Blazity/next-saas-starter
- https://github.com/spotify/confidence
- https://github.com/Alephbet/gimel
- https://github.com/Unleash/unleash
