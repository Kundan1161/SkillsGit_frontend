---
id: skillsgit-curated/imported-voltagent-cloudflare-workers-best-practices
version: 1.0.0
name: Cloudflare Workers Best Practices
description: Review and author Cloudflare Workers code against production best practices, with a strong bias toward retrieving current docs rather than relying on pre-trained knowledge.
authors:
  - name: Cloudflare
    handle: cloudflare
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, cloudflare, workers, code-review, best-practices]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [workers review, cloudflare best practices, workers code audit, ctx.waitUntil, nodejs_compat]
example_invocations:
  - Review my Cloudflare Worker for production best practices
  - Audit Workers code for security and performance anti-patterns
  - Check my Worker handler for streaming and waitUntil usage
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Cloudflare Workers Best Practices

## When to use

Use this skill when reviewing or authoring Cloudflare Workers code for production. It enforces best practices around configuration, request handling, async work, security, and observability.

## How to apply

Bias toward **retrieving current documentation** rather than relying on pre-trained knowledge. This applies to API signatures, config fields, binding shapes, and anti-patterns. Read full files (not diffs) before flagging issues.

## Retrieval Sources

| Resource | URL / Path |
|----------|------------|
| Best practices page | https://developers.cloudflare.com/workers/best-practices/ |
| Workers types | `npm pack @cloudflare/workers-types` or `node_modules` |
| Wrangler config schema | `node_modules/wrangler/config-schema.json` |
| Cloudflare docs | https://developers.cloudflare.com/workers/ |

## Critical Rules to Enforce

- **Set a current `compatibility_date`** and enable `nodejs_compat` when using Node APIs.
- **Stream large or unbounded payloads** — never call `await response.text()` on data of unknown size.
- **Use `ctx.waitUntil()`** for post-response work. Never destructure `ctx` from the handler signature.
- **Prefer in-process bindings** (KV, R2, D1, DO) over REST API calls — they're faster, cheaper, and don't count against subrequest limits.
- **Flag floating promises**, hardcoded secrets, and module-level mutable state.
- **Use Web Crypto** (`crypto.subtle`) for security operations — never `Math.random()` for tokens, IDs, or keys.
- **Generate `Env` types via `wrangler types`** — never hand-write them.

## Review Workflow

1. **Retrieve latest sources** (docs, types, schema) before reviewing.
2. **Read full files** — not just diffs — to understand context.
3. **Validate types and config** against the wrangler schema.
4. **Check for anti-patterns**: unbounded `text()` reads, missing `waitUntil`, REST calls where bindings exist.
5. **Verify security**: secrets in code, weak randomness, missing input validation.
6. **Reference rules with evidence** — cite the file:line and the relevant docs URL.

## Common Anti-Patterns

- Module-level state that accumulates across requests (Workers are shared across requests; don't store user data in module scope).
- Sync work after the response is sent without `ctx.waitUntil()` (cancelled when the response finishes).
- Hardcoded API keys, tokens, or URLs that should be `env` bindings or secrets.
- Polling external APIs from Worker code instead of using Queues, Workflows, or Cron Triggers.
- Using `Math.random()` for security-sensitive values.

## Output Format

When reviewing, structure feedback as:

- **Critical** — Security, data loss, or compliance violations. Block deploy.
- **High** — Reliability, performance, or correctness issues likely to trigger production incidents.
- **Medium** — Maintainability or style. Recommend before merge.
- **Low** — Nits and suggestions.

Always include the file path, line number, and a link to the relevant Cloudflare docs page.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `cloudflare/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/cloudflare/skills/tree/main/skills/workers-best-practices (Apache-2.0)
