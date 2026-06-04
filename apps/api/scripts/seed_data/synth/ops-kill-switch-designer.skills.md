---
id: skillsgit-curated/ops-kill-switch-designer
version: 1.0.0
name: Kill-Switch Designer
description: Designs a kill switch and rollback runbook for a feature or change — decision criteria, owners, telemetry to watch, the exact mechanism to flip, the comms that follow, and the recovery path back to the new state when ready.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: operations
tags: [niche:change-management, kill-switch, feature-flags, rollback, rollout-safety, incident-prevention, operations]
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
  - kill switch
  - rollback plan
  - feature flag
  - emergency disable
  - abort criteria
  - rollback runbook
  - revert procedure
  - feature toggle
  - rollback comms
  - rollout safety
  - blast radius
  - circuit breaker
example_invocations:
  - "Design a kill switch for the new checkout flow we're shipping next week."
  - "We're rolling out a billing change; draft the kill-switch and rollback runbook."
  - "How do we revert the new search ranker if it tanks conversion?"
inputs:
  - name: change_under_protection
    type: text
    required: true
    description: What the kill switch protects — the feature, change, or behavior being introduced, and the system in which it lives.
  - name: rollout_mechanism
    type: text
    required: false
    description: How the change is being shipped — feature flag platform, percentage rollout, cohort-targeted, blue/green, canary, or a manual config change. Different mechanisms imply different switches.
  - name: known_failure_modes
    type: text
    required: false
    description: Failure modes the team has hypothesized or seen in similar changes. The more specific, the sharper the switch design.
  - name: telemetry_available
    type: text
    required: false
    description: Metrics, logs, traces, and dashboards that exist or can exist for this change — error rates, latency percentiles, business KPIs, customer-reported events.
  - name: blast_radius
    type: choice
    required: false
    description: Severity band that calibrates how aggressive the switch and triggers should be.
    choices: [contained, single-product, cross-product, customer-data, revenue-impacting]
outputs:
  - name: kill_switch_design
    type: markdown
    description: A design document covering switch mechanism, trigger thresholds, decision authority, telemetry to watch, the rollback runbook, the comms template, and the recovery-back-to-rollout path.
  - name: triggered_comms_template
    type: markdown
    description: A pre-filled comms template for the moment the kill switch is activated — internal acknowledgement, customer notification if applicable, status-page update, and a post-event summary skeleton.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a change is going to ship and one of the following is true: the change is partially or fully irreversible without a deliberate mechanism; the change has a plausible failure mode that would be expensive to ride out; the change is going behind a flag or percentage rollout and the team has not yet defined what would cause them to flip the flag; or the team has been bitten before by a change that took too long to revert. The output is a design that names the switch, the triggers, the authority to flip, the telemetry, the procedure, and the comms — written before the change ships, when the team can think clearly.

The skill is opinionated about four things. First: **kill switches are designed before the failure, not invented during it.** Decisions made under pressure with incomplete information are systematically worse than decisions written in advance. Second: **trigger thresholds are observable and pre-agreed.** "If things look bad" is not a trigger; "if checkout conversion drops by more than 15% over a 30-minute window on traffic > 1k rps" is. Third: **the authority to flip is named and decentralized to the lowest competent level.** A switch that requires VP approval at 2am will not be flipped. Fourth: **the comms are pre-written.** When the switch flips, the on-call has 90 seconds to communicate; reading "I need to draft a Slack post" in that window is a failure mode.

Do not use this skill for runbooks for foreseeable operational tasks (use the runbook generator). Do not use it for incident response — by the time the incident is open, this design should already exist. Use it during the rollout-planning phase, before the change is shipped.

## How to apply

The skill produces the design in twelve moves.

1. **Restate the change and its happy path in one paragraph.** What is shipping, what the new behavior is, and why the team believes it is an improvement. The kill switch protects this hypothesis; if the hypothesis is wrong, the switch is the path back. The paragraph is the design's grounding context.

2. **Enumerate the failure modes that justify a switch.** A kill switch defends against specific failure modes, not against "anything bad." List the modes: latency regression, error rate spike, conversion drop, data-quality degradation, downstream integration failure, customer-visible incorrectness, revenue-impacting bug. For each mode, note whether the failure would be obvious, subtle (silent), or delayed (manifesting hours or days later). Subtle and delayed failures are the dangerous ones; they shape the telemetry section.

3. **Pick the switch mechanism appropriate to the change.** Options: (a) **boolean feature flag** — flip to disable for everyone at once; appropriate when the new behavior is opt-in or strictly additive. (b) **percentage rollback** — reduce the rollout percentage; appropriate for traffic-routable changes. (c) **cohort revert** — turn off for specific cohorts; appropriate when only certain segments are affected. (d) **deploy revert** — roll back the deployment; appropriate when the change is not flag-protected and there is a known-good prior revision. (e) **config flip** — swap a non-flag configuration (e.g., a routing rule, a model version, a destination). Each mechanism has different latency to take effect (milliseconds for a flag, minutes for a deploy revert) and different reversibility characteristics. Pick one and state it explicitly; ambiguity here is the most common failure of kill-switch design.

4. **Write the trigger conditions as observable rules with thresholds and windows.** Each trigger has three parts: a metric, a threshold, and a time window. Examples: "p95 checkout-API latency > 1500ms for a 5-minute window when request volume > 500 rps." "Error rate on `POST /payments` > 2% over 10 minutes." "Conversion rate (visits-to-purchase) drops by more than 20% relative to the trailing 7-day baseline over a 30-minute window during business-hours traffic." Triggers must be checkable from a dashboard or alert that exists; if the telemetry doesn't exist, it must be added before the change ships, which is part of the deliverable.

5. **Add at least one qualitative trigger.** Not all failures appear in metrics in time. A qualitative trigger names a human signal: "executive escalation about the change reaches the rollout owner," "customer support reports more than 10 unique customers affected within 4 business hours," "a credible internal report of customer data loss or corruption." Qualitative triggers must have a single named owner who can pull the switch on their judgment.

6. **Name the authority to flip — by role, not by name — and give it to the lowest competent level.** "The on-call engineer for service X can flip without further approval, given a met trigger." "The on-call may flip on a qualitative trigger and notify the rollout owner within 15 minutes." Identify the cases that require escalation (revenue impact > $X, regulator-facing change, public-comms required) but minimize them. A switch behind too much process is a switch that does not get flipped at 2am.

7. **Specify the telemetry that must exist before the change ships.** For every quantitative trigger, name the metric, the dashboard or alert that surfaces it, and the data source. For every failure mode flagged as subtle or delayed in step 2, name the early-detection signal — what would tell us in hours that the change is silently bad. Telemetry is the design's hardest requirement: a kill switch with no instrumented dashboard is a switch that only flips after Twitter notices.

8. **Write the rollback runbook for each switch mechanism.** Numbered steps to flip the switch: where to log in, what command or button, what to verify after flipping, how long it takes to propagate, what to do if it doesn't take effect within N minutes. Each step has an expected output. The runbook is short — 5 to 10 steps — because long runbooks are not executed under stress. Include the verification: how the on-call confirms the switch took effect, with the dashboard panel and threshold that confirms recovery.

9. **Pre-write the activation comms.** Three drafts: (a) internal Slack post for the engineering channel and the rollout channel — "kill switch activated for [feature] at [time] due to [trigger]; we are reverted to [prior behavior]; investigating; updates every 30 minutes." (b) status-page update if customer-visible — "we have rolled back a recent change to [feature] after detecting [observable]; affected functionality is restored; we will share more in the postmortem." (c) executive notification if blast radius warrants. Each draft has the right placeholders, the right tone, and a named sender role.

10. **Define the recovery path back to the rolled-out state.** A kill switch that flips and is never flipped back is a permanent rollback; the team has not yet decided that. The design names: who decides when to attempt re-rollout, what evidence opens that conversation, what the second-attempt rollout looks like (smaller cohort, more telemetry, different time of day, with a fix for the failure that triggered the switch). Recovery is not the same as the original rollout — the team learns, instruments, and tries again with a sharper plan.

11. **Specify what NOT to do at the moment of activation.** Anti-patterns under stress that the design pre-empts. "Do not gather more data before flipping if a trigger has fired; data-gathering is post-flip." "Do not consult more than one additional person before flipping; the authority is the on-call." "Do not partially flip — if the trigger fires, the switch is binary." Naming the anti-patterns reduces the chance they happen.

12. **Include the audit trail.** Every kill-switch activation records: who flipped, what trigger fired (or what qualitative signal), exact time, what was reverted, what is to follow up (postmortem, recovery plan). The audit trail is automatic where possible (the flag platform logs it) and manual where not (the on-call posts to a designated channel). It feeds the postmortem and the trust the team has that the mechanism worked.

### Standard kill-switch design layout

The output document uses these section headers in this order:

1. `# Kill Switch Design: <change name>`
2. `## Change under protection` — one-paragraph context.
3. `## Failure modes guarded` — list with obvious/subtle/delayed labels.
4. `## Switch mechanism` — exactly one choice, named explicitly.
5. `## Quantitative trigger conditions` — metric × threshold × window, table form.
6. `## Qualitative trigger conditions` — human signals with owners.
7. `## Authority and escalation` — who can flip, when escalation is required.
8. `## Telemetry required before ship` — metrics, dashboards, alerts.
9. `## Rollback runbook` — numbered steps with verification.
10. `## Activation comms` — internal Slack, status page, executive notification.
11. `## Recovery path` — when and how to attempt re-rollout.
12. `## Anti-patterns at activation` — what not to do.
13. `## Audit trail expectations` — what is recorded automatically vs. manually.

### Composition rules

- **One switch mechanism per design.** Multiple mechanisms invite ambiguity. If the change needs more than one, split into multiple kill switches with named scopes.
- **Triggers are pre-agreed.** A trigger added during an incident is a trigger that did not exist when it was needed.
- **Authority is single-keyed by default.** Multi-key authority is reserved for revenue-impacting or regulator-facing cases.
- **Comms are pre-written.** Drafting under stress produces worse copy and slower response.
- **Recovery is a separate decision.** Flipping the switch back is not automatic; it is its own deliberate action with its own evidence.
- **Telemetry is a deliverable, not an assumption.** If the dashboard doesn't exist, the design names what must be built before ship.

## Inputs

- **Change under protection (required, text).** What the switch protects and the system it lives in.
- **Rollout mechanism (optional, text).** Feature flag platform, percentage rollout, cohort routing, blue/green, deploy-based.
- **Known failure modes (optional, text).** Failures the team anticipates from this or similar changes.
- **Telemetry available (optional, text).** Existing metrics, dashboards, and alerts.
- **Blast radius (optional, choice).** Severity banding that calibrates trigger aggressiveness and authority.

## Outputs

A full markdown kill-switch design and a pre-filled activation comms template ready to send.

## Examples

### Worked example: new checkout flow rollout

**Change under protection:** "We are rolling out a redesigned checkout flow that reduces from 4 steps to 2. Behavior change for all customers. Behind a feature flag, ramping 1% → 10% → 50% → 100% over 14 days."

**Rollout mechanism:** "LaunchDarkly-style feature flag. Per-customer evaluation. We can drop to 0% in under 60 seconds."

**Known failure modes:** "Conversion drop (we know the redesign changes the flow customers know). New checkout doesn't render in some older browsers. Payment-failure rate could rise if the consolidated step doesn't handle a card-decline edge case. Risk of a silent address-validation regression that we'd see in fulfillment hours later."

**Telemetry available:** "Conversion funnel dashboard updates every 60s. Frontend error rate per route in Datadog. Payment-API error rate per merchant. Address-validation failures are logged but not dashboarded."

**Blast radius:** revenue-impacting

**Expected output (excerpted):**

> # Kill Switch Design: redesigned checkout flow
>
> ## Change under protection
>
> The new 2-step checkout flow replaces the 4-step legacy flow for customers behind feature flag `checkout-v2-flow`. The hypothesis is that the new flow lifts mobile conversion by 5%+ without degrading desktop. The flag ramps 1% → 10% → 50% → 100% over 14 days.
>
> ## Failure modes guarded
>
> | Failure mode | Type |
> | --- | --- |
> | Conversion drop on either platform | obvious |
> | Frontend render failure on older browsers | obvious (errors dashboard) |
> | Payment success-rate regression from consolidated step | obvious (payment dashboard) |
> | Address-validation regression seen later in fulfillment | delayed (hours-to-days) |
> | Silent UX regression — customer completes purchase but enters wrong data | subtle |
>
> ## Switch mechanism
>
> Feature flag `checkout-v2-flow` set to 0% via the flag platform. Effective in under 60 seconds. No deploy required. Per-customer evaluation means in-flight checkout sessions on v2 complete on v2; new sessions go to v1. Acceptable because in-flight session count is bounded by the checkout window.
>
> ## Quantitative trigger conditions
>
> | # | Metric | Threshold | Window | Conditions |
> | --- | --- | --- | --- | --- |
> | T1 | Conversion rate, v2-cohort vs. v1-cohort | v2 is more than 5% worse | 60-minute rolling | Total sample > 5,000 v2 sessions |
> | T2 | Frontend error rate, `/checkout` route | > 2% | 10-minute rolling | Sample > 500 sessions |
> | T3 | Payment API error rate, v2 cohort | > 1.5× v1-cohort baseline | 15-minute rolling | Sample > 1,000 attempts |
> | T4 | Address-validation failure rate | > 2× trailing-7-day baseline | 60-minute rolling | Across all v2 sessions |
> | T5 | Fulfillment-side address-correction rate (next-day signal) | > 1.3× prior-week baseline | 24-hour rolling | Reviewed once daily by rollout owner |
>
> ## Qualitative trigger conditions
>
> - Three or more credible customer reports of completed-but-wrong-data orders attributed to v2, within any 4-hour window — owner: rollout owner (Maya) or her delegate.
> - Executive escalation citing customer-visible breakage of checkout — owner: VP Eng on-call.
> - Internal credible report (employee or partner) of revenue-impacting bug specific to v2 — owner: checkout team lead.
>
> ## Authority and escalation
>
> - Any on-call engineer for the checkout service can flip the flag to 0% upon T1, T2, T3, or T4 trigger. No further approval required.
> - On-call must post in `#checkout-rollout` within 5 minutes of flip with the trigger that fired.
> - Qualitative triggers (Q1-Q3): the named owner may flip; if the owner is unreachable within 15 minutes, the on-call may flip on the qualitative trigger and post.
> - Escalation required (notify before flip): if revenue impact in the trigger window exceeds $50,000 — notify VP Eng on-call. This is a notification, not a gate; the flip still proceeds at the on-call's discretion.
> - Recovery (re-rollout) decision: rollout owner with input from checkout team lead.
>
> ## Telemetry required before ship
>
> - **Exists:** conversion funnel dashboard (60s refresh), frontend error-rate per route, payment-API error rate per merchant.
> - **Must build before ship:**
>   - Conversion cohort comparison panel (v1 vs. v2) with sample-size guard — owner: data team — due before 10% ramp begins.
>   - Address-validation failure-rate dashboard — owner: checkout engineering — due before any ramp begins.
>   - Fulfillment-side address-correction rate panel — owner: fulfillment team — due before 50% ramp begins.
>   - Alert on T1, T2, T3 wired to PagerDuty service `checkout-oncall`.
> - Without these, ramp does not advance past the gate that requires them.
>
> ## Rollback runbook
>
> 1. Open the flag platform; navigate to flag `checkout-v2-flow`.
> 2. Set rollout percentage to **0**. Expected: flag platform shows 0% within 5 seconds; effective at edges within 60 seconds.
> 3. Watch `frontend error rate /checkout` and `payment API error rate` panels for return to baseline. Expected within 5 minutes.
> 4. Watch conversion funnel — total conversion rate should return to v1 baseline within 30 minutes.
> 5. If the flag UI does not respond within 2 minutes, escalate to platform on-call (PagerDuty service `platform-flags-oncall`); fallback is a config push that hard-codes the flag to false in checkout service config.
> 6. Verify in `#checkout-rollout` that the post is visible; confirm rollout owner acknowledged within 10 minutes.
> 7. Open a postmortem ticket and populate the audit trail (who flipped, time, trigger).
>
> ## Activation comms
>
> **Internal Slack — `#checkout-rollout` and `#engineering-announcements`:**
> > Kill switch activated for `checkout-v2-flow` at [time] by [on-call name]. Trigger: [T#, metric value]. We are reverted to v1. Investigating; status updates every 30 minutes. Customers in flight on v2 complete on v2; new sessions are v1. Rollout owner is paged.
>
> **Status page (if customer-visible):**
> > We've rolled back a recent change to our checkout flow after observing a regression in [conversion / payment success / address validation]. Affected functionality is restored. A full update will follow.
>
> **Executive notification (if triggered by escalation rule):**
> > [Concise: which flag, when flipped, why, projected revenue impact of the window in which the issue ran, status of investigation, when next update.]
>
> ## Recovery path
>
> - No re-rollout attempt for at least 48 hours after the flip.
> - Recovery prerequisites: postmortem complete with named root cause; code fix or telemetry improvement merged; trigger thresholds reviewed and adjusted if appropriate.
> - Recovery rollout: restart at 1% with the same triggers active; advance gate is now "no triggers fire over a 48-hour window at each ramp step," more conservative than the original ramp.
> - Recovery rollout owner: same rollout owner (Maya), with explicit sign-off from VP Eng.
>
> ## Anti-patterns at activation
>
> - Do not "gather more data" before flipping when a quantitative trigger has fired. The data is the trigger.
> - Do not partial-flip (e.g., reduce to 5% instead of 0). The switch is binary; partial states obscure whether the issue was contained.
> - Do not wait for the rollout owner if a quantitative trigger has fired and the on-call has authority. The owner is notified, not consulted.
> - Do not edit the trigger thresholds during the active rollout. Trigger threshold changes are a between-rollout decision.
>
> ## Audit trail expectations
>
> - The flag platform logs the activation automatically (actor, time, prior state, new state).
> - The on-call's Slack post in `#checkout-rollout` is the human-readable audit entry; it must include trigger reference, prior state, and time.
> - The postmortem ticket references both.

## Limitations

- The skill produces a design; it does not implement telemetry or wire alerts. The "must build before ship" section is a checklist for the team, not a working dashboard.
- Trigger thresholds are starting estimates. They should be tuned against the system's actual baseline behavior; thresholds calibrated against the wrong baseline cause either false positives (kill switch flips for noise) or false negatives (real failure rides out the window).
- The skill assumes a flag-flippable or revert-able mechanism. For changes that are not flag-protected and cannot be cleanly reverted (e.g., destructive data migrations), the skill will say so and recommend that the change be re-architected behind a switchable mechanism before ship, rather than produce a design that cannot be executed.
- Authority delegation depends on organizational trust and the on-call's competence. The skill recommends the lowest competent level; in some organizations that authority sits above the on-call for reasons (incentives, audit, regulator) that the skill cannot evaluate. Teams should adjust authority to their context without softening it to the point of inaction.
- Qualitative triggers are judgment-based. Naming an owner is the most important defense; debate about whether a qualitative signal "really counts" during a live event is itself a failure mode.
- The recovery path is a sketch. A second attempt at rollout deserves its own rollout plan with the new learnings folded in; this design's recovery section names the sketch but does not replace that plan.
- Some changes do not deserve a kill switch — they should be shipped without one because the cost of building the switch exceeds the cost of riding out a failure. The skill should be honest when the inputs describe such a change and recommend skipping rather than over-engineer.

## Sources reviewed

- https://github.com/Unleash/unleash
- https://github.com/flagsmith/flagsmith
- https://github.com/argoproj/argo-rollouts
- https://github.com/fluxcd/flagger
- https://github.com/release-drafter/release-drafter
- https://github.com/vintasoftware/production-launch-checklist
- https://github.com/reactjs/rfcs
