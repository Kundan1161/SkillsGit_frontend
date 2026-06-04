---
id: jane-devops-demo/2025-03-paging-policy-rewrite
version: 1.0.0
name: 2025-03 Paging policy rewrite — cutting pages 62% by gating on user impact
description: "[sample data] On-call was paged 38 times in February; rewrote alert routing to require either user-facing symptom OR irreversible operation as the page criterion. March pages: 14, with no missed real incidents."
authors:
  - name: Jane Devops (sample)
    handle: jane-devops-demo
    role: author
category: personas
tags:
  - sample-data
  - alerting
  - on-call
  - sre
  - alert-fatigue
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
trigger_keywords:
  - alert fatigue
  - paging policy
  - on-call burden
  - actionable alerts
example_invocations:
  - "We're paging 30+ times a month and most are noise. How do I rewrite the policy without missing real incidents?"
kind: memory_neuron
parent_occupation_id: skillsgit-curated/ai-devops-engineer
links:
  - target: base/alert-policy-architect
    relation: applies
  - target: base/slo-designer
    relation: extends
  - target: base/ops-incident-commander
    relation: see-also
neuron:
  situation: |
    On-call rotation review showed 38 pages in February across 5
    engineers. Of those, 9 were actionable (had a real incident with
    user impact), 22 were transient self-resolving conditions, and
    7 were duplicates of the same upstream issue. Two engineers said
    they were considering changing teams over the burden. The error
    budget for the period had only burned 4%, suggesting the page
    count was wildly out of proportion to actual customer-visible
    incidents.
  decision: |
    Audited every alert that had fired in the trailing 90 days against
    two criteria: (a) does it represent a user-facing symptom right
    now, or (b) does it represent an irreversible operation that has
    failed (e.g. data corruption, secret exposure, billing miss). If
    neither, demoted to ticket-only. Added a 5-minute "for" duration
    to symptom-based alerts to suppress transient blips. Built a
    deduplication rule that suppresses downstream alerts when an
    upstream alert has fired in the last 15 minutes.
  outcome: |
    March: 14 pages across the same 5 engineers. 11 of the 14 were
    actionable (a 79% precision rate, vs February's 24%). No missed
    incidents (verified by cross-referencing against customer support
    tickets and the deferred-tickets queue). One of the two engineers
    considering changing teams stayed.
  recorded_at: "2025-03-04"
  confidence: 0.85
---

# 2025-03 Paging policy rewrite — cutting pages 62% by gating on user impact

> SAMPLE DATA — this neuron is part of the seeded `@jane-devops-demo`
> persona shipped alongside the Cycle-1 demo. Real persona neurons are
> published by named DevOps practitioners and replace this content.

## When to use
Apply this neuron when alert fatigue is materializing as on-call
burnout (engineers asking to leave the rotation, post-page recovery
time growing, or "page precision" — pages that map to real incidents
— below 50%). The audit framework here is the small set of two
criteria that survived our review; almost everything else demotes
cleanly to ticket-only.

## How to apply
1. Compute "page precision" for the prior 30-90 days: pages that
   mapped to a real customer-impacting incident or irreversible
   operation, divided by total pages. If under 50%, the rest of
   this neuron applies.
2. For every alert rule in the registry, ask: (a) does firing
   this alert mean a real user is having a worse experience right
   now? (b) does it mean an irreversible operation has failed?
   If neither, demote to ticket-only.
3. Add a 5-minute `for:` window to surviving symptom-based alerts
   to suppress transients that self-resolve.
4. Add `inhibit_rules` (or equivalent) so downstream alerts
   suppress when an upstream is already paging.
5. Re-measure page precision after 30 days. Cross-reference
   against customer support tickets to confirm no missed incidents.

## What happened
The rotation review in early March surfaced a clear pattern: 38 pages
in February, of which only 9 mapped to an actual user-impacting
incident or an irreversible operation. The other 29 broke down as:

- 22 transient: brief CPU spike, brief queue depth excursion, brief
  upstream slowdown that resolved before anyone could log in.
- 7 duplicates of a single upstream issue (one Kafka broker outage
  cascaded to 7 downstream service alerts).

Error budget burn for February was 4%. If the page count tracked
actual customer impact we'd have expected at most 9-12 pages, not
38. Two engineers said in 1:1s that they were considering rotating
off the team.

The audit framework was deliberately narrow. For every alert rule
in the registry (about 240 of them across the orders domain) we
asked two questions:

1. **Does firing this alert mean a real user is having a worse
   experience right now?** ("right now" meaning within the next 5
   minutes if not acted on, not "could in theory")
2. **Does firing this alert mean an irreversible operation has
   failed?** (data corruption, secret leakage, billing event missed,
   privacy violation, anything where a delay makes the outcome
   permanently worse)

If neither, the alert was demoted to ticket-only (still fires into
our alerts board, still appears in the on-call dashboard, but does
not page). Concretely:

- 87 alerts demoted to ticket-only. Examples: "CPU > 80% for 10
  minutes," "pod restart count > 3 in 1h," "disk usage > 75%."
  None of these directly correlate with user pain; they're indicators
  that something might become a problem.
- 31 alerts kept as pages but got a 5-minute `for:` window added so
  transients self-resolve. Examples: any p99 latency alert.
- 14 alerts left untouched (the irreversible-operation set).
- 108 alerts already met the criteria.

We also built a dedup rule: if an upstream service has fired a
"service down" page in the last 15 minutes, suppress alerts on its
known downstream consumers. Implemented via Alertmanager
`inhibit_rules`.

March numbers: 14 pages, 11 actionable. The 3 non-actionable were
genuinely ambiguous cases (one was a real spike that resolved during
investigation, one was a real spike that turned out to be load test
traffic from a partner, one was a paging-system bug that we fixed).
No missed incidents — we cross-referenced March's customer support
tickets against the alert log and the on-call had been notified
(via ticket-only or page) of every issue that customers reported.

The engineer who had been considering rotating off stayed. The other
one moved, but cited unrelated reasons in the exit conversation.

## Lessons
- Page on user impact OR irreversibility, not on cause. Most alerts
  are caused by infrastructure conditions (CPU, memory, disk, restart
  count) that may or may not produce user pain. Pages should fire
  when pain is happening or about to.
- A 5-minute `for:` window costs you nothing real. A transient that
  self-resolves in 5 minutes was almost certainly never going to hurt
  anyone; if it does become persistent, paging at minute 5 is just as
  good as paging at minute 0.
- Dedup at the routing layer, not in the alert rules. Alertmanager's
  `inhibit_rules` (or its equivalent) lets you say "if upstream is
  down, suppress downstream" without modifying any of the downstream
  alert definitions. Centralised and reviewable.
- The audit is the work. Don't try to fix paging policy by adding
  more rules; fix it by removing rules that don't meet the criteria.
  Our before/after rule count was 240 -> 153 (87 demoted, 0 added).
- Track page precision as a leading indicator. "Pages that mapped
  to a real incident / total pages" is a single number that captures
  alert health. We now report it in the monthly ops review with the
  same weight as error budget burn.
