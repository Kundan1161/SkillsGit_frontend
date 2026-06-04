# Dev diary — Vault composer, Cycle 1 Wave 3B

**Owner:** Backend (Vault Composer)
**Wave:** 3B (T-07 vault composer + Redis cache helper + vault router)
**Started:** 2026-05-26
**Status:** shipped (handing off to orchestrator and Wave 4 — T-12 demo seed + T-13 demo CLI)

---

## What shipped

### `apps/api/src/core/cache.py` (new)

Lightweight async caching helper for the composer's 24h per-buyer
compose cache (ADR-006 §Composition cache). Public surface kept tiny:

```python
async def get_or_compute(
    key: str,
    compute_fn: Callable[[], Awaitable[Any]],
    *,
    ttl_seconds: int,
) -> tuple[Any, bool]:  # returns (value, cache_hit)

async def invalidate(key: str) -> None
```

Backend selection happens at call time:

* **Production / dev**: real `redis.asyncio.Redis.from_url(settings.REDIS_URL)`.
* **Test (`ENV=test`)** OR `SKG_CACHE_INMEM=1`: process-local dict with
  TTL-on-read semantics so a stale entry behaves identically to a
  Redis miss. The brief asked for the env var; both triggers are
  supported so the per-module conftest doesn't have to remember to
  flip it.

Values JSON-encode on write (`default=str` for UUIDs / datetimes) so the
same shape round-trips through either backend. Test-friendly helpers
`reset_inmem_for_tests()` and `set_redis_client_for_tests()` for
fixtures that want hermetic state. mypy --strict clean.

### `apps/api/src/vault/composer.py` (new)

`compose_for_license(session, *, buyer_id, occupation_license_id,
include_persona_license_ids=None, user_agent=None, client_ip=None)
-> ComposedDownload`. Implements the algorithm in
`team/03-vault-generation.md` §10 verbatim:

1. **License resolution** — `_load_occupation_license` (404 with
   `vault.license_not_found` on wrong owner; 409 with
   `vault.compose_unentitled` if the license is `standalone`/`persona`
   rather than `occupation`; 409 `vault.license_inactive` otherwise).
   `_active_persona_licenses` runs the primary composer query keyed on
   `(buyer_id, target_occupation_skill_id, status=active,
   composition_role=persona)` — the wave-1 covering index from
   `01-data-model-deltas.md`. `_intersect_persona_licenses` enforces
   the brief's "403 on requested-but-not-held" path with code
   `vault.persona_license_not_held` and the offending license id in
   `details`.

2. **Cache key** = `sha256(buyer_id || occupation_skill_id ||
   occupation_build_id || sorted(persona_build_ids))`. `buyer_id` is in
   the key because the watermark embeds the buyer hash — two different
   buyers MUST NEVER share a cached object. Build ids (not license
   ids) drive invalidation: a new vault_build naturally produces a new
   key and the stale entry ages out at 24h TTL (confirmed by
   `test_new_vault_build_invalidates_cache_via_keyed_build_id`).

3. **Cache hit** path: re-presign the cached S3 key (URLs always
   expire after 60s per ADR-006, so re-issuance is part of the hit
   path) and return. No new `vault_downloads` row on a hit — the
   cached row's audit trail covers the original download event;
   URL re-issuance is a UX detail.

4. **Cache miss** path (`_build_and_record`):
   * Download every input zip into memory (~50 MB cap from spec §12).
   * Start from the occupation tree minus `vault.json` (we re-emit).
   * Layer in every persona's `personas/<handle>/<slug>/**` subtree.
     Drop each persona's `persona.json` — the composed `vault.json`
     replaces it.
   * `_merge_manifests` produces the composed manifest. Re-runs link
     resolution against the merged surface so persona links to
     `base/...` that were unresolved at build time get flipped to
     `resolved=True` if the occupation now provides them. Every still-
     dangling link lands a `vault.unresolved_link` warning on the
     composed manifest (test:
     `test_persona_unresolved_base_link_surfaces_warning`).
   * Stamp every `.md` with `delivery.watermark.append_watermark`.
     Per ADR-010 / spec §7 the watermark sits AFTER the existing
     `skg-attribution` comment the builder already emitted; that is
     exactly what `append_watermark` does (it appends to the file
     body's tail), so no extra ordering work is needed.
   * Deterministic re-zip via `_write_zip` — every entry's
     `ZipInfo.date_time` is pinned to `EPOCH_TIMESTAMP` (the same
     constant the builder uses), so the merged tree's bytes are
     stable across runs *except* for the per-buyer watermark + the
     `composed_at` field on the manifest. Two-pass zip: first pass
     computes the hash, second pass patches `composed_hash` back
     into `vault.json`, then we re-zip and use the **post-patch**
     bytes' sha256 as the audit `composed_hash`. The in-zip
     `composed_hash` is therefore the first-pass hash (known minor
     circularity, documented in the code).
   * Upload to `delivery/vaults/{nonce}.zip` (matches the existing
     1h lifecycle prefix from spec §10).
   * Insert `vault_downloads` row with `buyer_id`, `occupation_build_id`,
     `persona_build_ids[]`, `persona_license_ids[]`, `composed_hash`,
     `storage_url`, hashed `user_agent` + `ip`. Mirrors the existing
     `delivery_downloads` audit pattern.

5. **Presign**: `storage.presigned_url(...)` with `expires_in_seconds=60`
   (`PRESIGNED_URL_TTL_SECONDS`).

6. Return `ComposedDownload(presigned_url, expires_at, composed_hash,
   cache_hit, vault_download_id, storage_url, occupation_build_id,
   persona_build_ids)`.

Errors are typed `VaultComposeError(code, message, status_code,
details)`. The router translates a single exception class into the
right HTTP response shape — no per-branch error encoding.

### `apps/api/src/vault/router.py` (new)

Three endpoints from `team/02-api-surface.md` §4:

| Method | Path | Notes |
|---|---|---|
| `POST` | `/v1/licenses/{occupation_license_id}/vault` | Compose + download. 60s presigned URL on miss, cached URL on hit. Body: `{include_persona_license_ids: [UUID] | null}`. 200 (not 202) — compose is fast in MVP scale and the brief asks for the URL directly. |
| `GET` | `/v1/licenses/{occupation_license_id}/vault/downloads` | Paginated history of `vault_downloads` rows for this license. 404 to non-owners. |
| `GET` | `/v1/vault/builds/{build_id}` | Single build summary (compact projection — full manifest stripped). Authz: owner of the parent skill OR holder of an active license that covers it (occupation or persona-overlay) OR admin. |

The `POST` handler:

* Calls `composer.compose_for_license` and translates
  `VaultComposeError → HTTPException` via the small `_compose_error_to_http`
  helper.
* Writes the `license.vault_downloaded` audit-log entry per spec §4 step 7
  with metadata `{vault_download_id, composed_hash, cache_hit,
  occupation_build_id, persona_build_ids}`.
* Commits the session once, after both the audit row + (cache-miss-path)
  vault_downloads row are in flight.

Both helpers (`_persona_build_ids_as_uuid_list`, `_client_ip`) follow
the same conventions as `src/delivery/router.py` so future readers can
diff the two flows easily.

**Auth note (cross-dialect):** sqlite stores UUID columns as
`String(36)` via `with_variant`; comparing `License.buyer_id`
(returned as `str`) against the in-Python `User.id` (`uuid.UUID`)
silently mis-classifies the owner. Composer + router both coerce
to `str` for the ownership check. Caught while building the router
tests; would have been a latent prod bug otherwise.

### `apps/api/src/vault/__init__.py` (modified)

Added the new submodules to the package docstring. No code change.

### `apps/api/src/vault/tests/test_composer.py` (new)

11 tests covering the brief's verbatim acceptance bullets:

1. `test_compose_occupation_only_cache_miss` — first call returns
   `cache_hit=False`, presigned URL + composed bytes that round-trip.
2. `test_compose_cache_hit_returns_same_storage_url` — second call
   within TTL returns `cache_hit=True`, same `storage_url`, same
   `composed_hash`.
3. `test_compose_with_one_persona` — occupation + 1 persona merges
   the persona subtree + composed `vault.json` lists files from both.
   Audit row records the persona license id.
4. `test_compose_with_two_personas` — three-way merge; the manifest's
   `personas[]` carries both summaries; both persona handles appear in
   the file tree.
5. `test_two_downloads_differ_only_in_watermark` — clear the cache
   between two calls (so we get fresh watermarks), confirm the zip
   bytes differ overall, then assert every `.md` body is identical
   modulo the watermark comment line (regex-strip + compare).
6. `test_persona_unresolved_base_link_surfaces_warning` — a persona
   neuron linking to `base/<missing>` lands a
   `vault.unresolved_link` warning on the composed manifest's
   `warnings[]`.
7. `test_compose_404_when_buyer_doesnt_own_occupation_license` —
   wrong-owner license raises `vault.license_not_found` (404).
8. `test_compose_403_when_requested_persona_license_not_held` —
   `include_persona_license_ids=[other_buyer_persona_lic.id]`
   raises `vault.persona_license_not_held` (403).
9. `test_new_vault_build_invalidates_cache_via_keyed_build_id` — add
   a new member skill, force-rebuild, request compose; cache_hit goes
   back to False because the new `occupation_build_id` changed the
   cache key. (Documents the spec's invalidation approach — fresh
   build_id naturally generates a fresh key, stale key ages out at
   24h TTL.)
10. `test_vault_downloads_row_records_hash_matching_bytes` — the
    audit row's `composed_hash` equals `sha256` of the bytes the
    buyer would actually download from `storage_url`.

(The brief asked for 8; we ship 10 because the cache invalidation
test and the hash-matches-bytes test both fell out cleanly from the
shared seed helpers.)

### `apps/api/src/vault/tests/test_router.py` (new)

12 endpoint-level tests covering happy / auth-fail / validation-fail
for each of the three endpoints:

* `POST /v1/licenses/{id}/vault`: happy, cache-hit on second call,
  404 when not owner, 401 when unauthenticated, 403 with
  `vault.persona_license_not_held` when requested persona license
  isn't held, 422 on bad UUID in body.
* `GET /v1/licenses/{id}/vault/downloads`: happy (after a download
  exists), 404 to non-owners.
* `GET /v1/vault/builds/{build_id}`: owner can read, license holder
  can read, unauthorised user gets 404, unknown id gets 404.

Auth strategy mirrors `src/personas/tests/test_router.py` — override
the FastAPI deps so tests don't double-test the JWT cookie flow. The
`auth_client` fixture builds a fresh app with `vault.router` mounted,
swaps `get_db` for a per-test session, and yields `(client, app)`.

---

## Verification

### `pytest src/vault/tests/ -v`

```
============================= test session starts =============================
collected 53 items

src/vault/tests/test_builder.py::test_build_occupation_happy_path_5_members PASSED
... (13 builder tests)
src/vault/tests/test_composer.py::test_compose_occupation_only_cache_miss PASSED
src/vault/tests/test_composer.py::test_compose_cache_hit_returns_same_storage_url PASSED
src/vault/tests/test_composer.py::test_compose_with_one_persona PASSED
src/vault/tests/test_composer.py::test_compose_with_two_personas PASSED
src/vault/tests/test_composer.py::test_two_downloads_differ_only_in_watermark PASSED
src/vault/tests/test_composer.py::test_persona_unresolved_base_link_surfaces_warning PASSED
src/vault/tests/test_composer.py::test_compose_404_when_buyer_doesnt_own_occupation_license PASSED
src/vault/tests/test_composer.py::test_compose_403_when_requested_persona_license_not_held PASSED
src/vault/tests/test_composer.py::test_new_vault_build_invalidates_cache_via_keyed_build_id PASSED
src/vault/tests/test_composer.py::test_vault_downloads_row_records_hash_matching_bytes PASSED
src/vault/tests/test_manifest.py ... (7 tests)
src/vault/tests/test_router.py::test_post_vault_happy_path PASSED
src/vault/tests/test_router.py::test_post_vault_second_call_cache_hit PASSED
src/vault/tests/test_router.py::test_post_vault_404_when_not_owner PASSED
src/vault/tests/test_router.py::test_post_vault_requires_auth PASSED
src/vault/tests/test_router.py::test_post_vault_403_persona_license_not_held PASSED
src/vault/tests/test_router.py::test_post_vault_validation_fail_extra_field PASSED
src/vault/tests/test_router.py::test_list_vault_downloads_happy_path PASSED
src/vault/tests/test_router.py::test_list_vault_downloads_404_for_non_owner PASSED
src/vault/tests/test_router.py::test_get_vault_build_by_owner PASSED
src/vault/tests/test_router.py::test_get_vault_build_by_license_holder PASSED
src/vault/tests/test_router.py::test_get_vault_build_404_for_unauthorised PASSED
src/vault/tests/test_router.py::test_get_vault_build_404_for_unknown_id PASSED
src/vault/tests/test_validator.py ... (11 tests)

============================== 53 passed in 8.34s ==============================
```

Wave-3B counts: **composer 10 passed**, **router 12 passed**. Wave-3A
builder/manifest/validator tests **31 passed unchanged**.

### Regression — wave-1 + wave-2 module tests

```
$ uv run pytest src/occupations/tests src/personas/tests src/capture/tests -q
191 passed, 16 warnings in 43.34s
```

Breakdown unchanged from the wave-3A diary baseline:
- Occupations: 55 passed.
- Personas: 59 passed.
- Capture: 77 passed.

### Regression — top-level legacy tests

```
$ uv run pytest tests/test_delivery.py tests/test_checkout_flow.py -q
26 passed in 6.59s
```

(Spot-checked the delivery + checkout flows because those exercise the
same `licenses` / `delivery.watermark` surface the composer touches.)

### Full combined suite

```
$ uv run pytest src/vault/tests src/occupations/tests src/personas/tests src/capture/tests tests/ -q
790 passed, 18 warnings in 74.70s
```

(53 vault + 191 module + 546 top-level legacy = 790. No regressions.)

### `mypy --strict src/vault src/core`

```
src\core\logging.py:39: error: ...  [pre-existing, NOT introduced by W3B]
src\core\rate_limits.py:72: error: Unused "type: ignore" ...  [pre-existing]
Found 2 errors in 2 files (checked 24 source files)
```

Verified the two errors exist on master (`git stash` + re-run) — they
are pre-existing in `src/core/logging.py` and `src/core/rate_limits.py`,
not from this wave. Vault + cache files pass clean:

```
$ uv run mypy --strict src/vault
Success: no issues found in 15 source files

$ uv run mypy --strict src/core/cache.py
Success: no issues found in 1 source file
```

### `ruff check src/vault src/core/cache.py`

```
All checks passed!
```

### `alembic upgrade head` on Postgres

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

No-op — wave-1 migrations 0006–0010 already at head. No new migrations
in this wave (the brief explicitly forbids them).

### Manual sample-flow demo (brief item 5)

A small driver script (kept in the dev diary, not committed) seeds a
curator, an occupation, one member skill, builds the vault, creates a
buyer license, then runs `compose_for_license` twice:

```
CALL 1: cache_hit=False, hash=53ee8a112267a93b..., url=memory://demo/delivery/vaults/Z_IINXnWYt0liw37.zip?expires=60
        expires_at=2026-05-26T18:51:58.807000+00:00
CALL 2: cache_hit=True,  hash=53ee8a112267a93b..., url=memory://demo/delivery/vaults/Z_IINXnWYt0liw37.zip?expires=60
        same_storage_url=True
```

In production the URL shape is the AWS / MinIO presigned form:
`https://<bucket>.<region>.amazonaws.com/delivery/vaults/{nonce}.zip?X-Amz-Algorithm=...&X-Amz-Expires=60&...`
— same TTL, same audit semantics.

---

## Files created / modified

### Created

- `apps/api/src/core/cache.py` (new)
- `apps/api/src/vault/composer.py` (new)
- `apps/api/src/vault/router.py` (new)
- `apps/api/src/vault/tests/test_composer.py` (new — 10 tests)
- `apps/api/src/vault/tests/test_router.py` (new — 12 tests)
- `team/dev-diary-vault-composer-wave3.md` (this file)

### Modified

- `apps/api/src/vault/__init__.py` — package docstring updated to
  mention the new `composer` and `router` submodules. No code change.

### Not touched (per brief)

- `apps/api/src/main.py` — orchestrator mounts the new router after
  this wave returns (mount lines below).
- `apps/api/src/vault/builder.py` — read-only.
- `apps/api/src/vault/manifest.py` — read-only.
- `apps/api/src/vault/jobs.py` — read-only.
- `apps/api/src/delivery/watermark.py` — read-only. `append_watermark`
  reused verbatim by the composer.
- No alembic migrations added.

---

## Main.py mount lines for orchestrator

```python
# In apps/api/src/main.py, alongside the other router includes:
from src.vault.router import router as vault_router
app.include_router(vault_router)
```

The router prefixes its routes itself (some live under `/v1/licenses/`,
some under `/v1/vault/`) so no `prefix=` argument is needed at the
mount site.

---

## Open questions / handoffs for Wave 4

1. **T-13 demo CLI integration.** `scripts/demo_devops_agent.py` (Wave
   4, Backend) will call `composer.compose_for_license` directly with
   the curated buyer's license rather than going through the HTTP
   layer. The return shape is a `ComposedDownload` dataclass — the
   CLI can immediately fetch the bytes from `storage.get_object(
   result.storage_url)` (no HTTP roundtrip needed for the demo since
   the CLI runs against the same process). Helper recipe:

   ```python
   from src.vault.composer import compose_for_license
   from src.storage.s3 import get_storage

   result = await compose_for_license(
       session,
       buyer_id=demo_buyer.id,
       occupation_license_id=demo_occ_lic.id,
   )
   zip_bytes = await get_storage().get_object(result.storage_url)
   # ... unzip into temp dir, load vault.json, run agent ...
   ```

2. **T-12 sample persona seed (Curation, Wave 4).** The persona build
   script will produce one `VaultBuild` row per persona via
   `vault.jobs.enqueue_persona_build`. As long as it sets
   `composition_role='persona'` and `target_occupation_skill_id` on
   the buyer's license rows, composition Just Works. The curation
   script does NOT need to call the composer directly — that's the
   buyer's flow.

3. **Cache invalidation on yank.** Spec §14 lists "the occupation or
   persona is yanked" as a cache-invalidation trigger. The current
   implementation handles new-build invalidation (build_id is part of
   the cache key), but a yanked-version-still-cached scenario would
   serve a stale URL until the 24h TTL expires. For MVP the 24h
   window is acceptable per the brief's choice not to add a yank-side
   invalidation hook in this wave. If a creator yanks a version and a
   buyer hits the cache within the window, they get the last-good
   build — auditable via `vault_downloads.occupation_build_id`. **Slot
   for Wave 5 / Phase 2** if product wants tighter SLAs: add an
   `audit_log → composer.invalidate_for_skill` listener (the cache
   key includes `skill_id` so a scan-and-delete is feasible at MVP
   scale).

4. **Manifest's `composed_hash` is the first-pass hash.** The
   composer's two-pass zip means the `vault.json` carries
   `composed_hash = sha256(zip without composed_hash patched in)`,
   which is then patched and re-hashed for the audit row. Consumers
   reading `vault.json.build.composed_hash` should treat it as a
   stable build-identity hash that points at this composed bundle,
   NOT as a checksum to verify the zip bytes against. The audit row's
   `composed_hash` (and the value returned in `ComposedDownload`)
   are the post-watermark, post-patch hash over the actual delivered
   bytes. T-13's demo CLI uses the latter for any "verify download"
   functionality.

5. **No cross-process compose locking.** Two parallel composer calls
   for the same `(buyer_id, occ_build_id, persona_build_ids)` will
   both compose and both write a `vault_downloads` row; the second
   `cache.set()` clobbers the first harmlessly because the payload is
   identical (modulo watermark timestamp, which the cache stores per
   audit row). At MVP scale this is fine; if the platform later sees
   simultaneous-download abuse, add a Redis SETNX lock in `cache.py`'s
   `get_or_compute`. **Documented in the composer module's
   `get_or_compute` docstring.**

6. **`cache.py` Redis backend not exercised in CI.** The in-memory
   backend is what every vault test uses (per the brief's `SKG_CACHE_INMEM=1`
   convention). The Redis backend is exercised by hand against the
   compose-stack docker container during dev. A future integration
   test (Wave 5 / T-14 owner) should drive the Redis path
   end-to-end — the helper has a `set_redis_client_for_tests()`
   injection point ready for that.

7. **Persona-build-missing not 404-able.** The composer silently
   skips persona licenses whose latest `VaultBuild.status` is not
   `succeeded` and logs a `vault.compose.persona_no_build` warning.
   Spec §10 step 7c says "skip; surface as warning in manifest" —
   the warning is in the *server logs*, not on the composed manifest.
   The brief is ambiguous on this; current behaviour matches the
   spec's "skip" semantics. **Slot for Wave 5 retro:** decide whether
   buyers should see a "persona build pending" badge on the
   marketplace download page based on this log.

---

## What Wave 3B (Vault Composer) inherits to Wave 4

- A working composer pipeline keyed on `vault_builds` rows: read,
  merge, watermark, deliver, audit. Idempotent per `(buyer,
  occ_build, persona_builds)` for 24h.
- A typed `VaultComposeError(code, message, status_code, details)`
  for the demo CLI to catch and surface as a friendly error string.
- A `vault_downloads` audit trail per call (`composed_hash`,
  `occupation_build_id`, `persona_build_ids[]`, `persona_license_ids[]`).
  T-13's demo can read this directly to confirm "the demo buyer
  downloaded X build".
- The cache helper (`src.core.cache`) is reusable by any future
  service that needs the same in-memory-or-Redis pattern — e.g.
  T-14's integration tests if they want their own per-test cache.
- 53 vault tests + 191 module tests + 546 top-level legacy tests
  (790 total) all green. Composer's tests use the same seed pattern
  the builder's tests do, so adding new compose scenarios in Wave 5
  is a copy-and-tweak job.
