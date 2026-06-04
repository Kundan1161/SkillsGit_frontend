---
id: skillsgit-curated/content-gap-hunter
version: 1.0.0
name: Content Gap Hunter
description: Identify content gaps where named competitors rank and you don't, scoring each gap by traffic potential, ranking difficulty, business fit, and topical-authority leverage — output as a prioritized capture plan.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [seo, content-gap, competitive-analysis, content-strategy, topical-authority, keyword-research]
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
trigger_keywords: [content gap, competitor gap, gap analysis, content opportunities, competitive content, ranking gap, share of search, topic gap, content audit competitor, missing content]
example_invocations:
  - "Find content gaps between our site and these three competitors."
  - "What topics are our competitors ranking for that we're not?"
  - "Show me the highest-value content opportunities we're missing."
  - "Prioritize the gaps between our blog and competitor X."
inputs:
  - name: own_domain
    type: text
    required: true
    description: The user's root domain or specific section to benchmark.
  - name: competitor_domains
    type: text
    required: true
    description: Two to five competitor root domains (newline-separated). More than five dilutes signal — pick the closest fits.
  - name: business_context
    type: text
    required: false
    description: Product, audience, and which conversions matter. Used to weight gaps by business fit, not just traffic.
  - name: priority_keywords
    type: text
    required: false
    description: Optional list of strategic keywords the team wants prioritized regardless of competitor coverage.
  - name: scope_limit
    type: choice
    required: false
    description: Top 100 gaps, Top 500, or All. Default Top 100 — diminishing returns past the top tier.
    choices: [top-100, top-500, all]
outputs:
  - name: gap_inventory
    type: markdown
    description: Sortable table of gaps with the topic, competitor URLs ranking, estimated difficulty, business-fit score, and recommended action.
  - name: capture_plan
    type: markdown
    description: A staged capture roadmap (quick wins, strategic plays, long-tail fills) with the rationale for each tier.
  - name: gap_data
    type: json
    description: Machine-readable export of every identified gap for tracker import.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Content Gap Hunter

## When to use

Use this skill when a user wants to know what topics or queries their competitors are winning that they are not. Typical triggers:

- Quarterly or annual content planning needs a competitive lens.
- A new entrant is showing up in shared SERPs and the team needs to understand the threat.
- An existing content program has plateaued and the team needs fresh, externally-validated ideas.
- A leadership ask along the lines of "what should we be writing about that we're not."

Do not use this skill when:

- The user wants an internal-only audit (use Site Audit Pro).
- The user has no specific competitors in mind and wants pure expansion from a topic (use Keyword Cluster Builder).
- The user wants to copy competitor articles directly. This skill identifies opportunities, not templates; copying is bad for ranking and worse for legal.

Subscribers receive periodic updates to the difficulty model and SERP-feature scoring as Google's ranking signals shift. The skill assumes competitor SERPs are a moving target and that a gap inventory expires faster than an audit does — refresh quarterly for active categories.

## How to apply

The workflow has ten phases. Phases 1-3 set up the comparison, phases 4-6 build the gap inventory, phases 7-9 score gaps, and phase 10 packages the output.

### Phase 1 — Define the comparison set

1. **Pick competitors carefully.** Two to five competitors. More than that dilutes signal and produces a long-tail report no one will execute against. Reject competitors that are obviously off-fit (a marketplace where the user is a SaaS, a media site where the user is a tool) unless the user explicitly insists. Explain the rejection in the report.

2. **Clarify the comparison scope.** Whole-site comparison is the default. If the user owns a blog and a product surface, ask whether to compare both or just one. A SaaS company benchmarking its blog against an indirect competitor's blog is a different report from benchmarking its product pages against a direct competitor's product pages.

3. **Establish business context.** The single most important input. Without it, gaps are scored by raw traffic potential, which produces a list dominated by broad informational queries the user will never convert. With it, the same gap inventory can be reranked to surface queries that match the buyer journey.

### Phase 2 — Build the comparison corpus

4. **Enumerate each competitor's indexed content.** Use public sitemap exposure first, fall back to site: operators where sitemaps are missing or obviously incomplete. Sample if the corpus is enormous — a 30,000-URL competitor blog should be sampled stratified by section rather than crawled exhaustively.

5. **Categorize competitor URLs by template** (article, comparison, listing, product, landing, glossary, etc.). The gap analysis is more useful when expressed as "they have a glossary, we don't" than as a flat list of missing terms. Templates surface structural gaps that flat term lists hide.

6. **Do the same for the user's site.** Map their templates and content sections. A complete gap report requires symmetric inventories; otherwise the user gets a list of competitor URLs with no comparison context.

### Phase 3 — Resolve the keyword universe per side

7. **For each competitor URL, infer the primary keyword(s)** from the title tag, H1, meta description, URL slug, and visible H2 structure. Use the SERP fingerprint as confirmation — fetch the top 10 SERP for the inferred keyword and check whether the competitor URL ranks in the top 20. If it does not, the inference was wrong; back off and infer again from page content. Without paid rank data this is imperfect; flag low-confidence rows.

8. **For the user's URLs, do the same** so the comparison is apples to apples. Reusing the technique on both sides eliminates a class of false-positive gaps that come from mismatched keyword extraction methods.

### Phase 4 — Identify the raw gaps

9. **Compute set differences.** Gaps are keywords (or keyword clusters, after light grouping) where (a) at least one competitor ranks in the top 20, and (b) the user does not rank in the top 50. Choose those thresholds deliberately — narrowing the competitor band to top 10 misses long-tail wins; widening the user band to "any position" inflates the gap count with queries the user already covers weakly.

10. **Distinguish kinds of gaps.** Four kinds appear:
    - **Coverage gaps** — the user has no page on the topic at all.
    - **Quality gaps** — the user has a page but it ranks poorly because the page is thin, mismatched on intent, or outdated.
    - **Format gaps** — the user has a page that targets the right topic with the wrong format (a blog post where the SERP rewards a tool, a comparison table where the SERP rewards a long-form guide).
    - **Authority gaps** — the user has a page that is correct on intent and format but cannot break the top 10 because the competitor pages have stronger inbound links. These are the slowest to close.

   Tag every gap with its kind. The recommended action differs by kind.

### Phase 5 — Cluster related gaps

11. **Group near-duplicate gaps.** Five competitor keywords like "how to write a press release", "press release format", "press release template", "press release example", and "writing a press release" all map to the same single page. Cluster them; create one gap not five. This step alone often cuts a raw gap inventory by half.

12. **Identify topical clusters competitors own.** Sometimes the gap is not one keyword but a whole topic the competitor has built out. If a competitor has 30 pages on "marketing analytics" and the user has zero, that is one strategic gap, not 30 tactical ones. Flag these as "topical authority gaps" — they require a hub-and-spoke plan, not a single article.

### Phase 6 — Score gaps for opportunity

13. **Estimate traffic potential per cluster.** Combine search volume (when available from the user's tooling), SERP feature presence (a cluster with a People Also Ask block and a featured snippet has higher capture potential than one without), and competitor URL freshness (if the ranking page is old and shallow, it is easier to displace).

14. **Estimate difficulty.** Look at the linking-domain magnitude of the ranking competitor URLs, the diversity of result types (a SERP dominated by huge brand domains is hard; a SERP with a mix of small sites is reachable), and the presence of search features that absorb clicks (heavy ad load, knowledge panels, video carousels). Difficulty is a 0-100 score with the inputs disclosed.

15. **Estimate business fit.** Map each gap topic to the buying journey (top, middle, bottom of funnel) and to product fit (does ranking for this query reach a buyer the user can actually serve). A high-volume top-of-funnel gap with weak product fit scores lower than a lower-volume middle-of-funnel gap with strong fit. This is where the business_context input does most of its work.

16. **Estimate topical-authority leverage.** A gap that fills a hole in a topic the user already partially covers scores higher than an isolated gap in a topic the user has never touched, because the existing topical signals lift the new page. Quantify this as the overlap between the new gap topic and the user's existing topic graph.

### Phase 7 — Compose the priority score

17. **Combine the four estimates** (traffic potential, difficulty, business fit, topical-authority leverage) into a single 0-100 priority score. Use a transparent weighting (default: 30% traffic, 25% difficulty inverted, 30% fit, 15% leverage) and expose the weights so the user can rerank. Do not hide the formula — opaque priority scores destroy trust.

18. **Apply hard filters last.** Any gap the user named in priority_keywords floats to the top regardless of score. Any gap that conflicts with brand or legal constraints (competitor brand terms, regulated claims) is removed with a note.

### Phase 8 — Recommend an action per gap

19. **Coverage gaps get a new-page recommendation** with intent, format, and scope estimate — the same shape as a Keyword Cluster Builder output for that cluster.

20. **Quality gaps get a refresh recommendation** that names the existing URL, the specific weaknesses (intent mismatch, thin coverage, stale data, missing SERP features), and the minimum set of changes needed. A refresh is faster and usually higher-ROI than a new page, so quality gaps often rank higher in the capture plan than their priority score alone would suggest.

21. **Format gaps get a rebuild recommendation,** including the call on whether to redirect the old URL into the new format or keep both. The default rule: redirect when the old URL has accumulated meaningful inbound links and authority; keep separate when the old URL serves a real distinct audience.

22. **Authority gaps get a link-building or PR recommendation,** not a content one. The content already exists and is correct. The output should say so honestly rather than recommending yet another rewrite. This is the single most useful kind of finding to surface because most gap tools mis-prescribe these as content problems.

### Phase 9 — Stage the capture plan

23. **Tier the recommendations into three buckets:**
    - **Quick wins** — quality and format gaps on high-fit topics where execution is days, not weeks.
    - **Strategic plays** — coverage gaps inside topical clusters where the user has partial authority, requiring 3-10 new pages over a quarter.
    - **Long-tail fills** — coverage gaps on isolated topics with modest opportunity, suitable for slow weeks or junior writers.

24. **Time-box each tier.** Quick wins are 30-day work, strategic plays are quarterly commitments, long-tail fills are backlog. Make the expectation explicit so a content lead can sequence the program rather than executing top-to-bottom on the priority list.

### Phase 10 — Output

25. **Produce the gap inventory** as a markdown table sortable by score, kind, and topic. Include the competitor URLs ranking, the inferred keyword, the four sub-scores, the composite score, the recommended action, and a confidence level on the inference. The confidence level is critical when keyword inference was uncertain.

26. **Produce the capture plan** as a narrative document. Open with three named opportunities the user should fund this quarter. Then walk through each tier with rationales. Close with the topical-authority hubs that should anchor a multi-quarter program — these are the structural plays that compound.

27. **Produce a JSON export** of every gap row for import into editorial planning tools. Schema: gap_id, kind, topic, cluster, member_keywords, competitor_urls, our_url (if any), sub_scores, composite_score, recommended_action, confidence, tier.

28. **Note coverage caveats explicitly.** If a competitor's site is largely behind authentication, or if their sitemap is incomplete, or if a section of their content is recent enough that ranks have not stabilized, say so. A gap report that overstates its completeness will be used to make decisions it cannot support.

29. **Note ethical guardrails.** The output describes opportunities; it does not describe competitor pages in enough detail to copy. Recommended actions reference the topic and format, not the structure or wording of any specific competitor URL. This is both an ethical line and a practical one — copying loses to original work in the SERPs that matter.

## Inputs

- **own_domain** (required): The user's root or section to benchmark.
- **competitor_domains** (required): Two to five competitor domains. The skill rejects oversized lists with a note.
- **business_context** (recommended): Drives the business-fit score; without it the report is generic.
- **priority_keywords** (optional): Floats specific topics to the top regardless of competitive scoring.
- **scope_limit** (optional): Default Top 100. Past that, returns diminish quickly.

## Outputs

Three artifacts:

1. **gap_inventory** — sortable table with scores and confidence levels.
2. **capture_plan** — narrative roadmap with three named opportunities for the quarter.
3. **gap_data** — JSON export.

## Examples

**Example 1: B2B SaaS vs three SaaS competitors**

Input: a project-management SaaS benchmarking against three direct competitors. The skill identifies 240 raw gaps, clusters them to 86, scores them. The top three: a "switching from [legacy tool]" topic where all three competitors have refreshed pages and the user has nothing (coverage gap, high fit, mid difficulty), a glossary template the user lacks (structural format gap, low effort, high topical leverage), and a refresh of an existing pricing-comparison page that ranks #14 with thin content (quality gap, fast win).

**Example 2: Ecommerce category benchmarking**

Input: an outdoor-gear retailer benchmarking against two larger retailers. The skill flags 60+ "buying guide" gaps where competitors have category-attached guides and the user has only product pages. The capture plan recommends a structured guide template launch (strategic play, 90 days) rather than picking off guides one by one, on the grounds that the template itself is the highest-leverage investment.

## Limitations

- The skill cannot match the precision of a paid backlink and rank index for difficulty scoring. Difficulty estimates are directional; the skill labels them as such and recommends a paid index for due-diligence work.
- Keyword inference from competitor URLs is heuristic. Low-confidence rows are flagged but not removed — the user can choose to drop them or to investigate.
- Search volume is taken from user-provided data when available; otherwise the skill uses cluster size and SERP-feature presence as opportunity proxies and says so.
- The skill respects competitor sites' robots.txt and rate limits. Where a competitor blocks crawl, coverage on that competitor will be partial and the report will say so.
- Recommendations stop at the brief level. Drafting the content is the job of a content-creation skill.

## Sources reviewed

- https://github.com/eliasdabbas/advertools
- https://github.com/jfaccioli/seo-keyword-clusters
- https://github.com/janreges/siteone-crawler
- https://github.com/PhialsBasement/LibreCrawl
- https://github.com/evemilano/keyword_clustering_easy_demo
- https://github.com/unclecode/crawl4ai
- https://github.com/scrapy/scrapy
- https://github.com/StJudeWasHere/seonaut
