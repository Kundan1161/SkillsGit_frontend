---
id: janedoe/dcf-valuation-pro
version: 1.2.0
name: DCF Valuation Pro
description: Build a defensible discounted cash flow model from raw financials.
authors:
  - name: Jane Doe
    handle: janedoe
    role: author
category: finance
tags:
  - valuation
  - dcf
  - finance
license_type: one_time
pricing:
  one_time_cents: 1900
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
  compatible_models:
    - gpt-4o
  min_context_tokens: 50000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - dcf
  - valuation
  - intrinsic value
example_invocations:
  - "Build a DCF for Acme Corp using the attached financials."
inputs:
  - name: financials
    type: file
    required: true
    description: CSV or XLSX with historical income, balance sheet, cash flow.
outputs:
  - name: valuation
    type: markdown
    description: Narrative valuation with key drivers and sensitivities.
changelog:
  - version: 1.2.0
    date: 2026-04-12
    notes: Add WACC sensitivity table.
  - version: 1.0.0
    date: 2026-01-20
    notes: Initial release.
---

# DCF Valuation Pro

## When to use
Use this skill when the user provides a company's financials and asks for a defensible
valuation, intrinsic value estimate, or capital-allocation recommendation.

## How to apply
1. Extract historical revenue, EBITDA, capex, and working-capital figures.
2. Project five explicit years using sensible growth assumptions.
3. Compute terminal value via Gordon growth.
4. Discount cash flows at the requested WACC (default 9%).
5. Output a narrative explaining drivers and sensitivities.

## Inputs
- A clean financial dataset covering at least three years.

## Outputs
- A markdown valuation memo with intrinsic-value range.

## Examples
> "Value Acme Corp using the attached three-year financials."

## Limitations
Best for stable cash-generating businesses; not suitable for early-stage startups.
