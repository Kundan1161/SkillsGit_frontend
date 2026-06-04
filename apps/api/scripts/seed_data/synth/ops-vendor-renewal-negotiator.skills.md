---
id: skillsgit-curated/ops-vendor-renewal-negotiator
version: 1.0.0
name: Vendor Renewal Negotiator
description: Reviews a vendor renewal proposal and produces a counter-position covering price, term, commitment, exit, SLA, audit rights, and sub-processors, with reasoning and BATNA.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: operations
tags: [niche:vendor-management, procurement, contract-negotiation, renewal, saas, vendor-management, commercial-terms]
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
  - vendor renewal
  - contract renewal
  - renewal negotiation
  - price increase
  - saas renewal
  - true-up
  - auto-renew
  - termination for convenience
  - sla credits
  - audit rights
  - sub-processor
  - exit assistance
example_invocations:
  - "Our CRM renewal landed with a 22% increase. Help me build a counter."
  - "Review this renewal quote and tell me what to push back on."
  - "Draft my negotiation position for the security tool renewal — they want 3 years up front."
inputs:
  - name: renewal_proposal
    type: text
    required: true
    description: The vendor's renewal proposal — pricing, term length, payment terms, any new modules being introduced, any commercial conditions attached to discounts.
  - name: current_contract
    type: text
    required: false
    description: Material terms of the current contract — price, expiry date, auto-renewal mechanics, notice period, surviving clauses, exit assistance, audit rights, SLA structure.
  - name: usage_and_value
    type: text
    required: false
    description: What the team is actually using (seats, volume, modules), what value the team is getting (concrete outcomes, not vendor-marketed metrics), and what would happen if the team left.
  - name: batna_options
    type: text
    required: false
    description: The team's best alternative — incumbent of a different vendor we could move to, an internal-build option, a downgrade-and-live-with-it option, walk-away cost.
outputs:
  - name: counter_position
    type: markdown
    description: A complete counter-proposal organized by negotiation lever — price, term, commitment, exit, SLA, audit, sub-processors — with the ask, the reasoning, and the fallback.
  - name: walkaway_threshold
    type: markdown
    description: An explicit statement of what terms make the renewal a no-deal, written before the negotiation starts so it cannot be retroactively rationalized.
  - name: negotiation_brief
    type: markdown
    description: A one-page brief for the lead negotiator — opening position, sequencing, the moves to make in order, what to concede when.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a vendor has put a renewal proposal in front of the team and the default behavior — accept the increase, sign for another year — is about to happen. The skill is for the moment after the renewal email arrives and before the team replies. It works for SaaS renewals, professional-services retainers, managed-service contracts, and any commercial relationship with a defined term that the vendor is proposing to extend on new terms.

Renewals are where vendors recover the discount they gave the team at the initial sale. The headline 5–10% "standard" increase often masks a real economic shift — new modules quietly added, a usage tier that has been exceeded for six months, a multi-year commitment requested in exchange for the smaller increase, an auto-renewal clause that just kicked in and locked the team for another year without anyone noticing. The skill is opinionated about not signing reflexively. Reading the proposal carefully and constructing a counter is cheap; the savings on a typical mid-market renewal are 8–25% off the proposed number, and the term improvements are even more durable than the price savings.

The skill is not the right tool for the initial vendor selection (use the scorecard, RFP, and TCO skills for that), and it is not a substitute for legal review on terms changes. It is the right tool for the commercial position: what to ask for, in what order, with what fallback. Legal review focuses on the contract language; this skill focuses on the deal shape.

## How to apply

1. **Surface every change the renewal makes — not just the price.** A renewal proposal is rarely just a price update. The vendor has typically also moved the price metric (per seat to per user, per event to per million events), added or shifted modules between paid and free tiers, changed the SLA structure, lengthened the auto-renewal notice period, or introduced a multi-year commitment as a default. List every change against the current contract on one page. Until that page exists, the team cannot negotiate; they are reacting to a price number while signing terms they have not noticed.

2. **Compute the real year-over-year price change in your unit.** Vendors quote increases against list, against this-year-paid, or against a "had you bought today" reference price. Pick the unit that matters to the team — total spend per relevant business driver (per active user, per protected workload, per dollar of revenue protected) — and compute the year-over-year change in that unit. A 10% increase in dollar terms on a 30% smaller seat count is a 57% increase per seat. A flat dollar number with a moved metric (per user to per active user) is often a real increase. State the comparable number in the team's response so the vendor cannot fall back on the list comparison.

3. **Identify what the team actually uses and at what value.** Renewals are the moment to right-size. Pull the usage data: how many seats are active in the last 90 days, what modules have not been touched, what volume tier the team is actually consuming. A renewal often surfaces 20–40% paid seats that have not been used in months. Drop them in the counter; if the vendor pushes back, the team has a documented use number to defend it. Separately, name the value: what concrete outcome the tool delivers, in numbers if possible. This becomes the answer to the vendor's "but we deliver $X of value" pitch.

4. **State the BATNA before opening the counter.** Best Alternative To a Negotiated Agreement is the negotiation lever the team has if the renewal fails. Document it concretely: which competing vendor would be the next pick, how long would a migration take, what would the migration cost, what is the productivity gap during transition. The BATNA does not have to be exercised; it has to be credible. A vendor who senses no BATNA will hold pricing. A vendor who hears a specific alternative ("we have ProductX in pilot; if we cannot reach terms, we extend the pilot and migrate by Q3") moves faster. Write the BATNA in two lines for the negotiation brief and one line for the counter to the vendor.

5. **Identify the negotiation levers and rank them by reversibility.** A vendor renewal has six classic levers. Rank them by how hard each is to change later if the team gives way today:
   - **Price.** Easy to revisit next year; medium-reversibility.
   - **Term length.** Hard to change mid-term; low-reversibility — once signed for three years, the team is committed.
   - **Commitment volume.** Hard to true-down mid-term; low-reversibility.
   - **Auto-renewal and notice.** Hard to escape once you miss the window; very low reversibility.
   - **Exit and transition-assistance terms.** Very hard to add at exit; near-zero reversibility — has to be set now.
   - **SLA structure and credits.** Hard to negotiate when an SLA event has happened; low reversibility.
   - **Audit and sub-processor rights.** Hard to enforce retroactively; low reversibility.
   The team's negotiating energy goes to the low-reversibility levers first. Trading a 3% price concession for a 10-day notice-period reduction and a transition-assistance clause is almost always a good trade.

6. **For price, lead with the ask that is supportable, not the ask that is aggressive.** A counter at 50% off list is theater that wastes a round. A counter that is grounded — "we will renew at flat year-over-year, supported by usage that is X seats below committed, market reference of competitor Y at lower per-unit cost, and a 90-day timeline that allows us to alternative-source if needed" — sets the negotiation on the team's facts. The fallback positions step down from there: flat, then 5% increase, then 8%, with each step tied to a specific concession from the vendor on a different lever.

7. **Reshape the term length deliberately.** Vendors prefer multi-year commitments because they reduce churn risk and lock the customer through any service degradation. Customers prefer one-year terms unless they get a meaningful concession for length. Default counter: renew for one year. Trade up to two years for a stated price concession (commonly 10–20% off the year-1 number) and a price-lock on years 2 and 3. Decline three-year commitments unless the vendor is a clear strategic anchor — three years is too long given the cadence of product change in most categories.

8. **Reshape commitment volume to match current usage plus an honest growth allowance.** If the team paid for 200 seats but uses 140, the renewal commit is 140 plus a stated growth allowance (usually 15–25% of current usage, depending on the team's plan). Anything above the allowance can be added at a contractually-stated tier price during the term. The vendor's negotiator will resist on the "true-down" because it directly reduces their renewal number; this is where the documented usage data is the team's lever.

9. **Negotiate auto-renewal explicitly. Always.** Auto-renewal clauses are vendor-favorable by design — they convert customer inattention into renewals at the vendor's preferred terms. The counter is one of:
   - Remove auto-renewal entirely; renewal is opt-in.
   - Keep auto-renewal but with a 90-day prior written notice from the vendor (not from us) before the renewal date, identifying the proposed terms.
   - Keep auto-renewal but shorten our termination window to 30 days before renewal (commonly vendors push for 90 days; we want 30).
   At least one of the three is achievable in almost every renewal. Pick the one that fits the relationship.

10. **Add transition-assistance terms now, before they matter.** The clause to add: on termination (for any reason), the vendor provides N days of transition assistance at no incremental cost, including data export in a documented format, knowledge transfer to a successor team or vendor, and named contact availability. Without this clause, the team's exit cost is what the vendor decides it is, charged at professional-services rates. With it, the exit cost is bounded. Common ask: 60–90 days of transition assistance, 40–80 hours of named-contact time, data export in CSV plus a documented schema. Vendors resist; the team wins this clause more often than they expect because vendors do not like to admit on the renewal call that exits are common.

11. **Tighten SLA credits and define their math.** SLA structure is the most-marketed and least-enforced part of vendor contracts. The renewal is the moment to fix the math. Two things to insist on:
    - **Service credits are not the sole remedy.** If the vendor materially breaches an SLA for two consecutive months, the customer has a termination right without early-termination fees. Otherwise the SLA is a refund of one month's fee for an outage that cost the customer ten times that — credit-only structures are not credible.
    - **Credit computation is automatic and documented.** Define the calculation; do not leave it to the vendor's discretion. State the data source (vendor's status page, or a customer-controlled monitor for higher-rigor needs).
    A 15-minute discussion at renewal on these two points is worth more than the headline price concession.

12. **Audit and sub-processor rights are the legal-leaning lever, but the operator owns them.** Two clauses to fight for:
    - **Audit right exercisable annually on 30 days notice**, with the cost borne by the customer if no material finding and by the vendor if a material finding (this fee shift makes the audit credible without bankrupting the team).
    - **Sub-processor notification with right to object** — the vendor notifies of new sub-processors at least 30 days before they touch customer data; the customer has the right to terminate if it objects in writing and the vendor proceeds.
    These are standard in mature vendor contracts but are often missing from mid-market renewals where the original sale was light on legal review. The renewal is the moment to add them.

### Standard counter-position layout

The output document uses these sections in this order:

1. `# Renewal Counter-Position: <vendor / contract>`
2. `## Summary of changes the renewal proposes` — diff against current contract on one page.
3. `## Real year-over-year change` — translated into the team's unit of comparison.
4. `## Usage and value baseline` — what the team uses, what value it gets.
5. `## BATNA` — alternative path if the renewal fails.
6. `## Negotiation levers, ranked` — six levers with reversibility scores.
7. `## Counter by lever`
   - Price: ask, reasoning, fallback ladder.
   - Term: ask, reasoning, fallback.
   - Commitment volume: ask, reasoning, fallback.
   - Auto-renewal and notice: ask, reasoning, fallback.
   - Exit and transition assistance: ask, reasoning, fallback.
   - SLA and credits: ask, reasoning, fallback.
   - Audit and sub-processors: ask, reasoning, fallback.
8. `## Walkaway threshold` — terms below which the renewal is not done.
9. `## Negotiation brief` — opening position, sequencing, the trades to make.

### Composition rules

- **The diff is the foundation; do not negotiate before the diff exists.**
- **Every ask has a reason and a fallback.** A position with no reason cannot be defended; a position with no fallback is a hostage situation.
- **Trade across levers, not within one.** A 2% price concession from the vendor traded for a notice-period reduction is a real trade; arguing the price down by an extra 1% in exchange for nothing is just attrition.
- **The walkaway threshold is set before the negotiation starts.** It is the team's protection against the gravitational pull of the deal.
- **The negotiator is not the sponsor.** The person on the call is one rung below the person who can sign. This keeps an escalation lever in reserve. If the team's CIO is on the renewal call, there is no escalation move left.
- **Document concessions and counter-concessions in writing as the negotiation moves.** A renewal that improves over four conversations and then "ends up where the vendor started" usually got there because nobody tracked the concessions in writing.

## Inputs

- **Renewal proposal (required, text).** What the vendor has put on the table — every term, not just price.
- **Current contract (optional, text).** Material terms of what is being replaced. Without this, the diff is incomplete; with it, the counter is precise.
- **Usage and value (optional, text).** Actual consumption and concrete value. Strong renewals are won on usage data the vendor did not expect the team to bring.
- **BATNA options (optional, text).** Alternatives the team has if the renewal fails. The skill operates with or without; with a documented BATNA, the counter is more confident.

## Outputs

A counter-position document, a separate explicit walkaway-threshold statement, and a one-page negotiator's brief. The brief is the artifact the person on the call uses; the counter-position is the full reasoning for internal alignment; the walkaway threshold is the team's pre-commitment against drift.

## Examples

### Worked example: marketing automation tool renewal

**Input renewal proposal:** "Vendor proposes 3-year renewal at $180k/year (current is $145k/year), with auto-renewal at year 3 unless 90-day notice; new 'AI features module' bundled at no extra charge year 1 then $40k/year years 2–3; SLA 99.9% with service-credit-only remedy."

**Input current contract:** "$145k/year, 1-year term expiring in 75 days, auto-renews unless 60-day notice given (notice window closes in 15 days). Contract has no transition-assistance clause. SLA 99.5% with credits. No documented audit right."

**Input usage and value:** "Current commit 50 seats; active users in last 90 days: 31. Three modules paid for; only two are used. Tool drives our nurture program — measurable lift in qualified leads by ~12% versus last year's manual sequence."

**Input BATNA options:** "Competitor we evaluated 18 months ago at lower price-per-seat; could pilot in 6 weeks, migrate in 12. Downgrade option: cut to 30 seats and live with reduced functionality; saves ~$50k. Walk away: revert to manual sequencing; loses the 12% lift."

**Expected output (excerpted):**

> # Renewal Counter-Position: Marketing Automation Tool
>
> ## Summary of changes the renewal proposes
>
> | Term | Current | Proposed | Change |
> |---|---|---|---|
> | Price | $145k/yr | $180k/yr | +$35k (+24%) |
> | Term | 1 year | 3 years | +2 years |
> | Modules | 3 paid | 3 + AI Module bundled yr1 then $40k yrs 2–3 | +$80k embedded |
> | Auto-renewal notice | 60 days | 90 days | Worse for us |
> | SLA | 99.5% credits | 99.9% credits | Slightly tighter, still credits-only |
> | Transition assistance | None | None | Unchanged (still missing) |
>
> True ask: $180k year 1, $220k years 2–3 (with the AI module bill-on activated). Three-year value $620k versus prior three-year run-rate of $435k. **Real increase: 43% over three years**, not 24%.
>
> ## Real year-over-year change in our unit
>
> Per active user (90-day-active basis): current $145k / 31 active = $4,677/active-user/yr. Proposed year 1: $180k / 31 = $5,806 (+24%). Proposed years 2–3 with AI module: $220k / 31 = $7,097 (+52%).
>
> Per paid seat: current $2,900/seat. Proposed year 1: $3,600/seat (+24%). Years 2–3: $4,400/seat (+52%).
>
> ## Usage and value baseline
>
> - 50 seats committed, 31 active in the last 90 days. 19 paid-and-unused.
> - Two of three paid modules in regular use. The "advanced reporting" module has not been opened by an admin in 6 months.
> - Documented value: 12% lift in qualified leads year-over-year. Estimated incremental revenue contribution: $X. Walking away is not free; reverting to manual sequencing loses the lift.
>
> ## BATNA
>
> Competitor with prior evaluation at $95–110k for 35 seats. Migration estimated 12 weeks, ~250 internal hours of marketing-ops time at our loaded rate $X. Net migration cost ~$30k. Migration is credible and within the renewal-decision timeframe. Downgrade option (30 seats, two modules) is a soft BATNA that the vendor will recognize as easy for us.
>
> ## Negotiation levers, ranked
>
> | Lever | Reversibility | Priority |
> |---|---|---|
> | Auto-renewal notice | Very low | 1 (must fix) |
> | Transition assistance | Near zero | 2 (must add) |
> | Term length | Low | 3 (must shorten) |
> | Commitment volume | Low | 4 (right-size to active + 25%) |
> | SLA structure | Low | 5 (add material-breach termination) |
> | Price | Medium | 6 (last, after the others) |
>
> ## Counter by lever
>
> **Price.** Ask: $130k/year for 1 year, reflecting 39 seats (active + 25% growth allowance), all current modules included, AI module declined for now. Reasoning: 19 unused seats over the last year; AI module untested for our workflow; competitor at $95–110k for similar shape. Fallback ladder: $135k flat → $140k flat → $145k flat (current price) → walk to the BATNA.
>
> **Term.** Ask: 1-year renewal. Trade up to 2 years if price drops to $128k/year and is rate-locked. Decline 3 years.
>
> **Commitment volume.** Ask: 39-seat commit (active + 25% headroom), additional seats at $3,300/seat with stated tier breakpoint. Reasoning: documented active-user count; we are not paying for 19 ghost seats.
>
> **Auto-renewal and notice.** Ask: remove auto-renewal entirely; renewal is opt-in by both sides at least 60 days before expiry. Fallback: keep auto-renewal but vendor provides written notice 90 days before the renewal date with the proposed terms, and our termination notice window is 30 days, not 90.
>
> **Exit and transition assistance.** Ask: add a clause providing 90 days of transition assistance at no incremental cost, including (a) data export of all contacts, segments, and engagement history in CSV plus documented schema, (b) up to 40 hours of named-contact time, (c) read-only access for an additional 30 days after termination for verification. Reasoning: standard in mature vendor contracts; not a hard ask. The vendor's negotiator may resist; the customer-success owner usually agrees. Escalate to a director if blocked.
>
> **SLA and credits.** Ask: keep 99.9% target; add a material-breach termination right — if the vendor misses 99.9% for two consecutive calendar months, we have a 30-day termination right without early-termination fees. Credits remain as proposed.
>
> **Audit and sub-processors.** Ask: add an annual audit right exercisable on 30 days notice (cost-shift on material finding). Add 30-day notice on new sub-processors with right to object.
>
> ## Walkaway threshold
>
> The renewal does not happen if any of the following are not achieved by [signature deadline two weeks before current contract expiry]:
> - Total year-1 cost ≤ $145k (no increase versus current).
> - Term length ≤ 2 years.
> - Auto-renewal removed or notice window reduced to 30 days.
> - Transition-assistance clause added with at least 60 days of assistance.
> - AI module is opt-in, not bundled-then-billed.
>
> Below these terms, we exit and execute the BATNA. Walkaway is signed off by the head of marketing today, before the negotiation starts.
>
> ## Negotiation brief
>
> **Negotiator on call:** Marketing-ops lead. Escalation point (held in reserve): head of marketing.
>
> **Opening move:** open with the diff page and the real 43%-over-three-years number; ask the vendor to explain the increase. Do not table the counter-price yet.
>
> **Sequence:**
> 1. Establish the diff; align on the real economic ask.
> 2. Table the term shortening (1 year). Establish that we are renewing short.
> 3. Table the seat right-sizing (39 not 50). Provide the usage data.
> 4. Table the auto-renewal change.
> 5. Table transition assistance. This is the lever most likely to get a yes early.
> 6. Table SLA termination right.
> 7. Table audit and sub-processor terms.
> 8. **Last:** table the price counter, anchored to the seat right-sizing.
>
> **Trades to make:** willing to go to a 2-year term if the year-1 price hits $128k and is rate-locked. Willing to keep auto-renewal if notice window drops to 30 days and vendor provides written renewal terms 90 days ahead.
>
> **Signals to escalate:** if the vendor refuses the transition-assistance clause outright, escalate immediately — that is a sign of where the vendor sees this relationship going. If the vendor refuses to right-size seats, the negotiation is in trouble; surface the BATNA explicitly.

## Limitations

- The skill produces a commercial position; legal review of contract language is still required. The team's lawyer translates the negotiated terms into clauses; the skill does not write the redlines.
- A renewal counter only works if there is time for it. The most common failure is that the team starts the renewal conversation two weeks before expiry, the auto-renewal notice window has closed, and the vendor knows the team is trapped. Start renewal preparation 90 days before expiry; for multi-year contracts, start 120 days before.
- The skill cannot reliably model the vendor's internal negotiation room. Each vendor's salespeople have different discount authority and different motivation (end of quarter, fiscal year, retention bonus structure). The team learns this over time with a specific vendor; the first renewal is partly information-gathering for the second.
- Some vendors are genuinely take-it-or-leave-it at smaller spend tiers. If the team is not the vendor's largest customer in their tier and the vendor has automated the renewal motion, the negotiation room may be narrow. In that case, the team's leverage is the BATNA — and the skill's value is in being honest about that.
- The skill assumes the team is comfortable walking away. Walkaway threats with no follow-through train the vendor that the threats are theatrical. The walkaway threshold should only be set at a level the team is willing to act on.
- Renewal negotiation is partly relationship management. A vendor account manager who is going to be the team's escalation contact during the next year of incidents has more value than a 2% price concession. The skill optimizes the deal; the team optimizes the relationship.

## Sources reviewed

- https://github.com/mgifford/open-source-contracting
- https://github.com/open-agreements/open-agreements
- https://github.com/ankane/awesome-legal
- https://github.com/accordproject/template-archive
- https://github.com/tractorjuice/arc-kit
- https://github.com/delschlangen/vendor-risk-rubric
- https://github.com/SalesforceLabs/ProposalForce
