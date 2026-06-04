---
id: skillsgit-curated/frontend-state-architect
version: 1.0.0
name: Frontend State Architect
description: Recommend a state architecture for a new or evolving frontend app — separating server state, UI state, URL state, and form state — with concrete library picks and integration patterns.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:frontend-web, state-management, tanstack-query, zustand, redux, react-hook-form, url-state, architecture]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  min_context_tokens: 16000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - state architecture
  - state management plan
  - server state vs ui state
  - url state
  - form state library
  - pick a state library
  - tanstack query
  - zustand
  - redux toolkit
  - pinia
  - jotai
  - react hook form
example_invocations:
  - "Plan the state architecture for a B2B dashboard with heavy filtering."
  - "Should we use Redux, Zustand, or TanStack Query for this app?"
  - "Design how form state, server state, and URL state should split in this checkout flow."
  - "We're migrating from a single Redux store to something better — what does the target look like?"
inputs:
  - name: app_description
    type: text
    required: true
    description: Description of the app — domain, key flows, expected scale, team size, and any constraints (e.g. SSR required, mobile-first, offline support).
  - name: framework
    type: choice
    required: false
    description: Primary framework. Affects idiomatic recommendations.
    choices: [react, next, remix, vue, nuxt, svelte, sveltekit, solid, mixed]
  - name: existing_stack
    type: text
    required: false
    description: What is currently in use (libraries, patterns, pain points). If this is a greenfield app, say so.
  - name: constraints
    type: text
    required: false
    description: Hard requirements — no new dependencies, must work without JS, must persist offline, must server-render, must integrate with a specific backend client. Sharpens the recommendation.
outputs:
  - name: architecture
    type: markdown
    description: Recommended state architecture with reasoning, library choices, integration patterns, and migration notes if applicable.
  - name: decisions_json
    type: json
    description: Machine-readable decisions (state tier, chosen library, alternatives considered, reasoning).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Frontend State Architect

## When to use

Use this skill when a team is about to commit to a state architecture and wants a defensible plan. Common triggers:

- Greenfield: a new app is starting, and the team wants to avoid the common trap of reaching for one global store and pushing everything through it.
- Mid-life migration: the app started small with `useState` everywhere, grew, and is now hard to reason about; the team wants a target architecture and a path to it.
- Library re-evaluation: the team is considering replacing Redux with Zustand, swapping Vuex for Pinia, or adopting TanStack Query for the first time, and wants the trade-offs spelled out.
- Painful flow: one feature (a multi-step form, a heavily-filtered list, a chat thread, a wizard) keeps generating bugs, and the team suspects the state shape is the cause.

The skill is **not** a tutorial. It does not walk through how to wire up a particular library; it decides which libraries belong where, names the seams between them, and explains the integration points.

The skill is calibrated to recommend less rather than more. A second state library only earns its place when the first cannot do that job without distortion.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `app_description` | yes | The core signal. Domain, flows, scale, and team size shape the recommendation. |
| `framework` | no | Steers to idiomatic choices (Pinia for Vue, Svelte stores or runes for Svelte, TanStack Query for React). |
| `existing_stack` | no | Frames the recommendation as "from here to there" instead of "from nothing." |
| `constraints` | no | Hard limits that eliminate otherwise-reasonable choices. |

## Outputs

- A markdown plan structured by state tier: server, UI, URL, form, and (if relevant) persisted.
- A JSON decision list naming each tier, its chosen library, the alternatives considered, and why.
- A short migration section when the input suggests an existing app.

## How to apply

### Stage 1 — Sort state into tiers

Before any library names appear, the agent sorts the app's state into tiers. Mixing tiers is the single most common cause of frontend state pain; sorting them is the most important step.

The five tiers:

1. **Server state**. Data that lives on a backend, can go stale, and benefits from caching. Examples: a user's profile fetched from an API, a list of orders, a search result, a real-time feed. The defining property: the canonical copy is on the server, not in the client.
2. **UI state**. Ephemeral, in-memory state about how the interface is presented. Examples: which modal is open, which tab is active, hover and focus, drag-in-progress positions, optimistic UI mid-flight. The defining property: refreshing the page can lose this and the user does not mind.
3. **URL state**. State the URL is the source of truth for, so a refresh, link share, or back-button press restores it. Examples: current page in pagination, search query, active filter selections, sort order, the route itself. The defining property: a user pasting the URL elsewhere should land on the same view.
4. **Form state**. Inputs the user is editing, with validation, dirty tracking, field-level errors, and submission state. Examples: a profile editor, a checkout form, a multi-step wizard. The defining property: there is a moment of commitment (submit) after which the state moves elsewhere (server, URL, or away).
5. **Persisted state**. Client-side state the app wants to survive reload. Examples: a logged-in token, a draft message, a user preference like theme. The defining property: lives in localStorage, IndexedDB, or a cookie.

For each tier the agent identifies which slices of the app's state belong there, based on the `app_description`. A slice that belongs in two tiers is a smell — surface it explicitly. Common mismatches:

- Pagination kept in `useState` instead of the URL. Refresh loses the page.
- Search query kept in a global store instead of the URL. Link-sharing is broken.
- Server records duplicated into a Redux slice. Cache invalidation now lives in two places.
- Modal open/closed state hoisted to a global store. No one else reads it.
- Auth token in memory only. Reload logs the user out.
- Form draft in component state. Navigate away and the draft is lost.

If the input describes any of these directly, address them in the recommendation. If the input is vague, ask the user implicitly through the recommendation itself: state the assumption you made and the consequence if it is wrong.

### Stage 2 — Pick a library per tier

The agent now names a library or pattern per tier. Each pick is justified by what the tier needs — not by what is fashionable.

#### Server state

The server-state tier is where the biggest gains live. A dedicated server-state library handles caching, deduping in-flight requests, background revalidation, optimistic updates, and stale-while-revalidate behavior — features that hand-rolled fetches almost always implement worse.

Default recommendation: **TanStack Query** in React (or its Vue, Svelte, and Solid variants), or the framework-native equivalent if the framework provides one (Nuxt's `useFetch`, Remix or React Router's route loaders, SvelteKit's `load` functions).

Alternatives the agent should consider:

- **SWR** — lighter and simpler than TanStack Query; suits a marketing site or a small app where the full feature set is overkill.
- **RTK Query** — natural choice when Redux Toolkit is already the chosen client-state library and the team prefers one ecosystem.
- **Apollo Client or urql** — for GraphQL backends, where the schema knowledge unlocks features (fragment colocation, normalized caching) that REST equivalents do not have.
- **Route loaders** — when the framework provides loaders (Remix, SvelteKit, Nuxt, modern Next.js with server components), prefer them for initial page data and reserve the query library for client-initiated reads.

Recommend exactly one server-state mechanism per app. Mixing two (Apollo and TanStack Query, RTK Query and SWR) creates a cache-coordination problem and is almost always wrong outside of incremental migrations.

#### UI state

UI state belongs as close to the using component as possible. The first reach is framework-native primitives: `useState`, `useReducer`, Vue `ref` and `reactive`, Svelte runes or `$state`, Solid signals.

A global UI-state library earns its place only when a piece of UI state has multiple, distant readers — typically:

- A theme toggle that affects every component.
- A global notification or toast tray.
- A sidebar collapse state shared across pages.
- A command-palette open/closed state.

Default recommendation when a global tier is needed: **Zustand** for React, **Pinia** for Vue, **Svelte stores or runes** for Svelte, **Solid stores** for Solid. These are intentionally minimal and avoid the boilerplate that pushed teams away from earlier global stores.

Alternatives the agent should consider:

- **Redux Toolkit** — when the app already uses Redux and the team is comfortable with the pattern, or when time-travel debugging and middleware are valuable (large enterprise apps, complex undo systems).
- **Jotai or Recoil-style atoms** — when state is naturally fragmented into many small pieces with derived computations and a coarse global store would be awkward.
- **Context** — for values that change rarely (theme, user identity, locale). Context is not a state management library; treat it as a dependency injection mechanism.

A common pitfall: using context for frequently-changing values. This forces re-renders across the consumer tree on every change. Flag and replace with a store.

#### URL state

URL state is owned by the router. The recommendation is therefore a pattern rather than a library: **read and write the URL through the router's primitives**, not through a parallel store.

- React: `useSearchParams`, route loaders' params, or a small adapter on top.
- Vue: `useRoute` and `useRouter`.
- Svelte: `$page.url.searchParams` and `goto`.

For complex filter sets, a thin helper around the router (an adapter that serializes typed filter objects to and from search params) is appropriate. Do not introduce a separate state library to hold filters; the URL is the store.

When SSR is in play, URL state has a special property: it is available on the server before any client store hydrates. Place anything the first render depends on in URL state when possible.

#### Form state

Forms are a domain of their own. Field-level dirty tracking, validation, async validation, and submission state interact in ways that ad-hoc `useState` chains handle poorly.

Default recommendation for React: **React Hook Form** for most forms; **TanStack Form** for forms with complex cross-field dependencies. Pair with a schema validator (typically **Zod** or **Valibot**) used by both client and server to keep validation rules consistent.

For Vue, **VeeValidate** with the same Zod schema works well; Vue 3.5's reactive form patterns plus `useForm` from a small wrapper is a reasonable simpler choice for small forms.

For Svelte, native form actions plus a thin validation helper are often sufficient; reach for a form library only when fields are dynamic.

A pitfall to flag: re-rendering the entire form on every keystroke because the form state lives in a top-level reactive object. Both React Hook Form and the equivalents subscribe at the field level to avoid this; if the existing stack does not, that is a finding.

Pair form state with the server tier explicitly: on submit, the form library calls a mutation from the server-state library, which handles optimism, retries, and cache invalidation. The handoff between tiers is where many bugs hide; describe it explicitly in the architecture.

#### Persisted state

Persisted state is small in scope but easy to get wrong. The recommendation is a pattern:

- **Auth tokens**: in an `HttpOnly` cookie when possible; never in localStorage if a XSS risk is plausible. Match the backend's session model.
- **Preferences** (theme, locale, density): localStorage with a versioned key and a defensive read (try/catch around parse, fall back to default).
- **Drafts** (unsent messages, in-progress forms): IndexedDB when the data is non-trivial or larger than approximately 5 MB; localStorage otherwise.
- **Cached server data for offline**: the server-state library's persister plugin if the team needs offline reads; do not roll a parallel cache.

The agent should note that persisted state across releases needs a migration path. A schema-version number stored alongside the data, and a one-shot migration function on load, prevents the "user upgrades the app and their saved data crashes the new version" failure mode.

### Stage 3 — Describe the seams

The architecture document is not just a list of libraries. The most valuable part is naming the seams between tiers so the team agrees on how data flows.

The recommendation should explicitly describe:

1. **Where server data enters the app.** A small fetcher module (or the framework's loader). Components do not call `fetch` directly.
2. **How UI state references server data.** UI state holds ids or query keys, not records. The server-state library is queried for the records.
3. **How URL state references server data.** The URL holds inputs (filters, page, sort), not outputs. The server-state library translates URL inputs into query parameters and produces results.
4. **How form state hands off to server state.** Submit calls a mutation; the mutation invalidates relevant caches; the UI re-reads through the server-state library.
5. **How errors propagate.** Server-state errors surface through the library's hooks; UI state should not have to mirror error fields by hand.
6. **How loading propagates.** Use the library's loading flags directly; do not duplicate them in UI state.

These rules are short but eliminate most of the everyday confusion. Place them prominently in the document.

### Stage 4 — Write the plan

Compile the recommendation into a single markdown document.

1. Open with a one-paragraph summary: the chosen architecture in a sentence, the headline trade-off, and the biggest payoff. If migrating, name the largest single mismatch in the existing stack.
2. List the five tiers in order. For each tier: the slices of state that belong there, the recommended library or pattern, the alternatives considered, and one or two pitfalls to avoid.
3. Add a "Seams" section enumerating the six handoffs above, tailored to the chosen libraries.
4. If an existing stack was described, end with a "Migration path" section. Order moves by independence (least-dependent first), and group them into phases the team can ship without halting feature work.
5. If hard constraints were given, end with a "Constraint check" mini-section confirming each constraint is satisfied (or stating which one is not and why).

## Calibration heuristics

- Default to fewer libraries. A new library has a long tail of cost: bundle size, type churn, hire-training cost, debugging unfamiliarity.
- A single state library cannot cover all five tiers well. If the existing stack uses one library for everything, the recommendation will almost always be "split into tiers."
- For SSR-first frameworks (Next, Remix, Nuxt, SvelteKit), prefer the framework's loaders for initial reads and reserve a query library for post-mount fetches. This avoids double-fetching.
- For small apps with one or two routes, do not recommend a server-state library; native fetch in a loader is fine. Recommend the library when there are three or more routes or when the app does any client-initiated revalidation.
- For real-time features (chat, presence, collaborative cursors), call out that the server-state library handles request-response well but real-time benefits from a dedicated subscription mechanism (WebSocket client, a sync engine, or the library's streamed-update support). Pair the two; do not pick only one.
- When the framework provides primitives for a tier (Svelte runes, Solid signals, modern Vue), prefer them over imported libraries for in-component state. Imported libraries earn their place only across components.

## Examples

### Example 1 — Greenfield B2B dashboard

Input: "New SaaS dashboard. ~30 routes, heavy filtering and sorting on most tables, multi-tenant, no offline. React. Team of six."

Selected output excerpt:

> **Summary**
> Use route loaders (or TanStack Query) for server state, the URL for filter and sort state, Zustand for the global UI state (sidebar, command palette, theme), React Hook Form with Zod for forms, and an HttpOnly cookie for auth. Do not introduce a Redux store.
>
> **Server**: TanStack Query. Alternatives: SWR (rejected — needs paginated and infinite features), RTK Query (rejected — pulls Redux for one job).
>
> **UI**: Zustand for the three pieces of true global UI state. Everything else stays in component state.
>
> **URL**: Pagination, filter selections, sort, and active tab in the search params. Use a small typed adapter so each route declares its filter schema with Zod and reads back typed values.

### Example 2 — Mid-life Vue migration

Input: "Vue 2 + Vuex app, growing painful. ~80 components, lots of API calls duplicated across pages. Migrating to Vue 3 over the year."

Selected output excerpt:

> **Summary**
> Migrate Vuex to Pinia in the first phase. In the second, lift all fetched data out of Pinia stores and into Vue Query. By the end, Pinia holds only the global UI state and persisted preferences; data lives in the query cache.
>
> **Migration path**
> Phase 1: replace Vuex modules with Pinia stores one feature at a time. No behavior changes.
> Phase 2: introduce Vue Query. For each Pinia store, identify the fetched data; move it into queries; keep mutations as mutation hooks.
> Phase 3: hoist filter and pagination state into route query params. Delete the corresponding Pinia state.

## Limitations

- The skill cannot evaluate the team's familiarity with each library; a technically-best pick that the team hates is the wrong pick. The recommendation should note the learning curve when it is significant.
- For very large apps (hundreds of routes, dozens of teams), a single document cannot capture every nuance. The recommendation should propose patterns and example slices, then defer to per-domain decisions.
- The skill assumes a single-page or hybrid app. For multi-page server-rendered apps with little client state, the answer is often "you do not need most of these libraries."
- The skill picks libraries known to be active. If a library named here becomes unmaintained, the recommendation should be reread; freshness of the underlying ecosystem cannot be guaranteed by a static document.

## Sources reviewed

Synthesized from study of the following public, permissively licensed projects. None of their code or documentation was reproduced.

- https://github.com/TanStack/query
- https://github.com/reduxjs/redux-toolkit
- https://github.com/pmndrs/zustand
- https://github.com/pmndrs/jotai
- https://github.com/vuejs/pinia
- https://github.com/react-hook-form/react-hook-form
- https://github.com/colinhacks/zod
- https://github.com/remix-run/react-router
- https://github.com/sveltejs/kit
