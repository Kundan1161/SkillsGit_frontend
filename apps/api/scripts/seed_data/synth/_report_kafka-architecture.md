# Wave-3 Report — Kafka Architecture niche

**Agent:** methodology-synthesis, Wave-3
**Niche:** data — Apache Kafka / Kafka-API broker topic design, consumer patterns, exactly-once, schema evolution, Streams topologies
**Date:** 2026-05-14

## Files produced

- `synth/kafka-topic-architect.skills.md`
- `synth/kafka-consumer-pattern-picker.skills.md`
- `synth/kafka-schema-evolution-architect.skills.md`
- `synth/kafka-streams-pipeline-designer.skills.md`

All four are net-new (the synth/ directory was empty at start).

## Merge analysis vs eng-eventing-architect

The Wave-2 `eng-eventing-architect` skill at `apps/api/scripts/seed_data/synth/eng-eventing-architect.skills.md` covers broker-family selection, taxonomy basics, schema-versioning basics, and delivery-semantics at the conceptual level — across all broker families (Kafka, Pulsar, NATS, RabbitMQ, etc.). It explicitly defers Kafka-specific details ("does not generate concrete Kafka or Pulsar configuration").

The four Kafka skills produced here add materially Kafka-specific depth that does **not** fit the broker-neutral eventing-architect:

- Topic-architect: partition-count math, RF/min-ISR, compaction details, cleanup policies, KRaft notes, tiered storage, rack-awareness, CreateTopicPolicy.
- Consumer-pattern-picker: consumer-group identity rules, cooperative sticky assignor, `max.poll.interval.ms`, EOS-v2 with `transactional.id` stability, retry-tier topics, idempotent producer settings.
- Schema-evolution-architect: registry placement, subject naming strategies (TopicNameStrategy etc.), Avro/Protobuf compat modes including transitive variants, Protobuf reserved-field-number rule, CI-gated registration.
- Streams-pipeline-designer: KStream/KTable/GlobalKTable, RocksDB and changelog-topic configs, standby replicas, EOS-v2 inside Streams, windowing types and grace, `num.standby.replicas`, `commit.interval.ms`, application-reset hazard.

Decision: **do not merge**. Keep eng-eventing-architect as the broker-neutral chooser; the four new skills are the Kafka-specific implementation. Cross-reference is in each "When to use" / "Do not use this skill for" section.

## Sources

Per-skill sources (5–7 each), URL-only, all license-verified MIT / Apache-2.0 / BSD-2-Clause / BSD-3-Clause:

**kafka-topic-architect**
- https://github.com/apache/kafka (Apache-2.0)
- https://github.com/strimzi/strimzi-kafka-operator (Apache-2.0)
- https://github.com/confluentinc/cp-demo (Apache-2.0)
- https://github.com/confluentinc/librdkafka (BSD-2-Clause)
- https://github.com/debezium/debezium (Apache-2.0)
- https://github.com/provectus/kafka-ui (Apache-2.0)
- https://github.com/twmb/franz-go (BSD-3-Clause)

**kafka-consumer-pattern-picker**
- https://github.com/apache/kafka (Apache-2.0)
- https://github.com/confluentinc/librdkafka (BSD-2-Clause)
- https://github.com/segmentio/kafka-go (MIT)
- https://github.com/twmb/franz-go (BSD-3-Clause)
- https://github.com/strimzi/strimzi-kafka-operator (Apache-2.0)
- https://github.com/debezium/debezium (Apache-2.0)

**kafka-schema-evolution-architect**
- https://github.com/apache/avro (Apache-2.0)
- https://github.com/protocolbuffers/protobuf (BSD-3-Clause)
- https://github.com/apache/kafka (Apache-2.0)
- https://github.com/debezium/debezium (Apache-2.0)
- https://github.com/apache/iceberg (Apache-2.0)
- https://github.com/confluentinc/cp-demo (Apache-2.0)

**kafka-streams-pipeline-designer**
- https://github.com/apache/kafka (Apache-2.0)
- https://github.com/confluentinc/kafka-streams-examples (Apache-2.0)
- https://github.com/confluentinc/cp-demo (Apache-2.0)
- https://github.com/apache/flink (Apache-2.0)
- https://github.com/strimzi/strimzi-kafka-operator (Apache-2.0)
- https://github.com/apache/avro (Apache-2.0)

## Rejected sources

- **confluentinc/schema-registry** — dual-licensed Confluent Community License (main project) plus Apache-2.0 (client and avro libs). The main project is **not** in the allowlist (MIT/Apache-2.0/BSD/ISC/Unlicense). Discarded as a citation target. The skill therefore stays registry-product-agnostic and recommends apache/avro and google/protobuf for the schema spec layer instead.
- **redpanda-data/redpanda** — Business Source License (BSL) on the core engine; converts to Apache-2.0 after a delay. BSL is **not** in the allowlist. Rejected; advice is broker-API-agnostic (Kafka-API-compatible) without citing Redpanda.
- **confluentinc/kafka-connect-iceberg** — could not verify a single Apache-2.0 license on the repo within the time budget; Apache Iceberg itself (Apache-2.0) was used instead as a cleaner citation.

## Patterns captured

- **Topic-architect**: event vs entity classification, naming convention (`{env}.{domain}.{kind}`), partition-key rules incl. skew handling, partition-count formula with re-evaluation triggers, retention defaults by topic kind, RF=3 / min-ISR=2 production default, rack awareness, compaction details, ACL conventions, tenancy strategies, KRaft / tiered storage notes.
- **Consumer-pattern-picker**: side-effect class taxonomy (in-Kafka, in-Kafka-plus-DB, in-Kafka-plus-external-API, user-visible), delivery-semantics ladder, group-id rules, cooperative sticky as default assignor, offset-commit cadence rules, in-process retry vs tiered retry topics vs DLQ, EOS-v2 with stable `transactional.id`, idempotency-key patterns for external calls, observability minimums.
- **Schema-evolution-architect**: Avro/Protobuf/JSON-Schema selection criteria, registry as a hot dependency, TopicNameStrategy vs TopicRecordNameStrategy, BACKWARD_TRANSITIVE for events / FULL_TRANSITIVE for compacted entities, full rollout playbook (add field, deprecate field, remove field, rename, type change, split entity, hard break), Protobuf reserved-field-number rule, CI-gated registry writes, deprecation windows.
- **Streams-pipeline-designer**: DSL vs Processor API, KStream/KTable/GlobalKTable selection, stateful operations (aggregations, joins, windows), co-partitioning requirement, window types incl. grace periods and suppression, EOS-v2 scope and limits, RocksDB state stores plus changelog topics, standby replicas, static membership, `commit.interval.ms` and threading, restart-time engineering, application-reset hazards.

## Confidence

- **High** on the technical content: Kafka primitives are stable and well-documented; the configuration knobs and trade-offs cited are mainstream and broker-version-correct for 2.5+ (KRaft and EOS-v2 era).
- **High** on license compliance: every cited repo verified via WebFetch; non-allowlist licenses (Confluent Community License, BSL) explicitly rejected with notes in this report.
- **Medium-high** on no-merge decision: the eng-eventing-architect skill is clearly broker-neutral; this skill set is clearly Kafka-specific. Cross-references in each skill body keep them composable.
- **Medium** on partition-count and retention defaults: these are workload-dependent. Skills state defaults as "starting points" with re-evaluation triggers rather than fixed prescriptions; bodies are explicit about benchmark-and-tune.

## Frontmatter and spec compliance

- Each skill uses `category: data` (per niche assignment).
- First tag on every skill: `niche:kafka-architecture` (per niche assignment).
- Each skill has 4–7 additional tags within the 0–10 limit.
- `license_type: free` on all four; `pricing` block contains currency and `support_included: false` only (no monetary values).
- `ai.required_models: [claude-opus-4-7]` plus a `compatible_models` list.
- Body lengths: each within the 300–700-line guideline.
- Required body sections present: When to use, How to apply, Outputs, Examples, Limitations, Sources reviewed.
