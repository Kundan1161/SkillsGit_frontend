---
id: skillsgit-curated/ops-vendor-tco-modeler
version: 1.0.0
name: Vendor TCO Modeler
description: Builds a 3-year total cost of ownership model for a vendor purchase — licenses, implementation, integration, change-management, switching costs, residual risk — and produces a side-by-side apples-to-apples comparison of two or more options that survives finance scrutiny.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: operations
tags: [niche:vendor-management, procurement, tco, total-cost-of-ownership, financial-analysis, vendor-comparison, buy-vs-build]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - tco
  - total cost of ownership
  - vendor cost model
  - 3-year cost
  - cost comparison
  - apples to apples
  - hidden costs
  - implementation cost
  - switching cost
  - buy vs build
  - business case
  - finance model
example_invocations:
  - "Build a 3-year TCO comparing these two HRIS vendors."
  - "Model the real cost of buying this observability tool vs. extending our current one."
  - "We have three quotes. Help me normalize them into a single TCO comparison."
inputs:
  - name: vendor_quotes
    type: text
    required: true
    description: The pricing terms offered by each vendor — list price, discount, units of measurement (per seat, per event, per GB), payment terms, year-over-year escalators, optional modules.
  - name: usage_projection
    type: text
    required: false
    description: Expected volume year-over-year — users, events, GB, transactions, whatever the pricing meter is. Best-effort is acceptable; the model surfaces sensitivity to this.
  - name: organization_burdens
    type: text
    required: false
    description: Internal costs the team can quantify — fully loaded engineering hour rate, ops hour rate, internal project-manager rate, training cost per employee.
  - name: incumbent_or_alternative
    type: text
    required: false
    description: If the comparison is against a current vendor or a build-it-yourself alternative, the incumbent's true cost and the build option's assumptions.
outputs:
  - name: tco_model
    type: markdown
    description: A 3-year TCO model per option, broken down by cost category, with year-by-year totals and an apples-to-apples comparison table.
  - name: sensitivity_analysis
    type: markdown
    description: Tornado-chart-equivalent narrative showing which input assumptions most change the answer, so the team can stress-test the decision.
  - name: finance_one_pager
    type: markdown
    description: A one-page summary suitable for the CFO or budget owner — headline number, key assumptions, comparison delta, and the top three risks to the number.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when the team is comparing the financial story of two or more vendor options — a new vendor vs. another new vendor, a new vendor vs. the incumbent renewing, or buy-vs-build — and the vendor quotes are not directly comparable. The dominant failure mode in vendor decisions is comparing list prices and missing the costs that show up after signature: integration engineering, change management, the second-year escalator, the per-event overage when usage scales as the business intends, the switching cost from the incumbent, the residual risk that a chosen vendor will fail and force a second selection in 18 months.

The skill is appropriate for any vendor purchase above the threshold where finance starts asking for a model — commonly $100k annual or $250k total commitment, though regulated environments often require modeling at lower thresholds. It is not the right tool for low-stakes purchases (modeling a $5k tool is more expensive than the tool), and it is not a substitute for finance team review on large commitments — the model is the team's contribution to that review, not a replacement for it.

A TCO model produced by this skill is opinionated about transparency over precision. Every assumption is named, every dollar has a stated source, every range is widened where evidence is thin. A precise wrong number is worse than a transparent rough one, because the precise number gets defended and the rough one gets debated. The skill's bias is toward showing the work so finance and the deciders can challenge the assumptions, not toward a single defended bottom line.

## How to apply

1. **Normalize the unit of comparison before opening the spreadsheet.** Every vendor quotes in their preferred unit — per seat, per event, per ingestion GB, per protected endpoint, per active customer. Pick the unit that matches the team's actual usage driver (the one that will scale with the business) and convert every vendor's quote into that unit. If vendor A is $10 per seat per month and vendor B is $0.0001 per event with an expected 100 events per seat per month, the head-to-head is $10 vs. $1 per seat per month at projected usage — provided the per-event rate stays the same as volume grows. State the unit choice and defend it in one line.

2. **Project volume in three scenarios, not one.** Pick low, expected, and high volume trajectories for the three-year window. Low is "the business plan slips by 30%." Expected is the team's current plan. High is "the business outperforms by 30%, or we expand the use case." Every TCO number is then a range, not a point. Vendor pricing curves diverge sharply between scenarios — usage-based vendors get expensive faster on the high path, seat-based vendors get expensive faster on the expected path because seats and not usage drive cost. The team's preferred vendor often changes between scenarios; that is the most important finding the model produces.

3. **Build the cost stack as seven categories, every option uses all seven.** Some categories will be zero for some options, which is fine — explicitly zero is more useful than missing. The seven:
   - **License / subscription** — the headline number, three years out.
   - **Implementation** — vendor professional services plus our internal engineering, ops, and PM time during go-live.
   - **Integration** — engineering work to connect to existing systems plus the ongoing maintenance burden on those integrations.
   - **Change management** — training, internal communications, productivity loss during transition.
   - **Operating overhead** — the FTE-equivalent time to run the tool once it is live (admin, monitoring, dealing with vendor support).
   - **Switching cost** — what we pay to leave the incumbent: contractual exit, data migration, parallel-run costs, transition risk.
   - **Residual risk reserve** — a stated cost reserve for the probability-weighted event that this vendor underperforms and we need a re-selection in 18 months.

4. **License pricing is the easiest category to get wrong; pull it apart deliberately.** Take the vendor quote and decompose: list price, discount percentage and what was given up for it (multi-year commitment, marketing reference, payment-terms concession), year-over-year escalator (commonly 5–10% but ranges widely), volume-tier breakpoints, overage rate if usage exceeds the committed tier. The headline annual number is the team's best case in year one; the three-year number is year-1 plus the escalator compounding plus an honest projection of usage growth crossing tier breakpoints. Vendors quote three-year totals using year-1-style math; the model corrects that.

5. **Implementation cost is two budgets, not one.** The vendor's professional-services line item is one budget. The internal engineering, ops, and project-management time during implementation is the other, and it is usually 1x to 2x the vendor PS line. Use the team's fully-loaded hour rate (the rate finance uses for capital-vs-expense decisions, not the salary number — typically 1.3x to 1.6x salary depending on benefits and overhead allocation). Reference customers from the vendor selection scorecard are the best source for hour estimates; if a comparable customer reported 600 engineer-hours over 90 days, that is the input, not the vendor's optimistic estimate.

6. **Integration cost is a build cost plus an ongoing tax.** The one-time engineering work to integrate is straightforward. The ongoing maintenance — keeping the integration working as both systems evolve — is commonly 10–20% of the build cost per year. Capture both. A vendor that integrates via a managed connector to a major SaaS has near-zero ongoing tax; a vendor requiring a custom-built API integration carries an integration tax for the life of the contract.

7. **Change-management cost is real and almost always under-counted.** Training time times average-loaded-rate-per-trainee times number of trainees. Productivity loss during the cutover, typically modeled as 20% of the affected role's loaded cost for two to six weeks depending on the tool. If a change-management consultant is in the plan, their fee plus the internal time supporting them. A vendor whose adoption story relies on the team driving heavy change management has a higher TCO than the licensing line suggests, and the team often discovers this after signing.

8. **Operating overhead is FTE-equivalent, expressed in money.** Pick an honest number for the ongoing FTE time the tool requires once live. Half an FTE of admin time at $X loaded cost. The time the team spends in monthly vendor reviews. The pager hours for an integration that pages. Multiply by the loaded rate. This is the line that distinguishes vendors that look cheap on license but are expensive to run.

9. **Switching cost separates incumbent renewals from new buys.** For a new buy with no incumbent, switching cost is zero. For an incumbent comparison, switching cost is the contractual exit (early termination fees, transition assistance hours we pay for, parallel-run period where both vendors are live), the data migration cost (engineering time to extract, validate, and load data into the new vendor in a usable shape), and the unbudgeted time the team spends supporting both systems for the cutover period. Switching cost is the incumbent's most powerful retention asset; the model makes it visible so the team can decide whether the gap to the new vendor is worth it.

10. **Residual risk reserve makes vendor-failure cost explicit.** Every vendor purchase carries a probability that the choice underperforms and the team has to re-select. Pick a probability (commonly 10–25% over three years for an unproven vendor, 5–10% for an established one), multiply by the cost of a re-selection (a fraction of original implementation cost, typically 30–60%), and book it as a line. This is the most contested line in the model — finance teams sometimes reject it as speculative — but it surfaces the real difference between picking a market leader and picking a hot startup, which the rest of the model otherwise hides.

11. **Build the comparison table as deltas, not absolutes.** Side-by-side absolute numbers force the reader to subtract. The comparison table shows: each cost category for option A, for option B, and the delta (B minus A) with the larger number flagged. The bottom row is the three-year total delta with the sign. A reader who skims the table walks away with one number — which option costs more, by how much, and where the difference comes from.

12. **Run sensitivity analysis on the top three input drivers.** Pick the three inputs that have the widest plausible range — usually usage growth, internal engineering hour estimate, and year-over-year price escalator — and re-run the model at the low and high end of each, holding others at expected. The output is a list: "if usage grows 30% faster, vendor A becomes $X cheaper than vendor B over three years; if it grows 30% slower, vendor B becomes $Y cheaper." This is the tornado-chart story in prose. It tells the deciders which assumptions they are actually betting on.

### Standard TCO model layout

The output document uses these sections in this order:

1. `# 3-Year Total Cost of Ownership: <subject>`
2. `## Decision being modeled` — what options are compared, what time horizon, what unit of comparison.
3. `## Volume projections` — low / expected / high scenarios with named assumptions.
4. `## Cost stack — Option A`
   - License / subscription
   - Implementation (vendor PS + internal hours)
   - Integration (build + ongoing tax)
   - Change management
   - Operating overhead
   - Switching cost (if comparing to incumbent)
   - Residual risk reserve
5. `## Cost stack — Option B` (same structure)
6. `## Apples-to-apples comparison table` — by category, with delta column.
7. `## Sensitivity analysis` — top three input drivers, range, effect on outcome.
8. `## Assumptions register` — every assumption with source, in one place.
9. `## What the model cannot say` — known-unknowns and limits of the analysis.
10. `## Finance one-pager` — for the CFO; headline number, key assumptions, top three risks.

### Composition rules

- **Every number has a source.** Vendor quote, reference customer, finance loaded-rate document, team estimate with named owner. A number without a source is excluded.
- **Ranges over points where evidence is thin.** "$50k–$80k" is honest; "$67,400" is precision theater.
- **The model is reproducible.** Anyone with the inputs can re-derive the totals; nothing is buried in a personal heuristic.
- **Three-year horizon is the default; state when it is not appropriate.** A multi-year SaaS commit needs the full term modeled; a perpetual-license-with-support model may need five years; a renewal modeled at one-year commit needs only one year.
- **No NPV unless finance requires it.** Net present value adds a layer of assumption (discount rate) that often does not change the decision. Default to nominal dollars; offer NPV as an appendix if requested.
- **The output is a decision document, not a spreadsheet.** A TCO that lives only in Excel does not change minds; the markdown narrative with embedded tables is the artifact that travels through approval chains.

## Inputs

- **Vendor quotes (required, text).** Pricing terms per option, including discount basis, escalator, units, tiering, optional modules.
- **Usage projection (optional, text).** Expected volume trajectory in the relevant unit. If absent, the skill makes a stated guess and flags sensitivity.
- **Organization burdens (optional, text).** Loaded hour rates for the roles that will spend time on this. If absent, the skill uses a conservative industry default and flags it.
- **Incumbent or alternative (optional, text).** Current vendor's true cost (license + operating overhead) or build-it-ourselves assumptions. If absent, the skill only compares the listed options.

## Outputs

A complete TCO model document, a separate sensitivity analysis narrative, and a one-page summary intended for the CFO or budget owner. The one-pager is the artifact that gets circulated; the full model is the appendix that backs it up.

## Examples

### Worked example: comparing two enterprise observability vendors

**Input vendor quotes:** "Vendor A: $120k year 1 list, 25% discount for 3-year commit, 6% YoY escalator, priced per host with 800 hosts committed and $0.40/host/day overage. Implementation PS quote $40k. Vendor B: $0.20 per GB ingested, no committed minimum, 8% YoY escalator on rate card, no PS quoted (self-serve)."

**Input usage projection:** "Currently 800 hosts and 12 TB/month of telemetry. Engineering plan adds ~15% hosts per year. Telemetry volume historically grows 25–30% per year due to new instrumentation."

**Input organization burdens:** "Loaded engineering hour rate $200. Loaded ops/SRE hour rate $180. Loaded PM rate $150. Training cost $50/employee for a 2-hour session, applied to ~40 engineers."

**Input incumbent or alternative:** "Incumbent is Vendor C, current contract $90k/year, 2 years remaining at the locked rate, but team complains about query speed and unit-cost growth on the next renewal."

**Expected output (excerpted):**

> # 3-Year Total Cost of Ownership: Observability Platform
>
> ## Decision being modeled
>
> Compare Vendor A (host-priced, committed) and Vendor B (volume-priced, usage-based) for replacing Vendor C (incumbent, two years remaining on existing contract). Time horizon: three years from signature. Unit of comparison: total cost in nominal USD across all cost categories.
>
> ## Volume projections
>
> | Driver | Year 1 | Year 2 | Year 3 |
> |---|---|---|---|
> | Hosts (low) | 800 | 880 | 968 |
> | Hosts (expected) | 800 | 920 | 1,058 |
> | Hosts (high) | 800 | 1,040 | 1,352 |
> | Telemetry GB/mo (low) | 12,000 | 14,400 | 17,280 |
> | Telemetry GB/mo (expected) | 12,000 | 15,600 | 20,280 |
> | Telemetry GB/mo (high) | 12,000 | 16,800 | 23,520 |
>
> Assumptions: host growth follows engineering plan (low) to outperformance (high); telemetry growth driven by instrumentation density, not host count, so it grows independently.
>
> ## Cost stack — Vendor A (host-priced)
>
> | Category | Year 1 | Year 2 | Year 3 | 3-yr total |
> |---|---|---|---|---|
> | License (expected) | $90,000 | $101,520 | $123,648 | $315,168 |
> | License (high — overage) | $90,000 | $115,920 | $187,200 | $393,120 |
> | Implementation — vendor PS | $40,000 | — | — | $40,000 |
> | Implementation — internal (engineering 200h × $200; ops 120h × $180; PM 80h × $150) | $73,600 | — | — | $73,600 |
> | Integration — build (existing dashboards, alerting) | $50,000 | — | — | $50,000 |
> | Integration — ongoing tax (15% of build) | — | $7,500 | $7,500 | $15,000 |
> | Change management — training | $2,000 | — | — | $2,000 |
> | Change management — productivity loss (40 eng × 2 wks × 20% × $200 × 40 h/wk) | $128,000 | — | — | $128,000 |
> | Operating overhead (0.25 FTE ops × $180 × 1,800 h/yr) | $81,000 | $81,000 | $81,000 | $243,000 |
> | Switching cost — exit Vendor C early (incl. 2-yr remainder buyout est. 60% of remaining commit $90k × 2 × 60%) | $108,000 | — | — | $108,000 |
> | Switching cost — parallel run (2 months Vendor C + Vendor A) | $15,000 | — | — | $15,000 |
> | Residual risk reserve (15% × 40% × $113,600 implementation) | — | — | — | $6,816 |
> | **3-yr total (expected)** | | | | **$996,584** |
> | **3-yr total (high)** | | | | **$1,074,536** |
>
> Notes: License high-case uses overage rate for hosts above 800; year 3 sees 258 hosts of overage at $0.40 × 365 days each. The change-management productivity loss is the single largest non-license line — flagged in the assumptions register because the range is wide.
>
> ## Cost stack — Vendor B (volume-priced)
>
> | Category | Year 1 | Year 2 | Year 3 | 3-yr total |
> |---|---|---|---|---|
> | License (expected, 12k–15.6k–20.3k GB/mo × $0.20 × 12 × escalator) | $28,800 | $40,435 | $56,766 | $126,001 |
> | License (high — 12k–16.8k–23.5k GB/mo) | $28,800 | $43,545 | $65,830 | $138,175 |
> | Implementation — vendor PS | $0 | — | — | $0 |
> | Implementation — internal (engineering 280h × $200; ops 80h × $180; PM 60h × $150) | $79,400 | — | — | $79,400 |
> | Integration — build | $65,000 | — | — | $65,000 |
> | Integration — ongoing tax (15%) | — | $9,750 | $9,750 | $19,500 |
> | Change management — training | $2,000 | — | — | $2,000 |
> | Change management — productivity loss | $128,000 | — | — | $128,000 |
> | Operating overhead (0.4 FTE ops × $180 × 1,800 h/yr — more tuning needed) | $129,600 | $129,600 | $129,600 | $388,800 |
> | Switching cost — exit Vendor C | $108,000 | — | — | $108,000 |
> | Switching cost — parallel run | $15,000 | — | — | $15,000 |
> | Residual risk reserve (10% × 40% × $144,400 implementation) | — | — | — | $5,776 |
> | **3-yr total (expected)** | | | | **$937,477** |
> | **3-yr total (high)** | | | | **$949,651** |
>
> Notes: Vendor B is cheaper on license (especially at high host count where Vendor A's overage kicks in) but more expensive on operating overhead due to volume-tuning work. Self-serve implementation has lower PS but slightly higher internal hours.
>
> ## Apples-to-apples comparison
>
> | Category | Vendor A | Vendor B | Delta (B − A) |
> |---|---|---|---|
> | License (expected, 3 yr) | $315,168 | $126,001 | **−$189,167** (B cheaper) |
> | Implementation (PS + internal) | $113,600 | $79,400 | −$34,200 |
> | Integration (build + tax) | $65,000 | $84,500 | +$19,500 |
> | Change management | $130,000 | $130,000 | $0 |
> | Operating overhead | $243,000 | $388,800 | **+$145,800** (B more expensive) |
> | Switching cost | $123,000 | $123,000 | $0 |
> | Residual risk reserve | $6,816 | $5,776 | −$1,040 |
> | **3-yr total (expected)** | **$996,584** | **$937,477** | **−$59,107 (B cheaper)** |
> | **3-yr total (high)** | **$1,074,536** | **$949,651** | **−$124,885 (B cheaper)** |
>
> ## Sensitivity analysis
>
> | Input | Low | Expected | High | Effect on B − A delta |
> |---|---|---|---|---|
> | Telemetry growth rate | 15%/yr | 25%/yr | 35%/yr | At low growth, B is ~$110k cheaper; at high growth, B is only ~$25k cheaper. |
> | Operating overhead FTE for Vendor B | 0.25 FTE | 0.40 FTE | 0.60 FTE | At 0.25 FTE for B, Vendor B is ~$140k cheaper; at 0.60 FTE, the gap closes to ~$10k. |
> | Vendor A YoY escalator | 4% | 6% | 9% | A 9% escalator widens the gap by ~$30k in B's favor; a 4% escalator narrows it by ~$25k. |
>
> Key takeaway: the decision depends most on the operating overhead assumption for Vendor B. If the team can run Vendor B with the same 0.25 FTE as Vendor A, the gap doubles in B's favor. If not, the two options are nearly tied on cost — and the choice should be made on non-cost criteria from the scorecard.
>
> ## Assumptions register
>
> - Loaded engineering hour rate: $200. **Source:** finance loaded-rate document, 2026 H1.
> - Productivity loss during cutover: 20% × 2 weeks × 40 engineers. **Source:** post-mortem of last major tooling migration; range is 15–30%.
> - Vendor C early-exit cost: 60% of remaining commit. **Source:** Vendor C contract section 14.2; team's legal counsel confirms enforceability.
> - Residual risk probability: 15% for Vendor A (mid-tier vendor, smaller installed base), 10% for Vendor B (market-leading volume-priced vendor). **Source:** team judgment; documented for finance.
> - All other assumptions: see line-item notes.
>
> ## What the model cannot say
>
> - Whether Vendor B's volume-based pricing exposes us to a runaway bill from an instrumentation accident (e.g., debug logging left on in production for a week). The model assumes the team has volume guardrails; if not, residual risk is higher than booked.
> - Whether Vendor A's host-based pricing makes us under-instrument to save cost. This is a quality risk, not a cost risk, and is not in the TCO.
> - Vendor C's renewal rate two years from now, when the existing contract expires. The "do nothing" option is not fully costed; it carries an unknown renewal jump.
>
> ## Finance one-pager
>
> **Subject:** Observability platform replacement — 3-year TCO comparison
>
> **Recommendation:** Vendor B is approximately $60k cheaper over three years at expected usage, widening to $125k at high usage. The recommendation is contingent on the operating overhead assumption (0.4 FTE for B vs. 0.25 FTE for A); if the team cannot operate B at the modeled overhead, the options are near-tied and selection should hinge on the scorecard's non-cost criteria.
>
> **Key assumptions, in order of impact:**
> 1. Telemetry growth at 25%/yr — based on three years of historical pattern.
> 2. Vendor B can be run with 0.4 FTE of ops time — based on Vendor B reference customer of comparable scale.
> 3. Vendor A escalator at 6% — based on Vendor A's commercial pattern with similar-sized customers.
>
> **Top three risks to the number:**
> 1. Vendor B volume bill spikes from an instrumentation accident — mitigated by a quota guardrail in the integration design; cost of guardrail included in build line.
> 2. Vendor A overage charges if host count exceeds 800 — committed-tier shape protects up to 800; beyond that the overage rate applies and changes the comparison sharply.
> 3. Change-management productivity loss exceeds the 20% × 2 weeks assumption. A 30% × 3 weeks scenario adds ~$160k to both options equally; does not change the comparison but raises the absolute number.

## Limitations

- A TCO is the cost story. It does not tell the team which option to pick; it tells them what each option costs across three years and where the costs come from. If the cheaper option is also the worse functional fit (see the scorecard skill), the team has a real trade-off to make, not a TCO answer.
- Vendor pricing in the early conversations is rarely the final pricing. The discount story changes in negotiation, the escalator is negotiable, and the overage rate is one of the most flexible variables. The model is built on the offered terms; the team should re-run it on the final terms before signature.
- The "residual risk reserve" line is mathematically soft. It is a probability times a hypothetical cost; finance teams sometimes object that it is double-counting. The skill includes it because the alternative (zero probability of vendor failure) is also wrong, and the line surfaces the discussion explicitly rather than burying it.
- Internal-hours estimates are the second-softest input after residual risk. The skill uses reference-customer-validated estimates where available; teams should bias toward higher estimates and run the sensitivity. Engineering hours are almost always under-counted on the first pass.
- The skill does not produce a fully formatted financial model the CFO's finance team can drop into their quarterly model. The output is a decision document with embedded tables; the team's finance partner will translate to the corporate model and re-run the math. Plan for that translation step.
- For incumbent renewals, the "do nothing" option needs separate treatment — including a forecast of the incumbent's likely renewal price. That forecast is its own analysis (look at the vendor's recent renewal patterns with similar customers); the TCO model leaves a placeholder for it rather than fabricating a number.

## Sources reviewed

- https://github.com/cisco-open/device-tco-calculator
- https://github.com/CenturyLinkCloud/EstimatorTCO
- https://github.com/tractorjuice/arc-kit
- https://github.com/Funkmyster/awesome-supply-chain
- https://github.com/makegov/awesome-procurement-data
- https://github.com/mgifford/open-source-contracting
