---
id: skillsgit-curated/load-test-planner
version: 1.0.0
name: Load Test Planner
description: Design a load test for a target system — workload model, traffic shapes, ramp/soak/spike/break, acceptance criteria, and the telemetry that has to be in place before you press start.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:performance, load-testing, stress-testing, capacity-planning, slo, benchmarking, reliability, scaling]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  tools_optional: [web_search, code_execution]
  min_context_tokens: 24000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - load test plan
  - design a load test
  - stress test plan
  - capacity test
  - soak test
  - spike test
  - break test
  - performance test plan
  - workload model
  - traffic shape
  - peak hour test
  - black friday test
  - pre-launch perf test
  - benchmark plan
example_invocations:
  - "Design a pre-launch load test for our new checkout API. We expect 5x our current peak."
  - "Plan a 24-hour soak test and tell me what to watch for."
  - "I need a spike test that simulates the marketing push next month."
inputs:
  - name: system_under_test
    type: text
    required: true
    description: What the test is targeting — service or path, technology, dependencies, current traffic shape if known.
  - name: objective
    type: choice
    required: false
    description: Why the test is being run; drives the shape and the acceptance criteria.
    choices: [pre-launch, regression-check, capacity-planning, scalability-find-the-limit, soak-stability, spike-resilience, dependency-failure-resilience, unknown]
  - name: traffic_baseline
    type: text
    required: false
    description: Current production traffic — rps, peak hours, geographic spread, ratio of read to write, session length.
  - name: target_envelope
    type: text
    required: false
    description: The traffic envelope the test should cover — expected peak, growth assumptions, marketing event volume.
  - name: environment
    type: text
    required: false
    description: Where the test will run — pre-prod replica, isolated tenant, prod with shadow traffic. Includes data realism notes.
  - name: budget
    type: text
    required: false
    description: Time, money, and risk budget; lets the skill scale the plan up or down.
outputs:
  - name: test_plan
    type: markdown
    description: Full plan with workload model, traffic shapes, ramp/soak/spike/break stages, environment requirements, telemetry checklist, acceptance criteria, and abort criteria.
  - name: runbook
    type: markdown
    description: Operator-facing runbook with go/no-go checks, the start-of-test announcement template, the abort procedure, and the report template for after the run.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Load Test Planner

## When to use

Use this skill when a system needs a load test and the team has not yet written down what "the test" actually is. It is the right skill for the moment a leader says "we should load-test this before launch" or "let's make sure we can handle the marketing event" — the moment before someone opens a load-tester and starts firing requests. The skill produces the plan; another agent or a human runs the test.

The skill is designed for distributed HTTP and gRPC services with traditional request-response shapes, for background-job pipelines fed by a queue, for streaming APIs, and for any system whose performance is bottlenecked on a small number of measurable resources (CPU, memory, IO, connections, database, downstream). It is not the right skill for browser-rendering performance (use a web-performance-audit skill) or for the per-query latency of a single SQL statement (use a query-optimizer skill).

It is opinionated about three things. First, every load test starts with a workload model — a description of who the users are and what they do — rather than a tool invocation. Second, every load test has an acceptance criterion that is a function of percentiles and time, not averages. Third, every load test has an abort criterion that triggers automatically; tests are not babysat by humans pressing the stop button when something looks wrong.

The skill assumes the target system already has working observability. If it doesn't, the first half of the plan is "instrument the system" and the load test does not run until that is done.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `system_under_test` | yes | What is being tested, its shape, its dependencies. |
| `objective` | no | Why; drives the test shape and acceptance criteria. |
| `traffic_baseline` | no | The current production volume; lets the test set realistic targets. |
| `target_envelope` | no | The peak the test should cover; lets the test set the ceiling. |
| `environment` | no | Where the test runs and how realistic the data is. |
| `budget` | no | The time, dollars, and risk available; lets the skill cut scope sensibly. |

If `objective` is missing, the skill asks. Different objectives produce very different plans; running a soak test when the team wanted a capacity-finder is a waste of a day.

## Outputs

The skill produces two artifacts.

The `test_plan` is the test design document. It includes the workload model, the traffic shape, the staged sequence of runs (ramp, peak, soak, spike, break), the environment requirements, the telemetry checklist that has to be green before the test runs, the acceptance criteria for each stage, and the abort criteria that will stop the test automatically.

The `runbook` is the operator-facing companion. It lists the go/no-go checks, the announcement template the on-call sends before pressing start, the abort procedure, and the report template for after the run. The runbook is short on purpose; it is meant to be skimmable at three in the morning if the test has to be re-run.

## How to apply

The agent works through the nine-step planning procedure. Steps are sequential because later steps depend on earlier choices.

### Step 1 — Restate the objective in one sentence

The agent writes a single sentence describing why the test exists. Sample shapes:

- "Confirm the checkout API holds p99 under 600ms at 2x current peak for 30 minutes before the holiday-launch deploy."
- "Find the peak RPS at which the search service violates its SLO so the capacity-planning model can be calibrated."
- "Verify the order-events worker drains a 4-hour backlog in under one hour without restarts."

If the team has stated multiple objectives, the agent splits them. A single test should answer one question. Mixed-objective tests produce mixed evidence.

### Step 2 — Build the workload model

A workload model describes the population of virtual users and what each one does. The agent writes:

- The user mix. What kinds of users send what kinds of traffic? On an e-commerce backend, the mix might be 70% anonymous browsing, 20% logged-in browsing, 8% adding to cart, 2% checking out. Each user-class has its own request pattern.
- The session shape. How long does a typical session last, and how many requests does it make? A test that fires 10,000 single-request virtual users behaves very differently from one that fires 1,000 users each making 10 requests over a session.
- The data distribution. What does the input data look like? A search workload that always queries the most popular term tests the cache, not the search engine; a workload that queries a uniform distribution tests the engine. Both are legitimate but they answer different questions.
- The think time. What's the pause between requests within a session? A test with zero think time is a closed-loop stress test and is the right shape for some objectives; a test with realistic think time is an open-loop simulation and is the right shape for others.

The model is open-loop or closed-loop. Open-loop means arrival rate is independent of system response time — request 100 happens at second 100 whether or not request 99 finished. Closed-loop means each virtual user waits for the response before sending the next request. Open-loop is the better model for most production-realistic tests because real users do not wait for your queue; choosing closed-loop accidentally is one of the most common mistakes in load testing.

The agent writes the model as a table the user can argue with: user-class, share, requests-per-session, think-time-distribution, key inputs.

### Step 3 — Pick the right traffic shape

Different objectives need different shapes. The agent maps objective to shape:

- **Pre-launch acceptance test** — a steady-state run at the target peak rate for a defined duration (commonly 30 to 60 minutes), with a short ramp.
- **Soak / stability test** — a steady-state run at a moderate rate (often 60-80% of expected peak) for 4 to 24 hours, designed to surface slow leaks, slow growth, and dependency rate-limit accumulations.
- **Capacity-finder test** — a stepwise ramp that increases load every N minutes until the acceptance criterion breaks, then holds for one step beyond to confirm.
- **Spike test** — a baseline rate for warm-up, then a sudden multiplier (2x, 5x, 10x) within seconds to simulate a marketing burst or a thundering herd. Tests autoscaling reactiveness and connection-pool elasticity.
- **Break test** — load increased until something obvious fails; the goal is to characterize the failure mode (graceful degradation vs. cascade vs. cliff) rather than to claim a number.
- **Dependency-failure resilience test** — steady load while a dependency is degraded or removed; tests circuit breakers, timeouts, fallbacks.

The agent writes the shape as an ASCII diagram or table indicating rps over time, the duration of each stage, and the transition between stages.

### Step 4 — Sketch the staged sequence

A real test session is rarely a single shape — it is a sequence. The agent designs a sequence in this order:

1. **Smoke** — five minutes at very low load with full assertions on, designed to catch broken test scripts and broken environments. If smoke fails the rest of the test is aborted.
2. **Ramp** — gradual increase to the target rate over five to twenty minutes. The ramp surfaces autoscaling lag and cold-cache effects; do not start at peak.
3. **Steady-state at peak** — the body of the test. Duration depends on objective: thirty minutes for an acceptance test, multiple hours for a soak.
4. **Spike (optional)** — a short burst above peak to simulate worst-case bursts within the peak window.
5. **Cool-down** — gradual decrease for ten minutes so the team can observe recovery — connection pools draining, queues clearing, CPU returning to idle.

The agent annotates each stage with its purpose and what would constitute a stage-level failure.

### Step 5 — Choose the environment and data plane

The agent assesses environment realism along four dimensions:

- **Topology** — same number of replicas, same instance class, same network topology as production? Tests on under-scaled environments give optimistic results because the math doesn't translate linearly.
- **Data shape** — production-sized tables, realistic data skew, realistic cache state. A test against an empty database tests query parsing, not query performance.
- **Dependencies** — real downstream services, stubbed services, or recorded responses? Each is legitimate; the trade-off is fidelity vs blast radius.
- **Traffic origin** — load injected from one box, multiple boxes, or geographically distributed boxes? Single-origin tests can be limited by the load-generator's own networking before they limit the target.

The agent recommends the most realistic environment that fits the `budget`. When the team must test in production (which is sometimes the only realistic option) the plan includes shadow-traffic patterns, percentage rollouts, and a clear separation of test users from real ones.

### Step 6 — Define acceptance and abort criteria

This is the step the skill cannot let the user skip. The agent writes two criteria:

The **acceptance criterion** describes what success looks like at the end of the steady-state stage. It is always a function of percentiles over time, never a function of an average. Sample shape: "p95 of `/checkout` POST under 400ms and p99 under 1.0s, error rate under 0.1%, sustained for the full 30-minute steady-state window."

The **abort criterion** is what stops the test before it damages the environment. The criterion is automated — the load generator or the orchestrator monitors it and halts the run. Sample shapes:

- Error rate above 5% sustained for 60 seconds.
- p99 above 5.0s sustained for 60 seconds.
- Any dependency's published SLO blown by 50% sustained for 60 seconds.
- CPU on the database master above 90% sustained for 5 minutes.
- Any alert page firing for a non-test service.

Without abort criteria, a stress test can take down adjacent systems. The criteria are part of the runbook, and the test does not start until the orchestrator has them wired up.

### Step 7 — Build the telemetry checklist

Before the test can run, certain telemetry must be in place. The agent writes the checklist as a pre-flight document the on-call signs off:

- Latency histograms (not roll-ups) on every relevant route, with at least 1-second resolution.
- Error rates broken down by error class.
- Request rate, with tagging by user-class or endpoint.
- Resource metrics on every component of the system — CPU, memory, disk IO, network bytes, file descriptors.
- Connection-pool metrics — waiting threads, active connections, timeouts.
- Queue and backlog metrics on every async boundary.
- Garbage collection metrics for managed runtimes — pause time, frequency, generation sizes.
- Saturation metrics on every shared resource — locks, connection pools, thread pools, semaphores.
- Distributed-traces sampled at the slow tail (not random sampling), with the test traffic tagged.
- A dashboard the operator can watch live during the test, with the abort-criterion thresholds drawn on the panels.

The agent flags any missing instrument as a blocker for the test. Running a load test without saturation metrics is running blind.

### Step 8 — Plan the run logistics

The agent writes the operational details:

- Who is on the call and what their role is (operator, observer, owner of each dependency).
- Communication channels and the announcement-before-press-start template.
- The window in which the test will run, chosen to minimize blast radius (low traffic period, low-deploy day).
- A pre-test dry run if the test plan itself is new.
- The abort procedure: who can call abort, the exact button to press, what happens after abort.
- A post-run cleanup checklist — synthetic data deletion, cache invalidation, log archival, dashboard snapshotting.

The agent writes the announcement template the operator will paste into the team's channel before each stage transition. Templates remove ambiguity at moments of stress.

### Step 9 — Plan the report

The test is not done when the load generator stops; the test is done when the report is written. The agent writes the report template now, so the operator knows what evidence to collect during the run.

The template includes: objective restated, plan summary, the actual numbers per stage (p50/p95/p99 latency, error rate, throughput, CPU/memory/IO peaks), the comparison to the acceptance criterion (pass/fail), any abort events with their cause, the bottlenecks identified, the hypotheses for follow-up, and the change-list for the next test run.

The report does not include "we ran the test and it was fine." Either acceptance criteria were met, with the numbers shown, or they were not, with the numbers shown.

## Workload model worked example

**Input:** `system_under_test` is a checkout API for an e-commerce site. `objective` is pre-launch acceptance for a holiday-week feature. `traffic_baseline` is "average 200 rps, peak 800 rps." `target_envelope` is "expect 4000 rps peak during the launch event."

**Workload model output (abbreviated):**

| User-class | Share | Session length | Think time | Key inputs |
| --- | --- | --- | --- | --- |
| Browse-only | 55% | 8 reqs | 5-15s lognormal | search terms drawn from 100k pool, weighted by popularity |
| Cart-builder | 30% | 12 reqs | 4-12s lognormal | mix of browse, add-to-cart, view-cart |
| Checkout-completer | 13% | 9 reqs | 6-20s lognormal | full funnel; payment uses test card with 1% failure injection |
| Refresher | 2% | 30 reqs | 2-5s uniform | repeated polling of a single page; simulates "did my order go through?" anxiety after a slow page |

Open-loop arrivals at the target rate, randomly assigned to a user-class according to the share column.

Sessions are sticky to a virtual user identity for the duration of the session so authentication tokens, server-side cart state, and customer-id-based sharding behave realistically.

Data inputs are drawn from a pre-generated dataset committed alongside the test scripts, so the test is reproducible across runs.

## Traffic shape worked example

For the same checkout test the shape is:

| Stage | Duration | Target rate | Purpose |
| --- | --- | --- | --- |
| Smoke | 5 min | 20 rps | catch broken test, broken environment |
| Ramp | 15 min | 20 → 4000 rps | exercise autoscaling, warm caches |
| Steady-state | 30 min | 4000 rps | acceptance |
| Spike | 90 s | 4000 → 6000 rps | within-peak burst |
| Steady-state | 10 min | 4000 rps | recovery from spike |
| Cool-down | 10 min | 4000 → 50 rps | observe recovery |

Acceptance criterion: during the 30-minute 4000-rps steady-state, p95 of `POST /checkout` under 400ms, p99 under 1.0s, error rate under 0.1%.

Abort criteria as in step 6.

## Reading load-test results without getting fooled

The agent applies the following rules when interpreting results.

Averages lie. The mean of a bimodal distribution may be at a value almost no request actually had. Always report percentiles.

Coordinated omission distorts results in closed-loop tools. When a request takes long, the closed-loop tool does not send the next requests during the wait — so the percentile is computed only on the requests that did get sent, masking the worst latencies. Use a tool or mode that compensates (constant-arrival-rate scheduling) when measuring tail latency.

A single load-generator can become the bottleneck. Saturate the generator before the target and you'll claim the target is faster than it is. The plan includes a pre-check that the generator has headroom.

Warm caches mask cold-start behavior. If the test starts after a multi-minute warm-up, the test does not represent the moment after a deploy when caches are cold and the system is most vulnerable. Include a cold-start variant when that's relevant.

Synthetic data hides production-shaped problems. A test that issues a small uniform random distribution of inputs will not trigger the hot-row contention that real traffic will. Either replay recorded traffic or sample from production-shaped distributions.

The right peak is not last year's peak. Capacity tests project forward — the right target envelope accounts for growth between now and when the test's conclusion will be acted on.

Comparison across runs requires that the system, the data, and the test be the same. The agent flags every change between runs in the report; a regression that "shows up" between two runs that differ in three ways cannot be attributed.

## Examples

**Input:**

`system_under_test`: "the checkout API described above." `objective`: pre-launch. `target_envelope`: 4000 rps peak. `environment`: staging replica at 75% of prod scale.

**Agent reasoning:** the environment is under-scaled at 75%. The plan accounts for this — either scale staging up for the test, or design the test as a "this number scaled by 4/3 should hold in prod" target, with the scaling assumption written down. The agent chooses to recommend scaling staging up for the test window, because the linear projection assumption is itself a load-test risk.

**Output:** the full plan described in the worked examples above.

## Worked example two — a soak test

**Input:** `objective` is soak-stability for a long-running queue worker. `traffic_baseline`: typical depth 10k messages, drain rate 200/s. `target_envelope`: 600/s sustained for 24 hours.

**Plan:**

- Workload: messages generated to match the size and shape of production messages, with a fault-injection mode that flips one in 500 messages into a known-bad payload to exercise the dead-letter pipeline.
- Shape: smoke 10 min, ramp 30 min, steady-state 24 hours at 600/s, cool-down 30 min.
- Acceptance: drain rate ≥ 600/s sustained over rolling 5-minute windows; memory steady-state with no growth in the last 6 hours; no worker restarts unrelated to deploys; DLQ depth ≤ 0.2% of total processed.
- Abort: drain rate below 400/s sustained for 10 minutes; any unbounded memory growth; an underlying dependency outage longer than 5 minutes.
- Telemetry: heap usage, GC time, queue depth and age, per-message processing histogram, downstream call latency, fd count, restart counter.
- Logistics: start Monday 21:00 local to minimize overlap with deploys; on-call rotation acknowledged.

## Limitations

- The skill plans the test; it does not execute it. Realized numbers depend on the test runner, the environment, and the operator.
- The skill is best for HTTP and queue-driven systems. For database-only benchmarking, browser-side performance, or specialized hardware throughput, additional skills are appropriate.
- The skill cannot tell whether a chosen environment is realistic without information from the user. It will ask, and it will flag environments it considers under-scaled, but the final call is operational.
- Acceptance criteria are only as good as the team's SLOs. If the team does not have SLOs yet, the skill proposes interim targets but flags them as provisional.
- The skill does not design fault injection beyond simple known-shape inputs. For chaos-engineering plans, prefer a dedicated resilience skill.
- The skill does not produce executable scripts in any specific load-test tool's DSL. It produces a plan; the team or another agent writes the script.
- Long-running tests carry operational risk that the skill cannot quantify without knowing the team's risk appetite. The runbook includes abort criteria but the team must staff the rotation.
- The skill is opinionated about open-loop modeling for realism. Teams whose tooling supports only closed-loop will get a plan annotated with the bias they should expect to see.

## Sources reviewed

- https://github.com/locustio/locust (MIT)
- https://github.com/tsenart/vegeta (MIT)
- https://github.com/rakyll/hey (Apache-2.0)
- https://github.com/codesenberg/bombardier (MIT)
- https://github.com/giltene/wrk2 (Apache-2.0)
- https://github.com/sharkdp/hyperfine (MIT / Apache-2.0)
- https://github.com/GoogleChrome/lighthouse (Apache-2.0)
