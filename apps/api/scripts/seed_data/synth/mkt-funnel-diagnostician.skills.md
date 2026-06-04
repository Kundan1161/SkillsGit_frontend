---
id: skillsgit-curated/funnel-diagnostician
version: 1.0.0
name: Funnel Diagnostician
description: From a list of funnel-stage drop-offs, diagnose where the leaks are, generate ranked hypotheses for each leak, and produce a test plan ordered by expected impact.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [niche:conversion-rate-optimization, funnel-analysis, drop-off, diagnosis, hypotheses, test-plan, segmentation, prioritization]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8500
trigger_keywords:
  - funnel analysis
  - funnel drop-off
  - conversion funnel
  - funnel leak
  - signup funnel
  - checkout funnel
  - onboarding funnel
  - activation funnel
  - test plan
  - hypothesis generation
  - prioritized hypotheses
  - drop-off diagnosis
example_invocations:
  - "Our signup funnel drops 60% between email entry and password creation. Why?"
  - "Give me a ranked list of hypotheses for our checkout drop-off and what to test first."
  - "Walk our activation funnel from ad click to day-7 retention — where are we losing the most users?"
  - "Mobile signup converts at half the rate of desktop. Diagnose."
  - "Build a quarterly test plan starting from our funnel data."
inputs:
  - name: funnel_stages
    type: text
    required: true
    description: The ordered stages of the funnel with stage-to-stage conversion rates (or absolute counts) and the period the rates were measured over.
  - name: audience_and_source
    type: text
    required: true
    description: Who enters the funnel and where they came from (paid search, organic, email, referral, in-product, partner). Mix shifts diagnosis.
  - name: goal
    type: text
    required: true
    description: What outcome the funnel is meant to produce (signup, paid trial, retained user at day 7, purchase, demo booked).
  - name: segmentation
    type: text
    required: false
    description: Conversion rates by device, geo, channel, plan, or other relevant segments if available. Often reveals where the leak concentrates.
  - name: known_observations
    type: text
    required: false
    description: Heatmap, session-replay, support-ticket, or user-interview observations that point at specific stages. Used to calibrate hypothesis ranking.
  - name: traffic_volume
    type: text
    required: false
    description: Weekly volume at the top of the funnel, used to estimate which leak fixes are testable within reasonable windows.
outputs:
  - name: diagnosis
    type: markdown
    description: A walkthrough of the funnel naming the largest leaks, the supporting evidence for each, and the most plausible mechanisms (technical, design, copy, audience-mismatch, expectation-mismatch).
  - name: ranked_test_plan
    type: markdown
    description: A prioritized list of tests and ship-now fixes addressing each leak, ranked by expected lift, confidence, effort, and traffic-testability, with the recommended sequence for the next quarter.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Funnel Diagnostician

## When to use

Use this skill when a team has a multi-stage funnel — paid-ad to signup, signup to activation, free user to paid, cart to confirmation — and the stage-to-stage conversion numbers are known but the diagnosis is not. Typical surfaces include marketing-to-product handoffs, signup and onboarding sequences, checkout and post-purchase flows, free-to-paid conversion paths, and content-to-action funnels (newsletter to course, demo to closed deal). The skill is most useful before any tests are designed; it answers "what should we even test" with a defensible ranking.

The skill works whether the inputs are exact conversion percentages with confidence intervals, rough counts pulled from an analytics dashboard, or a written description like "we drop a lot of users between step 2 and step 3 on mobile." Better inputs produce sharper output, but the structure of the diagnosis holds either way. Skip the skill when the funnel is single-step (use the landing-page audit instead), when the request is to design one specific test (use the test designer), or when the question is "did our experiment work" (use the readout skill).

## How to apply

1. **Restate the funnel.** Lay out the stages in order with one-line names that any reader can understand without a glossary. If the inputs used internal codenames (`step_x42a`), translate them to plain English. Add the conversion rate (and absolute count if available) between each pair of stages. Add the eligibility for each stage explicitly — who is even counted in the denominator. The funnel as restated is the spine of the rest of the analysis; any later finding will reference these stage names.
2. **Compute the conversion math both ways.** Stage-to-stage conversion rates (each stage as a percentage of the prior stage) are useful for finding the leak. End-to-end conversion (each stage as a percentage of the top of the funnel) is useful for ranking the impact of fixing the leak. A stage with a 30% drop-off looks dramatic but if it sits at the bottom of a funnel where only 4% of the top reaches it, the absolute impact of fixing it is small. Present both views.
3. **Identify the largest absolute leak.** The leak that matters is the one where fixing the drop-off rate moves the most users. Multiply the leak's drop-off rate by the prior-stage volume to estimate users lost per period. The largest absolute leak is usually the priority — but not always; see step 4.
4. **Distinguish between leaks the team can fix and leaks the team cannot.** Some drop-offs are structural and not addressable through testing: the visit-to-add-to-cart drop-off on a marketing site reflects that not everyone is in-market today and that fact will not change by tweaking the page. The cart-to-checkout-start drop-off is much more addressable. Rank leaks by the product of size and tractability, not by size alone. Mark the structural leaks explicitly so they do not eat the test backlog.
5. **Compare each leak to a reasonable benchmark.** Industry-typical conversion rates for similar funnels (signup-to-activation, cart-to-purchase, demo-request-to-meeting-held) are not authoritative, but they bound what is plausible. A leak that puts conversion 20 percentage points below typical is a structural fault. A leak that puts conversion in line with typical is a "near the frontier" leak where wins will be smaller and harder. Setting this expectation early protects the team from overoptimism.
6. **Segment every leak.** Before generating hypotheses, ask what the segmentation shows. Mobile vs. desktop, paid vs. organic, new vs. returning, by geo, by plan, by signup source — the segmentation reveals where the leak concentrates and what kind of fix will help. A leak that is entirely mobile is a mobile-experience problem, not a copy problem. A leak that is entirely on paid traffic is an audience-quality or expectation-mismatch problem, not an interface problem. A leak that is uniform across segments is a structural problem with the step.
7. **Generate hypotheses across five mechanism categories.** For each leak, walk the categories systematically rather than gravitating to one favorite. (a) Friction — required fields, latency, captchas, multi-page forms, ambiguous next steps. (b) Clarity — vague labels, unclear value at this step, decision fatigue, jargon. (c) Trust — security signals missing, surprise pricing, unfamiliar brand, missing social proof. (d) Audience mismatch — wrong people reached this step, expectations set upstream do not match what they find here. (e) Technical — broken flows, errors, mobile rendering issues, third-party dependency failures, mismatched authentication. Each leak should have at least one hypothesis in each category before any are eliminated.
8. **Eliminate hypotheses that the evidence contradicts.** If support tickets show no complaints, the friction is not interfering at this step. If the segment data shows the leak is uniform across mobile and desktop, the hypothesis "mobile rendering" is ruled out. If the leak appears only on paid traffic from a specific campaign, the upstream campaign is the cause, not the funnel page. Make the elimination explicit so the reader can audit the reasoning.
9. **Score the remaining hypotheses.** Three axes: (a) expected lift if true (a "missing trust signal" hypothesis on a 60% drop is "high"; a "form field tooltip is awkward" hypothesis on a 5% drop is "low"); (b) confidence the hypothesis is the right one (a hypothesis backed by session-replay or interview data is "high"; a hypothesis from pattern-matching alone is "medium-low"); (c) cost to test (a copy change is "small," a structural redesign is "large"). Combine into a priority. Show the scoring so reasoning is auditable.
10. **Generate a test for the top hypotheses.** Each top hypothesis becomes a test with a one-sentence hypothesis statement, the primary metric, the secondary diagnostics, the guardrails, the expected MDE band, and the testability rating (can the funnel volume support a test of this MDE in a reasonable window). Tests that fail testability should be rewritten with a coarser MDE, scoped to a higher-volume segment, or replaced with qualitative methods.
11. **Honor the upstream-downstream rule.** Fixing an upstream leak amplifies the impact of downstream fixes, but only if the upstream fix improves the quality of the cohort reaching the next step, not just the count. If the variant brings more users through step 2 by attracting low-intent visitors, the downstream conversion rates may drop and the net is zero or negative. Pre-commit to measuring downstream conversion when testing an upstream fix. The funnel is not a stack of independent rates.
12. **Distinguish friction reduction from filter loosening.** Reducing required fields at signup makes signup easier; the result is more signups. Whether those new signups produce more activated users depends on whether the filter was screening out users who would have failed activation anyway. Many signup-flow tests look great at the signup step and disappear by activation. Diagnose this risk upfront by recommending each test be measured at signup AND at activation (or whatever the durable downstream metric is). For B2B, downstream typically means qualified-meeting-held or paid-conversion, not just signup-completion.
13. **Watch for selection effects in segment analysis.** A segment that converts well at step 2 may simply be the segment that self-selected through step 1. Comparing step-3 conversion of a tightly-filtered segment to step-3 conversion of a broad segment is misleading. When a segment shows a strong rate, check whether the segment is a meaningful audience or an artifact of upstream filtering. State the caveat in the diagnosis so the reader does not over-read segment lifts.
14. **Look for stage-skipping signals.** If the analytics show users reaching step 4 without an event for step 3, the stage instrumentation has a gap. The funnel is not actually what the dashboard says it is. Flag instrumentation gaps as the first finding when present; no amount of hypothesis-generation matters if the input data is wrong.
15. **Identify cohort effects.** A funnel measured over a long window mixes users with different upstream sources, marketing campaigns, and product states. If the funnel was measured over a quarter that included a major product launch, the rates at each stage are not stable — they reflect a mix of pre- and post-launch behavior. Recommend recomputing rates on a shorter, more recent window when stability matters. Cohort drift is a common but invisible threat to funnel analysis.
16. **Identify time-to-event distortions.** Some conversions take days or weeks (free trial to paid is typically 14 days; demo request to closed deal is typically 30–90 days). A funnel measured over a window that does not give downstream events time to occur shows artificially low downstream rates. Make the measurement window explicit and consistent across stages; ideally, only count cohorts whose downstream events have had time to mature.
17. **Look for the channel-funnel interaction.** Different channels feed different audiences who behave differently in the funnel. A funnel diagnostic that averages across channels can obscure that paid-search audiences pass step 2 and fail step 4 while organic audiences pass step 4 and fail step 2. A "channel-by-stage" matrix reveals where each channel underperforms its own potential. The fix may be channel-specific landing pages, channel-specific onboarding sequences, or channel-mix shifts rather than funnel-page changes.
18. **Sequence the recommended tests across a quarter.** Most teams have throughput for two to four tests per quarter on a given funnel. The first test should be the highest-priority leak that is testable within the traffic and time budget. The second and third tests should be independent of the first (so a winning first test does not invalidate the others). The fourth test, if any, can be a smaller experiment on the next-highest-priority leak. Document the sequence and the rationale for the ordering.
19. **Mark the "ship now" items.** Some funnel issues are not test candidates: a broken step, an accessibility defect, a typo in a critical button label, a misconfigured tracking event, a tap target below 44px on mobile. List these separately as "ship without a test." Test slots are scarce; do not spend them on bugs.
20. **Recommend the qualitative companion.** Funnel diagnosis from data alone is incomplete. A handful of moderated sessions with users in the affected segment often surfaces explanations the analytics cannot. Recommend qualitative research as the companion to the test plan, especially for leaks where multiple hypotheses survived elimination and the team cannot pick between them with the available data.
21. **Distinguish acute leaks from chronic leaks.** A leak that appeared in the last two weeks has a different diagnosis than a leak that has existed for 18 months. The acute leak warrants an incident-style investigation: what changed in code, in marketing campaign, in upstream traffic mix, in the third-party stack? The chronic leak warrants the test plan. Always ask the requester whether the leak is acute or chronic; the wrong assumption wastes a quarter of testing on a problem a config rollback would fix.
22. **Account for known optimization ceilings.** A funnel step that converts at 95% has limited upside; a step that converts at 30% has substantial upside. The expected lift of a "win" at the 95% step is smaller in absolute terms than at the 30% step, but the relative lift is also smaller, and the test takes longer to reach significance. Reflect this in the test-plan rankings — testing near a ceiling is rarely the highest-priority work.
23. **Watch for Goodhart drift.** If a previous round of optimization focused on raising the signup-completion rate, the current signup-completion rate may reflect that the team taught itself to score on that metric. Subsequent gains may come at the cost of a downstream metric that was not measured in the prior round. State the suspicion explicitly when prior tests are reported.
24. **Right-size the depth of the diagnosis.** A funnel with three stages and clean data does not warrant a fifteen-page analysis. Default to a one-page-per-leak diagnosis with a single-page test plan summary. A complex multi-channel funnel with segmentation needs deeper treatment.
25. **Return two artifacts.** The diagnosis document walks the funnel stage by stage with the largest leaks highlighted, the evidence per leak, the surviving hypotheses, and the qualitative-vs-quantitative-evidence split. The ranked test plan is a sortable list with the next-quarter sequence, the ship-now bugs, and a short note on qualitative research that should accompany the tests.

## Inputs

- `funnel_stages` — ordered stages with stage-to-stage rates or counts.
- `audience_and_source` — who enters and where from.
- `goal` — the outcome the funnel is meant to produce.
- `segmentation` (optional) — rates by device, geo, channel, plan.
- `known_observations` (optional) — heatmap, session-replay, ticket, or interview data.
- `traffic_volume` (optional) — weekly top-of-funnel volume for testability.

## Outputs

- A funnel-walk diagnosis: stage names, conversion math, largest leaks, evidence, mechanism hypotheses by category, and surviving hypotheses with eliminations shown.
- A ranked test plan: prioritized tests with hypothesis, metric, testability, and quarterly sequence; ship-now bug list; qualitative research recommendation.

## Examples

**Example 1: Signup-flow drop-off on mobile.**

*Input* — funnel: email entry (100%) → password creation (60%) → email verification (45%) → first session (38%); audience: paid-social to landing page, mobile-heavy; goal: first session = activation; segmentation: desktop converts email→password at 78%, mobile at 51%; observation: support team mentions occasional "verification link expired" complaints; traffic: 4,200 email entries per week.

*Diagnosis sketch* — Largest leak is email→password on mobile (49% drop). End-to-end activation is 38%; structural ceiling above industry typical is plausible to 50%, so headroom exists. Mobile concentration suggests friction or rendering, not copy. Surviving hypotheses, ranked: (1) password-creation step has a strict requirement (e.g., 12-char min with special chars) that mobile users abandon at higher rates; (2) password-input field has a known autofill issue on iOS Safari (mobile-only); (3) the step requires a CAPTCHA only on mobile (geo-IP-triggered); (4) lack of a "show password" toggle pushes typo retries on mobile keyboards. The "expired verification link" support volume is downstream and concerns email→verification, not email→password; flag separately. *Test plan* — (1) ship-now: add "show password" toggle (small, accessibility too); (2) test relaxed password rules (8 char min, allow no special char) vs. control on mobile only — high lift, high confidence, small effort; (3) audit autofill behavior, ship fix without test if a fix exists; (4) move CAPTCHA later in the flow or replace with risk-based, if feasible — medium lift, medium confidence, medium effort. Companion qualitative: five moderated mobile sessions on the signup step.

**Example 2: Checkout drop-off, DTC, post-launch.**

*Input* — funnel: add-to-cart (100%) → cart-view (80%) → checkout-start (55%) → shipping-complete (50%) → payment-complete (45%) → confirmation (44%); goal: confirmed order; segmentation: paid-social converts add-to-cart→checkout-start at 40%, email at 70%; observation: recent ad campaign drove a 3x increase in paid-social traffic; traffic: 22,000 carts per week.

*Diagnosis sketch* — End-to-end is 44%, which is in line with DTC typical; the absolute volume increase from the campaign is the story. Largest absolute leak is cart-view→checkout-start (25 percentage points lost, concentrated in paid-social). Acute, not chronic: the leak emerged with the campaign. Mechanism hypotheses: (1) audience-mismatch — paid-social campaign reached lower-intent visitors who add to cart for consideration but do not intend to buy at this session; (2) ad creative makes price-implicit promises the cart contradicts; (3) shipping cost shock at cart-view; (4) mobile-experience issue compounded by the heavier mobile mix on paid-social. Surviving after elimination: (1) and (3) are most plausible given the acute timing. *Test plan* — (1) test free-shipping threshold or shipping-cost transparency on the ad and PDP — medium lift, medium confidence, small effort; (2) test a "starting at" price on the ad creative, not just on the landing page — medium lift, medium confidence, small effort; (3) audit paid-social UTM intent — if the campaign targets cold prospecting on a fast-decision creative, retarget separately for warm intent — large lift if the audience-mismatch hypothesis holds, medium confidence, medium effort. Ship-now: ensure cart shows shipping cost line item from the start.

**Example 3: B2B trial-to-paid funnel.**

*Input* — funnel: trial-start (100%) → activated user (54%) → 5+ users in account (22%) → paid (9%); goal: paid conversion; segmentation: SMB activated at 60%, enterprise activated at 38%; observation: sales team reports enterprise prospects often want SSO before activating their team; traffic: 1,100 trial-starts per week, 14-day trial period.

*Diagnosis sketch* — Largest absolute leak is activated→5+ users (32 pp). Mechanism: friction at the team-invite step combined with SSO requirement for enterprise. Segmentation confirms enterprise concentration. Hypotheses: (1) SSO is unavailable on trial, blocking enterprise team adoption; (2) team-invite step is hard to reach (deep in settings); (3) trial period is too short for the team-adoption motion (14 days insufficient when invite-acceptance lag is multi-day); (4) admin who started trial does not have authority to add seats without IT approval. *Test plan* — (1) enable trial SSO on enterprise plans — large lift, high confidence, medium-large effort (engineering), high-priority but a build not a test; (2) test moving team-invite onto the welcome screen vs. settings — medium lift, medium confidence, small effort; (3) test a 30-day enterprise trial (segment-gated) — large lift, medium confidence, medium effort, slow to read (long time-to-event). Sequence: ship SSO; test invite placement; test the longer trial last. Companion qualitative: interview five enterprise admins who started a trial but did not reach 5 users.

## Limitations

- The skill does not query analytics; it works from the inputs provided. Missing instrumentation produces gaps the skill will name but cannot fill.
- Hypothesis ranking is opinionated; the actual lift can only be confirmed by testing.
- Long time-to-event funnels (60-day trials, multi-month sales cycles) require analyses with delayed observation that this skill flags but does not solve.
- Multi-touch attribution effects are out of scope; if upstream channels interact, the diagnosis assumes single-touch attribution as supplied.
- Network and viral funnels (where invited users become new top-of-funnel) need closed-loop modeling beyond this skill.
- The skill does not replace user research; qualitative companions are recommended for any leak where data alone leaves multiple hypotheses standing.
- The skill assumes the funnel is correctly defined in the inputs; redefining the funnel itself is a separate exercise that this skill can suggest but does not perform.

## Sources reviewed

- https://github.com/PostHog/posthog
- https://github.com/growthbook/growthbook
- https://github.com/spotify/confidence
- https://github.com/zalando/expan
- https://github.com/facebookarchive/planout
- https://github.com/Unleash/unleash
- https://github.com/Alephbet/gimel
