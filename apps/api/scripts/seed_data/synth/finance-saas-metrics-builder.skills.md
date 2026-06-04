---
id: skillsgit-curated/saas-metrics-builder
version: 1.0.0
name: SaaS Metrics Builder
description: Define and calculate core SaaS metrics from raw subscription data — MRR, ARR, NDR, GDR, CAC payback, LTV, burn multiple, magic number — with named definitions, formula choices, and the pitfalls each one is famous for.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: finance
tags: [niche:fp-and-a, saas-metrics, mrr, arr, net-dollar-retention, cac-payback, burn-multiple, subscription-analytics]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: [code_execution]
  tools_optional: [file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - saas metrics
  - MRR
  - ARR
  - net dollar retention
  - NDR
  - gross retention
  - GDR
  - CAC payback
  - LTV
  - burn multiple
  - magic number
  - rule of 40
  - subscription metrics
  - revenue retention
example_invocations:
  - "Calculate our SaaS metrics from this monthly subscription event file — MRR, NDR, CAC payback, LTV, burn multiple."
  - "Define how we should be measuring net dollar retention and what the pitfalls are."
  - "Build a metrics pack for our board update from raw billing data — flag any definition choices I should be aware of."
inputs:
  - name: subscription_data
    type: file
    required: true
    description: Subscription event data — at minimum customer ID, period, MRR or recurring revenue amount, and a flag for new, expansion, contraction, churn, or reactivation.
  - name: cost_data
    type: file
    required: false
    description: Optional — sales and marketing spend by period for CAC and CAC payback. Cost of revenue by period for gross margin.
  - name: cash_data
    type: file
    required: false
    description: Optional — cash balance and burn by period for burn multiple and magic number.
  - name: metric_definition_preference
    type: choice
    required: false
    description: Which definition conventions to use when multiple are defensible.
    choices: [bookings-based, billings-based, recognized-revenue-based, mixed]
  - name: business_segments
    type: text
    required: false
    description: Optional — segments to split metrics by (e.g., self-serve vs. sales-led, by product line, by customer size).
outputs:
  - name: metrics_pack
    type: markdown
    description: A structured metrics pack with each headline metric, the definition used, the value over the requested periods, and the noteworthy patterns.
  - name: definitions_appendix
    type: markdown
    description: An appendix specifying exactly how each metric was computed, the formula used, and any data exclusions.
  - name: pitfalls_called_out
    type: markdown
    description: A list of the pitfalls or definitional ambiguities that affected the calculations, with the choices made and the alternatives that would change the number.
  - name: data_quality_flags
    type: markdown
    description: Flags raised by the data — duplicate customer IDs, negative MRR not classified as churn, currency assumption issues, etc.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when an FP&A team, finance partner, or operator at a subscription business needs to produce a clean set of SaaS metrics — typically for a board pack, an investor update, a monthly operating review, or an internal benchmarking exercise. The skill is built for the moment when the user has raw subscription event data (or a billing extract) but no canonical computed metric layer, and wants both the numbers and a record of the choices behind them.

Use this skill when the user can provide customer-level subscription data with at least the basics: who, when, how much, and the lifecycle event (new, expansion, contraction, churn, reactivation). The skill is most accurate when the user supplies cost and cash data too, because the most useful SaaS metrics combine the subscription side with the spend side. The skill works for both early-stage SaaS (where definitions are still being formed) and growth-stage SaaS (where consistency over time matters more than raw value).

Do not use this skill to produce a single number divorced from its definition. SaaS metrics suffer from a definitional Wild West — net dollar retention is computed at least four credible ways, LTV has at least three, CAC has at least two. The skill makes the choices explicit and produces an audit trail; bypassing the audit trail defeats the point. Do not use the skill to invent the data — if the user lacks data, the right output is a clear "this metric cannot be computed from the input, here is what is needed" rather than a plausible-looking but unsupported number.

## How to apply

SaaS metrics are deceptively simple. The formulas are mostly arithmetic. The hard part is the definitions: what counts as recurring, what counts as new versus expansion, what counts as churn versus contraction, whether to use trailing-twelve-month or quarterly windows, whether to use gross or net or contribution margin in CAC payback. The skill's job is to compute the metrics correctly under named definitions, document the choices, and call out where a different choice would materially change the number.

The methodology below produces a metrics pack in four passes. The first pass classifies the data and flags quality issues. The second pass computes the revenue metrics. The third pass computes the efficiency metrics. The fourth pass writes the commentary and the pitfalls.

### Step 1 — Validate the input data

Before computing anything, run the input through a quality check.

For subscription data:

- Is every row tied to a customer ID, a period, an amount, and a lifecycle event?
- Are MRR values stated in a consistent unit (monthly, not annualized for some rows and monthly for others)?
- Are negative values where you expect them — contractions and churn — and absent where you do not?
- Is the currency consistent or, if multi-currency, is there a stated FX policy?
- Are there duplicate customer-period rows? If so, are they intentional (multiple subscriptions per customer) or errors?
- Do new customer events have a positive amount, and do churn events have a negative amount equal to the prior MRR?

Raise every data issue explicitly in the data_quality_flags output. A metric computed from broken data is worse than no metric — it gives false confidence.

### Step 2 — State the definition framework up front

Before computing the first metric, write down the definitional choices the rest of the pack will inherit. At minimum:

- **Recurring vs non-recurring** — what counts as recurring revenue. Subscriptions count. One-time setup fees do not. Usage-based revenue counts if it is a stable run-rate from existing customers; it is contested if it is highly variable.
- **Bookings vs billings vs revenue** — which view of "revenue" the metrics are built on. The same business looks different through each lens.
- **Cohort definition** — what date establishes a customer's cohort (first paid subscription, first invoice, first usage).
- **Multi-product customers** — do you measure them as one customer or one per product. Affects new-vs-expansion classification.
- **Cancellation accounting** — does churn count at notice or at end-of-term.
- **Reactivations** — are reactivated customers new again, returned, or expansions.

Each choice produces different numbers. Document the choice and note when a different defensible choice would move the number by more than 5%.

### Step 3 — Compute the recurring revenue base

The foundation of every SaaS metric is the recurring revenue base, expressed at a point in time and as a flow over a period.

MRR at point in time: sum of monthly recurring revenue across all active subscriptions on that date.

ARR at point in time: MRR times twelve. For businesses with annual contracts, an alternative is to compute ARR directly from the contracted annual values; note which approach you used.

Build a month-by-month MRR table for the period in scope. Build the same table broken into new MRR, expansion MRR, contraction MRR, churned MRR, and reactivation MRR. The sum of these flows reconciles to the change in opening-to-closing MRR; if it does not, the data has a classification error, and the discrepancy goes to the data quality flags.

### Step 4 — Compute net and gross revenue retention

Net revenue retention (NRR) and net dollar retention (NDR) — used interchangeably in practice — is the share of beginning-period MRR from a cohort that remains as ending-period MRR from that same cohort, including expansion.

The pitfalls:

- The cohort is locked. NDR at month N from a January cohort uses only customers active in January, not customers added since. Mixing cohorts is the most common error.
- The window matters. Trailing-twelve-month NDR is the standard; quarterly NDR is noisy; monthly NDR is mostly random walk.
- Whether to include new customers added in the window. The standard definition excludes them (NDR measures what happens to the customers you started with). Some sloppy definitions include them and produce inflated numbers.

Gross revenue retention (GRR) and gross dollar retention (GDR) excludes expansion: it is the share of beginning-period MRR retained from a cohort, capped at 100%. GRR is always less than or equal to NRR. The gap between them is the expansion strength of the base; useful diagnostically.

Compute both for the requested periods. State the cohort window. Note that a healthy SaaS business in the mid-market segment typically runs NDR between 100% and 115%; outside this range needs explanation rather than celebration or alarm.

### Step 5 — Compute customer acquisition cost and CAC payback

CAC is the fully-loaded cost of acquiring a customer. The choices:

- **Numerator**: sales and marketing spend in the period. Sales spend includes sales-team payroll, commissions, sales tools, sales-event spend. Marketing spend includes campaigns, content, paid acquisition, marketing-team payroll, marketing tools. Some definitions exclude payroll; that produces a misleadingly low CAC.
- **Denominator**: new customers added in the period. The choice is whether to use customers or accounts (if multiple subscriptions per account) and whether to use a lag (sales spend in month N produces customers in month N plus a lag of one or two months).

CAC payback is the number of months of gross margin from a new customer that equal the CAC. Two definitions are common:

- **Gross-margin CAC payback**: CAC divided by (new ARR added in period times gross margin), expressed in months by multiplying by twelve. This is the standard.
- **Contribution-margin CAC payback**: uses contribution margin instead of gross margin, recognizing that some customer-service costs are post-acquisition.

State which one you used. Note that a benchmark of 12 months is healthy for mid-market SaaS, 24 months is the upper bound for venture-backed enterprise SaaS. CAC payback computed on a single month is noisy; the four-quarter average is more stable.

### Step 6 — Compute lifetime value

LTV is the most-abused SaaS metric. Three common definitions:

- **Gross-margin LTV with constant retention**: average customer MRR times twelve times gross margin divided by annual churn rate. Implicitly assumes retention is constant and customers eventually churn. The simplest definition; reasonable for businesses with stable churn.
- **Cohort-based LTV**: actual cumulative gross-margin revenue per customer in a closed cohort, plus a projection of the open tail using the observed survival curve. Better but data-hungry.
- **Contribution-margin LTV**: same shape, contribution margin instead of gross margin.

All three are sensitive to retention assumptions. A 95% net retention rate produces a much smaller LTV than a 110% net retention rate; the gap is not linear. If retention is above 100% on a net basis, the simple constant-churn formula produces infinity, which is the formula breaking, not the business being infinite. In that case, switch to a finite-horizon LTV (lifetime value over the next 3 or 5 years) or a contribution-margin LTV with a terminal-value assumption.

The LTV-to-CAC ratio is a derived metric beloved of investors. Three is the common benchmark; the benchmark assumes the same retention and margin choices were made on both sides. State the assumptions; do not just report the ratio.

### Step 7 — Compute the burn multiple

Burn multiple is the efficiency of cash burn relative to net new ARR. Defined as net burn for the period divided by net new ARR for the period. A burn multiple below 1 is excellent; 1-to-2 is healthy; above 2 indicates an inefficient growth motion.

The pitfalls:

- Net burn definitions vary. The clean one: change in cash from operations and investing, excluding financing. Adding back stock-based compensation produces a different but useful view.
- Net new ARR is the closing minus opening ARR. The window matters; quarterly is the most-cited.
- The ratio is meaningless if net new ARR is negative; report it as "n/a — negative net new ARR" and discuss the underlying numbers.

### Step 8 — Compute the magic number

Magic number is a quarterly efficiency ratio: net new ARR in the quarter divided by sales and marketing spend in the prior quarter. Used as a quick read on go-to-market efficiency.

A magic number above 1 indicates a strong growth motion; 0.5 to 1 indicates a workable but tightening motion; below 0.5 indicates the growth model needs work. The pitfall is that the metric is most reliable in steady-state — for a company changing its sales motion or pricing, the prior-quarter lag is the wrong window.

### Step 9 — Compute the rule of 40

Rule of 40 is a heuristic: a SaaS company's revenue growth rate plus its operating margin (or its free-cash-flow margin) should sum to 40% or more. It is a portfolio-level rule, not a target, but boards and investors use it as a quick read.

Compute both versions: revenue growth plus operating margin, and revenue growth plus free-cash-flow margin. The free-cash-flow version is tougher and more honest. The pitfall is that the rule was developed for public SaaS at scale; a Series A company is not expected to satisfy it, and using it as a benchmark for early-stage companies misleads.

### Step 10 — Segment, where data permits

For any of the above metrics, segmenting reveals more than the aggregate. The most common segments:

- By customer size (small, mid-market, enterprise). The metrics differ dramatically: enterprise has higher CAC payback and lower churn; small business has the inverse.
- By acquisition motion (self-serve vs. sales-led). Mixing them obscures both.
- By product line, for multi-product companies.
- By cohort (yearly cohorts of new customers), to see whether unit economics are improving or degrading over time.

If the user provided segment information, produce a segmented view. If not, note that the aggregate metrics obscure segment differences that may be material.

### Step 11 — Surface the pitfalls in the output

For each metric reported, append a one-line pitfall callout. Examples:

- "MRR includes self-serve trial conversions only after the first paid month — pre-paid trial revenue is excluded. Including it would inflate new MRR by an estimated 4%."
- "NDR uses the trailing-twelve-month window with cohorts locked at month-12-prior. Quarterly NDR is volatile and not reported here to avoid confusion."
- "CAC denominator counts logos, not accounts. If we counted accounts (multi-subscription customers as one), new-customer count would be 8% lower and CAC would be 8% higher."
- "LTV uses constant-churn formula. With the observed 102% NDR, the formula would diverge; this report uses a 5-year horizon LTV instead."

The pitfalls section is the most important part of the output for a careful reader. Do not bury it.

### Step 12 — Produce a single coherent metrics pack

The headline output is a one-page pack with the major metrics organized into three blocks:

- **Revenue and retention**: ARR, MRR by month with the breakdown, NDR (trailing-twelve-month), GRR (trailing-twelve-month).
- **Efficiency**: CAC, CAC payback, LTV, LTV-to-CAC, magic number, burn multiple, rule of 40.
- **Cash and runway**: cash balance, change in cash, runway in months at current burn.

Each block has the numbers, a one-line trend note (improving, stable, deteriorating), and a one-line pitfall. The definitions appendix follows. Then the data quality flags.

### Step 13 — Connect metrics to operating reality

Metrics in isolation are noise. A short commentary block at the top of the pack should connect them to the operating story: "NDR has improved from 105% to 109% over the trailing twelve months, driven primarily by the launch of the enterprise tier in the back half of last year. CAC payback worsened from 13 months to 17 months over the same window, reflecting the heavier sales-team investment required to land enterprise deals; these two metrics are connected and should be read together."

### Step 14 — Refuse to fabricate values

Where data is missing or ambiguous, do not invent. Mark the line clearly: "LTV not computed: insufficient cohort history (less than 18 months of data)." This is more useful than a number with an unstated assumption built in.

### Step 15 — Set up a repeatable metric run

Note at the end of the pack: this same definitions framework should be used in the next period to produce a comparable pack. Metric reporting that changes definitions between periods is uninterpretable. If a definition change is required, the prior-period numbers should be restated under the new definition and the change called out explicitly.

## Inputs

- **subscription_data** (required) — customer-level subscription events with lifecycle flags.
- **cost_data** (optional) — S&M and cost-of-revenue by period.
- **cash_data** (optional) — cash balance and burn by period.
- **metric_definition_preference** (optional) — which convention to use for ambiguous metrics.
- **business_segments** (optional) — segments to split metrics by.

## Outputs

- A one-page metrics pack with revenue, retention, efficiency, and cash blocks.
- A definitions appendix specifying exactly how each metric was computed.
- A pitfalls section listing the choices made and the alternatives that would move the number.
- A data quality flags section listing any issues found in the input data.

## Examples

### Worked example — Producing the quarterly metrics pack for a Series B SaaS business

**Inputs given to the skill:**

- subscription_data: a monthly file with 1,400 customer rows over 30 months, columns customer_id, period, mrr, lifecycle_event, segment.
- cost_data: monthly S&M spend and gross margin by quarter.
- cash_data: month-end cash balance.
- metric_definition_preference: "recognized-revenue-based."
- business_segments: "self-serve vs. sales-led."

**Output produced by the skill (the one-page pack, abridged):**

> **SaaS metrics pack — Q1**
>
> **Revenue and retention (trailing twelve months):**
> - ARR exit: $14.6M, up from $11.2M four quarters prior (+30%).
> - NDR: 108%. Trend improving from 104% four quarters ago. Pitfall: cohort-locked; if computed on a non-cohort basis, NDR would be ~3 points higher.
> - GRR: 92%. Below the 95% mid-market healthy floor. Investigating the small-business segment, which has logo churn approaching 18% annualized.
>
> **Efficiency (quarterly):**
> - CAC: $11,200 blended. Self-serve: $1,400. Sales-led: $34,800.
> - CAC payback (gross-margin basis): 15 months blended. Self-serve: 6 months. Sales-led: 22 months.
> - LTV (5-year horizon, contribution-margin): $42,300 blended. LTV-to-CAC: 3.8x blended.
> - Magic number: 0.83. Healthy but tightening from 1.1 four quarters ago.
> - Burn multiple: 1.4. Within the healthy band; flag that it deteriorated from 0.9 in the prior year as the sales-led motion scaled.
>
> **Cash and runway:**
> - Cash $18.4M, down $1.2M in the quarter. Runway 16 months against trailing-three-month burn of $1.15M.
>
> **Commentary:** The NDR improvement reflects the success of the expansion campaign in the enterprise segment; the CAC payback deterioration reflects the same investment. The two metrics should be read together — the business is making the deliberate trade of higher CAC payback in exchange for higher retention and expansion. Burn multiple deterioration is the cash consequence of that trade and is within plan.

**Pitfalls called out:** 4 items, including the cohort-locked NDR choice, the contribution-margin LTV choice (with the constant-churn-formula failure noted), and the use of a 5-year horizon for LTV.

**Data quality flags:** 3 items, including 12 customer rows with negative MRR not classified as churn or contraction (sent back for cleanup), and a self-serve segment with 47 customers missing the segment tag (allocated to "unknown" and excluded from segment splits).

## Limitations

This skill produces metric definitions that are defensible but not unique. A board, investor, or counterparty using a different definition will compute different numbers. The skill makes the choices explicit so the user can defend them and so future periods can be computed consistently; it does not resolve industry-wide definitional disagreement.

The skill is most accurate for software and subscription businesses with relatively stable unit economics. For marketplaces, usage-based products, or transaction businesses, the metrics still apply but require additional definitional work the skill cannot do without input. Hybrid models (subscription plus services plus transaction) need explicit guidance on what is recurring; the skill prompts the user but cannot decide.

LTV is the metric most sensitive to small assumption changes. A 100 basis point change in net retention can move LTV by 30% or more. The skill reports LTV with an explicit horizon and assumption set; treat any single LTV number as an estimate with a wide error band.

The skill does not audit. Numbers reported are derived arithmetically from the input data, not validated against a general ledger or a billing system. For board or audit purposes, the input data should be tied back to those systems before the metrics are published.

Benchmarks cited (NDR around 100-115%, CAC payback under 24 months, LTV-to-CAC of 3x) are public-domain heuristics for mid-market SaaS. They are starting points for conversation, not absolute standards; segments, geographies, and stages produce wide variation that the skill cannot capture in a single benchmark.

## Sources reviewed

- https://github.com/JerBouma/FinanceToolkit
- https://github.com/ESeufert/theseus_growth
- https://github.com/CamDavidsonPilon/lifetimes
- https://github.com/pmorissette/ffn
- https://github.com/gopalakrishnanarjun/modelmyfinance
- https://github.com/jdvelasq/cashflows
