# marketplace — 06 Versioning & Updates

**Phase:** 2
**Depends on:** `marketplace/00-overview.md`, `02-data-model-core.md`, `marketplace/04-licensing-and-delivery.md`, `shared/skills-md-spec.md`
**Parallel-safe with:** `05-trust-and-quality.md`, `07-creator-dashboard.md`
**Status:** ready
**Owner:** _empty_

> Skills evolve. The ecosystem only works if updating is **safe for creators** and **valuable for buyers**. Semver is the contract; UX is the proof.

---

## Scope

- Semantic versioning policy (enforced at publish).
- Major-version upgrade flow for one-time buyers (paid upgrade).
- "What's new" digest UX for active subscribers.
- Yanking versions safely.
- Migration helpers when a creator changes inputs/outputs.

---

## Semver enforcement

The validator already checks well-formedness (see `shared/skills-md-spec.md`). This prompt adds **behavioral** checks across versions.

### Rules

For a new version `N` against the previous published version `P`:

| Change | Patch (`x.y.Z`) | Minor (`x.Y.0`) | Major (`X.0.0`) |
|---|---|---|---|
| Body text edits | ✅ | ✅ | ✅ |
| Add an optional input | ❌ → must minor | ✅ | ✅ |
| Add a required input | ❌ | ❌ → must major | ✅ |
| Remove an input | ❌ | ❌ → must major | ✅ |
| Rename an input | ❌ | ❌ → must major | ✅ |
| Add an output | ❌ → must minor | ✅ | ✅ |
| Remove or rename an output | ❌ | ❌ → must major | ✅ |
| Add `required_models[]` entry | ❌ → must minor | ✅ | ✅ |
| Remove `required_models[]` entry | ❌ | ❌ → must major | ✅ |
| Add `tools_required[]` entry | ❌ | ❌ → must major | ✅ |
| Remove `tools_required[]` entry | ❌ | ✅ | ✅ |
| Increase `min_context_tokens` | ❌ | ❌ → must major | ✅ |
| Reduce `min_context_tokens` | ❌ | ✅ | ✅ |
| Body adds `## How to apply` step | ✅ | ✅ | ✅ |
| Body removes `## How to apply` step that was load-bearing | ⚠️ flag for review | ⚠️ | ✅ |
| `license_type` change | ❌ (always blocked — Phase 1 rule) | ❌ | ❌ |
| `pricing` change | governed separately (see `03-pricing-and-checkout.md`) | | |

Implement in `apps/api/src/skills/version_diff.py` as `analyze_diff(prev: SkillVersion, next_frontmatter, next_body) -> DiffReport`. The publish endpoint runs this before insertion and returns a structured error when violated, including a suggested correct version number.

### "Bump version for me"

When a creator submits a new version and we detect a constraint violation, the API responds with a helpful 422 like:

```json
{
  "error": {
    "code": "version.bump_required",
    "message": "This change requires a minor version bump.",
    "details": [
      {
        "field": "version",
        "code": "minor_bump_required",
        "message": "You added an optional input; bump to 1.3.0 (you submitted 1.2.5).",
        "suggested_version": "1.3.0"
      }
    ]
  }
}
```

Frontend offers a one-click "Use suggested version" button.

---

## Major-version upgrades — buyer side

When a creator releases version `2.0.0` of a skill, existing one-time buyers (license `max_version = "1.x"`) are NOT auto-entitled. We run an upgrade flow.

### Upgrade pricing

- Creator sets an `upgrade_price_cents` field on the new major version (defaults to 50% off the current full price).
- Upgrade is its own one-time purchase that produces a NEW license capped at the new major.
- Old license remains valid for `1.x` — buyer can keep using the old major or pay to move forward.

### UX

On `/library/{license-id}` and the skill detail page, banner:
> **v2.0 is out** with [breaking changes] — upgrade for $9 (50% off).
> [What's new] [Upgrade now] [Stay on v1]

"Stay on v1" dismisses the banner for 30 days (per-buyer cookie + `notification_dismissals` table).

### Subscribers

Subscribers always have `max_version = null`. No upgrade flow. They get `2.0.0` automatically. The "What's new" digest highlights it.

### Free / freemium

Free license is `max_version = "1.x"` like one-time. v2 of a free skill is its own listing decision by the creator — they can release as free or paywall it. (Document this in creator UX.)

---

## Update notifications

### Digest (default)

Daily cron at 09:00 UTC. For each buyer:
1. Find skills they have active licenses on.
2. For each, check if a new version was released since their `last_notification_seen_at` for that skill (table `user_skill_state(user_id, skill_id, last_notification_seen_at)` — define here).
3. If anything new, send one email with up to 10 entries: skill name, new version, changelog excerpt, link to detail page or library.
4. Update `last_notification_seen_at`.

Also a "new release" banner in `/library` driven by the same data, dismissable per skill.

### Per-skill notifications (opt-in)

In `/settings/notifications`, buyer can flip per-skill setting to "Notify on every release". Sends individual emails when version published. Off by default.

### Creator-side webhook

Already covered in `shared/api-conventions.md` (Webhooks). Specific event: `version.published` fires for every public version release on a creator's skills. Useful for creators wiring their own marketing.

---

## Yanking a version

A creator (or admin) can yank a published version if they find a bug. Yanking does NOT delete; it sets `is_yanked=true` with a typed reason.

Effects:
- New licenses do not see the yanked version when resolving.
- Existing licenses pointing to the yanked version are *re-resolved* to the latest non-yanked version within their entitlement.
- The version still appears in version history with a strike-through and yank reason.
- Audit log: `version.yanked` with reason.

UI:
- Creator dashboard → skill versions list → "Yank" button per version with required reason field.
- Admin can yank any version with the same flow.

**`POST /v1/skills/{id}/versions/{version}/yank`** body `{ reason }`. **`POST /v1/.../unyank`** to reverse (admin-only).

---

## Migration helpers (when inputs/outputs change)

For major version releases that change input/output schemas, the creator can author a **migration note** in the changelog. This is a markdown field but rendered with a special "Migration steps" header in the buyer's update banner.

We do NOT auto-migrate buyer code — buyers integrate skills into their own agents and we can't reach in. We just communicate clearly.

---

## Frontend

- `apps/web-marketplace/components/versioning/`:
  - `VersionTimeline` (used on detail page; defined in `02-skill-detail.md` — extend here for changelog rendering, yank state).
  - `UpdateBanner` — shown on library card or detail page when an update is available within entitlement OR upgrade is offered.
  - `UpgradeFlowSheet` — payment summary for major-version upgrade, reuses checkout from `03-pricing-and-checkout.md`.
- Creator-side:
  - `VersionEditor` in dashboard with diff preview, "bump version for me" helper.
  - `YankDialog` with required reason.

---

## Acceptance

- [ ] `analyze_diff()` correctly classifies the version-bump matrix above (covered by unit tests, 1 per row).
- [ ] Publish flow rejects under-bumped versions with the "suggested_version" payload.
- [ ] Major-version upgrade purchase creates a NEW license; old license remains.
- [ ] Yank flow re-resolves dependent licenses to the next-best version.
- [ ] Daily digest emails fire correctly against seeded data.
- [ ] Subscribers automatically receive v2.0 on release; one-time buyers see upgrade banner.
- [ ] All `version.*` events appear in the audit log and fire creator webhooks.
