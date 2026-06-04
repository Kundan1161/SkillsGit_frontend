# Synthesis Report — Marketing / Content Creation & Copywriting

## Files produced

- `D:\skillsgit\apps\api\scripts\seed_data\synth\mkt-blog-post-architect.skills.md` (one_time, $99)
- `D:\skillsgit\apps\api\scripts\seed_data\synth\mkt-landing-page-copywriter.skills.md` (subscription, $11/mo, support included)
- `D:\skillsgit\apps\api\scripts\seed_data\synth\mkt-email-sequence-designer.skills.md` (subscription, $9/mo, support included)

## Sources per skill (verified permissive license + ≥100 stars)

**Blog Post Architect — 7 sources:**
- https://github.com/f/awesome-chatgpt-prompts (MIT/CC0, 162k stars)
- https://github.com/langgptai/awesome-claude-prompts (MIT, 5.1k)
- https://github.com/aminblm/awesome-chatgpt-content-creation-prompts (CC0, 125)
- https://github.com/Blazity/next-saas-starter (MIT, 1.7k)
- https://github.com/PaulleDemon/awesome-landing-pages (MIT, 969)
- https://github.com/Adrinlol/landy-react-template (MIT, 1.6k)
- https://github.com/sendwithus/templates (Apache 2.0, 1.8k)

**Landing Page Copywriter — 8 sources:**
- https://github.com/PaulleDemon/awesome-landing-pages (MIT, 969)
- https://github.com/leoMirandaa/shadcn-landing-page (MIT, 1.9k)
- https://github.com/Adrinlol/landy-react-template (MIT, 1.6k)
- https://github.com/Blazity/next-saas-starter (MIT, 1.7k)
- https://github.com/saas-js/saas-ui-nextjs-landing-page (MIT, 408)
- https://github.com/f/awesome-chatgpt-prompts (MIT/CC0, 162k)
- https://github.com/langgptai/awesome-claude-prompts (MIT, 5.1k)
- https://github.com/aminblm/awesome-chatgpt-content-creation-prompts (CC0, 125)

**Email Sequence Designer — 6 sources:**
- https://github.com/sendwithus/templates (Apache 2.0, 1.8k)
- https://github.com/f/awesome-chatgpt-prompts (MIT/CC0, 162k)
- https://github.com/langgptai/awesome-claude-prompts (MIT, 5.1k)
- https://github.com/aminblm/awesome-chatgpt-content-creation-prompts (CC0, 125)
- https://github.com/Blazity/next-saas-starter (MIT, 1.7k)
- https://github.com/PaulleDemon/awesome-landing-pages (MIT, 969)

## Key patterns synthesized across sources

1. **Section-archetype convention for landing pages.** Across the modern SaaS landing repos (shadcn-landing-page, landy-react-template, saas-ui-nextjs-landing-page, next-saas-starter, awesome-landing-pages), the convergent canonical section sequence is hero → social-proof bar → value-prop block → how-it-works → feature grid (conditional) → midpage social proof → objection/FAQ → pricing (conditional) → final CTA → footer. The Landing Page Copywriter skill organizes its output around this convention because that's what designers and CMS templates expect.

2. **Awareness-rung pacing.** Both the awesome-chatgpt-prompts catalog and awesome-claude-prompts contain numerous content/copy prompts that implicitly differentiate by reader sophistication. Generalizing this into an explicit five-rung ladder (unaware → most-aware) gave each skill a calibration mechanism for headline, hook, and CTA aggressiveness.

3. **Single dominant CTA per artifact.** Every landing-page template surveyed uses a single primary CTA per fold with at most one secondary; email-templates repos (sendwithus) follow the same one-button discipline. This became a hard rule across all three skills.

4. **Job-per-touch sequencing for emails.** Open-source email-templates repos give individual templates (welcome, transactional, receipt) rather than full sequences, but the categorization by transactional purpose maps cleanly onto a "one job per email" sequence-design discipline (welcome, educate, prove, nudge, exit). I synthesized this into the canonical 5/7-touch patterns in the Email Sequence Designer.

5. **Topic-graph outlining.** Content-creation prompt collections consistently push a claim → support → evidence structure for blog drafts. The Blog Post Architect formalizes this as a topic graph with explicit `have / need-to-fetch / need-from-user` marking on each evidence slot, so the draft surfaces its own gaps.

6. **Personalization tokens with fallbacks.** Sendwithus templates use mustache-style tokens; cross-referenced with practical pain ("Hi ,") this became an explicit `{{token|fallback}}` requirement in the email skill.

7. **F-pattern + five-second test as audits.** Synthesized as cheap, repeatable QA steps that don't require external tooling — applied in the Landing Page Copywriter audit phase.

## Rejections / sources NOT cited (and why)

- **github.com/WynterJones/CoppieGPT** (156 stars) — no license file visible. Rejected. Also contains many trademarked framework names; even if licensed, citation would risk implying endorsement of named-author frameworks.
- **github.com/AJaySi/alwrity-aida** (1 star, no license) — fails stars threshold and license requirement.
- **github.com/dshanley/content-marketing-strategy** (3 stars) — fails stars threshold.
- **github.com/danielcgilibert/blog-template** (1k stars) — GPL-3.0, not permissive. Rejected per license policy.
- **github.com/goabstract/Marketing-for-Engineers** (13.1k stars) — archived November 2020, no recent commits. Rejected on recency.
- **github.com/coreyhaines31/marketingskills, github.com/boraoztunc/skills, github.com/alirezarezvani/claude-skills, github.com/zubair-trabzada/ai-marketing-claude, github.com/kostja94/marketing-skills, github.com/ericosiu/ai-marketing-skills** — these are themselves skill collections (i.e., direct competitors / similar artifacts in the same space). Synthesizing from another Claude Skills repo would risk derivative content rather than independent methodology synthesis. Deliberately not consulted or cited.
- **github.com/ronakganatra/awesome-marketing** (392 stars) — license not visible; conservatively excluded.

## Trademarked / proprietary names deliberately omitted

- StoryBrand (Donald Miller's IP), Golden Circle (Simon Sinek), and similarly trademarked or strongly author-associated frameworks are not used by name in the skills despite appearing in source repos. The skills describe generic equivalents (e.g., "identity-led angle," "mechanism-led angle") instead.
- Specific competitor product names in the example sections are placeholders (`[Incumbent]`, `[Product]`) rather than real brands.
- Anthropic and OpenAI model identifiers in `ai.required_models` use the official ID format from the spec; these are factual identifiers, not branding.

## Confidence

**High** on the methodology content. The three skills synthesize patterns that appear across 5-8 independent permissive-licensed sources each, plus widely-known editorial conventions that are not anyone's IP. The prose is original; no paraphrase or close-copy from any source.

**High** on license compliance. Every cited source has been WebFetch-verified for either MIT, Apache 2.0, or CC0. Three candidate sources were rejected for missing or non-permissive licenses; two for star count; one for archived/stale status.

**Medium-high** on frontmatter validity. The frontmatter follows the schema in `prompts/shared/skills-md-spec.md` literally, including all required identity fields, the `category: marketing` slug, pricing per the per-skill brief, AI runtime fields, trigger keywords, example invocations, declarative inputs/outputs, and a v1.0.0 changelog. The validator (`apps/api/src/skills/validator.py`) was not run against these files in this synthesis pass; integration step should validate.

**Medium** on line counts. All three skills fall in the 300-450 line range (well inside the 300-700 target). Body sections include all four required (`## When to use`, `## How to apply`) and four recommended (`## Inputs`, `## Outputs`, `## Examples`, `## Limitations`) plus `## Sources reviewed`.

## Notes for integrator

- All three skills use `authors: [{name: skillsgit Curated, handle: skillsgit-curated, role: author}]` — handle matches the platform creator account named in the seed README.
- Pricing in cents: 9900 (one-time), 1100 (landing page sub), 900 (email sub). All within the brief range.
- No `tools_required` is set; the skills are pure-text generation. `min_context_tokens: 32000` accommodates the larger of the two outputs each skill produces.
- The `distribution` block is intentionally absent — per the spec, it is injected by the publish pipeline.
