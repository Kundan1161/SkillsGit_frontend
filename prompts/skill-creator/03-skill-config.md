# skill-creator — 03 Skill Config (Metadata, AI Requirements, Pricing)

**Phase:** 3
**Depends on:** `skill-creator/00-overview.md`, `skill-creator/01-visual-builder.md`, `shared/skills-md-spec.md`, `marketplace/03-pricing-and-checkout.md`
**Parallel-safe with:** `02-import-from-projects.md`, `04-test-and-preview.md`, `05-publish-to-marketplace.md`
**Status:** ready
**Owner:** _empty_

> The builder defines **what the skill does**. The config form defines **how it's listed, priced, and run**. Together they produce a complete, publishable skills.md.

---

## Scope

- The `/skills/{id}/config` page.
- Forms for: identity, marketplace metadata, AI runtime requirements, pricing.
- Validation, defaults, and helpful presets.
- The "What does this map to in skills.md?" inline cues.

**Not** in scope: the canvas itself, sandbox runs, publish flow.

---

## Page structure

Single page, accordion sections (all open by default; collapse-state persisted per-user):

1. **Identity** — name, tagline, slug, cover image, screenshots.
2. **Discovery** — category, tags, description (markdown), FAQ (markdown).
3. **AI runtime** — required models, compatible models, tools, context window, token estimate.
4. **Pricing** — model picker (free / one-time / subscription / freemium), prices, support tier.
5. **Support & contact** — support_url, response SLA (when subscription).
6. **Inputs & Outputs** — read-only view of what the builder produced; "Edit in builder" link.
7. **Versioning** — target version (semver), changelog draft for this release.

Sticky bottom bar: "Save draft" / "Preview compiled file" / "Open builder" / "Run in sandbox" / "Publish".

---

## Sections in detail

### 1. Identity

| Field | Type | Rules |
|---|---|---|
| `name` | text | required, 3–80 chars |
| `tagline` | text | required, 10–140 chars, single line |
| `slug` | text | required, kebab-case, unique per creator. Pre-filled from name; editable only before first publish, locked after |
| `cover_image` | image upload | required for publish. 1200×630 min. JPG/PNG/WebP. ≤ 2MB. Stored in S3, returns URL. |
| `screenshots` | image multi-upload | 0–8. Same constraints. |

Image upload: client-side compresses (browser-image-compression), uploads to a presigned URL from `POST /v1/uploads/presign`, then stores the returned URL. Show progress bars.

### 2. Discovery

| Field | Type | Rules |
|---|---|---|
| `category` | select | required, from `/v1/catalog/categories` |
| `tags` | chips input | 0–10. Free-form lowercase; warn if a tag matches an existing skill exactly 0 times (might be a typo). |
| `description_md` | markdown editor | required, 50–5000 chars. Preview tab. |
| `faq_md` | markdown editor | optional. Up to 10k chars. |

Markdown editor: a lightweight one (e.g., `react-md-editor` or our own from `unified` + a textarea). Tabs: Write / Preview.

### 3. AI runtime

| Field | Type | Rules |
|---|---|---|
| `required_models` | multi-select | required, ≥ 1. Source: a curated list maintained in `apps/api/src/skills/models.py`. Each entry: id, display name, provider, capabilities. |
| `compatible_models` | multi-select | optional. Models known to work but not certified. |
| `tools_required` | multi-select | optional. Common: `web_search`, `code_execution`, `file_io`, `image_input`, `image_output`, `function_calling`. |
| `tools_optional` | multi-select | optional. |
| `min_context_tokens` | number | optional. Slider: 4k, 8k, 32k, 128k, 200k, 1M presets + "custom". |
| `estimated_tokens_per_invocation` | number | optional. Helpful for buyer cost previews. |

Inline education: a "?" tooltip on each field explains why it matters. For `required_models`, a small cost preview: "Buyers running this on Claude Opus will spend ~$0.20 per invocation".

### 4. Pricing

Pricing model picker (radio group, large cards):

- **Free** — "Build reputation; no income."
- **One-time** — "Single payment; no support obligation."
- **Subscription** — "Recurring revenue; you commit to a response SLA."
- **Freemium** — "Free version + paid sibling."

When selected, reveal model-specific fields:

| Model | Fields |
|---|---|
| free | (none) |
| one_time | `one_time_price_cents` (with payout preview), `upgrade_price_cents` (preset 50% off; appears when bumping to a new major version) |
| subscription | `subscription_price_cents`, `support_tier` (basic/priority), `support_sla` (response time commitment text) |
| freemium | paired skill picker (must already exist OR "Create paired paid skill now" CTA), plus the paid sibling's fields |

Price input: dollar field that converts to cents under the hood. Show payout preview: "$19 → you earn $15.20 (after our 20% fee)".

**Constraints (enforced server-side too):**
- `one_time_price_cents` ≥ 100 (i.e., $1.00 minimum).
- `subscription_price_cents` ≥ 100.
- Maximum: $999/one-time, $99/month subscription. (Soft caps; raise with admin override.)
- Pricing model is **locked after first publish** (matches marketplace rule).

### 5. Support & contact

Only relevant for subscription tier (but visible for any).
- `support_url` — text URL field. Buyers click "Contact creator" from their library if support is included.
- `support_response_sla` — free text shown on the listing. e.g., "Within 24 business hours."

### 6. Inputs & Outputs (read-only)

Tables listing what was extracted from the parameter and output nodes. Each row has an "Edit in builder" link that jumps to the relevant node.

### 7. Versioning

| Field | Type | Rules |
|---|---|---|
| `target_version` | semver text | required. Pre-filled by the version-bump suggester (`apps/api/src/skills/version_diff.py`). |
| `changelog_md` | markdown editor | required for non-first versions. Mini template offered: "### Added / ### Changed / ### Fixed". |
| `breaking_changes` | bool | computed automatically by the diff analyzer; read-only badge. |

The publish wizard reads from these fields.

---

## Form architecture

- React Hook Form root provider over the whole page.
- Each section is a `<FormSection>` with its own Zod sub-schema.
- Submit is debounced (1s) → autosave to `/v1/creator/skills/{id}/draft` (PATCH frontmatter_json).
- Validation runs on every change; field-level errors render inline; section-level errors render at section header (count badge).

Server-side mirror: every PATCH triggers re-validation against `shared/skills-md-spec.md` and persists `compiled_valid` + `compile_errors`. The UI surface mirrors backend truth.

---

## Inline education ("What does this map to?")

For each field, a tiny code-style hint button reveals the corresponding skills.md frontmatter key:

```
[ ?  → `frontmatter.ai.required_models` ]
```

Click → opens a side panel showing the compiled skills.md with the relevant section highlighted. Helps creators build a mental model of the output format.

---

## Presets by industry

When the user enters Identity for the first time, after choosing a category, surface preset config bundles:

- "Finance — DCF-style skill" → required_models: [claude-opus-4-7], tools: [code_execution], min_context: 32k.
- "Design — Critique skill" → required_models: [claude-sonnet-4-6, gpt-4o], tools: [image_input], min_context: 8k.
- "Marketing — Campaign plan" → similar.

A row of preset chips beneath the AI runtime section: "Apply finance preset", "Apply design preset", etc. Stored in `apps/web-creator/lib/config/presets.ts`.

---

## API

This page mostly piggybacks on the draft API from `01-visual-builder.md`:
- `GET /v1/creator/skills/{id}/draft` returns `frontmatter_json`.
- `PATCH /v1/creator/skills/{id}/draft` accepts a partial `frontmatter_json`.

Specific helpers:
- `GET /v1/catalog/models` — list available AI models (id, display, provider, capabilities). Cached.
- `GET /v1/catalog/tools` — list known tool identifiers. Cached.
- `POST /v1/uploads/presign` — returns `{ url, fields }` for direct S3 upload.
- `POST /v1/creator/skills/{id}/suggest-version` — runs the diff analyzer against the previous published version and returns the suggested next version.

---

## Edge cases

- Creator hasn't completed Stripe Connect: can fill in pricing as `free` only. For paid models, show a blocking banner and a link to onboarding.
- Slug conflicts: shown inline; suggest alternates ("dcf-valuation-2").
- Cover image missing at publish time: publish wizard blocks; can save draft.
- Tags overlap with category names: warn, allow.

---

## Acceptance

- [ ] All sections render and bind to RHF; field-level + section-level validation works.
- [ ] Autosave debounces and reflects server-side validation results.
- [ ] Image upload via presigned URL works end-to-end with S3 (MinIO locally).
- [ ] Pricing tier picker shows correct sub-fields and payout previews.
- [ ] Version suggester returns a sensible default given a known prior version.
- [ ] Inline "maps-to" hints open a panel that highlights the corresponding frontmatter line.
- [ ] Presets correctly populate AI runtime fields when applied.
- [ ] Frontmatter compiles cleanly: `compile + validate` on the saved draft returns green.
