---
id: skillsgit-curated/design-token-system-critic
version: 1.0.0
name: Design Token System Critic
description: Audit a proposed design token system across color, type, spacing, radius, shadow, and motion for consistency, semantic naming, theme-ability, dark/light coverage, and an accessibility floor.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: design
tags: [design-tokens, design-system, theming, naming, dark-mode, contrast]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - design tokens
  - design system
  - token audit
  - token naming
  - theming
  - dark mode tokens
  - semantic tokens
  - typography scale
  - spacing scale
  - color tokens
  - motion tokens
  - token critique
example_invocations:
  - "Review our proposed color token set for dark mode coverage."
  - "Critique this spacing scale before we lock it in."
  - "Are these semantic token names consistent across our component library?"
  - "Does our type ramp work at 200% zoom and in long-form content?"
inputs:
  - name: tokens
    type: text
    required: true
    description: The proposed token system. Accepts JSON, YAML, CSS custom properties, a style-dictionary-style tree, a Tokens Studio export, or a plain list with values.
  - name: target_themes
    type: text
    required: false
    description: Names of themes the system must cover — for example "light, dark, high-contrast" or "consumer, enterprise, partner-brand."
  - name: platforms
    type: choice
    required: false
    description: Platforms the tokens must compile to.
    choices: [web, ios, android, multi-platform]
  - name: constraints
    type: text
    required: false
    description: Brand, regulatory, or product constraints — for example "must meet WCAG 2.2 AA on every named pair" or "must reuse existing primitive ramp."
outputs:
  - name: critique
    type: markdown
    description: A structured review covering coverage gaps, naming consistency, hierarchy soundness, accessibility floor, and theme-ability.
  - name: recommendations
    type: markdown
    description: A prioritized list of changes with concrete renamings, additions, and removals.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Reach for this skill when an agent is asked to evaluate, critique, or stress-test a design token system before adoption or before a major refactor. Typical situations:

- A design-systems team has drafted a v1 token tree and wants outside review.
- An organization is migrating from hard-coded values to tokens and needs a sanity check before committing.
- A product team has added a new theme — dark mode, high-contrast, a partner brand — and wants coverage verified.
- A new platform target — iOS, Android, watchOS — is being onboarded and the token set must compile to it cleanly.
- A token system has accumulated technical debt and needs a structured audit before consolidation.

Skip this skill if the input is a single component's styles rather than a system, if the request is to generate tokens from scratch with no input, or if the request is for visual design taste — this skill audits structure, naming, coverage, and accessibility floor, not aesthetic preference.

## How to apply

Work the audit in this order. Skip steps that the input genuinely does not cover and say so in the report.

1. Identify the token layers. Most mature systems separate three layers: primitives (raw values like `blue-500: #2563eb`), semantic tokens (meaning-bearing names like `color-surface-action`), and component tokens (component-scoped names like `button-primary-bg`). Note which layers the proposal includes. A flat system without semantic indirection is a red flag — it makes theming and reskinning painful.

2. Inventory the token categories. Walk the input and group tokens by category: color, typography (family, size, weight, line height, letter spacing), spacing, radius, border width, shadow/elevation, motion (duration, easing), opacity, z-index, breakpoints, and asset sizes. Note any category that is missing entirely.

3. Audit primitive coverage. For color, expect a ramp per hue with at least seven to twelve stops, plus neutrals. Confirm the ramp is perceptually even — equal lightness steps, not arbitrary mixes. Confirm that names are stable across hues (each hue has the same set of stops). For neutrals, confirm a dedicated ramp with enough stops to support borders, surfaces, dividers, and text on backgrounds.

4. Audit the type ramp. Confirm sizes follow a consistent scale (modular ratio, t-shirt sizes, numeric tokens). Confirm there are not too many sizes — beyond eight or nine, the system becomes harder to reason about. Verify that line height is defined alongside size, that weights are constrained to those the font file supports, and that letter spacing is defined where it changes perceptibly across sizes.

5. Audit the spacing scale. A base unit (commonly 4 or 8 pixels) plus a consistent multiplier is preferred. Flag arbitrary one-offs like `13px`. Confirm the scale stretches to the largest needed gap and does not require ad hoc additions for hero layouts. Confirm that spacing tokens are not duplicated as ad hoc margins inside component tokens.

6. Audit the radius scale. A small set — for example none, xs, sm, md, lg, xl, full — is sufficient. Flag any component using a raw radius that does not match a token. Confirm a `radius-full` or `radius-pill` exists for circular elements.

7. Audit the shadow or elevation scale. Confirm a small number of named levels (resting, hover, raised, overlay, modal) rather than per-component shadow blobs. Confirm dark mode has a separate set — light-mode shadows often disappear or look wrong on dark surfaces.

8. Audit the motion tokens. Confirm distinct duration tokens (instant, fast, normal, slow, deliberate) and easing tokens (standard, emphasized, decelerate, accelerate). Confirm there is a reduced-motion equivalent or guidance about how to disable motion at the system level when `prefers-reduced-motion: reduce` is set.

9. Audit semantic indirection. For every place a component would consume color, ask: is there a semantic token like `color-text-default`, `color-text-subtle`, `color-text-inverse`, `color-surface-default`, `color-surface-raised`, `color-border-default`, `color-border-strong`, `color-action-default`, `color-action-hover`, `color-action-pressed`, `color-feedback-success`, `color-feedback-danger`, `color-feedback-warning`, `color-feedback-info`? If the answer is no, the system will leak primitives into components and every reskin will be a search-and-replace project.

10. Audit naming consistency. Choose a naming convention — dot, dash, slash, camel, BEM-like — and confirm the proposal sticks to it. Confirm category order (category-role-variant-state, for example `color-text-default-hover`) is consistent. Flag mixed orders like `text-color-default` next to `color-text-default`.

11. Audit naming clarity. Names should describe meaning, not appearance. `color-warning` survives a brand refresh; `color-yellow` does not. Allow a primitive layer to carry color names; semantic and component layers should not. Flag semantic names that bake in appearance (`color-text-blue`).

12. Audit token collisions. Search for tokens that resolve to the same primitive but mean different things — for example `color-surface-default` and `color-background-default` both pointing at `neutral-0`. Decide whether the duplication is harmful or merely two names for the same concept and consolidate where it is harmful.

13. Audit dark-mode coverage. For every semantic token defined in the light theme, confirm a dark-mode counterpart exists. Flag missing pairs. Confirm that dark mode is not simply inverted lightness — shadows, brand colors, and saturations usually need bespoke adjustments. Confirm that semantic tokens, not primitives, are the swap targets.

14. Audit high-contrast or accessibility theme coverage if claimed. A high-contrast theme typically increases border weight, lifts contrast ratios to AAA where possible, and reduces gradients. Confirm that those tokens are independent of the light/dark switch.

15. Audit accessibility contrast floors. For every named text-on-surface pair in the semantic layer, compute the contrast ratio in both light and dark themes. Body text must clear 4.5:1; large text and UI components must clear 3:1. Flag every pair that does not meet the floor and propose the nearest primitive that does. Pay special attention to subtle, secondary, and disabled text tokens — these are the most common offenders.

16. Audit focus indicator tokens. Confirm there is a dedicated `color-border-focus` or `color-outline-focus` semantic token, that its contrast against adjacent surfaces meets 3:1, and that its width and offset are also tokenized. Flag systems that rely on browser defaults or leave focus styling to component authors.

17. Audit state coverage. For every interactive surface (action, link, input, selection), expect default, hover, pressed, focused, disabled, and selected states as semantic tokens. Flag missing states. Confirm disabled states do not communicate critical information by color alone.

18. Audit gradient and overlay tokens. Where gradients are used for surfaces, scrim, or skeleton states, confirm they are tokenized with explicit stops. Flag inline gradients in component styles.

19. Audit asset and icon size tokens. Icons should pull from a small named set (`size-icon-sm`, `size-icon-md`, `size-icon-lg`). Avatars likewise. Confirm these are not duplicated as raw pixel values across components.

20. Audit responsive coverage. Confirm there is a token set for breakpoints. Confirm that spacing and type ramps include responsive variants where the system supports fluid scaling (clamps, container queries, or tier-by-tier overrides).

21. Audit platform translation. If the system targets iOS and Android in addition to web, confirm the tokens compile cleanly — colors as named resources, spacing as densities or points, type weights mapped to platform font systems. Flag any token that depends on a web-only construct (a CSS function, a relative unit) without a documented platform equivalent.

22. Audit theme switching mechanics. Confirm that themes are swappable at the semantic layer without touching primitives. Confirm that the swap is technically achievable (CSS custom property cascade, a theme provider, a per-platform asset bundle). Flag systems where dark mode requires a primitive ramp change.

23. Audit deprecation and aliasing strategy. A maturing system needs aliases that hold names stable while the underlying primitives evolve. Flag the absence of an alias layer or deprecation labels.

24. Audit documentation and discoverability. Confirm that every token has a description and an example. Confirm there is a single canonical source — a JSON file, a style-dictionary tree, a Tokens Studio export — and that downstream artifacts (CSS, SCSS, Swift, Kotlin) are generated from that source rather than maintained by hand.

25. Cross-check against component library. Where the input includes component styles, sample five to ten components and verify that every hard-coded value can be traced to a token. Flag inline values, magic numbers, and aliased component tokens that lack a semantic backer.

26. Stress-test with edge cases. Ask: how does this system render an extreme dark mode? a partner brand reskin? a high-contrast theme? a small mobile screen at 200% zoom? a long-form text page? Each stress test usually surfaces a missing token or a missing layer of indirection.

27. Produce a categorized critique. Group findings as Structure (layering and naming), Coverage (missing tokens, missing themes), Accessibility (contrast and focus), Consistency (naming, collisions, duplicates), Theme-ability (swap mechanics), and Platform (translation gaps). Each finding includes the token in question, the observed issue, the user or developer impact, and a concrete proposal.

28. Prioritize. Tag each finding as Blocker (the system cannot ship with this), Important (should be fixed before broad adoption), or Polish (improves the experience but is not load-bearing). Order findings by tag, then by category, then by frequency across the system.

29. Suggest next steps. Recommend a remediation order: usually fix structure and layering first, then accessibility floor, then naming and coverage, then platform translation. Note which steps require redesign versus rename.

30. Distinguish opinion from rule. When the critique reflects a stylistic preference rather than a rule (single-axis spacing scale versus dual-axis, t-shirt sizes versus numeric), label it as opinion and offer the alternative.

## Inputs

- A token set in any of the common formats — JSON, YAML, CSS custom properties, style-dictionary tree, Tokens Studio export, or a hand-written list.
- The themes the system must cover (light, dark, high-contrast, brand variants).
- The platforms the tokens compile to.
- Brand, accessibility, or platform constraints to apply.

## Outputs

- A categorized critique grouped by Structure, Coverage, Accessibility, Consistency, Theme-ability, and Platform.
- A prioritized remediation list — Blocker, Important, Polish — with concrete proposals.
- An explicit list of stress tests that were applied and the result of each.

## Examples

### Example 1 — Audit of a flat color set

Input: a color palette with thirty named tokens like `color-blue`, `color-blue-light`, `color-blue-dark`, `color-error`, `color-error-light`, `color-background`, `color-text`.

Output excerpt:

- Blocker — Structure. The proposal has no separation between primitives and semantic tokens. Every component will encode brand-specific names, making theming and reskinning manual. Introduce a primitive ramp (`blue-50` through `blue-900`) and a semantic layer (`color-action-default`, `color-text-default`, `color-surface-default`). Reserve hue-based names for the primitive layer.
- Important — Coverage. There is no token for hover, pressed, or focused states. Add `color-action-hover`, `color-action-pressed`, `color-border-focus`.
- Important — Accessibility. `color-text` resolves to `#5b6b7c` on `color-background` (`#ffffff`). Contrast is 4.18:1 — below the 4.5:1 floor for body text. Replace with `#475569` or darker.

### Example 2 — Audit of a spacing scale

Input: `space-1: 4px`, `space-2: 8px`, `space-3: 12px`, `space-4: 16px`, `space-5: 20px`, `space-6: 24px`, `space-7: 32px`, `space-8: 40px`, `space-9: 64px`, `space-10: 80px`.

Output excerpt:

- Polish — Consistency. The scale uses a 4px base from steps 1 through 6, then jumps to 32px for step 7 and 64px for step 9. The non-linear progression is fine for hero spacing but breaks intuition. Document the rationale and consider renaming the upper steps semantically (`space-section`, `space-page`) to communicate that they are not part of the linear ramp.
- Important — Coverage. There is no token for `space-0` (zero) or `space-px` (one-pixel separators). Add both to avoid magic numbers downstream.

### Example 3 — Audit of dark mode coverage

Input: a semantic token set with eighteen color tokens defined in light and twelve defined in dark.

Output excerpt:

- Blocker — Coverage. Six light-mode semantic tokens have no dark-mode counterpart, including `color-surface-raised`, `color-border-strong`, and `color-feedback-warning-subtle`. Components that consume these will render unstyled or fall back to primitives in dark mode.
- Important — Accessibility. In dark mode, `color-text-subtle` (`#8a93a4`) on `color-surface-default` (`#0e131a`) is 4.7:1 — passes for body text. In light mode, the same semantic token resolves to `#94a3b8` on `#ffffff`, which is 3.4:1 — fails. Lift the light value to `#475569` or restrict the semantic token to large-text contexts.

## Limitations

- Cannot verify a Figma or design-tool export's binary fidelity; assumes the input represents the intended values accurately.
- Cannot taste-test a brand — does not opine on whether a hue feels on-brand, only whether the tokens are structurally sound.
- Contrast checks assume sRGB. Wide-gamut and HDR pipelines may need additional review with platform-specific tools.
- Cannot guarantee platform compilation — recommends a generation pass through a token transformer and a visual diff before adoption.
- Naming is partly cultural. Some recommendations reflect prevalent conventions and may not match an organization's house style; the critique flags them as opinion when so.

## Sources reviewed

- https://github.com/style-dictionary/style-dictionary
- https://github.com/tokens-studio/sd-transforms
- https://github.com/primer/css
- https://github.com/carbon-design-system/carbon
- https://github.com/chakra-ui/chakra-ui
- https://github.com/adobe/react-spectrum
