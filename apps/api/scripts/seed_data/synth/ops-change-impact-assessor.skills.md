---
id: skillsgit-curated/ops-change-impact-assessor
version: 1.0.0
name: Change Impact Assessor
description: Assesses the impact of a proposed change across affected audiences — what changes for whom, friction sources, training needs, support burden, dependencies, and a severity-by-likelihood risk register that surfaces the unspoken cost of the change.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: operations
tags: [niche:change-management, impact-analysis, risk-assessment, stakeholders, readiness, operations, planning]
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
  - impact assessment
  - change impact
  - readiness review
  - stakeholder analysis
  - risk register
  - blast radius
  - who is affected
  - friction analysis
  - training needs
  - support burden
  - change readiness
  - dependency map
example_invocations:
  - "Run an impact assessment on the proposed move from quarterly to monthly performance reviews."
  - "We're consolidating three regional pricing models into one. Who is impacted and how badly?"
  - "Assess the impact of deprecating the v1 public API across our customer base."
inputs:
  - name: proposed_change
    type: text
    required: true
    description: What is being proposed — the system, process, behavior, or policy that would change, and the current state it replaces.
  - name: known_audiences
    type: text
    required: false
    description: Audiences the proposer already knows are affected, with any context they have on each. The skill will probe for omitted audiences in addition to assessing the named ones.
  - name: change_drivers
    type: text
    required: false
    description: Why the change is being proposed — the goal, the forcing function, the deadline. Drivers shape what trade-offs are acceptable.
  - name: existing_pain
    type: text
    required: false
    description: Pain in the status quo that the change is meant to relieve. Useful for identifying audiences who will welcome the change and the ones whose pain is unrelated.
outputs:
  - name: impact_assessment
    type: markdown
    description: A structured assessment with audience-by-audience impact, friction sources, training and support burden, dependency map, and a severity-by-likelihood risk register with mitigations.
  - name: readiness_summary
    type: markdown
    description: A one-page executive-readable summary identifying the highest-friction audiences, the top three risks, and the single most important question the sponsor should answer before approving the change.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill before committing to a change whose surface area extends beyond a single team's workflow. The skill answers four questions the sponsor of a change usually wants but rarely gets in writing: who is affected, what changes for each of them, how hard is it for them to absorb the change, and what could go wrong. The output is the input to a rollout plan and the evidence base for a go/no-go decision.

The skill is opinionated about three things. First: **audiences are discovered, not assumed**. The named audiences the proposer brings are the starting point; the skill systematically probes for omitted audiences, including the ones whose pain is silent (downstream consumers, support and audit, the system of record that someone else integrates against). Second: **friction is decomposed** — into behavior change, system change, identity change, and incentive change — because mitigations differ. A new system can be trained for; an incentive flip cannot be trained for and must be redesigned. Third: **the risk register uses severity × likelihood with named mitigations and named owners**. A risk with no mitigation or no owner is a risk that has been listed, not managed.

Do not use this skill for changes the sponsor already understands and the team has already absorbed (use a rollout plan or a deploy checklist). Use it for changes where someone has said "let's just do it" and the affected groups have not yet been polled or counted.

## How to apply

The skill works in nine moves. Together they produce the audience map, the friction analysis, the dependency map, and the risk register.

1. **Restate the change neutrally.** Strip the proposer's framing. "We are consolidating three regional pricing models into a single global model effective January 1." Not "we are simplifying pricing for our customers." The neutral statement is what audiences will encounter. The proposer's framing is one input, not the truth.

2. **Identify direct audiences — the people whose work or behavior changes.** Direct audiences are those who must do something differently after the change. Be granular: "sales" is not an audience, "enterprise AEs in EMEA" and "SDRs in NAM" are. For each direct audience, capture rough size, primary system or process they use today, and the smallest unit of change they will encounter.

3. **Probe for indirect audiences — the people whose inputs or outputs change.** Indirect audiences do not change behavior, but their context does. Finance consumes a different data shape; legal reads a different contract; customer support receives a different question mix; integrators read a different API. Indirect audiences are systematically under-counted because they are not in the room when the change is conceived. The skill must prompt for: who consumes the affected system's output? who depends on the affected process's outputs? who has documented the current state in any way that will go stale?

4. **For each audience, name the friction in four categories.** (a) **Behavior change**: what they do differently day-to-day. (b) **System change**: what tool, screen, or step replaces another. (c) **Identity change**: what does this say about who they are or how they are evaluated (e.g., "I used to be the regional pricing authority"). (d) **Incentive change**: how their compensation, recognition, or accountability shifts. Friction in different categories needs different mitigations; lumping them produces a single "needs training" recommendation that doesn't address the actual obstacle.

5. **Score friction and absorb-capacity per audience.** Friction is a 1–5 estimate of total burden across the four categories. Absorb-capacity is a 1–5 estimate of the audience's bandwidth and willingness to take it on — accounting for what else is on their plate, how recently they absorbed prior changes, and whether they perceive the change as in their interest. Net difficulty is friction × (6 − absorb-capacity); audiences with high net difficulty are where the rollout will live or die.

6. **Estimate training, support, and material needs per audience.** Training: what does the audience need to learn, in what format, delivered by whom? Support: what is the elevated support burden during transition, who absorbs it, and how is it staffed? Materials: what reference artifacts (docs, FAQs, demos, cheat sheets) must exist before the audience encounters the change? The estimate is a rough size (small/medium/large effort) plus an owner; precision comes during rollout planning.

7. **Build the dependency map.** Two kinds of dependencies: upstream (what must be true or completed before the change can land — system readiness, data migrations, contract amendments, training delivered) and downstream (what is affected by the change in a way that will surface later — quarterly reports, audit trail, integrations, third-party SLAs). Each dependency has an owner and a known state (in flight, blocked, unknown). The dependency map is where rollout dates die; surfacing them in the assessment prevents that.

8. **Compose the risk register: severity × likelihood × mitigation × owner.** Risks are observable failure modes, not vague concerns. "Sales adoption is slow" is not a risk; "AE adoption below 60% by week 6 due to inability to enter complex multi-product opps in NewCRM" is. For each risk, score severity (1–5: cosmetic to existential) and likelihood (1–5: rare to expected). The product gives a heat ranking. Each risk has a stated mitigation (what we do in advance to reduce severity or likelihood) and a named owner. Risks without mitigations and owners are surfaced explicitly as **unmitigated** so the sponsor sees them.

9. **Identify the single highest-leverage question for the sponsor.** Every assessment surfaces one question the sponsor must answer before committing. Examples: "are we willing to defer this by a quarter to land it after Q4 close, when audience absorb-capacity will be 2× higher?" "is it acceptable to lose 5% of the smallest tier of customers in exchange for the simplified pricing model?" "do we have an executive willing to defend the change to the affected business-unit leader who will object?" The question is what stops the change from being a decision made by inertia and surfaces the real trade-off.

### Standard impact assessment layout

The output document uses these section headers in this order:

1. `# Change Impact Assessment: <change name>`
2. `## Change (neutral statement)` — one paragraph, no framing.
3. `## Drivers and trade-offs` — why is this happening, what is non-negotiable.
4. `## Audience map` — direct and indirect audiences, with counts.
5. `## Audience friction analysis` — per audience, the four-category friction breakdown.
6. `## Friction × absorb-capacity scoring` — table with net difficulty ranking.
7. `## Training, support, and materials` — per audience, what is needed.
8. `## Dependency map` — upstream and downstream, with owners and states.
9. `## Risk register` — severity × likelihood × mitigation × owner; unmitigated risks called out.
10. `## Quiet failure modes` — failure modes that won't be visible until after rollout, with proposed early-detection signals.
11. `## Question for the sponsor` — the single decision the sponsor must make before approving.
12. `## Recommendation` — proceed, proceed with caveats, defer with conditions, or decline.

### Composition rules

- **Audiences are granular.** "Engineering" is not an audience; "platform engineers who own services X and Y" is.
- **Friction is decomposed.** Always score all four categories, even if one is zero — surfacing zeros confirms they were considered.
- **Risks are observable.** A risk statement contains a measurable threshold and a plausible mechanism.
- **Every risk has a mitigation and an owner.** If none, mark the risk **unmitigated** and surface it in the recommendation.
- **The sponsor question is one sentence.** Multiple questions in this slot dilute the decision.
- **Recommendation is one of four states.** Proceed, proceed with caveats, defer with conditions, decline. Hedged recommendations get rewritten until they pick a state.

## Inputs

- **Proposed change (required, text).** What is being proposed and the state it replaces.
- **Known audiences (optional, text).** The proposer's audience hypothesis, to be expanded.
- **Change drivers (optional, text).** The forcing function, deadline, or goal.
- **Existing pain (optional, text).** Status-quo pain the change is intended to relieve.

## Outputs

A full markdown impact assessment and a one-page executive-readable readiness summary.

## Examples

### Worked example: deprecating the v1 public API

**Proposed change:** "Deprecate v1 of the public API. v2 has been available for 14 months. v1 supports 30% of current public-API traffic, mostly from older integrations. We want to set the v1 sunset for 6 months out and remove it entirely 12 months out."

**Known audiences:** "External customers who integrate with v1. Our developer-relations team. Customer support, who will hear about it."

**Change drivers:** "v1 doubles our infrastructure cost in the public-API tier due to a different data model. It blocks the planned rate-limiting overhaul. The platform team wants this deprecated before the new product launches in Q3."

**Existing pain:** "Engineering carries the cost of maintaining two API surfaces. Several recent incidents touched v1-only code paths."

**Expected output (excerpted):**

> # Change Impact Assessment: deprecate v1 public API
>
> ## Change (neutral statement)
>
> v1 of the public API will be marked deprecated immediately, with sunset 6 months out (T+180) and removal 12 months out (T+365). Traffic on v1 will return a deprecation header through T+180 and a sunset response from T+180 to T+365. After T+365, v1 endpoints will return 410 Gone.
>
> ## Drivers and trade-offs
>
> Non-negotiable: v1 must be removed before Q3 platform launch (T+330). Acceptable: losing some long-tail integrators who do not migrate; absorbing migration support burden for 6–9 months. Not yet decided: whether enterprise customers with v1 dependencies get extended timeline contractually.
>
> ## Audience map
>
> **Direct audiences:**
> - External integrator developers on v1 (~430 unique tokens producing v1 traffic; ~120 distinct customer accounts).
> - Customers with custom SDKs wrapping v1 (subset of above; estimated ~30 accounts based on UA strings).
>
> **Indirect audiences:**
> - Customer support (will receive migration questions and "why is my integration broken" tickets post-sunset).
> - Sales — particularly account managers on the 30 affected enterprise accounts.
> - Developer relations (writes migration content, runs office hours).
> - Internal teams that use v1 for one-off integrations (audit, finance reports, partner team). Estimated 6 internal consumers based on internal token registry.
> - Compliance/legal — customer contracts may reference API behavior that the v1→v2 shape changes.
> - Status-page subscribers — deprecation/sunset events need to appear on the status page or comms calendar.
>
> ## Audience friction analysis (excerpted)
>
> **External integrator developers (v1 only):**
> - Behavior change: must rewrite integration against v2's different auth and resource model.
> - System change: v2's response shape is materially different in 3 endpoints.
> - Identity change: minimal — these are individual developers, not roles.
> - Incentive change: their company may not prioritize this work; they may carry it personally.
>
> **Enterprise customer account managers (sales):**
> - Behavior change: must proactively contact accounts; create migration tickets in their tracker.
> - System change: none directly.
> - Identity change: low.
> - Incentive change: medium — distracts from new-business motion; should be reflected in quota relief or recognition for migration assist.
>
> **Customer support:**
> - Behavior change: new ticket macros, escalation path for migration help, monitoring of v1-related ticket volume.
> - System change: minor — new tags in the ticketing system.
> - Identity change: low.
> - Incentive change: low — measured on resolution time; migration tickets are longer, so the team's standard metrics will degrade unless adjusted.
>
> ## Friction × absorb-capacity scoring
>
> | Audience | Friction (1-5) | Absorb-capacity (1-5) | Net difficulty | Rank |
> | --- | --- | --- | --- | --- |
> | Enterprise customers (v1-only, deep integration) | 5 | 2 | 20 | 1 |
> | External developers (v1, single integration) | 4 | 3 | 12 | 2 |
> | Account managers (sales) | 3 | 2 | 12 | 2 |
> | Customer support | 2 | 3 | 6 | 4 |
> | Internal v1 consumers | 3 | 3 | 9 | 3 |
>
> ## Training, support, and materials
>
> - **External developers**: published migration guide (large effort, devrel owner); side-by-side endpoint mapping reference (large, devrel); 4 office-hours sessions across timezones over the deprecation window (medium, devrel + platform).
> - **Account managers**: enablement deck with the 30-account list and per-account state, talking points, escalation path (medium, sales enablement owner).
> - **Customer support**: migration ticket macros, escalation path doc, internal FAQ (small, support ops owner).
> - **Internal v1 consumers**: direct outreach with 1:1 migration pairing (small, platform team owner).
>
> ## Dependency map
>
> **Upstream:**
> - v2 must support the 3 remaining v1-only fields by T+30. State: in flight, platform team owns, scheduled T+25.
> - Customer contracts review for any v1-behavior commitments. State: unknown, legal must scope.
> - Status-page deprecation/sunset events designed. State: not started, communications owner.
>
> **Downstream:**
> - Rate-limiting overhaul depends on v1 removal. State: queued for after T+365.
> - Q3 platform launch depends on v1 removal. State: scheduled T+330; cannot slip.
> - Quarterly partner reporting includes API-version distribution; the chart will change shape during deprecation.
>
> ## Risk register
>
> | # | Risk | Severity | Likelihood | Mitigation | Owner | Status |
> | --- | --- | --- | --- | --- | --- | --- |
> | 1 | Enterprise customer fails to migrate by T+180; v1 sunset creates customer-facing outage | 5 | 3 | Account-by-account migration plan in T+0 to T+60 window; per-account weekly status; CSM escalation criteria; option to grant 90-day contractual extension on case-by-case basis | VP Customer Success | mitigated |
> | 2 | Undiscovered v1 consumer breaks at sunset (an integration we did not know about) | 4 | 4 | Token-usage scan T-30 to identify all active v1 tokens; outreach to accounts with no migration activity logged; sunset response carries deprecation header for 30 days before 410 cutover | platform team lead | mitigated |
> | 3 | Customer support ticket volume spikes at T+180 and exceeds capacity | 3 | 3 | Pre-load support FAQ; cross-train two additional agents on v1 migration; spike-budget for contracted support hours during T+165 to T+200 | support ops manager | mitigated |
> | 4 | Migration guide is unclear in practice; integrators struggle silently | 4 | 3 | T+30 dogfood pass with three friendly integrator partners; track guide visits vs. migrations to detect dropoff | devrel manager | mitigated |
> | 5 | Internal compliance discovers a contract commits to v1 indefinitely | 5 | 2 | Legal contract review in T+0 to T+30 window; if found, scope renegotiation or per-customer exemption | general counsel | mitigated |
> | 6 | Engineering team that owns v1 has key person dependency; if that engineer is unavailable during sunset, no one knows the system | 4 | 2 | Pair-programming session for the deprecation work; documentation pass to fix bus-factor on v1 internals | platform team lead | partially mitigated |
> | 7 | Q3 platform launch slips for unrelated reasons, leaving v1 removal date dangling | 3 | 3 | Decouple v1 removal date from platform-launch date; v1 removal is on its own T+365 schedule regardless | platform PM | **unmitigated as stated; needs decision** |
>
> ## Quiet failure modes
>
> - Internal token scan misses tokens used by external partners we forgot we provisioned (legacy integrations through old partner-management process). Early-detection signal: residual v1 traffic at T+150 still attributable to unknown account.
> - Sales account managers do migration outreach but customers respond agreeably without actually doing the work; T+150 shows no v2 traffic from the account. Early-detection signal: weekly per-account v2 traffic dashboard, with red highlight for any of the 30 enterprise accounts at 0 v2 calls past T+90.
> - Documentation looks complete but is missing a corner case; integrators silently roll their own. Early-detection signal: spike in 4xx error rate on a specific v2 endpoint from migrating integrators.
>
> ## Question for the sponsor
>
> Are we willing to grant per-customer extensions (to T+450) for any of the top-10 v1-revenue customers that have not migrated by T+150, accepting the platform-team cost of carrying v1 longer and the precedent that creates?
>
> ## Recommendation
>
> Proceed with caveats. Caveats: (a) close the unmitigated risk #7 by decoupling the v1 removal date from the Q3 platform-launch date; (b) the sponsor must answer the per-customer-extension question above before T+0 announcement; (c) commit account-by-account enterprise migration plan as a precondition for the public deprecation announcement.

## Limitations

- The skill identifies audiences from inputs and patterns. It cannot discover audiences whose existence is unknown to the proposer and not implied by the change description; the dependency map prompts catch many but not all (e.g., a regulator that audits an undocumented data flow).
- Friction and absorb-capacity scores are judgment-based. The skill produces defensible scores from the inputs; teams should treat them as the basis for conversation with the affected audience, not as measurements.
- The skill does not size the change; it sizes the impact. A change that looks small in scope can produce a large assessment if the audience footprint is broad, and a change that looks large in scope can produce a small assessment if it changes nothing observable.
- The risk register is a snapshot. Risks evolve; the assessment should be re-run when major inputs change (audience size, dependency state, drivers, mitigations).
- The skill is opinionated about decomposing friction into behavior/system/identity/incentive categories. Some changes do not have all four. The skill names zero categories where they don't apply rather than skipping the framework.
- The sponsor question is the highest-leverage output and the easiest to soften under pressure. The skill should resist hedging; ambiguous sponsor questions are tells that the assessment hasn't yet found the real trade-off.

## Sources reviewed

- https://github.com/argoproj/argo-rollouts
- https://github.com/fluxcd/flagger
- https://github.com/Unleash/unleash
- https://github.com/flagsmith/flagsmith
- https://github.com/reactjs/rfcs
- https://github.com/concourse/rfcs
- https://github.com/vintasoftware/production-launch-checklist
