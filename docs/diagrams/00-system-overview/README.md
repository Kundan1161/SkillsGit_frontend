# 00 — System overview

Top-of-funnel diagrams. Start here, then descend into the per-subsystem
folders (`01-web-frontend/`, `02-backend-api/`, `03-data-model/`, ...).

## Read order

1. **[`system-context.drawio`](system-context.drawio)** — C4 level-1 context
   diagram. Shows external actors (Creator, Buyer, Admin, AI Agent),
   the Skills Git platform as a single node, and every external system
   it talks to (Stripe, Anthropic, S3/R2, SMTP, Obsidian on the buyer
   side). Read this first to understand the surface area.
2. **[`high-level-architecture.drawio`](high-level-architecture.drawio)** —
   one zoom level deeper. Shows the three apps (`apps/api`,
   `apps/web-marketplace`, `apps/web-creator`), the three shared
   packages (`packages/skills-schema`, `packages/api-client`,
   `packages/ui`), and the local-dev infra in `infra/docker-compose.yml`
   (postgres, redis, minio, mailhog). The `web-creator` capture UI is
   marked `<<deferred>>` because the routes ship in Cycle 2 — the
   backend already supports them today.
3. **[`component-map.drawio`](component-map.drawio)** — every backend module
   in `apps/api/src/` grouped by bounded context. Subgraphs split
   "Existing" (auth, users, skills, catalog, billing, delivery,
   reviews, creator, webhooks, admin, storage) from "Cycle-1 new"
   (`occupations`, `personas`, `capture`, `vault`) and "Core" (config,
   db, deps, errors, logging, pagination, rate_limits, cache,
   anthropic). Edges are real import / FK / runtime dependencies
   observed in the source — notably `capture → anthropic`,
   `vault → occupations`/`personas`/`cache`, and the dashed
   `billing → personas` 409-gate added by Wave 2.

## A note on `high-level-architecture.drawio`

This is one of the three headline diagrams in the repo that ships as
**native mxgraph cells** (Mode C in the master README) rather than as a
Mermaid-embedded `.drawio`. Every shape is editable directly in
draw.io — no re-rendering or import step. See the
[master README](../README.md#two-flavours-of-drawio-in-this-repo) for
the full list of native vs Mermaid-embedded files.

## How to view

Every file in this folder is a `.drawio` file. Open it in the draw.io
desktop app or at [app.diagrams.net](https://app.diagrams.net), or
render it inline in VS Code with the
[Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)
extension. See [`docs/diagrams/README.md`](../README.md#how-to-view-these-diagrams)
for the full guide and the two flavours of `.drawio` in this repo
(native mxgraph vs Mermaid-embedded).

## Stereotypes used in these diagrams

- `<<existing>>` — module that existed before Cycle 1 (auth, users,
  skills, catalog, billing, delivery, reviews, creator, webhooks,
  admin, storage, core).
- `<<new>>` — module shipped in Cycle 1 (occupations, personas,
  capture, vault).
- `<<deferred>>` — scoped but pushed to Cycle 2 (`web-creator`
  capture UI).
