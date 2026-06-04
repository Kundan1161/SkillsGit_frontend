# Report — Documentation System Architecture (Wave-4 methodology-recovery)

## Skills produced

Four skills authored in `D:\skillsgit\apps\api\scripts\seed_data\synth\`:

1. `documentation-site-information-architecture.skills.md` — top-level nav by reader job, sidebar shapes, search-vs-browse, versioning, deprecation, contribution model.
2. `docs-as-code-pipeline-architect.skills.md` — repo layout, authoring lints, CI checks, preview deploys, search indexing, analytics, contributor experience.
3. `legacy-docs-migration-planner.skills.md` — audit by doc shape, IA re-map, redirects, sequencing, dual-publish, retirement.
4. `developer-portal-architect.skills.md` — integrator journey, day-one page set, OpenAPI reference integration, code-block discipline, SDK + sample-app strategy, changelog/versioning/deprecation.

All four use `category: productivity`, first tag `niche:documentation-system-architecture`, `license_type: free`, body sized in the 300-600-line target band. Each carries a `## Sources reviewed` block with permissive-license tags.

## Sources reviewed (with license tags)

| Source | License | Contribution |
|---|---|---|
| github.com/evildmp/diataxis-documentation-framework | CC-BY-SA 4.0 | Read + cited only; four-doc-type framework as concept, no prose, no name |
| github.com/facebook/docusaurus | MIT (code) / CC-BY-4.0 (docs) | Site structure conventions, sidebar, versioning, plugins |
| github.com/squidfunk/mkdocs-material | MIT | Navigation, instant search, content tabs, code-block patterns |
| gitlab.com/antora/antora | MPL-2.0 | Component-version model, multi-repo aggregation, playbooks |
| github.com/google/docsy | Apache-2.0 | Hugo theme conventions for technical docs |
| github.com/readthedocs/readthedocs.org | MIT | Versioned-docs hosting, build pipelines |
| github.com/writethedocs/www | repo LICENSE.md | Community conventions for docs-as-code |
| github.com/Redocly/redoc | MIT | API reference rendering, three-panel layout, OpenAPI integration |
| github.com/stoplightio/elements | Apache-2.0 | API reference + markdown content mix, multi-spec versions |
| github.com/errata-ai/vale | MIT (referenced in pipeline skill only) | Prose-linter conventions |
| github.com/DavidAnson/markdownlint | MIT (referenced in pipeline skill only) | Structural lint conventions |

## Patterns drawn (synthesized, not copied)

- **Four-shape doc segregation** as the foundational organizing principle. The CC-BY-SA framework name is *never used in body content*. The body describes the framework generically as "four-doc-type framework: tutorials, how-tos, references, explanations" and (in IA skill, step 4) as "study-oriented lessons, task-oriented recipes, information-oriented lookups, understanding-oriented discussions." Citation lives only in `## Sources reviewed`.
- Reader-job axis vs. product-surface axis at top level (IA skill, phase 2).
- Five-to-seven top-level items, two-level sidebar depth budget.
- Search-versus-browse instrumentation as IA-health signal.
- Versioning models: single-living, semver-major, channel, calendar.
- Three-state deprecation banners with explicit timeline.
- Docs-as-code pipeline stages: structural lint, prose lint, terminology check, spell check, doc-type lint, broken-link CI (internal per-PR, external nightly), preview deploys, smoke tests post-deploy.
- Redirect-as-public-interface discipline: forever URLs, lint the redirect map for cycles/chains/404s.
- Dual-publish window length tied to SEO equity (one week minimal, two for heavy equity).
- Integrator first-hour / return-hour / debug-hour journey shaping the portal page set.
- OpenAPI spec as canonical source-of-truth; reference auto-generated, not hand-authored.
- Code-block discipline: language tags required, language-tabs for multi-language, copy-pastable, output shown, samples tested in CI.

## Methodology-vs-expression boundary checks

- **Trademarked methodology name**: searched all four bodies — "Diataxis" / "Diátaxis" appears zero times in body content. It appears only as part of the canonical GitHub URL in the `## Sources reviewed` block (`evildmp/diataxis-documentation-framework`), which is the repository's identifier, not a prose use of the mark.
- **CC-BY-SA framework prose**: no sentences from the framework's `tutorials.rst`, `how-to-guides.rst`, `reference.rst`, or `explanation.rst` were fetched and embedded. The four shapes are described in the synthesized vocabulary of this corpus (e.g., "study-oriented lessons / task-oriented recipes / information-oriented lookups / understanding-oriented discussions"; "the reader is a learner / competent and goal-driven / auditing or scanning / wants understanding"). No close paraphrase of canonical definitions.
- **Other framework prose**: the closest brush is the four-line *what it is / install / run / where to read more* README skeleton, which is a widespread industry convention pre-existing the cited templates and is expressed in this corpus's own structure.
- **No verbatim chunks** from any fetched README, license text, or doc page. Each WebFetch result was read once and discarded; the bodies were written from synthesized notes.
- **License compatibility**: free-tier skills authored under the marketplace's terms; sources are cited but not reproduced, so the CC-BY-SA share-alike clause is not triggered (no derivative work of CC-BY-SA prose). The MIT / Apache / MPL / CC-BY-4.0 sources are cited for attribution per their terms.

## Frontmatter and structural compliance

- All four files have `id: skillsgit-curated/<slug>`, `version: 1.0.0`, `license_type: free`, `pricing: { currency: USD, support_included: false }`.
- `category: productivity` on all four.
- First tag is `niche:documentation-system-architecture`; each file carries 6 additional tags (within the 0-10 budget).
- Required body sections present on all four: `## When to use`, `## How to apply`. Plus recommended `## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources reviewed`.
- AI requirements: `required_models: [claude-opus-4-7]`; compatible models declared; `min_context_tokens: 32000`; `estimated_tokens_per_invocation: 5000` (slightly above the related tech-doc-drafter, reflecting larger output artifacts).
- 5 example invocations each; trigger-keyword lists in the 10-12 range.
- Bodies sized 300-600 lines per the brief.

## Confidence

- **High** on framework-name avoidance and license-clean expression.
- **High** on coverage of the niche: IA, pipeline, migration, and portal are the four standard sub-problems in documentation-system architecture, and they compose cleanly without overlap.
- **High** on frontmatter validity against `prompts/shared/skills-md-spec.md`.
- **Medium-high** on methodology fidelity: the synthesized methodology aligns with industry-common practice as represented across the cited projects, but a docs-engineering practitioner reviewer would tighten specific tooling recommendations (Vale config templates, Algolia tuning details, specific Antora playbook fields). These details are intentionally out of scope at this level; they belong in lower-level companion skills.
- **Medium** on uniqueness vs. the existing `prod-tech-doc-drafter` skill: that skill is page-level (drafts a single doc); these four are system-level (design the surrounding site, pipeline, migration, portal). The boundary is clean — the drafter skill is cited as the natural downstream collaborator in the IA skill's Phase 5 closing step.
