---
id: marcoart/design-critique-rubric
version: 2.1.0
name: Design Critique Rubric
description: Apply a 12-point design critique against any UI screenshot or Figma frame.
authors:
  - name: Marco Art
    handle: marcoart
    role: author
category: design
tags:
  - design
  - critique
  - ui
license_type: one_time
pricing:
  one_time_cents: 900
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-sonnet-4-6
    - gpt-4o
  estimated_tokens_per_invocation: 4000
trigger_keywords:
  - design critique
  - ui review
example_invocations:
  - "Critique this checkout flow screenshot."
inputs:
  - name: screenshot
    type: file
    required: true
    description: PNG/JPEG of the UI to critique.
outputs:
  - name: critique
    type: markdown
    description: 12-point scored critique with prioritized fixes.
changelog:
  - version: 2.1.0
    date: 2026-05-01
    notes: Added accessibility checks (contrast, focus order).
  - version: 1.0.0
    date: 2026-02-12
    notes: Initial release.
---

# Design Critique Rubric

## When to use
Use when a designer or PM shares a screen and asks "is this good?". Produces a
prioritized list of issues with specific fixes.

## How to apply
1. Run the 12-point rubric: hierarchy, alignment, contrast, spacing, typography,
   colour, copy, affordance, feedback, accessibility, consistency, polish.
2. Score each axis 1–5; flag any below 3 as blocking.
3. For each blocking axis, write a one-sentence fix.

## Inputs
- A clear screenshot of the UI under review.

## Outputs
- A markdown table with score + fix per axis.

## Examples
> "Critique this onboarding hero."

## Limitations
Vision-based; will be coarse on tiny details. Not a replacement for usability testing.
