---
id: skillsgit-curated/imported-voltagent-sentry-claude-settings-audit
version: 1.0.0
name: Claude Settings Audit
description: Analyze a repository's tech stack and generate a tailored .claude/settings.json with read-only permissions, MCP configs, and merge instructions.
authors:
  - name: Sentry
    handle: getsentry
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, sentry, claude-code, settings, permissions, mcp]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [claude settings, .claude/settings.json, permissions audit, claude allowlist]
example_invocations:
  - Generate a Claude Code settings.json for my Node project
  - Audit my current permissions and tighten them
  - Add MCP server configs for my stack
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Claude Settings Audit

## When to use

Use this skill when generating or tightening a `.claude/settings.json` file for a repository — choosing the right allowlist of read-only commands, MCP server entries, and ensuring no state-modifying commands or absolute paths slip in.

## How to apply

Detect the tech stack first. Generate a minimal, read-only allowlist matched to what the repo actually uses. Provide explicit merge instructions if the user has existing settings — don't overwrite blindly.

## Inputs Needed

1. **Repository content** — either:
   - Run Phase 1 detection commands and share output, or
   - Share relevant config files (`package.json`, `pyproject.toml`, `Gemfile`, `go.mod`, `Cargo.toml`, etc.), or
   - Describe the tech stack.
2. **Current settings** — if `.claude/settings.json` or `.mcp.json` already exist, share them.

## Output

- Complete, ready-to-use `settings.json`.
- Suggested MCP configurations if applicable.
- Merge instructions for existing settings.

## Guarantees

- Only **read-only** commands appropriate for your actual tech stack.
- No absolute paths or state-modifying commands.
- Proper package manager detection — only what you use.
- Framework-specific documentation domains.

## Workflow

1. **Detect** — Identify package managers, build tools, test runners, linters, formatters, and any service tooling (kubectl, terraform, gcloud, aws).
2. **Filter** — Keep only commands you observed in the repo. Drop language-class tools that aren't actually in use.
3. **Permission shape** — Use the most restrictive form that still works (`Bash(npm test:*)` instead of `Bash(npm:*)`).
4. **MCP** — Add MCP servers for documented external integrations (Postgres MCP, GitHub MCP) only when the stack uses them.
5. **Diff against existing** — If the user supplied current settings, show only added/removed entries with rationale.

## Anti-Patterns

- Blanket `Bash(*)` allowlists.
- Including absolute paths to user-specific directories.
- Allowing `rm`, `git push`, `git reset --hard` without explicit scoping.
- Adding domains the project doesn't actually reference.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `getsentry/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/getsentry/skills/tree/main/skills/claude-settings-audit (Apache-2.0)
