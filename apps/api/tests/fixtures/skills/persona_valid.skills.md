---
id: jane-devops/jane-devops-on-call-lead
version: 1.0.0
name: Jane Devops — On-call Lead Persona
description: A persona overlay capturing Jane's on-call lead experience leading 200+ services across a fintech rollout.
authors:
  - name: Jane Devops
    handle: jane-devops
    role: author
category: personas
tags:
  - persona
  - on-call
  - fintech
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
  compatible_models:
    - claude-sonnet-4-7
trigger_keywords:
  - on-call
  - fintech
  - pagerduty
example_invocations:
  - "Stack Jane's on-call lead persona on top of the DevOps occupation."
kind: persona
parent_occupation_id: jane-devops/ai-devops-engineer
links:
  - target: base/alert-policy-architect
    relation: extends
  - target: base/incident-commander
    relation: applies
---

# Jane Devops — On-call Lead Persona

## When to use
Use this persona when stacking on top of the AI DevOps Engineer
occupation for a fintech-shaped problem — high-cardinality alerts,
regulated change windows, and 200+ services.

## How to apply
1. Compose this persona's neurons into the buyer's occupation vault.
2. Each neuron carries a `recorded-instance-of` link back to the
   base occupation methodology it instantiates.

## Examples
> "My on-call rotation handoff is leaking incidents."

The agent loads the `on-call-rotation-handoff-template` neuron from
this persona and adapts the template to the buyer's team size.

## Limitations
- Persona is fintech-shaped; healthcare or industrial-control buyers
  should layer a domain-specific persona instead.
