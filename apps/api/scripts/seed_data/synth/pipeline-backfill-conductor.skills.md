---
id: skillsgit-curated/pipeline-backfill-conductor
version: 0.1.0
name: Pipeline Backfill Conductor
description: Plan and execute a historical backfill safely — idempotency, throttling, resource sharing with live runs, validation, and stakeholder comms.
authors:
  - name: Synthwave Methodology Lab
    handle: synthwave
    role: author
category: data
tags:
  - niche:workflow-orchestration
  - backfill
  - airflow
  - dagster
  - prefect
  - idempotency
  - throttling
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
  - backfill
  - reprocess
  - replay partitions
  - historical run
  - catchup
  - airflow backfill
  - dagster partition backfill
  - prefect retro run
example_invocations:
  - Plan a backfill for the last 90 days of `orders_enriched` after a schema bug fix.
  - Help me reprocess 6 months of Kafka topic into a new Dagster asset.
  - We changed our revenue calc — plan the safe re-run without hurting live SLAs.
  - Backfill plan for 2 years of S3 partitions into Snowflake.
inputs:
  - name: orchestrator
    type: choice
    required: true
    description: Where the backfill will run.
    choices:
      - airflow
      - dagster
      - prefect
  - name: pipeline_id
    type: text
    required: true
    description: The DAG / asset key / flow being backfilled.
  - name: range
    type: text
    required: true
    description: The partition range to backfill — e.g. "2024-01-01 to 2024-06-30, daily" or "hourly partitions 2026-04-01T00 to 2026-04-30T23".
  - name: reason
    type: text
    required: true
    description: Why a backfill is needed — bug fix, new column, new asset, schema change, missed runs.
  - name: live_load
    type: text
    required: false
    description: Current live load on the system (peak concurrency, sink write throughput, expensive API quotas). Drives throttling.
outputs:
  - name: backfill_plan
    type: markdown
    description: A backfill plan with chunking, throttling, idempotency proof, validation, comms, and an orchestrator-specific execution command sequence.
changelog:
  - version: 0.1.0
    date: 2026-05-14
    notes: Initial release. Chunked, throttled backfill with safety preconditions and validation gates.
---

# Pipeline Backfill Conductor

## When to use

Use this skill when a pipeline needs to **re-process historical data** safely without harming live operations. Signals:

- "Plan a backfill for the last N days."
- "We deployed a fix; how do we reprocess past partitions?"
- "Replay this Kafka topic into a new asset."
- "We missed N runs; how do we catch up without overloading the warehouse?"
- "Reprocess the last 2 years into a new column."

Do **not** use this skill for:
- One-off re-runs of a single failed partition (just re-run it).
- Backfills that cross orchestrator boundaries (use `orchestrator-migration-planner`).
- Backfills that require a schema migration first (do the migration via `pipeline-data-contract-author` and *then* run this skill).

## Inputs

| Input         | Required | Notes |
|---------------|----------|-------|
| `orchestrator`| yes      | Determines the execution command sequence. |
| `pipeline_id` | yes      | DAG id / Dagster asset key / Prefect flow name. Must already exist. |
| `range`       | yes      | The partition range and granularity. |
| `reason`      | yes      | The skill writes different plans for "bug fix" (verify before promote) vs "new asset" (no live consumer yet) vs "missed runs" (catch up to current). |
| `live_load`   | no       | If omitted, the skill will assume a conservative throttle and flag the assumption. |

If the pipeline is not idempotent (per its own design), the skill will **refuse** to plan the backfill and instead direct the user to make it idempotent first (use `dag-architect`).

## Outputs

A backfill plan with:

1. **Summary** — what is being backfilled, why, range, expected duration, expected cost order of magnitude.
2. **Pre-flight checks** — must-pass items before the first chunk runs.
3. **Chunking** — how the range is divided.
4. **Throttling** — concurrency caps, queue isolation, rate limits.
5. **Idempotency proof** — why re-running the same partition twice is safe.
6. **Validation** — what is checked after each chunk and after the full backfill.
7. **Promotion** — how backfilled output replaces (or coexists with) current data.
8. **Comms** — who is told what, when.
9. **Execution commands** — orchestrator-specific.
10. **Rollback** — how to undo the backfill.

## How to apply

### Step 1 — Confirm the pipeline is idempotent

A backfill is only safe on an idempotent pipeline. Verify against the same checklist used in `dag-architect`:

- Every write is keyed on the partition (no blind append).
- Reads use the partition as input, not "latest".
- No side effect outside the sink (no email-on-row, no API call per record without an idempotency key).
- The sink supports overwrite-by-partition or MERGE on a stable key.

If any item fails, **stop**. Backfilling a non-idempotent pipeline corrupts data. Tell the user.

### Step 2 — Confirm the reason and shape the plan

The plan differs by reason:

- **Bug fix backfill** — backfill writes to a **shadow location** first. Validate equivalence on non-buggy partitions and divergence on buggy ones (the diff should be exactly the fix). Promote by atomic swap.
- **New column / new asset** — write directly to the target location since the new column did not exist before. No promotion phase.
- **Missed runs catch-up** — write directly to the live target; idempotency keys protect from overlap. Order matters less.
- **Source corrected upstream** — backfill is "wash and replace": delete-write to the same target partitions.

State the chosen shape in the summary so the rest of the plan is anchored.

### Step 3 — Run the pre-flight checks

Must pass *before* the first chunk:

- [ ] Pipeline runs green for the last live partition (do not start a backfill against a broken pipeline).
- [ ] Storage available for the full output (estimate from one chunk × number of chunks × 1.5 safety factor).
- [ ] Compute quota available (warehouse credits, K8s capacity, API quotas).
- [ ] Backfill queue / pool isolated from live runs (Airflow `pool=backfill`, Dagster `tag` for isolation, Prefect separate work pool or concurrency tag).
- [ ] Downstream consumers notified — they may see double writes during the dual-write window if applicable.
- [ ] On-call aware. Backfill can mask real incidents; on-call needs to know.
- [ ] A "kill switch" — a single command or flag that pauses all backfill chunks within 60 seconds.

### Step 4 — Chunk the range

Chunk size balances:
- **Restartability**: smaller chunks recover faster from failure.
- **Throughput**: larger chunks reduce per-chunk overhead.
- **Blast radius**: smaller chunks reduce damage per bad chunk.

Default chunk sizes:
- Daily-partitioned pipeline, 1+ year: chunk = 7 days.
- Daily-partitioned pipeline, < 1 year: chunk = 1 day.
- Hourly-partitioned pipeline: chunk = 6 hours.
- Event-stream replay: chunk = 1 hour of source-time or 100k events, whichever is smaller.

Total chunks = `range / chunk_size`. If total > 500, increase chunk size — operator overhead dominates beyond that count.

### Step 5 — Set throttling and isolation

The backfill **must not** harm live SLAs. Apply layered caps:

- **Concurrency cap**: max N chunks in flight at once. Default `min(4, available_workers / 4)`. For warehouses, start at 2 and increase only after observing live query latency.
- **Queue isolation**: backfill runs in its own pool/queue. Airflow `Pool` with limited slots; Dagster `tag_concurrency_limits`; Prefect separate work pool or `concurrency` block.
- **Sink rate limit**: warehouse statement concurrency capped (e.g. Snowflake warehouse with `MAX_CONCURRENCY_LEVEL`); APIs hit at < 50% of their published rate limit; object store writes paced.
- **Scheduling**: prefer off-peak hours. State the local time window.
- **Live-run preemption**: if a live run queues, pause backfill workers within one chunk boundary. Airflow: pause the backfill DAG run; Dagster: stop scheduling new partition runs; Prefect: set work-pool concurrency to 0.

State each cap as a number, not a vibe.

### Step 6 — Prove idempotency for this run

Write a one-paragraph **proof**: *"For each partition P in the range, the pipeline reads inputs filtered by P and writes outputs keyed by P using `<MERGE on PK / OVERWRITE PARTITION / delete-write>`. Therefore running the chunk twice yields the same final state as running it once."* If you cannot write this paragraph cleanly, the pipeline is not actually idempotent — go back to Step 1.

### Step 7 — Define validation gates

Validate per chunk and at the end:

Per chunk:
- Row count for the chunk is within ±5% of the row count of the equivalent calendar period in the **same** live partition's neighbors (for backfills of existing data).
- Quality SLOs from the data contract pass (use `pipeline-data-contract-author` output if available).
- Comparator (for bug-fix backfills): diff between backfilled shadow and live equals the expected fix. Anything else is investigated before the next chunk starts.

End of backfill:
- Aggregate metrics (sum of revenue, count by category, etc.) match expectations.
- Downstream consumers refresh and pass their own quality checks.
- Lineage events emitted for every partition; catalog reflects the new partitions.

If a chunk fails validation, **halt the backfill**. Do not power through.

### Step 8 — Promote (for bug-fix and replace shapes)

If the backfill wrote to a shadow:
- Final comparator run on the entire range.
- Atomic swap: rename / repoint / `ALTER TABLE ... SWAP WITH` / update the catalog pointer. Single operation.
- Keep the previous location for 7–30 days for rollback.

If the backfill wrote in place: nothing to promote; validation is the gate.

### Step 9 — Comms plan

- **D-7**: notify downstream consumers + their on-call. Explain the reason, the range, the expected window, the impact (e.g. "you may see backfilled rows update; the values will change to the new corrected calculation").
- **D-1**: confirm pre-flight checks pass; confirm window; confirm kill switch tested.
- **During**: a status thread with chunk-level progress. Pause/resume notifications.
- **D+0** (end of backfill): success notice with summary metrics, promotion timestamp, rollback availability window.
- **Post-rollback (if used)**: incident channel, postmortem within 5 business days.

### Step 10 — Write the execution commands

For the chosen orchestrator, produce the literal commands.

**Airflow**:

```bash
# Pre-flight: create / verify pool
airflow pools set backfill_pool 4 "isolation for orders_enriched backfill"

# Trigger backfill in chunks via the CLI; the loop bounds concurrency.
START="2026-04-01"
END="2026-04-30"
DAG="orders_enriched"
for d in $(seq 0 6 29); do
  S=$(date -d "$START + $d days" +%F)
  E=$(date -d "$START + $((d+6)) days" +%F)
  airflow dags backfill -s "$S" -e "$E" --pool backfill_pool --reset-dagruns "$DAG"
  # validation gate runs as a separate DAG; wait + check
done
```

For Airflow 3, prefer `airflow dags reparse` + `airflow assets backfill ...` if asset-shaped.

**Dagster**:

```python
# CLI
# dagster asset backfill -m my_module --select orders_enriched --partition-from 2026-04-01 --partition-to 2026-04-30

# Or programmatically via the GraphQL API:
# mutation launchPartitionBackfill { ... }

# Tag-concurrency for isolation, set in code:
@asset(op_tags={"dagster/concurrency_key": "backfill"})
def orders_enriched(...): ...
# instance config:
# concurrency:
#   pools:
#     backfill: 4
```

**Prefect**:

```python
from prefect.deployments import run_deployment
from datetime import date, timedelta

start, end = date(2026, 4, 1), date(2026, 4, 30)
chunk_days = 7
cur = start
while cur < end:
    nxt = min(cur + timedelta(days=chunk_days), end)
    run_deployment(
        name="orders_enriched/main",
        parameters={"start": cur.isoformat(), "end": nxt.isoformat()},
        work_pool_name="backfill_pool",  # isolated pool
        tags=["backfill"],
        timeout=0,  # fire and observe; gate with separate validator flow
    )
    cur = nxt
```

### Step 11 — Rollback

State the rollback path explicitly:

- If the backfill wrote to a **shadow** and was not promoted: drop the shadow location. Done.
- If the backfill **promoted** and rollback is needed within the retention window: atomic swap back to the previous location. Downstream consumers will see the previous data on next read.
- If the backfill wrote **in place** and is wrong: this is the worst case. The rollback is *another* backfill that restores the previous values from a snapshot. Require: a verified snapshot of the target partitions taken at pre-flight time (S3 versioning, Snowflake Time Travel, Iceberg snapshot id, Delta versions). If no snapshot exists, document that there is no rollback and require stakeholder sign-off before proceeding.

## Examples

### Example A — 90-day bug-fix backfill on `orders_enriched`

Reason: a bug undercounted refunds for partitions in `2026-02-01..2026-04-30`. Live pipeline is fixed as of `2026-05-01`.

Plan summary:
- Shape: bug-fix → shadow + atomic swap.
- Chunks: 13 × 7-day chunks.
- Throttle: 2 concurrent chunks, off-peak (22:00–06:00 UTC).
- Idempotency: writes use `MERGE ON order_id`; shadow location is `prod.orders_enriched__bf_20260514`.
- Validation: per-chunk row count parity ±0.1%; diff against live shows only refund-related rows changed; sum of refund_amount equals the expected correction (compute from raw).
- Promotion: `ALTER TABLE ... SWAP WITH` after full-range validation.
- Comms: D-7 to BI + Finance + Data team; D-1 confirmation; D+0 success.
- Rollback: keep `prod.orders_enriched__legacy` for 30 days.

### Example B — Replay last 7 days of missed runs

A sensor outage caused 7 daily partitions to be skipped.

Plan summary:
- Shape: catch-up → write to live target, no shadow.
- Chunks: 7 × 1-day.
- Throttle: 1 concurrent chunk (live runs are still happening).
- Idempotency: pipeline is `INSERT OVERWRITE PARTITION`; running over the missed partition fills it, no risk to neighbors.
- Validation: per-chunk row count within ±20% of the rolling 7-day mean (the dataset has weekday seasonality).
- Promotion: none.
- Rollback: not required; missed partitions had no prior content.

## Limitations

- The skill does **not** estimate backfill cost in dollars. It identifies cost drivers (compute hours, sink writes, API calls) and asks the operator to apply rate cards.
- The skill assumes the source data for the backfill range is still available. If the source is itself ephemeral (a stream past retention, a deleted file, an API that does not allow historical pulls), backfill is impossible — the skill will say so.
- The skill does not write the validation queries; it specifies their shape. Pair with a SQL-authoring skill if needed.
- For streaming-replay backfills (Kafka offsets), the skill addresses the orchestration shape but not the broker config (retention extensions, consumer-group resets) which must be coordinated with platform owners.
- Backfills that themselves require a schema migration must be sequenced: do the migration first, version the data contract, *then* run the backfill against the new schema.

## Sources (verified)

- https://github.com/apache/airflow — Apache-2.0
- https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html — Apache-2.0 (project docs)
- https://github.com/dagster-io/dagster — Apache-2.0
- https://docs.dagster.io/guides/build/assets/defining-assets — Apache-2.0 (project docs)
- https://github.com/PrefectHQ/prefect — Apache-2.0
- https://docs.prefect.io/v3/api-ref/python/prefect-tasks — Apache-2.0 (project docs)
- https://github.com/apache/airflow/discussions/28905 — Apache-2.0 (idempotency reference for the proof step)
