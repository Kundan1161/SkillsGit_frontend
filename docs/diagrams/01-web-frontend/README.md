# 01 — Web frontend

Diagrams of the two Next.js apps, plus the buyer-journey end-to-end.
Source: actual files under `apps/web-marketplace/app/` +
`apps/web-marketplace/components/` and `apps/web-creator/app/` — not
the marketing site map. Where the spec promised more UI than ships
today (capture + persona builder in `web-creator`), the diagrams mark
those routes `<<deferred>>` so the gap is explicit.

## Files

### [`marketplace-routes.drawio`](marketplace-routes.drawio) — public + buyer UI

Every `apps/web-marketplace/app/<segment>/.../page.tsx` rendered as a
route tree, grouped by top-level URL segment. Dynamic segments stay
in their `[bracket]` form (`/c/[slug]`, `/s/[handle]/[slug]`,
`/u/[handle]`, `/library/[license-id]`, `/dashboard/skills/[id]`,
`/admin/skills/[id]/review`). Cross-route flows (home → detail →
checkout → success → library) are annotated as labelled edges. Notes
the actually-shipped surface: there is no `/settings` index page,
only the three children (`/settings/account`, `/settings/api-tokens`,
`/settings/billing`), and `/_design` is an internal preview that
isn't linked from `SiteHeader.NAV_LINKS`.

### [`creator-routes.drawio`](creator-routes.drawio) — creator UI today + deferred

The `apps/web-creator/app/` tree as it ships in Cycle 1 (skill
builder pipeline, import, templates, settings, auth, `/_design`) plus
a `Cycle2 << deferred >>` subgraph for the routes that
`team/04-capture-flow.md` §1 specs but that ship in Cycle 2:
`/personas`, `/personas/new`, `/personas/[id]`,
`/personas/[id]/neurons`, `/capture`, `/capture/[id]`. The backend
for those routes (`/v1/capture/*`) ships in Cycle 1 — the dashed
edge to the API node makes that explicit so a reader doesn't conclude
the capture feature is missing entirely.

### [`buyer-journey.drawio`](buyer-journey.drawio) — discovery → vault → agent

End-to-end LR flow from a buyer landing on the home page through
discovery (home / search / browse / category), the skill-detail
decision page, checkout (`/v1/checkout/sessions` → Stripe →
`checkout.session.completed` webhook → License issued), library
(`/library/[license-id]` + `VersionPicker` + `DownloadButton`),
delivery (`POST /v1/delivery/resolve` →
`vault.composer.compose_for_license` → S3 presigned URL with 60s
TTL), and the agent loop (Obsidian opens the vault; an AI agent
reads `vault.json` + neuron `.md` files and answers with
consulted-by attribution). Side branches: subscribe path (dashed),
freemium path (dashed), refund path (7-day MVP window).

### [`component-hierarchy.drawio`](component-hierarchy.drawio) — components by feature

The marketplace components tree grouped by feature subgraph:
`SiteHeader` / `SiteFooter` (chrome), `discovery/` (`SearchBar`,
`SkillCard`, `SkillGrid`, `CategoryRail`, `FilterSidebar`,
`SortDropdown`, `HeroBento`, `EmptyState`), `skill/`
(`SkillHero`, `PriceCard`, `WhatsInsidePreview`,
`AiRequirementsCard`, `VersionTimeline`, `FaqAccordion`,
`CreatorChip`, `InspiredBySection`), `checkout/`
(`checkout-summary`, `price-tag`, `stripe-redirect-button`),
`library/` (`LicenseCard`, `VersionPicker`, `DownloadButton`),
`reviews/` (scaffolded today — currently rendered inline on the
skill detail page), `admin/` (`ModerationQueue`,
`SkillReviewPanel`), `creator/` (`CreatorHeader`, `CreatorStats`,
`CreatorSkillsGrid`), `ui/` (shadcn primitives — the long list lives
in one node to keep the graph readable). `HeroBento.tsx` is marked
`<<wip>>` because it is uncommitted in the working tree at capture
time (git status: `??`).

## How to view

Every file in this folder is a `.drawio` file. Open it in the draw.io
desktop app or at [app.diagrams.net](https://app.diagrams.net), or
render it inline in VS Code with the
[Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)
extension. See [`docs/diagrams/README.md`](../README.md#how-to-view-these-diagrams)
for the full guide and the two flavours of `.drawio` in this repo
(native mxgraph vs Mermaid-embedded).

## A note on creator-side capture UX

The capture UX (`/capture`, `/capture/[id]`, `/personas`, etc.) is
defined in [`team/04-capture-flow.md`](../../../team/04-capture-flow.md)
§1 and the routes are listed there. Cycle 1 ships the **backend** for
them (`POST /v1/capture/sessions`, `/extract`, `/finalize` and friends
— see [`05-capture-pipeline/`](../05-capture-pipeline/)). The
**frontend** routes land in Cycle 2. The `<<deferred>>` stereotype on
the creator-routes diagram marks this explicitly. The
`docs/diagrams/00-system-overview/high-level-architecture.drawio`
already carries the same `<<deferred>>` marker for the `web-creator`
capture UI for the same reason.

## Stereotypes used in these diagrams

- `<<deferred>>` / `<<deferred Cycle 2>>` — scoped in
  `team/04-capture-flow.md` but pushed to Cycle 2 (no `page.tsx` on
  disk today).
- `<<wip>>` — file is present in the working tree but not yet
  committed (used today only for `components/discovery/HeroBento.tsx`).
