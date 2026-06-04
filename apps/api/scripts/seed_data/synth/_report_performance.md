# Wave-2 Synthesis Report — Engineering / Performance & Profiling

## Files produced

- `apps/api/scripts/seed_data/synth/eng-perf-investigation-playbook.skills.md` (v1.0.0, 294 lines)
- `apps/api/scripts/seed_data/synth/eng-db-query-optimizer.skills.md` (v1.0.0, 327 lines)
- `apps/api/scripts/seed_data/synth/eng-load-test-planner.skills.md` (v1.0.0, 327 lines)
- `apps/api/scripts/seed_data/synth/eng-web-perf-audit.skills.md` (v1.0.0, 278 lines)

No existing performance/profiling skills were present in the synth directory, so all four files are new — no merges or version bumps were needed.

## Sources per skill (all license-verified MIT / Apache-2.0 / BSD / ISC)

**perf-investigation-playbook**
- py-spy — MIT — https://github.com/benfred/py-spy
- async-profiler — Apache-2.0 — https://github.com/async-profiler/async-profiler
- google/pprof — Apache-2.0 — https://github.com/google/pprof
- fgprof — MIT — https://github.com/felixge/fgprof
- bcc — Apache-2.0 — https://github.com/iovisor/bcc
- memray — Apache-2.0 — https://github.com/bloomberg/memray
- lighthouse — Apache-2.0 — https://github.com/GoogleChrome/lighthouse

**db-query-optimizer**
- google/pprof — Apache-2.0
- py-spy — MIT
- hyperfine — MIT/Apache-2.0 — https://github.com/sharkdp/hyperfine
- locust — MIT — https://github.com/locustio/locust
- vegeta — MIT — https://github.com/tsenart/vegeta
- lighthouse — Apache-2.0
- bombardier — MIT — https://github.com/codesenberg/bombardier

**load-test-planner**
- locust — MIT
- vegeta — MIT
- hey — Apache-2.0 — https://github.com/rakyll/hey
- bombardier — MIT
- wrk2 — Apache-2.0 — https://github.com/giltene/wrk2
- hyperfine — MIT/Apache-2.0
- lighthouse — Apache-2.0

**web-perf-audit**
- lighthouse — Apache-2.0
- web-vitals — Apache-2.0 — https://github.com/GoogleChrome/web-vitals
- sitespeed.io — MIT — https://github.com/sitespeedio/sitespeed.io
- critical — Apache-2.0 — https://github.com/addyosmani/critical
- hyperfine — MIT/Apache-2.0
- locust — MIT

## Cross-cutting patterns observed

1. **Methodology over tooling.** The strongest open-source performance content (Brendan Gregg's USE method, Google's CWV docs, Postgres EXPLAIN guides) frames investigation as a structured procedure, not a tool-checklist. All four skills are structured as ordered playbooks with explicit gate criteria between stages.
2. **Percentiles, not averages.** Every source treats latency as a histogram; the skills inherit this and refuse mean-based acceptance criteria.
3. **Open-loop vs closed-loop modeling.** Modern load-testing literature (k6 docs, vegeta design, wrk2's coordinated-omission defense) consistently flags closed-loop testing as a measurement bias. The load-test-planner skill encodes that prior.
4. **Cardinality lies dominate query plans.** Postgres and MySQL performance writing converges on "the estimator is wrong" as the leading cause of bad plans; the db-query-optimizer skill orders its diagnostic accordingly.
5. **Field beats lab for CWV.** Lighthouse documentation and Chrome team posts consistently advise field-data primacy for INP and CLS; the web-perf-audit skill makes that explicit.

## Rejections (sources considered and excluded)

- **FlameGraph (brendangregg/FlameGraph)** — CDDL-1.0. Not in allowed license list. Excluded despite being the canonical flamegraph tool. Methodology referenced abstractly in the perf-investigation-playbook skill via Brendan Gregg's USE-method public writing, but no source link.
- **perf-tools (brendangregg/perf-tools)** — GPL-2.0. Not in allowed list. Excluded.
- **k6 (grafana/k6)** — AGPL-3.0. Excluded despite being the most popular modern load tester.
- **Pyroscope (grafana/pyroscope)** — AGPL-3.0. Excluded.
- **percona-toolkit** — GPL-2.0. Excluded.
- **pgBadger (darold/pgbadger)** — PostgreSQL License (BSD-style, but not on the explicit allowed list). Initially included with a note, then removed for strict compliance with the allowed-license constraint.
- **Artillery (artilleryio/artillery)** — MPL-2.0. Not in allowed list. Excluded.

## Confidence

- perf-investigation-playbook: high. Strong source backing across runtimes; methodology well-validated.
- db-query-optimizer: high. EXPLAIN-driven approach is industry-standard; offender catalog is well-grounded.
- load-test-planner: high. Workload-modeling and traffic-shape design draw directly on verified MIT/Apache load-tester docs; coordinated-omission discussion is sourced from wrk2.
- web-perf-audit: high. Lighthouse and web-vitals are the canonical references; both Apache-2.0.

## Suggested follow-up niches

1. **Engineering — Distributed Systems / Reliability** (saga design, idempotency, retry/backoff, circuit breakers, consensus fundamentals).
2. **Engineering — Observability & Telemetry** (instrumenting code, log structure, trace propagation, SLO authoring, alert design).
3. **Engineering — Memory Leak / Heap Investigation** (the optional fifth skill from this brief was deferred; deserves its own niche covering JVM heaps, Node/V8, Go heap profiles, Python tracemalloc).
4. **Engineering — Caching Strategy** (cache topologies, invalidation, stampede protection, near-cache vs distributed).
5. **Data — OLAP / Warehouse Query Tuning** (separate from OLTP query optimization; distribution keys, sort keys, broadcast joins).
