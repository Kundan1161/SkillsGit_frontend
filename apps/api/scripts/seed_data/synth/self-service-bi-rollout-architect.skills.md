---
id: skillsgit-curated/self-service-bi-rollout-architect
version: 1.0.0
name: Self-Service BI Rollout Architect
description: Designs an end-to-end rollout for a self-service BI tool — governance model, semantic-layer placement, collection structure, certified vs sandbox content, deprecation policy, training plan, and audit cadence.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:self-service-bi, governance, semantic-layer, rollout, content-organization, certification, training, audit]
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
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - self-service BI
  - BI rollout
  - BI governance
  - semantic layer
  - certified content
  - dashboard governance
  - BI training program
  - data product rollout
  - business intelligence rollout
  - metrics layer
  - analytics platform launch
  - dashboard sprawl
  - dashboard catalog
example_invocations:
  - "We are rolling out a self-service BI tool to 800 employees. Design the governance model."
  - "Plan the launch of a new BI platform: where should the semantic layer live, and how do we organize collections?"
  - "Help us define certified vs. sandbox content rules and a deprecation policy for our analytics platform."
  - "We have dashboard sprawl. Design a content audit and cleanup process we can run quarterly."
inputs:
  - name: organization_profile
    type: text
    required: true
    description: Headcount, departments using analytics today, current analytics maturity, regulatory regime (if any), and the dominant data culture (centralized analyst team, embedded analysts, citizen analysts).
  - name: current_state
    type: text
    required: true
    description: What exists today — incumbent BI tool if any, warehouse or lakehouse layout, modeling layer (dbt, hand-rolled views, none), known pain points, and content volume to migrate or coexist with.
  - name: target_outcomes
    type: text
    required: true
    description: The decisions or workflows the platform must enable, the audiences served (executive, operator, analyst, external customer), and any timing or budget constraints.
  - name: tool_category
    type: choice
    required: false
    description: Category of the chosen self-service BI tool, used to tune recommendations.
    choices: [open-source-self-hosted, open-source-cloud-managed, proprietary-cloud, semantic-layer-plus-thin-client, embedded-in-product, undecided]
  - name: modeling_stack
    type: choice
    required: false
    description: Where business logic lives or will live.
    choices: [in-warehouse-dbt, in-warehouse-views, in-tool-semantic-layer, hybrid, none]
outputs:
  - name: rollout_plan
    type: markdown
    description: A phased rollout plan with milestones, owners, and exit criteria for each phase.
  - name: governance_model
    type: markdown
    description: "The governance model: roles, decision rights, certified vs. sandbox tiers, change management."
  - name: semantic_layer_design
    type: markdown
    description: Where the semantic layer lives, what it owns, and how it interfaces with the BI tool.
  - name: content_organization
    type: markdown
    description: Collection hierarchy, naming conventions, ownership tagging, and access patterns.
  - name: training_and_enablement
    type: markdown
    description: Cohort-based training plan, role-specific curricula, and ongoing enablement rituals.
  - name: audit_and_deprecation
    type: markdown
    description: Quarterly audit cadence, usage-based deprecation rules, and the retirement workflow.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when an organization is about to deploy, re-deploy, or substantially overhaul a self-service business-intelligence platform and needs a methodology — not a feature comparison — for how to do it well. Typical situations:

- The data team has chosen a tool and now must roll it out to several hundred or several thousand non-analyst users.
- An existing deployment has accumulated thousands of charts and dashboards, most unused, and leadership wants a reset without a full re-platform.
- A new modeling layer (warehouse-resident transformations, a metrics layer, or a headless semantic layer) is being introduced and the BI tool's role must be redefined around it.
- A regulated business needs a defensible audit trail of which numbers are official, who owns them, and how they change.
- An acquisition or merger is bringing two analytics estates into one and a governance design must precede technical merging.

Do not invoke this skill to pick a tool — that is a vendor-evaluation problem with different inputs. Do not invoke it for single-dashboard design (use a dashboard-architect skill). Do not invoke it for embedded analytics in a customer-facing product (use the embedded-analytics-architect skill).

## How to apply

The methodology treats a BI rollout as a sociotechnical change, not a software deployment. The hardest decisions are about who owns what, what "official" means, and how content earns and loses trust over time. Skip those decisions and the platform will accumulate the same chaos the user is trying to escape.

### 1. Establish the operating model before touching the tool

1. **Name the operating model out loud.** Centralized, decentralized, or hub-and-spoke. Centralized means one team produces all analytics and consumers read it. Decentralized means every domain produces its own. Hub-and-spoke means a central team owns shared infrastructure, definitions, and certified content, while domain analysts produce most consumer-facing content. Most successful rollouts at non-trivial scale converge on hub-and-spoke; name it explicitly so subsequent decisions follow.
2. **Identify the four populations.** Stewards (own definitions and certify content), Builders (create dashboards and explorations), Readers (consume), and Embedders (place analytics inside other surfaces). Estimate counts for each. The ratio between Builders and Readers drives nearly every downstream decision; a ratio above 1:20 indicates the tool is being used as a report-writer, not a self-service platform.
3. **Map domains to stewards.** Every metric and every certified dashboard must trace to a named human owner in a named domain. Anonymous ownership is the failure mode. List domains (revenue, product, marketing, finance, ops, people) and pick one steward per domain who is empowered to certify and deprecate.
4. **Set decision rights.** Who can create a metric? Who can certify it? Who can change a certified definition? Who can deprecate it? Write these decisions down before the tool is provisioned. Without decision rights, the loudest stakeholder wins every disagreement and definitions drift.
5. **Pick a default failure mode.** When two groups need slightly different versions of the "same" metric, what wins — one canonical metric and a documented dispute, or two metrics with prefixed names? Either policy can work; not picking guarantees both will spawn.

### 2. Place the semantic layer

6. **Decide where business logic lives.** Three plausible homes: warehouse-resident transformations (modeling-tool models with documented metrics), a headless semantic layer that sits between the warehouse and the tool, or the BI tool's own modeling layer. Each is defensible; the wrong move is to spread the same logic across all three.
7. **Prefer warehouse-resident transformations when the consumer set is broader than one tool.** If the same metric must serve a dashboard, a reverse-ETL syncing audience back to a marketing platform, and an embedded view, putting the logic upstream of all three avoids duplicate definitions.
8. **Prefer a tool-native modeling layer when the audience is overwhelmingly single-tool and the modeling team wants tight coupling between definitions and exploration.** This trades portability for iteration speed.
9. **Reserve a headless semantic layer for the case where multiple consumer surfaces need governed metrics and the upstream warehouse cannot easily serve them all.** A semantic layer adds an extra service to operate; only adopt it when the second consumer is real, not speculative.
10. **Pin one definition per metric, however the layer is shaped.** A metric defined once, exposed through the layer, surfaced everywhere. If the user is currently in a "every dashboard recalculates revenue its own way" situation, fixing this is the most valuable single act of the rollout.
11. **Document the definition adjacent to the code.** Description, owner, formula in plain language, refresh cadence, known caveats. The documentation must be readable by a non-analyst stakeholder, because they are the ones who will challenge the number.

### 3. Tier content explicitly

12. **Define three content tiers.** Certified, Working, and Personal. Certified content has a named steward, passes the documentation bar, is on the audit cadence, and is the answer the organization stands behind. Working content is shared but unofficial — useful for a team but not load-bearing. Personal content is the user's sandbox and is invisible to others by default.
13. **Apply visual cues to the tier.** A badge, an icon, a banner — whatever the tool supports. A reader must be able to tell at a glance whether the number is the official one. Untagged content reads as if it were certified; that is the default failure mode.
14. **Reserve the top of search results, the home page, and shared links for certified content.** Working and personal content is reachable but not promoted. Without this, the most recently created dashboard wins discovery regardless of quality.
15. **Set promotion criteria from Working to Certified.** Typically: a steward owner, a populated description, a clearly named source, a passing freshness check, and at least one user beyond the author. Resist letting "well, lots of people use it" become a promotion path; usage and correctness are different signals.
16. **Set demotion criteria.** When does Certified become Working again? Usually: steward leaves, definition changes without re-certification, freshness goes stale for more than a defined window, or an upstream source is deprecated. Without demotion criteria the certified set ossifies and gradually loses meaning.

### 4. Organize the content namespace

17. **Pick a hierarchy and use it consistently.** Two patterns dominate: by-domain (one top-level folder per business domain) or by-audience (one top-level folder per consumer group, with domain folders nested below). By-domain is usually better for stewardship; by-audience is better when consumer groups are stable and rarely cross domains.
18. **Cap the depth at three levels.** Beyond three levels the tree becomes a maze. If a fourth level is tempting, the second level is probably too broad.
19. **Name folders by stable nouns, not by initiatives.** "Revenue" survives reorgs; "FY24 Annual Plan" does not. Time-bound work lives inside the stable folder.
20. **Reserve a top-level "Certified" or "Official" surface that aggregates certified content across domains.** Readers who don't know where to look should arrive there first.
21. **Give every Builder a personal space by default.** Without a sandbox, they will put exploratory work in shared folders and pollute the namespace.
22. **Forbid empty folders and orphan content.** A monthly audit run by the platform team removes both; an empty folder is dead weight, and orphan content (no owner, no folder) is the seed of future chaos.

### 5. Set access and security

23. **Grant access by group, never by individual.** Individual grants create an audit nightmare and accumulate as people change roles. Groups (sourced from the identity provider when possible) are the only sustainable unit.
24. **Apply least privilege to data, not just to dashboards.** Row-level rules at the source are stronger than per-dashboard rules in the tool; a Builder who can query the source can always reconstruct the row-filtered data otherwise.
25. **Define a public-by-default or private-by-default stance and stick to it.** Public-by-default suits low-sensitivity environments and accelerates sharing; private-by-default suits regulated environments. Mixing the two confuses users.
26. **Audit privileged groups every quarter.** Stewards, admins, and anyone with write access to the modeling layer. People accrete privileges and rarely shed them voluntarily.
27. **Distinguish "can read the dashboard" from "can see the underlying rows."** Many platforms confuse these; design and document the answer explicitly so it doesn't surprise an auditor.

### 6. Plan the rollout in waves

28. **Wave 0 — Platform team only.** Stand up the tool, model two or three foundational metrics, build one reference dashboard. Goal: prove the stack works end-to-end before exposing it to anyone else.
29. **Wave 1 — One pilot domain with high motivation.** A domain that has both a clear pain and an analyst champion. Co-build the first 5–10 certified pieces of content with them. Goal: a real success story to point to, plus discovery of operational gaps.
30. **Wave 2 — Two or three adjacent domains.** Replicate the wave-1 pattern. The platform team supports but the domain analysts do most of the building. Goal: prove the support model scales.
31. **Wave 3 — General availability.** Open to the rest of the organization with the support model, documentation, and content library now in place.
32. **Pace the waves on outcomes, not calendar.** Each wave has explicit exit criteria: number of certified pieces of content, training completion rate, dashboards consumed per week, support-ticket trend. Do not advance to the next wave until the prior wave's exit criteria are green.
33. **Run an explicit deprecation track in parallel.** If the rollout is replacing an incumbent, every wave includes a list of incumbent content to retire by the wave's close. Otherwise the new tool becomes the third place dashboards live, not the first.

### 7. Train by role, not in bulk

34. **Build at least three curricula.** Reader (find content, interpret a certified dashboard, request a change), Builder (model a dataset or use the existing semantic layer, build a chart, share, request certification), Steward (definitions, certification process, deprecation, audit duties). A single all-hands training fails everyone.
35. **Train in cohorts of 15–30, not 200.** Hands-on practice with a real question from the cohort's domain is the only kind of training that sticks for Builders. Recorded lectures are reference material, not training.
36. **Have new Builders ship one real piece of certified content as their graduation requirement.** Course-completion certificates correlate poorly with platform adoption; shipped content correlates strongly.
37. **Hold an open office hour weekly during the first quarter and biweekly thereafter.** A standing place for "I tried to build X and got stuck" is more valuable than any document.
38. **Maintain a public, searchable solutions library.** Recipes for common patterns ("how do I compute period-over-period," "how do I filter by a rolling window"). Update it from real questions.
39. **Identify and resource a champion network.** One Builder per domain who attends a monthly platform-team sync. Champions cascade knowledge faster and identify problems earlier than any centralized survey.

### 8. Establish an audit cadence

40. **Quarterly audit, with a written checklist.** Stewards review their certified content: still accurate, still used, still owned, still documented. The platform team runs the same review on platform-level objects (groups, permissions, integrations).
41. **Use usage telemetry, not feelings.** Most tools expose view counts, last-viewed timestamps, and user counts per piece of content. Rank certified content by usage; investigate the long tail.
42. **Set explicit deprecation rules tied to usage.** Example: content untouched for 180 days and viewed by zero unique users in 90 days is auto-archived (not deleted) with a notification to the owner. Archived content is restorable for 90 days, then deleted. Adjust thresholds to taste, but write them down.
43. **Audit definitions, not just dashboards.** A drifted metric definition silently breaks every chart that depends on it. The steward owns proving the definition is unchanged or documenting the change with a version bump.
44. **Audit the access groups.** People leave teams and accrete groups. Quarterly review trims this. Without it, an ex-finance analyst still sees finance data three roles later.
45. **Publish the audit results.** Internal transparency about what passed, what was deprecated, and what is pending review builds trust faster than any marketing.

### 9. Define the support model

46. **Three tiers of support.** Self-service (docs, solutions library, search), peer (champion network, shared channel for questions), and platform team (escalation for bugs, missing data, modeling-layer changes). Users always try the first two before the third.
47. **Funnel all platform-team requests through a single channel.** A shared queue with explicit ticket types. Direct messages to the platform engineer are a load-balancing failure that burns out the team.
48. **Tag tickets by category.** Definition disagreement, missing data, performance, bug, training. The category distribution tells the platform team where to invest next.
49. **Define a service-level expectation, even if internal.** "Critical (production dashboard broken): 1 business day. Standard: 5 business days. Enhancement: triaged monthly." Setting and meeting expectations is more important than the absolute speed.
50. **Measure platform-team load.** Tickets per week, time to first response, time to resolution. If the trend is up and to the right after wave 3, the rollout is creating dependence the team cannot sustain; redirect investment into self-service.

### 10. Compose the deliverable

51. **Lead with the operating-model decision.** Centralized, decentralized, or hub-and-spoke, with rationale tied to the user's organization profile.
52. **State the semantic-layer placement.** Where business logic lives, who owns it, how the BI tool consumes it.
53. **Specify the content tiers and visual cues.** Certified, Working, Personal — with promotion and demotion rules.
54. **Sketch the namespace.** Top-level structure, depth, and a sample populated outline using the user's actual domains.
55. **Sketch the access model.** Group structure, default privacy stance, row-level rules at the source, audit cadence.
56. **Lay out the rollout waves.** Wave by wave, with exit criteria and the deprecation track running in parallel.
57. **Sketch the training and enablement plan.** Curricula by role, cohort size, graduation requirement, office hours, champion network.
58. **Sketch the audit and deprecation cadence.** Quarterly checklist, usage thresholds, archive-then-delete workflow.
59. **Sketch the support model.** Three tiers, single intake channel, ticket taxonomy, service expectation.
60. **Surface assumptions explicitly.** If the user did not state regulatory regime, ratio of Builders to Readers, or whether an incumbent tool exists, name the assumptions made.

### 11. Self-check before responding

61. **Confirm every certified piece of content traces to a named human.** No anonymous stewardship.
62. **Confirm one definition per metric.** If the design tolerates duplicate definitions, the rollout has failed before it began.
63. **Confirm the rollout has a deprecation track.** Otherwise the new tool joins the old; it does not replace it.
64. **Confirm the audit cadence is calendarized, not aspirational.** A quarterly audit with no owner does not happen.
65. **Confirm the plan addresses the user's actual organization profile** — headcount, regulatory regime, current pain points — and is not generic.

## Inputs

- Organization profile: headcount, departments, regulatory regime, data culture.
- Current state: incumbent tool, warehouse layout, modeling stack, pain points, content volume.
- Target outcomes: decisions enabled, audiences served, constraints.
- Optional: tool category, modeling stack, downtime budget for migration.

## Outputs

- Phased rollout plan with wave-level exit criteria.
- Governance model with roles, tiers, decision rights.
- Semantic-layer placement and ownership.
- Content namespace with naming and depth rules.
- Training plan by role with graduation requirements.
- Audit and deprecation cadence with usage thresholds.
- Support-model design with tiers, intake, and service expectations.

## Examples

**Example invocation**

> "We are deploying a self-service BI tool to ~800 employees across product, revenue, finance, and people. We have dbt models in a cloud warehouse but no formal semantic layer. There is an incumbent reporting tool with ~1,200 dashboards, most untouched. The data team is six people. Target: every leader can self-serve their weekly metrics within two quarters."

**Expected high-level output**

Operating model: hub-and-spoke. The data team owns the modeling layer, the platform, and certification. Each domain (product, revenue, finance, people) gets one named steward — a senior analyst embedded in the domain — empowered to certify and deprecate.

Semantic layer: warehouse-resident, expressed in the existing modeling tool. Every certified metric has a definition, an owner, and a description in the model code. The BI tool consumes these definitions; it does not redefine them. A small set of presentation-layer transforms (formatting, locale) is acceptable inside the tool.

Content tiers: Certified (badge, top of search), Working (visible to a group), Personal (sandbox). Promotion requires steward, description, freshness check; demotion triggers on steward departure or 90-day staleness.

Namespace: by-domain, three levels max. Top level: Revenue, Product, Finance, People, Cross-Functional, Certified. Each domain has subfolders for Operational, Strategic, and Working. Personal sandboxes live under each Builder's user space.

Access: groups synced from the identity provider. Row-level rules implemented at the warehouse. Private-by-default. Quarterly access-group audit.

Rollout: Wave 0 (data team, 2 weeks): stack stood up, 5 certified metrics modeled, 1 reference dashboard. Wave 1 (revenue, 6 weeks): 10 certified pieces of content co-built with the revenue steward. Wave 2 (product + finance, 8 weeks): same pattern in parallel. Wave 3 (general availability + people, 6 weeks): full launch with training waves. Deprecation: target retirement of 600 of 1,200 incumbent dashboards by end of Wave 2; second tranche of 400 by end of Wave 3.

Training: three curricula (Reader, Builder, Steward). Cohorts of 20. Builder graduation = one shipped certified piece of content. Weekly office hours during waves 1–3. Champion network of 8 (two per domain).

Audit: quarterly. Usage-based deprecation: 180 days untouched + zero unique viewers in 90 days = auto-archive with owner notification. Restorable for 90 days, then deleted.

Support: three tiers, single intake channel, ticket taxonomy, 5-business-day standard service expectation.

## Limitations

- The methodology assumes a non-trivial scale (hundreds to thousands of users). For teams under 50 users the overhead of the governance design is too high; a lighter operating model is appropriate.
- It does not pick a specific tool. Tool choice changes implementation detail but not the methodology.
- It assumes a warehouse or lakehouse exists. Organizations still serving analytics from production OLTP have prerequisite work this skill does not address.
- It does not address embedded analytics (analytics surfaced inside a customer-facing product). That is a different design problem; use the embedded-analytics-architect skill.
- Regulatory specifics (HIPAA, PCI, regulated industries) require additional controls that this skill flags but does not exhaustively enumerate.

## Sources reviewed

The methodology synthesized here draws on patterns observed across the following projects and public documentation. License tags reflect each project's stated terms at the time of review. No prose, code, configuration, or branded terminology is derived from any single source; the design vocabulary above is generic.

- https://github.com/metabase/metabase — AGPL-3.0 (community) + proprietary (commercial). Read only; cited for governance and content-organization patterns.
- https://github.com/apache/superset — Apache-2.0. Read; cited for role-based-access, dataset-certification, and dashboard organization patterns.
- https://github.com/lightdash/lightdash — MIT (most code) + proprietary enterprise modules. Read; cited for modeling-layer-coupled-to-warehouse-transformations patterns.
- https://github.com/cube-js/cube — Apache-2.0 (backend) + MIT (client). Read; cited for headless-semantic-layer patterns.
- LookML documentation (Google Cloud, proprietary). Read only; cited for explore/view/derived-table layering concepts, expressed generically.
- https://github.com/dbt-labs/dbt-core — Apache-2.0. Read; cited for in-warehouse modeling-layer patterns.
