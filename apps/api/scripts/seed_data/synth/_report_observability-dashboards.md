# Wave-4 Methodology-Recovery Report — Observability Dashboards and Log/Trace/Metric Stack Design

**Niche:** engineering — observability dashboards and log/trace/metric stack design
**Author handle:** `wave4-observability-dashboards`
**Date:** 2026-05-14

## Files produced

All under `apps/api/scripts/seed_data/synth/`:

1. `observability-dashboard-architect.skills.md` — design service dashboards layered top-to-bottom (user-journey golden-signal panels → service RED panels → resource USE panels → SLO budget panels) with variable, link, panel-inventory, audit, and hygiene discipline. Body 305 lines. v1.0.0.
2. `log-aggregation-stack-architect.skills.md` — design a log aggregation pipeline: collection topology, parsing point, label-versus-text indexing trade-off, multi-tenancy model, three-tier retention, cost ceiling, query-pattern catalogue, onboarding contract. Body 300 lines. v1.0.0.
3. `distributed-tracing-stack-architect.skills.md` — design a trace store: two-stage sampling (edge + collector tail), three-tier collector topology, span attribute discipline, PII handling, per-service-tier retention with error escalation, incident-time query playbook, drills. Body 302 lines. v1.0.0.
4. `metric-tsdb-scaling-architect.skills.md` — scale a metric TSDB beyond a single binary: HA pairs with deduplication, sharded ingestion, long-term object storage with downsampling, federation topology choice, per-tenant quotas, cardinality governance, disaster recovery. Body 307 lines. v1.0.0.

Four skills, all net-new at v1.0.0.

## Methodology-vs-expression boundary checks

Each skill was authored with a strict separation between methodology (free to describe) and expression (the trademarked names of specific AGPL-licensed implementations, which the brief required be kept out of body content as methodology anchors).

- **No trademarked names appear as methodology anchors in any body.** Searched all four body sections for occurrences of "Grafana", "Loki", "Tempo", "Mimir", "Prometheus" (as labels for the methodology itself). None found. The names appear in the `## Sources reviewed` section at the end of each skill, with explicit license tags, as the brief permits.
- **Generic technique names used throughout bodies.** "Log aggregator", "trace store", "metric TSDB", "metric time-series store", "label-driven indexing", "tail-based sampling", "sampling collector", "storage-facing collector", "long-term storage in object storage", "downsampling", "federation", "remote-write protocol", "HA pair", "sharded ingestion". These are the standard architecture vocabulary in the wider observability community and are not the property of any specific implementation.
- **No code or prose was copied from source READMEs.** WebFetch results were read for architecture concepts only; original phrasing was authored from scratch in every body section. Cross-checked against the slo-designer reference for tone and house style.
- **Source citations are URL-only with license tag suffixes.** The Sources section in each skill follows the pattern `- <description> (<license>): <url>`, never a multi-line block of copied text.

## Sources reviewed with license tags

Across the four skills, the following sources informed methodology. The brief permitted reading AGPL stack repositories and citing them with a `(AGPL-3)` tag; permissive sources keep their original license tag.

| Source | License | Used in skills | Methodology informed |
| --- | --- | --- | --- |
| `grafana/grafana` | AGPL-3 | dashboard-architect | Dashboarding patterns: panels, rows, variables, mixed data sources, drill-down links, alerting integration in panels. |
| `grafana/loki` | AGPL-3 | log-aggregation | Label-driven indexing model versus full-text; compressed chunks; multi-tenancy via per-tenant rate limits; structured-log expectations. |
| `grafana/tempo` | AGPL-3 | distributed-tracing | Object-storage block format for trace backends; trace-by-ID query patterns; metrics-from-traces; deployment patterns. |
| `grafana/mimir` | AGPL-3 | metric-tsdb | Distributor/ingester/store-gateway/querier/compactor topology; multi-tenancy; HA replication; long-term object storage; horizontal scaling. |
| `prometheus/prometheus` | Apache-2.0 | dashboard, metric-tsdb | Pull-based scrape, recording rules, hierarchical and horizontal federation, autonomous-server HA pattern, remote-write protocol. |
| `cortexproject/cortex` | Apache-2.0 | dashboard, metric-tsdb | Multi-tenant horizontally scalable metric backend; distributor/ingester/querier/store-gateway/compactor/ruler topology. |
| `thanos-io/thanos` | Apache-2.0 | dashboard, metric-tsdb | Sidecar pattern, global query view, HA-pair deduplication, downsampling, object storage retention. |
| `VictoriaMetrics/VictoriaMetrics` | Apache-2.0 | dashboard, tracing, metric-tsdb | High-cardinality TSDB design; cluster mode components; downsampling and dedup; single-binary scaling limits. |
| `open-telemetry/opentelemetry-collector` | Apache-2.0 | log-aggregation, tracing | Receiver/processor/exporter pipeline model; tail-based sampling processor; batch processor; memory limiter. |
| `open-telemetry/semantic-conventions` | Apache-2.0 | tracing | Span attribute naming conventions, status semantics, route templating. |
| `jaegertracing/jaeger` | Apache-2.0 | tracing | Collector/query/storage components; sampling strategies; pluggable storage backends. |
| `fluent/fluent-bit` | Apache-2.0 | log-aggregation | Input/filter/output pipeline; per-node agent topology; buffering and backpressure. |
| `fluent/fluentd` | Apache-2.0 | log-aggregation | Mature log routing daemon; multi-source ingestion patterns. |
| `uber-go/zap` | MIT | log-aggregation | Reference structured-logging library; production-grade emission patterns. |
| Industry SRE Workbook | CC-BY | all four | Multi-window multi-burn-rate alerting, SLO-as-contract patterns, operability emphasis. |

## Patterns extracted across skills

- **Four-layer dashboard stack: journey → RED → USE → SLO budget.** The reading order from top to bottom matches incident-response decision flow.
- **Two-stage sampling for traces** (edge head + collector tail) with sampling decisions propagated, never invented mid-trace, and "trace either whole or dropped" rule.
- **Label-driven indexing for logs at scale**, with hybrid text indexing scoped narrowly to recent error/warn slices; analytics moves to a separate column store.
- **Three-tier retention** (hot/warm/cold) consistently applied to logs, traces, and (as native/5-min/1-hour resolutions) metrics.
- **Per-tenant quotas at three points** — ingest, query, storage — in every multi-tenant design, with tenancy aligned to on-call rotation.
- **HA pair as the first scaling step** for metric TSDBs, with explicit deduplication strategy to avoid doubling long-term storage cost.
- **Cardinality governance**, not just cardinality limits — review at metric-definition time, weekly bad-label dashboard, ingestion-time drop relabelling.
- **Audit and drill cadence** baked into every design — quarterly reviews, synthetic-incident drills, scrub-list reviews.

## Tagging conformance

All four skills:

- `category: engineering`.
- First tag: `niche:observability-dashboards`.
- 6-7 additional tags per file from a controlled vocabulary (golden-signals, red-method, use-method, slo-panels, template-variables, dashboard-hygiene, log-aggregation, log-collection, retention-tiers, log-cost, structured-logging, log-tenancy, log-pipeline, distributed-tracing, trace-sampling, span-attributes, trace-retention, collector-pipeline, trace-queries, opentelemetry, metric-tsdb, ha-pairs, federation, long-term-storage, downsampling, sharding, remote-write, on-call).

## Frontmatter conformance

- `license_type: free` on all four. No `pricing` block.
- `id` slug under `skillsgit-curated/` per the existing wave-3 convention in the synth directory.
- `version: 1.0.0` with a single dated `changelog` entry.
- `ai.required_models: [claude-opus-4-7, claude-sonnet-4-6]`; compatible models listed; `min_context_tokens: 32000`; estimated tokens 7000-7500.
- Inputs and outputs declared. 4 example invocations and 10 trigger keywords per skill.
- `authors` block names the wave-4 synthesis handle.

## Body lengths (target 300-600 body lines)

| Skill | Body lines | Total lines |
| --- | --- | --- |
| observability-dashboard-architect | 305 | 375 |
| log-aggregation-stack-architect | 300 | 370 |
| distributed-tracing-stack-architect | 302 | 372 |
| metric-tsdb-scaling-architect | 307 | 377 |

All four are within the 300-600 body band. Counts measured by an awk pass that ignores the YAML frontmatter (everything between the two `---` markers).

## Confidence

**High confidence** on:

- License verification on every cited URL via WebFetch (each README's licence string was read back).
- Methodology-vs-expression boundary discipline — bodies use generic technique names; trademarked names appear only in the per-skill Sources section with explicit license tags.
- Internal consistency across the four skills (handoffs to neighbouring skills are explicit; vocabulary is shared; no contradictions found in cross-reading).
- Fidelity to the canonical references (the architecture decomposition matches the broadly accepted shape of these systems in the community).

**Medium confidence** on:

- The default starting numbers (retention windows, sampling thresholds, quota ceilings, downsampling tiers). These are reasonable industry defaults; each skill's Limitations section flags that they need real-workload calibration.
- The order of cost levers in the tracing skill — different workloads may have different dominant costs and reorder steps 3-5; the skill is explicit that the order is a starting point.

**Lower confidence (flagged for future revision):**

- I deferred to using the existing creator-account slug `skillsgit-curated/` based on inspection of the slo-designer reference; the brief did not explicitly name a new wave-4 handle. If wave-4 should publish under a distinct slug, all four `id` fields and the `authors.handle` field need a one-line edit.
- No live validator was run against the `packages/skills-schema` definitions — I relied on the spec text and on the structure of the existing slo-designer and motion-planner-selector references.
- The tracing skill discusses PII scrub-list governance but does not enumerate fields; that is intentional (it is a contract not a content list) but a future revision could pair with a privacy-fields skill.

## Notes on the AGPL-cite policy

The brief explicitly permitted reading AGPL stack repos for methodology and citing them in `## Sources reviewed` with an `(AGPL-3)` tag, provided no code, prose, close paraphrase, or trademarked-name anchoring appeared in the body. I followed this in all four skills:

- Bodies were authored from scratch using the generic vocabulary the wider community uses (label-driven indexing, tail sampling, HA pair, etc.).
- AGPL repos appear in the Sources section with the `(AGPL-3)` tag and a one-line technique description; no name appears outside that section.
- Where a methodology is described in multiple repos under different names, I cited each repo with its own license tag rather than collapsing.

This is a different policy from the wave-3 observability-sre report, which rejected the same AGPL repos outright. The wave-4 cited-but-not-anchored approach is reversible — should a future review tighten policy back to "AGPL not cited at all", the Sources entries can be replaced with the Apache-2.0 alternatives (Cortex, Thanos, VictoriaMetrics, Jaeger, Cortex) that are already cited alongside.
