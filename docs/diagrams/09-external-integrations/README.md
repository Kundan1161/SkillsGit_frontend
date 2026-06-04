# 09 — External integrations

Diagrams of every third-party integration the platform depends on:
Stripe (Connect for payouts + webhooks for state machine), Anthropic
Claude (capture LLM + demo CLI), S3-compatible object storage (MinIO
locally, Cloudflare R2 in prod), and the inbound Stripe webhook
dispatch.

Source: shipped code under `apps/api/src/billing/`,
`apps/api/src/webhooks/`, `apps/api/src/storage/`,
`apps/api/src/capture/`, `apps/api/src/core/anthropic.py`, and
`apps/api/scripts/demo_devops_agent.py` — all read directly so the
diagrams reflect what's actually wired up.

## Files

### [`stripe-connect.drawio`](stripe-connect.drawio) — buyer-pays-creator flow

End-to-end sequence: creator's one-time Stripe Connect Express
onboarding → buyer's `POST /v1/checkout/sessions` (with the 409
`persona.requires_parent_occupation` gate inline) → `assert_skill_purchasable`
pre-flight → Stripe Checkout Session creation with `transfer_data.destination
= creator.stripe_connect_account_id` and `application_fee_amount =
compute_fee(amount)` → buyer redirected to Stripe-hosted checkout →
on payment, Stripe webhook `checkout.session.completed` fires → service
creates Order + OrderItem rows, issues a one-time License, writes
audit log → buyer's `/checkout/success` page polls `/finalize` for the
license id and redirects to `/library`. Money settlement: application
fee lands in platform's Stripe balance; remainder transfers to the
creator's connected account per their Express payout schedule.

### [`anthropic-claude.drawio`](anthropic-claude.drawio) — two Claude call sites

Capture LLM (`src/capture/llm.py`) — neuron-draft extraction from a
capture session; stub-swap via `SKG_CAPTURE_LLM_STUB=1` returns
`tests/stubs/llm.StubAnthropicClient` for hermetic CI runs; production
uses `_RealAnthropicClient` against `settings.SKG_CAPTURE_LLM_MODEL`
(`claude-sonnet-4-6` default); Redis-backed monthly quota (10/mo per
creator, refunded on extract failure). Demo CLI
(`scripts/demo_devops_agent.py`) — one-shot answer with attribution
via the shared `core/anthropic.py:get_async_client()` factory;
`--snapshot-only` bypasses the API call entirely. Both paths share the
single platform `ANTHROPIC_API_KEY` for MVP; BYOK (per-creator keys)
is Cycle 2 work per ADR-008.

### [`s3-object-layout.drawio`](s3-object-layout.drawio) — bucket key structure

Single bucket (`settings.S3_BUCKET`, default `"skillsgit-skills"`).
Prefix layout:

- `skills/{skill_id}/{version}.md` — canonical skill bodies
  (note: code uses `{version}.md` directly, NOT `{version}/body.md`
  as the spec brief suggested — see drift #2)
- `covers/{skill_id}/cover.{ext}` — skill cover images
- `vaults/{skill_id}/{version}/{content_hash}.zip` — built occupation
  + persona zips (same path shape; `kind` is on the skill row, not the
  path); immutable per content_hash
- `delivery/vaults/{nonce}.zip` — composed buyer bundles
  (`nonce = secrets.token_urlsafe(12)`); 1h lifecycle (target — not
  wired in MinIO yet)
- `attachments/captures/{capture_session_id}/{filename}` — capture
  uploads (survives finalize)
- `attachments/personas/{persona_id}/...` — post-finalize copies
  (best-effort server-side copy during finalize)

Includes the backend swap (`S3Storage` aioboto3 vs `InMemoryStorage`
test dict, both behind `get_storage()`).

### [`webhook-flow.drawio`](webhook-flow.drawio) — inbound Stripe webhook

Sequence for `POST /v1/webhooks/stripe`:

1. Read raw body (do NOT json-parse before HMAC verify)
2. Verify signature via the Stripe SDK against `STRIPE_WEBHOOK_SECRET`
   (test mode skips verification for unit-test convenience)
3. Persist `webhook_events` row keyed on Stripe's `event.id`
   (re-deliveries dedup at the SELECT-then-INSERT layer)
4. Dispatch on `event.type` — handlers cover
   `checkout.session.completed` (Order + License issuance),
   `payment_intent.payment_failed` (mark Order FAILED),
   `charge.refunded` (Order REFUNDED + revoke spawned Licenses),
   `account.updated` (sync creator's `payouts_enabled`),
   `payment_intent.succeeded` (no-op; license already issued)
5. Unhandled types (`subscription.*`, `invoice.*`) → row stays
   RECEIVED, Stripe gets 200; Cycle-2 handlers will pick these up
6. Handler exception → row marked FAILED, 500 returned so Stripe
   retries; idempotency at INSERT layer makes retries safe

## Spec vs code drift summary (also in the per-diagram comments)

- **Drift 1 (compose 202/200):** spec §4 promises `202 JobAccepted`
  then `200 VaultDownloadResponse` on cache hit; code returns `200`
  on both paths (synchronous inline compose; cold path ~1-5s at MVP
  scale). Documented in `06-composition-delivery/compose-sequence.drawio`.
- **Drift 2 (S3 path shape for skill bodies):** spec brief listed
  `skills/{skill_id}/{version}/body.md`; code uses
  `skills/{skill_id}/{version}.md` (no `/body.` suffix). Code wins.
- **Drift 3 (vault download endpoint body field):** spec §4 listed
  the request body as `{include_personas?: [persona_license_id...]}`;
  code uses `{include_persona_license_ids?: [...]}`. Minor naming.
- **Drift 4 (one-time license `granted_at` filter):** spec implies
  one-time licenses cap candidates by `released_at > granted_at`;
  shipped `resolve_version` does NOT actually apply that filter (the
  buyer gets free bug-fixes within their major-version cap). The
  behavioural difference is in `06-composition-delivery/license-resolution.drawio`.

## How to view

Every file in this folder is a `.drawio` file. Open it in the draw.io
desktop app or at [app.diagrams.net](https://app.diagrams.net), or
render it inline in VS Code with the
[Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)
extension. See [`docs/diagrams/README.md`](../README.md#how-to-view-these-diagrams)
for the full guide and the two flavours of `.drawio` in this repo
(native mxgraph vs Mermaid-embedded).

## Env-var quick reference

| Variable | Used by | Purpose |
|---|---|---|
| `STRIPE_SECRET_KEY` | `billing/stripe_client.py` | Server-side Stripe SDK auth |
| `STRIPE_WEBHOOK_SECRET` | `webhooks/router.py` | Verify `Stripe-Signature` header |
| `PLATFORM_FEE_PERCENT` | `billing/fees.py:compute_fee` | Application fee on every checkout |
| `S3_ENDPOINT` / `S3_ACCESS_KEY` / `S3_SECRET_KEY` / `S3_BUCKET` | `storage/s3.py:S3Storage` | aioboto3 client config |
| `ANTHROPIC_API_KEY` | `core/anthropic.py` + `capture/llm.py` | Platform Claude key (MVP) |
| `SKG_CAPTURE_LLM_MODEL` | `capture/llm.py` + `core/anthropic.py:resolve_model` | Default Claude model |
| `SKG_CAPTURE_LLM_STUB` (and legacy `SKG_LLM_STUB`) | `capture/llm.py:is_stub_enabled` | Swap real client for `tests/stubs/llm.py` |
| `SKG_CAPTURE_QUOTA_PER_MONTH` | `capture/quota.py` | Free-tier capture cap (default 10) |
| `PLATFORM_HMAC_KEY` | `delivery/watermark.py` | HMAC ids in per-buyer watermark |

## Source pointers

| Topic | File |
|---|---|
| Checkout router (+ persona 409 gate) | `apps/api/src/billing/router.py:create_checkout_session` |
| Checkout service (Stripe API call) | `apps/api/src/billing/service.py:create_checkout_session` |
| Stripe Connect onboarding | `apps/api/src/billing/service.py:start_connect_onboarding` |
| Persona entitlement check | `apps/api/src/personas/service.py:check_persona_checkout_entitlement` |
| Stripe SDK wrapper | `apps/api/src/billing/stripe_client.py` |
| Webhook router | `apps/api/src/webhooks/router.py:stripe_webhook` |
| Webhook dispatcher | `apps/api/src/webhooks/service.py:process_event` |
| Checkout-completed handler | `apps/api/src/webhooks/service.py:_on_checkout_session_completed` |
| Charge-refunded handler | `apps/api/src/webhooks/service.py:_on_charge_refunded` |
| Account-updated handler | `apps/api/src/webhooks/service.py:_on_account_updated` |
| Webhook events dedup table | `apps/api/src/billing/models.py:WebhookEvent` |
| One-time license issuance | `apps/api/src/billing/service.py:issue_one_time_license` |
| Shared Anthropic factory | `apps/api/src/core/anthropic.py` |
| Capture LLM wrapper | `apps/api/src/capture/llm.py` |
| Capture LLM stub | `apps/api/tests/stubs/llm.py` |
| Capture quota | `apps/api/src/capture/quota.py` |
| Storage wrapper | `apps/api/src/storage/s3.py` |
| Skill body storage keys | `apps/api/src/skills/service.py:_skill_storage_key` + `_cover_storage_key` |
| Vault build storage keys | `apps/api/src/vault/builder.py` (around line 1016 / 1200) |
| Composed bundle storage keys | `apps/api/src/vault/composer.py:_build_and_record` |
| Capture attachment paths | `apps/api/src/capture/service.py` + `tests/test_service.py:test_attachment_finalize` |
| Spec — pricing + checkout | `prompts/marketplace/03-pricing-and-checkout.md` |
| Spec — webhooks | same file, "Webhooks" section |
| ADR-008 — capture LLM key | `team/decisions.md` |
| ADR-018 — demo CLI is loader, not runtime | `team/decisions.md` |
