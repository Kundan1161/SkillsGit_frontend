---
id: skillsgit-curated/internal-linking-strategy-designer
version: 1.0.0
name: Internal Linking Strategy Designer
description: Design internal linking at scale — link equity flow, anchor diversity, contextual relevance scoring, automation guardrails, audit cadence, and broken-link recovery — as an executable strategy not a one-time cleanup.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [niche:programmatic-seo, internal-linking, link-equity, anchor-text, link-graph, automation, content-architecture, audit]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: [web_search, code_execution]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - internal linking
  - link graph
  - anchor text
  - link equity
  - pagerank distribution
  - orphan pages
  - linking strategy
  - link audit
  - broken links
  - link rot
  - hub linking
  - contextual links
  - automated internal links
  - link velocity
example_invocations:
  - "Design an internal linking strategy for our 8,000-page site."
  - "We have a programmatic engine with no link graph — design one."
  - "Audit the linking on our knowledge base — too many orphans and weak hubs."
  - "How should we automate internal links without anchor-stuffing penalties?"
  - "Plan an internal-link recovery after a site migration broke half the inbound URLs."
inputs:
  - name: site_overview
    type: text
    required: true
    description: One paragraph on the site — page count, primary page types (blog, product, category, programmatic, docs), stack, and current rough state of internal linking.
  - name: business_priority
    type: text
    required: false
    description: Which page types or sections should receive the most link equity (e.g., "category pages drive transactions; the blog drives discovery").
  - name: current_problem
    type: text
    required: false
    description: The specific symptom that triggered this work — orphan pages, ranking stagnation, post-migration link rot, programmatic engine without structure, or general overhaul.
  - name: automation_level
    type: choice
    required: false
    description: How much link insertion can be automated. Manual (editorial only), Hybrid (automation suggests, editor approves), or Automated (rules-driven insertion with guardrails).
    choices: [manual, hybrid, automated]
  - name: scale
    type: choice
    required: false
    description: Approximate page count. Affects whether the strategy can be hand-curated or must be rule-driven.
    choices: [under-500, 500-5k, 5k-50k, 50k-plus]
outputs:
  - name: linking_strategy
    type: markdown
    description: The full strategy — equity flow design, hub structure, anchor-text policy, automation rules and guardrails, audit cadence, and broken-link recovery protocol.
  - name: rule_set
    type: markdown
    description: Concrete linking rules engineering or editors can apply — when to link, what to anchor with, how many outbound links per page, and what never to link.
  - name: audit_playbook
    type: markdown
    description: Reusable audit playbook with the seven checks to run on every cadence, the metrics to report, and the threshold-to-action mapping.
  - name: linking_spec
    type: json
    description: Machine-readable rule set and audit schedule for engineering import.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Internal Linking Strategy Designer

## When to use

Use this skill when a user needs to design or repair internal linking as an ongoing system, not as a one-time cleanup. Concrete triggers:

- A new content engine or programmatic build needs a link graph designed from the start.
- An existing site has accumulated thousands of pages with little or no structural linking, and the team wants a coherent plan rather than a Friday-afternoon batch.
- A migration, replatform, or category restructure has broken the link graph and traffic has dropped.
- A team has noticed orphan pages, weak hubs, anchor-text repetition, or rankings stuck at page two on pages with good external links — all symptoms of a broken internal graph.
- The team wants to automate link insertion at scale and needs guardrails to avoid anchor-stuffing or pattern-detection penalties.

Do not invoke this skill for the broader question of "how should our content be organized" (use Topic Cluster Architect), for individual SEO bugs on specific pages (use SEO Site Audit Pro), or for keyword and competitor questions (use Keyword Cluster Builder and Content Gap Hunter). This skill assumes the content architecture is settled and focuses on how the pages connect.

The skill is opinionated about one principle: internal linking is a function of the site, not a project. A strategy that requires a quarterly team scramble to "fix the links again" is failing. The output is therefore weighted toward rule design, automation guardrails, and recurring audits — not a one-time list of links to add.

## How to apply

The strategy proceeds in eleven phases. The first three diagnose the current state and set the equity priorities. The middle four design the structure, anchor policy, and automation rules. The last four make the strategy operational with audits, broken-link handling, and ownership.

### Phase 1 — Inventory and current-state diagnosis

1. **Bucket pages by type and role.** A site is not a single graph; it is a graph of graphs. Categorize every page by its content type (blog post, category, product, programmatic page, docs page, landing page, legal) and by its role in the funnel (awareness, consideration, decision, support). The linking rules differ by both axes.

2. **Map the existing graph at a sample.** Pull or estimate the existing internal-link graph for a representative sample of each page type. For each sampled page, note the inbound link count from internal pages, the outbound link count to internal pages, and the depth from the homepage. These three numbers describe the page's structural position.

3. **Identify the four common pathologies.** Look for (a) orphan pages with zero internal inbound links, (b) dead-end pages with zero internal outbound links to value pages, (c) over-linked hubs that exceed roughly 150 outbound internal links per page from primary navigation alone, and (d) weak hubs whose subordinate pages receive more aggregate inbound linking than the hub itself. Each pathology calls for a distinct fix; do not lump them together.

### Phase 2 — Equity-flow priorities

4. **Name the equity destinations.** Within each page type, identify the pages that the business needs to win — typically a small fraction of category, comparison, product, or pillar pages. The strategy directs internal link equity toward those destinations.

5. **Bound the destination list.** A site that lists every page as a priority destination has set no priorities. A reasonable rule of thumb is that priority destinations comprise 5–15% of indexable pages. If the list is longer, force a ranking; the bottom of the list is "supports the destinations above" not "destination."

6. **Decide whether the homepage is a hub or an entry point.** A homepage is structurally a hub only if it links into the category layer with weight. Many homepages are entry points (link prominently to product or brand pages but not into category/blog depth) and should be treated as such, with the equity hubbing happening one level down.

### Phase 3 — Hub design

7. **Establish a hub for every page-type cluster.** Each meaningful cluster of pages needs an addressable hub: a category page over its products, a pillar page over its cluster posts, a directory page over its directory entries, a sub-pillar over its sub-cluster. Pages that do not have an obvious hub are orphans waiting to happen.

8. **Bound link-graph depth from the homepage.** Every indexable priority page should be reachable from the homepage in three hops or fewer. Long-tail and archival pages can sit at four or five hops, but the priority destinations must be shallow. Excess depth is a sign that an intermediate hub is missing.

9. **Design hub pages as more than navigation.** A hub page that is purely a list of links is structurally a category template, but if there is no editorial content above the list, the hub itself rarely accumulates external links. Add an introductory section, a useful framework, or a curated overview to the hub so that it can attract inbound links of its own — equity it then redistributes to its spokes.

10. **Cap outbound links per hub.** A hub with 600 outbound links to its spokes dilutes weight across all of them. Where the spoke set is large, paginate or sub-cluster the hub so any one hub page exposes only the spokes it can meaningfully boost.

### Phase 4 — Contextual linking rules

11. **Define the unit of a contextual link.** A contextual link is a link inside the body content of a page from prose that names the target's topic. Navigation links, footer links, and sidebar links are not contextual; they are structural. Both kinds count, but contextual links carry more weight per link and merit the design attention.

12. **Establish a contextual relevance score.** For each candidate link, the source page and the target page should share enough topical overlap that the link makes sense to a reader. A simple scoring heuristic combines (a) keyword overlap between the link's surrounding paragraph and the target's H1, (b) co-occurrence of the same primary entities, and (c) intent alignment (a transactional target from a transactional context, an informational target from informational context). The strategy specifies the score threshold below which a candidate link should not be inserted.

13. **Cap contextual outbound links per body page.** A long-form post can comfortably carry 4–8 contextual internal links; a short post 1–3; a programmatic page 2–6 depending on body length. Excess linking flattens the signal of any one link.

14. **Forbid linking to thin or empty pages.** A linking rule that points contextual links at "noindex" templates, empty category pages, or under-development pages spreads quality damage outward. The strategy explicitly forbids these targets at the rule layer.

### Phase 5 — Anchor-text policy

15. **Define the anchor-text variant set.** For each linking destination, define a small set (typically two to five) of anchor variants drawn from the target's H1, primary entities, and natural language references. Variants should sound like phrases a reader would write organically, not keyword stems.

16. **Set an anchor-distribution target per destination.** A page receiving 50 inbound contextual links from 50 anchor instances should not have 45 of them be the exact same keyword phrase. A defensible distribution mixes exact-match anchors (typically 10–25% of inbound), partial-match anchors (30–50%), branded or generic anchors (10–25%), and naked-URL or image anchors (small percentage). These are heuristic targets; the strategy specifies them and the audit later checks them.

17. **Forbid sitewide footer-link stuffing.** A sitewide footer link to a money page with exact-match anchor sends a pattern signal that has been a documented penalty trigger. The strategy explicitly excludes this pattern. Footer links should be navigational and use natural anchors.

18. **Treat image alt text as anchor text.** When a page links to an internal destination through an image, the alt text functions as the anchor. The anchor-distribution targets apply equally. Pages that link from many decorative images with empty alt and many text links with exact-match anchor combine the worst of both signals.

### Phase 6 — Automation and guardrails

19. **Decide what is automatable.** Three categories of internal link can be automated safely: (a) hub-to-spoke links inside templated sections, (b) sibling-recommendation widgets driven by content similarity, and (c) "see also" suggestions appended below body content. Inline body links — links inserted into existing prose — are riskier to automate; they reward editorial review.

20. **Specify the matching function.** Automation needs a deterministic rule for what to link. Examples that work: nearest-neighbor by an entity overlap or embedding similarity above a threshold, top-N most-trafficked siblings within the same cluster, hand-curated link tables stored as data. Examples that do not: random selection, alphabetical order, last-published order. Specify the function and the data inputs.

21. **Set anchor-variant rotation.** Even an automated module should rotate anchor variants per insertion. Specify the rule: pick the variant whose form factor matches the target's H1 modulo small phrasal variations, rotate by hash of the source URL, do not repeat the same anchor within the same paragraph.

22. **Set automation guardrails that block insertion.** No automated insertion should fire if the resulting page would (a) exceed the cap on internal outbound links, (b) cross into a forbidden target type, (c) repeat the same anchor more than once on the same page, (d) place the link inside an existing link, (e) introduce a self-link, or (f) match a partial-word pattern that fragments the surrounding sentence. The strategy lists these guardrails explicitly.

23. **Log every automated insertion.** Every automation event records the source page, target page, anchor used, matcher score, and timestamp. Without this log, audits cannot distinguish editorial links from automated ones, and rollback after a quality regression is guesswork.

### Phase 7 — Linking velocity and rate

24. **Avoid mass insertions to a single destination.** A money page that accumulates 800 inbound internal links overnight from an automated batch produces a pattern that is detectable and unhelpful. Spread automated insertion over time, prefer linking when new content is produced, and target a steady velocity rather than a one-time fill.

25. **Tie insertions to content events.** Insertion is best triggered by content events — a new page published, a refresh detected, a category-change event — rather than by a linking-coverage goal. A coverage goal motivates a batch; an event-trigger produces a steady stream.

### Phase 8 — Broken-link and link-rot recovery

26. **Distinguish three broken-link classes.** A broken internal link can be (a) a hard 404 — the target no longer exists at all, (b) a 301 chain — the target moved and the link still points at the original, or (c) a soft 404 — the target returns 200 but is now empty or `noindex`. Each class has a different fix.

27. **Fix at the source, not at the redirect.** A 301 redirect is a patch, not a fix. Inbound links to a moved page should be updated to point at the new URL. Long redirect chains accumulate over time and dilute crawl efficiency. The audit identifies redirect chains; the strategy updates source links.

28. **Plan migration link-rot recovery explicitly.** After any URL change at scale (replatform, category rename, slug normalization), schedule a directed audit within two weeks of cutover. Pull a sample of internal links, identify the broken or redirected ones, and update them in place. Without this, a migration's link rot compounds and undermines the new architecture.

29. **Handle retired content with intent.** When a page is retired, decide whether inbound internal links should be rewritten to point at a replacement page or removed entirely. Leaving them pointing at a 410 is the worst option — it teaches no one anything and burns crawl on broken edges.

### Phase 9 — Audit cadence and playbook

30. **Define a recurring audit checklist.** A defensible audit cadence runs once a quarter for small sites, once a month for fast-changing sites, and continuously for large programmatic engines. The audit always checks: orphan count, dead-end count, average inbound contextual links per priority page, anchor-distribution by destination, broken-link rate, redirect-chain count, average depth from homepage, and the share of priority pages above their inbound-link target.

31. **Report against thresholds, not snapshots.** A "report" that lists "12 orphans" without a threshold is undirected. The strategy sets a target threshold per metric (e.g., orphan rate below 1% of indexable pages, broken-link rate below 0.5% of internal links) and the audit reports each metric against its threshold.

32. **Assign each threshold breach a named action.** Breaching the orphan-rate threshold triggers a re-link batch. Breaching the broken-link threshold triggers a source-side fix sweep. Breaching the anchor-concentration threshold triggers a rotation review. Without named actions, the audit becomes a report that no one acts on.

### Phase 10 — Measurement and decline detection

33. **Measure equity flow as the priority-page-coverage metric.** The headline metric of an internal-linking program is not "number of internal links." It is the share of priority destinations that receive at least the target inbound contextual link count from relevant siblings. Track that share over time.

34. **Detect link-graph regression early.** A sudden uptick in orphans, a drop in average depth, or a redirect-chain spike usually signals an upstream change — a template refactor, a CMS update, a migration. Connect the audit metrics to a regression alert; do not wait for ranking signals to surface the structural cause.

35. **Connect linking metrics to organic metrics with care.** Internal linking changes show up in rankings on the order of weeks, not days. Avoid attributing every weekly traffic move to the linking work; report monthly trend for the priority pages against the baseline cohort.

### Phase 11 — Ownership and operating model

36. **Name owners by surface.** Editorial owns inline body links and anchor choices in new content. Engineering owns navigation, hub templates, and automation modules. SEO owns the rules, the priority list, and the audit cadence. Without explicit ownership, the linking strategy decays into the last surface anyone touched.

37. **Build a change-review checkpoint for templates.** Any template change — new sidebar, new related-posts module, hub-page redesign, breadcrumb refactor — touches the link graph at scale and must pass through an SEO review. The strategy names the artifact (a brief documenting the before/after edge counts and anchor patterns) and the threshold at which template changes require it.

38. **Document the strategy where it can be referenced.** A linking strategy that lives in a slide deck no one opens decays in months. The strategy should be a single living document, referenced from the engineering wiki, the editorial style guide, and the CMS authoring UI's help text. Names, links, and a date.

## Inputs

- **site_overview** (required): The site's shape — page count, page types, stack, current state of internal linking. Without this the strategy defaults to generic best practice.
- **business_priority** (recommended): Which sections should receive equity. Sharpens the priority-destinations list.
- **current_problem** (recommended): The triggering symptom. Used to weight the strategy toward the failure mode that prompted the work.
- **automation_level** (optional): How aggressive automation can be. Default is Hybrid.
- **scale** (optional): Approximate page count. Affects whether hand-curation is feasible.

## Outputs

The skill produces four artifacts.

1. **Linking strategy** — the full document covering equity flow, hub structure, anchor policy, automation rules and guardrails, audit cadence, broken-link recovery, and ownership.
2. **Rule set** — the concrete linking rules suitable for direct application by editors and engineers.
3. **Audit playbook** — the recurring audit definition with metrics, thresholds, and threshold-to-action mapping.
4. **Linking spec JSON** — machine-readable rule set and audit schedule for engineering.

## Examples

**Example 1: SaaS blog plus product site, post-migration**

Input: site_overview describes a 1,400-page site with a blog (900 posts), product pages (40), and a knowledge base (450 articles). Current problem is that a recent slug normalization created a 31% inbound-link redirect rate and rankings have flattened. The skill returns a strategy that prioritizes the 14 product pages and 30 pillar posts as equity destinations, defines a hub structure with a top-level product hub and four blog pillars, prescribes a source-side link rewrite pass for the redirect rate, and sets a quarterly audit cadence with the four post-migration metrics elevated as triggers for the next six months.

**Example 2: 25,000-page programmatic real-estate engine**

Input: site_overview describes a directory of cities, neighborhoods, and listings totaling 25,000 indexable pages. Current problem is high orphan rate (estimated 12%) and inconsistent anchor patterns. automation_level is Automated. The skill returns a hybrid hub structure (state hubs over city hubs over neighborhood hubs over listings), an automated nearest-neighbor sibling module with five-variant anchor rotation per destination, guardrails that block insertion above six contextual links per listing page, a depth target of three hops from the homepage to any indexable city, and a monthly audit that elevates orphan rate, near-duplicate cluster size, and redirect-chain count.

## Limitations

- The strategy is only as strong as its enforcement. A team without the ability to enforce template changes through review will see template drift erode the link graph regardless of the policy.
- Anchor-distribution targets are heuristic. The percentages cited reflect commonly-discussed bands rather than precise penalty thresholds; for sites in penalty-prone niches the operator should choose more conservative numbers.
- The skill does not crawl. It produces the strategy and the audit playbook; running the audit requires a crawler, an internal data dump, or a focused crawler skill.
- Automation rules are framework-aware but not framework-specific. The skill notes typical patterns for major stacks but does not write production automation code.
- Link-graph improvements take weeks to surface in rankings, and the noise floor is wide. The measurement plan emphasizes structural metrics first and organic outcomes second.

## Sources reviewed

- https://github.com/devbret/website-internal-links
- https://github.com/eliasdabbas/advertools
- https://github.com/garmeeh/next-seo
- https://github.com/iamvishnusankar/next-sitemap
- https://github.com/harlan-zw/nuxt-seo
- https://github.com/kjvarga/sitemap_generator
- https://github.com/spatie/schema-org
- https://github.com/amplifying-ai/awesome-generative-engine-optimization
