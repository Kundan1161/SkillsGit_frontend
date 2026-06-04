---
id: skillsgit-curated/data-contract-author
version: 1.0.0
name: Data Contract Author
description: Author an enforceable data contract between a producer team and consumers — schema, semantics, freshness SLA, quality SLOs, ownership, on-violation, and deprecation policy.
authors:
  - name: Wave-3 Data Synth
    handle: wave3-data
    role: author
category: data
tags:
  - niche:data-governance
  - data-contracts
  - schema
  - sla
  - data-mesh
  - producer-consumer
  - odcs
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - data contract
  - producer consumer contract
  - schema contract
  - data sla
  - data slo
  - odcs
  - data contract cli
  - data mesh contract
  - api for data
  - dataset contract
example_invocations:
  - "Write a data contract for our orders fact table."
  - "Producer team is breaking our schema weekly — author a contract."
  - "Draft an ODCS contract for the customer_events Kafka topic."
  - "We need a freshness SLA and on-violation policy for the finance feed."
inputs:
  - name: dataset
    type: text
    required: true
    description: What is being contracted (table, topic, file feed). Storage, format, location.
  - name: producer
    type: text
    required: true
    description: The owning team, on-call contact, business purpose.
  - name: consumers
    type: text
    required: true
    description: Known consumers, their use cases, and how a breakage would hurt them.
  - name: known_pain
    type: text
    required: false
    description: Past incidents, drift, breakage, or unclear ownership.
outputs:
  - name: contract
    type: markdown
    description: A YAML data contract (ODCS-compatible) plus rationale and operational policy.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Data Contract Author

## When to use

Use this skill when a producer team is about to **promise** a dataset to one or more downstream consumers — or when an existing dataset is being formalized after repeated breakage. A data contract is the **API for a dataset**: the schema, the semantics, the freshness SLA, the quality SLOs, the on-violation behavior, and the deprecation policy. Without one, every change is a surprise; with one, change becomes a managed process.

Trigger phrases include:

- "data contract for..."
- "producer/consumer contract"
- "schema contract"
- "ODCS contract"
- "data SLA / data SLO"
- "deprecate a column / dataset"
- "freshness guarantee for..."

Do **not** use when the user is asking for table design (route to a table-format skill), for quality tests on an existing dataset (route to `data-quality-test-designer`), or for classification/retention (route to `data-classification-and-retention-policy-author`).

## How to apply

A data contract has **eight sections**. Author them in order. Resist the temptation to skip any — the ones people skip (semantics, on-violation, deprecation) are precisely the ones that cause the next incident.

### 1. Identity and ownership

Every contract starts with **who answers the pager** when this data is wrong.

- `id`: a stable, URL-safe identifier — `{domain}.{dataset}` (e.g., `orders.line_items_v1`). Never reuse an id for a different dataset; version the contract instead.
- `version`: semver. **Breaking** changes (column removed/renamed, type narrowed, nullability tightened, semantics changed) require a major bump. New optional columns are minor. Doc-only edits are patch.
- `producer.team`: a team, not a person. Couple with a Slack channel or paging route, not just an email.
- `producer.escalation`: the second hop when on-call doesn't respond inside the agreed window.
- `consumers`: each declared consumer + their criticality tier (P0/P1/P2). A P0 consumer drives the SLA; a P2 may tolerate longer breach windows.
- `business_purpose`: one paragraph in business language. If the producer can't write this, the contract is premature.

Ownership anti-patterns to flag:

- "Data Engineering owns it." Too broad — name the specific team.
- "@username" instead of a team. People rotate; pages do not.
- No declared consumers. A contract without named consumers cannot be evaluated for breakage.

### 2. Schema (structural contract)

Use a typed schema language — Avro, JSON Schema, Protobuf, or the ODCS `schema` block. Free-form column tables are not enforceable.

For each field declare:

- **Name** and **logical type**. Distinguish logical (`timestamp_micros_utc`) from physical (`bigint`).
- **Nullability**. `NOT NULL` is a promise; flag any column where the producer can't guarantee it.
- **Cardinality / format constraints**: enums, regex, range, length.
- **Stability**: `stable` | `evolving` | `experimental`. Experimental fields may break with a minor bump; consumers depending on them do so at their own risk.
- **Primary key / natural key** declaration. Without one, dedup and replay are undefined.
- **Reference keys**: foreign-key-like relationships to other contracted datasets.

Forbid implicit schema:

- "JSON blob" / `payload string` columns. Either parse them server-side and contract the parsed fields, or declare the blob as `opaque` and forbid consumers from parsing it.
- "We add columns whenever we want." Allowed only for `additionalProperties: true` with explicit consumer opt-in.

### 3. Semantics (what the data means)

Schema tells you the shape; **semantics** tells you what it represents. Most "data quality" incidents are actually semantic drift, not schema drift.

For each non-trivial field document:

- **Definition**: one sentence. "`amount_cents`: the post-discount, pre-tax line total in the order's currency, in minor units."
- **Unit / currency / timezone**: minor units? UTC? Local time of the warehouse?
- **Granularity**: is one row one event, or one event-day aggregate?
- **Late-arrival policy**: how late can a row arrive? What is the watermark?
- **Soft deletes**: are deletes represented as tombstone rows, status flags, or by absence?
- **PII / sensitivity tag**: link to the classification policy (see classification skill).

### 4. Freshness SLA

Freshness is a contract, not a hope. Specify:

- **Cadence**: streaming, micro-batch (e.g., every 5 min), hourly, daily by 06:00 UTC.
- **Maximum lag**: the largest delay between event-time and availability that the producer guarantees. State it for **p50**, **p95**, and **p99**.
- **Definition of "available"**: row visible in the consuming engine, or written-and-committed at the source? They are different.
- **Calendar exceptions**: holidays, scheduled maintenance windows, planned backfills.
- **Watermark publication**: how does a consumer know what's "in" for a window? Publish a high-watermark column or a separate watermark table — consumers should never have to guess.

### 5. Quality SLOs

Quality SLOs are **measurable** assertions a consumer can verify. Hand off the actual test wiring to `data-quality-test-designer`; this contract just states the targets.

Typical SLOs:

- **Completeness**: `% rows where required_field IS NOT NULL >= 99.9%`.
- **Uniqueness**: `count(distinct pk) = count(*)`.
- **Validity**: `% rows passing regex/enum check >= 99.95%`.
- **Referential integrity**: `% rows whose fk resolves >= 99.5%` (set the bar to what's actually achievable given late arrivals).
- **Volume bounds**: `daily row count within ±30% of trailing-7-day average`.
- **Distribution drift**: a categorical column's top-K mix changes by < X% week over week (useful for ML feature tables).

For each SLO declare: target, measurement window, **error budget**, and what happens when the budget is burned (see § 7).

### 6. Compatibility and evolution policy

Promise the consumer what kinds of changes the producer can make, and how.

- **Additive-only by default**: new optional columns are minor; consumers MUST ignore unknown fields.
- **Breaking changes**: require a major version bump, **and** the old version remains served for a stated overlap window (e.g., 90 days).
- **Schema-registry enforcement**: if using Avro/Protobuf, declare which compatibility mode the registry enforces (`BACKWARD`, `FORWARD`, `FULL`). State this in the contract — don't rely on the registry default.
- **Default policy for new enum values**: are consumers expected to handle unknown enum values gracefully, or is the producer required to coordinate?
- **Time-zero policy for backfills**: when the producer rewrites history, do they create a new version, or mutate the existing one?

### 7. On-violation policy

What happens when an SLO is missed? Without this, contracts become decorative.

Define, in order of severity:

- **Quality breach (within budget)**: log + alert on producer side; downstream proceeds.
- **Quality breach (budget burned)**: page the producer; **freeze the dataset** (no new commits past the breach point) or **fail downstream pipelines** depending on consumer criticality.
- **Schema breach**: hard fail — never write incompatible data, even if it means dropping the batch.
- **Freshness breach**: page after `2 * SLA` lag; auto-open an incident at `4 * SLA`.
- **Communication**: every breach triggers a public note in the producer's status channel within 30 minutes. Silence is itself a violation.

Pair the policy with a **circuit breaker**: a flag the producer can flip to stop publishing while they fix things, and a documented consumer expectation of how to behave when the breaker is open.

### 8. Deprecation policy

Every dataset dies; design the funeral.

- **Notice period**: minimum N days (90 is common; less for experimental, more for finance/regulatory).
- **Migration target**: name the replacement dataset and version.
- **Dual-write window**: the old and new datasets are produced in parallel.
- **Sunset switch**: a hard date after which the old version returns errors / 410.
- **Read-after-sunset policy**: archived to cold storage, retained per the classification skill's retention rule.

### Worked contract (ODCS-flavored YAML)

```yaml
id: orders.line_items_v1
version: 1.4.0
producer:
  team: orders-platform
  pager: pd-orders-platform
  slack: "#orders-platform-oncall"
  escalation: data-platform-leadership
consumers:
  - team: finance-analytics
    criticality: P0
    use_case: revenue recognition daily close
  - team: ml-pricing
    criticality: P1
    use_case: dynamic pricing feature pipeline
  - team: bi-self-serve
    criticality: P2
    use_case: dashboards
business_purpose: |
  One row per shipped line item. Source of truth for recognized revenue
  by SKU and shipment date.
schema:
  primary_key: [order_id, line_item_id]
  fields:
    - name: order_id
      type: string
      nullable: false
      stability: stable
    - name: line_item_id
      type: string
      nullable: false
      stability: stable
    - name: sku
      type: string
      nullable: false
      stability: stable
      semantics: canonical product SKU after normalization
    - name: amount_cents
      type: int64
      nullable: false
      stability: stable
      semantics: post-discount pre-tax line total in order currency, minor units
    - name: currency
      type: string
      nullable: false
      constraints: { enum: [USD, EUR, GBP, JPY] }
    - name: shipped_at
      type: timestamp_micros
      nullable: false
      semantics: UTC, the moment carrier scan was recorded
freshness:
  cadence: hourly
  max_lag:
    p50: 15m
    p95: 45m
    p99: 90m
  availability: visible in warehouse `orders.line_items`
  watermark_column: shipped_at_watermark
slos:
  - id: completeness-sku
    rule: "amount_cents IS NOT NULL"
    target: 99.99%
    window: rolling 24h
    error_budget: 0.5h/30d
  - id: uniqueness-pk
    rule: "count(distinct (order_id, line_item_id)) = count(*)"
    target: 100%
    window: per batch
  - id: volume-bounds
    rule: "daily rows within ±25% of trailing-7d mean"
    target: 100%
    window: daily
compatibility:
  mode: BACKWARD
  registry: confluent-schema-registry
  unknown_enum_handling: consumer-must-tolerate
on_violation:
  quality_within_budget: alert
  quality_budget_burned: page-producer; pause-downstream-finance
  schema_breach: drop-batch; page-producer
  freshness_breach: page at 2x SLA; incident at 4x SLA
  communication: status post in #orders-platform-oncall within 30m
deprecation:
  policy: 90-day notice; 30-day dual-write; hard sunset
  current_status: active
classification: confidential   # see classification skill
retention: 7y                  # see classification skill
```

## Inputs

- **dataset** (required): identity, storage system, format, location.
- **producer** (required): owning team, on-call contact, business purpose.
- **consumers** (required): named consumers, their use cases, and impact of breakage.
- **known_pain** (optional): past incidents that inform the SLOs and on-violation policy.

## Outputs

- A complete data contract in YAML (ODCS-compatible or registry-native).
- Rationale for each non-obvious choice (why this SLO target, why this freshness, why this compatibility mode).
- An operational checklist: registry entry, monitor hookups, status channel, runbook stub.
- A "first 30 days" plan: what to instrument, what to expect, when to renegotiate.

## Examples

> "We have an `orders` table that finance and ML both consume; finance breaks weekly when ML adds columns."

Author a contract with `BACKWARD` compatibility, explicit primary key, finance as P0 (drives the SLA), ML as P1. Forbid in-place column renames; require a v2 dataset with a 90-day overlap. Add a `compatibility` registry monitor that fails CI for non-additive Avro changes.

> "Kafka topic for user events, four downstream Flink jobs, three teams complain about silent schema drift."

Author the contract against the Avro schema registry. Mode = `FULL`. Add semantics for every event field and an explicit late-arrival window. SLO: 99.9% of events committed within p95 = 60s of `event_time`. On schema breach, the producer drops the malformed batch and pages itself. Tag PII fields and link the classification policy.

> "Vendor file feed lands in S3 daily; we have no contract with the vendor and they change columns silently."

Author an **inbound contract** that the *ingest team* enforces: file pattern, expected schema (parsed at land time), volume bounds, freshness (file must arrive by 06:00 UTC). On violation, the ingest pipeline quarantines the file and pages the ingest team — they negotiate with the vendor. Downstream consumers see a stable derived dataset, not the raw drop.

## Limitations

- This skill writes the contract; it does not wire the enforcement (registry, monitors, paging). Hand off to your platform team or to `data-quality-test-designer` for the SLO probes.
- ODCS is one of several schemas; if you already use a registry-native format (Avro IDL, Protobuf with annotations), keep it and map the same eight sections into your tool of choice.
- Freshness SLAs are only meaningful if you have end-to-end latency measurement. If the producer can't observe lag today, the first contract task is to instrument it.
- The contract is a social tool as much as a technical one. A perfectly-written contract that no consumer reads is worth less than a one-page agreement everyone signs.

## Sources

- https://github.com/bitol-io/open-data-contract-standard
- https://github.com/datacontract/datacontract-specification
- https://github.com/datacontract/datacontract-cli
- https://github.com/OpenLineage/OpenLineage
- https://github.com/datahub-project/datahub
