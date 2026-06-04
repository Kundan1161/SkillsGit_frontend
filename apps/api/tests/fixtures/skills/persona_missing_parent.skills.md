---
id: jane-devops/persona-no-parent
version: 1.0.0
name: Persona without parent_occupation_id
description: Negative fixture — kind=persona but parent_occupation_id is absent.
authors:
  - name: Jane Devops
    handle: jane-devops
    role: author
category: personas
tags:
  - persona
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
kind: persona
---

# Negative fixture — persona missing parent

## When to use
This fixture is intentionally invalid; the validator should reject it
with `frontmatter.parent_occupation_id: required_for_persona`.

## How to apply
1. Run validate_file() against this fixture.
2. Assert the error code is present.
