# marketplace — 00 Overview

**Phase:** 1
**Depends on:** `00-vision.md`, `01-tech-stack-and-repo.md`, `02-data-model-core.md`, `shared/*`
**Parallel-safe with:** all marketplace/* siblings (each owns its own files)
**Status:** ready

> This file is the entry point for every agent working on the marketplace. Read it, then jump to your assigned sibling.

---

## What the marketplace is

The buyer-facing storefront and the creator-facing dashboard, both backed by the same FastAPI service. It exists to:

1. Let buyers **discover** skills they need.
2. Let buyers **license** skills (one-time, subscription, or freemium).
3. Let buyers **download** the skills.md file and any updates they're entitled to.
4. Let creators **publish, price, and update** skills.
5. Let creators **get paid** via Stripe Connect.
6. Earn the platform a **revenue share** on every transaction.

The marketplace must work end-to-end **without** the visual builder existing yet — creators publish via the API or admin tools in Phase 1. The builder ships later as a better path to the same endpoint.

---

## Top-level pages (marketplace web app)

```
/                            home — featured + browse-by-category
/browse                      all skills, with filters
/c/{category-slug}           category landing
/s/{creator-handle}/{slug}   skill detail page
/u/{creator-handle}          creator public profile
/search?q=...                search results
/checkout                    cart + payment
/library                     buyer's owned skills
/library/{license-id}        download + version history for a specific license
/settings/account            profile, email, password
/settings/billing            payment methods, subscriptions, invoices
/settings/api-tokens         programmatic access
/become-a-creator            onboarding wizard → Stripe Connect → handle picker
```

Creator dashboard (lives in same Next.js app, gated by `creator_profile` existence):

```
/dashboard                   overview, MRR, recent sales
/dashboard/skills            list of my skills
/dashboard/skills/{id}       edit listing, manage versions
/dashboard/skills/new        upload skills.md directly (Phase 1) or open builder (Phase 3)
/dashboard/earnings          payouts, pending balance
/dashboard/reviews           reviews on my skills, with reply
/dashboard/webhooks          outbound webhook config
```

Admin pages (gated by `is_admin`):

```
/admin                       moderation queue, recent flags
/admin/skills/{id}/review    approve/reject pending publishes
/admin/users                 user search, role grants
/admin/payouts               manual payout overrides
```

---

## Prompt-to-feature map

| Prompt | Owns |
|---|---|
| `01-discovery.md` | Home, browse, category, search, filters |
| `02-skill-detail.md` | Skill listing page, version history, screenshots, public profile |
| `03-pricing-and-checkout.md` | Cart, Stripe checkout, Stripe Connect onboarding, subscription, freemium math |
| `04-licensing-and-delivery.md` | License issuance, signed download URLs, watermarking, refund handling |
| `05-trust-and-quality.md` | Reviews, ratings, sandbox preview, moderation queue, automated publish checks |
| `06-versioning-and-updates.md` | Semver enforcement, update notifications, major-version upgrade flow |
| `07-creator-dashboard.md` | Earnings, sales analytics, payouts, webhook config |

---

## Cross-cutting concerns each prompt should respect

- **All money in cents (int).** Reference `02-data-model-core.md`.
- **All API endpoints follow `shared/api-conventions.md`** — cursor pagination, error format, idempotency where it matters.
- **All UI uses `packages/ui` primitives** and respects `shared/design-system.md`.
- **All skill file operations go through the validator** in `apps/api/src/skills/validator.py` (see `shared/skills-md-spec.md`). No raw filesystem access in routers.
- **Audit log every state change** — publishes, refunds, role changes, review hides.

---

## Phase 1 success looks like

A buyer, starting from a Google search:
1. Lands on `/s/janedoe/dcf-valuation`.
2. Clicks "Buy for $19" → Stripe checkout (Phase 1 supports one-time only).
3. Returns to `/library/{license-id}`.
4. Clicks "Download skills.md" → gets a watermarked file.
5. Drops it into Claude Code or another agent. It works.

Behind the scenes:
- A `licenses` row is created with `source=one_time`, `max_version=1.x`.
- An `order_items` row is created with snapshotted price + fee.
- A pending Stripe transfer for the creator is queued.
- `audit_log` records `order.placed` and `license.granted`.

## Phase 2 success looks like

Same buyer:
- Subscribes monthly to a different skill. Gets support badge.
- Sees a "new version available" banner for their one-time purchase. Clicks "What's new", reads the changelog, optionally upgrades to v2.0.0 at a discount.
- Leaves a 5-star review on the subscribed skill.
- The reviewed creator sees the review in their dashboard, replies, and gets analytics on which categories drive their MRR.

---

## Non-goals (so we don't drift)

- No social features beyond reviews (no follows, no DMs, no comments outside reviews).
- No gifting, no referral program — Phase 5 at earliest.
- No marketplace-as-a-service for white-label resellers.
- No multi-currency display in Phase 1; charge in USD, show local-currency estimates only after Phase 2.
