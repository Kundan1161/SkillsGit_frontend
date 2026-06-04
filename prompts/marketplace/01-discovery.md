# marketplace — 01 Discovery

**Phase:** 1
**Depends on:** `marketplace/00-overview.md`, `02-data-model-core.md`, `shared/design-system.md`, `shared/api-conventions.md`
**Parallel-safe with:** `02-skill-detail.md`, `03-pricing-and-checkout.md`, `04-licensing-and-delivery.md`
**Status:** ready
**Owner:** _empty_

> Discovery is the **front door** of the marketplace. Buyers come here without knowing what they need. We help them find it.

---

## Scope

- Marketplace home (`/`)
- Browse all (`/browse`)
- Category landing (`/c/{category-slug}`)
- Search results (`/search`)
- Filter & sort controls
- Search and browse APIs

**Not** in scope: the skill detail page (next prompt), checkout, creator profile.

---

## Pages

### Home (`/`)

A composed page of curated rails. RSC-rendered, cached for 60s at the edge.

Sections, top to bottom:

1. **Hero** — value prop in one sentence, search bar prominent, two CTAs ("Browse skills", "Become a creator").
2. **Featured** — admin-curated rail of 4–8 skills. Backed by an `editorial_picks` table with `(skill_id, slot, starts_at, ends_at, sort_order)`. Define the table in this prompt.
3. **Trending this week** — top 8 by `total_sales` over the last 7 days, joined with `skills` for full card data.
4. **Top rated** — top 8 by `rating_avg` with ≥ 5 ratings.
5. **Browse by category** — 12 category cards (icon + name + count).
6. **New releases** — most recent 8 skills by `latest_version.released_at`.
7. **Footer** — links, legal, "Become a creator".

### Browse (`/browse`)

A two-column layout: sticky filter sidebar + grid.

**Filters:**
- Category (multi-select checkboxes, with skill counts)
- Pricing model (`free`, `one_time`, `subscription`, `freemium`)
- Price range (slider, dollars; only applies to non-free)
- AI model (multi-select from `ai.required_models` allowlist)
- Tags (typeahead chip input)
- Rating (≥ 3★, ≥ 4★, ≥ 4.5★)
- Has free preview (checkbox)
- Has support tier (checkbox)

**Sort options:**
- Relevance (default when `q` is set)
- Newest (by `latest_version.released_at` desc)
- Top rated (by `rating_avg` desc, min 5 reviews)
- Most sold (by `total_sales` desc)
- Price low to high
- Price high to low

URL is the source of truth: `/browse?categories=finance,data&pricing=one_time&rating=4&sort=top_rated`. Filter state lives in `searchParams`, not React state.

### Category landing (`/c/{slug}`)

Same as `/browse` but with `categories={slug}` pinned and a category-specific hero (description, top creators in this category, a featured sub-row).

### Search results (`/search?q=...`)

Same grid as `/browse` but ranking favors relevance. Empty-state surfaces:
- "Did you mean ..." suggestions (basic Postgres trigram similarity for v1).
- 4 popular categories.
- "Get notified when a skill matches" — adds a `search_alerts(user_id, query, filters)` row (define here).

---

## APIs

All under `/v1/catalog/`.

### `GET /v1/catalog/skills`

The workhorse. Used by browse, category, search, and rails.

**Query params:**
- `q` (string, optional) — free-text search
- `categories` (csv, optional)
- `pricing_models` (csv, optional)
- `min_price_cents` / `max_price_cents` (int, optional)
- `required_models` (csv, optional)
- `tags` (csv, optional)
- `min_rating` (float, optional)
- `creator_handle` (string, optional)
- `sort` (enum: `relevance`, `newest`, `top_rated`, `most_sold`, `price_asc`, `price_desc`)
- `limit`, `cursor` (see `shared/api-conventions.md`)

**Response item shape (lean for card rendering):**
```json
{
  "id": "uuid",
  "slug": "dcf-valuation",
  "name": "DCF Valuation Pro",
  "tagline": "Build a defensible discounted cash flow model.",
  "cover_image_url": "...",
  "category": "finance",
  "tags": ["dcf", "valuation"],
  "pricing_model": "one_time",
  "one_time_price_cents": 1900,
  "subscription_price_cents": null,
  "rating_avg": 4.7,
  "rating_count": 23,
  "total_sales": 412,
  "creator": {
    "handle": "janedoe",
    "display_name": "Jane Doe",
    "avatar_url": "...",
    "is_verified": true
  },
  "latest_version": "1.2.0",
  "released_at": "2026-05-01T..."
}
```

### `GET /v1/catalog/categories`

Returns categories with skill counts. Cached for 5 min.

```json
{
  "items": [
    {"slug": "finance", "name": "Finance", "description": "...", "skill_count": 142}
  ]
}
```

### `GET /v1/catalog/featured`

Returns the active `editorial_picks`. Admin-only mutations:

### `POST /v1/admin/featured` (admin)
### `DELETE /v1/admin/featured/{id}` (admin)

### `POST /v1/catalog/search-alerts`

Persists a saved search. Body: `{ q, filters }`. Returns the alert row. Backed by a `search_alerts` table:

| col | type |
|---|---|
| id | uuid pk |
| user_id | uuid fk |
| name | text |
| query_json | jsonb |
| created_at | timestamptz |
| last_notified_at | timestamptz |

A nightly cron checks for new skills matching saved alerts and emails the user (digest-style). Implement the cron in `apps/api/src/catalog/jobs.py`.

---

## Search implementation

Phase 1: Postgres-native.

- Maintain a `tsvector` column on `skills` (generated, indexed with GIN): `setweight(to_tsvector('english', name), 'A') || setweight(..., tagline, 'B') || setweight(..., description_md, 'C') || setweight(..., array_to_string(tags, ' '), 'B')`.
- Search query: `websearch_to_tsquery('english', :q)` against the tsvector. Rank with `ts_rank_cd`.
- Trigram fallback for typo tolerance: `similarity(name, :q) > 0.3` as an OR clause.
- Combined relevance score is `0.7 * ts_rank + 0.3 * similarity`. Plus a popularity boost: `+ 0.1 * log(1 + total_sales)`.

Phase 2 (deferred): swap to Meilisearch when listings cross 5k or relevance complaints accumulate.

---

## Components (frontend)

In `apps/web-marketplace/components/discovery/`:

- `SkillCard` — image, name, tagline, price, rating, creator handle. Used in every rail and grid.
- `SkillGrid` — responsive grid wrapping `SkillCard`s with skeleton states.
- `CategoryRail` — horizontal scroll on mobile, grid on desktop.
- `FilterSidebar` — collapsible sections, count badges next to each option.
- `SortDropdown` — Radix select.
- `SearchBar` — top-of-page input with debounced autocomplete (250ms). Suggestions come from `/v1/catalog/skills?q=...&limit=5`.
- `EmptyState` — used when filters return zero results.

Card hover behavior: `-translate-y-0.5`, shadow lift. Click navigates to skill detail. Avoid full-page navigations from card actions — buttons inside card stop propagation.

---

## Performance budget

- Home: < 1.5s LCP on Slow 4G simulated (Vercel Speed Insights).
- Browse: < 2s LCP, paginated 20 per page, prefetch next page on intersection observer.
- Search query API p95 < 200ms at 1k listings, < 500ms at 10k listings.

---

## Accessibility

- All filters are keyboard-navigable; arrow keys move within a group.
- Filter "applied" state announced via `aria-live`.
- Cards have a single landmark link (the title), not a card-wide anchor (so screen readers don't read every element on the way in).

---

## Acceptance

- [ ] Home renders with at least 8 seeded skills across 3+ categories from `infra/seed/`.
- [ ] Browse supports every filter listed above; URL is shareable and reflects state on refresh.
- [ ] Search returns relevant results for "dcf", "design critique", "social media" against seeded data.
- [ ] Saved search alert persists and emails on next cron run (verified in mailhog).
- [ ] Lighthouse perf ≥ 90 on home and browse pages.
- [ ] Playwright E2E: anonymous user lands on home → clicks featured skill → reaches detail page (smoke test, detail page can be a stub in this phase).
