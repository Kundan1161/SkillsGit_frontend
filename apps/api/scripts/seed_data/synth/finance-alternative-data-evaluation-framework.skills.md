---
id: skillsgit-curated/alternative-data-evaluation-framework
version: 1.0.0
name: Alternative Data Evaluation Framework
description: Evaluate an alternative data source on coverage, latency, accuracy, signal-to-noise, decay, capacity, vendor risk, and return on investment relative to subscription cost.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: finance
tags: [niche:open-financial-analytics, alternative-data, vendor-evaluation, signal-to-noise, data-coverage, signal-decay, capacity-analysis, vendor-risk]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: [code_execution]
  tools_optional: [web_search, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 10000
trigger_keywords:
  - alternative data
  - alt data
  - data vendor
  - data evaluation
  - signal to noise
  - data coverage
  - data latency
  - vendor due diligence
  - data ROI
  - subscription cost
  - data capacity
  - alpha decay
example_invocations:
  - "Evaluate this credit-card transaction panel vendor for use in our consumer coverage."
  - "Set up a framework to assess web-traffic data against our existing fundamental signals."
  - "Help me decide whether the satellite-imagery feed is worth its annual subscription."
inputs:
  - name: data_source_description
    type: text
    required: true
    description: A description of the alternative data source — what it measures, how it is collected, the vendor and product name (if any), the geographic and temporal coverage.
  - name: intended_use
    type: text
    required: true
    description: How the user intends to use the data — discretionary research, systematic factor input, monitoring of specific names, sector overview, or a combination.
  - name: existing_stack
    type: text
    required: false
    description: The data the user already has access to — fundamentals, estimates, prices, other alternative feeds. Used to assess incremental contribution.
  - name: budget_constraint
    type: text
    required: false
    description: The cost (annual subscription, per-pull pricing, total-cost-of-ownership) the user is evaluating against.
  - name: trial_data_available
    type: choice
    required: false
    description: Whether a trial or sample of the data is available for empirical evaluation.
    choices: [full-trial, sample-only, no-trial]
outputs:
  - name: evaluation_framework
    type: markdown
    description: A structured framework with the seven dimensions of evaluation, the questions for each, and how to score them.
  - name: empirical_test_plan
    type: markdown
    description: A test plan for the trial period — coverage checks, accuracy validation, signal tests, robustness checks.
  - name: vendor_due_diligence_checklist
    type: markdown
    description: A vendor-side checklist for legal, compliance, and operational risk.
  - name: roi_analysis_template
    type: markdown
    description: A template for computing return on investment with conservative, base, and optimistic assumptions.
  - name: decision_recommendation
    type: markdown
    description: A go / no-go / conditional-go recommendation structure with the named conditions and the trigger for re-evaluation.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Reach for this skill when a researcher, portfolio manager, head of data, or sourcing lead needs to evaluate an alternative data source for inclusion in an investment-research stack. The decision is harder than it looks. The vendor's pitch is built around the best historical examples; the buyer's needs are around the marginal contribution beyond what they already have. The skill is calibrated to bridge that gap with a disciplined, empirical evaluation.

Use this skill when the user can describe the data source, the intended use, and ideally has access to a trial or sample. The skill works without a trial — it produces a paper-evaluation framework — but the conclusions are weaker. Empirical evaluation against a representative sample is the single highest-leverage step in any alt-data decision.

Do not use this skill to source data vendors (a separate sourcing or RFP process belongs upstream). Do not use it for traditional data evaluations (price, fundamentals, estimates) where the comparison is between known competing vendors of well-defined commodities; the dimensions for those evaluations are different. Do not use it as a substitute for legal and compliance review — those are inputs to the framework, not produced by it.

The outputs are educational and methodological. Subscription decisions, vendor selections, and any use of alt-data in live investment decisions must be reviewed by legal, compliance, and risk functions appropriate to the user's firm and jurisdiction. Outputs are NOT investment advice and the empirical signal estimates the framework produces are historical reconstructions, not forecasts.

## How to apply

A useful alt-data evaluation runs along seven dimensions. The dimensions are not equally weighted across use cases; a systematic factor input weights signal-to-noise and capacity heavily, while a discretionary research input weights coverage and accuracy more. The framework names the dimensions, the questions inside each, and how to assemble them into a decision.

### Dimension 1 — Coverage

Coverage is the first dimension because it is a gating condition. A data source that covers the wrong universe is irrelevant regardless of how high-quality it is for what it does cover.

Coverage has several axes:

- **Entity coverage** — what fraction of the user's investable universe is in the data. A vendor that covers 90% of large-cap US consumer names is useful for that beat and not useful for mid-cap industrials or emerging-market names. Ask for the actual list of covered entities, not the vendor's coverage claim.
- **Temporal coverage** — how far back does the history go, and is the history actually populated or are there long gaps. Backtests require populated history; six months of clean history may be more useful than six years of patchy history but you cannot tell without looking.
- **Granularity** — daily, weekly, monthly. Sub-entity (store-level, SKU-level, segment-level) or entity-level. Granularity that the vendor exposes but does not measure cleanly is worse than honest entity-level aggregation.
- **Stability of coverage** — does the universe of covered entities change over time. A panel that adds and drops entities is harder to use than a panel whose coverage is stable, even if the changing panel has higher aggregate coverage.

A coverage failure is usually a hard no. A data source that does not cover the user's universe is not made useful by being cheap; it is just irrelevant.

### Dimension 2 — Latency

Latency is the lag between an event happening in the world and the data being available to the user.

- **Collection latency** — the time between the event and the vendor's collection.
- **Processing latency** — the time the vendor takes to clean, aggregate, and publish.
- **Delivery latency** — the time the user takes to ingest the data into their systems.

Total latency matters relative to the use case. A signal that is one week late is too late for a daily systematic factor but is fine for a monthly thematic check. A signal that is two days late is fine for an earnings-window monitoring use case if the next earnings is in two months, and is useless for an earnings-window monitoring use case if the next earnings is tomorrow.

Examine the **stability** of latency. A vendor whose typical delivery is two days but whose ninety-fifth percentile is twelve days will produce intermittent surprises. Latency should be measured in distribution, not in headlines.

Also examine the **revision pattern**. Some alt-data is published once and final; some is revised heavily in the first weeks after publication. A heavily-revised signal is much weaker for real-time decisions because the version known on the decision date is not the version that ends up in the published history.

### Dimension 3 — Accuracy

Accuracy is the agreement between the data and ground truth — when ground truth is available. For many alt-data sources, true ground truth is not directly observable; instead, accuracy is assessed via convergent validity.

Useful accuracy checks:

- **Cross-validation against reported financials.** When the company reports, does the alt-data signal that was visible before the report align with the direction and magnitude of the result. A vendor that systematically over-predicts the strong quarters or under-predicts the weak ones has a known bias that can be modelled.
- **Cross-validation against a second alt-data source.** Two independent measurements of the same phenomenon should agree directionally. Divergence is informative — it may reflect bias in one source, a real coverage gap, or noise.
- **Backfill consistency.** When the vendor extends history back to a new period, do the new values agree with what would have been seen at the time. Backfilled data that is internally consistent but not consistent with real-time observation is a frequent and costly trap.
- **Internal consistency.** Aggregates should sum to the component values; growth rates and levels should reconcile.

Document the named accuracy weaknesses. Every alt-data source has them. A vendor who cannot describe their data's known weaknesses has either not done the analysis or is hiding it; either is a meaningful signal.

### Dimension 4 — Signal-to-noise

Signal-to-noise is the dimension that decides whether the data actually contributes anything. The empirical test of this dimension is the heart of any alt-data evaluation.

For systematic uses, the diagnostic suite from cross-sectional factor research applies. Compute the information coefficient of the alt-data signal against the forward returns over the relevant horizons. Compute the quintile or decile spread. Examine the persistence and decay of the signal. Examine the cut by sector, by size, and by liquidity.

For discretionary uses, the diagnostic is less formal but the discipline is the same. Pick five to ten cases where the data should have been informative — known beats, known misses, known turning points — and ask whether the data would have pre-figured the outcome. The hit rate, the lead time, and the magnitude of the inference are the relevant metrics.

The signal-to-noise diagnostic should also test the **incremental value** beyond what the user already has. A signal that has independent edge is more valuable than a signal that is highly correlated with existing fundamentals and merely restates them. The cleanest test is to regress forward returns on the user's existing signals and the alt-data signal jointly; the t-statistic on the alt-data coefficient measures incremental contribution.

### Dimension 5 — Decay and capacity

Even strong signals decay. Alt-data signals decay especially fast because the user community in alt-data is sophisticated and competitive — what works today is often crowded within months.

Two related questions:

- **Decay** — at what rate is the signal's edge eroding. Compute the IC and quantile spread in early periods of the history and in recent periods. A signal whose edge is half what it was four years ago is decaying; a signal whose recent edge is one-quarter of the early edge is decaying fast. Some decay is normal; rapid decay is a yellow flag for crowding.
- **Capacity** — at what AUM does the signal's edge get consumed by the user's own market impact. Capacity depends on the universe (mid-caps have less capacity than large-caps), the rebalance frequency (higher turnover consumes capacity faster), and the size of the long-short portfolio (large gross positions consume capacity faster). Capacity is hard to estimate precisely; conservative estimates based on average daily volume and a market-impact model are the standard practice.

The decay-and-capacity dimension is often where exciting signals lose their luster. A signal with 0.10 in-sample IC, 0.04 recent IC, and capacity that runs out at $100M deployed is a different proposition than a signal with 0.06 stable IC and capacity that supports $5B. Both are real, but they are not interchangeable.

### Dimension 6 — Vendor risk

The data is one thing; the vendor is another. Vendor risk evaluation covers operational, legal, and compliance posture.

Operational:

- **Stability of delivery.** How often have the vendor's pipelines failed or been delayed in the last twelve months. Ask for a real answer; the vendor knows.
- **Engineering maturity.** Documentation, versioning, deprecation policy, support response times.
- **Business viability.** Is the vendor profitable. Are they raising. Is the leadership stable. A vendor that goes out of business takes the historical data with them in practical terms.

Legal and compliance:

- **Provenance.** Where does the data come from. Some sources (consented panels, public records, official statistics) are low-risk; others (scraped sites, brokered data, third-party app SDKs) carry meaningful legal risk.
- **Permitted-use restrictions.** Does the contract permit the use cases the user intends. Many alt-data contracts have restrictive language that constrains derivative-product creation, redistribution, or cross-team use.
- **Material non-public information (MNPI) posture.** Most alt-data is non-MNPI; some has been challenged. The vendor's own analysis of MNPI risk, and their handling of it, is part of evaluation.
- **Privacy posture.** PII handling, especially for transaction and behavioral data. Privacy regulations vary by jurisdiction and are tightening over time.
- **Audit rights.** Does the contract allow the buyer to audit the data's provenance and processing.

A vendor whose risk profile is high enough to require senior compliance escalation should know that before the deal closes. The framework should surface the risk early, not after the data is integrated and decisions are running through it.

### Dimension 7 — Return on investment

The final dimension is the comparison between the contribution the data is expected to make and the cost it carries.

The cost side includes:

- **Subscription cost** — annual fee.
- **Total cost of ownership** — engineering effort to ingest, validate, and maintain. Often comparable to or larger than the subscription on a small-vendor first integration.
- **Switching cost** — if the data becomes embedded in research processes, removing it later carries cost. Heavier integration means heavier switching cost.

The contribution side is harder. For systematic uses, the contribution can be quantified as the incremental Sharpe or expected return contribution of the signal, scaled by the AUM that can use it. For discretionary uses, the contribution is the value of the inferences the data enabled that the user would not have reached otherwise. This is inherently squishy; the framework recommends a structured estimate with conservative, base, and optimistic assumptions, and a sensitivity analysis showing which assumptions matter.

A clean ROI structure:

- Stated dollar value of marginal alpha or improved decisions (per year, base case).
- Stated annual cost (subscription + amortized integration + ongoing engineering).
- Multiple of value over cost, with the conservative and optimistic ranges.

A data source whose base-case ROI is less than two-to-one is rarely worth the integration friction. A data source whose conservative-case ROI is below one-to-one carries downside risk that needs explicit acknowledgment.

### Putting the dimensions together — the decision

The decision is rarely a uniform yes-or-no. The framework recommends one of three outcomes:

- **Go** — the data clears every dimension at the level the use case requires. Move to contract negotiation with the standard compliance and integration playbook.
- **No-go** — the data fails on at least one dimension that the use case cannot accommodate. Document the failure and the conditions under which the decision should be revisited.
- **Conditional go** — the data passes the gating dimensions (coverage, latency, vendor risk) but the signal evaluation needs more depth or the ROI is borderline. Negotiate a longer trial, a deeper sample, a phased subscription, or a paid pilot. Pre-commit the conditions under which the conditional becomes a full subscription, so the decision is not endlessly deferred.

### Cross-cutting practices

- **Run the empirical evaluation before talking commercials.** Vendor commercials are designed around urgency; the most useful information comes from the data, not the conversation.
- **Time-box the evaluation.** Two to six weeks is typical. Evaluations that drag past two months produce stale data and indecision rather than better answers.
- **Pre-commit minimum thresholds.** Before the evaluation begins, write down the IC, hit rate, coverage percentage, latency, and ROI levels the data must clear. Decisions made against pre-committed thresholds are more robust than decisions made against shifting feelings of "is this good."
- **Plan for ongoing monitoring.** A data source that passed evaluation a year ago may not pass now. Schedule annual re-evaluation, with the same framework, on every data subscription. The most expensive alt-data is the data that is paid for but no longer used.

### Calibrating the framework to the use case

- **Systematic factor input.** Weighting tilts toward signal-to-noise, decay, capacity, and stable coverage. Accuracy matters less in absolute terms than its stability.
- **Discretionary research.** Weighting tilts toward coverage of the names in scope, accuracy on specific cases, and the analyst's ability to interrogate the data. Capacity barely matters.
- **Monitoring use.** Weighting tilts toward latency, stability of delivery, and ease of operationalizing into a dashboard or alert.
- **Sector overview.** Weighting tilts toward breadth, history, and the ability to cut by sub-segments.

### Common failure modes in alt-data evaluation

A few specific failure modes recur across alt-data evaluations and are worth flagging because they tend to be invisible in the vendor's own materials:

- **Cherry-picked vendor case studies.** Vendors lead with the names where the signal worked. The framework counters this by selecting the evaluation universe in advance from the user's coverage, not from the vendor's examples.
- **Backfill that does not match real-time observation.** Backfilled history often looks cleaner than what would have been visible at the time. Where possible, evaluate the signal on history that the vendor produced in real-time, not history that was constructed retrospectively.
- **Latency that is good on average and terrible on key dates.** A vendor whose median latency is two days but whose pre-earnings latency stretches to ten days is unusable for the highest-value use case even if the headline latency reads well. Test the latency around the dates that matter.
- **Hidden survivorship in the panel.** A panel constructed from currently-active merchants, currently-tracked properties, or currently-listed apps may exclude the entities that failed during the historical window. The exclusion biases the historical signal upward.
- **Free trials that are too short to evaluate.** A two-week trial cannot evaluate a quarterly factor. Negotiate a trial that spans at least one full cycle of the use case before signing.

### When to walk away early

Some alt-data evaluations should end before the deep dive. The framework recommends a 30-minute screen for hard nos: coverage that doesn't include the user's universe, latency that doesn't meet the use case, vendor risk that would not pass a routine compliance review, or pricing that is incompatible with even an optimistic ROI. The deep empirical work is for the candidates that clear the screen.

## Inputs

- **data_source_description** (required) — what the source measures and who provides it.
- **intended_use** (required) — how the user plans to use the data.
- **existing_stack** (optional) — the data the user already has.
- **budget_constraint** (optional) — the cost the data is being measured against.
- **trial_data_available** (optional) — full trial, sample, or no trial.

## Outputs

- A structured evaluation framework along the seven dimensions.
- An empirical test plan for the trial period.
- A vendor due-diligence checklist for legal, compliance, and operational risk.
- An ROI analysis template with conservative, base, and optimistic cases.
- A go / no-go / conditional-go decision recommendation with named conditions.

## Examples

### Worked example — Evaluating a consumer credit-card transaction panel

**Inputs given to the skill:**

- data_source_description: "Vendor panel of anonymized US consumer card transactions; claimed coverage of approximately 5% of US debit/credit volume; daily delivery with weekly aggregation; eight-year history. Anonymized at point of collection."
- intended_use: "Pre-print monitoring of US large-cap consumer staples and discretionary names; systematic input into a quarterly factor model; supporting input to discretionary coverage."
- existing_stack: "Fundamentals, estimates, two adjacent alt-data feeds, internal earnings model."
- budget_constraint: "Annual subscription quoted at $X; integration effort estimated at one senior data engineer-quarter."
- trial_data_available: "sample-only — 18 months of history on 200 covered tickers."

**Output (abridged):**

> **Coverage assessment.** Vendor coverage for top-50 US consumer names: 47 covered with stable history, 3 with patchy coverage. Coverage for the next 100 names: 76 covered with usable history. Conclusion: coverage clears the gate for the top-50 names; conditional for the next layer.
>
> **Latency assessment.** Collection-to-publication median latency: 2 business days; 95th-percentile latency: 9 days. Revision: published values revise meaningfully within the first 14 days, stabilizing thereafter. Conclusion: latency clears the gate for monthly factor uses; the revision pattern is a yellow flag for any use that depends on values within the first week after publication.
>
> **Accuracy assessment (on the sample).** Quarterly aggregated vendor revenue change correlates with reported revenue change at r=0.62 across the top-50 names. Strong cases (consumer staples with stable models) show r > 0.75; weaker cases (discretionary names with high gift-card or non-card revenue) show r < 0.4. Documented bias: under-coverage of cash and gift-card transactions tilts the panel toward credit-heavy demographics. Conclusion: accuracy is usable with bias model; specific names should be screened.
>
> **Signal-to-noise (on the sample).** Cross-sectional IC of vendor-implied revenue surprise against forward 21-day returns: 0.07 in-sample, 0.05 in the most recent 36-month window. Long-short quintile spread Sharpe (gross of cost): 0.9. Incremental t-stat over existing internal earnings model in joint regression: 2.1. Conclusion: incremental signal is real and meaningful, with visible decay over time.
>
> **Decay and capacity.** Decay across the sample is consistent with the broader alt-data trend; signal half-life on the relevant horizon is shortening. Capacity estimate at acceptable market-impact: approximately $X00M deployed across the universe, sufficient for the intended factor allocation but constraining if the use scales.
>
> **Vendor risk.** Vendor is profitable, six-year operating history, documented data provenance via licensed anonymized panels with explicit consent. Contract permits intended uses with redistribution restriction; MNPI posture documented; PII handling reviewed by vendor's external counsel annually. Audit rights present. Conclusion: vendor risk is acceptable for the intended use; legal review needed for the redistribution clause.
>
> **ROI.** Base-case alpha contribution estimated at $Y across the deployed portfolio per year; cost (subscription plus amortized integration plus ongoing engineering): $Z. Base-case ROI: 3.4x; conservative-case ROI: 1.6x; optimistic: 5.1x. Conclusion: ROI clears the threshold in the conservative case.
>
> **Decision: conditional go.** Move forward with the subscription contingent on (a) signed compliance review of the redistribution clause, (b) full-trial extension to 36 months and the full top-100 name list to confirm the signal evaluation on out-of-sample data, and (c) committed integration plan with named senior data engineer. Re-evaluate after twelve months of live use against the same framework.

The full output would include the empirical test plan, the vendor due-diligence checklist, the ROI template, and the decision structure as fully expanded sections.

## Limitations

This skill produces a framework for evaluation and a structured decision, not an empirical evaluation by itself. The most valuable analyses require trial data, which the user must obtain. A paper-only evaluation can identify hard nos (coverage failures, gating latency, legal red flags) but cannot validate the signal claim.

The skill is calibrated to evaluation of a single source. Evaluating a portfolio of sources or designing an alt-data strategy across a firm involves additional considerations — interaction between sources, redundancy, vendor concentration risk, central versus team-level subscriptions — that are out of scope.

The signal-to-noise diagnostic depends on the user's universe and use case. A signal that scores well in one user's evaluation may score poorly in another's because the universes or strategies are different. Do not transfer signal evaluations across firms without confirming applicability.

The ROI analysis is necessarily forecast-dependent. Alpha contribution is hard to estimate prospectively and easy to over-estimate by anchoring on vendor case studies. The framework recommends conservative, base, and optimistic cases with sensitivity analysis precisely because the central case is fragile.

Legal and compliance review is an input to the framework, not a substitute for it. The framework cannot certify the regulatory acceptability of a data source for a given firm and jurisdiction; that requires qualified counsel.

The framework cannot anticipate every operational failure mode of a vendor's pipeline. Live deployment surfaces failure modes that evaluation can only sample. Plan for the failure modes operationally with redundancy, monitoring, and the ability to remove the source from production at short notice.

Outputs are educational. Subscription decisions, vendor selection, and any use of alt-data in investment processes must be reviewed by the appropriate functions in the user's firm. Nothing produced by this skill is investment advice.

## Sources reviewed

- https://github.com/microsoft/qlib (MIT)
- https://github.com/quantopian/alphalens (Apache-2.0)
- https://github.com/JerBouma/FinanceToolkit (MIT)
- https://github.com/ranaroussi/yfinance (Apache-2.0)
- https://github.com/AI4Finance-Foundation/FinRobot (Apache-2.0)
- https://github.com/jerryxyx/AlphaTrading (no LICENSE file — methodology pointer only)
- https://github.com/OpenBB-finance/OpenBB (AGPL-3) — referenced for methodology of open financial data terminals; no code or prose reused
