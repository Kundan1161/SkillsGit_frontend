---
id: skillsgit-curated/commitment-strategy-planner
version: 1.0.0
name: Cloud Commitment Strategy Planner
description: Design a Savings Plans / Reserved Instances / Committed Use Discounts portfolio — coverage target, term mix, payment option, blast-radius limits, and hedging strategy.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:cloud-finops, savings-plans, reserved-instances, committed-use-discounts, commitment-strategy, hedging, aws, gcp, azure]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  tools_optional: [code_execution, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - savings plan strategy
  - reserved instance plan
  - committed use discount
  - commitment portfolio
  - coverage target
  - ri laddering
  - sp laddering
  - commitment hedging
  - convertible ri
  - compute savings plan vs ec2 savings plan
  - cud strategy
  - commitment renewal
example_invocations:
  - "Design a Savings Plan portfolio for our $250K/month AWS compute spend with 60% on stable services."
  - "We have RIs expiring next quarter — recommend a laddering and term-mix strategy."
  - "Help me decide between 1-year no-upfront and 3-year partial-upfront Compute Savings Plans."
inputs:
  - name: spend_baseline
    type: text
    required: true
    description: A description of the eligible-for-commitment compute baseline — total monthly $, breakdown by service/family, growth trend over the last 6-12 months, stable vs spiky portion. Numbers are better than adjectives.
  - name: cloud_provider
    type: choice
    required: true
    description: Which commitment construct to model.
    choices: [aws_savings_plans, aws_reserved_instances, gcp_cud, azure_reservations, azure_savings_plan, multi_cloud, unknown]
  - name: existing_commitments
    type: text
    required: false
    description: Any active commitments — type, term, payment option, monthly $ committed, expiration date. Used to model laddering and renewal cliffs.
  - name: business_constraints
    type: text
    required: false
    description: Constraints that shape acceptable risk — cash-flow position, contract horizon, M&A plans, customer-concentration risk, planned migrations or shutdowns.
  - name: workload_volatility
    type: choice
    required: false
    description: Self-assessed volatility of the workload mix over the next 1-3 years.
    choices: [very_stable, stable, moderate, volatile, very_volatile, unknown]
  - name: organizational_authority
    type: choice
    required: false
    description: Who can sign the commitment, and how fast.
    choices: [engineering_can_self_serve, finance_approval_required, board_approval_required, joint_venture_or_jca, unknown]
outputs:
  - name: strategy_report
    type: markdown
    description: Narrative report with recommended portfolio (coverage target, term mix, payment mix), the reasoning, blast-radius analysis under three scenarios (workload drops 20%, drops 40%, grows 50%), laddering schedule, and renewal checklist.
  - name: strategy_json
    type: json
    description: Machine-readable structure — target_coverage_pct, portfolio (array of {type, term_years, payment_option, monthly_commitment_usd, scope, rationale}), laddering_schedule (array of {purchase_window, commitment_block, rationale}), blast_radius (object with three scenarios and resulting waste estimates), break_even_months (per block), confidence (float).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Cloud Commitment Strategy Planner

## When to use

**Mandatory framing.** This skill produces methodology guidance for commitment-purchase decisions. The outputs are not financial advice and are not a substitute for finance, treasury, or procurement review. Any commitment purchase locks the organization into multi-year cash and contract obligations that survive personnel changes, reorgs, and M&A; the recommended portfolio must be approved by the people who own those exposures before any purchase is made.

Use this skill when the organization has enough cloud spend that commitment economics start mattering — practically, this is $20K–$50K/month of compute and up. Below that, the savings rarely justify the complexity, and on-demand plus aggressive rightsizing is the right answer. Above that, leaving commitments on the table is a real-money decision, and the question becomes not "should we commit?" but "how much, on what term, in what payment mix, with what hedging against the workload changing under us?"

Typical entry points: a FinOps lead preparing the first commitment-purchase recommendation to leadership; a platform engineer whose previous Savings Plan is expiring and is being asked to recommend the renewal; a CFO-office analyst asked to model the cash-vs-discount trade-off across payment options; a startup approaching its Series C with a meaningful cloud bill and a board that wants to see margin discipline.

The skill is appropriate for *designing* the portfolio. It is **not** appropriate for:

- Executing the purchase. The skill does not have account access and does not call any provider APIs.
- Negotiating Enterprise Discount Programs / private pricing. EDP and committed-spend agreements layer on top of commitments; the interaction is a procurement question, not a methodology one. Surface as a parallel workstream.
- Forecasting the workload. The skill's blast-radius analysis depends on the volatility input the user provides; if that input is hand-wavy, the recommended coverage target should be lower.

## How to apply

Commitment strategy is a hedge-construction problem. The organization is short on-demand price (i.e., exposed to it) and long on its own forecast of workload demand. Commitments are how the org swaps some of that on-demand exposure for a fixed cash obligation at a discount. Everything in the methodology flows from making that trade explicit.

1. **Reduce the workload to a *commitable baseline* first.** Not all spend is eligible. Strip out: spot/preemptible spend (already cheap, and the wrong instrument for it), one-off batch jobs that won't recur on the same SKU, ephemeral test environments that will be deleted before any commitment pays back, and any line item that the team is actively trying to eliminate (e.g., a soon-to-be-migrated workload). What's left is the *stable, recurring* compute baseline. Express it as a monthly $ with a confidence band, not a point estimate. A baseline of "$180K/month +/- $20K with 70% confidence over the next 12 months" is honest; "$180K/month" is theater.

2. **Choose the right commitment instrument before choosing the size.** The instrument matters more than the discount rate:
   - **Compute Savings Plans (AWS)** trade some discount for maximum flexibility: covers EC2, Fargate, Lambda; any family, any region, any OS. The right default for most orgs.
   - **EC2 Instance Savings Plans (AWS)** give a deeper discount but lock to a family in a region. Use only when a meaningful block of demand is genuinely locked to one family and the org tolerates the lock.
   - **Standard RIs (AWS)** give the deepest EC2 discount and the least flexibility. Mostly relevant for RDS, Redshift, OpenSearch — where SPs don't apply.
   - **Convertible RIs (AWS)** trade discount for the right to swap family/region. Useful as a hedge layer.
   - **Committed Use Discounts (GCP)** — resource-based CUDs vs spend-based CUDs differ similarly: spend-based is flexible (the GCP analogue to Compute SP); resource-based is deeper but family-specific.
   - **Azure Reservations** are roughly equivalent to RIs; **Azure Savings Plans for compute** are roughly equivalent to Compute SPs and are usually the right default.

3. **Set the coverage target by *risk appetite*, not by industry benchmark.** A common piece of bad advice is "aim for 70% coverage." The right target is the largest fraction of the baseline the org is willing to keep paying for under the worst plausible workload-decline scenario. Concretely:
   - Estimate `floor_baseline` = the monthly compute spend the org is virtually certain to still need 12 months from now, even under reasonable adverse scenarios (lost a top customer, paused a product line).
   - Target coverage somewhere between `floor_baseline` and `0.85 * floor_baseline`. Anything above `floor_baseline` is reasonable; anything below leaves too much on the table.
   - **Never recommend 100% coverage.** It maximizes static discount but offers zero hedge against demand drops and tends to push over-commitment into the next renewal cycle.

4. **Pick the term mix to match the workload's predictability horizon.** Most orgs cannot honestly forecast workload three years out. The default is:
   - **1-year term as the spine.** Covers the bulk of `floor_baseline`. Renews annually so you can rebalance.
   - **3-year term as the underlay.** Used only for the portion of `floor_baseline` you are *very* confident in (long-running production workloads, regulated services with long contract horizons). 3-year deepens discount materially but adds material lock.
   - A 70/30 or 60/40 split between 1-year and 3-year is a reasonable default if no constraints push it. State the split explicitly; don't bury it in an aggregate number.

5. **Pick the payment option as a cash-vs-discount trade-off, not a habit.** All-upfront beats partial-upfront beats no-upfront on rate, but each step costs cash today. The decision rule:
   - If the company is cash-constrained (early-stage startup, post-bridge, working capital tight), **no-upfront** is almost always right despite the lower discount. The dollar saved by going partial- or all-upfront is not worth the risk-adjusted cost of tying up cash.
   - If the company is cash-rich and the treasury yield on cash is comparable to or below the implied yield of the upfront discount, **all-upfront** can be the disciplined answer. Compute the implied annualized yield on the difference (typically 4-8%) and compare to the org's current cost of capital.
   - **Partial-upfront** is rarely the right pick. It tends to be the compromise nobody wanted; either you can pay up or you can't.

6. **Stagger purchases to avoid renewal cliffs.** A single $X million purchase that all expires on the same Monday is operationally fragile and gives the team zero room to rebalance. Spread purchases across 3-6 months in tranches. A laddering schedule like: 25% of the 1-year block bought now, 25% in 90 days, 25% in 180 days, 25% in 270 days, then renew each tranche on its own anniversary. This converts "one big bet" into "four smaller, rolling bets," which is what you want operationally.

7. **Model blast radius under at least three workload scenarios.** For each scenario, compute the *waste exposure* (the $ of commitment that would go unused) and the *coverage shortfall* (the on-demand spend that would resume).
   - **Scenario A — workload drops 20%.** A normal-bad scenario. The portfolio should waste <5% of committed spend here. If it doesn't, the recommended coverage is too high.
   - **Scenario B — workload drops 40%.** A severe-but-survivable scenario (loss of a flagship customer, deliberate workload migration off-cloud). Waste should be tolerable; the recommendation should explicitly call out the dollar number.
   - **Scenario C — workload grows 50%.** A success scenario. The portfolio should still capture savings on the new spend (Compute SPs auto-apply within scope, so this is mostly automatic — but EC2-SP and standard-RI exposures need explicit recommendation to top-up).

8. **Compute break-even months for each commitment block.** Break-even = the number of months at the assumed utilization at which the commitment's cumulative discount equals its sunk cost (the upfront payment, if any). If break-even is more than two-thirds of the term, the block is fragile — small workload changes can flip it to a loss. Recommend either a shorter term, a smaller block, or a more flexible instrument.

9. **Hedge with convertibles where the workload's *shape* is uncertain.** If the org is confident in `floor_baseline` dollars but uncertain in family/region mix (e.g., mid-migration from x86 to Graviton, or planning a multi-region rollout), a Convertible RI layer (or a Compute SP in place of an EC2 SP) provides the right hedge. The discount is lower; the option value is real.

10. **Build a renewal checklist into the recommendation.** Every commitment expires; the moment of renewal is when the org either (a) leaks on-demand because nobody noticed, or (b) rolls over the old size without rechecking the baseline. The recommendation should include: a calendar reminder 90 days before expiry, a re-audit step (re-run the baseline calculation), and a default policy (renew at the floor, not at the prior commitment level).

11. **Acknowledge the procurement layer.** Above ~$0.5M/year in commitment, the org should also be in conversation with the provider about a private pricing agreement / Enterprise Discount Program. These are not exclusive with commitments; they are *layered*. Surface this as a parallel workstream and recommend looping procurement in before any large 3-year purchase.

12. **Self-check before returning.** Confirm: (a) the baseline is stated with a confidence band; (b) the instrument choice is justified, not assumed; (c) the coverage target is anchored to `floor_baseline`, not an arbitrary percentage; (d) three blast-radius scenarios are present with dollar numbers; (e) the laddering schedule is concrete (dates or month offsets, not "stagger over time"); (f) break-even months are computed for each block; (g) the disclaimer is present.

13. **Calibrate confidence.** Below 0.6, recommend the org defer the purchase by 30-60 days and pull better data first (typical gaps: no amortized cost view, no usage-type breakdown, no clarity on which workloads are migrating). Below 0.4, refuse to recommend any 3-year block; only 1-year blocks should be in scope until the baseline is clearer.

## Inputs

- `spend_baseline` (required, text) — the more quantitative, the better. A monthly $ with breakdown by service/family and a trend chart description is enough; a vague "we spend a lot on EC2" forces lower confidence.
- `cloud_provider` (required, choice) — anchors which instruments are in scope.
- `existing_commitments` (optional, text) — drives laddering and renewal-cliff analysis.
- `business_constraints` (optional, text) — drives term and payment recommendations.
- `workload_volatility` (optional, choice) — drives the blast-radius scenarios and coverage target.
- `organizational_authority` (optional, choice) — drives how the recommendation is framed and what approvals it flags.

## Outputs

- `strategy_report` (markdown) — opens with the recommended target coverage and one-line rationale; portfolio table (per-block: instrument, term, payment, monthly commitment, scope, rationale); laddering schedule with concrete month offsets; blast-radius table for three scenarios; break-even months per block; renewal checklist; procurement-layer note; explicit limitations.
- `strategy_json` (JSON) — fully structured per the frontmatter schema.

## Examples

### Example 1 — AWS, $250K/month compute, partially covered

**Input spend_baseline:** "AWS compute $250K/month amortized, growing ~2% MoM, ~$180K of which is stable production on m6i/r6i/c6i; ~$50K spiky CI/CD and batch; ~$20K GPU (g5/g6) growing fast as we launch an ML product." **cloud_provider:** `aws_savings_plans`. **existing_commitments:** "1-year no-upfront Compute SP $100K/yr committed, 6 months remaining." **workload_volatility:** `stable`. **business_constraints:** "Series C-ready, cash-rich, board pushing on gross margin."

**Output strategy_report (excerpt):**

> **Recommendation.** Target ~$155K/month covered (≈62% of current baseline). Portfolio: a $120K/month 1-year no-upfront Compute SP (renews the expiring block at right-size), plus a $35K/month 3-year all-upfront Compute SP layered underneath the production-baseline floor. Do *not* commit on the GPU workload yet — too new, family mix still moving; revisit in 90 days when the g5/g6 split is clearer.
>
> **Laddering.** Buy the 1-year block now at expiry. Buy the 3-year block in two tranches: $20K/month at T+0, $15K/month at T+90 days, both with 1-month overlap to the expiring block to avoid a coverage gap.
>
> **Blast radius.**
> - 20% drop: ~$3K/month of unused commitment, recoverable next renewal.
> - 40% drop: ~$22K/month unused — material but not catastrophic; flag as the maximum acceptable scenario.
> - 50% growth: existing SPs cap discount; recommend a top-up tranche if growth sustains past 60 days.
>
> **Break-even.** 1-year no-upfront: zero upfront, break-even is effectively month 1. 3-year all-upfront: ~14 months at the assumed utilization. Well inside the 36-month term; safe.

### Example 2 — GCP, mid-migration

**Input spend_baseline:** "GCP $90K/month, 70% on Compute Engine, mid-migration from N2 to C3D (~40% migrated). Strong growth on BigQuery slots." **cloud_provider:** `gcp_cud`. **workload_volatility:** `volatile`.

**Output strategy_report (excerpt):**

> **Recommendation.** Use **spend-based CUDs** as the spine while the family mix moves. Avoid resource-based CUDs on N2 — the migration will strand them. Target ~50% coverage, 1-year only, no 3-year exposure until the migration completes. Add BigQuery slot commitments separately, sized to p50 not p95 of the slot baseline.
>
> **Why not 70%.** Volatility is high; the migration alone introduces +/- 25% family-mix uncertainty. The hedge value of 1-year/spend-based dominates the deeper discount of 3-year/resource-based.

### Example 3 — first-time buyer

**Input spend_baseline:** "Azure $35K/month, we have never bought a reservation, mostly D-series VMs." **cloud_provider:** `azure_savings_plan`. **workload_volatility:** `stable`. **organizational_authority:** `finance_approval_required`.

**Output strategy_report (excerpt):**

> **Recommendation.** Start with a $15K/month 1-year no-upfront Azure Savings Plan for compute. This is small enough to be a low-blast-radius first commitment and large enough to demonstrate the savings to finance before requesting a larger purchase next quarter. Do not buy any 3-year block on the first cycle; build the org muscle first.

## Limitations

- The skill does not have live pricing or live discount rates. Estimates assume current published rates; if rates change materially, downgrade confidence.
- The skill does not model EDP / private pricing layered on top of commitments. That interaction is non-linear and is a procurement workstream.
- The skill assumes the buyer can purchase. Some enterprise accounts require approval chains that can take longer than the recommended laddering window; surface that as a process risk.
- The blast-radius scenarios are illustrative — the actual workload shape can deviate in ways the three canonical scenarios don't capture.
- The skill does not negotiate with the provider on the user's behalf and does not place orders.

## Sources

The methodology synthesizes patterns from these permissively-licensed open-source FinOps projects (used for taxonomy of commitment constructs, coverage-calculation patterns, and amortization conventions). No code or text is copied; the methodology is original.

- https://github.com/opencost/opencost
- https://github.com/infracost/infracost
- https://github.com/project-koku/koku
- https://github.com/ravikiranvm/aws-finops-dashboard
- https://github.com/aws-samples/coast-grafana-cost-intelligence-dashboards
- https://github.com/cloud-custodian/cloud-custodian
