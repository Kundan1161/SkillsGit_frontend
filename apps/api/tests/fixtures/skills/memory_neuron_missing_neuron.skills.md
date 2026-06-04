---
id: jane-devops/2024-08-flaky-tests-no-neuron-block
version: 1.0.0
name: 2024-08 Flaky tests (missing neuron block)
description: Negative fixture — kind=memory_neuron but the `neuron` block is missing entirely.
authors:
  - name: Jane Devops
    handle: jane-devops
    role: author
category: personas
tags:
  - neuron
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
kind: memory_neuron
parent_occupation_id: jane-devops/ai-devops-engineer
---

# Negative fixture — missing neuron block

## When to use
This fixture is intentionally invalid; the validator should reject it
with `frontmatter.neuron: required_for_memory_neuron`.

## How to apply
1. Run validate_file() against this fixture.
2. Assert the error code is present.
