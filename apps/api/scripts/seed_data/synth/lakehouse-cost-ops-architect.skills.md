---
id: skillsgit-curated/lakehouse-cost-ops-architect
version: 1.0.0
name: Lakehouse Cost Ops Architect
description: Engineers cost discipline into a data lakehouse — storage tiering, table layout aligned to query patterns, per-team query cost attribution, hot/warm/cold migration, and lifecycle policies — by translating workload economics into concrete configuration and a measurable cost SLO.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:lakehouse-cost-ops, lakehouse, finops, storage-tiering, lifecycle-policy, query-attribution, cost-allocation, layout-optimization]
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
  - lakehouse cost
  - data finops
  - storage tiering
  - hot warm cold
  - lifecycle policy
  - query cost attribution
  - chargeback data
  - showback
  - parquet compression
  - lakehouse budget
  - s3 cost
  - small file problem
  - cold storage data
  - data egress cost
example_invocations:
  - "Our lakehouse storage bill has doubled in six months. Design the cost-ops plan."
  - "Build the chargeback model for our data platform — query cost per team and storage cost per project."
  - "Pick the tiering policy for our 200 TB lakehouse on S3 with mixed hot, warm, and cold tables."
  - "Our query bill on the lakehouse is unpredictable. Design a cost SLO with guardrails."
  - "Plan the hot-to-cold migration for tables that have not been queried in 90+ days."
inputs:
  - name: storage_inventory
    type: text
    required: true
    description: Total storage size, growth rate, table count, and rough split between hot, warm, cold; current storage tier per table or per prefix; current monthly storage spend.
  - name: query_workload
    type: text
    required: false
    description: Query engines in use, monthly query volume, top consumer teams, total monthly query spend, distribution of query types (interactive, dashboard, ETL).
  - name: table_layout
    type: text
    required: false
    description: Partitioning, sort order, file size distribution, table format (Iceberg, Delta, Hudi, raw parquet), and known layout pain points.
  - name: access_patterns
    type: text
    required: false
    description: Per-table or per-tier access frequency, retention requirements, regulatory holds, and historical query logs if available.
  - name: organizational_model
    type: text
    required: false
    description: Team structure, cost-center mapping, current chargeback or showback maturity, budget approval process, and finance partner expectations.
  - name: cost_targets
    type: text
    required: false
    description: Cost reduction goal, predictability goal, per-team budget envelope, and any executive-level commitments on storage or query spend.
outputs:
  - name: tiering_policy
    type: markdown
    description: Hot/warm/cold tier definitions, the rules for moving tables between tiers, and the lifecycle policies that automate the moves.
  - name: layout_optimization
    type: markdown
    description: Layout fixes that reduce query cost — file size, partition pruning, projection pruning, compression, sort order — prioritized by impact.
  - name: attribution_model
    type: markdown
    description: Per-team and per-query cost attribution scheme, the labels and tags required, and the dashboard or report shape.
  - name: lifecycle_runbook
    type: markdown
    description: Automated lifecycle policies, hot-to-cold migration playbook, retention enforcement, and the cold-table reactivation path.
  - name: cost_slo
    type: markdown
    description: Cost SLO with budgets, alerts, guardrails, anomaly detection, and the response runbook when a budget is breached.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a data lakehouse has crossed the threshold where cost discipline matters and the team needs a coherent plan rather than ad-hoc savings. Typical triggers:

- The storage bill has grown faster than the data, signaling small files, missed compaction, or unmanaged snapshot retention.
- The query bill is unpredictable from month to month and finance needs a forecast or guardrails.
- Different teams use the same lakehouse and there is no chargeback or even showback in place.
- Tables exist that have not been queried in months but still occupy hot storage.
- An executive mandate for a percentage cost reduction needs a plan, not a slogan.
- A new tier of cold storage has become available and the platform team wants to use it where it makes sense.
- A "cost incident" has happened — a runaway job, a misconfigured ingest, or a forgotten backfill — and the team wants prevention, not just remediation.

Do not use this skill for query-level tuning of a single slow job; pair with a Spark or query-engine tuning skill. Do not use it for table-format selection in a greenfield setup; that decision is upstream. Do not use it for warehouse-style platforms where the vendor controls tiering and chargeback is built in.

## How to apply

Work the steps in order. Tiering and layout decisions made in steps 2–4 unlock the attribution model in step 5; without those, attribution surfaces noise rather than signal.

### 1. Build the cost portrait

1. **Total cost decomposition.** Storage cost, query cost, data transfer cost (egress, cross-region), API operation cost (PUT/GET/LIST on object stores), and platform cost (catalog, control plane). The portrait needs all five.
2. **Twelve-month trend per category.** Plot monthly cost in each category. A storage line that bends upward faster than data growth is a small-file or snapshot-retention problem; a query line that spikes during the month is a workload or a runaway-job problem.
3. **Top tables and top teams by spend.** Pareto rule applies — usually 10–20% of tables hold 80% of the bytes; 10–20% of teams cause 80% of the queries.
4. **Top untracked spend.** Snapshot churn, orphan files, intermediate scratch, log volumes, and unused materialized state often hide as "platform" cost and have no owner.
5. **Anchor each cost component with a "is this normal" question.** A $50k/month object-store bill for 100 TB looks expensive; for 10 PB it looks cheap. Without unit cost ratios the plan is blind.

### 2. Define tiers

6. **Hot tier.** Queried daily or more often; latency-sensitive; lives on the fastest object-store class. Compaction frequent; retention generous; snapshot retention longer.
7. **Warm tier.** Queried weekly to monthly; latency-tolerant; lives on infrequent-access object-store classes. Compaction less aggressive; retention narrower.
8. **Cold tier.** Queried rarely; minutes-to-hours reactivation acceptable; lives on archive object-store classes (Glacier-like). Limited reads; restore-fee aware.
9. **Frozen tier (optional).** Legal hold and compliance archive; not queried under normal operation; deep archive class; multi-region copies for resilience.
10. **Each tier has a unit cost, an access SLA, and an SLO.** Tier definitions in a table the platform team and finance both endorse.
11. **Pick the boundary metric per tier.** Days since last query is the most defensible; access count per period works for very high-volume tables; explicit table tag overrides the metric.

### 3. Optimize layout for query cost

12. **Right-size files.** Tens of millions of tiny parquet files is the leading cause of inflated query cost on object stores. Compact to a target size matched to engine and read pattern — typically 128 MB to 1 GB per file.
13. **Partition by predicate columns, not data columns.** Partitions that match dominant query filters reduce bytes scanned dramatically; partitions that match data volume but not query shape inflate metadata for no benefit.
14. **Sort within files.** A sort by a frequently filtered column lets parquet skip row groups via min/max statistics. Sorting halves to quarters the bytes read on many real workloads.
15. **Project at write time.** Columns rarely used belong in separate tables or separate columnar stores; the lakehouse table should not carry rarely-touched 4 KB JSON blobs alongside numeric measures every query reads.
16. **Tune compression per column type.** Stronger compression (zstd at higher levels) is worth the CPU on cold archival data; faster compression (snappy, zstd-low) on hot data prioritizes scan throughput.
17. **Use column statistics.** Modern table formats expose stats per file; verify that the writer produces them. A query that cannot prune misses obvious wins.
18. **Drop unused columns and unused tables.** A schema review every quarter finds columns no one queries and tables no one reads. The cheapest byte is the byte not stored.

### 4. Operate the layout

19. **Schedule periodic compaction by tier.** Hot: daily or hourly. Warm: weekly. Cold: rarely or never (rewriting cold data is expensive and rarely pays back).
20. **Schedule snapshot expiration.** A table that retains every snapshot for a year stores many copies of the same data. Tier-specific retention windows; longer for hot, shorter for warm, minimal for cold.
21. **Schedule orphan-file cleanup.** Failed writes, failed compaction, abandoned snapshots leave bytes nobody references. A safe-lookback orphan sweep recovers them.
22. **Audit lifecycle policy alignment.** The object-store lifecycle policy and the table-format snapshot policy must agree; an object-store rule that deletes files referenced by an Iceberg snapshot is a data-loss bug.
23. **Maintenance compute matters.** Compaction and rewrite jobs themselves cost money; a maintenance schedule that does not pay back in storage and query savings is just cost-shifted.

### 5. Build per-team and per-query attribution

24. **Tag every table with owner and cost-center.** A simple key-value pair on the table metadata or the object-store prefix. The single highest-leverage step.
25. **Tag every query with team, project, and intent.** Engine-specific support varies; at minimum, run queries under per-team service accounts so the engine's audit log attributes correctly.
26. **Compute query cost per run.** Bytes scanned times engine unit price plus any per-query premium. Engines that expose `bytes_scanned` or `data_processed` per query make this trivial; ones that do not require sampling.
27. **Compute storage cost per table.** Bytes per tier times the tier unit price, summed across tiers per table. Lifecycle-managed tables span tiers; the calculation respects current placement.
28. **Allocate platform cost** (catalog, control plane, maintenance jobs) by either a flat per-team share or by share-of-storage. Pick one and document.
29. **Publish a monthly showback report** per team. Storage, query, transfer; trend; top tables; top queries. Showback alone changes behavior even without chargeback.
30. **Graduate to chargeback when finance is ready.** A chargeback model requires accurate metering and a closed-loop with finance; the showback period builds trust and surfaces accounting errors before they hit a P&L.

### 6. Engineer hot-to-cold migration

31. **Detect cold candidates.** Tables with no read traffic in N days (e.g., 90) and no upcoming planned use (per the owner's confirmation) are candidates.
32. **Engage owners before moving.** A direct nudge to the owner — "this table has not been queried in 120 days; OK to tier?" — is faster and cleaner than automated moves that surprise teams.
33. **Move tables atomically.** Write the new files to the colder class, update the table metadata to point at the new location, verify reads, and only then delete the old files. Avoid partial states.
34. **Preserve query access via a thin shim if needed.** Some engines do not transparently read from archive tiers; either restore on demand, route through a tier-aware proxy, or document the latency expectation explicitly.
35. **Track reactivation cost.** Restoring a table from archive is a fixed restore fee plus elevated read cost; build the reactivation cost into the showback report.
36. **Avoid thrash.** A table that flips hot/cold every month either has a wrong tier definition or unpredictable usage; freeze the tier and document.

### 7. Engineer write-side cost

37. **Audit ingest patterns.** Many small files written per minute is a tiny-file generator. Either widen the write batch, add a downstream compaction, or pick a write distribution mode that produces fewer files.
38. **Audit ingest egress.** Cross-region writes carry transfer costs that dwarf storage. Co-locate writers with storage or design explicit replication windows.
39. **Audit duplicate writes.** A pipeline that writes to two prefixes or formats for "compatibility" or "hedging" doubles storage. Confirm both are needed and budget accordingly.
40. **Audit unbatched API operations.** A `PUT` per row is the most expensive thing to do to an object store. Either batch in the writer or interpose a small queue.

### 8. Engineer read-side cost

41. **Cache hot-table scans where possible.** Engine-level result caches, materialized aggregates, and a cache tier in front of object storage all reduce repeated full scans.
42. **Promote pre-aggregates.** Dashboards repeatedly aggregating the same data over the same window benefit from a small pre-aggregate table updated incrementally.
43. **Push filters and projections into the source.** Engine support varies; verify pushdown for the engines you use. Filters that cannot push down become full scans.
44. **Reject misshapen queries at the edge.** A query that reads 10 TB to return three rows because it forgot a partition filter belongs in a dev environment, not in production. A gateway or planner-hook that warns or blocks unpartitioned scans is a strong control.
45. **Provide per-engine governance.** Engines differ in how they expose limits — query timeouts, bytes-scanned caps, concurrency limits. Set them per team and per environment.

### 9. Lifecycle automation

46. **Object-store lifecycle rules.** Automate transitions across object-store storage classes by prefix. Default: standard for hot prefix, infrequent access for warm, archive class for cold, with delete after retention. Document and review per environment.
47. **Catalog-side lifecycle.** Schedules in the orchestrator that run compaction, snapshot expiration, manifest rewrite, and orphan cleanup per tier.
48. **Tag-driven automation.** Tables tagged `tier=cold` or `retention=7y` are picked up by automation without manual prefix moves. Tags are the single source of truth.
49. **Test the lifecycle.** A sandbox with synthetic data exercising every transition before applying to production. Lifecycle bugs are silent until they delete the wrong data.
50. **Document the reactivation path.** A cold table needs a documented procedure for restoring it: who approves, how long it takes, what it costs.

### 10. Build the cost SLO

51. **State the SLO.** Total cost within budget Y% of the time, per category. Anomaly response within Z hours.
52. **Define budgets per team and per environment.** Production, staging, sandbox; absolute budget and soft-cap percentage that triggers an alert.
53. **Define anomaly detection.** A daily-cost dashboard with month-to-date projection. Alert when the projection exceeds the budget by more than a threshold.
54. **Define guardrails.** Bytes-scanned cap per query class, concurrency cap per team, write-rate cap per pipeline, retention cap per tier.
55. **Define the budget-breach runbook.** Who pages on a budget breach, what diagnostics they run (top table delta, top query delta, top team delta), and the emergency lever (a circuit breaker on cost-runaway queries).
56. **Review cadence.** Monthly cost review with finance and platform leadership; quarterly architecture review with team leads.

### 11. Org and process

57. **Designate a cost-ops owner.** A named role on the data platform team responsible for the showback report, the SLO, and the budget-breach runbook.
58. **Embed cost in code review.** A "what does this cost?" question on every pipeline change that touches data volume, partitioning, or retention.
59. **Set expectations with teams.** A monthly office hour where teams can question their bill; transparency over the formula reduces friction.
60. **Track wins.** A simple log of "we changed X, it saved $Y" creates internal proof points and motivates further work.

### 12. Write the cost-ops plan

61. **Tier section.** Definitions, boundaries, automated rules.
62. **Layout section.** Compaction, partitioning, sort, projection, compression.
63. **Attribution section.** Tags, metering, showback report, chargeback graduation.
64. **Lifecycle section.** Object-store rules, catalog jobs, hot-to-cold migration playbook.
65. **SLO section.** Budgets, alerts, guardrails, breach runbook.
66. **Org section.** Owner, cadence, review process, wins log.

## Inputs

- Storage and query cost portrait with twelve-month trend.
- Table inventory with access patterns and current tiering.
- Layout and table-format details.
- Organizational and finance partner expectations.
- Cost targets and predictability needs.

## Outputs

- A tiering policy with rules and automation.
- A layout-optimization plan prioritized by impact.
- An attribution model with showback and chargeback graduation.
- A lifecycle runbook covering automation and reactivation.
- A cost SLO with budgets, alerts, and runbook.

## Examples

### Example 1: storage bill doubled in six months

Input: a 500 TB lakehouse where storage spend went from $40k to $80k per month, while data grew 30%. Iceberg tables on a major object store; team has not run snapshot expiration in six months.

Diagnosis: snapshot retention is the silent culprit; orphan-file cleanup missing; some tables have unbounded incremental files (no compaction). The 30% data growth alone would have cost $52k — the gap is metadata and dead data.

Plan: enable monthly snapshot expiration with 30-day retention on hot tables, 7 days on warm, 7 days plus immediate cleanup on cold. Schedule weekly orphan-file cleanup with 48-hour lookback. Add bin-pack compaction targeting 256 MB. Move tables not queried in 90 days to infrequent-access tier; review with owners. Expected savings: 25–35% within two months.

### Example 2: building chargeback from scratch

Input: a five-team data platform with shared lakehouse; no chargeback today; finance wants to allocate cost in next year's planning.

Plan: month one — tag every table with owner and cost-center; configure per-team service accounts in each query engine; baseline cost per category. Month two — produce a monthly showback report per team; surface storage, query, and transfer. Month three — review report with teams and finance; correct misclassifications. Month four onward — graduate to chargeback once the showback numbers reconcile against the cloud bill. Budget per team set quarterly with finance partnership.

### Example 3: dashboards blowing through query budget

Input: dashboards backed by a query engine over parquet files; query bill spikes mid-month and again at month-end as analysts run heavy reports.

Plan: identify the top-five dashboards by bytes scanned; build incremental pre-aggregates that update hourly; route dashboards to the pre-aggregate tables. Add a bytes-scanned cap per dashboard query class. Move month-end reports to a scheduled batch pipeline that produces a parquet artifact rather than running interactively. Expected effect: query bill flattens 40–50% and becomes predictable.

## Limitations

- Cost-attribution depth depends on engine and table-format support for tagging and metering; some engines lack per-query byte attribution and require sampling.
- Cloud-specific lifecycle rules and storage tier names vary; the skill prescribes the model, not the exact configuration.
- The skill does not architect cost-managed warehouse platforms where pricing is per-credit or per-query and tiering is internal to the vendor.
- Hot-to-cold migration assumes engines can read from the cold tier within an acceptable latency; some archive tiers require explicit restore.
- Per-team chargeback only works when finance, platform, and team leadership accept the metering methodology; the skill describes the path, not the political work.
- Long-term cost prediction depends on usage growth assumptions that the team must own.

## Sources reviewed

- https://github.com/apache/iceberg
- https://github.com/delta-io/delta
- https://github.com/apache/hudi
- https://github.com/apache/parquet-format
- https://github.com/trinodb/trino
- https://github.com/apache/spark
- https://github.com/opencost/opencost
