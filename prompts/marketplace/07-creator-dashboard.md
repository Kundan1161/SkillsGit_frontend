# marketplace — 07 Creator Dashboard

**Phase:** 2
**Depends on:** `marketplace/00-overview.md`, `02-data-model-core.md`, `marketplace/03-pricing-and-checkout.md`, `marketplace/05-trust-and-quality.md`, `marketplace/06-versioning-and-updates.md`, `shared/auth.md`
**Parallel-safe with:** `05-trust-and-quality.md`, `06-versioning-and-updates.md`
**Status:** ready
**Owner:** _empty_

> The dashboard is the creator's home. It should answer: am I making money, are buyers happy, what should I do today.

---

## Scope

- Dashboard overview page.
- Skills management (list, edit listing, manage versions, publish — uploads only in Phase 1; visual builder takes over in Phase 3).
- Earnings & payouts UI.
- Reviews moderation & reply.
- Webhooks management.

**Not** in scope: the visual builder itself (`skill-creator/*`), import pipelines (`skill-creator/02`).

---

## Pages

### `/dashboard` — overview

Top section: a single hero KPI row.
- This month's earnings (after fees), with delta vs last month.
- Active subscriptions count, with delta.
- Pending payout (Stripe pending balance).
- 30-day sales count.

Middle section: two columns.
- **Recent activity** — last 20 events (sales, subscriptions, reviews, refunds, version publishes) rendered as a timeline.
- **Action items** — auto-generated nudges:
  - "Reply to 2 new reviews"
  - "v1.2.0 of Skill X is pending review"
  - "Finish Stripe Connect onboarding"
  - "Buyer flagged a bug in v1.1.5 — consider patching"
  - Each item is a typed `dashboard_task` with `(kind, target_id, dismissed_at)` — implement table.

Bottom section: a small chart strip (4 sparklines) for the last 30 days: sales, subscriptions, MRR, refunds. Use a tiny SVG chart lib (recharts is fine, but minimal).

### `/dashboard/skills` — list

Table of the creator's skills with columns: name, status (badge), pricing model, latest version, total sales, MRR contribution, avg rating, actions (Edit, Versions, View public).

Filters: status, pricing model. Sort: by sales / by MRR / by rating.

### `/dashboard/skills/{id}` — edit listing

Tabs:
- **Listing** — name, tagline, description_md, category, tags, cover image, screenshots, faq_md, support_url. All editable; publishes the change immediately (no version bump — this is metadata, not skill content).
- **Versions** — list of versions with publish/yank/unyank actions. "New version" CTA opens the upload (Phase 1) or builder (Phase 3).
- **Pricing** — read pricing model (locked). Edit price (downward instantly, upward shows 14-day notice modal). Toggle support_included on subscription.
- **Reviews** — reviews on this skill with reply UI.
- **Sales** — sales over time, top buyers (anonymized to display_name), refund rate, regional breakdown (Phase 5).

### `/dashboard/skills/new` — create (Phase 1)

Form:
- Name, tagline, category, tags.
- Pricing model picker.
- Upload `skills.md` file. Validator runs; show errors inline.
- Cover image upload.

On submit:
1. Creates `skills` row in `draft`.
2. Creates `skill_versions` row with `released_at=null`.
3. Goes to publish step: review-and-confirm screen showing pricing summary, payout estimate, content checks status.
4. "Publish" → status becomes `pending_review` (or `published` if creator is fast-tracked).

In Phase 3 this entire form is replaced by entry into the visual builder.

### `/dashboard/earnings`

Sections:
- **Available balance** — Stripe-provided "available" amount; "Withdraw" links to Stripe Express dashboard (Stripe handles the actual transfer).
- **Pending balance** — Stripe-provided "pending" (funds in 2-day rolling window or longer).
- **Lifetime earnings** — sum of `order_items.creator_payout_cents` for this creator, minus refunds.
- **Payout history** — table from `payouts`; CSV export.
- **Per-skill earnings** — table of skills sorted by lifetime earnings.

### `/dashboard/reviews`

Inbox-style view of recent reviews:
- Unreplied (default tab) — chronological, oldest first.
- All — chronological.
- Flagged — reviews reported by users (visible to creator if their skill).

Each row: skill name, rating, body excerpt, time. Click → reply inline.

### `/dashboard/webhooks`

CRUD on `creator_webhooks` table (define here):

| col | type |
|---|---|
| id | uuid pk |
| creator_id | uuid fk → users.id |
| url | text |
| events | text[] |
| secret | text |
| status | enum(`active`, `disabled`, `failing`) |
| last_delivery_at | timestamptz |
| last_failure_at | timestamptz |
| consecutive_failures | int |
| created_at | timestamptz |

UI:
- List of webhooks with status, last delivery time, recent failure count.
- "Add webhook" → URL, event picker (multi-select from event allowlist), test ping button.
- "Recent deliveries" view per webhook (last 50 attempts with response code + duration). Backed by `webhook_deliveries` log table.
- Rotate secret button.
- Auto-disable after 50 consecutive failures (24h+).

---

## APIs

### Skills management

- `GET /v1/creator/skills` — list mine.
- `POST /v1/creator/skills` — create draft from upload.
- `PATCH /v1/creator/skills/{id}` — update listing metadata.
- `POST /v1/creator/skills/{id}/versions` — submit a new version (multipart with skills.md). Runs validator + diff analysis + content scans.
- `POST /v1/creator/skills/{id}/publish` — transition `draft` → `pending_review` (or `published` if fast-tracked).
- `POST /v1/creator/skills/{id}/versions/{ver}/yank` — yank.
- `DELETE /v1/creator/skills/{id}` — soft-remove. Listings disappear; existing licenses preserved (file still resolvable).

### Earnings

- `GET /v1/creator/earnings/summary` — MRR, this-month, pending, lifetime.
- `GET /v1/creator/earnings/per-skill?period=30d|90d|all` — per-skill breakdown.
- `GET /v1/creator/earnings/payouts` — paginated.

### Reviews

- `GET /v1/creator/reviews?unreplied=true|false` — paginated.
- `POST /v1/reviews/{id}/reply` — already specified in `05-trust-and-quality.md`; same endpoint.

### Webhooks

- `GET /v1/creator/webhooks`.
- `POST /v1/creator/webhooks`.
- `PATCH /v1/creator/webhooks/{id}`.
- `DELETE /v1/creator/webhooks/{id}`.
- `POST /v1/creator/webhooks/{id}/test` — fires a sample event.
- `GET /v1/creator/webhooks/{id}/deliveries`.

### Dashboard tasks

- `GET /v1/creator/tasks` — auto-generated action items.
- `POST /v1/creator/tasks/{id}/dismiss`.

Tasks are generated by a periodic job (every 10 minutes) reading: pending reviews, pending publishes, Stripe Connect status, recent flagged reviews.

---

## Sales analytics math

For the per-skill / per-period views:

```sql
-- one-time sales in period
SELECT skill_id,
       SUM(price_cents - platform_fee_cents) AS net_earned,
       COUNT(*) AS units_sold
FROM order_items
JOIN orders ON orders.id = order_items.order_id
WHERE orders.status = 'paid' AND orders.placed_at BETWEEN :start AND :end
  AND order_items.creator_id = :creator_id
GROUP BY skill_id;

-- MRR contribution = sum of price_cents on active subscriptions
SELECT skill_id, SUM(price_cents * 0.8) AS mrr_net  -- adjust for platform fee %
FROM subscriptions
WHERE status = 'active' AND skill_id IN (SELECT id FROM skills WHERE creator_id = :creator_id);
```

Always join on creator_id to ensure isolation. Centralize in `apps/api/src/creator/analytics.py`.

---

## Permissions

- All `/v1/creator/*` endpoints require: authenticated, `creator_profile` exists, and the targeted resource belongs to the caller.
- Admin override: admins can read any creator's dashboard via `/admin/creators/{handle}/...` mirror endpoints.

---

## Empty states

- New creator with 0 skills: dashboard shows a 3-step wizard:
  1. "Finish Stripe Connect onboarding" (with progress)
  2. "Create your first listing"
  3. "Tell buyers about it" (link to share/embed snippets)
- Stripe Connect incomplete: top banner persists across all dashboard pages until resolved.

---

## Acceptance

- [ ] Dashboard overview renders with seeded creator data including KPI deltas.
- [ ] A creator can upload a skills.md file and publish (Phase 1 path).
- [ ] Earnings page numbers match: sum of order_items minus refunds for the period.
- [ ] Webhook CRUD works, test ping fires a signed event to a mock receiver.
- [ ] All `/v1/creator/*` endpoints enforce ownership and return 403 on cross-creator access.
- [ ] Action-items job populates `dashboard_tasks` based on real state changes.
- [ ] E2E: new user signs up → onboards as creator → uploads skill → it appears in `/dashboard/skills` and (after admin approval) on the marketplace.
