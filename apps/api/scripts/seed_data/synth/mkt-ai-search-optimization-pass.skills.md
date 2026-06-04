---
id: skillsgit-curated/ai-search-optimization-pass
version: 1.0.0
name: AI Search Optimization Pass
description: Adapt existing content for retrieval and citation by AI-powered answer engines — extractability, schema, citation-worthiness, query-fan-out coverage, entity clarity, publisher signals, and citation instrumentation.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [niche:programmatic-seo, ai-search, aeo, llm-citations, generative-engine-optimization, structured-data, entity-seo, extractability]
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
  estimated_tokens_per_invocation: 8500
trigger_keywords:
  - ai search optimization
  - answer engine optimization
  - aeo
  - geo
  - generative engine optimization
  - llm citations
  - ai overviews
  - llm visibility
  - citation tracking
  - extractability
  - snippet optimization
  - entity optimization
  - schema for ai
  - query fan out
  - llms.txt
example_invocations:
  - "Run an AI search optimization pass on our pillar pricing page."
  - "Our blog ranks fine in classic SERPs but gets zero AI citations — what do we change?"
  - "Audit this how-to article for extractability and answer-engine citation."
  - "How do I make our SaaS landing page citation-worthy for AI answer engines?"
  - "Plan an AEO upgrade for a 200-article knowledge base."
inputs:
  - name: target_page
    type: text
    required: true
    description: The page being optimized. Provide the URL, the full body text, or both. If only a URL is given, the skill assumes web fetch is available to retrieve the page.
  - name: page_purpose
    type: text
    required: true
    description: What the page is supposed to accomplish (e.g., "drive demo signups for our infrastructure-cost product", "rank for how-to-set-up-Kubernetes-RBAC and earn citations from AI answers"). Sharpens the trade-offs.
  - name: primary_queries
    type: text
    required: false
    description: The classic search queries the page already targets. Used as the seed for query-fan-out expansion. Skip if you want the skill to derive them from the page itself.
  - name: brand_entity
    type: text
    required: false
    description: The canonical name of the company, product, or author the page should be associated with, plus any known sameAs URLs (Wikipedia, Wikidata, Crunchbase, LinkedIn, GitHub). Improves entity-clarity recommendations.
  - name: page_type
    type: choice
    required: false
    description: The shape of the page. Affects which schema, structure, and extractability tactics apply.
    choices: [landing-page, how-to, comparison, listicle, product-detail, glossary, pillar-article, faq, case-study]
  - name: tracking_stack
    type: text
    required: false
    description: Tools currently used for analytics and referral tracking (GA4, server logs, CDP, any AI-citation monitoring tool). Used to scope the instrumentation recommendations.
outputs:
  - name: optimization_report
    type: markdown
    description: The full pass — extractability score, schema gaps, citation-worthiness audit, query-fan-out coverage matrix, entity-clarity findings, publisher-signal review, and a ranked change list with before-and-after examples.
  - name: rewrite_patch
    type: markdown
    description: Concrete suggested edits — passage rewrites, new headings, FAQ blocks, byline and about-page additions, and JSON-LD patches — that the editor can apply directly.
  - name: instrumentation_plan
    type: markdown
    description: How to track AI-search citations and referrals after the pass ships — referrer patterns to log, query-log mining cadence, brand-mention monitoring, and the dashboard structure for the next quarter.
  - name: optimization_spec
    type: json
    description: Machine-readable summary of issues, fixes, schema patches, and tracking events for handoff to engineering or a CMS automation.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# AI Search Optimization Pass

## When to use

Invoke this skill when a user wants existing content adapted for AI-powered search and answer engines. Concrete triggers:

- A page already ranks reasonably in classic search but does not show up in AI answer surfaces, AI Overviews, or chat-style search referrals.
- A team wants to standardize an AEO checklist they can run on every new article or landing page before publish.
- A pillar page is being refreshed and the operator wants the refresh to do double duty for AI-search retrieval.
- The site is launching a citation-tracking program and needs the upstream content audited before the dashboard goes live.
- A product launch needs the announcement, the landing page, and the support docs to all reinforce one canonical entity across AI-readable surfaces.

Do not invoke this skill for tasks that have a sharper-focus sibling. Use Topic Cluster Architect when the question is which content to create, not how to optimize what exists. Use Programmatic SEO Content Engine Designer when the work is template-driven page generation at scale. Use Internal Linking Strategy Designer when the link graph itself is the work. Use SEO Site Audit Pro for general technical SEO. This skill assumes the page exists and the goal is to make it extractable, citation-worthy, and entity-clear for AI retrieval pipelines.

The skill is opinionated about a few things. AI-search optimization is content discipline first and markup second — schema cannot save a page that does not earn citation on its substance. The skill refuses to recommend AI-bait tactics that contradict the page's actual value (keyword stuffing rewritten as "question stuffing", invented statistics with fake source attribution, FAQ blocks that do not match the page topic). It also treats the AI-search ecosystem as fast-changing and avoids hard-coded vendor names so the methodology survives the next round of platform changes.

## How to apply

The pass runs in nine phases. The phases are ordered so a finding in one phase informs the next; do not skip ahead to schema before extractability is settled, and do not finalize instrumentation before the rewrite patch is staged. The output is a report engineering and editorial can act on together, not a checklist.

### Phase 1 — Read the page like a retriever would

1. **Strip the page to plain text.** Discard navigation, footer, sidebars, modals, and chrome. What remains is roughly what an AI retriever or extractor will see. If the plain-text version makes no sense without the chrome, the page is too dependent on visual context to survive extraction; flag that as the first finding.

2. **Identify the page's primary claim in one sentence.** If you cannot, the page lacks an extractable thesis. AI answer engines prefer to cite passages that read as standalone statements. The first major rewrite is usually adding or sharpening this sentence near the top.

3. **List the page's secondary claims in priority order.** Each secondary claim is a candidate for citation by a sub-question. Count how many are present. Pages with one strong claim and zero secondary claims rarely earn fan-out citations; the page needs to broaden, not just sharpen.

4. **Mark every passage that contains a discrete fact, statistic, definition, or step.** These are the units that get extracted. If they live inside dense prose with no surrounding structural cues (sub-heading, bullet, table cell, definition list), they will be hard to isolate. The pass aims to move each one closer to a structural anchor.

### Phase 2 — Extractability discipline

5. **Apply the claim-evidence-source pattern to each primary and secondary claim.** A citable passage has three parts in close proximity: the claim, the supporting evidence (data, example, walkthrough), and the source (where the evidence comes from — internal data, named study, named author, or first-party measurement). Passages that are missing one of the three get rewritten in the patch.

6. **Favor short, self-contained paragraphs in passages that should be quotable.** A retriever tends to surface passages roughly the size of a paragraph. A paragraph that runs longer than five or six sentences is more likely to be split awkwardly. Sentences should be parseable in isolation — avoid leading with anaphora like "this" or "that" when the antecedent lives in the prior paragraph.

7. **Use structural anchors immediately above critical claims.** A descriptive H2 or H3 above a passage gives the retriever both a label and a boundary. Avoid clever or punning headings on pages where citation matters; the headline should restate the question the passage answers in plain language.

8. **Audit for the "buried lede" pattern.** Many pages place the most quotable summary in the conclusion or the last third of the body. AI retrievers do read full pages, but the early portion is more reliably weighed. Lift the strongest standalone sentence near the top, even if a longer expansion follows below.

9. **Write at the lowest reading grade level the content can honestly support.** Readability scoring tools (Flesch-Kincaid, Gunning-Fog, SMOG, Coleman-Liau, Dale-Chall) are useful proxies for whether a passage will survive extraction without ambiguity. Do not pursue a single target score; instead, flag passages two grade levels above the rest of the page and rewrite them down unless the complexity is load-bearing.

### Phase 3 — Schema and structured data

10. **Choose one canonical schema type for the page.** A landing page is usually a WebPage with an Organization or Product reference; a how-to is a HowTo; a comparison is a CollectionPage with `about` references to both items; a glossary entry is a DefinedTerm; a case study is an Article with a clearly identified subject Organization. Mixing types confuses crawlers without helping retrievers.

11. **Generate JSON-LD for the chosen type using a validator-backed tooling.** Hand-rolling JSON-LD scales poorly across a site. Use a generator that validates against the schema vocabulary so type-property mismatches are caught before publish.

12. **Wire schema values to the same source variables as the visible content.** A common AEO failure mode is JSON-LD that disagrees with the visible page — different author name, different price, different step count, different update date. Both surfaces should read from the same data, not be authored separately.

13. **Add FAQPage schema only for genuine, page-specific FAQs.** Generic boilerplate FAQs duplicated across pages have triggered manual actions in the past and add no signal to AI retrievers. Each FAQ entry must reflect a question a real visitor asked or a real sub-question of the page topic. Two or three high-quality entries beat ten generic ones.

14. **Add HowTo schema when the page has discrete steps in clear order.** Each step needs a name, a clear textual instruction, and ideally a step-level anchor on the page. Do not use HowTo schema on a page where the steps are speculative ("you might consider...") rather than instructional ("first, do X").

15. **Add citation-worthy schema fields explicitly.** `datePublished`, `dateModified`, `author` (as Person with `url` and `sameAs`), `publisher` (as Organization with `logo`), `mainEntityOfPage`, and `inLanguage` are routinely consumed by AI retrievers when deciding whether to surface a page. Missing one of these does not block citation, but the page becomes harder to attribute confidently.

### Phase 4 — Citation-worthiness audit

16. **Score the page for first-party data.** AI retrievers preferentially cite pages that show original measurement, original analysis, or first-party benchmarks. A page that repackages widely available facts without adding new measurement competes with hundreds of equally-cited pages. Identify whether the page has any first-party data; if not, recommend adding at least one original chart, table, or measurement before the pass ends.

17. **Audit named-author signals.** Pages that name their author, link to an author bio with credentials, and bind the author to a verified entity (LinkedIn, university page, ORCID, recognized publication byline) get cited more reliably than anonymous ones on the same topic. If the page is anonymous, recommend a byline and an author-page link as a P0 fix.

18. **Audit recency signals.** Many AI retrievers weight recently updated content for time-sensitive topics. Ensure `dateModified` reflects substantive updates, not template republishes, and that the visible page shows a "Last updated" line near the title for topics where freshness matters (pricing, regulations, software versions, statistics).

19. **Audit internal consistency.** A page that contradicts itself across sections, or contradicts a sibling page on the same site, is risky for an AI retriever to cite — the model cannot tell which assertion the publisher endorses. Cross-check claims against the rest of the site; flag contradictions for editorial resolution.

20. **Audit fact-checkability.** Every quantitative claim should have a primary-source link or a clearly identified internal source. Vague phrases like "studies show" or "industry research suggests" with no link are downgraded by retrievers and by careful readers. Either link the source or rewrite the claim as an observation rather than a fact.

### Phase 5 — Query fan-out coverage

21. **Decompose the page's primary query into the sub-questions an AI answer engine would ask.** A user query like "how to set up multi-region failover for Postgres" is rarely answered by retrieving one passage. The retriever decomposes it into sub-questions: what is multi-region failover, why do it for Postgres, what are the patterns, what is the cost, what are the failure modes, how is it tested. List the decomposed sub-questions explicitly.

22. **Map each sub-question to a passage on the page.** If a sub-question has no corresponding passage, the page cannot be cited for that fan-out branch. Decide whether to add the passage, link to a sibling page that covers it, or accept the gap.

23. **Verify each mapped passage is self-contained.** A passage that requires three earlier paragraphs of context to make sense will not survive fan-out retrieval. Each sub-question's answer paragraph should be readable without the rest of the page.

24. **Add an explicit summary that answers the fan-out questions in order.** A short "On this page" or "Key answers" block near the top, with one-sentence answers and anchor links to the full passages, increases the chance that the page is selected for multiple fan-out branches at once.

### Phase 6 — Entity clarity

25. **Identify the canonical entity the page is about.** This is the named thing — company, product, person, concept — that the page should reinforce. Most pages have one primary entity. Pages that try to anchor to several entities at once dilute the signal.

26. **Audit for entity-name consistency.** A product referred to as "Acme Cloud", "Acme", "AcmeCloud", and "the Acme Cloud platform" within a single page scatters the entity signal. Pick one canonical form and use it everywhere visible content names the entity; allow descriptive variants only in supporting prose.

27. **Wire sameAs links in JSON-LD.** The canonical entity should have `sameAs` references pointing at its public identity surfaces — Wikipedia, Wikidata, Crunchbase, LinkedIn, GitHub organization, official social handles. This is one of the strongest signals an AI retriever uses to reconcile an entity across the web.

28. **Confirm the about page and author pages exist and resolve.** Many citation pipelines verify a publisher entity by following the `publisher` reference to an about page and confirming the organization is identifiable there. A broken or missing about page silently weakens citation chances; flag this as a fix outside the page itself.

29. **Consider an llms.txt or equivalent machine-readable index.** A discoverable plain-text file that explains what the site is, who publishes it, and which pages are canonical for which topics is increasingly used by AI retrievers as a publisher hint. Recommend adding one if the site lacks it, and reference the canonical entity name consistently inside it.

### Phase 7 — Publisher and E-E-A-T-equivalent signals

30. **Confirm the page has a visible byline.** Anonymous pages can still be cited but rank lower on author-trust signals. The byline should resolve to a real person with a credible bio.

31. **Confirm the byline person has a topical track record.** A page on infrastructure cost authored by a person whose bio shows ten prior posts on infrastructure cost is a stronger signal than the same page authored by a generalist marketer. If the author does not have a public track record, recommend either rotating the byline to someone who does or building one over time on the author page.

32. **Confirm the publisher organization is identifiable and stable.** Retrievers look for an about page, a contact path, a physical or legal address where relevant, and a consistent organization name across the site, the JSON-LD publisher block, and external profiles. Missing one of these does not block citation but accumulates risk.

33. **Confirm citation discipline within the page.** Pages that cite their sources visibly — with named studies, named publications, dated reports, and links to primary sources — earn citation more reliably than pages that synthesize sources opaquely. Demonstrate the behavior you want retrievers to do.

34. **Avoid AI-bait stuffing.** A page that retrofits a hundred "people also ask" sub-headings, lists every conceivable related question, and pads with definitions for terms it does not actually use will likely test worse than the simpler version. Retrievers and human editors increasingly detect this pattern. The do-no-harm rule of this pass is: every addition must reflect content the page genuinely supports.

### Phase 8 — Instrumentation for citation tracking

35. **Set up referrer-source logging that survives AI-search referrers.** Many AI answer surfaces send referrers that look unlike classic search referrers, sometimes with no referrer at all on click-through. Configure server-side logging to capture user-agent strings, the referer header where present, and any UTM-style parameters AI surfaces propagate.

36. **Schedule a query-log mining cadence.** If the site has internal search, customer-support transcripts, or sales-call transcripts, mine them quarterly for newly-asked questions that the page should now cover. The questions that show up in your own logs are the same fan-out branches the retrievers are decomposing externally.

37. **Schedule a brand-mention monitoring cadence.** A simple programmatic check that asks AI answer engines a small panel of canonical brand-relevant queries at a defined cadence (weekly is a reasonable default) and records whether the page is cited, paraphrased, ignored, or misrepresented. Track the trend by query, not just the absolute citation count.

38. **Decide what counts as a citation worth tracking.** A linked citation in an AI answer is one signal. A paraphrase without a link is another. A brand mention with no link is a third. The instrumentation plan should record all three categories distinctly so the team does not over-rotate on the most visible one.

39. **Resist over-attribution.** AI-search referrals are inherently undercounted and partially attributable. The instrumentation plan should label the citation metric as a directional signal, not a precise revenue attribution input. Combine it with brand-search volume and direct-traffic patterns when explaining results to a non-technical stakeholder.

### Phase 9 — Synthesize the report and stage the rewrite

40. **Rank the findings.** Three buckets are usually enough: P0 (the page cannot be cited reliably without this fix), P1 (the page is citable but underperforming), P2 (incremental polish). Resist the temptation to mark everything P0; the editor will not finish.

41. **Produce a rewrite patch the editor can apply.** For each P0 and P1 finding, write the suggested replacement passage, heading, FAQ block, or JSON-LD snippet. Do not leave the editor to guess what "improve extractability" means.

42. **Stage the rollout.** Land the structural and schema fixes first (they are reversible and low-risk), then the content rewrites (they change visible meaning and need editorial review), then the instrumentation (no point shipping a dashboard before the fixes that will move it). Each stage has a measurable check before the next stage ships.

43. **Plan a re-pass in three months.** The AI-search landscape changes faster than the classic SERP landscape — new retrievers, new schema fields, new platform behavior. The report ends with a calendar note to re-run the pass on the same page in roughly ninety days, with explicit notes on what to compare against this baseline.

## Inputs

- **target_page** (required): The page to optimize. URL, full body text, or both.
- **page_purpose** (required): What the page must accomplish for the business. Sharpens trade-offs between citation-friendliness and conversion-friendliness.
- **primary_queries** (optional): Classic queries the page already targets. Used as the seed for fan-out expansion. If omitted, the skill derives them from the page itself.
- **brand_entity** (optional but recommended): Canonical entity name plus known sameAs URLs. Materially improves the entity-clarity findings.
- **page_type** (optional): The shape of the page (landing, how-to, comparison, etc.). Routes to the right schema and structure tactics.
- **tracking_stack** (optional): Analytics and tracking tools available. Scopes the instrumentation recommendations to what the team can actually deploy.

## Outputs

The skill produces four artifacts.

1. **Optimization report** — extractability findings, schema gaps, citation-worthiness audit, fan-out coverage matrix, entity-clarity findings, publisher-signal review, and a ranked change list with before-and-after examples.
2. **Rewrite patch** — concrete passages, headings, FAQ blocks, bylines, and JSON-LD snippets the editor can apply.
3. **Instrumentation plan** — referrer logging, query-log mining cadence, brand-mention monitoring panel, and the dashboard structure.
4. **Optimization spec JSON** — machine-readable issues, fixes, schema patches, and tracking events for engineering handoff.

The report is the most-read artifact. Write the rewrite patch and instrumentation plan first; the report then summarizes and prioritizes them rather than restating findings twice.

## Examples

**Example 1: SaaS landing page for an infrastructure-cost product**

Input: a landing page for an infrastructure-cost-monitoring product, purpose is qualified demo signups, page is already ranking on three head terms but receives zero AI-answer citations.

The skill returns a report that finds: the primary claim ("we cut cloud cost by X") sits in the third fold under a marketing-style headline, no author is named, JSON-LD is missing entirely, and the page contains no original benchmark data. The rewrite patch lifts a one-sentence summary of the value claim into the first fold, adds a byline to the head of product with a sameAs reference to LinkedIn, adds Organization plus SoftwareApplication schema with `aggregateRating` only where ratings are real, and embeds a small first-party benchmark chart sourced from the product's own anonymized customer data. Query fan-out coverage adds three short passages — what the product measures, how it differs from generic cloud-bill analysis, and what the implementation effort looks like — each behind its own H2. Instrumentation adds server-side AI-referrer logging and a weekly panel of ten queries (mix of brand and category) tracked against a baseline citation count.

**Example 2: How-to article in a developer knowledge base**

Input: a how-to article on configuring a specific authentication flow, purpose is to support self-serve users and earn citations from AI-coding-answer surfaces, page is technically accurate but written as a long-form narrative with code samples scattered throughout.

The skill returns a report that finds: the steps are present but not numbered or structurally separated, code blocks are not labelled with their language and surrounding intent, the page has no HowTo schema, prerequisites are buried in the middle of the prose, and the article's `dateModified` is over a year old despite the underlying API having shipped a v2. The rewrite patch reorganizes the body into a labelled prerequisites block, a numbered step list with one self-contained code block per step, an explicit troubleshooting section keyed to the most common error messages, and HowTo plus Article JSON-LD wired to the same step names. Citation-worthiness audit recommends adding the named author (an engineer on the team that owns the flow), a `datePublished` and accurate `dateModified`, and a link to the upstream API changelog as a primary source. Instrumentation adds query-log mining of the support inbox to find new sub-questions every quarter.

## Limitations

- The skill cannot guarantee citation in any specific AI answer surface. Retrievers' selection logic is opaque, frequently updated, and varies by query and locale. The pass improves the page's odds; it does not buy a placement.
- Specific thresholds in this skill (paragraph length, fan-out branch count, reading grade level) are conservative heuristics drawn from public discussion of generative engine optimization. Niches with heavy regulatory or technical density may justify stricter or looser numbers; the pass flags this rather than enforcing a single rule.
- The AI-search landscape changes quickly. New retrievers, new schema vocabulary fields, and new platform behavior may make some recommendations stale within months. The pass ends with a re-run schedule for exactly this reason. The methodology is stable; specific tactics are not.
- This pass does not generate first-party data. If the citation-worthiness audit finds the page has none, the fix requires real measurement or analysis that the operator must produce; the skill cannot manufacture it.
- The pass does not replace human editorial review. Suggested rewrites must be checked for accuracy, voice, legal exposure, and brand consistency before publish.
- AI-bait stuffing tactics that contradict the page's actual substance — invented statistics, padded FAQ blocks, keyword-spammed sub-headings — are out of scope by design. The skill will refuse to recommend them even when they might produce a short-term citation lift.

## Sources reviewed

- https://github.com/amplifying-ai/awesome-generative-engine-optimization
- https://github.com/luka2chat/awesome-geo
- https://github.com/DavidHuji/Awesome-GEO
- https://github.com/geotoolco/Answer-Engine-Optimization
- https://github.com/google/schemarama
- https://github.com/google/schema-dts
- https://github.com/spatie/schema-org
- https://github.com/textstat/textstat
- https://github.com/AnswerDotAI/llms-txt
- https://github.com/cdimascio/py-readability-metrics
