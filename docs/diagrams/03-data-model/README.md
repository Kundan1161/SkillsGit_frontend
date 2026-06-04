# 03 — Data model

Entity-relationship diagrams for the Skills Git Postgres schema after
Cycle 1 (Occupations + Personas + Capture + Vault). Source of truth is
the SQLAlchemy ORM in `apps/api/src/*/models.py` plus the Alembic
migrations under `apps/api/alembic/versions/0001*` (initial spine) and
`0006*` through `0010*` (Cycle-1 deltas). Specs:
[`prompts/02-data-model-core.md`](../../../prompts/02-data-model-core.md)
and [`team/01-data-model-deltas.md`](../../../team/01-data-model-deltas.md).

## Files

### [`er-full.drawio`](er-full.drawio) — every table in the system

22 tables: the pre-Cycle-1 spine (`users`, `creator_profiles`,
`api_tokens`, `categories`, `skills`, `skill_versions`, `orders`,
`order_items`, `subscriptions`, `licenses`, `reviews`, `payouts`,
`audit_log`, `editorial_picks`, `search_alerts`, `webhook_events`,
`moderation_actions`) plus the eight Cycle-1 additions
(`occupations`, `occupation_skills`, `personas`, `persona_neurons`,
`capture_sessions`, `capture_attachments`, `vault_builds`,
`vault_downloads`). Shows the 2–5 most-queried columns per table and
every foreign key with cardinality. Start here if you're new to the
codebase.

### [`er-skills-core.drawio`](er-skills-core.drawio) — the pre-Cycle-1 spine

Five tables: `users`, `creator_profiles`, `categories`, `skills`,
`skill_versions`. The only Cycle-1 change visible here is the `kind`
discriminator column on `skills` (added in migration 0006).
Everything else predates Cycle 1. Read this if you want to understand
the original marketplace data shape.

### [`er-marketplace.drawio`](er-marketplace.drawio) — pricing + licensing

Seven tables: `users`, `skills`, `skill_versions`, `orders`,
`order_items`, `subscriptions`, `licenses`, `reviews`, `payouts`. The
Cycle-1 additions visible here are the two new columns on `licenses`:
`composition_role` and `target_occupation_skill_id`, both shipped in
migration 0009.

### [`er-cycle1-extensions.drawio`](er-cycle1-extensions.drawio) — just the new tables

The eight new tables from migrations 0006–0009, with `skills`,
`users`, and `licenses` shown only as anchor nodes so the new FK
edges have endpoints. Read this if you already know the marketplace
and want to see exactly what Cycle 1 added.

### [`er-licensing-composition.drawio`](er-licensing-composition.drawio) — license → vault download

Focused view of how a buyer's license set composes into a downloaded
vault. The diagram covers `licenses` (with both composition roles),
`vault_builds` (per skill, per version), and `vault_downloads` (per
buyer, per compose call). Below the ER, a Mermaid `%%` comment block
walks through the 13-step composition algorithm — see
[`team/03-vault-generation.md`](../../../team/03-vault-generation.md)
§10 for the canonical spec and
[`apps/api/src/vault/composer.py`](../../../apps/api/src/vault/composer.py)
for the actual implementation.

### A note on `er-full.drawio`

`er-full.drawio` is one of the three headline diagrams in this repo
that ships as **native mxgraph cells** (Mode C in the master README) —
hand-laid boxes-and-arrows rather than a Mermaid embed. Every entity
is directly editable in draw.io with no Mermaid re-render. The four
other `.drawio` files in this folder are Mermaid-embedded (Mode A).

## Recommended read order

- **New to the codebase:** `er-full.drawio` → `er-skills-core.drawio` →
  `er-cycle1-extensions.drawio`. Then `er-licensing-composition.drawio`
  before reading the composer code.
- **Already know the original marketplace:** jump straight to
  `er-cycle1-extensions.drawio` and `er-licensing-composition.drawio`.
- **Working on billing or delivery:** `er-marketplace.drawio` plus
  `er-licensing-composition.drawio`.

## Cycle-1 stereotypes

Mermaid `erDiagram` does not support `<<new>>` / `<<existing>>`
stereotypes on entities (those are a `classDiagram` feature). Cycle-1
additions are called out in the per-column comments instead. The
eight wholly-new tables are listed in the
`er-cycle1-extensions.drawio` description above; the two column-level
additions are:

| Table | Cycle-1 columns | Migration |
|---|---|---|
| `skills` | `kind` enum (`skill | occupation | persona | memory_neuron`) | 0006 |
| `licenses` | `composition_role` enum + `target_occupation_skill_id` FK | 0009 |

A small set of join FKs (`occupations.latest_build_id`,
`personas.latest_build_id` → `vault_builds.id`) is added as deferred
foreign keys in migration 0009 because `vault_builds` doesn't exist
when `occupations`/`personas` are first created in 0006/0007.

## How to view

Every file in this folder is a `.drawio` file. Open it in the draw.io
desktop app or at [app.diagrams.net](https://app.diagrams.net), or
render it inline in VS Code with the
[Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)
extension. See [`docs/diagrams/README.md`](../README.md#how-to-view-these-diagrams)
for the full guide and the two flavours of `.drawio` in this repo
(native mxgraph vs Mermaid-embedded).

## Source pointers

| Topic | File |
|---|---|
| `User`, `CreatorProfile`, `ApiToken` ORM | `apps/api/src/users/models.py` |
| `Skill`, `SkillVersion`, `Category`, `SkillKind` enum | `apps/api/src/skills/models.py` |
| `Occupation`, `OccupationSkill`, `OccupationMemberRole` | `apps/api/src/occupations/models.py` |
| `Persona`, `PersonaNeuron` | `apps/api/src/personas/models.py` |
| `CaptureSession`, `CaptureAttachment`, `CaptureSessionStatus` | `apps/api/src/capture/models.py` |
| `VaultBuild`, `VaultDownload`, `VaultBuildStatus` | `apps/api/src/vault/models.py` |
| `Order`, `OrderItem`, `Subscription`, `License`, `LicenseCompositionRole`, `Payout`, `WebhookEvent` | `apps/api/src/billing/models.py` |
| `Review` | `apps/api/src/reviews/models.py` |
| `EditorialPick`, `SearchAlert` | `apps/api/src/catalog/models.py` |
| `ModerationAction` | `apps/api/src/admin/models.py` |
| `AuditLog` (no module owns it — defined inline) | `apps/api/src/core/db.py` |
| Initial spine migration | `apps/api/alembic/versions/0001_initial.py` |
| Cycle-1 deltas | `apps/api/alembic/versions/0006_…` through `0010_…` |
