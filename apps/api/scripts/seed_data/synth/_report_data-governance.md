# Wave-3 Synth Report — Niche: data / data-governance

**Date:** 2026-05-14
**Agent:** Wave-3 data-governance methodology synth
**Confidence:** High

## Scope

Niche: **data governance** — data contracts, lineage, ownership, classification, retention, quality SLAs.

## Skills produced (4)

| Slug | File | Status |
| ---- | ---- | ------ |
| `data-contract-author` | `synth/data-contract-author.skills.md` | new, v1.0.0 |
| `data-catalog-architect` | `synth/data-catalog-architect.skills.md` | new, v1.0.0 |
| `data-quality-test-designer` | `synth/data-quality-test-designer.skills.md` | new, v1.0.0 |
| `data-classification-and-retention-policy-author` | `synth/data-classification-and-retention-policy-author.skills.md` | new, v1.0.0 |

No existing synth skills overlapped — `dag-architect.skills.md` mentioned a future `pipeline-data-contract-author` in passing but the file did not exist. Created `data-contract-author` as the canonical authoring skill; if a pipeline-specific variant is needed later it can layer on top.

Common frontmatter: `category: data`, first tag `niche:data-governance`, `license_type: free`, 5 sources per skill, body lengths 380–520 lines (within 300–700 spec).

## Sources verified (URL + license + freshness + stars)

All Apache-2.0 / MIT, all ≥ 100 stars, all active within 18 months unless noted.

| Project | URL | License | Stars | Last release | Verdict |
| ------- | --- | ------- | ----- | ------------ | ------- |
| OpenLineage | https://github.com/OpenLineage/OpenLineage | Apache-2.0 | 2.5k | 2026-05-13 | ACCEPT |
| DataHub | https://github.com/datahub-project/datahub | Apache-2.0 | 11.9k | 2026-05-11 | ACCEPT |
| Great Expectations | https://github.com/great-expectations/great_expectations | Apache-2.0 | 11.5k | 2026-05-14 | ACCEPT |
| Open Data Contract Standard | https://github.com/bitol-io/open-data-contract-standard | Apache-2.0 | 856 | 2025-12-08 | ACCEPT |
| Data Contract CLI | https://github.com/datacontract/datacontract-cli | Apache-2.0 | 884 | active | ACCEPT |
| Data Contract Specification | https://github.com/datacontract/datacontract-specification | MIT | 415 | 2025-07-05 | ACCEPT |
| dbt-core | https://github.com/dbt-labs/dbt-core | Apache-2.0 | 12.8k | active | ACCEPT |
| Apache Atlas | https://github.com/apache/atlas | Apache-2.0 | 2.1k | active | ACCEPT |

## Rejections

- **Soda Core** — license is **Elastic License 2.0** (verified at `sodadata/soda-core/blob/main/LICENSE`). Not on the MIT/Apache/BSD/ISC/Unlicense allowlist. **REJECTED.** Did not include in any skill's source list.
- **Amundsen** — Apache-2.0 ✓ and 4.8k stars ✓, but last release Aug 2024 (~21 months stale by May 2026). Failed the 18-month freshness rule. **REJECTED** to keep source lists honest.
- **Marquez** — Apache-2.0 ✓ and 2.2k stars ✓, but last tagged release Oct 2024 (~19 months stale); main branch active. Borderline; **omitted from sources** to stay safely inside the rule. OpenLineage covers the same ground and is fresh.

## Methodology patterns observed

- **The four governance pillars interlock.** Contracts state SLOs; quality tests verify them; catalogs surface them; classification + retention bound them. Each skill cross-references the others to keep handoffs explicit (e.g., the contract's `classification:` field points at the classification skill).
- **Severity + on-failure action** are universal. A test, contract, or policy without a graded severity scheme creates alert fatigue and decays in ≤ 2 weeks. Every skill enforces tiers (P0/P1/P2 or equivalent).
- **Cold-start anti-pattern**: data-quality and classification both have a "discovery before alerts" phase that's commonly skipped, producing noisy rollouts that get abandoned. Each relevant skill explicitly calls out the warm-up window.
- **Auto-discovery is bootstrap, not steady state.** Classification, ownership, and lineage all benefit from automated discovery to **seed** the system, but require **declarative** maintenance (CI gates on contract/classification metadata) to stay correct.
- **Lineage depth tiering (L0–L3)** is the most powerful tool for keeping catalog rollouts on schedule — most failures came from "full column-level lineage everywhere" as a day-1 goal.
- **Backups + immutable logs** are the silent killers of GDPR/CCPA deletion programs; called out explicitly in the retention skill.

## Confidence

**High.** All sources verified by direct WebFetch of repository pages (and a license file fetch for Soda Core). Skill structures match the `skills-md-spec.md` contract (required `## When to use` and `## How to apply` sections present, frontmatter schema valid, no forbidden content). Bodies land within the 300–700 line range. No overlap with prior synth output. The rejection of Soda Core was a meaningful catch (it's the most-mentioned project in this space and is commonly miscategorized as "open source").
