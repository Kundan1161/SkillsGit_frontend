---
id: skillsgit-curated/legacy-shape-skill
version: 1.0.0
name: Legacy-shape Skill
description: Mirrors the pre-ADR-009 shape — no kind, no links, no neuron. Should validate green; kind defaults to skill.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags:
  - legacy
  - smoke-fixture
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
  compatible_models:
    - claude-sonnet-4-6
trigger_keywords:
  - legacy
example_invocations:
  - "Run a legacy-shape skill."
---

# Legacy-shape Skill

## When to use
Use this fixture to confirm the validator does not break on files
authored before the ADR-009 frontmatter extension landed.

## How to apply
1. Run validate_file() against this fixture.
2. Assert `is_valid=True` with zero errors.
3. Assert the parsed frontmatter has `kind=skill` by default.

## Examples
> A pre-ADR-009 skill.md from the curated 456-skill library.
