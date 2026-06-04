---
id: skillsgit-curated/imported-voltagent-cloudflare-sandbox-sdk
version: 1.0.0
name: Cloudflare Sandbox SDK
description: Build sandboxed applications for secure, isolated code execution on Cloudflare — shell commands, LLM-generated code with rich outputs, and file operations.
authors:
  - name: Cloudflare
    handle: cloudflare
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, cloudflare, sandbox, containers, code-interpreter]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [cloudflare sandbox, code interpreter, sandbox sdk, exec, runCode, isolated execution]
example_invocations:
  - Set up a Cloudflare sandbox to run LLM-generated Python
  - Add file operations to my sandbox Worker
  - Configure preview URLs for sandbox containers
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Cloudflare Sandbox SDK

## When to use

Use this skill when building sandboxed applications that need secure, isolated code execution — for running shell commands, executing LLM-generated code with rich outputs, or performing file operations inside a containerized workspace.

## How to apply

Prefer retrieval over pre-training. The Sandbox SDK launched recently and APIs continue to evolve. Verify the current binding shape and class names in the official Cloudflare docs at https://developers.cloudflare.com/sandbox/.

## Essential Setup

The Sandbox SDK requires Docker for local development and npm installation. Your `wrangler.jsonc` must include container configuration with a Durable Objects binding, and your Worker entry point must export the `Sandbox` class.

## Three Execution Patterns

1. **Command execution** via `exec()` for shell scripts and direct control.
2. **Code interpreter** via `runCode()` for LLM-generated code with state persistence and rich outputs (stdout, plots, returned values).
3. **File operations** for reading, writing, and managing workspace contents — useful for staging inputs and collecting outputs.

> Use `runCode()` for executing LLM-generated code with rich outputs.

## Key Constraints

- **Preview URLs** require a custom domain with wildcard DNS (`*.yourdomain.com`). The `.workers.dev` domain does not support preview URL subdomains.
- **Auto-sleep** — Containers automatically sleep after 10 minutes of inactivity. Use `destroy()` to immediately free resources from short-lived/temporary sandboxes.
- **Multi-user apps** — Don't hardcode sandbox identifiers. Derive them from user/session context.
- **Public API** — Use the public sandbox methods. Avoid relying on internal client classes that may change without notice.

## Common Mistakes to Avoid

- Hardcoded sandbox identifiers in multi-user applications.
- Skipping the required `Sandbox` export from your Worker entry.
- Relying on internal client classes instead of the documented public API.
- Forgetting wildcard DNS for preview URLs.

## Reference

For current implementation details, signatures, and pricing, consult:

- Official docs: https://developers.cloudflare.com/sandbox/
- Containers docs: https://developers.cloudflare.com/containers/

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `cloudflare/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/cloudflare/skills/tree/main/skills/sandbox-sdk (Apache-2.0)
