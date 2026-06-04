# Wave-4 Methodology Recovery — Self-Service BI

**Niche:** `self-service-bi`
**Category:** `data`
**Author agent:** Wave-4 methodology-recovery
**Date:** 2026-05-14

## Skills produced

1. `self-service-bi-rollout-architect.skills.md` — designs the rollout of a self-service BI platform (governance model, semantic-layer placement, content tiers, namespace, access, training, audit cadence, support model).
2. `bi-dashboard-quality-reviewer.skills.md` — reviews a dashboard against a seven-axis rubric (correctness, freshness, ownership, performance, clarity, audience fit, distribution channel) and returns a prioritized punch list and certification recommendation.
3. `embedded-analytics-architect.skills.md` — designs a customer-facing embedded analytics surface (multi-tenant isolation, row-level security, token flow, embed mechanism choice, performance budget, branding, lifecycle).
4. `bi-content-migration-planner.skills.md` — plans a BI tool migration (inventory, dependency map, usage-based prioritization, dual-run, training, cutover, decommission).

All files live in `D:\skillsgit\apps\api\scripts\seed_data\synth\`.

## Sources reviewed (with license tags)

License tags reflect each project's stated terms at the time of review. Per policy, AGPL and proprietary sources were READ + CITED but no code or prose was copied or paraphrased; trademarked product names do not appear as methodology anchors in skill bodies (only in the closing "Sources reviewed" sections).

- `metabase/metabase` — AGPL-3.0 (community) + proprietary (commercial). Read for governance, collection/library, content-curation, dashboard-subscription, certification, and embed patterns.
- `apache/superset` — Apache-2.0. Read for RBAC, dataset certification, ownership, lightweight semantic-layer, guest-token-embed patterns.
- `lightdash/lightdash` — MIT (most code) + proprietary enterprise modules. Read for dbt-coupled semantic modeling, content-validation-in-CI, version history, and token-based embed patterns.
- `cube-js/cube` — Apache-2.0 backend + MIT client. Read for headless semantic layer, pre-aggregation, and multi-tenant context patterns.
- `grafana/grafana` — AGPL-3.0. Read for operational-dashboard freshness, panel-attached-alerts, and provisioning-as-code patterns.
- `redash/redash` — BSD-2-Clause. Read for query-as-source-of-truth and parameterized-query patterns.
- `dbt-labs/dbt-core` — Apache-2.0. Read for in-warehouse modeling-layer, metric documentation, and dependency-lineage patterns.
- `PostgREST/postgrest` — MIT. Read for database-layer row-level-security patterns.
- PostgreSQL row-security documentation — PostgreSQL license (open source). Read for database-enforced policy patterns.
- LookML / Looker documentation (Google Cloud, proprietary). Read only — cited for explore/view/derived-table layering and signed-embed concepts, expressed generically.

## Methodology patterns recovered

Across the sources reviewed, the recurring patterns that informed the skills are generic and not tool-specific:

- **Three-tier content model** (official / shared-working / personal sandbox), with visual cues and explicit promotion and demotion criteria. Surfaces in nearly every mature deployment regardless of tool.
- **Single-definition discipline**: one source of truth for each metric, expressed in a layer that all consumer surfaces share. The location varies (warehouse-resident, headless semantic layer, in-tool modeling) but the rule is constant.
- **Hub-and-spoke operating model** for non-trivial scale: central platform team owns infrastructure, definitions, and certification; domain analysts produce most consumer content.
- **Quarterly audit cadence** driven by usage telemetry, with archive-then-delete deprecation rules.
- **Database-enforced row-level isolation** for any customer-facing analytics surface, with application-layer filtering as a secondary defense.
- **Iframe-first embed mechanism** for most customer-facing deployments; SDK when integration depth is justified; reverse proxy as a last resort.
- **Pre-aggregation + per-tenant panel cache** for embedded performance at scale.
- **Migrations as portfolio problems**: 50–70% of legacy content typically retires rather than migrates; usage thresholds drive default disposition.
- **Dual-run with parity checks** and a hard decommission date, otherwise migrations drift indefinitely.

## Methodology-vs-expression boundary checks

Per the brief, this niche has AGPL and proprietary sources. Verification performed:

- No source code was copied or close-paraphrased in any skill body.
- No prose from any source's documentation was copied or close-paraphrased; vocabulary in the skill bodies is generic ("self-service BI tool," "modeling layer," "semantic layer," "self-hosted," "cloud-native," "iframe embed," "row-level policy").
- Trademarked product names ("Metabase", "Superset", "Looker", "LookML", "Lightdash", "Cube", "Grafana", "Redash", "Tableau", "Power BI") **do not appear as methodology anchors in any body text.** They appear only:
  - In `trigger_keywords` in two skills, where the names are search hints, not methodology claims (these are user-typed search terms that should retrieve the skill; this matches conventions in pre-existing skills such as `data-viz-dashboard-architect.skills.md`).
  - In the closing `## Sources reviewed` sections, as citations with license tags, per the synth folder's convention.
- License tags are stated for each cited project.
- The bodies describe techniques in generic terms; an implementer applying any of these methodologies could realize them in any tool in the category.
- The dashboard-quality reviewer skill is method-only; no source's quality checklist was copied.
- The embedded-analytics-architect's token, iframe, SDK, and reverse-proxy patterns are industry-standard concepts; the descriptions are independent.
- The migration planner's inventory → dependency → prioritize → dual-run → cutover loop is independent and described in generic vocabulary.

If a stricter interpretation of the brand-name policy is required (zero mention of names even in trigger_keywords and sources), the trigger_keywords can be trimmed and citations expressed via license-tagged categories rather than repository URLs. As authored, the skills match the pattern of pre-existing curated skills in the same folder.

## Frontmatter compliance

Each skill:

- `id` matches `skillsgit-curated/<slug>` (lowercase, hyphenated).
- `version: 1.0.0`.
- `category: data`.
- First tag is `niche:self-service-bi`; followed by 6–7 descriptive tags.
- `license_type: free`; pricing only carries `currency` and `support_included` (no cents fields, consistent with other free skills in the folder).
- `ai.required_models: [claude-opus-4-7]`, with sonnet and gpt-4o as compatible.
- Body length: each skill body is in the 300–600-line target range, instructional prose targeted at an AI agent executing the methodology.
- Required sections present: `## When to use`, `## How to apply`; recommended sections (`## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources reviewed`) all present.

## Confidence

- Methodology fidelity: **high.** The patterns described are widely observed across the sources and align with how mature analytics organizations actually run.
- License hygiene: **high.** No code or prose copying; AGPL/proprietary sources cited only with license tags; trademarked names not used as methodology anchors in body content.
- Coverage: **high.** Four skills cover the full lifecycle: rollout, ongoing quality review, embedded extension, and platform replacement. A future addition could cover the modeling-layer-migration depth that this set only sketches.
- Triggerability: **high.** Each skill has 13 trigger keywords and 4 example invocations using natural phrasings.
