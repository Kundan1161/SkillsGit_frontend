# 04 — Vault + Obsidian

How a Skills Git vault is built, composed, watermarked, and rendered in
Obsidian. Source of truth is the code under
[`apps/api/src/vault/`](../../../apps/api/src/vault/) (`builder.py`,
`composer.py`, `manifest.py`, plus the `schema/vault-manifest-v1.json`
JSON Schema) and the curation orchestration script
[`apps/api/scripts/build_devops_vault.py`](../../../apps/api/scripts/build_devops_vault.py).
Buyer-facing summary lives in
[`docs/vault-format.md`](../../vault-format.md); the canonical spec
is [`team/03-vault-generation.md`](../../../team/03-vault-generation.md).

## Files

### [`vault-folder-structure.drawio`](vault-folder-structure.drawio) — what's in the zip

Folder tree for the two artifact shapes the system produces: an
occupation-only build and a persona-only build. Uses real filenames
from `apps/api/scripts/seed_data/devops/occupation.yaml` (30 members
across 7 domains) and the `jane-devops-demo/incident-veteran` persona
(7 memory neurons). Also shows the composed (delivered) shape =
occupation tree + persona subtrees overlay + regenerated `vault.json`
+ per-buyer watermark line on every `.md`.

### [`vault-build-pipeline.drawio`](vault-build-pipeline.drawio) — `build_occupation` + post-step

Sequence diagram for
[`vault/builder.py:build_occupation`](../../../apps/api/src/vault/builder.py)
plus the curation-side `.obsidian/graph.json` injection in
[`scripts/build_devops_vault.py:_polish_vault_with_graph_json`](../../../apps/api/scripts/build_devops_vault.py).
Eleven steps from "load DB rows" through "validate the produced
bundle". `build_persona` runs the same shape with two differences:
members are `PersonaNeuron` rows under `kind=memory_neuron`, and the
in-zip manifest is `persona.json` instead of `vault.json` (the
composer regenerates the canonical `vault.json` at delivery time).

### [`obsidian-rendering.drawio`](obsidian-rendering.drawio) — what happens when a buyer opens the vault

How stock Obsidian (no plugins required) renders the vault: walks
every `.md`, extracts `[[wiki-links]]` from body text (including the
auto-appended `## Linked notes` footer) into the graph view, groups
nodes by tag using the shipped `.obsidian/graph.json` color preset,
and shows reverse references in the backlinks panel. A separate
machine-readable mirror lives in `vault.json` for agents that don't
want to walk files.

### [`attribution-format.drawio`](attribution-format.drawio) — comment ordering inside every .md

The five-layer file format spec §7: frontmatter → body → `## Linked
notes` → `<!-- skg-attribution: -->` → `<!-- license: ... -->`.
Builder emits the multi-line YAML-style attribution comment per
[`vault/builder.py:_emit_attribution_comment`](../../../apps/api/src/vault/builder.py);
composer appends the single-line per-buyer watermark per
[`delivery/watermark.py:append_watermark`](../../../apps/api/src/delivery/watermark.py).
HMAC-keyed ids (not raw uuids) keep the watermark non-identifying.

### [`composition-merge.drawio`](composition-merge.drawio) — `compose_for_license` end-to-end

Sequence diagram for
[`vault/composer.py:compose_for_license`](../../../apps/api/src/vault/composer.py).
Thirteen numbered steps: license validation → persona license
intersection → build resolution → cache key → cache lookup → (on
miss) zip read + persona subtree merge + manifest re-assembly + link
re-resolution + per-buyer watermark + deterministic re-zip + S3
upload + `vault_downloads` row + cache write → (always) 60-second
presigned URL. Includes the 24h cache TTL, 60s URL TTL, 1h S3
lifecycle, and the documented drift that the audit row is written
only on cache miss.

### A note on `composition-merge.drawio`

This is one of the three headline diagrams in the repo that ships as
**native mxgraph cells** (Mode C in the master README) — hand-laid
boxes-and-arrows rather than a Mermaid embed. Every shape is directly
editable in draw.io with no Mermaid re-render. The four other
`.drawio` files in this folder are Mermaid-embedded (Mode A).

## Buyer-facing reference

[`docs/vault-format.md`](../../vault-format.md) is the short
buyer-facing summary of the vault format. It covers the manifest
fields a consumer agent cares about, the attribution comment shape,
how `[[wiki-links]]` and the graph view render, watermark semantics,
a minimal Python loader, and the schema evolution policy. Read it
alongside `attribution-format.drawio` and `obsidian-rendering.drawio`.

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
| `VaultManifest` Pydantic model + `write_manifest` | `apps/api/src/vault/manifest.py` |
| JSON Schema (`vault-manifest-v1.json`) | `apps/api/src/vault/schema/vault-manifest-v1.json` |
| `build_occupation` / `build_persona` | `apps/api/src/vault/builder.py` |
| Attribution comment emitter | `apps/api/src/vault/builder.py:_emit_attribution_comment` |
| Determinism (epoch timestamp + sorted zip) | `apps/api/src/vault/builder.py:_write_zip` |
| `compose_for_license` + helpers | `apps/api/src/vault/composer.py` |
| Cache key + cache TTL constants | `apps/api/src/vault/composer.py` (top of file) |
| Per-buyer watermark | `apps/api/src/delivery/watermark.py:append_watermark` |
| `vault_validator.validate_vault` | `apps/api/src/vault/validator.py` |
| `.obsidian/graph.json` post-step | `apps/api/scripts/build_devops_vault.py:_polish_vault_with_graph_json` |
| Buyer-facing format doc | `docs/vault-format.md` |
| Canonical spec | `team/03-vault-generation.md` |
