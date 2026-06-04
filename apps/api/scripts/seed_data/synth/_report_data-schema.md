# Data — Schema Design, Modeling, dbt Patterns: Synthesis Report

## Files produced

1. `data-star-schema-designer.skills.md` — one-time, $99. 8 sources cited.
2. `data-dbt-model-reviewer.skills.md` — subscription, $9/mo with support. 8 sources cited.
3. `data-migration-planner.skills.md` — subscription, $11/mo with support. 7 sources cited.

## Sources accepted (license verified, ≥100 stars, recent activity)

| Repo | License | Stars | Used in |
|---|---|---|---|
| dbt-labs/dbt-core | Apache-2.0 | 12.8k | all three |
| dbt-labs/dbt-utils | Apache-2.0 | 1.7k | designer, reviewer |
| dbt-labs/dbt-project-evaluator | Apache-2.0 | 554 | designer, reviewer |
| dbt-checkpoint/dbt-checkpoint | MIT | 742 | designer, reviewer |
| sqlfluff/sqlfluff | MIT | 9.7k | designer, reviewer |
| Datavault-UK/automate-dv | Apache-2.0 | 587 | designer, reviewer |
| Data-Engineer-Camp/dbt-dimensional-modelling | MIT | 170 | designer, reviewer |
| dataform-co/dataform | Apache-2.0 | 977 | designer, reviewer |
| xataio/pgroll | Apache-2.0 | 6.5k | migration-planner |
| fabianlindfors/reshape | MIT | 1.8k | migration-planner |
| github/gh-ost | MIT | 13.3k | migration-planner |
| amacneil/dbmate | MIT | 6.9k | migration-planner |
| golang-migrate/migrate | MIT | 18.5k | migration-planner |
| sqitchers/sqitch | MIT | 3.1k | migration-planner |

Star schema designer: 8 sources. dbt reviewer: 8 sources. Migration planner: 7 sources. All within the 5–10 range.

## Rejected candidates

- **Hiflylabs/awesome-dbt** — GPL-3.0. Not in the allowed license set.
- **percona/percona-toolkit** — GPL-2.0. Not allowed.
- **liquibase/liquibase** — Functional Source License (FSL). Not in the allowed permissive set.
- **norton120/kimball_dbt** — MIT but only 43 stars (below 100-star threshold).
- **CarlTimms/Data-Vault-Example-Northwind** — MIT but only 12 stars; last commit October 2023 (older than 18 months from May 2026).
- **ScalefreeCOM/turbovault4dbt** — Apache-2.0 but only 46 stars.
- **calogica/dbt-expectations** — Apache-2.0, 1.2k stars, but last release September 2024 (outside 18-month freshness window from May 2026) and project marked no longer actively supported.

## Key patterns observed across sources

### Dimensional / star-schema patterns
- **Grain first.** Every implementation guide leads with naming the grain in plain English before writing any DDL. Mixed grain is the consistent root cause of broken fact tables.
- **Surrogate keys + natural keys, never just one.** Surrogate for joining and SCD; natural for traceability back to source.
- **SCD Type 2 is the default for analytics history**, with effective_from/effective_to/is_current. Type 1 is for typo fixes. Type 3 is rare. Type 6 only when business explicitly demands all of (current, history, prior).
- **Conformed dimensions are non-negotiable** when business processes overlap. The bus matrix is the standard tool to identify them.
- **Default to denormalized star, not snowflake.** Modern columnar warehouses make wide dimensions cheap.

### dbt project conventions
- **Three-layer convention** (staging / intermediate / marts) appears in nearly every reviewed project, with variant naming (e.g. `stg_`, `int_`, `fct_`/`dim_`).
- **Only staging models touch sources.** Everything else uses `ref()`. This is enforced both as a style rule and as a structural rule by `dbt-project-evaluator`.
- **Generic tests (unique, not_null, relationships, accepted_values) are baseline**; macros from `dbt-utils` and `dbt-expectations` extend coverage.
- **Materialization patterns:** view for staging, table for non-trivial intermediates, incremental for large append-only facts, snapshot for SCD Type 2.
- **Documentation via schema.yml + doc() blocks** is the standard; tools like `dbt-checkpoint` enforce description presence pre-commit.

### Schema migration patterns
- **Expand → migrate → contract** is the universal pattern across pgroll, reshape, gh-ost, and the migration-tool docs. Never modify in place when phased steps can keep both shapes valid.
- **Dual-write before switch-read before stop-write-old before contract.** Each transition needs its own deploy and soak period.
- **Backfill must be batched, throttled, and resumable.** Single-statement updates on large tables are the most common cause of incidents.
- **Online DDL matrix is engine-specific.** Postgres metadata-only ALTERs, MySQL `ALGORITHM=INPLACE`, Snowflake metadata operations, Redshift `DEEP COPY` — each has its own constraints worth surfacing.
- **Foreign keys, materialized views, triggers, and CDC consumers** are the four "hidden" dependencies that derail migrations. Every reviewed tool warns about them.

## Confidence per skill

- **Star Schema Designer — high confidence.** Patterns are stable, well-documented across 8 sources, methodology is consensus.
- **dbt Model Reviewer — high confidence.** The check list is concrete and aligned with what `sqlfluff`, `dbt-checkpoint`, and `dbt-project-evaluator` enforce mechanically, with reviewer judgment layered on top.
- **Migration Planner — medium-high confidence.** The expand/contract pattern is robust, but engine-specific advice depends on the engine; flagged this clearly. The plan is a strong starting point; the user must adapt to their migration framework.
