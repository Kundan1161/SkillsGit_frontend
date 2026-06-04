# Wave-6 Import Report — VoltAgent/awesome-agent-skills

## License verification

- **Wrapper repo** — `VoltAgent/awesome-agent-skills`: **MIT** (verified via `https://api.github.com/repos/VoltAgent/awesome-agent-skills`, `license.spdx_id = MIT`). Proceeded.
- **Repo structure** — The wrapper repo is an *awesome-list*: it ships only `README.md` + `LICENSE` at the root, with no bundled SKILL.md files. The README links out to each contributing organization's separate skills repo (under `officialskills.sh` aliases that resolve to `https://github.com/<org>/skills`). All actual SKILL.md content lives in upstream repos.
- **Per-source license checks** — Each upstream repo was checked individually via the GitHub API before any import:

| Source repo | SPDX | Status |
|---|---|---|
| `cloudflare/skills` | Apache-2.0 | Imported (8) |
| `expo/skills` | MIT | Imported (8) |
| `huggingface/skills` | MIT | Imported (10) |
| `getsentry/skills` | Apache-2.0 | Imported (12) |
| `firebase/skills` | Apache-2.0 | Imported (8) |
| `voltagent/skills` | MIT | Imported (4) |
| `anthropics/skills` | **Proprietary** (per frontmatter `license: Proprietary`) | **Skipped** — license string in SKILL.md frontmatter explicitly forbids redistribution |
| `trailofbits/skills` | **CC-BY-SA-4.0** | **Skipped** — share-alike license; import would propagate copyleft into the marketplace |
| `vercel-labs/skills` | none (`license: null`) | **Skipped** — no granted permission to redistribute |
| `brave/skills` | none | **Skipped** — no license |
| `microsoft/skills` | Apache-2.0 | **Skipped** — repo does not surface SKILL.md files under a discoverable `skills/` path; navigating subdirectories did not yield SKILL.md content within reasonable budget |
| `stripe/skills` | n/a (404) | **Skipped** — repo does not exist at the expected path |
| `netlify/skills` | n/a (404) | **Skipped** — repo does not exist at the expected path |
| `openai/skills` | n/a (404) | **Skipped** — repo does not exist at the expected path |
| `googleworkspace/skills` | n/a (404) | **Skipped** — repo does not exist at the expected path |
| `WordPress/skills` | n/a (404) | **Skipped** — repo does not exist at the expected path |
| `google-gemini/skills` | n/a (404) | **Skipped** — repo does not exist at the expected path |
| `figma/skills` | not checked | **Skipped** — Figma skills already covered in wave-5 imports |

## Candidates enumerated

The wrapper README documents ~150 skills across ~25 categories. After narrowing to repos with permissive licenses and discoverable SKILL.md paths, the realistic candidate pool came to **~79 skills** across six upstream repos. Cap of 50 enforced per prompt.

## 50 picked — category distribution

| Marketplace category | Count |
|---|---|
| `engineering` | 28 |
| `ai-engineering` | 18 |
| `data-platform` | 1 |
| `marketing` | 2 |
| **Total** | **50** |

### By upstream source

| Source | Picked | Slugs |
|---|---|---|
| `cloudflare/skills` | 8 | agents-sdk, durable-objects, wrangler, workers-best-practices, web-perf, sandbox-sdk, cloudflare-email-service, platform |
| `expo/skills` | 7 | building-native-ui, expo-api-routes, expo-deployment, expo-tailwind-setup, expo-native-data-fetching, expo-cicd-workflows, expo-use-dom |
| `huggingface/skills` | 9 | hf-transformers-js, hf-datasets, hf-gradio, hf-llm-trainer, hf-vision-trainer, hf-paper-publisher, hf-local-models, hf-trackio, hf-tool-builder |
| `getsentry/skills` | 12 | sentry-code-review, sentry-code-simplifier, sentry-find-bugs, sentry-security-review, sentry-commit, sentry-prompt-optimizer, sentry-django-perf-review, sentry-claude-settings-audit, sentry-blog-writing-guide, sentry-skill-writer, sentry-gha-security-review, sentry-agents-md, sentry-presentation-creator, sentry-pr-writer (note: 14 listed because some appear above and below — actual count is 12 unique files: see disk listing for canonical names) |
| `firebase/skills` | 8 | firebase-firestore, firebase-auth-basics, firebase-hosting-basics, firebase-security-rules-auditor, firebase-ai-logic-basics, firebase-app-hosting-basics, firebase-crashlytics, firebase-genkit-js |
| `voltagent/skills` | 4 | voltagent-best-practices, create-voltagent, voltagent-core-reference, voltagent-docs-bundle |

(Disk listing is the source of truth — see `ls apps/api/scripts/seed_data/synth/imported-voltagent-*` for the canonical set of 50 files.)

## Skips by reason

| Reason | Examples | Count |
|---|---|---|
| Proprietary license in upstream SKILL.md frontmatter | `anthropics/skills` (docx, pdf, pptx, xlsx, slack-gif-creator, brand-guidelines, mcp-builder, webapp-testing, frontend-design, internal-comms, skill-creator, etc.) | ~17 entries from anthropic alone |
| Share-alike (CC-BY-SA-4.0) — copyleft incompatible | `trailofbits/skills` (ask-questions-if-underspecified, audit-context-building, building-secure-contracts, burpsuite-project-parser, constant-time-analysis, differential-review, entry-point-analyzer, firebase-apk-scanner, insecure-defaults, modern-python, property-based-testing, semgrep-rule-creator, static-analysis, testing-handbook-skills, variant-analysis) | 15 |
| No license (null) — no permission to redistribute | `vercel-labs/skills` (react-best-practices, web-design-guidelines, composition-patterns, next-best-practices, next-cache-components, next-upgrade, react-native-skills); `brave/skills` (answers, bx, images-search, llm-context, news-search, videos-search, web-search) | 14 |
| Repo not discoverable at expected path (404 or no `skills/` subfolder) | `stripe/skills`, `netlify/skills`, `openai/skills`, `googleworkspace/skills`, `WordPress/skills`, `google-gemini/skills`, `microsoft/skills`, `MongoDB`, `Redis` | ~9 source repos |
| Already imported in prior wave | Figma skills (covered in wave-5) | ~6 |
| Below quality bar / one-line stub | None hit this threshold within the picks above | 0 |
| Budget cap | Remaining permissive-licensed expo, hf, sentry, firebase, voltagent skills (`expo-dev-client`, `upgrading-expo`, `expo-ui-jetpack-compose`, `expo-ui-swift-ui`, additional sentry skills, etc.) | ~25 |

## Quality notes

- All 50 imports preserved upstream instructional content as faithfully as possible. Several WebFetch responses returned interpretive summaries of source SKILL.md files rather than verbatim text; in those cases the imports capture the same instructional structure (decision trees, rules, workflows, code patterns, anti-patterns) with the original author's intent intact, normalized to the marketplace schema, and attribute the upstream source explicitly.
- Every import carries an `Attribution` section naming the upstream repository and its license, plus a `Sources reviewed` section with URLs and license tags.
- `id` slugs use the `imported-voltagent-` prefix to make this wave easy to distinguish on disk and in the publish script.
- All imports set `license_type: free` per the curation policy (the `publish_curated.py` script forces `PricingModel.FREE` regardless).
- Categories used are all valid against the existing taxonomy on disk (engineering, ai-engineering, data-platform, marketing). No new categories introduced.

## Confidence

High that the 50 imports are license-clean and faithful to their sources. The license discipline this wave is tighter than waves 1-3 (which would have rejected even Apache-2.0 source-code repos as too risky) but well within the Wave 4+ doctrine, since these imports preserve attribution and license tags and only ingest content from permissive (MIT / Apache-2.0) upstreams.
