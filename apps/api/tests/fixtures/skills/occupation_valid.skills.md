---
id: jane-devops/ai-devops-engineer
version: 1.0.0
name: AI DevOps Engineer
description: A curated bundle of CI/CD, observability, incident response, and platform-engineering methodology for an AI-augmented DevOps practitioner.
authors:
  - name: Jane Devops
    handle: jane-devops
    role: author
category: occupations
tags:
  - devops
  - sre
  - ci-cd
  - observability
license_type: one_time
pricing:
  one_time_cents: 14900
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
  compatible_models:
    - claude-sonnet-4-7
    - gpt-4o
  min_context_tokens: 100000
trigger_keywords:
  - devops
  - sre
  - ci/cd
  - incident
example_invocations:
  - "Bootstrap an AI DevOps Engineer for our team."
kind: occupation
links:
  - target: base/incident-response-loop
    relation: applies
  - target: base/observability-dashboards
    relation: extends
    weight: 0.8
---

# AI DevOps Engineer

## When to use
Use this occupation when the buyer wants a job-role-shaped agent that
covers the full DevOps lifecycle — pipelines, observability, incident
response, and cost.

## How to apply
1. Compose the base occupation vault with the buyer's persona overlays.
2. Load `00-index.md` to understand domain layout.
3. Route each prompt to the most relevant member skill via `links[]`.

## Examples
> "My CI just started failing intermittently after a Redis upgrade."

The agent loads the `flaky-tests` neuron from the buyer's persona,
applies the incident-response loop from the base occupation, and
returns a structured triage plan.

## Limitations
- The occupation is opinionated about CI/CD on Linux; Windows-first
  shops should add a Windows persona overlay.
