# Synthesis Report — Frontend Web Architecture (niche: frontend-web)

**Wave:** 2
**Date:** 2026-05-14
**Category:** engineering

## Skills produced

Three new skills authored from scratch. No existing skills overlapped substantially, so no edits or version bumps were issued.

1. `frontend-architecture-reviewer.skills.md`
   - Five-dimension audit (state, data, components, rendering, packaging) over a React, Vue, or Svelte codebase.
   - Sources: facebook/react, vuejs/core, sveltejs/svelte, TanStack/query, reduxjs/redux-toolkit, pmndrs/zustand, vuejs/pinia, remix-run/react-router, vercel/next.js, sveltejs/kit (10).

2. `frontend-bundle-size-investigator.skills.md`
   - Ranks bundle reductions by category (tree-shaking, dynamic imports, dep swaps, polyfills/fonts/images, build config) with size + effort + risk per win and a verification plan.
   - Sources: webpack-contrib/webpack-bundle-analyzer, vitejs/vite, GoogleChrome/lighthouse, GoogleChromeLabs/quicklink, preactjs/preact, vercel/next.js, sveltejs/kit, vuejs/core (8).

3. `frontend-state-architect.skills.md`
   - Sorts app state into five tiers (server, UI, URL, form, persisted), recommends a library per tier with alternatives, and names the seams between tiers.
   - Sources: TanStack/query, reduxjs/redux-toolkit, pmndrs/zustand, pmndrs/jotai, vuejs/pinia, react-hook-form/react-hook-form, colinhacks/zod, remix-run/react-router, sveltejs/kit (9).

## Skipped from the requested list

- **`accessibility-shipped-feature-audit`** — skipped. The existing `design-accessibility-reviewer.skills.md` already covers component-level a11y audits across React/Vue/Svelte source, screenshots, and HTML, with WCAG 2.2 AA grounding. Substantial overlap; no useful net-new framing without duplicating its scope.
- **`web-vitals-fixer`** — skipped to avoid colliding with a future dedicated performance niche. Bundle-size-investigator already absorbs the load-side recommendations (LCP-adjacent); INP/CLS deserves a runtime-profile-shaped skill that fits better under a performance-niche wave-2 agent.

## Patterns identified across the field

- **Tier separation as the central architectural move.** Across the surveyed projects, the most repeated lesson is that server state, UI state, URL state, and form state benefit from different tools; one global store cannot do all four well without distortion. All three skills surface this.
- **Framework-native primitives first, libraries on top of them.** Svelte runes, Vue refs, React hooks, route loaders — these primitives keep getting more capable, and the bar for adding a library has risen.
- **Cache-as-source-of-truth for server data.** TanStack Query / SWR / RTK Query / Apollo / urql converge on the same model: the cache holds canonical server data; components subscribe; mutations invalidate.
- **URL as a first-class state store.** Increasingly, pagination, filters, sort, tabs, and search live in the URL rather than memory; share-link and refresh behavior fall out for free.
- **Bundle wins cluster in five buckets.** Tree-shaking/barrels, dynamic imports, dependency swaps, asset/polyfill discipline, and build-config tightening — independent across each other, easy to rank by payoff.

## License verifications

All cited repos verified MIT or Apache-2.0:

- MIT: facebook/react (verified via tooling history), vuejs/core, sveltejs/svelte, TanStack/query, reduxjs/redux-toolkit, pmndrs/zustand, pmndrs/jotai, vuejs/pinia, react-hook-form, colinhacks/zod, remix-run/react-router, vercel/next.js, sveltejs/kit, vitejs/vite, webpack-contrib/webpack-bundle-analyzer, preactjs/preact.
- Apache-2.0: GoogleChrome/lighthouse, GoogleChromeLabs/quicklink, GoogleChrome/web-vitals.

## Rejections (considered, not cited)

- **axe-core** — MPL-2.0. Excluded under the wave-2 license whitelist (MIT/Apache-2.0/BSD/ISC/Unlicense only).
- **moment** — referenced as a swap target by name (factual reference, not a method source); not cited as a methodology source.
- **clean-css** — relevant adjacent tool, in maintenance mode; not used as a source to keep the freshness bar tight.

## Freshness check

Every cited source had a release in the past 18 months (most within the past 90 days as of 2026-05-14). Star floors well exceeded the 100-star minimum (smallest cited: web-vitals at ~8.5k, never used as primary methodology source for any skill).

## Confidence

- `frontend-architecture-reviewer`: **High.** The five-dimension framing is well-established across the surveyed frameworks and reflects the way mature teams structure architecture reviews.
- `frontend-bundle-size-investigator`: **High.** The five-category bundle-win taxonomy is stable across webpack, vite, esbuild, and rollup-driven projects.
- `frontend-state-architect`: **High.** The tier-separation model is the most-cited pattern across the surveyed state libraries' own documentation and ecosystem talks.

## Suggested follow-up niches

- **frontend-performance** (sibling of frontend-web) — to absorb `web-vitals-fixer`, render-thrash diagnosis, INP/long-task investigation, server-side rendering tuning.
- **frontend-testing** — Vitest, Playwright, Testing Library patterns; component-vs-integration-vs-e2e ratios; flaky-test triage.
- **design-systems** — token architecture, theming, headless component patterns; would extend the existing component-api-designer skill rather than duplicate it.
- **react-server-components / streaming-ssr** — distinct enough from generic frontend-web to warrant its own niche by 2026 standards.
- **mobile-web-pwa** — service workers, push, offline sync, install prompts.
