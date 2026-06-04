---
id: skillsgit-curated/imported-voltagent-sentry-code-simplifier
version: 1.0.0
name: Sentry Code Simplifier
description: Simplify and refine code for clarity, consistency, and maintainability while preserving all functionality — explicit over compact.
authors:
  - name: Sentry
    handle: getsentry
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, sentry, refactoring, code-quality, readability]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [simplify code, refactor, code clarity, reduce complexity, readability]
example_invocations:
  - Simplify this nested ternary into clear branches
  - Refactor for readability without changing behavior
  - Break this dense one-liner into readable steps
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Sentry Code Simplifier

## When to use

Use this skill when enhancing code quality by simplifying and refining code for clarity, consistency, and maintainability — while preserving all functionality. Prioritize recently modified code sections unless instructed otherwise.

## How to apply

- **Preserve behavior** — never alter what the code does, only how it does it.
- **Follow project standards** — apply conventions from established style guides (ES modules, function declarations, explicit types).
- **Improve readability** — reduce complexity, eliminate redundancy, choose explicit over compact solutions.
- **Maintain balance** — avoid over-simplification that sacrifices maintainability or understanding.

## Core Principle

> Explicit code is often better than overly compact code.

This guides decisions like:

- Replacing nested ternary operators with clear `if/else` chains or `switch` statements.
- Breaking dense one-liners into readable steps.
- Naming intermediate values that are referenced multiple times.
- Extracting helper functions when a block exceeds a screen.

## Workflow

1. Read the modified code in context.
2. Identify dense or unclear sections.
3. Propose a clearer rewrite with the same outputs.
4. Verify behavior is unchanged (mentally trace tests; run them if available).
5. Apply project conventions consistently.

## Examples of "Simplify, Don't Mutate"

| Before | After |
|--------|-------|
| `const r = a ? b ? c : d : e ? f : g;` | Multi-line `if/else` chain |
| `[...x.filter(p).map(t).slice(0, n)]` | Three named steps |
| Deep destructuring in function params | Destructure inside the function body |

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `getsentry/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/getsentry/skills/tree/main/skills/code-simplifier (Apache-2.0)
