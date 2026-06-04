# marketplace — 05 Trust & Quality

**Phase:** 2
**Depends on:** `marketplace/00-overview.md`, `02-data-model-core.md`, `marketplace/04-licensing-and-delivery.md`, `shared/skills-md-spec.md`
**Parallel-safe with:** `06-versioning-and-updates.md`, `07-creator-dashboard.md`
**Status:** ready
**Owner:** _empty_

> Trust is the moat. A buyer who's burned once doesn't come back. We invest in four mechanisms: **reviews**, **sandbox previews**, **moderation**, and **automated quality checks**.

---

## Scope

- Review submission, listing, replies, helpful votes.
- Rating math and recalculation.
- Sandbox preview runtime (try-before-you-buy).
- Manual moderation queue.
- Automated publish-time quality checks (extends `shared/skills-md-spec.md`).
- Creator verification (verified badge).

---

## Reviews

### Permission rules

- Only a buyer with an `active` or `expired` license on the skill can review. (Expired subscribers count.)
- One review per buyer per skill. Editable; edits update `updated_at` and surface "edited" badge.
- Cannot review your own skill.
- Cannot review while a refund is in progress.

### Submission

**`POST /v1/reviews`** body: `{ skill_id, rating: 1..5, title?, body_md }`. Returns the review.

**`PATCH /v1/reviews/{id}`** body: partial. Author or admin only.

**`DELETE /v1/reviews/{id}`** — author can delete their own; admin can hide via moderation flow instead.

### Listing

**`GET /v1/skills/{id}/reviews`** — cursor-paginated, sort options:
- `helpful` (default — by `helpful_count` desc, fallback `created_at` desc)
- `newest`
- `oldest`
- `rating_high` / `rating_low`

Filter: `rating={1..5}` to show only N-star reviews.

Response item:
```json
{
  "id": "uuid",
  "rating": 5,
  "title": "Saved me hours",
  "body_md": "...",
  "author": {
    "handle": "buyer-handle",
    "display_name": "Sam",
    "avatar_url": "..."
  },
  "is_verified_purchase": true,
  "helpful_count": 12,
  "viewer_voted_helpful": false,
  "created_at": "...",
  "updated_at": "...",
  "creator_reply": {
    "body_md": "Thanks Sam!",
    "created_at": "..."
  }
}
```

### Helpful votes

- Logged-in buyer who is NOT the author can mark a review "helpful". One vote per user per review; toggling removes the vote.
- Table: `review_helpful_votes(review_id, user_id, created_at)` with composite PK.
- Denormalize `helpful_count` on `reviews`.

### Creator replies

- Each review has at most one reply by the skill's creator (or co-author/maintainer).
- **`POST /v1/reviews/{id}/reply`** body `{ body_md }`. **`PATCH`** / **`DELETE`** similar.
- Reply is visible on the public detail page nested under the review.

### Aggregate ratings

- `skills.rating_avg` and `skills.rating_count` are denormalized.
- Update on `review.created`, `review.updated`, `review.deleted`, `review.hidden`.
- Recompute job runs nightly to correct drift.
- Display threshold: don't show `rating_avg` publicly until `rating_count >= 3`. Show "Not enough reviews" instead.

### Anti-abuse

- Each review goes through automated checks before publishing:
  - Length: at least 10 chars body or 5 chars title.
  - Profanity filter: soft block with warning (`flagged_for_review = true`) — show in moderation queue but don't block publish.
  - Sentiment-vs-rating mismatch heuristic (Phase 5; flag only).
  - Same-IP cluster within 24h: rate-limit.
- Buyers can **report** a review with a typed reason (`spam`, `fake`, `abusive`, `off-topic`, `other`). Two reports send it to moderation queue.

---

## Sandbox preview

> Buyers click "Try in sandbox" on the detail page. They paste sample inputs, pick a model, and see the skill's output before buying. This is the **single biggest trust lever** on the platform.

### Rules

- Requires login (creates an account if anonymous click).
- 3 free runs per skill per buyer per 24h; tracked in Redis.
- Sandbox runs use a **redacted preview** of the skill body — same "What's inside" content shown on the detail page, NOT the full skill. (Otherwise we'd just be giving the skill away.) Creators can opt-in to "full sandbox" if they accept the leak risk; default off.
- Buyer brings their own AI provider credentials (Phase 2 starting point) OR pays a small per-run fee using platform credits (Phase 3+). Default Phase 2: BYO credentials.

### Flow

1. **`POST /v1/skills/{id}/sandbox/sessions`** body: `{ model_id, provider_key_ref? }` — `provider_key_ref` points to a `provider_keys` table where the buyer has stored their Anthropic/OpenAI/Gemini API keys (encrypted with libsodium sealed boxes, key in env).
2. Server constructs the prompt: redacted skill body + buyer's inputs.
3. Server proxies the call to the chosen model's API. Stream the response back over SSE.
4. Server logs `sandbox_runs` row: `{ id, user_id, skill_id, model_id, status, started_at, finished_at, tokens_in, tokens_out, error }`. Don't store the prompt or output — privacy by default. (Logging metadata only.)

### Provider key management

- **`GET /v1/me/provider-keys`** — list keys (returns only `id`, `provider`, `last_used_at`).
- **`POST /v1/me/provider-keys`** — `{ provider: claude|openai|gemini, key }` — encrypts and stores.
- **`DELETE /v1/me/provider-keys/{id}`**.
- Keys are scoped to sandbox-only. Never used elsewhere. Stored encrypted-at-rest with platform key in env (libsodium SecretBox). Decrypted in-memory, never logged.

### UI

On the skill detail page, "Try in sandbox" opens a `Sheet`:
- Step 1: Pick a model (from `ai.required_models` and `ai.compatible_models`).
- Step 2: Pick a provider key OR add one inline.
- Step 3: Enter inputs (form generated from `inputs[]` in frontmatter — text, file upload, choice, etc.).
- Step 4: Run. Streaming output in a chat-like panel. Token count + estimated cost shown at the end.

---

## Moderation

### Queue

Pages:
- `/admin/moderation` — list of flagged content: pending publishes, reported reviews, reported skills, refund-fraud watchlist.
- `/admin/skills/{id}/review` — moderator approves/rejects publishes.
- `/admin/reviews/{id}` — hide/restore.
- `/admin/users/{id}` — warn / suspend.

### Actions

- **Publish review** (auto): runs `validate_file()` + content scans (see below). On clean pass, mark skill version `published`, transition `skills.status` from `pending_review` to `published`.
- **Reject publish**: send creator an email with a typed reason. Skill stays `pending_review` with `rejection_reason` on the version.
- **Hide review**: sets `status=hidden`. Author is emailed. Aggregate rating recomputed.
- **Suspend user**: blocks login, marks all their skills `unlisted`. Audit-logged.

### Action log

A moderation action table: `moderation_actions(id, actor_admin_id, target_type, target_id, action, reason, metadata, created_at)`. All entries also surface in `audit_log` but here we keep moderator-friendly columns.

---

## Automated publish-time checks

When a creator publishes a new version, in order:

1. **Schema validation** — `validate_file()` from `shared/skills-md-spec.md`. Hard fail.
2. **Hash & sign** — compute content_hash, inject distribution block.
3. **Forbidden content scan** — regex for secrets (`api[_-]?key`, `sk-`, `pk-`, `BEGIN PRIVATE KEY`, real-looking CC + Luhn check). Hard fail.
4. **Malware scan** (placeholder) — call ClamAV or skip in Phase 2; ship `apps/api/src/skills/malware.py` with a no-op + TODO for Phase 5.
5. **Link safety** — extract URLs, check each against a small denylist (`google-safebrowsing` API in Phase 3, denylist file in Phase 2).
6. **Self-referential pricing check** — body must not contradict frontmatter (e.g., body says "this skill is free" but `license_type=one_time`). Heuristic regex; flag for manual review on hit.
7. **Versioning rules** — compared to previous version: no `required_models` removal that drops a model in use by an active license; no major version skip (1.x → 3.0 rejected); patch/minor must not change inputs/outputs schema.
8. **Cooldown** — a single skill can't publish more than 5 versions per day. Throttle to slow runaway iteration.

If all pass, status moves directly to `published`. If anything is in "flag for review", status moves to `pending_review` and the moderation queue picks it up.

Creators can opt their account into "fast track" once they hit reputation thresholds (verified + ≥ 4.5 avg rating + ≥ 50 sales). Fast-track skips manual review on minor/patch versions.

---

## Creator verification

Manual program in Phase 2 — no public application form.

- Admin grants `users.is_creator_verified=true` via `/admin/users/{id}`.
- Triggers: identity check (Stripe Identity in Phase 3), portfolio review, 30+ sales with ≥ 4.0 avg.
- Verified badge appears on creator chip + detail page + creator profile.
- Verified creators bypass the publish cooldown limit (still subject to fast-track rules above).

---

## Frontend

- `apps/web-marketplace/components/reviews/`: `ReviewItem`, `ReviewList`, `ReviewForm`, `RatingStars`, `RatingBreakdown` (5-star histogram).
- `apps/web-marketplace/components/sandbox/`: `SandboxSheet`, `ProviderKeyPicker`, `InputFormFromSchema`, `StreamingOutput`.
- `apps/web-marketplace/app/admin/`: moderation queue, review action UI. Server-only, gated by `is_admin`.

---

## Acceptance

- [ ] Review submission gated by license; one per buyer per skill enforced.
- [ ] Helpful votes work; counts update in real-time on the page.
- [ ] Aggregate `rating_avg` updates within seconds of a new review.
- [ ] Sandbox preview runs against Claude with a buyer-provided API key; streams output.
- [ ] At least 5 automated check failures are covered in tests (secret leak, malformed semver, breaking input schema change, etc.).
- [ ] Moderation queue surfaces pending publishes; admin can approve/reject with audit trail.
- [ ] Verified badge renders on profile + cards + detail page when granted.
