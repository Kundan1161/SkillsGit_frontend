---
id: skillsgit-curated/seo-site-audit-pro
version: 1.0.0
name: SEO Site Audit Pro
description: Run a prioritized, end-to-end SEO audit of a domain or URL set covering crawlability, indexation, Core Web Vitals, schema, on-page quality, internal linking, and authority signals — output as a ranked action plan.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [seo, audit, technical-seo, on-page, core-web-vitals, schema, crawl, lighthouse]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: [web_search]
  tools_optional: [code_execution, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords: [seo audit, site audit, technical seo, crawl audit, core web vitals, indexation, on-page seo, schema audit, lighthouse audit, page speed, canonical issues, internal linking, seo report, audit website]
example_invocations:
  - "Run a full SEO audit on example.com and rank the fixes."
  - "Audit these 50 URLs for technical and on-page SEO issues."
  - "Why is my organic traffic dropping? Audit the site end-to-end."
  - "Give me a prioritized SEO action plan for our blog."
inputs:
  - name: domain_or_urls
    type: text
    required: true
    description: A root domain (preferred for full audits) or a newline-separated list of URLs to audit.
  - name: business_context
    type: text
    required: false
    description: One paragraph on what the site is, who it serves, and what conversions matter. Sharpens prioritization.
  - name: target_keywords
    type: text
    required: false
    description: Optional comma-separated list of priority keywords the site should rank for. Used to score on-page relevance.
  - name: competitors
    type: text
    required: false
    description: Optional comma-separated list of 2-5 competitor root domains for authority and content benchmarking.
  - name: audit_depth
    type: choice
    required: false
    description: Quick (top 50 URLs), Standard (top 500), or Deep (full site map). Default Standard.
    choices: [quick, standard, deep]
outputs:
  - name: executive_summary
    type: markdown
    description: One-page summary scoring the site across five pillars and naming the three highest-impact fixes.
  - name: prioritized_findings
    type: markdown
    description: Findings table ranked by severity x effort, each with affected URLs, evidence, root-cause hypothesis, and a recommended fix.
  - name: action_plan
    type: markdown
    description: A 30/60/90-day remediation roadmap mapped to roles (engineering, content, SEO ops).
  - name: raw_data
    type: json
    description: Machine-readable findings (issue type, severity, urls, metrics) for ticket import.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# SEO Site Audit Pro

## When to use

Invoke this skill when a user asks for any of the following:

- A full SEO audit of a domain, subdomain, or sitemap section.
- An investigation into why organic traffic, rankings, or impressions have moved (up or down) without a clear cause.
- A pre-launch or pre-migration check on a staging or new site.
- A second-opinion review of a previous audit, an agency deliverable, or a SaaS tool's automated report.
- A prioritized action list when the team already knows there are problems but does not know which to fix first.

Do not invoke this skill for narrow tasks better served by a focused tool: pure keyword expansion (use Keyword Cluster Builder), competitor content gap discovery (use Content Gap Hunter), copy editing or rewriting (use a content skill), or paid-search account audits.

This skill is opinionated about output. It always returns a prioritized list — never an undifferentiated dump of every issue a crawler can find. Severity is judged by likely impact on organic traffic and conversions, not by the count of affected URLs.

## How to apply

The audit proceeds in eleven phases. Each phase produces structured findings that feed the final prioritization. Move through them in order; do not skip ahead to recommendations before evidence is collected.

### Phase 1 — Scope and ground truth

1. **Confirm the unit of work.** Resolve the input to (a) a single root domain, (b) a defined subdomain or path prefix, or (c) an explicit URL list. If the input is ambiguous (for example, the user provides example.com but only cares about example.com/blog), ask one clarifying question before proceeding. Record the chosen scope at the top of the report.

2. **Identify hosting and stack signals.** Note the CMS or framework (WordPress, Shopify, headless React/Next, custom), CDN, and any server-rendered vs client-rendered indicators. These shape what kinds of issues are likely and which fixes are realistic. Do not guess — read the response headers, view the source of two or three sample pages, and check the sitemap location.

3. **Inventory the audit surface.** Fetch and parse `/robots.txt` and the sitemap(s) it references. Count URLs by section. If the sitemap lists more than 10,000 URLs, sample stratified (homepage, top-level templates, deep content, archive pages) rather than crawling everything. Document the sample plan.

4. **Establish a baseline of intent.** From the business context and target keywords (if provided), articulate in one or two sentences what this site is trying to do for organic search. Every later finding will be weighted against this intent. Without it, prioritization defaults to generic best practice.

### Phase 2 — Crawlability and indexation

5. **Validate robots directives.** Check that `robots.txt` does not block important sections by accident (a common regression after a launch) and does not advertise admin or staging paths in a way that creates a footprint. Flag any `Disallow` rule that overlaps with URLs in the sitemap — that combination is almost always a bug.

6. **Sample the index status.** Without privileged access to Search Console, use site: operators and live crawls to estimate the indexed-to-submitted ratio for each section. A large gap means either (a) thin or duplicate content, (b) accidental noindex directives, or (c) a recent deindexing event. Treat these as three different findings.

7. **Audit canonicals and hreflang.** For each template (home, category, product, article, etc.), confirm the canonical URL self-references where appropriate and points to the chosen primary where duplicates exist. For multilingual sites, verify that every hreflang cluster is reciprocal and includes an `x-default`. Mismatched or one-way hreflang is one of the most under-reported audit issues — call it out explicitly.

8. **Check status codes and redirect chains.** Crawl the sample and bucket responses: 2xx, 3xx (separating 301 vs 302), 4xx, 5xx. For every redirect, walk the chain — flag any chain longer than one hop and any chain that ends in a 404. For 4xx responses linked from internal pages, list the source URLs so the link owners can fix them at the source rather than via redirect plasters.

### Phase 3 — Rendering and JavaScript

9. **Compare raw HTML vs rendered DOM** on a handful of pages representative of each template. If critical content (title tag, h1, main copy, internal links) is missing from the raw HTML and only appears after JS execution, document the gap. Search engines do render JavaScript but with a delay and cost; if the site relies on it for primary content, score this as a high-severity finding for any page that depends on organic discovery.

10. **Inspect the critical render path** on one representative page per template. Note render-blocking resources, large hydration bundles, and third-party scripts that fire before paint. This feeds into Core Web Vitals analysis but also into a separate "crawl efficiency" finding when bots time out before content loads.

### Phase 4 — Core Web Vitals and performance

11. **Sample lab metrics with a Lighthouse-style audit** on five to ten representative URLs (one per template, plus the homepage). Record LCP, INP (or its proxy), CLS, and TTFB. Run three trials per URL and report the median to avoid noise.

12. **Cross-reference field data when available.** If the site is on the Chrome UX Report dataset, prefer the 75th-percentile real-user numbers over lab numbers for the headline finding. Lab metrics are for diagnosing causes; field metrics are for stating the problem to leadership.

13. **Attribute Web Vitals failures to causes**, not just to URLs. A failing LCP rooted in a hero image is a different ticket from one rooted in a server response time, which is different from one rooted in a render-blocking font. Group findings by cause and list affected templates underneath.

### Phase 5 — On-page elements

14. **Audit titles and meta descriptions.** Flag duplicates (across the crawl sample), excessive length (titles over roughly 60 characters frequently truncate; descriptions over roughly 155), missing tags, and boilerplate templates that fail to differentiate pages. Do not score short titles as a defect on their own — short, specific titles often outperform padded ones.

15. **Audit headings.** Each page should have exactly one h1 that names the topic. Walk the heading hierarchy — h2s under h1, h3s under h2 — and flag pages where the hierarchy skips levels or where multiple h1s reflect a template bug.

16. **Audit images.** Sample images per template and check for: descriptive alt text where the image carries meaning, empty alt attributes on decorative images (better than missing), oversized dimensions relative to displayed size, and modern formats (AVIF/WebP) where reasonable. Roll up findings as percentages, not per-image lists, except for hero or product images on revenue-critical templates.

17. **Audit internal linking.** Build a link graph of the crawled sample. Surface (a) pages with zero internal inbound links from the body content (orphans), (b) pages with very many outbound links to low-value destinations, and (c) anchor-text patterns that are either repetitive ("click here") or keyword-stuffed. Recommend specific link additions where high-value pages are underlinked.

### Phase 6 — Content quality signals

18. **Sample content depth.** Pull word count, reading level, and structural patterns (presence of FAQ, table of contents, images, code blocks) per template. Do not propose minimum word counts as a target — propose them only as a diagnostic of thin templates. A 200-word product description may be fine; a 200-word "ultimate guide" almost never is.

19. **Check freshness signals.** Note last-modified dates exposed in markup or sitemaps. Pages that haven't been updated in years but target time-sensitive queries are candidates for refresh — flag them as content debt rather than as bugs.

20. **Check for AI-generated boilerplate or thin programmatic pages.** Look for repeated sentence skeletons, near-duplicate paragraphs across pages, and templates that exist primarily to capture long-tail variants. These are not automatic defects, but if the site has many such pages and a recent traffic decline, they are a likely cause.

### Phase 7 — Structured data and schema

21. **Extract structured data** (JSON-LD preferred, microdata/RDFa accepted) from each template. Validate against schema.org definitions and Google's documented rich-result types. Flag (a) invalid syntax, (b) markup that does not match visible page content (a common penalty trigger), and (c) opportunities where a rich result type fits but is not implemented (Product, FAQ, HowTo, Article, Breadcrumb, Organization, LocalBusiness).

22. **Prioritize schema by traffic potential.** A Product schema fix on a top-selling category template outranks an Organization schema fix on a footer-only payload, even if both are technically valid.

### Phase 8 — Mobile and accessibility intersect

23. **Confirm mobile parity.** With mobile-first indexing as the default, the mobile rendering of every audited template should expose the same content, headings, internal links, and structured data as the desktop version. Sample two or three templates and document any parity gaps.

24. **Note accessibility issues that double as SEO issues.** Missing form labels, low color contrast on text, and inaccessible navigation hurt search bots as much as humans. Do not turn this into a full accessibility audit — only surface the items that also affect crawlability or content extraction.

### Phase 9 — Authority and off-page signals

25. **Profile the link graph at a high level** using publicly available signals: referring domain count from any free index, brand-mention frequency in web search, presence in industry directories. Without paid tools, do not claim precision — frame these as directional signals.

26. **Spot toxic patterns.** Footer link networks, comment spam, sitewide links from unrelated low-quality sites — call these out. The recommended fix is almost always disavow-or-ignore plus root-cause hygiene, not a per-link cleanup.

27. **Benchmark against named competitors.** If the user supplied competitors, compare visible authority indicators (rough referring-domain magnitude, brand presence in SERPs for shared queries) and note where the audited site lags or leads. Keep this directional; precise numbers require a paid index.

### Phase 10 — Synthesis and prioritization

28. **Score every finding on two axes:** impact and effort. Impact is the expected lift in organic sessions or conversions if fixed, judged against the site's intent baseline from Phase 1. Effort is engineering- or content-hours from the team that will execute. Plot findings on a 2x2 (high/low impact, high/low effort).

29. **Build the executive summary around three fixes**, not thirty. Pick the highest-impact item from each of three buckets: technical (something engineering owns), content (something the editorial team owns), and structural (something product or design owns). This forces cross-functional ownership and prevents the audit from becoming an engineering ticket queue alone.

30. **Produce the action plan as a 30/60/90.** The 30-day list is unblocked quick wins. The 60-day list is fixes that require coordination. The 90-day list is structural changes that should kick off now but will not show effects until the following quarter. For each item, name the owner role, the metric that will move, and the expected magnitude of the move.

## Inputs

- **domain_or_urls** (required): The audit target. A bare domain triggers a full crawl plan; a URL list triggers a per-URL audit.
- **business_context** (recommended): What the site does, who it serves, what counts as a win. Without this, the audit defaults to generic best practice and is much less useful.
- **target_keywords** (optional): Used to score on-page relevance and to pick representative templates.
- **competitors** (optional): Used for relative authority and content benchmarking only.
- **audit_depth** (optional): Trades thoroughness for speed. Default is Standard.

## Outputs

The skill produces four artifacts in a single response:

1. An **executive summary** — one page, five pillar scores, three named fixes.
2. A **prioritized findings table** — every issue with severity, effort, evidence, and recommended fix.
3. An **action plan** — 30/60/90-day, mapped to roles.
4. A **raw_data JSON** — structured findings for import into a tracker.

The executive summary is the only artifact the buyer will reliably read. Write it last, after all evidence is gathered, and make every sentence load-bearing.

## Examples

**Example 1: SaaS pricing page audit**

Input: `pricing` page of a B2B SaaS site, business_context says enterprise leads from organic are the primary KPI. The audit surfaces a missing Product schema, a non-self-referential canonical, two internal links from the homepage with mismatched anchor text, and a slow LCP from a hero illustration. Prioritization puts the canonical fix and the schema addition in the 30-day bucket (high impact, low effort), the LCP in the 60-day bucket (needs design coordination), and a recommended new comparison page in the 90-day bucket (structural).

**Example 2: Multilingual ecommerce category audit**

Input: a French-language category template with three hreflang siblings (en, es, de). The audit finds reciprocal hreflang missing on the Spanish version, duplicate H1s introduced by a recent template refactor, and a noindex tag accidentally left in by the migration team on the German version. The 30-day bucket is two engineering tickets; the 60-day work is a structured-data rollout across the category template; the 90-day item is consolidating eight near-duplicate facet pages into canonical hubs.

## Limitations

- This skill produces an opinionated audit, not a tool replacement. It cannot match the URL-by-URL coverage of a dedicated crawler on a million-URL site. For sites that large, run a crawler first and pass the crawl export as input.
- Authority and backlink analysis is directional without a paid link index. The skill explicitly marks these findings as directional and recommends a paid index for due-diligence-grade analysis.
- Real-user (CrUX) field data is only available if the audited origin has enough traffic to be in the dataset. For low-traffic sites, lab metrics are the only source and the report says so.
- Recommendations are framework-aware but not framework-specific. The skill will note that a Next.js site likely fixes a JS rendering issue via `getStaticProps` rather than client fetching, but it will not write the patch.
- The audit assumes the buyer can supply credentials or access if a deeper inspection is needed (Search Console, Analytics, server logs). Without that access the report flags gaps openly rather than guessing.

## Sources reviewed

- https://github.com/GoogleChrome/lighthouse
- https://github.com/StJudeWasHere/seonaut
- https://github.com/janreges/siteone-crawler
- https://github.com/PhialsBasement/LibreCrawl
- https://github.com/eliasdabbas/advertools
- https://github.com/google/schemarama
- https://github.com/spatie/schema-org
- https://github.com/harlan-zw/nuxt-seo
- https://github.com/treosh/web-vitals-reporter
- https://github.com/addyosmani/web-quality-skills
