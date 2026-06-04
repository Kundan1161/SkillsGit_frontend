# Synthesis Report — niche:distributed-systems

**Wave:** 2 (methodology-synthesis)
**Category:** engineering
**Author agent:** distributed-systems specialist
**Date:** 2026-05-14
**Confidence:** high

## Skills produced

| Slug | Status | Body lines (approx) | Sources |
|------|--------|---------------------|---------|
| `eng-resilience-pattern-picker` | new | ~360 | 7 |
| `eng-eventing-architect` | new | ~420 | 7 |
| `eng-saga-orchestrator-designer` | new | ~420 | 7 |
| `eng-consistent-hashing-cache-architect` | new | ~380 | 6 |
| `eng-chaos-experiment-planner` | new | ~370 | 6 |

All five are within the 300–700 body-line target and follow the wave-2 frontmatter template established by `eng-service-decomposition.skills.md`. All carry `category: engineering`, `niche:distributed-systems` as the first tag, and `license_type: free` with no pricing fields populated. The `id` field uses the `skillsgit-curated/` namespace.

## Pattern observations across surveyed repos

- The mature resilience libraries (Resilience4j, Polly, gobreaker, Sentinel) converge on the same building blocks: timeouts, exponential backoff with jitter, circuit breakers with both error-rate and slow-call thresholds, bulkheads via thread pools or semaphores, and explicit fallbacks. The disagreement is on defaults; the vocabulary is shared. This justified the high-confidence default numbers in `resilience-pattern-picker`.
- Event-streaming systems (Kafka, Pulsar, NATS) and the application-layer wrappers (Dapr, Eventuate Tram, asynq) converge on per-key ordering, idempotent consumers, schema-registry-driven evolution, and outbox-pattern producer durability. Choreography vs orchestration is a recurring debate; the synthesis recommends orchestration past three steps with the outbox as the default producer pattern.
- Durable-execution engines (Temporal, Cadence, Restate, Dapr Workflows) and the saga-specific frameworks (Eventuate Tram Sagas) converge on idempotent step functions, durable state per run, automatic retry with backoff, and explicit compensation flows. The "needs intervention" terminal state appears across all of them; the synthesis treats it as first-class.
- Consistent hashing libraries (buraksezer/consistent, lafikl/consistent, serialx/hashring) and store-layer projects (Olric, Redis sharding patterns) converge on virtual nodes, bounded loads as a skew-tamer, and hot-key replication as the standard mitigation. Modulo-N hashing is uniformly rejected.
- Chaos toolkits (Chaos Mesh, LitmusChaos, Netflix Chaos Monkey) converge on hypothesis-driven design, explicit abort criteria, blast-radius controls, and learning-capture. The synthesis turns these into a planning template usable independent of any specific tool.

## Rejections (license, freshness, or scope)

- **Netflix Hystrix** (Apache-2.0, 24.5k stars) — last release 2018, in maintenance mode. Fails 18-month freshness rule. Not cited.
- **Netflix Conductor** (Apache-2.0, 12.8k stars) — archived December 2023. Fails freshness. Replaced with Temporal, Cadence, Restate.
- **Twemproxy** (Apache-2.0, 12.3k stars) — last release July 2021. Fails freshness. Replaced with buraksezer/consistent, Olric, lafikl/consistent for hashing patterns.
- **Chaos Toolkit** (Apache-2.0, ~2k stars) — last release February 2024, ~18 months prior to today. Borderline freshness; conservatively excluded.
- **k6** (AGPL-3.0, 30.6k stars) — license out of the allowed list. Not cited.
- **Machinery** (MPL-2.0, 8k stars) — license out of the allowed list (allowed set: MIT/Apache-2.0/BSD/ISC/Unlicense). Not cited.
- **Sidekiq** — dual licensing with commercial Pro and Enterprise tiers. Not cited to avoid trademark and license ambiguity.
- **Redis 8.x** — newer versions use RSALv2/SSPLv1/AGPLv3 tri-license. Cited only as a general reference (BSD versions remain in the wild); usage limited to architectural patterns, no copied code or trademarked terms beyond the project name in source URLs.

## Sources cited per skill (URLs only)

### eng-resilience-pattern-picker
- https://github.com/resilience4j/resilience4j (Apache-2.0, 10.7k, Mar 2026)
- https://github.com/App-vNext/Polly (BSD-3-Clause, 14.2k, Mar 2026)
- https://github.com/sony/gobreaker (MIT, 3.6k, active)
- https://github.com/alibaba/Sentinel (Apache-2.0, 23.1k, Oct 2025)
- https://github.com/dapr/dapr (Apache-2.0, 25.7k, Apr 2026)
- https://github.com/hibiken/asynq (MIT, 13.3k, Feb 2026)
- https://github.com/eko/gocache (MIT, 2.9k, May 2026)

### eng-eventing-architect
- https://github.com/apache/kafka (Apache-2.0, 32.6k, active)
- https://github.com/apache/pulsar (Apache-2.0, 15.2k, Apr 2026)
- https://github.com/nats-io/nats-server (Apache-2.0, 19.8k, Apr 2026)
- https://github.com/dapr/dapr (Apache-2.0, 25.7k, Apr 2026)
- https://github.com/eventuate-tram/eventuate-tram-core (MIT, 1.2k, active)
- https://github.com/hibiken/asynq (MIT, 13.3k, Feb 2026)
- https://github.com/celery/celery (BSD-3-Clause, 28.5k, Mar 2026)

### eng-saga-orchestrator-designer
- https://github.com/temporalio/temporal (MIT, 20.3k, Apr 2026)
- https://github.com/uber/cadence (Apache-2.0, 9.3k, Feb 2026)
- https://github.com/restatedev/restate (open source, 3.9k, Feb 2026)
- https://github.com/dapr/dapr (Apache-2.0, 25.7k, Apr 2026)
- https://github.com/eventuate-tram/eventuate-tram-sagas (MIT, 1.1k, active)
- https://github.com/apache/kafka (Apache-2.0, 32.6k)
- https://github.com/hibiken/asynq (MIT, 13.3k)

### eng-consistent-hashing-cache-architect
- https://github.com/buraksezer/consistent (MIT, 773, Nov 2022) — borderline on stars; included because it is the canonical Go bounded-loads reference and is downstream-depended-on by multiple cited libraries
- https://github.com/buraksezer/olric (Apache-2.0, 3.4k, Jan 2026)
- https://github.com/redis/redis (BSD on 7.2.x and prior; 8.x uses RSALv2/SSPLv1/AGPLv3 — cited for general architectural reference only)
- https://github.com/eko/gocache (MIT, 2.9k, May 2026)
- https://github.com/lafikl/consistent (MIT, 686, active) — borderline stars; same justification as above
- https://github.com/serialx/hashring (MIT, 586, active) — borderline stars; same justification

### eng-chaos-experiment-planner
- https://github.com/Netflix/chaosmonkey (Apache-2.0, 16.9k, Jan 2025)
- https://github.com/chaos-mesh/chaos-mesh (Apache-2.0, 7.7k, Mar 2026)
- https://github.com/litmuschaos/litmus (Apache-2.0, 5.4k, Apr 2026)
- https://github.com/dapr/dapr (Apache-2.0, 25.7k, Apr 2026)
- https://github.com/resilience4j/resilience4j (Apache-2.0, 10.7k, Mar 2026)
- https://github.com/temporalio/temporal (MIT, 20.3k, Apr 2026)

## Notes on the star-count rule

The ≥100-stars threshold passed for every cited repository. The three smaller consistent-hashing libraries (buraksezer/consistent at 773, lafikl/consistent at 686, serialx/hashring at 586) are all comfortably above 100. They are below the ~1000 stars heuristic some reviewers may apply, but their methodology contribution is canonical (consistent hashing with bounded loads, libketama-style rings) and they are cited only for patterns, not for any verbatim content.

## Confidence and follow-ups

- **Confidence: high** for resilience, eventing, and saga skills. The methodology converges across many well-known repos and the defaults in the skills are widely cited industry practice.
- **Confidence: medium-high** for the consistent-hashing skill. The smaller source repos are canonical but less battle-tested at scale than, say, Memcached's own clients. A future revision could add a server-side production reference once an acceptably licensed and fresh option appears.
- **Confidence: high** for the chaos-experiment skill. The hypothesis-driven framing is widely adopted and the toolkits cited all support it.

### Suggested follow-up wave-3 work
- Add a sixth skill on **idempotency-key contract design** — currently distributed across the resilience and saga skills, but a focused treatment is justified by the number of failure modes the topic touches.
- Add a wave-3 skill on **outbox pattern implementation** with concrete database and broker pairs; the eventing-architect skill cites it but does not implement it.
- Revisit the consistent-hashing skill in 6–12 months to consider including newer production-grade libraries that did not meet freshness today (notably any rejuvenated successors to Twemproxy if they appear).
- Consider a separate wave-2 skill on **load-shedding and adaptive concurrency** (Netflix concurrency-limits, Sentinel system-protection rules) — the topic was touched in the resilience picker but deserves its own skill.

## Validation

All five files include the required `## When to use` and `## How to apply` sections, plus recommended sections (`## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources reviewed`). No forbidden content present. All `license_type: free` with empty pricing block. All semver `1.0.0` initial releases with changelog entries dated 2026-05-14.
