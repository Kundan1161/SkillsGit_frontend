# Import Report — alirezarezvani/claude-skills

**Wave:** 6 (import agent)
**Source repo:** https://github.com/alirezarezvani/claude-skills
**License:** MIT (confirmed via `https://api.github.com/repos/alirezarezvani/claude-skills`, `license.spdx_id = "MIT"`)
**Default branch:** main
**Curation date:** 2026-05-14

## Summary

The source repository advertises 263+ Claude Code skills and agent plugins organized into domain trees (`engineering/`, `marketing-skill/`, `product-team/`, `c-level-advisor/`, `compliance-os/`, `finance/`, etc.), each with a `skills/` subdirectory whose entries each contain a `SKILL.md`. Frontmatter in the source is minimal (`name` + `description` only).

Per the import doctrine, we capped the import at **30 high-quality picks** spread across all major domains, with original body content preserved and frontmatter normalized to the skillsgit schema.

## Imported count: 30

## Category distribution

| Category | Count | Slugs |
|---|---|---|
| engineering | 8 | api-design-reviewer, chaos-engineering, codebase-onboarding, database-designer, mcp-server-builder, pr-review-expert, rag-architect, slo-architect |
| marketing | 6 | ab-test-setup, ai-seo, brand-guidelines, cold-email, email-sequence, pricing-strategy |
| product | 6 | competitive-teardown, experiment-designer, product-analytics, product-discovery, roadmap-communicator, saas-scaffolder |
| business (C-level advisory) | 5 | board-deck-builder, ceo-advisor, cfo-advisor, change-management, founder-coach |
| compliance | 3 | gdpr-audit-prep, iso27001-audit-prep, soc2-audit-prep |
| finance | 2 | financial-analyst, saas-metrics-coach |

## Selection heuristics applied

- Full frontmatter (`name` + `description`) present in source.
- Substantive body content (>~2.5 KB raw) — no stub SKILL.md files imported.
- Breadth across the source repo's domain trees rather than over-concentration in one area.
- Skipped near-duplicates (e.g., `database-schema-designer` skipped because `database-designer` was already imported; `chief-ai-officer-advisor` skipped because we took `ceo-advisor` and `cfo-advisor` already).
- Skipped highly tool-specific scaffolds (`docker-development`, `helm-chart-builder`, `kubernetes-operator`) in favor of broader engineering practice skills (SLO, RAG, MCP, PR review).
- Skipped `.zip` packaged agents at top of `engineering-team/` (they would require unzip + further inspection — out of scope for a 30-pick import).

## Skips / notable rejections

- `engineering-team/a11y-audit/SKILL.md` returned 404 in this layout — the entry exists as a directory but its primary file is not at `SKILL.md` (likely a different filename or nested deeper). Replaced with `product-team/skills/saas-scaffolder` to keep the count at 30.
- Top-level `.zip` agent bundles (`marketing-skill/*.zip`, `engineering-team/*.zip`, `ra-qm-team/*.zip`, `c-level-advisor/*.zip`) were not unpacked — outside the lightweight import workflow.
- `business-growth/`, `engineering-team/skills/`, `project-management/skills/`, `ra-qm-team/skills/` enumerated but not sampled beyond confirming their existence — could be a follow-up wave.
- 263+ skills total in repo; ~233 not imported. The remainder are good candidates for future waves should we want to expand coverage further (e.g., security-focused `engineering/skills/{skill-security-auditor, secrets-vault-manager, dependency-auditor}`, marketing-CRO subfamily, additional C-level role advisors).

## Normalization applied to every imported file

- `id` rewritten to `skillsgit-curated/imported-alirezarezvani-<slug>` namespace.
- `version` set to `1.0.0`.
- `name` derived from source `name` (title-cased when source value was a raw slug); truncated to ≤ 80 chars.
- `description` preserved from source, single-line, truncated to ≤ 280 chars when necessary.
- `authors` set to `[{alirezarezvani (curator), role: author}, {skillsgit Curated, role: maintainer}]`.
- `category` mapped to one of `engineering | marketing | product | business | compliance | finance`.
- `tags` start with `[imported, source-alirezarezvani, ...]` and add 3–5 derived topical tags (capped at 10).
- `license_type: free`, pricing block stubbed (currency USD, no support).
- `ai`: required `[claude-opus-4-7]`, compatible `[claude-sonnet-4-6, gpt-4o]`, context 32k, est 6k tokens.
- `trigger_keywords` derived from the topical tags (≤ 5).
- `inputs: []`, `outputs: []`, `example_invocations: []` — stubbed (most source files don't declare these in frontmatter).
- `changelog` initialized with a single `1.0.0` entry dated `2026-05-14`.
- Body preserved verbatim from source. Missing `## When to use` / `## How to apply` sections appended only when not already present (most source files have these or close equivalents such as `## When To Use`, `## When to Run`).
- Standard `## Attribution` and `## Sources reviewed` sections appended to every file, citing the source path under MIT.

## Output location

All 30 files written to `D:\skillsgit\apps\api\scripts\seed_data\synth\imported-alirezarezvani-<slug>.skills.md`.

## Confidence

High. License verified as MIT directly from the GitHub API. Raw `SKILL.md` content fetched verbatim via `curl` (not via summarizing fetcher), ensuring the imported body is the source body unmodified except for the appended attribution sections. Frontmatter validated structurally against the skillsgit schema (Pydantic/Zod source-of-truth at `prompts/shared/skills-md-spec.md`).
