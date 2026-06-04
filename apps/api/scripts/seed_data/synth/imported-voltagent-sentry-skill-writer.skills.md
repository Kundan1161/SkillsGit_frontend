---
id: skillsgit-curated/imported-voltagent-sentry-skill-writer
version: 1.0.0
name: Sentry Skill Writer
description: Canonical workflow for creating and improving agent skills — resolve target, synthesize, author, optimize description, register and validate.
authors:
  - name: Sentry
    handle: getsentry
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, sentry, skill-creation, agent-skills, claude-code]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [skill writer, create skill, improve skill, agent skill, claude skill]
example_invocations:
  - Create a new skill for code review on Go projects
  - Improve this skill's description for better routing
  - Synthesize a skill from these example prompts
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Sentry Skill Writer

## When to use

Use this skill when creating or improving agent skills within Claude's Agent SDK ecosystem — authoring `SKILL.md` files, choosing execution shape, optimizing description for routing accuracy.

## How to apply

Follow the six-step canonical workflow. Default to the **simplest adequate shape** unless complexity is justified. Maximize high-value input coverage before authoring while minimizing wasted runtime tokens.

## Six-Step Workflow

1. **Resolve target and execution shape** — Identify the operating mode (create, update, synthesize, iterate) and the execution shape (inline, reference-backed, script-backed, argument-driven, asset-based).
2. **Run synthesis for new skills** — Capture sources with provenance.
3. **Iterate from examples** when improving an existing skill — observe behavior deltas grounded in real cases.
4. **Author artifacts** — Compose the SKILL.md and any references.
5. **Optimize description quality** — Tune the frontmatter `description` for routing accuracy.
6. **Register and validate** — Run the validator; ensure round-trip.

## Architectural Elements

- **Core router**: `SKILL.md` serves as the primary navigation layer.
- **Reference architecture**: Flat references under `references/` with explicit "open when..." routing.
- **Three reference categories**: core workflow, artifact layout, workflow mechanics.

## Operating Modes

- Create
- Update
- Synthesize
- Iterate

## Execution Shapes (Simplest First)

- **Inline** — Everything fits in SKILL.md.
- **Reference-backed** — SKILL.md links into `references/` for deep dives.
- **Script-backed** — Ships scripts that the agent invokes.
- **Argument-driven** — Takes structured arguments from the caller.
- **Asset-based** — Bundles templates or data files.

## Primary Success Criterion

> Maximize high-value input coverage before authoring while minimizing wasted runtime tokens.

## Design Philosophy

- Simplicity over complexity — default to the simplest adequate shape.
- Precision passes over big rewrites.
- Source capture with provenance.
- Behavior deltas grounded in examples, not assumption.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `getsentry/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/getsentry/skills/tree/main/skills/skill-writer (Apache-2.0)
