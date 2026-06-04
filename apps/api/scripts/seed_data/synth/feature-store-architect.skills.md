---
id: skillsgit-curated/feature-store-architect
version: 1.0.0
name: Feature Store Architect
description: Recommend a feature store design — online vs offline layers, materialization schedule, point-in-time correctness, lineage, and migration plan for a team's actual workload.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:ml-engineering, feature-store, mlops, online-offline, point-in-time, materialization, lineage, data-engineering]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: []
  tools_optional: [web_search, code_execution, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - design a feature store
  - feature store architecture
  - online offline features
  - point in time correctness
  - feature freshness
  - feature materialization
  - feature lineage
  - feature reuse
  - training serving skew
  - feature pipeline review
  - feature versioning
  - feature governance
example_invocations:
  - "Recommend a feature store design for our recommender — we have batch features and a few near-real-time signals."
  - "We have training-serving skew bugs. Help me design point-in-time correctness into the next iteration of our pipeline."
  - "Should we adopt a feature store or roll our own with the data warehouse?"
inputs:
  - name: workload_description
    type: text
    required: true
    description: Models that will consume features — type, scoring frequency (batch vs realtime), and the latency budget for online lookups.
  - name: data_sources
    type: text
    required: false
    description: Where the raw signals come from — event streams, transactional DBs, third-party APIs, data warehouse tables — and their typical update cadence.
  - name: team_capacity
    type: text
    required: false
    description: Headcount, current data stack, and willingness to operate new infrastructure vs adopt a managed service.
  - name: pain_points
    type: text
    required: false
    description: Specific problems prompting this design (e.g. training/serving skew bugs, feature duplication, slow iteration on new features).
  - name: scale
    type: text
    required: false
    description: Approximate row counts, number of entities, number of features today, projected growth.
outputs:
  - name: architecture_doc
    type: markdown
    description: Section-by-section architecture covering layers, materialization, point-in-time joins, lineage, governance, and migration.
  - name: design_json
    type: json
    description: Structured spec with `online_store`, `offline_store`, `feature_groups`, `materialization`, `pit_strategy`, `lineage`, `governance`, `migration_phases`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Feature Store Architect

## When to use

Use this skill when an ML team is either (a) considering whether to introduce a feature store at all, (b) outgrowing an ad-hoc set of Spark jobs and online-lookup hacks, or (c) repeatedly burned by training-serving skew bugs and wants a design that prevents the next one. The skill produces a written architecture: which layers exist, what each layer is responsible for, how the offline and online stores stay in sync, how point-in-time correctness is enforced, what gets versioned, and how the team migrates from where they are.

The skill applies whether the team plans to adopt an open-source feature-store framework, to build a thin wrapper over their data warehouse, or to use a managed cloud service. The design questions are largely orthogonal to the implementation choice; the skill calls out the trade-offs at each branching decision.

The skill is not the right tool for a deep data-modelling exercise on which features to compute. That is upstream — once the team knows what signals they want, the skill designs how to deliver those signals consistently. It is also not for one-off batch-only ML where every model run scores a static frame; a feature store is unnecessary overhead for that workload.

The skill expects the user to bring honest context — pretending the workload is "real-time" when it is in fact daily-batch leads to over-engineering.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `workload_description` | yes | Determines whether an online layer is required at all. |
| `data_sources` | no | Drives materialization-schedule recommendations. |
| `team_capacity` | no | Calibrates how operationally heavy the design can be. |
| `pain_points` | no | Anchors the design to the specific problems the user has. |
| `scale` | no | Sets the storage and read-throughput targets. |

## How to apply

The skill walks a nine-stage design pipeline. The output is an architecture document a team can implement in phases.

### Stage 1 — Frame what kind of feature store the team actually needs

1. Read `workload_description` and classify the dominant access pattern:
    - **Batch scoring only**: features are joined to training data and to a batch prediction frame. No online lookup is needed. A "feature store" here is really a feature-curation layer in the data warehouse.
    - **Online point lookups**: every prediction request fetches a small number of feature values keyed by an entity ID, with single-digit-millisecond latency. Requires an online key-value layer.
    - **Online range or session lookups**: each prediction needs a recent history (e.g. last N events for a user). Requires either pre-aggregated rolling features or an online store that supports the range query.
    - **Mixed**: most teams. The plan must support both batch backfills for training and online lookups for serving.
2. If the workload is "batch scoring only", the rest of the plan is much smaller; the user does not need an online store and should not pay for one. Surface this conclusion early.
3. If the workload is online but the latency budget for feature lookup is generous (>100ms), the design can use a cheaper online store than the typical sub-10ms target. Latency budget directly drives the online layer choice.
4. Establish what "fresh" means for each kind of feature. A "lifetime spend" feature can be a day stale; a "last 5 minutes click count" feature cannot. Pin freshness expectations per feature group, not globally.
5. Pin a one-paragraph problem statement at the top of the design doc: scoring patterns, latency budget, freshness expectations, and which pain points the design must fix.

### Stage 2 — The two-store pattern

6. The canonical design has two physical stores:
    - **Offline store**: typically the data warehouse or a lake table format. Optimised for large reads with row-level history kept indefinitely. Used for training-data construction and backfills.
    - **Online store**: typically a key-value store with low-latency point lookups. Holds only the latest (or near-latest) value per entity-feature pair. Used at inference time.
7. The two stores must agree. Every feature value present online must have been derived from a row in the offline store via a deterministic transformation. Without this invariant, training and serving diverge and the model behaves differently in production than in offline evaluation.
8. The bridge between the two stores is a **materialization job**: it reads from the offline store and writes to the online store. The job is the heart of the design; its correctness is the design's correctness.
9. For some streaming features the bridge is reversed: a stream processor writes to the online store and also lands events in the offline store for later training. The invariant still applies: same transformation, same definition, no skew.
10. The team should never compute features differently in training and in serving. The design must enforce this by sharing transformation code or by both pipelines reading the same materialized values.

### Stage 3 — Online store selection

11. Match the online store to the access pattern:
    - **Point lookup, sub-10ms p99, high read QPS**: Redis-style key-value cache or a managed equivalent.
    - **Point lookup, 10-100ms acceptable**: a wide-column or NoSQL database (Cassandra-style or DynamoDB-style) where scale is easier and cost is lower.
    - **Range queries on entity history**: a time-series-friendly store, or pre-aggregated rolling features in a key-value store.
    - **Embedding nearest-neighbour**: a vector index alongside the key-value store; do not try to express vector queries in a feature store designed for scalar features.
12. Capacity planning for the online store: read QPS at peak × payload size × replication factor. Recommend 3-5x headroom above peak; online stores are awful to scale under load.
13. Recommend TTLs only for genuinely transient features. Persistent features should not silently disappear at midnight; a missing feature at serve time is a different bug class from a stale feature.
14. Recommend a **fallback value** strategy: every feature should have a documented default for when the lookup misses (zero, dataset mean, "unknown" category). Without defaults, missing-key handling becomes ad-hoc per-call-site and skews training-serving consistency.
15. For multi-region serving, the online store must replicate. Recommend either active-active replication or read-only replicas with a single writer; trade-off is consistency vs availability.

### Stage 4 — Offline store and feature groups

16. The offline store should be the data warehouse the team already uses (or a lake-table format on top of object storage) — adopting a separate offline store just for the feature platform usually adds more pain than it removes.
17. Organise features into **feature groups**: a group is a set of features that share an entity key, an update cadence, and a materialization job. Examples: `user_lifetime`, `user_last_30_days`, `product_inventory`, `session_realtime`.
18. Each feature group has a schema: entity key columns, timestamp column, feature columns with types. The schema is the contract; changing it is a versioned event.
19. Each feature group has an SLA: latest acceptable row timestamp, expected row count, expected null-rate per feature. Violations of the SLA become alerts (Stage 8).
20. Avoid mega-groups (50+ features in one job). Split by update cadence and by entity; the orchestration becomes much easier when each job has a focused contract.
21. Distinguish **base features** (raw rolled-up signals) from **derived features** (transformations of base features, often per-model). Derived features that only one model uses do not need to live in the feature store; the productionization cost is not justified. Reserve the store for features at least two consumers will use.

### Stage 5 — Materialization schedule

22. Each feature group runs on one of three cadences:
    - **Batch (hourly / daily)**: most common; cheap; suitable for features that change slowly.
    - **Micro-batch (every few minutes)**: stream-aggregated and landed periodically; suitable for rolling features that need minute-level freshness.
    - **Streaming**: maintained continuously in the online store from an event stream; required when freshness must be sub-minute.
23. Recommend the cheapest cadence that meets the SLA. Streaming costs an order of magnitude more in engineering and operations than batch; only adopt where freshness genuinely demands it.
24. For batch jobs: idempotency is a hard requirement. Re-running yesterday's materialization with the same inputs must produce the same outputs. Otherwise backfills are unsafe.
25. For batch jobs: write each materialized snapshot with both an entity key and an `event_timestamp` plus a `materialization_run_id`. Without those columns, point-in-time joins (Stage 6) cannot work and historical debugging is impossible.
26. For streaming jobs: emit a watermark and a lag metric so the team knows how far behind real-time the stream is. Without lag visibility, a stalled pipeline silently serves stale features.
27. The materialization layer must publish to both the online and the offline stores from the same logic — either same code, or one logical computation expressed once and applied twice. Code duplication across stores is the second most common source of training-serving skew.
28. Materialization jobs need a re-run strategy: when a bug is found, the team must be able to backfill from a specific date with a specific transformation version and have downstream consumers pick up the corrected values cleanly. Plan this from the start; bolting it on later is painful.

### Stage 6 — Point-in-time correctness

29. The single most important invariant of a feature store is: when training data is constructed, each row sees only feature values that were known at the row's event time. Without this, the model trains on information from the future and behaves catastrophically when deployed.
30. The mechanism is the **point-in-time (PIT) join**: for each training row with entity `e` and timestamp `t`, look up each feature group as of time `t`. The query must return the most recent value with `event_timestamp <= t`, not the current value.
31. Implement PIT joins via an as-of-join in the offline store (a window function ranking feature rows by timestamp and joining on the latest <= t) or via the feature store framework's own PIT semantics if it provides them.
32. The offline store must keep historical rows. Overwriting a row when the feature value changes destroys the ability to do PIT joins for past events. Use slowly-changing-dimension-style modelling or append-only with timestamp.
33. PIT join correctness must be tested. Recommend a unit test that constructs a synthetic training set with known-correct PIT values and asserts the join returns them. Without a test, a silent bug in PIT logic can re-introduce future leakage.
34. For streaming features: PIT correctness requires the materialization timestamp to reflect when the value would have been *available to a serving call*, not when the event happened. A value derived from an event at `t` but only available in the online store at `t + 30s` must be treated as available only after `t + 30s` for training joins. Without this, the model trains on values it cannot actually have at serve time.
35. Recommend a test that scores a held-out time slice with the *online store as it would have been at that historical moment*, not as it is now, and compares to the training-time score. Discrepancies surface training-serving skew the PIT join missed.

### Stage 7 — Versioning and lineage

36. Versions to track:
    - **Feature definition version**: the transformation code that produces a feature value.
    - **Feature group schema version**: column names and types.
    - **Materialization run version**: which run produced which rows in the offline store.
    - **Online snapshot version**: which materialization run is currently authoritative in the online store.
    - **Model-to-feature binding**: which feature-definition version a given model artifact was trained on.
37. The model-to-feature binding is critical for incident response. When a model misbehaves, the team must be able to retrieve the exact feature definitions it expects so the online lookup can return the right value.
38. Lineage must answer: for a given feature, what raw tables and event streams produced it, through which transformations? Without lineage, GDPR / privacy / quality investigations become forensics.
39. Recommend automated lineage capture: the materialization framework records input tables, transformation code identifier, and output feature group at every run.
40. Backward compatibility: when a feature definition changes, the previous version must remain queryable until all dependent models have been retrained or retired. Recommend a deprecation window of at least one model-retraining cycle.

### Stage 8 — Governance, monitoring, and safety

41. Every feature has an **owner** (a person or team). Without ownership, features rot — definitions drift from intent, broken pipelines persist.
42. Every feature has a **description** in plain English. A feature called `user_score_v2` with no description is a future incident.
43. Discovery: a catalog (a UI or a code-generated docs site) lets data scientists find existing features before computing duplicates. Duplicate features that compute "the same thing" slightly differently are a recurring source of waste and disagreement.
44. Quality monitoring per feature group:
    - Row count vs expected baseline.
    - Null-rate per feature.
    - Distribution of each feature (mean, percentiles, top categorical values).
    - Materialization-lag SLA breach.
    - Online-vs-offline value consistency on a sample (compute the same feature both ways for a held-out set of entities and alert when they diverge).
45. Privacy: features derived from sensitive fields (PII, payment, health) carry a sensitivity tag that propagates to derived features. Access to sensitive feature groups is controlled at the catalog level, not at the underlying store level only.
46. Retention: align retention with the data-protection policy the rest of the company uses. A feature store is not exempt from "delete user data on request".

### Stage 9 — Migration plan and team-capacity calibration

47. Most teams introducing a feature store have existing pipelines. The plan must phase the migration.
    - **Phase 0**: catalog what features exist today, where they live, and which models use them. No migration yet; just inventory.
    - **Phase 1**: stand up the offline feature groups for the highest-value features (the ones that 2+ models share). Define schemas and ownership. Migrate one model to read from the new layer in training only.
    - **Phase 2**: stand up the online store and materialize the highest-priority feature groups. Migrate one model's serving path. Compare predictions before / after to confirm parity.
    - **Phase 3**: enforce PIT joins, lineage, and monitoring. Migrate remaining models. Retire the old pipelines feature group by feature group.
    - **Phase 4**: opening the catalog for self-service feature creation, with the on-call rotation and platform team that implies.
48. Each phase must have a definition of done that includes parity tests, owner sign-offs, and a documented rollback path. Big-bang migrations to a feature store fail more often than they succeed; phased migration is the safer default.
49. Calibrate the design to `team_capacity`. A 3-person ML team should not adopt a feature-store framework that requires a dedicated platform engineer to operate. Recommend either a managed service or a much thinner internal abstraction; the design document is the same shape but the components are smaller.
50. End the document with a section on operational ownership: who runs the materialization scheduler, who responds to SLA alerts, who approves schema changes, who rotates secrets, what the on-call playbook is.

## Outputs

The skill returns two artifacts:

1. `architecture_doc` (markdown) — the design organised by stage.
2. `design_json` (JSON) — the structured spec described under `outputs`.

## Examples

**Input (placeholder):**

`workload_description`: "A product-page recommender that scores about 200 candidate products per page view. Currently 2k page views per second at peak. Latency budget for the recommender call is 60ms end-to-end."

`data_sources`: "Click events from Kafka. User profile from Postgres. Inventory and pricing from a daily warehouse snapshot."

`team_capacity`: "Four ML engineers, no dedicated platform engineer. Current stack: dbt, Airflow, Snowflake, Kafka."

`pain_points`: "Training-serving skew on recently-viewed-products features. Two duplicate definitions of 'is-premium-user' across teams. Online lookup is a bespoke Redis with hand-written ETL jobs that fall over."

`scale`: "50M active users, 5M products, 200 features today, growing 30/quarter."

**Plan (abbreviated):**

- Two-store design: Snowflake as offline; managed key-value store for online (Redis-compatible or DynamoDB-compatible, whichever the team's cloud bill prefers).
- Feature groups: `user_profile` (daily batch), `user_lifetime_aggregates` (daily batch), `user_last_30_days` (hourly micro-batch), `user_recent_session` (streaming from Kafka), `product_attributes` (daily batch), `product_inventory_pricing` (daily batch).
- Materialization: a thin orchestration on existing Airflow + dbt; the streaming feature group runs on a small consumer service that writes to both online and offline stores from the same code path.
- PIT correctness: an as-of-join template in dbt for training-set construction; a unit test on a synthetic case asserts the join returns historical values, not current.
- Online store budget: 60ms - 20ms (model) - 10ms (network ingress + egress) = 30ms for feature lookup. With 200 candidates × 4 feature groups, batch the lookups by entity to fit. Recommend a multi-key lookup primitive in the client.
- Governance: feature catalog generated from dbt manifest + materialization metadata; `is_premium_user` consolidation is part of Phase 1.
- Migration: Phase 1 unifies `is_premium_user` and moves the recommender's batch features into a single owner. Phase 2 stands up the new online store and migrates the recently-viewed features. Phase 3 enforces PIT. Phase 4 opens self-service to other teams.

**Output excerpt:** the markdown plan and a JSON `design_json` whose `migration_phases` array enumerates phase goals with parity-test definitions.

## Limitations

- The skill writes the design; building and operating the platform is the user's work. Phase estimates are heuristic.
- Cost estimates depend on the user's cloud and traffic profile; absolute dollar numbers are not produced.
- The skill is biased toward stable, well-understood patterns; bleeding-edge architectures (e.g. multi-tenant feature meshes) are flagged only if the user mentions them.
- Specific framework recommendations are limited to the trade-offs the user describes; the skill does not endorse one open-source framework over another.
- The skill does not design the upstream data pipelines that produce raw events; assume the data sources are reliable inputs.
- PIT correctness is enforced by the user's test discipline; the skill recommends the tests but cannot verify them.
- For very small teams (<3 engineers), introducing a feature store is often not worth the cost; the skill will surface this as a recommendation against rather than a phased plan.

## Sources reviewed

- https://github.com/feast-dev/feast
- https://github.com/feathr-ai/feathr
- https://github.com/zenml-io/zenml
- https://github.com/mlflow/mlflow
- https://github.com/evidentlyai/evidently
- https://github.com/NannyML/nannyml
