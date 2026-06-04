---
id: skillsgit-curated/slo-designer
version: 1.0.0
name: SLO Designer
description: Design service-level objectives end-to-end — user journeys to SLIs to SLOs, multi-window multi-burn-rate alerts, error-budget policy, and review cadence.
authors:
  - name: Wave-3 Methodology Synthesis
    handle: wave3-observability-sre
    role: author
category: engineering
tags:
  - niche:observability-sre
  - slo
  - sli
  - error-budget
  - burn-rate
  - reliability
  - alerting
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
    - gpt-4.1
    - gemini-1.5-pro
  min_context_tokens: 32000
  tools_optional:
    - web_search
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - slo
  - sli
  - service level objective
  - error budget
  - burn rate
  - reliability target
  - availability target
  - latency objective
  - openslo
  - sloth
example_invocations:
  - "Design SLOs for our checkout service — it's three RPC hops with a Stripe dependency."
  - "We have no SLOs. Where do we start for a B2B SaaS API with 12 endpoints?"
  - "Translate this 99.9% availability target into Prometheus burn-rate alerts."
  - "Help me write an error-budget policy that the product team will actually respect."
inputs:
  - name: service_description
    type: text
    required: true
    description: What the service does, who depends on it, the critical user journeys, current architecture (sync vs async, dependencies), and traffic profile.
  - name: current_state
    type: text
    required: false
    description: Existing SLOs, monitors, dashboards, recent incidents, and what telemetry already exists (Prometheus, OTel, vendor APM).
  - name: org_context
    type: text
    required: false
    description: Team size, on-call maturity, who owns the service, and any commercial commitments (SLAs in contracts).
outputs:
  - name: slo_design
    type: markdown
    description: Journey map, SLI definitions with queries, SLO targets with windows, burn-rate alert rules, error-budget policy, and a 90-day rollout plan.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release covering SLI taxonomy, multi-window multi-burn-rate alert math, OpenSLO spec output, and error-budget policy templates.
---

# SLO Designer

## When to use

Use this skill when an engineer or SRE needs to design service-level objectives for a system — typically one of:

- A new service is launching and needs reliability targets before it goes to production.
- An existing service has dashboards and ad-hoc alerts but no formal SLO, and noise or missed incidents motivate doing this properly.
- Leadership has asked for "an SLO program" and the team needs a starting service and a template the rest of the org can copy.
- A contractual SLA exists (e.g. 99.9% uptime in a customer contract) and the internal SLO must be tighter than the SLA with explicit margin.

Do **not** use this skill for incident response itself (use an incident-commander skill), for tuning existing alerts post-incident (use a detection-tuner skill), or for designing the alert routing/escalation taxonomy (use an alert-policy skill — SLO burn-rate alerts will *feed into* that taxonomy).

## How to apply

Work through the following phases in order. Each phase has a question you must answer before moving on.

### Phase 1 — Anchor on user journeys, not endpoints

The first mistake most teams make is defining one SLO per endpoint or per microservice. That produces dozens of SLOs nobody can act on. Instead:

1. Ask the user to list **2–5 critical user journeys** for the service. Examples for a payments API: "place an order", "view past orders", "issue a refund". Examples for an internal data platform: "ingest a batch", "run a scheduled query", "export a result".
2. For each journey, identify the **request class** it corresponds to (the HTTP routes, RPC methods, queue topics, or job types involved).
3. Mark each journey **user-facing** (an end customer notices), **partner-facing** (an integrating system notices), or **internal** (only employees notice). Reliability budgets should be tightest for user-facing and loosest for internal.
4. Confirm with the user: "Are these the journeys we want to commit to? Anything we'd be embarrassed about if it failed silently?"

If the user can't articulate journeys yet, do not invent them — push back and ask. SLOs designed against the wrong journeys are worse than no SLOs.

### Phase 2 — Choose SLI types per journey

For each journey, pick **one or two** Service Level Indicators. The taxonomy below covers >95% of cases:

| SLI type | When to use | Common formula |
| --- | --- | --- |
| **Availability** (request success) | Synchronous request/response journeys | `good_events / valid_events` where good = 2xx/3xx/4xx-client and valid = all non-excluded |
| **Latency** (response time) | Same journeys where slow ≈ broken to users | `count(latency < threshold) / count(valid)` — note: it is a count ratio, not a percentile! |
| **Freshness** | Pipelines, replicas, caches | `count(data_age < threshold) / count(samples)` |
| **Correctness** | Computations whose output can be silently wrong | Sample-based comparison against ground truth, expressed as a ratio |
| **Throughput / coverage** | Batch and analytics jobs | `successful_units_processed / expected_units` |
| **Quality** (degraded mode) | Systems with graceful degradation | `count(full_quality) / count(any_response)` |

Three rules that prevent classic mistakes:

- **Express every SLI as a ratio of good events over valid events.** This makes the math for error budgets work and matches OpenSLO and Sloth conventions.
- **Latency SLIs are count ratios, not percentile gauges.** "99% of requests under 500 ms" → `good = requests with latency < 500 ms`, not `p99 latency < 500 ms`. Percentile alerts are notoriously hard to combine across windows and aggregate across replicas; count ratios are not.
- **Exclude what you cannot control** from `valid`: 4xx client errors caused by malformed input, requests from synthetic prober endpoints you own separately, requests during an announced maintenance window. Document every exclusion — they always come up in audits.

### Phase 3 — Set the SLO target and window

For each SLI, propose a target and a window. Default to a **30-day rolling window**; calendar windows make month-end behavior weird. Suggest target ranges based on journey criticality:

| Journey class | Reasonable target range | Don't promise more than |
| --- | --- | --- |
| User-facing critical (login, checkout) | 99.9% – 99.95% | 99.99% (four-nines is hard and rarely worth it) |
| User-facing non-critical (search suggestions, recommendations) | 99% – 99.5% | 99.9% |
| Partner integrations | 99.5% – 99.9% | 99.95% |
| Internal tools, async jobs | 99% – 99.5% | 99.9% |

Three principles to share with the user:

- **The SLO must be tighter than any external SLA** by at least one nine, or by enough buffer that an SLA breach is preceded by an SLO breach with time to react.
- **The SLO must be loose enough that the team currently meets it** in normal operations, with room for occasional bad weeks. If you propose 99.99% but the service runs at 99.7%, you have invented a perpetual emergency.
- **Round to a number humans can talk about** (99.9, not 99.873). The budget math is a tool; the target is a contract.

Compute the implied error budget for the proposed target:

- 99.9% over 30 days = **43.2 minutes** of bad time per month, or **0.1%** of valid events.
- 99.95% over 30 days = **21.6 minutes** per month.
- 99.99% over 30 days = **4.32 minutes** per month — typically below the latency of a human paging response.

If the budget is smaller than your mean-time-to-detect, you cannot meet it. Adjust.

### Phase 4 — Write burn-rate alerts

Use the **multi-window, multi-burn-rate** approach from the Google SRE workbook (see Sources). It is the only alert design that gives you good precision *and* good reset time without per-team tuning.

Two pages and one ticket per SLO:

| Severity | Long window | Short window | Burn rate | Budget burned at fire | Typical action |
| --- | --- | --- | --- | --- | --- |
| **Page (fast)** | 1 hour | 5 minutes | 14.4 | 2% of 30-day budget in 1h | Wake someone up |
| **Page (slow)** | 6 hours | 30 minutes | 6 | 5% of 30-day budget in 6h | Page during business hours, or after-hours if it persists |
| **Ticket** | 3 days | 6 hours | 1 | 10% of 30-day budget in 3 days | File a ticket, fix this week |

The short window is the confirmation guard: both the long-window burn rate AND the short-window burn rate must exceed the threshold for the alert to fire. This eliminates the long tail of alerts that keep firing for an hour after the incident is resolved.

Render the alerts as Prometheus rules. Example for a 99.9% availability SLO on `api-checkout`:

```yaml
groups:
- name: checkout-slo-burn
  rules:
  - alert: CheckoutSLOFastBurn
    expr: |
      (
        sum(rate(http_requests_total{job="api-checkout",code=~"5.."}[1h]))
        / sum(rate(http_requests_total{job="api-checkout"}[1h]))
      ) > (14.4 * 0.001)
      and
      (
        sum(rate(http_requests_total{job="api-checkout",code=~"5.."}[5m]))
        / sum(rate(http_requests_total{job="api-checkout"}[5m]))
      ) > (14.4 * 0.001)
    for: 2m
    labels:
      severity: page
      slo: checkout-availability
    annotations:
      summary: "Checkout SLO fast burn — 2% of monthly budget in 1h"
      runbook_url: https://runbooks.example.com/checkout-slo
  - alert: CheckoutSLOSlowBurn
    expr: |
      ( ... 6h window > 6 * 0.001 ... )
      and
      ( ... 30m window > 6 * 0.001 ... )
    for: 15m
    labels:
      severity: page
      slo: checkout-availability
  - alert: CheckoutSLOTicket
    expr: |
      ( ... 3d window > 1 * 0.001 ... )
      and
      ( ... 6h window > 1 * 0.001 ... )
    for: 1h
    labels:
      severity: ticket
      slo: checkout-availability
```

If the team uses Sloth or OpenSLO (recommended for any team with more than ~5 SLOs), output a Sloth spec instead and let it generate the rules. The Sloth spec is shorter, version-controllable, and round-trippable. Example Sloth spec:

```yaml
version: prometheus/v1
service: api-checkout
labels:
  team: payments
slos:
  - name: availability
    objective: 99.9
    description: "Checkout request success rate over 30 days."
    sli:
      events:
        error_query: sum(rate(http_requests_total{job="api-checkout",code=~"5.."}[{{.window}}]))
        total_query: sum(rate(http_requests_total{job="api-checkout"}[{{.window}}]))
    alerting:
      name: CheckoutAvailability
      page_alert:
        labels: { severity: page }
      ticket_alert:
        labels: { severity: ticket }
```

### Phase 5 — Error-budget policy

The SLO is half the system. The other half is what the team **does** when the budget is exhausted. Without an explicit policy this is the most common failure mode of SLO programs: the budget runs out, nobody notices, business as usual continues, and the SLO becomes decorative.

Draft a policy with the following four sections. Keep it under one page.

1. **Budget healthy (>50% remaining):** Normal operations. No restrictions on feature work or releases.
2. **Budget warning (10–50% remaining):** Soft restrictions. The service owner reviews planned changes for risk. Any change with rollback complexity > trivial must get a second reviewer.
3. **Budget exhausted (0–10% remaining):** Hard restrictions. Feature freeze for the affected component. The team must spend at least 50% of capacity on reliability work (test gaps, runbook gaps, missing monitors) until the budget recovers above 25%. Releases require explicit sign-off.
4. **Budget overrun (negative):** Stop-the-line. Pause non-reliability work, post-incident review the period, and escalate to the engineering lead. No releases without a written exception.

The policy must name a **decision-maker** — usually the engineering manager or staff engineer who owns the service. If nobody can pull the freeze handle, the policy is theater.

### Phase 6 — Governance and review cadence

Set a recurring review at three cadences:

- **Weekly (15 min, on the team):** Look at burn-rate over the last week, page volume, any alerts that fired but were ignored. Adjust runbooks and noisy alerts.
- **Quarterly (60 min, with the eng manager):** Reset targets if the service has changed materially. Decide whether to tighten or loosen any SLO. Review the budget policy — did we actually follow it?
- **Annually (with leadership):** Confirm the SLO portfolio still maps to the company's most important user journeys. Retire SLOs for retired journeys.

## Inputs

- **Required:** a description of the service, its critical user journeys, and the architecture/dependencies.
- **Recommended:** current alert configuration, recent incident summaries, existing telemetry sources, and any contractual SLAs.
- **Optional:** team size and on-call rotation maturity (used to calibrate target ambition).

## Outputs

A single markdown document with these sections, in this order:

1. **Journey map** — 2–5 user journeys with criticality classification.
2. **SLI catalog** — for each journey, the SLI type, the precise definition of "good" and "valid", and a sample query in the user's metrics dialect (Prometheus by default).
3. **SLO targets** — target percentage, window, implied monthly error budget in minutes and in events.
4. **Burn-rate alerts** — multi-window multi-burn-rate alert rules, either as Prometheus YAML or as a Sloth/OpenSLO spec.
5. **Error-budget policy** — a one-page policy with the four budget states and the named decision-maker.
6. **Rollout plan** — a 90-day plan: week 1–2 wire up SLIs and dashboards, week 3–4 dry-run alerts in a ticket-only channel, week 5–8 turn on paging and tune, week 9–12 publish budget policy and start weekly reviews.

## Examples

### Example 1 — B2B SaaS API, no existing SLOs

User says: *"We're a Series B SaaS. Our API has 40 endpoints. We have Datadog dashboards but no SLOs. We just got our first enterprise contract with a 99.9% SLA. Where do we start?"*

Recommended response shape:

- Push back on the 40-endpoint framing. Ask: of those 40, which 3–4 are on critical user journeys? Likely: authenticate, create resource, list resources, webhook delivery.
- Propose four SLIs: availability + latency for auth and create-resource (user-facing critical, target 99.95% availability and 99% latency under 500ms); availability for list and webhooks (less critical, 99.9% and 99% respectively).
- Since contractual SLA is 99.9%, internal SLO must be 99.95% on the critical-path SLIs.
- Generate Sloth spec output.
- Stage rollout: start with one SLO (auth availability) for 30 days before adding the others.

### Example 2 — Batch pipeline, mature team

User says: *"We run a nightly ETL that 12 downstream teams depend on. We have Prometheus. We have on-call. We want SLOs but our service isn't request/response."*

Recommended response shape:

- The right SLI type here is **freshness** ("dataset X is updated by 08:00 UTC on 99% of days") plus **coverage** ("99.5% of expected partitions present").
- Reframe "availability" away from request success and toward the user-visible promise: "the dashboards downstream teams check at 9am are based on data no older than 24 hours."
- Burn-rate alerts on a 7-day window are more useful than 30-day for a daily job.
- Error-budget policy here translates to: more than 2 missed runs per quarter triggers a structured review with the downstream teams.

## Limitations

- **Not a metrics-tooling guide.** This skill assumes the user can express SLIs in their existing tooling (Prometheus, OTel, Datadog, etc.). It does not instrument code.
- **Not for one-off availability calculations.** If the user just needs "what's our uptime last month", this is overkill; point them at a simpler computation.
- **Not for capacity planning.** Saturation and headroom belong in a separate analysis; an SLO measures the outcome, not the underlying resource pressure.
- **Burn-rate alert thresholds are starting points, not laws.** After 30–60 days of real traffic, the team will need to adjust (especially the slow-burn threshold for low-traffic services where 5-minute windows are statistically noisy).
- **Low-traffic services need different math.** If the service handles fewer than a few hundred requests per hour, the 5-minute window contains too few samples to be meaningful — use longer minimums or switch to a synthetic-prober SLI.

## Sources

- Google SRE Workbook — Alerting on SLOs: https://sre.google/workbook/alerting-on-slos/
- OpenSLO specification (Apache-2.0): https://github.com/OpenSLO/OpenSLO
- Sloth — Prometheus SLO generator (Apache-2.0): https://github.com/slok/sloth
- Prometheus alerting rules documentation (Apache-2.0): https://github.com/prometheus/prometheus
- kube-prometheus example SLO/alert manifests (Apache-2.0): https://github.com/prometheus-operator/kube-prometheus
- Awesome Prometheus Alerts community rule catalog (MIT/CC-BY): https://github.com/samber/awesome-prometheus-alerts
