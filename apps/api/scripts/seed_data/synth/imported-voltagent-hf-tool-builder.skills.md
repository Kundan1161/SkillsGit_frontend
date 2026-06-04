---
id: skillsgit-curated/imported-voltagent-hf-tool-builder
version: 1.0.0
name: Hugging Face API Tool Builder
description: Build reusable command-line scripts and utilities for the Hugging Face API — chain calls, pipe through jq, and emit composable JSON for automation.
authors:
  - name: Hugging Face
    handle: huggingface
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, huggingface, api, cli, scripting, automation]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [hf api, huggingface scripts, hf cli, model search api, jq huggingface]
example_invocations:
  - Build a script that enriches model IDs with download counts
  - Chain trending models → metadata → model card parsing
  - Query HF datasets and export to NDJSON
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under MIT.
---

# Hugging Face API Tool Builder

Your purpose is to create reusable command-line scripts and utilities for using the Hugging Face API, allowing chaining, piping, and intermediate processing where helpful.

## When to use

Use this skill when building tools or scripts that use data from the Hugging Face API — chaining or combining API calls, or automating a repeated task. Output reusable scripts to fetch, enrich, or process data.

## How to apply

Access the API directly via `curl` or use the `hf` CLI. Model and dataset cards can be accessed from repositories directly. Investigate the shape of API results before committing to a final design.

## Script Rules

- Scripts MUST take a `--help` argument to describe inputs and outputs.
- Non-destructive scripts should be tested before handing over.
- **Shell scripts preferred**; use Python or TSX if complexity requires.
- **IMPORTANT** — Use `HF_TOKEN` environment variable as an Authorization header: `curl -H "Authorization: Bearer ${HF_TOKEN}" https://huggingface.co/api/`. Higher rate limits and access to gated/private content.
- Investigate shape of API results before final design.
- Prefer simple solutions; use piping/chaining where composability helps.
- Share usage examples once complete.

## High-Level Endpoints

```
/api/datasets
/api/models
/api/spaces
/api/collections
/api/daily_papers
/api/notifications
/api/settings
/api/whoami-v2
/api/trending
/oauth/userinfo
```

## Accessing the API

OpenAPI spec at `https://huggingface.co/.well-known/openapi.json`.

> **DO NOT** read the openapi.json directly — it's too large. Use `jq` to query and extract relevant parts.

```bash
# All 160 endpoints
curl -s "https://huggingface.co/.well-known/openapi.json" | jq '.paths | keys | sort'

# Model search endpoint details
curl -s "https://huggingface.co/.well-known/openapi.json" | jq '.paths["/api/models"]'
```

Constrain results to low numbers to make them easy to process, yet representative.

## `hf` CLI Commands

```
auth         Manage authentication
buckets      Interact with buckets
cache        Manage local cache
collections  Interact with collections
datasets     Interact with datasets
discussions  Manage discussions and PRs
download     Download files
endpoints    Manage Inference Endpoints
env          Print environment info
extensions   Manage CLI extensions
jobs         Run and manage Jobs
models       Interact with models
papers       Interact with papers
repos        Manage repos
skills       Manage skills for AI assistants
spaces       Interact with spaces
sync         Sync files between local and bucket
upload       Upload file or folder
version      Print hf version
webhooks     Manage webhooks
```

`hf` has replaced the deprecated `huggingface-cli`.

## Composable Pipeline Examples

```bash
# Top 10 by downloads
references/baseline_hf_api.sh 25 | jq -r '.[].id' | references/hf_enrich_models.sh \
  | jq -s 'sort_by(.downloads) | reverse | .[:10]'

# Same with one-liner
references/baseline_hf_api.sh 50 | jq '[.[] | {id, downloads}] | sort_by(.downloads) | reverse | .[:10]'

# Model card frontmatter
printf '%s\n' openai/gpt-oss-120b meta-llama/Meta-Llama-3.1-8B \
  | references/hf_model_card_frontmatter.sh \
  | jq -s 'map({id, license, has_extra_gated_prompt})'
```

## Sample Reference Scripts (in the source repo)

- `references/hf_model_papers_auth.sh` — uses `HF_TOKEN` automatically, chains trending → metadata → model card parsing.
- `references/find_models_by_paper.sh` — `--token` flag, resilient query strategy.
- `references/hf_model_card_frontmatter.sh` — uses the `hf` CLI to download cards, extracts YAML frontmatter, emits NDJSON.
- `references/baseline_hf_api.{sh,py,tsx}` — minimal raw-JSON baselines.
- `references/hf_enrich_models.sh` — reads model IDs from stdin, fetches metadata per ID, emits NDJSON.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `huggingface/skills` repository under the MIT license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/huggingface/skills/tree/main/skills/huggingface-tool-builder (MIT)
