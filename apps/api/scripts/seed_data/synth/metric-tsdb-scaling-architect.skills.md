---
id: skillsgit-curated/metric-tsdb-scaling-architect
version: 1.0.0
name: Metric TSDB Scaling Architect
description: Scale a metric time-series store beyond a single binary — HA pairs, sharded ingestion, federation, long-term object storage, query federation, and downsampling.
authors:
  - name: Wave-4 Methodology Recovery
    handle: wave4-observability-dashboards
    role: author
category: engineering
tags:
  - niche:observability-dashboards
  - metric-tsdb
  - ha-pairs
  - federation
  - long-term-storage
  - downsampling
  - sharding
  - remote-write
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
    - gpt-4.1
    - gemini-1.5-pro
  min_context_tokens: 32000
  tools_optional:
    - web_search
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - metrics scaling
  - tsdb
  - high availability
  - ha pair
  - federation
  - long term storage
  - remote write
  - downsampling
  - metric retention
  - cardinality
example_invocations:
  - "Our single metric server is at the limit. Design the next architecture stage."
  - "We need two-year retention for compliance. The current setup keeps 15 days."
  - "Three teams want a global view across five regions. Help us federate."
  - "How do we run HA pairs without doubling the write volume to long-term storage?"
inputs:
  - name: current_state
    type: text
    required: true
    description: Current metric system architecture, active series count, ingestion rate, retention, query patterns, and the pain (resource saturation, retention shortfall, outage exposure, query timeouts).
  - name: target_state
    type: text
    required: false
    description: Desired retention, desired query reach (single region, multi-region, multi-cluster), HA goals, and any tenancy requirements.
  - name: constraints
    type: text
    required: false
    description: Object storage available, network egress between regions, ops team size, cost ceiling, and any existing components to preserve.
outputs:
  - name: scaling_design
    type: markdown
    description: A staged architecture — HA pair, sharded ingestion, federation, long-term storage, downsampling, and query federation — with the cardinality and retention budgets that keep it healthy.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release covering the five scaling stages, HA deduplication patterns, sharding by series, downsampling, and query federation patterns.
---

# Metric TSDB Scaling Architect

## When to use

Use this skill when an engineering or platform team has outgrown a single-binary metric store and needs the next architecture stage. Common triggers:

- The single server is saturating on CPU, memory, or disk and the team needs a sharded ingestion path.
- A regulatory or business requirement demands metric retention beyond what local disk holds.
- A platform now spans multiple regions or multiple Kubernetes clusters and the team needs a global query view.
- An on-call rotation has tolerated single-server outages long enough; high availability is now a hard requirement.
- The team is spending too much on retention because of redundant data from HA pairs and needs deduplication at storage time.

Do not use this skill to choose between commercial vendors — the design output is technology-agnostic and helps the team compare vendors. Do not use it to design SLOs or alerts; this skill produces the substrate that an SLO design will rely on.

## How to apply

Five stages, in order. Skip the later stages only when the user explicitly does not need them.

### Stage 1 — Quantify cardinality, ingest, and query load

The most common mistake at this stage is to scale up the wrong dimension. Quantify all three.

| Quantity | Why it matters | Practical limit on a single binary |
| --- | --- | --- |
| Active series (distinct label combinations) | Drives memory and index cost | Low millions; above that you need sharded ingestion or aggressive label hygiene. |
| Samples per second ingested | Drives CPU and write throughput | Order of low hundreds of thousands sustained on a moderately sized server. |
| Distinct sources (scrape targets or remote-write senders) | Drives connection overhead and discovery cost | Thousands per server; above that consider sharding or hierarchical scraping. |
| Concurrent dashboard queries during peak | Drives query CPU and disk read pressure | Tens of concurrent expensive queries; recording rules carry most of the load. |
| Heaviest query bytes scanned per execution | Drives query latency and OOM exposure | Comfortable below a few GB scanned; over that, pre-aggregate. |

Before scaling out, force a cardinality review. Sharding is not a substitute for label hygiene; it preserves bad habits at higher cost. The cardinality rule of thumb:

- **Every label multiplies, every value adds.** A new label with a hundred values can multiply active series by a hundred. Reviewers should reject any new label whose value space they cannot bound.
- **Identifiers do not belong in labels.** Trace IDs, request IDs, user IDs, full URLs, and full SQL statements collapse a metric system. Push those into logs or traces.
- **Recording rules pre-aggregate the dashboards.** Any query that runs more than once a minute should have a recording rule that does the heavy lifting at write time.

### Stage 2 — High-availability pairs at the producer

The first scaling step is rarely about throughput; it is about surviving the loss of one server. Establish HA pairs:

- Run two identical scrape-and-store instances per region or cluster. Both scrape the same targets independently.
- Give both instances the same external label set except for one `replica` label distinguishing them.
- A query layer in front of the pair deduplicates results, preferring whichever replica returned data for a given timestamp first. This is the canonical pattern from the open-source federation projects.
- The pair is for availability, not for capacity. Both instances do the full work; do not assume the pair doubles ingest capacity.

Three operational rules:

- **Treat the pair as one logical instance for change management.** Roll one replica at a time, validate, then roll the other. Never push both at once.
- **Do not write both replicas independently to long-term storage.** Pick one replica as the "primary writer" or, better, deduplicate at the upload step. Writing both doubles storage cost and complicates downstream queries.
- **Probe both replicas independently from outside the cluster.** A pair where both replicas have been silently broken for a week is worse than no pair.

### Stage 3 — Sharded ingestion when the single pair is full

When a pair saturates, shard. Two sharding axes are common; pick deliberately.

**Sharding by source** (each scrape target assigned to exactly one shard):

- Easy to reason about; the shard for a target is deterministic.
- A target that grows organically can drift its shard out of balance; periodic rebalancing required.
- Per-source sharding is the right default for pull-based scraping.

**Sharding by series hash** (push-based with the receiver hashing each series):

- Hot series can land on a single shard; rebalancing requires reshuffling.
- Best for remote-write topologies where producers cannot easily be partitioned.
- Replication across shards (each series written to N shards) is required for availability.

In either case:

- **Shards must be addressable by the query layer**, which fans out and merges. The query layer is not optional; without it, users cannot run global queries.
- **Shard count is not a number to optimise around; it is a number to plan headroom into.** Start at a count that supports two to three times current load and grow by doubling. Frequent reshards are expensive.
- **Tenant routing happens at ingestion**, before sharding. Same-tenant series should land in the same shard pool so per-tenant quotas can be enforced cheanly.

### Stage 4 — Long-term storage in object storage

Local disk is the wrong substrate for retention beyond about 15 to 30 days. Move long-term storage to an object store with the following pattern:

- The ingesting instance flushes blocks (immutable time-bounded chunks of compressed data) to an object bucket at a regular cadence — typically every two hours.
- A storage-gateway component is responsible for reading those blocks back when a query needs historical data. Recent data (the last two hours) is served from the ingestor's memory and local disk.
- A compactor process periodically merges small blocks into larger ones, deduplicates overlapping blocks from HA pairs (this is where the duplicate write is reclaimed at storage cost), and applies downsampling.

Downsampling is the lever that makes multi-year retention affordable:

| Resolution | Typical retention | Use cases |
| --- | --- | --- |
| Native (15s or 30s samples) | 15 to 30 days | Recent incident review, fine-grained dashboards, alert rule evaluation. |
| 5-minute aggregates | 1 to 6 months | Quarterly capacity planning, recent SLO history, postmortems older than the native window. |
| 1-hour aggregates | 1 to 7 years | Compliance retention, year-over-year trends, long-horizon capacity planning. |

Two principles:

- **Downsampling is a one-way operation.** Once the 15-second data is dropped you cannot recover it. Be deliberate about the native-resolution window and align it with the longest practical incident-review interval.
- **Downsampled data is for queries it is suitable for.** A burn-rate alert needs native resolution; a "show me 2024 quarter-over-quarter" panel does not. The query layer should route to the appropriate resolution automatically and refuse to compute a burn rate against hour aggregates.

### Stage 5 — Federation and global query view

When the platform spans regions, clusters, or business units, decide where queries land. Three patterns:

**Hierarchical federation:**

- Per-region instances scrape their region. A "top-level" instance pulls a curated subset (usually pre-aggregated recording rules) from each region.
- The top-level answers global queries; regional instances answer region-local queries.
- Cheap to operate; the cost is that the top-level sees only what was pre-aggregated, so ad-hoc cross-region queries are limited.

**Global query layer over remote shards:**

- A query proxy receives a query, fans out to every regional instance and to long-term storage, merges results, deduplicates HA replicas.
- Powerful; users see one logical store. The cost is that bad queries fan out everywhere and amplify their impact.
- Per-tenant query quotas measured in fan-out bytes and concurrency are mandatory.

**Remote-write to a central store:**

- Regional ingest pushes to a central store via a remote-write protocol. Queries run only against the central store.
- Simplifies the query story at the cost of network egress and central capacity.
- Best for multi-cluster environments inside one region; cross-region remote-write has egress costs and latency implications that need to be measured before commitment.

Choose based on the user's actual query patterns:

- If global queries are rare and per-region queries dominate, hierarchical federation with a small top-level is the right answer.
- If global queries are common and the platform team can run the necessary query proxy and quota system, use a global query layer.
- If a single central store is sized for the load and egress cost is acceptable, use remote-write to centralise.

### Stage 5b — Remote-write topology details

If the chosen pattern uses remote-write between tiers, the details matter more than they appear to.

- **Backpressure must propagate without collapsing the producer.** A remote-write sender that blocks writes to its in-memory TSDB has lost the entire point of buffering; the producer should fail-open with a metric named after the lost samples, never block its own scrape loop.
- **Replication factor at the receiver must match the durability promise.** A receiver writing each sample to one replica before acknowledging is durable up to one replica failure; a receiver acknowledging on quorum across three replicas is durable up to one failure with the additional cost of three-times write fan-out. Pick deliberately.
- **The wire format is a contract.** Major-version changes in the remote-write protocol are not transparent; both sides must be upgraded in lockstep. The receiver should accept both the current and the previous major version during transitions.
- **Per-tenant authentication and tenant labelling at the receiver.** A producer's claim of tenant identity is verified at the receiver against an authentication token, not trusted on the wire.
- **Egress cost.** Cross-region remote-write is a network bill; measure it before commitment and consider per-region pre-aggregation to reduce the volume that crosses regions.

### Stage 6 — Tenancy and quotas

Whatever the topology, multi-tenant deployments need quotas. Define them at three points:

- **Ingest quota per tenant** in active series and samples per second. Enforced at the receiver. Crossing it triggers a soft alert and then a hard rejection with a clear named error.
- **Query quota per tenant** in concurrent queries, total bytes scanned per minute, and total fan-out targets per query. Enforced at the query layer. Crossing it fails the query with a quota error visible to the tenant.
- **Storage quota per tenant** for object-storage usage and for blocks per day. Enforced at the compactor.

Two rules:

- **Quotas are not punishment; they are protection.** Communicate the quota to the tenant, expose usage on a dashboard, and warn before the cap rather than after.
- **Tenants do not see other tenants' data, ever.** Cross-tenant access is reserved for a small platform-team role and is audit-logged. Tenancy is a security boundary, not just an accounting one.

### Stage 7 — Cardinality governance, not just cardinality limits

A hard limit on series per tenant is necessary but not sufficient. Add governance.

- **Cardinality budget per tenant** is the headline number, but **cardinality budget per metric name** is the lever that catches misuse before it grows. A new metric whose label combinatorics could exceed thousands of series gets reviewed before it ships.
- **A bad-label dashboard** ranks labels across all metrics by their distinct-value counts and by their week-over-week growth. The top entries are reviewed weekly by the platform team and the relevant tenant.
- **A series-cliff alert** fires when a tenant's active-series count grows faster than a defined rate. Most cardinality incidents are not a steady creep; they are a deploy that introduced a high-cardinality label and trigger within minutes.
- **Recording rules are produced and owned by the platform team for cross-service queries.** Tenants who write their own recording rules are reviewed for cost; a recording rule that runs every fifteen seconds across a million series is more expensive than a thousand dashboards.
- **Drop relabelling is a routine tool, not an emergency one.** When a tenant emits a label that breaks cardinality, the platform applies an ingestion-time drop rule with the tenant's agreement and the tenant fixes the source on a documented timeline. The drop rule and the timeline are tracked in the same change-management system as other platform changes.

### Stage 8 — Disaster recovery for the metric store

Designs that pass functional review fail when the dependent infrastructure breaks. Plan for these explicitly.

- **Object storage outage.** Recent data is still in the ingestor's local store; the query layer must serve native-resolution recent queries even when historical reads fail. Long-horizon queries return a partial-result indicator. Recovery is automatic once storage returns; the compactor catches up.
- **Single shard loss.** With HA pairs, the surviving replica serves until the lost replica is rebuilt. Rebuild reads from object storage; the rebuild process is a documented and rehearsed procedure, not improvised.
- **Region loss.** Multi-region designs continue serving from surviving regions. Cross-region queries return partial results clearly labelled. The lost region's recent data may be unrecoverable depending on whether remote-write was in use; the team has an explicit decision on what is acceptable.
- **Corrupt block in long-term storage.** The compactor detects via checksum on read, quarantines the block, and surfaces a metric. Queries against the affected time range return a partial-result indicator. Recovery is a tracked operations task, not a per-incident scramble.
- **Wholesale data deletion event.** A wrongful delete by an operator or by automation is irreversible if not detected. The object store should have object-versioning or a separate immutable backup with a documented restore procedure. Practice it.

## Inputs

- **Required:** current architecture, active series count, ingest rate, retention, query patterns, and the immediate pain point that motivated this design.
- **Recommended:** target retention, target query reach, HA goals, tenant count, and any regulatory obligations.
- **Optional:** existing object storage substrate, network topology between regions, ops team capacity.

## Outputs

A markdown design with these sections, in order:

1. **Cardinality and load assessment** — current numbers, identified violations of label hygiene, recommendations for recording rules before any scaling.
2. **HA pair design** — replica labelling, deduplication strategy, change-management rules.
3. **Sharding plan** — if needed, the sharding axis, shard count, growth plan, query-layer fan-out.
4. **Long-term storage** — block flush cadence, object-storage layout, compactor responsibilities, downsampling table.
5. **Federation topology** — chosen pattern with reasoning and per-tenant quotas.
6. **Tenancy model** — ingest, query, and storage quotas with enforcement points.
7. **Migration plan** — staged sequence to move from current state to target without metric loss.

## Examples

### Example 1 — Single binary outgrown, no retention need yet

User says: *"We are at 8 million active series on one server, hitting OOM during query peaks. No multi-region need yet but we expect to add a second region next year."*

Recommended response shape:

- Cardinality review first. The team is likely 30% bloat from labels with unbounded value spaces; identify and remove or migrate.
- HA pair to remove the single-point-of-failure exposure.
- Sharded ingestion by source after the cardinality work cuts series; aim for 3 shards with headroom for 2 more.
- Long-term storage to object storage at 2-hour block cadence; 30 days native, 6 months 5-minute downsample.
- Defer federation; document the option and plan the proxy when the second region lands.
- Quotas modest at launch; revisit after 30 days of production data.

### Example 2 — Multi-region, two-year compliance retention required

User says: *"We have five regions, three Kubernetes clusters each. Compliance now requires two years of metric retention. We have a central object store available."*

Recommended response shape:

- Per-region HA pairs scraping their region.
- Hierarchical federation: per-region instances pre-aggregate recording rules at 1-minute resolution for the curated set of cross-region metrics; top-level pulls those.
- Long-term storage: per-region writes to per-region object-storage prefixes inside a central bucket. Compactor deduplicates HA replicas at upload.
- Downsampling: 30 days native, 12 months 5-minute, 2 years 1-hour.
- Global query layer for ad-hoc cross-region investigation, with quotas published per team.
- Migration: regions adopt the new pattern one at a time; the last region completes the global query layer enablement.

### Example 3 — Spending too much because both HA replicas write to object storage

User says: *"Our long-term storage bill doubled when we added HA. Each replica writes the same blocks. Can we deduplicate?"*

Recommended response shape:

- Two acceptable patterns. The first is a primary-writer designation: one replica is "the writer" for object storage and the other does not upload. Failure of the writer causes a brief gap until promotion; for most teams this is acceptable.
- The second is parallel writes from both replicas with a compactor that deduplicates overlapping blocks. This is more robust but requires a compactor capable of cross-replica dedup.
- The compactor-side approach pays the storage cost briefly before dedup; size accordingly. The metric to watch is the lag between upload and dedup; if it exceeds a small fraction of a day, raise the compactor's resource budget.
- A bad option to refuse: skipping HA entirely to save the cost. The point of HA is uptime; trading uptime for storage cost is rarely the right call.

### Example 4 — Cardinality cliff after a deploy

User says: *"Yesterday a deploy added a `request_id` label by accident. Our active-series count is now ten times higher and queries are timing out."*

Recommended response shape:

- Apply an immediate ingestion-time drop rule for the `request_id` label on the affected metrics. The deploy team has 48 hours to roll back the source change.
- Investigate the alerting: the series-cliff alert in stage 7 should have fired within minutes. If it did not, calibrate the threshold downward.
- Once the source is fixed, retire the drop rule. Keep the postmortem visible to other teams; the same mistake recurs in different shapes.
- Add the `request_id` pattern to the platform's prohibited-labels list with documented reasoning so the next reviewer rejects it without debate.

## Common review findings

1. **A single binary at the cardinality limit with unbounded labels.** Fix labels before sharding; sharding masks the problem at higher cost.
2. **No HA pair on a critical metric path.** A single-server outage is the leading cause of metric blindness during incidents.
3. **Both HA replicas writing to long-term storage with no dedup.** Doubles storage cost silently. Add dedup or primary-writer designation.
4. **No long-term storage at all and the team is buying ever-larger disks.** Migrate to object storage; the disk-scaling curve is steeper than the dev-time cost.
5. **Native-resolution retention beyond 30 days.** Native resolution is rarely needed past two or three weeks. Downsample and recover budget.
6. **Federation top-level pulling raw series across regions.** Egress bill ballooning. Use recording rules to pre-aggregate at the source region.
7. **No per-tenant query quota.** A misbehaving dashboard takes the platform down. Add quotas.
8. **Cardinality budget per metric not enforced.** A bad metric ships and the cliff alert is the first the team hears. Move enforcement to review time.
9. **Compactor failures unseen.** A silently failing compactor causes block bloat and slow queries weeks later. Alert on compactor health, not just on the query plane.

## Limitations

- **Not a vendor selection guide.** Multiple open and commercial implementations satisfy each stage; the skill produces an architecture and helps comparison.
- **Not for high-cardinality observability beyond metrics.** Wide events, traces, and arbitrary attributes belong in different stores; do not stretch a metric TSDB to hold them.
- **Not for capacity-cost modelling.** The skill identifies the architecture and where costs scale; producing a dollar-accurate forecast requires the team's pricing and the workload's measured profile.
- **Sharding numbers are starting points.** Real shard sizing depends on the chosen implementation and on storage media; expect to revisit after the first month.
- **Federation latency is sensitive to network topology.** A global query layer that crosses oceans will be slower than one inside a single region; benchmark before commitment.
- **HA pair semantics differ by implementation.** The replica-label convention is widely adopted but the dedup rules vary; verify the chosen implementation's behaviour under partial outage before relying on it.
- **Long-term retention compliance is not addressed.** WORM (write-once, read-many) and legal-hold semantics are implementation-specific; pair with a compliance review for regulated data.

## Glossary used in this skill

- **Active series.** Distinct combinations of metric name and label values producing samples within a recent window. The dominant memory cost on most metric stores.
- **Sample.** A single timestamped value for a series. Ingest is measured in samples per second.
- **HA pair.** Two instances scraping the same targets independently for availability; deduplicated at query.
- **Shard.** A partition of the ingestion or storage workload. Sharding axes include by source and by series hash.
- **Block.** A time-bounded, immutable chunk of compressed series data flushed to long-term storage.
- **Compactor.** A process that merges blocks, deduplicates HA replicas, and applies downsampling.
- **Federation.** A pattern in which one instance pulls a subset of data from another for a higher-level view.
- **Remote-write.** A push-based ingestion protocol that lets a producer send samples to a different store.
- **Downsampling.** Aggregating samples to a coarser resolution to reduce storage for long retention.
- **Tenant.** A logical isolation boundary at ingest, query, and storage.

## Handoff to neighbouring designs

A metric TSDB at scale is one part of an observability practice. Coordinate explicitly.

- **To SLO and alerting design.** Recording rules that power SLO burn-rate alerts are platform-owned, but their definitions originate in the SLO design. Confirm rule ownership at the platform-SLO boundary so a tightening of an SLO does not silently fail because nobody updated the rule.
- **To dashboarding.** Dashboard panel queries should prefer recording rules over raw expressions. The platform team publishes the recommended recording-rule set; dashboard owners pull from it.
- **To logging and tracing.** The label vocabulary (`service`, `environment`, `region`, `tenant`, `service.tier`) is shared across pipelines. Inconsistency across pipelines breaks correlation; publish and enforce once.
- **To capacity owners.** The growth curves in stage 1 should feed the capacity planning conversation. Surprise growth in active series is a leading indicator of a service that has shipped a high-cardinality label and not yet noticed.
- **To finance.** Object-storage costs, downsampling savings, and HA-replica deduplication are line items in the platform's cost model. A cost owner who can read the same dashboards the platform team reads will make better budget decisions than one who cannot.

## Capacity headroom planning — a worked example

A team has measured the following and asks where to grow.

- 5 million active series, growing 8% per month.
- Ingestion peaks at 180,000 samples per second; steady state at 90,000.
- 30 days retention on local NVMe, no long-term storage.
- Two regions, one server each. Cross-region queries do not exist today.
- Memory: 96 GB per server; running at 72 GB steady state, 84 GB peak.

The skill's recommended planning order:

1. **Cardinality review first.** Even at 8% monthly growth the team has six months before memory becomes critical, but a label hygiene exercise often cuts active series by 20-30%, buying additional months of headroom at minimal cost. Do this before any capital spend.
2. **HA pair as the next step.** The risk of an unattended single-server outage exceeds the cost of doubling the local fleet. Implement this within the current quarter, before any other change, because every other improvement depends on a working HA pair.
3. **Long-term storage migration.** The 30-day retention on local NVMe is expensive per GB; migrating older data to object storage and adding a downsampling tier reduces total cost while extending retention to a year. This is a one-quarter project.
4. **Sharded ingestion deferred.** At current and projected growth, a single HA pair handles the load until at least the end of next year. Defer until cardinality review and long-term storage are complete; revisit when active series cross a documented threshold or when ingestion peak crosses 75% of a single server's sustainable rate.
5. **Federation deferred.** Cross-region queries do not exist today and the team has not articulated a need. Build the recording-rule infrastructure now to make federation cheap when it lands, but do not stand up the global query layer prematurely.

The output of the planning exercise is a four-quarter roadmap, each quarter's project sized against the team's actual capacity, with named triggers that escalate later phases earlier if the workload grows faster than projected.

## Sources reviewed

- Horizontally scalable, multi-tenant long-term metric store (AGPL-3): https://github.com/grafana/mimir
- Long-term storage and global query layer for a pull-based metric system (Apache-2.0): https://github.com/thanos-io/thanos
- Horizontally scalable multi-tenant metric backend (Apache-2.0): https://github.com/cortexproject/cortex
- High-cardinality, high-compression time-series store with cluster and single-node modes (Apache-2.0): https://github.com/VictoriaMetrics/VictoriaMetrics
- Pull-based metric collection and rule evaluation system, with remote-write protocol (Apache-2.0): https://github.com/prometheus/prometheus
- Industry SRE workbook on practical operation of monitoring systems (CC-BY): https://sre.google/workbook/
