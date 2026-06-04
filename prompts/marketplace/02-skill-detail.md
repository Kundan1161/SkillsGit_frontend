# marketplace — 02 Skill Detail Page

**Phase:** 1
**Depends on:** `marketplace/00-overview.md`, `02-data-model-core.md`, `shared/skills-md-spec.md`, `shared/design-system.md`
**Parallel-safe with:** `01-discovery.md`, `03-pricing-and-checkout.md`, `04-licensing-and-delivery.md`
**Status:** ready
**Owner:** _empty_

> The detail page is where the buyer **decides**. It must answer: what does it do, does it match my model, is the creator credible, what do other buyers say, what's it cost, and what version am I getting.

---

## Scope

- Skill detail page (`/s/{creator-handle}/{slug}`)
- Public creator profile (`/u/{creator-handle}`)
- APIs for fetching detail + version history + creator profile

**Not** in scope: reviews submission UI (lives in `05-trust-and-quality.md`, but the detail page **reads** reviews — coordinate with that prompt's API), the buyer's `/library` view, checkout (next prompt), sandbox preview UI (also in `05`).

---

## Skill detail page (`/s/{handle}/{slug}`)

Server-rendered. URL is canonical and stable.

### Layout (desktop)

Two-column above the fold:

**Left (8 cols):**
- Breadcrumb: `Browse / {category} / {skill name}`
- H1: skill name
- Tagline (text-lg, fg-muted)
- Creator chip: avatar + handle + verified badge → links to `/u/{handle}`
- Hero image (cover_image_url) + screenshots carousel
- Tabs: `Overview`, `What's inside`, `Versions`, `Reviews`, `FAQ`

**Right (4 cols, sticky):**
- Price card:
  - Pricing model (one-time / subscription / freemium)
  - Price (large)
  - Support badge if subscription
  - Primary CTA — "Buy for $X", "Subscribe — $X/mo", or "Get free version"
  - Secondary CTA — "Try in sandbox" (gated to logged-in users; opens preview)
  - "Add to wishlist" tertiary link
- AI requirements block:
  - Required models (badges)
  - Compatible models (collapsed list)
  - Tools required (icons)
  - Min context tokens (if set)
- Quick facts:
  - Latest version + released date
  - Category
  - Tags (chips, click → `/browse?tags=…`)
  - Total sales (only when ≥ 25, to avoid social-proof shame)
  - Avg rating + count

### Tabs

**Overview** — `description_md` rendered (sanitized). Links open in new tab.

**What's inside** — rendered preview of the skill's body **excluding** the literal "How to apply" instructions (we don't want to give the whole skill away pre-purchase). Show: `When to use`, `Inputs`, `Outputs`, `Examples` (clipped if very long), `Limitations`. Use `unified` + `remark` + `rehype` with a sanitizer.

**Versions** — version timeline:
- Each version: version number, released date, changelog markdown, breaking-change flag.
- Yanked versions show a struck-through chip with the yank reason on hover.
- The currently displayed version is selectable from a dropdown — defaults to `latest_version`. Changing it updates the "What's inside" preview.

**Reviews** — list rendered from `/v1/skills/{id}/reviews` (paginated). Each review:
- Stars, reviewer display name + handle (anonymized if buyer chose), date, title, body.
- Creator's reply (if any) appears nested beneath.
- Sort: most-helpful (default — by `helpful_count` once that lands) / newest.
- "Leave a review" button at top → only enabled if current user has an active license and hasn't reviewed. Submit UI defined in `05-trust-and-quality.md`.

**FAQ** — pulled from `skills.faq_md` (optional new column on `skills` — add it in your migration). Markdown rendered. Empty state if no FAQ; creator can edit from dashboard.

### Mobile

Single column. Price card collapses into a sticky bottom bar with the primary CTA + price; tap to expand into full card as a sheet.

---

## Creator public profile (`/u/{handle}`)

Server-rendered.

Sections:

- Header: avatar (large), display name, handle, verified badge, bio (markdown), website, social links, industries.
- Stats strip: total skills, total sales (only when ≥ 100), avg rating across skills.
- Skills grid: all `published` skills by this creator, default sort `most_sold`. Reuses `SkillCard`.
- "Follow" placeholder for Phase 5+ — disabled button with tooltip "Coming soon" or just omit.

---

## APIs

### `GET /v1/skills/{id_or_slug}`

Accepts either UUID or `{handle}/{slug}` (URL-encoded slash).

**Response:**
```json
{
  "id": "uuid",
  "slug": "dcf-valuation",
  "name": "DCF Valuation Pro",
  "tagline": "...",
  "description_md": "...",
  "category": "finance",
  "tags": [...],
  "cover_image_url": "...",
  "screenshots": [...],
  "faq_md": "...",
  "pricing": {
    "model": "one_time",
    "one_time_price_cents": 1900,
    "subscription_price_cents": null,
    "currency": "USD",
    "support_included": false,
    "freemium_paired_with": null
  },
  "ai_requirements": {
    "required_models": ["claude-opus-4-7"],
    "compatible_models": ["claude-sonnet-4-6"],
    "tools_required": ["code_execution"],
    "min_context_tokens": null,
    "estimated_tokens_per_invocation": 8000
  },
  "latest_version": {
    "version": "1.2.0",
    "released_at": "...",
    "changelog_md": "..."
  },
  "stats": {
    "rating_avg": 4.7,
    "rating_count": 23,
    "total_sales": 412
  },
  "creator": { /* same shape as in discovery */ },
  "preview_body_md": "...   /* sanitized + clipped body for 'What's inside' tab */"
}
```

`preview_body_md` is computed server-side from the latest non-yanked version: parse the markdown, drop the `## How to apply` section, clip `## Examples` to 1 example, return the rest.

### `GET /v1/skills/{id}/versions`

Paginated list of versions, newest first. Includes `is_yanked`, `yank_reason`.

### `GET /v1/skills/{id}/versions/{version}/preview`

Returns `preview_body_md` for a specific version (used when the user selects a different version in the Versions tab).

### `GET /v1/creators/{handle}`

```json
{
  "handle": "janedoe",
  "display_name": "Jane Doe",
  "avatar_url": "...",
  "bio_md": "...",
  "website_url": "...",
  "social": {...},
  "industries": ["finance", "data"],
  "is_verified": true,
  "stats": {
    "total_skills": 4,
    "total_sales": 1820,
    "rating_avg": 4.6
  }
}
```

### `GET /v1/creators/{handle}/skills`

Paginated. Same item shape as discovery.

---

## Components

In `apps/web-marketplace/components/skill/`:

- `SkillHero` — title, tagline, creator chip, image carousel.
- `PriceCard` — sticky right column, includes CTAs.
- `AiRequirementsCard` — model badges, tools, context.
- `VersionTimeline` — vertical list with dot rail; expand to see changelog.
- `WhatsInsidePreview` — markdown renderer with clipped sections.
- `ReviewList` — fetches reviews via TanStack Query, infinite scroll.
- `CreatorChip` — small avatar + handle + verified mark; used in cards too.
- `FaqAccordion` — Radix accordion over `faq_md`.

For the creator profile, in `apps/web-marketplace/components/creator/`:
- `CreatorHeader`, `CreatorStats`, `CreatorSkillsGrid`.

---

## SEO

- Page title: `{name} by {creator display_name} — Skills Marketplace`
- Meta description: tagline (truncate to 150 chars).
- Open Graph: cover image, name, tagline. Twitter card large.
- JSON-LD `Product` schema with `aggregateRating`, `offers`, `brand` (creator). Embed in head via Next metadata API.
- Canonical URL: `/s/{handle}/{slug}` (lowercase, no trailing slash).
- Sitemap: dynamic, generated at `/sitemap.xml`, paginated if > 50k URLs (Next supports this natively).

---

## Edge cases

- Skill in `unlisted` status: detail page accessible by direct URL, not indexable (`<meta robots="noindex">`), not in sitemap.
- Skill in `removed` or `pending_review`: 404 to the public, but 200 to the creator and admins. Show a banner explaining the state.
- All versions yanked: detail page shows "This skill is currently unavailable" with the creator's contact link (if public). CTAs disabled.
- Buyer already owns the skill: replace primary CTA with "Open in library" linking to `/library/{license-id}`. Add a small "Latest version available" notice if their license max_version < latest.

---

## Acceptance

- [ ] Detail page renders for a seeded skill with all sections populated.
- [ ] Switching versions in the Versions tab updates "What's inside" without a full page reload.
- [ ] Creator profile page renders with 3+ skills from seed data.
- [ ] All API responses match the OpenAPI schema; types regenerate cleanly.
- [ ] SEO: page passes Lighthouse SEO ≥ 95.
- [ ] Owned-skill state correctly swaps CTA to "Open in library" (tested via Playwright with a logged-in fixture user).
