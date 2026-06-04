---
id: skillsgit-curated/accessibility-reviewer
version: 1.0.0
name: Accessibility Reviewer
description: Audit a UI surface against WCAG 2.2 AA from a screenshot description, component source, or HTML markup, producing severity-classed findings with concrete remediations.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: design
tags: [a11y, wcag, accessibility, audit, aria, keyboard, contrast, review]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: [image_input]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - accessibility review
  - a11y audit
  - wcag check
  - aria review
  - keyboard navigation
  - color contrast
  - focus management
  - screen reader
  - inclusive design
  - touch target
  - reduced motion
  - accessibility findings
example_invocations:
  - "Review this modal component code for WCAG 2.2 AA compliance."
  - "Here's a screenshot of our checkout form — flag accessibility issues."
  - "Audit this HTML snippet for keyboard and screen reader problems."
  - "Check this date picker pattern against ARIA practices."
inputs:
  - name: artifact
    type: text
    required: true
    description: A pasted component source, HTML snippet, or detailed verbal description of the UI under review.
  - name: screenshot
    type: file
    required: false
    description: Optional image of the rendered UI. Triggers visual-only checks (contrast, focus visibility, target sizing) that source alone cannot answer.
  - name: scope
    type: choice
    required: false
    description: Conformance ceiling to target. Defaults to WCAG 2.2 AA.
    choices: [WCAG 2.1 AA, WCAG 2.2 AA, WCAG 2.2 AAA]
  - name: context
    type: text
    required: false
    description: Surrounding details — assistive tech in use, user population, regulated industry, prior known issues — that adjust severity.
outputs:
  - name: report
    type: markdown
    description: A structured review with an executive summary, findings grouped by severity, and a prioritized remediation backlog.
  - name: fixes
    type: markdown
    description: Concrete code-level or copy-level suggestions for each high and critical finding.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when an agent is asked to review the accessibility of a user interface and the input takes any of these shapes:

- A pasted component source file (React, Vue, Svelte, Angular, web component, plain HTML, JSX, TSX).
- A rendered screenshot or visual mockup of one or more screens.
- A spoken or written description of a UI ("a modal that traps focus and has an X icon in the top right…").
- A live URL pasted in for a static review of the markup it produces.

Avoid invoking this skill for purely functional bug reports, layout-only critiques, brand reviews, or copy edits — those are not in scope. Defer to a usability or visual design skill when the user wants a heuristic walkthrough that goes beyond conformance. Defer to a security skill if the artifact under review is server-side logic or auth flow.

This skill assumes the reviewer is asked to produce a written report rather than to interactively pilot assistive technology. It can recommend assistive technology tests for a human to run but cannot run them itself.

## How to apply

Work through the following procedure in order. Skip a step only when the input clearly does not contain the surface that step inspects, and say so in the report so the reader understands what was not examined.

1. Establish scope. Identify whether the input is source, screenshot, description, or a mix. Identify the target conformance ceiling — default to WCAG 2.2 AA when not specified. Record assumptions explicitly in a short preamble so the reader can challenge them.

2. Identify the widget pattern. Name the pattern the artifact most resembles (button, link, disclosure, accordion, tabs, dialog, alert dialog, combobox, listbox, menu, menubar, slider, switch, table, tooltip, toolbar, tree, treegrid, carousel, breadcrumb). The pattern selection drives every subsequent rule. If the artifact is a composition (a card containing a heading, image, and link), decompose into its constituent patterns and review each.

3. Inventory the interactive elements. List every element that receives focus, every element that fires a click or keypress, and every element that uses a native form control. Flag any focusable element built from a non-semantic tag (a `div` with an `onClick`, a `span` rigged with `tabindex`) and note the cost of that decision.

4. Audit semantics. For each interactive element, ask: is the role correct? Does the element communicate its name, role, value, and state? Native HTML elements are preferred over ARIA. Where ARIA is used, verify that the role is appropriate, that required ARIA properties for that role are present, and that no contradictory roles are stacked. Flag custom widgets that re-implement a native control without justification.

5. Audit names and descriptions. Every interactive element must have an accessible name. Prefer visible text. If an icon-only button is used, require an `aria-label`, an `aria-labelledby`, or visually hidden text. Flag duplicated names that refer to different targets ("Read more" repeated five times) and recommend disambiguation. Flag empty buttons, decorative images with non-empty alt text, and meaningful images with empty alt.

6. Audit keyboard support. For each pattern, list the expected key bindings and check whether the source implements them. Common expectations: a button activates on Enter and Space; a link activates on Enter; a dialog traps focus and restores it on close; a listbox supports arrow keys, Home, End, and type-ahead; a menu closes on Escape and returns focus to its trigger. Flag any focusable element that cannot be reached by Tab, any focus order that diverges from visual order without justification, and any keyboard trap that is not a deliberate modal.

7. Audit focus visibility. Confirm that every focusable element has a visible focus indicator that is not solely conveyed by color, that the indicator has at least a 3:1 contrast ratio against adjacent colors, and that the indicator is not occluded by sticky headers or overlapping elements. Flag the removal of the default outline without a replacement.

8. Audit color and contrast. For each text run on a background, request or estimate the foreground and background hex values and compute the contrast ratio. Body text needs at least 4.5:1; large text (18pt or 14pt bold and above) needs at least 3:1; UI components and graphical objects need at least 3:1. Flag low-contrast placeholder text, ghost buttons, gray-on-gray captions, and disabled-state text that is unreadable when it carries information the user must access.

9. Audit non-color signals. Any state, status, or required field that is communicated by color alone fails. Verify that errors, success states, required fields, and selected states also carry an icon, text, pattern, or position cue.

10. Audit touch targets. For pointer input, interactive controls should have a target size of at least 24 by 24 CSS pixels under WCAG 2.2 AA, with exceptions for inline links in prose and equivalent alternatives elsewhere on the page. Flag dense icon rows in toolbars, close buttons under 24 pixels, and adjacent targets that overlap their hit areas.

11. Audit motion and animation. Identify any animation that lasts longer than five seconds, loops, autoplays, or includes parallax. Confirm that the implementation respects the user's `prefers-reduced-motion` media query by disabling or reducing motion. Flag carousel autoplay without a pause control and large transform-based scroll effects.

12. Audit text resizing and reflow. The artifact must remain usable at 200% browser zoom and at a 320 CSS pixel viewport width with no loss of content or function and no horizontal scrolling outside legitimate two-dimensional content like maps or data tables. Flag fixed-pixel containers, overflow hidden on text, and text rendered inside images.

13. Audit form patterns. For every form control: there is a programmatically associated label; required state is conveyed in text not only color; instructions appear before the control; errors appear after submission with a clear association via `aria-describedby`; error messages are announced to screen readers via `aria-live` or by moving focus to a summary. Flag placeholder-as-label, error styling without text, and form-level error toasts that disappear before assistive technology can announce them.

14. Audit dynamic content and live regions. Any region that updates outside user-initiated focus changes — a toast, a results count, a chat message — must be announced via a polite or assertive live region or by moving focus deliberately. Flag silent updates of critical status and over-assertive live regions that interrupt the user constantly.

15. Audit modal and overlay behavior. A dialog must trap focus, restore focus to the invoking element on close, dismiss on Escape, and either inert or `aria-hidden="true"` the background. An alert dialog adds an immediate focus on a descriptive element. Flag dialogs that are merely visually overlaid without focus management.

16. Audit headings and landmarks. Headings should form a logical outline starting at h1 with no skipped levels. Landmarks — header, nav, main, aside, footer — should appear once where they map to a single region or be labeled when repeated. Flag skipped heading levels, multiple unlabeled navs, and entire pages lacking a main landmark.

17. Audit language and locale. The root element should declare a language. In-page language switches should be marked with `lang`. Right-to-left content should mirror appropriately. Flag missing language declarations and untranslated `aria-label` strings.

18. Audit time-based components. Session timeouts must offer extension; auto-refreshing content must offer pause; carousels must offer pause or be triggered by user input. Flag automatic logouts without warning and unstoppable rotators.

19. Audit content order. Verify that the DOM order and the visual order match, or that any divergence is intentional and does not break the user's understanding. Flag CSS-only repositioning that desynchronizes reading order.

20. Map findings to WCAG success criteria. For every finding, name the specific success criterion (for example, 1.4.3 Contrast Minimum, 2.1.1 Keyboard, 2.4.7 Focus Visible, 4.1.2 Name, Role, Value, 2.5.8 Target Size Minimum). This grounds the recommendation in a citation the reader can verify.

21. Classify severity. Use these tiers and be consistent:
    - **Critical** — blocks an entire population from completing a primary task (a checkout button that no keyboard user can reach).
    - **High** — significantly degrades the experience for a population (insufficient contrast on body copy, missing labels on form fields, unannounced errors).
    - **Medium** — adds friction but a workaround exists (skipped heading levels in a section, decorative animation that respects reduced motion only partially).
    - **Low** — minor polish (subtle focus ring style, redundant ARIA attributes that are not harmful).

22. Write each finding in a consistent shape: a title line, the WCAG citation, the affected element (with selector or screenshot region), the observed behavior, the expected behavior, the user impact, and a concrete fix. Avoid generic phrases like "add ARIA" — name the attribute, value, and the element it belongs on.

23. Sequence remediations. Provide a prioritized backlog at the end. Order by severity first and by estimated effort second. For each high or critical finding, draft a one-paragraph fix that a developer could paste into a ticket without further research.

24. Distinguish what was tested from what was inferred. If you reviewed only source, you cannot verify rendered contrast — say so, recommend a visual sweep, and mark contrast findings as provisional. If you reviewed only a screenshot, you cannot inspect ARIA — say so and recommend a source pass.

25. Recommend follow-up testing. Suggest manual assistive technology testing on at least one screen reader and browser combination (NVDA + Firefox, VoiceOver + Safari, JAWS + Chrome, TalkBack + Chrome). Recommend a keyboard-only walkthrough and a 200% zoom pass.

26. End with an executive summary the reader sees first. State the total findings by severity, the top three issues, and whether the surface is likely to meet the stated conformance ceiling after the proposed fixes.

27. Be honest about uncertainty. If a pattern is ambiguous or genuinely contested in the accessibility community — for example, when to use a button versus a link versus a tab, or how aggressively to use `aria-live` — say so and present the trade-off.

28. Maintain a respectful tone. The output is read by designers and engineers who care. Be precise about defects, generous about intent, and concrete about fixes. Avoid moralizing.

## Inputs

- A source snippet, an HTML fragment, a screenshot, or a verbal description of the surface to review.
- The conformance target if it differs from WCAG 2.2 AA.
- Optional context — assistive tech, regulated industry, prior audits — that should shift the severity calibration.

## Outputs

- A markdown report with a one-screen executive summary, findings grouped by severity, each citing a WCAG success criterion, each with a concrete fix.
- A prioritized remediation backlog ordered by severity then effort.
- A scope statement that lists what was not examined and why.

## Examples

### Example 1 — Source review of a custom toggle

Input: a React component that renders a `div` with `onClick` toggling a class.

Output excerpt:

- Critical — 4.1.2 Name, Role, Value. The component renders a non-semantic `div` with no role, name, or state. Keyboard users cannot reach it; screen readers announce nothing. Replace with a native `button` and use `aria-pressed` to communicate state. Move the click handler to the button; bind Space and Enter via the native button semantics. Restore a visible focus ring with at least 3:1 contrast.
- High — 1.4.11 Non-text Contrast. The off-state thumb is `#cccccc` on a `#eeeeee` track. Contrast is below the 3:1 minimum for UI components. Recommend the off-state token from the design system instead.

### Example 2 — Screenshot review of a checkout form

Input: a screenshot showing a checkout form with light gray placeholder labels inside inputs.

Output excerpt:

- High — 3.3.2 Labels or Instructions. Placeholder text is used as the only label. When the user begins typing, the field's purpose disappears. Add a visible label above each input and keep the placeholder only for format hints (or remove it).
- High — 1.4.3 Contrast (Minimum). The "Continue" button text appears to be `#ffffff` on `#cfd8dc`. Estimated ratio is 1.9:1. Increase to a darker brand color or change the text to a darker tone.

### Example 3 — Description review of a search combobox

Input: a description of a combobox where typing filters a list and Enter selects the highlighted item.

Output excerpt:

- Medium — 4.1.2 Name, Role, Value. Confirm that the input has `role="combobox"`, `aria-expanded`, `aria-controls` pointing at the popup, and `aria-activedescendant` pointing at the highlighted option. The popup should be `role="listbox"` with `role="option"` items.
- Medium — 2.1.1 Keyboard. Verify Arrow Down opens the popup when closed, Arrow Up/Down move the active option, Home/End jump, Escape closes and returns focus to the input, and Enter both selects and closes.

## Limitations

- Cannot measure rendered contrast precisely from a screenshot without color values; estimates assume sRGB and ignore subpixel anti-aliasing.
- Cannot detect dynamic behavior from source alone (for example, JavaScript-driven focus restoration); recommends a manual pass.
- Cannot verify assistive technology announcement quality without an actual screen reader; recommends a manual test run.
- WCAG citations are guides, not legal advice. Regulated industries may have additional rules (Section 508, EAA, AODA, EN 301 549) — the report flags them when scope mentions them, but full legal review is out of scope.
- Severity calibration is a judgment call. Two reviewers may legitimately disagree on whether a given issue is high or medium.

## Sources reviewed

- https://github.com/radix-ui/primitives
- https://github.com/tailwindlabs/headlessui
- https://github.com/adobe/react-spectrum
- https://github.com/KittyGiraudel/a11y-dialog
- https://github.com/chakra-ui/chakra-ui
- https://github.com/carbon-design-system/carbon
- https://github.com/primer/css
