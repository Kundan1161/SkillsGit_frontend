# Wave-2 Synthesis Report — Data: Analytics Engineering & Metrics Layer

## Scope and positioning

Wave 1 covered the warehouse-engineering layer of the data category: `data-dbt-model-reviewer` (code review for dbt models), `data-migration-planner` (schema changes), and `data-star-schema-designer` (dimensional modeling at the table level). This wave covers the **analytics layer above** — the metrics, KPI structures, mart-as-product packaging, and experimentation pipelines that turn warehouse models into a governable analytics surface. No overlap with wave-1; the four new skills explicitly pair with the wave-1 skills as their downstream consumers.

## Files produced

All under `apps/api/scripts/seed_data/synth/`:

- `data-metric-definition-designer.skills.md` — 242 lines. Turns an ambiguous business question into a fully-specified metric (name, owner, grain, formula, dimensions, filters, governance) with explicit traps (fanout, count-distinct collisions, late binding, time-zone drift, refund/reversal handling, currency, versioning behavior). Outputs implementation sketches in MetricFlow YAML, Cube measures, LookML, or generic SQL.
- `data-kpi-tree-builder.skills.md` — 244 lines. Decomposes a north-star into a tree of drivers and operational inputs (arithmetic / funnel / segment / driver flavors), assigns owners and leverage estimates per node, then translates the tree into a 5-9-tile executive dashboard layout with commentary slots.
- `data-mart-designer.skills.md` — 264 lines. Designs a domain mart (revenue / marketing / product / support / custom) with facts at stated grain, dims with explicit SCD strategy, conformed dimensions across marts, materialization choices, tests, contracts, exposures, and a phased dual-publish rollout plan. Includes domain-specific shape recommendations.
- `data-experimentation-pipeline-architect.skills.md` — 288 lines. Designs the data pipeline for A/B testing — randomization unit choice, exposure logging discipline, warehouse landing, primary/secondary/guardrail metric set, SRM checks, CUPED-style variance reduction, power analysis with explicit MDE and duration, pre-launch and during-experiment checklists.

All four use the standard wave-2 frontmatter template with `category: data`, first tag `niche:analytics-engineering`, `license_type: free`, no pricing fields.

## Sources reviewed and verified

Every source confirmed for license (MIT / Apache-2.0 / BSD / ISC / Unlicense), star count (≥100), and freshness (commit or release within the last 18 months — most within last 30 days, given the May 2026 date):

- `cube-js/cube` — Apache-2.0 (backend) + MIT (client) — 20k stars — v1.6.46 May 11 2026
- `dbt-labs/metricflow` — Apache-2.0 (0.209+) — 1.6k stars — v0.211.0 May 12 2026
- `lightdash/lightdash` — MIT — 5.8k stars — v0.2945.1 May 14 2026
- `growthbook/growthbook` — MIT core (Open Core; enterprise dirs separately licensed but not relied upon) — 7.8k stars — v4.3.0 Feb 2026
- `apache/superset` — Apache-2.0 — 72.8k stars — actively maintained
- `Unleash/unleash` — Apache-2.0 — 13.5k stars — v7.6.4 May 14 2026
- `evidence-dev/evidence` — MIT — 6.3k stars — Feb 2026 release
- `rittmananalytics/ra_data_warehouse` — Apache-2.0 — 269 stars — actively maintained

Each skill cites 5-7 of these sources. `cube`, `metricflow`, `lightdash`, `superset`, and `evidence` appear in all four (they ground the analytics-engineering vocabulary). `growthbook` + `unleash` are unique to the experimentation skill. `ra_data_warehouse` is cited where domain-mart packaging patterns are relevant.

## Patterns extracted across sources

- **Semantic-layer grammar** (MetricFlow / Cube / LookML) converges on the same primitives: measure, dimension, time-grain, filter, metric type. The five-type taxonomy (simple / ratio / derived / cumulative / conversion) is canonical and used as the backbone of the metric-definition skill.
- **Conformed-dimension governance** is consistently underspecified across projects. The mart-designer skill makes the ownership rule explicit ("one owning mart per conformed dim, others consume by reference") because this is where most cross-domain reporting bugs originate.
- **Exposure-logging discipline** is the differentiator between teams that have feature flags (config) and teams that have experimentation (measurement). The experimentation skill makes this distinction loudly because conflating the two is the single most common pre-launch design error.
- **SRM-as-gate** (sample ratio mismatch as a hard gate, not a warning) is implicit in GrowthBook's design but rarely surfaced explicitly in tutorials. The experimentation skill foregrounds it.
- **KPI-tree decomposition** has no canonical open-source reference; commercial tools dominate. The kpi-tree-builder skill is the most original-prose-heavy of the four, with patterns synthesized from the structural conventions visible in Cube's data model, Lightdash's dashboards-as-code patterns, and the dashboard layouts common in Superset and Evidence.

## Rejected sources

- **Metabase** (47.3k stars) — AGPL-3.0; not in allowed list.
- **Mozilla Glean** — MPL-2.0; not in allowed list.
- **Hiflylabs/awesome-dbt** (1.7k stars) — GPL-3.0; not in allowed list.
- **welpo/srm** — AGPL-3.0 and only 0 stars.
- **Flipt** server code — Fair Core License; not in allowed list. (Client/SDK code is MIT but the experimentation-relevant logic is server-side, so the whole project was passed over.)
- **Statsig** — closed core; SDKs only open under various licenses; not relied upon.
- **Zenlytic/metrics_layer** — Apache-2.0 but only 47 stars (below 100-star threshold).
- **Victoriapm/awesome-analytics-engineering** — no LICENSE file declared (33 stars); ambiguous, conservatively excluded.
- **dbt-labs/jaffle-shop** — 301 stars but no LICENSE file declared on the repo; conservatively excluded despite being a useful pattern reference.
- **dbt-labs/dbt-semantic-interfaces** — Apache-2.0 but only 99 stars (just under the 100-star threshold; excluded for strictness even though the project is core dbt infrastructure).
- **michaellindon/ssrm** — Apache-2.0 but only 13 stars.

## Merge decisions

Examined all existing `synth/*.skills.md` files. No existing skill covered metric definition, KPI-tree construction, domain-mart packaging, or experimentation pipelines. All four new skills produced as net-new files; no existing skills edited or version-bumped.

## Confidence

- **High** on metric-definition-designer. The semantic-layer grammar converges cleanly across MetricFlow, Cube, and LookML; the five-type taxonomy is well-supported; the pitfall list (fanout, count-distinct, late binding, time zones, refund handling, currency, versioning) is universally cited.
- **High** on data-mart-designer. The fact/dim split, conformed-dimension governance, and domain-specific shape recommendations are well-grounded in dbt-labs documentation and the rittmananalytics warehouse package. The dual-publish rollout pattern is a wave-1 alignment.
- **Medium-high** on experimentation-pipeline-architect. The pipeline patterns (exposure logging, SRM, CUPED, guardrails) are well-established in the GrowthBook codebase and surrounding industry practice. Less direct open-source reference for power analysis specifics, but the patterns are textbook.
- **Medium** on kpi-tree-builder. KPI-tree structure is more management-consulting territory than open-source software; the skill synthesizes structural conventions from how Cube, Lightdash, Superset, and Evidence dashboards are typically organized, with explicit acknowledgement of decomposition flavors. The original-prose ratio here is highest among the four (least direct source coverage), so reviewers should pay extra attention to the tree-of-metrics terminology and the leverage-estimation guidance.

## Possible follow-ups for future waves

- A **semantic-layer migration planner** skill that pairs with the metric-definition designer and the schema migration planner — for moves from BI-tool-native metrics (LookML) to a warehouse-native semantic layer (MetricFlow, Cube).
- An **analytics-engineering hiring scorecard** skill — defining the rubric for analytics-engineer interview loops, paired with the engineering category.
- A **data contract / SLA writer** skill — pairing with the mart-designer to formalize the producer-consumer interface around marts and metrics.
- A **dashboard review skill** — auditing existing dashboards for cognitive load, comparison consistency, time-period selectors, and commentary discipline. Would pair with the kpi-tree-builder.
- An **AI-on-the-semantic-layer skill** — guidance for designing the metric catalog so that an LLM agent can answer business questions reliably; this is the data-side counterpart to the AI/agents marketplace category.
