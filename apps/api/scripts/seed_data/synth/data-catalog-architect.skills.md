---
id: skillsgit-curated/data-catalog-architect
version: 1.0.0
name: Data Catalog Architect
description: Plan a data-catalog rollout — entity model, ingestion patterns, lineage capture, ownership assignment, discovery UX, and governance review cadence.
authors:
  - name: Wave-3 Data Synth
    handle: wave3-data
    role: author
category: data
tags:
  - niche:data-governance
  - data-catalog
  - lineage
  - metadata
  - ownership
  - discovery
  - datahub
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - data catalog
  - metadata platform
  - data discovery
  - data lineage
  - openlineage
  - datahub
  - apache atlas
  - column-level lineage
  - data ownership
  - glossary
example_invocations:
  - "Plan a data-catalog rollout for a 2,000-table warehouse."
  - "Which catalog should we pick, and how do we ingest metadata?"
  - "We need column-level lineage across Airflow, Spark, and dbt."
  - "Design ownership assignment and stewardship review cadence."
inputs:
  - name: estate
    type: text
    required: true
    description: Inventory of systems to catalog — warehouses, lakes, BI tools, pipelines, streams.
  - name: goals
    type: text
    required: true
    description: Why a catalog now — discovery, compliance, lineage for incidents, ML feature reuse, deprecation, etc.
  - name: org_shape
    type: text
    required: false
    description: Number of producers and consumers, central platform team size, data-mesh maturity.
  - name: constraints
    type: text
    required: false
    description: SaaS vs self-hosted, cloud, security posture, existing tools to integrate.
outputs:
  - name: rollout_plan
    type: markdown
    description: Entity model, ingestion plan, ownership scheme, governance cadence, and 90-day rollout.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Data Catalog Architect

## When to use

Use this skill when an organization is **rolling out a data catalog / metadata platform** — either for the first time, or replacing a failed first attempt. The work is 30% picking the tool and 70% picking the **rollout strategy**: entity model, ingestion patterns, ownership mechanics, lineage scope, discovery UX, and the governance ritual that keeps it from rotting.

Trigger phrases include:

- "data catalog rollout"
- "metadata platform"
- "data discovery / data search"
- "column-level lineage"
- "DataHub / Amundsen / Atlas / OpenMetadata pick"
- "ownership assignment for datasets"
- "data steward program"

Do **not** use when the user is asking how to author a single contract (route to `data-contract-author`) or how to test data quality (route to `data-quality-test-designer`). Catalog is the substrate; contracts and tests are what live on top of it.

## How to apply

Work through six decisions. The order matters: skip ahead and you'll find you didn't have enough information to make the later choices.

### 1. Goals before tooling

Force the user to pick a **primary** goal. Catalog rollouts that try to do everything die in committee.

Common primary goals, ranked by ease of demonstrable ROI:

1. **Incident response / lineage**: "When dashboard X breaks, find the upstream table." Wins fans fast.
2. **Discovery / reuse**: "Find a trustworthy revenue table." Wins fans slowly.
3. **Regulatory inventory**: "Where is PII?" Required, but rarely loved.
4. **Cost attribution**: "Which team owns this $80k/month query?" Politically charged.
5. **ML feature reuse**: "Has anyone built a churn feature?" Niche, high value when it lands.

Pick one as the **demo case** for the first 90 days. Everything else is a nice-to-have until that one is undeniable.

### 2. Entity model

A catalog isn't a list of tables; it's a graph of metadata entities. Decide which entity types are first-class for your org. A typical minimal set:

- **DataPlatform**: Snowflake, BigQuery, S3, Kafka, Postgres, Looker, Tableau.
- **Dataset**: a table, topic, file, view, dashboard. Datasets have a stable URN that survives renames.
- **Schema**: the typed structure of a dataset; columns are first-class so lineage can hang off them.
- **DataJob / DataFlow**: an Airflow DAG, a dbt model run, a Spark job. Required for run-time lineage.
- **User and Group**: identities synced from SSO. Owners and stewards are roles on these.
- **Domain**: a business area (Finance, Growth, Trust). Anchors discovery and access.
- **GlossaryTerm**: business definitions linked to columns/datasets ("Active Customer", "Recognized Revenue").
- **Tag**: lightweight classification (`pii`, `tier-1`, `deprecated`).

Optional, add later: **MLModel**, **Feature**, **DataProduct**, **Container** (folder), **Assertion** (quality result), **Incident**.

Anti-pattern: modeling **departments** as first-class. They reorg; the catalog should not. Model by **domain** (a Finance domain survives a reorg even when the team moves).

### 3. Ingestion patterns

Decide for each source: **pull**, **push**, or **stateless agent**.

- **Pull** (catalog calls the source on a schedule): fine for SQL warehouses; cheap to operate; loses anything that happened between scrapes (intra-day runs).
- **Push** (source emits events to the catalog): best for pipelines and streaming engines. OpenLineage is the lingua franca — emit OpenLineage events from Airflow/Spark/Flink/dbt and route them to the catalog.
- **Stateless agent** (CI/CD step or sidecar that scans then exits): right for ephemeral or sandboxed environments where the catalog can't reach in.

Recommendations:

- Warehouses (Snowflake, BigQuery, Postgres): **pull** on a 15–60 min cadence via the catalog's connector. Capture statistics with the metadata (row counts, last-modified) so consumers see freshness.
- Pipelines (Airflow, dbt, Spark, Flink): **push** via OpenLineage. This is the only practical way to get **column-level lineage** without parsing thousands of SQL strings out-of-band.
- BI tools (Looker, Tableau, Superset): **pull**. Lineage stitching from BI back to the warehouse is rarely automatic — plan to model the joins explicitly.
- Streaming (Kafka, Pulsar): **pull** from the schema registry; **push** OpenLineage from the consumer jobs.
- Files (S3, GCS): pull listings + a `crawler` for partitioned tables. If you have Iceberg/Delta/Hudi, ingest the table metadata, not the raw file list.

Operational rules:

- Idempotent ingestion. Catalogs that lose history on a re-run aren't catalogs.
- Backfill plan: how do you reconstruct historical lineage if the agent was down for a day?
- Rate limits: don't take down production by scraping every 5 minutes.

### 4. Lineage scope

Pick a **target depth** explicitly. The conversation "we want full column-level lineage everywhere" guarantees a 6-month delay.

Depth tiers:

- **L0 — Dataset-level (table → table)**: the cheap default; useful for impact analysis.
- **L1 — Run-level (which job touched which dataset, when)**: needed for incident response.
- **L2 — Column-level (which output column is derived from which input columns)**: the gold standard; expensive to build; valuable for PII propagation and breaking-change impact.
- **L3 — Transformation-aware (the actual SQL/code that produced the column)**: a recent column lineage parser plus OpenLineage SQL facets get you here.

Recommended rollout: L0 + L1 in the first 90 days, L2 on tier-1 pipelines (finance, regulatory), L2/L3 elsewhere over the following two quarters.

Lineage hygiene rules:

- **Never trust** lineage that hasn't been refreshed in N hours (configurable). Stale lineage is worse than no lineage — it lies confidently.
- **Show the source** of each lineage edge: which agent, which run, when. Build the UX so a viewer can click through.
- **Manual edits** are allowed but flagged as `manual` and re-asserted on next agent run if still valid.

### 5. Ownership assignment

A dataset without an owner is a liability. Ownership has to be:

- **Required** at ingestion. Reject metadata pushes without an owner field. Block creation of new datasets that don't declare one.
- **A team, not a person.** Persons go on vacation. Sync teams from your identity provider.
- **Time-stamped.** Owners change; show "owned by X since 2026-02".
- **Auditable.** Changes are events.

Bootstrap strategy for an existing estate:

1. Auto-assign by heuristic: dataset name prefix, schema name, source dbt repo `team:` annotation, recent committers in the producing pipeline.
2. Publish the auto-assignment to the candidate teams with a 14-day correction window.
3. Anything still unclaimed after 14 days is **escalated to leadership** and (optionally) **frozen** — read access stays, writes are blocked until owned.

Steward roles beyond owner:

- **Business steward**: defines glossary terms and approves classification.
- **Technical steward**: maintains the schema, contracts, quality monitors.
- **Privacy steward**: confirms classification for PII-bearing datasets.

### 6. Discovery UX and governance cadence

A catalog that nobody opens is a database. Optimize for **the search experience**.

- **Search**: full-text on names, descriptions, columns, tags; rank by usage (queries in the last N days), tier, freshness, and personal affinity (recently viewed by you/your team).
- **Trust signals on result cards**: owner, classification, tier, last-updated, last-queried, quality SLO status, deprecation flag.
- **Glossary inline**: hovering a column shows the linked business term.
- **Lineage panel**: 1-hop graph by default with depth controls; never blast the user with a 200-node firehose.
- **"Ask"**: who do I message? Owner + stewards are one-click chat.

Governance ritual that keeps the catalog alive:

- **Weekly**: owners triage unowned/quarantined entities flagged by ingestion. Owners receive a digest of changes.
- **Monthly**: domain stewards review glossary additions, classification disputes, deprecation candidates.
- **Quarterly**: leadership review of coverage metrics (% datasets owned, % with descriptions, % with quality SLOs, lineage coverage by tier), cost of the platform, top unmet requests.

Catalog **coverage SLOs** to publish:

- ≥ 95% of tier-1 datasets have an owner.
- ≥ 90% have a description longer than N chars.
- ≥ 80% have at least one quality SLO.
- ≥ 95% have L0 lineage; ≥ 70% tier-1 have L2 lineage.

If these don't improve quarter-over-quarter, the program is failing — escalate.

### 90-day rollout sketch

- **Weeks 1–2**: pick the catalog, stand up the dev instance, ingest one warehouse + one pipeline orchestrator. Demo to a friendly internal customer.
- **Weeks 3–6**: ingest the rest of the tier-1 warehouses, OpenLineage from Airflow/dbt, build the search UX, draft the entity model in production.
- **Weeks 7–10**: ownership bootstrap pass; publish coverage dashboard; integrate with one incident-response use case (lineage in the on-call runbook).
- **Weeks 11–13**: BI tool ingestion, glossary v1, governance rituals kick off, baseline coverage SLOs.

## Inputs

- **estate** (required): systems to catalog, with rough scale (datasets, daily runs).
- **goals** (required): the one or two primary outcomes that justify the project.
- **org_shape** (optional): producer/consumer counts, central platform size, mesh maturity.
- **constraints** (optional): SaaS vs self-hosted, cloud, security posture, must-integrate tools.

## Outputs

- A picked **primary goal** and a 90-day demo case.
- The **entity model** — which types are first-class and why.
- The **ingestion plan** per system (pull / push / agent), with cadence and failure mode.
- The **lineage depth target** with rollout staging.
- The **ownership scheme** — required fields, bootstrap heuristic, escalation policy.
- The **discovery UX checklist** — search ranking, trust signals, lineage panel rules.
- The **governance cadence** — weekly / monthly / quarterly rituals, coverage SLOs.
- A **risks list** — common ways catalog rollouts fail in this org's specific shape.

## Examples

> "200-team data mesh, dbt + Snowflake + Looker, want self-serve discovery."

Pick discovery as primary. Use a graph-native catalog (DataHub-style) so domains and lineage are first-class. Ingestion: Snowflake pull every 30m, dbt OpenLineage on every run, Looker pull nightly. Bootstrap ownership from dbt repo `+meta: {owner: team-x}` annotations. L1 lineage everywhere, L2 only on dbt models that produce dashboards. Glossary owned by domain stewards; central team owns the platform, not the content.

> "Compliance-driven: SOX + GDPR; we have 2,000 tables and don't know where PII is."

Pick regulatory inventory as primary. Ingestion: warehouse pull plus a column-name and sample-based PII classifier on first ingestion. Entity model includes Classification as first-class. Ownership bootstrapped from system owners; unowned PII is frozen until claimed. L0 + L1 lineage to support DPO reports of "where did this PII flow". Quarterly access review feeds into the governance cadence.

> "We failed at catalog v1 — the metadata went stale and nobody trusted it."

Diagnose: probably ingestion was pull-only with a long cadence, ownership wasn't required, and there were no coverage SLOs. Restart with push-based OpenLineage on pipelines, required ownership at write time, and a public coverage dashboard. The hardest part is rebuilding consumer trust — pick one team, make their search experience excellent, let them tell the others.

## Limitations

- This skill produces a rollout plan, not a tool selection by SKU. Tool-specific configuration (e.g., DataHub ingestion recipes, Atlas hook config) is left to the implementation team.
- Cost modeling depends on dataset count and event volume; budget a separate spike to size storage and compute.
- ML feature catalogs (feature stores) overlap with general catalogs but have different SLOs (latency, point-in-time correctness); if that's the goal, partner with a feature-store-specific design.
- A catalog without an engaged owner population becomes shelfware in ~6 months. The governance cadence is not optional.

## Sources

- https://github.com/datahub-project/datahub
- https://github.com/OpenLineage/OpenLineage
- https://github.com/apache/atlas
- https://github.com/bitol-io/open-data-contract-standard
- https://github.com/datacontract/datacontract-cli
