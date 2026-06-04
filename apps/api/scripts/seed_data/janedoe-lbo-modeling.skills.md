---
id: janedoe/lbo-modeling
version: 1.0.0
name: LBO Modeling Suite
description: Build a leveraged buyout model with debt schedules, returns, and IRR sensitivity.
authors:
  - name: Jane Doe
    handle: janedoe
    role: author
category: finance
tags:
  - lbo
  - private-equity
  - modeling
license_type: one_time
pricing:
  one_time_cents: 2900
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  estimated_tokens_per_invocation: 12000
trigger_keywords:
  - lbo
  - buyout
  - irr
example_invocations:
  - "Build an LBO model for the target at 8x EBITDA."
inputs:
  - name: target_financials
    type: file
    required: true
    description: Three years of target company financials.
outputs:
  - name: model
    type: file
    description: Populated LBO model with returns analysis.
changelog:
  - version: 1.0.0
    date: 2026-03-04
    notes: Initial release.
---

# LBO Modeling Suite

## When to use
Use when a user wants to evaluate a leveraged buyout, structure debt tranches,
or compute sponsor returns under varying exit multiples.

## How to apply
1. Calibrate the sources and uses table from the offered enterprise value.
2. Layer in senior + mezzanine debt at the stated coverage ratios.
3. Build a 5-year operating model with mandatory amortisation.
4. Compute IRR at a range of exit multiples (6x–10x EBITDA).

## Inputs
- Three years of historical financials.
- Optional purchase multiple and leverage ratio.

## Outputs
- A returns table across exit-multiple scenarios.
- A narrative summary of risk factors.

## Examples
> "Model the LBO at 7.5x with 60% leverage."

## Limitations
Does not handle dividend recaps or PIK toggles — covered in the LBO-Advanced skill.
