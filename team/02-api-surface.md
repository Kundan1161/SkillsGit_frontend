# 02 — API Surface

**Owner:** Architect
**Status:** Proposed
**Reads:** `prompts/shared/api-conventions.md`, existing routers in
`apps/api/src/*/router.py`.
**Cross-refs:** ADR-004 through ADR-014, `team/01-data-model-deltas.md`.

All new endpoints follow `prompts/shared/api-conventions.md`:

- `/v1` prefix, cursor pagination (`limit`, `cursor`), idempotency
  header on every state-mutating POST, `ErrorResponse` body shape on
  non-2xx, `audit_log` writes on every meaningful mutation.
- Existing dependencies: `current_active_user`, `require_creator`,
  `require_admin` from `src/auth/deps.py`.
- New scope per ADR-002: an authz helper
  `require_license_owner(license_id)` already implicit in
  `get_license_for_user` (delivery/service.py).

Groups below:
1. Occupations (creator + reader)
2. Personas (creator + reader)
3. Capture
4. Vault builds + composed downloads
5. Discovery additions (browse + recommendations)
6. Webhooks (creator-facing — new event types only)

**Cross-references rather than re-spec:** the existing
`POST /v1/checkout/sessions` and `POST /v1/subscriptions` already
handle paid purchases of any `skills` row regardless of `kind`. We
add **gating logic** for persona purchases but no new checkout
endpoint. Refunds, downloads of single skills.md files, and license
listing all reuse existing endpoints.

---

## 1. Occupations module

Module path: `apps/api/src/occupations/`. New router mounted at `/v1`.

### Creator endpoints (require_creator)

| Method | Path | Auth scope | Request | Response | Module |
|---|---|---|---|---|---|
| POST | `/v1/occupations` | creator | `OccupationCreate { name, slug, summary_md, domains[], description_md, category, tags[], pricing_model, one_time_price_cents?, subscription_price_cents? }` | 201 `OccupationRead` (includes new `skill_id`, `kind`, side-table fields) + `Location` header | occupations |
| PATCH | `/v1/occupations/{id}` | creator (owner) | `OccupationUpdate` — partial of the above (excludes `slug`) | 200 `OccupationRead` | occupations |
| POST | `/v1/occupations/{id}/skills` | creator (owner) | `OccupationSkillsBulkSet { items: [{member_skill_id, domain, role, sort_order, pinned, notes_md?}] }` | 200 `OccupationSkillList` — replaces the membership set transactionally | occupations |
| POST | `/v1/occupations/{id}/skills/{member_skill_id}` | creator (owner) | `OccupationSkillUpsert { domain, role, sort_order, pinned, notes_md? }` | 200 `OccupationSkillRead` — add/update single | occupations |
| DELETE | `/v1/occupations/{id}/skills/{member_skill_id}` | creator (owner) | — | 204 | occupations |
| POST | `/v1/occupations/{id}/build` | creator (owner) | `OccupationBuildRequest { version }` | 202 `JobAccepted { job_id, build_id }` — enqueues Arq job, sets `vault_builds` row in `queued` | occupations + vault |
| POST | `/v1/occupations/{id}/publish` | creator (owner) | `PublishRequest { version, changelog_md?, target_version? }` | 202 `JobAccepted` — runs build → marks `skill_versions.released_at` on success → fires `version.published` webhook | occupations |

Service-level validations:
- `OccupationSkillsBulkSet`: every `member_skill_id` must reference a
  row with `kind='skill'`; else 422 `occupation.invalid_member_kind`.
  `domain` must be a member of the occupation's `domains[]`.
- `OccupationBuildRequest`: requires at least 1 member skill and a valid
  semver `version`.

### Public reader endpoints

| Method | Path | Auth scope | Request | Response | Module |
|---|---|---|---|---|---|
| GET | `/v1/occupations` | public | filters: `category?`, `domain?`, `q?`, `creator_handle?`, `order?`; pagination | 200 `OccupationListResponse` — cards include name, summary, domain chips, persona_count, price | occupations |
| GET | `/v1/occupations/{handle}/{slug}` | public | — | 200 `OccupationDetailResponse` — includes member skill summaries grouped by domain + role, persona overlays list, latest build summary, version history | occupations |
| GET | `/v1/occupations/{id}/personas` | public | filters: `order?`, pagination | 200 `PersonaListResponse` filtered to `parent_occupation_id={id}` and `status='published'` | personas |
| GET | `/v1/occupations/{id}/versions` | public | pagination | 200 `SkillVersionList` — straight passthrough to `skill_versions` for the occupation row | skills (existing) |
| GET | `/v1/occupations/{id}/graph-preview` | public | — | 200 `VaultGraphPreview { nodes[], edges[] }` — derived from member skills' `links[]` for the marketplace's "see the graph" widget; capped at 200 nodes | occupations |

`OccupationDetailResponse` is the source of truth for the detail page
component — schema lives in `apps/api/src/occupations/schemas.py`.

---

## 2. Personas module

Module path: `apps/api/src/personas/`.

### Creator endpoints

| Method | Path | Auth scope | Request | Response | Module |
|---|---|---|---|---|---|
| POST | `/v1/personas` | creator | `PersonaCreate { name, slug, parent_occupation_id, creator_intro_md, specialization?, years_of_experience?, pricing_model, one_time_price_cents?, subscription_price_cents?, description_md, category, tags[] }` | 201 `PersonaRead` | personas |
| PATCH | `/v1/personas/{id}` | creator (owner) | `PersonaUpdate` — partial; cannot change `slug` or `parent_occupation_id` after first publish | 200 `PersonaRead` | personas |
| POST | `/v1/personas/{id}/neurons/order` | creator (owner) | `NeuronOrderUpdate { items: [{neuron_skill_id, sort_order, section?}] }` | 200 `PersonaNeuronList` — reorders only, never adds | personas |
| DELETE | `/v1/personas/{id}/neurons/{neuron_skill_id}` | creator (owner) | — | 204 — removes from persona; the neuron row is soft-deleted only if no other persona references it (Phase-2 cleanup job) | personas |
| POST | `/v1/personas/{id}/build` | creator (owner) | `PersonaBuildRequest { version }` | 202 `JobAccepted` | personas + vault |
| POST | `/v1/personas/{id}/publish` | creator (owner) | `PublishRequest { version, changelog_md? }` | 202 `JobAccepted` — runs build → sets `released_at` | personas |

### Public reader endpoints

| Method | Path | Auth scope | Request | Response | Module |
|---|---|---|---|---|---|
| GET | `/v1/personas` | public | filters: `parent_occupation_id?`, `creator_handle?`, `q?`, pagination | 200 `PersonaListResponse` | personas |
| GET | `/v1/personas/{handle}/{slug}` | public | — | 200 `PersonaDetailResponse` — includes parent occupation summary, neuron count, sample neuron titles (no body content), reviews, version history | personas |
| GET | `/v1/personas/{id}/neurons` | **owner of an entitlement only** (license on this persona OR creator owns the persona) | filters: `section?`, pagination | 200 `NeuronList` — full body content gated behind the entitlement check; non-entitled callers get 404 to avoid existence leak | personas |
| GET | `/v1/personas/{id}/graph-preview` | public | — | 200 `VaultGraphPreview` — shows neurons + their declared links into the parent occupation (parent nodes labeled "from base") | personas |

### Persona checkout enforcement

This is **not** a new endpoint — it is added validation to the existing
`POST /v1/checkout/sessions`:

```
If skill.kind == 'persona':
   require buyer has an active license on persona.parent_occupation_id;
   else 409 {
     code: "persona.requires_parent_occupation",
     message: "Buy the parent occupation first.",
     details: [{
       field: "parent_occupation_id",
       code: "missing_license",
       suggested_action: "purchase_occupation",
       occupation_skill_id: "<uuid>",
       occupation_listing_url: "..."
     }]
   }
```

The 409 response body carries enough information for the frontend to
render a "Buy the base first" CTA without a second roundtrip.

---

## 3. Capture module

Module path: `apps/api/src/capture/`.

### Endpoints

| Method | Path | Auth scope | Request | Response | Module |
|---|---|---|---|---|---|
| POST | `/v1/capture/sessions` | creator | `CaptureSessionCreate { persona_id, title, situation_md, decision_md, outcome_md, context_md? }` | 201 `CaptureSessionRead` (status=`draft`) + 202-like body promising async extraction; `Location` header | capture |
| POST | `/v1/capture/sessions/{id}/attachments` | creator (owner) | `multipart/form-data` — file upload | 201 `CaptureAttachmentRead { id, storage_url, filename, sha256, size_bytes }` | capture |
| DELETE | `/v1/capture/sessions/{id}/attachments/{aid}` | creator (owner) | — | 204 | capture |
| POST | `/v1/capture/sessions/{id}/extract` | creator (owner) | — | 202 `JobAccepted { job_id }` — re-runs LLM extraction (idempotent: same input → same draft within model-version drift) | capture |
| GET | `/v1/capture/sessions/{id}` | creator (owner) | — | 200 `CaptureSessionRead` — includes `draft_md`, `suggested_links_json`, `pii_flags_json`, `status` | capture |
| PATCH | `/v1/capture/sessions/{id}` | creator (owner) | `CaptureSessionUpdate { draft_md?, suggested_links_json?, title?, fields? }` | 200 `CaptureSessionRead` — creator can edit the AI draft directly | capture |
| POST | `/v1/capture/sessions/{id}/finalize` | creator (owner) | `CaptureFinalize { neuron_slug, neuron_version, links_accept[] }` | 201 `NeuronCreated { neuron_skill_id, neuron_version, persona_id, vault_path_hint }` — runs validate_file() one last time; 422 with field errors on failure | capture |
| POST | `/v1/capture/sessions/{id}/abandon` | creator (owner) | `Abandon { reason? }` | 200 `CaptureSessionRead` (status=`abandoned`) — for analytics, no real cleanup | capture |
| GET | `/v1/capture/sessions` | creator | filters: `persona_id?`, `status?`, pagination | 200 `CaptureSessionListResponse` — creator's draft list | capture |

The job status endpoint `GET /v1/jobs/{job_id}` (already specified in
`shared/api-conventions.md`) reports progress on the `extract` task.

### Capture quota

Tracked in `users` via a small denormalized field (deferred — for MVP
we ride a Redis counter keyed `capture_quota:{user_id}:{yyyy-mm}`,
incremented on each successful extraction, with the daily limit
documented as 10/month per ADR-008. Schema enhancement for paid quota
is Phase 2).

---

## 4. Vault builds + composed downloads

Module path: `apps/api/src/vault/` (new — see ADR open note).

### Build status endpoints

| Method | Path | Auth scope | Request | Response | Module |
|---|---|---|---|---|---|
| GET | `/v1/vault-builds/{id}` | creator (owner of parent skill) OR admin | — | 200 `VaultBuildRead { id, skill_id, skill_version_id, status, content_hash, manifest_summary, build_log_json, built_at, error? }` | vault |
| GET | `/v1/occupations/{id}/builds` | creator (owner) OR admin | filters: `status?`, pagination | 200 `VaultBuildList` | vault |
| GET | `/v1/personas/{id}/builds` | creator (owner) OR admin | same | 200 `VaultBuildList` | vault |
| GET | `/v1/vault-builds/{id}/manifest` | creator (owner) | — | 200 `VaultManifest` — full vault.json contents from `manifest_json` column | vault |

### Composed-bundle download (the buyer flow)

| Method | Path | Auth scope | Request | Response | Module |
|---|---|---|---|---|---|
| POST | `/v1/licenses/{occupation_license_id}/vault` | license owner OR admin | `VaultDownloadRequest { include_personas?: [persona_license_id...] (defaults to "all active") }` | 202 `JobAccepted` first time (compose async), then 200 `VaultDownloadResponse { download_url, composed_hash, expires_at, manifest_summary }` on subsequent (cache hit) | vault |
| GET | `/v1/licenses/{occupation_license_id}/vault/latest` | license owner | — | 302 to a freshly composed URL, or 202 to a job if not cached | vault |
| GET | `/v1/me/vault-downloads` | current user | pagination | 200 `VaultDownloadListResponse` — history with `composed_hash`, persona set, timestamps | vault |

Compose flow (refresher from ADR-006):
1. Validate the buyer owns an active license on the occupation behind
   `occupation_license_id`. The license's `composition_role` must be
   `occupation`.
2. Build the persona license set: all active licenses where
   `buyer_id = caller` AND `composition_role = 'persona'` AND
   `target_occupation_skill_id = <occupation.skill_id>`. Intersect with
   the optional `include_personas` filter.
3. Compute the cache key:
   `sha256(occupation_build_id || sorted(persona_build_ids))`.
4. If cached in Redis (`composed:{buyer}:{occ}:{key}`) AND its S3
   object still exists → return it (200).
5. Else queue `vault.compose(occupation_license_id, persona_license_ids[])`
   → respond 202.
6. The job runs the composer (see `03-vault-generation.md`), writes
   `vault_downloads` row, populates the Redis cache, returns the URL via
   job-status endpoint.
7. Audit log entries: `license.vault_downloaded` for the occupation
   license, plus one per persona license (so creator dashboards show
   "your persona was used in N composed vaults this week").

### Single-skill download remains untouched

Buyers who only want a specific neuron or skill file can still hit
`GET /v1/licenses/{id}/download` (existing). The vault is a *bundle*
on top, not a replacement.

---

## 5. Discovery additions

Catalog router gets light additions only; the bulk of "browse
occupations" is its own resource endpoint covered above.

| Method | Path | Auth scope | Request | Response | Module |
|---|---|---|---|---|---|
| GET | `/v1/discovery/occupations/recommended` | public | optional `category`, `domain`, `for_skill_id` | 200 `OccupationList` — editorial picks + simple "occupations including this skill" if `for_skill_id` given | catalog |
| GET | `/v1/discovery/personas/featured` | public | optional `parent_occupation_id` | 200 `PersonaList` — editorial picks scoped to the occupation if given | catalog |

Reuses `editorial_picks` (existing) — a new `slot` value
(`occupations_home`, `personas_for_<occupation_id>`) is recognized. No
schema change.

### `GET /v1/skills` extension

Add `kind` filter to the existing search endpoint:

- `GET /v1/skills?kind=skill` (default — preserves current behavior)
- `GET /v1/skills?kind=occupation` (equivalent to `/v1/occupations`,
  kept for power-users)
- `GET /v1/skills?kind=persona` (rare; tools)

The marketplace home grid stays `?kind=skill` to keep the existing
"discover individual skills" experience intact. Occupations get their
own rail above the skill grid (UX detail; not API surface).

---

## 6. Webhooks (creator-facing)

`shared/api-conventions.md` already enumerates webhook events on
skills. Add three:

| Event | Trigger | Payload (top-level) |
|---|---|---|
| `occupation.published` | a new SkillVersion released on a `kind=occupation` skill | `{ skill_id, version, content_hash, vault_build_id, member_count }` |
| `persona.published` | same for `kind=persona` | `{ skill_id, version, content_hash, vault_build_id, neuron_count, parent_occupation_id }` |
| `persona.composed_into_vault` | a buyer composed this persona into a vault download | `{ persona_skill_id, persona_license_id, occupation_skill_id, buyer_id_hash, composed_at }` — useful for creators tracking "real usage" of their persona |

Webhook delivery (HMAC, retries) is unchanged.

---

## Audit log additions

New action codes (target_type / action):
- `occupation` / `created`, `updated`, `members_set`, `build_queued`, `build_succeeded`, `build_failed`, `published`, `yanked`
- `persona` / `created`, `updated`, `neuron_added`, `neuron_removed`, `build_queued`, `build_succeeded`, `build_failed`, `published`, `yanked`
- `capture_session` / `created`, `extracted`, `finalized`, `abandoned`, `attachment_added`
- `license` / `vault_downloaded` (new — same target_type as the existing `downloaded`)
- `vault_build` / `composed`

Existing `audit_log` schema accommodates this without changes (action
is `text`, metadata is `jsonb`).

---

## Error code namespace additions

All new codes follow the existing dotted-namespace convention
(`shared/api-conventions.md` §Error format):

- `occupation.invalid_member_kind` — tried to add a non-`skill` row to
  `occupation_skills`.
- `occupation.empty_membership` — tried to build with zero members.
- `occupation.domain_unknown` — `domain` not in occupation's `domains[]`.
- `persona.requires_parent_occupation` — checkout gating.
- `persona.parent_occupation_invalid` — non-occupation skill passed as parent.
- `persona.published_lock` — tried to change `slug` or `parent_occupation_id` after publish.
- `persona.no_neurons` — publish with zero neurons.
- `capture.draft_not_ready` — finalize called before extract finished.
- `capture.pii_blocked` — PII flags unresolved at finalize time.
- `capture.quota_exceeded` — monthly capture-extraction quota exceeded.
- `vault_build.in_progress` — buyer requested download while build still running.
- `vault.compose_unentitled` — `composition_role` mismatch.
- `vault.persona_drift` — composed persona links unresolved against
  current occupation build (warning only — surfaces in
  `manifest.warnings[]`; not an error).

---

## OpenAPI generation

Per `shared/api-conventions.md`, all new routes set `tags`, `summary`,
`response_model`, and `responses=error_responses(...)`. Tags:
`occupations`, `personas`, `capture`, `vault`. Generated TS client
regenerates via `pnpm codegen` and the frontend imports `OccupationRead`,
`PersonaRead`, `CaptureSessionRead`, `VaultManifest`, etc.

---

## What we explicitly did NOT add

- A new auth scope. Existing capability checks (`require_creator`,
  `current_active_user`) are sufficient.
- A new checkout endpoint. Personas and occupations sell through
  `/v1/checkout/sessions` with the new `kind` filter and gating logic.
- A new pricing model. `free | one_time | subscription | freemium` are
  the only options for occupations and personas, same as everything
  else. Persona-stacked-pricing UX is a Phase-2 concern.
- A new license source. Buying an occupation creates a `one_time` (or
  `subscription`/`free`) license exactly like a skill purchase; the
  new `composition_role` column on `licenses` is what makes the row
  semantically an "occupation license" vs. "persona license".

---
