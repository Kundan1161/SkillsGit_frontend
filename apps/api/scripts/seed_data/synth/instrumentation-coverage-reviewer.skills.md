---
id: skillsgit-curated/instrumentation-coverage-reviewer
version: 1.0.0
name: Instrumentation Coverage Reviewer
description: Review a service's metrics, traces, and logs against RED/USE, span discipline, structured logging, and end-to-end correlation IDs — output a gap-and-fix report.
authors:
  - name: Wave-3 Methodology Synthesis
    handle: wave3-observability-sre
    role: author
category: engineering
tags:
  - niche:observability-sre
  - instrumentation
  - red-method
  - use-method
  - opentelemetry
  - structured-logging
  - tracing
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
  - instrumentation review
  - observability coverage
  - red metrics
  - use metrics
  - golden signals
  - span discipline
  - structured logging
  - correlation id
  - trace context
  - opentelemetry coverage
example_invocations:
  - "Review the observability of our checkout service — code is in Go, uses zap and otel-go."
  - "We have logs and CPU metrics but no traces. What should we add first?"
  - "Audit this service's spans — are we naming and attributing them correctly?"
  - "Our incident took an hour to root-cause because we couldn't correlate logs across services. Fix the design."
inputs:
  - name: service_description
    type: text
    required: true
    description: What the service does, its language and frameworks, and a high-level call graph (upstream callers, downstream dependencies, queues, databases).
  - name: current_telemetry
    type: text
    required: true
    description: A description or sample of what's currently emitted — metric names, sample log lines, span examples, the libraries in use (zap, zerolog, OTel SDK, etc.).
  - name: pain_points
    type: text
    required: false
    description: Recent incidents where instrumentation was insufficient, blind spots known to the team, or specific questions ("why are p99 latencies impossible to diagnose?").
outputs:
  - name: coverage_review
    type: markdown
    description: A coverage assessment by signal (metrics/traces/logs), a prioritized gap list, concrete instrumentation patches in the service's language, and a follow-up checklist.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release covering RED/USE coverage, OpenTelemetry span discipline, structured-log fields, correlation-ID propagation, and a 24-point review rubric.
---

# Instrumentation Coverage Reviewer

## When to use

Use this skill when an engineer or SRE wants an opinionated review of **what telemetry a service emits** and what's missing. Typical triggers:

- A service is about to graduate to production and needs a pre-launch observability check.
- A recent incident was harder to root-cause than it should have been; the team suspects instrumentation gaps.
- A team is migrating from one observability vendor to another and needs to verify they aren't losing fidelity.
- A new microservice is being instrumented from scratch and the engineer wants a "what does good look like" baseline.
- A platform team is publishing a service-readiness checklist and needs the instrumentation portion.

Do **not** use this skill to size or cost the telemetry pipeline (use a cardinality/cost reviewer), to design dashboards (separate skill), to write alerts (use the alert-policy or SLO designer skills), or to debug a specific live incident.

## How to apply

Work through the three signals — **metrics, traces, logs** — and then the cross-cutting concerns of correlation and sampling. Score each section against the rubric at the end. Output a single review.

### Phase 1 — Metrics: RED for services, USE for resources

The RED method (Rate, Errors, Duration) measures the **service's user-visible behavior**. The USE method (Utilization, Saturation, Errors) measures the **resources the service depends on**. A complete metrics layer has both.

For every service, require these RED metrics with the named labels:

| Metric | Type | Required labels | Forbidden labels |
| --- | --- | --- | --- |
| `http_requests_total` (or `rpc_requests_total`) | Counter | `service`, `route` (templated path), `method`, `status_class` (`2xx`/`5xx`) | Raw URL path with IDs, user ID, request ID |
| `http_request_duration_seconds` | Histogram | Same as above | Same as above |
| `http_inflight_requests` | Gauge | `service` | — |

Two principles:

- **Route, not URL.** `/users/{id}` not `/users/12345`. The latter explodes cardinality (every user is a series). Most frameworks have route-templating helpers; if not, normalize manually before recording.
- **Status class, not status code.** Five buckets (`1xx`, `2xx`, `3xx`, `4xx`, `5xx`) are enough for almost every alert; the raw code can live in traces and logs.

For every backend dependency (DB, cache, queue, downstream service), require an outbound RED set:

- `<dep>_calls_total{service, target, operation, status_class}`
- `<dep>_call_duration_seconds`

For every resource the service consumes, require USE coverage:

| Resource | Utilization | Saturation | Errors |
| --- | --- | --- | --- |
| CPU | `cpu_usage` (% busy) | Run queue length, throttling time | Hard faults |
| Memory | `mem_used` / `mem_limit` | Swap, OOM kills | Allocation failures |
| Goroutines / threads | `goroutines_total` or `threads_active` | Time waiting on locks | — |
| Connection pools | Pool in-use | Pool waiters, queue depth | Pool timeouts |
| Disk / storage | Used capacity | I/O queue depth | I/O errors |
| Network | Bytes in/out | Connection backlog | TCP retransmits, drops |

USE metrics are usually exposed by the runtime (Go's `runtime/metrics`, JVM JMX, Node's `process` events) and by infrastructure exporters (`node_exporter`, `cadvisor`). Confirm the service actually scrapes them — do not assume.

The four golden signals (latency, traffic, errors, saturation) are a strict subset of RED+USE.

### Phase 2 — Traces: span discipline

Traces answer "where did the time go in this request?" Most services emit traces but not in a way that helps. The bar:

**Every inbound request opens a server span.** Named `<verb> <route>` (e.g. `POST /api/checkout`). It carries:

- `http.method`, `http.route`, `http.status_code`
- `service.name`, `service.version`
- `user.id` (if known and not PII-sensitive) or `tenant.id`

**Every outbound call opens a client span**, as a child of whatever was active. Named `<system> <operation>` (e.g. `postgres SELECT users`, `redis GET session`). It carries:

- For DBs: `db.system`, `db.operation`, `db.statement` (parameterized template, never raw values)
- For HTTP clients: `http.method`, `http.url` (hostname + route template only)
- For queues: `messaging.system`, `messaging.destination`, `messaging.operation`

**Internal spans only when they add value.** A common mistake is wrapping every function in a span — this inflates trace size 10× and obscures the meaningful structure. Internal spans should mark phases that take meaningful time *or* that are common debug targets ("authn", "cache lookup", "render"). Skip 5-line helpers.

**Errors are span events**, not separate signals. When a span fails, set `status=ERROR` and add an event with `exception.type`, `exception.message`, and (for top frames) `exception.stacktrace`.

**Attribute names follow OpenTelemetry semantic conventions.** This is what enables vendor-portable queries. Don't invent `service_name` — use `service.name`.

Span discipline checklist (review each):

- [ ] Server span name uses the route template, not the URL.
- [ ] DB statements are parameterized.
- [ ] Errors set `status=ERROR` and attach exception attributes.
- [ ] No PII in attributes (emails, full names, payment details). If present, scrub or redact.
- [ ] Trace context propagates across async boundaries (channels, queues, goroutine spawns) — many bugs hide here.

### Phase 3 — Logs: structured, sampled, correlated

A modern log line is a JSON object, not a string. Required fields:

```json
{
  "ts": "2026-05-14T12:00:00.123Z",
  "level": "info",
  "msg": "checkout completed",
  "service": "api-checkout",
  "version": "v1.42.0",
  "trace_id": "0af7651916cd43dd8448eb211c80319c",
  "span_id": "b7ad6b7169203331",
  "request_id": "req_01HXYZ...",
  "tenant_id": "acme-corp",
  "duration_ms": 142,
  "outcome": "success"
}
```

The non-negotiable five: `ts`, `level`, `msg`, `trace_id`, `span_id`. With those, an engineer can pivot from a slow trace to its logs in one click. Without `trace_id`, every incident becomes archaeology.

**Log volume principles:**

- **INFO logs are sampled** at the request level for hot paths (sample rate matched to trace sampling). Logging every successful request at full volume is expensive and useless.
- **WARN and ERROR logs are not sampled.** They are rare; lose none.
- **DEBUG is off in production**, gated by a per-request override (header or trace baggage) for targeted debugging.
- **No PII** by default. Use a redaction middleware or library helper.
- **No multi-line stack traces in raw text.** Capture them as a structured `stack` field; renderers expand them.

In Go, structured logging is typically `zap` or `zerolog`; in Node, `pino`; in Java, `slf4j` + a JSON encoder; in Python, `structlog`. All of these support context-aware fields — bind `trace_id` once per request, not at every log call.

### Phase 4 — Correlation IDs end-to-end

Every request needs an ID that survives every hop. The pieces:

1. **Inbound:** an edge proxy or the service entry handler generates a request ID (UUID v7 or ULID) if the upstream didn't pass one. Read `X-Request-Id` if present; respect it.
2. **In-process:** stored in the request context and added to every log line and span.
3. **Outbound:** propagated as both `X-Request-Id` (for ops-friendly grepping) and W3C `traceparent` (for trace continuity).
4. **Across async:** when a request enqueues work for later, the message body carries the trace context. Workers extract it and create a span linked (`SpanLink`) to the originating server span.

Three failure modes to look for:

- **Lost at the edge:** the ingress strips or doesn't pass headers. Test by curling with `-H "X-Request-Id: test-1"` and grepping logs.
- **Lost in a goroutine/thread pool:** the worker doesn't read the context. Symptom: parent span ends with no children for an async path you know exists. Fix: propagate `context.Context` (Go) or use the language's async-local-storage equivalent.
- **Lost across a queue:** worker spans appear under their own random trace. Fix: inject `traceparent` into message metadata on enqueue, extract on dequeue, and use `SpanLink` to connect.

### Phase 5 — Sampling

Sampling is where instrumentation hits the wallet. Recommend:

- **Head-based trace sampling at the edge**, 1–10% of normal traffic. Set the `sampled` bit at the entry service and propagate.
- **Tail-based sampling at the collector** if budget allows: keep 100% of error traces, 100% of slow traces, plus a sample of normal traces. The OpenTelemetry Collector supports this; configure it once at the central collector tier.
- **Always-on for marked requests:** allow a `debug=1` baggage value (or header) to force `sampled=1`. This lets engineers debug specific traffic in production.
- **Match log sampling to trace sampling** for the request-class lines, so when you have a trace you have its logs.

### The 24-point review rubric

Apply this to the service. Mark each as pass / partial / fail.

**Metrics (8):**
1. Server-side request rate metric exists with templated route.
2. Server-side latency histogram exists with sensible buckets (covering both p50 and p99).
3. Server-side error counter exists with status_class label.
4. Inflight gauge exists.
5. Each outbound dependency has a RED triple.
6. Runtime USE metrics (CPU, memory, GC, threads/goroutines) are scraped.
7. Connection pools / queues expose saturation.
8. No metric carries a high-cardinality label (user IDs, request IDs).

**Traces (8):**
9. Server spans cover every inbound entry point.
10. Client spans cover every outbound call.
11. Span names use templates, not raw values.
12. DB spans carry parameterized statements.
13. Errors are tagged with `status=ERROR` and exception attributes.
14. Span attribute names follow OTel semantic conventions.
15. Trace context propagates across async boundaries.
16. No PII in span attributes.

**Logs (4):**
17. All logs are JSON.
18. Every log line includes `trace_id`, `span_id`, `service`, `version`.
19. WARN/ERROR are unsampled; INFO is sampled in hot paths.
20. No PII in logs by default; redaction middleware in place.

**Correlation & sampling (4):**
21. Request ID generated at edge if missing, propagated end-to-end.
22. `traceparent` propagated end-to-end (sync and async).
23. Trace sampling is head-based at edge, with tail-based at collector for errors/slow.
24. Debug-on-demand override exists for targeted traffic.

A passing service has at least 20 of 24 green, with no fails in 8, 16, or 20 (the PII/cardinality safety items).

## Inputs

- **Required:** service description (language, frameworks, dependencies) and a sample of current telemetry (metric names, log lines, span examples).
- **Recommended:** the libraries in use, recent incident retros mentioning observability gaps.
- **Optional:** dashboards screenshots, on-call complaints, vendor cost data (if you also want a cardinality-cost angle — defer to the cost reviewer skill).

## Outputs

A markdown review document with:

1. **Coverage scorecard** — the 24-point rubric with pass/partial/fail per item.
2. **Top 5 gaps**, ranked by user impact-per-cost.
3. **Concrete patches** — code snippets in the service's language showing how to add the missing instrumentation (e.g. zap logger with trace fields, otel-go server middleware, Prometheus histogram with route template).
4. **Cross-cutting fixes** — usually a middleware or a base library change that closes multiple gaps at once.
5. **Verification steps** — how to confirm each fix lands (curl with header, dashboard query, log filter).
6. **Follow-up backlog** — anything below the top 5 that is worth tracking.

## Examples

### Example 1 — Go HTTP service, has metrics and logs, no traces

User says: *"We have a Go service using `prometheus/client_golang` and `zap`. We have CPU and HTTP metrics. We have logs. We don't have traces. Tell me what to add."*

Recommended response shape:

- Metrics: pass on the basics, but check labels for high-cardinality (`user_id` is a common offender). Confirm routes are templated.
- Logs: confirm JSON encoding. Add `trace_id` / `span_id` fields via a zap context middleware.
- Traces: add `go.opentelemetry.io/otel` with the `otelhttp` middleware for server spans, `otelhttp.NewTransport` for client spans, and database driver wrappers (e.g. `otelsql`) for DB spans. Configure a head sampler at 5%.
- Correlation: add a request-ID middleware that reads `X-Request-Id`, generates one if missing, stuffs it into context and the response header, and binds it to the logger.
- Output a single patch file the user can drop into their middleware stack.

### Example 2 — Node service, vendor APM auto-instrumented, custom spans look weird

User says: *"We use Express and an auto-instrumented vendor agent. Most requests look fine in the trace UI but our long-running background workers don't trace properly."*

Recommended response shape:

- Auto-instrumentation gives you server and client spans for free but loses context across `setImmediate`/queue boundaries.
- Patch: use `@opentelemetry/api`'s `context.with()` to bind context when enqueueing, extract on dequeue, and create a `SpanLink` from the worker's root span back to the enqueue span.
- For queue-mediated work, inject `traceparent` into the message envelope; do not rely on the runtime's async-local-storage to cross the queue.
- Verification: open a trace from an enqueue and confirm the worker span appears as a linked span, with the same trace_id appearing in worker logs.

## Limitations

- **Language-agnostic by design, but examples are in Go and Node.** The patterns translate to Java/Python/Rust/.NET cleanly; the exact library names differ.
- **Does not compute cost.** A service can be fully covered and still expensive — that's a cardinality/cost question (separate skill).
- **Does not replace SLOs.** Coverage is necessary but not sufficient. A service with perfect telemetry and no SLOs has good visibility but no defined success criteria.
- **Assumes Prometheus + OpenTelemetry as the default stack.** Datadog, New Relic, Honeycomb, Dynatrace agents auto-instrument many of the items above; the rubric still applies — the verification queries change.
- **Does not handle compliance redaction policy.** PII-handling rules are organization-specific. The skill flags PII risk but does not prescribe the redaction policy.

## Sources

- OpenTelemetry specification & semantic conventions (Apache-2.0): https://github.com/open-telemetry/opentelemetry-specification
- OpenTelemetry organization — language SDKs and contrib instrumentation (Apache-2.0): https://github.com/open-telemetry
- Prometheus client library and instrumentation guides (Apache-2.0): https://github.com/prometheus/prometheus
- Uber's `zap` structured logger for Go (MIT): https://github.com/uber-go/zap
- `rs/zerolog` zero-allocation JSON logger for Go (MIT): https://github.com/rs/zerolog
- Jaeger distributed tracing platform (Apache-2.0): https://github.com/jaegertracing/jaeger
- Google SRE Workbook — Monitoring and Observability methodology context: https://sre.google/workbook/alerting-on-slos/
