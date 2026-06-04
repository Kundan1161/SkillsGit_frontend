# 03 — Vault Generation Spec

**Owner:** Architect
**Status:** Proposed
**Reads:** ADR-007, ADR-010, ADR-011, ADR-013, existing
`apps/api/src/delivery/watermark.py` for the watermark + frontmatter
patterns.

This file defines the on-disk format the buyer receives, the function
that produces it, and the function that composes occupation + persona
builds at delivery time.

---

## 1. Folder layout (root of the vault)

```
ai-devops-engineer-v1.0.0/                  ← top-level folder; matches the zip name
├── README.md                                ← human-readable overview (occupation summary)
├── 00-index.md                              ← table of contents grouped by domain + role
├── vault.json                               ← machine-readable manifest (ADR-010)
│
├── base/                                    ← always present; the occupation's curated skills
│   ├── ci-cd/
│   │   ├── devops-ci-pipeline-architect.md
│   │   ├── devops-gha-workflow-optimizer.md
│   │   └── ...
│   ├── observability/
│   │   ├── observability-dashboard-architect.md
│   │   ├── alert-policy-architect.md
│   │   └── ...
│   ├── infra-as-code/
│   │   ├── devops-terraform-module-reviewer.md
│   │   └── ...
│   ├── incident-response/
│   │   ├── ops-incident-commander.md
│   │   └── ...
│   └── platform/
│       └── internal-platform-strategy-author.md
│
├── personas/                                ← present only when composing with ≥1 persona
│   ├── jane-devops/
│   │   ├── README.md                        ← creator bio + persona description
│   │   └── neurons/
│   │       ├── 2024-08-flaky-tests.md
│   │       ├── 2024-10-blue-green-rollback.md
│   │       └── ...
│   └── another-creator-handle/
│       └── ...
│
└── attachments/                             ← content-addressed binary blobs
    ├── 0a3f9c4e2d1b.png
    ├── 6c8e4a2b1d0f.yaml
    └── ...
```

### File-naming convention (ADR-011)

- kebab-case ASCII only: `[a-z0-9-]+`
- max length 80 characters before the `.md` extension
- no leading/trailing hyphens
- no underscores (matches the existing skill slug convention)
- folders: same rules; no dotfiles, no spaces
- attachments: `<sha256-12>.<ext>` where `<sha256-12>` is the first 12
  hex chars of the sha256 of the file bytes (collision-resistant
  enough for ≤10⁶ attachments per vault)

The vault builder rejects any neuron filename that violates this rule
with error code `vault_build.invalid_filename`. The same rule applies
to base skills, but those are already conformant via the existing
publish pipeline.

---

## 2. `[[wiki-links]]` generation (ADR-007)

Source of truth: `links:` frontmatter on every neuron / skill file.

Each entry: `{target: <slug-or-relative-path>, relation: <enum>, weight?: float}`.

### Target resolution

The builder resolves `target` in this order:

1. Exact vault-relative path: `base/observability/observability-dashboard-architect`
   (no `.md` extension; matches the file at that path inside the vault).
2. Within the current scope: a sibling neuron in the same persona's
   `neurons/` folder, by filename slug.
3. A skill slug in the base occupation: scan `base/` recursively and
   match by stripped filename (the kebab slug). Returns the first hit.
4. A creator-prefixed slug: `<handle>/<slug>` → look up in the composed
   vault's `vault.json.files[].vault_path` whose `creator_handle` and
   filename slug match.

If none of the above resolves at *occupation build time*, the link is
emitted as `[[<target>]]` (still works visually in Obsidian if the
buyer later acquires a persona that adds the target; Obsidian shows
broken links as a dimmed style). The build's `manifest.warnings[]`
captures `{file: vault_path, unresolved_link: target}` so the creator
can fix.

At *composition time* (occupation + personas) the composer re-runs
resolution and updates `manifest.warnings[]` and the per-file
`vault.json.files[].links_resolved` flag. Warnings do not block
download.

### Emission inside each markdown file

The vault builder appends a stable `## Linked notes` section to every
file's body:

```markdown
## Linked notes

- [[base/incident-response/ops-incident-commander]] — applies
- [[base/observability/observability-dashboard-architect]] — see-also
- [[personas/jane-devops/neurons/2024-08-flaky-tests]] — recorded-instance-of
```

Authors MAY use inline `[[wiki-links]]` in body prose for readability;
the validator does NOT extract those for graph purposes. Inline links
that don't resolve simply render as broken in Obsidian — no
build-time enforcement (this is intentional; ADR-007 keeps the source
of truth narrow).

### Why `## Linked notes` over Obsidian's `aliases`/`tags`

Stock Obsidian (no plugin) renders `[[wiki-links]]` regardless of
where they sit in the body. Putting them in a stable footer means:
- Easy to regenerate without touching author prose.
- Diffable (the section is always at the end of the file).
- Agent-readable — the LLM in Layer C parses this footer for routing
  hints if `vault.json` is unavailable for some reason.

---

## 3. Graph view

Obsidian's built-in **Graph View** is computed at file-open time from
`[[wiki-links]]` extracted from every `.md` in the vault. We don't
configure or override it. Confirmed constraints for MVP:
- The graph is implicit; no `.obsidian/graph.json` shipped.
- Tag-based grouping (Obsidian's color-by-tag feature) works
  automatically off the `tags:` frontmatter we already populate.
- For a vault of 30 occupation skills + 50 neurons ≈ 80 nodes,
  Obsidian Graph View is interactive and instant.

No custom CSS, no plugins, no manifest. The user opens the vault and
hits `Ctrl-G` to see the graph.

---

## 4. Persona name-collision-safe linking

Personas can have neuron slugs that collide with each other or with
base skill slugs. Resolution rules:

- Two personas with the same neuron slug are isolated by their
  `personas/{handle}/neurons/` path. No collision in the filesystem.
- A neuron with the same slug as a base skill: `[[<slug>]]` (path-less
  target) resolves to whichever is found first by the order above. To
  disambiguate, the author writes the full path:
  `[[base/observability/observability-dashboard-architect]]` or
  `[[personas/jane-devops/neurons/observability-dashboard-architect]]`.
- The capture UX (`04-capture-flow.md`) prevents the AI from
  suggesting links by bare slug if a collision exists; it always
  produces a fully-qualified `target`.

For backwards safety, the builder writes ALL links it emits as
fully-qualified vault paths, never as bare slugs.

---

## 5. The vault manifest (`vault.json`)

A single JSON file at the vault root, machine-readable index used by:
- The reference agent in Layer C (`apps/api/scripts/demo_devops_agent.py`).
- Any downstream tool wanting to know what's in the vault.

Schema:

```jsonc
{
  "$schema": "https://docs.skillsgit.com/vault-manifest/v1.json",
  "vault_id": "01HX-...",                       // uuid v7, stable per composed bundle
  "schema_version": 1,
  "occupation": {
    "skill_id": "01HX-...",
    "name": "AI DevOps Engineer",
    "slug": "ai-devops-engineer",
    "creator_handle": "skillsgit-curated",
    "version": "1.0.0",
    "content_hash": "abc123...",
    "domains": ["ci-cd", "observability", "infra-as-code",
                "incident-response", "platform"]
  },
  "personas": [
    {
      "skill_id": "01HX-...",
      "name": "Jane's On-Call Brain",
      "slug": "jane-devops-on-call",
      "creator_handle": "jane-devops",
      "version": "1.0.0",
      "content_hash": "def456...",
      "neuron_count": 12
    }
  ],
  "files": [
    {
      "vault_path": "base/ci-cd/devops-ci-pipeline-architect.md",
      "skill_id": "01HX-...",
      "version": "1.0.0",
      "kind": "skill",
      "creator_handle": "skillsgit-curated",
      "content_hash": "...",
      "tags": ["ci-cd", "github-actions"],
      "links": [
        {"target": "base/observability/observability-dashboard-architect",
         "relation": "see-also", "resolved": true}
      ]
    },
    {
      "vault_path": "personas/jane-devops/neurons/2024-08-flaky-tests.md",
      "skill_id": "01HX-...",
      "version": "1.0.0",
      "kind": "memory_neuron",
      "creator_handle": "jane-devops",
      "content_hash": "...",
      "tags": ["incident", "flaky-tests"],
      "links": [
        {"target": "base/ci-cd/devops-ci-pipeline-architect",
         "relation": "applies", "resolved": true}
      ],
      "neuron": {
        "situation": "...",                  // mirrored from frontmatter for fast read
        "decision": "...",
        "outcome": "...",
        "recorded_at": "2024-08-12",
        "confidence": 0.8
      }
    }
  ],
  "attribution_index": {
    "01HX-skill-id-1": "base/ci-cd/devops-ci-pipeline-architect.md",
    "01HX-skill-id-2": "personas/jane-devops/neurons/2024-08-flaky-tests.md"
  },
  "build": {
    "occupation_build_id": "01HX-...",
    "occupation_build_hash": "...",
    "persona_build_ids": ["01HX-..."],
    "persona_build_hashes": ["..."],
    "composed_hash": "ghi789...",          // sha256 of the final bytes pre-watermark
    "built_at": "2026-05-26T18:30:00Z",
    "composed_at": "2026-05-26T18:30:42Z"
  },
  "warnings": [
    // e.g. {"file": "personas/.../foo.md", "unresolved_link": "base/missing-thing"}
  ]
}
```

The `attribution_index` is the fast lookup the demo agent uses to
turn an LLM-reported `skill_id` back into a human-readable
`vault_path`. The agent code in Layer C is approximately:

```python
manifest = json.loads((vault_dir / "vault.json").read_text())
def cite(skill_id: str) -> str:
    path = manifest["attribution_index"][skill_id]
    file = next(f for f in manifest["files"] if f["vault_path"] == path)
    return f"{path}  ({file['creator_handle']}, v{file['version']}, {file['kind']})"
```

---

## 6. Skills.md ↔ vault manifest binding

A vault is consistent with its source skills.md files if and only if:
- Every `vault.json.files[*].content_hash` matches the sha256 over the
  normalized body of the on-disk file at `vault_path` (post-watermark
  normalization: strip the final HTML comment block before hashing
  for comparison purposes — see `delivery/watermark.normalize_body`).
- Every entry in `vault.json.attribution_index` resolves to a file in
  `vault.json.files[]`.
- Every neuron file with `kind=memory_neuron` has a non-null
  `frontmatter.neuron` block.

The validator running inside the vault builder enforces these
invariants at build time. The composer re-checks before signing the
final bundle.

A separate `vault_validator.py` (Python) exposes
`validate_vault(directory: Path) -> ValidationResult` for use by:
- QA smoke tests.
- A future "verify my vault" buyer-side CLI (Phase 2).

---

## 7. Attribution comment in each file

Per ADR-010, every emitted markdown file gets a trailing HTML comment:

```markdown
<!-- skg-attribution:
  vault_path: "personas/jane-devops/neurons/2024-08-flaky-tests.md"
  skill_id: "01HX-..."
  version: "1.0.0"
  kind: "memory_neuron"
  creator_handle: "jane-devops"
  built_at: "2026-05-26T18:30:00Z"
-->
```

Order in file (top-to-bottom):
1. `---` YAML frontmatter `---`
2. body markdown (sections like `## When to use`, `## How to apply`, …)
3. `## Linked notes` section (auto-generated)
4. `<!-- skg-attribution: ... -->`
5. (composer-added) `<!-- skg-license: {license_id_hash} buyer:{...} ts:... -->`

The second comment is the existing per-buyer watermark from
`delivery/watermark.py:append_watermark`. The attribution comment is
new and lives between the body and the watermark.

An agent that wants to return citation strings only needs to read
`vault.json`. The HTML comments are belt-and-suspenders for tools
that load files individually.

---

## 8. README.md template

```markdown
# AI DevOps Engineer — v1.0.0

> A curated, graph-linked vault of methodology for the AI DevOps
> Engineer role. Built by @skillsgit-curated. Composed with personas:
> @jane-devops, @another-handle.

## What's in this vault

- 30 base methodology skills across 5 domains (CI/CD, observability,
  IaC, incident response, platform).
- 24 memory neurons from 2 practitioners with recorded situations,
  decisions, and outcomes.

## How to use this vault

1. Open the folder in **Obsidian** (no plugins required).
2. Press `Ctrl-G` to view the graph.
3. Start at `00-index.md`.
4. Drop the vault folder into your AI agent's working directory; point
   your agent at `vault.json` for routing.

## Attribution

This vault was assembled at 2026-05-26T18:30:42Z by Skills Git from:
- `skillsgit-curated/ai-devops-engineer` v1.0.0
- `jane-devops/jane-devops-on-call` v1.0.0

See `vault.json` for the machine-readable manifest.

## License

Each file's license is governed by the buyer's purchase of the
parent product. This bundle is per-buyer; the watermark in each file
identifies the licensee. Redistribution is not permitted.
```

The builder fills the template with values from the manifest.

---

## 9. 00-index.md template

```markdown
# Index — AI DevOps Engineer

## Base methodology

### Core

- [[base/ci-cd/devops-ci-pipeline-architect]] — Design a CI pipeline you won't regret
- [[base/observability/observability-dashboard-architect]] — Build dashboards that answer real questions
- ...

### Supporting

- [[base/incident-response/ops-incident-commander]] — Run an incident as a commander
- ...

### Optional

- [[base/platform/internal-platform-strategy-author]] — Strategy for an internal platform org
- ...

## Personas

### @jane-devops — On-Call Brain (12 neurons)

- [[personas/jane-devops/neurons/2024-08-flaky-tests]] — Aug 2024 — Flaky CI in fintech
- [[personas/jane-devops/neurons/2024-10-blue-green-rollback]] — Oct 2024 — Blue/green rollback at 3am
- ...

### @another-creator-handle — ... (N neurons)

- ...
```

The structure is generated from `occupation_skills` (grouped by
`domain`, sub-grouped by `role`) and `persona_neurons` (grouped by
`section` if set, sorted by `sort_order`).

---

## 10. Composition algorithm (delivery time)

```
def compose(buyer_id, occupation_license_id, persona_license_ids=None):
    occ_license = load_license(occupation_license_id)
    assert occ_license.buyer_id == buyer_id
    assert occ_license.composition_role == 'occupation'
    assert occ_license.status == 'active'

    occ_version = resolve_entitled_version(occ_license)    # uses delivery/service.entitled_version
    occ_build = latest_succeeded_build(skill_version_id=occ_version.id)
    assert occ_build is not None       # if None: 202 + queue rebuild

    if persona_license_ids is None:
        persona_licenses = all_active_persona_licenses_for_buyer_and_occupation(
            buyer_id, occ_license.skill_id
        )
    else:
        persona_licenses = [load_license(i) for i in persona_license_ids]
        for pl in persona_licenses:
            assert pl.buyer_id == buyer_id
            assert pl.composition_role == 'persona'
            assert pl.target_occupation_skill_id == occ_license.skill_id
            assert pl.status == 'active'

    persona_builds = []
    for pl in persona_licenses:
        pv = resolve_entitled_version(pl)
        pb = latest_succeeded_build(skill_version_id=pv.id)
        if pb is None:
            continue                    # skip; surface as warning in manifest
        persona_builds.append((pl, pb))

    cache_key = sha256(occ_build.id || sorted([pb.id for _, pb in persona_builds]))
    if cached := redis.get(f"composed:{buyer_id}:{occ_license.skill_id}:{cache_key}"):
        if s3.exists(cached.storage_url):
            return cached

    # --- merge ---
    with tempdir() as work:
        unzip(s3.get(occ_build.storage_url), work)
        for _, pb in persona_builds:
            unzip_into(s3.get(pb.storage_url), work, only_paths=["personas/"])

        # rewrite 00-index.md to include personas listed
        regenerate_index(work, occ_build.manifest_json, [pb.manifest_json for _, pb in persona_builds])

        # rewrite vault.json (compose files[], attribution_index, personas[], warnings[])
        composed_manifest = compose_manifest(occ_build.manifest_json,
                                             [(pl, pb.manifest_json) for pl, pb in persona_builds])
        write_json(work / "vault.json", composed_manifest)

        # re-resolve links across the composed surface; update file `links_resolved` flags
        resolve_links_in_place(work, composed_manifest)

        # per-buyer watermark on every .md
        for md_file in work.rglob("*.md"):
            content = md_file.read_text()
            stamped = append_license_watermark(content, occ_license.id, buyer_id)
            md_file.write_text(stamped)

        # zip
        bundle_bytes = zip_directory(work)
        composed_hash = sha256(bundle_bytes)

        # upload to short-lived delivery prefix
        nonce = secrets.token_urlsafe(12)
        delivery_key = f"delivery/vaults/{nonce}.zip"
        s3.put(delivery_key, bundle_bytes)

        # record vault_downloads
        insert vault_downloads(
            occupation_license_id=occ_license.id,
            buyer_id=buyer_id,
            occupation_build_id=occ_build.id,
            persona_build_ids=[pb.id for _, pb in persona_builds],
            persona_license_ids=[pl.id for pl, _ in persona_builds],
            composed_hash=composed_hash,
            storage_url=delivery_key,
            user_agent_hash=..., ip_hash=...
        )

        url = s3.presign(delivery_key, ttl=60)
        redis.setex(f"composed:{buyer_id}:{occ_license.skill_id}:{cache_key}",
                    timedelta(hours=24), {url, composed_hash, delivery_key})
        return {download_url=url, composed_hash=composed_hash, expires_at=...}
```

Determinism notes:
- Folder traversal in zip must be **sorted** so two runs over the same
  inputs produce byte-identical archives (modulo the timestamped
  watermark which we accept as variation).
- The per-buyer watermark uses `datetime.now()` — the composed_hash is
  computed AFTER watermark is applied. Therefore two downloads by the
  same buyer at different times will differ by `composed_hash`. That
  is by design (audit trail).

---

## 11. Validation rules added to the existing validator

The existing `apps/api/src/skills/validator.py` is extended (NOT
replaced) with rules that only fire when the new optional fields are
present:

| Rule | Code | Triggered when |
|---|---|---|
| `kind` must be in the enum | `frontmatter.kind: invalid_kind` | `kind` set to an unrecognized value |
| `links[].relation` must be in the enum | `frontmatter.links.N.relation: invalid_relation` | always |
| `kind=persona` requires `parent_occupation_id` | `frontmatter.parent_occupation_id: required_for_persona` | `kind=persona` AND field absent |
| `kind=memory_neuron` requires `neuron` block with `situation`, `decision`, `outcome`, `recorded_at` | `frontmatter.neuron: required_for_memory_neuron` | `kind=memory_neuron` AND block missing or incomplete |
| `vault_path` MUST NOT be set by creator | `frontmatter.vault_path: platform_authored_field` | `vault_path` present at validate-on-publish time (the builder is allowed to set it) |
| filename matches `[a-z0-9-]{1,80}\.md` (kebab-ASCII rule from ADR-011) | `filename: invalid_format` | filename violates pattern; checked by the builder, not validate_file |
| For `kind=memory_neuron`: at least one `link` targeting `base/` | `frontmatter.links: neuron_needs_base_link` | warning only — surfaces in `manifest.warnings[]`, not a hard fail |

The validator changes are **additive only**. A file with `kind`
absent and no other new fields passes exactly as before. All existing
fixtures continue to validate green.

---

## 12. ZIP format

- DEFLATE compression, standard ZIP64.
- File entries are stored with POSIX paths (forward slashes).
- File timestamps inside the zip are set to a deterministic constant
  (`2026-01-01T00:00:00Z`) so two runs over the same content produce
  identical archives. (The composed hash will still differ across
  downloads because of the per-buyer watermark in file bodies.)
- Total size cap for MVP: 50 MB per vault. Hard reject at build time
  with code `vault_build.too_large` to keep the demo predictable.

---

## 13. Manifest schema version

The `schema_version` field in `vault.json` is `1` for MVP. The
manifest schema is published at `apps/api/src/vault/schema/vault-manifest-v1.json`
and packaged into `packages/skills-schema/` so downstream tools can
validate against it.

Future bumps:
- `2`: add semantic-vector embeddings inline for fast offline search.
- Anything that adds a required field without a default is a major bump.

---

## 14. Composition cache invalidation

Triggers that invalidate `composed:{buyer_id}:{occupation_id}:*`:
- A new vault_build for the occupation succeeds (occupation upgrade).
- A new vault_build for any persona the buyer owns succeeds.
- The buyer adds or removes a persona license.
- The occupation or persona is yanked.

Implementation: on the publish/yank/license events listed above, the
service writes a Redis SET membership operation
(`composed_invalidate:{buyer_id}` += {occupation_id}) which the
composer checks on read. Cheaper than KEY scan invalidation. Cleanup
via TTL on the cache entries themselves.

---

## 15. What lives where

| Concern | Code path |
|---|---|
| Build a single occupation vault | `apps/api/src/vault/builder.py` (new) |
| Build a single persona vault | same module |
| Compose buyer-specific bundle | `apps/api/src/vault/composer.py` (new) |
| Validate a built vault on disk | `apps/api/src/vault/validator.py` (new) |
| Manifest schema | `apps/api/src/vault/schema/vault-manifest-v1.json` |
| Watermark reuse | `apps/api/src/delivery/watermark.py` (existing — reused) |
| S3 reuse | `apps/api/src/storage/s3.py` (existing — reused) |
| Arq jobs | `apps/api/src/vault/jobs.py` (new) — `build_occupation`, `build_persona`, `compose_vault` |

---

## 16. TBD

- **TBD:** Whether to include the parent occupation's `00-index.md`
  inside a persona's standalone build artifact so a creator can preview
  in isolation. Lean **no** — the persona vault build contains only
  `personas/{handle}/` and a minimal manifest slice; preview tooling
  composes on the fly even for the creator.
- **TBD:** Whether to ship a top-level `LICENSE.md` alongside `README.md`
  carrying the per-buyer license terms. Probably yes for MVP — the
  composer drops in a templated copy with the buyer's email and the
  vault_download id.
- **TBD:** Whether to add an `.obsidian/` config dir that pre-sets sane
  graph view colors. Probably yes for the demo — a single
  `graph.json` with edge-weighted color by `relation` makes the demo
  pop. Adds ≈100 bytes. Not required by spec; can land in Curation's
  build script.

---
