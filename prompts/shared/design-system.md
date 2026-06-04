# shared — Design System

**Phase:** 0 (foundation)
**Depends on:** `01-tech-stack-and-repo.md`
**Parallel-safe with:** other shared/* prompts
**Status:** ready

> The marketplace and creator apps share a visual language and component library. Diverging on primitives is technical debt; diverging on themes is fine.

---

## Stack

- **Tailwind CSS v4** with CSS variables for theming.
- **shadcn/ui** as the primitive library — install components into `packages/ui/src/components/` once, both apps consume from there.
- **Icons:** lucide-react.
- **Fonts:** Inter for UI (variable weight 100–900), JetBrains Mono for code blocks.
- **Themes:** light + dark. System-aware default with persisted user override.

---

## Tokens

Define in `packages/ui/src/styles/tokens.css`. Both apps `@import` this file in their root layout.

```css
@layer base {
  :root {
    /* Brand */
    --color-brand-50:  #f5f0ff;
    --color-brand-500: #6d28d9;     /* primary purple — "skills" identity */
    --color-brand-600: #5b21b6;
    --color-brand-900: #2e1065;

    /* Surfaces */
    --color-bg:        #ffffff;
    --color-bg-muted:  #f8fafc;
    --color-bg-raised: #ffffff;
    --color-border:    #e2e8f0;

    /* Text */
    --color-fg:        #0f172a;
    --color-fg-muted:  #475569;
    --color-fg-subtle: #94a3b8;

    /* Semantic */
    --color-success:   #16a34a;
    --color-warning:   #d97706;
    --color-danger:    #dc2626;
    --color-info:      #0284c7;

    /* Marketplace-specific */
    --color-price:     #15803d;     /* listing prices */
    --color-rating:    #facc15;     /* star fill */

    /* Radius */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;

    /* Shadows */
    --shadow-sm: 0 1px 2px rgb(15 23 42 / 0.06);
    --shadow-md: 0 4px 12px rgb(15 23 42 / 0.08);
    --shadow-lg: 0 12px 32px rgb(15 23 42 / 0.12);

    /* Type scale (Tailwind defaults are fine; only call out overrides) */
    --font-display: "Inter", system-ui, sans-serif;
    --font-mono:    "JetBrains Mono", ui-monospace, monospace;
  }

  .dark {
    --color-bg:        #0f172a;
    --color-bg-muted:  #1e293b;
    --color-bg-raised: #1e293b;
    --color-border:    #334155;

    --color-fg:        #f8fafc;
    --color-fg-muted:  #cbd5e1;
    --color-fg-subtle: #64748b;

    --color-brand-500: #8b5cf6;
    --color-brand-600: #7c3aed;

    --color-price:     #4ade80;
  }
}
```

Map these to Tailwind in `tailwind.config.ts` via `theme.extend.colors`. Components use semantic Tailwind classes (`bg-bg`, `text-fg-muted`) — never raw hex.

---

## Components (Phase 0 set)

Install via shadcn into `packages/ui/src/components/`:

- `Button` — variants: `primary`, `secondary`, `ghost`, `outline`, `destructive`, `link`. Sizes: `sm`, `md`, `lg`, `icon`.
- `Input`, `Textarea`, `Select`, `Combobox`, `Checkbox`, `RadioGroup`, `Switch`, `Slider`.
- `Form` (RHF integration), `Label`, `FormError`.
- `Card`, `CardHeader`, `CardContent`, `CardFooter`.
- `Dialog`, `Sheet`, `Popover`, `Tooltip`, `DropdownMenu`, `ContextMenu`.
- `Tabs`, `Accordion`, `Collapsible`, `Separator`.
- `Toast` (sonner).
- `Badge`, `Avatar`, `Skeleton`, `Progress`, `Spinner`.
- `Table`, `Pagination`.
- `Breadcrumb`, `EmptyState`, `Banner`.

### App-specific components (live in app, not in `packages/ui`)

- Marketplace: `SkillCard`, `PriceTag`, `RatingStars`, `CategoryChip`, `ReviewItem`, `VersionTimeline`, `CheckoutSummary`, `LicenseBadge`.
- Creator: `NodePalette`, `NodeInspector`, `GraphCanvas`, `CompiledPreview`, `SandboxPanel`.

---

## Typography rules

- **Display headings** (page H1): `text-3xl font-semibold tracking-tight` (mobile) / `text-4xl` (desktop). Sentence case.
- **Section headings** (H2): `text-xl font-semibold`.
- **Subheads** (H3): `text-base font-medium uppercase tracking-wide text-fg-muted`.
- **Body**: `text-sm leading-relaxed` for compact UI, `text-base` for marketing/long-form.
- **Code**: `font-mono text-xs` inline, `text-sm` in blocks.
- **Never** mix font weights mid-paragraph. No italics for emphasis — use bold sparingly.

---

## Spacing

- Use Tailwind defaults. Common rhythms: `gap-2`, `gap-4`, `gap-6`, `gap-8`.
- Page padding: `px-4 md:px-8 max-w-7xl mx-auto` on top-level layouts.
- Card padding: `p-6` (default), `p-4` (dense).

---

## Motion

- Default duration: 150ms (`duration-150`), ease: `ease-out`.
- Modals/sheets: 200ms with slight scale-in.
- No bouncy springs except for skill-card hover (`hover:-translate-y-0.5 hover:shadow-md`).
- `prefers-reduced-motion`: disable all transitions; only opacity transitions remain.

---

## Accessibility floor

- All interactive elements have ≥ 44×44 touch targets on mobile.
- Color contrast: 4.5:1 for body, 3:1 for large text. Verified in tokens above.
- Focus rings always visible: `focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2`.
- Every form input has a visible `<Label>` — placeholders are not labels.
- Modals trap focus and restore it on close (handled by Radix).
- ARIA live regions for toast notifications (`aria-live="polite"`).
- Skip-to-content link on every layout.

---

## Light vs dark default

- Marketplace: light by default (sells better; familiar shopping context).
- Creator: dark by default (long-running canvas work, less eye strain).
- Both expose a system/light/dark toggle in the user menu.

---

## Voice & copy

Centralize copy in `packages/ui/src/copy/` so we can refine voice without hunting through components.

- Tone: confident, plain, no jargon. "Buy" not "Procure". "Skill" not "Capability artifact".
- Numbers: prices in `$1.99` format always, no trailing zeros for whole dollars in card UI (`$5`), full cents in checkout (`$5.00`).
- Dates: relative for recent (`2 days ago`), absolute for older (`Mar 14, 2026`).
- Empty states have a friendly one-liner + a CTA, never a dead stare.

---

## Acceptance

- [ ] `packages/ui` exports all Phase 0 components, type-clean, story-covered (Storybook optional — defer if budget tight).
- [ ] `tokens.css` is imported in both apps' root layouts; dark mode toggle works.
- [ ] A "kitchen sink" route exists at `/_design` in both apps showing every component for visual regression review.
- [ ] Lighthouse accessibility ≥ 95 on the marketplace home and creator dashboard.
