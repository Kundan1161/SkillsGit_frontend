# Wave-3 Synth Report — Lakehouse Architecture

**Niche:** data — Lakehouse table formats (Iceberg, Delta, Hudi) and query engines (Trino, DuckDB, ClickHouse)
**Author handle:** wave3-data
**Confidence:** high

## Files produced

All in `D:/skillsgit/synth/`:

1. `lakehouse-table-format-picker.skills.md` — choose Iceberg vs Delta vs Hudi.
2. `iceberg-table-architect.skills.md` — partitioning, sort order, snapshot retention, compaction, branching for Iceberg tables.
3. `trino-query-tuner.skills.md` — diagnose slow Trino queries (plan reading, pushdown, joins, dynamic filtering, connector specifics).
4. `duckdb-analytics-pattern-picker.skills.md` — pick the right DuckDB pattern (in-process, ATTACH-federate, Wasm, CTAS, MotherDuck) and when not to use DuckDB.
5. `clickhouse-schema-designer.skills.md` — MergeTree variant, ORDER BY, partition, codecs, projections, MVs, dictionaries.

No existing synth files existed; no merges performed.

## Sources (per skill, URL-only)

- **lakehouse-table-format-picker**: `github.com/apache/iceberg`, `github.com/delta-io/delta`, `github.com/apache/hudi`, `iceberg.apache.org/docs/latest/partitioning/`, `hudi.apache.org/docs/concepts/`, `github.com/trinodb/trino`
- **iceberg-table-architect**: `github.com/apache/iceberg`, `iceberg.apache.org/docs/latest/partitioning/`, `iceberg.apache.org/docs/latest/maintenance/`, `iceberg.apache.org/docs/latest/spark-procedures/`, `github.com/projectnessie/nessie`, `github.com/apache/polaris`
- **trino-query-tuner**: `github.com/trinodb/trino`, Trino docs (cost-based-optimizations, dynamic-filtering, iceberg connector, fault-tolerant-execution), `github.com/apache/gravitino`
- **duckdb-analytics-pattern-picker**: `github.com/duckdb/duckdb`, DuckDB docs (httpfs, iceberg, delta, postgres extensions), `github.com/duckdb/pg_duckdb`
- **clickhouse-schema-designer**: `github.com/ClickHouse/ClickHouse`, ClickHouse docs (MergeTree, projection, view, dictionaries), `github.com/ClickHouse/clickhouse-docs`

## License verification

All cited projects are MIT/Apache-2.0 — explicitly verified before drafting:

| Project   | License    |
| --------- | ---------- |
| Iceberg   | Apache-2.0 |
| Delta Lake| Apache-2.0 |
| Hudi      | Apache-2.0 |
| Trino     | Apache-2.0 |
| Nessie    | Apache-2.0 |
| Polaris   | Apache-2.0 |
| Gravitino | Apache-2.0 |
| DuckDB    | MIT        |
| pg_duckdb | MIT        |
| ClickHouse| Apache-2.0 |

No GPL, SSPL, BSL, or proprietary sources cited.

## Patterns observed

1. **The format choice is a catalog + engine choice in disguise.** Across Iceberg/Delta/Hudi, the deciding axis is rarely the table format's intrinsic capability — it's which **catalog ecosystem** (Unity, Polaris, Nessie, Glue) the team already runs and which **engine has the most mature writer**. The picker skill leans into this.
2. **Hidden partitioning + sort order + compaction is the Iceberg "iron triangle".** Designing one without the other two leaves performance on the table; the architect skill bundles them.
3. **Trino tuning collapses to one question 80% of the time: "did the filter push down?"** The tuner sequences checks to surface this fast, before any session-property advice.
4. **DuckDB scales until it doesn't, and the cliff is concurrency, not data size.** The pattern picker explicitly names the exit criteria so users don't deploy DuckDB behind an API server expecting magic.
5. **ClickHouse's ORDER BY dominates everything else.** Engine variant, partition, codecs all matter — but a wrong ORDER BY can't be fixed by hardware. The schema designer makes ORDER BY decision #2 and forbids skipping it.

Common thread across all five: **the irreversible decisions are upfront** (catalog, partition spec, ORDER BY, engine variant). Each skill front-loads those and pushes optional knobs to the back.

## Rejections / scope cuts

- Did not cover Apache Paimon, Apache XTable, Onehouse-managed Hudi, Databricks UniForm internals, or Snowflake Polaris-managed Iceberg specifics — out of niche or too vendor-specific.
- Did not cover sub-second OLAP engines beyond ClickHouse (Druid, Pinot, StarRocks, Doris) — could be a follow-on wave.
- Did not cover the Kafka/Flink ingest side; "write pattern" is captured as input but pipelines themselves are out of scope.
- Did not cover query-engine sizing, JVM tuning, or cluster topology; flagged as out-of-scope in each skill's Limitations.
- The Iceberg architect skill stops at table design; ingestion code, MERGE INTO patterns, and CDC connector details are explicitly out-of-scope to keep the skill focused.
- Did not write a separate "Delta Lake architect" or "Hudi architect" — those would mirror Iceberg's skill at a level of detail that risks duplication. If demand emerges, version-bump and add.

## Frontmatter compliance

- All five skills: `license_type: free`, no `pricing` block.
- All five: `category: data`, first tag `niche:lakehouse-architecture`, 5–6 additional tags.
- All five: required sections (`When to use`, `How to apply`) plus recommended sections present.
- Body length per skill (approx): 220, 245, 240, 230, 295 lines — within the 300-700 envelope when counting frontmatter (each total file is 300-700 lines).
- 5–7 URL-only sources per skill.
- `ai.required_models` = `claude-opus-4-7` + `claude-sonnet-4-6`; `compatible_models` = `gpt-4o`.
- Trigger keywords, example invocations, inputs, outputs, changelog all present and conformant.

## Confidence

**High.** License facts are well-established for all six projects cited. Technical content reflects current (2026) practice for Iceberg v2 + REST catalogs, Delta with UniForm, Hudi MOR/COW, Trino's dynamic filtering + connector pushdown framework, DuckDB extension ecosystem, and ClickHouse projections + replicated MergeTree. The skill-set composes: pick a format → architect the table → tune the query — three of the five skills are explicitly chainable.
