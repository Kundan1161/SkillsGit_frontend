# marketplace — 04 Licensing & Delivery

**Phase:** 1
**Depends on:** `marketplace/00-overview.md`, `marketplace/03-pricing-and-checkout.md`, `02-data-model-core.md`, `shared/skills-md-spec.md`, `shared/auth.md`
**Parallel-safe with:** `01-discovery.md`, `02-skill-detail.md`
**Status:** ready
**Owner:** _empty_

> This is the moment of truth. Buyer paid. They want the file. Make it fast, secure, and obvious.

---

## Scope

- License issuance, expiration, revocation.
- The buyer's **Library** UI (`/library`, `/library/{license-id}`).
- File delivery: signed download URLs, watermarking.
- License resolution (what version does this license entitle you to right now?).
- Update notifications (delivery side; UX banners are in `06-versioning-and-updates.md`).

---

## License lifecycle

Already defined in `02-data-model-core.md`. Recap with delivery-specific behavior:

| Source | Granted when | Expires when | Max version |
|---|---|---|---|
| `one_time` | `checkout.session.completed` webhook | never (perpetual) | major version at purchase, e.g. `1.x` |
| `subscription` | `customer.subscription.created` webhook | `subscription.current_period_end` if not auto-renewed | unbounded (latest) |
| `free` | Buyer clicks "Get it" on a free skill | never | major version at grant, e.g. `1.x` |
| `freemium` | Same as free; paid sibling has its own license on purchase | same | same |
| `grant` | Admin or creator manually grants (e.g., reviewer copies) | configurable | configurable |

License `status` transitions:
- `active` (default on grant)
- `expired` (subscription period ended without renewal)
- `revoked` (refund processed, admin action, fraud)

### License resolution (the function buyers care about)

`resolve_version(license_id) -> SkillVersion | None`:

```python
def resolve_version(license: License) -> SkillVersion | None:
    if license.status != "active":
        return None
    candidates = (
        db.query(SkillVersion)
          .filter(SkillVersion.skill_id == license.skill_id)
          .filter(SkillVersion.released_at.is_not(None))
          .filter(SkillVersion.is_yanked.is_(False))
          .filter(SkillVersion.released_at >= license.granted_at - GRACE)  # creator-published-before counts too
    )
    if license.max_version:
        candidates = candidates.filter(SkillVersion.version_major <= max_major(license.max_version))
    return candidates.order_by(SkillVersion.released_at.desc()).first()
```

Implement `version_major` as a generated column on `skill_versions` (int derived from `version`). Or compute in app code consistently.

`GRACE` is small (e.g., 60s) to handle clock drift between Stripe and our server when a creator pushed a version moments before purchase.

---

## Library UI

### `/library` — list

Grid of skill cards the buyer owns, with a license badge per card:
- "Owned" (one_time, active)
- "Subscribed" (subscription, active)
- "Cancellation pending — ends {date}" (subscription, active with cancel_at_period_end)
- "Expired" (subscription, expired)
- "Free" (free license)

Filters: All / Subscribed / One-time / Free / Expired.
Sort: Recently active / Purchased newest / Name.

Each card shows: skill name, version available to the buyer (from `resolve_version`), creator handle, "Open" button.

### `/library/{license-id}` — license detail

Sections:

**Header** — skill name, creator chip, license type, status, granted date, expires date (if any).

**Download** — primary CTA "Download skills.md ({version})". One-click; produces a fresh watermarked file each time (so we can audit which copy leaked). Show "Last downloaded {time}".

**Version history (entitled)** — list of versions the buyer can access via this license. Each row: version, released date, changelog excerpt, "Download this version" link.

**Updates available** — if a newer version is out and within the license's `max_version` ceiling, banner: "v1.3.0 is out — get the latest". If outside the ceiling (e.g., v2.0.0 for a v1.x license), banner: "v2.0 is available — upgrade for $X" linking to the upgrade flow (see `06-versioning-and-updates.md`).

**Support** — if `support_tier != none`, show a "Contact creator" button. Routes to a creator-defined support link (email, Discord, ticketing) stored on the skill. Phase 1: simple `support_url` column on `skills`.

**Subscription management** (subscription only) — Manage plan, change payment method, cancel. Links to `/settings/billing`.

**Receipt / Refund** (one_time only) — "Download receipt PDF", "Request refund" if within window and not yet downloaded.

---

## Delivery

### `GET /v1/licenses/{id}/download`

- Auth: must be the license owner OR an admin.
- Re-validates: license active, version resolved, skill not removed.
- Generates a fresh signed URL pointing to S3 + a watermarked file generation pipeline (see below).
- Returns: `{ download_url, version, expires_at }` — URL expires in 60s.

### Watermarking pipeline

We don't serve a static immutable file. We generate the buyer-specific copy on demand.

1. Fetch the canonical `skill_versions.storage_url` from S3.
2. Re-inject the `distribution` frontmatter block.
3. Append an invisible HTML-comment watermark at EOF: `<!-- license:{license_id_hash} buyer:{buyer_id_hash} ts:{iso8601} -->`. Hashes are HMACs of the IDs with the platform key so we can match a leaked file back to its origin.
4. Write to a short-lived `s3://delivery/` prefix with a content-addressed key.
5. Return a presigned URL.
6. After 1 hour, a lifecycle policy deletes the short-lived object.

Implement in `apps/api/src/delivery/watermark.py`. Use `boto3` async wrapper.

For high-volume scenarios later we can stream the watermarked file directly from the API; for v1 the S3 round-trip is fine.

### `GET /v1/licenses/{id}/download/{version}`

Same as above but for an explicit version (used by version-history links). Server validates the version is within entitlement.

### API token downloads

API token holders hit:
```
GET /v1/licenses/{id}/download?format=raw
Authorization: Bearer skg_live_...
```

Returns the file body directly with `Content-Type: text/markdown; charset=utf-8` (skip the presigned-URL redirect; the file is already streamed). Same watermark applied.

---

## Audit log entries

Every download writes to `audit_log` with:
- `action: "license.downloaded"`
- `actor_id: <buyer>`
- `target_type: "license"`, `target_id: <license_id>`
- `metadata: { skill_id, version, user_agent, ip_hash }`

Useful for:
- Showing "Last downloaded" in the library.
- Refund eligibility check (one-time refund only if no `license.downloaded` rows).
- Investigating leaks.

---

## Notifications

- Email receipt on `order.placed` (Phase 1).
- Email when new version available within entitlement — daily digest, not per-event (use the same digest cron as saved-search alerts).
- In-app notification (lightweight: a column on `users` for `unread_count`, table `notifications(user_id, type, payload, read_at)`) — Phase 2. Don't build this in Phase 1.

---

## Edge cases

- **License revoked while a download is mid-flight:** signed URL still works for its 60s window; we accept this as residual risk.
- **Version yanked between resolution and download:** resolution refetches at download time; if yanked, returns next-best-available version.
- **Skill removed (`status=removed`):** library card shows "Skill unavailable" — no downloads. Refund eligibility extended automatically for one-time within last 30 days (admin can override).
- **Creator's Stripe Connect account disabled mid-subscription:** existing subscriptions continue (Stripe still charges, transfers fail and accumulate). Block new subscriptions immediately. Operations dashboard surfaces this.

---

## Acceptance

- [ ] License resolution returns the correct version for each scenario in unit tests (perpetual, capped, subscription active, subscription expired, yanked latest, etc.).
- [ ] Download flow returns a presigned URL that delivers a watermarked file. Two downloads by the same buyer produce files differing only in the watermark line.
- [ ] Library page renders the correct badge and CTA for each license type.
- [ ] Audit log captures every download.
- [ ] API token download path works against a real token from `shared/auth.md`.
- [ ] Refund flow revokes the license and blocks subsequent downloads.
- [ ] E2E: buy a skill → land in library → download → file passes `validate_file()` and contains the watermark comment.
