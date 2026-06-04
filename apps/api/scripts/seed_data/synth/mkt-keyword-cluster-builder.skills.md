---
id: skillsgit-curated/keyword-cluster-builder
version: 1.0.0
name: Keyword Cluster Builder
description: Expand a seed keyword list or topic into a clustered keyword universe organized by search intent, with priority scores, parent-child hierarchy, and content-format recommendations per cluster.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [seo, keyword-research, clustering, search-intent, content-strategy, topic-modeling]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: [web_search]
  tools_optional: [code_execution]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords: [keyword research, keyword clustering, topic clusters, search intent, keyword expansion, content strategy, semantic clusters, keyword map, keyword universe, content planning, intent classification, keyword grouping, topical authority]
example_invocations:
  - "Cluster these 200 keywords by intent and tell me which to target first."
  - "Expand 'workflow automation for finance teams' into a full keyword map."
  - "Build me a content calendar from this keyword list."
  - "Group my Google Search Console queries into topic clusters."
inputs:
  - name: seeds
    type: text
    required: true
    description: Seed keywords or topic phrases (newline-separated) OR a paste of a keyword list with optional volume and difficulty columns.
  - name: industry_context
    type: text
    required: false
    description: One paragraph on the product, audience, and the buying journey. Sharpens intent classification.
  - name: existing_content
    type: text
    required: false
    description: Optional list of URLs already covering some of these topics; used to flag clusters that already have a target page.
  - name: target_languages
    type: text
    required: false
    description: Comma-separated ISO codes (default en). Multilingual clustering handles each language separately.
  - name: depth
    type: choice
    required: false
    description: How aggressively to expand seeds. Tight (close variants only), Standard (semantic neighborhood), or Wide (adjacent topics included).
    choices: [tight, standard, wide]
outputs:
  - name: cluster_map
    type: markdown
    description: A hierarchical map of clusters and sub-clusters with the head term, intent label, member keywords, and recommended content format.
  - name: priority_queue
    type: markdown
    description: A ranked list of clusters scored on opportunity x effort, with rationale for the top ten.
  - name: cluster_data
    type: json
    description: Machine-readable cluster structure for import into a content calendar or CMS.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Keyword Cluster Builder

## When to use

Use this skill when a user needs to convert raw keyword data or a topic idea into an organized content plan. Specific triggers:

- A team has just exported keywords from a research tool, Search Console, or paid-ads accounts and needs to know what to do with them.
- A new product, vertical, or geographic market needs a topical-authority plan from scratch.
- An existing content library has grown unwieldy and the team needs a topic taxonomy to deduplicate and consolidate.
- A piece of content needs a list of supporting keywords and FAQs to round out coverage.

Do not invoke this skill when the user has a specific URL that needs fixing (use Site Audit Pro) or when the goal is to find topics competitors cover that you don't (use Content Gap Hunter, which scores opportunities differently).

The skill assumes search behavior shifts over time — both because user intent changes with seasons and product cycles and because the search results themselves rerank around new content. Subscribers receive periodic updates to the intent-classification heuristics, the search-intent taxonomy, and the SERP-feature mappings as those evolve.

## How to apply

The workflow has nine phases. Phases 1-3 are about preparing the input, phases 4-7 build the cluster structure, and phases 8-9 produce the ranked recommendations.

### Phase 1 — Normalize the seed set

1. **Detect the input shape.** Three shapes are common: (a) a flat list of phrases with no metadata, (b) a list with volume / difficulty / CPC columns from a research tool, or (c) a single topic phrase that needs expansion before clustering. Branch on the shape — flat lists go to phase 2; metadata-rich lists go to phase 3 directly; single topics go through an expansion pass first.

2. **Clean the strings.** Lowercase, trim whitespace, normalize Unicode (NFKC), collapse repeated spaces, strip surrounding quotes. Preserve punctuation that carries meaning ("free vs paid" is not the same as "free paid"). Deduplicate.

3. **Detect language per row** rather than assuming the whole list is in one language. Multilingual clustering must keep languages in separate clusters even when phrases look superficially similar — the SERPs are different and the intent often differs.

### Phase 2 — Expand to a working universe

4. **Generate variants for thin seeds.** For each seed under five tokens, produce: question forms (who/what/why/how/when), comparative forms (X vs Y, alternatives to X, best X), commercial qualifiers (pricing, cost, free, alternatives, review), and modifier expansions (for [audience], in [context], near me). Cap the expansion at a sensible multiple — a 50-seed list with the Standard depth setting should yield no more than a few hundred candidates, not thousands.

5. **Pull SERP-driven suggestions** where the runtime permits — autocomplete completions for the seed, "People also ask" questions, "Related searches" footer phrases. These are higher-signal than algorithmic expansions because they reflect actual queries. Tag each candidate with its source.

6. **Filter aggressively.** Drop branded queries the user didn't ask to include, drop adult content unless explicitly in scope, drop misspellings that map cleanly to a canonical form (and keep the canonical), and drop queries that are obviously navigational to a specific competitor unless the user wants to study them.

### Phase 3 — Attach metadata

7. **Resolve volume and difficulty when present.** If the input had these columns, carry them through. Where missing for some rows, mark as "not provided" rather than imputing. Do not invent volume numbers — buyers will catch it and trust collapses.

8. **Estimate intent and modifier features** for every keyword (see phase 5). These are computed regardless of whether tool metadata exists, because intent is the dominant axis of clustering and the cheap external metrics rarely include it.

### Phase 4 — Compute pairwise similarity

9. **Compute semantic distance** between keywords using whatever embedding the runtime allows. The clustering is more robust when distance is semantic (so "cancel netflix subscription" and "how to stop netflix billing" cluster together) than when it is purely lexical (which would split them). Where embeddings are unavailable, fall back to token-set Jaccard combined with stem matching as a coarser proxy.

10. **Layer in SERP overlap** where available. Two keywords whose top-10 SERPs share four or more URLs are almost always the same intent and should cluster together regardless of how different the surface phrasing is. This is the single most reliable clustering signal and should override semantic distance when the two disagree.

### Phase 5 — Classify search intent

11. **Use a four-class taxonomy** as the primary axis: Informational ("how does X work"), Commercial Investigation ("best X for Y", "X vs Z"), Transactional ("buy X", "download X", "X pricing"), and Navigational ("X login", "X dashboard"). Avoid finer-grained taxonomies (more classes increase noise without increasing decision value).

12. **Score intent by signal stacking,** not by single keyword tokens. Modifiers like "how to", "what is", "best", "vs", "buy", "pricing", "login" are necessary but not sufficient. Confirm by the SERP shape — if the top results are blog posts and Wikipedia, the intent is informational regardless of what the modifier looks like. If they are product pages and comparison sites, it is commercial. A keyword whose phrase looks transactional but whose SERP is informational should be classified by the SERP, with a note that the user expects content, not a checkout.

13. **Flag mixed-intent keywords explicitly.** Some queries have a SERP that mixes content types — a guide, a comparison table, and a product page all on page one. These are "mixed intent" and should be clustered with their dominant intent but tagged so the content team knows to address multiple needs in one page.

### Phase 6 — Cluster

14. **Cluster within intent class, not across.** Two informational queries about the same topic cluster together; an informational and a transactional query on the same topic do not — they need separate pages. This rule is the single most common mistake in keyword clustering tools and is responsible for the "why isn't my page ranking even though it covers everything" problem.

15. **Choose a head term per cluster.** The head term is the keyword in the cluster with the highest volume that also represents the cluster's center semantically. If those are different keywords, prefer the semantic center — ranking for it tends to pull the high-volume tail along.

16. **Build a parent-child hierarchy.** Small, tightly related clusters frequently roll up under a broader topic. Build at most two levels — a topic and its sub-clusters. Deeper hierarchies look impressive in slides but are not actionable for content teams.

17. **Set a minimum cluster size of two.** Singleton clusters are valid only when the single keyword has high volume and a unique SERP. Otherwise route singletons into a "long-tail support" bucket attached to the nearest parent cluster — they belong as section headings or FAQ entries, not as standalone pages.

### Phase 7 — Recommend content format

18. **Map intent + SERP features to format.** Informational with a "People also ask" block: long-form article with structured FAQ. Commercial investigation with comparison tables in the SERP: a comparison page with a visible table early. Transactional with shopping or product results: a product page, not a blog post. Informational with video carousels: include or embed video. Local intent with map pack: a location-specific page.

19. **Estimate scope** in approximate word count, number of supporting sections, and required media assets (image, table, video, schema). Frame these as floors, not targets — content that needs more depth will exceed the estimate naturally; content forced past the estimate becomes padded and underperforms.

### Phase 8 — Score clusters for prioritization

20. **Score each cluster on opportunity** as a function of summed search volume (or count of member keywords when volume is missing), commercial value implied by intent (transactional > commercial investigation > informational), and the difficulty of competing in the SERP. Use a 0-100 normalized score; show the inputs so the buyer can second-guess weights.

21. **Score each cluster on effort** as a function of recommended scope, the team's existing coverage of the topic (if the existing-content input was provided), and the technical complexity of the recommended format (a comparison table is more effort than a how-to article, a video integration more than either).

22. **Build a 2x2 of opportunity x effort.** High opportunity / low effort is the immediate queue. High opportunity / high effort is the strategic queue — pitch these explicitly as quarter-level commitments rather than as tickets. Low opportunity / low effort is fill-in work for slow weeks. Low opportunity / high effort is the "no" pile; surface it so the team stops debating those clusters.

### Phase 9 — Output

23. **Produce a cluster map** as a hierarchical markdown document. Each top-level cluster gets a heading; sub-clusters become subheadings; member keywords become lists with intent labels and volume (where present). The map is the artifact the content team will paste into a doc; design it for skimming.

24. **Produce a priority queue** that names the top ten clusters with one-paragraph rationales each. The rationale must reference both the opportunity inputs (why this cluster is worth chasing) and the recommended format (what the team will actually build).

25. **Produce a JSON export** of the full structure for import into editorial tools. The schema includes cluster id, parent id, head term, intent, member keywords with optional volume / difficulty, recommended format, scope estimate, and the opportunity / effort scores.

26. **Surface coverage warnings** if the existing-content input was provided. Two failure modes: (a) cluster has a target page but it is poorly aligned (wrong intent, wrong format), and (b) multiple existing pages compete for the same cluster (cannibalization). Both warnings include the specific URLs involved.

27. **Note the freshness of the input.** Keyword data ages — volumes shift seasonally, new queries emerge from product launches and news, and SERPs rerank quarterly. The output includes the date the analysis was run and a recommendation on when to refresh (typically every 90 days for active categories, longer for evergreen).

## Inputs

- **seeds** (required): Seed keywords or topic phrases. The skill auto-detects whether the input is a flat list, a metadata-rich list, or a single topic.
- **industry_context** (recommended): What the product is, who the audience is, what the buying journey looks like. Without this, intent classification falls back on lexical signals alone and is noticeably noisier.
- **existing_content** (optional): URLs of existing pages. Enables cannibalization detection and coverage warnings.
- **target_languages** (optional): Defaults to English. Multilingual inputs are clustered per-language.
- **depth** (optional): Tight, Standard, or Wide. Default Standard.

## Outputs

Three artifacts:

1. **cluster_map** — hierarchical markdown of clusters and sub-clusters.
2. **priority_queue** — ranked top-ten with rationales.
3. **cluster_data** — JSON for import into content tools.

## Examples

**Example 1: SaaS topic expansion**

Input: a single seed `workflow automation for finance teams`, depth Standard, industry_context describes a controllership-focused product. The skill expands to ~180 candidates, clusters them into 12 top-level topics (close management, accruals automation, journal-entry workflows, etc.) with sub-clusters under each. Intent classification puts about 60% in informational, 25% in commercial investigation, 10% in transactional, 5% mixed. The priority queue recommends starting with three commercial-investigation clusters where the SERPs have weak comparison content and the recommended format is a structured comparison page.

**Example 2: Search Console export refactor**

Input: 1,200 keywords pulled from Search Console with impressions and average position. The skill clusters them into 47 clusters, then cross-references against six existing-content URLs. Three clusters flag cannibalization (two existing pages competing); one cluster flags an existing page targeting transactional intent when the SERP rewards informational. The priority queue recommends consolidations first, then new pages second.

## Limitations

- Cluster quality depends on the embedding model used at runtime. Older or smaller models produce coarser clusters; the skill flags low-confidence clusters where adjacent keywords have ambiguous distance.
- Search volume is only as reliable as the source the user provides. The skill does not estimate volume from web signals — it asks for tool data or proceeds without volume and uses keyword count as a fallback opportunity proxy.
- SERP-based intent classification requires live SERP fetches or recent SERP data. Without it, classification falls back to lexical heuristics and accuracy drops; the skill labels rows accordingly.
- Multilingual clustering handles each language separately and does not attempt cross-language equivalence. A "best CRM for small business" in English and its German equivalent will not be linked unless the user explicitly maps them.
- The skill does not generate content for the clusters. That is the job of a content-creation skill — this one stops at the brief.

## Sources reviewed

- https://github.com/eliasdabbas/advertools
- https://github.com/jfaccioli/seo-keyword-clusters
- https://github.com/evemilano/keyword_clustering_easy_demo
- https://github.com/andrea-dagostino/simple_keyword_clusterer
- https://github.com/amazon-science/supervised-intent-clustering
- https://github.com/chukhraiartur/seo-keyword-research-tool
- https://github.com/scrapy/scrapy
- https://github.com/unclecode/crawl4ai
