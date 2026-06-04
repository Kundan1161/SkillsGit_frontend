---
id: skillsgit-curated/ops-rollout-plan-author
version: 1.0.0
name: Rollout Plan Author
description: Produces a phased rollout plan for a change — audience sequencing, comms cadence, training, enablement, success and abort criteria, and rollback — sized to the change's risk and blast radius.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: operations
tags: [niche:change-management, rollout, deployment, release-management, phased-launch, enablement, operations]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - rollout plan
  - phased rollout
  - launch plan
  - release plan
  - deployment plan
  - change rollout
  - go-live plan
  - cutover plan
  - staged rollout
  - canary rollout
  - progressive rollout
  - readiness review
example_invocations:
  - "Draft a rollout plan for replacing our expense tool across the company over the next quarter."
  - "We're shipping a new pricing model to existing customers. Give me a phased rollout plan."
  - "Plan a rollout for our new on-call rotation tool that 200 engineers will be affected by."
inputs:
  - name: change_description
    type: text
    required: true
    description: Plain-language description of what is changing — the system, process, or behavior. Include who is making the change and what problem it is solving.
  - name: affected_audiences
    type: text
    required: false
    description: Groups affected by the change — internal teams, customer segments, partner systems. Include rough counts where known and any segments with elevated sensitivity (regulated, VIP, executive sponsors of the status quo).
  - name: risk_level
    type: choice
    required: false
    description: Self-assessed risk band that guides phasing aggressiveness.
    choices: [low, medium, high, irreversible]
  - name: hard_constraints
    type: text
    required: false
    description: Non-negotiable dates, dependencies, regulatory deadlines, or freeze windows the plan must respect.
  - name: success_signals
    type: text
    required: false
    description: How the team will know the rollout is healthy — adoption metrics, error rates, support volume, NPS shifts, business KPIs.
outputs:
  - name: rollout_plan
    type: markdown
    description: A phased rollout plan with audience sequencing, per-phase entry/exit criteria, comms cadence, enablement touchpoints, success and abort thresholds, and a rollback sketch.
  - name: phase_gate_checklist
    type: markdown
    description: A short standalone checklist for each phase gate so the rollout owner can review readiness without re-reading the whole plan.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a change is large enough that "ship it on Tuesday" is not a plan. The trigger is any combination of: more than one audience to migrate; behavior the audience has to learn (not just code that runs differently); a window where old and new must coexist; a meaningful chance of needing to back out under time pressure; or visibility that means a stumble becomes a story. The output is a phased rollout plan — who gets the change in what order, what comms and enablement wrap each phase, what evidence opens the next phase, and what evidence aborts the rollout entirely.

The skill is opinionated about two things. First: rollout phases are defined by **exit criteria**, not dates. A phase ends when the evidence that gates the next phase is in hand. Calendar dates are predictions, not commitments; dates that masquerade as commitments cause organizations to either ship under-baked or sit on baked changes for political reasons. Second: every rollout plan answers the abort question — at what observable threshold do we stop, hold, or reverse? Skipping that question is the single most common failure mode of rollouts, technical and organizational alike.

Do not use this skill for tiny, reversible technical changes that one engineer can ship in an afternoon (a runbook or a deploy checklist is sufficient). Do not use it for emergencies (use incident response). Use it when the change has audiences who must adapt, where the cost of getting it wrong includes confused users, sales motions interrupted, support volume spikes, or executive escalation.

## How to apply

The skill builds the plan in eleven moves. Each move produces a section of the final document; the moves are ordered because earlier outputs feed later ones (audiences feed comms cadence, success signals feed abort criteria, etc.).

1. **Restate the change as a single observable sentence.** Strip marketing and motivation; what changes for someone, after the rollout, that wasn't true before. "Sales reps will enter opportunities in NewCRM instead of OldCRM, with OldCRM read-only and decommissioned 90 days after cutover." That sentence is the contract. Every phase, every comm, every metric ultimately serves it. If the sentence cannot be written without ambiguity, the rollout is not ready to plan and the skill should say so plainly.

2. **Inventory the affected audiences and rank them by friction.** Friction is the sum of three things: how much behavior the audience has to change; how visible they are if it breaks; and how much they care about the status quo. The output is a friction-ordered list — usually three to seven audience segments. Low-friction segments go early (they tolerate rough edges and provide signal cheaply). High-friction segments go late (they need polished enablement and absorbed lessons). Order matters; "everybody on day one" is the rollout antipattern that produces the most rework.

3. **Decide the phase shape.** Most rollouts fall into one of four shapes: (a) **pilot → expansion → general availability**, used when the change is novel and learnings are expected to be expensive; (b) **canary → percentage ramp → 100%**, used when the change is technical and traffic-based shifting is feasible; (c) **cohort waves**, used when audiences naturally segment (regions, business units, customer tiers); (d) **dual-run → cutover**, used when the old and new must coexist for a known window before a hard switch. Pick one shape and name it; mixing shapes by accident produces plans that look thorough but cannot be executed because nobody knows when one mode hands off to the next.

4. **Define entry and exit criteria per phase.** Entry criteria answer: what must be true to start this phase? (Pilot cohort identified, training delivered, support team briefed, telemetry instrumented.) Exit criteria answer: what evidence will we accept that the phase succeeded enough to advance? (Adoption rate above X, error rate below Y, support ticket volume below Z, no severity-1 escalations for N business days.) Every criterion is observable and timeboxed. A criterion like "users feel comfortable with the change" is not a criterion; rewrite it as "the post-pilot survey returns ≥ 4/5 on the 'I can do my job in NewCRM' question from at least 80% of pilot users."

5. **Build the comms cadence as a calendar against the phases.** For each phase there are at least three communication beats: a **pre-phase announcement** (audience knows the change is coming, when, what they have to do), an **in-phase reminder or office-hours touch** (audience knows where to get help and what behavior the rollout owner is observing), and a **post-phase summary** (audience hears what was learned and whether the rollout proceeds). Comms are tied to phases, not to weeks; if a phase slips, the comms slip with it. The cadence document names the sender (which leader, which team), the channel (email, slack, in-app, all-hands), and the action the audience is expected to take after reading.

6. **Plan enablement per audience, not per phase.** Each affected audience has its own enablement profile: training format (self-serve doc, recorded walkthrough, live session), support resource (dedicated slack channel, embedded coach, office hours), and reference material (cheat sheet, FAQ, demo environment). Build the matrix as audience × enablement-type. The matrix exposes the audiences who have a lot of friction and no support — those are the rollout's quiet failure points. Add enablement before scheduling them into a phase; do not schedule them and hope.

7. **Specify success metrics with a lead and a lag.** Lead metrics tell you the rollout is working before the business outcome is visible: login rate to the new tool, ratio of tasks completed in the new system vs. the old, time-to-first-meaningful-action for a new user. Lag metrics tell you whether the change produced its intended business outcome: cycle time, error rate, customer NPS, revenue impact. Lead metrics drive phase decisions in days and weeks; lag metrics are the post-rollout retrospective evidence. A plan with only lag metrics flies blind through the rollout window.

8. **Write the abort criteria in advance and name the decider.** Abort criteria are the thresholds that flip the rollout from "proceed" to "hold" or "reverse." Examples: support ticket volume exceeds 3× the pre-rollout baseline for two consecutive days; severity-1 incident directly traceable to the change; pilot survey returns < 3/5 on the core job question. For each criterion, name the person authorized to call abort and the comms that follow. Abort criteria written in advance are the single highest-leverage element of a rollout plan; abort criteria invented in the moment under stress are usually wrong or arrive too late.

9. **Sketch the rollback path appropriate to the change's reversibility.** For traffic-routable technical changes, rollback is mechanical — flip the percentage. For data-model changes, rollback is partial and depends on whether old writes can be replayed. For behavior changes (people doing their jobs differently), full rollback is rarely possible; what is possible is suspending the requirement and reverting the system, while accepting that audiences have already adapted somewhat. State honestly what rollback can and cannot recover. A rollout plan that claims "fully reversible" for a change that is not reversible is worse than no plan.

10. **Identify dependencies and freeze windows.** What other teams' work must land before each phase? What organizational dates must the plan respect (year-end close, peak-traffic event, regulatory filing, executive offsite)? What system freeze windows constrain the change-introduction date? Surface these explicitly; the most common cause of rollouts slipping is an undocumented dependency on another team's deliverable that quietly drifts.

11. **Define the post-rollout cleanup and decommissioning steps.** Most plans end at "100% live." Real rollouts have a long tail: old system decommissioning, training material archival, role and permission revocation, audit and compliance closeout, retrospective. Name the activities, the dates relative to the GA milestone (T+30, T+60, T+90), and the owners. A rollout that has not been retired produces ongoing confusion and zombie systems that re-emerge a year later.

### Standard rollout plan layout

The output document uses these section headers in this order:

1. `# Rollout Plan: <change name>`
2. `## What is changing` — the single observable sentence and a one-paragraph context.
3. `## Audiences and friction ranking` — table of audience, count, friction score (1-5), notes.
4. `## Phase shape` — named shape (pilot/expansion/GA, canary/ramp, cohort waves, dual-run/cutover) with rationale.
5. `## Phases` — for each phase: name, target audience, entry criteria, activities, exit criteria, planned duration (and explicit note that duration is an estimate, not a commitment).
6. `## Communications cadence` — schedule keyed to phases, not dates.
7. `## Enablement matrix` — audience × enablement type.
8. `## Success metrics` — lead and lag, with thresholds.
9. `## Abort criteria` — observable thresholds and named decider.
10. `## Rollback plan` — what is and is not recoverable, by what mechanism.
11. `## Dependencies and constraints` — upstream teams, freeze windows, regulatory dates.
12. `## Post-rollout cleanup` — decommissioning, retrospective, ownership transitions.
13. `## Roles` — sponsor, rollout owner, comms lead, enablement lead, technical owner, abort decider.

### Composition rules

- **Phases are defined by exit criteria, not by dates.** Dates may appear as estimates but are never the gating condition.
- **Audiences ordered by friction, low to high.** Easy audiences first to develop signal cheaply.
- **Every criterion is observable.** No "feels right" criteria. If a criterion cannot be checked by someone other than the author, rewrite it.
- **Every metric has a threshold.** "Watch error rate" is not a metric; "error rate < 0.5% over a 24-hour window" is.
- **Comms are tied to phase events, not to weeks.** If the phase slips, the comm slips with it.
- **Abort criteria precede go-live.** Writing abort criteria during a rollout-in-trouble is usually too late.
- **Reversibility is stated, not assumed.** Be explicit when a change is partially or fully irreversible.

## Inputs

- **Change description (required, text).** What is changing, who is making it, and what problem it is solving.
- **Affected audiences (optional, text).** Groups, rough counts, and segments with elevated sensitivity.
- **Risk level (optional, choice).** Banding that influences phasing aggressiveness.
- **Hard constraints (optional, text).** Dates, dependencies, freeze windows that the plan must respect.
- **Success signals (optional, text).** How the team will know the rollout is healthy — adoption, error rate, support volume, business KPIs.

## Outputs

A complete markdown rollout plan and a standalone phase-gate checklist for the rollout owner.

## Examples

### Worked example: replacing the company CRM

**Change description:** "Sales operations is moving the company from OldCRM to NewCRM. Reason: OldCRM contract is up for renewal at 3× current cost, NewCRM is materially cheaper and integrates with the new revenue stack. About 240 sales and CS users use OldCRM daily. The change happens this quarter."

**Affected audiences:** "AEs (160), CSMs (50), SDRs (30), Sales Ops (8), Finance (consume CRM reports, 15). VIP segment: enterprise AEs who own the largest accounts — they will be the loudest if anything is wrong."

**Risk level:** high

**Hard constraints:** "Cannot have a dual-run window during board-meeting prep weeks. Quarter-end pipeline review must run from a single source of truth. Finance close depends on CRM reports on the 5th of each month."

**Success signals:** "Adoption (% of new opps entered in NewCRM), data parity (NewCRM vs. OldCRM pipeline coverage match), CSAT-equivalent (sales team survey), and the lag metric — quarter close happens on schedule with NewCRM as the source."

**Expected output (excerpted):**

> # Rollout Plan: NewCRM migration
>
> ## What is changing
>
> Sales, CS, and Sales Ops will move from OldCRM to NewCRM as the system of record for opportunities, accounts, and activities. OldCRM becomes read-only at cutover and is decommissioned 60 days later. Finance reports re-source from NewCRM.
>
> ## Audiences and friction ranking
>
> | Audience | Count | Friction (1-5) | Notes |
> | --- | --- | --- | --- |
> | Sales Ops | 8 | 2 | Power users, will be implementation partners |
> | SDRs | 30 | 2 | Limited surface area in CRM; mostly contact creation |
> | CSMs | 50 | 3 | Multiple custom workflows; some 5-year veterans of OldCRM |
> | AEs (non-enterprise) | 130 | 4 | Daily heavy use; tied to compensation reporting |
> | Enterprise AEs | 30 | 5 | High-touch, low-tolerance, executive visibility |
> | Finance | 15 | 3 | Downstream consumers; require report parity |
>
> ## Phase shape
>
> Cohort waves with a pilot leading. Pilot establishes signal cheaply, cohort waves let high-friction enterprise AEs go last after lessons land.
>
> ## Phases
>
> ### Phase 0 — Foundation (estimated 3 weeks)
>
> Entry criteria: NewCRM tenant provisioned; OldCRM → NewCRM data sync running with < 1% deltas; admin training delivered to Sales Ops.
> Activities: data sync stabilization, role/permission matrix in NewCRM, dashboard parity build, integration smoke tests with finance reports.
> Exit criteria: 14 consecutive days of < 0.5% nightly sync deltas; finance report parity validated for the most recent closed month; Sales Ops admins certified on NewCRM.
>
> ### Phase 1 — Pilot (estimated 2 weeks)
>
> Entry criteria: Phase 0 exited; pilot cohort selected (Sales Ops + 8 self-volunteer AEs across territories, 2 SDRs); pilot enablement delivered.
> Activities: pilot users dual-enter for first week, NewCRM-only for second week; daily office hours; pilot tracker for issues.
> Exit criteria: pilot users complete the pilot survey at ≥ 4/5 on "I can run my standard week in NewCRM"; no severity-1 issues open; data parity at < 1% deltas during NewCRM-only week.
>
> ### Phase 2 — SDR and CSM wave (estimated 2 weeks)
>
> Entry criteria: Phase 1 exited; SDR and CSM enablement delivered; OldCRM and NewCRM dual-write configured for these cohorts.
> Activities: dual-write window of 5 business days, then NewCRM-only; cohort slack channel open; one live training session per role.
> Exit criteria: 90% of cohort users have entered at least one opp/activity in NewCRM during the NewCRM-only window; cohort survey ≥ 4/5; support ticket volume returns to within 1.5× baseline within 5 business days of cutover.
>
> ### Phase 3 — Non-enterprise AE wave (estimated 3 weeks)
>
> Entry criteria: Phase 2 exited; comp-plan reporting validated in NewCRM; AE-specific enablement delivered.
> Activities: as Phase 2, with comp-plan dry-run during the dual-write window.
> Exit criteria: 95% NewCRM adoption among the cohort; comp report reconciliation against OldCRM agrees within 0.5% for the dry-run period.
>
> ### Phase 4 — Enterprise AE wave (estimated 3 weeks)
>
> Entry criteria: Phase 3 exited; enterprise AE 1:1 enablement scheduled; account-team migration validated for largest 30 accounts.
> Activities: AE-by-AE migration with a Sales Ops partner shadowing for the first opportunity; daily executive update.
> Exit criteria: all 30 enterprise AEs have completed at least one full opportunity workflow in NewCRM; no escalations to VP Sales open.
>
> ### Phase 5 — Cutover and decommission (estimated 60 days post-Phase-4)
>
> Activities: OldCRM moves to read-only; OldCRM decommission at T+60; archival of legacy reports; retrospective at T+30.
>
> ## Communications cadence
>
> Per phase: T-7 days pre-announcement from VP Sales; T-1 day reminder; daily slack update during phase; office-hours twice weekly; post-phase summary from the rollout owner. All comms include the next phase's audience expectations.
>
> ## Enablement matrix (excerpted)
>
> | Audience | Self-serve | Live | Embedded | Office hours |
> | --- | --- | --- | --- | --- |
> | Sales Ops | yes | yes (admin) | n/a | n/a (they run it) |
> | SDRs | yes | recorded | n/a | yes |
> | CSMs | yes | live | n/a | yes |
> | AEs (non-enterprise) | yes | live + recorded | n/a | yes |
> | Enterprise AEs | yes | live + recorded | 1:1 Sales Ops partner | yes |
> | Finance | yes (reports) | live (reports) | n/a | yes |
>
> ## Success metrics
>
> **Lead:** weekly NewCRM-entered opportunity ratio; daily support ticket count against the rollout tag; cohort survey scores.
> **Lag:** quarter-end close runs from NewCRM without manual reconciliation; deal-cycle time within 10% of baseline at T+90; sales team CSAT-equivalent survey at T+60 ≥ 3.5/5.
>
> ## Abort criteria
>
> - Severity-1 data-loss or sync-failure incident during any phase → hold; reverse to OldCRM-only for the affected cohort; VP Sales is the abort decider.
> - Pilot survey returns < 3/5 on the core job question → extend Phase 0 by 2 weeks; do not begin Phase 1.
> - Support ticket volume > 3× baseline for 3 consecutive business days during any cohort wave → hold rollout to next cohort; remain on dual-write for current cohort.
> - Two consecutive nightly sync runs show > 5% deltas → pause; engage NewCRM vendor; do not advance phases.
>
> ## Rollback plan
>
> Through Phase 1: full rollback is mechanical — pilot users return to OldCRM, no data loss because of dual-entry.
> Phases 2–4: rollback per cohort is mechanical because of the 5-day dual-write window. Beyond the dual-write window, rollback requires reverse-sync from NewCRM to OldCRM, which has been tested and produces < 1% loss; treat as last-resort because of customer-facing disruption.
> Post Phase 5 cutover: no full rollback. Recovery from a discovered-late issue is forward-only — fix in NewCRM, accept the data shape, do not attempt to revive OldCRM.
>
> ## Dependencies and constraints
>
> - Finance close cycle: Phase 5 cutover must not occur in the 5 business days preceding month-end.
> - Board prep weeks: no dual-write windows during the 10 business days preceding each board meeting.
> - Comp-plan reporting integration (owned by the data team) must land before Phase 3.
>
> ## Post-rollout cleanup
>
> T+0 (cutover): OldCRM read-only, comms confirming cutover, retrospective scheduled.
> T+30: retrospective; enablement materials archived; rollout slack channels archived.
> T+60: OldCRM contract ends; final archival snapshot; permissions revoked.
> T+90: lag metric review; rollout closed.
>
> ## Roles
>
> Sponsor: VP Sales. Rollout owner: Sales Ops director. Comms lead: Sales Ops business partner. Enablement lead: sales enablement manager. Technical owner: data team lead. Abort decider: VP Sales (with input from CRO and CFO).

## Limitations

- The skill produces a plan; it cannot guarantee execution. Plans degrade on contact with reality; the value is the structured artifact that names what changes when reality intervenes (which phase slips, which abort criterion triggers).
- Friction ranking is judgment, not measurement. The skill will produce a defensible ranking from the inputs, but real audience friction is best discovered by the pilot itself. Treat the ranking as a hypothesis to falsify.
- Estimated phase durations are estimates. The skill marks them as such; teams that promote estimates to commitments and miss them often abandon the plan rather than the dates.
- The skill does not size the change. If the inputs describe a change too small to warrant phased rollout, the skill should say so and recommend a deploy checklist or runbook instead, rather than generate a heavyweight plan.
- Organizational rollouts (process and behavior changes) have weaker rollback than technical rollouts. The skill is honest about this in the rollback section; teams that need genuine reversibility should design for it earlier, in the change itself.
- The skill does not own change adoption past the GA milestone. Sustained adoption is a separate discipline (reinforcement, manager accountability, removal of fallback paths) that the plan can sketch but not execute.

## Sources reviewed

- https://github.com/argoproj/argo-rollouts
- https://github.com/fluxcd/flagger
- https://github.com/Unleash/unleash
- https://github.com/flagsmith/flagsmith
- https://github.com/vintasoftware/production-launch-checklist
- https://github.com/thoughtbot/templates
- https://github.com/reactjs/rfcs
- https://github.com/concourse/rfcs
