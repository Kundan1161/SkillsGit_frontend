# marketplace — 03 Pricing & Checkout

**Phase:** 1 (one-time only) → Phase 2 (subscriptions, freemium)
**Depends on:** `marketplace/00-overview.md`, `02-data-model-core.md`, `shared/auth.md`, `shared/api-conventions.md`
**Parallel-safe with:** `01-discovery.md`, `02-skill-detail.md`, `04-licensing-and-delivery.md`
**Status:** ready
**Owner:** _empty_

> Money is the most error-prone surface. Be paranoid. Every state transition is logged. Every webhook is idempotent. Every refund has a paper trail.

---

## Scope

- Pricing models: `free`, `one_time`, `subscription`, `freemium`.
- Cart and checkout flows.
- Stripe Connect onboarding for creators.
- Stripe Billing for subscriptions.
- Webhook handling for payment events.
- Refund flow.
- Payout schedule.

**Not** in scope: post-purchase delivery of the skill file (next prompt).

---

## Pricing models — full semantics

### `free`
- No payment. License issued immediately on "Get it" click.
- `licenses.source = free`, `max_version = "<latest_major>.x"` (e.g., `1.x`), `support_tier = none`.
- Refund N/A.

### `one_time`
- Stripe one-time payment intent.
- License issued on `payment_intent.succeeded` webhook.
- `licenses.source = one_time`, `max_version` capped at the **current major version** at time of purchase (e.g., bought at 1.2.0 → max_version `1.x`), `support_tier = none`.
- Buyer gets all patch and minor versions within that major for free, forever.
- Major-version upgrades (2.0.0) require a separate purchase — see `06-versioning-and-updates.md` for upgrade-discount flow.
- Refundable within 14 days, **only if** the skill has not been downloaded by the buyer (audit log check).

### `subscription`
- Stripe Billing recurring product.
- License issued on `customer.subscription.created` webhook with status `active` or `trialing`.
- `licenses.source = subscription`, `max_version = null` (unbounded — always latest), `support_tier = basic` or `priority` (TBD via plan tier).
- Auto-renews monthly. Cancellation at period end → license status → `expired` on `current_period_end`. No refund on cancel.
- Plan price is **locked at subscription creation**. Price changes by the creator do not affect existing subscribers until they re-subscribe.

### `freemium`
- A pair of `skills` rows: one `free` and one `one_time`-or-`subscription`. They are linked by a new column on `skills`:
  - `freemium_paired_with: uuid` (nullable, foreign key to the paid sibling or null).
  - The free skill has `freemium_paired_with = paid_skill_id`.
  - The paid skill has `freemium_paired_with = null` (it's the source of truth).
  - Define this column extension in the migration owned by this prompt.
- The detail page of the free version shows a banner: "Upgrade to Pro for $X — unlock support and full features".
- The free version's `description_md` and body must clearly state limitations.
- Conversion link uses pre-filled checkout for the paid pair.

### Pricing constraints
- Listings cannot change pricing model after first publish. The creator deletes the listing and creates a new one. (Phase 1 hard rule; relax later if needed.)
- Price can be changed only to a **lower** value at any time; upward changes require a 14-day notice banner on the listing (enforce in API).
- All prices in USD cents. Local-currency display is presentation only (Phase 2+).

---

## Cart & checkout

### Cart

- Single-skill checkout in Phase 1 (no real "cart"). Buyer clicks Buy → goes to `/checkout?skill={id}`.
- A `cart` Redis-backed structure can be added in Phase 2 for batched one-time purchases. Don't build it now.
- Subscriptions never go through a cart — one-click subscribe creates the Stripe subscription directly.

### Checkout flow (one-time)

1. **`POST /v1/checkout/sessions`** with `{ skill_id, idempotency_key }`.
2. Server validates: skill is `published`, latest version is not yanked, buyer doesn't already own it, creator has completed Stripe Connect.
3. Server creates a Stripe Checkout Session (`mode=payment`) with:
   - `line_items`: one item with `price_data` populated from the skill (don't pre-create Stripe prices for one-time — too much churn).
   - `payment_intent_data.application_fee_amount` = platform fee in cents.
   - `payment_intent_data.transfer_data.destination` = creator's Stripe Connect account id.
   - `metadata`: `{ skill_id, skill_version_id, buyer_id }`.
   - `success_url`, `cancel_url`.
4. Returns `{ checkout_url }`. Frontend redirects.
5. Stripe redirects to `success_url` with `?session_id={CHECKOUT_SESSION_ID}`.
6. Frontend hits **`POST /v1/checkout/sessions/{session_id}/finalize`** to confirm — but the source of truth is the webhook, not this call. Show "Processing..." until webhook lands.

### Checkout flow (subscription)

1. **`POST /v1/subscriptions`** with `{ skill_id, idempotency_key }`.
2. Server validates same as one-time.
3. Server ensures the buyer has a `stripe_customer_id` (create if not).
4. Server creates a Stripe Subscription with:
   - `items: [{ price: <stripe_price_id_for_skill> }]` — Stripe prices for subscriptions ARE pre-created per skill (one per pricing change). Track in a `stripe_prices(skill_id, stripe_price_id, price_cents, created_at)` table; create here.
   - `payment_behavior: "default_incomplete"`.
   - `expand: ["latest_invoice.payment_intent"]`.
   - `application_fee_percent` = platform fee %.
   - `transfer_data.destination` = creator's Stripe Connect account id.
5. Returns `{ client_secret }` for Stripe Elements to complete payment on the frontend.
6. Frontend confirms payment with Stripe.js.
7. Webhook `customer.subscription.created` issues the license.

### Platform fee

- Configurable via env: `PLATFORM_FEE_PERCENT` (default 20.0). Stored as an integer or `Decimal` — never float.
- For one-time: pass `application_fee_amount` in cents.
- For subscription: pass `application_fee_percent`.
- All math centralized in `apps/api/src/billing/fees.py`. Helper: `compute_fee(amount_cents, percent) -> int` rounds banker's rounding.
- Surfaced to creator in pricing UI: "List at $19 → you earn $15.20 after our 20% fee."

---

## Stripe Connect onboarding (for creators)

Triggered when a user clicks "Become a creator".

1. Collect `handle` and `payout_country`.
2. Create a `creator_profiles` row.
3. Create a Stripe Connect Express account (`type=express`, `country=<payout_country>`).
4. Generate an Account Link with `type=account_onboarding`, redirect URLs back to `/dashboard?onboarding=done` / `/dashboard?onboarding=incomplete`.
5. Persist `users.stripe_connect_account_id`.
6. On return, fetch the account; verify `details_submitted` and `payouts_enabled`. If not, show a "Finish setting up payouts" banner.
7. Creators cannot list paid skills until `payouts_enabled = true`. They CAN list free skills earlier (gated check: `if pricing_model != "free": require payouts_enabled`).

Webhook listeners on `account.updated` re-fetch and update local cache (`creator_profiles.payouts_enabled`).

---

## Webhooks

Endpoint: `POST /v1/webhooks/stripe`.

- Signature verification with `Stripe-Signature` header against `STRIPE_WEBHOOK_SECRET`.
- All handlers must be **idempotent** — Stripe retries. Use the Stripe event id as the dedup key in Redis (`stripe_event:{id}` for 24h).
- Persist every event in `webhook_events` table with `{ id, type, payload_json, received_at, processed_at, status, error }`. Re-process flag for ops.

Events to handle:

| Event | Action |
|---|---|
| `checkout.session.completed` | Create `orders` + `order_items`, issue `licenses`, write audit log, fire creator webhook `skill.purchased`, queue receipt email. |
| `payment_intent.succeeded` | Fallback / no-op if already processed. |
| `payment_intent.payment_failed` | Mark order `failed`, surface to buyer. |
| `customer.subscription.created` | Create `subscriptions` row, issue `licenses`, fire `subscription.created` webhook. |
| `customer.subscription.updated` | Update status (active → past_due → canceled), cancel_at_period_end. |
| `customer.subscription.deleted` | Mark `subscriptions.status = canceled`, expire `licenses` for that subscription at `current_period_end`. |
| `invoice.paid` | Extend license `current_period_end`. |
| `invoice.payment_failed` | Mark subscription `past_due`. After Stripe's retry schedule exhausts, status → `canceled` (handled by `customer.subscription.deleted`). |
| `charge.refunded` | Process refund (see below). |
| `account.updated` | Update Connect account flags. |

---

## Refunds

Flow:
1. Buyer clicks "Request refund" from `/library/{license-id}` (visible only within window + un-downloaded for one-time).
2. **`POST /v1/orders/{id}/refund`** — server checks eligibility, calls Stripe `refunds.create` with `reverse_transfer=true` so creator's transfer is clawed back.
3. Stripe fires `charge.refunded` → mark `orders.status = refunded`, revoke `licenses` (`status = revoked`), audit log.
4. Creator sees the refund in their dashboard with a "reason" if provided.

Partial refunds: deferred to Phase 5; out of scope here.

---

## Payout schedule

- Stripe Connect handles transfers immediately on charge.succeeded with `transfer_data.destination`. Stripe then disburses to the creator's bank per Stripe's payout schedule (default: rolling 2-day in US, longer in other countries).
- Our `payouts` table is a *reporting view* on top of Stripe data — we don't initiate transfers ourselves. Phase 1 just shows pending balance from Stripe API.
- Phase 2: persist payout history nightly via cron (call `Stripe::Payout::list` on each creator account, upsert).

---

## Subscription UX details

- "Cancel subscription" sets `cancel_at_period_end=true` in Stripe. Show buyer the date access ends.
- "Resume" before period end flips it back.
- Plan changes: not in Phase 2. Buyer must cancel + resubscribe to a different tier.

---

## Frontend

`/checkout?skill={id}`:
- Pre-flight: confirm skill state, price.
- Auth-gate: redirect to sign-in if anonymous, returnTo back to checkout.
- "Continue to payment" → POST checkout session, redirect to Stripe.
- Stripe Elements only used for subscription card collection inline (one-time goes to hosted Checkout).

`/settings/billing`:
- Payment methods (Stripe Customer Portal link).
- Active subscriptions: list with skill name, plan, next billing date, cancel/resume.
- Invoices: paginated list, link to Stripe-hosted PDFs.

---

## Acceptance — Phase 1

- [ ] Creator can complete Stripe Connect onboarding in test mode.
- [ ] Buyer can complete one-time purchase end-to-end with test card.
- [ ] License is issued via webhook, not via the success-URL redirect.
- [ ] Refund within 14 days (pre-download) succeeds and revokes license.
- [ ] All Stripe webhook events are persisted and idempotent.
- [ ] Platform fee math is unit-tested with rounding edge cases.

## Acceptance — Phase 2

- [ ] Buyer can subscribe monthly; license auto-renews on `invoice.paid`.
- [ ] Cancel-at-period-end works; license expires on the correct date.
- [ ] Freemium pair: free version surfaces upgrade CTA; paid version is purchasable.
- [ ] Past-due subscriptions show a "Update payment method" banner in `/settings/billing`.
- [ ] Creator's price change is blocked from going up without 14-day notice; going down is allowed instantly.
