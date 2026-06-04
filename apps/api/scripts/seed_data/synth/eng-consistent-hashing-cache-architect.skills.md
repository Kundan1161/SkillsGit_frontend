---
id: skillsgit-curated/consistent-hashing-cache-architect
version: 1.0.0
name: Consistent Hashing Cache Architect
description: Design a sharded cache or key-value store layer with consistent hashing, replication, hot-key mitigation, and replacement-friendly topology that survives node churn.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags:
  - niche:distributed-systems
  - consistent-hashing
  - sharded-cache
  - hot-keys
  - replication
  - rendezvous-hashing
  - bounded-loads
  - cache-design
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  tools_optional: [web_search]
  min_context_tokens: 24000
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - consistent hashing
  - shard a cache
  - cache topology
  - hot key mitigation
  - rendezvous hashing
  - bounded loads
  - cache rebalancing
  - sharded key-value store
  - cache stampede
  - cache replication
  - hash ring
  - virtual nodes
  - jump hash
  - shard map design
example_invocations:
  - "Design a sharded Redis layer for 200 GB of cache with hot-key protection."
  - "Help us plan rebalancing when we double the cache cluster from 8 to 16 nodes."
  - "We have one cache key that takes 60% of traffic — how do we keep that from killing one node?"
inputs:
  - name: workload
    type: text
    required: true
    description: Cache or store workload — total dataset size, read and write rate, item size distribution, expected hot-key concentration, durability needs.
  - name: failure_tolerance
    type: text
    required: false
    description: What is acceptable on a node loss — small fraction of cold misses, momentary unavailability of a shard, or strict no-loss requirement.
  - name: scaling_horizon
    type: text
    required: false
    description: How the cluster is expected to grow or shrink — never, twice a year, daily autoscaling, planned spike events.
  - name: existing_stack
    type: text
    required: false
    description: Existing cache or store technology, language ecosystem, available client libraries, and operational maturity with stateful services.
  - name: consistency_needs
    type: choice
    required: false
    description: Required consistency of the cache or store layer.
    choices: [cache-best-effort, cache-with-coherence, kv-eventual, kv-strong-per-key, kv-strong-cross-key]
outputs:
  - name: shard_design
    type: markdown
    description: Design document covering shard count, hashing scheme, replica policy, hot-key strategy, rebalancing plan, and failure handling.
  - name: capacity_table
    type: markdown
    description: Per-shard capacity assumptions, headroom factors, and the conditions that trigger horizontal growth.
  - name: ops_runbook_seed
    type: markdown
    description: Seeded runbook entries for the most common cache operations — adding a node, replacing a node, draining a node, handling a hot key.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Consistent Hashing Cache Architect

## When to use

Use this skill when a team is designing or fixing a sharded cache or key-value store that must distribute keys across nodes without restarting the world every time a node is added or replaced. The output is a topology design, a hot-key mitigation plan, and an operations seed for the most common reshape events.

The skill applies to cache layers (Redis, Memcached, in-memory caches inside a service) and small key-value stores. It does not design full distributed databases; those have stronger consistency requirements and their own placement schemes.

Common triggers:

- A cache cluster is being introduced and the team is about to write a naive modulo-N sharder that breaks on resize.
- A node loss in the existing cluster caused 100% miss for 1/N of keys and an origin-database stampede.
- A single hot key concentrates traffic on one node, leaving the rest idle.
- The cluster needs to grow from 8 to 16 nodes and the team is afraid of the rebalancing impact.
- A small KV store needs to span more than one node and the team is reaching for a managed product without understanding the trade-offs.

Do not use this skill for:

- Full distributed databases with multi-key transactions; those need a different design vocabulary.
- Single-node caches; sharding is unnecessary.
- Strongly consistent stores with global ordering; you want a consensus protocol, not a hash ring.

## Inputs

- `workload` (required) — Dataset size, RPS by read and write, item size distribution, hot-key shape (how skewed), and whether the data is regenerable or durable.
- `failure_tolerance` — Drives replica count and the choice between hashing schemes that minimize key movement and schemes that maximize balance.
- `scaling_horizon` — Drives whether to bias toward minimal-movement schemes (good for frequent autoscaling) or maximal-balance schemes (good for fixed cluster sizes).
- `existing_stack` — Affects which client library and broker the design will recommend; matching the team's operational base is usually right.
- `consistency_needs` — Cache-best-effort tolerates loss; kv-strong-per-key requires careful replica policy.

## How to apply

The output is a design document built section by section.

### 1. Frame the workload

1.1. Translate the workload into a few headline numbers: total dataset size, target hit rate, sustained read RPS, peak read RPS, write RPS, average and max item size, hot-key skew estimate.

1.2. State what is regenerable. If a cache miss can refill from a primary store, the design tolerates more movement and more partial-loss. If the store is the source of truth, replicas and durability matter more.

1.3. Identify the **fanout pattern**: how the cache is read. Per-request single key, per-request mget, per-request scan, background prefetch. Mget patterns benefit from grouping related keys to the same shard; single-key patterns do not.

### 2. Pick a hashing scheme

2.1. Reject **modulo-N hashing**. It moves nearly every key on resize. Useful only for fixed-size clusters that never grow, shrink, or replace nodes — almost never in practice.

2.2. The candidates that survive:

- **Ring-based consistent hashing with virtual nodes**: each physical node is placed at many positions on a hash ring; keys land at the next clockwise node. Adding a node moves only the keys whose ring segments are reassigned. Good default for most caches.
- **Rendezvous (HRW) hashing**: each key picks the node with the highest hash(node, key) value. No ring; very low movement on node changes; slightly higher per-lookup cost.
- **Jump consistent hash**: a stateless function that maps a key plus a bucket count to a bucket. Excellent when the bucket count grows monotonically and shrinking is rare; awkward when arbitrary nodes leave.
- **Maglev hashing**: lookup tables built from per-node permutations. Used in load balancers; can apply to caches when client computation budget is tight.
- **Consistent hashing with bounded loads**: ring-based consistent hashing with a load cap per node. Keys that would land on an overloaded node spill to the next. Reduces skew without destroying locality.

2.3. Default recommendation: ring-based consistent hashing with virtual nodes plus a bounded-load cap. Switch to rendezvous when client computation is cheap and per-key lookups need to skip ring construction. Switch to jump when the cluster only grows.

2.4. Pick **virtual node count** per physical node: 100–200 is a usable starting range. More virtual nodes give smoother distribution at higher ring memory cost; fewer cause noticeable hot spots.

2.5. Pick the **bounded-loads multiplier**: a node may carry at most `c × (total_keys / num_nodes)` keys, where c is typically 1.25–1.5. Below 1.25 the spills cascade; above 1.5 the bound is too loose to help.

### 3. Decide the shard count and node sizing

3.1. Shard count is the number of physical placement units. It is not the same as the node count. Designs that allow shards to migrate between nodes independently of the hash scheme are easier to operate.

3.2. Pick the **shard count to be larger than the foreseeable node count**: a common choice is a power of two between 64 and 4096. Many shards on few nodes lets the cluster grow without re-hashing — shards move, hashing does not.

3.3. Per-node sizing: pick a target memory and CPU per node based on the workload. Cache nodes are typically RAM-bound. Reserve at least 30% headroom for tail load and rebalance overhead.

3.4. Avoid extreme node sizes. Very large nodes amplify the blast radius of one node loss; very small nodes inflate operational overhead.

### 4. Plan replication

4.1. For pure cache (regenerable, miss-tolerant): replication is optional. A node loss causes a refill burst; that may be acceptable if the origin can handle it. Add replication when the origin is fragile or the cache holds expensive-to-compute values.

4.2. For KV stores: replicate every shard. Common factor is N=3 with a quorum read or a read-replica fanout. Replication factor 2 is acceptable for tolerant workloads; 1 is dangerous.

4.3. **Placement** of replicas matters: never place all replicas of a shard on the same failure domain (rack, availability zone). Make the hashing scheme aware of failure domains, or maintain a placement map outside the hash function.

4.4. **Write fanout** policy: synchronous to all replicas (strong consistency, higher write latency) vs primary plus async fanout (weaker consistency, lower latency). For caches, async fanout is usually fine and may even be omitted in favor of write-through to the origin.

4.5. **Read policy**: primary-only (clearer reasoning), any-replica (better read throughput), or quorum (consistent reads at higher latency). Caches usually use any-replica with stale-while-revalidate semantics.

### 5. Mitigate hot keys

5.1. A hot key is a key whose RPS dwarfs the average. Hot keys are the most common cause of single-node overload in otherwise well-balanced rings.

5.2. Mitigation strategies, from cheapest to heaviest:

- **Client-side micro-cache** for known-hot keys (a few seconds to a few minutes TTL in the calling process). Eliminates most traffic without changing the cluster.
- **Bounded-loads spill** (built into the hashing scheme) — the hot key's neighbor takes the spill load.
- **Replication of the hot key only**: maintain N copies of identified hot keys on different nodes, with client-side random replica selection.
- **Per-key sharding** of compound keys: split a single hot key into many sub-keys (e.g. by a random suffix on writes, sum on reads) when the value is aggregatable.
- **Hot-key promotion**: move identified hot keys to a separate small high-throughput tier (in-memory closer to callers) and keep the rest in the main cluster.

5.3. Detect hot keys with **per-key sampling**: each node samples request counts per key over short windows and reports tops. A centralized aggregator builds a hot-key list. Avoid full per-key counters; they are expensive.

5.4. Plan **eviction interaction with hot keys**: an LRU cache may evict an item right when it heats up. Use LFU or W-TinyLFU policies for caches with skewed access patterns; pure LRU is the wrong default at high skew.

### 6. Plan rebalancing

6.1. Adding a node moves a fraction of keys. Compute the expected fraction: for ring-based with V virtual nodes per physical node and current N nodes, the new node takes roughly 1/(N+1) of the keys.

6.2. Move keys **gracefully**: not in a single burst. Stream them with a throttle that respects origin capacity. Use the rebalance window to refill the moving keys' values on the new node, not on the origin.

6.3. **Hand-off protocol**: while a key is being moved, reads should land on either the old or the new owner without violating the consistency target. Common pattern: the client checks the new owner first, then falls back to the old owner during the transition window. Mark the transition complete only after a verification scan.

6.4. **Cold-cache risk after add**: a new node starts empty. Eager warming is sometimes possible (replicate from a neighbor), but for caches a slow ramp is usually acceptable. Schedule node additions for off-peak windows when feasible.

6.5. **Removing a node** is the dangerous case: that node's keys move at once. For planned removal, drain the node — proactively move keys to their new owners over hours before the actual removal. For unplanned removal, the bounded-loads spill or the replica set absorbs the loss.

6.6. **Failure-domain reshuffles**: if the cluster spans availability zones, a zone outage moves many keys at once. Pre-compute the failover topology and verify the bounded-loads cap holds across the failover.

### 7. Plan the failure response

7.1. **Single-node failure**:

- Cache: bounded-loads cap absorbs spill; alert on origin load; rely on miss-storm prevention (request coalescing) at the cache client.
- KV store: replicas serve reads; writes route to the new primary; alert on under-replication.

7.2. **Multi-node correlated failure** (rack or zone):

- Capacity must survive a zone loss. Plan headroom such that the remaining nodes can carry the load. Hot-key replicas should span zones.

7.3. **Stuck nodes**: a node up but slow (full memory, GC pauses, network buffer overflow) is worse than a dead node. Use latency-based circuit breaking at the client; route around slow nodes until they recover.

7.4. **Origin protection**: a cache failure can crush the database. Use request coalescing at the cache client so concurrent misses for the same key result in one origin call. Combine with a small jittered TTL extension on near-expiry to prevent thundering herd at expiration.

### 8. Plan client libraries and observability

8.1. The hashing scheme lives in the client, the server, or both. Default: client-side hashing for simplicity (no extra hop), but ship the hashing logic as a versioned library so all callers agree.

8.2. **Topology distribution**: clients need to know the current node list. Sources: gossip from the cluster, a small coordination service, or a config push. Test topology updates by injecting node-add and node-remove events in staging.

8.3. **Per-node and per-key metrics**: requests per second, hit rate, p99 latency, memory used, evictions, top-N keys by traffic. Hot-key detection rides on these.

8.4. **Cluster-wide metrics**: ring imbalance (max load / mean load), rebalance progress, replica lag if applicable.

8.5. **Tracing**: include the chosen shard in every trace span so single-shard incidents are obvious in dashboards.

### 9. Plan the rollout

9.1. For a greenfield cache, deploy with the smallest reasonable cluster (3 or 4 nodes) and verify the hashing under failure injection before scaling.

9.2. For migration from a modulo-N cache:

- Stand up the new cluster alongside.
- Dual-write from clients for a window; read from the new cluster with fallback to the old on miss.
- Cut over reads when hit rate on the new cluster matches the old.
- Retire the old cluster after the dual-write window ends.

9.3. For scheme changes within the same cluster (e.g. switching from ring to rendezvous):

- Run both schemes in parallel in the client for a window; verify they produce the same shard for the same key against a baseline mapping.
- Switch when the schemes agree.

### 10. Emit the design

10.1. Lead with a one-paragraph summary: shard count, hashing scheme, replica factor, hot-key strategy, expected blast radius on single-node loss.

10.2. Include the capacity table: shard count, nodes per shard, memory per node, RPS per node, headroom factor, growth trigger.

10.3. Include the failure-mode table: failure scenario, automatic response, alert, runbook reference.

10.4. Include the hot-key playbook: how a hot key is detected, how it is mitigated, who owns the response.

10.5. Provide the ops-runbook seed: add node, remove node, replace node, handle hot key, handle full memory, handle slow node.

### Decision rules and heuristics

- **Modulo-N is a trap.** It is the first thing developers reach for; it breaks at the first resize.
- **Many shards beat many nodes.** Shards as the unit of placement, nodes as the unit of capacity. Independent counts for each.
- **Virtual nodes are not free.** More virtual nodes give smoother distribution at the cost of memory and lookup work. Pick a moderate number and measure.
- **Bounded loads tame skew with little extra complexity.** They are not a substitute for hot-key mitigation when skew is extreme.
- **Replicate failure domains, not just bytes.** Same-rack replicas are not replicas.
- **Hot keys need detection first.** Without per-key sampling, mitigation strategies are guesses.
- **Plan rebalance windows.** Off-peak rebalancing is much cheaper than peak rebalancing.
- **Origin protection is part of cache design.** A cache that protects nothing on miss-storm has failed its job.

### Edge cases

- **Very small item sizes with very high RPS.** Network protocol overhead dominates; consider request batching at the client and pipelining at the server.
- **Very large items.** Memory pressure spikes when a single item is updated. Consider chunking or moving large items to an object store with a small metadata cache.
- **Time-series-shaped keys.** Keys with a timestamp prefix create hot tails because writes concentrate on the newest range. Either reverse the prefix (timestamp as suffix) or use a key shard prefix.
- **Multi-tenant cache.** Tenants of vastly different sizes destroy balance. Consider per-tenant shard pools sized to expected load, with elastic capacity for spikes.
- **Cross-region cache.** Replication across regions adds latency that may violate the cache's value. Often better to run regional caches with origin-of-truth in one place.
- **Cache used for negative results.** Caching a "not found" prevents repeated origin lookups but creates correctness risk if a later write changes the answer. Set short TTLs on negative caches and invalidate on writes.
- **Persistent caches that must survive restart.** Crosses into KV-store territory; the design must consider durability, fsync policy, and crash-consistent state.

## Outputs

- `shard_design` — Markdown document with the summary, hashing scheme, shard and node counts, replication policy, hot-key plan, failure-mode table.
- `capacity_table` — Per-shard memory, RPS, headroom, and growth triggers. Suitable for sizing a capacity model.
- `ops_runbook_seed` — A starter runbook with the most common operations (add, remove, replace, hot key, full memory, slow node) sized for a junior on-call to follow.

## Examples

### Worked example

Input excerpt:

> Need a Redis-based cache for product catalog. ~80 GB hot data, ~150 GB warm. Reads: 30k RPS sustained, 90k peak. Writes: 200 RPS. Item size: 1–8 KB. Known hot keys: top 50 SKUs take ~40% of traffic. Stack: Kubernetes, Redis 7, Java clients. Failure tolerance: 1% of keys missing on single-node loss is acceptable; full shard outage of 5 minutes is acceptable.

Expected output sketch:

- Headline: 16 shards, ring consistent hashing with 200 virtual nodes per physical, bounded loads at 1.4×, hot-key replication for the top 50 SKUs (4 replicas each, client picks at random).
- Nodes: 8 physical Redis nodes (2 shards each initially), 32 GB memory, p99 4ms read target. Headroom: 35%.
- Replication: 1 primary, 1 read replica per shard, cross-zone placement.
- Hot key plan: per-node sampler reports top keys to a small aggregator every 30 seconds; identified hot keys provisioned with 4 replicas via a manual confirm step.
- Rebalance: shards as the unit of move; client uses a topology service for the shard-to-node map. Add a node by transferring 2 shards from the most loaded host; expected 10-minute move per shard with throttle.
- Origin protection: cache-aside with single-flight per key at the client; near-expiry jitter of 10%.
- Failure mode: single node loss takes 2 shards offline → bounded-loads spills + origin refill of 12.5% of keys. Origin sustains 4k RPS extra for the refill window.
- Ops runbook seeds: add node, drain node, replace node, hot-key promotion, full-memory event, slow-node detection.

## Limitations

- The skill works from a description of the workload; if the access pattern is described inaccurately, the recommendations are off. Encourage callers to attach a real distribution of key sizes and access counts.
- It does not pick a specific cache product. Recommendations apply across cache families.
- It does not size a database tier behind the cache; that is a separate concern with its own constraints.
- It assumes the team can run a stateful service. Teams without that experience should consider a managed cache first and revisit when the operational maturity supports self-management.
- It cannot solve cache correctness questions that are upstream of the cache itself (e.g. invalidation racing writes). Those answers come from the write path's design.

## Sources reviewed

- https://github.com/buraksezer/consistent
- https://github.com/buraksezer/olric
- https://github.com/redis/redis
- https://github.com/eko/gocache
- https://github.com/lafikl/consistent
- https://github.com/serialx/hashring
