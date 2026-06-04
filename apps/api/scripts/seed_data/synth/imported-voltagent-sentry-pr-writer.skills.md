---
id: skillsgit-curated/imported-voltagent-sentry-pr-writer
version: 1.0.0
name: Sentry PR Writer
description: Create and update pull requests following Sentry conventions — conventional-commits title, why-first description, gh CLI usage, and rewrite-not-append on updates.
authors:
  - name: Sentry
    handle: getsentry
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, sentry, pull-request, gh-cli, conventional-commits]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [pr writer, write pull request, gh pr create, sentry pr, pr title]
example_invocations:
  - Write a PR for my feature branch in Sentry style
  - Update my draft PR title and body
  - Convert my commits into a single coherent PR description
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# PR Writer

## When to use

Use this skill when creating or updating pull requests following Sentry's engineering conventions.

## How to apply

Verify branch state first — never PR from the default branch. Analyze the diff to ground the title and description in real changes. If a PR already exists, rewrite the body as one coherent description of the current PR, not an append-only log. Use the `gh` CLI; the user must already be authenticated.

## Requirements

- GitHub CLI (`gh`) authenticated.
- Changes committed to a feature branch (never the default branch).
- All work complete before opening a PR.

## Process

1. **Verify branch state** — Confirm on a feature branch with all changes committed.
2. **Analyze changes** — Review commits and diffs to understand scope.
3. **Check existing PRs** — If one exists, compare current title/body against the actual diff.
4. **Write the title** — `<type>(<scope>): <Subject>`. Example: `fix(replay): Paginate segment downloads`.
5. **Write description** — Lead with the **why**. 1–3 sentences plus optional bold emphasis blocks.
6. **Create or update** — `gh pr create --draft` or `gh api PATCH ...` to update.

## Title Rules

Allowed types: `feat`, `fix`, `ref`, `perf`, `docs`, `test`, `build`, `ci`, `chore`, `style`, `meta`, `license`, `revert`.

Avoid:

- Bracketed labels like `[codex]`.
- Vague titles like `update`.
- Trailing periods.
- Automation attribution in the title.

## Description Rules

- No checkbox lists, test plans, or redundant diff summaries.
- No customer data or PII.
- Include issue references only when IDs are verifiable (e.g., `Fixes SENTRY-1234`).
- When updating, rewrite the body as one coherent description of the current PR — not an append-only log.

## Example PR

```
Title: fix(replay): Paginate segment downloads

Body:
Segment downloads were loading the full history into memory for every
replay viewer load, which caused OOMs on long sessions. This change
paginates downloads to 50 segments at a time and fetches more on demand.

Fixes SENTRY-4821
```

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `getsentry/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/getsentry/skills/tree/main/skills/pr-writer (Apache-2.0)
