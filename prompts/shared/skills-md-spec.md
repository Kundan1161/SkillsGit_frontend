# shared — skills.md File Specification

**Phase:** 0 (foundation)
**Depends on:** `00-vision.md`
**Parallel-safe with:** all other shared prompts, all marketplace prompts (they reference it but don't author it)
**Status:** ready
**This is the single most-referenced spec in the repo. Treat it as a contract.**

---

## Purpose

`skills.md` is the canonical artifact of this platform. The marketplace lists, prices, licenses, and delivers it. The creator engine compiles its visual graph into it. Buyers drop it into their AI agents (Claude Code skills, OpenAI Assistants instructions, custom orchestrators, etc.).

The spec below extends Anthropic's published skill file conventions with the additional metadata our marketplace requires (pricing, categories, AI requirements, signing). A skill produced by the creator engine **MUST** be valid against this spec. The marketplace **MUST NOT** accept a publish that fails validation.

---

## File structure

A skills.md file is **YAML frontmatter** followed by a **markdown body**.

```markdown
---
# frontmatter (see schema below)
id: janedoe/dcf-valuation
version: 1.2.0
name: DCF Valuation Pro
description: Build a defensible discounted cash flow model from raw financials.
# ... see full schema
---

# Body — instructions for the AI agent

## When to use
Use this skill when the user provides a company's financials and asks for valuation.

## Steps
1. Extract historical revenue, EBITDA, capex, working capital from the input.
2. ...
```

---

## Frontmatter schema

Validated by `packages/skills-schema` (Pydantic on backend, Zod on frontend, generated from the same source).

```yaml
# ── Identity ─────────────────────────────────────────────────────────
id: string             # required. format: "{creator-handle}/{slug}". immutable.
version: string        # required. semver 2.0.0. immutable per published version.
name: string           # required. <= 80 chars. human title.
description: string    # required. <= 280 chars. one-line summary for cards & AI tool descriptions.

# ── Authorship ───────────────────────────────────────────────────────
authors:
  - name: string
    handle: string     # platform handle
    role: enum [author, contributor, maintainer]   # default: author

# ── Marketplace metadata ─────────────────────────────────────────────
category: string       # required. one of the seeded category slugs (see 02-data-model-core.md)
tags: [string]         # 0-10 tags
license_type: enum [free, one_time, subscription, freemium]   # required
pricing:
  one_time_cents: int?           # required iff license_type == one_time or freemium
  subscription_cents: int?       # required iff license_type == subscription or freemium
  currency: string                # default "USD", ISO 4217
support_included: bool            # default false; true only for subscription tier

# ── AI runtime requirements ──────────────────────────────────────────
ai:
  required_models: [string]      # required, non-empty. e.g. ["claude-opus-4-7", "claude-sonnet-4-6"]
  compatible_models: [string]    # optional. models known to work but not certified.
  min_context_tokens: int?       # optional. minimum context window the skill assumes.
  tools_required: [string]       # optional. e.g. ["web_search", "code_execution", "file_io"]
  tools_optional: [string]       # optional.
  estimated_tokens_per_invocation: int?   # optional. used for buyer cost previews.

# ── Discoverability ──────────────────────────────────────────────────
trigger_keywords: [string]       # 0-20. used by host agents to decide when to invoke
example_invocations: [string]    # 0-5. concrete user phrasings that should trigger this skill

# ── Inputs & outputs (declarative; for sandbox preview UX) ──────────
inputs:
  - name: string
    type: enum [text, file, url, json, number, choice]
    required: bool
    description: string
    choices: [string]?            # for type=choice

outputs:
  - name: string
    type: enum [text, markdown, json, file]
    description: string

# ── Versioning & changelog ──────────────────────────────────────────
changelog:                       # entries newest first
  - version: string
    date: string                 # YYYY-MM-DD
    notes: string                # markdown allowed
    breaking: bool?              # default false

# ── Distribution & integrity (set by marketplace at publish time) ───
# These fields are AUTHORED by the platform, not the creator.
# Creators leave them out; the publish pipeline injects them and re-signs the file.
distribution:
  content_hash: string           # sha256 hex of body bytes
  signed_at: string              # ISO 8601 UTC
  signed_by: string              # "marketplace" or creator key id
  signature: string              # base64

# ── Optional kinds, links, neurons (ADR-009, added 2026-05-26) ──────
# All five fields below are optional. Existing files without any of
# them validate exactly as before. See "Optional fields" section below.
kind: enum [skill, occupation, persona, memory_neuron]   # optional, default: skill
links:                                                   # optional, default: []
  - target: string               # slug or vault-relative path
    relation: enum [applies, extends, contradicts, see-also, recorded-instance-of]   # default: see-also
    weight: float?               # 0..1, optional — informational
parent_occupation_id: string?    # optional; REQUIRED when kind=persona or kind=memory_neuron
neuron:                          # optional; REQUIRED when kind=memory_neuron
  situation: string              # the trigger event
  decision: string               # what was chosen and why
  outcome: string                # what actually happened
  recorded_at: string?           # ISO 8601 date
  confidence: float?             # 0..1, default 0.6 — creator's self-rating
  context: string?               # optional extra notes
vault_path: string?              # optional, SERVER-SET — creators MUST NOT supply this.
                                 # The vault builder writes it during composition.
---
```

### Validation rules

- `id` matches `^[a-z0-9-]+/[a-z0-9-]+$`. The creator handle in `id` MUST equal `creator_profiles.handle`.
- `version` matches semver 2.0.0 (`^\d+\.\d+\.\d+(?:-[\w.]+)?$`).
- `description` is exactly one line, no embedded newlines.
- `pricing.one_time_cents` and `pricing.subscription_cents` are positive integers when present.
- For `license_type=freemium`, exactly one of `one_time_cents`/`subscription_cents` must be set (the "upgrade target"); the free version is a separate skill row that references this one via `freemium_paired_with` (see `02-data-model-core.md` extension in `marketplace/03-pricing-and-checkout.md`).
- `ai.required_models[*]` must be a known model id (see `apps/api/src/skills/models.py` for the allowlist; cover at minimum Claude Opus/Sonnet/Haiku 4.5+, GPT-4o/4.1, Gemini 1.5+). Reject unknown ids with a clear error.
- Trigger keywords and example invocations are case-insensitive and trimmed.
- `vault_path` MUST NOT be present in a creator-submitted file. The validator rejects with `frontmatter.vault_path: server_assigned`.
- When `kind=memory_neuron`, the `neuron` block MUST be present (with `situation`, `decision`, `outcome`). Missing → `frontmatter.neuron: required_for_memory_neuron`.
- When `kind=memory_neuron`, `parent_occupation_id` MUST be set. Missing → `frontmatter.parent_occupation_id: required_for_memory_neuron`.
- When `kind=persona`, `parent_occupation_id` MUST be set. Missing → `frontmatter.parent_occupation_id: required_for_persona`.

### Optional fields — kinds, links, neurons

Added per ADR-009 (and gated by ADR-017). Every field below is optional; a file that omits all five validates exactly as it did before this section landed.

**`kind`** — discriminator. One of `skill` (default), `occupation`, `persona`, `memory_neuron`. Drives downstream behaviour: the marketplace listing surface, the vault composer, and the persona/neuron pipelines. Files with no `kind` field continue to be `skill`. Example:

```yaml
kind: occupation
```

**`links[]`** — explicit outbound `[[wiki-link]]` declarations for the vault graph. ADR-007 makes this list the authoritative source (not body-prose extraction). Each entry has:

- `target` (required, string): a slug, a sibling vault-relative path, or an absolute vault path. The vault builder resolves it at composition time.
- `relation` (optional, enum): one of `applies | extends | contradicts | see-also | recorded-instance-of`. Defaults to `see-also`.
- `weight` (optional, float 0..1): informational only — the builder does not currently differentiate weighted edges, but the field is reserved.

Example:

```yaml
links:
  - target: base/incident-response-loop
    relation: applies
  - target: base/observability-dashboards
    relation: extends
    weight: 0.8
```

**`parent_occupation_id`** — required when `kind=persona` or `kind=memory_neuron`; absent otherwise. Identifies the occupation a persona overlays (or the neuron's parent persona's parent occupation). The value can be a slug (`creator-handle/occupation-slug`) or a UUID; the catalog service resolves it.

```yaml
kind: persona
parent_occupation_id: jane-devops/ai-devops-engineer
```

**`neuron`** — required when `kind=memory_neuron`. Captures a single recorded situation. Fields:

- `situation` (required, string): the trigger event in 1-3 sentences.
- `decision` (required, string): what was chosen and why.
- `outcome` (required, string): what actually happened.
- `recorded_at` (optional, string): ISO 8601 date the situation occurred.
- `confidence` (optional, float 0..1): creator's self-rating of how reliably this generalises. Defaults to `0.6`.
- `context` (optional, string): extra freeform notes.

Example:

```yaml
kind: memory_neuron
parent_occupation_id: jane-devops/ai-devops-engineer
neuron:
  situation: |
    Two days after upgrading Redis 6→7 across CI, the nightly suite
    started failing 1-in-12 runs on the payments integration test.
  decision: |
    Pinned the Redis client library and reverted the tcp-keepalive
    change the upgrade had reset to default.
  outcome: |
    Failure rate dropped to 0/200 over the next week.
  recorded_at: "2024-08-23"
  confidence: 0.9
```

**`vault_path`** — set by the vault builder during composition. Creators MUST NOT include this field; submitting it is a validation error (`server_assigned`). Reference loaders and downstream agents read it from the manifest and the `<!-- skg-attribution: ... -->` trailing comment.

### Compatibility

Existing files without these fields continue to validate. The default `kind` is `skill`. The Curation pipeline (`publish_curated.py`) treats unset `kind` as `skill`, so the 456-skill library publishes unchanged.

---

## Body conventions

The body is markdown that will be read by an AI agent at runtime. The marketplace renders a subset of it (sections like `## When to use`, `## Examples`) in the listing UI.

### Required sections (validator enforces)

- `## When to use` — describes the trigger conditions for the agent.
- `## How to apply` — step-by-step instructions.

### Recommended sections

- `## Inputs` — what the skill needs from the user/agent.
- `## Outputs` — what it produces.
- `## Examples` — at least one worked example with placeholder data.
- `## Limitations` — known weaknesses, out-of-scope inputs.

### Forbidden content (publish-time rejection)

- Secrets, API keys, customer PII, real credit card numbers, real SSNs (regex-screened).
- External `<script>` or `<iframe>` tags (markdown should be safe; the renderer strips them anyway, but we reject at publish to keep files clean).
- Links to non-HTTPS URLs (warning at v1, hard reject if exploit-pattern detected).
- Self-referential pricing claims that contradict the frontmatter (e.g. body says "free" but `license_type=one_time`).

---

## Compilation contract (from creator engine)

The visual builder graph compiles to skills.md as follows. Detailed mapping lives in `skill-creator/01-visual-builder.md`, but the invariants are:

1. **Lossless round-trip is NOT required.** Once compiled, the canonical form is the markdown. Re-opening a published skill in the builder re-parses the markdown and best-effort reconstructs nodes.
2. **Each node type maps to a stable section or list item** in the body so the parser can find it again.
3. **Metadata fields in the builder UI map 1:1 to frontmatter keys.** No "hidden" fields.

---

## Versioning & immutability

- A `(id, version)` pair is **immutable** once `released_at` is set on its `skill_versions` row.
- Patch releases (1.2.0 → 1.2.1) must be **buyer-transparent**: no breaking input/output schema changes, no `required_models` reduction that drops a model an existing buyer is using.
- Minor releases (1.2 → 1.3) may add optional inputs, add `compatible_models`, expand `tags`.
- Major releases (1.x → 2.0) may change anything; trigger an upgrade flow for one-time buyers (see `marketplace/06-versioning-and-updates.md`).
- The validator enforces these constraints when a creator submits a new version against the previous one. Block release on violation; offer to bump the version number with an inline explanation.

---

## Signing & delivery

- On publish, the marketplace computes `content_hash = sha256(body_bytes_after_normalization)` and injects the `distribution` block.
- `body_bytes_after_normalization` = body with CRLF→LF, trailing whitespace stripped, single trailing newline.
- The signature is currently a placeholder (`signed_by: "marketplace"`, signature is HMAC of `content_hash` with platform key). Real per-creator keys land in Phase 5.
- Delivered files have the distribution block re-injected with a license-specific watermark (an invisible HTML comment near EOF: `<!-- license:{license_id} buyer:{buyer_id_hash} -->`). This lets us audit leaks without affecting AI consumption.

---

## Reference example (canonical)

A complete passing example lives at `apps/api/tests/fixtures/skills/dcf-valuation.skills.md`. Every parser/validator test loads it.

---

## Acceptance for "spec is live"

- [ ] `packages/skills-schema` exports Pydantic + Zod models generated from a single source-of-truth definition file.
- [ ] `apps/api/src/skills/validator.py` exposes `validate_file(content: bytes) -> ValidationResult` with explicit error codes and human messages.
- [ ] The reference fixture validates green.
- [ ] At least 10 negative fixtures (one per validation rule above) validate red with the correct error code.
- [ ] Frontend uses the same Zod schema for in-browser preview validation in the creator app.
