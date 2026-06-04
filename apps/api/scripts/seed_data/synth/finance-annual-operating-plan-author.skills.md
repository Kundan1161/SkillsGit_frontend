---
id: skillsgit-curated/annual-operating-plan-author
version: 1.0.0
name: Annual Operating Plan Author
description: Build a reconciled annual operating plan from top-down ambition and bottom-up driver math — revenue model, cost lines, hiring plan, capex, ratios, and three scenarios — with the assumptions named and challengeable.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: finance
tags: [niche:fp-and-a, annual-operating-plan, budgeting, forecasting, headcount-planning, scenario-planning, startup-finance]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: [code_execution]
  tools_optional: [file_io]
  min_context_tokens: 64000
  estimated_tokens_per_invocation: 12000
trigger_keywords:
  - annual operating plan
  - AOP
  - annual budget
  - operating plan
  - financial plan
  - top-down bottom-up
  - hiring plan
  - revenue plan
  - cost plan
  - opex plan
  - capex plan
  - scenario plan
  - budget vs actual baseline
example_invocations:
  - "Help me build the annual operating plan for our 80-person SaaS company for next fiscal year."
  - "Draft a top-down vs bottom-up reconciled plan from this revenue target and current headcount file."
  - "Build an AOP with base, upside, and downside cases and a hiring plan tied to the revenue cases."
inputs:
  - name: company_profile
    type: text
    required: true
    description: Stage, business model, current ARR or revenue run-rate, current headcount, fiscal year start.
  - name: top_down_target
    type: text
    required: true
    description: The revenue, growth, or profitability target the founders or board have set for the year, in plain words. Include any non-negotiables.
  - name: historicals
    type: file
    required: false
    description: A file or pasted table of trailing 12 months of revenue, gross margin, opex by category, and headcount. Strongly recommended; the plan is weak without it.
  - name: current_headcount
    type: text
    required: false
    description: Current headcount by department or function, with fully-loaded cost assumption if known.
  - name: known_commitments
    type: text
    required: false
    description: Known fixed commitments for the plan year — multi-year contracts, signed real-estate leases, committed equipment purchases, planned launches.
  - name: cash_constraint
    type: text
    required: false
    description: Starting cash balance, any committed debt facility, and the runway target the plan must satisfy.
outputs:
  - name: annual_operating_plan
    type: markdown
    description: A structured AOP document covering revenue model, cost lines, headcount plan, capex plan, summary ratios, and three scenarios.
  - name: assumptions_register
    type: markdown
    description: A line-by-line list of every assumption the plan rests on, with owner and confidence rating.
  - name: scenario_summary
    type: markdown
    description: A side-by-side comparison of base, upside, and downside cases with the deltas explained.
  - name: open_questions
    type: markdown
    description: The questions the plan cannot answer without more input from the CEO, sales leader, or board.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when an FP&A lead, finance partner, or founder-operator needs to construct an annual operating plan (AOP) — the twelve-month financial blueprint that translates strategic ambition into a budget, a hiring plan, and a set of measurable commitments. The skill is most useful in the four-to-six week window leading up to a fiscal-year start, when leadership has agreed on direction but the numbers still need to be built.

Use this skill when the user can articulate a top-down target (a revenue number, a growth rate, a margin floor, or some combination), share at least an outline of current trading, and is willing to spend time validating assumptions. The skill is structured around reconciliation — top-down vs bottom-up — and the reconciliation only works when the user engages with both sides. If the user wants a single tidy number with no engagement, redirect them to a simpler exercise; AOPs cannot be ghost-written.

Do not use this skill to publish numbers without human sign-off. The output is a draft for negotiation and challenge, not a board commitment. Do not use it to model individual deals or accounts (deal-level forecasting is a different problem with different inputs). Do not use it as a substitute for a properly audited financial statement; this skill produces planning artifacts, not GAAP or IFRS deliverables.

## How to apply

An annual operating plan is a reconciliation device. Two views of the future need to meet. The first is top-down: what leadership wants the year to look like — a revenue target, a margin floor, a runway commitment, a market-share goal. The second is bottom-up: what the operating units can actually deliver if you build their numbers from headcount, pipeline, sales capacity, marketing spend efficiency, and known commitments. A real AOP is the negotiation between these two views, made transparent through driver math.

A useful plan has six pieces: a revenue model, a cost plan, a headcount plan, a capex plan, a set of summary ratios, and three scenarios. Each piece is built from the same underlying drivers, so when an assumption changes the consequences are visible everywhere. The methodology below produces all six in sequence and forces an explicit reconciliation step before declaring the plan complete.

### Step 1 — Stake the top-down target

Begin by writing down the top-down target in the user's own words. Make it specific. "Grow to $30M ARR with 60% gross margin and 18 months runway by fiscal year end" is a usable target. "Grow aggressively while being disciplined" is not — push back and refine. A target that is not specific enough to disagree with is not specific enough to plan from.

Note the implied trade-offs in the target. A revenue target without a margin floor is permission to spend; a margin floor without a runway floor is permission to grow slowly. Surface these trade-offs early so the leader can adjust before the team builds against an over-constrained or under-constrained brief.

### Step 2 — Build the bottom-up revenue model

Pick the revenue model that matches the business. For a subscription business, the model is opening ARR plus new ARR minus churned ARR plus expansion ARR equals closing ARR. For a transactional business, the model is users times average order value times order frequency. For a services business, the model is billable headcount times utilization times bill rate. Whichever model you pick, name every driver and tag every driver as either historically-measured, externally-benchmarked, or assumed.

Build the model month by month for the plan year. Avoid the temptation to draw an annual total and divide by twelve — seasonal businesses lie in monthly detail. For each month, project new bookings, churn, expansion, and net new revenue. Then aggregate to an annual total and compare to the top-down number. The first comparison will almost never match. That gap is the reconciliation work.

### Step 3 — Build the headcount plan tied to the revenue model

Headcount is the largest cost line for most software and services businesses, and it is the cost line most tightly coupled to the revenue model. Build headcount by function — go-to-market, product and engineering, general and administrative — and tie each function's growth to a driver. Sales headcount grows with required pipeline coverage, which grows with the new-bookings target. Engineering headcount grows with the product investment thesis. G&A grows roughly with company size with step-functions at certain thresholds.

For each role, specify a hire month, a fully-loaded cost (salary, benefits, taxes, software, equipment, and a real-estate or remote allocation), a ramp curve for revenue-producing roles (a sales rep at $0 in month one ramps to full quota by month nine or so), and any backfill assumptions. Producing a clean monthly headcount roster is what separates a plan from a wish.

### Step 4 — Build the cost plan from drivers

Group costs into three buckets: cost of revenue, operating expenses, and capital expenditures. Within each bucket, separate driver-based costs from fixed commitments from discretionary spend.

Driver-based costs are the ones tied to a measurable rate: hosting costs that scale with revenue, payment processing as a percentage of GMV, support costs per active customer. Build these as a unit-cost times a quantity from the revenue model.

Fixed commitments are the costs the company has already promised: signed leases, multi-year software contracts, contractual minimums. Build these from the contracts themselves, not from a benchmark.

Discretionary spend is the budget the leader can dial up or down — marketing programs, conferences, consulting projects, one-time launches. Build these as targets the team has agreed to, with named owners.

The headcount plan from Step 3 lands here as the largest line in operating expenses. Make sure the numbers reconcile — the cost plan's payroll line should match the headcount plan's monthly cost total to the dollar.

### Step 5 — Build the capex plan

For most software businesses, capex is light — laptops, leasehold improvements, capitalized internal software development if that is the accounting policy. For asset-heavy businesses, capex is one of the more important lines and has multi-year cash consequences. Build capex by category, with an in-service date and a depreciation schedule. Treat capex differently from opex in the cash view — the cash hit happens in the spend month, the P&L hit spreads across the useful life.

### Step 6 — Compute the summary ratios

A plan without ratios is harder to read than a plan with ratios. Compute, monthly and annually, at least: gross margin, contribution margin by major product line, operating expense as a percentage of revenue, operating margin, cash burn or operating cash flow, runway in months, and any business-specific ratios (CAC payback for subscription, gross merchandise value-to-cost ratio for marketplaces, billable utilization for services).

The ratios are how the board reads the plan. If a ratio looks structurally wrong — gross margin compressing while the business should be scaling, operating expense expanding faster than revenue with no investment thesis to justify it — the underlying numbers need a second look.

### Step 7 — Reconcile top-down to bottom-up

This is the central step. The bottom-up revenue number from Step 2 rarely matches the top-down target from Step 1 on the first pass. The gap is informative. Quantify it precisely — bottom-up says $24M, top-down says $30M, gap is $6M or 25%.

Then propose specific paths to close the gap, each tied to a driver: a higher new-logo target requires X more sales hires hired Y months earlier, expansion at a higher net-retention rate requires investment in customer success, a price increase contributes to gap-closing if the demand assumption holds. Each path has costs and risks; surface them. The leader and team then choose which paths are realistic.

The output of this step is a single reconciled plan, not two plans — but the reconciliation moves should be visible so the choices made are auditable later.

### Step 8 — Build three scenarios

A single number is a wish. Three scenarios is a plan. Build base, upside, and downside cases with explicit assumption deltas — not just "revenue is 20% higher in upside" but specifically "in upside, new-logo bookings ramp 15% above plan, expansion runs 110% of base, and churn stays at the historical floor."

For each scenario, recompute the cost plan. Upside cases are often weaker than they look because the cost plan rarely scales linearly — onboarding a faster growth rate may require pre-investment in capacity and a temporarily worse efficiency ratio. Downside cases should be honest about which costs are sticky (signed leases, severance to unwind headcount) versus dial-able.

For each scenario, compute ending cash and runway. The downside case is the one the board cares most about — it tells them the failure mode of the plan. The upside case is the one the team rallies around. The base case is what gets reported against.

### Step 9 — Name the trigger criteria for each scenario

A scenario is only useful if the operator knows when they are in it. Define trigger criteria — observable metrics that, if missed or exceeded by a stated amount in a stated number of months, indicate that the company has slipped into a different scenario. "If new ARR booked in the first quarter is more than 20% below plan, we are in the downside case and we trigger the contingency hiring freeze." Be concrete; vague triggers do not produce action.

### Step 10 — Build the assumptions register

Every plan rests on assumptions. Make them visible. For every driver in the model, write a line in the assumptions register: the driver name, the assumed value, the basis for the assumption (historical average, vendor quote, sales-leader commitment, benchmark from comparable companies), the assumption owner, and a confidence rating (high, medium, low).

The register has two purposes. The first is to make challenge tractable — a reviewer can read the register in five minutes and identify which assumptions to push on. The second is to make the next plan's revision tractable — you read the register at the end of the quarter, see which assumptions held and which broke, and rebuild from there.

### Step 11 — Surface open questions

A plan that pretends to have answered everything is a plan that has hidden its weakest links. Maintain an open-questions section listing the decisions the plan could not make on its own: which initiative gets funded if cash deteriorates, which hires are first to be deferred, what the price-increase strategy actually is, when the next financing has to close. Each open question belongs to a named owner, with a date by which it must be answered.

### Step 12 — Format for the audience

The CFO reads the plan one way; the CEO reads it another; the board reads it a third. Produce one canonical document with three views layered into it: a one-page summary at the top (the headline numbers, the top three risks, the cash trajectory, the ratios), a fifteen-page operating view in the middle (the driver math, the scenarios, the hiring plan, the assumptions register), and a detailed appendix at the back (month-by-month tables, the historicals reconciliation, the supporting schedules).

### Step 13 — Recommend a cadence for revisits

The plan you ship in November is wrong by January. Build into the output a recommended revision cadence — typically a monthly variance review, a quarterly reforecast, and a mid-year deeper-than-quarterly reset if material assumptions break. Note what counts as "material" — a 10% miss against revenue plan for a quarter is usually enough to trigger a reforecast in early-stage companies; a 3% miss is enough at later stages where the plan is tighter.

### Step 14 — Flag the things this plan cannot do

Explicitly note what the plan does not include. Common gaps: M&A is excluded unless explicitly modeled, foreign-exchange effects are simplified to a single rate, equity-financing rounds are noted but not modeled in detail, share-based compensation accounting is summarized. Flagging these makes the plan honest and prevents downstream surprises.

### Step 15 — Refuse to invent numbers

If the user has not provided a driver — for example, sales productivity per rep — and the skill cannot reasonably benchmark one from public information, do not invent a number. Mark the line as `[REQUIRES INPUT]` with a question for the user. A plan with three missing inputs and the right shape is more useful than a plan with three guessed inputs and false confidence.

## Inputs

- **company_profile** (required) — stage, business model, current scale, fiscal year start.
- **top_down_target** (required) — the revenue, margin, or profitability commitment the plan must reconcile to.
- **historicals** (optional but strongly recommended) — trailing twelve months of P&L and headcount.
- **current_headcount** (optional) — current headcount by function with fully-loaded cost.
- **known_commitments** (optional) — multi-year obligations the plan must accommodate.
- **cash_constraint** (optional) — starting cash, debt facility, runway floor.

## Outputs

- A reconciled annual operating plan with revenue, cost, headcount, and capex sections.
- A side-by-side scenario summary with base, upside, downside, trigger criteria, and ending cash for each.
- An assumptions register with owner and confidence per assumption.
- An open-questions section listing decisions the plan defers.
- A recommended revision cadence.

## Examples

### Worked example — Building the AOP for a Series B SaaS company

**Inputs given to the skill:**

- company_profile: "Vertical SaaS for the construction industry, Series B, $14M ARR run-rate, 78 headcount, fiscal year starting February."
- top_down_target: "Hit $24M ARR by fiscal year end with gross margin at or above 72% and at least 14 months of runway."
- historicals: a CSV of trailing 12 months P&L and a roster of current headcount.
- known_commitments: "Lease through August next year at $42K/month, multi-year cloud contract with 12% YoY increases, two product launches planned for May and October."
- cash_constraint: "$18M cash on hand, $8M undrawn debt facility we prefer not to draw."

**Output produced by the skill (abridged):**

The plan opens with a one-page summary stating: base case ends at $23.4M ARR, upside at $25.7M, downside at $20.6M. Base case ending cash is $9.1M with 13.8 months of forward runway against the next plan year's burn; this misses the runway floor by two months and is flagged in red.

The bottom-up revenue model is built month by month from opening ARR, new logo bookings driven by sales-rep capacity, expansion bookings driven by product-launch adoption, and churn at the trailing-twelve-month rate adjusted for the cohort mix.

The reconciliation step shows the bottom-up came in at $22.8M before reconciliation. To close to $24M, the plan adds one extra sales rep starting in March (cost $180K in plan year), accelerates the May product launch by three weeks (cost: $90K of accelerated marketing), and assumes net retention improves 200 basis points through customer success investment (cost: two new CSM hires).

The scenario summary highlights that the downside case occurs if first-quarter bookings miss plan by more than 18%, in which case the contingency action is to freeze G&A hiring and defer the October product launch.

The assumptions register lists 47 line items. The highest-confidence assumptions are the lease cost, the cloud contract, and the existing customer churn rate. The lowest-confidence assumptions are the productivity ramp of the new sales hires (medium-low, basis: comparable benchmark, owner: VP Sales) and the conversion rate of the May launch's leads (low, basis: pre-launch survey, owner: head of marketing).

The open-questions section has five items, including: should the company draw on the debt facility if base case is tracking and runway dips below 12 months, and what is the trigger for raising the next equity round.

## Limitations

This skill produces a planning artifact, not a financial statement. The output is structured for managerial decision-making, not for audit. Numbers in the plan should not be presented externally as audited financials.

The skill is most accurate for businesses with reasonably stable unit economics — established subscription businesses, services firms with steady utilization, transaction businesses with stable margins. For pre-product-market-fit companies, asset-heavy capex-driven businesses, or businesses undergoing major strategic shifts, the methodology still applies but the assumption register grows much larger and the scenario spread widens accordingly.

The skill cannot replace the judgment of an experienced FP&A operator. It can structure the work, surface gaps, and force reconciliation, but the choices about which assumptions to accept, which to push on, and which to escalate to the CEO remain human choices.

Tax, equity compensation, and complex revenue recognition are simplified in the planning view. Final accounting numbers will diverge from the plan's view; the divergence is normal and managed in close, not in plan.

This skill produces twelve months of detail. Multi-year plans require an extension that this skill does not perform; a twelve-month plan extended naively into a three-year view will mislead more than it informs.

## Sources reviewed

- https://github.com/JerBouma/FinanceToolkit
- https://github.com/jdvelasq/cashflows
- https://github.com/gopalakrishnanarjun/modelmyfinance
- https://github.com/misken/whatif
- https://github.com/pmorissette/ffn
- https://github.com/jason-ash/pyesg
- https://github.com/Ro5s/Startup-Starter-Pack
