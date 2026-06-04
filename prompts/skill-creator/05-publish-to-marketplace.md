# skill-creator — 05 Publish to Marketplace

**Phase:** 4
**Depends on:** all previous skill-creator/* prompts, `marketplace/05-trust-and-quality.md`, `marketplace/06-versioning-and-updates.md`, `marketplace/07-creator-dashboard.md`
**Parallel-safe with:** `02-import-from-projects.md`, `03-skill-config.md`, `04-test-and-preview.md`
**Status:** ready
**Owner:** _empty_

> The publish wizard is the hand-off from creator to marketplace. It is the **last chance** to catch problems and the **first impression** of the listing. Make both work.

---

## Scope

- The publish wizard (`/skills/{id}/publish`).
- Pre-publish checks (re-use validators, version diff, content scans).
- The "diff against previous version" view.
- Submission API and post-publish redirect.

---

## Wizard steps

A linear 5-step flow with a progress strip and "Back" allowed up to the final submit.

### Step 1 — Pre-flight checks

A checklist of automated checks; all must pass before "Next".

- [ ] **Validation** — `validate_file()` returns green on the compiled file.
- [ ] **Version diff** — `analyze_diff()` returns OK or `bump_required` with a suggested version (offer 1-click apply).
- [ ] **Content scans** — secret detection, link safety, malware placeholder.
- [ ] **Sandbox tested** — at least one sandbox run on the current draft against a required model marked "passed" (soft requirement; warn but allow override with explicit checkbox).
- [ ] **Cover image present**.
- [ ] **Stripe Connect ready** (only enforced for non-free pricing).
- [ ] **Slug unique** for this creator.

Each item is rendered with a status icon and (on failure) a "Fix this" link that deep-links into the appropriate editor.

### Step 2 — Diff against previous version (for non-first publishes)

If `based_on_version` is set:
- Side-by-side: prev skills.md (left, immutable) vs. new compiled skills.md (right).
- Inline highlights from the diff analyzer:
  - Frontmatter changes (added/removed/changed keys).
  - Body sections changed (line-level diff via `unified` + `diff`).
- Top: a summary banner: "Detected: 1 new input, 2 changed steps, no breaking changes. Suggested version: 1.3.0."
- "Use suggested" button updates `target_version` and re-validates.

For first publishes, skip this step.

### Step 3 — Listing preview

Render the actual marketplace listing as it'll appear:
- Skill card (used in browse rails).
- Detail page (without reviews, since none yet).
- "What's inside" preview (after server applies the `preview_body_md` truncation).
- Price card.
- AI requirements card.

Side-by-side: how it looks in light mode and dark mode.

This is a `<iframe>` pointing to `/preview/{id}?token=...` in the marketplace app, with a short-lived JWT that grants preview access. Or, simpler: render the components directly inside the creator app using the shared `packages/ui` primitives.

### Step 4 — Changelog & version notes

A focused editor for `changelog_md`:
- Pre-filled template (Added / Changed / Fixed for non-first releases).
- For breaking changes, a required "migration notes" field appears.
- Live preview.

### Step 5 — Confirm & publish

Final review:
- Skill name + tagline.
- Pricing summary with payout breakdown.
- Version + breaking-change flag.
- Reminder of marketplace terms (link, must-check box: "I confirm I own all rights to this content and grant the platform a license to distribute it").

Big "Publish" button. On click:
1. `POST /v1/creator/skills/{id}/publish` body: `{ version, changelog_md, breaking, force?: bool }`.
2. Server runs ALL pre-flight checks once more (defensive — UI might be stale).
3. If pass: create `skill_versions` row with `released_at=now()`, status moves per fast-track rules (`published` for fast-tracked, `pending_review` otherwise).
4. Update `skills.latest_version_id` if this is the highest semver and not yanked.
5. Audit log: `version.published`.
6. Fire creator webhook `version.published`.
7. Wipe the `skill_drafts.compiled_md` cache (force re-compile on next edit).
8. Returns the new version row.

Frontend redirects to `/dashboard/skills/{id}` (back in the marketplace app) with a success toast: "v1.3.0 published — currently in review" or "v1.3.0 is live!" depending on status.

---

## Force-publish path

Power users can bypass the soft "sandbox tested" check by ticking "I've tested elsewhere". This sets `force=true` on the publish call. Audit-logged. Cannot bypass hard validation failures.

---

## API

### `POST /v1/creator/skills/{id}/publish`

Body:
```json
{
  "version": "1.3.0",
  "changelog_md": "### Added\n- New input ...",
  "breaking": false,
  "force": false
}
```

Server logic:
1. Lock the draft row (`SELECT FOR UPDATE`).
2. Re-compile from `graph_json` + `frontmatter_json` (canonical).
3. Run `validate_file()`. Fail → 422.
4. Run `analyze_diff()` against prev version. Fail → 422 with suggested version.
5. Run content scans. Fail → 422.
6. Hash + sign the file. Write to immutable S3 path `skills/{skill_id}/{version}.md`.
7. Insert `skill_versions` row with `storage_url`, `content_hash`, `released_at`, `released_by`.
8. Decide status:
   - If creator is fast-tracked (verified + reputation thresholds) AND no flags from content scans → `skills.status = published`, version is publicly visible.
   - Else → `skills.status = pending_review`. Insert a row in `moderation_queue` (table introduced by `marketplace/05-trust-and-quality.md`).
9. Update `latest_version_id` only if version is the new max AND status is `published`.
10. Audit log + webhook fire.
11. Return:
```json
{
  "version": {...},
  "skill_status": "published" | "pending_review",
  "moderation_eta": "1-2 business days"  /* if pending */
}
```

### `POST /v1/creator/skills/{id}/unpublish` (admin or creator)

Sets `skills.status = unlisted`. Does NOT delete versions. Buyers retain access.

---

## Post-publish UX

In the marketplace app's `/dashboard/skills/{id}`:
- A banner if `pending_review` with ETA and a link to the moderation help doc.
- If `published`, the skill is now live; show the public URL and a copy button.
- A "Share" panel with pre-canned snippets:
  - Twitter/X share text + image.
  - LinkedIn share text.
  - Embed snippet (an `<iframe>` of the skill card for the creator's own site).

---

## Edge cases

- **Race condition: two publishes in flight.** The row lock + draft optimistic concurrency (ETag-based) prevents simultaneous publishes. Second one gets 409.
- **Same version published twice.** Server enforces unique `(skill_id, version)`. Returns 409 with suggestion to bump.
- **Creator yanks the draft mid-wizard.** Wizard refreshes state on each step; if draft no longer exists, redirect to home.
- **Network failure during publish.** The publish is transactional server-side; if step 7 fails, no version row exists, frontend retries.
- **Cover image missing in updated version** but present in older one: the listing keeps the older cover until the new one is uploaded. Wizard surfaces this as a warning, not a block.

---

## Acceptance

- [ ] Pre-flight checks render correctly for: a clean draft, a draft missing cover, a draft with secrets, an under-bumped version, an un-tested skill.
- [ ] Diff view renders for an updated skill against its previous version, with frontmatter and body changes highlighted.
- [ ] Listing preview renders identical to the actual marketplace detail page (verified with a Playwright snapshot test).
- [ ] Publish endpoint is idempotent under the row-lock + idempotency-key combo.
- [ ] Fast-tracked creator's publish lands directly in `published`; others land in `pending_review`.
- [ ] Creator webhook fires `version.published` with correct payload.
- [ ] E2E: build a skill from blank → sandbox-test → publish → see it on the public marketplace within seconds.
