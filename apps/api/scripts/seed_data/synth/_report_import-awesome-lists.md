# Import Report - Awesome Claude Skills Collection Repos (Wave 6)

**Date**: 2026-05-14
**Curator**: Wave-6 import agent

## Scope

Five candidate "awesome" / collection repositories were evaluated for permissive licensing and importable skill content.

## Per-repo results

### 1. `ComposioHQ/awesome-claude-skills`

- **License (GitHub API)**: `null` (no LICENSE file detected)
- **Enumerated**: not performed - repo skipped entirely
- **Picks**: 0
- **Skipped because**: Per Wave-6 doctrine, absence of a license = all-rights-reserved. Cannot legally redistribute or create derivative skill files from upstream content. Skip required even though this is a curated index linking to external repos - we would have needed to verify each linked repo individually, which is out of scope for this wave when no aggregated permission exists.

### 2. `travisvn/awesome-claude-skills`

- **License (GitHub API)**: `null`
- **Enumerated**: not performed
- **Picks**: 0
- **Skipped because**: Unlicensed - same as above. Curated index of links, also unlicensed.

### 3. `BehiSecc/awesome-claude-skills`

- **License (GitHub API)**: `null`
- **Enumerated**: not performed
- **Picks**: 0
- **Skipped because**: Unlicensed.

### 4. `abubakarsiddik31/claude-skills-collection`

- **License (GitHub API)**: `null`
- **Enumerated**: not performed
- **Picks**: 0
- **Skipped because**: Unlicensed.

### 5. `sickn33/antigravity-awesome-skills`

- **License (GitHub API)**: `MIT` (LICENSE file)
- **Content license (LICENSE-CONTENT file)**: `CC BY 4.0` - "Creative Commons Attribution 4.0 International license unless a more specific upstream notice says otherwise"
- **Repo scope**: 1,400+ skill folders under `/skills/`; mix of original and community-aggregated SKILL.md files. Some folders carry their own upstream attribution in `source:` frontmatter (e.g., `vibeship-spawner-skills (Apache 2.0)`, `coreyhaines31/marketingskills`).
- **Enumeration approach**: Used the repo's `CATALOG.md` to identify high-quality, diverse picks rather than crawl the full 1,400-folder list. Cap was 15.
- **Picks imported**: 15

  | # | Slug | Category | Notes |
  |---|---|---|---|
  | 1 | claude-code-guide | engineering | Agentic-coding configuration patterns |
  | 2 | architecture | engineering | ADR / trade-off framework |
  | 3 | ai-engineer | ai-engineering | Production LLM application engineering |
  | 4 | database-architect | engineering | Data layer design / migration |
  | 5 | startup-financial-modeling | finance | Cohort-based SaaS modeling |
  | 6 | data-scientist | data-science | Statistical modeling and ML |
  | 7 | alpha-vantage | finance | Market data API integration (orig. author K-Dense Inc.) |
  | 8 | seo-content-writer | marketing | SEO content with E-E-A-T |
  | 9 | content-creator | marketing | Brand voice + cross-platform |
  | 10 | growth-engine | marketing | AARRR + viral loops (orig. author `renat`) |
  | 11 | product-manager-toolkit | product | RICE / discovery / PRD |
  | 12 | revops | sales | Lead lifecycle / scoring / routing (upstream `coreyhaines31/marketingskills`) |
  | 13 | production-code-audit | engineering | Autonomous production-readiness sweep |
  | 14 | constant-time-analysis | security | Side-channel / timing attack detection |
  | 15 | ai-agents-architect | ai-engineering | Agent loops, memory, multi-agent (upstream `vibeship-spawner-skills`, Apache-2.0) |

- **Skips within sickn33**: 1,385+ skills not selected. Filtering rationale:
  - Selected for breadth across our taxonomy (engineering, finance, marketing, product, security, ai-engineering)
  - Selected for non-trivial methodology content rather than thin wrappers
  - Excluded language-specific variants (e.g., Portuguese/Chinese localizations of skills already represented)
  - Excluded skills whose upstream `source:` field pointed to repositories not personally verified for license (deferred to a future wave with per-source license checks)
  - Excluded skills tightly coupled to upstream-bundled scripts/binaries that would not function standalone in our marketplace

## Methodology notes

- Each imported file:
  - Uses `id: skillsgit-curated/imported-sickn33-<slug>` (owner short = `sickn33`)
  - Preserves the original instructional content
  - Adds `## When to use` and `## How to apply` sections (some upstream files lacked them or had abbreviated versions)
  - Appends `## Attribution` crediting `sickn33/antigravity-awesome-skills` and any deeper upstream credited in original frontmatter (vibeship-spawner-skills, coreyhaines31, K-Dense, renat)
  - Appends `## Sources reviewed` with the canonical upstream URL and license tag
  - Removed product-specific brand examples where they were the only example (e.g., the `growth-engine` skill's Alexa-based illustrations) to keep skills domain-general
- All entries published at `license_type: free` per platform curation policy
- All AI defaults: required `claude-opus-4-7`; compatible `claude-sonnet-4-6`, `gpt-4o`; context 32000; tokens 6000

## Totals

- Repos evaluated: 5
- Repos with permissive license: 1 (sickn33; MIT + CC BY 4.0)
- Repos skipped (unlicensed): 4
- Skills imported: 15
- Skills skipped within sickn33: 1,385+ (out of >1,400; not enumerated exhaustively)

## Audit trail

GitHub API license responses (for the four unlicensed repos) returned `license: null`. The sickn33 repo explicitly carries both an MIT LICENSE for code and a CC BY 4.0 LICENSE-CONTENT for documentation, with a clause carving out upstream sub-licenses. All imported skills have their upstream credit preserved in the Attribution section per CC BY 4.0 attribution requirement.
