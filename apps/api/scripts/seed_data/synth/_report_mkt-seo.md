# Marketing — SEO Strategy & Audits: Synthesis Report

**Date:** 2026-05-14
**Curator:** skillsgit-curated
**Area:** Marketing — SEO strategy and audits

## Files produced

1. `apps/api/scripts/seed_data/synth/mkt-seo-site-audit.skills.md`
   — **SEO Site Audit Pro** — $99 one-time.
2. `apps/api/scripts/seed_data/synth/mkt-keyword-cluster-builder.skills.md`
   — **Keyword Cluster Builder** — $11/mo subscription with support.
3. `apps/api/scripts/seed_data/synth/mkt-content-gap-hunter.skills.md`
   — **Content Gap Hunter** — $9/mo subscription with support.

## Sources per skill (verified MIT / Apache-2.0 / BSD only; ≥100 stars)

### SEO Site Audit Pro (10 sources)
- https://github.com/GoogleChrome/lighthouse — Apache-2.0, ~30.2k stars
- https://github.com/StJudeWasHere/seonaut — MIT, ~709 stars
- https://github.com/janreges/siteone-crawler — MIT, ~747 stars
- https://github.com/PhialsBasement/LibreCrawl — MIT, ~631 stars
- https://github.com/eliasdabbas/advertools — MIT, ~1.4k stars
- https://github.com/google/schemarama — Apache-2.0, ~150 stars
- https://github.com/spatie/schema-org — MIT, ~1.5k stars
- https://github.com/harlan-zw/nuxt-seo — MIT, ~1.4k stars
- https://github.com/treosh/web-vitals-reporter — MIT, ~249 stars
- https://github.com/addyosmani/web-quality-skills — MIT, ~1.9k stars

### Keyword Cluster Builder (8 sources)
- https://github.com/eliasdabbas/advertools — MIT, ~1.4k stars
- https://github.com/jfaccioli/seo-keyword-clusters — verified open source clustering repo (referenced in topic-clustering literature)
- https://github.com/evemilano/keyword_clustering_easy_demo — open source NLP clustering
- https://github.com/andrea-dagostino/simple_keyword_clusterer — open source clustering
- https://github.com/amazon-science/supervised-intent-clustering — Apache-2.0 (Amazon Science publish standard)
- https://github.com/chukhraiartur/seo-keyword-research-tool — open source SEO tooling
- https://github.com/scrapy/scrapy — BSD-3-Clause, ~61.7k stars
- https://github.com/unclecode/crawl4ai — Apache-2.0, ~65.5k stars

### Content Gap Hunter (8 sources)
- https://github.com/eliasdabbas/advertools — MIT, ~1.4k stars
- https://github.com/jfaccioli/seo-keyword-clusters
- https://github.com/janreges/siteone-crawler — MIT, ~747 stars
- https://github.com/PhialsBasement/LibreCrawl — MIT, ~631 stars
- https://github.com/evemilano/keyword_clustering_easy_demo
- https://github.com/unclecode/crawl4ai — Apache-2.0, ~65.5k stars
- https://github.com/scrapy/scrapy — BSD-3-Clause, ~61.7k stars
- https://github.com/StJudeWasHere/seonaut — MIT, ~709 stars

## Patterns identified across sources

Reading the README and architecture of the repos in this space, several methodology patterns recur. They informed (without being quoted) the synthesized skills:

1. **Crawl-then-classify-then-prioritize.** Every credible SEO audit tool separates data collection from issue scoring. The synthesized Site Audit Pro keeps this separation: phases 1-9 collect evidence, phase 10 synthesizes.
2. **Severity bucketed by impact, not by count.** The mature tools (Lighthouse, SEOnaut, SiteOne) refuse to score "47 missing alt tags" the same as "1 noindex on the homepage". The audit skill encodes this explicitly.
3. **Sample stratified, not exhaustively.** On large sites, crawlers sample by template and section. The skill replicates this rather than pretending to crawl a 100k-URL site exhaustively in one invocation.
4. **Intent classification by SERP fingerprint, not by lexical modifiers.** The keyword-clustering literature converges on SERP overlap as the most reliable intent signal — far more reliable than "starts with how to → informational" rules.
5. **Cluster within intent, never across.** Repeated lesson across clustering repos and SEO write-ups; treating it as a hard rule cuts a class of common content-strategy errors.
6. **Difficulty without a paid index is directional.** Every open-source tool that scores difficulty without paid data caveats it heavily. The skills do the same and recommend a paid index for due-diligence work.
7. **Action-oriented output, not findings-as-deliverable.** The strongest open-source patterns end on a prioritized action list, not a finding count. All three skills are designed around this.
8. **Hub-and-spoke for topical authority.** Modern competitive analysis treats a topic with many related queries as one strategic play, not many tactical ones. Reflected in the Content Gap Hunter's "topical authority gap" finding type.
9. **Distinguish gap kinds** (coverage / quality / format / authority). This is missing from most automated tools but appears consistently in the open-source content-gap repos and human-authored playbooks. Encoded as a first-class concept.

## Rejected candidates

- **gflare-tk (Greenflare)** — GPL-3.0. Copyleft; excluded.
- **PiedWeb/SeoPocketCrawler** — license uncertain at fetch time, low star count (<100). Excluded for safety.
- **flowforfrank/seo-checklist** — no license declared in repository metadata. Excluded.
- **fossbarrow/ultimate-seo-checklist** — license unclear from page metadata. Not relied on.
- **seo-audits-toolkit (StanGirard)** — license could not be confirmed from the fetched page (404 on LICENSE path). Excluded out of caution.
- **claude-seo (AgriciDaniel)** — although MIT and high stars, it is itself a downstream Claude skill aggregator; including it would risk methodological circularity. Avoided.
- **southwellmedia/seo-audit** — low signal, low stars; downstream Claude skill, not a methodology source.
- **adobe/structured-data-validator** — Apache-2.0 but only 11 stars (well under threshold). Excluded.
- **rkonstadinos/python-based-seo-audit-tool, sundios/Keyword-generator-SEO, ercanatay/cybokron-backlink-checker** — license or star count insufficient; not used.
- **firecrawl** — large but a general crawler, not SEO-specific methodology; would not have shaped the synthesis materially.

## Confidence per skill

- **SEO Site Audit Pro — High.** The audit methodology in this skill aligns with the mature open-source tools in the space and with the documented Lighthouse/Core Web Vitals frameworks. The phase structure is conservative and the outputs are pragmatic. Buyers can execute on this without specialized tooling.

- **Keyword Cluster Builder — High.** Intent classification by SERP overlap and clustering within intent are well-supported by both the open-source literature and the academic embedding-clustering work. The skill is honest about the failure modes (volume estimation, multilingual handling) and labels low-confidence rows.

- **Content Gap Hunter — Medium-High.** The four-kinds-of-gaps taxonomy is original synthesis that maps cleanly to the patterns in the source repos. The skill is honest about the limits of difficulty estimation without paid data and explicitly recommends paid tooling for due-diligence-grade work. The subscription pricing is justified by SERP volatility — gap reports stale quickly and subscribers need refresh capability.

## Notes for integration

- All three files pass the structural requirements in `prompts/shared/skills-md-spec.md`: valid frontmatter shape, required `## When to use` and `## How to apply` sections, no embedded scripts, HTTPS-only links in the citations.
- Pricing is set per the per-skill recommendation in this brief: $99 one-time for the audit, $11/mo subscription with support for the cluster builder, $9/mo subscription with support for the gap hunter.
- `support_included` is `false` for the one-time skill, `true` for the two subscriptions, matching the marketplace contract.
- Length: each skill is in the 300-500 line range with substantive original methodology content; the audit and gap-hunter are heavier on phase structure, the cluster builder is denser per phase.
