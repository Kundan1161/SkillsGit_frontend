---
id: samdata/schema-architect
version: 1.0.0
name: Schema Architect
description: Design a normalised relational schema from a plain-English domain description.
authors:
  - name: Sam Data
    handle: samdata
    role: author
category: data
tags:
  - postgres
  - schema
  - data-modeling
license_type: one_time
pricing:
  one_time_cents: 3900
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - schema
  - database design
  - er diagram
example_invocations:
  - "Design a schema for a small SaaS billing system."
inputs:
  - name: domain
    type: text
    required: true
    description: Plain-English description of the business domain.
outputs:
  - name: schema
    type: markdown
    description: ER overview + ddl with explanations.
changelog:
  - version: 1.0.0
    date: 2026-02-28
    notes: Initial release.
---

# Schema Architect

## When to use
Use when an engineer describes a domain and needs a normalised relational schema
with proper keys, indexes, and audit columns — without slipping into the trap of
denormalising for the wrong reasons.

## How to apply
1. Extract entities, attributes, relationships, and lifecycle states from the domain.
2. Apply 3NF, then identify any pragmatic denormalisations with justification.
3. Pick primary keys (UUID v7 by default) and surrogate timestamps.
4. Emit CREATE TABLE statements with FKs, indexes, and check constraints.
5. Diagram in mermaid.

## Inputs
- A paragraph or two describing the business.

## Outputs
- A markdown design doc with mermaid ER diagram and DDL.

## Examples
> "Design a schema for a vehicle-rental marketplace."

## Limitations
Optimises for clarity over performance — review indexes once you've seen real traffic.
