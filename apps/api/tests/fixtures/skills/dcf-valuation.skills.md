---
id: janedoe/dcf-valuation
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
  one_time_cents: 4900
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
  min_context_tokens: 50000
  tools_required:
    - code_execution
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - dcf
  - valuation
  - intrinsic value
example_invocations:
  - "Build a DCF for Acme Corp using the attached financials."
  - "Value this company over a 5-year horizon."
inputs:
  - name: financials
    type: file
    required: true
    description: CSV or XLSX with historical income statement, balance sheet, cash flow.
  - name: forecast_years
    type: number
    required: false
    description: Number of explicit-forecast years (default 5).
outputs:
  - name: valuation
    type: markdown
    description: Narrative valuation with key drivers and sensitivities.
  - name: model
    type: file
    description: XLSX with the populated DCF model.
changelog:
  - version: 1.2.0
    date: 2026-04-12
    notes: Add WACC sensitivity table.
  - version: 1.1.0
    date: 2026-02-04
    notes: Improved working-capital schedule.
  - version: 1.0.0
    date: 2026-01-20
    notes: Initial release.
---

# DCF Valuation Pro

## When to use
Use this skill when the user provides a company's financials and asks for a defensible
valuation, intrinsic value estimate, or capital-allocation recommendation.

## How to apply
1. Extract historical revenue, EBITDA, capex, and working-capital figures from the input.
2. Project five explicit years using sensible growth assumptions tied to history.
3. Compute terminal value via Gordon growth, sanity-check against exit-multiple.
4. Discount all cash flows at the requested WACC (default 9%).
5. Output a narrative explaining drivers and sensitivities.

## Inputs
- A clean financial dataset (CSV or XLSX) covering at least three years.
- An optional WACC override; otherwise defaults to 9%.

## Outputs
- A markdown valuation memo.
- An XLSX with the populated DCF model.

## Examples
> "Value Acme Corp using the attached three-year financials."

Returns: a memo concluding "Acme intrinsic value: $42/share (range $36–$48)" with the
working model attached.

## Limitations
- Best for stable cash-generating businesses; not suitable for early-stage startups
  or financials companies (use the bank-DCF skill instead).
- Assumes the input data is already cleaned; will error out on missing primary lines.
