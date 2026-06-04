---
id: skillsgit-curated/imported-voltagent-voltagent-best-practices
version: 1.0.0
name: VoltAgent Best Practices
description: Architecture and usage patterns for VoltAgent — agents vs workflows, project structure, provider/model naming, server choice, observability, and the safeStringify rule.
authors:
  - name: VoltAgent
    handle: voltagent
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, voltagent, agents, workflows, architecture]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [voltagent best practices, agent vs workflow, voltops, voltagent architecture]
example_invocations:
  - Should I use an Agent or a Workflow for this task?
  - Structure my VoltAgent project directory
  - Set up VoltOps observability
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under MIT.
---

# VoltAgent Best Practices

## When to use

Use this skill when designing or reviewing a VoltAgent project — picking between Agent and Workflow, organizing source files, configuring providers and memory, choosing a server, and wiring up observability.

## How to apply

Use the Agent vs Workflow rule of thumb to decide the shape first, then organize source directories accordingly. Use the `provider/model` naming convention everywhere. Never call `JSON.stringify` inside VoltAgent packages — use `safeStringify` from the internal utilities.

## Key Distinction — Agent vs Workflow

- **Agent** — Open-ended tasks that require tool selection and adaptive reasoning.
- **Workflow** — Multi-step pipelines with explicit control flow and suspend/resume.

If the work has a fixed step sequence, it's a Workflow. If the model decides what to do next based on observations, it's an Agent.

## Project Structure

```
src/
  agents/
  tools/
  workflows/
```

Group by role (agents, tools, workflows) at the top level. Sub-organize by domain inside each.

## Configuration Patterns

- **Provider/model naming** — `openai/gpt-4o-mini`, `anthropic/claude-3-5-sonnet`, etc.
- **Memory** — Configure a default memory and override per agent or per workflow when needed.

## Server Choice

- **Hono** or **Elysia** for Node environments.
- **Serverless** for fetch-based runtimes (Cloudflare Workers, Netlify).

## Observability

- VoltOpsClient explicit init.
- Or **automatic** configuration when the relevant environment variables are present.

## Critical Caveat

> Never use `JSON.stringify` inside VoltAgent packages. Use `safeStringify` from the internal utilities instead.

This avoids cycles and serialization edge cases that break downstream consumers.

## Reference

For comprehensive guidance, see embedded recipes and official documentation at https://voltagent.dev.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `voltagent/skills` repository under the MIT license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/voltagent/skills/tree/main/skills/voltagent-best-practices (MIT)
