---
id: skillsgit-curated/bundle-size-investigator
version: 1.0.0
name: Bundle Size Investigator
description: Given a bundle report, dependency list, or app description, find the biggest size wins — tree-shaking, dynamic imports, dependency swaps, polyfills, fonts, and images — ranked by payoff and effort.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:frontend-web, bundle-size, performance, tree-shaking, code-splitting, webpack, vite, rollup]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  min_context_tokens: 24000
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - bundle size analysis
  - shrink bundle
  - tree shaking
  - reduce javascript
  - code splitting opportunities
  - replace heavy dependency
  - dependency swap
  - polyfill audit
  - font optimization
  - webpack analyzer
  - vite bundle report
  - rollup bundle
example_invocations:
  - "Here's our webpack-bundle-analyzer JSON — find the top size wins."
  - "Our main bundle is 480 kB gzipped, here's the package.json and route list. Where do I cut?"
  - "Why is moment.js shipping when we only format three dates? Suggest replacements."
  - "Rank the biggest bundle reductions we can do this sprint."
inputs:
  - name: report
    type: text
    required: false
    description: A bundle analyzer report (webpack-bundle-analyzer JSON, esbuild metafile, vite stats), or a copy-pasted text view of the top chunks and their contents.
  - name: dependencies
    type: text
    required: false
    description: The `dependencies` block of package.json, or the output of `npm ls --prod --depth=0`. Either alone gives partial signal; the report plus this is ideal.
  - name: app_description
    type: text
    required: false
    description: A few sentences describing what the app does, which routes are hot, and what users do on those routes. Sharpens prioritization.
  - name: build_config
    type: text
    required: false
    description: Relevant snippets of webpack, vite, rollup, or esbuild config — especially externalization, target, and chunk-splitting settings.
  - name: targets
    type: text
    required: false
    description: Browser support targets (browserslist string or prose). Determines whether polyfills are removable.
outputs:
  - name: investigation
    type: markdown
    description: Ranked list of bundle reductions with size estimate, effort estimate, risk, and step-by-step move.
  - name: wins_json
    type: json
    description: Machine-readable wins (category, target, estimated savings in kB gzipped, effort hours, risk).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Bundle Size Investigator

## When to use

Use this skill when a frontend team has a measurable bundle problem (slow first paint, lighthouse warnings about unused JavaScript, slow TTI on mobile, an oversize budget alert in CI) and wants to know which cuts will move the number the most for the least effort. Common triggers:

- A new lighthouse run flags hundreds of kilobytes of unused JavaScript.
- The marketing team wants a landing page under a specific size budget for a campaign.
- The bundle has grown ten or twenty percent over a quarter and nobody can point to why.
- A user complains about a slow first load on a mid-range mobile device and the network panel shows JavaScript blocking paint.
- A migration to a new framework, build tool, or runtime is on the table, and the team wants a "before" reading to make the "after" credible.

The skill is **not** a runtime performance audit (use a web-vitals or render-thrashing skill for that). It is not a refactor pass. It cares only about the bytes that ship to the user's browser and the load-time effects of those bytes.

The skill prefers measurement-backed wins over speculative ones. Every recommendation is paired with a way to verify the change after the fact.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `report` | no | The richest signal. A bundle analyzer report names the actual heavy modules and lets the agent rank by real numbers. |
| `dependencies` | no | Lets the agent flag heavy or duplicated dependencies even without a report. |
| `app_description` | no | Steers priorities — a landing page and a dashboard need different bundle strategies. |
| `build_config` | no | Reveals whether tree-shaking, scope-hoisting, or modern targets are already on. |
| `targets` | no | A modern browserslist unlocks aggressive cuts (polyfill removal, native ES modules, modern syntax). |

At least one of `report`, `dependencies`, or `app_description` must be provided. With only `app_description`, findings are guidance rather than measured wins.

## Outputs

- A markdown investigation organized by win category and ranked by estimated savings.
- A JSON wins list suitable for tracker import.
- A short "verification plan" at the end describing what to re-measure after each change.

## How to apply

### Stage 1 — Read the signal

Before naming any win, the agent reconstructs what is actually in the bundle.

1. If a report is present, list the top ten heaviest modules in the largest chunk by gzipped size. Note duplicates (same module name in multiple chunks), barrel files that pull in entire libraries, and any module larger than approximately 30 kB gzipped.
2. Identify the chunk graph: which chunks share which modules, which chunks load on initial paint, and which chunks load on demand. Flag any large chunk that loads on initial paint but is only used after a click.
3. From the dependency list, mark known heavy or commonly-replaced packages: `moment`, `lodash` (as a default import), `core-js` (in modern builds), full icon libraries imported as one default, `rxjs` if only a few operators are used, `date-fns` imported via barrel, full charting libraries when one chart type is in use, full PDF libraries, full markdown libraries when only inline formatting is needed, full validation libraries duplicated across the codebase.
4. From the build config, note: tree-shaking enabled, `sideEffects` declared, modern syntax targets, browserslist scope, externalization of any dependencies, asset modules, image and font loaders, chunk-splitting strategy.
5. From the app description, identify the **hot** routes (first page users hit) and the **cold** routes (admin, settings, rare flows). Initial bundle wins target hot routes; chunk-splitting wins target cold routes.

The stage 1 output is internal scaffolding for the wins; do not surface it as a section. Cite it only when a finding needs to explain why a number is what it is.

### Stage 2 — Categorize the wins

The agent walks five categories and lists wins per category. Each win includes: target (the module, asset, or config knob), estimated savings (in kB gzipped, with explicit hedging when the report is absent), effort (small, medium, large), risk (low, medium, high), and the move itself.

#### Category 1 — Tree-shaking and barrels

The cheapest wins are usually here: code that already exists in a form the bundler can drop, blocked by a barrel file or a default import.

Look for and propose:

- **Default-imported utility libraries**: `import _ from 'lodash'` swapped for `import debounce from 'lodash/debounce'` or for a smaller alternative (`lodash-es` with named imports, or hand-written single functions for one-call-site uses).
- **Date library swaps**: `moment` replaced by `date-fns`, `dayjs`, or native `Intl.DateTimeFormat` when only formatting and parsing are needed. Quantify by the number of `moment` call sites and whether timezone math is actually in use.
- **Icon set barrels**: full icon packages replaced by per-icon imports, an SVG sprite, or inline SVG. Quantify by the number of icons actually used versus shipped.
- **Internal barrel files**: `import { Button } from '~/components'` where `components/index.ts` re-exports two hundred symbols. Propose deep imports or marking the package `"sideEffects": false`.
- **Mis-resolved CommonJS**: a library that ships an ESM build but the bundler resolves the CJS build because of the `main` field. Propose pinning `module`/`exports` fields or upgrading the bundler config.
- **Polyfill leakage**: `core-js` pulled in by Babel preset-env with an outdated browserslist. Tighten targets and re-measure.

Tree-shaking wins are usually small effort and low risk, and they compound. Place them at the top of the backlog when present.

#### Category 2 — Dynamic imports and route splitting

The next-cheapest wins shift code to where users actually need it.

Look for and propose:

- **Route-level splitting**: every page in its own chunk, loaded by the router on navigation rather than on first paint.
- **Below-the-fold splitting**: heavy modal contents, accordion bodies, complex tables, code editors, charts, and rich-text editors loaded only when the user opens or scrolls to them.
- **Conditional features**: admin-only, beta-only, or feature-flag-gated code excluded from the main chunk and loaded behind the flag check.
- **Vendor splitting**: large dependencies used only on one route (a PDF renderer, a 3D library, a markdown editor) split out so the other routes do not carry them.
- **Worker offload**: CPU-heavy code (sync parsers, large schema validators, image processors) moved to a web worker so the main thread chunk shrinks. Note that worker offload changes the threading model and is medium risk.
- **Idle-time prefetch**: dynamic chunks the agent recommends splitting can be prefetched on idle to keep the navigation feeling fast. Mention this as a paired action so the team does not regress perceived speed when reducing initial size.

Dynamic-import wins usually require code changes (an `import()` call, an Suspense or `defineAsyncComponent` boundary, an error fallback). Mark the risk medium because boundaries change error semantics.

#### Category 3 — Dependency swaps

When a single dependency dominates a chunk, the question becomes: is the dependency justified by what it does, or could a smaller alternative work?

Look for and propose:

- **Heavy-for-purpose libraries**: a multi-megabyte charting library used for one bar chart, swapped for a smaller chart library or a hand-rolled SVG.
- **Markdown library** rendering a small set of inline formats, swapped for a regex-based formatter or a smaller parser.
- **Full UI kit** when the design system only uses a handful of components, swapped for either deep imports or a tree-shakeable headless library.
- **PDF rendering** on the client when the same task could be done at build time or on the server.
- **Schema validation libraries** duplicated (a runtime validator and a TypeScript-only type guard library) when one of them could do both jobs.
- **Animation libraries** when the animations in use are all CSS-expressible, swapped for transitions and keyframes.

Dependency swaps are higher effort and higher risk than tree-shaking. Always list at least one specific module the swap would touch, and call out which behaviors of the original library the alternative does not cover. If unsure, recommend a spike (an isolated prototype) before a full swap.

#### Category 4 — Polyfills, fonts, and images

JavaScript is often only part of the load. The agent should not stop at JS.

Look for and propose:

- **Polyfills shipped to modern browsers**: serve a modern bundle to evergreen targets and a legacy bundle to old ones, or stop supporting legacy targets if the analytics show no traffic from them.
- **Custom font weights**: a webfont family loaded with eight weights when two are used; or loaded synchronously (blocking text render) when `font-display: swap` would be fine. Subset fonts to the characters in use.
- **Icon fonts**: replace with inline SVG or an SVG sprite — icon fonts are heavy, hurt accessibility, and can shift layout.
- **Hero images**: serve responsive sizes, use modern formats (AVIF, WebP), lazy-load anything below the fold, and avoid loading retina assets to non-retina viewports.
- **Third-party scripts on the critical path**: analytics, chat widgets, ad scripts, A/B testing libraries — defer, lazy-load, or move server-side. Quantify by the script's transferred bytes and main-thread blocking time.
- **Source maps shipped to production**: source maps generated and served alongside the bundle when they should only be uploaded to the error tracker. Quantify by total source-map bytes.

These wins often have the biggest impact on perceived load even when their raw byte savings are smaller than JS wins, because they sit on the critical render path.

#### Category 5 — Build configuration

The last category looks at the build itself.

Look for and propose:

- **Tree-shaking off**: confirm production mode is enabled and `sideEffects: false` is set where safe.
- **Mismatched targets**: `browserslist` set wider than the analytics support, forcing Babel to transpile features that ship natively in modern browsers.
- **CSS shipping all variants**: CSS-in-JS or a utility framework producing a stylesheet with rules no component uses. Enable purging or critical-CSS extraction.
- **Source maps in client bundle**: ensure source maps are emitted but not referenced from production HTML.
- **No long-term caching split**: vendor chunks not separated from app code, forcing users to re-download the whole vendor blob on every release.
- **Compression**: confirm gzip and brotli are enabled at the edge; serve brotli to clients that accept it.
- **HTTP/2 push or preload misuse**: preloading the wrong chunks, or hinting too many resources at once.

Build config wins are usually low effort and low risk but require a CI run to verify.

### Stage 3 — Rank and write

After all five categories are scanned, combine into one investigation.

1. Open with the headline: total estimated savings in kB gzipped, expressed as a range when measurements are partial. Name the single biggest win in the first sentence.
2. List wins by category. For each: target, savings estimate, effort, risk, and the exact move. When the report is missing, prefix the savings estimate with "approximately" and explain the basis.
3. Order the backlog by payoff over effort, not by category. Quick wins (small effort, low risk, measurable savings) at the top.
4. End with a verification plan: the exact metric to re-measure (initial transfer size, gzipped main chunk size, Lighthouse "unused JavaScript" total, LCP on a slow-network profile) and the order in which to make changes so each delta is attributable.

## Calibration heuristics

- Quote sizes in kilobytes gzipped, not raw. Decisions are made against transfer bytes.
- Do not propose a swap of a 4 kB library for a 3 kB library unless that swap also unblocks other wins.
- When the report shows a single module above approximately 100 kB gzipped, that module is almost always the headline win; spend disproportionate attention on it.
- Treat any third-party script on the critical path as a high-severity finding regardless of byte size, because its main-thread cost is often larger than its transfer cost.
- For monorepos with multiple deployable apps, scope the investigation to one app at a time; cross-app refactors are out of scope for a single pass.
- If the team's runtime cost is small but their build time is huge, note that observation but do not extend the investigation into build performance — that is a different skill.

## Examples

### Example 1 — A consumer site with a 600 kB main chunk

Input: webpack-bundle-analyzer JSON, package.json dependencies, browserslist set to `> 0.5%, not dead`.

Selected output excerpt:

> **Headline**
> Approximately 240 kB gzipped of removable weight, two-thirds of it in three modules. The single biggest win is splitting the rich-text editor off the home route (≈ 95 kB gz).
>
> **Tree-shaking and barrels (≈ 35 kB)**
> - `lodash` default import in `utils/format.ts`. Replace with three deep imports. Small effort, low risk.
> - Internal `components/index.ts` barrel re-exports 180 symbols. Mark the package `sideEffects: false` and verify the barrel paths.
>
> **Dynamic imports (≈ 130 kB)**
> - The rich-text editor (`tiptap` + extensions) loads at home. Move behind the comment composer; lazy-mount on focus.
> - The PDF preview modal pulls `pdfjs-dist` into the main chunk. Lazy-load the modal contents.

### Example 2 — App description only, no report

Input: a paragraph describing an internal admin tool used on desktop Chrome, no report.

Selected output excerpt:

> **Caveat**
> Without a bundle report, savings below are directional. Run `webpack-bundle-analyzer` (or `rollup-plugin-visualizer` or `vite-bundle-visualizer`) and re-invoke this skill for measured numbers.
>
> **Likely wins**
> - With only desktop Chrome to support, drop `core-js` and tighten `browserslist` to last two Chrome versions. Likely 30–80 kB gzipped depending on the current preset-env footprint.
> - Replace `moment` with `Intl.DateTimeFormat` or `date-fns`. Quantify by the number of formats in use.

## Limitations

- Without a bundle report, all numbers are estimates; the skill should hedge every figure.
- Many modern bundlers (vite, esbuild, rspack) report sizes differently and tree-shake differently; the agent should not cite specific bytes that depend on which tool ran.
- The skill does not measure runtime CPU cost. A module that is small to download but expensive to execute (large parser, big regex engine) needs a runtime-profile follow-up.
- The skill cannot judge whether a dependency is essential to the product's brand or UX (a specific charting library may be a non-negotiable design choice). Propose alternatives but note when a swap should be a design conversation, not an engineering call.
- For multi-tenant or per-customer builds, byte savings on one tenant may not generalize; ask for the most-loaded tenant's build.

## Sources reviewed

The methodology was synthesized from study of the following public, permissively licensed tools and frameworks that shape modern frontend bundles. No content from any source was reproduced.

- https://github.com/webpack-contrib/webpack-bundle-analyzer
- https://github.com/vitejs/vite
- https://github.com/GoogleChrome/lighthouse
- https://github.com/GoogleChromeLabs/quicklink
- https://github.com/preactjs/preact
- https://github.com/vercel/next.js
- https://github.com/sveltejs/kit
- https://github.com/vuejs/core
