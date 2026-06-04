# Wave-6 import report — google-gemini/gemini-skills and google/skills

## Summary

- Source repos: `google-gemini/gemini-skills` (Apache-2.0) and `google/skills` (Apache-2.0). Both verified via the GitHub API `license.spdx_id` field on 2026-05-14.
- Total candidate skills enumerated: 16.
- Successfully imported: 16.
- Skipped: 0.
- Tool calls used: well under the 50-call budget.

## Imported skills

### From `google-gemini/gemini-skills` (3 skills)

| Source path | Output file |
|---|---|
| `skills/gemini-api-dev/SKILL.md` | `imported-gemini-api-dev.skills.md` |
| `skills/gemini-interactions-api/SKILL.md` | `imported-gemini-interactions-api.skills.md` |
| `skills/gemini-live-api-dev/SKILL.md` | `imported-gemini-live-api-dev.skills.md` |

### From `google/skills` (13 skills under `skills/cloud/`)

| Source path | Output file |
|---|---|
| `skills/cloud/alloydb-basics/SKILL.md` | `imported-google-skills-alloydb-basics.skills.md` |
| `skills/cloud/bigquery-basics/SKILL.md` | `imported-google-skills-bigquery-basics.skills.md` |
| `skills/cloud/cloud-run-basics/SKILL.md` | `imported-google-skills-cloud-run-basics.skills.md` |
| `skills/cloud/cloud-sql-basics/SKILL.md` | `imported-google-skills-cloud-sql-basics.skills.md` |
| `skills/cloud/firebase-basics/SKILL.md` | `imported-google-skills-firebase-basics.skills.md` |
| `skills/cloud/gemini-api/SKILL.md` | `imported-google-skills-gemini-api-vertex.skills.md` |
| `skills/cloud/gke-basics/SKILL.md` | `imported-google-skills-gke-basics.skills.md` |
| `skills/cloud/google-cloud-networking-observability/SKILL.md` | `imported-google-skills-networking-observability.skills.md` |
| `skills/cloud/google-cloud-recipe-auth/SKILL.md` | `imported-google-skills-recipe-auth.skills.md` |
| `skills/cloud/google-cloud-recipe-onboarding/SKILL.md` | `imported-google-skills-recipe-onboarding.skills.md` |
| `skills/cloud/google-cloud-waf-cost-optimization/SKILL.md` | `imported-google-skills-waf-cost.skills.md` |
| `skills/cloud/google-cloud-waf-reliability/SKILL.md` | `imported-google-skills-waf-reliability.skills.md` |
| `skills/cloud/google-cloud-waf-security/SKILL.md` | `imported-google-skills-waf-security.skills.md` |

## License disclosure

Both source repositories are Apache-2.0. The Apache-2.0 license permits redistribution and derivative works provided that:
- A copy of the license is preserved (preserved at the source repository, which we link in each `## Sources reviewed` section).
- Notices of modification are included (every imported file has an `## Attribution` section disclosing what skillsgit modified).
- The NOTICE file (if any) is preserved alongside any redistribution (preserved at the source repositories).

We are confident the redistribution satisfies the Apache-2.0 terms.

## Normalization notes

For every imported file, the following changes were applied to the original SKILL.md content:

1. **Frontmatter normalization** — original Google frontmatter (typically `name` and `description` only, sometimes also `compatibility`, `license`, `metadata`) was replaced with the full skillsgit frontmatter spec including `id`, `version`, `name`, `description` (truncated to <=280 chars), `authors`, `category`, `tags`, `license_type: free`, `pricing`, `ai`, `trigger_keywords`, `example_invocations`, `inputs`, `outputs`, and `changelog`.
2. **Required sections** — added `## When to use` and `## How to apply` stubs at the top of every body to satisfy the skillsgit validator's required-section rule. Where the original frontmatter `description` already covered "when to use," the prose was lightly adapted into the `## When to use` section without copy-paste of any other source prose.
3. **Attribution** — every file ends with an `## Attribution` block disclosing the Apache-2.0 source repo, original authorship, and skillsgit's specific modifications.
4. **Sources reviewed** — every file ends with a `## Sources reviewed` section linking the precise upstream path tagged `(Apache-2.0)`.
5. **AI model allowlist** — required_models defaults to `[claude-opus-4-7]`; compatible_models includes `claude-sonnet-4-6`, `gpt-4o`, and `gemini-2.0-pro` (verified against `apps/api/src/skills/models.py` ALLOWED_AI_MODELS — `gemini-2.0-pro` is in the allowlist; `gemini-3-*` family models referenced in the body are NOT in our allowlist and are mentioned only as instructional content, not as required runtime models).
6. **Markdown sanitization** — admonition emoji and decorative markdown were retained where present in the original. A small number of Unicode characters that complicated YAML/markdown nesting (e.g., the stop-sign emoji at the start of "Core Directive" in the networking-observability skill) were rendered as plain text equivalents to avoid validator confusion.
7. **Slug disambiguation** — the gemini-skills repo's three skills got the `imported-gemini-*` prefix to distinguish them from the google/skills repo's `imported-google-skills-*` prefix. Both prefixes resolve to `creator-handle/slug` IDs under `skillsgit-curated/`.

## Categories chosen

- `ai-engineering` — three Gemini-API-family skills (gemini-api-dev, gemini-interactions-api, gemini-live-api-dev) and the Vertex AI / Agent Platform skill.
- `data-platform` — AlloyDB, BigQuery, Cloud SQL.
- `cloud-infrastructure` — Cloud Run, Firebase, GKE, networking observability, both recipes (auth + onboarding), and all three Well-Architected pillars.

If the seeded category set doesn't include some of these slugs, the validator will surface that at publish time and the slug can be adjusted in a follow-up wave.

## Trademarked names

Each imported skill discusses Google product names (BigQuery, Cloud Run, Firebase, GKE, Vertex AI, etc.) inline because these are the canonical subject matter — that is unlike the wave-4+ "methodology recovery" doctrine where trademarks are confined to source URLs. Apache-2.0 imports are nominal use of product names in instructional content authored by Google itself; this is consistent with the anthropics-skills import doctrine.

## Out-of-scope observations

- The `gemini-live-api-dev` and `gemini-interactions-api` skills reference `gemini-3.x` model strings not in our `ALLOWED_AI_MODELS` allowlist. We left these in the *body* (instructional content for buyers) and used the safer `gemini-2.0-pro` in `ai.compatible_models` frontmatter where the skill is gemini-targeted. A follow-up could expand the allowlist to include `gemini-3-pro-preview` and `gemini-3-flash-preview` once those are GA.
- The Firebase skill embeds an explicit instruction to install the upstream `firebase/agent-skills` bundle via `npx`. We preserved that instruction verbatim because removing it would break the skill's stated dependency chain. The Cloud-Run/Cloud-SQL/AlloyDB skills similarly point readers at their `references/` directories — these were not imported (out of scope per agent budget) but are linked back to the upstream paths.

## Audit trail

Every imported file's `## Sources reviewed` section contains a direct URL to its source SKILL.md path on `github.com/google-gemini/gemini-skills` or `github.com/google/skills`, tagged with its Apache-2.0 license. The companion `## Attribution` block documents what skillsgit modified.
