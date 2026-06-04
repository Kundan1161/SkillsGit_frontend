---
id: skillsgit-curated/developer-experience-metrics-designer
version: 1.0.0
name: Developer Experience Metrics Designer
description: Design a DX measurement program that combines DORA, SPACE, and platform-specific metrics (time-to-first-deploy, onboarding time, NPS-style cohorts) without gaming the numbers.
authors:
  - name: Wave-3 Platform Synth
    handle: wave3-platform
    role: author
category: engineering
tags:
  - niche:platform-engineering
  - dora-metrics
  - space-framework
  - developer-experience
  - dx-metrics
  - platform-metrics
  - deployment-frequency
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
    - gpt-4.1
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6800
trigger_keywords:
  - DORA metrics
  - SPACE framework
  - developer experience metrics
  - DX metrics
  - deployment frequency
  - lead time for changes
  - change failure rate
  - MTTR
  - time to first deploy
  - developer NPS
  - platform metrics
example_invocations:
  - "What metrics should we track for our developer platform?"
  - "Help me set up DORA metrics across 30 teams without gaming."
  - "Design a developer NPS survey program for our IDP."
  - "Our deploy frequency went up but quality dropped — how do we measure both?"
inputs:
  - name: platform_stage
    type: text
    required: true
    description: New / scaling / mature platform; rough number of product teams and services under measurement.
  - name: available_signals
    type: text
    required: true
    description: Tooling that can emit data — Git, CI, deployer, incident tool, on-call, observability, survey tool.
  - name: leadership_question
    type: text
    required: false
    description: The specific question leadership keeps asking (ROI, where to invest, why deploys are slow).
  - name: prior_metrics
    type: text
    required: false
    description: What's already measured today and what isn't working (vanity numbers, gaming, low trust).
outputs:
  - name: metrics_program
    type: markdown
    description: A layered metrics program with definitions, instrumentation sources, reporting cadence, and anti-gaming controls.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Developer Experience Metrics Designer

## When to use

Use this skill when a platform team, engineering leader, or VP needs to design (or fix) a **developer experience metrics program** — the set of numbers that prove the platform is working, locate where it isn't, and justify continued investment. The bar is high: most metrics programs either measure the wrong thing, get gamed, or collapse under their own weight.

This skill is the **measurement design** skill. It does not pick analytics vendors and does not build dashboards. It produces a program: which metrics, why, how they're instrumented, how they're reported, and how they're protected from gaming.

Trigger on phrases like:

- "DORA metrics" / "four key metrics"
- "SPACE framework"
- "DX metrics" / "developer experience metrics"
- "deploy frequency" / "lead time" / "change failure rate" / "MTTR"
- "time to first deploy" / "onboarding time"
- "developer NPS" / "developer satisfaction"
- "platform ROI" / "platform success metrics"

Do **not** trigger when the question is about individual developer performance reviews — these metrics are explicitly **team-level**, not individual. Push back firmly if asked to design individual scoring.

## How to apply

Walk the user through five layers of metrics, in order. Each layer answers a different question; together they form the program.

### Layer 1 — DORA (delivery throughput and stability)

The DORA four are the floor of any program. Definitions matter; teams game on definitions.

- **Deployment frequency** — how often code reaches **production**. Count deploys, not merges. Bucket per team per week.
- **Lead time for changes** — time from first commit on a change-branch to the change being live in production. Track median and 85th percentile; the tail matters more than the median.
- **Change failure rate (CFR)** — percent of production changes that result in a rollback, hotfix, or user-impacting incident. Require a linked rollback PR or incident; otherwise it's not counted.
- **Time to restore service (MTTR)** — for user-impacting incidents, time from declaration to "no longer user-impacting". Excludes purely internal disruptions.

Industry buckets (Elite / High / Medium / Low) are a useful sanity check but **stop comparing teams against each other**. Compare each team against its own prior quarter; that's where action lives.

Anti-gaming controls:

- Tie all four to the **same incident/change source of truth** so teams can't define their way to elite.
- Require both **throughput** (deploy frequency, lead time) and **stability** (CFR, MTTR) to be reported together. A team that doubles deploys while CFR doubles isn't winning.
- Roll up per **team** and per **System** (catalog entity), not per individual.

Instrumentation: a deployer (Argo CD, GitHub Actions, Spinnaker) emits deploy events; the incident tool emits incidents; a small ETL (or a tool like Middleware or a homegrown Four-Keys equivalent) joins them. Use the platform's already-mandated deployer to enforce consistent event shape across teams.

### Layer 2 — SPACE (the qualitative complement)

SPACE (Forsgren et al.) widens the lens beyond delivery. Don't try to measure all five dimensions; pick **one signal per dimension** that you can sustain.

- **Satisfaction & well-being** — quarterly developer survey (5-7 questions, < 5 minutes). Include "I would recommend our platform to a new hire" (the developer-NPS prompt) and a free-text "biggest friction this week".
- **Performance** — outcome metric, not output. Examples: percentage of customer-impacting bugs closed within SLA; product KPIs the team owns.
- **Activity** — counts of things done. Useful for spotting load shifts (PRs/week per team), **never** for evaluating individuals.
- **Communication & collaboration** — PR review latency, percentage of services with two+ active maintainers, cross-team contribution counts.
- **Efficiency & flow** — interruption rate (estimated via survey), focus-time hours, context-switch count (proxied by branch switches per day).

Use SPACE to **explain** DORA. When deploy frequency drops, the SPACE signals tell you whether it's because focus-time collapsed, review latency spiked, or satisfaction dropped.

### Layer 3 — Platform-specific funnel metrics

These are unique to a platform team and prove the platform's leverage.

- **Time to first deploy** — wall-clock from "new developer joined / new service scaffolded" to "their code is running in prod". Target hours, not weeks. Measure both flows separately.
- **Time to onboard** — from offer-acceptance to first PR merged. Mostly a hiring metric, but a useful proxy for environment setup pain.
- **Golden-path adoption rate** — percentage of new services in the last quarter that used the supported template. < 70% means the path isn't golden, it's beige.
- **Off-path drift** — count of services that started on a golden path and have since diverged in their CI/deploy/observability setup. Rising drift = upgrade story is broken.
- **Self-service deflection** — ratio of platform features used self-service vs. via ticket. Should trend up over time.
- **Platform-driven security baseline coverage** — percentage of services that pass the baseline scorecard via the platform's pipeline. This is the security team's view of platform ROI.

Each metric needs a **target** and a **direction of travel**, not just a value. "Time to first deploy = 6 hours" is useless without "down from 3 days, target 1 hour".

### Layer 4 — Cohort and per-team views

Aggregate numbers hide everything important. Always show:

- **By team** — to find struggling teams early; pair the metric with an enabling-team intervention, not a blame.
- **By tenure cohort** — new hires (0-3 months) feel friction first; track time-to-first-deploy specifically for this cohort.
- **By service tier** (Tier 1 vs Tier 3) — Tier 1 services should have lower CFR and longer review cycles; collapsing the average masks both.
- **By "uses platform vs. forked off"** — gives the platform team a clean A/B story.

Reporting cadence: monthly for delivery and platform funnel metrics; quarterly for SPACE survey results; never daily — daily noise erodes signal.

### Layer 5 — Protecting the program from gaming and decay

Failure modes to design around:

- **Individual-developer scoring**: forbidden. Document this in the program charter and refuse if leadership asks. SPACE and DORA are team-and-system metrics.
- **Metric inflation through definition drift**: lock the definitions in a one-page wiki and require a CHANGELOG entry to change them.
- **Cherry-picked dashboards**: produce the same monthly report org-wide; do not let individual teams hide their numbers.
- **Survey fatigue**: cap surveys at quarterly; share the results back within two weeks with named actions; otherwise response rate collapses.
- **The "deploys went up, customers complained" trap**: always pair throughput with stability; if CFR rises while DF rises, that's a regression, not a win.
- **Goodhart's law in practice**: when a metric becomes a target it stops being a good measure. Rotate the headline metric every 12-18 months; the program is the constant, the headline is the lens.

### Tie metrics to platform investment

Every quarter, tie one delivered platform improvement to one moved metric. Example narratives:

- "We shipped the Argo CD golden path → deploy frequency up 2.4x for adopting teams, no change in CFR."
- "We rolled out the standard service template → time-to-first-deploy for new services dropped from 9 days median to 6 hours."
- "We auto-merged Renovate PRs for low-risk deps → review latency dropped, satisfaction score for 'time spent on toil' improved."

If you can't tie an improvement to a metric within a quarter, suspect the metric isn't load-bearing.

## Inputs

- **platform_stage** (required): "new (no metrics yet)", "scaling (some DORA, no SPACE)", or "mature (full program, but trust is dropping)". Include rough scope — number of teams and services.
- **available_signals** (required): list each tool you can emit events from — Git host, CI, deployer, incident tool (PagerDuty/Opsgenie/incident.io), observability (Prometheus/Datadog), survey tool, on-call rotation.
- **leadership_question** (optional): the recurring exec question — e.g. "what's the ROI?", "why are deploys slow?", "are we faster than competitors?".
- **prior_metrics** (optional): what's measured today, what's failing — vanity numbers, gamed numbers, low trust, missing data, etc.

## Outputs

A markdown program with this shape:

1. **Program charter** — one paragraph stating the program's purpose, the team-level guarantee (never individual scoring), and the rotation cadence for the headline metric.
2. **Layer 1: DORA** — exact definitions, source of truth per metric, target buckets per team.
3. **Layer 2: SPACE signals** — one chosen signal per dimension, with the survey or telemetry source.
4. **Layer 3: Platform funnel** — chosen metrics with current baseline (if known) and 12-month targets.
5. **Layer 4: Cohort cuts** — which cuts you will publish (by team, tenure, tier).
6. **Layer 5: Anti-gaming controls** — explicit list of guardrails for this org's specific risks.
7. **Reporting cadence and owners** — who produces each artifact, when, and who reviews it.
8. **First 90 days** — what gets instrumented first; what is explicitly deferred.

## Examples

> "We're new. 12 teams. We have Argo CD, GitHub Actions, PagerDuty, Datadog. Leadership wants 'DORA metrics next month'."

Recommendation: ship DORA only in month one, derived from Argo CD deploy events + PagerDuty incidents joined on the catalog System ID. Report per-team monthly. Defer SPACE survey to month three (you need trust first). Lock the four definitions in a one-pager. Add time-to-first-deploy from scaffold to first prod deploy in month two. Explicitly resist any request to compare teams against each other in month one — only "this team this quarter vs last quarter".

> "We have DORA, but our 'lead time' is fantastic because we measure from PR-open to merge, not commit to prod. Leadership thinks we're elite. We're not."

Diagnosis: definition drift. Redefine lead time to commit-to-prod (use the deployer event as the end timestamp), publish the corrected number, and document the prior measurement as deprecated. Expect the visible number to roughly double; the explanation is "we were measuring a subset of the pipeline; this is the true number". Pair this with a SPACE satisfaction signal so leadership can see the metric collapse is honesty, not regression.

> "We do quarterly NPS surveys. Response rate fell from 70% to 22% over four quarters."

Cause is almost always feedback loop failure. Fix in this order: (1) publish the prior survey's results and the actions taken within 10 business days of close; (2) cut the survey to 5 questions; (3) make the platform PM the named owner of the close-the-loop email; (4) skip exactly one quarter to break the pattern and relaunch with a "what changed" preamble.

## Limitations

- The skill is opinionated against individual-developer scoring; if your org requires it, this is the wrong skill — use HR performance frameworks instead.
- Industry "Elite/High/Medium/Low" buckets are heuristics from public DORA research, not laws; your industry's safety profile changes the targets.
- The skill assumes you have a deployer that emits structured events. Without one (or a clear path to one in a quarter), implement the deployer first; the metrics will follow.
- Survey design beyond the developer-NPS prompt is out of scope; consult a research/UX team for instrument validation.
- The skill does not cover cost-per-developer-hour metrics, which are sensitive and should be designed jointly with finance.

## Sources

- https://github.com/middlewarehq/middleware
- https://github.com/backstage/backstage
- https://github.com/cnoe-io/idpbuilder
- https://github.com/score-spec/score-compose
- https://github.com/argoproj/argo-cd
- https://github.com/syntasso/kratix
- https://github.com/apptension/developer-handbook
