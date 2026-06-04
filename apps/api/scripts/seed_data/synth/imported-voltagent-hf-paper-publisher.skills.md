---
id: skillsgit-curated/imported-voltagent-hf-paper-publisher
version: 1.0.0
name: Hugging Face Paper Publisher
description: Manage research papers on the Hugging Face Hub — index from arXiv, claim authorship, link papers to models and datasets, and author scientific articles.
authors:
  - name: Hugging Face
    handle: huggingface
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, huggingface, papers, arxiv, research, publishing]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [hf papers, arxiv huggingface, paper publisher, research article, paper card]
example_invocations:
  - Index my arXiv paper on Hugging Face and claim authorship
  - Link my paper to its dataset and model repos
  - Generate a research article with the modern template
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under MIT.
---

# Hugging Face Paper Publisher

## When to use

Use this skill when managing research papers on the Hugging Face Hub — indexing papers from arXiv, claiming authorship, controlling visibility, linking papers to models and datasets, or authoring formatted scientific articles.

## How to apply

Use the official `huggingface_hub` Python library (>=0.26.0). Execute scripts with `uv run` and set an `HF_TOKEN` environment variable with write access. Use the appropriate markdown template (standard, modern, arXiv-style, ML-report) for the target audience.

## Capabilities

- **Paper Management** — Index from arXiv, claim authorship, control visibility, discover research within the HF ecosystem.
- **Repository Integration** — Link papers to models and datasets through metadata. The Hub extracts the arXiv ID from the link and automatically generates corresponding tags for discoverability.
- **Research Article Creation** — Markdown templates in multiple formats (standard, modern, arXiv, ML-report) with dynamic tables of contents and LaTeX math support.
- **Metadata Management** — YAML frontmatter for model and dataset cards, citation tracking, and version control across repositories.

## Technical Requirements

- Python with `huggingface_hub` (>=0.26.0), `pyyaml`, `requests`, `markdown`, `python-dotenv`.
- Run scripts via `uv run` with `HF_TOKEN` set for write access.

## Common Workflows

1. **Publish new research** — create → submit to arXiv → index on HF → link to models/datasets.
2. **Discover and link existing papers** — search the Hub, attach to model/dataset cards.
3. **Manage author portfolios** — claim authorship, toggle visibility on public profiles.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `huggingface/skills` repository under the MIT license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/huggingface/skills/tree/main/skills/huggingface-paper-publisher (MIT)
