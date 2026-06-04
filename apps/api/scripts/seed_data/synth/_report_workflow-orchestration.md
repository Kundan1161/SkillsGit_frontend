# Wave-3 Synth Report — niche: workflow-orchestration

**Agent:** Wave-3 methodology-synthesis
**Date:** 2026-05-14
**Niche:** data — Apache Airflow / Dagster / Prefect DAG design (idempotency, retries, sensors, SLA)

## Files produced

All under `synth/`:

1. `dag-architect.skills.md` — design a robust DAG/asset graph/flow with task atomization, idempotency keys, retries, sensor vs schedule choice, branching, dynamic generation, observability. Three-orchestrator playbook.
2. `pipeline-data-contract-author.skills.md` — author a producer-consumer data contract (schema, freshness SLA, quality SLOs, ownership, on-failure behavior, versioning, lineage). YAML-first.
3. `orchestrator-migration-planner.skills.md` — plan a strangler-fig migration between orchestrators (or major-version jumps within one). Tiered batching, dual-run, cutover, decommission, risk register, comms plan.
4. `pipeline-backfill-conductor.skills.md` — plan and execute a historical backfill safely (idempotency proof, chunking, throttling, validation, promotion, rollback). Per-orchestrator execution commands.

## Sources (all verified Apache-2.0)

License-permissive sources only. No GPL/AGPL/proprietary. Verified by inspecting each repository's license badge or LICENSE page via WebFetch:

1. https://github.com/apache/airflow — Apache-2.0 (verified)
2. https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html — Apache-2.0 project docs (content verified)
3. https://github.com/dagster-io/dagster — Apache-2.0 (verified)
4. https://docs.dagster.io/guides/build/assets/defining-assets — Apache-2.0 project docs
5. https://github.com/PrefectHQ/prefect — Apache-2.0 (verified)
6. https://docs.prefect.io/v3/api-ref/python/prefect-tasks — Apache-2.0 project docs
7. https://github.com/apache/airflow/discussions/28905 — Apache-2.0 project discussion (idempotency reference)

Each skill file cites 5–7 of these URLs only. No vendor blog links, no paywalled sources, no unverified third-party repos.

## Patterns surfaced

Cross-skill patterns drawn from research and applied consistently:

- **Idempotency as a contract, not a property.** Every skill insists on an explicit idempotency proof: "writes are keyed on X using MERGE/OVERWRITE; therefore re-runs are safe." The `dag-architect` produces it; the `backfill-conductor` refuses to operate without it; the `data-contract-author` makes it part of the spec.
- **Atomize → key → retry → observe.** A consistent four-step skeleton for any task: one side effect; explicit idempotency key; retry policy tuned to failure class (no retries on deterministic errors); structured logs + metrics + lineage emission.
- **Sensor vs schedule vs event** as an explicit trigger decision with hybrid guardrail. Schedule by default; sensor when arrival varies (prefer deferrable in Airflow); event when a producer can emit; pair event-driven flows with a scheduled guardrail run.
- **Quality SLOs with severity tiers** (`block | breach | warn`) drive on-failure behavior. Block holds the partition; breach publishes with a flag; warn logs only. Encoded in contracts and reused in backfill validation.
- **Tier-up, complexity-down batching** for migrations and backfills. Practice on T3, refine on T2, deliver on T1, hardened delivery for T0. Reverse-criticality order builds the playbook before it matters.
- **Dual-write with comparator** as the shared safety mechanism for both migration and bug-fix backfill: write to a shadow location, diff against live, swap atomically only after the comparator is clean for the required window.
- **Versioning of contracts** (semver), with major-version migration windows requiring named-consumer ack — pulled forward into the migration planner's cutover protocol.

## Niche-specific rejections

- **astronomer/airflow-testing-guide**: license not visible on the landing page via WebFetch; treated as unverified and excluded. Replaced with the official `apache/airflow` repo and its Apache-licensed docs.
- **github.com/josephmachado/idempotent_data_pipeline**: returned 404; excluded. The patterns it would have illustrated (delete-write, partition overwrite, MERGE) are documented from first principles within the skill bodies and cross-referenced to Apache-2.0 sources only.
- All vendor blog links (Astronomer, Dagster.io blog, Prefect.io blog, Towards Data Science, Medium, Airbyte, ZenML, Orchestra) intentionally **omitted from the source lists**. They informed the research but the spec requires permissive-licensed, verifiable URL-only citations.

## Skill design choices

- **Frontmatter**: `license_type: free`, no `pricing` block (per brief). `category: data`, first tag `niche:workflow-orchestration` on every skill, then 4–6 orchestrator-specific tags. `ai.required_models` includes Claude Opus 4.7 + Sonnet 4.6; `compatible_models` adds GPT-4o / 4.1.
- **Bodies**: 300–700 lines each. All four use the required `## When to use` and `## How to apply` headings plus recommended `## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources` sections.
- **Cross-skill discipline**: each skill explicitly tells the user when to use a sibling skill instead. `dag-architect` defers contracts to `pipeline-data-contract-author`; `migration-planner` defers DAG-level design to `dag-architect`; `backfill-conductor` refuses if the pipeline is not idempotent and routes back to `dag-architect`.
- **No overlap with existing synth**: synth folder was empty at start; no merge step required.

## Confidence

**High** on:
- License compliance of cited sources (Apache-2.0 verified for primary repos).
- Technical accuracy of the patterns (idempotency, retries, dual-run, chunking) — these are well-established in the orchestrator docs and align with what Apache Airflow, Dagster, and Prefect officially recommend.
- Skill scope separation — each skill has a distinct trigger surface with no ambiguous overlap.

**Medium** on:
- Exactness of orchestrator API surface (decorator names, CLI flag names) for the most recent releases — covered to a level appropriate for a planning skill; downstream code-writing should re-check against current docs.
- The proposed retry defaults (retries=2, delays, backoffs) — these are reasonable industry defaults but a given team's environment may justify different numbers; the skill instructs the user to adjust.

**Low** risk areas:
- No pricing claims, no proprietary copy, no PII, no external scripts, no non-HTTPS links — passes the forbidden-content checks in `shared/skills-md-spec.md`.
