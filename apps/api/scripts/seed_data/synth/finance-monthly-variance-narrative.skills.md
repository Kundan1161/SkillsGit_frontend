---
id: skillsgit-curated/monthly-variance-narrative
version: 1.0.0
name: Monthly Variance Narrative
description: Turn a budget-versus-actual table into an executive narrative — name the real drivers, separate one-timers from trends, surface leading indicators for next month, and end with the asks finance needs from the operators.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: finance
tags: [niche:fp-and-a, variance-analysis, budget-vs-actual, monthly-close, fp-and-a-reporting, executive-narrative, management-reporting]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: [code_execution]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - variance analysis
  - budget vs actual
  - BvA narrative
  - monthly variance
  - monthly review
  - variance commentary
  - variance explanation
  - operating review
  - flash report
  - actuals narrative
  - month-end commentary
  - month-end variance
example_invocations:
  - "Write the variance narrative for April actuals against budget — here is the BvA file."
  - "Turn this budget-vs-actual table into a one-page executive memo for the monthly business review."
  - "Draft the variance commentary for our March close, with a leading-indicator section for April."
inputs:
  - name: bva_data
    type: file
    required: true
    description: A budget-versus-actual table for the period, by line item, with budget, actual, variance, and variance percent. Multiple periods welcome.
  - name: business_context
    type: text
    required: true
    description: One paragraph on the business — stage, model, what was happening operationally in the period (launches, hires, pricing changes, market events).
  - name: prior_period_drivers
    type: text
    required: false
    description: Optional — the named drivers from last month's variance narrative, so this month's narrative can track them.
  - name: audience
    type: choice
    required: false
    description: Who reads this — CEO, full leadership team, board, or department head.
    choices: [CEO, leadership team, board, department head]
  - name: known_one_timers
    type: text
    required: false
    description: Known one-time items the user already knows about — a large refund, a settlement, an accelerated invoice. Pre-disclosing prevents the narrative from mistaking them for trends.
outputs:
  - name: variance_narrative
    type: markdown
    description: A one-page executive narrative covering headline result, key drivers, one-timers, leading indicators, and asks.
  - name: line_item_table
    type: markdown
    description: A compact table of the largest variances with two-line commentary each.
  - name: leading_indicators
    type: markdown
    description: A short list of things to watch in the next period based on what this period revealed.
  - name: asks_from_operators
    type: markdown
    description: Specific questions or information requests finance needs from operating leaders to improve next month's narrative.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when an FP&A team or finance partner needs to translate a monthly budget-versus-actual table into a narrative document the leadership team can read in under ten minutes. The skill is the bridge between the close output (numbers locked, variances computed) and the operating review (where decisions get made). It is most useful in the two-to-five day window after books close, when the numbers are fresh but the operating leaders have not yet read them carefully.

Use this skill when the user has a clean BvA file with budget, actual, and variance columns at a meaningful level of detail — typically by department and major line item, not just a top-line P&L. The skill works best when the user can also describe what was happening operationally in the period; numbers alone do not produce useful narrative. The user should know who the audience is, because the narrative tone and depth differs sharply between a CEO read, a leadership team review, and a board read.

Do not use this skill to fabricate explanations. If a variance is unexplained, the right output is a clean "this variance is unexplained, here is what we know, here is what we are investigating" rather than a plausible-sounding guess. Do not use it as a substitute for talking to the operating leaders — the best narratives are confirmed against the people running the lines before they go out. Do not use it to mask operational problems with elegant prose; the narrative's job is to surface, not bury.

## How to apply

A monthly variance narrative does three jobs. It tells the reader what happened against plan, separating the meaningful from the noisy. It explains why each meaningful variance happened, distinguishing one-time events from emerging trends. And it points forward — telling the reader what to watch for next month and what decisions are now in front of them.

The methodology below builds the narrative in passes. The first pass is mechanical, separating the signal from the noise in the BvA. The second pass is causal, explaining the drivers. The third pass is forward-looking, identifying the leading indicators. The fourth pass is editorial, compressing everything into a one-page document the executive can read on a phone.

### Step 1 — Read the BvA and compute the noise threshold

Open with discipline about what counts as a variance worth narrating. A 2% miss on a $50K line is noise; a 2% miss on a $5M line is two percentage points of operating margin and needs explanation. Set a dollar threshold and a percentage threshold and treat variances as material when they breach either one.

A common default: material variances are those greater than the smaller of 5% of budget or $100K. Adjust the dollar threshold to the company's scale. Below the threshold, the variance is not narrated; it lives in the appendix.

### Step 2 — Compute the headline result

Before line-item commentary, state the headline. Two or three lines, no more: "Revenue came in at $4.2M against a budget of $4.0M, a $200K favorable variance. Operating expense came in at $3.6M against $3.5M, a $100K unfavorable variance. Operating income was $600K against a budgeted $500K, a $100K favorable variance." Then the cash and runway view: "Ending cash $14.2M, runway 17 months at the trailing-three-month burn."

The headline tells the reader what story they are about to read. Without it the reader has to compute it themselves from the line items, which most readers will not do.

### Step 3 — Decompose the revenue variance

For most businesses, the revenue variance is the most consequential one to explain. Decompose it into price, volume, and mix.

A price variance is what happens when the average selling price is different from the assumption. A volume variance is what happens when the unit count is different. A mix variance is what happens when the proportion of high-priced versus low-priced products is different. For subscription businesses, decompose into new bookings, expansion bookings, churn, and contraction; each of these has its own dynamics.

For each component, state whether the variance is favorable or unfavorable, the dollar amount, and the underlying driver. "Volume favorable by $150K driven by 12% over-plan in inbound demand for the small-business segment, primarily from a search-traffic increase after the March product update."

Avoid the temptation to call the variance "due to strong execution by the sales team" — that is praise, not analysis. The narrative needs the actual driver.

### Step 4 — Decompose the cost variance by category

Operating costs split into three useful buckets: people costs, vendor and software costs, and program and discretionary costs. For each bucket, identify the largest variances and write a two-line commentary.

People costs: were hires earlier or later than planned? Was severance involved? Did benefits or payroll-tax assumptions change? People costs are sticky, so an unfavorable variance here tends to persist; flag this.

Vendor and software costs: was a tool added or removed? Did a contract renegotiation land? Did usage exceed the contractual minimum? Were any payments accelerated into the period?

Program and discretionary spend: was a planned campaign deferred? Did a launch cost more than budgeted? Were one-time setup costs absorbed?

For each commentary line, distinguish between a true variance (the spend itself was different) and a timing variance (the spend was budgeted in a different month than it landed). Timing variances reverse in subsequent months; true variances do not.

### Step 5 — Separate one-time items from trends

This is the most important analytical step in the narrative. A favorable revenue variance driven by a customer who pre-paid an annual contract in this month is a one-time item; a favorable revenue variance driven by an improvement in new-logo conversion is a trend. Treating these the same way confuses the reader.

For each material variance, classify it as one of three types:

- **One-time event** — happened in this period and will not recur. Example: a tax refund, a settlement, a one-time deal acceleration.
- **Timing shift** — the budgeted item simply landed in a different period than expected. Example: a vendor invoice that was budgeted for March and landed in April.
- **Emerging trend** — early evidence of a sustained shift in the business. Example: a new-logo close rate that has improved for three consecutive months, a customer-support cost that is scaling faster than headcount.

The narrative should mark each commentary item with its type. Pre-disclosed one-timers from the user input should be tagged accordingly. Items the skill is uncertain about should be marked "trend or one-time — needs one more month of data to call."

### Step 6 — Connect variances to operating context

The numbers are not self-explanatory. The narrative should link each material variance to the operating context the user provided. "The favorable hosting cost variance reflects the data-warehouse migration completing two weeks early, removing the dual-running cost the budget assumed for the full month." Without the operating context, the narrative reads like a number-restating exercise.

If the user did not provide operating context for a material variance, the narrative says so explicitly: "Marketing spend was $80K below budget. Reason not yet confirmed with the marketing team; investigating." This is more honest and more useful than inventing a reason.

### Step 7 — Identify leading indicators for next period

The most valuable section of a variance narrative is the one that points forward. After narrating the current period, identify the metrics that will tell you, before the next monthly close, whether the trends you flagged are real.

Examples:

- If a favorable conversion-rate variance is showing up this month, the leading indicator is the conversion rate in the first ten business days of next month.
- If a hiring delay drove a favorable cost variance, the leading indicator is signed offers as of mid-month next month.
- If a churn spike showed up this month, the leading indicator is the customer-success risk-flag report for the at-risk cohorts.

Three to five leading indicators is the right number. Each one should be observable inside the next two-to-three weeks, with a name and an owner.

### Step 8 — Surface the asks

A variance narrative that asks for nothing is a narrative that has accepted everything. The narrative should end with a short list of asks — specific questions the operating leaders need to answer to make the next month's review more useful.

Examples of good asks:

- "Marketing leader: confirm whether the $80K underspend is permanent (program canceled) or timing (program shifted to next month)."
- "Sales leader: confirm whether the over-plan in inbound is being absorbed by reps without dropping outbound activity, or whether we need to hire ahead of schedule."
- "Customer success leader: explain the $40K of one-time professional services revenue — was it a deal we want to repeat, or a special accommodation?"

Each ask has a named owner and a date. Asks without owners get ignored.

### Step 9 — Tune for audience

The same numbers produce different narratives for different readers.

For the **CEO**, the narrative is short, decision-oriented, and forward-looking. The CEO wants to know: what is working, what is breaking, what decision do I need to make. Cut the line-item detail; foreground the asks and the leading indicators.

For the **leadership team**, the narrative is the operating document. It covers more line-item detail because each functional leader will read for their function. The asks section is where action gets assigned.

For the **board**, the narrative is more polished and more strategic. Foreground the headline against plan, the cash position, the trends rather than the one-timers, and the implications for the year-end view. Hide most of the line-item detail in an appendix.

For a **department head**, the narrative is deeply detailed for their lines and brief on the rest. Lead with their variances; provide enough context on company variances that they can connect their work to the whole.

### Step 10 — Format for under-five-minute reading

Constraints on the final artifact:

- One page for the executive narrative — roughly 350–500 words, hierarchical headers, no walls of prose.
- A compact table of the largest variances follows, with two-line commentary per row.
- The leading indicators and asks sections are at the bottom of the one-page, because that is where the reader's attention should land.
- Detail tables and appendices follow, separated, for the reader who needs to go deeper.

### Step 11 — Use favorable and unfavorable carefully

"Favorable" and "unfavorable" are accounting language for "good for the P&L" and "bad for the P&L" — they do not always correspond to good and bad operationally. A favorable cost variance from a deferred hire is unfavorable if the hire was critical to the next-quarter revenue. Avoid pure accounting framing on items where the operational interpretation is the opposite.

When the operational and accounting interpretations diverge, the narrative should note the divergence. "The hiring variance is favorable for the period ($90K underspent) but unfavorable for the trajectory — three of the four deferred hires were on the engineering team, slipping the November release by roughly four weeks."

### Step 12 — Maintain continuity with prior periods

If the user provided last month's drivers, track them. "Last month we flagged the inbound demand acceleration as a trend to confirm. This month it persisted, so we are reclassifying it from emerging trend to working assumption and adjusting the forward forecast." This continuity is what distinguishes a narrative practice from a one-off explanation.

If a previously-flagged trend reverses or disappears, say so. "Last month's expansion-bookings strength did not repeat in this period. Two of the three customers that drove last month's spike have not added seats this month; investigating with customer success."

### Step 13 — End with the cash and runway view

Even when the operating P&L looks good, cash is the truth. Close the narrative with a short cash section: ending cash balance, change in cash for the period (operating cash flow plus or minus investing and financing items), trailing-three-month average burn, runway in months against the latest forecast.

If runway moved materially — a month or more in either direction — open with that fact rather than burying it.

### Step 14 — Refuse to spin

The narrative is read most carefully when it is most honest. If the period was bad, say so plainly. "Revenue came in 12% below plan, the largest miss of the fiscal year. Three of the four shortfalls were in the enterprise segment and reflect a pattern we have been watching for three months." Spinning a bad period makes the next bad period harder to surface, because trust in the narrative degrades.

## Inputs

- **bva_data** (required) — the BvA file with budget, actual, and variance columns by line item.
- **business_context** (required) — operating context for the period.
- **prior_period_drivers** (optional) — last month's named drivers, for continuity.
- **audience** (optional) — CEO, leadership team, board, or department head.
- **known_one_timers** (optional) — items the user has already classified as one-time.

## Outputs

- A one-page executive narrative with headline, drivers, one-timers, leading indicators, and asks.
- A compact table of the largest variances with two-line commentary.
- A short list of leading indicators with owners.
- A list of asks for operating leaders with owners and dates.

## Examples

### Worked example — Producing the April variance narrative for a Series B SaaS company

**Inputs given to the skill:**

- bva_data: an April BvA showing revenue $4.18M against budget $4.00M (+$180K), opex $3.60M against $3.45M (-$150K), operating income $580K against $550K (+$30K), ending cash $14.2M.
- business_context: "Product launch landed mid-month; one new sales rep joined late; expansion campaign with twenty existing accounts ran for two weeks; data-warehouse migration completed three days early; one large customer pre-paid a six-month renewal."
- prior_period_drivers: "March narrative flagged improving inbound conversion and a build-up in support ticket volume."
- audience: "leadership team."
- known_one_timers: "Customer pre-payment of $90K for the six-month renewal is a timing shift; budgeted across the next two months."

**Output produced by the skill (the one-page narrative, abridged):**

> **April variance narrative — leadership team review**
>
> **Headline:** Revenue $4.18M vs $4.00M plan, $180K favorable. Opex $3.60M vs $3.45M, $150K unfavorable. Operating income $580K vs $550K, $30K favorable. Ending cash $14.2M, runway 17 months against current burn.
>
> **Revenue drivers:**
> - Volume favorable by $120K [trend]. Inbound new-logo bookings ran 11% over plan; the conversion-rate improvement flagged in March persisted. Reclassifying from emerging trend to working assumption.
> - Mix favorable by $60K [trend]. The launch drove a higher proportion of mid-tier rather than entry-tier sign-ups; mid-tier ARPU runs about 35% higher.
> - One offset: a $30K customer cancellation in the enterprise segment, the third such cancellation in two months. Watching closely.
>
> **Cost drivers:**
> - People costs $80K unfavorable [trend]. Two hires landed earlier than budgeted, and the late-joining sales rep onboarded faster than the ramp curve assumed; both effects persist.
> - Marketing programs $50K unfavorable [one-time]. The launch carried $50K of one-time event and PR costs that were budgeted for May; timing shift.
> - Hosting $35K favorable [trend]. Data-warehouse migration removed dual-running cost three days early.
>
> **One-timers flagged separately:** The $90K customer pre-payment is classified per CFO note as a timing shift; reflected in next two months' deferred revenue.
>
> **Leading indicators to watch in May:**
> - Inbound conversion rate in the first ten business days of May — confirms the trend.
> - At-risk enterprise pipeline coverage from customer success — confirms or refutes the third cancellation as the start of a pattern.
> - Marketing-program spend in May — confirms the April overage was timing, not a real run-rate increase.
>
> **Asks:**
> - VP Sales: confirm whether enterprise cancellations are connected (same root cause) or coincidental. Needed by May 15.
> - VP Marketing: confirm the May program plan absorbs the timing shift cleanly. Needed by May 10.
> - VP Customer Success: top-five list of at-risk enterprise accounts with current intervention plan. Needed by May 12.

## Limitations

This skill is only as good as the BvA file it receives. If the BvA has classification errors, dollar-routing errors, or missing accruals, the narrative inherits them. The skill flags suspicious-looking variances (an account with zero budget and material actuals, a department with no variance commentary feasible from the input) but cannot fix the underlying data.

The skill produces commentary, not investigation. A material variance flagged as "investigating" means the operating leader needs to do the investigation; the narrative is a prompt for that work, not a substitute.

The skill operates over one period at a time by design. Multi-period trend analysis (six-month rolling, full-year tracking, prior-year comparison) is a different exercise and benefits from a different artifact. The narrative can refer to prior-period flags if the user provides them but does not perform a multi-period roll-up.

Accounting nuance is simplified. Distinctions between accrual and cash, between revenue recognition timing and bookings timing, between capitalized and expensed costs, are real and material; the narrative simplifies them for the reader. For close-period audit work, a properly trained accountant is the right tool, not this skill.

The skill assumes the user wants a written narrative document. For some audiences a brief verbal walkthrough plus a dashboard is more effective than written prose; this skill does not replace the dashboard.

## Sources reviewed

- https://github.com/JerBouma/FinanceToolkit
- https://github.com/jdvelasq/cashflows
- https://github.com/gopalakrishnanarjun/modelmyfinance
- https://github.com/pmorissette/ffn
- https://github.com/pgoswami3/Financial-Analysis
- https://github.com/misken/whatif
