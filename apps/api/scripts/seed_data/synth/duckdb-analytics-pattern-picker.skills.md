---
id: skillsgit-curated/duckdb-analytics-pattern-picker
version: 1.0.0
name: DuckDB Analytics Pattern Picker
description: Pick the right DuckDB pattern — in-process, attached external, federated CTE — and recognize when to use something else.
authors:
  - name: Wave-3 Data Synth
    handle: wave3-data
    role: author
category: data
tags:
  - niche:lakehouse-architecture
  - duckdb
  - embedded-analytics
  - olap
  - parquet
  - federated-query
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
  min_context_tokens: 24000
  estimated_tokens_per_invocation: 5500
trigger_keywords:
  - duckdb
  - embedded analytics
  - in-process sql
  - parquet query
  - attach postgres
  - duckdb iceberg
  - duckdb wasm
  - motherduck
example_invocations:
  - "Should I use DuckDB or Trino for this dashboard?"
  - "How do I query Parquet on S3 from DuckDB?"
  - "Can DuckDB replace our small data warehouse?"
  - "When is DuckDB the wrong choice?"
inputs:
  - name: workload
    type: text
    required: true
    description: Data size, query type, concurrency, where data lives, deployment surface.
  - name: data_locations
    type: text
    required: false
    description: Local files, S3/GCS/Azure, Postgres/MySQL, Iceberg/Delta tables, etc.
  - name: deployment
    type: text
    required: false
    description: Notebook, server-side, mobile, browser (Wasm), edge, lambda, desktop app.
outputs:
  - name: recommendation
    type: markdown
    description: Pattern selection with sample SQL, scaling limits, and exit criteria.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# DuckDB Analytics Pattern Picker

## When to use

Use this skill to pick the right DuckDB pattern for a workload — or to recognize that DuckDB is the **wrong** tool. DuckDB is brilliant inside its envelope (single-node, OLAP, embedded) and frustrating outside it. The cost of misuse is silent: it'll work in a notebook and fall over in production.

Trigger on:

- "DuckDB" + workload question
- "Parquet on S3 query"
- "embedded analytics"
- "do we need a warehouse?"
- "ATTACH postgres"
- "DuckDB Wasm in the browser"

Do **not** use for OLTP, multi-user concurrent writes, or sub-10ms request-path SQL.

## How to apply

Decide along five axes. The output is one of six patterns.

### 1. Where does the data live?

- **Local files (Parquet/CSV/JSON)**: DuckDB's home turf. Use `read_parquet('path/*.parquet')` directly; no schema setup.
- **Object storage (S3/GCS/Azure)**: install the `httpfs` extension; use `s3://bucket/path/*.parquet` with credentials via secrets. Beware: every list/get hits the network.
- **Iceberg / Delta tables**: install the `iceberg` or `delta` extension. Read-only in OSS DuckDB; for writes use a writer engine (Spark/Flink) and let DuckDB read.
- **Live OLTP DB (Postgres/MySQL/SQLite)**: `ATTACH` and query in place; DuckDB pulls only the columns and rows you need. Filters and projections push down.
- **A mix**: DuckDB's superpower is joining **across** these without materializing intermediates.

### 2. How big?

- **< 100 GB compressed Parquet on a beefy single node**: DuckDB scales here.
- **100 GB – 1 TB**: works, but you'll need careful columnar layout, file pruning, and memory tuning (`SET memory_limit='X GB'`, `SET threads = N`).
- **> 1 TB or > 10 billion rows scanned per query regularly**: use a distributed engine (Trino, ClickHouse, Snowflake, BigQuery). Don't be the person who tries to scale DuckDB beyond one node.

### 3. Concurrency model

- **Single-user, one process** (notebook, script, CLI tool, embedded in a binary): perfect fit. DuckDB is **in-process**: no server, no port, no auth.
- **Multiple readers, one writer (single process)**: fine.
- **Multiple writers across processes**: DuckDB supports concurrent reads + single-writer; cross-process writes serialize via file lock. Treat the DB file as single-author.
- **Many concurrent users hitting one shared DB**: that's a warehouse use case. Use Postgres, ClickHouse, MotherDuck (managed multi-tenant DuckDB), or Trino. Do not stand up DuckDB behind an API server hoping it scales.

### 4. Latency target

- **Interactive analyst (1–10 s)**: ideal.
- **Dashboard sub-second on warm data**: doable with materialized views (DuckDB's CTAS into a local table is your "MV"), tight WHERE clauses on sorted columns, and Parquet row-group pruning.
- **Request-path < 50 ms**: avoid; use a row-store or a serving database. Embedded vectorized scans have predictable but non-zero startup cost.

### 5. Deployment surface

- **Server / container**: install the binary or use the language client (Python, Node, Java, Rust, Go).
- **Notebook**: `pip install duckdb`; use `duckdb.sql(...)`. The de-facto "Pandas replacement" pattern.
- **Browser**: DuckDB-Wasm. Limited memory, no file system, but excellent for client-side dashboards on bounded data.
- **Mobile / edge / lambda**: works; cold start ~tens of ms; binary size is non-trivial — measure.
- **Desktop app**: DuckDB ships as a single embedded file; perfect for app-local analytics.

### The six patterns

| Pattern                                 | When                                                 |
| --------------------------------------- | ---------------------------------------------------- |
| **A. In-process local files**           | Single user, files on disk, < 100 GB.                |
| **B. In-process object-store reader**   | Single user, Parquet on S3/GCS, lakehouse Iceberg/Delta read replica. |
| **C. ATTACH-and-federate**              | Need to join OLTP + warehouse + Parquet without ETL. |
| **D. Materialize-then-serve (CTAS)**    | Repeating dashboard / report workload.               |
| **E. Wasm in the browser**              | Client-side analytics, privacy, no backend.          |
| **F. Hosted DuckDB (MotherDuck etc.)**  | Multi-user, persistent storage, team sharing.        |

### Anti-patterns to call out

- Putting DuckDB behind an HTTP server to serve concurrent users. Use a warehouse or MotherDuck.
- Using DuckDB for OLTP. It's not transactional in the row-store sense; even single-row updates rewrite columnar segments.
- Writing 100k tiny Parquet files to S3 and querying them with `httpfs` — list+get overhead dominates. Compact first.
- Treating ATTACH like a permanent ETL — for repeating production queries, materialize.
- Running DuckDB on a tiny container (1 GB RAM) for warehouse-sized scans. DuckDB is fast because it uses RAM; starve it and it spills.

### Worked snippets

Pattern B (object store Parquet):

```sql
INSTALL httpfs;  LOAD httpfs;
CREATE SECRET (TYPE S3, KEY_ID '...', SECRET '...', REGION 'us-east-1');

SELECT user_id, COUNT(*) AS events
FROM read_parquet('s3://bucket/events/dt=2026-05-*/*.parquet',
                  hive_partitioning = true)
WHERE dt >= '2026-05-01'
GROUP BY user_id
ORDER BY events DESC
LIMIT 100;
```

Pattern C (ATTACH-and-federate):

```sql
INSTALL postgres; LOAD postgres;
ATTACH 'host=db user=ro dbname=prod' AS prod (TYPE POSTGRES, READ_ONLY);

WITH active_users AS (
  SELECT id FROM prod.public.users WHERE active = true
)
SELECT e.event_type, COUNT(*)
FROM read_parquet('s3://lake/events/*.parquet') e
JOIN active_users u ON u.id = e.user_id
GROUP BY 1
ORDER BY 2 DESC;
```

Pattern D (materialize-then-serve):

```sql
CREATE OR REPLACE TABLE dashboard_daily AS
SELECT date_trunc('day', occurred_at) AS day,
       country, count(*) AS events,
       count(DISTINCT user_id) AS dau
FROM read_parquet('s3://lake/events/*.parquet')
WHERE occurred_at >= now() - INTERVAL 30 DAY
GROUP BY 1, 2;

-- serve from dashboard_daily, refresh nightly
```

## Inputs

- **workload** (required): describe rows, bytes, query shape, concurrency, latency.
- **data_locations** (optional): where data lives today.
- **deployment** (optional): notebook, server, browser, edge, etc.

## Outputs

- One of the six patterns named with a one-line rationale.
- A runnable SQL skeleton.
- A scaling ceiling: the size or concurrency at which the user should migrate to a distributed engine.
- An "exit criteria" list: signals that say "you've outgrown DuckDB".

## Examples

> "Two-person data team, weekly business reports off ~30 GB of S3 Parquet, plus a join into our Postgres user table."

Pattern C (ATTACH-and-federate). Read Parquet via httpfs, ATTACH Postgres read-only, join in-process. Exit when concurrent analyst seats exceed ~5 or scan volume per query exceeds ~500 GB.

> "Embed in a desktop app, ship analytics to customers, data lives in app-local CSV the user imports."

Pattern A. Bundle DuckDB binary, read CSV directly, CTAS to a `.duckdb` file for persistence. Exit when concurrent app sessions need to share writes (move to a hosted DB).

> "Sub-200ms dashboard for 50 concurrent business users on the same data."

Not DuckDB (single-process concurrency mismatch). Recommend ClickHouse, a Postgres + pre-aggregations, or a hosted MotherDuck/Snowflake. If they insist on DuckDB, route the API through MotherDuck.

## Limitations

- Distributed and multi-writer scenarios are out of scope.
- DuckDB write paths for Iceberg/Delta are still maturing; recommend read-only.
- The 100 GB / 1 TB thresholds are heuristic — hardware (RAM, NVMe) shifts them up.
- For browser (Wasm) deployments, validate data size against tab memory budget; OOM in a tab is a UX disaster.
- Extension availability varies by build (especially Wasm); confirm the extension you want is supported on your target platform.

## Sources

- https://github.com/duckdb/duckdb
- https://duckdb.org/docs/extensions/httpfs/overview
- https://duckdb.org/docs/extensions/iceberg
- https://duckdb.org/docs/extensions/delta
- https://github.com/duckdb/pg_duckdb
- https://duckdb.org/docs/extensions/postgres
