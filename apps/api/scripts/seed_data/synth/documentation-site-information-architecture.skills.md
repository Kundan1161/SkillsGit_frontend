---
id: skillsgit-curated/documentation-site-information-architecture
version: 1.0.0
name: Documentation Site Information Architecture
description: Design the information architecture of a documentation site — top-level navigation by reader job, doc-type segregation, search-versus-browse paths, getting-started funnel, versioning, deprecation banners, and contribution surface.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: productivity
tags:
  - niche:documentation-system-architecture
  - information-architecture
  - developer-experience
  - docs-site
  - navigation-design
  - versioning
  - contribution-model
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 5000
trigger_keywords:
  - docs site architecture
  - documentation IA
  - information architecture
  - docs navigation
  - sidebar structure
  - docs site design
  - developer docs structure
  - docs getting started
  - docs versioning
  - deprecation banner
  - docs site map
  - landing page docs
example_invocations:
  - "Design the top-level navigation for our new SDK docs site."
  - "We have 400 pages of docs growing organically — propose an IA that segregates by reader job."
  - "Plan a getting-started funnel that gets a new user to first success in under ten minutes."
  - "Our docs cover three product lines and four versions — propose a versioning and navigation model."
  - "Recommend a deprecation-banner scheme and a contribution surface for our docs site."
inputs:
  - name: product_summary
    type: text
    required: true
    description: One or two paragraphs describing the product, its main user roles, and its rough size — number of features or surface areas.
  - name: existing_content_inventory
    type: text
    required: false
    description: A list, tree, or CSV of existing doc pages. Helps the skill propose mappings rather than greenfield architecture. If absent, the skill works greenfield.
  - name: reader_personas
    type: text
    required: false
    description: Two to five short persona descriptions — role, prior knowledge, and the job they arrive at the docs to do.
  - name: constraints
    type: text
    required: false
    description: Generator (Hugo, Docusaurus, MkDocs, Antora, Sphinx, custom), search backend, hosting limits, brand or legal constraints, and any house-style IA rules.
  - name: versioning_model
    type: choice
    required: false
    description: How the product is versioned for the reader.
    choices: [single_living, semver_major, calendar, channel_stable_beta, none]
outputs:
  - name: ia_proposal
    type: markdown
    description: The information-architecture proposal — top-level sections, sidebar shapes, search-versus-browse paths, versioning plan, deprecation scheme, and contribution model — with rationale.
  - name: sitemap
    type: markdown
    description: A tree-form sitemap with URL slugs at every node, ready to hand to a generator's nav config.
  - name: open_questions
    type: markdown
    description: Decisions the team must make before the IA can be finalized, framed as binary or short-list choices.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Documentation Site Information Architecture

## When to use

Reach for this skill when someone owns a documentation site that has grown organically and is now confusing, or when a team is greenfielding docs for a new product and wants a structure that will not collapse at version four. The skill produces a top-level architecture: what sections exist at the root, what shape each section's sidebar takes, how a new reader is funneled into success, how versions and deprecation are surfaced, and how outside contributors find the door.

It is not the right tool when:

- The user wants a single page drafted. Reach for a doc-drafting skill instead.
- The user wants a content audit of existing prose quality. Reach for an editorial-review skill.
- The user wants a generator picked. This skill is generator-agnostic; it produces a model that any modern static-site generator can express.
- The user wants brand visual design. Visual decisions are downstream; this skill stops at the information layer.

Engage the skill when the request mentions navigation, sidebar, sitemap, IA, getting-started, landing, versioning, deprecation, contribution model, or "our docs are a mess." The output is a model and a sitemap, not pages of finished prose.

## How to apply

The methodology has five phases. Each phase ends in a written artifact the next phase consumes.

### Phase 1 — Name the reader jobs

1. **Enumerate the reader roles.** Most products have three to six. Common patterns: a first-time evaluator, a hands-on integrator, an operator running the thing in production, an architect choosing between options, a contributor extending the thing, a support engineer debugging a customer issue. Write each role on one line.
2. **For each role, write the *jobs to be done* on the docs.** A job is a verb-first phrase: "decide whether to adopt," "set up a development environment," "wire the SDK into a service," "diagnose an HTTP 503," "extend the auth plugin," "find the exact shape of a webhook payload." Keep jobs concrete; "learn the product" is not a job, "build the first integration in an afternoon" is.
3. **Cluster jobs by reader posture.** Four postures cover almost every job: *learning* (the reader wants to be taught), *doing* (the reader wants to finish a task they already understand), *looking up* (the reader wants a fact fast), and *understanding* (the reader wants to grasp the model or the trade-offs). Note each job's posture.
4. **Verify the four-doc-type framework fits.** The four postures map cleanly onto four document shapes used widely in the field: study-oriented lessons, task-oriented recipes, information-oriented lookups, and understanding-oriented discussions. Each shape has different prose, different navigation, and different ranking in search. Keep them segregated; mixing them is the root cause of most bad docs sites.
5. **Reject jobs that are not docs jobs.** If a job belongs in support, in onboarding software, in marketing, or in a sales conversation, write it down separately and remove it. A docs site cannot be a marketing site, a community forum, and a status page at once without collapsing under its own navigation.

### Phase 2 — Choose the top-level sections

6. **Pick a primary axis.** Two choices dominate: organize the top level *by reader job* (Get Started, Build, Operate, Reference, Extend) or *by product surface* (API, CLI, SDKs, Dashboard, Integrations). Prefer reader-job for products with one tightly-coupled offering. Prefer product-surface for platforms whose surfaces are used by different audiences. Mixing the axes at the top level is a common error; the result is a sidebar where users cannot predict where anything lives.
7. **Hold the top level to five to seven items.** Eight or more and the eye cannot scan it; four or fewer and the structure is hiding work the reader will have to do anyway. Common shapes that fit the budget: *Get Started* — *Concepts* — *Guides* — *Reference* — *Changelog*; or *Tutorials* — *How-to* — *Reference* — *Explanation* — *Releases*; or per-surface tabs (API / CLI / SDK / Dashboard) with the same internal shape.
8. **Decide once whether *Get Started* is a top-level section or the landing page's only content.** Two patterns are common. Pattern A: the landing page is a hub with four to six cards, and *Get Started* is a sibling section. Pattern B: the landing page itself runs the new reader through quickstart, and the top-level nav skips it. Either works; the failure mode is to do both, which forks the funnel.
9. **Treat Reference as its own region.** Reference content reads differently — high-density tables, alphabetical or surface-based ordering, deep linking from search. It deserves its own sidebar shape and ideally its own URL prefix so search and analytics can treat it distinctly.
10. **Place Concepts/Explanation behind Get Started.** Readers who land cold rarely want a concept page first; they want to see the thing run. Concepts are the second visit, not the first. Place them third or fourth in the top-level order.

### Phase 3 — Shape each section's sidebar

11. **Get Started: one path, time-boxed.** The sidebar should show three to five steps, numbered if the generator supports it. Quickstart first, with a stated time budget. Then a *first integration* page. Then a *what next* hub linking forward into Build and Reference. Do not branch the sidebar here; branching collapses funnels.
12. **Guides / How-to: organized by task family.** Group by what the reader is *doing*, not by what part of the product is involved. "Authenticate users" trumps "Auth SDK." Use a two-level sidebar: families at the top, individual recipes nested. Keep each recipe single-purpose; a how-to with branching paths is two how-tos.
13. **Concepts / Explanation: a linear-but-skippable reading order.** Use a flat list of essays; the reader should be able to read any one without needing the previous. Open each essay by stating the question it answers ("Why do we use signed URLs?"). Cross-link to how-tos for action, not to other concepts.
14. **Reference: structure mirrors the surface.** API reference follows the OpenAPI tag/operation tree. CLI reference follows the command tree. SDK reference follows the package/class tree. Auto-generation is strongly preferred over hand-rolled reference; the maintenance gap between code and prose is the primary defect in reference docs.
15. **Tutorials: one promise per tutorial.** A tutorial sidebar should not exceed a handful of entries. Each tutorial has a single outcome named in its title. Resist a sidebar tree more than two levels deep here; tutorials are linear journeys, not lookup pages.
16. **Use exactly one navigation control per region.** Two competing nav elements — sidebar tree plus tabs plus breadcrumbs plus on-page TOC — overwhelm the reader. Choose the smallest set that works for each region: a linear sidebar in Get Started, a two-level sidebar in Guides, a flat list in Concepts, a deep tree plus a search-first message in Reference.

### Phase 4 — Decide on cross-cutting concerns

17. **Search versus browse.** The reader who knows the term searches; the reader who is exploring browses. Budget for both. Search must be present on every page, must support keyboard activation (slash-key is the de-facto default), and must rank Reference and How-to high while down-ranking Concepts. Browse is the sidebar tree plus the landing hub. Track on the analytics side: what fraction of sessions use search? Above thirty percent and your IA is failing to surface what users want.
18. **Versioning model.** Pick one of: *single living docs* (no version selector — appropriate for SaaS with strong backwards compatibility), *semver major* (separate docs trees per major — appropriate for libraries with breaking changes), *channel* (stable vs. beta vs. next — appropriate for frameworks), or *calendar* (year-based — appropriate for platform-as-a-service with quarterly cuts). Surface the choice in the header; default to *current*. When a reader lands on an old version, show a banner that names the current version and links to the same page on it.
19. **Deprecation banners.** Three states need visible markers: *deprecated* (still works, will be removed), *removed in this version* (does not work here, was here last version), and *experimental / beta* (works but may change). Use three distinct banner colors and three distinct verbs. State the timeline; "deprecated, will be removed in 3.0 (currently shipping 2.4)" beats "deprecated, removal date TBD."
20. **Landing page model.** The home page is the most-trafficked page on most docs sites. Treat it as a router, not a marketing piece. A useful default: a single primary call-to-action (Quickstart), three to six cards by reader job, a search box, and a row of useful entry points (Reference index, Changelog, Status). Skip the carousel; the reader did not come to scroll.
21. **404 and search-fail pages.** When a reader hits a dead URL or an empty search, do not say "page not found." Show the top five most-visited pages, the search box pre-filled with the term the reader typed, and a link to file an issue. These pages are the docs site's user-research surface; instrument them.
22. **i18n posture.** Decide before launch: English-only, English-primary with translations, or fully localized. The cost of retrofitting localization is high. If the answer is "not now," still pick URL slugs that will allow `/en/`, `/ja/`, etc. without breaking existing inbound links.
23. **Contribution model.** The docs site should expose two doors: an *edit this page* link in the page header pointing at the source file in the repo, and an *issue* link pointing at a templated issue form pre-filled with the page URL. Both reduce drive-by contributions by an order of magnitude without them, and both are cheap to add. State the contribution license up front in the contributor guide.

### Phase 5 — Express the model as a sitemap and an IA proposal

24. **Draw the sitemap as a tree, two levels visible, URL slugs at every node.** Slugs are forever; treat them as a public interface. Prefer short, kebab-case, lowercase slugs; avoid putting reader role or product version in the slug (those belong in path prefixes or query strings handled by the generator).
25. **Spell out the rules in prose.** A sitemap without an IA proposal in prose is a map without a key. The proposal should answer: what is the primary axis, what each top-level section contains, what each section's sidebar shape is, how versions are surfaced, how deprecation is surfaced, how readers contribute, and how search ranks across sections.
26. **List the open questions explicitly.** Almost every IA exercise surfaces three or four decisions the team must own. Common open questions: "do API and SDK docs share a sidebar?", "is the changelog one page or one page per release?", "do we expose the developer dashboard's docs in this site or its own?", "is the marketing landing distinct from the docs landing or merged?"
27. **Express the proposal at two levels of detail.** A one-page executive summary for the team owner, and a detailed proposal with one page per section. The executive summary is what gets signed off; the detailed proposal is what implementers work from.
28. **Do not author content yet.** This skill stops at the IA. Page-level drafts are a separate, downstream step, owned by a doc-drafting skill or by writers on the team.

## Inputs

- **`product_summary`** — required. Without it the skill cannot guess audience or section count. Two paragraphs is plenty.
- **`existing_content_inventory`** — optional but strongly recommended for retrofits. The skill maps existing pages into the new IA in an annex and flags pages that have no home; those are migration tickets.
- **`reader_personas`** — optional. Without it the skill applies a default of three personas — evaluator, integrator, operator — and flags the assumption.
- **`constraints`** — optional. If the generator is named, the sitemap is expressed in the generator's idioms (Docusaurus sidebar items, MkDocs nav YAML, Antora navigation files); if not, generator-agnostic markdown.
- **`versioning_model`** — optional. If absent, the skill recommends one based on `product_summary` and flags the recommendation as a decision point.

## Outputs

- **`ia_proposal`** — the prose model: primary axis, section descriptions, sidebar shapes per section, version model, deprecation model, contribution model, search-versus-browse model, open questions.
- **`sitemap`** — a tree with URL slugs at every node, ready to translate to the generator's nav config.
- **`open_questions`** — a short list of binary or three-choice decisions the team must make to finalize the IA.

## Examples

### Example 1 — Retrofit for a growing SaaS API

**Input.** A summary describes a SaaS billing API with a CLI, three SDKs, and a dashboard. The team has 220 existing pages in a flat `/docs/` folder, organic growth over three years, growing complaints from new users that "getting started is impossible."

**Result.** Reader-job axis chosen because the offering is one product with one audience (developers integrating billing). Top level: *Get Started* — *Concepts* — *Guides* — *Reference* — *Changelog*. Reference subdivides by surface: *API* / *CLI* / *SDKs* / *Dashboard*. The 220 existing pages are mapped to the four-shape grid in an annex; thirty-eight are flagged as *concept disguised as how-to* (rewrite needed) and twelve as *orphans* (probably delete). Versioning model: single living docs with a date-stamped changelog, because the API maintains strict backwards compatibility. Deprecation scheme: banner on the page, plus a Concepts page named *Lifecycle and deprecation*. Open questions list contains: "does the dashboard need its own docs domain?" and "is the SDK changelog merged into the API changelog or kept separate?"

### Example 2 — Greenfield for a new platform

**Input.** A platform team launching an internal-plus-external developer platform with three product surfaces (a workflow engine, an event bus, an identity service) used by different audiences within enterprise customers.

**Result.** Product-surface axis chosen because the three surfaces have non-overlapping audiences. Top-level tabs: *Workflow Engine* / *Event Bus* / *Identity Service* / *Platform Reference* / *Status*. Each product surface tab has the same internal shape: *Get Started* (3 pages) — *Concepts* (5–8 essays) — *How-to* (recipe library, two-level sidebar) — *Reference* (auto-generated from the OpenAPI spec) — *Changelog*. A platform-level *Concepts* hub explains how the three surfaces compose. Versioning model: stable / beta channel, because the platform ships features behind feature flags. Deprecation banners use the standard three states. Contribution model: edit-on-GitHub for external surfaces, edit-on-internal-Gitea for internal-only pages. Open questions: "does the platform have one search index or three?" and "is the changelog cross-surface or per-surface?"

### Example 3 — Migration target for a library

**Input.** An open-source library with three major versions in active use (v1, v2, v3-rc), docs currently a single tree on Read the Docs with deeply nested folders.

**Result.** Reader-job axis. Top level: *Tutorials* — *How-to* — *Reference* — *Explanation* — *Releases*. Versioning model: semver major with a version selector in the header; stable defaults to v3 once it is out of release-candidate. Each version's docs tree is built from a branch in the repo, allowing parallel publishing. Deprecation banners on v1 and v2 announce end-of-life dates. *Releases* section is a flat list of changelog pages, one per minor version, with breaking changes called out at the top. Sample sitemap provided with full slugs. Open questions: "do we keep v1 docs alive after v1 end-of-life?" and "do we host translations on the same domain or subdomains?"

## Limitations

- This skill produces a model, not a finished site. Translating the model into a specific generator's configuration is a separate, downstream step.
- The skill assumes the product is real and stable enough to have nameable surfaces. For a product whose surfaces are still in flux, the IA should be re-run when the surfaces settle; an IA designed against a moving target ages badly.
- The skill recommends but cannot enforce. A team that ignores the doc-shape segregation rule (Phase 1, step 4) will produce a site that drifts back into the original mess; the IA proposal includes a *governance* note for this reason.
- Search ranking decisions across sections are described in principle here; tuning them is a job for whoever owns the search backend and depends heavily on the backend chosen.
- Analytics-driven IA refinement is out of scope of the initial design. Plan to re-run this skill after six months of live data; the initial cut is a hypothesis, not a final answer.

## Sources reviewed

The methodology in this skill was synthesized after reviewing the following projects. None of their prose, structure, or assets was copied. Each contributed a pattern or a constraint that informed the steps above; the synthesis is original.

- https://github.com/evildmp/diataxis-documentation-framework — four-doc-type framework reference (CC-BY-SA 4.0)
- https://github.com/facebook/docusaurus — MIT (code), CC-BY-4.0 (docs)
- https://github.com/squidfunk/mkdocs-material — MIT
- https://gitlab.com/antora/antora — MPL-2.0
- https://github.com/google/docsy — Apache-2.0
- https://github.com/readthedocs/readthedocs.org — MIT
- https://github.com/writethedocs/www — see repo LICENSE.md
- https://github.com/Redocly/redoc — MIT
- https://github.com/stoplightio/elements — Apache-2.0
