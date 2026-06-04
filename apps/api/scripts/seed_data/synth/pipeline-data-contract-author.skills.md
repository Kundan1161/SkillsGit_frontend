---
id: skillsgit-curated/pipeline-data-contract-author
version: 0.1.0
name: Pipeline Data Contract Author
description: Author a machine-readable data contract between two pipeline stages — schema, freshness SLA, quality SLOs, ownership, and on-failure behavior.
authors:
  - name: Synthwave Methodology Lab
    handle: synthwave
    role: author
category: data
tags:
  - niche:workflow-orchestration
  - data-contracts
  - schema
  - sla
  - data-quality
  - lineage
  - governance
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
    - gpt-4.1
  min_context_tokens: 12000
  tools_required: []
  tools_optional:
    - web_search
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - data contract
  - pipeline contract
  - schema agreement
  - freshness sla
  - data quality slo
  - producer consumer contract
  - data product
  - data ownership
  - on failure behavior
example_invocations:
  - Write a data contract for our `orders_enriched` table between the ingestion team and analytics.
  - Author the schema + SLA contract between our Kafka producer and the downstream Dagster asset.
  - I need a YAML data contract for the staging-to-mart handoff with quality checks.
  - Document the freshness and quality SLOs for our customer 360 feature.
inputs:
  - name: producer
    type: text
    required: true
    description: Who produces the dataset — team or service, plus the upstream pipeline stage (e.g. "Ingestion squad / Airflow DAG `raw_orders`").
  - name: consumer
    type: text
    required: true
    description: Who consumes it — team, service, or named downstream stage. List multiple if applicable.
  - name: dataset_brief
    type: text
    required: true
    description: What the dataset is — physical location, current schema (if known), volume, expected freshness, criticality.
  - name: format
    type: choice
    required: false
    description: Output format for the contract.
    choices:
      - yaml
      - json
      - markdown
    description: Default yaml.
outputs:
  - name: contract
    type: markdown
    description: The data contract as a fenced YAML/JSON block plus a human-readable summary and a checklist for activation.
changelog:
  - version: 0.1.0
    date: 2026-05-14
    notes: Initial release. Producer-consumer contract template with schema, freshness, quality SLOs, ownership, and breakage protocol.
---

# Pipeline Data Contract Author

## When to use

Use this skill when two stages of a data pipeline need a **written, machine-checkable agreement** about a shared dataset — the boundary between a producer and one or more consumers. Typical signals:

- "Write a data contract for the handoff between X and Y."
- "What's the schema and SLA we should commit to for this table?"
- "We keep breaking analytics with our schema changes — we need a contract."
- "Document our data product."

Do **not** use this skill for:
- Designing the DAG itself (use `dag-architect`).
- Planning a migration (use `orchestrator-migration-planner`).
- Implementing the runtime checks — this skill produces the *spec*, not the implementation. Pair with Great Expectations, dbt tests, Soda, or Dagster asset checks downstream.

## Inputs

| Input          | Required | Notes |
|----------------|----------|-------|
| `producer`     | yes      | The owning team **and** the technical producer (DAG, asset, topic, table). |
| `consumer`     | yes      | Each downstream consumer team and their use case. Contracts with many consumers must list them all. |
| `dataset_brief`| yes      | What the dataset is and where it lives (`db.schema.table`, S3 prefix, Kafka topic, Dagster asset key). Include current schema in any structured form if available. |
| `format`       | no       | `yaml` (default), `json`, or `markdown`. Most teams operationalize YAML. |

If `producer` and `consumer` are the same team, the skill will warn that this is an internal handoff and the contract weight should be reduced — but still produce one if asked.

## Outputs

A single markdown document with:

1. **Summary** — one paragraph: what the dataset is, who produces, who consumes, why a contract is needed.
2. **The contract** — in the chosen format, with every section below filled in.
3. **Activation checklist** — what producer and consumer must each do to make the contract real (CI checks, monitors, alerts, runbook links).
4. **Open questions** — things the brief did not answer.

## How to apply

### Step 1 — Identify the contract boundary

A data contract sits at exactly one boundary. State it explicitly: *"This contract covers the dataset `<id>` as produced by `<producer>` and consumed by `<consumers>`."* If the user describes multiple boundaries, produce multiple contracts — never bundle.

The dataset identity must be canonical:
- Warehouse table: fully-qualified `database.schema.table`.
- Lakehouse / object store: bucket + prefix + format + partitioning scheme.
- Stream: cluster + topic + key/value schema registry id.
- Orchestrator asset: orchestrator + asset key (e.g. Dagster `["sales", "orders_enriched"]`).

### Step 2 — Write the schema section

Schema is the bedrock. Every field gets:
- `name` — snake_case.
- `type` — a typed system the consumer can rely on. Prefer Avro/Parquet/Arrow primitive types or SQL types. Avoid ambiguous `string`-for-everything.
- `nullable` — explicit boolean. If `true`, document the meaning of null.
- `description` — one sentence; what it semantically represents, not what it physically is.
- `pii` — `none | direct | quasi | sensitive` (use the producing team's classification, but require *one* value).
- `example` — a realistic literal.
- `constraints` — `unique`, `min`, `max`, `regex`, `enum`, `foreign_key`. Constraints are part of the contract; violations are contract breaches.

Mark **primary key** and **partition key** explicitly. These cannot change in a minor version.

### Step 3 — Write the freshness SLA

Freshness has two numbers, not one:
- **`max_lag`** — the maximum acceptable delay between an event happening in the source-of-truth and it appearing in this dataset. This is the consumer's worst-case planning horizon.
- **`target_lag`** — the typical lag during healthy operation. The producer commits to keeping the p95 of measured lag ≤ this target.

Add a **measurement definition**: how lag is computed (e.g. `now() - max(event_ts)` evaluated every 5 minutes from a monitoring query). Lag that cannot be measured does not exist for SLA purposes.

For batch pipelines, also state the **delivery deadline**: "the partition for `dt = D` must be readable by `D + 24h` at `09:00 UTC`". This is the form consumers actually care about.

### Step 4 — Write the quality SLOs

Quality SLOs are stricter than schema — schema says "the column exists and is an int", quality says "the column is correct".

Use this taxonomy:
- **Completeness**: `null_rate(column) <= X%`, `row_count(partition) >= Y`, `row_count(partition) >= 0.5 * 7d_avg`.
- **Uniqueness**: `count(distinct pk) = count(*)`.
- **Validity**: `column matches enum/regex/range`. Reuse the constraints from the schema section.
- **Referential**: `count(child.fk not in parent.pk) = 0`.
- **Distributional**: `mean(column) within 3σ of 30d mean` (use sparingly — noisy).
- **Custom**: business rules expressed as SQL or as Great-Expectations expectations.

Each SLO has:
- `severity` — `warn | breach | block`. `block` means "consumer is notified and the partition is held". `breach` means "alert fires, partition is published with a flag". `warn` means "log only, monthly review".
- `evaluation` — when and where the check runs (producer-side pre-publish, consumer-side post-read, both).

Aim for **5–12 SLOs**. Fewer means the contract is decorative; more means the team will mute alerts.

### Step 5 — Document ownership and on-call

- `owner_team` — the team accountable when the contract is violated.
- `owner_contact` — a paging route (PagerDuty service, Slack channel, email list). Not an individual.
- `support_hours` — `24/7 | business-hours | best-effort`. Be honest; consumers will plan around this.
- `producer_runbook_url` — link to the producer's runbook for this dataset.
- `escalation_path` — first responder → secondary → engineering manager. Three levels with names of *roles*, not people.

### Step 6 — Define on-failure behavior

This is the section everyone forgets. For each failure class, state the agreed response:

- **Schema breakage attempted by producer**: contract validator blocks the publish; producer must open a versioning ticket.
- **Quality SLO `block` violated**: partition is **not** published to the consumer-visible location. Producer pages on-call. Consumer reads previous partition with a clear staleness signal.
- **Freshness `max_lag` exceeded**: producer pages on-call; consumer's dashboard auto-renders a "stale data" banner driven by the lag metric.
- **Producer outage**: how long can the consumer tolerate stale data? Document the consumer's degradation behavior (cached read, last-known-good, hard error).
- **Backfill in progress**: a flag in the dataset metadata (`_meta_backfill_running`) so consumers can suppress alerts or recompute downstream.

### Step 7 — Specify versioning rules

A contract is versioned, semver-style:
- **Patch** (1.2.0 → 1.2.1): documentation, examples, non-functional. No code change required by consumers.
- **Minor** (1.2 → 1.3): additive only — new nullable columns, new SLOs at `warn`. Old consumers keep working.
- **Major** (1.x → 2.0): anything else — column rename, type change, semantic change. Requires a **migration window** with both versions live in parallel for ≥ 30 days, and explicit ack from every named consumer.

Spell out the **deprecation protocol**: how the producer announces a major version, how consumers register acknowledgement, and what happens at the cutover date.

### Step 8 — Lineage and discovery

Link out:
- `upstream` — the contract IDs or dataset IDs of inputs.
- `downstream_known` — the consumers listed in this contract (may not be exhaustive; flag it).
- `catalog_url` — link to the data catalog entry (DataHub, OpenMetadata, Atlan, Dagster catalog).
- `lineage_emitter` — how lineage is reported (OpenLineage events, Dagster lineage, manual).

### Step 9 — Produce the contract file

Default to YAML. Use this skeleton; fill every field; do not invent fields not in the skeleton without a comment explaining why:

```yaml
contract:
  id: orders_enriched.v1
  version: 1.0.0
  status: active   # draft | active | deprecated
  dataset:
    kind: warehouse_table   # warehouse_table | object_store | stream | orchestrator_asset
    location: analytics.prod.orders_enriched
    partitioning: { by: event_date, granularity: day }
    primary_key: [order_id]
  producer:
    team: ingestion
    pipeline: airflow://dags/orders_enriched
    owner_contact: pagerduty://services/ingestion-primary
    support_hours: business-hours-pt
    runbook_url: https://wiki.corp/runbooks/orders_enriched
  consumers:
    - team: analytics
      use_case: daily KPI dashboards
    - team: ml-platform
      use_case: churn-feature
  schema:
    - { name: order_id, type: string, nullable: false, pii: none,    example: "ord_8f3...", constraints: [unique] }
    - { name: customer_id, type: string, nullable: false, pii: quasi, example: "c_42",     constraints: [foreign_key:dim.customer.customer_id] }
    - { name: order_total_usd, type: decimal(12,2), nullable: false, pii: none, example: "129.95", constraints: [min:0] }
    - { name: event_date, type: date, nullable: false, pii: none,    example: "2026-05-13", constraints: [] }
    # ...
  freshness:
    max_lag: 26h
    target_lag_p95: 22h
    delivery_deadline: "D+1 09:00 UTC for partition dt=D"
    measurement: "now() - max(event_ts) sampled every 5m by Datadog query orders_enriched.lag_seconds"
  quality_slos:
    - id: row_count_floor
      check: "count(*) >= 0.5 * 7d_avg(count(*))"
      severity: block
      evaluation: producer_pre_publish
    - id: pk_uniqueness
      check: "count(distinct order_id) = count(*)"
      severity: block
      evaluation: producer_pre_publish
    - id: customer_fk
      check: "0 = count(*) where customer_id not in (select customer_id from dim.customer)"
      severity: breach
      evaluation: producer_pre_publish
    - id: null_rate_total
      check: "null_rate(order_total_usd) <= 0.001"
      severity: breach
      evaluation: producer_pre_publish
    # ...
  on_failure:
    block: "Partition held in staging; consumers see previous partition; ingestion on-call paged."
    breach: "Partition published with flag _meta_quality=breach; consumers may exclude; alert fires."
    warn:   "Logged to quality dashboard; reviewed monthly."
    producer_outage: "Stale data banner via lag metric; analytics reads last-known-good up to 7 days."
    backfill: "_meta_backfill_running=true on partition metadata; downstream alerts suppressed."
  versioning:
    policy: semver
    deprecation_window_days: 30
    consumer_ack_required_for_major: true
  lineage:
    upstream:   [raw_orders.v3, dim_customer.v2]
    downstream_known: [analytics.kpi_daily, ml.churn_features]
    catalog_url: https://catalog.corp/datasets/orders_enriched
    emitter: openlineage
  changelog:
    - { version: 1.0.0, date: 2026-05-14, notes: "initial contract" }
```

### Step 10 — Write the activation checklist

The contract is words until both sides commit. Produce a checklist:

Producer must:
- [ ] Implement the quality SLO checks pre-publish (dbt tests / Dagster asset checks / Great Expectations).
- [ ] Wire the lag metric to monitoring.
- [ ] Stand up the runbook URL.
- [ ] Page route exists and has been tested.

Consumer must:
- [ ] Subscribe to the producer's incident channel.
- [ ] Implement the degraded-read behavior (last-known-good or hard error).
- [ ] Render the staleness signal in user-facing views.
- [ ] Sign off on the version (named consumers each give explicit ack).

Platform must:
- [ ] Register the contract in the catalog.
- [ ] Configure the contract validator in CI to block schema changes that violate it.
- [ ] Configure the lineage emitter.

## Examples

### Example A — Staging-to-mart in a warehouse

User: *"Contract for `prod.fact_orders` produced by dbt run `mart_orders`, consumed by the BI team and the finance team."*

The skill produces:
- A YAML contract with `kind: warehouse_table`, partitioning by `order_date`.
- 8 SLOs: row count floor, PK uniqueness, FK to `dim_customer`, FK to `dim_product`, null-rate on `order_total`, distributional bound on `mean(order_total)` (warn), referential to `dim_currency`, freshness measurement.
- On-failure: block on PK and FK; breach on distributional; warn on documentation drift.
- Activation: dbt tests `unique`, `not_null`, `relationships` plus a custom freshness test; Datadog monitors on the lag metric; Slack channel `#mart-orders-incidents`.

### Example B — Producer-consumer for a Kafka topic

User: *"Contract for `orders.created.v1` topic produced by the checkout service, consumed by analytics and fraud."*

The skill produces:
- `kind: stream`, location includes cluster + topic + schema-registry subject + Avro schema id.
- Schema mirrors the Avro contract; nullable fields explicit.
- `freshness.max_lag: 5m`, `target_lag_p95: 30s`, measurement via Kafka consumer-group lag.
- SLO `block` on schema-registry compatibility (BACKWARD); SLO `breach` on dead-letter rate.
- On-failure: block prevents publish at the producer's schema-registry gate; breach pages on-call; consumer-side dedup keyed on `event_id`.

## Limitations

- This skill produces a **spec**, not the runtime checks. It will reference where to implement them (dbt, Dagster asset checks, Great Expectations, Soda, schema registry) but it does not write those test files.
- The skill assumes the producer can implement pre-publish checks. For pipelines where checks can only run post-publish, the skill will note the gap and recommend a "publish, then verify, then promote" pattern.
- Cross-organization contracts (vendor → you) need legal review beyond what this skill covers. The skill will flag this.
- Contracts for ML features have an extra dimension (training/serving skew) that this skill addresses lightly; use a dedicated feature-store contract skill for production ML.
- The skill does not pick a catalog or quality tool — that is a platform decision the team makes once.

## Sources (verified)

- https://github.com/apache/airflow — Apache-2.0 (provider for many of the producer/consumer patterns described)
- https://github.com/dagster-io/dagster — Apache-2.0 (asset checks and freshness policy concepts informed this skill)
- https://docs.dagster.io/guides/build/assets/defining-assets — Apache-2.0 (project docs)
- https://github.com/PrefectHQ/prefect — Apache-2.0
- https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html — Apache-2.0 (project docs on inter-task and partitioning patterns)
- https://github.com/apache/airflow/discussions/28905 — Apache-2.0 (idempotency reference for the on-failure section)
