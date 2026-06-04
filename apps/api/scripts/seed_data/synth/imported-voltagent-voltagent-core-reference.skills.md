---
id: skillsgit-curated/imported-voltagent-voltagent-core-reference
version: 1.0.0
name: VoltAgent Core Reference
description: Reference for the VoltAgent class options and lifecycle — memory defaults, tool routing, event triggers, server providers, MCP/A2A integrations, and graceful shutdown.
authors:
  - name: VoltAgent
    handle: voltagent
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, voltagent, core, lifecycle, mcp]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [voltagent core, voltagent class, voltagent options, voltagent lifecycle]
example_invocations:
  - Configure VoltAgent with memory defaults and overrides
  - Register agents and workflows in the VoltAgent constructor
  - Use MCP and A2A integrations
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under MIT.
---

# VoltAgent Core Reference

## When to use

Use this skill when configuring the `VoltAgent` class from `@voltagent/core` — picking constructor options, understanding lifecycle behavior, registering components, and shutting down cleanly.

## How to apply

Configure `VoltAgentOptions` with sensible memory defaults and override per-agent or per-workflow as needed. Avoid deprecated options (`port`, `autoStart`, `customEndpoints`, `enableSwaggerUI`). Pair `startServer()` with a matching `stopServer()` plus telemetry cleanup on shutdown.

## Key Configuration Options

`VoltAgentOptions` supports:

- **Memory** — Default Memory used for agents and workflows. Override with agent-specific or workflow-specific memory instances.
- **Tool routing** — Configure how tool calls are dispatched.
- **Event triggers** — Wire callbacks for lifecycle events.
- **Server providers** — Hono, Elysia, serverless.
- **Integrations** — MCP and A2A servers.

## Initialization Behavior

On construction, `VoltAgent`:

1. Registers supplied agents and workflows.
2. Applies memory defaults.
3. Initializes server infrastructure if a provider is specified.
4. Configures VoltOps client credentials from environment variables when not explicitly provided.

## Core Methods

- **Registration** — for agents, workflows, and triggers.
- **Retrieval** — accessors for registered components.
- **Server lifecycle** — `startServer()`, `stopServer()`.
- **Graceful shutdown** — telemetry cleanup, in-flight request draining.

## Deprecated Options

Avoid these — they're scheduled for removal:

- `port`
- `autoStart`
- `customEndpoints`
- `enableSwaggerUI`

Use the modern server-provider API instead.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `voltagent/skills` repository under the MIT license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/voltagent/skills/tree/main/skills/voltagent-core-reference (MIT)
