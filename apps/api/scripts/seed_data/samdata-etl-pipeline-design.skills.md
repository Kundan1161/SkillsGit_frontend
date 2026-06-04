---
id: samdata/etl-pipeline-design
version: 1.0.0
name: ETL Pipeline Design
description: Draft an end-to-end ETL/ELT pipeline with idempotency, retries, and SLOs.
authors:
  - name: Sam Data
    handle: samdata
    role: author
category: data
tags:
  - etl
  - pipelines
  - data-engineering
license_type: one_time
pricing:
  one_time_cents: 2400
  currency: USD
  support_included: false
ai:
  required_models:
    - gpt-4o
    - claude-opus-4-7
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - etl
  - pipeline
  - airflow
example_invocations:
  - "Design a daily ETL pulling Stripe events into Snowflake."
inputs:
  - name: sources
    type: text
    required: true
    description: List of sources, destinations, and refresh cadences.
outputs:
  - name: design
    type: markdown
    description: Pipeline graph, DAG sketch, retry/SLO doc.
changelog:
  - version: 1.0.0
    date: 2026-04-18
    notes: Initial release.
---

# ETL Pipeline Design

## When to use
Use when a team is about to build a non-trivial pipeline and you want
idempotency, retries, watermarking, and observability designed-in rather
than retrofitted.

## How to apply
1. List sources, destinations, frequencies, and per-table volumes.
2. Pick orchestration (Airflow / Prefect / Dagster) based on team familiarity.
3. Layer in idempotent merge writes, watermarks, and dead-letter queues.
4. Define SLOs per pipeline (freshness, completeness, accuracy) and dashboards.
5. Emit a DAG sketch.

## Inputs
- A description of the source systems and destinations.

## Outputs
- A pipeline architecture markdown doc.

## Examples
> "Daily Stripe → Snowflake with 1h freshness SLO."

## Limitations
Doesn't pick the underlying compute (Snowflake vs BigQuery vs Databricks) — that's a separate decision.
