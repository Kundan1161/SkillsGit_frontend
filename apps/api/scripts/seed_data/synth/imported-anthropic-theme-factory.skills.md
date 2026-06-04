---
id: skillsgit-curated/imported-anthropic-theme-factory
version: 1.0.0
name: "Theme Factory"
description: "Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to any artifact that has been creating, or can generate a new theme on-the-fly."
authors:
  - name: "Anthropic (original)"
    handle: anthropic
    role: author
  - name: "skillsgit Curated"
    handle: skillsgit-curated
    role: maintainer
category: design
tags: [imported, source-anthropics-skills, theming, design-system, color, typography]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - theme
  - factory
  - toolkit
  - styling
  - artifacts
example_invocations:
  - "Use the theme factory skill on this."
  - "Apply theme factory guidance to my work."
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: "Imported from anthropics/skills under Apache-2.0."
---
## When to use

Use this skill when: Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to any artifact that has been creating, or can generate a new theme on-the-fly.

_Note: this section was added during import to satisfy the marketplace validator. The original Anthropic skill expresses its trigger conditions throughout the body below._

## How to apply

Follow the instructional content in the sections below. The original skill body (preserved verbatim) contains the step-by-step guidance. Read it top-to-bottom, treat any `## Overview` / introductory paragraphs as orientation, then execute the numbered or sub-headed procedures as written.

_Note: this section was added during import to satisfy the marketplace validator._

# Theme Factory Skill

This skill provides a curated collection of professional font and color themes themes, each with carefully selected color palettes and font pairings. Once a theme is chosen, it can be applied to any artifact.

## Purpose

To apply consistent, professional styling to presentation slide decks, use this skill. Each theme includes:
- A cohesive color palette with hex codes
- Complementary font pairings for headers and body text
- A distinct visual identity suitable for different contexts and audiences

## Usage Instructions

To apply styling to a slide deck or other artifact:

1. **Show the theme showcase**: Display the `theme-showcase.pdf` file to allow users to see all available themes visually. Do not make any modifications to it; simply show the file for viewing.
2. **Ask for their choice**: Ask which theme to apply to the deck
3. **Wait for selection**: Get explicit confirmation about the chosen theme
4. **Apply the theme**: Once a theme has been chosen, apply the selected theme's colors and fonts to the deck/artifact

## Themes Available

The following 10 themes are available, each showcased in `theme-showcase.pdf`:

1. **Ocean Depths** - Professional and calming maritime theme
2. **Sunset Boulevard** - Warm and vibrant sunset colors
3. **Forest Canopy** - Natural and grounded earth tones
4. **Modern Minimalist** - Clean and contemporary grayscale
5. **Golden Hour** - Rich and warm autumnal palette
6. **Arctic Frost** - Cool and crisp winter-inspired theme
7. **Desert Rose** - Soft and sophisticated dusty tones
8. **Tech Innovation** - Bold and modern tech aesthetic
9. **Botanical Garden** - Fresh and organic garden colors
10. **Midnight Galaxy** - Dramatic and cosmic deep tones

## Theme Details

Each theme is defined in the `themes/` directory with complete specifications including:
- Cohesive color palette with hex codes
- Complementary font pairings for headers and body text
- Distinct visual identity suitable for different contexts and audiences

## Application Process

After a preferred theme is selected:
1. Read the corresponding theme file from the `themes/` directory
2. Apply the specified colors and fonts consistently throughout the deck
3. Ensure proper contrast and readability
4. Maintain the theme's visual identity across all slides

## Create your Own Theme
To handle cases where none of the existing themes work for an artifact, create a custom theme. Based on provided inputs, generate a new theme similar to the ones above. Give the theme a similar name describing what the font/color combinations represent. Use any basic description provided to choose appropriate colors/fonts. After generating the theme, show it for review and verification. Following that, apply the theme as described above.

## Attribution

This skill was imported from the public `anthropics/skills` repository under the Apache-2.0 license. Original content authored by Anthropic. Modifications by skillsgit: frontmatter normalization to fit marketplace spec, addition of attribution and sources sections. The original LICENSE and NOTICE files are preserved at the source repository.

## Sources reviewed
- https://github.com/anthropics/skills/tree/main/skills/theme-factory (Apache-2.0)
