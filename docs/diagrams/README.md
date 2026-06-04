# Architecture diagrams

Complete technical architecture of the Skills Git platform after Cycle 1
(Occupations + Personas + Capture). One folder per subsystem; each folder
contains draw.io files (`.drawio`) and a `README.md` explaining what's
inside.

## Folder index

| Folder | What's inside |
|---|---|
| [`00-system-overview/`](00-system-overview/) | System context (actors + external systems), high-level architecture, component map of every module and technology |
| [`01-web-frontend/`](01-web-frontend/) | `web-marketplace` and `web-creator` route trees, buyer journey, component hierarchy |
| [`02-backend-api/`](02-backend-api/) | FastAPI module graph, request pipeline, auth flow, full `/v1/*` API surface |
| [`03-data-model/`](03-data-model/) | Full ER diagram, plus focused views: skill-core, marketplace, Cycle-1 extensions, licensing-composition |
| [`04-vault-and-obsidian/`](04-vault-and-obsidian/) | Vault folder structure, build pipeline, Obsidian wiki-link rendering, attribution comment format, composition merge |
| [`05-capture-pipeline/`](05-capture-pipeline/) | `CaptureSession` state machine, full capture sequence, atomic finalize transaction, PII + quota |
| [`06-composition-delivery/`](06-composition-delivery/) | Compose-for-license sequence, per-buyer watermark format, cache invalidation, license resolution |
| [`07-demo-cli/`](07-demo-cli/) | Layer-C demo CLI flow, consulted-neuron attribution extraction, `--snapshot-only` path |
| [`08-infrastructure/`](08-infrastructure/) | Docker Compose stack, `.env` → settings → runtime config flow, CI pipeline, production deployment target |
| [`09-external-integrations/`](09-external-integrations/) | Stripe Connect payouts, Anthropic Claude usage, S3 object layout, Stripe webhook → audit-log flow |

## How to view these diagrams

Every diagram in this tree is a `.drawio` file. Open one of these ways:

1. Double-click the file (opens the draw.io desktop app if installed).
2. Drag-and-drop it onto [https://app.diagrams.net](https://app.diagrams.net).
3. In VS Code, install the
   ["Draw.io Integration"](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)
   extension — `.drawio` files then render inline in the editor.

GitHub does **not** render `.drawio` natively — clicking a file in the
GitHub UI shows the raw XML or downloads it. Use one of the three
options above instead.

### Two flavours of `.drawio` in this repo

The 40 diagrams ship in two formats. Both open the same way; the
difference matters only when you want to edit:

**Native mxgraph (Mode C)** — three headline diagrams are hand-built as
native draw.io cells (rectangles, arrows, groups). You can drag, resize,
restyle every element visually:

- [`00-system-overview/high-level-architecture.drawio`](00-system-overview/high-level-architecture.drawio)
- [`03-data-model/er-full.drawio`](03-data-model/er-full.drawio)
- [`04-vault-and-obsidian/composition-merge.drawio`](04-vault-and-obsidian/composition-merge.drawio)

**Mermaid-embedded (Mode A)** — the other 37 are a single Mermaid cell
wrapped in a `.drawio` shell (using draw.io's built-in
`shape=mxgraph.mermaid` with the source URL-encoded into the
`mermaidData` style attribute). draw.io renders the Mermaid inline.
To edit: right-click the cell → *Edit Mermaid* (or *Extras → Edit
Diagram* if you want raw XML access). The Mermaid source stays inside
the `.drawio` file — no separate `.mmd` to maintain.

### Regenerating Mermaid-embedded `.drawio` files

Mermaid sources live inside each `.drawio` file's `mermaidData` style
attribute. To regenerate from a fresh `.mmd` (e.g. for a new diagram or
after an edit done outside draw.io), use the conversion script:

```bash
# Add a new .mmd file in the appropriate subfolder, then:
python scripts/convert_mermaid_to_drawio.py
```

The script (`scripts/convert_mermaid_to_drawio.py`) globs
`docs/diagrams/**/*.mmd`, writes a Mermaid-embedded `.drawio` next to
each one, and deletes the `.mmd` on success. It skips the three Mode-C
headline files even if you accidentally drop a `.mmd` with the same
name.

## Diagram conventions

Each Mermaid-embedded diagram uses one of these Mermaid diagram types
(visible in the first non-comment line of the embedded source):

- **`graph LR` / `graph TB`** — system architecture (boxes + arrows).
- **`sequenceDiagram`** — request/response flows over time.
- **`erDiagram`** — data model (tables + relationships).
- **`stateDiagram-v2`** — state machines (e.g., capture session lifecycle).
- **`classDiagram`** — module structure with public surface.
- Solid arrows = synchronous call. Dashed arrows = async (queue, webhook, etc.).
- `<<existing>>` stereotype = component that existed before Cycle 1.
- `<<new>>` stereotype = component shipped in Cycle 1.
- `<<deferred>>` stereotype = scoped but pushed to Cycle 2.

## Source of truth

The diagrams reflect the codebase at commit `cycle-1/occupations-personas-capture`
(Cycle 1 complete). They depend on:

- 18 ADRs in [team/decisions.md](../../team/decisions.md)
- Architecture spec in [team/00-architecture.md](../../team/00-architecture.md)
- Data model deltas in [team/01-data-model-deltas.md](../../team/01-data-model-deltas.md)
- API surface in [team/02-api-surface.md](../../team/02-api-surface.md)
- Vault generation spec in [team/03-vault-generation.md](../../team/03-vault-generation.md)
- Capture flow spec in [team/04-capture-flow.md](../../team/04-capture-flow.md)
- 5 Alembic migrations in [apps/api/alembic/versions/](../../apps/api/alembic/versions/)

When the code changes, the diagrams stay accurate by regenerating from the
spec + module source (the agents that wrote them read both).
