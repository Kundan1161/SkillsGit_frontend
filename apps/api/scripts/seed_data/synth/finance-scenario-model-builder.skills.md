---
id: skillsgit-curated/scenario-model-builder
version: 1.0.0
name: Scenario Model Builder
description: Produce a three-case financial model — base, upside, downside — with explicit assumption deltas, observable trigger criteria, and the operating actions that follow when a trigger fires.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: finance
tags: [niche:fp-and-a, scenario-planning, financial-modeling, sensitivity-analysis, downside-planning, contingency-planning, forecasting]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: [code_execution]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - scenario model
  - scenario planning
  - base upside downside
  - sensitivity analysis
  - downside case
  - upside case
  - contingency model
  - financial scenarios
  - what-if analysis
  - case planning
  - reforecast
  - trigger criteria
example_invocations:
  - "Build base, upside, and downside scenarios from this annual plan with trigger criteria for each."
  - "Help me model what happens if our largest customer renewed at half — what cuts would the plan require?"
  - "Create a three-case scenario model with the contingency actions if we slip into the downside."
inputs:
  - name: base_plan
    type: file
    required: true
    description: The base-case plan — at minimum month-by-month revenue, opex, and cash. A full annual operating plan is ideal.
  - name: drivers_to_flex
    type: text
    required: true
    description: The drivers the scenarios should flex — for example, new-bookings growth rate, churn rate, hiring pace, gross margin, pricing.
  - name: business_context
    type: text
    required: true
    description: Why scenarios are being built now — fundraising prep, board reset, downturn-preparedness, acquisition due diligence.
  - name: downside_appetite
    type: choice
    required: false
    description: How aggressive the downside case should be. Stress test (severe), realistic miss (moderate), or thin downside (conservative trim).
    choices: [stress, moderate, conservative]
  - name: known_constraints
    type: text
    required: false
    description: Constraints that limit operational levers — multi-year leases, contractual minimums, jurisdictional severance costs, founder commitments.
outputs:
  - name: scenario_model
    type: markdown
    description: A three-case model with side-by-side revenue, cost, cash, and runway lines and a one-page summary.
  - name: assumption_deltas
    type: markdown
    description: A line-by-line list of which assumptions changed between base, upside, and downside, with rationale.
  - name: trigger_criteria
    type: markdown
    description: The observable metrics that, if missed by stated amounts in stated windows, indicate the company has slipped into upside or downside.
  - name: contingency_actions
    type: markdown
    description: For each scenario, the operating actions the leadership team has pre-decided to take if the scenario materializes.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when an FP&A lead or CFO needs to stand up a three-case scenario model around an existing base plan — usually because the company is preparing for a board, facing a fundraising decision, hedging against a known risk, or testing the resilience of the plan before committing to a hiring or investment ramp. The skill is most useful when there is already a credible base case; layering scenarios on a fragile base produces theatre, not insight.

Use this skill when the user can name the drivers worth flexing, can articulate the business reason scenarios are being built, and is willing to commit to contingency actions if a scenario materializes. The actions are the most valuable output; a scenario model with no pre-decided actions becomes a paperweight at the moment the company actually needs it.

Do not use this skill to produce decorative scenarios designed to make a base case look better by surrounding it with strawman alternatives. Do not use it for tail-risk analysis that requires statistical sophistication (Monte Carlo with correlated drivers, value-at-risk on financial instruments) — the skill is built for operating scenarios with named drivers, not stochastic financial-risk modeling. Do not use it to replace the human conversation about what the company would actually do under stress; the skill structures the conversation, it does not substitute for it.

## How to apply

A three-case scenario model is useful when it does three things. First, it forces the team to specify what would have to be different about the world to produce a different outcome, in observable terms. Second, it pre-commits the team to operating actions tied to each scenario, so the response is fast when the trigger fires. Third, it shows the cash and runway consequence of each scenario plainly enough that the leader knows which scenario is the one to plan against, not just hope through.

The skill follows a sequence: anchor on the base case, define the cases by assumption deltas, recompute the model, identify trigger criteria, name contingency actions, and lay out the document. The trap to avoid is collapsing this into a single sensitivity table; sensitivities tell the reader how the model moves, scenarios tell the reader how the business moves.

### Step 1 — Anchor on the base case

The first task is to make the base case explicit and challengeable. Read the supplied plan. Confirm the revenue model, the cost drivers, the hiring plan, and the cash trajectory. State the base case in three lines: "Base case ends the year at $X revenue, $Y operating loss, $Z ending cash, W months of runway. The base case assumes [the three or four key drivers]."

If the base case is incomplete or internally inconsistent, name the gaps before building scenarios. A scenario layered on a broken base inherits the breakage.

### Step 2 — Identify the drivers worth flexing

Most plans have dozens of drivers. Scenarios should flex the ones that matter — the drivers where a plausible change moves the outcome materially. Start from the user's list of `drivers_to_flex` and validate against a quick sensitivity pass: for each candidate driver, ask what a 10% change does to revenue, operating income, and ending cash.

The drivers usually worth flexing for a SaaS business:

- New-bookings growth rate or new-logo acquisition volume.
- Net retention rate (a combination of churn and expansion).
- Sales productivity, especially for new hires.
- Hiring pace, especially in the largest functions.
- Gross margin, especially as a function of mix.
- Average selling price or list-price change.

The drivers usually not worth flexing as a primary lever: G&A line items, small vendor costs, one-time program spend. Flex them as second-order effects of the primary drivers, not as scenario inputs in their own right.

### Step 3 — Define the upside case

Build the upside case as a coherent story, not a uniform multiplier. A plausible upside has a few drivers above plan and most others near plan; uniform-upside cases are not realistic and are not useful for planning. The driver moves should be coherent — a higher new-bookings rate often comes with a slightly worse churn rate (you sold more, including to weaker fits), or with a higher CAC (you spent more to acquire faster).

Typical upside drivers:

- New-bookings growth 15–25% above base.
- Net retention 200–400 basis points higher.
- One specific initiative — a launch, a campaign, a partnership — landing materially better than plan.

The upside case should also surface what it costs to capture the upside. If sales productivity is above plan, that does not buy itself — it usually requires pre-investment in sales capacity, customer success, or product. Build the cost side honestly, so the upside case shows ending cash that may be lower than the base case in the early months of the year before the revenue catches up.

### Step 4 — Define the downside case

The downside case is the most important of the three to build well. Most plans are not stress-tested adequately; downside cases that are merely 10% below base teach the team nothing.

Calibrate the downside to the `downside_appetite` input:

- **Stress** — what would happen if the worst plausible scenario unfolded. Bookings 30–40% below plan, retention degrading meaningfully, no upside levers available. This is a "could we survive" test.
- **Moderate** — a realistic miss. Bookings 15–25% below plan, retention slipping somewhat, some compensating cost actions available. This is a "what do we do if we are off plan" test.
- **Conservative** — a thin downside. Bookings 8–12% below plan, retention stable, modest cost adjustments. This is a "what is the worst quarter we could absorb without changing the year" test.

The downside should be coherent in the same way the upside is. A bookings miss is often correlated with retention pressure (the deals you would have closed are with customers who would have stayed) and with higher discount pressure (the deals you do close are at lower prices). Build the correlations explicitly.

### Step 5 — Recompute the cost side honestly

Costs do not scale linearly with revenue, especially on the downside. Some costs are sticky:

- Signed leases, multi-year vendor contracts, contractual minimums. These cannot be cut without negotiation or breakage costs.
- Already-hired headcount. Severance costs apply on the way down; the cash impact lags the P&L impact.
- Already-committed program spend. Marketing budgets locked in advance, event sponsorships, multi-month media buys.

Some costs are dial-able:

- Open-but-unfilled headcount slots. The fastest cost lever; pause hiring and the cost line moves immediately.
- Discretionary program spend not yet committed. Marketing campaigns, consulting projects, conferences.
- Variable people compensation. Commissions and bonuses move with performance.

Build the downside case's cost line using the dial-able costs first, then the harder-to-cut costs only if the dial-able ones are insufficient. The honest downside often shows that the company can move six to twelve weeks before cash becomes critical, and that the moves available in the first six to twelve weeks are the small ones; the larger moves (headcount, lease renegotiation) take longer to execute.

### Step 6 — Recompute the cash and runway view

For each case, recompute the month-by-month cash trajectory. The cash trajectory is what matters most to the board and the leadership team; ending cash and minimum-cash-month tell the operational story.

For the downside case, identify the month in which cash dips lowest. That month is the action-forcing month — the cuts you would take in that case have to be decided before that month, and ideally before the second half of the year preceding it.

For the upside case, identify the month in which cash dips lowest before the revenue catches up. The upside is often a cash story before it is a revenue story; the team needs to know whether they can fund the upside without an additional financing event.

State runway in months against the closing month's burn rate. Note that runway computed against a trailing average is more reassuring than runway computed against the next month's expected burn; choose the more conservative view for the board.

### Step 7 — Identify trigger criteria

For each scenario, name the observable metrics that, if breached, indicate the company has slipped into that scenario. Triggers must be observable inside the fiscal year — preferably inside the first quarter — or they do not produce useful action.

Properties of a good trigger:

- Observable in a stated window (e.g., "first 90 days").
- Quantified (e.g., "new ARR booked is more than 18% below plan").
- Tied to a single owner who watches the metric (e.g., "VP Sales reviews weekly").
- Tied to a contingency action (see Step 8) that fires automatically.

Triggers that are too vague ("if bookings are soft") do not produce action. Triggers that are too tight ("if any quarter misses plan by 5%") fire constantly and lose meaning. The right calibration is wide enough to catch real shifts and narrow enough to be unambiguous.

Three to five triggers per scenario is the right number. Most should be revenue-side; one should be cost-side (a hiring overrun or a vendor renegotiation breakdown can also trip a downside scenario), and one should be cash-side (a financing milestone slipping).

### Step 8 — Pre-decide contingency actions

The contingency-action list is the most valuable artifact of the scenario model. For each scenario, write the actions the leadership team has pre-decided to take if the trigger fires.

For the downside case, contingency actions usually escalate over three stages:

- **Stage 1 (mild downside, first trigger)** — defer or freeze. Pause open hiring, defer non-committed marketing programs, slow discretionary spend. Reversible inside the year.
- **Stage 2 (deeper downside, second trigger)** — cut and renegotiate. Cancel committed programs where exit clauses allow, renegotiate vendor contracts, slow product investment in lower-priority initiatives. Some actions are not reversible inside the year.
- **Stage 3 (severe downside, third trigger)** — restructure. Headcount actions, lease renegotiation or sublet, strategic refocus. These take months to execute and have lasting consequences.

For each action: who decides, who executes, how long it takes to land in the cash line, and what its cumulative effect is on the year's burn.

For the upside case, the contingency actions are usually about deploying the upside, not absorbing it. Pre-decide which investments are funded with upside cash — accelerated hiring in the rate-limited functions, accelerated product launches, increased marketing programs, debt paydown, or kept on the balance sheet for runway extension.

### Step 9 — Make the trade-offs visible

Each contingency action has a trade-off. The pause on hiring buys cash but pushes out product capacity. The vendor renegotiation buys cash but consumes leadership attention. The headcount cut buys cash but degrades morale and execution.

For each contingency action, name the trade-off in one line. The trade-offs are how the leadership team has the actual conversation about whether to fire the trigger; teams without the trade-offs documented tend to either fire too quickly (and over-cut) or too slowly (and over-spend).

### Step 10 — Reconcile the scenarios against the constraints

If the user provided `known_constraints`, validate the contingency actions against them. A contingency action that violates a signed contract (canceling a multi-year lease, terminating a vendor under a no-termination clause) is not actually available; replace it with what is. A contingency action that violates a founder commitment (no layoffs in year one, no salary cuts to the leadership team) is similarly off the menu and should be replaced.

If a downside case becomes uncomfortable because the dial-able costs are too small relative to the downside revenue, that is a meaningful finding — surface it. The user needs to know that the downside case requires moves they have committed to not making.

### Step 11 — Layout the document

The scenario document has four pieces:

- A **one-page side-by-side summary**. Three columns (base, upside, downside) and seven or eight rows (revenue, growth rate, gross margin, opex, operating income, ending cash, minimum cash month, runway). The reader should be able to read the cases in 30 seconds.
- An **assumption deltas table**. Each row is a driver. Each column is a case. The values are the assumption under each case, with the rationale in one line.
- A **trigger and action table**. Rows are triggers, with the metric, the threshold, the window, the owner, and the linked action.
- The **detailed monthly model**, in an appendix. Tables of revenue, cost, and cash by month for each case.

Total length should be twelve to fifteen pages for a serious model; ten pages or less indicates the model has skipped detail.

### Step 12 — Recommend a cadence for review

A scenario model that is built once and shelved is a wasted artifact. Recommend a review cadence: monthly review of which scenario the company is tracking against (with the triggers as the framework), quarterly refresh of the assumption deltas, and a full rebuild when the base case changes materially.

Note specifically when the model becomes stale: a base case more than 90 days old without a reforecast usually needs the scenarios rebuilt around the new base before they can be trusted.

### Step 13 — Refuse to model wishful upside

Watch for upside cases that are not coherent — a higher revenue number with the same cost base, a faster bookings ramp with no investment, a higher retention with no customer-success spend. Real upside has costs. If the user's upside case is uncoherent, push back and adjust.

Similarly, watch for downside cases that are too easy to absorb. A downside case where the team simply pauses some marketing and is fine is rarely the real downside case. The honest downside requires a cut the team would prefer not to make; if no such cut is in the model, the downside has not been stressed.

### Step 14 — Cap the precision

Scenario outputs have spurious precision. A model that reports ending cash to the nearest dollar implies a level of confidence that is unwarranted. Round outputs to the nearest $10K (or $100K for larger companies); state ranges where ranges are appropriate. "Ending cash $9.1M, runway 14 months" is more honest than "Ending cash $9,127,432, runway 14.3 months."

## Inputs

- **base_plan** (required) — the base case the scenarios sit on top of.
- **drivers_to_flex** (required) — the drivers worth flexing.
- **business_context** (required) — why the scenarios are being built.
- **downside_appetite** (optional) — stress, moderate, or conservative.
- **known_constraints** (optional) — constraints that limit contingency actions.

## Outputs

- A three-case model with side-by-side summary and a detailed monthly view in the appendix.
- A line-by-line assumption-delta table.
- A trigger-criteria table with thresholds, windows, and owners.
- A contingency-action list for each case, with trade-offs and execution time.

## Examples

### Worked example — Building three cases for a Series B SaaS company before a board

**Inputs given to the skill:**

- base_plan: an annual operating plan showing $24M ending ARR, $14M ending cash, 14 months runway.
- drivers_to_flex: "new-bookings growth, net retention, hiring pace, gross margin."
- business_context: "Board meeting in six weeks. Board has signaled concern about macro softness and wants to see downside-preparedness."
- downside_appetite: "moderate."
- known_constraints: "Lease through August next year. Founder has committed to no layoffs in calendar year one of post-Series B."

**Output produced by the skill (the one-page summary, abridged):**

> **Three-case scenario summary**
>
> | Metric | Base | Upside | Downside |
> |---|---|---|---|
> | Closing ARR | $24.0M | $25.7M | $20.6M |
> | Revenue growth | 60% | 71% | 37% |
> | Gross margin | 72% | 73% | 70% |
> | Opex | $16.8M | $17.4M | $16.0M |
> | Operating loss | ($3.6M) | ($2.8M) | ($5.4M) |
> | Ending cash | $14.0M | $14.7M | $9.5M |
> | Minimum cash month | Nov | Nov | Feb (year+1) |
> | Runway at year-end | 14 months | 17 months | 8 months |
>
> **Key assumption deltas (abridged):**
> - New bookings: Base $14M, Upside $17M, Downside $10.5M.
> - Net retention: Base 108%, Upside 112%, Downside 102%.
> - Hiring pace: Base on plan, Upside +4 hires Q3, Downside hiring freeze Q2.
> - Gross margin: Base 72%, Upside 73% (mix benefit), Downside 70% (discount pressure).
>
> **Trigger criteria (abridged):**
> - Downside trigger: New ARR booked in first half is more than 18% below plan AND pipeline coverage for second half is below 3x. Owner: VP Sales, weekly review.
> - Upside trigger: New ARR booked in first half is more than 12% above plan AND pipeline coverage for second half is above 4.5x. Owner: VP Sales, weekly review.
>
> **Contingency actions for downside (abridged):**
> - Stage 1 (trigger fires): Freeze hiring on the 7 open roles. Defer the September product launch by one quarter. Cancel the Q3 event sponsorship ($120K, exit clause allows full refund through July). Expected effect: $2.1M of cash preserved.
> - Stage 2 (trigger persists into second half): Renegotiate the largest cloud contract (under MFN clause, renegotiation typically lands within 60 days, expected 12–15% savings). Pause the second cohort of CS hires. Expected effect: additional $1.4M of cash preserved.
> - Stage 3 (cash falls below 6-month forward floor): Not available within calendar year given the founder commitment; trigger pre-financing conversation 90 days before reaching this threshold.
>
> **Trade-offs called out:** The downside case is constrained by the founder commitment against layoffs. If the downside materializes, the available levers preserve cash but not enough to reach a 12-month forward runway by year-end. Pre-financing the next round becomes the gating action and should be initiated when Stage 1 fires, not waited on until Stage 3.

## Limitations

This skill produces operating scenarios for managerial decision-making. It does not perform stochastic risk modeling, value-at-risk analysis, or any form of probability-weighted expected-value computation. Cases are deterministic with named assumptions; they do not carry probabilities.

The skill is most useful when the base case is solid and the business has stable drivers. For companies in pre-product-market-fit phase, in major strategic transitions, or in markets undergoing structural change, the scenario approach still applies but the assumption widths grow and the contingency actions become harder to specify.

Contingency actions are pre-decisions, not commitments. The leadership team has to actually take the actions when the trigger fires; teams that have built the model but not built the muscle to execute it tend to wait too long, and the cash impact compounds. The skill produces the document; the team produces the discipline.

The skill cannot model events that are not in the input. Black-swan events (a major outage, a regulatory change, a co-founder departure, a key-customer concentration risk realized) often produce scenarios more severe than the moderate downside. If the user wants a black-swan scenario, name it explicitly and feed it as a `drivers_to_flex` input; the skill will build the case but cannot generate the black swan on its own.

Numerical outputs carry the precision of the input data; reporting outputs to false precision is a misleading practice. The skill rounds to reasonable units and notes when ranges would be more honest than point estimates.

## Sources reviewed

- https://github.com/misken/whatif
- https://github.com/jason-ash/pyesg
- https://github.com/JerBouma/FinanceToolkit
- https://github.com/jdvelasq/cashflows
- https://github.com/gopalakrishnanarjun/modelmyfinance
- https://github.com/pmorissette/ffn
