---
id: skillsgit-curated/spark-pipeline-architect
version: 1.0.0
name: Spark Pipeline Architect
description: Designs an Apache Spark batch-and-streaming pipeline with layered storage (raw/refined/curated), idempotent writes, checkpoint discipline, schema evolution, and late-data handling — so the pipeline survives reprocesses, schema drift, and partial failures.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:spark-tuning, apache-spark, pipeline, idempotency, schema-evolution, delta-lake, iceberg, hudi]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - spark pipeline
  - data pipeline design
  - medallion architecture
  - bronze silver gold
  - raw refined curated
  - schema evolution spark
  - idempotent writes
  - checkpoint discipline
  - late data
  - delta lake architecture
  - iceberg pipeline
  - hudi pipeline
  - cdc spark
  - upsert merge spark
example_invocations:
  - "Design our new Spark pipeline from Kafka to a curated reporting table."
  - "We need to reprocess six months of data without breaking downstream consumers — design the layering."
  - "Late-arriving events are wrecking our daily aggregates. How should we architect for it?"
  - "Move our nightly batch from hand-rolled parquet to a proper layered format."
inputs:
  - name: pipeline_goal
    type: text
    required: true
    description: What the pipeline produces and who consumes it. The output table, its grain, and the SLAs (freshness, lateness, completeness).
  - name: sources
    type: text
    required: false
    description: Input systems (Kafka, Kinesis, files in object store, CDC from a transactional database) and their reliability and ordering guarantees.
  - name: data_volumes
    type: text
    required: false
    description: Event rate, daily volume, peak vs steady-state ratio, retention requirements.
  - name: current_stack
    type: text
    required: false
    description: Spark version, storage layer (plain parquet, Delta, Iceberg, Hudi), orchestrator (Airflow, Dagster, custom), and any catalog (Hive, Unity, Glue).
  - name: constraints
    type: text
    required: false
    description: Regulatory (GDPR right-to-erasure, retention windows), operational (single-region vs multi-region), team (size, skills).
outputs:
  - name: architecture
    type: markdown
    description: End-to-end design — layers, formats, partitioning, write modes, checkpoints, and orchestration.
  - name: contracts
    type: markdown
    description: The contract for each layer — schema, grain, partition keys, allowed mutations, and consumer expectations.
  - name: operational_runbook
    type: markdown
    description: How to reprocess, how to evolve a schema, how to backfill, how to handle late data, and how to delete by request.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a team needs to design or redesign a Spark-based pipeline beyond a single one-off job. Typical triggers:

- Greenfield pipeline from a streaming source to a reporting layer.
- Migration from hand-rolled parquet (write-once, manual cleanup) to a layered transactional format.
- A pipeline that has accreted bugs around schema changes, late events, and reprocessing — every reprocess is a fire drill.
- A regulated workload needing deletion guarantees, audit trails, or strict retention windows.
- A pipeline whose backfill cost is unacceptable because the design conflates raw, refined, and curated layers.

Do not use this skill to optimize an existing query in place — pair with the Spark Job Tuner skill. Do not use it to choose between Delta Lake, Apache Iceberg, and Apache Hudi as a one-line answer; the differences come from the actual constraints and are captured in the steps. Do not use it to design a non-Spark pipeline; while the layering ideas generalize, the operational specifics here assume Spark on a transactional table format.

## How to apply

Work the steps in order. Architecture choices are sticky: changing the layer model or the storage format after launch is an order of magnitude more painful than getting it close to right up front.

### 1. State the contract of the final output

1. **Identify the consumer.** A BI tool, a downstream ML training pipeline, an API, an export. The consumer's tolerance for freshness, completeness, and shape determines everything upstream.
2. **State the grain.** "One row per order per day." "One row per user per hour." The grain locks the partition strategy and the deduplication discipline.
3. **State the SLAs.** Freshness (max lag from event time to consumer visibility), lateness tolerance (how late an event can arrive and still be included), and completeness (percentage of events that must reach the table within the freshness window).
4. **State the lifecycle.** How long the table retains data, whether deletions are supported, whether updates are supported, and the audit requirements.

### 2. Pick the storage layer

5. **Default to a transactional table format** (Delta Lake, Apache Iceberg, or Apache Hudi) unless there is a specific reason not to. Plain parquet has no atomic appends, no schema evolution semantics, and no time travel. The maintenance burden of plain parquet at any reasonable scale dwarfs the licensing or compatibility downsides of the transactional formats. All three of Delta, Iceberg, and Hudi are Apache-2.0 licensed.
6. **Choose Delta when** the workload is Spark-heavy, write-heavy with frequent merges, and the team prizes simplicity. Strong on `MERGE`, time travel, and change data feed. The most batteries-included for Spark.
7. **Choose Iceberg when** the workload has multiple readers (Spark plus Trino plus Flink plus Snowflake) and the team prizes engine independence and schema-evolution flexibility. Strong on hidden partitioning and partition evolution.
8. **Choose Hudi when** the workload is upsert-heavy with strict end-to-end latency requirements (sub-minute), record-level indexing matters, and the team is comfortable with the operational model. Strong on incremental queries and copy-on-write vs merge-on-read trade-offs.
9. **Pick one and commit.** Mixed-format pipelines are a maintenance burden; the small gains from per-table optimization rarely justify the team cost.

### 3. Lay out the layers

10. **Adopt three layers: raw, refined, curated.** The conventional names are bronze/silver/gold; the meaning is the same.
11. **Raw is append-only and lossless.** The raw layer captures the source exactly as it arrived, with minimal transformation — typically just unpacking the envelope (Kafka headers, S3 path metadata) and adding ingest timestamps. Schema is the source's schema; do not project columns here.
12. **Refined is deduplicated, conformed, and quality-checked.** Refined applies the rules that make the data trustworthy: deduplication on a business key, type coercion, null handling, reference-data joins, hard quality gates. The output of refined is a table that downstream teams can use without re-doing the cleansing.
13. **Curated is consumer-shaped.** Curated tables match a specific consumer's needs — a star schema for BI, a flat denormalized table for ML, a hot serving table for an API. There can be many curated tables fed by the same refined table.
14. **Write each layer's contract.** Owner, schema, grain, partition columns, mutability (append-only, upsert, full-refresh), SLAs.
15. **Resist mixing concerns across layers.** A pipeline that does deduplication during the curated write is brittle; if a downstream curated table needs slightly different deduplication, the upstream is hard to share.

### 4. Decide batch, streaming, or both

16. **Default to micro-batch streaming** for new pipelines with continuous sources. Structured Streaming gives backpressure, exactly-once semantics, and the same code as batch. Triggers can be set to once-per-N-minutes for a "scheduled batch" feel without losing the streaming guarantees.
17. **Use pure batch** when the source is file-arrival driven, when the SLA is "next day," or when the upstream is a transactional database snapshot.
18. **Use streaming with Trigger.Once or Trigger.AvailableNow** for cost-efficient periodic ingestion — the job claims the work and exits. Combines streaming bookkeeping with batch operations.
19. **Avoid lambda architecture.** Maintaining a parallel batch path "in case streaming is wrong" doubles the surface area and is rarely justified once the streaming pipeline matures. Use the same code path with different triggers if needed.

### 5. Design for idempotent writes

20. **Define the natural unique key per layer.** Raw: (source, partition, offset) or (source, event_uuid). Refined: business key + event time. Curated: business key + grain timestamp.
21. **Use `MERGE` for refined and curated writes** when the storage format supports it (Delta, Iceberg, Hudi all do). `MERGE` enforces "at most one row per key" atomically and gracefully handles re-runs.
22. **For raw, use append with a deduplication clause** at the read of refined. Raw is the immutable log; refining is where dedup happens.
23. **Generate stable batch identifiers** for each pipeline run. Pass the batch id through transformations so re-running the same batch produces the same writes. The batch id often combines the orchestrator's run id, the source watermark, and the pipeline version.
24. **Never use timestamps as the only deduplication key.** Two events can share an event timestamp legitimately. Use the source's event id, or a derived key like a hash of the payload.
25. **Verify idempotency in tests.** Run the job twice on the same input and confirm the output is unchanged. This catches a surprising number of subtle non-idempotencies.

### 6. Design checkpoints and watermarks

26. **Every streaming job has a checkpoint location.** Set `option("checkpointLocation", "...")` per query, in stable object storage that survives cluster restarts. Never reuse a checkpoint location across logically different queries.
27. **Treat the checkpoint as the source of truth for progress.** A query that loses its checkpoint must be reprocessed from a known good source offset, not "started fresh" — that loses exactly-once.
28. **Set watermarks honestly.** `withWatermark("event_time", "1 hour")` says "events older than the maximum observed event time by more than 1 hour are dropped." The watermark trade-off is freshness (short watermark, ship sooner) vs completeness (long watermark, include more late events).
29. **Choose watermarks per business need.** A fraud signal that must alert in seconds tolerates 1–5 minutes. A daily revenue total tolerates 24 hours. Match the watermark to the downstream SLA.
30. **Document the late-data policy.** What does the pipeline do with events that arrive after the watermark closed? Dropped silently (default), sent to a side table for manual reconciliation, or merged with a "late arrival" flag.

### 7. Handle late data and reprocessing

31. **Partition refined and curated by event-time, not ingest-time** for analytical workloads. Late data lands in the correct partition; reprocessing a date affects only that partition's files.
32. **Use `MERGE` to incorporate late arrivals** into refined tables. The merge condition includes the business key plus the event timestamp window the pipeline is willing to reopen.
33. **Decide the late-data window per table** and write it into the contract. "Refined orders accept events up to 72 hours late." Beyond the window, late events go to a side table for batch reconciliation.
34. **Design backfill paths.** A backfill is just a re-run with a different start and end watermark. If backfill requires a separate code path, the design is wrong.
35. **Use partition overwrite mode carefully.** `INSERT OVERWRITE PARTITION` is fast but unforgiving. With a transactional format, `MERGE` is usually safer.

### 8. Design schema evolution

36. **Pick an evolution policy per layer.** Raw: accept any new column, never drop. Refined: explicit add, explicit type widen, never drop without a deprecation window. Curated: most-stable, downstream-consumer-coordinated.
37. **Enable schema evolution at the storage format.** Delta `mergeSchema` and `overwriteSchema`, Iceberg native schema evolution, Hudi schema evolution.
38. **Prefer adding columns over changing types.** Type changes break downstream consumers. Adding a column is non-breaking.
39. **Document deprecation explicitly.** A column to be removed is renamed to `..._deprecated`, kept for a release, then dropped. Downstream consumers get warning.
40. **Use a schema registry for streaming.** Avro or Protobuf with a schema registry catches mismatches at the source rather than at the sink.

### 9. Partition for the read pattern, not the write pattern

41. **Default partition columns: event date plus one categorical column.** Date partitions enable retention and partition-pruning; the categorical column should be one consumers actually filter on.
42. **Aim for 100 MB to 1 GB per partition file.** Smaller wastes object-store request budget; larger hurts parallelism on read.
43. **Avoid high-cardinality partitions.** Partitioning by `user_id` is almost always wrong. Use bucketing or Z-ordering for high-cardinality predicates.
44. **Use hidden partitioning where the format supports it.** Iceberg hidden partitioning eliminates the need for users to know the partition columns; partition strategy can evolve without breaking queries.
45. **Use `OPTIMIZE` and `Z-ORDER`** (Delta) or compaction operations (Iceberg, Hudi) on tables that are written incrementally. Small files accumulate and degrade read performance.

### 10. Compact, vacuum, and tune

46. **Schedule a daily compaction job per layer.** Compaction merges small files into target-sized files. Run during off-peak.
47. **Schedule a weekly VACUUM (Delta) or expire-snapshots (Iceberg).** Removes orphaned files older than a retention window. Set the retention long enough to support time travel for diagnostic needs, short enough to control storage cost.
48. **Track table statistics.** Up-to-date statistics make plans accurate. The transactional formats all maintain statistics automatically on writes; periodic `ANALYZE` is still useful after backfills.
49. **Monitor file size distribution.** Small-file count and average file size are leading indicators of performance regression.

### 11. Orchestration and dependencies

50. **Each layer is its own scheduled job.** Raw ingestion, refined transformation, and curated build are independent units. Inter-layer dependencies are expressed in the orchestrator.
51. **Pass watermarks, not row counts.** The downstream layer waits for a watermark to advance, not for a count to be reached. Counts are unreliable signals in streaming systems.
52. **Make every job restartable.** Idempotency above plus a defined "from where to where" range allow a failed job to resume without operator intervention.
53. **Alert on data-quality signals, not job status.** A job that "succeeds" with 0 rows is worse than one that fails loudly. Build expectations (row counts, key uniqueness, null rates) and alert on them.

### 12. Deletion, retention, and audit

54. **Implement deletion at the refined layer.** A GDPR right-to-erasure request rewrites the refined records and propagates down. The raw layer is typically retained on a shorter window with pseudonymization where required.
55. **Use the transactional `DELETE` / `MERGE` for compliance deletes.** All three table formats support row-level deletes. Track deletion runs for audit.
56. **Use time travel for incident response, not as a backup.** Time travel windows are typically 7–30 days; long-term recovery uses object-store versioning or separate backups.
57. **Log every write with provenance.** Source offset range, pipeline version, batch id, row count. Stored in a metadata table; queryable by ops.

### 13. Document and operationalize

58. **Write the architecture diagram and the layer contracts** into the repository, not into a wiki that drifts. Markdown next to the code is the single source.
59. **Write a runbook for the five canonical operations:** start the pipeline from scratch; reprocess a date range; evolve a schema; delete a user; recover from a corrupted batch.
60. **Build a smoke test that exercises end-to-end** weekly in a staging environment with synthetic data. The smoke test catches most regressions before they hit production.
61. **Review the design quarterly** against observed pain points. Architecture decisions calcify; pain that has been tolerated for six months is often a sign the design is the wrong shape for the workload.

## Inputs

- The pipeline's business goal and consumer contract.
- Source systems and their guarantees.
- Volumes and SLAs.
- Current stack and constraints.

## Outputs

- An end-to-end architecture for ingestion, transformation, and serving.
- Per-layer contracts.
- An operational runbook for the canonical operations.

## Examples

### Example 1: Kafka to BI

Goal: feed a BI dashboard with hourly aggregates from a Kafka event stream of 200M events/day. Freshness SLA: 30 minutes. Lateness tolerance: 24 hours.

Architecture: raw — Structured Streaming append from Kafka into a partitioned Delta table by date and source, micro-batch every 30s, checkpoint on stable object storage. Refined — micro-batch every 5 minutes, dedup on `event_id`, conform types, partition by event date, `MERGE` into a Delta table with 24-hour late-data window. Curated — every 15 minutes, aggregate refined into hourly rollups, partition by hour, `MERGE` upserts.

### Example 2: nightly snapshot to denormalized fact

Goal: build a flat denormalized fact table from a postgres snapshot for an ML team. Freshness: next-day. Lateness: not applicable.

Architecture: raw — CDC stream from postgres into a Delta table, append + last-write-wins on primary key. Refined — daily batch with `MERGE` to maintain current-state slow-changing-dimension tables. Curated — daily batch building a wide denormalized table for the ML team, partitioned by snapshot date.

### Example 3: GDPR-sensitive product analytics

Goal: a product analytics pipeline that must respect right-to-erasure on a 30-day promise.

Architecture: raw — partitioned by date with a 30-day retention; user identifiers pseudonymized at ingest; reversible mapping in a secured side table. Refined — keyed on the pseudonymous id; `DELETE` job triggered by erasure requests, propagated to refined and curated. Curated — aggregates without user-grain identifiers; row-level identifiers only in refined for ML use cases. Deletion is logged in an audit table with the request id and the run id that performed it.

## Limitations

- The skill assumes Spark 3.x with a transactional table format. Older stacks need separate guidance.
- This is a design skill, not a code generator. Each layer's concrete code (the Structured Streaming query, the MERGE statement, the schema) is left to implementation.
- Specific tuning knobs (executor sizing, AQE configs) live in the Spark Job Tuner skill; this skill focuses on architecture, not execution.
- The advice on table format choice is principled but not exhaustive; specific organizational constraints (existing catalog, vendor commitments) may override the defaults here.

## Sources reviewed

- https://github.com/apache/spark
- https://github.com/delta-io/delta
- https://github.com/apache/iceberg
- https://github.com/apache/hudi
- https://github.com/MrPowers/quinn
- https://github.com/awesome-spark/awesome-spark
- https://github.com/great-expectations/great_expectations
