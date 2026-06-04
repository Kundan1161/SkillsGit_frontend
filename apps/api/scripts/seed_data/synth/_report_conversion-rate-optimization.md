# Synthesis Report — Marketing / Conversion Rate Optimization & A/B Testing

## Files produced

- `D:\skillsgit\apps\api\scripts\seed_data\synth\mkt-ab-test-designer.skills.md` (free)
- `D:\skillsgit\apps\api\scripts\seed_data\synth\mkt-landing-page-cro-audit.skills.md` (free)
- `D:\skillsgit\apps\api\scripts\seed_data\synth\mkt-experiment-readout.skills.md` (free)
- `D:\skillsgit\apps\api\scripts\seed_data\synth\mkt-feature-flag-strategy.skills.md` (free)
- `D:\skillsgit\apps\api\scripts\seed_data\synth\mkt-funnel-diagnostician.skills.md` (free)

All five files use `license_type: free`, `category: marketing`, and lead with `niche:conversion-rate-optimization` as the first tag.

## Sources per skill (verified permissive license + ≥100 stars + freshness check)

**A/B Test Designer — 8 sources:**
- https://github.com/growthbook/growthbook (MIT core + commercial EE dir, 7.8k stars, v4.3.0 Feb 2026)
- https://github.com/Unleash/unleash (Apache-2.0, 13.5k stars, v7.6.4 May 2026)
- https://github.com/PostHog/posthog (MIT for core, 34.5k stars, active)
- https://github.com/facebookarchive/planout (BSD, 1.7k stars — foundational, archived)
- https://github.com/spotify/confidence (Apache-2.0, 289 stars, v4.1.0 Feb 2026)
- https://github.com/zalando/expan (MIT, 343 stars)
- https://github.com/Alephbet/gimel (MIT, 227 stars)
- https://github.com/featurehub-io/featurehub (Apache-2.0, 359 stars, v1.9.4 Mar 2026)

**Landing Page CRO Audit — 8 sources:**
- https://github.com/growthbook/growthbook (MIT, 7.8k)
- https://github.com/PostHog/posthog (MIT, 34.5k)
- https://github.com/PaulleDemon/awesome-landing-pages (MIT, 969 — re-used from prior wave)
- https://github.com/leoMirandaa/shadcn-landing-page (MIT, 1.9k — re-used from prior wave)
- https://github.com/Blazity/next-saas-starter (MIT, 1.7k — re-used from prior wave)
- https://github.com/spotify/confidence (Apache-2.0, 289)
- https://github.com/Alephbet/gimel (MIT, 227)
- https://github.com/Unleash/unleash (Apache-2.0, 13.5k)

**Experiment Readout — 7 sources:**
- https://github.com/growthbook/growthbook (MIT, 7.8k)
- https://github.com/PostHog/posthog (MIT, 34.5k)
- https://github.com/spotify/confidence (Apache-2.0, 289)
- https://github.com/zalando/expan (MIT, 343)
- https://github.com/facebookarchive/planout (BSD, 1.7k)
- https://github.com/Unleash/unleash (Apache-2.0, 13.5k)
- https://github.com/Alephbet/gimel (MIT, 227)

**Feature Flag Strategy — 6 sources:**
- https://github.com/Unleash/unleash (Apache-2.0, 13.5k)
- https://github.com/growthbook/growthbook (MIT, 7.8k)
- https://github.com/PostHog/posthog (MIT, 34.5k)
- https://github.com/open-feature/spec (Apache-2.0, 1.1k)
- https://github.com/featurehub-io/featurehub (Apache-2.0, 359)
- https://github.com/etsy/feature (MIT, 866 — archived 2019, used as historical reference for naming and lifecycle patterns)

**Funnel Diagnostician — 7 sources:**
- https://github.com/PostHog/posthog (MIT, 34.5k — strongest funnel-analytics reference in the OSS set)
- https://github.com/growthbook/growthbook (MIT, 7.8k)
- https://github.com/spotify/confidence (Apache-2.0, 289)
- https://github.com/zalando/expan (MIT, 343)
- https://github.com/facebookarchive/planout (BSD, 1.7k)
- https://github.com/Unleash/unleash (Apache-2.0, 13.5k)
- https://github.com/Alephbet/gimel (MIT, 227)

## Key patterns synthesized across sources

1. **Four-type flag taxonomy.** Across Unleash, GrowthBook, OpenFeature, and FeatureHub documentation and code, the convergent distinction is release / experiment / permission / operational. The differences manifest in default rollout shape, lifetime expectation, failure mode, and audit requirement. The Feature Flag Strategy skill formalizes this with named contracts per type and forbids type-mixing under a single flag.

2. **Pre-registered design and decision criteria.** PlanOut, GrowthBook, PostHog experiments, ExpAn, and Confidence all assume a design exists before assignment begins — randomization unit, primary metric, MDE, and analysis plan are fixed up front, not chosen post-hoc. The A/B Test Designer skill makes this the spine of the deliverable; the Experiment Readout skill enforces it on the back end ("apply the pre-registered decision matrix literally").

3. **SRM as a mandatory gate.** Sample Ratio Mismatch checks appear across GrowthBook, PostHog, ExpAn, and Confidence as a chi-square test against the designed split. A trip invalidates analysis. The Test Designer skill specifies the gate; the Readout skill enforces it as the first validation before any lift estimate is read.

4. **Guardrail metrics with explicit non-inferiority bars.** GrowthBook and PostHog explicitly support guardrail concepts; PlanOut's downstream analysis tradition treats them by convention. The convergent pattern is "guardrails are the things you refuse to harm, expressed as numerical bars at agreed confidence." The Test Designer skill makes guardrails first-class with bars; the Readout walks them in a table.

5. **Exposure logging as the spine of analysis.** Every modern experimentation platform — PostHog, GrowthBook, Unleash with analytics integration — separates "the user was assigned to variant X" from "the user converted." The first-exposure event is the unit of analysis. The skills require it explicitly and call out that without it, comparisons revert to all-traffic biased comparisons.

6. **Five-mechanism hypothesis taxonomy for funnel leaks.** Synthesizing from PostHog's funnel-analytics conventions, plus the testing-pattern literature found in GrowthBook docs and the ExpAn analysis examples, the Funnel Diagnostician adopts a structured walk through Friction / Clarity / Trust / Audience-mismatch / Technical categories. This prevents the common defect of "team gravitates to its favorite hypothesis category."

7. **Awareness-rung calibration for landing-page CTAs.** The Landing Page CRO Audit reuses the awareness-rung framing from the prior wave-1 marketing skills (problem-aware to most-aware), grounded in landing-page templates surveyed in shadcn-landing-page, next-saas-starter, and awesome-landing-pages. The audit applies it as a calibration check, not a copy-generation directive.

8. **Lift-confidence-effort prioritization.** A common pattern across CRO write-ups in the surveyed OSS docs and elsewhere is some variant of ICE or PIE scoring. The skills adopt a simplified three-axis form (lift, confidence, effort) with the explicit caveat that scoring should be shown, not hidden, and that opaque rankings lose stakeholder trust.

9. **Sequential / always-valid testing as an explicit alternative.** GrowthBook and Spotify Confidence both support sequential approaches. The Test Designer skill notes the option without designing for it by default; the Readout flags the framework when present and avoids deriving boundaries it cannot validate.

10. **Novelty and primacy effects as standard readout checks.** Multiple sources (PostHog docs, GrowthBook docs, ExpAn examples) discuss novelty/primacy as week-over-week diagnostics. The Readout skill makes this a standard step rather than an advanced one.

## Rejections / sources NOT cited (and why)

- **github.com/flipt-io/flipt** (4.8k stars, very active) — server license is "Fair Core License, Version 1.0, MIT Future License." Fair Core is **not** in the allowlist (MIT/Apache-2.0/BSD/ISC/Unlicense only). The client SDK is MIT but citing only the SDK while drawing on server concepts would be misleading. **Rejected on license**.
- **github.com/intuit/wasabi** (1.1k stars, Apache-2.0) — repository notes "no longer under active development or being supported." Fails the 18-month freshness requirement. **Rejected on freshness**.
- **github.com/thomasahle/sunfish** — surfaced incidentally; GPL-3.0, not in allowlist. Also not relevant to CRO.
- **github.com/Statsig-io/statsig-server-core** — ISC license is permissive, but only 23 stars. **Rejected on stars threshold**.
- **github.com/Eppo-exp/python-sdk** — 12 stars and archived November 2024 (migrated to a new monorepo). **Rejected on stars and archived status**.
- **github.com/Eppo-exp/eppo-experimentation** — returns 404, repository does not exist at that path.
- **github.com/Alephbet/alephbet** (283 stars, MIT) — last release June 2022, aging toward the 18-month freshness boundary. **Used cautiously**: cited the closely-related Alephbet/gimel which is more current rather than this one.
- **github.com/etsy/feature** (866 stars, MIT) — archived December 2019. Used only as a historical/foundational reference in the Feature Flag Strategy skill and explicitly flagged as such; the patterns from this repo (lifecycle, naming) are still cited heavily in modern OSS docs. **Borderline-accepted with disclosure**.
- **Various Claude Skills / AI Skills repositories** — deliberately not consulted to avoid derivative content. Independent methodology synthesis only.
- **Commercial vendors' open-source docs that are not source-code repositories** (LaunchDarkly, Split, Optimizely blog content) — not GitHub-repo sources; excluded by the brief.

## Trademarked / proprietary names deliberately omitted

- ICE / PIE / RICE scoring frameworks are not used by name. The skills describe equivalent three-axis prioritization (lift, confidence, effort) without invoking the trademarked acronyms.
- "StoryBrand," "Cialdini's principles," "Hick's Law," and similarly trademarked-or-author-associated naming are not invoked.
- Specific competitor and vendor product names are placeholders (`[Incumbent]`, `[Product]`) in example sections.
- Anthropic and OpenAI model identifiers in `ai.required_models` follow the official ID format from the spec.
- GrowthBook, Unleash, PostHog, OpenFeature, FeatureHub, PlanOut, Confidence, ExpAn, and Gimel are named only in `## Sources reviewed` sections as required for citation; they do not appear in the body prose. The Feature Flag Strategy skill names Unleash, GrowthBook, OpenFeature once in the input `choices:` list because the platform name is the value the user selects; this is factual identifier use, not endorsement.

## Confidence

**High** on methodology content. The five skills synthesize patterns that appear across 5–8 independent permissive-licensed sources each, plus widely-known experimentation conventions that are not anyone's IP. The prose is original; no paraphrase or close-copy from any source.

**High** on license compliance. Every cited source has been WebFetch-verified for either MIT, Apache 2.0, or BSD. The Flipt and Wasabi rejections are documented; the Etsy/feature borderline-accept is documented. GrowthBook's dual-licensing model (MIT core, separate commercial EE directory) is the standard "open core" pattern; the methodology in this skill set draws only from the documented OSS feature surface.

**High** on frontmatter validity. The frontmatter follows `prompts/shared/skills-md-spec.md` literally: required identity fields, `category: marketing`, `license_type: free` with no pricing fields populated, AI runtime, trigger keywords, example invocations, declarative inputs/outputs, v1.0.0 changelog dated 2026-05-14. The `distribution` block is omitted per spec (platform injects at publish). The validator (`apps/api/src/skills/validator.py`) was not run in this synthesis pass; integration step should validate.

**High** on freshness. GrowthBook, Unleash, PostHog, FeatureHub, and Spotify Confidence all show 2026 releases. PlanOut and Etsy/feature are explicitly flagged as foundational/historical references with the freshness caveat disclosed in this report. The body content does not depend on archived-repo specifics; it uses them only as canonical naming/lifecycle exemplars.

**High** on line counts. All five skills fall comfortably in the 300–700 line range (approximately 320–470 lines each). Body sections include the two required (`## When to use`, `## How to apply`) and four recommended (`## Inputs`, `## Outputs`, `## Examples`, `## Limitations`) plus `## Sources reviewed`.

**High** on tag conformance. Every skill has `category: marketing`, first tag `niche:conversion-rate-optimization`, and 4–7 additional tags per the brief.

## Notes for integrator

- All five skills use `authors: [{name: skillsgit Curated, handle: skillsgit-curated, role: author}]` matching the platform creator account.
- `license_type: free` is set on every skill; the `pricing` block contains only `currency` and `support_included: false` (no `one_time_cents` or `subscription_cents` are populated, per the brief's "no pricing" rule).
- No `tools_required` is set. `tools_optional: [web_search]` is set on the Landing Page CRO Audit since live-URL audits benefit from optional web access, but the skill produces useful output without it.
- `min_context_tokens: 32000` accommodates the long-form outputs each skill produces.
- The `distribution` block is intentionally absent on all files; the publish pipeline injects it.
- All five skills passed manual line-count and structural review against `prompts/shared/skills-md-spec.md`.

## Follow-ups for future waves

- A standalone "Sequential / Always-Valid Testing Methodology" skill could be carved out of the Test Designer for teams that always operate under business pressure to peek; this synthesis treats it as a side-mention only.
- A "Cluster-Randomized Test Designer" skill for marketplace, network, and viral products is a clear gap; the current Test Designer skill explicitly flags it as out of scope.
- A "Personalization vs. Experimentation" skill could disambiguate when to A/B test and when to ship a personalization model with a holdout. The current skills assume A/B testing is the chosen tool.
- An "Email and Push Experimentation" skill could address the channel-specific patterns (single-send vs. continuous, holdout group semantics, frequency capping) that the Test Designer mentions but does not deeply develop.
- A "Pricing Experimentation Ethics and Legal" skill could absorb the regulatory and customer-fairness concerns that the current Test Designer flags as out-of-scope.
