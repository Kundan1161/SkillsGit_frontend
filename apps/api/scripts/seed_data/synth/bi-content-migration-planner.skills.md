---
id: skillsgit-curated/bi-content-migration-planner
version: 1.0.0
name: BI Content Migration Planner
description: Plans a migration from one self-service BI tool to another — inventory, dependency map, usage-based prioritization, retirement criteria, dual-run strategy, training, and cutover.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:self-service-bi, migration, inventory, dependency-mapping, deprecation, dual-run, cutover, training]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8500
trigger_keywords:
  - BI migration
  - dashboard migration
  - tool migration
  - analytics platform migration
  - dashboard inventory
  - dependency map
  - retirement plan
  - dual-run
  - cutover plan
  - dashboard portfolio
  - usage analytics
  - deprecation
  - re-platform analytics
example_invocations:
  - "Plan a migration from our legacy BI tool to a new one. We have ~3,500 dashboards."
  - "We are switching analytics platforms next year — design the inventory, prioritization, and cutover."
  - "Most of our dashboards are unused. How do we figure out what is worth migrating?"
  - "Plan the dual-run period and training waves for moving 1,200 dashboards to a new tool."
inputs:
  - name: source_and_target
    type: text
    required: true
    description: The current (source) BI tool category, the target tool category, and any known feature gaps between them. Use generic categories if names are sensitive.
  - name: portfolio_size
    type: text
    required: true
    description: Approximate count of dashboards, charts, reports, datasets, and users on the source. Note any subsets already known to be high-value or already known to be junk.
  - name: time_budget
    type: choice
    required: true
    description: The window available for the migration.
    choices: [under-3-months, 3-to-6-months, 6-to-12-months, 12-to-18-months, open-ended]
  - name: people_budget
    type: text
    required: true
    description: How many engineers, analysts, and stakeholders are available for the migration, and any constraints (must-not-block other quarterly initiatives, etc.).
  - name: modeling_layer_state
    type: choice
    required: false
    description: Whether a shared modeling layer exists on the source side, the target side, or neither.
    choices: [shared-layer-exists, source-only, target-only, neither, being-built-in-parallel]
  - name: licensing_status
    type: choice
    required: false
    description: Posture toward the source tool's license at the end of migration.
    choices: [must-shut-off-by-deadline, can-keep-read-only, no-deadline, unknown]
outputs:
  - name: inventory_and_dependency_plan
    type: markdown
    description: How to take inventory of the source portfolio and build a dependency map between content, datasets, and the upstream warehouse.
  - name: prioritization_framework
    type: markdown
    description: How to rank source content for migration, retirement, or rebuild — by usage, business value, complexity, and overlap.
  - name: dual_run_strategy
    type: markdown
    description: How the two tools coexist during migration, including data-source sharing, parity checks, and traffic redirection.
  - name: training_and_change_management
    type: markdown
    description: How users learn the new tool while still using the old one, and how the cutover is communicated.
  - name: cutover_and_decommission
    type: markdown
    description: The cutover plan — final parity check, freeze, redirect, deprecation, and shutdown of the source.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when an organization is replacing one self-service BI tool with another and needs a structured plan for doing so without losing trust, breaking dependent workflows, or quietly inheriting the same dashboard sprawl on the new tool. Typical situations:

- Licensing has changed and the incumbent tool must be retired by a fixed date.
- The incumbent has been outgrown — capacity, governance, or semantic-layer alignment — and a different tool fits the target state better.
- An acquisition is consolidating two analytics estates into one.
- A new modeling layer is being introduced and the BI tool's coupling to the warehouse must be redesigned.
- The current tool is a mix of working, abandoned, and unmaintainable content and leadership has decided a re-platform is cheaper than a cleanup.

Do not invoke this skill to choose the target tool — that is a vendor-evaluation problem. Do not invoke it to design the target tool's governance model (use the self-service-bi-rollout-architect skill); the migration plan slots into that governance model.

## How to apply

The methodology treats the migration as a portfolio problem first, a translation problem second. Most failed BI migrations failed because the team treated every source asset as something to rebuild on the target. Almost always, a large fraction of the source portfolio should be retired, not migrated; another fraction should be merged; another fraction is the actual work. Decide what is in scope before estimating effort.

### 1. Take inventory of the source

1. **Enumerate everything.** Dashboards, individual charts, scheduled reports, datasets, modeling-layer artifacts, alerts, embed integrations. Each is a candidate object for the migration decision.
2. **Capture metadata per object.** Name, owner (if any), folder, last-modified date, last-viewed date, view count over the last 90 days, the data source it depends on, and any downstream consumers.
3. **Distinguish content from infrastructure.** A dashboard is content; a modeling-layer dataset that feeds 40 dashboards is infrastructure. Infrastructure needs a different migration approach (typically: replicate first, redirect later).
4. **Tag by source freshness.** A dashboard untouched in two years is different from one touched yesterday. Freshness is a strong predictor of whether anyone will notice if it disappears.
5. **Tag by visibility.** Pinned on a portal, scheduled email, linked from a wiki, embedded — these are signs of integration with the broader business. Unlinked content is easier to retire silently.
6. **Capture the unknown-owner population.** Content with no named owner is the bulk of every aging deployment. Surface the count; it will drive a major part of the prioritization step.

### 2. Build a dependency map

7. **Map content → dataset → source table.** Every dashboard depends on one or more datasets; every dataset depends on one or more source tables. Without this map, "what does this break?" cannot be answered.
8. **Map cross-content dependencies.** A dashboard may link to another dashboard; a chart may be reused in multiple dashboards. Reused charts are a hidden refactor.
9. **Map content → consumer.** Which users view which content, and which content is the trigger for which downstream action (an email, a meeting, an alert).
10. **Identify the spine.** A small number of objects sit upstream of a large fraction of consumers. Migrating the spine first delivers most of the user-visible value.
11. **Identify the long tail.** A large number of objects with zero or one consumer. The long tail is the strongest candidate for retirement.
12. **Identify orphan content.** Content with no human consumer (or only the author) in 90 days. Default disposition: retire, not migrate.
13. **Identify circular and ambiguous dependencies.** A dataset that depends on a dashboard that exports back into a dataset is a smell; fixing the dependency may be cheaper than migrating both.

### 3. Prioritize

14. **Score each object on three axes.** Usage (views, unique consumers, criticality of the downstream action), business value (revenue-supporting, regulator-required, customer-facing), and migration complexity (how hard to rebuild on the target — simple, moderate, deep).
15. **Bucket the portfolio into four dispositions.** Migrate now (high usage, high value), Rebuild from requirements (high value but the source implementation is bad), Retire (low usage, low value), Defer (medium usage, low complexity — migrate in a later wave).
16. **Quantify the expected reduction.** A typical aging deployment can retire 50–70% of its content without consumer complaint. State the target reduction explicitly; without it, every owner defends their content.
17. **Apply a usage threshold.** Content viewed by fewer than N unique users in the last 90 days defaults to Retire; the owner must actively defend it to escape that disposition. Pick N from the usage distribution — the elbow is usually obvious.
18. **Defend high-value low-usage content.** Some content matters precisely because it is rarely consulted — regulatory reports, year-end views, disaster-recovery dashboards. Do not retire by usage alone; the value axis is separate.
19. **Decide the rebuild policy.** When migrating a complex dashboard, the temptation is to clone panel-for-panel. The better policy: rebuild from the question, not from the implementation. Most source dashboards have accreted panels nobody needs, and a literal port carries the cruft.
20. **Reject the "lift and shift" framing for non-trivial content.** Lift and shift sounds cheap; in practice it produces dashboards on the new tool that no one trusts, because they look slightly different from the originals and no one knows why.

### 4. Plan the dual-run period

21. **Define the dual-run scope.** Both tools live for a defined window. The source is read-only for new content from a stated date; the target is the only place new content is built.
22. **Share the data source between the tools.** Wherever feasible, both tools query the same warehouse or modeling layer. Otherwise discrepancies arise from data drift, not from the migration itself, and the team chases ghosts.
23. **Run parity checks on migrated content.** For each migrated object, the same query against the same source produces the same numbers in both tools. Document the parity test and run it before the source version is decommissioned.
24. **Accept small documented differences.** Slight rounding, different time-zone handling, different null-treatment — fix or document, not both.
25. **Provide a redirect path.** When a user visits a migrated dashboard on the source, they should land on the equivalent on the target — or at least see a banner pointing to it. Silent retirement of a still-visited dashboard breaks workflows.
26. **Stage the migration by wave, by domain.** All-at-once cutovers fail. Move one domain at a time, validate parity, then move the next. The order is by readiness, not by alphabet.
27. **Maintain a single source of truth for definitions during dual-run.** If the modeling layer is being migrated as well, the two tools must consume the same canonical definitions during the overlap, or numbers will disagree and the migration will be blamed for the disagreement.

### 5. Train and communicate

28. **Train per cohort, per domain, during the wave that domain is in.** Generic all-hands training does not stick. Domain-specific cohorts using domain-specific examples do.
29. **Identify champions early.** One analyst per domain who learns the target tool before their cohort. The champion is the local helper.
30. **Document the target's idioms, not its features.** A user does not need a feature tour; they need "how do I do the five things I do every week on the source tool, on the target tool." Build the playbook from real questions.
31. **Pre-emptively communicate retirement.** The owner of content marked for retirement gets a notice ahead of decommission, with the dispositioning rationale and an appeal path. Surprise retirements destroy trust in the migration program.
32. **Set up an open feedback channel during dual-run.** Users will discover edge cases that the dependency map missed; the channel must surface them quickly.
33. **Publish wave-level progress.** A simple dashboard of dashboards: how many migrated, retired, deferred, rebuilt; how many users have been trained; how many parity checks have passed. Visibility builds confidence.

### 6. Decommission the source

34. **Define an end-state for the source.** Three plausible end-states: full shutdown, read-only frozen archive, or extracted snapshot of historical numbers. Pick one and design the decommission to match.
35. **Set a decommission date and protect it.** Schedule pressure is what forces real prioritization decisions. A migration without a shutdown date drifts indefinitely.
36. **Freeze the source at a stated date.** No new content; existing content read-only. The freeze is itself a milestone and shifts behavior more than any communication.
37. **Run a final parity sweep.** Every object marked Migrate must have a verified parity pass on the target before the source is decommissioned.
38. **Snapshot the source.** Even if the tool is being shut off, the underlying queries and dashboard definitions are worth archiving — a future archaeologist will want them.
39. **Cancel the license at the date.** Licensing dollars are a continued sponsor of the new world; do not let them shadow-fund the old.

### 7. Carry forward the lessons

40. **Apply the new governance to the migrated content immediately.** The target tool starts with the governance model — certified vs. working content, named ownership, audit cadence. Migrating content does not exempt it from those rules; in fact, the migration is the natural moment to enforce them.
41. **Resist re-creating the source's organization on the target.** The source's folder structure encodes years of organizational drift. The target deserves a clean namespace designed against the rules, not the past.
42. **Capture the retirement reasons.** Why each piece of retired content was retired is itself a data set. Patterns in the reasons (entire categories of dashboard that no one used) inform the future content strategy.
43. **Inventory what got dropped on the floor.** Some users will, post-migration, ask for something that was retired. Have an "exception" process for resurrecting individual items, capped at a small budget. Most exceptions never get used; offering the process is what matters.
44. **Hand off operations to the standing platform team.** A migration program ends; the platform team continues. Document everything they need to run the target without the migration team.

### 8. Compose the deliverable

45. **Lead with the inventory and dependency plan.** Without this, every later step is hand-waving.
46. **Show the prioritization framework with proposed disposition counts.** "Of 3,500 dashboards: 350 Migrate now, 200 Rebuild, 2,400 Retire, 550 Defer to wave 3" is a real plan; "we will migrate dashboards" is not.
47. **Lay out the dual-run strategy with parity and redirect policy.**
48. **Lay out the training and change-management plan by wave by domain.**
49. **Lay out the cutover, the final parity sweep, the freeze, and the decommission date.**
50. **State the assumptions.** If the user did not specify portfolio size, time budget, or licensing deadline, name the assumption.
51. **Estimate effort per wave.** Person-weeks per wave, with the caveat that the first wave teaches the team and subsequent waves are faster.

### 9. Self-check before responding

52. **Confirm the plan retires a substantial fraction of the portfolio.** A plan that migrates everything is not a plan; it is a budget request.
53. **Confirm the cutover has a date.** Without one, the migration will not end.
54. **Confirm parity checks are explicit.** "It looks the same" is not a parity check; same query, same source, same number is.
55. **Confirm the dual-run period has a stated end.** Dual-run that lingers becomes the new normal.
56. **Confirm the plan applies the target's governance to migrated content from day one.** Otherwise the source's chaos is inherited.
57. **Confirm the user's actual constraints — time budget, people budget, licensing deadline — are reflected.** A plan that doesn't fit the constraints is fiction.

## Inputs

- Source and target tool categories and known feature gaps.
- Portfolio size: object counts and any known-good or known-junk subsets.
- Time budget and people budget.
- Optional: modeling-layer state, licensing status.

## Outputs

- Inventory and dependency plan.
- Prioritization framework with proposed disposition counts.
- Dual-run strategy with parity and redirect policy.
- Training plan by wave by domain.
- Cutover and decommission plan with a date.

## Examples

**Example invocation**

> "We need to migrate from an aging self-hosted BI deployment to a managed cloud-native one within 9 months. We have ~3,500 dashboards, ~14,000 saved questions, ~600 datasets, ~2,000 active users, and ~50 scheduled email reports. Most content has no owner. We have a small dbt project on the warehouse but no formal semantic layer. The data team is five engineers and three analysts; one analyst can lead the migration. Licensing is on a contract that renews in 10 months — must shut off by then."

**Expected high-level output**

Inventory and dependency plan: full export of source metadata (name, owner, folder, last-viewed, view-count, source dataset, downstream consumers). Build a content → dataset → source-table map. Capture orphan-owner population and view-count distribution.

Prioritization framework: score on usage (90-day unique consumers), business value (revenue-supporting / regulator-required / customer-facing), complexity (simple/moderate/deep). Apply usage threshold of < 3 unique consumers in 90 days = default Retire. Expected dispositions of 3,500 dashboards: ~350 Migrate, ~200 Rebuild from requirements, ~2,400 Retire, ~550 Defer. Saved questions: ~95% Retire (most are one-off exploration). Datasets: ~600 → ~120 governed datasets on the target.

Dual-run strategy: both tools query the same warehouse. Modeling layer expanded in dbt with canonical metrics so both tools can consume the same definitions. Parity check per Migrate object: same query, same source, same number. Source becomes read-only at month 5. Migrated content gets a redirect banner on the source pointing to the target. Three waves by domain: Wave 1 (revenue + finance, months 1–3, ~120 objects), Wave 2 (product + marketing, months 3–6, ~180 objects), Wave 3 (operations + people + cross-functional, months 6–8, ~50 objects + Defer queue).

Training and change-management: champion network of 6 (one per domain). Cohort training of 25 per wave, scheduled when each wave starts. Playbook of "the five things you do every week, mapped from source to target." Retirement notices sent to owners 30 days before decommission with appeal path. Wave-progress dashboard published weekly.

Cutover and decommission: source frozen at month 5, read-only through month 8. Final parity sweep month 8. Source decommissioned month 9; license cancelled at the renewal date. Snapshot of source definitions and queries archived to long-term storage.

Effort: roughly 12 person-weeks for Wave 1 (team is learning), 8 for Wave 2, 5 for Wave 3, plus 4 person-weeks for the dependency map and inventory tooling up front, plus 2 person-weeks for cutover. Total roughly 31 person-weeks — comfortably within the 9-month window for the available team. Risk: ownership-discovery for the 70%+ owner-less population will require domain-by-domain outreach during Wave 1.

## Limitations

- The methodology assumes the target tool can serve the workload. If the target has hard feature gaps relative to the source, those gaps must be addressed independently (build, accept, or pick a different tool).
- It does not migrate alerts, scheduled deliveries, or embedded surfaces in a single pass; those follow the content they depend on, on a wave-by-wave basis.
- Effort estimates are coarse. Real per-wave timing depends on team experience, content shape, and warehouse cooperation.
- Migrating a modeling layer in parallel is described, not detailed; a separate modeling-layer-migration skill would cover that depth.
- The skill assumes a warehouse is available to both tools during dual-run. If the migration includes a warehouse change as well, treat that as a separate predecessor project.

## Sources reviewed

Methodology synthesized across the following projects and public documentation. License tags reflect each project's stated terms at the time of review. No prose, code, or branded terminology is copied; the migration vocabulary above is original.

- https://github.com/metabase/metabase — AGPL-3.0 (community) + proprietary. Read; cited for content-export and dashboard-as-versioned-object patterns.
- https://github.com/apache/superset — Apache-2.0. Read; cited for dataset-and-dashboard import/export patterns.
- https://github.com/lightdash/lightdash — MIT + proprietary. Read; cited for content-validation-in-CI and dbt-coupled-migration patterns.
- https://github.com/redash/redash — BSD-2-Clause. Read; cited for query-portfolio inventory patterns.
- https://github.com/grafana/grafana — AGPL-3.0. Read; cited for dashboard-provisioning-as-code patterns.
- https://github.com/dbt-labs/dbt-core — Apache-2.0. Read; cited for warehouse-resident modeling-layer migration patterns.
- LookML / Looker documentation (Google Cloud, proprietary). Read only; cited for content-validation and project-lifecycle patterns, expressed generically.
