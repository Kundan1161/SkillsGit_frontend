# skill-creator — 00 Overview

**Phase:** 3
**Depends on:** all of Phase 1–2 (the marketplace must work first), `00-vision.md`, `shared/skills-md-spec.md`
**Parallel-safe with:** all skill-creator/* siblings
**Status:** ready

> The creator app is what makes a **non-technical professional** able to publish a skill. It is the second half of the product. **Do not start coding here until Phase 2 is done.**

---

## What the creator app is

A standalone Next.js app (`apps/web-creator/`) that signs in with the same accounts as the marketplace and persists draft skills to the same FastAPI backend. The visual canvas is the heart of it.

A creator using this app should be able to:
1. Start a new skill from scratch on a blank canvas.
2. OR import an existing project from Claude Code, OpenAI Custom GPT, OpenAI Assistant, or Codex — and see a populated graph.
3. Add nodes (context, decision, parameter, action, output) and wire them together.
4. Fill in metadata: name, category, tags, pricing, AI runtime requirements.
5. Compile the graph into a valid `skills.md` and preview it.
6. Test the skill in a sandbox against the target model(s) with sample inputs.
7. Publish to the marketplace in one click → enters `pending_review`.
8. Edit the graph later, bump the version, push an update — all from the same canvas.

---

## Top-level pages

```
/                                   creator home — list of my drafts + recent activity
/skills/new                          new skill chooser: blank, import, template
/skills/{id}/builder                 the visual canvas (main editor)
/skills/{id}/config                  metadata, pricing, AI requirements form
/skills/{id}/preview                 compiled skills.md preview
/skills/{id}/sandbox                 sandbox runs against model(s)
/skills/{id}/publish                 publish wizard
/skills/{id}/versions                version history (read-only view of versions)
/import                              import wizard (Phase 4)
/templates                           starter templates by industry
/settings                            shared with marketplace (links into marketplace settings)
```

The dashboard (sales, earnings, etc.) stays in the marketplace app at `/dashboard`. There's a shared top-nav link between them.

---

## Prompt-to-feature map

| Prompt | Owns |
|---|---|
| `01-visual-builder.md` | React Flow canvas, node types, palette, inspector, graph → skills.md compiler |
| `02-import-from-projects.md` | Importers for Claude Code, GPTs, Assistants, Codex |
| `03-skill-config.md` | Metadata forms, AI requirements, pricing |
| `04-test-and-preview.md` | Sandbox runtime, model picker, compiled preview |
| `05-publish-to-marketplace.md` | Publish wizard, version creation, hand-off to marketplace |

---

## Design principles (specific to this app)

1. **The graph is the source of truth in-edit.** Markdown is generated, not edited directly. (Power users may export and edit raw markdown, but re-opening re-parses; lossy by design.)
2. **Forgiving over strict.** Drafts may be invalid for long stretches. Validation is non-blocking until publish.
3. **Templates over blank canvas.** The default new-skill flow shows a 3×4 grid of templates by industry (finance, design, marketing, …) — picking one drops in a 5–8 node starter graph.
4. **Autosave aggressively.** Every meaningful interaction debounce-saves to backend within 1s. No "save" button in the UI.
5. **Visual diff on update.** When pushing a new version, show the creator a side-by-side: previous skills.md vs new skills.md, with the version-bump suggestion (see `marketplace/06-versioning-and-updates.md`).

---

## Storage model (creator-specific tables)

Add to the data model (define in `01-visual-builder.md`):

### `skill_drafts`

Holds the **live graph state** while editing. Distinct from `skill_versions` (which is immutable published files).

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| skill_id | uuid fk → skills.id | one draft per skill at a time (unique) |
| graph_json | jsonb | nodes + edges in React Flow shape |
| frontmatter_json | jsonb | working metadata, edited via config form |
| compiled_md | text | last successful compile, for preview |
| compiled_valid | bool | last `validate_file()` result |
| compile_errors | jsonb | last validation errors, if any |
| target_version | text | semver the creator is bumping toward |
| based_on_version | uuid fk → skill_versions.id | nullable; what version this draft is based on, for diffing |
| updated_at | timestamptz | |
| autosave_count | int | for ops insight |

### `skill_draft_snapshots`

Periodic snapshots for "Undo to yesterday".

| col | type |
|---|---|
| id | uuid pk |
| draft_id | uuid fk |
| graph_json | jsonb |
| frontmatter_json | jsonb |
| created_at | timestamptz |
| label | text | nullable; e.g., "after importing GPT" |

Snapshot policy: every 10 minutes during an active session, on import completion, on publish.

---

## Cross-app navigation

- Marketplace user-menu has a "Open creator" item that deep-links to `/dashboard` if 0 skills, otherwise to the creator home.
- Creator top-nav has a "View marketplace" link.
- Same auth cookie works on both. Both share `packages/api-client` and `packages/ui`.

---

## Phase 3 success looks like

A non-technical financial analyst:
1. Signs up, becomes a creator.
2. Picks the "DCF Valuation Template" from the templates grid.
3. Edits the nodes to match her firm's process (renames variables, adjusts step prompts).
4. Sets pricing: one-time $29.
5. Picks Claude Opus + Sonnet as required models.
6. Runs the sandbox with a sample 10-K — gets a DCF output.
7. Hits Publish — skill goes to `pending_review`.
8. Total time: under 30 minutes.

---

## Phase 4 success looks like

A designer who has an existing Custom GPT for design critique:
1. Goes to `/import`.
2. Pastes their GPT URL or uploads the GPT export.
3. Sees a populated graph: context node ("you are a senior designer reviewer..."), 5 decision nodes (visual hierarchy, accessibility, brand fit, etc.), output node ("critique with severity levels").
4. Reviews the auto-extracted frontmatter (description was guessed; she edits it).
5. Hits Publish.

---

## Non-goals

- No multi-author co-editing in Phase 3. Single-creator drafts.
- No version-control git-style branching. Drafts are linear; snapshots provide rollback.
- No "fork this skill" feature. Skills are owned by their creator.
- No marketplace browsing inside the creator app. Send users to marketplace pages.
