---
id: skillsgit-curated/iceberg-s3-operations-architect
version: 1.0.0
name: Iceberg S3 Operations Architect
description: Design an Apache Iceberg operations runbook for object storage covering snapshot retention, compaction cadence, manifest control, partition evolution, branching, conflict resolution, and disaster recovery tuned to table workload.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:iceberg-s3-ops, apache-iceberg, object-storage, compaction, snapshot-retention, partition-evolution, branching, disaster-recovery]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1]
  tools_required: []
  tools_optional: [code_execution]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - iceberg operations
  - iceberg maintenance
  - iceberg compaction
  - iceberg snapshot expiration
  - iceberg manifest rewrite
  - iceberg partition evolution
  - iceberg branching
  - iceberg tagging
  - iceberg orphan files
  - iceberg s3
  - iceberg catalog
  - iceberg time travel
  - iceberg disaster recovery
  - table format operations
example_invocations:
  - "Our Iceberg table is at 4 million files and queries are slow. Design the compaction schedule."
  - "Plan the maintenance cadence for our 200-table Iceberg lakehouse on S3."
  - "We need to add a partition column to an Iceberg table that already has 18 months of data. How?"
  - "Set up branching and tagging so the data team can publish atomic releases."
  - "Build a disaster recovery plan for Iceberg metadata on S3 across two regions."
inputs:
  - name: table_inventory
    type: text
    required: true
    description: List of tables — name, row count, byte size, partition layout, write frequency (streaming, hourly, daily), read patterns, current file count and manifest count if known.
  - name: write_path
    type: text
    required: false
    description: Engines writing to the tables (Spark, Flink, Trino, custom) and the catalog in use (Hive Metastore, REST catalog, AWS Glue, JDBC, Nessie-compatible).
  - name: query_patterns
    type: text
    required: false
    description: Most common queries — partition predicates, projections, point lookups, full scans. Latency targets per query class.
  - name: storage_layout
    type: text
    required: false
    description: Object store and region, bucket layout, encryption, lifecycle policies, multi-region needs, prefix sharding policy.
  - name: governance_needs
    type: text
    required: false
    description: Retention requirements, time-travel window, audit trail expectations, branching workflow, change-management policies.
  - name: operational_constraints
    type: text
    required: false
    description: Maintenance windows, available compute for maintenance jobs, budget envelope, concurrency limits on writers.
outputs:
  - name: maintenance_schedule
    type: markdown
    description: Per-table or per-tier cadence for compaction, snapshot expiration, manifest rewrite, orphan-file cleanup, with trigger conditions.
  - name: layout_recommendations
    type: markdown
    description: Partition strategy, sort order, file size targets, write distribution mode, and how to evolve them safely.
  - name: governance_plan
    type: markdown
    description: Branching strategy, tagging policy, retention rules, audit and lineage hooks, write conflict resolution.
  - name: disaster_recovery_plan
    type: markdown
    description: Catalog backups, metadata snapshots, region failover, cross-region replication, restore drills.
  - name: verification_runbook
    type: markdown
    description: Checks that prove the system is healthy — file size distribution, manifest count, snapshot age, orphan ratio, query latency on key tables.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when an Apache Iceberg deployment on object storage needs an operations plan rather than a one-off fix. Typical triggers:

- Tables have grown into hundreds of thousands or millions of files and queries are slow because metadata reads dominate.
- The snapshot list is large enough that catalog operations are slow and storage bills are climbing from undeleted data files.
- Writers report frequent commit conflicts and the team needs a write-path policy.
- A new partition column must be introduced into an existing large table.
- Several teams want to read from a "stable" version of a table while another team continues to write — branching needs to be designed.
- A region or catalog failure scenario has to be modeled before it becomes a real incident.
- The maintenance jobs currently run "when someone remembers"; a recurring schedule has to be designed.

Do not use this skill to choose between table formats; pair with a lakehouse-table-format-picker skill. Do not use it for raw Spark tuning of the maintenance jobs themselves; that is a tuning concern. Do not use it for catalog selection in a greenfield setup; that is a separate decision documented elsewhere.

## How to apply

Work the steps in order. Maintenance, layout, governance, and disaster recovery interact; an early layout choice can save or cost weeks of maintenance work later.

### 1. Inventory the tables

1. **Categorize each table into a workload tier.** Hot streaming tables, frequent batch tables, daily ingest tables, append-only event logs, slow-changing reference tables, archival cold tables. Each tier has its own cadence.
2. **Quantify file and manifest counts** per table. Tables under 10k files rarely need aggressive maintenance; tables over 100k files almost always do. Manifests grow with snapshot count and with file count; a 50k-manifest table is past due for a rewrite.
3. **Quantify byte size and row count.** A 50 TB table with 100k files averages 500 MB per file (healthy). The same byte size with 4 million files averages 12 MB per file (sick).
4. **Record write cadence and write engine.** A table written once per hour by a single Spark job behaves very differently from a table written every 30 seconds by a streaming Flink job and read by a Trino federation.
5. **Record read patterns.** Partition-predicate queries that hit a single day's data have different layout needs than scan-heavy analytics queries across many partitions.
6. **Tag each table with its retention class.** Some tables need 7-day time travel; some need years; some have legal hold; some are derived and can be rebuilt from upstream.

### 2. Set file-size and layout targets

7. **Pick a target file size per table class.** 128 MB for hot streaming write paths, 256–512 MB for batch tables, 1 GB for cold or wide-row tables. Smaller files reduce query latency on selective reads but inflate metadata; larger files do the opposite.
8. **Pick a target rows-per-file budget** where rows are very wide or very narrow. A 1 GB file with 10 billion narrow rows is unreadable; a 1 GB file with 10k wide rows wastes parallelism. Aim for tens-of-millions to low-hundreds-of-millions rows per file for typical analytics workloads.
9. **Pick a partitioning strategy by query predicate, not by data shape.** Date is universal; secondary partitioning on tenant or region matters when those columns are in nearly every predicate.
10. **Use hidden partitioning transforms** (truncate, bucket, year, month, day, hour). They survive partition evolution and remove the need for query-time partition columns.
11. **Set the write distribution mode.** `hash` for parallel writers without skew, `range` for sorted writes, `none` when writers control file layout themselves. Mismatched distribution mode is the most common source of tiny-file proliferation.
12. **Set a sort order** that matches the dominant query's filter columns. Sort order propagates through compaction and dramatically helps Z-order-like scan pruning.

### 3. Schedule compaction

13. **Pick a per-tier compaction cadence.** Hourly bin-pack for hot streaming; daily for batch; weekly for slow-changing reference; on-demand for archival.
14. **Use bin-pack rewrite as the default.** It coalesces small files into target-sized files without re-sorting. Cheap and predictable.
15. **Use sort or Z-order rewrite for read-optimized tables.** More expensive than bin-pack but yields the best scan pruning. Schedule less often (weekly or monthly).
16. **Set a minimum-input file size for rewrite.** Files already at target size should not be rewritten — wasted I/O. Use a threshold below the target (e.g., rewrite files smaller than 75% of target).
17. **Cap rewrite group size.** Each rewrite "group" should produce files of the target size; a group of 50 small files into one 256 MB file is fine; a group of 5,000 small files into one file is a single-threaded bottleneck. Tune `rewrite-job-order` and `max-file-group-size-bytes` accordingly.
18. **Throttle concurrent rewrites.** Concurrent rewrite on the same partition causes commit conflicts. Either serialize per partition or use partial-progress mode so partial wins commit even if the whole job retries.
19. **Choose compaction compute.** A dedicated maintenance cluster (Spark or another engine) is preferable to running maintenance on the user-query cluster. Maintenance is bursty and steals capacity unpredictably.

### 4. Schedule snapshot expiration

20. **Set per-table retention by tier.** 7 days for most tables, 30 days for tables with compliance review needs, 90+ days for slow-evolving tables, or a specific number of snapshots when the snapshot rate is unpredictable.
21. **Always retain at least N snapshots** as a floor, even if all are recent. A table with one snapshot loses time travel.
22. **Expire metadata, then delete data.** The two-phase pattern: `expireSnapshots` marks the snapshots, then a `deleteOrphanFiles` or equivalent removes the underlying data and manifest files. Skipping the second step leaves storage growing.
23. **Tune `min-snapshots-to-keep` and `max-snapshot-age-ms`.** Use the more restrictive of the two; the looser one becomes the de-facto rule otherwise.
24. **Schedule expiration after compaction.** Compaction creates new snapshots; expiring before compaction loses the just-written compaction snapshot in some edge cases. Always: compact → snapshot expire → orphan cleanup.
25. **Run orphan-file cleanup carefully.** A naive orphan cleanup that lists the bucket and deletes anything not referenced from a snapshot can race with in-progress writes and delete live files. Use the engine's built-in `removeOrphanFiles` with a safe lookback window (older than 24–48 hours).

### 5. Manage manifest growth

26. **Monitor manifest count per snapshot.** A snapshot referring to thousands of manifests is slow to plan against. The internal metadata cost shows up at query time.
27. **Schedule manifest rewrites independent of data compaction.** A manifest rewrite consolidates manifest files without rewriting underlying data — cheap and effective.
28. **Tune `commit.manifest.min-count-to-merge` and `commit.manifest.target-size-bytes`.** Each table's optimum depends on its size; defaults are reasonable but a table with hundreds of partitions written hourly typically wants smaller target manifest size to keep planning fast.
29. **Watch metadata file size.** A `metadata.json` over a few MB is unusual; it usually means the snapshot list is long. Tighten retention before manifests.

### 6. Plan partition evolution

30. **Iceberg supports partition evolution without rewrite.** New partition specs apply to new writes; old data keeps its old spec. Both are queryable through the same table.
31. **Plan the cutover query window.** Queries spanning the boundary read both old and new layouts. Verify that the engine's partition pruning handles both correctly before flipping the spec.
32. **Document the evolution with an inline comment.** A `partition_spec_changed_at` table property and a runbook note prevent confusion months later when an analyst sees mixed layouts.
33. **Optional: rewrite old data to the new spec.** A `rewrite_data_files` with the new spec migrates historical data over time. Only do this when read patterns will keep hitting historical data; otherwise the cost is wasted.
34. **Drop, don't replace, deprecated transforms.** Removing a partition column from the spec is supported; replacing it inline is not. Plan the schema change as add-new, deprecate-old, eventually drop-old.

### 7. Branching and tagging

35. **Use tags for atomic publishes.** A tag is an immutable named reference to a snapshot. Producing teams can write to the main branch then tag a snapshot as `release_2026_05_14`; consumers read the tag and see a stable view.
36. **Use branches for experiment isolation.** A branch is a divergent timeline. Write experiments to a `feature_x` branch; promote by fast-forwarding main to the branch's head; abandon by deleting the branch.
37. **Set per-branch retention.** Branches can have their own snapshot retention; experimental branches typically have shorter retention than main.
38. **Tag retention overrides snapshot retention.** A snapshot referenced by a tag is never expired regardless of age. Use this for legal-hold and compliance snapshots.
39. **Document the branching workflow.** Who can create branches, who can fast-forward main, who can drop tags. Without policy, branches accumulate and become metadata noise.

### 8. Manage write concurrency

40. **Iceberg uses optimistic concurrency.** A writer reads the table state, computes its changes, then commits via the catalog with an expected snapshot id. If another writer committed in between, the second writer retries.
41. **Configure retries with backoff.** `commit.retry.num-retries=4` and exponential backoff defaults are workable; raise retries on tables with many concurrent writers.
42. **Partition writers by partition** when possible. Two writers committing to disjoint partitions still conflict at the catalog level (table-level commit), but logical conflicts are absent and retries succeed.
43. **Avoid mixed-engine writes without coordination.** Spark and Flink writers to the same table commit through the same catalog protocol but may have engine-specific assumptions; pin write engines per table when feasible.
44. **Serialize maintenance writes.** Compaction, manifest rewrite, and snapshot expiration each create a commit; serialize them in the maintenance job rather than running in parallel.
45. **For high-throughput append, use the `fast-append` mode** that skips manifest list rewrite. Pair with manifest rewrite as a separate periodic job.

### 9. Catalog operations and access control

46. **Pin the catalog.** Hive Metastore, AWS Glue, REST catalog, JDBC catalog, Nessie-compatible. Each has different concurrency, audit, and identity stories.
47. **Back up the catalog.** A catalog with no backup is a single point of failure for table location and snapshot pointers. Daily or hourly snapshot of the catalog database; longer retention for compliance.
48. **Manage table-level access via the catalog plus storage policy.** Catalog-level grants control schema visibility; storage policy controls byte-level access. Both layers are needed.
49. **Use a REST catalog when several engines coexist.** A REST catalog provides a uniform contract for Spark, Trino, Flink, and custom clients; pinning to a single backend removes implementation-specific gotchas.

### 10. Disaster recovery on object storage

50. **Two-region resilience needs three components.** The data files in the primary bucket replicated to the secondary bucket; the metadata in the primary bucket replicated to the secondary; the catalog mirrored or restorable in the secondary.
51. **Replicate the bucket with strong-consistency replication.** Cross-region replication tools that preserve ordering and provide replication lag metrics. The lag bound is your data RPO.
52. **Replicate the catalog through its native mechanism.** A relational catalog with read replicas; a Glue catalog through a cross-region copy job; a Nessie-compatible catalog with its own replication. Document the RPO and RTO targets.
53. **Run restore drills quarterly.** Pick a small subset of tables, simulate the loss, run the documented restore steps, and measure. Drills surface broken assumptions before incidents do.
54. **Document the read-only fallback path.** If the catalog is unreachable, can engines load tables via the metadata file location directly? Some engines support this and it is a useful interim mode during catalog incidents.
55. **Document the rollback path.** Iceberg supports rolling a table back to a prior snapshot. Practice it on a sandbox table; the procedure is straightforward but easy to fumble during an incident.

### 11. Observability and SLO

56. **Track per-table file count, manifest count, average file size, and snapshot count.** These metrics signal whether maintenance is keeping up.
57. **Track maintenance job duration and success.** Maintenance silently failing for weeks is a common operational failure mode.
58. **Track storage growth versus row growth.** A table whose bytes grow much faster than rows is accumulating untracked data — orphan files, missed compaction, or snapshot expiration not running.
59. **Track query latency on canonical queries** per table. A regression on read latency typically signals a layout problem before a user complains.
60. **Set SLOs.** P95 file size in range; manifest count under bound; oldest snapshot age under bound; orphan file ratio under bound. SLOs drive the maintenance triage list.

### 12. Write the runbook and schedule

61. **Maintenance schedule.** Per-table or per-tier rows in a table, with the cadence and the engine for each operation.
62. **Layout reference.** Partition spec, sort order, file-size target, write distribution mode.
63. **Branching and tagging policy.** Who can create what, with what retention.
64. **DR runbook.** Step-by-step for catalog loss, bucket loss, region loss; with RPO and RTO targets.
65. **Verification checklist.** The SLO metrics and how to read them; the chaos drills already executed; the next planned drill.
66. **Risk register.** Concurrency conflicts, runaway snapshot growth, expensive Z-order rewrites, region failover scope.

## Inputs

- An inventory of tables with row counts, byte sizes, file counts, and write cadence.
- Engines writing and reading the tables; catalog in use.
- Query patterns and latency targets.
- Storage and region layout, governance needs.
- Operational constraints — maintenance windows, available compute, budget.

## Outputs

- A maintenance schedule per tier or per table.
- Layout recommendations with partition spec, sort order, and file-size targets.
- A governance plan with branching, tagging, and retention.
- A disaster recovery plan with backups and drills.
- A verification runbook with SLOs and chaos checks.

## Examples

### Example 1: streaming event table at scale

Input: a clickstream event table written every 30 seconds by a streaming pipeline; 30 TB; 12 million files; partitioned by day plus tenant.

Plan: switch to hidden partitioning by `days(event_ts)` plus `bucket(64, tenant_id)`. Hourly bin-pack compaction with target 256 MB. Daily snapshot expiration with 7-day retention. Weekly manifest rewrite. Orphan-file cleanup with 48-hour lookback. Run maintenance on a dedicated cluster sized at 100 vCPU. Result: file count drops to under 200k within a week; query p95 drops by ~60%.

### Example 2: monthly partition evolution

Input: a sales fact table partitioned by month; the business team wants to add region as a secondary partition for the next 12 months; 18 months of history exists.

Plan: add the new partition spec `month, region` as the new default for writes. Document the evolution date. Run new ingest into the new spec; historical data continues in the old spec. After 90 days, schedule a one-time `rewrite_data_files` on the trailing 12 months to migrate to the new spec. Verify query pruning for predicates that span the boundary before promising the new SLA.

### Example 3: cross-region disaster recovery

Input: a 200-table Iceberg lakehouse on S3 in one region; the business needs an RPO of 15 minutes and RTO of 2 hours.

Plan: enable cross-region replication on the bucket with replication-time-control to bound lag. Replicate the catalog database with a read replica in the secondary region; promote the replica on failover. Quarterly drill: pick a non-critical table, simulate the primary loss, run the documented restore, measure RTO. Document the rollback for incidents that turn out to be transient. Add storage lifecycle policies that match in both regions to prevent post-failover bloat.

## Limitations

- The skill prescribes operations, not Iceberg internals tuning of compaction jobs themselves. Pair with a Spark Job Tuner skill when compaction itself is slow.
- Catalog-specific behaviors vary; specific concurrency guarantees and API contracts depend on the catalog implementation in use.
- Object-store specifics — consistency model, request quotas, eventual-consistency edge cases — differ across providers; the runbook calls out where to verify per-provider.
- Disaster recovery quality depends on the replication primitives the cloud provider offers; the plan describes the model, not the SLA.
- This skill does not cover real-time CDC ingest patterns end-to-end; pair with a streaming-ingest skill where CDC is the source.

## Sources reviewed

- https://github.com/apache/iceberg
- https://github.com/apache/spark
- https://github.com/projectnessie/nessie
- https://github.com/trinodb/trino
- https://github.com/apache/flink
- https://github.com/dremio/dremio-oss
- https://github.com/tabular-io/iceberg-rest-image
