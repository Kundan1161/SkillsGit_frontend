# 01 — Data Model Deltas

**Owner:** Architect
**Status:** Proposed
**Reads:** `prompts/02-data-model-core.md`, existing `apps/api/src/*/models.py`,
all five Alembic migrations.
**Cross-refs:** `team/decisions.md` ADR-004 through ADR-013.

This file enumerates every new table and every column added to an
existing table. Conventions match the existing codebase:

- UUID v7 PKs (`uuid7()` helper from `src/core/db.py`).
- Money in cents (Integer).
- Timestamps `timestamptz`, UTC.
- Soft-delete via `SoftDeleteMixin` where the row should never truly
  vanish (everything tied to billing or licensing).
- Enums implemented as Postgres `CREATE TYPE` with idempotent DO-block
  pattern (`0001_initial.py` is the canonical example).
- All new tables get `created_at` / `updated_at` via `TimestampMixin`
  unless explicitly noted.

Migration ordering proposal:

| Rev | Title | Depends on |
|---|---|---|
| 0006 | `occupations_and_kind` — `skills.kind` enum/column + `occupations` + `occupation_skills` + index updates | `0005_delivery_and_moderation` |
| 0007 | `personas_and_neurons` — `personas` + `persona_neurons` + `parent_occupation_id` enforcement | `0006_occupations_and_kind` |
| 0008 | `capture` — `capture_sessions` + `capture_attachments` | `0007_personas_and_neurons` |
| 0009 | `vault_builds_and_downloads` — `vault_builds` + `vault_downloads` + license join columns | `0008_capture` |
| 0010 | `categories_seed_occupations_personas` — append `occupations` and `personas` to seeded categories | `0009_vault_builds_and_downloads` |

Each section below contains: (a) table definition, (b) indexes, (c) FK
diagram, (d) justification.

---

## Migration 0006 — `occupations_and_kind`

### `skills` — new column `kind`

| col | type | notes |
|---|---|---|
| kind | enum `skill_kind`(`skill`,`occupation`,`persona`,`memory_neuron`) | non-null, default `skill`; backfills existing 456 rows to `skill`; required for new product types |

Backfill: `UPDATE skills SET kind='skill' WHERE kind IS NULL;` then
`ALTER COLUMN kind SET NOT NULL;`. The existing publish_curated.py
continues to default to `skill` via DB default.

Justification: ADR-004. Discriminator column avoids fragmenting
pricing/licensing/delivery code paths.

### New table `occupations`

| col | type | notes |
|---|---|---|
| skill_id | uuid pk, fk → skills.id ON DELETE CASCADE | one-to-one with the parent skill row |
| summary_md | text | longer-form description; rendered on the occupation detail page above the skills grid |
| domains | text[] | top-level groupings used as folder names in the vault (e.g. `["ci-cd","observability","incident-response"]`) |
| persona_count | int | denormalized count of published personas with this as parent; updated by trigger or service |
| latest_build_id | uuid fk → vault_builds.id, nullable (FK added in 0009) | the canonical build the marketplace serves "preview" data from |
| recommended_persona_count | int | display hint on the detail page ("most users add 2 personas") |
| created_at, updated_at | timestamptz | TimestampMixin |

### New table `occupation_skills`

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| occupation_id | uuid fk → occupations.skill_id ON DELETE CASCADE | |
| member_skill_id | uuid fk → skills.id ON DELETE RESTRICT | references a `kind=skill` row in seed_data |
| domain | text | which `occupations.domains` bucket this member sits in; must be a member of the parent occupation's `domains` |
| sort_order | int | display + folder sort |
| role | enum `member_role`(`core`,`supporting`,`optional`) | "core" gets prominent placement in the vault index |
| pinned | bool | force into Featured rail on the occupation detail page |
| notes_md | text, nullable | curator notes (why this skill is in the bundle) |
| created_at, updated_at | timestamptz | |

Constraints:
- `UNIQUE(occupation_id, member_skill_id)` — no double inclusion.
- Application-level: `member_skill.kind = 'skill'` (cannot include
  another occupation or persona as a member). Enforced in the service
  with a clear error code.

Indexes:
- `(occupation_id, sort_order)` for fast vault build queries.
- `(member_skill_id)` for "which occupations include this skill?" lookups.

Justification: lets a single skill belong to multiple occupations
without duplication. `member_role` drives the vault's `00-index.md`
sectioning ("Core methodology", "Supporting practices").

### `skills` index addition

| index | columns | notes |
|---|---|---|
| `ix_skills_kind_status` | (`kind`, `status`) | required: every catalog/discovery query now filters by `kind`; the existing `ix_skills_status_category` is no longer sufficient on its own |

---

## Migration 0007 — `personas_and_neurons`

### New table `personas`

| col | type | notes |
|---|---|---|
| skill_id | uuid pk, fk → skills.id ON DELETE CASCADE | |
| parent_occupation_id | uuid fk → occupations.skill_id ON DELETE RESTRICT | **non-null**; deleting an occupation that still has personas is rejected at the service layer with a clear path forward |
| creator_intro_md | text | rendered above the persona's neuron list on the detail page |
| years_of_experience | int, nullable | optional credibility signal |
| specialization | text, nullable | one-line ("On-call lead for fintech with 200+ services") |
| neuron_count | int | denormalized count of finalized neurons |
| latest_build_id | uuid fk → vault_builds.id, nullable | |
| created_at, updated_at | timestamptz | |

Indexes:
- `(parent_occupation_id)` for "personas for this occupation" listing.

Justification: ADR-005. Persona is a thin envelope. All sales/billing
attributes live on the `skills` row.

### New table `persona_neurons`

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| persona_id | uuid fk → personas.skill_id ON DELETE CASCADE | |
| neuron_skill_id | uuid fk → skills.id ON DELETE RESTRICT | must be a row with `kind=memory_neuron` |
| sort_order | int | controls neuron order inside the persona's vault folder |
| section | text, nullable | optional sub-folder name under `personas/{handle}/`, e.g. `incidents`, `architecture-decisions`; defaults to flat layout |
| added_at | timestamptz | |

Constraints:
- `UNIQUE(persona_id, neuron_skill_id)`.
- App-level: `neuron_skill.creator_id = persona.creator_id` — a creator
  cannot insert another creator's neurons into their persona. Enforced
  at insert time.

Indexes:
- `(persona_id, sort_order)`.
- `(neuron_skill_id)`.

### `skill_versions` — no new columns (yet)
Considered adding `built_at` for vault-build status; rejected — the
build artifact lives in `vault_builds` and a successful build setting
`released_at` on `skill_versions` is sufficient signaling.

---

## Migration 0008 — `capture`

### New enum `capture_session_status`

`draft | extracting | draft_ready | finalizing | finalized | abandoned`

### New table `capture_sessions`

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| creator_id | uuid fk → users.id ON DELETE CASCADE | the practitioner doing the capture |
| persona_id | uuid fk → personas.skill_id ON DELETE CASCADE | which persona this neuron will land in if finalized |
| title | text | required, ≤140 chars |
| situation_md | text | as typed by the creator |
| decision_md | text | as typed |
| outcome_md | text | as typed |
| context_md | text | optional — extra notes |
| suggested_links_json | jsonb | AI-extracted suggestions: `[{target, relation, confidence, accepted: bool}]` |
| draft_md | text, nullable | the full skills.md the LLM produced (post-validation cleanup) |
| status | enum capture_session_status | non-null, default `draft` |
| llm_model | text | snapshot of which Claude variant produced `draft_md` |
| token_usage_json | jsonb | `{prompt, completion, total}` for billing/quota analytics |
| pii_flags_json | jsonb | array of `{type, span, severity}` from the PII scan |
| finalized_at | timestamptz, nullable | set on successful finalize |
| finalized_neuron_skill_id | uuid fk → skills.id, nullable | the resulting neuron row |
| abandoned_at | timestamptz, nullable | manual abandon by creator |
| created_at, updated_at | timestamptz | |

Indexes:
- `(creator_id, status, updated_at desc)` — creator's draft list.
- `(persona_id)` — show drafts inline on persona detail page.

Justification: ADR-015. Drafts never pollute `skills`. PII flags and
token usage live on the session so they don't pollute the published
neuron file.

### New table `capture_attachments`

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| capture_session_id | uuid fk → capture_sessions.id ON DELETE CASCADE | |
| storage_url | text | S3 key (existing `storage/` module) |
| filename | text | original filename (display only) |
| content_type | text | sniffed at upload |
| size_bytes | bigint | |
| sha256 | char(64) | content addressing; dedupes within a creator |
| created_at | timestamptz | |

On finalize, attachments are copied to the persona's permanent
`s3://attachments/personas/{persona_id}/{sha256}.{ext}` prefix and
referenced from the neuron's frontmatter (optional `attachments[]`
list — TBD: add to skills.md spec as a Phase-2 enhancement, NOT
in MVP; for MVP, attachments are referenced via standard markdown
image/link syntax inside the body).

---

## Migration 0009 — `vault_builds_and_downloads`

### New table `vault_builds`

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| skill_id | uuid fk → skills.id ON DELETE CASCADE | the parent occupation OR persona |
| skill_version_id | uuid fk → skill_versions.id ON DELETE CASCADE | exact version this build is for |
| content_hash | char(64) | sha256 over zipped bytes; unique per (skill_id, content_hash) |
| storage_url | text | `vaults/{skill_id}/{version}/{content_hash}.zip` |
| manifest_json | jsonb | full vault.json contents (mirror of the in-zip file for fast queries) |
| file_count | int | quick stat |
| total_bytes | bigint | quick stat |
| status | enum `vault_build_status`(`queued`,`running`,`succeeded`,`failed`) | |
| error | text, nullable | populated when status=failed |
| build_log_json | jsonb, nullable | structured log: warnings about unresolved links etc. |
| built_at | timestamptz, nullable | |
| built_by | uuid fk → users.id, nullable | creator who triggered |
| created_at, updated_at | timestamptz | |

Constraints:
- `UNIQUE(skill_id, content_hash)` — same content under same skill is
  the same build (idempotent rebuilds).
- `UNIQUE(skill_version_id) WHERE status='succeeded'` — at most one
  authoritative build per version.

Indexes:
- `(skill_id, status, built_at desc)` — "latest successful build for
  occupation X".

The composer reads `manifest_json` directly when assembling a buyer's
composed vault — no need to download and unzip the artifact for the
metadata it carries.

After this migration, alter `occupations` and `personas` to populate
the deferred FKs:

- `ALTER TABLE occupations ADD FOREIGN KEY (latest_build_id) REFERENCES
  vault_builds(id) ON DELETE SET NULL;`
- `ALTER TABLE personas ADD FOREIGN KEY (latest_build_id) REFERENCES
  vault_builds(id) ON DELETE SET NULL;`

### New table `vault_downloads`

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| occupation_license_id | uuid fk → licenses.id ON DELETE CASCADE | the buyer's occupation license that anchored the composition |
| buyer_id | uuid fk → users.id ON DELETE CASCADE | denormalized for fast "my downloads" queries |
| occupation_build_id | uuid fk → vault_builds.id ON DELETE RESTRICT | the build used |
| persona_build_ids | uuid[] | every persona vault_build merged in |
| persona_license_ids | uuid[] | the buyer's persona licenses in effect at compose time (snapshot) |
| composed_hash | char(64) | sha256 over the composed bytes (post-watermark) |
| storage_url | text | short-lived `delivery/vaults/{nonce}.zip` |
| user_agent_hash | text, nullable | |
| ip_hash | text, nullable | |
| created_at | timestamptz | |

Indexes:
- `(buyer_id, created_at desc)` — buyer's download history.
- `(occupation_license_id, created_at desc)` — license-side audit.

Justification: ADR-013. Per-buyer download trail without storing the
artifact long-term (lifecycle policy on `delivery/vaults/` prefix
deletes after 1 hour, same as existing single-file delivery).

### `licenses` — composition-related additions

| col | type | notes |
|---|---|---|
| composition_role | enum `license_composition_role`(`occupation`,`persona`,`standalone`) | non-null, default `standalone`; backfill: every existing license = `standalone` |
| target_occupation_skill_id | uuid fk → skills.id, nullable | for `composition_role=persona` licenses, the parent occupation this persona is intended to compose into (snapshot of `personas.parent_occupation_id` at purchase time so a creator changing parents doesn't invalidate sold licenses) |

Backfill SQL:
```sql
UPDATE licenses SET composition_role='standalone' WHERE composition_role IS NULL;
ALTER TABLE licenses ALTER COLUMN composition_role SET NOT NULL;
```

Justification: ADR-002 + ADR-006. The composer query needs to ask "give
me this buyer's licenses where composition_role='persona' AND
target_occupation_skill_id = X". The snapshot column protects against
creator-side reparenting (which we may allow Phase 2).

Indexes:
- `(buyer_id, target_occupation_skill_id, status)` — primary composer
  query.
- Existing `(buyer_id, skill_id, status)` retained.

---

## Migration 0010 — categories seed update

Append two rows to `categories`:

| slug | name | description | parent_slug | display_order |
|---|---|---|---|---|
| occupations | Occupations | Job-role playbooks built from curated skill bundles. | NULL | 50 |
| personas | Personas | Practitioner overlays — recorded situations layered onto an occupation. | NULL | 51 |

Reuse the existing seed pattern from `0002_seed_categories.py` —
idempotent INSERT … ON CONFLICT DO NOTHING.

Why a new category? Browse pages can filter `category='occupations'`
without needing to know about the `kind` discriminator (which is a
data-modeling concept the marketplace UI shouldn't surface as a top
nav). The `kind` column remains the authoritative source for
behavioral branching; the category is a discoverability concession.

---

## Summary FK diagram

```
                                  ┌──────────────┐
                                  │   skills     │  (kind column added)
                                  │              │
                                  └──┬───────────┘
                                     │
            ┌────────────────────────┼─────────────────────────┐
            │                        │                         │
            ▼                        ▼                         ▼
  ┌─────────────┐         ┌──────────────────┐        ┌──────────────────┐
  │ occupations │         │     personas     │        │  (kind=memory_   │
  │  (1:1 with  │         │   (1:1 with      │        │    neuron skills)│
  │   skills)   │         │    skills,       │        │   no side table  │
  └──────┬──────┘         │    parent_occu-  │        │   needed         │
         │                │    pation_id ─┐  │        │                  │
         │                └──────┬───────┘   │        └────────┬─────────┘
         │                       │           │                 │
         ▼                       ▼           │                 │
  ┌─────────────────────┐  ┌──────────────┐  │                 │
  │ occupation_skills   │  │persona_neurons│ │                 │
  │ (occupation_id,     │  │(persona_id,  │  │                 │
  │  member_skill_id,   │  │ neuron_skill │◄─┼─────────────────┘
  │  domain, role)      │  │ _id, section)│  │
  └─────────────────────┘  └──────────────┘  │
                                             │
        ┌────────────────────────────────────┘
        │ FK parent_occupation_id
        │ (must point to a kind=occupation row)
        ▼
  (occupations.skill_id)

                              ┌──────────────────┐
                              │ vault_builds     │  (per skill_version)
                              │ (skill_id,       │
                              │  skill_version_  │
                              │  id, content_hash)│
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │ vault_downloads  │
                              │ (occupation_     │
                              │   license_id,    │
                              │  buyer_id,       │
                              │  occupation_     │
                              │   build_id,      │
                              │  persona_build_  │
                              │   ids[])         │
                              └──────────────────┘

  ┌──────────────────┐           ┌──────────────────┐
  │ capture_sessions │  ────►    │ capture_         │
  │ (creator_id,     │           │  attachments     │
  │  persona_id,     │           │ (capture_session │
  │  draft_md, etc.) │           │   _id, sha256)   │
  └──────────────────┘           └──────────────────┘
            │
            │ on finalize
            ▼
  (creates a kind=memory_neuron skill + version + persona_neurons row)

  ┌──────────────────┐
  │     licenses     │  (composition_role + target_occupation_skill_id added)
  └──────────────────┘
```

---

## Existing tables NOT touched

For reference — verifying no scope creep:

- `users` — unchanged.
- `creator_profiles` — unchanged.
- `categories` — only seed rows added (no schema change).
- `skill_versions` — unchanged structurally.
- `orders`, `order_items` — unchanged.
- `subscriptions`, `subscription_prices` — unchanged.
- `payouts` — unchanged.
- `reviews` — unchanged (a buyer can review an occupation or persona
  with the existing constraint).
- `editorial_picks`, `search_alerts` — unchanged.
- `audit_log` — unchanged structurally; new action codes documented
  in §02.
- `webhook_events`, `moderation_actions` — unchanged.
- `api_tokens` — unchanged.

---

## Why no graph DB / vector DB

ADR-012 is the long-form. Short version: the largest occupation MVP
(~30 skills × ≤10 personas × ≤50 neurons each) yields ≤1500 nodes and
maybe 5000 edges. Postgres handles this with a single indexed join
table. Graph view is computed by Obsidian on the client. Semantic
search inside the vault is a buyer-side concern. Add infra only when
a feature demands it.

---

## Index review checklist (for migration author)

When implementing 0006–0010, verify each of the following queries has a
covering index. If not, add one:

| Query | Required index |
|---|---|
| "List occupations" | `ix_skills_kind_status` (0006) |
| "List personas for occupation X" | `ix_personas_parent_occupation_id` (0007) |
| "Skills in occupation X, sorted" | `(occupation_id, sort_order)` on `occupation_skills` (0006) |
| "Neurons in persona Y, sorted" | `(persona_id, sort_order)` on `persona_neurons` (0007) |
| "Latest build for skill_version Z" | `(skill_version_id) WHERE status='succeeded'` partial unique (0009) |
| "Buyer's persona licenses for occupation X" | `(buyer_id, target_occupation_skill_id, status)` on `licenses` (0009) |
| "Creator's capture drafts" | `(creator_id, status, updated_at desc)` on `capture_sessions` (0008) |
| "Find skill membership of a member skill" | `(member_skill_id)` on `occupation_skills` (0006) |

---

## TBD items routed elsewhere

- **TBD:** Persona pricing tiers + payout split when bundled — Q-1 in
  `06-open-questions.md`.
- **TBD:** Capture LLM key model (platform vs BYOK) — locked to
  platform-key MVP in ADR-008, BYOK schema deferred.
- **TBD:** Multi-occupation persona (a persona overlaying more than one
  occupation) — out of scope MVP. If we want it later, change
  `personas.parent_occupation_id` to a join table
  `persona_parent_occupations`.
- **TBD:** Whether to allow buyers to publish "private" personas (their
  own captures, never sold). Would need a `is_private` flag on
  `personas` and a checkout-skip path. Defer — Q-3 in
  `06-open-questions.md`.

---
