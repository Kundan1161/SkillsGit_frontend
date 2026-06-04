# @skillsgit/web-marketplace

Buyer-facing storefront **and** creator dashboard for the Skills Marketplace,
backed by `apps/api`. Light mode default, port `3000`.

## Quickstart

From the repo root:

```bash
pnpm install
pnpm dev          # runs api, marketplace, and creator concurrently
```

Or just this app:

```bash
pnpm --filter @skillsgit/web-marketplace dev
```

Visit:

- <http://localhost:3000> — home
- <http://localhost:3000/_design> — kitchen sink of every Phase 0 component
- <http://localhost:3000/browse> — browse stub
- <http://localhost:3000/dashboard> — creator dashboard stub

## Scripts

| Script            | What it does                            |
| ----------------- | --------------------------------------- |
| `pnpm dev`        | `next dev -p 3000`                      |
| `pnpm build`      | Production build                        |
| `pnpm start`      | Production server                       |
| `pnpm lint`       | `next lint`                             |
| `pnpm typecheck`  | `tsc --noEmit` (strict)                 |

## Layout

```
app/                     App Router routes (RSC by default)
  _design/               Kitchen sink for visual regression
  (route stubs)          Browse, skill detail, dashboard, admin, settings, auth
components/
  ui/                    shadcn/ui primitives (Phase 0 set)
  discovery/             Marketplace home/browse/search (see prompt 01)
  skill/                 Skill detail (see prompt 02)
  reviews/               Reviews + moderation (see prompt 05)
  creator/               Creator dashboard (see prompt 07)
  site-header.tsx        Sticky top nav
  site-footer.tsx
  theme-toggle.tsx
  placeholder.tsx        "Coming soon" stub used by route stubs
lib/
  utils.ts               `cn()` helper (clsx + tailwind-merge)
  api.ts                 Placeholder fetch wrapper — replaced by @skillsgit/api-client after `pnpm codegen`
  query-client.tsx       TanStack QueryClientProvider
  theme.tsx              next-themes provider
```

## Design system

All visual primitives follow `prompts/shared/design-system.md`. Tokens live
in `packages/ui/src/styles/tokens.css` and are imported once in
`app/layout.tsx`. Tailwind classes use semantic names (`bg-bg`,
`text-fg-muted`, `text-brand-500`) — never raw hex.

## Conventions

- **Server Components by default.** Add `"use client"` only when state,
  effects, refs, or event handlers are required.
- **No `fetch` in components.** Use TanStack Query hooks (client) or async
  functions (server). The `lib/api.ts` wrapper is a placeholder until the
  generated client lands.
- **Strict TypeScript.** No `any`. No implicit indexed access (`noUncheckedIndexedAccess`).
- **Forms** use React Hook Form + Zod. See `components/ui/form.tsx`.

## Quality targets

- Lighthouse accessibility ≥ 95 on `/` and `/_design`.
- Lighthouse performance ≥ 90 on `/` on a cold load.
- No layout shift on theme toggle.

## Spec entry point

Start at `prompts/marketplace/00-overview.md`, then drill into the per-feature
prompts referenced from each route stub.
