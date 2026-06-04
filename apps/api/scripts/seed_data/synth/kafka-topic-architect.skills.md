---
id: skillsgit-curated/kafka-topic-architect
version: 1.0.0
name: Kafka Topic Architect
description: Design a Kafka or Kafka-API topic taxonomy — naming, event vs entity split, partition keys, partition count, retention, compaction, replication factor, and ACL boundaries.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags:
  - niche:kafka-architecture
  - kafka
  - topic-design
  - partitioning
  - compaction
  - retention
  - replication
  - acls
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  tools_optional: [web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - kafka topic design
  - kafka partition key
  - partition count
  - log compaction
  - kafka retention
  - replication factor
  - min in-sync replicas
  - topic naming convention
  - kafka acl
  - kafka multi-tenant
  - kafka event vs entity
  - keyed topic
  - rack awareness
  - tiered storage
example_invocations:
  - "We're standing up Kafka for our orders domain — help us design topics, partition keys, and retention."
  - "Our partitions are unbalanced and one consumer is lagging — review our partition-key strategy."
  - "Design a compacted topic taxonomy for current-state customer data shared across teams."
inputs:
  - name: domain_workload
    type: text
    required: true
    description: Producers, consumers, expected throughput per topic, average and max message size, ordering needs, retention needs, and whether the data represents events or current state.
  - name: cluster_constraints
    type: text
    required: false
    description: Cluster size, broker count, available disk per broker, rack or zone count, whether tiered storage is available, and any organization-wide topic-count limits.
  - name: tenancy_model
    type: text
    required: false
    description: Single team, multi-team in one cluster, multi-tenant SaaS in one cluster, or per-tenant clusters. Includes regulatory isolation constraints.
  - name: existing_topics
    type: text
    required: false
    description: Existing topic names, partition counts, retention settings, and any pain points the team has observed.
  - name: ordering_scope
    type: choice
    required: false
    description: The scope at which message order must be preserved.
    choices: [per-entity, per-tenant, global, none]
outputs:
  - name: topic_taxonomy
    type: markdown
    description: Named topic list with type (event or entity), partition key, partition count, replication factor, retention, cleanup policy, ACL group, and rationale per topic.
  - name: partition_sizing_table
    type: markdown
    description: Per-topic partition-count calculation showing target throughput, consumer parallelism ceiling, and a recommended initial value with a re-evaluation trigger.
  - name: governance_rules
    type: markdown
    description: Naming convention, ACL conventions, retention defaults, and topic-creation policy that the team will apply to future topics.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Kafka Topic Architect

## When to use

Use this skill when a team needs to design or audit Kafka topics and the answer is not obvious. The skill is opinionated about partition keys, partition counts, retention, compaction, replication, and ACL boundaries — the choices that get baked in early and are painful to change later.

It applies to Apache Kafka and to Kafka-API-compatible brokers (e.g. Kafka deployed via Strimzi). The advice is broker-version-aware where it matters (KRaft vs ZooKeeper, tiered storage, exactly-once semantics v2). It does not cover Kafka Streams topology design, which has its own skill, nor consumer-side patterns, which have their own skill.

Common triggers:

- A team is standing up Kafka for a new domain and asks "how many partitions" or "what should we name the topics".
- An existing cluster has unbalanced partitions, one hot consumer, or a topic count climbing into the tens of thousands.
- A team built compacted topics by accident or forgot to set them and now retention is wrong.
- A multi-team cluster has ACLs glued on after the fact and reads cross team boundaries.
- A migration from RabbitMQ or SQS to Kafka needs a taxonomy plan before any code ships.

Do not use this skill for:

- The decision of whether to adopt Kafka at all. Use `eventing-architect` for broker-family selection.
- Designing the Kafka Streams or ksqlDB topology that sits above topics. Use the streams pipeline designer skill.
- Sizing the broker cluster (number of brokers, disk type, network). That is capacity planning and depends on numbers this skill collects but does not produce.

## Inputs

- `domain_workload` (required) — producers and consumers, throughput per topic, message size distribution, ordering scope, retention needs, and whether the data is events (facts) or entities (current state).
- `cluster_constraints` — broker count, disk per broker, rack or zone count, whether tiered storage exists, and any topic-count budget the platform team enforces.
- `tenancy_model` — single team, multi-team shared cluster, multi-tenant SaaS, or per-tenant clusters. Determines ACL boundaries and naming.
- `existing_topics` — current state for audits and migrations. Often the pain points point at the right redesign.
- `ordering_scope` — how strict the ordering requirement is. Per-entity is the common case and partitioning supports it cheaply; global is expensive and usually unnecessary.

## How to apply

The steps produce three deliverables: a topic taxonomy, a partition-sizing table, and a governance ruleset. Work the steps in order; later steps reference choices made earlier.

### 1. Classify each stream as event or entity

1.1. Restate every producer-to-consumer flow in two columns: what changed (event) or what it is now (entity). A stream that says "order placed", "payment captured", or "user signed in" is event-shaped. A stream that says "current user profile", "current price for SKU", or "last known device state" is entity-shaped.

1.2. Event streams map to **standard (delete-by-time) topics**. They retain history for replay over a fixed window. Cleanup policy is `delete`.

1.3. Entity streams map to **compacted topics**. They retain the latest value per key indefinitely (subject to compaction lag). Cleanup policy is `compact`.

1.4. Streams that are both — e.g. audit history of state changes plus current state for new consumers — are usually two topics with different cleanup policies, not one topic with `compact,delete`. Use the dual-cleanup option only when the team has explicit reason and has read the broker compaction semantics.

1.5. Reject the temptation to put events and entities on the same topic. Compaction will erase events you wanted to retain; long retention will bloat entity topics that should converge to a small footprint.

### 2. Name the topics

2.1. Adopt one naming convention and apply it everywhere. The convention has three parts: namespace, domain, kind.

- Namespace: `{environment-or-org}.{domain}` (e.g. `prod.orders`, `prod.payments`). Skip the environment prefix when environments are separate clusters with no shared topic routing.
- Domain: the bounded context owning the topic (`orders`, `billing`, `inventory`).
- Kind suffix: `events` for event streams, `state` for compacted entity streams, `commands` for command streams, `dlq` for dead-letter, `retry` for retry topics.

2.2. Example concrete names: `prod.orders.events`, `prod.users.state`, `prod.notifications.commands`, `prod.orders.events.dlq`.

2.3. Avoid the following in names: implementation details (`kafka_`, `topic_`), version suffixes that hard-code current schema (`_v3`), tenant ids (the broker should isolate tenants, not the name), or human handles (`fred_test_topic`).

2.4. Reserve a system namespace for infrastructure topics: `system.audit.events`, `system.metrics.events`, `system.tracing.events`. Apply strict ACLs and lower retention.

2.5. Forbid topic creation by ad-hoc users in production. All topics ship via a declarative manifest (Strimzi `KafkaTopic` CRD, Terraform Kafka provider, or a homegrown registry).

### 3. Choose the partition key

3.1. The partition key determines per-key ordering and consumer parallelism. **Order is preserved within a single partition only**; messages with the same key always land in the same partition.

3.2. For events: the partition key is the **aggregate id** the event belongs to — `order_id` for order events, `user_id` for user events. This gives per-aggregate ordering, which is what most domain workflows actually need.

3.3. For entities: the partition key is the **entity primary key**. Compaction operates per key per partition, so this is mandatory; null keys on a compacted topic are a configuration bug.

3.4. For commands targeting a worker pool: a null key (or a low-cardinality hashed key) is fine; ordering across commands is usually not required.

3.5. Avoid the following keys: timestamps (everything lands in one partition during a burst), monotonically increasing ids without hashing (skew across partitions over time), tenant id as the only key in a multi-tenant SaaS (one large tenant skews one partition).

3.6. If the natural key has very high cardinality and uneven distribution (e.g. a few huge customers and a long tail), wrap the producer to compute `(key, sub-partition)` and round-robin within the large key while preserving order for small keys. Document the asymmetry; it leaks into consumers that assume strict per-key order.

3.7. Document the partition key on every topic. Consumers will assume the wrong key if you do not write it down.

### 4. Compute the partition count

4.1. The partition count caps consumer parallelism inside one consumer group: at most P consumers can read a topic with P partitions usefully. Choose P with three numbers in mind:

- **Target throughput**, in messages per second and MB per second at peak.
- **Per-partition throughput ceiling**, conservatively 10 MB/s and 1–5k messages/s on a healthy cluster. Plenty of clusters do more; plenty do less.
- **Consumer concurrency**, the maximum number of consumer instances the heaviest consumer group will run.

4.2. Starting formula (sanity check, not gospel):

```
P = max(
  ceil(peak_mb_per_sec / per_partition_mb_ceiling),
  ceil(peak_msg_per_sec / per_partition_msg_ceiling),
  expected_consumer_concurrency,
  3
)
```

A minimum of 3 covers any topic that matters; below that, a single bad partition stalls a meaningful slice of the workload.

4.3. Common partition counts in practice: 3, 6, 12, 24, 48. Multiples of common consumer counts make rebalancing assignments even.

4.4. Re-partitioning is expensive: it breaks per-key ordering across the boundary because the hash output changes. Prefer to over-provision modestly (say 50%) rather than under-provision. Do not over-provision wildly: each partition consumes broker memory, file handles, and replication overhead.

4.5. Document a re-evaluation trigger per topic: "review when sustained throughput exceeds 70% of P × per-partition ceiling for 7 days" or "review when consumer concurrency exceeds P/2".

4.6. Reject the request for "thousands of partitions per topic" unless the cluster is sized for it. Many large clusters cap at low hundreds of partitions per topic and rely on partition-count discipline.

### 5. Choose retention and segment policy

5.1. Retention has two axes: time (`retention.ms`) and size (`retention.bytes`). Either limit triggers deletion. Set both; the size cap protects against accidental volume spikes.

5.2. Default retention guidance by topic kind:

- Event topic, transactional domain: 7–14 days. Enough for replay during incident recovery; not so long it becomes a cold archive.
- Event topic, analytics fan-out: 7 days hot, archive to object storage for longer history. Tiered storage (where available) extends hot retention without a separate pipeline.
- Compacted entity topic: retention is governed by compaction, not time. Set `min.cleanable.dirty.ratio` to 0.5 by default; lower for hot topics needing more aggressive compaction, higher for low-write topics.
- Command topic: short, 1–3 days. Commands not consumed in that window are stale anyway and should land in a DLQ.
- DLQ topic: 30 days or more. The operator needs time to triage.
- Audit topic: per the audit policy. Often 1+ years with tiered storage or archive.

5.3. Segment sizing matters for compaction and deletion. Default `segment.bytes` of 1 GB and `segment.ms` of 7 days are reasonable for medium-throughput topics. For low-throughput topics, lower `segment.ms` so deletion happens on the expected schedule.

5.4. For compacted topics, set `delete.retention.ms` (tombstone retention) to at least the maximum expected consumer downtime. A consumer offline for longer than this can miss deletions and end up with stale state.

5.5. Document retention as a topic property, not a global default. Audit logs and metrics topics should not inherit the same number.

### 6. Choose replication and durability

6.1. Production topics: `replication.factor = 3`. The cluster is sized to handle this; anything less risks data loss on a single broker failure.

6.2. Set `min.insync.replicas = 2` on production topics. This is the durability lever: when fewer than two replicas are in sync, producers with `acks=all` fail rather than risk losing acknowledged writes. Pair with `acks=all` on the producer side.

6.3. Non-production topics may use replication factor 1 to save disk, but they are not durable. Document this so no one mistakes them for safe storage.

6.4. Use **rack awareness** when the cluster spans racks or availability zones. Set `broker.rack` on each broker and let the controller spread replicas across racks. A topic created without rack awareness in a multi-AZ cluster is a latent outage waiting for a zone failure.

6.5. For workloads that must survive a whole region failure, replication factor 3 within a region is not enough. The pattern is asynchronous mirroring to a second region (MirrorMaker 2, or a multi-region cluster on a broker that supports it). State this requirement on each affected topic.

6.6. Do not set `unclean.leader.election.enable = true` to recover availability. The cost is silent data loss; the trade-off is rarely worth it for transactional topics. Document any exception with a named owner.

### 7. Decide compaction details for entity topics

7.1. Set `cleanup.policy = compact` and ensure every record has a non-null key. Compaction collapses to the latest value per key per partition; null keys break this.

7.2. Use **tombstones** to delete a key: produce a record with the key and a null value. Tombstones are retained for `delete.retention.ms`, then compacted away. Consumers that read the topic from start must observe tombstones to converge correctly.

7.3. Compaction has lag. Latest values converge over `log.cleaner.min.compaction.lag.ms`; older duplicates linger. Consumers that read from start should expect to see multiple values per key during the initial pass; do not assume one-record-per-key.

7.4. Avoid producing high-volume "no-op" updates to a compacted topic. Compaction cannot keep up with unbounded write amplification; the topic grows.

7.5. For change-data-capture (CDC) feeds (Debezium-style), use compacted topics keyed on the table primary key. Set a reasonable `delete.retention.ms` so deleted-row tombstones are visible to downstream consumers.

### 8. Plan ACLs and tenancy

8.1. Apply ACLs per **producer-or-consumer group, per topic**. Default-deny: a client without an ACL grant should not be able to read or write any topic.

8.2. Use a naming convention that aligns ACLs with topics. Pattern-based ACLs (`prefix: prod.orders.`) scale better than per-topic grants for a team that owns a whole domain.

8.3. Producer ACLs: `WRITE` and `DESCRIBE` on the topic; `WRITE` and `DESCRIBE` on the transactional id if the producer uses transactions; `IDEMPOTENT_WRITE` on the cluster if idempotence is enabled.

8.4. Consumer ACLs: `READ` and `DESCRIBE` on the topic; `READ` on the consumer group resource. Do not share a consumer group id across teams; each consumer group is a unit of progress and isolation.

8.5. For multi-tenant SaaS in one cluster, isolate by topic prefix per tenant (`prod.tenant-{id}.orders.events`) only when the tenant count is small and stable. For large or growing tenant counts, prefer one topic with `tenant_id` in the payload and rely on consumer-side filtering or per-tenant materialized views.

8.6. Never share producer credentials between teams. A breach or rogue producer can write to topics it should not own and corrupt downstream consumers.

### 9. Decide cluster-level concerns the topic depends on

9.1. **KRaft vs ZooKeeper**: new clusters are KRaft. Older clusters in ZK should plan a migration. Topic design does not change between the two, but operational tools differ.

9.2. **Tiered storage**: if the cluster has tiered storage, the retention math changes. Hot retention drops to days; cold retention extends to months on object storage. Topics with long-tail replay needs benefit most.

9.3. **Quotas**: per-client and per-user produce/consume quotas protect a shared cluster from noisy neighbors. Set defaults; document overrides.

9.4. **Topic creation policy**: enable a server-side `CreateTopicPolicy` (or the operator equivalent) that enforces replication factor 3 and a sane partition count cap. Catch bad topics at create time, not in production.

### 10. Plan the rollout

10.1. For greenfield: ship topics via a declarative manifest reviewed by the platform team. No application code creates topics in production. The manifest includes every property in this design.

10.2. For migration from an existing cluster or broker: dual-write or mirror first, validate consumers on the new topology, then cut producers. Keep the old topics readable until consumers fully migrate.

10.3. For partition-count changes: increasing partitions in place breaks per-key ordering for keys that hash to new partitions. The safe path is to create a new topic with the desired count, mirror, then cut over consumers.

10.4. For schema-only changes that require a new topic (e.g. major version of an event), see `kafka-schema-evolution-architect`.

### 11. Emit the design

11.1. The taxonomy is a table with one row per topic: name, kind (event or entity), partition key, partition count, replication factor, min ISR, retention.ms, retention.bytes, cleanup policy, owning team, ACL group, rationale.

11.2. The partition-sizing table shows the math behind each partition count and a re-evaluation trigger.

11.3. The governance rules document the naming convention, the default retention by kind, the ACL conventions, and the topic-creation policy. This is the artifact future topics get reviewed against.

### Decision rules and heuristics

- **Events and entities are different topics.** Compaction and time retention do different things; do not blend them by accident.
- **Per-key ordering is the practical guarantee.** Global ordering is rarely worth the single-partition bottleneck.
- **Replication factor 3 with min ISR 2 is the production default.** Anything less is non-durable; document and label clearly.
- **Partition counts go up reluctantly and down never.** Over-provision modestly at design time rather than chasing growth later.
- **Names from the business, not the implementation.** Topic names that mention "kafka" or include version suffixes age badly.
- **ACLs default-deny.** A topic without an explicit grant is silently inaccessible, which is the safe failure mode.
- **One topic per kind, not one topic per producer.** A topic shared by producers in the same domain is normal and good.
- **Compacted topics need non-null keys, always.** Null keys silently disable compaction.
- **Tombstones are messages.** Consumers must handle them; they are not silent deletes.
- **Tiered storage is a retention lever, not a partition lever.** It does not let you skip partition-count planning.

### Edge cases

- **Skewed keys.** A handful of large tenants on a tenant-id-keyed topic will hot-partition the cluster. Compute `(tenant_id, sub-key)` and document the per-key-pair ordering guarantee.
- **CDC topics.** They are compacted, keyed on the database primary key, and benefit from `null`-value tombstones for deletes. Producers must handle table schema migrations.
- **Very small topics.** A topic doing 1 message per minute does not need 12 partitions or 3-broker replication if it does not matter. Document the exception or it propagates.
- **Cross-region topics.** Use MirrorMaker 2 or a multi-region capable broker. Topic names should be region-suffix-free; the cluster topology, not the name, encodes location.
- **Topic explosion.** A cluster pushing past 50k partitions starts to suffer in controller failover and replication. Consider partition-count tightening or multi-cluster split before that point.
- **Internal topics from Streams or Connect.** They are automatically created and named (e.g. `myapp-store-changelog`). Treat them as managed by their owning service; do not include them in domain taxonomy reviews.
- **One-off "temporary" topics.** Set a hard expiration date in the manifest and a follow-up to delete. They never get cleaned up otherwise.

## Outputs

- `topic_taxonomy` — A table per topic with name, kind, partition key, partition count, replication factor, min ISR, retention, cleanup policy, owning team, ACL group, rationale.
- `partition_sizing_table` — The math behind partition counts: peak throughput, per-partition ceiling assumed, consumer concurrency expected, chosen partition count, re-evaluation trigger.
- `governance_rules` — Naming convention, default retention by topic kind, ACL conventions, and topic-creation policy.

## Examples

### Worked example

Input excerpt:

> We run Kafka in production for our retail platform. Existing pain: one `orders` topic with 100 partitions, retention 30 days, no compaction, producers writing both order events and current order state into the same topic. Consumers include billing (near-real-time), search (re-indexing), analytics (daily), and a customer-state cache that reads from start whenever it restarts. Throughput peaks at 8k events/sec.

Expected output sketch (taxonomy excerpt):

- `prod.orders.events` — event, key `order_id`, partitions 24, RF 3, min ISR 2, retention 14 days, cleanup `delete`, owner `orders`, ACL group `prod.orders.*`. Replaces the existing topic for event consumption.
- `prod.orders.state` — entity, key `order_id`, partitions 24, RF 3, min ISR 2, cleanup `compact`, `min.cleanable.dirty.ratio` 0.5, owner `orders`, ACL group `prod.orders.*`. New topic for the customer-state cache; backed by an outbox-driven CDC stream.
- `prod.orders.events.dlq` — event, key `order_id`, partitions 6, RF 3, retention 30 days, owner `orders`. Per-consumer DLQs feed from this.

Partition-sizing excerpt for `prod.orders.events`:

```
peak_mb_per_sec   = 8000 events/s × 1.5 KB avg = 12 MB/s
per_partition_mb  = 10 MB/s (conservative)
required_p_thrpt  = ceil(12 / 10) = 2
consumer_concurr  = 8 (largest group: search re-indexing)
chosen_partitions = max(2, 8, 3) = 8 ... rounded to 24 for 3× headroom

re-evaluation trigger: review when sustained throughput exceeds 250 MB/s
  or consumer concurrency exceeds 12
```

Governance rules excerpt:

- Naming: `{env}.{domain}.{kind}` with `kind` in `{events, state, commands, commands.dlq, events.dlq, retry}`.
- All production topics: RF 3, min ISR 2, default retention 14 days for events.
- ACLs: prefix-based per domain (`prod.orders.*` group, `prod.payments.*` group). Per-topic exceptions reviewed quarterly.
- Topic creation: declarative manifest only; the platform CI rejects PRs that violate the policy.

## Limitations

- The skill does not size the broker cluster. It assumes a competent operator and reasonable defaults. Sizing requires hardware, network, and load-test data this skill does not collect.
- It does not pick between Apache Kafka, Strimzi-managed Kafka, or hosted Kafka. It produces a design that runs on any Kafka-API-compatible broker.
- It does not generate broker configuration. It tells the operator what topic properties to set; broker-side defaults are out of scope.
- It assumes producers will respect the ordering and key conventions. Producers that ignore partition keys or write null keys to compacted topics will defeat the design.
- It cannot enforce taxonomy. Without a CreateTopicPolicy or operator review, teams will create topics that violate the design within a quarter.
- For ksqlDB and Kafka Connect internal topics, the skill gives only guidance on owner labels; their internal structure is governed by those tools.

## Sources reviewed

- https://github.com/apache/kafka
- https://github.com/strimzi/strimzi-kafka-operator
- https://github.com/confluentinc/cp-demo
- https://github.com/confluentinc/librdkafka
- https://github.com/debezium/debezium
- https://github.com/provectus/kafka-ui
- https://github.com/twmb/franz-go
