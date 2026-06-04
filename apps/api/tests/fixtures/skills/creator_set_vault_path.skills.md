---
id: jane-devops/creator-set-vault-path
version: 1.0.0
name: Creator-set vault_path
description: Negative fixture — creator illegally sets the platform-authored vault_path field.
authors:
  - name: Jane Devops
    handle: jane-devops
    role: author
category: engineering
tags:
  - negative
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
vault_path: personas/jane-devops/incidents/should-not-be-here.md
---

# Negative fixture — creator-set vault_path

## When to use
This fixture is intentionally invalid; the validator should reject it
with `frontmatter.vault_path: server_assigned`.

## How to apply
1. Run validate_file() against this fixture.
2. Assert the error code is present.
