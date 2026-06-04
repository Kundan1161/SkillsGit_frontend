# Decisions — Architecture Decision Record (ADR) log

> Append-only. Supersede with a new ADR rather than rewriting an old one.
> One ADR per architectural choice that another role would otherwise have
> to re-derive. Format taken from `team/README.md`.

Index:

- [ADR-001 — Vault-bundle download is the only runtime in MVP](#adr-001--vault-bundle-download-is-the-only-runtime-in-mvp)
- [ADR-002 — Persona is a composable add-on to Occupation, with separate license + payout](#adr-002--persona-is-a-composable-add-on-to-occupation-with-separate-license--payout)
- [ADR-003 — Architect drafts the spec; user approves; then implementation agents spawn](#adr-003--architect-drafts-the-spec-user-approves-then-implementation-agents-spawn)
- [ADR-004 — Occupations and Personas are first-class skill kinds (discriminator on `skills`), not separate root entities](#adr-004--occupations-and-personas-are-first-class-skill-kinds-discriminator-on-skills-not-separate-root-entities)
- [ADR-005 — Memory neurons are skills.md files with `kind=memory_neuron`, addressable inside a persona vault](#adr-005--memory-neurons-are-skillsmd-files-with-kindmemory_neuron-addressable-inside-a-persona-vault)
- [ADR-006 — Vault composition happens at download time, in a deterministic builder script](#adr-006--vault-composition-happens-at-download-time-in-a-deterministic-builder-script)
- [ADR-007 — `[[wiki-links]]` are explicit in `links:` frontmatter, not auto-derived from body prose](#adr-007--wiki-links-are-explicit-in-links-frontmatter-not-auto-derived-from-body-prose)
- [ADR-008 — Capture LLM extraction uses platform-key Claude (metered) for MVP; BYOK is a Phase-2 opt-in](#adr-008--capture-llm-extraction-uses-platform-key-claude-metered-for-mvp-byok-is-a-phase-2-opt-in)
- [ADR-009 — Extend `prompts/shared/skills-md-spec.md` with optional `kind`, `links`, `parent_occupation_id`, `neuron`, `vault_path` fields](#adr-009--extend-promptssharedskills-md-specmd-with-optional-kind-links-parent_occupation_id-neuron-vault_path-fields)
- [ADR-010 — Attribution surfaces via stable trailing HTML comments in every neuron and a `vault.json` manifest](#adr-010--attribution-surfaces-via-stable-trailing-html-comments-in-every-neuron-and-a-vaultjson-manifest)
- [ADR-011 — Vault format: stock Obsidian, no plugins, ASCII-kebab filenames, `attachments/` folder, root `00-index.md`](#adr-011--vault-format-stock-obsidian-no-plugins-ascii-kebab-filenames-attachments-folder-root-00-indexmd)
- [ADR-012 — Reuse Postgres + Redis + S3 for all new state; no new infrastructure for MVP](#adr-012--reuse-postgres--redis--s3-for-all-new-state-no-new-infrastructure-for-mvp)
- [ADR-013 — Vault builds are addressable artifacts: `vault_builds(occupation_id, version, content_hash)` + immutable S3 object](#adr-013--vault-builds-are-addressable-artifacts-vault_buildsoccupation_id-version-content_hash--immutable-s3-object)
- [ADR-014 — Layer C demo ships as a CLI in `apps/api/scripts/`, not a new app — fastest path to "attributed answer"](#adr-014--layer-c-demo-ships-as-a-cli-in-appsapiscripts-not-a-new-app--fastest-path-to-attributed-answer)
- [ADR-015 — Capture neuron drafts live in `capture_sessions`, never in `skills` until the creator clicks Publish](#adr-015--capture-neuron-drafts-live-in-capture_sessions-never-in-skills-until-the-creator-clicks-publish)

---

## ADR-001 — Vault-bundle download is the only runtime in MVP
**Status:** Accepted (locked by user, 2026-05-26)
**Context:** Buyers consume occupations + personas via their AI agent. Two
plausible delivery modes exist: a downloadable Obsidian-compatible vault
that the buyer's agent reads from disk, or an MCP server we host that
streams skill content on demand. MCP would centralize updates and
licensing enforcement, but requires us to run inference-adjacent
infrastructure, design an auth model for arbitrary agent runtimes, and
ship per-customer endpoint provisioning.
**Decision:** Phase-1 (MVP) delivery is **vault bundle download only**.
The vault is a `.zip` of an Obsidian-compatible folder plus a `skills.md`
manifest. MCP is explicitly Phase 2 and the data model is designed so
the same `vault_builds` artifact can be served either way later.
**Consequences:**
- We extend the existing `delivery/` watermark+presigned-URL flow rather
  than build a new transport.
- Buyers' agents are responsible for reading the vault — we add a tiny
  reference loader in the Layer C demo CLI but don't ship a runtime.
- Updates are pulled, not pushed: a buyer's agent must re-download to
  receive a new build. The library page surfaces a "new build available"
  badge using the existing notification path.
- License enforcement remains the watermark-comment audit pattern; we
  cannot revoke a downloaded vault, only block subsequent downloads.

---

## ADR-002 — Persona is a composable add-on to Occupation, with separate license + payout
**Status:** Accepted (locked by user, 2026-05-26)
**Context:** A practitioner publishes a persona that overlays on a
specific occupation. The buyer needs both a base occupation and at
least one persona to get value, but should be able to mix-and-match
personas across the lifetime of the occupation purchase. Pricing must
flow correctly: the occupation creator gets paid for the occupation, the
persona creator gets paid for the persona, and the platform clips its
fee from each transaction independently.
**Decision:** Persona is a **separately listed and licensed product** —
its own `skills` row with `kind=persona`, its own pricing model, its own
Stripe Connect destination. The buyer holds **one license per
occupation** plus **N licenses per persona**. Vault composition happens
when a download is requested: the builder reads the buyer's license set,
fetches the base occupation vault build, merges in each persona's neuron
files, and writes a delivery-side bundle. The persona declares its
parent occupation in frontmatter (`parent_occupation_id`); the catalog
enforces that the buyer owns a license to that occupation before they
can purchase or compose the persona.
**Consequences:**
- Stripe Connect remains unchanged — each transaction routes the
  `transfer_data.destination` to the correct creator. No multi-creator
  splits per transaction; that complexity is avoided.
- A persona purchased without owning the parent occupation cannot be
  composed into a working vault. The marketplace gates the buy button.
- Composition is a pure function of license set + builds — no shared
  mutable state. Adding a persona later just produces a new composed
  bundle.
- Versioning: occupation and persona evolve independently. Persona
  `links:` must remain valid against the *current* occupation build at
  composition time; mismatches downgrade to "best-effort" with a
  surfaced warning in the manifest.

---

## ADR-003 — Architect drafts the spec; user approves; then implementation agents spawn
**Status:** Accepted (locked by user, 2026-05-26)
**Context:** This is greenfield work on a live codebase. Premature
implementation by parallel agents risks contradictory data-model
choices, duplicated tables, and silent breakage of existing 456-skill
publish flow.
**Decision:** The Architect (this role) writes the eight `team/` files
listed in `team/README.md` before any implementation agent runs.
`team/06-open-questions.md` is the **gating artifact** — the user must
answer the open questions before Cycle 1 begins. Once approved,
implementation agents are spawned with worktree isolation per role
(Backend, Frontend, Curation, QA/Docs) following `team/05-mvp-plan.md`.
**Consequences:**
- One cycle of designer-up-front cost (this work).
- All implementation roles share a single, internally-consistent spec.
- ADRs added by the Architect during spec writing (ADR-004 through
  ADR-015) carry the same weight as the user-locked decisions — they
  are open to challenge in Cycle 1 retros only.

---

## ADR-004 — Occupations and Personas are first-class skill kinds (discriminator on `skills`), not separate root entities
**Status:** Accepted (Architect, 2026-05-26)
**Context:** Two plausible models for new product types:
- (A) New top-level tables `occupations`, `personas`, each with their
  own listing/pricing/licensing/delivery stacks.
- (B) Reuse the existing `skills` row as the listing/billing record;
  add a discriminator column `kind` that takes values `skill` (default,
  the existing 456), `occupation`, `persona`, `memory_neuron`. Specific
  metadata for occupations and personas lives in narrow side tables.
**Decision:** Option B. Add `skills.kind` (enum, default `skill`). Add
side tables `occupations(skill_id pk → skills.id)` and
`personas(skill_id pk → skills.id)` for kind-specific metadata only.
The existing pricing, licensing, delivery, reviews, and webhooks
pipelines apply uniformly. New discovery surfaces (occupation rail,
persona browse on an occupation page) filter by `kind`.
**Consequences:**
- Zero re-implementation of pricing/checkout/licenses/delivery for the
  new product types — they ride existing rails.
- The marketplace UI must filter listings by `kind` so an "AI DevOps
  Engineer" occupation doesn't show up in the default "skills" grid
  unless requested.
- The 456 existing skills migrate by backfilling `kind='skill'` — a
  one-line column add with default value.
- A `kind` mismatch (e.g. trying to purchase a `memory_neuron` directly,
  or stacking an `occupation` on another occupation) must be enforced
  in the catalog service. Documented in §02 API surface.
- `vault_builds` is keyed on `skill_id` regardless of kind, so an
  occupation has builds and a persona has builds — composition merges
  them at delivery time.

---

## ADR-005 — Memory neurons are skills.md files with `kind=memory_neuron`, addressable inside a persona vault
**Status:** Accepted (Architect, 2026-05-26)
**Context:** A persona is composed of "memory neurons" — recorded
situations + decisions + outcomes. Two plausible models:
- (A) Neurons are rows in a `persona_neurons` table with their own
  fields (situation, decision, outcome, links). The persona vault is
  generated from rows at build time.
- (B) Neurons are themselves skills.md files (one per neuron), bundled
  into a parent persona by membership. The persona is a
  manifest-of-neurons, and the build step just copies the neuron files
  into the vault.
**Decision:** Option B. Each neuron is a `skills` row with
`kind=memory_neuron`, status=`published` or `draft`, but **not
discoverable in the marketplace** (`status=unlisted` semantics: present,
parented to a persona, never listed). Each neuron has its own
`skill_versions` row so the existing immutability + signing + watermark
pipeline applies. Persona-to-neuron membership is a join table
`persona_neurons(persona_id, neuron_skill_id, sort_order)`.
**Consequences:**
- Every neuron is validated by the existing `skills/validator.py` (plus
  new fields from ADR-009). No bespoke parser.
- Per-neuron versioning gives us granular updates: a creator fixing a
  typo in one situation doesn't rebuild the entire persona.
- A neuron-as-skill is **never sold standalone** — the catalog API
  hides `kind=memory_neuron` listings from the public storefront. They
  appear only inside their owning persona's vault and inside the
  creator's own dashboard.
- The persona's *price* is per-persona (per-package), not per-neuron.
  The persona row carries the pricing; neuron rows are free internal
  parts. We document this explicitly in capture UX.
- Naming collisions (two personas with a neuron named `incident-2024-08-pagerduty-outage`)
  are namespaced under the persona handle in the vault filesystem.

---

## ADR-006 — Vault composition happens at download time, in a deterministic builder script
**Status:** Accepted (Architect, 2026-05-26)
**Context:** A buyer with `1 occupation license + 3 persona licenses`
needs a single vault bundle. We can either pre-build every possible
combination (combinatorial explosion) or compose on demand.
**Decision:** Compose on demand at download time. The
`vault_composer` service reads the buyer's license set for a given
occupation, fetches the latest entitled `vault_builds` for each, merges
neuron folders into a single vault tree, regenerates `00-index.md` and
the `vault.json` manifest, watermarks each constituent neuron file,
zips, and returns a presigned URL. Composition is **deterministic**:
same license set + same build hashes ⇒ identical output bytes (modulo
the timestamped watermark).
**Consequences:**
- Composition latency: a few hundred milliseconds for typical sizes;
  acceptable for a click-to-download UX.
- We can cache the composed bundle per `(buyer_id, occupation_id,
  persona_id_set_hash, occupation_build_hash, persona_build_hashes)` in
  Redis + S3 for ≤24h. Cache invalidation is automatic on any input
  hash change.
- Removing or adding a persona to the buyer's library is a no-op on
  existing downloads — the next download produces the new composition.
- The composition algorithm is spelled out in `03-vault-generation.md` §
  Composition.

---

## ADR-007 — `[[wiki-links]]` are explicit in `links:` frontmatter, not auto-derived from body prose
**Status:** Accepted (Architect, 2026-05-26)
**Context:** Obsidian renders `[[target]]` links and builds the graph
view automatically. To make a vault graph useful, every neuron must
declare its outbound links. Options:
- (A) Author writes `[[wiki-links]]` directly in body markdown; the
  validator extracts them.
- (B) Author adds a `links: [...]` frontmatter list; the builder emits
  them as a stable "Linked notes" footer in the body.
- (C) AI extracts likely links from body prose at build time.
**Decision:** Option B (primary) with (A) as opt-in. The frontmatter
`links: [{target: "incident-response-loop", relation: "applies"}, ...]`
is the canonical source. The builder writes a `## Linked notes` section
at the end of each file with `- [[target]] — relation` lines so Obsidian
indexes them. Authors *can* also use inline `[[wiki-links]]` in prose
for natural reading, but the validator does not depend on them. AI
extraction (Option C) is a *suggestion* during capture (`04-capture-flow.md`),
never auto-confirmed.
**Consequences:**
- The graph is provably complete from frontmatter alone — no body
  parsing fragility.
- Renaming a target (changing a slug) breaks links unless we run a
  migration. We add a `link_check` step to the vault builder that
  warns when a `links[].target` doesn't resolve in the composed vault.
- The capture pipeline AI suggests `links[]` entries; the creator
  confirms each before publish.

---

## ADR-008 — Capture LLM extraction uses platform-key Claude (metered) for MVP; BYOK is a Phase-2 opt-in
**Status:** Accepted (Architect, 2026-05-26)
**Context:** Capture turns a freeform recorded situation into a draft
neuron skills.md. This needs an LLM call. Two routes:
- Platform-managed key (we pay, we meter, we charge).
- Bring-your-own-key (BYOK) — creator supplies their Anthropic key in
  settings, we pass through.
**Decision:** MVP uses a platform-managed Claude key (one of the
allowlisted models in `src/skills/models.py`, default `claude-sonnet-4-7`).
Each capture session debits a quota counter on the creator's account.
Free tier: 10 captures/month. Beyond that, the creator either upgrades
(future tier) or supplies BYOK. BYOK lands in Phase 2 with a
`creator_api_keys` table; defer.
**Consequences:**
- Capture works out of the box for every creator in the demo.
- We carry a (small) inference bill; tracked per-capture in
  `capture_sessions.token_usage_json`.
- The model used is recorded on each draft so re-runs can be deterministic.
- We need an env-var `CAPTURE_LLM_API_KEY` and a centralized client in
  `apps/api/src/capture/llm.py`.

---

## ADR-009 — Extend `prompts/shared/skills-md-spec.md` with optional `kind`, `links`, `parent_occupation_id`, `neuron`, `vault_path` fields
**Status:** Accepted (Architect, 2026-05-26)
**Context:** The skills.md spec is a contract. ADRs 004-007 require new
metadata. We must add it without breaking parsing of the existing 456
skill files, and without breaking the validator on absent fields.
**Decision:** Add five optional frontmatter fields. All default to
`null` / `[]`. The validator treats them as **opt-in**: a file without
any of them parses and validates exactly as before. The schema diff
below is the binding contract:

```yaml
# ── New optional fields (default semantics: skill-as-today) ──────────
kind: enum [skill, occupation, persona, memory_neuron]   # default: skill
links:                                                   # default: []
  - target: string                # slug or vault-relative path
    relation: string              # 'applies' | 'extends' | 'contradicts' | 'see-also' | 'recorded-instance-of'
    weight: float?                # 0..1, default 1.0 — informational
parent_occupation_id: string?     # required when kind=persona; absent otherwise
neuron:                           # required when kind=memory_neuron
  situation: string               # the trigger event (1-3 sentences)
  decision: string                # what was chosen and why
  outcome: string                 # what actually happened
  recorded_at: string             # ISO 8601 date
  confidence: float?              # 0..1, default 0.6 — creator's self-rating
vault_path: string?               # set by vault-builder; relative path within the vault.
                                  # creators leave blank — the builder writes it.
```

A new ADR will supersede this if we tighten any of the optionals to
required after MVP feedback. The Curation pipeline (`publish_curated.py`)
treats unset `kind` as `skill`, so the 456 existing files publish
unchanged.

**Consequences:**
- Backward compatibility preserved — `extra="forbid"` in the existing
  `SkillFrontmatter` Pydantic model widens to accept these five named
  fields; nothing else changes.
- The `vault_path` field is platform-authored at build time (same
  pattern as the `distribution` block). Creators MUST NOT set it.
- The `links[].target` field is a string the builder resolves at
  composition time. A target may be a sibling skill slug, a relative
  path, or an absolute vault path. The resolver tries each in order.
- `relation` is a small enum to keep graph semantics tractable. We can
  add more values later (non-breaking).

---

## ADR-010 — Attribution surfaces via stable trailing HTML comments in every neuron and a `vault.json` manifest
**Status:** Accepted (Architect, 2026-05-26)
**Context:** The "killer feature" is the agent returning "I used neuron
`<path>` for this answer." For that to work, the agent needs:
- A stable, machine-readable identifier on every neuron file.
- A way to look up source skill + version + creator from that identifier.
**Decision:** Every file the vault builder emits gets a trailing HTML
comment (already a watermark pattern in `delivery/watermark.py`):

```markdown
<!-- skg-attribution:
  vault_path: "personas/jane-devops/neurons/2024-08-pagerduty.md"
  skill_id: "01HX..."
  version: "1.0.0"
  kind: "memory_neuron"
  creator_handle: "jane-devops"
  links: ["base/incident-response-loop", "base/observability-dashboards"]
-->
```

A root `vault.json` manifest carries the same data in structured form
for fast loading: `{ vault_id, occupation: {...}, personas: [...],
files: [{vault_path, skill_id, version, kind, creator_handle, content_hash}],
attribution_index: { skill_id → vault_path }, build: { hash, built_at } }`.
The reference agent in the Layer C demo reads `vault.json` once, then
returns `vault_path` strings as attribution citations.

**Consequences:**
- The HTML comment is invisible to markdown renderers (already verified
  in the existing watermark pipeline).
- The agent author can choose to surface citations as filenames, full
  paths, or rich cards — they only need to map `vault_path` → human
  string.
- The manifest doubles as a checksum index: an agent that loaded the
  vault yesterday can diff `vault.json.files[*].content_hash` against
  today's to detect drift.

---

## ADR-011 — Vault format: stock Obsidian, no plugins, ASCII-kebab filenames, `attachments/` folder, root `00-index.md`
**Status:** Accepted (Architect, 2026-05-26)
**Context:** Vaults must open in stock Obsidian without prompting the
user to install plugins. Filenames must work cross-platform (Windows,
macOS, Linux) and in ZIP archives without surprises.
**Decision:** See `03-vault-generation.md` for the full spec. Core
rules:
- Root contains `README.md`, `00-index.md`, `vault.json`, then folders.
- One folder per domain (e.g. `base/`, `personas/<handle>/`,
  `attachments/`).
- All filenames are kebab-case, ASCII-only, max 80 chars before the
  `.md` extension.
- No leading numbers in folders (Obsidian sort order is alphanumeric,
  which sorts `10-foo` before `2-foo`; we don't fight it — domains are
  not numbered).
- Attachments (screenshots, configs, recordings) live under
  `attachments/` with content-addressed filenames (`<sha256-12>.<ext>`).
- No Obsidian-specific frontmatter (no `aliases:`, no `cssclass:`).
  Stock graph view and search work without configuration.
**Consequences:**
- Vaults open identically across platforms.
- The builder rejects any neuron filename that violates the
  kebab/ASCII rule (validator enhancement).
- We do not depend on Obsidian features that require Sync or paid
  plugins.

---

## ADR-012 — Reuse Postgres + Redis + S3 for all new state; no new infrastructure for MVP
**Status:** Accepted (Architect, 2026-05-26)
**Context:** Tempting to reach for a graph DB (Neo4j) for neuron links
or a vector DB for semantic search inside the vault.
**Decision:** None of that for MVP. Postgres holds all metadata
(occupations, personas, neurons, links, builds, downloads). Redis holds
the composition cache and capture-session draft state. S3 holds vault
build artifacts and attachments. Graph semantics are computed at vault
build time and rendered by Obsidian. Semantic search inside the vault
is an Obsidian-native feature (the user can install a plugin later if
they want). If a future feature legitimately needs a vector DB
(e.g. server-side semantic retrieval for an MCP delivery mode), it gets
its own ADR.
**Consequences:**
- No new infra to provision, monitor, back up, or pay for.
- We accept that "find me the neuron that contradicts this approach"
  is a non-feature in MVP — the graph view + manual search suffice.
- Postgres `links` queries on a small (≤500 neurons per vault) join
  table are trivially fast.

---

## ADR-013 — Vault builds are addressable artifacts: `vault_builds(occupation_id, version, content_hash)` + immutable S3 object
**Status:** Accepted (Architect, 2026-05-26)
**Context:** A vault is non-trivial to build. We want to:
- Trigger a build once per occupation version and reuse it across all
  buyers of that occupation version.
- Verify integrity of a delivered bundle (`content_hash`).
- Roll back a bad build by yanking the version.
**Decision:** A `vault_builds` row records `(skill_id, version,
content_hash, manifest_json, storage_url, built_at)`. The vault file
itself (the `.zip` of the vault folder) is immutable in S3 at
`vaults/{skill_id}/{version}/{content_hash}.zip`. The composer service
fetches the build for the entitled version, merges personas, and
produces a per-buyer bundle on the fly. The composed bundle for the
buyer is *also* hashed and recorded (`vault_downloads.composed_hash`)
for traceability.
**Consequences:**
- Build is async: when a creator publishes a new occupation version, an
  Arq job triggers a build. The version's `released_at` is set only
  after the build succeeds.
- A bad neuron published into a persona triggers a rebuild only of that
  persona, not the parent occupation.
- Buyers see a "preparing your vault" state for ≤30 seconds on first
  download if the build hasn't completed yet.

---

## ADR-014 — Layer C demo ships as a CLI in `apps/api/scripts/`, not a new app — fastest path to "attributed answer"
**Status:** Accepted (Architect, 2026-05-26)
**Context:** The end-of-cycle-1 demo must show a buyer's agent loading
the composed vault and returning an answer with neuron attribution.
Spending time on a web UI for the demo would steal from the core work.
**Decision:** Ship a CLI `apps/api/scripts/demo_devops_agent.py` that:
1. Accepts an occupation slug and 0+ persona slugs as arguments.
2. Calls the local API to fetch a composed vault bundle (using the
   curated creator's owner license).
3. Unpacks the vault, loads `vault.json`, builds a system-prompt-style
   context window with `## When to use` summaries from every neuron.
4. Sends the user's DevOps prompt + the context to Claude via the
   platform key.
5. Asks Claude to return both an answer and a list of consulted neuron
   slugs.
6. Renders the answer plus a "Consulted neurons" list with attribution
   pulled from `vault.json` (creator handle + version).
The Web frontend gets a stub "vault graph preview" later in Cycle 2.
**Consequences:**
- One file, one command, one observable output — perfect for demo.
- No frontend coupling for cycle 1.
- The CLI is also QA's smoke-test driver — run it nightly with a
  hard-coded prompt, snapshot the attribution list, alert on diff.

---

## ADR-015 — Capture neuron drafts live in `capture_sessions`, never in `skills` until the creator clicks Publish
**Status:** Accepted (Architect, 2026-05-26)
**Context:** A capture session may contain unfinished, half-confidential,
or hallucinated content. It must not pollute the `skills`/`skill_versions`
tables until the creator approves.
**Decision:** `capture_sessions` is a draft-only side table.
`capture_sessions.draft_md` holds the AI-extracted neuron skills.md
candidate. On finalize, the service:
1. Validates `draft_md` against `validate_file()`.
2. Creates a `skills` row (`kind=memory_neuron`, `status=draft`).
3. Creates a `skill_versions` row at `1.0.0` (or next semver).
4. Adds the neuron to the parent persona via `persona_neurons`.
5. Marks the capture session `finalized_at`.
Until that finalize call, the draft is private to the creator and never
appears in any catalog query.
**Consequences:**
- The 456-skill library is unaffected by half-baked captures.
- A creator can iterate on a draft as many times as they want (re-run
  AI, edit, etc.) without touching `skills`.
- PII/redaction enforcement runs at finalize time (see
  `04-capture-flow.md` §PII).

---

## ADR-016 — User gate approvals on `06-open-questions.md`
**Status:** Accepted (user, 2026-05-26)
**Context:** Six open questions in `06-open-questions.md` were the
gating artifact before Cycle 1 implementation could begin.
**Decision:** User approved all six architect recommendations as
written:
- Q-1 → A (persona price = free for MVP)
- Q-2 → A (platform-key Claude only for MVP capture)
- Q-3 → A (no private mode; every persona is at minimum a draft listing)
- Q-4 → C (ship seeded `@jane-devops-demo`; recruit real practitioner
  in parallel)
- Q-5 → A + existing `SECRET_PATTERNS` hard-block + the PII warn list
  from `04-capture-flow.md`
- Q-6 → B (ship `.obsidian/graph.json` color-by-tag preset for demo)
**Consequences:**
- Cycle 1 implementation agents may spawn immediately per `05-mvp-plan.md`.
- The deferred items (Q-1→B paid personas, Q-2→B BYOK, Q-3→B private
  mode, Q-6→C plugin) are flagged for the Cycle 2 retrospective.

---

## ADR-017 — Amend `prompts/shared/skills-md-spec.md` per ADR-009
**Status:** Accepted (user, 2026-05-26)
**Context:** ADR-009 specified 5 new optional frontmatter fields
(`kind`, `links`, `parent_occupation_id`, `neuron`, `vault_path`)
needed by occupations + personas + memory-neurons. The spec amendment
itself was gated per `team/README.md` §Governance.
**Decision:** User approved amending `prompts/shared/skills-md-spec.md`
to add the 5 optional fields. Backend's T-02 (validator extensions)
includes the spec edit as a sub-task. The 456 existing skills continue
to validate green (no fields are required for `kind=skill`).
**Consequences:**
- The canonical contract stays single-sourced.
- Backend ships the spec edit + validator + Pydantic→Zod regeneration
  as a coupled change so the contract never diverges from the runtime.

---

## ADR-018 — Layer-C demo CLI may call the Claude API as a reference loader
**Status:** Accepted (user, 2026-05-26)
**Context:** `prompts/00-vision.md` lines 64-66 say "not building a
general-purpose agent runtime." The MVP demo per ADR-014 calls Claude
to produce an answer with neuron attribution. Risk of contradicting the
vision constraint was flagged.
**Decision:** User approved. The demo CLI is framed as a **reference
loader / sample integration**, not a hosted runtime. Documentation
(per T-15) explicitly labels it as such. Buyers' own agents (Claude
Code, ChatGPT via MCP, custom) remain responsible for runtime;
skillsgit ships the vault and a reference example showing how to
consume it.
**Consequences:**
- T-13 (Layer-C demo CLI) implements the Anthropic SDK call directly.
- `docs/vault-format.md` (T-15) carries the "reference example, not
  a hosted runtime" framing prominently.
- Vision document needs no edit; the demo is a downstream example,
  not infrastructure.

---
