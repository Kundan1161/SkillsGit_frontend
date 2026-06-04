# 06 — Composition + delivery

Diagrams of the buyer-facing compose-on-demand flow: the HTTP wire
shape, the per-buyer watermark format, the 24h Redis cache lifecycle,
and license → SkillVersion → VaultBuild resolution. Source of truth is
the shipped code under `apps/api/src/vault/` and `apps/api/src/delivery/`
— not the spec — so this folder reflects what the buyer actually
experiences today (vs the spec's wishful version).

The internal manifest merge, link re-resolution, and deterministic
re-zip are NOT re-drawn here — Agent C already covered them in
[`04-vault-and-obsidian/composition-merge.drawio`](../04-vault-and-obsidian/composition-merge.drawio).
This folder fills in everything around that hot path.

## Files

### [`compose-sequence.drawio`](compose-sequence.drawio) — wire-level API flow

End-to-end sequence for a buyer's `POST
/v1/licenses/{occupation_license_id}/vault` call. Walks router → auth
gates (404 / 403 / 409 codes) → cache check → cold-path merge → 60s
presigned URL → audit row. The download itself is a direct
`Buyer → S3` GET against the presigned URL; the platform does not
proxy the bytes. **Drift note:** spec §4 promises a 202-then-200
two-call pattern; the code returns 200 on both hit and miss paths
(`cache_hit` boolean on the response distinguishes them). The compose
is synchronous inline; cold path is ~1-5s at MVP scale and that's
acceptable per spec §12 (~50 MB max bundle).

### [`watermark-format.drawio`](watermark-format.drawio) — per-buyer HMAC watermark

The single-line HTML comment the composer appends to every `.md` in
a delivered bundle: `<!-- license:HMAC16 buyer:HMAC16 ts:ISO8601-Z -->`.
The diagram shows where in the file stack it lands (after the builder's
`<!-- skg-attribution: -->`), how `hmac_id()` derives the 16-hex ids
from `PLATFORM_HMAC_KEY`, why the surrounding bytes are stable across
buyers (sorted zip + pinned epoch timestamps), and the server-side
forensic replay that maps a leaked file back to a buyer.

### [`cache-invalidation.drawio`](cache-invalidation.drawio) — Redis lifecycle

The 24h composed-bundle cache: key derivation (`sha256` over
`buyer_id | occ_skill_id | occ_build_id | sorted(persona_build_ids)`),
hot-path (HIT → presign cached `storage_url`), cold-path (MISS → full
compose → upload → cache write), and natural invalidation (new
`vault_build` → new `build_id` → new cache key; old entry just ages
out). `cache.invalidate()` exists but is currently unused — Cycle 2's
creator-side "rebuild now" UI will wire it up. Two-backend façade:
in-memory dict under `ENV=test` / `SKG_CACHE_INMEM=1`; `redis.asyncio`
otherwise.

### [`license-resolution.drawio`](license-resolution.drawio) — version + build resolution

"What version of skill S does buyer B see for license L?" The
existing pre-Cycle-1 rule (`License.max_version` ceiling, `is_yanked`
filter, subscription vs one-time `released_at` semantics) plus the
composition-specific layer the composer adds on top: `_latest_succeeded_build`
for the occupation skill + each held persona license, filtered by
`composition_role=persona` AND `target_occupation_skill_id =
occupation.skill_id`. Includes the persona-reparenting protection:
`target_occupation_skill_id` is snapshotted on the license row at
purchase time per migration 0009 / ADR-002, so a creator later
changing `personas.parent_occupation_id` does not invalidate sold
licenses.

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
| `compose_for_license` entry point | `apps/api/src/vault/composer.py` |
| Composer constants (24h cache, 60s URL) | `apps/api/src/vault/composer.py` top-of-file |
| Cache key derivation | `apps/api/src/vault/composer.py:_cache_key` |
| HMAC id helper | `apps/api/src/delivery/watermark.py:hmac_id` |
| Watermark append | `apps/api/src/delivery/watermark.py:append_watermark` |
| Watermark stamp loop | `apps/api/src/vault/composer.py:_stamp_markdown_with_watermark` |
| Cache façade (Redis + in-mem) | `apps/api/src/core/cache.py` |
| FastAPI compose endpoint | `apps/api/src/vault/router.py:compose_vault_endpoint` |
| License version resolver | `apps/api/src/billing/service.py:resolve_version` |
| Latest succeeded build | `apps/api/src/vault/composer.py:_latest_succeeded_build` |
| Persona license intersection | `apps/api/src/vault/composer.py:_intersect_persona_licenses` |
| `vault_downloads` audit row | `apps/api/src/vault/models.py:VaultDownload` + migration `0009_vault_builds_and_downloads.py` |
| `licenses.composition_role` + `target_occupation_skill_id` | migration `0009_vault_builds_and_downloads.py` |
| Spec — composition algorithm | `team/03-vault-generation.md` §10 |
| Spec — vault download endpoints | `team/02-api-surface.md` §4 |
| Spec — license-resolution rule | `prompts/02-data-model-core.md` §License resolution |
| ADRs | ADR-002 (per-buyer license set), ADR-006 (compose-on-demand + cache), ADR-010 (watermark), ADR-013 (auditable composed artifact) |
