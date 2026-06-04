---
id: janedoe/unknown-model
version: 1.0.0
name: Unknown Model
description: Requires a model that is not in the allowlist.
category: finance
license_type: free
ai:
  required_models:
    - claude-2
    - gpt-3
---

# Unknown Model

## When to use
Trigger validator on unknown ai.required_models entry.

## How to apply
1. Run validator.
2. See "unknown_model_id" errors.
