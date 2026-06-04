---
id: skillsgit-curated/creative-test-planner
version: 1.0.0
name: Creative Test Planner
description: Design a structured paid-ad creative test with a falsifiable hypothesis, a variant matrix, a holdout group, win criteria, budget guardrails, and a learning-velocity plan.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [niche:paid-acquisition, creative-testing, ad-testing, experiment-design, learning-velocity, holdout, variant-matrix, paid-social]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - creative test
  - ad test
  - creative experiment
  - variant matrix
  - creative iteration
  - hook test
  - format test
  - creative holdout
  - learning velocity
  - creative refresh
  - creative fatigue
  - test plan
  - paid social test
example_invocations:
  - "Design a creative test for our new value-prop on Meta."
  - "We want to test three video hooks against our current static — give me the plan."
  - "Build a structured creative test program we can run for the next eight weeks."
  - "How should we test a new offer without losing the bidder's learning on the current concept?"
  - "Plan a hook vs. format vs. offer test matrix for paid social this quarter."
inputs:
  - name: program_context
    type: text
    required: true
    description: Platform(s), monthly spend, business model, primary conversion event, current baseline CPA or ROAS, and whether the test is on a prospecting or retargeting program.
  - name: hypothesis_seed
    type: text
    required: true
    description: What the team believes will work and why. A user belief like "new social-proof hook will beat current product-led hook" or a problem like "current creative is fatigued and we don't know which lever to pull next."
  - name: change_dimension
    type: choice
    required: false
    description: Which creative variable the test most needs to isolate.
    choices: [hook, format, offer, audience-message-fit, landing-page, full-stack]
  - name: constraints
    type: text
    required: false
    description: Brand-safety constraints, regulatory text requirements, legal review timelines, production budget, creative-team capacity, locked launch windows, and any "must-not-touch" assets.
  - name: weekly_volume
    type: text
    required: false
    description: Weekly conversions and weekly spend on the program. Used to estimate per-variant sample size and test duration.
outputs:
  - name: test_plan
    type: markdown
    description: A complete one-page test plan with hypothesis, variant matrix, holdout strategy, sample size, duration, win and stop criteria, monitoring cadence, and post-test rollout plan.
  - name: production_brief
    type: markdown
    description: A short brief the creative team can build against — concept-by-concept descriptions, copy guardrails, format specs, and which dimensions are held constant.
  - name: open_questions
    type: markdown
    description: Clarifications whose answers would change the design.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a paid-media team wants to test creative deliberately rather than "ship five new ads and see what wins." The skill is for situations where the team has already decided that the creative lever (not the audience lever, not the bidding lever) is the right one to pull, and now needs a plan that distinguishes between a real concept win and noise.

Typical triggers:

- A program has been running the same creative concepts long enough that CPA is drifting up and the team wants the next concept to be picked on evidence, not opinion.
- A new value proposition, offer, or campaign is launching and the team wants to test it inside paid before scaling.
- The creative team has built a backlog of ideas and the paid team needs a way to prioritize which to ship first.
- A platform has rolled out a new format (vertical video, collection, interactive) and the team wants to know whether to invest in production.
- Leadership has asked for a "creative testing program" and the team needs a defensible framework rather than a list of ads.

Do NOT use this skill for:

- Pure A/B copy tweaks on a single ad headline — those are inside an ad, not a test program.
- Audience or bidding experiments — those need an experimentation skill, not a creative one.
- Landing-page tests where the ad is held constant — that is a CRO test.
- "Should we change our brand" decisions — that is a brand-research project.

## How to apply

The shape of a good creative test is: one falsifiable hypothesis, a small set of variants that isolate one or two variables, a holdout that protects the current winner, and a stopping rule that prevents both premature calls and indefinite wandering. Walk the requester through the following steps.

### Step 1 — Pin the question to one or two variables

Creative has many simultaneous variables: hook, visual, format, length, offer, social proof, CTA, audience-message fit, landing-page handoff. A test that varies five of them at once cannot answer any of them.

Force a choice. Ask the requester: "If this test runs and we only learn one thing from it, what is the most useful one thing?" The answer becomes the **primary dimension**. A weaker secondary dimension is acceptable if the variant matrix can isolate it factorially without exploding cell count.

### Step 2 — Write the hypothesis as a falsifiable statement

A creative test hypothesis is not "let's try X." It is a falsifiable claim with a direction, a magnitude, and a metric. Template:

> "If we change `{dimension}` from `{control}` to `{variant}` on `{audience or placement}`, we expect `{metric}` to `{improve|degrade|hold}` by at least `{magnitude}` because `{causal story}`."

The causal story matters. A hypothesis without a causal mechanism is a guess; a hypothesis with one is testable in a way that updates the team's mental model regardless of outcome.

### Step 3 — Choose the unit of comparison

Decide whether the test compares concepts, campaigns, or ad sets:

- **Concept-level** tests put each concept in its own ad set under one campaign and let the platform's bidder choose impressions. Cleanest for "which message wins" but coarse on attribution.
- **Campaign-level** tests use separate campaigns with split budgets and ideally a budget-split feature the platform provides (campaign budget optimization with experiment tooling, A/B test feature, lift study, or geo split). Cleaner causal claim, slower to converge.
- **Ad-level within one set** tests are the most common and the least conclusive — the platform optimizer will starve the loser fast and you will not learn what would have happened under equal impressions.

Recommend the cleanest unit the program's volume can support.

### Step 4 — Choose the primary metric

The primary metric is the metric the test will be called on. Default ranking, best to worst:

1. **Downstream conversion CPA or ROAS**, measured at the platform with deduped server-side conversions, at a sample size the program's volume actually supports.
2. **First-touch-to-qualified-lead rate** (for B2B lead-gen with long sales cycles), measured at the warehouse against a stable cohort definition.
3. **CTR-to-conversion-rate composite**, only when conversion volume per variant is too low for a direct conversion read.
4. **CTR alone**, only as a last resort and only when paired with a downstream guardrail (see Step 5).

Reject "engagement" (likes, shares, comments, video views past 3s) as a primary unless the business literally pays for engagement. They are diagnostics, not decisions.

### Step 5 — Pick guardrail metrics

Guardrails are the metrics that say "even if the primary moved, do not ship." Minimum guardrail set:

- **Downstream conversion rate** if the primary is upper-funnel.
- **Cost per qualified lead or CAC** if the primary is volume-only.
- **Frequency** if the test is in retargeting or in a narrow audience.
- **Brand-safety flags** (comment sentiment, ad-disapproval rate) for any test using bolder copy or visual treatments.
- **Landing-page bounce or session-duration regression** if the variant changes the post-click promise.

Two to four guardrails. More than that and the team is back to "let's look at everything."

### Step 6 — Build the variant matrix

Limit to between two and five live cells, including control. Use a deliberate matrix:

- **2-cell**: control vs single variant. Use when the question is binary and volume is tight.
- **3-cell**: control vs two variants on the same dimension (e.g., social-proof hook vs feature-led hook). Use when the team has two strong candidates.
- **Factorial 2×2**: control + three combinations across two dimensions (e.g., hook × format). Use only if per-cell weekly volume is ≥ the platform's documented learning minimum.
- **5-cell concept bake-off**: control + four concepts. Use when the goal is "find the next concept to scale," not "answer a hypothesis." Expect higher false-positive rate and plan for a confirmatory follow-up.

Hold every variable not under test constant: same audience, same placement set, same landing page, same CTA, same campaign objective.

### Step 7 — Decide the holdout strategy

Three options, in increasing order of statistical strength and operational cost:

- **Within-program holdout.** A share of impressions (typically 10–20%) is reserved for the current control concept regardless of bidder preference. Cheapest; protects against bidder over-rotation. Most platforms support this through their A/B test or split-test tooling.
- **Geo holdout.** A randomized set of geographies sees the new variants; a matched set sees only control. Strongest within-platform causal claim. Requires enough geos and enough per-geo volume.
- **Conversion-lift / brand-lift study.** The platform randomizes who sees the ad vs PSA. Strongest causal claim for measuring "did the test concept produce incremental conversions" but only available on some platforms and requires meaningful spend per cell.

For most prospecting tests on Meta or Google, a within-program holdout is the right default. Recommend geo or conversion-lift only when the spend and the decision stakes justify it.

### Step 8 — Estimate per-cell sample size and duration

Use the program's weekly conversion volume per cell to estimate when the test will reach a useful read. Rough heuristics, to be replaced by the team's preferred sample-size calculator:

- For a binary conversion metric and a target detectable lift of ~10% relative, expect roughly 250–500 conversions per cell at typical baseline conversion rates. Below 5% baseline, sample requirements rise sharply.
- For ROAS or revenue-per-impression metrics with high variance, expect roughly 2–4× the conversion sample, because revenue distributions have fat tails.
- Plan duration as `target_conversions_per_cell / weekly_conversions_per_cell`. Add one full business cycle (typically one week for B2C, two weeks for B2B) to absorb day-of-week and recency effects.

If the math says the test will take more than six weeks at current volume, escalate: either reduce cell count, raise budget, choose a more sensitive metric, or accept a coarser detectable effect.

### Step 9 — Set the win criteria, stop criteria, and tie-breaker

Before the test launches, write down:

- **Win** — what result causes the team to scale the variant? "Variant beats control on primary by ≥ X% with at least Y conversions per cell and no guardrail breach."
- **Stop early for harm** — what result causes the team to kill the variant before duration? "Variant trails control on primary by ≥ Z% with at least W conversions, or any guardrail breach."
- **Stop early for win** — is early stopping for a positive result allowed? Usually no; if yes, name the sequential testing correction the team is using.
- **Tie-breaker** — if primary is flat, which guardrail or diagnostic determines the call? Decide once, in writing, before the data arrives.

### Step 10 — Plan the launch ramp

Do not launch all cells at full budget at once. Recommended ramp:

- Day 0–2: launch all cells at equal share-of-budget, low-volume QA mode. Verify pixel/CAPI fires for every cell, landing pages serve, frequency caps respect the test boundary.
- Day 2 onward: ramp to full test budget. Allow the platform's learning phase to elapse before reading any cell-level numbers.
- Mid-test: do not edit creative, budget, or audiences. Edits invalidate the test.

### Step 11 — Define a daily and weekly monitoring cadence

Daily check: pixel/CAPI health, spend pacing per cell, any platform policy flags, any obvious anomaly.

Weekly check: cell-level primary and guardrail metrics, no early-call decisions. Document the read each week so the post-test narrative is not reconstructed from memory.

Do not stare at intra-day numbers. Bidder volatility looks like signal and corrodes decision discipline.

### Step 12 — Calibrate against learning velocity, not just statistical power

For paid social and short-form video, the cost of taking eight weeks to learn one thing is often higher than the cost of being 80% sure instead of 95% sure. A creative testing program is judged on:

- **Number of decisions per quarter.** How many "ship / kill / iterate" calls did the program produce?
- **Concept hit rate.** What share of tested concepts produced a scalable winner?
- **Time-to-decision.** Median weeks from variant brief to ship-or-kill.

Design each test to maximize learning velocity at acceptable risk. A 70%-confident weekly call is often more valuable than a 95%-confident monthly one.

### Step 13 — Plan the post-test rollout

Define in advance what happens at the end:

- If the variant wins, how does it get into the standing creative rotation? Does it replace the control or run alongside?
- If the variant loses, what is the next test in the queue? A losing test should still produce a queued follow-up; otherwise the program is reactive.
- If the result is inconclusive, what is the smallest change that would make the next test conclusive? Reduce cells, increase budget, sharpen hypothesis, or extend duration — name which.

### Step 14 — Write the production brief

The creative team needs a brief that names exactly what to build. For each variant:

- The concept in one sentence.
- The hook in one or two specific phrases (not "social proof" — the actual line).
- The visual direction.
- The format and aspect ratios required by each placement.
- The CTA.
- The held-constant elements (so the team does not "improve" the control out of comparability).
- The legal or brand-safety guardrails.

Constraints are part of the brief, not a separate document.

### Step 15 — Document open questions

Examples that often need answers:

- "Is finance willing to call winners on platform-reported CPA, or do we wait for the warehouse number?"
- "Can the creative team produce four concepts within three weeks, or do we run a smaller matrix?"
- "Is there budget headroom to absorb a 20% short-term CPA increase during the test, or does the test have to be inside the current budget envelope?"

### Step 16 — Sanity-check the plan against three failure modes

Before publishing the plan, walk these three:

- **"Optimizer eats my test"**: if the test relies on the bidder distributing impressions, the bidder will over-rotate to early winners. Mitigate with platform A/B test tooling, equal-share budget at the campaign or ad-set level, or geo split.
- **"Learning phase ate the first week"**: if the campaign was paused or restructured to run the test, the first 3–7 days of data are not reliable. Plan to ignore that window in the final read.
- **"We changed the meaning of the metric mid-test"**: if any upstream attribution change (lookback window, dedup key, conversion event definition) ships during the test, the read is invalid. Freeze relevant config for the test window.

### Step 17 — Write a one-page plan

Lead with the hypothesis. Then the variant matrix. Then the primary and guardrails. Then duration and stop rules. Then the production brief reference. Then the post-test rollout. Anything not on that page is supporting material.

### Step 18 — Calibrate confidence

Note the confidence level the plan is operating at — what assumptions, what unknowns, what the team should watch for that would change the design. Honest calibration beats false precision.

## Inputs

- `program_context` (required): platforms, spend, business model, primary conversion event, baseline.
- `hypothesis_seed` (required): what the team believes or wants to learn.
- `change_dimension` (optional): hook, format, offer, audience-message-fit, landing-page, or full-stack.
- `constraints` (optional): brand, legal, production, timeline.
- `weekly_volume` (optional): used to estimate sample size and duration.

## Outputs

- `test_plan` — one-page plan with hypothesis, matrix, holdout, metrics, duration, decision rules, rollout.
- `production_brief` — per-variant creative brief the production team can build against.
- `open_questions` — clarifications that would change the plan.

## Examples

**Example 1 — Meta prospecting, hook test, mid-budget DTC brand.**

Input: "$60k/month on Meta prospecting for a skincare brand. Current best concept is an ingredient-led video that's now four months old. We have a hunch that a social-proof / before-after concept could beat it. Three weeks of creative production lead time."

Expected behavior:
- Hypothesis: "If we replace the ingredient-led hook with a social-proof / before-after hook in the first three seconds of a vertical video, prospecting CPA will improve by ≥ 12% on a four-week read, because the cold-audience evidence in our brand-research suggests trust is the binding constraint."
- Matrix: 3-cell. Control (ingredient-led), Variant A (before-after with creator), Variant B (review-pull-quote overlay). All other elements held constant.
- Unit: separate ad sets under one campaign using the platform's A/B test feature for equal-share budget.
- Holdout: within-program via the platform A/B test tooling, ~33% per cell.
- Primary: CPA on the standard purchase event, deduped via pixel + CAPI with shared `event_id`.
- Guardrails: 7-day post-click conversion rate, frequency, comment-sentiment.
- Duration: four weeks, with reads at weeks 2, 3, 4 and stop-for-harm at week 2 if any variant trails by ≥ 20% with ≥ 200 conversions.
- Rollout: winner replaces control in standing rotation; losers are killed; if inconclusive, run a follow-up with one of the variants vs control at higher budget split.

**Example 2 — LinkedIn B2B SaaS, format test.**

Input: "$30k/month LinkedIn, single-image ads only. Wondering if document ads or conversation ads would unlock new volume."

Expected behavior:
- Hypothesis is reframed: format alone is not the variable; the audience-message fit changes with format. Recommend a hook-and-format factorial 2×2 (current hook + current format, current hook + new format, new hook + current format, new hook + new format), only if weekly MQL volume per cell supports the sample.
- If volume does not support a 2×2, drop to 2-cell — current best vs the most-different variant — and queue the second comparison as a follow-up.
- Primary: cost per MQL with offline conversion import enabled so the LinkedIn bidder optimizes against MQL, not form-fill.
- Duration: six weeks given low B2B volume.
- Open question: is offline conversion import live on this account, because if not, the test cannot read at the right metric and the prerequisite must ship first.

## Limitations

- This skill assumes the team has measurement integrity (deduped server-side conversions, stable attribution model). If not, defer to the Paid Channel Audit skill first; a creative test on broken measurement is wasted budget.
- Sample-size estimates are heuristics. For high-stakes decisions, use the team's preferred statistical calculator (sequential, Bayesian, or frequentist) and document which.
- The skill does not write copy or design creative. It produces the brief the team builds against.
- Platform features (A/B test tooling, geo split, lift studies) change. Methodology is stable; feature names and minimums are not — verify on the live platform.
- "Learning velocity" trade-offs depend on the team's risk tolerance. A regulated industry (financial services, health) cannot adopt the same speed-over-confidence posture a fashion DTC can.

## Sources reviewed

- https://github.com/facebookexperimental/Robyn
- https://github.com/google/meridian
- https://github.com/pymc-labs/pymc-marketing
- https://github.com/facebookincubator/GeoLift
- https://github.com/google/trimmed_match
- https://github.com/CamDavidsonPilon/lifetimes
- https://github.com/segmentio/utm-params
