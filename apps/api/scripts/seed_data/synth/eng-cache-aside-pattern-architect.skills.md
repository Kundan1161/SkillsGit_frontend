---
id: skillsgit-curated/cache-aside-pattern-architect
version: 1.0.0
name: Cache-Aside Pattern Architect
description: Design a cache layer for a service — choose cache-aside vs read-through vs write-through, set TTL and invalidation, prevent stampedes, mitigate hot keys, and document the consistency model.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags:
  - niche:caching-patterns
  - cache-aside
  - read-through
  - write-through
  - stampede-prevention
  - ttl-strategy
  - invalidation
  - cache-warming
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
  estimated_tokens_per_invocation: 6500
trigger_keywords:
  - cache aside
  - read through cache
  - write through cache
  - write behind
  - cache invalidation
  - cache stampede
  - thundering herd
  - hot key
  - cache ttl
  - cache warming
  - negative cache
  - dogpile
  - single flight
  - cache consistency
  - request coalescing
example_invocations:
  - "Design a cache for our product detail page — high read rate, occasional writes."
  - "We keep getting database spikes when popular keys expire — help us prevent the stampede."
  - "Pick between cache-aside and write-through for our user profile service."
inputs:
  - name: workload
    type: text
    required: true
    description: Service or endpoint being cached — read rate, write rate, item shape, freshness expectations, fanout of misses to the origin.
  - name: origin_characteristics
    type: text
    required: false
    description: What the cache fronts — database, downstream API, computed result. Cost and latency of a miss. Maximum tolerable load on the origin.
  - name: consistency_needs
    type: choice
    required: false
    description: How fresh the cache must be after a write.
    choices: [eventual-seconds, eventual-minutes, eventual-best-effort, read-your-writes, strict]
  - name: cache_substrate
    type: text
    required: false
    description: Available cache technology — in-process LRU, remote Redis/Memcached, CDN, multi-layer combination. Operational maturity.
  - name: failure_tolerance
    type: text
    required: false
    description: What is acceptable when the cache itself fails — increased origin load, stale reads, errors to callers.
outputs:
  - name: cache_design
    type: markdown
    description: Design document covering pattern choice, TTL strategy, invalidation strategy, stampede prevention, hot-key handling, and a stated consistency model.
  - name: failure_mode_table
    type: markdown
    description: Failure scenarios (origin slow, cache down, hot key, mass invalidation) with the cache's response and the alert that fires.
  - name: rollout_plan
    type: markdown
    description: How to introduce or change the cache safely — shadow reads, gradual cutover, observability, and rollback.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Cache-Aside Pattern Architect

## When to use

Use this skill when a team is adding a cache to a service for the first time, replacing an ad-hoc cache, or fixing a cache that is causing more trouble than it prevents. The output is a design document that picks the pattern, sets the TTL and invalidation policy, plans for stampedes and hot keys, names the consistency model out loud, and tells the team what to do when the cache itself fails.

The skill applies to:

- Service-level caches in front of a database (the most common case).
- Caches in front of a downstream API where the upstream wants to reduce latency or rate-limit consumption.
- Caches of expensive computed results (rendered HTML, search index lookups, ML inferences).
- Multi-tier setups combining an in-process cache, a remote cache, and a CDN.

Do not use this skill for:

- Sharded cache topology and consistent hashing — that is a separate, deeper concern with its own skill.
- Full distributed databases with strong consistency requirements.
- Browser-side caching of static assets where HTTP cache headers and CDN policy dominate.

## Inputs

- `workload` (required) — Read and write rates, the shape of items being cached, how stale they can be, and how concentrated the access is.
- `origin_characteristics` — Drives the urgency of stampede prevention and the value of caching at all. A cheap idempotent origin is a weak case; a slow expensive origin is a strong case.
- `consistency_needs` — Drives the invalidation strategy and whether write-through or write-around is appropriate.
- `cache_substrate` — Affects which patterns are practical. CDNs do not support fine-grained invalidation; in-process caches cannot be invalidated cluster-wide without a fanout.
- `failure_tolerance` — Drives the fallback behavior when the cache is unavailable.

## How to apply

Walk the design top-down: pattern, keys, TTL, invalidation, stampede prevention, hot keys, consistency statement, observability, rollout.

### 1. Decide whether a cache belongs

1.1. Compute the rough hit rate the cache will need to justify itself. A cache that delivers a 50% hit rate is not a cache; it is a complication. Useful caches typically run 80–99% hit rate. If the working set does not fit in the cache, or if the access pattern is too uniform, the cache will not earn its cost.

1.2. Confirm the origin is slow or expensive enough that caching helps. A fast in-region database often does not need a cache. A cross-region call, a complex query, or an external API usually does.

1.3. Confirm the data tolerates being stale. The freshness requirement is the load-bearing constraint of every cache design. If the data must be read-your-writes for the calling user, that is achievable; if it must be strictly consistent across all readers, the cache choices narrow significantly.

1.4. If the cache does not pass these gates, the right design may be no cache and a faster origin. Say so.

### 2. Pick the pattern

2.1. **Cache-aside (lazy loading)** — the application checks the cache first, falls back to the origin on miss, and writes the result into the cache. Writes go directly to the origin and either invalidate or update the cache entry. This is the default pattern for service-level caching. Pros: simple, works with any cache, the cache is purely an optimization (the system works without it). Cons: every miss has the latency of an origin call; coordination of invalidation is the application's job.

2.2. **Read-through** — the cache library is the only thing the application talks to for reads. On miss, the library calls a configured loader to fetch from the origin and stores the result. Application code does not see misses. Pros: clean call site; the cache is the abstraction. Cons: requires a cache library with this affordance; harder to reason about which calls hit the origin.

2.3. **Write-through** — every write goes through the cache, which writes to the origin synchronously and updates the cached entry. Pros: cache is always populated; reads-after-writes are consistent at the cache level. Cons: write latency includes both the cache and the origin; writes that bypass the cache (a batch job, a different service) leave the cache stale.

2.4. **Write-behind (write-back)** — writes are acknowledged after landing in the cache; the cache asynchronously flushes to the origin. Used by some databases internally. For application-level caches in front of a database, this is a dangerous pattern: data can be lost if the cache fails before flush, and ordering with concurrent writers becomes tricky. Reserve for cases with a strong durability story (replicated cache, persistent log).

2.5. **Write-around** — writes go straight to the origin and do not populate the cache. The cache fills on the next read. Pros: avoids polluting the cache with writes that are never read. Cons: read-after-write for the writing user requires an explicit fill or invalidation.

2.6. **Refresh-ahead** — on read, if the entry is near expiry, asynchronously refresh it from the origin while serving the cached value. Pros: keeps hot keys warm without a miss spike at expiration. Cons: extra origin load for items that may not be read again.

2.7. Default recommendation: cache-aside with explicit invalidation on writes, combined with a refresh-ahead pass for known hot keys. Switch to read-through when the language ecosystem makes it natural. Use write-through only when the origin and cache must remain in lockstep and write latency is acceptable.

### 3. Design keys and items

3.1. The cache key encodes the read. State its structure. Common shape: `service:entity:id:version` or `service:query-hash:version`. The version is a literal in the code; bumping it invalidates the entire keyspace, which is the simplest tool for incompatible-shape changes.

3.2. Confirm keys are bounded in size and free of user input that could explode the keyspace. An attacker who can choose cache keys can fill the cache with garbage.

3.3. The cached value is a serialized form of the result. Pick a serialization format that survives schema evolution; protobuf, MessagePack, and well-versioned JSON are common. Document the format and the version.

3.4. Bound the size of cached values. Very large values fragment the cache and inflate eviction rates. For multi-megabyte values, cache a reference (URL, blob id) and store the value out-of-band.

3.5. **Negative caches** — store cache entries for "not found" results with a short TTL. Without negative caches, repeated lookups for non-existent ids hammer the origin. Pick a separate, much shorter TTL for negatives (seconds to a minute).

### 4. Design TTL and freshness

4.1. The TTL is the maximum staleness the design tolerates. It is not arbitrary; it derives from the consistency need stated in section 1. Choose the longest TTL that satisfies the staleness requirement; it minimizes origin load.

4.2. Use **jittered TTLs**. A nominal TTL of 5 minutes should expand to a random range of 4.5–5.5 minutes per key. Without jitter, items inserted together expire together, and the cache sheds them in a coordinated burst.

4.3. For items with a known event-driven invalidation path (e.g. a record updated implies an invalidation message), the TTL can be longer — it is the safety net, not the primary freshness mechanism.

4.4. For items with no invalidation path, the TTL is the only freshness mechanism. Pick conservatively.

4.5. For items whose freshness need varies by caller (one caller tolerates a minute, another needs a second), the cache key should not include the tolerance — instead, the caller decides whether to accept the cached value or force a refresh.

4.6. **Stale-while-revalidate** — serve a slightly stale entry while triggering an asynchronous refresh. The cache returns the old value instantly and warms the new value in the background. Powerful when paired with refresh-ahead.

4.7. **Stale-if-error** — if the origin is unavailable, serve the cached value past its TTL rather than failing the request. Document the maximum staleness allowed in this mode (often minutes to hours, much longer than the normal TTL).

### 5. Design invalidation

5.1. Choose between TTL-only and event-driven invalidation. TTL-only is simpler and entirely correct as long as the staleness budget tolerates the TTL. Event-driven adds complexity but reduces staleness without paying origin load on every read.

5.2. For event-driven invalidation:

- The write path emits an invalidation event after the write to the origin commits.
- The invalidation handler deletes (or updates) the affected cache entries.
- The handler must be idempotent and survive at-least-once delivery.
- The invalidation must reach every cache instance — clusterwide for remote caches; per-process for in-process caches.

5.3. The two-store consistency problem: a write commits to the origin and then to the cache (or vice versa). Either order fails in interesting ways under failure. Mitigations:

- Write origin first, then delete the cache entry. On read miss, refill from the origin. This is the standard cache-aside flow and is correct if reads tolerate a brief stale window after a write.
- Use a single-source-of-truth change feed (CDC, outbox) and treat cache invalidation as a downstream subscriber.

5.4. **Avoid update-in-place on writes.** A pattern that reads-modify-writes through the cache races with other writers. Prefer delete-then-fill or invalidate-then-fetch.

5.5. **Bulk invalidation** — when a schema change or correctness fix demands invalidating many keys at once, bump the version literal in the key prefix. The old keys become unreachable and expire naturally; the new keys are filled by traffic. This is faster, simpler, and safer than a mass delete.

5.6. For CDNs, invalidation primitives are coarser (purge by URL or surrogate key). Design surrogate keys at the cache-fill site so a logical invalidation matches the surrogate set.

### 6. Prevent stampedes

6.1. A cache stampede happens when a popular key expires and N concurrent requests miss simultaneously, all calling the origin. The origin sees a sudden traffic burst.

6.2. **Single-flight (request coalescing)** — at each cache client, when a miss is in progress for a key, other concurrent misses for the same key wait for the first to finish and share the result. The origin sees one call instead of N. This is the highest-value stampede defense and should be the default.

6.3. **Probabilistic early expiration** — clients that read a near-expiry value occasionally recompute it ahead of expiry with a probability that grows as the entry ages. Approximates refresh-ahead without an explicit background pass.

6.4. **Locked refill** — only one process at a time refills a specific key; others serve the stale value or wait briefly. Implement with a short-lived lease in the cache itself.

6.5. **Jitter** — already covered in TTL design; prevents the coordinated-expiry case.

6.6. **Origin protection** — even with all of the above, set a circuit breaker around the origin call. If the origin is unhealthy, return stale-if-error rather than amplifying the failure.

### 7. Mitigate hot keys

7.1. A hot key is a key whose individual RPS dwarfs the average. Hot keys overload the single shard or node that owns them.

7.2. Detect hot keys with per-node sampling: each cache client samples request counts per key over short windows and reports the top entries to an aggregator. Avoid full per-key counters; sampling is cheaper and good enough.

7.3. Mitigations, from cheapest to heaviest:

- A small in-process micro-cache in front of the remote cache (single-digit seconds TTL) shields the remote cache from the bulk of the hot-key traffic.
- Replicate hot keys to multiple shards or to multiple keys on the same shard, with client-side random selection.
- Promote hot keys to a separate higher-throughput tier.
- Compute the hot value once per node per short window and broadcast it.

7.4. Hot keys interact poorly with LRU eviction; the value can be evicted just as it heats up. Consider LFU or W-TinyLFU eviction policies for caches with skewed access patterns.

### 8. State the consistency model

8.1. Write down, in one paragraph, what a reader of this cache can expect after a write. Examples:

- "Eventual consistency: reads may return values up to N seconds stale after a write."
- "Read-your-writes for the writer's session: the write path purges the cache entry before the response returns; subsequent reads from the same session refill from the origin."
- "Bounded staleness with event-driven invalidation: typical staleness under 1 second, worst case N seconds if the invalidation queue lags."

8.2. Document the failure cases too: what happens if the invalidation event is lost, if the cache cluster restarts, if the cache is unreachable. The consistency model is only useful if its failure modes are explicit.

8.3. Confirm the model matches what the calling product or feature actually needs. A user-visible feature that displays a value the user just wrote needs read-your-writes; a homepage list view usually tolerates more.

### 9. Plan cache warming

9.1. A cold cache (after restart, after deployment, after a region failover) sends a burst of misses to the origin. For most workloads, the origin can absorb this and the cache warms within minutes.

9.2. For workloads where the cold-start burst would overload the origin, plan explicit warming:

- Replay the top-N keys from a recent snapshot of the cache.
- Drive a background scan that hits the hottest keys in order.
- Stage the deployment to bring instances back gradually rather than all at once.

9.3. For caches with very large working sets and bursty cold starts, consider a persistent cache layer (snapshot to disk or replica from a peer).

### 10. Plan observability

10.1. Track per-key-prefix metrics: hit rate, miss latency, total RPS, eviction rate, and value size distribution. A drop in hit rate is usually the first sign of a regression in the cache design.

10.2. Track the origin load that the cache prevents: requests served from cache vs requests passed to origin per second. Expose to product owners so they can see the cost the cache is avoiding.

10.3. Track stampede defenses: single-flight coalesces per second, lock-refill waits, near-expiry refreshes. If these numbers are zero on a busy service, the defenses are not actually wired up.

10.4. Trace cache lookups in distributed traces so cache-induced tail latency is visible.

10.5. Alert on:

- Hit-rate drop versus baseline.
- Eviction-rate spike (working set is no longer fitting).
- Origin-load spike paired with cache RPS drop (the cache is failing).
- Near-expiry refresh failures (refresh-ahead is broken).

### 11. Plan failure handling

11.1. The cache must fail gracefully. If the remote cache is unreachable, every request becomes a miss. Confirm the origin and the service can survive 100% miss for at least a short window. If not, this is an availability problem that no cache can solve.

11.2. Decide whether to short-circuit on cache failure: if the cache client times out quickly, the request falls through to the origin. Without a short timeout, a slow cache adds to every request's latency.

11.3. Decide whether cache failure produces user-visible errors or degraded performance. Most designs prefer degraded performance and visible alerts.

11.4. Plan for the cache as a noisy neighbor: a runaway producer can fill the cache, evicting useful entries. Use per-tenant or per-prefix quotas if multi-tenant.

### 12. Plan the rollout

12.1. For a greenfield cache: stand up the cache disabled, enable it in shadow mode (cache filled but result not used), compare cached vs origin results to detect mismatches, then enable for traffic. Watch hit rate climb to the expected steady state.

12.2. For a change to an existing cache: bump the cache key version so the old keys retire naturally. Watch the origin load during the transition window.

12.3. For a high-stakes consistency change: pair the rollout with a test that drives a stream of writes and reads at controlled timing, and verifies the documented consistency model.

12.4. Always have a kill switch that disables the cache and falls through to the origin. The kill switch is the most useful operational lever you can build.

### 13. Emit the design

13.1. Lead with the pattern, the consistency model, and the expected hit rate.

13.2. Document the key shape, the TTL policy, and the invalidation strategy.

13.3. Include the failure-mode table covering cache down, origin down, stampede, hot key, and mass invalidation.

13.4. Include the rollout plan and the kill switch.

13.5. Provide a short operator section: dashboards to add, alerts to wire, common cache operations.

### Decision rules and heuristics

- **Name the consistency model first.** Every later choice descends from it.
- **TTL is freshness; invalidation is freshness too — pick which one is primary.** Both are belt and suspenders; one is load-bearing.
- **Hit rate below 80% is rarely worth the operational cost.**
- **Single-flight is non-negotiable on hot reads.**
- **Jitter every TTL.** No exceptions.
- **Bump a key version to invalidate the world.** Faster and safer than a delete loop.
- **Delete on write, fill on read.** Update-in-place races.
- **Negative caches matter.** Missing ids are the most common stampede vector.
- **The cache must fall through when it dies.** A cache that takes the system with it has failed its job.

### Edge cases

- **Multi-region writes** — a write in one region must invalidate caches in all regions, or readers in other regions get stale reads for the TTL window. Plan the cross-region invalidation path explicitly.
- **Write-then-immediate-read in tests** — flaky tests often come from read-your-writes assumptions that the production design does not promise. Tighten the consistency model or the test.
- **Bulk imports** — a bulk import that writes many records should not generate a flood of invalidation events; batch them or rely on a key-version bump.
- **Conditional caches** — entries whose validity depends on the caller's identity or permissions are easy to get wrong. Cache the underlying data and apply the permission check at the call site; do not cache the permission-applied view per caller.
- **Time-bound entries** — entries that go stale at a specific wall-clock time (e.g. promo ending at midnight) need either a TTL aligned to that time or a scheduled invalidation.
- **Boolean caches** — caching a yes/no answer about a record without a versioning hint is fragile; include the record's version or last-modified.
- **Idempotency keys** — server-side dedup tables look like a cache and behave nothing like one. They are durability, not optimization; do not cache them with eviction.

## Outputs

- `cache_design` — A design document with the pattern, key shape, TTL policy, invalidation, stampede defenses, hot-key plan, and the consistency model in plain prose.
- `failure_mode_table` — A table of failure scenarios and the cache's behavior in each.
- `rollout_plan` — A step-by-step plan to introduce or change the cache with checkpoints and a kill switch.

## Examples

### Worked example

Input excerpt:

> Adding a cache in front of a product detail endpoint. Reads 12k RPS, writes 30 RPS. Each product fits in 4 KB. Freshness: an editor can update a product and expects to see the change within 30 seconds. Origin is a SQL database that handles 2k RPS comfortably and 4k RPS under stress. Stack: Go services, Redis available. A few hundred products account for 60% of read traffic.

Expected output sketch:

- Pattern: cache-aside with delete-on-write. TTL: 60 seconds with ±10% jitter. Hit-rate target: 95%+.
- Consistency model: bounded staleness — readers see updates within 60 seconds via TTL, faster via the delete-on-write path triggered by the editor's save.
- Key shape: `catalog:product:{id}:v1`. Negative cache: `catalog:product:{id}:v1:nf` with a 15-second TTL.
- Stampede defenses: per-process single-flight; probabilistic early refresh at 80% TTL; remote-cache short timeout (10ms) with origin fallthrough.
- Hot-key plan: top-200 SKUs identified by sampling and warmed in process via a 5-second micro-cache; remote-cache replication considered only if the micro-cache proves insufficient.
- Eviction policy: W-TinyLFU on the in-process micro-cache to resist scan pollution. Remote cache uses LRU with the working set sized to fit in memory.
- Failure modes: Redis down — fall through to the origin (origin sized for 4k RPS, sufficient); editor update during Redis outage — origin write succeeds, cache is empty, next read refills. Stale-if-error window: 5 minutes.
- Rollout: shadow mode for 1 day to verify hit rate; enable for traffic; watch origin RPS drop from 12k to the long-tail rate; keep the kill switch live for the first week.
- Operator notes: dashboards for hit rate, miss latency, eviction rate, single-flight coalesces; alerts on hit rate below 85%, eviction rate above 200/s, miss latency p99 above 50ms.

## Limitations

- The skill produces design recommendations from the description provided; if the workload differs in production, the choices may need adjustment.
- It does not size the cache cluster's hardware; pair with a capacity-planning pass.
- It does not address sharding and consistent hashing in depth; for clusters that must scale across many nodes, use a separate sharding skill.
- It assumes the team can operate the cache substrate; teams new to cache operations should start with a managed cache.
- Recommendations apply across cache families and are not tied to a specific product.

## Sources reviewed

- https://github.com/redis/redis
- https://github.com/memcached/memcached
- https://github.com/eko/gocache
- https://github.com/dgryski/go-tinylfu
- https://github.com/jellydator/ttlcache
- https://github.com/hashicorp/golang-lru
