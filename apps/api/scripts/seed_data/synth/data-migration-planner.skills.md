---
id: skillsgit-curated/data-migration-planner
version: 1.0.0
name: Schema Migration Planner
description: Drafts a phased schema-migration plan for non-trivial changes (adds, renames, drops, type changes, table splits) with rollback strategy and zero-downtime deployment steps.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [schema-migration, zero-downtime, postgres, mysql, ddl, deploy, rollback, expand-contract]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: [code_execution]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - schema migration
  - database migration
  - zero downtime
  - online ddl
  - expand contract
  - rename column
  - drop column
  - column type change
  - backfill
  - rollback plan
  - alter table large
  - blue green database
  - dual write
example_invocations:
  - "Plan a zero-downtime migration to rename `user_email` to `email` on a 200M-row table."
  - "I need to change a column from VARCHAR to INT — how do I do this safely?"
  - "Plan splitting our `orders` table into `orders` and `order_line_items`."
  - "Write a rollback plan for adding a NOT NULL column with a default."
inputs:
  - name: current_schema
    type: text
    required: true
    description: The current relevant DDL (CREATE TABLE, indexes, foreign keys, triggers). Include any column comments.
  - name: desired_change
    type: text
    required: true
    description: A precise description of the change — what column or table is changing, the new shape, and why.
  - name: data_volume
    type: text
    required: true
    description: Approximate row count, table size in GB, and write rate (rows/sec at peak). Drives backfill and online-DDL choices.
  - name: database_engine
    type: choice
    required: true
    description: Target database engine.
    choices: [postgres, mysql, sqlite, snowflake, bigquery, redshift, sqlserver, oracle, other]
  - name: downtime_budget
    type: choice
    required: true
    description: Acceptable downtime for the migration.
    choices: [zero, seconds, minutes, hours]
  - name: app_deploy_model
    type: text
    required: false
    description: How application code is deployed (rolling, blue/green, canary, all-at-once). Affects dual-write and read-from-new-column phases.
outputs:
  - name: phased_plan
    type: markdown
    description: An ordered list of phases (expand, migrate, contract) with the exact DDL and code steps in each.
  - name: ddl_scripts
    type: markdown
    description: The forward DDL for each phase.
  - name: rollback_plan
    type: markdown
    description: Per-phase rollback steps and the point of no return.
  - name: risk_assessment
    type: markdown
    description: Identified risks with mitigations and monitoring recommendations.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill any time a database schema change is non-trivial enough to deserve a written plan. Indicators:

- The target table has more than a few million rows or is under continuous write load.
- The downtime budget is zero or very small.
- The change is destructive or irreversible (column drop, type narrowing, table split).
- A rolling deploy means old and new application code will run simultaneously against the database for at least a few minutes.
- The change touches a primary key, a unique constraint, or a heavily-used index.
- A previous attempt at this change failed and the team wants a more careful plan.

Do not invoke this skill for trivial changes (adding a nullable column to a small table) where the routine migration tooling already handles the case. The plan it produces is overkill there and the user is better served by their migration tool's default behavior.

## How to apply

The methodology follows an **expand → migrate → contract** pattern: never modify in place when a multi-phase plan can keep both old and new shapes valid simultaneously. Each phase ends in a state where the application is healthy and rollback is possible. Only the final contract phase is one-way.

### 1. Establish context

1. **Read every input.** Confirm current schema, desired change, volume, engine, downtime budget, and deploy model. If any field is missing, ask before continuing.
2. **Restate the change in your own words.** Confirm with the user before drafting the plan. Misunderstood requirements are the dominant cause of failed migrations.
3. **Classify the change.** Use the categories below; each has a canonical plan shape.
   - Add column (nullable / not null / with default)
   - Drop column
   - Rename column
   - Change column type (widening / narrowing / lossless / lossy)
   - Add index (unique / non-unique / partial / covering)
   - Drop index
   - Add foreign key
   - Drop foreign key
   - Add unique constraint
   - Split table (vertical or horizontal)
   - Merge tables
   - Change primary key
   - Add or change a CHECK constraint
   - Add or change a generated column
4. **Identify the database engine's constraints.** Postgres, MySQL, Snowflake, BigQuery, and Redshift differ sharply on what can be done online. Note relevant facts:
   - **Postgres:** Recent versions allow many ALTERs without rewriting the table; `ADD COLUMN ... DEFAULT` is metadata-only on Postgres 11+ when the default is a constant; `CREATE INDEX CONCURRENTLY` is the safe way to build indexes.
   - **MySQL:** Online DDL via `ALGORITHM=INPLACE, LOCK=NONE` works for some operations; tools like gh-ost or pt-online-schema-change shadow-table the change for the rest.
   - **Snowflake / BigQuery:** ALTERs are usually instantaneous because the engines are columnar and metadata-driven, but type changes and partition-key changes may require table rewrites.
   - **Redshift:** Many ALTERs require a table rewrite. Use `DEEP COPY` and rename when needed.
5. **Compute write-volume sensitivity.** If peak write rate is over a few hundred rows/sec, exclusive locks or even brief table rewrites become user-visible. Use this to choose between in-place DDL, online DDL, and shadow-table approaches.

### 2. Plan the expand phase

The expand phase adds the new shape without removing the old. After expand, both old and new code can run.

6. **For an add: add the new column nullable, no default.** Filling in a default on a large table can be a multi-hour scan on engines that rewrite. Separate the "add" and the "backfill" steps explicitly.
7. **For a rename: add a new column with the new name.** Do not use `ALTER TABLE ... RENAME COLUMN` yet — that breaks any old code that still reads the old name during the rolling deploy. Both columns will coexist during dual-write.
8. **For a type change: add a new column of the new type alongside the existing one.** Type changes that touch every row are nearly always cheaper as expand-migrate-contract than as in-place.
9. **For a table split: create the new table(s) with no data.** Do not begin moving data yet.
10. **For an index add: build the index online.** Postgres `CREATE INDEX CONCURRENTLY`, MySQL `ALGORITHM=INPLACE, LOCK=NONE`. If the engine cannot build the index online, schedule the index build in a maintenance window.
11. **For a unique constraint add: first build the supporting unique index online, then `ALTER TABLE ... ADD CONSTRAINT ... USING INDEX`** on engines that support that two-step. The two-step keeps the locking window down.
12. **For a foreign key add: add the FK as `NOT VALID` first (Postgres), then `VALIDATE CONSTRAINT` separately.** The validate step takes a strong lock but is fast if the data is already clean; if it fails, you find dirty rows without holding the lock through the whole scan.
13. **For a NOT NULL on an existing nullable column: add a CHECK constraint `NOT VALID` first**, backfill the NULLs, then `VALIDATE`, then in a later release convert to a column NOT NULL.
14. **Write the expand DDL.** Every statement must be idempotent: wrap in `IF NOT EXISTS` where the engine supports it; otherwise check the catalog first.
15. **Verify expand is rollbackable.** Each expand step's rollback is "drop the new thing" — that is allowed because no application reads from the new shape yet.

### 3. Plan the dual-write phase

The dual-write phase deploys application code that writes to both the old and the new shape simultaneously. Reads still come from the old shape.

16. **Update application code to write to both columns / tables.** Every code path that wrote to the old shape must now also write to the new. Use a feature flag if rollout is staged.
17. **Decide between application dual-write and database triggers.** Application dual-write is preferred because it lives in source control and is easy to roll back. Triggers are appropriate when the writes come from multiple applications, third-party tools, or replication streams the application does not control.
18. **If using triggers:** make the trigger forward-only (write the new shape, never derive new from old in a way that loses precision). Trigger writes must be idempotent — the same source row written twice must produce the same target value.
19. **Ship the dual-write code; do not move on until 100% of write paths are dual-writing.** Verify by sampling rows written in the last hour and confirming the new column / table received the corresponding value.
20. **Establish a metric.** Count rows where `new_column IS NULL AND old_column IS NOT NULL` (or the table-split equivalent). This metric must reach zero for new writes before backfill begins.

### 4. Plan the backfill

The backfill phase fills in the new shape for historical rows that pre-date dual-write.

21. **Batch the backfill.** Never issue a single UPDATE over the whole table on a large table — it will hold long locks, blow out WAL/binlog, and may time out. Update in batches of 1k–50k rows depending on engine and write rate.
22. **Throttle.** Sleep between batches to keep replication lag and CPU under control. Common targets: replication lag under 5 seconds, CPU under 70%.
23. **Resume safety.** The backfill script must be resumable — if it crashes at 47% complete, restarting must not re-update the rows it already processed. Use a watermark column (`backfill_done_at IS NULL`) or a range driver (`WHERE id BETWEEN X AND Y`) tracked externally.
24. **Validate the backfill.** After the script declares completion, run a separate validator that randomly samples rows and confirms `new_column = transformed(old_column)` for every sampled row. The validator is not the same code as the backfill — independent implementations catch transformation bugs.
25. **Watch for new rows that the dual-write missed.** If the metric from step 20 is non-zero for recent rows, find the missing write path before continuing.
26. **For table splits:** the backfill copies rows from the old table to the new tables. After the copy completes, run a count check and a sample-equality check.

### 5. Plan the switch-read phase

Now the application starts reading from the new shape. Writes continue to both.

27. **Deploy code that reads from the new column / table.** Behind a feature flag if possible; flip the flag for a small percentage of traffic first.
28. **Monitor.** Watch error rates, latency, and any business metric that touches the changed column. A spike here is the signal to flip the flag back and investigate.
29. **Verify read parity.** For a sample of requests, log both the old and new read value and confirm they match. Discrepancies indicate either a stale backfill or a missed write path.
30. **Ramp the flag to 100%** only after the verification log has shown matching reads for at least one full business cycle (24 hours, a week — depending on the domain).

### 6. Plan the stop-write-old phase

31. **Update application code to stop writing to the old shape.** Old column / old table now receives no new writes.
32. **Wait.** Leave the old shape in place for at least one full business cycle in this state. If a bug surfaces requiring you to roll back to old reads, the old shape must still be up-to-date enough to serve correctly. Stopping writes too early followed by a rollback is a common cause of data loss.
33. **Monitor the old shape's read traffic.** Engine-specific tooling (Postgres `pg_stat_user_tables`, MySQL performance_schema, query logs) will tell you whether anything is still reading the old column / table — including ad-hoc dashboards and analytics. Track these consumers down before contraction.

### 7. Plan the contract phase

The contract phase removes the old shape. This is the only one-way step.

34. **Drop the old column / table.** Do this in a separate, isolated release — do not bundle with other changes.
35. **For a rename completion: do nothing in the database.** The "rename" was completed at switch-read; the database just sees an old column being dropped now.
36. **For a type change completion: drop the old column.** The old column has been ignored since switch-read.
37. **For a table split completion: drop the old table.** Optionally, keep a backup snapshot for some grace period.
38. **Do not drop indexes or foreign keys "while you're in there".** Each contraction is its own release.

### 8. Engine-specific tactics

39. **Postgres recommendations:**
    - Use `lock_timeout` and `statement_timeout` on every DDL statement so a blocked migration fails fast rather than holding the lock forever.
    - `CREATE INDEX CONCURRENTLY` is the standard online index build; if it fails it leaves an `INVALID` index that must be dropped before retrying.
    - `ADD COLUMN ... DEFAULT constant` is metadata-only on PG 11+. `ADD COLUMN ... DEFAULT volatile_function()` still rewrites — split it.
    - Use partition swapping for column-type-change migrations on partitioned tables.
    - For shadow-table style migrations on Postgres, consider tooling that wraps the table in views to serve old and new schema concurrently.
40. **MySQL recommendations:**
    - Prefer `ALGORITHM=INPLACE, LOCK=NONE` where supported. The MySQL documentation lists the matrix per ALTER type.
    - For operations not supported online, use binlog-based shadow-table tooling rather than trigger-based, when available. Binlog-based tools cause less write amplification.
    - Watch foreign keys — they constrain which online DDL paths are valid.
41. **Snowflake / BigQuery recommendations:**
    - Most ALTERs are metadata-only and effectively instant.
    - Type changes that require a rewrite are best done via CTAS (`CREATE TABLE new AS SELECT ... FROM old`) and swap.
    - Partition / cluster key changes always require a rewrite — plan for it.
42. **Redshift recommendations:**
    - Many ALTERs require `DEEP COPY`. Plan for a full table copy and rename.
    - Sortkey and distkey changes always rewrite — schedule them carefully.

### 9. Rollback strategy

43. **Each phase ends in a stable state.** State explicitly which phases are reversible (expand, dual-write, backfill, switch-read, stop-write-old) and which are not (contract).
44. **Per phase, write the exact rollback steps.**
    - After expand: drop the new column / table / index.
    - After dual-write: stop writing the new shape; the data already written is harmless because nothing reads it.
    - After backfill: data in the new shape is consistent but unused — no action needed.
    - After switch-read: flip the read flag back to old.
    - After stop-write-old: re-deploy code that writes the old shape; backfill old shape from new for any rows written during the gap.
    - After contract: rollback is "restore from backup". State this baldly.
45. **Identify the point of no return.** The contract step is irreversible without a backup restore. Confirm with the user when they want to cross that line — many teams choose to leave the old shape in place for weeks before contracting.

### 10. Risk assessment

46. **Replication lag.** A long backfill produces large amounts of binlog/WAL that replicas must apply. Plan for elevated lag and confirm read-replicas can keep up. If they cannot, throttle harder.
47. **Lock escalation.** Some engines escalate row locks to table locks under load. Test the migration on a representative replica before running on primary.
48. **Long-running transactions.** A pre-existing long transaction can block DDL indefinitely. Identify and kill or wait out long transactions before issuing DDL with a strict lock_timeout.
49. **Connection pool churn.** When a DDL holds a lock, connections pile up. Set application-level timeouts so a stuck migration does not exhaust the pool.
50. **Foreign-key cascades.** A column-type change on a parent FK column may force the same change on all child tables. Identify the full set up front.
51. **Trigger and rule interactions.** Existing triggers may misbehave on the new column shape. Audit triggers before expand.
52. **Materialized views.** A column change may invalidate dependent materialized views. List all dependents and refresh-plan them.
53. **External consumers.** Analytics replicas, CDC streams, change-data-capture-fed search indexes, and downstream warehouses all see schema changes. Coordinate with their owners. Add the new column to the CDC stream during expand so downstream systems see it early; drop the old column from CDC selectors before contract.

### 11. Validation and observability

54. **Pre-flight check.** Before running expand on prod, run the entire plan on a copy of prod (or staging with prod-shaped data). Time each step. Use the timings to estimate the prod run.
55. **Per-step success criteria.** Each step has a single checkable success condition. State it. Examples: "rowcount of new column non-null equals rowcount of old column non-null" or "average write latency over the next 10 minutes within 10% of baseline".
56. **Per-step monitoring dashboard.** Identify the metrics to watch live: lock waits, replication lag, error rate on the affected endpoints, write throughput.
57. **Abort criteria.** Define the conditions under which the migration is paused or rolled back: lock wait > N seconds, replication lag > M seconds, error rate up by P percent. State the criteria before starting so the operator does not have to invent them mid-incident.
58. **Communication plan.** Migrations of this size are not silent. Tell the on-call channel before expand, before switch-read, and before contract. Each communication includes the abort criteria and the expected duration of the step.

### 12. Output format

59. **Produce a phased timeline.** Each phase: name, expected duration, prerequisite, success criterion, rollback step.
60. **Produce the DDL for each phase in order**, with comments explaining what each statement does and why.
61. **Produce a rollback annex.** For each phase, the rollback steps in copy-paste form. Mark the contract step as "one-way".
62. **Produce a risk table.** Risk, likelihood, impact, mitigation. Sort by impact × likelihood descending.
63. **Produce a checklist.** A short, ordered checklist the operator can tick through on the day of the migration. The checklist is the executable summary of everything above.
64. **End with explicit open questions.** Any assumption you made — about the write rate, the deploy model, the presence of downstream consumers — gets listed as a question for the user to confirm before the plan is acted on.

## Inputs

- Current DDL.
- A precise description of the change.
- Volume and write-rate estimates.
- The database engine.
- The acceptable downtime budget.
- Optional: the application deploy model.

## Outputs

- A phased plan (expand / dual-write / backfill / switch-read / stop-write-old / contract).
- DDL per phase.
- Per-phase rollback steps.
- Risk table.
- Operator checklist.
- Open questions.

## Examples

**Renaming a hot column**

> Input: rename `user_email` to `email` on a 200M-row Postgres `users` table; peak write rate 1.5k rows/sec; zero downtime.
>
> Expected plan: expand adds `email TEXT` nullable; dual-write phase ships application code writing both columns; backfill copies `user_email` to `email` in 10k-row batches with 100ms sleeps and a watermark column; switch-read phase swaps reads under a feature flag; stop-write-old phase removes the write to `user_email`; contract drops `user_email` two weeks later. Total elapsed time: 3-5 weeks counting the soak periods. Total prod downtime: zero.

**Splitting orders into orders + order_line_items**

> Input: `orders` has a JSON `lines` column with line-item data; we want a relational `order_line_items` table.
>
> Expected plan: expand creates `order_line_items` empty; dual-write makes the application write line items to both the JSON column and the new table; backfill extracts existing JSON into rows; switch-read points line-item reads at the new table; stop-write-old drops the dual write of JSON; contract drops the JSON column. Backfill is the long phase — flag JSON parse errors as the most likely failure mode and plan to skip-and-log unparseable rows for human review.

**Changing a column type from VARCHAR to BIGINT**

> Input: `external_id VARCHAR(50)` on a 50M-row MySQL table; values are all numeric strings; we want `BIGINT`. Zero downtime.
>
> Expected plan: expand adds `external_id_int BIGINT` nullable; dual-write writes the parsed integer alongside the string; backfill parses existing strings in batches; switch-read consumes the integer column; stop-write-old removes the string write (or keeps it for a generated column shim if other systems still need it); contract drops the string column. Watch for non-numeric strings during backfill — quarantine them and surface them as a count for human triage.

## Limitations

- The skill produces a plan, not a runbook executed in a specific tool. The user must adapt the DDL to their migration framework (Alembic, Flyway, dbmate, sqitch, Liquibase, custom scripts).
- It does not benchmark a specific environment. Timings in the output are estimates; the pre-flight rehearsal step (54) is the source of truth.
- Engine-specific edge cases evolve with engine versions. Verify the online-DDL matrix for your exact version.
- Multi-region active-active replication adds constraints the plan does not handle by default; flag and ask.
- Logical replication consumers (Debezium, native logical decoding) may require explicit publication updates; the plan mentions but does not author those changes.
- The skill assumes the change is correct as specified. It does not second-guess whether dropping the column is a good business decision.

## Sources reviewed

Methodology synthesized from patterns observed across the following permissively licensed projects. No prose was lifted from any source.

- https://github.com/xataio/pgroll
- https://github.com/fabianlindfors/reshape
- https://github.com/github/gh-ost
- https://github.com/amacneil/dbmate
- https://github.com/golang-migrate/migrate
- https://github.com/sqitchers/sqitch
- https://github.com/dbt-labs/dbt-core
