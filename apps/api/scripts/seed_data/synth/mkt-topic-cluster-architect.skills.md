---
id: skillsgit-curated/topic-cluster-architect
version: 1.0.0
name: Topic Cluster Architect
description: Design a pillar-and-cluster content architecture — pillar pages, cluster pages, hub linking, search-intent mapping, content gap reuse, and query-fan-out resilience for the AI-search era.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [niche:programmatic-seo, topical-authority, content-clusters, pillar-pages, content-architecture, internal-linking, ai-search]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: [web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8500
trigger_keywords:
  - topic cluster
  - content cluster
  - pillar page
  - topical authority
  - hub and spoke
  - content architecture
  - content hierarchy
  - cluster strategy
  - subtopic mapping
  - query fan out
  - content silo
  - editorial calendar
example_invocations:
  - "Design a pillar-and-cluster architecture for our product category from these 300 keywords."
  - "We have 80 blog posts about CRM but no structure — turn them into a topic cluster."
  - "Build a hub-and-spoke content plan for 'workflow automation' with pillar and sub-pillars."
  - "Map the search intents under our chosen pillar and assign each one a page type."
  - "Audit our existing cluster — what subtopics are missing and which posts should merge?"
inputs:
  - name: pillar_topic
    type: text
    required: true
    description: The broad topic the cluster will own. Should be a noun phrase wide enough to support 20-100 related queries but narrow enough to be defensible.
  - name: business_context
    type: text
    required: false
    description: Product, audience, and which conversions matter. Determines which subtopics get prioritized and what calls to action belong on each page.
  - name: existing_content
    type: text
    required: false
    description: List of URLs already covering pieces of the topic. Used to plan merges, refreshes, and additions instead of starting from zero.
  - name: seed_queries
    type: text
    required: false
    description: Optional list of seed queries the team has identified. The skill expands these into a fuller subtopic map.
  - name: competitor_clusters
    type: text
    required: false
    description: Optional 2-5 competitor URLs covering the same broad topic. Used to benchmark depth and surface format gaps.
  - name: cluster_size
    type: choice
    required: false
    description: Target size of the resulting cluster. Compact (1 pillar + 8-12 clusters), Standard (1 pillar + 15-30 clusters + 2-3 sub-pillars), or Deep (multi-pillar architecture with 50+ pieces).
    choices: [compact, standard, deep]
outputs:
  - name: cluster_architecture
    type: markdown
    description: The full architecture — pillar page brief, sub-pillar briefs (if any), cluster pages with assigned intents and formats, and the linking diagram between them.
  - name: editorial_roadmap
    type: markdown
    description: Sequenced production plan — what to publish first, what to refresh from existing content, what to merge, and the dependencies between pieces.
  - name: query_fanout_map
    type: markdown
    description: For each piece, the family of related queries it should answer, mapped from likely AI-search fan-out behavior so the cluster stays cited as search shifts.
  - name: cluster_data
    type: json
    description: Machine-readable export of the cluster (pages, intents, formats, linking, status) for import into a CMS or content calendar.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Topic Cluster Architect

## When to use

Use this skill when a user needs to convert a broad topic, a pile of keywords, or a sprawling blog into a defensible content architecture organized around topical authority. Concrete triggers:

- A team has chosen a topic to "own" and wants the architecture before they write anything.
- An existing content library has grown chaotic, with overlapping posts, dead-end pages, and no clear hub. The team wants a cluster plan that organizes what exists and names what is missing.
- A product launch needs an SEO foundation, and the team understands that one good page is rarely enough.
- The strategy needs to be re-aligned for AI-driven search, where ranking is a function of being cited inside synthesized answers rather than being the top blue link.
- A new vertical or geographic market needs a topical-authority plan from scratch.

Do not invoke this skill when the question is "which individual keywords should we target" (use Keyword Cluster Builder) or "what specific pages should we add that competitors have and we don't" (use Content Gap Hunter) or "how should our internal-link graph work mechanically" (use Internal Linking Strategy Designer). This skill assembles those inputs into an architecture.

The skill is opinionated about one principle: a topic cluster wins by being *the* resource on a topic for one identifiable audience, not by being *a* resource that is slightly different. Every output is shaped by that. If the user wants a "competitive" content plan that produces parity coverage with three named competitors, the skill flags that as a content-gap exercise and recommends switching skills.

## How to apply

The architecture proceeds in ten phases. The first four scope the territory; the next four shape the structure; the last two prepare for production and for the AI-search context the cluster will compete in.

### Phase 1 — Pillar legitimacy check

1. **Test the pillar topic for the three legitimacy criteria.** A defensible pillar topic must (a) describe a broad, durable question or job, not a feature or a brand term; (b) be specific enough that the operating company has, or can credibly build, more knowledge about it than the average competitor; and (c) have a recognizable audience whose questions the pillar exists to answer. If any of the three fails, narrow or pivot before continuing.

2. **State the pillar promise in one sentence.** The promise is "A reader who lands on the pillar page should leave able to do X." Write it down. Every cluster decision later is judged against this promise.

3. **Verify topical demand.** Without paid tools, sample fifteen queries that a person interested in the pillar would search. Run them and read the SERP for each. If most surface the same five aggregator sites with no specialist coverage, that is opportunity. If most surface deep specialist coverage with first-party data and tools, that is harder ground — flag it.

4. **Bound the pillar.** Decide what is in scope and what is adjacent. The adjacent topics get linked to from the pillar but live in their own architecture. Without this boundary, clusters expand until they cover everything and own nothing.

### Phase 2 — Intent and subtopic map

5. **Inventory the search intents under the pillar.** A pillar usually spans informational ("what is X"), navigational ("which X tool"), commercial-investigation ("best X for Y"), and transactional ("X near me"). List 8-25 subtopic phrases per intent. Either expand from the seed queries if provided or build from web research of the pillar's SERP neighborhood.

6. **Cluster the subtopics within intent.** Within each intent, group subtopics that would be satisfied by the same single page. Two subtopics belong on one page if a reader would feel served reading just one of them when looking for the other. Subtopics that fail that test get separate pages.

7. **Score each cluster for fit.** For each candidate cluster, rate (a) audience alignment — does this cluster speak to the pillar's audience or to a different one; (b) business alignment — does winning this cluster move the conversion the pillar exists to drive; (c) defensibility — does the operator have first-party knowledge, data, or experience that competitors do not. Clusters that score low on all three should be cut, not deferred.

8. **Distinguish "head" and "long-tail" clusters.** A head cluster targets a high-volume, broadly searched query and serves as a content destination in its own right. A long-tail cluster targets a specific narrow question that feeds traffic but is less likely to be a destination. Head clusters carry more linking weight and editorial investment.

### Phase 3 — Architecture shape

9. **Pick the architecture shape.** Choose from three shapes: (a) single pillar with flat cluster ring (one pillar, 8-15 cluster pages, no sub-pillars) for compact topics; (b) pillar with sub-pillars (one master pillar, 2-4 sub-pillars, 4-8 cluster pages under each sub-pillar) for medium topics; (c) multi-pillar architecture (a hub page that introduces multiple pillars, each a full cluster) for ambitious topical authority plays. Match the shape to the `cluster_size` input and the demand inventory.

10. **Draft the page list.** Produce the full list of pages the architecture requires — pillar page(s), sub-pillar pages, cluster pages — each with a working title, the primary subtopic it serves, the intent it answers, and the recommended format (definitive guide, how-to, comparison, listicle, FAQ collection, tool, data report, case study). Avoid more than one page per subtopic; merge if two emerge.

11. **Assign each cluster page a content format that fits the intent.** Informational subtopics usually want definitions, how-to walkthroughs, or guides. Commercial-investigation subtopics want comparisons, criteria frameworks, and best-of lists. Transactional subtopics want short conversion-focused pages with structured data. Mismatched formats are the most common reason clusters underperform.

12. **Mark each page's role in the link graph.** Every page is either a hub (collects inbound links from siblings, sends outbound links to its children), a destination (terminal page for an intent), or a connector (a thin link page that exists only to route — usually a sign you should merge). Eliminate connector pages where possible.

### Phase 4 — Existing-content alignment

13. **Map existing content to the architecture.** If the user provided existing URLs, place each one against the page list. Mark each as (a) keep as-is and slot into the architecture, (b) refresh and slot in, (c) merge with another existing piece, (d) merge into a planned new piece, or (e) retire and 301 to the cluster page that replaces it.

14. **Resolve duplicate-coverage clusters first.** Two existing posts that cover overlapping subtopics are losing each other's link equity and confusing search engines about which to rank. Flag every pair, pick the keeper, and route the loser by 301. Doing this before producing new content prevents the new piece from inheriting the same confusion.

15. **Promote underperforming pages with strong inbound links.** A weak existing piece that has accumulated good external links is worth refreshing in place rather than retiring; preserve the URL and rebuild the content. Note these in the editorial roadmap explicitly.

### Phase 5 — Pillar page specification

16. **Specify the pillar page in detail.** The pillar page is the centerpiece. It needs (a) a clear definition of the topic in the opening paragraphs; (b) a navigable table of contents linking to every cluster page; (c) at least one piece of original value not available on any cluster page — a framework diagram, a self-assessment, a decision tree, a glossary, or a comparison matrix; (d) explicit calls to action mapped to the pillar's audience; (e) a prominent prompt to the next cluster page in the recommended reading order.

17. **Design the pillar's length and depth honestly.** A pillar page that tries to fully answer every subtopic ends up bloated and outranked by focused cluster pages. The pillar's job is to define the territory and route deep questions to the cluster pages that answer them. Recommended length is whatever it takes to do that job, typically 1,800–4,000 words but with no minimum required.

18. **Reserve the pillar for the head query.** The pillar page targets the broadest query of the pillar topic, e.g., "marketing attribution," not "marketing attribution models" (that is a cluster). If two pillar candidates compete for the head query, pick one and route the other to a sub-pillar role.

### Phase 6 — Cluster page specification

19. **Brief each cluster page in three paragraphs.** Each cluster page needs (a) the primary subtopic and the intent class, (b) the questions the page must answer in order, (c) the unique angle that differentiates this page from the top three results. Without the third item, the cluster page is parity coverage, which loses by default.

20. **Cap cluster page count per cycle.** A team that produces 20 cluster pages in two months in parallel ships uniform mediocrity. A team that produces 6 cluster pages in two months with depth ships work that survives. Stage the cluster build over multiple cycles in the editorial roadmap.

21. **Specify cross-cluster links.** Cluster pages link to (a) the pillar above, (b) the two or three most directly related sibling clusters, (c) cluster pages in adjacent pillars when natural. Do not link to siblings indiscriminately. Use anchor text drawn from the subtopic phrasing, not the page title.

### Phase 7 — Sub-pillars and depth

22. **Decide whether sub-pillars are necessary.** Sub-pillars are useful when the pillar has more than roughly fifteen cluster pages or when a substantial subtopic deserves its own audience entry point. They are noise when the pillar is small. If the architecture is borderline, default to no sub-pillars and revisit after the first cycle.

23. **Design sub-pillars as miniature pillars.** A sub-pillar is itself a pillar over its own cluster ring. Apply Phase 5 to each. Sub-pillars link up to the master pillar and down to their cluster ring.

24. **Bound sub-pillar overlap.** Two sub-pillars that share more than a couple of cluster pages probably should be merged. Two sub-pillars that share none usually mean one of them belongs to a different pillar entirely.

### Phase 8 — Link graph and hub design

25. **Diagram the hub linking.** Draw the cluster as a graph. Hubs (pillar, sub-pillars) sit at center nodes. Spokes (cluster pages) ring each hub. Cross-edges connect related siblings and adjacent clusters. Annotate each edge with the anchor-text pattern. The diagram is the work product, not decoration; it forces the architecture to be coherent before content writing starts.

26. **Bound link-graph depth.** Every cluster page should be reachable from the homepage in three hops or fewer for a standard architecture, four for a deep multi-pillar one. If the architecture forces deeper paths, restructure rather than ship.

27. **Plan anchor-text variants.** For each edge type (pillar-to-cluster, cluster-to-pillar, cluster-to-sibling, external-to-pillar), specify two to four anchor variants drawn from the target page's primary subtopic. Repeating the exact same anchor across every spoke flattens semantic signal and looks templated.

### Phase 9 — Query fan-out and AI-search resilience

28. **Map the query fan-out for each cluster page.** Generative search engines decompose a user query into a fan of related sub-queries and synthesize an answer from results across the fan. Each cluster page should list the fan of likely sub-queries it answers, phrased as full questions. This is both a content-completeness check and the structure AI engines use to decide what to cite.

29. **Write extractable answer blocks.** Inside each cluster page, designate two to four short answer blocks (typically 2–4 sentences each) that directly answer a specific sub-query, free of context dependence. These are the units most likely to be quoted by AI answer engines. Each cluster page brief should name them.

30. **Add citation-worthy original elements.** AI engines disproportionately cite content with original statistics, named frameworks, structured comparisons, and concrete examples. Each cluster page should include at least one such element — a statistic the operator can defend, a comparison table, a named heuristic, or an annotated example.

31. **Use structured data deliberately.** Mark up FAQs that genuinely exist on the page with FAQPage, mark up how-to content with HowTo, mark up the article itself with Article. Do not mark up an FAQPage that does not have visible FAQs; mismatch is a known penalty trigger.

### Phase 10 — Editorial roadmap and ongoing care

32. **Sequence the build for early authority signal.** Publish the pillar page only after at least four cluster pages exist to link up to it. Without inbound cluster links, the pillar has nothing to rank on. Sequencing the cluster pages first is counterintuitive but works.

33. **Stage the cluster release over three or four cycles.** Cycle one: pillar plus the four most defensible cluster pages. Cycle two: the next batch of cluster pages plus refreshes of any existing pieces folded in. Cycle three: sub-pillars (if any) and the remaining cluster pages. Cycle four: gaps surfaced by measurement.

34. **Plan refresh cadence.** Cluster pages on stable subtopics get refreshed annually. Pages on volatile subtopics (tooling, prices, news-adjacent topics) get refreshed quarterly. The pillar gets refreshed when the architecture changes, not on a calendar.

35. **Measure cluster health holistically.** Cluster health is not "did the pillar rank for the head query." It is the share of all queries inside the pillar's intent map where the operator's domain appears in the top results, weighted by query value. Track that aggregate, not individual rankings.

## Inputs

- **pillar_topic** (required): The broad topic the cluster will own. One noun phrase, defensible scope, recognizable audience.
- **business_context** (optional but recommended): Product, audience, conversions. Determines which subtopics get prioritized and which formats fit.
- **existing_content** (optional): URLs of existing pieces. The architecture will incorporate, merge, refresh, or retire each one rather than re-derive from scratch.
- **seed_queries** (optional): A starter set of queries the team has identified. Used to expand the subtopic map; not authoritative on its own.
- **competitor_clusters** (optional): 2-5 competitor URLs covering the same broad topic. Used to benchmark depth and surface format gaps, not to drive parity.
- **cluster_size** (optional): Target architecture size. Default is Standard.

## Outputs

The skill produces four artifacts.

1. **Cluster architecture** — the full page list with intents, formats, briefs, and the linking diagram.
2. **Editorial roadmap** — sequenced build plan with cycles, dependencies, and refresh cadence.
3. **Query fan-out map** — per-page family of sub-queries with designated extractable answer blocks.
4. **Cluster data JSON** — machine-readable export for CMS or calendar import.

## Examples

**Example 1: HR-tech pillar on remote-work compliance**

Input: pillar_topic is "remote-work compliance," business_context is a payroll product, existing content is twelve blog posts of mixed quality, cluster_size is Standard. The skill returns an architecture with one pillar page ("complete guide to remote-work compliance for distributed teams"), two sub-pillars (US multistate, international), and 22 cluster pages distributed across the two sub-pillars and a small ring around the pillar (definitions, role responsibilities, audit checklist). Six of the existing posts merge into four cluster pages; two refresh in place; four retire with 301s. The roadmap stages the build over four cycles, with cycle one shipping the pillar and four cluster pages on the highest-conversion US-multistate questions.

**Example 2: Consumer SaaS pillar on personal-finance budgeting**

Input: pillar_topic is "budgeting methods," business_context is a budgeting app, no existing content, competitor_clusters lists three deep-coverage finance media sites, cluster_size is Deep. The skill flags that competing for parity coverage with named media sites is unlikely to win and recommends a narrower angle (e.g., "zero-based budgeting for variable-income earners"). It returns a multi-pillar architecture with three pillars (zero-based, envelope, hybrid) each over its own cluster ring, and a hub page that routes audiences by income type. The query fan-out map includes extractable answer blocks for each method's headline questions, and cites original calculator data the app can publish to differentiate.

## Limitations

- The architecture is only as good as the pillar choice. The skill validates legitimacy in Phase 1 but cannot make a market that does not exist.
- Volume estimation without a paid index is unreliable. The architecture is built on demand structure (intents, subtopic count, SERP shape) rather than absolute volume forecasts.
- Competitor benchmarking is qualitative without paid tools. The skill notes when the cluster is competing against deep-pocketed media and recommends a narrower angle rather than parity.
- The skill does not write the content. It produces briefs, format choices, and word-count guidance, leaving execution to a content team or to a focused content-drafting skill.
- AI-search behavior is genuinely shifting; the query fan-out and citation-worthiness recommendations encode the patterns visible at the time of writing and may need refresh as engines evolve.

## Sources reviewed

- https://github.com/eliasdabbas/advertools
- https://github.com/garmeeh/next-seo
- https://github.com/harlan-zw/nuxt-seo
- https://github.com/spatie/schema-org
- https://github.com/google/schemarama
- https://github.com/AnswerDotAI/llms-txt
- https://github.com/amplifying-ai/awesome-generative-engine-optimization
- https://github.com/devbret/website-internal-links
