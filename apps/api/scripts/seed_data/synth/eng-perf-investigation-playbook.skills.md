---
id: skillsgit-curated/perf-investigation-playbook
version: 1.0.0
name: Performance Investigation Playbook
description: Turn a vague "the service got slow" report into a structured investigation — define the SLO, capture the right profile, find the hot path, and name the offender.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:performance, profiling, latency, slo, flamegraph, debugging, observability, backend]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  tools_optional: [code_execution, web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - service got slow
  - investigate slowness
  - performance investigation
  - latency regression
  - p95 spike
  - p99 spike
  - high cpu
  - flamegraph analysis
  - hot path
  - find the bottleneck
  - tail latency
  - request slow
  - throughput dropped
  - perf playbook
example_invocations:
  - "Our checkout API p99 doubled this morning — walk me through what to look at."
  - "The worker pod is at 90% CPU after the last deploy. Help me find the hot path."
  - "Customers say search feels slow but the dashboard looks green. Investigate."
inputs:
  - name: symptom_report
    type: text
    required: true
    description: What the reporter observed — the route or job, the metric that changed, when it started, who's affected.
  - name: slo_or_target
    type: text
    required: false
    description: The stated SLO or latency budget for the affected path. If absent, the agent will propose a working target.
  - name: telemetry_excerpt
    type: text
    required: false
    description: Metrics screenshots, trace samples, error logs, or a profile dump. Anything quantitative.
  - name: runtime
    type: choice
    required: false
    description: The runtime hosting the slow component. Drives the profiler and offender lists used.
    choices: [jvm, dotnet, nodejs, python, go, ruby, rust, cpp, php, mixed, unknown]
  - name: deploy_context
    type: text
    required: false
    description: Recent deploys, config changes, traffic shifts, or feature flags that flipped in the relevant window.
outputs:
  - name: investigation_plan
    type: markdown
    description: Ordered playbook with the SLO frame, hypotheses ranked by prior, the data each hypothesis needs, and stop-conditions.
  - name: findings_report
    type: markdown
    description: After data is provided back, a written conclusion naming the offender, the evidence chain, and a remediation outline.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Performance Investigation Playbook

## When to use

Use this skill the moment a teammate says "the service got slow" and the cause is not yet obvious. It is built for the messy middle of a latency or throughput incident — after the dashboards have shown that something changed but before anyone can point at a line of code. It works equally well for live incidents and for the slow-burn regression that snuck in over a quarter and only became visible when a single customer complained.

The skill assumes the agent is acting as a senior performance engineer who has been pulled into the call. It does not assume the agent can run commands on the production host. Instead it produces an ordered investigation plan that an on-call engineer (human or another agent with shell access) can execute, and it accepts the data those commands return so it can rank hypotheses and converge on a root cause.

Do not use this skill for a routine micro-benchmark of a single function — for that, the `db-query-optimizer` skill (for queries) or a dedicated benchmark harness is the right tool. Do not use it for one-time capacity planning where there is no incident; use a load-test design skill instead. And do not use it for memory pressure that has already produced a crash dump; that lives in the memory-leak workflow.

The skill is opinionated about ordering. It refuses to chase a profiler before an SLO is named, refuses to chase a hot function before the customer-visible symptom is reproduced, and refuses to ship a fix before there is a falsifiable hypothesis. These are guardrails, not preferences.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `symptom_report` | yes | The story so far — what slowed down, when, on which surface, for whom. |
| `slo_or_target` | no | A named latency or throughput target so the skill knows what "fast enough" means. |
| `telemetry_excerpt` | no | Any data already collected — metrics, traces, profiles, error logs. |
| `runtime` | no | The host runtime; lets the skill pick the right profiler vocabulary and offender list. |
| `deploy_context` | no | Recent changes (deploys, flags, config, traffic) that frame the regression window. |

If `slo_or_target` is missing, the skill writes a working target in its first pass and asks the reporter to confirm it before continuing. Investigations without targets drift.

## Outputs

The skill produces two artifacts:

1. An `investigation_plan` — the ordered playbook below, instantiated for the specific report. Each step has a command to run or question to answer and a stop-condition that tells the executor when to move on.
2. A `findings_report` — after the executor returns data, the skill writes the conclusion. The report names the offender, walks the evidence in causal order, lists the alternatives it considered and ruled out, and proposes a remediation plan with the smallest credible change first.

## How to apply

The agent runs the seven-stage playbook. Each stage gates the next; do not advance past a stage until its exit criterion is met.

### Stage 1 — Frame the symptom and pick the SLO

Before any tool is opened the agent restates the problem in the form: "On surface X, metric M moved from value V1 to V2 starting around time T, affecting population P." If any field of that sentence is missing, that becomes the first question to the reporter.

The agent then names a target. Prefer an existing SLO from the team's catalog; if none exists, propose a working one based on the surface type. Reasonable defaults for an interactive HTTP endpoint are p50 under 100ms, p95 under 400ms, p99 under 1.0s with a stated budget for 30 days. Background jobs use throughput and queue-age targets instead of percentile latency.

The agent ends Stage 1 by writing down the falsifiable claim that will close the investigation. Examples: "after the change, p99 for `/checkout` returns under 600ms for ninety minutes of production traffic at typical volume" or "the worker drains the backlog at greater than 1.2x the arrival rate for two consecutive hours." If the claim cannot be measured, the investigation has no exit. Stop and ask.

### Stage 2 — Reproduce or pin the regression window

The cheapest investigation is the one with a reliable reproducer. Before any deep dive, the agent asks: can the slow behavior be reproduced in a non-production environment, or at least pinned to a specific window in production traffic?

The agent enumerates the possible reproducers in order of cost:

- A single curl or HTTP client request against staging.
- A small load run against staging at the production traffic shape.
- A traffic replay from a captured slice of production.
- Observation of production at the time of day when the symptom appears.

If none of these is available, the agent treats the symptom window as the reproducer and works exclusively from passive telemetry. It marks every later finding as "from passive data" and downgrades confidence accordingly.

If a recent deploy or config change is in `deploy_context`, the agent bisects: did the symptom start within minutes of one of those changes? If yes, treat that change as the leading hypothesis. The agent does not skip Stage 3-5 just because the change looks guilty — but it orders later evidence to confirm or rule it out first.

### Stage 3 — Decide between latency and throughput investigations

The agent classifies the symptom along two axes that have very different toolchains.

Axis A — the metric. Is the complaint about a request-level latency (a single user waiting too long), about a system-level throughput (the backlog growing, the queue draining slow), or about a resource saturation (CPU, memory, IO at the limit)? Each leads to different first instruments.

Axis B — the regime. Is the system under heavy load (saturation suspected), under typical load (a code-path change suspected), or under low load (an inefficiency that was always there but now matters)? Heavy-load investigations prefer first looking at queueing behavior; typical-load investigations prefer first looking at flamegraphs of the hot path; low-load investigations often turn out to be a synchronous external dependency.

The agent writes the classification explicitly into the plan. It avoids treating every problem as a flamegraph problem; many production slowdowns are not CPU-bound and the flamegraph will be a flat sea of `epoll_wait`.

### Stage 4 — Capture the right profile

This is the stage where the agent chooses an instrument. The choice depends on `runtime` and on the classification from Stage 3. The skill never asks for "a profile" generically — it asks for a specific kind.

For CPU-bound suspicion the agent asks for a CPU flamegraph at 99Hz sampling for thirty to sixty seconds while the load that reproduces the symptom is on the box. It accepts on-CPU and off-CPU variants and reads each differently. On-CPU flamegraphs show where the cycles go; off-CPU flamegraphs show where threads sit blocked.

For latency-tail suspicion (p99 worse than the median by a wide factor) the agent asks for distributed traces of the slow tail specifically, not a random sample. Tail-biased trace sampling matters: random sampling will mostly capture the well-behaved median.

For memory-pressure or GC suspicion the agent asks for the runtime's allocation profile (heap profile on JVM, `--prof` allocations on Node, allocs profile on Go, `tracemalloc` snapshots on Python) and for the GC log over the same window.

For lock-contention suspicion the agent asks for the lock or mutex profile (`async-profiler` lock mode on JVM, `pprof` mutex/block profiles on Go, perf lock for native, `perf-trace`) and the contention summary.

For IO-bound suspicion the agent asks for the syscall and IO wait breakdown — what fraction of wall time is spent in epoll, in disk reads, in synchronous network calls.

For each instrument the agent records the cost in production (overhead estimate, sampling interval, blast radius) and the duration of the capture. Profiles taken for too short a window miss the slow tail; profiles taken too long blur the signal.

### Stage 5 — Read the profile against the prior

The agent does not start a flamegraph reading at the leaves. It starts at the customer-visible function — the route handler, the worker entrypoint, the message consumer — and walks downward, asking at each branch whether the time spent there is what an engineer who designed the system would expect.

The agent applies the seven common offender priors, in roughly this order:

1. The "N+1 in disguise" offender — a single user-visible operation that, somewhere on its stack, makes one downstream call per element of a collection. Look for tight loops that call the database client, the cache client, the HTTP client, or an internal RPC. The flamegraph signature is a wide call to a client function under a loop body.
2. The "lock contention" offender — threads waiting on a mutex, on a connection pool, or on a single-flight cache fill. The signature is a tall off-CPU flame on `lock`, `Acquire`, `pthread_mutex_lock`, or pool-checkout functions.
3. The "GC pause" offender — long stop-the-world or concurrent GC cycles that align temporally with the latency spikes. The signature is matching peaks in the GC log and the latency histogram.
4. The "allocation storm" offender — code that allocates on every request when it could allocate once. The signature is a tall column in the allocation profile under request-handler stacks.
5. The "synchronous external IO" offender — calls to a downstream service or third-party API that are part of the critical path of a request that should not depend on them, or whose timeout is unbounded. The signature is a wide leaf of `http`/`grpc`/`requests`/`reqwest`/`fetch` under the handler.
6. The "serialization tax" offender — JSON or protobuf encoding/decoding of payloads larger than expected, often a `SELECT *` that returns way more bytes than the caller uses. The signature is a wide leaf of marshalling functions.
7. The "background work bleeds into foreground" offender — a periodic task scheduled on the same thread pool, runtime, or event loop as the foreground request handlers, so when it runs everyone waits.

The agent matches the observed profile against each prior in turn and records evidence for or against. It does not stop at the first match; it ranks all matches by strength and revisits Stage 6 with the top three.

### Stage 6 — Form a hypothesis and design the falsifying experiment

A hypothesis at this stage has four parts: (a) the offender, (b) the mechanism — why this offender produces the observed symptom, (c) the predicted measurement that should change if the hypothesis is correct, and (d) the minimum experiment that would change that measurement.

The agent writes each hypothesis in that form. A hypothesis that cannot name a measurement to change is a guess and gets demoted. A hypothesis whose experiment requires shipping a feature is a guess; the agent prefers experiments that flip a flag, dial a concurrency, change a query, or move work to a thread pool.

Common low-cost experiments:

- Cap or remove the offending downstream call behind a feature flag and re-measure.
- Pre-warm the cache or pool that is contended and re-measure.
- Increase the pool size by 2x and re-measure (if a higher pool size hurts throughput, the offender is downstream, not the pool).
- Replace the inner loop's per-element call with a single batched call and re-measure.
- Move the suspicious work behind an async boundary and re-measure.

The agent assigns each experiment a cost (engineering time and risk to production) and an information value (how much it discriminates between hypotheses), and runs the cheapest, most-discriminating experiment first.

### Stage 7 — Conclude, remediate, and write the after-action

The investigation ends when one experiment moves the measured outcome past the SLO target stated in Stage 1, and the remaining hypotheses do not fit the observed change.

The agent writes the findings_report in a strict order: what was observed, what was measured, what was hypothesized and ruled out, what was hypothesized and confirmed, what the smallest credible fix is, what the larger fix is if the smallest is not enough, and what telemetry to add so the same regression is caught earlier next time.

The skill explicitly avoids the trap of fixing the first thing found. After the leading offender is identified the agent revisits Stage 5: are there other offenders in the same profile that, even if they did not cause this regression, will cause the next one? It surfaces those as "follow-up debts" rather than recommending they be fixed in the same change.

## Common offender catalog

The agent uses this catalog to assign priors based on `runtime` and surface.

For HTTP services on the JVM the highest priors are GC pauses (G1 humongous allocations on big payloads), connection pool starvation (HikariCP waiting threads), and reflection-heavy hot paths. The agent looks at the GC log first, the pool metrics second, the CPU flamegraph third.

For HTTP services on Node.js the highest priors are blocking the event loop (synchronous JSON parse on large payloads, a synchronous filesystem call), unbounded promise fan-out exhausting sockets or memory, and serialization overhead in the response path. The agent asks for event-loop lag metrics first, the CPU flamegraph second.

For HTTP services on Go the highest priors are mutex contention (a shared map or sync.RWMutex on the hot path), goroutine leaks growing memory, and per-request allocations defeating the escape analysis. The agent asks for the block profile and the heap profile first, the CPU profile second.

For HTTP services on Python the highest priors are the GIL serializing CPU-bound work, synchronous IO inside a coroutine, and ORM N+1 patterns. The agent asks for an `async`-aware profiler (e.g., async stack capture) when the framework is async; for a sampling profiler otherwise.

For background workers regardless of runtime the highest priors are tail-latency in a downstream service (a single slow dependency dominates the queue drain rate), task batching that has fallen below the optimal batch size, and a single-threaded coordinator that has become a bottleneck.

For databases under load the highest priors are missing or stale indexes, a query plan that flipped (cardinality estimates went bad after a data shift), and lock contention on a hot row. The agent hands the investigation off to the `db-query-optimizer` skill once the database is identified as the bottleneck.

## Reading flamegraphs without getting fooled

Flamegraphs lie when read carelessly. The agent applies the following rules.

A wide function near the bottom of the stack is wide because everyone goes through it, not because it is slow. The interesting question is whether one of its branches is unexpectedly wide compared to its peers. The agent reads flamegraphs by comparing siblings, not by absolute widths.

A flat sea of `epoll_wait` or `futex_wait` at the bottom of the flamegraph does not mean the system is fast; it means the system is off-CPU and the flamegraph is the wrong instrument. Switch to off-CPU profiling or to trace-based latency analysis.

An "inverted" or "icicle" flamegraph (leaves at the top) reads differently — the agent confirms orientation before describing widths to the reporter.

Profiles taken at low sample rates over short windows miss rare slow tail events. The agent insists on capture windows long enough to include the symptom — at least one or two of the slow events the investigation is trying to explain.

Symbol resolution can fail on stripped binaries; the agent notes when stacks contain `[unknown]` frames and requests symbol upload or re-capture with debug symbols available.

## Examples

**Input (placeholder):**

`symptom_report`: "After the 09:14 deploy the `POST /checkout` p99 went from 380ms to 1.6s. Error rate unchanged. CPU on the API pods is up but not pinned. Started immediately at deploy, no traffic shift."

`runtime`: nodejs

`deploy_context`: "Deploy included a new `auditLog.write(event)` call inside the checkout handler. Audit log is a separate service."

**Agent reasoning (abbreviated):**

- Stage 1: SLO `/checkout` p99 < 500ms. Restated: "After 09:14, p99 moved from 380ms to 1.6s on `/checkout`, all customers, no error-rate change."
- Stage 2: regression window pinned to deploy boundary. Strong prior: the new `auditLog.write` call.
- Stage 3: latency investigation, typical load regime — flamegraph plus trace tail.
- Stage 4: request CPU flamegraph and async stack capture for 60s on a single pod. Request distributed traces filtered to p95+ latency on `/checkout`.
- Stage 5: traces show 900-1100ms spent inside `auditLog.write` on slow requests. CPU flamegraph does not show audit code as wide — it's off-CPU. Matches "synchronous external IO" offender.
- Stage 6: hypothesis — `auditLog.write` is on the critical path, and the audit service has high tail latency. Experiment — wrap the call in a fire-and-forget enqueue behind a flag and measure p99.
- Stage 7: after flag flip in staging, p99 returns to 360ms. Confirmed. Recommend permanent move to async audit pipeline; add `auditLog.write` duration as a telemetry signal; add an SLO alert when audit-service tail latency exceeds 200ms.

**Output (abbreviated):**

```
**Verdict:** the new audit-log call is on the critical path of /checkout and the audit
service's tail latency is the dominant contributor to the p99 regression.
Smallest credible fix: enqueue audit events asynchronously.
Follow-up debts: the audit service has no visible SLO; add one. The checkout handler
should not perform any optional IO on the critical path.
```

## Worked example two — a slow worker queue

**Input:** `symptom_report` says the email-sending worker has been falling behind for three days; the backlog now stretches twelve hours. No deploy in that window. `runtime` is python.

**Agent reasoning:**

- Stage 1: throughput target — drain rate must exceed arrival rate. Restated: "Drain rate on `email-worker` < arrival rate since 3 days ago, backlog 12h, all senders affected, no deploy."
- Stage 2: no reproducer in staging; rely on production telemetry; mark all findings as "passive."
- Stage 3: throughput investigation, heavy-load regime — first look at queueing.
- Stage 4: ask for per-task duration histogram, downstream SMTP latency, and a sampling CPU profile during peak.
- Stage 5: per-task duration drifted from ~40ms to ~160ms over the three-day window. SMTP latency is flat. Matches "synchronous external IO" offender pointing at a different downstream — turns out a new third-party tracking pixel API was added to outbound email two weeks earlier and that API's tail latency has been climbing.
- Stage 6: hypothesis — the tracking pixel injector is on the critical path of the send. Experiment — disable the injector behind a feature flag for half the workers and compare drain rates.
- Stage 7: half-fleet experiment shows the injector-disabled workers drain at 3.2x the rate. Confirmed. Recommend moving injector behind an async post-send hook; the tracking pixel itself is non-essential to delivery.

## Limitations

- The skill cannot run profilers itself; it produces a plan that another agent or a human executes, and reasons over the returned data. Quality of conclusions depends on the data the executor returns.
- The skill is opinionated about ordering and will refuse to skip the SLO step. If the reporter wants only a quick-fix recommendation without framing, the skill will still ask for the target before proceeding.
- Conclusions about distributed-system regressions (cross-service tail amplification, head-of-line blocking, fan-out fanout-in latency) require traces; without them the skill can only hypothesize.
- The skill does not attempt to fix the offender — its remediation outline is high-level. Code-level fixes belong in dedicated refactor or query-optimization skills.
- Runtime-specific advice is best for the runtimes named in the catalog. For obscure runtimes (esoteric JVM languages, embedded runtimes, niche schedulers) the playbook still applies in shape but the offender priors lose accuracy.
- The skill assumes the telemetry pipeline is trustworthy. If the dashboards themselves are wrong (clock skew, downsampling, percentile-of-percentiles), the skill will inherit those errors.
- Investigations of intermittent slowness (a thundering herd that happens once a day) are harder; the skill will recommend longer capture windows and continuous profiling rather than ad-hoc captures.
- The skill does not produce a written runbook for the on-call rotation; it produces the investigation for one incident. Generalizing into a runbook is a separate task.

## Sources reviewed

- https://github.com/benfred/py-spy (MIT)
- https://github.com/async-profiler/async-profiler (Apache-2.0)
- https://github.com/google/pprof (Apache-2.0)
- https://github.com/felixge/fgprof (MIT)
- https://github.com/iovisor/bcc (Apache-2.0)
- https://github.com/bloomberg/memray (Apache-2.0)
- https://github.com/GoogleChrome/lighthouse (Apache-2.0)
