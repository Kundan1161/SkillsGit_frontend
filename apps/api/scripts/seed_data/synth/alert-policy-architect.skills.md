---
id: skillsgit-curated/alert-policy-architect
version: 1.0.0
name: Alert Policy Architect
description: Design an alert taxonomy across page/ticket/email/dashboard channels with severity, routing, deduplication, escalation, and an alert-fatigue audit.
authors:
  - name: Wave-3 Methodology Synthesis
    handle: wave3-observability-sre
    role: author
category: engineering
tags:
  - niche:observability-sre
  - alerting
  - on-call
  - alert-fatigue
  - alertmanager
  - escalation
  - runbook
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
  - alert policy
  - alert taxonomy
  - alert routing
  - on-call
  - paging
  - alertmanager
  - pagerduty
  - alert fatigue
  - escalation policy
  - runbook annotation
example_invocations:
  - "Our on-call gets paged 40 times a week and most are noise. Help us fix it."
  - "We need an alert policy doc for a new team. Page vs ticket vs email — how do we decide?"
  - "Design routing and escalation for two teams sharing one Alertmanager."
  - "Audit our PrometheusRule files for alert fatigue."
inputs:
  - name: current_alerts
    type: text
    required: true
    description: A list, dump, or description of existing alerts — names, severities, runbook links, how often each fired in the last 30–90 days if known.
  - name: team_context
    type: text
    required: true
    description: How many teams own alerts, on-call rotation structure, paging tool (PagerDuty, Opsgenie, etc.), and acceptable noise targets (e.g. "no more than 2 pages per on-call shift").
  - name: severity_definitions
    type: text
    required: false
    description: Any existing severity matrix or SEV1/SEV2 definitions. If absent, the skill will propose one.
outputs:
  - name: alert_policy
    type: markdown
    description: A complete alert policy with severity matrix, channel routing, dedup/grouping config, escalation chains, runbook requirements, and a fatigue-audit checklist applied to the current alerts.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release covering severity taxonomy, Alertmanager routing/inhibition patterns, escalation policy design, and a 12-point fatigue audit.
---

# Alert Policy Architect

## When to use

Use this skill when an SRE or platform engineer needs to design or repair the **alerting policy** — the rules for which alerts exist, where they go, how they escalate, and how they get retired. Trigger this skill for any of the following:

- "Our pager is constantly going off and most of it is noise." (alert fatigue audit)
- "We need a shared alert policy across multiple teams sharing one paging tool." (multi-tenant routing)
- "How do we decide whether something pages or tickets?" (severity taxonomy)
- "We're migrating from Opsgenie to PagerDuty — what's the right escalation policy structure?"
- "Every alert needs a runbook. How do we enforce that?"

Do **not** use this skill to design the SLOs themselves — use `slo-designer` for that. SLO burn-rate alerts are *consumers* of this policy. Also do not use this for incident response (use an incident-commander skill) or for postmortem detection-gap analysis on a specific incident (use a detection-tuner skill).

## How to apply

Work through five phases. Save anything you've heard from the user verbatim — alert policy is dense and easily contradicted by an offhand comment.

### Phase 1 — Establish the severity matrix

Most teams either have no severity definitions or they have eight levels and use two of them. Insist on **exactly four severities**, mapped to **exactly four delivery channels**. Anything else hides at the margins.

| Severity | When it applies | Channel | SLA |
| --- | --- | --- | --- |
| **SEV1 — Page** | User-visible impact happening now, or SLO fast-burn fired | Phone/SMS to on-call, escalation in 5 min | Ack ≤ 5m, response ≤ 15m |
| **SEV2 — Page (business hours) or escalate-to-page** | User-visible impact likely soon, SLO slow-burn, or critical-path component degraded | Push notification, voice escalation after 15 min | Ack ≤ 15m, response ≤ 1h |
| **SEV3 — Ticket** | Internal degradation, capacity warnings, scheduled-budget concerns | Auto-created ticket in tracker, assigned to team queue | Triaged within 1 business day |
| **SEV4 — Dashboard / informational** | Noteworthy but not actionable now — trends, deprecation notices | Dashboard panel, weekly digest email | Reviewed weekly |

Two principles to enforce:

- **No severity above SEV1.** Adding "SEV0" or "P0" inevitably stratifies SEV1 into "real SEV1" and "fake SEV1" and people learn to ignore SEV1. If something requires waking up the CTO, use SEV1 plus an escalation step.
- **No severity that pages without a runbook.** If there is no runbook, the alert is not ready to page. Either write the runbook or downgrade to a ticket.

### Phase 2 — Define the alert lifecycle

Every alert lives in one of four states. Make this explicit; it changes behavior.

1. **Proposed** — defined in code but routed only to a dry-run channel (e.g. `#alerts-dryrun` in Slack, or a SEV4 sink) for at least 14 days. Used to measure firing frequency before promotion.
2. **Live** — routed to its intended severity. Must have a runbook. Must have an owner team label.
3. **Snoozed** — temporarily silenced (named incident, planned maintenance, known bug with ticket). Must have an expiry — no indefinite silences.
4. **Retired** — removed from code. Tombstone entry in the policy doc so people know why it left.

A lot of fatigue comes from alerts that should have been in **Proposed** for two weeks but went straight to **Live**. The promotion bar is a single PR with the firing data attached.

### Phase 3 — Routing, grouping, deduplication

Use Alertmanager (or the equivalent in PagerDuty / Opsgenie) routes hierarchically. A working pattern that scales to ~50 services across ~10 teams:

```yaml
route:
  receiver: default-ticket
  group_by: [alertname, cluster, service]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    # Severity overrides
    - matchers: [severity="page"]
      receiver: pagerduty-default
      group_wait: 0s
      group_interval: 5m
      repeat_interval: 30m
      routes:
        - matchers: [team="payments"]
          receiver: pagerduty-payments
        - matchers: [team="platform"]
          receiver: pagerduty-platform
    - matchers: [severity="ticket"]
      receiver: jira-default
      routes:
        - matchers: [team="payments"]
          receiver: jira-payments
    - matchers: [severity="dashboard"]
      receiver: slack-dashboard-only
```

Three knobs that matter more than the rest:

- **`group_by`** — group by `alertname` plus the topology dimension that makes sense (cluster, region, service). If you group on too much (every label), each instance becomes its own page. If you group on too little (just `alertname`), a multi-region outage shows up as one page and on-call doesn't see the blast radius.
- **`group_wait` and `group_interval`** — `group_wait` of 30s for pages, longer for tickets. Lets correlated alerts coalesce before delivery.
- **`repeat_interval`** — for pages, 30 minutes is usually right (long enough to act, short enough to re-page if missed). For tickets, 4–24 hours; for dashboard, never.

**Inhibition rules** silence dependent alerts when a parent fires:

```yaml
inhibit_rules:
  - source_matchers: [alertname="ClusterDown"]
    target_matchers: [severity=~"page|ticket"]
    equal: [cluster]
```

If the cluster is down, you do not want sixty pages for sixty services on that cluster. Each parent alert (cluster down, region down, dependency hard down) should inhibit its children.

### Phase 4 — Escalation policy

Every paging channel needs an escalation chain. A safe default:

| Step | After | Action |
| --- | --- | --- |
| 0 | 0 min | Primary on-call (phone + push) |
| 1 | 5 min unack | Primary on-call (second attempt + SMS) |
| 2 | 10 min unack | Secondary on-call (phone + push) |
| 3 | 20 min unack | Team lead (phone) |
| 4 | 30 min unack | Engineering manager (phone) |
| 5 | 45 min unack | Director / company-wide incident channel |

Three rules:

- **Primary always escalates to secondary, never to "the team channel".** Channels don't get woken up. Specific humans do.
- **Step 5 must terminate at a human who can declare a SEV1 incident**, not at a group inbox.
- **The chain must be testable.** Run a fake page through it monthly; if anyone in the chain has left the company or doesn't know they're in it, fix it before you need it.

For multi-team setups, give each team its own escalation policy and have the routing tree pick the right one based on the `team` label. Do not have a single global chain; it loses ownership signals.

### Phase 5 — Runbook contract

Every alert above SEV4 must have a `runbook_url` annotation that points to a page satisfying these minimums:

1. **One-sentence symptom.** "Checkout p99 latency exceeded 1s for 5 minutes."
2. **One-sentence likely cause.** Updated by whoever resolves the alert when it fires.
3. **Three actions to triage in the first 5 minutes.** Specific commands, dashboard links, log queries.
4. **Escalation path.** Who to wake up next.
5. **Known false-positive conditions.** When you can safely close the alert without action.

A runbook URL that 404s is worse than no URL — auditing tooling should fail CI if any alert points to a missing or empty runbook. The Prometheus Operator runbook collection is a good reference for shape, even if the content doesn't match your system. The `runbook_url` annotation is the conventional key in Prometheus alerting.

### Phase 6 — Alert-fatigue audit (12 questions)

Run this audit against the current alerts inventory. Score each alert; alerts failing two or more questions are candidates for retirement, downgrade, or rework.

1. **Did this alert fire in the last 90 days?** If never, it is decorative. Retire or move to dashboard.
2. **Did at least 80% of firings result in an action by the responder?** If not, it is noisy. Downgrade or tune thresholds.
3. **Is the median time from firing to acknowledgement under the severity SLA?** If not, either the severity is too high (alert isn't actually urgent) or routing is broken.
4. **Does the alert have a working runbook URL?** If not, it cannot page.
5. **Does the alert have an owner team label?** If not, it cannot route.
6. **Is the alert symptom-based** (user-visible) **or cause-based** (a specific resource exceeded a threshold)? Symptom-based is preferred for pages; cause-based for tickets.
7. **Could this alert be derived from an SLO burn-rate** instead of an ad-hoc threshold? If yes, do so.
8. **Are there sibling alerts on the same condition** (e.g. `cpu_high` and `cpu_critical`)? Collapse to one with severity routing.
9. **Does the alert fire during deploys** as a false positive? If yes, gate on `for: 5m` or exclude `during_deploy=1` label.
10. **Has anyone silenced this alert indefinitely** anywhere? An indefinite silence is a vote to retire.
11. **Is the alert tied to a specific time-zone working pattern** (e.g. nightly batch finishing late)? If yes, severity should be SEV3, not page.
12. **If this alert went away, what would we lose?** If the answer is "nothing concrete", retire.

Produce the audit as a table with one row per alert and the failing question numbers in the rightmost column.

## Inputs

- **Required:** current alerts (names, severities, runbook links, firing counts if available); team and on-call structure; paging tool.
- **Recommended:** PagerDuty/Opsgenie configuration export, Alertmanager `route` config, last quarter's on-call surveys or retros.
- **Optional:** existing severity matrix, existing runbook template.

## Outputs

A single markdown document with:

1. **Severity matrix** — the four-severity table tailored with the user's channel names (PagerDuty service IDs, Slack channels, ticket queues).
2. **Routing tree** — an Alertmanager `route` config or PagerDuty service-team mapping, with `group_by`, intervals, and inhibition rules.
3. **Escalation chains** — one per team, with humans named (or placeholders the user fills in).
4. **Runbook contract** — the five required sections plus a template the team can copy.
5. **Lifecycle process** — how alerts go from Proposed → Live → Retired, including the PR template and the dry-run channel.
6. **Fatigue audit** — the 12-question table applied to the user's current alerts, with concrete recommendations (retire, downgrade, tune, rework).
7. **Adoption plan** — a 30/60/90 day rollout.

## Examples

### Example 1 — "We get 40 pages a week, mostly noise"

User provides a dump of 70 alert names from a PrometheusRule file. Recommended shape:

- Apply the fatigue audit. Typical result: ~25% are decorative (never fire), ~30% are noisy (fire but result in no action), ~30% are cause-based pages that should be tickets, ~15% are legitimate.
- Propose retiring the 25% decorative outright.
- Propose downgrading the 30% noisy to ticket or dashboard.
- Reframe the 30% cause-based as either SLO burn-rate pages (for symptom-side coverage) or tickets.
- Project page volume after the change: ~6–8 pages per week. Note: this is the target, not the immediate result; tuning takes 60 days.

### Example 2 — Multi-team Alertmanager

User has two teams (payments, platform) sharing one Alertmanager and one PagerDuty account. Recommended shape:

- Require every alert to carry `team` and `severity` labels. Provide a CI lint that fails the PR if missing.
- Tree: severity branches first (page vs ticket vs dashboard), then team branches inside page. This puts the strongest matcher first and makes routing reviews easy.
- One PagerDuty service per team, one escalation policy per team.
- Shared inhibition rules for cluster/region-level parent alerts.

## Limitations

- **Does not write SLO alerts directly.** Defer those to the SLO designer skill. This skill specifies the *taxonomy and routing* into which SLO alerts plug.
- **Tool-agnostic but Alertmanager-flavored.** Examples are in Prometheus Alertmanager YAML. PagerDuty Event Orchestration and Opsgenie Policies map cleanly but the syntax differs.
- **Not a postmortem skill.** "Why did we miss this incident?" is detection-gap analysis, which belongs in a separate skill that consumes the postmortem timeline.
- **Cannot predict the right page-volume target.** Use organizational norms (typical mature SRE teams aim for ≤2 pages per on-call shift) and adjust empirically over 60–90 days.
- **Inhibition rules can hide real incidents.** Audit inhibitions quarterly — a parent that always fires masks every dependent alert under it.

## Sources

- Prometheus Alertmanager routing & inhibition docs (Apache-2.0): https://github.com/prometheus/prometheus
- kube-prometheus alert routing examples (Apache-2.0): https://github.com/prometheus-operator/kube-prometheus
- Awesome Prometheus Alerts — community alert rule catalog (MIT/CC-BY): https://github.com/samber/awesome-prometheus-alerts
- Google SRE Workbook — Alerting on SLOs (the symptom-vs-cause framing): https://sre.google/workbook/alerting-on-slos/
- Sloth — burn-rate alert generator showing severity labels (Apache-2.0): https://github.com/slok/sloth
- OpenSLO spec — `alertPolicy` shape and severity conventions (Apache-2.0): https://github.com/OpenSLO/OpenSLO
