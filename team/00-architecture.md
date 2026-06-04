# 00 — System Architecture

**Owner:** Architect
**Status:** Proposed (awaits user approval per ADR-003)
**Reads:** `prompts/`, existing `apps/api/src/`, `team/decisions.md`
**Cross-refs:** every other `team/` file

---

## Summary

We layer two new product types — **Occupation** (a curated, graph-linked
bundle of existing skills) and **Persona** (a composable add-on of
practitioner-recorded "memory neurons") — onto the existing 456-skill
Skills Git marketplace **without forking pricing, licensing, delivery,
or webhooks**. Both new types are first-class kinds on the existing
`skills` row (ADR-004). Neurons are themselves skills with
`kind=memory_neuron` (ADR-005). Buyers download an **Obsidian-compatible
vault bundle** (ADR-001) composed at request time from the buyer's
license set (ADR-006). Vault builds are addressable, cacheable artifacts
(ADR-013). The killer feature — an agent answering with attribution
back to consulted neurons — is enabled by a `vault.json` manifest and
a trailing HTML-comment in every neuron file (ADR-010).

---

## Component diagram

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                              SKILLS GIT — Cycle-1 layout                        │
│                                                                                │
│  EXISTING modules (unchanged signature, possibly extended)                     │
│  ┌─────────────────────────────────────────────────────────────────────┐       │
│  │   auth   ▏  users   ▏  skills   ▏  catalog   ▏  billing   ▏ delivery│       │
│  │ (sessions, (creator   (Skill,    (categories,  (orders,   (license   │       │
│  │  tokens)    profiles)  Version,    discovery,   licenses,  resolution,│      │
│  │             ────────   validator,  search)      subs)      watermark, │      │
│  │                        parser)                              presign)  │      │
│  └──────┬─────────────────┬──────────┬──────────────┬──────────┬───────┘       │
│         │                 │          │              │          │               │
│         │ FK              │ FK       │ FK kind      │ FK       │ FK            │
│         ▼                 ▼          ▼              ▼          ▼               │
│  ┌─────────────────────────────────────────────────────────────────────┐       │
│  │                            NEW modules                              │       │
│  │                                                                     │       │
│  │  occupations  ─────┐                                                │       │
│  │  ┌──────────────┐  │   personas ──────┐    capture ────────┐       │       │
│  │  │ Occupation   │  │   ┌───────────┐  │    ┌──────────────┐│       │       │
│  │  │ row          │  │   │ Persona   │  │    │ CaptureSess  ││       │       │
│  │  │ (side table  │  │   │ row       │  │    │ (LLM extract,││       │       │
│  │  │  on skills)  │  │   │ + members │  │    │  PII scan,   ││       │       │
│  │  │              │  │   │ (neurons) │  │    │  draft_md)   ││       │       │
│  │  │ + occupation_│◄─┘   └─────┬─────┘  │    └──────┬───────┘│       │       │
│  │  │   skills join│           │ FK      │           │ on     │       │       │
│  │  │              │           ▼         │           │ finalize│      │       │
│  │  └──────┬───────┘    member neurons (kind=memory_neuron rows)      │       │
│  │         │                                                            │      │
│  │         │ build trigger                                              │      │
│  │         ▼                                                            │      │
│  │  ┌──────────────────────────────────────────┐  ┌──────────────────┐ │      │
│  │  │ vault-builder                            │  │ vault-composer   │ │      │
│  │  │  - lays out folder tree                  │  │ (delivery-side)  │ │      │
│  │  │  - resolves links[] to vault paths       │  │  - merges        │ │      │
│  │  │  - writes 00-index.md, vault.json        │  │    occupation +  │ │      │
│  │  │  - stamps attribution comment on each    │  │    N persona     │ │      │
│  │  │    skill / neuron                        │  │    builds        │ │      │
│  │  │  - zips, hashes, uploads to              │  │  - watermarks    │ │      │
│  │  │    s3://vaults/{skill}/{version}/        │  │  - presigns      │ │      │
│  │  │      {content_hash}.zip                  │  │  - records       │ │      │
│  │  │  - writes vault_builds row               │  │    vault_downloads│ │      │
│  │  └─────────────────────────────────────────┘  └──────────────────┘ │      │
│  └─────────────────────────────────────────────────────────────────────┘       │
│                                                                                │
│  Front-end (existing apps, new routes only)                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐       │
│  │  web-marketplace                            web-creator              │      │
│  │   /occupations/[handle/slug]                 /capture (new)          │      │
│  │   /personas/[handle/slug]                    /capture/[id]           │      │
│  │   /library — adds vault-aware badges          /personas (new)        │      │
│  │   /library/[id]/vault — download composed     /personas/[id]          │      │
│  │                                              /occupations (existing  │      │
│  │                                                user with creator role) │     │
│  └─────────────────────────────────────────────────────────────────────┘       │
│                                                                                │
│  CLI                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐       │
│  │  apps/api/scripts/build_devops_vault.py     (Curation, Cycle 1)     │      │
│  │  apps/api/scripts/demo_devops_agent.py      (Layer-C demo, ADR-014) │      │
│  └─────────────────────────────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────────────────────────┘
```

Arrow legend: `─►` = synchronous call; `FK` = database foreign key; modules
in the bottom block are **new**, modules in the top block are **existing
and used as-is**.

---

## How occupations relate to existing `Skill`

Decision: **`kind=occupation` on the existing `skills` table** (ADR-004),
with a side table `occupations(skill_id pk, summary, domains, ...)` for
occupation-specific metadata, and a join table `occupation_skills` for
the curated set of constituent skills.

Mapping table:

| Concern | Existing `Skill` (kind=skill) | Occupation (kind=occupation) |
|---|---|---|
| Listing | yes | yes — appears in catalog with `kind=occupation` filter |
| Pricing | per-skill | per-occupation (charged as a single product) |
| License | one per skill | one per occupation — entitles to the composed vault |
| Versions | semver per skill_versions | semver per occupation version (a "release" of the curated bundle) |
| Storage | one skills.md per version in S3 | one vault.zip per (occupation_version, build_hash) in S3 (see vault_builds) |
| Discoverability | category + tags + search | same machinery — `kind` is just another filter |
| Reviews / webhooks | full pipeline | full pipeline, free re-use |

The occupation row reuses **every existing piece of the platform**. The
only new state is the occupation→skills join + the vault build artifact.

Rejected alternative: a separate `occupations` root table. Would have
duplicated pricing, license, billing, audit-log, webhook wiring. ADR-004.

---

## How personas relate to occupations

Decision: persona is a separately listed and licensed product, **typed
to a parent occupation** via the new `parent_occupation_id` field on
`personas(skill_id pk)`. Buyer holds 1 license per occupation + N
licenses per persona. Composition is a delivery-time function.

Specifics:

- **Foreign key:** `personas.parent_occupation_id` references
  `occupations.skill_id`. A persona without a parent occupation cannot
  be published.
- **License stacking:** existing `licenses` rows. Buyer's vault for
  occupation O is composed from `{license on O} + {all active licenses
  on personas P where P.parent_occupation_id = O}`.
- **Composition at download:** `vault_composer.compose(buyer_id,
  occupation_skill_id)` queries the buyer's license set, fetches the
  entitled `vault_builds` for the occupation and each persona, merges
  the folder trees, rewrites `00-index.md` and `vault.json`, and writes
  the composed `.zip`. Cache key in Redis:
  `composed:{buyer_id}:{occupation_skill_id}:{build_hash_set_sha}`,
  TTL 24h. Cache invalidates automatically when any input hash changes.
- **Catalog enforcement:** the persona checkout endpoint refuses
  purchase if the buyer does not already hold a license on the parent
  occupation (or instead bundles the occupation into the same checkout
  as a Phase-2 enhancement; for MVP we require sequential purchase).
- **Persona standalone preview:** a persona detail page surfaces the
  parent occupation and offers "Get the base occupation + this persona"
  as a guided two-step checkout. For MVP this is two clicks; bundled
  one-step checkout is Phase 2.
- **Stripe Connect:** unchanged — persona purchase routes
  `transfer_data.destination` to the persona's creator; occupation
  purchase routes to the occupation's creator. No multi-creator split
  within a single transaction.

---

## Data flow — Scenario 1: Curator builds the DevOps occupation vault

```
Curator (Backend role + Curation role, Cycle 1)
  │
  │ 1. write apps/api/scripts/build_devops_vault.py
  │    that selects 30 DevOps skill slugs from seed_data/synth/
  │    (cherry-picked from the list in 05-mvp-plan.md §Layer A)
  │
  ▼
SCRIPT runs (`uv run python -m scripts.build_devops_vault`)
  │
  │ 2. ensure @skillsgit-curated user (already exists from publish_curated.py)
  │ 3. create a Skill row with kind=occupation, slug=ai-devops-engineer,
  │    name="AI DevOps Engineer", status=draft initially
  │ 4. create an Occupation side row: domains=["ci-cd","observability",
  │    "infra-as-code","incident-response","platform"], summary_md=...
  │ 5. for each cherry-picked skill, insert occupation_skills(
  │       occupation_id, skill_id, domain, sort_order, role)
  │    role ∈ {core, supporting, optional}
  │ 6. write graph edges: links[] on the occupation's skills are derived
  │    from a small YAML recipe ("incident-response-loop applies to
  │    observability-dashboards", etc.) — see Curation deliverable
  │    cross-link recipe.
  │ 7. POST /v1/occupations/{id}/build  (triggers Arq job)
  │
  ▼
ARQ JOB: vault_builder.build_occupation(occupation_id, version="1.0.0")
  │
  │ 8. fetch all member skills + their latest versions
  │ 9. lay out folder tree:
  │       base/
  │         ci-cd/
  │           devops-ci-pipeline-architect.md
  │           devops-gha-workflow-optimizer.md
  │         observability/...
  │         ...
  │       attachments/   (empty for occupation; populated by persona neurons)
  │       README.md
  │       00-index.md
  │       vault.json
  │
  │ 10. for each member skill: rewrite frontmatter — strip
  │     marketplace pricing block (irrelevant inside the vault), inject
  │     vault_path, set kind=skill, append <!-- skg-attribution: ... --> footer
  │ 11. resolve links[] across member skills, write Linked notes footers
  │ 12. write 00-index.md (grouped by domain), README.md (occupation
  │     summary + how to use)
  │ 13. write vault.json manifest (files[], attribution_index, build info)
  │ 14. compute content_hash over zipped bytes
  │ 15. upload to s3://vaults/{occupation_skill_id}/1.0.0/{content_hash}.zip
  │ 16. insert vault_builds row, set occupations.latest_build_id
  │ 17. set skill_versions.released_at  (now visible to buyers)
  │
  ▼
Marketplace: occupation visible at /occupations/skillsgit-curated/ai-devops-engineer
```

---

## Data flow — Scenario 2: Practitioner publishes a persona overlay

```
Creator clicks "Become a persona author" in web-creator
  │
  │ 1. UI: /personas/new — form with name, parent occupation picker,
  │    pricing (defaults to free for MVP), description
  │
  ▼
POST /v1/personas
  │
  │ 2. server creates Skill row (kind=persona, status=draft) + persona
  │    side row (parent_occupation_id, etc.)
  │ 3. enforces: parent occupation exists and is published
  │
  ▼
Creator clicks "Capture a situation" (separate flow — Scenario 3)
   ... after several captures and edits, they have N draft neurons ...
  │
  ▼
Creator clicks "Publish persona" in /personas/[id]
  │
  │ 4. validation: persona must have ≥1 finalized neuron; each neuron
  │    valid against validate_file(); links resolvable (warn if not)
  │ 5. server creates skill_versions row at 1.0.0
  │ 6. POST internal: vault_builder.build_persona(persona_id, "1.0.0")
  │
  ▼
ARQ JOB: vault_builder.build_persona
  │
  │ 7. fetch persona's member neurons (persona_neurons join)
  │ 8. lay out: personas/{handle}/neurons/<neuron-slug>.md  +
  │    personas/{handle}/README.md (creator bio, persona description)
  │ 9. for each neuron, inject vault_path, attribution footer,
  │    Linked notes footer (links[] resolved relative to the *parent
  │    occupation* expected at composition time — see §Composition)
  │ 10. write a partial vault.json (persona slice) — composer merges
  │     it with the occupation slice at delivery
  │ 11. zip, hash, upload to s3://vaults/{persona_skill_id}/1.0.0/{hash}.zip
  │ 12. insert vault_builds row
  │ 13. set skill_versions.released_at; persona now visible at
  │     /personas/{handle}/{slug} and listed on the parent occupation page
  │
  ▼
Marketplace: persona purchasable
```

---

## Data flow — Scenario 3: Practitioner records a situation in capture UX

```
Creator visits /capture (web-creator)
  │
  │ 1. UI shows: pick persona (existing or "new"), pick parent occupation
  │    if persona is new, then capture form with fields:
  │       • Title
  │       • Situation (what happened, when, who)
  │       • Decision (what you chose and why)
  │       • Outcome (what actually happened)
  │       • Linked base-occupation neurons (typeahead over occupation's
  │         skill slugs)
  │       • Optional attachments (drag-and-drop)
  │
  ▼
POST /v1/capture/sessions  { persona_id, title, fields, attachments[] }
  │
  │ 2. server creates capture_sessions row (status=draft), stores
  │    attachment files in s3://attachments/ via existing storage/
  │ 3. server enqueues Arq job: capture.extract_neuron(session_id)
  │
  ▼
ARQ JOB: capture.extract_neuron
  │
  │ 4. constructs a prompt: "Given this situation/decision/outcome,
  │    produce a skills.md file with kind=memory_neuron. Suggest 2-5
  │    `links[]` entries against the parent occupation's skill slug
  │    list (provided)."
  │ 5. calls Claude (ADR-008) via apps/api/src/capture/llm.py
  │ 6. parses the model's output, validates with validate_file()
  │ 7. PII scan over the draft (existing SECRET_PATTERNS plus a small
  │    `pii_patterns` extension — email, phone, IP — see 04-capture-flow.md)
  │ 8. writes capture_sessions.draft_md, status=draft_ready
  │
  ▼
Creator reviews in /capture/{id}
  │
  │ 9. UI shows: rendered draft, diff against the form input, suggested
  │    links with confirm/edit/remove controls, PII flags
  │ 10. Creator edits prose, accepts/edits links, resolves PII flags
  │
  ▼
POST /v1/capture/sessions/{id}/finalize
  │
  │ 11. server runs validate_file() one more time on the edited draft_md
  │ 12. creates Skill row (kind=memory_neuron, status=draft, unlisted),
  │     SkillVersion row at 1.0.0, persona_neurons join row
  │ 13. marks capture_sessions.finalized_at, finalized_neuron_skill_id
  │ 14. parent persona is NOT auto-built — creator triggers publish
  │     explicitly (Scenario 2 step 4 onward)
```

---

## Data flow — Scenario 4: Buyer purchases occupation + persona → receives composed vault bundle

```
Buyer browses /occupations/skillsgit-curated/ai-devops-engineer
  │
  │ 1. detail page lists: base occupation $X, persona overlays
  │    (jane-devops, etc.), reviews, version history
  │
  ▼
Buyer clicks "Buy occupation" → existing checkout flow
  │
  │ 2. POST /v1/checkout/sessions {skill_id=occupation_id, ...}
  │ 3. Stripe Checkout → checkout.session.completed webhook
  │ 4. existing billing/service.py issues licenses{source=one_time,
  │    skill_id=occupation_id}
  │
  ▼
Buyer revisits page; "Owned" badge on occupation. Now clicks "Add Jane's persona".
  │
  │ 5. POST /v1/checkout/sessions {skill_id=persona_id, ...}
  │ 6. server validates buyer already holds active license on persona's
  │    parent occupation; rejects otherwise with 409
  │ 7. Stripe Checkout → webhook → licenses{source=one_time,
  │    skill_id=persona_id}
  │
  ▼
Buyer opens /library and sees both licenses
  │
  │ 8. library shows the occupation with a new "Vault" tab listing
  │    composed personas with active licenses
  │
  ▼
Buyer clicks "Download vault" on the occupation library row
  │
  ▼
GET /v1/licenses/{occupation_license_id}/vault
  │
  │ 9. vault_composer.compose(buyer_id, occupation_skill_id):
  │     a. fetch occupation's entitled vault_build (latest released
  │        within max_version)
  │     b. fetch every persona license owned by this buyer where
  │        persona.parent_occupation_id = occupation_skill_id, and
  │        their entitled vault_builds
  │     c. cache lookup: composed:{buyer_id}:{occ_id}:{build_hash_set_sha}
  │     d. cache miss → merge:
  │          - copy occupation build into a tempdir
  │          - for each persona, copy persona build's personas/{handle}/
  │            tree into the tempdir
  │          - regenerate 00-index.md (occupation index + persona indices)
  │          - regenerate vault.json (composed files[], attribution_index,
  │            personas[])
  │          - per-buyer watermark: append to every skills.md / neuron.md a
  │            second <!-- skg-license: {license_id_hash} buyer:{...} ts:... -->
  │            comment (reuses delivery/watermark.py)
  │          - zip
  │          - upload to s3://delivery/vaults/{nonce}.zip
  │          - record vault_downloads row
  │     e. presigned URL, TTL 60s — returned to buyer
  │
  │ 10. UI: "Downloading skillsgit-curated/ai-devops-engineer +
  │     jane-devops/incident-loop · v1.0.0 · 2.3 MB"
  │ 11. Audit log: license.vault_downloaded for each constituent license
```

---

## Data flow — Scenario 5: Buyer's agent loads vault → query → answers with attribution

```
Buyer (or a script) unpacks the vault.zip in their working dir
  │
  │ 1. Agent starts; loads vault.json (root)
  │     vault.json contains:
  │        - files[] with {vault_path, skill_id, version, kind, content_hash,
  │                       creator_handle, links[]}
  │        - attribution_index: {skill_id → vault_path}
  │        - personas[] (which personas were composed in)
  │
  ▼
Agent indexes neurons in-memory:
  │   for each file in vault.json.files:
  │     read file body (markdown), keep `## When to use` block + any
  │     `### Triggers` lines as the routing summary
  │
  ▼
User prompts agent: "My CI just started failing intermittently in the test stage,
  what should I look at first?"
  │
  ▼
Agent constructs LLM call:
  │   system prompt = base agent instructions + "Below are skill summaries
  │     from a curated AI DevOps Engineer vault. When you answer, cite
  │     each skill or neuron you actually used by its vault_path."
  │   context = top-K skill summaries (selected by simple keyword match
  │     against trigger_keywords[]/tags[] in MVP; semantic retrieval is
  │     post-MVP — see ADR-012)
  │   user prompt = the user's question
  │
  ▼
LLM returns:
  │   {
  │     "answer": "Start by reproducing locally with the exact dep
  │       versions… then check observability dashboards for…",
  │     "consulted": [
  │       "base/ci-cd/devops-ci-pipeline-architect.md",
  │       "personas/jane-devops/neurons/2024-08-flaky-tests.md",
  │       "base/observability/observability-dashboard-architect.md"
  │     ]
  │   }
  │
  ▼
Agent renders:
  │   <answer>
  │
  │   Consulted neurons:
  │     • base/ci-cd/devops-ci-pipeline-architect.md
  │         (skillsgit-curated, v1.0.0, kind=skill)
  │     • personas/jane-devops/neurons/2024-08-flaky-tests.md
  │         (jane-devops, v1.0.0, kind=memory_neuron, "Flaky tests caused
  │         by shared Redis container — fixed by per-suite redis_db_index")
  │     • base/observability/observability-dashboard-architect.md
  │         (skillsgit-curated, v1.0.0, kind=skill)
  │
  │   each line is looked up via vault.json.attribution_index for human details
```

This is the demo. ADR-014 puts this exact flow in
`apps/api/scripts/demo_devops_agent.py`.

---

## Open architectural notes

- **TBD:** Whether to put `vault_composer` in `delivery/` or its own new
  module `vault/`. Lean toward `vault/` since it owns its own queue,
  cache, and S3 prefix; `delivery/` keeps doing single-file presigned
  delivery for the 456 existing skills.
- **TBD:** Composition cache TTL. 24h is a reasonable starting point;
  may shorten if buyers complain about staleness after a persona update.
- **TBD:** Whether the persona purchase flow should bundle occupation
  purchase into a single Stripe Checkout for new buyers (Phase 2
  enhancement, surfaced in `06-open-questions.md` as Q-1).

---
