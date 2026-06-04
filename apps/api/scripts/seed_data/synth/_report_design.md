# Design area — synthesis report

## Files produced

- `design-accessibility-reviewer.skills.md` — one-time $99, WCAG 2.2 AA audit skill with image_input tool.
- `design-token-system-critic.skills.md` — subscription $9/mo with support.
- `design-component-api-designer.skills.md` — subscription $11/mo with support.

## Sources per skill (license-verified)

### Accessibility Reviewer
- https://github.com/radix-ui/primitives — MIT, 18.9k stars, active
- https://github.com/tailwindlabs/headlessui — MIT, 28.6k stars, active
- https://github.com/adobe/react-spectrum — Apache-2.0, 15.1k stars, active
- https://github.com/KittyGiraudel/a11y-dialog — MIT, 2.5k stars, active
- https://github.com/chakra-ui/chakra-ui — MIT, 40.4k stars, active
- https://github.com/carbon-design-system/carbon — Apache-2.0, 9.1k stars, active
- https://github.com/primer/css — MIT, 12.9k stars, active

### Design Token System Critic
- https://github.com/style-dictionary/style-dictionary — Apache-2.0, 4.6k stars, active
- https://github.com/tokens-studio/sd-transforms — MIT, 245 stars, active
- https://github.com/primer/css — MIT, 12.9k stars
- https://github.com/carbon-design-system/carbon — Apache-2.0, 9.1k stars
- https://github.com/chakra-ui/chakra-ui — MIT, 40.4k stars
- https://github.com/adobe/react-spectrum — Apache-2.0, 15.1k stars

### Component API Designer
- https://github.com/radix-ui/primitives — MIT, 18.9k stars
- https://github.com/tailwindlabs/headlessui — MIT, 28.6k stars
- https://github.com/adobe/react-spectrum — Apache-2.0, 15.1k stars
- https://github.com/chakra-ui/chakra-ui — MIT, 40.4k stars
- https://github.com/mui/material-ui — MIT, 98.3k stars
- https://github.com/carbon-design-system/carbon — Apache-2.0, 9.1k stars
- https://github.com/primer/css — MIT, 12.9k stars

## Patterns synthesized across sources

- **Composition over configuration** for headless primitives — observed across Radix, Headless UI, React Aria. Compound parts (Root, Trigger, Content, Item) instead of monolithic props.
- **Controlled/uncontrolled symmetry** — `value` + `onChange` vs `defaultValue`, mutually exclusive at the type level. Same pattern across all surveyed libraries.
- **ARIA semantics handled internally** with passthrough escape hatches — primitives manage role and state; consumers can override labels.
- **Token layering** — primitive → semantic → component, observed in Primer, Carbon, Chakra. Flat token sets are universally treated as legacy.
- **Dark mode swaps at the semantic layer**, not the primitive. Carbon and Primer both document this rule.
- **Style Dictionary's transform pipeline** as the canonical multi-platform compilation model.
- **WCAG 2.2 AA as the modern conformance floor**, with 24px target size and visible focus indicators newly emphasized.
- **`asChild` / slot polymorphism** (Radix) vs `as` prop polymorphism (Chakra/MUI) — both surveyed; recommended `asChild` for primitives, `as` for styled wrappers.

## Rejections

- **axe-core (MPL-2.0)** — license is outside the MIT/Apache-2.0/BSD/ISC/Unlicense allowlist. Excluded as a source even though it dominates the field methodologically.
- **w3c/aria-practices** — license unclear from README scan (likely W3C document license); excluded to be safe.
- **design-tokens/community-group** — license unclear (W3C community license, not MIT/Apache); excluded.
- **openui/open-ui** — W3C Community License; excluded.
- **ardakaracizmeli/design-system-checklist** — license unspecified on the repo; excluded.
- **system-ui/theme-specification** — license unspecified and only 551 stars; borderline.
- **vrk-kpa/suomifi-design-tokens** — likely MIT but well under 100 stars on its own, and a narrow national-brand example; not central enough.

## Confidence

**High** on methodology — the patterns synthesized here are well-attested across at least four MIT/Apache surveyed libraries each, and the WCAG 2.2 references map to a stable public spec. The Accessibility Reviewer and Component API Designer skills draw on the most heavily-trafficked design-system repos on GitHub, so the synthesized practice reflects current mainstream consensus. The Token System Critic skill is on slightly thinner methodological ground because the most authoritative spec source (DTCG) had to be omitted on license grounds — but Style Dictionary and the surveyed component libraries supply enough overlapping practice to ground the audit checklist.

**Medium** on pricing calibration — the $9 and $11 subscriptions reflect the brief's guidance band but have not been market-validated.

**High** on originality — all prose is freshly authored; no copying or paraphrase from any source's documentation or README. Trademarks not used in body text; only as URLs in `## Sources reviewed`.
