---
id: skillsgit-curated/component-api-designer
version: 1.0.0
name: Component API Designer
description: Recommend a clean, composable component API — props, slots, events, refs, polymorphism, and controlled/uncontrolled patterns — given a component's intent and constraints.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: design
tags: [component-api, design-system, props, composition, headless, ergonomics]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - component api
  - props design
  - headless component
  - controlled uncontrolled
  - composition
  - polymorphism
  - slot api
  - render prop
  - component library
  - design system api
  - component ergonomics
  - prop drilling
example_invocations:
  - "Design the API for a Combobox we want to ship in our design system."
  - "Critique this Dialog component's prop surface."
  - "Help us decide between a configuration-style and a composition-style menu API."
  - "What should our Tabs component's props look like?"
inputs:
  - name: component_intent
    type: text
    required: true
    description: A description of what the component does — its role, the patterns it should support, and the audience.
  - name: existing_api
    type: text
    required: false
    description: An existing component signature to critique. JSX/TSX type signatures, Vue props, Svelte $props, or a TypeScript interface are all accepted.
  - name: constraints
    type: text
    required: false
    description: Framework target, design-system layer (primitive, semantic, composite), tree-shaking requirements, and any compatibility commitments.
  - name: comparable_libraries
    type: text
    required: false
    description: Libraries the team wants to feel familiar to — often Radix, Headless UI, React Aria, MUI, Chakra, Carbon, or Ant Design.
outputs:
  - name: api_proposal
    type: markdown
    description: A recommended component signature with rationale, alternative trade-offs, and worked example invocations.
  - name: critique
    type: markdown
    description: When an existing API is supplied, a structured critique with concrete renamings and refactors.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when an agent needs to design or review the public surface of a component. Concrete triggers:

- A design-system team is about to start a new component and wants a recommended prop and slot shape before writing code.
- A team is refactoring a component whose API has grown unwieldy through years of additions.
- Reviewers disagree about whether to expose a feature as a prop, a render slot, an event, or a context provider, and need an external opinion.
- A library is migrating from a configuration-heavy API to a composition-heavy one and wants a reference shape.
- A new framework target is being added and the existing API needs adaptation guidance.

Skip this skill if the task is implementation help — writing the component's internals, fixing a bug, or styling — rather than shaping the public surface. Skip when the question is about visual design rather than API design.

## How to apply

Work the design pass in order. The early steps narrow the scope; the later steps shape the signature.

1. Clarify the component's role in the system. Is it a primitive (unstyled, behavior-only — a focus trap, a popper, a dialog mechanism), a semantic component (the design system's branded version of a primitive), or a composite (a configured pattern like a checkout form)? The role determines how opinionated the API should be.

2. Identify the canonical pattern. Compare the intent against well-known patterns: button, link, toggle, switch, checkbox, radio, segmented control, accordion, disclosure, tabs, dialog, alert dialog, drawer, popover, tooltip, menu, menubar, combobox, listbox, select, autocomplete, slider, date picker, table, tree, breadcrumb, pagination, carousel, toast. Name the pattern explicitly so the user can challenge the framing.

3. List the responsibilities. Write down what the component owns: state, behavior, accessibility semantics, focus management, keyboard handling, layout, and styling hooks. Decide which responsibilities are mandatory and which are opt-in.

4. Decide the controlled/uncontrolled posture. Most stateful components should support both:
   - Uncontrolled — the component manages its own state via an internal hook; consumers pass `defaultValue` (or `defaultOpen`, `defaultChecked`).
   - Controlled — the consumer owns state and passes `value` (or `open`, `checked`) plus an `onChange` (or `onOpenChange`).
   Document the rule clearly: pass `defaultValue` for uncontrolled, pass `value` and `onChange` together for controlled, never mix the two without a warning. Type the signature so misuse is caught at compile time.

5. Decide composition style. Two ends of a spectrum:
   - Configuration — one component with many props (`<Select options={[…]} placeholder="…" disabled multiple searchable />`). Easy to start with, hard to extend.
   - Composition — a family of parts that the consumer assembles (`<Select.Root><Select.Trigger /><Select.Content><Select.Item /></Select.Content></Select.Root>`). Verbose at the call site but flexible and extensible.
   For primitives and complex widgets, prefer composition. For simple controls that have one canonical shape, configuration is fine. State both options in the proposal and recommend the one that fits the team's stage.

6. Define the part inventory if composition. Name each compound part precisely. Common patterns:
   - Root — owns context and state.
   - Trigger — the element the user interacts with to open or activate.
   - Content — the popped or expanded surface.
   - Item — a child within content.
   - Label, Description, Group — semantic grouping inside content.
   - Indicator, Icon — visual sub-elements that consumers may want to replace.
   Keep the naming consistent across all components in the system so consumers can guess the shape of a component they haven't used yet.

7. Choose between props, slots, and render functions for content holes. Three options:
   - Children — the most ergonomic when consumers want to drop in arbitrary JSX.
   - Named slots — a prop per content area (`leadingIcon`, `trailingIcon`). Use when the component shapes the slot specifically.
   - Render props or function children — when the consumer needs access to internal state to render. Provide a `{state, methods}` shape.
   Avoid double-exposure (the same content available through children and a prop) unless one is a deprecated path.

8. Design the event surface. Event handlers should use the framework's idiomatic naming (`onSelect`, `onOpenChange`, `onValueChange`, `onPressStart`). Each handler receives a typed payload. Avoid synthetic events that wrap framework events without adding value. Avoid event names that imply a DOM event the component does not emit (`onClick` on a non-clickable wrapper).

9. Decide on polymorphism. A common pattern allows a primitive to render as a different element via an `as` prop, an `asChild` boolean, or a render prop. Polymorphism is powerful but creates type complexity. Recommend `asChild` (slot-clone style) for headless primitives and `as` (element override) for styled wrappers. Avoid letting a component change its semantic role through polymorphism — a button-shaped link should stay a link.

10. Define accessibility props. Most components should accept `aria-label`, `aria-labelledby`, `aria-describedby`, and pass through unknown ARIA attributes by default. Document which ARIA properties the component manages internally so consumers do not collide. Provide an explicit prop when accessibility requires a value the component cannot infer (a date picker needs an `aria-label` on the underlying input if no visible label exists).

11. Design imperative escape hatches. Some interactions need an imperative API: focusing a field, opening a popover from a non-trigger source, scrolling an item into view. Expose these through a `ref` with a typed handle (`focus()`, `open()`, `close()`, `scrollToItem(value)`). Keep the imperative surface small — declarative props are easier to reason about.

12. Decide how to handle forwarded refs. Every interactive element should forward its DOM ref to the underlying focusable node. Document the ref target precisely so consumers know what they get.

13. Decide how to handle additional DOM attributes. The component should spread arbitrary `data-*` and `aria-*` attributes onto the appropriate underlying node. Style props (`className`, `style`) should merge with the component's own values rather than replace them.

14. Choose default values with care. Defaults define the canonical behavior. Aggressive defaults (autofocus, autosubmit, autoclose) surprise consumers. Conservative defaults (everything off until requested) are usually safer for a primitive; semantic components can be more opinionated.

15. Decide what to type narrowly versus loosely. Use string-literal unions for finite states (`"open" | "closed"`, `"primary" | "secondary" | "ghost"`). Use enums sparingly — they constrain consumers to import the enum. Use template literal types for tokenized values (`` `space-${number}` ``) when the system provides a finite set.

16. Decide on size and variant props. For semantic components, expect `size` and `variant` props with token-aligned values. For primitives, do not bake size and variant in — leave styling to the consumer.

17. Decide on disabled, loading, and busy states. Provide a `disabled` prop that maps to the native attribute on form controls. Provide a `loading` or `busy` prop for asynchronous actions; document whether `loading` implies `disabled`. Provide an `aria-busy` mapping when relevant.

18. Decide on form integration. Components that participate in forms should accept `name`, `value`, `defaultValue`, `required`, and integrate with native form submission. Document whether the component renders a hidden input under the hood. Plan for form library integration (uncontrolled refs, controlled values via `onChange`).

19. Decide on internationalization. Accept locale-sensitive props (date format, number format, direction). Avoid hard-coded English strings — accept label props for "Close", "Previous", "Next" rather than hard-coding them.

20. Decide on theming hooks. Where styling is shipped, expose CSS custom properties or class-name slots that consumers can override without forking. Document the public CSS surface so it can evolve without breaking consumers.

21. Decide on context propagation. Compound components usually pass state through context. Document the context shape so consumers can build their own parts that participate. Avoid leaking implementation details — the context type is part of the public API.

22. Audit naming consistency across the library. Names like `onChange`, `onValueChange`, `onSelect`, `onSelectionChange` proliferate inconsistently across libraries. Pick one and apply uniformly. The same goes for `open`/`isOpen`/`expanded`, `disabled`/`isDisabled`, `loading`/`isLoading`.

23. Sketch the call site. Write out three or four realistic usage examples — minimum invocation, fully controlled, composed with custom parts, integrated with a form. If a use case feels noisy, the API has the wrong center of gravity.

24. Audit the prop surface size. A primitive that exposes more than ten or twelve props is usually doing too much; consider composition. A semantic component can carry more (size, variant, loading, leading icon, trailing icon, helper text) but should still feel scannable.

25. Audit boolean prop proliferation. Five booleans are usually four too many. Collapse into a string-literal union (`tone="default" | "success" | "warning" | "danger"`) or compose with sub-parts.

26. Audit prop name clarity. `inverted` is unclear; `tone="inverse"` is better. `pill` is unclear; `radius="full"` is better. Names should describe meaning, not appearance metaphors.

27. Audit unsafe coupling. A `style` prop that overrides every internal style invites future breakage. A `className` prop that fully replaces the internal class deprives the system of base behavior. Provide additive APIs (merge, not replace) and document the contract.

28. Document deprecation. If renaming a prop, ship both for a release with a console warning and a clear migration path. Mark the old name `@deprecated` in TypeScript so editor tooling surfaces it.

29. Write the API proposal. Produce a TypeScript-style signature for each part, a call-site example, a rationale paragraph, and a list of alternatives considered. The rationale should reference the trade-offs above — controlled versus uncontrolled, composition versus configuration, polymorphism style.

30. Distinguish opinion from rule. Some choices are stylistic; say so. Some are forced by accessibility or framework idioms; say so too. End with three to five trade-off bullets so the team understands what they are giving up.

## Inputs

- A description of the component's intent — what it does, who uses it, what patterns it should support.
- An existing API to critique, when relevant.
- Constraints — framework target, layer in the design system, comparable libraries the team wants to feel familiar to.

## Outputs

- A recommended API as a typed signature for each part of the component.
- One or more call-site examples covering minimum, controlled, composed, and form-integrated usage.
- A rationale that names the trade-offs taken and the alternatives considered.
- A critique with concrete refactors when an existing API was supplied.

## Examples

### Example 1 — Combobox API recommendation

Input: "Design a combobox for our design system. It should support async loading, multi-select, and integration with our form library."

Output excerpt — recommended composition:

- `Combobox.Root` — owns state; accepts `value` and `onValueChange` for controlled, `defaultValue` for uncontrolled, `multiple`, `disabled`, `name` (for form integration), `loading`.
- `Combobox.Input` — the search input; forwards ref; accepts `placeholder` and ARIA passthrough.
- `Combobox.Trigger` — optional pop-on-click affordance; spreads to a button.
- `Combobox.Content` — popped panel; accepts `loading` to display a sentinel.
- `Combobox.Item` — accepts `value` and `disabled`; renders a focus ring at the root.
- `Combobox.Empty` — shown when no matches; supports custom children.
- `Combobox.Group` and `Combobox.GroupLabel` — for grouping options.

Rationale: composition over configuration because the multi-select, async, and form variants would otherwise each add three to five props at the root. Controlled and uncontrolled both work; passing `value` without `onValueChange` is a type error. Form integration is automatic when `name` is supplied; otherwise the component is purely declarative.

### Example 2 — Critique of an existing Dialog API

Input: an existing API with props `show: boolean`, `onShow`, `onHide`, `closeOnEscape`, `closeOnBackdrop`, `size: "sm" | "md" | "lg"`, `title: string`, `body: ReactNode`, `footer: ReactNode`, `centered: boolean`, `scrollable: boolean`.

Output excerpt:

- Rename `show` and the `onShow`/`onHide` pair to `open` and `onOpenChange`. The current pair forces consumers to wire two callbacks; a single boolean changer matches the rest of the ecosystem and reduces typos.
- Replace `title`, `body`, `footer` props with compound parts (`Dialog.Title`, `Dialog.Description`, `Dialog.Footer`). The current shape blocks consumers who want to interleave custom content between the title and the body, and it duplicates the rendering hole — content goes in `body` and in children inconsistently.
- Remove `centered` and `scrollable`. These are presentational concerns better handled via CSS or via a layout token. The component should not own them.
- Keep `size` but constrain it to the system's t-shirt scale.
- Add `defaultOpen` for uncontrolled use.
- Add an `onEscapeKeyDown` and `onInteractOutside` event surface so consumers can prevent close per gesture; document `closeOnEscape` and `closeOnBackdrop` as derivable from those handlers.

### Example 3 — Tabs API for a primitive layer

Input: "Tabs primitive, headless, framework is React. Accessible. Will be styled by downstream consumers."

Output excerpt — minimum surface:

- `Tabs.Root` — props: `value`, `defaultValue`, `onValueChange`, `orientation: "horizontal" | "vertical"`, `activationMode: "automatic" | "manual"`.
- `Tabs.List` — passes ARIA `role="tablist"`; spreads.
- `Tabs.Trigger` — props: `value` (required), `disabled`.
- `Tabs.Content` — props: `value` (required), `forceMount`.

Rationale: no styling props at the primitive layer — styling is the consumer's responsibility. `activationMode` follows the ARIA Authoring Practices distinction between automatic (focus = select) and manual (focus then explicit select). `forceMount` is offered for animated transitions where the consumer needs the content to stay in the DOM during exit animations.

## Limitations

- Recommends shapes that fit the patterns surveyed in the source libraries; bespoke domains may have legitimate reasons to deviate.
- Cannot guarantee binary compatibility with a specific library or framework — recommendations reference idioms common across React, Vue, Svelte, and Solid but may need translation.
- Does not produce implementation code; the output is the API surface and rationale, not the internals.
- TypeScript-specific recommendations may not translate cleanly to dynamic languages or to frameworks without rich type inference.
- Naming choices reflect prevalent conventions and may not match an organization's house style; the proposal flags those choices as opinion.

## Sources reviewed

- https://github.com/radix-ui/primitives
- https://github.com/tailwindlabs/headlessui
- https://github.com/adobe/react-spectrum
- https://github.com/chakra-ui/chakra-ui
- https://github.com/mui/material-ui
- https://github.com/carbon-design-system/carbon
- https://github.com/primer/css
