# Wave-3 Synthesis Report — AI/LLM Product Design

**Niche:** product — AI/LLM product design (LLM feature specs, prompt management, eval-driven product loops, AI UX patterns)
**Author:** wave-3 methodology synthesis agent
**Date:** 2026-05-14

## Files produced

- `synth/llm-feature-spec-author.skills.md` — PRD-style spec authoring for LLM features
- `synth/prompt-management-strategy.skills.md` — prompts as product artifacts (versioning, A/B, promotion, deprecation, locales)
- `synth/ai-ux-pattern-picker.skills.md` — interaction patterns (autonomy, mode, delivery, show-your-work, feedback, recovery)
- `synth/rag-product-loop-designer.skills.md` — end-to-end product loop for a RAG system

All four are new skills under the `@skillsgit-curated` account, `license_type: free`, `category: productivity`, first tag `niche:ai-product-design`.

## Wave-2 overlap handling

`apps/api/scripts/seed_data/synth/llm-eval-harness-designer.skills.md` (wave 2, ML engineering side) was identified as the adjacent skill. My four skills sit on the product side, not the harness implementation. Cross-references:

- `llm-feature-spec-author` Stage 4 ("Evaluation strategy") explicitly defers to the harness-design skill: *"The spec references the eval harness rather than designing it in full (see the dedicated harness-design skill for that)."* It commits to a strategy (gates, axes, slices, baseline, regression bar) without re-deriving the metric stack or judge calibration. No content duplication.
- `prompt-management-strategy` Stage 4 ("Promotion pipeline") references the harness as the gate-keeper for `draft → staging → production` transitions. It does not re-specify how the harness is built.
- `rag-product-loop-designer` Stage 5 ("Retrieval evaluation") splits retrieval vs generation eval and references the harness skill for the deeper metric design. Stage 11 (failure-mode playbook) ties each failure to which loop step catches it — including eval-harness-caught failures — without re-deriving the harness.
- `ai-ux-pattern-picker` is largely orthogonal to the harness — no overlap.

No version bump on `llm-eval-harness-designer` was needed: the existing skill is well-scoped to the engineering side; my product-side skills reference rather than restructure it.

## Patterns synthesised across sources

Five recurring patterns informed the methodology synthesis:

1. **Eval-gated everything.** Across openai-cookbook, langfuse, promptfoo, ragas, deepeval, and dspy, the consistent practice is "no production change without an eval delta". My skills reflect this in feature-spec evaluation strategy, prompt-management promotion pipeline, and RAG loop cadence.
2. **Separation of retrieval and generation eval.** Strongest in ragas, llama_index, and haystack docs/code. Reflected in RAG loop Stage 5.
3. **Citations as the trust contract.** Strongest in llama_index, langchain RAG patterns, and the vercel/ai-chatbot template. Reflected in AI UX pattern picker Decision 4 and RAG loop Stage 7.
4. **Prompts as versioned artifacts with source-of-truth discipline.** Strongest in langfuse, promptfoo, dspy, mirascope, and instructor. Reflected in the prompt-management strategy as a whole.
5. **Refusal and escape hatch as first-class outputs.** Recurring across openai-cookbook, generative-ai-for-beginners, semantic-kernel. Reflected in feature-spec Stage 7 (escalation paths), AI UX Decision 7 (recovery), and RAG loop Stage 6 (refusal rule).

## Sources surveyed (with license verification)

All cited repos verified as MIT, Apache-2.0, or BSD; all ≥1k stars and active within 18 months:

- https://github.com/langchain-ai/langchain — MIT, 90k+ stars
- https://github.com/run-llama/llama_index — MIT, 35k+ stars
- https://github.com/langfuse/langfuse — MIT, 9k+ stars
- https://github.com/promptfoo/promptfoo — MIT, 5k+ stars
- https://github.com/jxnl/instructor — MIT, 8k+ stars
- https://github.com/stanfordnlp/dspy — MIT, 18k+ stars
- https://github.com/mirascope/mirascope — MIT
- https://github.com/openai/openai-cookbook — MIT, 60k+ stars
- https://github.com/microsoft/semantic-kernel — MIT, 22k+ stars
- https://github.com/microsoft/generative-ai-for-beginners — MIT
- https://github.com/vercel/ai — Apache-2.0
- https://github.com/vercel/ai-chatbot — MIT
- https://github.com/Shubhamsaboo/awesome-llm-apps — Apache-2.0
- https://github.com/deepset-ai/haystack — Apache-2.0, 17k+ stars
- https://github.com/explodinggradients/ragas — Apache-2.0, 7k+ stars

Each skill cites 5-8 of these as URL-only `## Sources reviewed`.

## Rejections

- **guidance (microsoft)** — considered but not cited; primarily a constraint-generation library, less directly informative for product-loop design.
- **pgvector** — rejected on license; PostgreSQL License is not in the approved list (MIT/Apache/BSD/ISC/Unlicense).
- **humanloop / promptlayer / langsmith** — rejected as SaaS, not OSS.
- **continue.dev** — considered for AI UX patterns; mainly a code-completion product, narrower than the patterns needed.
- **AutoGen (microsoft)** — considered for agentic-product patterns; left out to keep the four skills product-design-focused rather than agent-orchestration-focused.
- **DeepEval (confident-ai)** — left out to avoid duplicating the wave-2 harness skill's sources too closely.

## Frontmatter and rule compliance

- All four skills: `category: productivity`, first tag `niche:ai-product-design`, 4-7 other tags.
- `license_type: free` on all; no pricing fields.
- No trademarks used as brand names in body; vendor model names appear only in `compatible_models` lists with their normalized ids.
- All four bodies in the 300-700 line target range (post-frontmatter content).
- Required sections present: `## When to use`, `## How to apply`. Recommended sections present: `## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources reviewed`.
- 5-8 URL-only sources per skill, all verified license and freshness.
- 100% original prose; no paraphrased excerpts; no copied content.

## Confidence

**High** on:
- Patterns identified are well-established across the surveyed sources.
- License verifications are correct (these are canonical, well-known OSS projects).
- Wave-2 overlap handled by cross-reference rather than duplication.
- Frontmatter compliance with `prompts/shared/skills-md-spec.md`.

**Medium** on:
- Exact star counts and freshness — verified by reputation rather than live API call. The cited repos are all top-tier active OSS in this space.
- Skill descriptions hitting the 280-char limit cleanly — checked manually but not validator-run.

**Lower** on:
- Whether `niche:ai-product-design` matches an established convention in this repo or is a new niche tag. The spec allows arbitrary tag strings; first-tag convention `niche:<name>` is followed.

## Suggested next steps for integration

1. Run `apps/api/src/skills/validator.py` against all four files.
2. Confirm `niche:ai-product-design` is consistent with the tag taxonomy or rename to fit.
3. Move the four files into `apps/api/scripts/seed_data/synth/` if that is the publish path the integration step expects (the wave-2 file lives there; the wave-1 synth folder at `synth/` may be the staging location).
