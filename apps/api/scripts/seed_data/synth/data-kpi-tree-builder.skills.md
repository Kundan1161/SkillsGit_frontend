---
id: skillsgit-curated/data-kpi-tree-builder
version: 1.0.0
name: KPI Tree Builder
description: Decomposes a north-star metric into a tree of drivers, sub-drivers, and operational inputs with owners and leverage estimates; turns the tree into a dashboard plan.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:analytics-engineering, kpi-tree, metric-tree, driver-tree, north-star, dashboarding, strategy]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: []
  min_context_tokens: 24000
  estimated_tokens_per_invocation: 6500
trigger_keywords:
  - kpi tree
  - metric tree
  - driver tree
  - north star
  - okr decomposition
  - input metrics
  - leverage analysis
  - dashboard plan
  - lever map
  - causal metric model
  - leading indicator
  - lagging indicator
example_invocations:
  - "Help me decompose ARR into a tree of drivers for the next planning cycle."
  - "Build a KPI tree under 'weekly active users' that the growth team can act on."
  - "Our north star is gross margin — what should the leadership dashboard show under it?"
  - "I have five team OKRs and no idea if they roll up to anything. Give me a tree."
inputs:
  - name: north_star
    type: text
    required: true
    description: The metric at the top of the tree. Phrase it as a complete metric (number, unit, time grain) — "ARR in USD as of month-end" beats "revenue".
  - name: business_context
    type: text
    required: false
    description: What does the company sell, what is the business model (subscription, transactional, marketplace, ads), and what stage (early growth, scale, mature). Two-paragraph overview is enough.
  - name: known_drivers
    type: text
    required: false
    description: Drivers the team already believes matter. Useful for grounding the tree in vocabulary the team uses, even if some are wrong.
  - name: team_map
    type: text
    required: false
    description: A list of teams and their charters. Lets the skill suggest credible owners for each branch.
  - name: depth
    type: choice
    required: false
    description: How deep to push the tree. Default is 3-level (north star, drivers, sub-drivers).
    choices: [2-level, 3-level, 4-level]
outputs:
  - name: kpi_tree
    type: markdown
    description: An indented tree of metrics from north star down to operational inputs, with the type, owner, leverage estimate, and a one-line definition for each node.
  - name: tree_diagnostics
    type: markdown
    description: Notes on the tree — branches that are weak (unowned, unmeasurable, irrelevant) and branches that are missing.
  - name: dashboard_plan
    type: markdown
    description: A proposed dashboard layout for the executive consumer of the tree — 5 to 9 tiles, organized by branch, with explicit commentary slots.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a team has a single, important metric at the top — usually called the north star, the company KPI, the leading indicator, or the OKR target — and needs to know what to actually do to move it. Specifically:

- A founder or executive wants to set quarterly priorities and only has the top-line number.
- A growth, product, or revenue team is trying to align on which inputs to invest in.
- OKRs are being written and the connection between team objectives and company outcomes is unclear.
- A board pack needs a "drivers" page that explains why the top number moved.
- A dashboard is being built and the team needs to decide which 5-9 tiles belong on the executive view versus the operating view.

Do not use this skill to define a single metric — pair it with the metric definition designer for that. Do not use it to set targets or write OKRs themselves; the tree describes structure, not goals.

## How to apply

The output is two artifacts: an indented metric tree and a dashboard plan that consumes the tree. The tree comes first; the dashboard is downstream.

### 1. Sharpen the north star

1. **Restate the north star as a fully-specified metric.** Number, unit, grain, time window, filters. If the input is "revenue", reject it; demand "net new ARR in USD per calendar month, gross of expansion, net of churn and downgrades". Vague tops produce useless trees.
2. **Confirm the north star is actually a north star.** A north star is a lagging outcome that the company exists to move, that customers indirectly pay for, and that the team can influence within a planning cycle. A tree under "share price" is mostly noise; a tree under "weekly active users" is mostly signal. Push back if the input is the wrong altitude.
3. **State the time horizon.** A tree for next quarter, next year, and next five years all look different. The horizon controls how many levels of leading indicators belong below the north star.
4. **Capture the current value and the target.** "We are at 8M, we want 12M in 12 months." This grounds leverage estimates that come later — a sub-driver that can move the north star by 0.1% is uninteresting against a 50% gap.

### 2. Decompose into types of input

Every node below the north star is one of four flavors. Decide which flavor by inspection, not by template.

5. **Arithmetic decomposition.** The north star equals a product or sum of its children. ARR = customers x ARPU. Sessions = users x sessions-per-user. Revenue = traffic x conversion x AOV. This is the cleanest decomposition; use it whenever the math holds.
6. **Funnel decomposition.** The north star is the output of a sequential process. Signups → activations → retained → paying. Each stage produces a conversion rate and a volume. Funnels appear under almost every growth tree.
7. **Segment decomposition.** The north star is the sum of contributions from distinct populations. Revenue from SMB plus Mid-Market plus Enterprise. Useful when the segments behave differently enough that one number obscures the story.
8. **Driver decomposition.** The child is not arithmetically connected, but a measurable input that the team believes causes the parent. Quality scores, NPS, support ticket rate. Driver branches are softer than arithmetic ones and require evidence that the causation exists.
9. **Mix decompositions across levels.** A common shape: arithmetic at level 2 (customers x ARPU), funnel under "customers" (lead → trial → paid), driver under "lead" (organic traffic, paid traffic, referral traffic), arithmetic under "paid traffic" (ad spend x CTR x conversion rate / CAC). The tree need not be one type; it should be each child's natural decomposition.

### 3. Build the second level

10. **Decompose the north star into 2-4 children.** Two is too few (one or the other dominates and the tree is barely informative); five is too many (the executive consumer loses the story). Three is canonical.
11. **Validate the second level adds up.** For arithmetic and segment decompositions, the children must sum or multiply to the parent. Inspect the math, do not assume it. A north star of "weekly active users" with children "daily active users" and "monthly active users" is broken — the children are correlated views of the parent, not its components.
12. **Name each child as a complete metric.** Same rigor as the metric definition step: grain, unit, time, exclusions. Trees written in shorthand ("DAU", "CAC", "LTV") rot within a quarter because the implicit definitions drift.
13. **For each child, write a one-sentence rationale** for why it is a child of this parent and not a sibling, not deeper, not absent. "ARPU is a multiplicative driver of ARR via the customer count" is rationale; "ARPU matters" is not.

### 4. Build subsequent levels

14. **Pick the highest-leverage child first and decompose it.** Resist the urge to decompose every branch equally. The tree's purpose is to surface where action happens — the team that owns the biggest branch will produce the deepest sub-tree, and that is correct.
15. **Stop at the level the team can act on.** A sub-driver is "actionable" if a single team can change it within one planning cycle through work they would actually do. "Improve onboarding" is not actionable; "reduce time-to-first-value from 14 minutes to 4 minutes" is.
16. **Allow asymmetric depth.** One branch may be one level deep ("we already know how this works"); another may be four levels deep ("this is where the experimentation happens"). Forcing symmetry produces fake leaves.
17. **Watch the math at each level.** Arithmetic and segment trees must check sum/product at every level. Funnel trees must check conversion rates resolve correctly to the parent. Driver trees do not have to check, but each driver must have a hypothesized direction (positive driver, negative driver) and an order-of-magnitude estimate of impact.

### 5. Assign owners

18. **Every node gets exactly one owning team and one accountable human.** No metric without an owner survives a quarter; unowned nodes are how trees become wallpaper.
19. **The owner is the team that, if asked, "why did this number move", can answer credibly.** If no team can answer, the metric is either missing instrumentation or is a vanity metric. Flag and resolve before publishing the tree.
20. **An owner can own multiple branches; a branch has exactly one owner.** Shared ownership is no ownership.
21. **The owner is not the same as the consumer.** Marketing owns "qualified leads"; sales consumes it. Capture both in the tree node.
22. **For metrics that span team boundaries, assign the team closest to the lever.** Activation rate sits between marketing and product; assign to the team that actually changes the onboarding funnel.

### 6. Estimate leverage

23. **For each node, estimate the potential impact** on the parent over the planning horizon. Use a coarse scale (10x, 3x, 1x relative to typical-quarter movement, or H/M/L). Precision is fake here; rank order is real.
24. **Anchor on history.** If "conversion rate" moved 8% in the best quarter and 1% in the worst, the planning-horizon range is the prior, not a wish.
25. **Multiply leverage by ownership confidence.** A high-leverage metric owned by a team that does not actually have the tools to change it is lower-priority than a medium-leverage metric owned by a team with full control. Flag the gap.
26. **Identify the top-three branches to invest in.** Three is the limit. Trees with eight equally-weighted "priorities" produce zero focus.

### 7. Diagnose the tree

Before publishing, work through this checklist:

27. **Are there any leaves with no instrumentation?** A metric that the data team cannot produce a query for is not yet a tree node — it is a roadmap item. Mark as "to-be-instrumented" with a target date.
28. **Are there any metrics in the tree that are not in the metrics catalog?** New metrics produced for the tree must be defined per the metric-definition discipline before they are published.
29. **Are there siblings that are perfectly correlated?** Two children of the same parent that always move together carry no information independently. Collapse to one.
30. **Are there orphan metrics on existing dashboards that the tree does not include?** Either they are missing from the tree (add) or they are noise (deprecate).
31. **Are any branches purely descriptive rather than causal?** "Stage 1 → stage 2 conversion rate" is descriptive of a funnel and useful; "average customer age" is descriptive of a population and useless as a driver unless someone is acting on it.
32. **Is the tree balanced across leading and lagging?** A tree with only lagging indicators tells you yesterday's score; a tree with only leading indicators is speculative. Aim for a leading-indicator majority at the deepest level (the operational inputs the team controls) and lagging indicators near the top (outcomes that reflect months of effort).
33. **Is the tree understandable to its consumer?** Read it to a person not in the conversation. If they cannot recite the level-2 decomposition after one pass, the labels are too dense.

### 8. Translate the tree into a dashboard

34. **The executive dashboard has 5-9 tiles.** Five is the minimum to tell the story; nine is the maximum a human reads in one glance. The number is fixed by cognitive load, not by what is interesting.
35. **The top tile is the north star at full-screen size.** Current value, target, trend over the relevant period, and a delta-versus-last-period number. Nothing else competes for the top of the page.
36. **The second row is the level-2 children.** Each child gets a tile of identical size and structure. Visual symmetry signals to the reader that these metrics are siblings.
37. **The third row optionally includes the top-leverage level-3 sub-driver per branch.** Only the top one — do not flatten the whole tree onto the dashboard.
38. **Every tile shows trend, not point-in-time.** A number without a sparkline is useless; a number with a 12-week trend tells the story.
39. **Every tile shows the comparison.** Versus prior period, versus target, versus the same period a year ago. Pick one and apply consistently across all tiles.
40. **Reserve commentary slots.** A dashboard with no commentary is a data dump; a dashboard with commentary is a report. Place commentary text below each tile or in a sidebar. The owner writes the commentary weekly; the data refreshes automatically.
41. **Time period selectors on every tile, defaulted to the cadence of the consumer.** Weekly executive review uses week defaults; monthly board pack uses month defaults. Inconsistent defaults make the same tile useful to no one.
42. **One operating dashboard per branch under the executive dashboard.** The executive dashboard is the table of contents; each branch's operating dashboard is the chapter. Link them.
43. **Use the same color and the same chart type for the same metric** wherever it appears across the dashboard set. A KPI that is blue on one screen and orange on another is two KPIs to the consumer.

### 9. Operationalize the tree

44. **Version the tree.** It is a document, not a wall poster. Date every revision, capture who approved it, store it next to the metric definitions in the analytics repo.
45. **Re-review quarterly.** Companies, products, and segments change. The tree that fit Q1 may be the wrong tree by Q3. A planning-cycle review with the executive owner is non-negotiable.
46. **When the tree changes, propagate.** Renamed branches must update the dashboard, the OKR doc, the team charters, and the board pack. Trees that drift from their downstream artifacts produce contradictions.
47. **Track which branches got investment** and which moved. Over time the tree teaches you which leverage estimates were credible and which were aspirational. This is the second-best output of the exercise after the tree itself.
48. **Publish the tree visibly.** A KPI tree that only exists in a private Notion page is half-built. The whole company should be able to find it, point to where their work sits on it, and trace their daily activity up to the north star.

### 10. Anti-patterns to surface

49. **The vanity tree.** Branches that look impressive in a deck but no team owns. Vanity branches die quietly; flag and prune.
50. **The "balanced scorecard" tree.** Four equally-weighted quadrants with no leverage discrimination. Useful for governance, useless for prioritization. Convert to a leveraged tree before publishing.
51. **The acronym tree.** Every node is a three-letter acronym. The result is unreadable. Demand full names; abbreviate only in the dashboard itself.
52. **The "everything matters" tree.** No branch is the most important. This is failure of decomposition. Force the rank order.
53. **The tree without a target.** A tree describes structure; without a target on the north star it cannot describe priorities. Demand the target before publishing.
54. **The tree built top-down then never validated bottom-up.** A reviewer reading from the leaves should be able to say "yes, if these all move, the parent moves". When they cannot, the tree has a logical gap.
55. **The tree borrowed from another company.** Spotify's tree is not your tree. Netflix's tree is not your tree. The structure that works for a marketplace does not work for SaaS. Build from your business model, not from a blog post.

### 11. Output discipline

56. **Indent the tree with leading hyphens or markdown bullets, two spaces per level.** Plain text. Avoid ASCII art; it breaks in every viewer.
57. **Each node line carries five fields:** name, type (arithmetic / funnel / segment / driver), unit and grain, owner, leverage estimate. Anything else goes into a footnote or the metric catalog.
58. **Group diagnostics into "weak branches" and "missing branches".** A reviewer reads diagnostics second; make them scannable.
59. **The dashboard plan is a numbered list of tiles** in display order, each with metric, comparison, trend length, and commentary owner.
60. **End with one paragraph summarizing the three branches the team should invest in next planning cycle.** This is what the executive consumer reads first; lead with the takeaway, not the methodology.

## Inputs

- A north-star metric, fully specified.
- Optional business context.
- Optional known drivers and team map.

## Outputs

- The KPI tree with one node per line and five fields per node.
- Tree diagnostics: weak branches, missing branches, unowned nodes.
- A dashboard plan with 5-9 tiles and commentary slots.
- A "next three" recommendation.

## Examples

**Example 1 — Subscription SaaS north star**

> Input: "Net new ARR in USD per month, gross of expansion, net of churn and downgrades. Currently $1.4M/month, target $2.4M/month within 12 months."
>
> Expected output: Level 2 — new logo ARR (arithmetic from new customers x ACV), expansion ARR (existing customers x net expansion rate), churn ARR (negative; existing customers x gross churn rate x ACV). Level 3 under new logo — pipeline coverage, win rate, deal velocity. Level 3 under expansion — multi-product attach rate, seat-expansion rate, contract uplift at renewal. Level 3 under churn — gross logo churn rate, downgrade rate, save rate. Leverage estimate: expansion is the highest leverage given target gap; new logo is second; churn third because retention is already healthy. Three priorities: invest in expansion playbook (sales-led), seat-expansion in product (product-led), pipeline coverage in marketing.

**Example 2 — Marketplace north star**

> Input: "Weekly gross merchandise volume in USD, currently $8M, target $12M in 6 months."
>
> Expected output: Level 2 — buyer count (segment), AOV (arithmetic), purchase frequency (arithmetic). Level 3 under buyer count — new buyer acquisition (funnel: visit → list → first-purchase), buyer reactivation (funnel: lapsed → email-open → repeat-purchase), buyer retention (cohort survival). Level 3 under AOV — average list price, conversion at high price points, cart-size at checkout. Level 3 under frequency — return-visit rate, push notification open rate, recommendation CTR. Leverage estimate: frequency is the highest leverage at this stage; new buyer acquisition is second; AOV is third because supply mix already saturates demand for the existing inventory.

**Example 3 — Product-led growth north star**

> Input: "Weekly active users, currently 220k, target 500k in 9 months."
>
> Expected output: Level 2 — new user activation (funnel), engaged user retention (cohort), reactivation (segment). Level 3 under activation — sign-up rate (visit → account), aha-moment rate (account → first key action), invitation rate (first key action → second user invited). Level 3 under retention — Day-1 / Day-7 / Day-28 cohort survival. Level 3 under reactivation — email reactivation CTR, push reactivation rate, returning-user value. Diagnostics: activation branch is heavily instrumented; retention branch has a Day-1 number but no Day-28 number — flag for instrumentation. Three priorities: aha-moment optimization, Day-7 retention investigation, invitation flow expansion.

## Limitations

- The tree describes structure, not causation proofs. Drivers in the tree are hypotheses; experiments are how you confirm them.
- Leverage estimates are coarse. Use them for prioritization, not for forecasting.
- A KPI tree is not an OKR system. OKRs require targets, key results, and accountability cadences that the tree does not produce.
- For multi-product, multi-segment, multi-geo companies, one tree is insufficient. Build one tree per business unit and link them via a portfolio tree above.
- The skill cannot validate that the metrics it places in the tree are correctly defined; pair with the metric definition skill.
- Trees built for very early-stage companies (pre-product-market-fit) are speculative. The tree itself is fine; the leverage estimates are guesses until enough data exists.

## Sources reviewed

The patterns and checks above were synthesized across the following permissively licensed projects. No prose was copied or closely paraphrased from any source.

- https://github.com/cube-js/cube
- https://github.com/dbt-labs/metricflow
- https://github.com/lightdash/lightdash
- https://github.com/apache/superset
- https://github.com/evidence-dev/evidence
- https://github.com/Unleash/unleash
- https://github.com/growthbook/growthbook
