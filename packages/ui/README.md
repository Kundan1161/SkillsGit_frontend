# @skillsgit/ui

Shared design tokens and UI primitives for the marketplace and creator apps.

- Tokens live in `src/styles/tokens.css` — import once in each app's root layout.
- shadcn/ui components will be installed into `src/components/` (see `prompts/shared/design-system.md`).
- Utilities: `clsx`, `tailwind-merge`, `lucide-react`.

Consumed as source — no build step. Both apps import directly from `@skillsgit/ui/...`.
