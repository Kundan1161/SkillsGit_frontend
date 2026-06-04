---
id: skillsgit-curated/duckdb-production-patterns
version: 1.0.0
name: DuckDB Production Patterns
description: Choose production DuckDB patterns for in-process analytics, ATTACH federation, S3 and HTTPFS access, materialized views, concurrency boundaries, and when to graduate to a clustered engine based on workload shape and scale.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:duckdb-patterns, duckdb, in-process-olap, federation, httpfs, materialized-views, parquet, embedded-analytics]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1]
  tools_required: []
  tools_optional: [code_execution]
  min_context_tokens: 24000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - duckdb production
  - duckdb at scale
  - duckdb in process
  - duckdb attach
  - duckdb httpfs
  - duckdb s3
  - duckdb materialized view
  - duckdb concurrency
  - duckdb vs clickhouse
  - duckdb vs spark
  - duckdb embedded
  - duckdb federated query
  - graduate from duckdb
  - duckdb parquet
example_invocations:
  - "We want to use DuckDB as the query engine for our analytics service. Design the deployment."
  - "Pick a pattern for letting DuckDB read parquet from S3 with sub-second latency."
  - "When should we move our DuckDB workload to a clustered engine? Build the graduation criteria."
  - "Set up federation so DuckDB reads from both Postgres and S3 parquet for ad-hoc joins."
  - "Our DuckDB jobs are slow under concurrency. Diagnose and design the right pattern."
inputs:
  - name: workload_description
    type: text
    required: true
    description: What the workload does — ad-hoc analytics, scheduled ETL, embedded analytics in an app, notebook usage, dashboard backend, BI tool target. Latency targets per query class.
  - name: data_volumes
    type: text
    required: false
    description: Raw input size, working-set size, expected query-touched size, growth rate, partition layout if any.
  - name: deployment_environment
    type: text
    required: false
    description: Process model — single CLI, embedded library in a service, serverless function, notebook kernel. Memory and CPU envelope per process.
  - name: concurrency_profile
    type: text
    required: false
    description: Concurrent query count, read vs write split, transactional semantics needed, multi-writer requirements.
  - name: data_sources
    type: text
    required: false
    description: Sources to read from — local parquet, S3 parquet, HTTPS files, Postgres, MySQL, SQLite, Iceberg, Delta, Arrow flight, in-memory dataframes.
  - name: persistence_needs
    type: text
    required: false
    description: Whether the database file persists, whether materialized state matters, retention policy, backup needs.
outputs:
  - name: deployment_pattern
    type: markdown
    description: The concrete pattern — single-file local, read-only library replica, ephemeral worker per request, attached federation — with rationale.
  - name: data_access_plan
    type: markdown
    description: How DuckDB reads each source — extensions, credentials, prefetching, caching, partition pruning, projection pushdown.
  - name: concurrency_plan
    type: markdown
    description: Connection model, isolation expectations, read vs write paths, queueing, and the place where multi-writer goes wrong.
  - name: performance_plan
    type: markdown
    description: Pre-aggregations, materialized views, per-thread settings, memory limits, profiling approach.
  - name: graduation_criteria
    type: markdown
    description: Quantitative signals — working-set size, concurrent query count, write throughput, multi-region needs — that say "move off DuckDB" with the next engine class to consider.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when DuckDB is being considered or is already in production and the team needs an opinionated deployment plan rather than ad-hoc snippets. Typical triggers:

- An analytics service that currently sends queries to a clustered warehouse but the query volume and latency budget suggest an in-process engine would be cheaper and faster.
- A scheduled job that loads parquet files from object storage and runs aggregations whose intermediate state is small enough to fit on one machine.
- An embedded analytics use case — a desktop or mobile app, a CLI, a serverless function — where shipping a query engine inside the process matters.
- A notebook or dashboard environment where queries should be fast and local but data lives in object storage.
- A team that uses DuckDB today and is hitting concurrency, memory, or write-throughput ceilings and is debating whether to scale up or move to a clustered engine.

Do not use this skill for OLTP workloads with many concurrent writers; DuckDB is an analytical store. Do not use it for multi-node distributed queries; DuckDB is single-process by design. Do not use it as a substitute for a warehouse with strong concurrent write transactions across many sessions.

## How to apply

Work the steps in order. The deployment pattern in step 2 cascades through every later step; reconsider it if a later step exposes a constraint that pattern cannot meet.

### 1. Classify the workload

1. **State the latency target per query class.** Sub-second interactive, single-digit-seconds for dashboards, minutes for batch. The target gates pattern choice.
2. **State the concurrency target.** Single user, a few simultaneous queries, hundreds of concurrent dashboard hits. DuckDB scales beautifully within a process but the process is the unit of scale.
3. **State the working-set size.** Total data lives in storage; working set is the bytes touched by typical queries. A 10 TB table with queries that always filter by day touch tens of GB — that is the working set, not 10 TB.
4. **State the write profile.** Append-only ingest from a single writer, periodic batch reloads, occasional ad-hoc inserts, or no writes (read-only library replica). The right pattern differs sharply.
5. **State the persistence need.** A query engine that loads parquet from object storage and discards state after each request is one mode; a long-lived database file is another.
6. **State the embedding constraints.** Process memory ceiling, available cores, container runtime, OS, and any restriction on file system access.

### 2. Pick the deployment pattern

7. **Pattern A: in-process embedded library.** DuckDB linked into the application process. The process owns the database file. Best for desktop, mobile, single-tenant web service, and CLI use. Concurrency is limited to one process; horizontal scale requires partitioning data across processes.
8. **Pattern B: ephemeral worker per request.** A short-lived process spawned per query that reads from object storage, executes, and exits. No persistent state; horizontal scale by spawning more workers. Best for serverless analytics, dashboard backends, and notebook-on-demand.
9. **Pattern C: long-lived service with shared file.** A long-lived process serving many queries from a persistent database file. Best when the data fits or can be sharded by tenant and the file lives on a fast disk.
10. **Pattern D: read-only file replica.** A canonical writer produces a database file on a schedule and replicates it to many reader processes that mount it read-only. Best when the read concurrency is high and writes are infrequent.
11. **Pattern E: federated frontend.** DuckDB attached to external sources (Postgres, MySQL, SQLite, Iceberg, S3 parquet, HTTPS files) and used as a join-and-project layer. Best for ad-hoc analytics across heterogeneous sources where the working set is small.
12. **Pick on the persistence-and-concurrency axes.** Long-lived state plus high concurrency favors C or D. Stateless plus high concurrency favors B. Stateful single-user favors A. Heterogeneous sources favor E.

### 3. Wire data access

13. **Local parquet is the cheapest read.** Mounted disk or fast NVMe; let DuckDB's parquet reader handle pruning and projection. Predicates on partition columns derived from file paths require `hive_partitioning=1` to be set.
14. **S3 and HTTPFS for object storage.** The HTTPFS extension reads parquet, CSV, and JSON directly from S3-compatible storage. Configure credentials via the secret manager or environment variables. Tune the prefetch buffer for high-throughput sequential reads.
15. **Iceberg and Delta read paths via extensions.** Read-only access through the iceberg or delta extensions, with the catalog wired to a metastore or REST catalog. Time travel and snapshot selection are supported as table-function arguments.
16. **ATTACH for Postgres/MySQL/SQLite.** The relational ATTACH lets DuckDB query foreign databases via the catalog. Pushdown of filters and projections is partial; expect full scans for complex expressions. Use it for joins where one side is small and the other lives in the foreign database.
17. **ATTACH for DuckDB-over-DuckDB federation.** Multiple DuckDB files attached to the same session; queries join across files. Useful for tenant-per-file deployments.
18. **Arrow integration for in-memory dataframes.** DuckDB queries pandas/Polars dataframes zero-copy. Best in notebook flows where the dataframe was just produced by another step.
19. **Set the `httpfs_keep_alive` and `s3_uploader_*` knobs** when reading at scale from object storage. Default settings are tuned for interactive use; production loads benefit from larger buffers.

### 4. Tune for the platform

20. **Set `memory_limit` explicitly.** The default is most of host RAM; in a multi-tenant or containerized environment, set a budget so DuckDB does not OOM the container.
21. **Set `threads` to the cores available to the process.** Default is logical core count; under cgroup quotas, set it to the quota.
22. **Set `temp_directory` to fast scratch.** Spill destination for queries that exceed memory; a tmpfs or NVMe is appropriate, network-attached storage is not.
23. **Enable progress bar and profiling only where useful.** `PRAGMA enable_profiling` for development; turn off in production to keep latency clean.
24. **Set `preserve_insertion_order=false`** for bulk loads where order does not matter — improves performance.

### 5. Pre-aggregate and materialize

25. **A "materialized" pre-aggregate is just a stored table.** DuckDB does not have transparent materialized-view maintenance; the pattern is to compute a stored aggregate table on a schedule and have queries hit it directly.
26. **For incremental aggregates, write the source-to-aggregate refresh as an explicit job.** Identify the new partitions, aggregate them, append to the aggregate table. Handle deduplication at append time.
27. **Use parquet for cold storage of aggregates.** A nightly aggregate written as parquet to object storage is cheap to keep and fast to read; the query engine reads it through the parquet path.
28. **Use views for logical reuse.** A view is free; queries get the cost of the underlying scan. For commonly used joined-and-filtered shapes, views improve readability without performance impact.
29. **Index sparingly.** DuckDB has secondary indexes for primary keys and unique constraints; full secondary indexes for analytics are not the right tool. Lean on partition pruning and clustering instead.
30. **Cluster by sort.** A parquet file written sorted by a frequently filtered column gives the parquet reader skip data via min/max stats. Sort during the write, not at query time.

### 6. Plan concurrency

31. **One process, many connections.** A single DuckDB process supports many concurrent connections in the same address space; queries run in parallel using the configured thread pool.
32. **Reader concurrency scales well.** Read-only queries can run in parallel without locking; the cost model parallelizes scans and joins automatically.
33. **Writer concurrency is the constraint.** A single writer at a time is the default. Mixing concurrent writers and readers in the same database requires care; transactional isolation is single-process MVCC.
34. **Multi-process write requires application-level coordination.** Two processes writing to the same DuckDB file is not safe in general; either route writes through a single process or partition data across files.
35. **Queue writes if needed.** A small write queue (one consumer process, many producers) avoids contention and gives explicit backpressure.
36. **Long-running queries hold resources.** A 30-second query consumes its share of the thread pool; if dashboard hits arrive faster than that, set a query timeout and a connection pool size.

### 7. Decide on persistence

37. **Pick the database file location.** Local fast disk is the canonical place; a network-attached share is acceptable for low-frequency access; object storage for the database file itself is not supported as a live mount.
38. **Plan backups.** For a long-lived database file, copy the file when it is not being written to; for higher-frequency backup, export tables to parquet on a schedule.
39. **Plan recovery.** A corrupted DuckDB file is a process incident; restoring from the latest backup or a parquet export is the usual path. Avoid in-place patching attempts.
40. **For ephemeral-worker patterns, persistence is parquet on object storage.** The DuckDB process holds only intermediate state and exits.

### 8. Observability

41. **Log every query with its duration, rows touched, and bytes read.** A small middleware that wraps the connection and emits structured logs is enough for most deployments.
42. **Surface slow queries to a dashboard.** Per-pattern p50/p95/p99; investigate any p99 over the target.
43. **Surface scan vs filter ratios.** A query that reads 10 GB but returns 100 rows after filtering is a candidate for clustering or pre-aggregation.
44. **Surface memory and spill events.** A query that spills indicates the working set exceeds budget; either raise memory, partition the workload, or pre-aggregate.
45. **Health-check the process.** A simple `SELECT 1` plus a sentinel query is enough; richer checks watch for catalog drift in federated setups.

### 9. Security and isolation

46. **Run as a non-root user.** Standard hygiene; the process should have minimum filesystem and network access.
47. **Restrict extension loading.** Set `allow_unsigned_extensions=false` and pin the extension repository to a known source.
48. **Manage secrets via the secret manager** for S3/HTTPFS credentials. Avoid baking long-lived keys into images.
49. **Tenant isolation.** One database file per tenant is the cleanest model. Single-file multi-tenant requires application-level filtering with absolute trust in the filter logic.
50. **Audit query content** for sensitive workloads. A query log with the SQL text supports compliance review.

### 10. Define graduation criteria

51. **Working-set ceiling.** When the bytes touched by typical queries grow past one-machine RAM plus reasonable spill, move on. The signal is sustained spill across most queries.
52. **Concurrency ceiling.** When the thread budget is exhausted and dashboard hits queue beyond the latency target, either shard across processes (still DuckDB) or move to a clustered engine.
53. **Write-throughput ceiling.** When ingest rates exceed single-process write throughput (typically order of magnitude tens to hundreds of MB/s depending on hardware) and partitioning across processes does not solve it, the workload is not in DuckDB's sweet spot.
54. **Multi-region need.** A workload that needs synchronous reads in two regions requires a distributed engine; DuckDB is single-process.
55. **Strong cross-session transactions.** ACID transactions across many concurrent sessions belong to a transactional warehouse.
56. **Cluster-managed metadata.** Tens of thousands of tables with centralized governance, lineage, and access control point to a clustered system with a real catalog.
57. **The next engine class.** Single-machine scale-up; columnar single-node engines with richer concurrency; clustered MPP engines for petabyte scans; a managed warehouse for high concurrency plus governance.

### 11. Write the deployment plan

58. **Pattern section.** Which of patterns A–E and why.
59. **Access section.** Extensions installed, credentials, source-by-source read path, prefetch and buffer settings.
60. **Concurrency section.** Connection model, thread settings, write coordination, queueing.
61. **Performance section.** Pre-aggregates, materialized tables, sort and cluster, memory budgets.
62. **Persistence section.** Database file location, backup, recovery.
63. **Observability section.** Logging, dashboards, health checks.
64. **Graduation section.** The numeric thresholds that say "this workload no longer belongs here" and the engine class that will replace it.

## Inputs

- A workload description with latency, concurrency, and volume targets.
- The deployment environment — process model, memory, cores.
- The data sources to read from and the persistence needs.

## Outputs

- A deployment pattern with rationale.
- A data-access plan covering each source.
- A concurrency plan with the write boundary.
- A performance plan with pre-aggregates and tuning.
- Graduation criteria with the next-engine choice.

## Examples

### Example 1: dashboard backend serving 200 concurrent users

Input: a SaaS dashboard backend that runs aggregations over the last 90 days of event data; data lands as hourly parquet on S3; 200 concurrent dashboard sessions; latency target p95 under 800 ms.

Plan: pattern B (ephemeral worker per request) behind a thin request router. Workers prefetch the partition files for the user's tenant via HTTPFS with a generous prefetch buffer. A nightly job writes per-tenant pre-aggregates as parquet that workers prefer over raw events. Worker process pool sized to peak concurrent queries; per-worker memory cap 4 GB; thread budget 4 per worker. Add a Postgres ATTACH for the small dimension tables. Graduation criterion: if working set per query exceeds 8 GB or concurrent queries exceed worker capacity, shard tenants across worker pools.

### Example 2: notebook environment over a parquet lake

Input: a data science team running interactive notebooks over a 5 TB parquet lake on S3; one to two analysts at a time; latency target sub-10-seconds for "give me a feel" queries; no writes from notebooks.

Plan: pattern E (federated frontend). Each notebook kernel hosts a DuckDB instance with HTTPFS, Iceberg, and Postgres extensions. Read-only access. A `notebook_views.duckdb` file holds saved views and small reference tables. Pre-aggregates from upstream batch land as parquet that analysts read. Set memory cap to 75% of kernel host. No graduation pressure unless concurrent analyst count grows past the host's thread budget.

### Example 3: embedded analytics in a desktop app

Input: a desktop app shipping with bundled DuckDB to give users local analytics on their own data; single user; data sizes 100 MB to 50 GB; user-installable.

Plan: pattern A (in-process embedded library). DuckDB statically linked or shipped as a platform binary. Database file in the app's user-data directory. Materialized aggregates updated on import. Memory cap set to half of host RAM. Backup is a file copy. No graduation criterion — this pattern is the destination.

## Limitations

- DuckDB is single-process; this skill does not architect distributed query execution. For multi-node, pair with a clustered-engine selection skill.
- Write concurrency on a single file is limited; multi-writer designs require application-level coordination not detailed beyond the boundaries.
- Extension behaviors (Iceberg, Delta, JSON) evolve quickly; verify version-specific capabilities against the live extension matrix before relying on a feature.
- Persistence and recovery patterns assume a Linux-style file system; embedded environments (mobile, browser) follow similar patterns with environment-specific storage primitives.
- Cost-attribution and chargeback are not central to single-process deployments; pair with a lakehouse-cost skill when multi-tenant cost control matters.

## Sources reviewed

- https://github.com/duckdb/duckdb
- https://github.com/duckdb/duckdb_iceberg
- https://github.com/duckdb/duckdb_delta
- https://github.com/duckdb/duckdb_httpfs
- https://github.com/pola-rs/polars
- https://github.com/apache/arrow
- https://github.com/apache/iceberg
