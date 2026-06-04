# 02 — Core Data Model

**Phase:** 0 (shared context)
**Depends on:** `00-vision.md`, `01-tech-stack-and-repo.md`
**Parallel-safe with:** all
**Status:** ready

> Entities shared across marketplace and creator. Module-specific tables (e.g., `cart_item`, `builder_graph_snapshot`) live in their respective prompts. This file defines the **stable spine** — adding columns is fine, renaming/removing requires a migration plan.

---

## Entity overview

```
User ────────────── owns ──────────── Skill ─── has many ─── SkillVersion
  │                                    │
  ├── is creator of ─── CreatorProfile │── has ── Pricing (per skill)
  ├── owns ──────────── License        │
  └── writes ────────── Review         └── has ── Category / Tag

Order ─── line items ─── OrderItem ─── grants ─── License
Subscription ─── tier ─── monthly access ─── grants ─── License (renewable)

Payout ─── creator ─── batched OrderItems
```

---

## Tables

All tables use UUID v7 primary keys, `created_at` / `updated_at` (timestamptz), and `deleted_at` (nullable, for soft-delete where applicable).

### `users`
| col | type | notes |
|---|---|---|
| id | uuid pk | |
| email | citext unique | required, verified |
| password_hash | text | nullable if OAuth-only |
| display_name | text | |
| avatar_url | text | |
| role | enum(`buyer`, `creator`, `admin`) | a user can be both buyer and creator; this is the *primary* role for UX defaults |
| is_creator_verified | bool | admin-granted badge |
| stripe_customer_id | text | for billing |
| stripe_connect_account_id | text | nullable; set when becoming a creator |

### `creator_profiles`
| col | type | notes |
|---|---|---|
| id | uuid pk | |
| user_id | uuid fk → users.id | unique |
| handle | citext unique | URL slug, immutable after first set |
| bio | text | markdown allowed |
| website_url | text | |
| social | jsonb | `{twitter, linkedin, github, …}` |
| industries | text[] | `[finance, design, marketing, …]` for discovery |
| payout_country | char(2) | ISO 3166-1 alpha-2 |

### `skills`
The "product" — buyers see this as the listing.

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| creator_id | uuid fk → users.id | |
| slug | citext | unique per creator (`creator_handle/slug`) |
| name | text | human title |
| tagline | text | one-line for cards (max 140 chars) |
| description_md | text | long markdown for listing page |
| category | text fk → categories.slug | primary category |
| tags | text[] | searchable secondary tags |
| cover_image_url | text | for cards |
| screenshots | text[] | array of URLs |
| status | enum(`draft`, `pending_review`, `published`, `unlisted`, `removed`) | |
| latest_version_id | uuid fk → skill_versions.id | nullable; the version pointed at by buyers on "latest" |
| pricing_model | enum(`free`, `one_time`, `subscription`, `freemium`) | |
| one_time_price_cents | int | nullable |
| subscription_price_cents | int | nullable; per month |
| support_included | bool | true if pricing tier includes creator support SLA |
| total_sales | int | denormalized; updated on order completion |
| rating_avg | numeric(3,2) | denormalized; recalculated nightly |
| rating_count | int | denormalized |

**Pricing model semantics** (referenced by `marketplace/03-pricing-and-checkout.md`):
- `free` — no price, no license restrictions, no support
- `one_time` — pay once, perpetual license to current major version + bug-fix updates; **no support**
- `subscription` — pay monthly, access to all updates while active; **includes support SLA**
- `freemium` — a free version exists (a separate `Skill` row marked `free`) and links to a paid sibling

### `skill_versions`
A skill is delivered as a versioned skills.md file. Buyers receive specific versions via their license.

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| skill_id | uuid fk → skills.id | |
| version | text | semver, e.g. `1.2.0`. Unique per `(skill_id, version)` |
| content_hash | char(64) | sha256 of the skills.md body |
| storage_url | text | signed URL or S3 key to the immutable file |
| ai_requirements | jsonb | mirrors `ai:` block in skills.md frontmatter |
| changelog_md | text | rendered on detail page |
| released_at | timestamptz | publish time, NOT created_at |
| released_by | uuid fk → users.id | |
| is_yanked | bool | yanked = no new licenses, existing licenses still resolve |

> **Immutability rule:** once `released_at` is set, the version is **frozen**. No edits. Patches require a new version row. Yanking is a flag, not a deletion.

### `categories`
| col | type | notes |
|---|---|---|
| slug | citext pk | e.g. `finance`, `design`, `marketing` |
| name | text | display name |
| description | text | |
| parent_slug | citext fk → categories.slug | nullable, for nesting |
| display_order | int | |

Seed with: `finance`, `design`, `data`, `marketing`, `sales`, `legal`, `operations`, `engineering`, `customer-support`, `productivity`, `creative`, `research`, `other`.

### `orders`
| col | type | notes |
|---|---|---|
| id | uuid pk | |
| buyer_id | uuid fk → users.id | |
| stripe_payment_intent_id | text | unique |
| subtotal_cents | int | |
| platform_fee_cents | int | |
| creator_payout_cents | int | total across line items |
| currency | char(3) | ISO 4217, default `USD` |
| status | enum(`pending`, `paid`, `refunded`, `partially_refunded`, `failed`) | |
| placed_at | timestamptz | |

### `order_items`
| col | type | notes |
|---|---|---|
| id | uuid pk | |
| order_id | uuid fk → orders.id | |
| skill_id | uuid fk → skills.id | |
| skill_version_id | uuid fk → skill_versions.id | the version active at purchase time |
| price_cents | int | snapshot at purchase |
| platform_fee_cents | int | snapshot at purchase |
| creator_id | uuid fk → users.id | denormalized for payout queries |

### `subscriptions`
| col | type | notes |
|---|---|---|
| id | uuid pk | |
| buyer_id | uuid fk → users.id | |
| skill_id | uuid fk → skills.id | |
| stripe_subscription_id | text | unique |
| status | enum(`active`, `past_due`, `canceled`, `paused`) | |
| current_period_start | timestamptz | |
| current_period_end | timestamptz | |
| cancel_at_period_end | bool | |
| price_cents | int | snapshot of price at signup; locked unless creator triggers re-quote |

### `licenses`
The unifying access record. Every entitlement (one-time, subscription period, freemium) materializes as a license.

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| buyer_id | uuid fk → users.id | |
| skill_id | uuid fk → skills.id | |
| source | enum(`one_time`, `subscription`, `free`, `freemium`, `grant`) | |
| source_id | uuid | order_item.id or subscription.id depending on source |
| granted_at | timestamptz | |
| expires_at | timestamptz | nullable for perpetual |
| max_version | text | semver ceiling; one-time licenses cap at major-version of purchase |
| support_tier | enum(`none`, `basic`, `priority`) | derived from pricing model |
| status | enum(`active`, `expired`, `revoked`) | |

> **License resolution:** "what version does buyer B see for skill S?" =
> latest `skill_version` where `version <= license.max_version` AND `released_at > license.granted_at OR (license.source = 'subscription' AND license.status = 'active')` AND NOT `is_yanked`.

### `reviews`
| col | type | notes |
|---|---|---|
| id | uuid pk | |
| skill_id | uuid fk → skills.id | |
| author_id | uuid fk → users.id | |
| license_id | uuid fk → licenses.id | required — must own a license to review |
| rating | int | 1–5 |
| title | text | nullable |
| body_md | text | |
| status | enum(`visible`, `hidden`, `flagged`) | |
| created_at | timestamptz | |

Unique constraint on `(skill_id, author_id)` — one review per buyer per skill, but editable.

### `payouts`
| col | type | notes |
|---|---|---|
| id | uuid pk | |
| creator_id | uuid fk → users.id | |
| stripe_transfer_id | text | unique |
| amount_cents | int | sum of payout amounts on included order_items minus refunds |
| currency | char(3) | |
| period_start | timestamptz | |
| period_end | timestamptz | |
| status | enum(`pending`, `paid`, `failed`) | |
| paid_at | timestamptz | nullable |

### `audit_log`
Generic append-only log for security-relevant actions (creator publishes, admin moderates, refund issued, role grants, etc.).

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| actor_id | uuid fk → users.id | nullable for system actions |
| action | text | dotted name, e.g. `skill.published`, `review.flagged` |
| target_type | text | `skill`, `user`, `review`, … |
| target_id | uuid | |
| metadata | jsonb | |
| created_at | timestamptz | |

---

## Indexes (start with these; add as queries demand)

- `users(email)` unique
- `creator_profiles(handle)` unique
- `skills(creator_id, slug)` unique
- `skills(status, category)` for browse
- `skills` GIN on `to_tsvector(name || ' ' || tagline || ' ' || description_md)` for search
- `skills` GIN on `tags`
- `skill_versions(skill_id, version)` unique
- `licenses(buyer_id, skill_id, status)` for "what do I own?"
- `order_items(creator_id, order.placed_at)` for payout queries
- `reviews(skill_id, status, created_at desc)` for listing pages

---

## What this file does NOT cover

- Builder-side persistence (graph nodes, draft snapshots): see `skill-creator/01-visual-builder.md`.
- Sandbox runtime execution records: see `skill-creator/04-test-and-preview.md`.
- Cart/checkout intermediate state: see `marketplace/03-pricing-and-checkout.md`.
- Webhook event log: see `marketplace/03-pricing-and-checkout.md` (Stripe section).

---

## Acceptance for "core data model is in"

- [ ] All tables above exist as SQLAlchemy models in `apps/api/src/*/models.py`.
- [ ] First Alembic migration applies cleanly to an empty Postgres.
- [ ] Categories table is seeded.
- [ ] Pydantic schemas exist for every entity (read/create/update variants where applicable).
- [ ] `pnpm codegen` produces TS types for all of them in `packages/api-client`.
