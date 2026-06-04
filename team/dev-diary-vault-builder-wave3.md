# Dev diary — Vault builder, Cycle 1 Wave 3A

**Owner:** Backend (Vault Builder)
**Wave:** 3A (T-06 vault builder + manifest + validator + Arq jobs)
**Started:** 2026-05-26
**Status:** shipped (handing off to orchestrator and T-07 composer)

---

## What shipped

### `apps/api/src/vault/` (new files)

- **`schema/vault-manifest-v1.json`** — JSON Schema (draft-07) for
  `vault.json`. Versioned (`schema_version: 1`, top-level `$schema`
  URI of `https://skillsgit.com/schema/vault-manifest-v1.json`). Mirrors
  the spec in `team/03-vault-generation.md` §5: `vault_id`, `occupation`
  / `personas[]`, `files[]` (with `tags`, `links[]`, `neuron`), the
  `attribution_index` map (skill_id → vault_path), the `build` block,
  and `warnings[]`. The schema's `$defs` enumerate every sub-shape with
  strict `additionalProperties:false`. Re-packageable verbatim into
  `packages/skills-schema/` for downstream tooling.

- **`manifest.py`** — Pydantic v2 models for the manifest:
  `VaultManifest`, `OccupationSummary`, `PersonaSummary`, `FileEntry`,
  `ManifestLinkEntry`, `ManifestNeuronBlock`, `BuildBlock`, `Warning`.
  Plus the public `write_manifest(manifest) -> str` serializer and
  `load_schema() -> dict` helper. `write_manifest()` always emits the
  `$schema` key alongside the payload for offline validation, sorted
  with `sort_keys=False` (keeps field order author-meaningful, matches
  the JSON Schema layout). All models are `extra="forbid"` except
  `Warning` (`extra="allow"` so downstream can attach extra context).

- **`builder.py`** — the heart of T-06. Public entry points:

  ```python
  async def build_occupation(
      session: AsyncSession,
      occupation_skill_id: UUID,
      version: str,
      *,
      force_rebuild: bool = False,
  ) -> VaultBuild: ...

  async def build_persona(
      session: AsyncSession,
      persona_skill_id: UUID,
      version: str,
      *,
      force_rebuild: bool = False,
  ) -> VaultBuild: ...
  ```

  Both:
  * Hydrate the parent skill + side-table row + every published member.
  * Pull each member's body bytes from `src/storage/s3.get_storage()`.
  * Assemble file payloads in sort-stable order (`(sort_order, slug)`).
  * Emit the body with:
    1. original frontmatter + body verbatim;
    2. an auto-generated `## Linked notes` footer per spec §2;
    3. a trailing `<!-- skg-attribution: ... -->` HTML comment per
       ADR-010 (placed BEFORE any future watermark comment so
       `delivery/watermark.append_watermark()` can stack on top at
       composition time without disturbing the attribution block).
  * Write `vault.json` (occupation) or `personas/<handle>/<slug>/persona.json`
    (persona-only) with the full manifest.
  * Deterministic zip: every `ZipInfo.date_time` is pinned to
    `EPOCH_TIMESTAMP = (2026, 1, 1, 0, 0, 0)`; `built_at` in the
    manifest is the matching `EPOCH_DATETIME`; `vault_id` is derived
    from `sha256(scope, skill_id, version, files[])` so two builds over
    identical inputs produce byte-identical archives (and therefore the
    same `content_hash`).
  * Hard caps from spec §12: 50 MB max per vault → `vault_build.too_large`.
  * Idempotency: if `(skill_id, content_hash)` already exists and
    `force_rebuild=False`, returns the existing `VaultBuild` row
    without re-uploading. With `force_rebuild=True`, re-uploads the
    (bytewise identical) zip but still returns the existing row so the
    unique constraint on `(skill_id, content_hash)` is preserved.
  * Patches `occupation.latest_build_id` / `persona.latest_build_id`
    after a successful build.
  * Validates every filename + creator handle against the ASCII-kebab
    rule from ADR-011 (`vault_build.invalid_filename`).

  Error codes (all routed through `VaultBuildError(code, message)`):

  | Code | When |
  |---|---|
  | `vault_build.not_found` | parent skill / side-table row missing |
  | `vault_build.empty_membership` | occupation with zero members |
  | `vault_build.no_neurons` | persona with zero neurons |
  | `vault_build.invalid_member_kind` | member skill has wrong `kind` |
  | `vault_build.no_published_version` | member has no version |
  | `vault_build.version_not_found` | requested version doesn't exist |
  | `vault_build.member_missing` | storage object gone |
  | `vault_build.malformed_member` | YAML parse failure on a member body |
  | `vault_build.invalid_filename` | slug fails the kebab/ASCII rule |
  | `vault_build.too_large` | zip > 50 MB |

- **`validator.py`** — `validate_vault(zip_bytes) -> ValidationResult`.
  Catches all 8 spec failure modes:

  | Code | Caught |
  |---|---|
  | `vault.bad_zip` | non-zip bytes / corrupt central directory |
  | `vault.missing_manifest` | no `vault.json` AND no `persona.json` |
  | `vault.required_file_missing` | occupation build missing README/index, persona build missing README |
  | `vault.malformed_manifest_json` | `vault.json` is not parseable JSON |
  | `vault.schema_violation` | JSON Schema (draft-07) validation fail |
  | `vault.manifest_pydantic_error` | Pydantic validation fail |
  | `vault.manifest_file_missing` | manifest lists a file the zip lacks |
  | `vault.missing_attribution` | per-file `skg-attribution` comment missing |
  | `vault.unresolved_wikilink` | `## Linked notes` footer wiki-link doesn't resolve |
  | `vault.attribution_dangles` | `attribution_index` value not in `files[]` |
  | `vault.neuron_block_missing` | `kind=memory_neuron` file w/o neuron block |

  Restricts the wiki-link scan to the auto-emitted footer (matches the
  spec: inline links elsewhere are allowed to dangle).

- **`jobs.py`** — Arq job wrappers `build_occupation_job` /
  `build_persona_job` + the service-facing façade
  `enqueue_occupation_build()` / `enqueue_persona_build()`. The façade
  has three modes:
  * **Production** (`ENV!=test`): submits an Arq job and returns
    `EnqueueResult(status="queued", build_id=None)`. The worker runs
    in a fresh DB session.
  * **Test (default)**: returns a synth `queued` `EnqueueResult` with
    job_id matching the legacy stub's `occupations:build:` / `personas:build:`
    prefix so the existing wave-2 tests pass unchanged.
  * **Test (inline opt-in)**: `set_inline_builds_for_tests(True)` flips
    a module-level flag that makes the façade run the builder on the
    caller's session inline. The vault tests' conftest autouse-flips
    this so the real path is exercised end-to-end.

  `WorkerSettings` exposes `max_tries=3`, `job_timeout=180` for the
  worker process. Run with `uv run arq src.vault.jobs.WorkerSettings`.

- **`__init__.py`** — intentionally light (docstring only, no submodule
  imports). The initial draft re-exported every submodule's public
  surface at the top level, but that caused a subtle conftest-loading
  bug: pytest imports `src.vault` (the package) when collecting
  `src/vault/tests/`, and an eager `from src.vault.builder import ...`
  chain pulled in `src.storage.s3` → `src.core.config.settings` BEFORE
  `tests/conftest.py` had a chance to set `ENV=test`. Settings froze at
  `dev`, and downstream `if settings.is_test:` branches (notably the
  Stripe webhook router) took the wrong path when later tests ran in
  the same pytest session. The fix: keep `__init__.py` empty-ish and
  let callers import the names they need from the submodules.

- **`tests/__init__.py`** + **`tests/conftest.py`** — self-contained
  fixtures mirroring `src/occupations/tests/conftest.py`:
  * Per-test in-memory sqlite engine with every model module loaded.
  * `memory_storage` fixture that injects an `InMemoryStorage`
    (`src.storage.s3.InMemoryStorage`) for the builder to read +
    write objects.
  * `_inline_builds_in_vault_tests` autouse fixture that flips the
    jobs façade to inline mode (and restores on teardown) so legacy
    occupations/personas tests are unaffected.

- **`tests/test_builder.py`** — 13 builder tests covering the T-06
  acceptance criteria + edge cases:
  * 5-member happy path → zip well-formed, `validate_vault()` passes,
    every member file carries `skg-attribution`.
  * Idempotency (`force_rebuild=False` → same row), determinism
    (`force_rebuild=True` → identical content_hash + bytes).
  * Empty membership / unknown version / wrong member kind / storage
    missing → typed `VaultBuildError` with the right code.
  * Persona happy path (3 neurons) → only the `personas/<handle>/<slug>/`
    subtree + `persona.json`, no `vault.json` / `base/` folders.
  * Linked-notes section renders resolved links; unresolved links land
    as `manifest.warnings[]` entries (build still succeeds).
  * `attribution_index` map covers every `files[]` entry.

- **`tests/test_manifest.py`** — 7 manifest tests:
  * Round-trip via `model_dump(mode='json')` → `model_validate()`.
  * `write_manifest()` output passes the JSON Schema validation.
  * `load_schema()` returns the bundled schema with `schema_version: 1`.
  * Pydantic rejects bad inputs (unknown relation, weight out of range,
    unknown kind).
  * Persona-only manifest (occupation=null) validates against the schema.

- **`tests/test_validator.py`** — 11 validator tests covering every
  failure mode listed above, plus the two happy paths (minimal
  occupation zip + minimal persona zip).

### `apps/api/src/occupations/service.py` (modified)

Replaced the stub `trigger_build()` with a call to
`vault.jobs.enqueue_occupation_build()`. The router contract is
unchanged (`JobAccepted` shape stays the same). Errors from the
builder are translated into `OccupationError(code=exc.code, ...)` so
the FastAPI handler maps them via the standard envelope.

### `apps/api/src/personas/service.py` (modified)

Mirror change — `trigger_build()` now calls
`vault.jobs.enqueue_persona_build()`. Same translation of
`VaultBuildError → PersonaError`.

### `apps/api/pyproject.toml` (modified)

Added `jsonschema>=4.23` to runtime dependencies (for the validator's
JSON Schema check) and to the mypy `ignore_missing_imports` overrides.

---

## Verification

### `pytest src/vault/tests/ -v`

```
============================= test session starts =============================
collected 31 items

src/vault/tests/test_builder.py::test_build_occupation_happy_path_5_members PASSED
src/vault/tests/test_builder.py::test_build_occupation_writes_vault_builds_row PASSED
src/vault/tests/test_builder.py::test_build_occupation_is_idempotent PASSED
src/vault/tests/test_builder.py::test_build_occupation_empty_membership_raises PASSED
src/vault/tests/test_builder.py::test_build_occupation_unknown_version_raises PASSED
src/vault/tests/test_builder.py::test_build_occupation_rejects_non_skill_member PASSED
src/vault/tests/test_builder.py::test_build_occupation_manifest_attribution_index PASSED
src/vault/tests/test_builder.py::test_build_persona_happy_path_3_neurons PASSED
src/vault/tests/test_builder.py::test_build_persona_no_neurons_raises PASSED
src/vault/tests/test_builder.py::test_zip_is_deterministic_across_two_builds PASSED
src/vault/tests/test_builder.py::test_linked_notes_renders_resolved_links PASSED
src/vault/tests/test_builder.py::test_unresolved_link_emits_warning_but_does_not_fail PASSED
src/vault/tests/test_builder.py::test_missing_storage_object_raises_member_missing PASSED
src/vault/tests/test_manifest.py::test_manifest_roundtrips_through_json PASSED
src/vault/tests/test_manifest.py::test_manifest_serialised_matches_json_schema PASSED
src/vault/tests/test_manifest.py::test_schema_is_loadable_and_versioned PASSED
src/vault/tests/test_manifest.py::test_link_entry_rejects_unknown_relation PASSED
src/vault/tests/test_manifest.py::test_file_entry_requires_kind_in_enum PASSED
src/vault/tests/test_manifest.py::test_link_entry_weight_must_be_between_0_and_1 PASSED
src/vault/tests/test_manifest.py::test_manifest_persona_only_build_has_no_occupation PASSED
src/vault/tests/test_validator.py::test_validate_minimal_occupation_zip_passes PASSED
src/vault/tests/test_validator.py::test_validate_minimal_persona_zip_passes PASSED
src/vault/tests/test_validator.py::test_validate_rejects_non_zip PASSED
src/vault/tests/test_validator.py::test_validate_missing_manifest PASSED
src/vault/tests/test_validator.py::test_validate_missing_readme_for_occupation_build PASSED
src/vault/tests/test_validator.py::test_validate_file_listed_in_manifest_but_missing_from_zip PASSED
src/vault/tests/test_validator.py::test_validate_missing_attribution_comment_in_file PASSED
src/vault/tests/test_validator.py::test_validate_unresolved_wiki_link_in_linked_notes PASSED
src/vault/tests/test_validator.py::test_validate_attribution_index_dangles PASSED
src/vault/tests/test_validator.py::test_validate_memory_neuron_must_have_neuron_block PASSED
src/vault/tests/test_validator.py::test_validate_malformed_manifest_json PASSED

============================= 31 passed in 2.26s ==============================
```

Per-file:
- `test_builder.py`: **13 passed**.
- `test_manifest.py`: **7 passed**.
- `test_validator.py`: **11 passed**.

### Regression on wave-2 module tests

```
$ uv run pytest src/occupations/tests src/personas/tests src/capture/tests -q
191 passed, 16 warnings in 44.35s
```

Breakdown matches the wave-2 baselines exactly:
- Occupations: **55 passed** (unchanged from wave-2 dev diary).
- Personas: **59 passed** (unchanged).
- Capture: **77 passed** (unchanged).

### Top-level legacy tests

```
$ uv run pytest tests/ -q
546 passed, 1 warning in 27.42s
```

Same as the wave-2 baseline — no regression.

### Full combined suite (vault + occupations + personas + capture + legacy)

```
$ uv run pytest src/vault/tests src/occupations/tests src/personas/tests src/capture/tests tests/ -q
768 passed, 17 warnings in 70.38s
```

(31 + 55 + 59 + 77 + 546 = 768.) No cross-test pollution between the
per-module conftests and the top-level conftest.

### `mypy --strict src/vault src/occupations src/personas`

```
Success: no issues found in 29 source files
```

### `ruff check src/vault src/occupations src/personas`

```
All checks passed!
```

### `alembic upgrade head` on Postgres

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

(No-op — wave-1 migrations 0006–0010 already at head. No new migrations
in this wave.)

### Hand-built occupation vault demo (T-06 acceptance brief item E.4)

Built a 3-skill occupation with 2 cross-links (`alpha → beta`, `beta →
gamma`) via the same path the real builder will exercise. Output:

```
Built occupation vault: content_hash=5b2e22cf45c07a59cc526589b793bb9a56db078406c0b2500a06c7ae5c2f8dfc
  file_count=6, total_bytes=3491
  storage_url=vaults/019e657d-7cc8-7470-a045-2e05e783539e/1.0.0/5b2e22cf45c07a59cc526589b793bb9a56db078406c0b2500a06c7ae5c2f8dfc.zip

Zip size: 3491 bytes

validate_vault() result:
  is_valid=True
  error_count=0

Zip layout:
  00-index.md (350 bytes)
  README.md (965 bytes)
  domains/ci-cd/alpha.md (699 bytes)
  domains/observability/beta.md (706 bytes)
  domains/observability/gamma.md (598 bytes)
  vault.json (2613 bytes)
```

Confirms: the spec's expected folder layout (`README.md`,
`00-index.md`, `vault.json`, per-domain folders) is emitted, the
content_hash is stable, and validate_vault is green with zero errors.

### `trigger_build` swap confirmation

Both `occupations.service.trigger_build()` and
`personas.service.trigger_build()` now call
`vault.jobs.enqueue_*_build()` instead of synthesising a stub job id.
The existing tests in `src/occupations/tests/test_service.py::
test_trigger_build_emits_audit_row` and the persona analogue still
assert `job.status == "queued"` and the prefix `occupations:build:` /
`personas:build:` — both pass green because the façade's test-mode
default returns a legacy-shaped `EnqueueResult`. The vault tests
flip `set_inline_builds_for_tests(True)` to exercise the real
in-process build path.

---

## Files created / modified

### Created (vault module)

- `apps/api/src/vault/schema/vault-manifest-v1.json`
- `apps/api/src/vault/manifest.py`
- `apps/api/src/vault/builder.py`
- `apps/api/src/vault/validator.py`
- `apps/api/src/vault/jobs.py`
- `apps/api/src/vault/tests/__init__.py`
- `apps/api/src/vault/tests/conftest.py`
- `apps/api/src/vault/tests/test_builder.py`
- `apps/api/src/vault/tests/test_manifest.py`
- `apps/api/src/vault/tests/test_validator.py`
- `team/dev-diary-vault-builder-wave3.md` (this file)

### Modified

- `apps/api/src/vault/__init__.py` — re-export the public surface;
  re-export `Warning as VaultWarning` to dodge the builtin shadow.
- `apps/api/src/vault/models.py` — two cosmetic `noqa: TC003` / `UP042`
  comments matching the project-wide enum pattern in
  `src/occupations/models.py`; no semantic change.
- `apps/api/src/occupations/service.py` — `trigger_build()` wired to
  `vault.jobs.enqueue_occupation_build()`; `import uuid` carries a
  pre-existing `noqa: TC003` (matches other modules).
- `apps/api/src/personas/service.py` — same wiring change for
  `enqueue_persona_build()`.
- `apps/api/pyproject.toml` — added `jsonschema>=4.23` runtime dep
  + `jsonschema.*` to the mypy ignore-missing list.

### Not touched (per brief)

- `apps/api/src/main.py` — T-07 will mount the future vault router.
- No alembic migrations added.
- `src/capture/`, `src/skills/`, `src/billing/` — read-only.

---

## Open questions / handoffs for Wave 3B (T-07 composer)

1. **Manifest read path is stable.** The composer can read
   `VaultBuild.manifest_json` directly and use the bundled Pydantic
   model (`from src.vault.manifest import VaultManifest`) to parse it
   without re-loading the zip. The schema URI
   `https://skillsgit.com/schema/vault-manifest-v1.json` is canonical;
   bumping `schema_version` is a major version change.

2. **S3 path conventions.** Both build types write to
   `vaults/{skill_id}/{version}/{content_hash}.zip`. The composer's
   per-buyer artifact should land under
   `delivery/vaults/{nonce}.zip` per `03-vault-generation.md` §10 to
   reuse the existing 1h lifecycle policy on the `delivery/` prefix.

3. **Composer's manifest assembly.** When merging an occupation build
   with N persona builds, the composer should:
   - Start with the occupation's manifest as a base.
   - For each persona build's manifest: append the `personas[]` entry,
     append the `files[]` entries (rewriting `vault_path` is unnecessary
     — persona builds already use the full
     `personas/<handle>/<slug>/...` path), merge into the
     `attribution_index`.
   - Re-run link resolution across the merged surface (use the
     `_build_target_resolver_for_occupation` pattern but with the
     persona neurons added). Flip per-link `resolved` flags and per-file
     `links_resolved` accordingly; update `warnings[]`.
   - Set `build.persona_build_ids[]`, `build.persona_build_hashes[]`,
     `build.composed_hash` (SHA-256 of the post-watermark composed
     bytes), `build.composed_at = datetime.now(UTC)` (the composed
     output IS allowed to be wall-clock — per ADR-006 consequences,
     each download is a unique audit entry by design).

4. **Watermark placement.** Per the spec §7, the composer's
   per-buyer watermark sits BELOW the `skg-attribution` comment:

   ```
   <body markdown>

   ## Linked notes
   - [[...]] ...

   <!-- skg-attribution: ... -->

   <!-- license:{license_id_hash} buyer:{...} ts:... -->
   ```

   The builder emits up through `skg-attribution`; the composer calls
   `src.delivery.watermark.append_watermark(content, license_id=..., buyer_id=...)`
   on each `.md` to append the second comment. The composed_hash is
   computed AFTER watermark application, so it varies per-buyer
   per-download (intentional — that's the audit trail).

5. **Validation at composition time.** The composer should call
   `validate_vault()` on its final bundle BEFORE handing back a
   presigned URL. Any error halts delivery with a typed code so the
   download endpoint can return 500 with a stable error code rather
   than a corrupt bundle.

6. **Test-mode façade.** If the composer needs an Arq job too, model
   it after `enqueue_occupation_build` — accept a fresh session-style
   second arg, gate on `settings.is_test`, expose a
   `set_inline_<x>_for_tests` toggle so legacy module tests can keep
   their synthesised return without exercising the real path.

7. **Determinism vs wall-clock.** The builder pins `built_at` to
   `EPOCH_DATETIME` for reproducibility. The composer should NOT do
   the same — `composed_at` is a real audit timestamp. The composed
   zip is therefore NOT byte-stable across runs (also: the per-buyer
   watermark varies), but the underlying occupation+persona artifacts
   ARE byte-stable, which is enough for cache-key generation.

8. **TBD ADR-016 Q-6 polish (`.obsidian/graph.json`).** Not landed
   in this wave (optional per the brief). The asset would be ~30
   lines of JSON applying color-by-tag to the three top-level domains.
   Easy add — emit it inside `_write_zip` for occupation builds only.
   Slot for Curation's T-08 build script to pick up if they want it.

---

## What Wave 3A (Vault Builder) inherits to Wave 3B (T-07 Composer)

- A working `VaultBuild` row pipeline: `enqueue_*_build` → builder →
  S3 upload → `VaultBuild` row with structured `manifest_json` +
  `build_log_json.warnings`. The composer reads `manifest_json`
  directly — no need to download the zip just for metadata.
- Stable on-disk format: every emitted `.md` carries
  `<!-- skg-attribution: ... -->`; every vault has a `vault.json` (or
  persona-only `persona.json`) that passes the JSON Schema in
  `src/vault/schema/vault-manifest-v1.json`.
- `validate_vault(zip_bytes)` — call it on the composed bundle before
  responding to the buyer; surfaces all 8 spec failure modes with
  typed codes.
- A `VaultBuildError(code, message)` exception that the composer can
  re-raise as a `VaultComposeError` (or map to its own envelope).
- The legacy occupations + personas tests are still green (191 passed).
  The composer can replace its own `vault.jobs.enqueue_*` stub the
  same way — the façade is structured so it stays test-friendly.
- An end-to-end demo script (run from `python -m vault_demo` in
  scratch) that exercises the real build + validate path; useful as
  a smoke test for the composer's own integration tests.
