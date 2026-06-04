---
id: skillsgit-curated/imported-alirezarezvani-experiment-designer
version: 1.0.0
name: Experiment Designer
description: Use when planning product experiments, writing testable hypotheses, estimating sample size, prioritizing tests, or interpreting A/B outcomes with practical statistical rigor.
authors:
  - name: alirezarezvani (curator)
    handle: alirezarezvani
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: productivity
tags: [imported, source-alirezarezvani, experimentation, ab-testing, hypothesis]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [experimentation, ab-testing, hypothesis]
example_invocations: []
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from alirezarezvani/claude-skills under MIT.
---

# Experiment Designer

Design, prioritize, and evaluate product experiments with clear hypotheses and defensible decisions.

## When To Use

Use this skill for:
- A/B and multivariate experiment planning
- Hypothesis writing and success criteria definition
- Sample size and minimum detectable effect planning
- Experiment prioritization with ICE scoring
- Reading statistical output for product decisions

## Core Workflow

1. Write hypothesis in If/Then/Because format
- If we change `[intervention]`
- Then `[metric]` will change by `[expected direction/magnitude]`
- Because `[behavioral mechanism]`

2. Define metrics before running test
- Primary metric: single decision metric
- Guardrail metrics: quality/risk protection
- Secondary metrics: diagnostics only

3. Estimate sample size
- Baseline conversion or baseline mean
- Minimum detectable effect (MDE)
- Significance level (alpha) and power

Use:
```bash
python3 scripts/sample_size_calculator.py --baseline-rate 0.12 --mde 0.02 --mde-type absolute
```

4. Prioritize experiments with ICE
- Impact: potential upside
- Confidence: evidence quality
- Ease: cost/speed/complexity

ICE Score = (Impact * Confidence * Ease) / 10

5. Launch with stopping rules
- Decide fixed sample size or fixed duration in advance
- Avoid repeated peeking without proper method
- Monitor guardrails continuously

6. Interpret results
- Statistical significance is not business significance
- Compare point estimate + confidence interval to decision threshold
- Investigate novelty effects and segment heterogeneity

## Hypothesis Quality Checklist

- [ ] Contains explicit intervention and audience
- [ ] Specifies measurable metric change
- [ ] States plausible causal reason
- [ ] Includes expected minimum effect
- [ ] Defines failure condition

## Common Experiment Pitfalls

- Underpowered tests leading to false negatives
- Running too many simultaneous changes without isolation
- Changing targeting or implementation mid-test
- Stopping early on random spikes
- Ignoring sample ratio mismatch and instrumentation drift
- Declaring success from p-value without effect-size context

## Statistical Interpretation Guardrails

- p-value < alpha indicates evidence against null, not guaranteed truth.
- Confidence interval crossing zero/no-effect means uncertain directional claim.
- Wide intervals imply low precision even when significant.
- Use practical significance thresholds tied to business impact.

See:
- `references/experiment-playbook.md`
- `references/statistics-reference.md`

## Tooling

### `scripts/sample_size_calculator.py`

Computes required sample size (per variant and total) from:
- baseline rate
- MDE (absolute or relative)
- significance level (alpha)
- statistical power

Example:
```bash
python3 scripts/sample_size_calculator.py \
  --baseline-rate 0.10 \
  --mde 0.015 \
  --mde-type absolute \
  --alpha 0.05 \
  --power 0.8
```

## How to apply

Follow the workflow, steps, and best-practice guidance laid out in the sections below. Treat the inputs as evidence, apply the listed checks, and produce the outputs described.

## Attribution

This skill was imported from `alirezarezvani/claude-skills` under the MIT license. Original content authored by the listed contributor(s). Modifications by skillsgit: frontmatter normalization; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/alirezarezvani/claude-skills/tree/main/product-team/skills/experiment-designer (MIT)
