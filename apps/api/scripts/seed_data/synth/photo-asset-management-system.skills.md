---
id: skillsgit-curated/photo-asset-management-system
version: 1.0.0
name: Photo Asset Management System
description: Manage a growing photo asset base at scale with ingestion taxonomy, sidecar discipline, keyword strategy, rights metadata, layered backups, and a search workflow that still finds files in five years.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: creative
tags: [niche:photo-raw-workflow, dam, asset-management, metadata, keywording, backup, rights, search]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6500
trigger_keywords:
  - digital asset management
  - dam
  - photo library
  - photo archive
  - keywording strategy
  - sidecar files
  - iptc metadata
  - photo backup
  - rights metadata
  - photo search
  - color labels
  - folder structure
  - catalog management
example_invocations:
  - "Design a digital-asset-management system for a 200,000-photo personal archive."
  - "How should a small studio structure folders, keywords, and backups for client work?"
  - "Migrate a flat folder archive to a properly catalogued library without losing capture-time order."
  - "Set up a rights and licensing metadata convention for a stock-contributing photographer."
inputs:
  - name: archive_scale
    type: choice
    required: true
    description: Approximate library size. Determines tooling and process recommendations.
    choices: [under-10k, 10k-100k, 100k-1m, over-1m]
  - name: working_context
    type: choice
    required: true
    description: Who the library serves. Drives rights, sharing, and retention defaults.
    choices: [personal, freelance, studio, agency, stock, archive-institution]
  - name: current_state
    type: text
    required: false
    description: What exists today — folder layout, naming, any catalogue tool in use, known pain points.
outputs:
  - name: system
    type: markdown
    description: A specification of the asset-management system covering ingestion, taxonomy, metadata, backups, and search.
  - name: migration
    type: markdown
    description: A migration plan from current state to the target system, with checkpoints and rollback notes.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when an agent is asked to design, audit, or migrate a photo asset management setup at scale and the question is about the system rather than about a single shoot. Typical triggers:

- A photographer's personal or professional archive has grown past the point where ad-hoc folders are workable and something more structured is needed.
- A studio is bringing on additional photographers and editors and needs a shared catalogue convention.
- An archive is being migrated from one catalogue tool to another and the user wants to ensure metadata survives.
- A stock contributor or rights-managed shooter needs to attach licensing, model release, and embargo state to thousands of files reliably.

Do not invoke this skill for single-shoot ingest decisions (use the RAW development-pipeline skill), for colour-management setup (use the colour-management skill), or for retouching technique (use the retouching skill). Defer to an institutional archive specialist for cultural-heritage or legal-evidence preservation requirements, which carry obligations beyond ordinary photographic asset management.

This skill assumes a working DAM-class tool exists (the user has chosen, or will choose, a catalogue that supports sidecars, keywords, and search). The principles transfer to any such tool; the skill is intentionally non-prescriptive about which one.

## How to apply

Design the system in seven layers. Each layer has its own decisions and its own failure modes.

### Layer 1: Tool choice and constraints

1. Pick a catalogue tool whose database format is documented or open enough that the archive is not held hostage. A proprietary catalogue that locks the user in is a liability for an archive measured in decades. Prefer tools that write sidecars on disk for every change, so the catalogue can be rebuilt if the database is lost.

2. Decide whether to run a single catalogue or multiple. A single catalogue scales easier to about half a million files on commodity hardware. Beyond that, split by year, by project, or by client. Splitting by anything that the user actually searches by (rather than by file count) keeps the splits meaningful.

3. Treat the catalogue as derived state. The disk layout and the sidecar files are the source of truth. The catalogue is an index that can be rebuilt. This inverts the assumption many catalogue tools push and is the single most important principle for long-term recoverability.

### Layer 2: Folder taxonomy

4. Folders carry capture-time ordering and shoot context, not subject matter. A workable convention: `library_root/{year}/{yyyy-mm-dd}_{shoot-slug}/{filename}`. Subject matter belongs in keywords, not folders, because a single shoot may span subjects and a single subject may span shoots.

5. Resist the urge to add hierarchy below the shoot level. Subfolders like `selects/`, `edited/`, `delivered/` are sometimes useful for client work but make migration harder. Prefer keywords and colour labels to express state; if subfolders are unavoidable, name them with a leading underscore so they sort to the top and are easy to spot during audit.

6. Reserve filename patterns for sortability. A pattern such as `{yyyymmdd}_{hhmmss}_{camera-id}_{sequence}` keeps filenames unique, sortable, and identifiable even if removed from the catalogue. Resist embedding subject information in the filename — it goes stale and contradicts the metadata.

### Layer 3: Sidecar discipline

7. Configure the catalogue to write metadata to sidecars (XMP or matching format) on every edit. Settings stored only in the catalogue's internal database are at risk if the database is lost or corrupted. Sidecars travel with the file.

8. Treat the sidecar as authoritative for all metadata: ratings, labels, keywords, captions, rights, and develop settings. If the sidecar disagrees with the catalogue, the sidecar wins on re-import.

9. Inspect sidecars at scale periodically. Tools that read XMP from disk can be used to verify that every file in the archive has a sidecar and that the sidecar contains the metadata the catalogue says it should. Drift is detectable; un-detectable drift is the failure mode that loses archives.

### Layer 4: Metadata fields and conventions

10. Standardise on a small set of IPTC and XMP fields the user will actually maintain. A workable minimum:

    - Title / headline: short, human-readable name for the image.
    - Description / caption: one or two sentences describing the subject and context.
    - Keywords: a controlled vocabulary, not free text.
    - Creator / by-line: photographer name.
    - Copyright notice: machine-readable rights statement.
    - Rights usage terms: human-readable summary of what the file may be used for.
    - Location: city, state, country at minimum; GPS where available.
    - People shown: structured list of identifiable individuals.
    - Event: shoot or assignment name.

11. Build the keyword hierarchy as a controlled vocabulary, not as ad-hoc tags. A small studio's hierarchy might split by who, what, where, when, why, and how. Keep it shallow: three levels is usually enough. Keep entry-point synonyms in the catalogue so "auto" and "car" do not both exist as separate top-level keywords.

12. Apply keywords at ingest as a coarse pass, then refine during cull. Coarse-pass keywords come from the shoot context (location, event, primary subject). Refined keywords come from looking at the frames. A shoot that gets only coarse-pass keywords is still findable; an unkeyworded shoot effectively does not exist in a large archive.

13. Use colour labels for state and stars for quality. A workable colour-label convention:

    - No label: working state, no special handling.
    - Red: needs retouch beyond global development.
    - Yellow: client question or hold outstanding.
    - Green: released or delivered.
    - Blue: legal hold — no use until cleared.
    - Purple: portfolio candidate.

    Stars track quality on the same one-to-five scale across the archive. Star creep is real; resist re-rating files higher just because a frame still looks good five years later, because the rating loses calibration if it drifts.

### Layer 5: Rights and consent

14. Attach a rights notice to every file at ingest, even personal archives. The default for client work is the contract's grant; the default for personal work is "all rights reserved". An archive without a rights line is harder to license later and harder to defend against unauthorised use.

15. Track model and property releases as a separate metadata field that the catalogue can search on. A frame without a release is not deliverable for commercial use; a search that filters by "has release = true" should be one click away in the catalogue.

16. Record embargo dates explicitly. An assignment with an embargo of six months should fail a delivery check until that date passes. Treat embargo as a hard constraint, not a soft note.

17. For stock-contributing photographers, maintain the stock-agency-specific keyword and category requirements per agency. Cross-agency portability is best served by maintaining a master keyword set and exporting subsets per agency rather than maintaining separate keyword sets per agency.

### Layer 6: Backup and durability

18. Apply the long-standing 3-2-1 backup principle: three copies, two media types, one off-site. The "off-site" copy is the one that survives a fire, a flood, or theft. For photo archives the off-site copy is usually a cloud-storage tier or a physically removed external drive.

19. Verify backups, do not assume them. A backup script that has never been tested is not a backup. Recovery testing at least quarterly catches silent corruption, missing folders, and changed paths that the user did not notice.

20. Separate working storage from archive storage. Working storage holds recent shoots that are still in active edit; archive storage holds delivered, finalised projects. Archive storage can be slower and cheaper. Don't archive working files mid-project — the round-trips are tedious.

21. Plan for media degradation. Spinning disks fail at five-to-eight-year scales, SSDs at similar scales with different failure modes. Optical media is unreliable for long-term storage in practice. Cloud storage abstracts the media but introduces vendor risk; the off-site copy should ideally be on media the user controls.

22. Maintain a chain of catalogues. Each backup of the catalogue file should be retained for some period — daily for two weeks, weekly for three months, monthly for two years. A catastrophic accidental change to the catalogue is recoverable if the prior version is on disk somewhere.

### Layer 7: Search workflow

23. Design searches that survive growth. A search that worked at ten thousand files may time out or be unusable at a million. Prefer searches that combine three or four narrow criteria over searches that depend on a single keyword.

24. Maintain a "smart album" or saved-search library for common views: portfolio candidates by year, work pending retouch, blue-label legal holds, files delivered to a specific client. Saved searches are documentation: a new collaborator learns the archive's structure by reading them.

25. Index full text of captions and descriptions, not only keywords. Free-text search finds files that the controlled vocabulary missed, especially for older imports where keywording was uneven.

26. Audit the archive yearly. Run a "files without keywords", "files without rights", "files without backup verification" report and resolve gaps. The audit is the only way to find files that have fallen out of the system.

## Migration considerations

When moving an archive into the system from an unstructured state:

- Inventory the source first. Count files, list extensions, note the existing folder layout, and read out whatever metadata is already on disk.
- Plan the migration in batches by year, oldest first. Oldest files are usually the most metadata-poor and the most error-prone; doing them first surfaces problems before they accumulate at scale.
- Preserve capture-time order during migration. Renaming by ingest-time, file-system-time, or any non-capture-time clock loses the photographer's actual chronology.
- Do not delete source files until at least two verified copies of the migrated archive exist, including one off-site.
- Snapshot the catalogue at each migration milestone so a botched batch can be rolled back without redoing earlier batches.

## Inputs

- `archive_scale` — required choice. Influences whether tooling recommendations are personal-tier or institutional-tier.
- `working_context` — required choice. Drives rights and retention defaults.
- `current_state` — optional text. Lets the migration plan be specific.

## Outputs

- `system` — markdown. The seven-layer system specification.
- `migration` — markdown. A migration plan with checkpoints.

## Reference templates

### Personal archive template (under 100k files)

- Tool: single catalogue with sidecars enabled.
- Folders: `library/{year}/{yyyy-mm-dd}_{trip-or-event-slug}/`.
- Keywords: shallow tree — Who / What / Where / When / Why with three to five entries per branch maintained.
- Labels: green = released to family or web; purple = portfolio; red = needs retouch. Others reserved.
- Stars: 1-3 only routinely; reserve 4-5 for genuine standouts.
- Rights: "All rights reserved — {photographer name}" default.
- Backup: working drive + on-site external + cloud or off-site external, with monthly verified sync.

### Freelance studio template (under 500k files)

- Tool: shared catalogue with sidecars and a documented multi-user workflow.
- Folders: same year/date/slug pattern, plus a top-level split between `clients/` and `personal/`.
- Keywords: controlled vocabulary aligned to client industries; bulk-update sessions quarterly to retire orphan tags.
- Labels and stars: written into the studio handbook; new collaborators read it on day one.
- Rights: per-client contract grant; default reverts to all-rights-reserved after the licence term.
- Backup: working NAS + nightly off-site cloud + verified quarterly restore drills.

### Stock contributor template

- Tool: catalogue plus a separate per-agency export-staging workflow.
- Folders: same year/date/slug pattern; production-ready files maintained in their own state via colour label.
- Keywords: master controlled vocabulary; per-agency export maps to agency requirements.
- Releases: model and property releases attached as metadata; release-status filter blocks unreleased files from delivery.
- Backup: per personal archive plus a separate archive of releases (PDFs and signed forms) under matched retention.

## Common failure modes

- **Catalogue lost or corrupted, files orphaned**: the catalogue database is the only source of ratings, keywords, and develop settings. Caused by treating the catalogue as the source of truth rather than as derived state. Fix: turn on sidecar writing immediately; rebuild from sidecars; commit to sidecar-first discipline going forward.
- **Keywords sprawl into incoherence**: thousands of free-text tags accumulate, some near-duplicates, some single-use. Caused by allowing free-text keywording without a controlled vocabulary. Fix: define a hierarchical vocabulary; bulk-update via metadata tooling; retire orphan tags.
- **Files without rights metadata become unusable**: legacy frames cannot be licensed because no rights line is on them. Caused by inconsistent rights application during ingest in years past. Fix: bulk-write a default rights statement to all files lacking one; review high-value files individually.
- **Backup looks intact, restore fails**: routine backups run but no restore has ever been tested. Caused by skipping recovery testing. Fix: schedule quarterly recovery drills; document a recovery runbook.
- **Off-site copy too stale to be useful**: the off-site copy was last updated six months ago and the studio's working drive failed yesterday. Caused by manual off-site sync that fell behind. Fix: automate the off-site sync; alert on missed sync windows.
- **Search slows to unusable as the archive grows**: ten-thousand-file searches were instant, two-hundred-thousand-file searches take minutes. Caused by single-keyword broad searches and an unindexed catalogue. Fix: design narrower compound searches; rebuild catalogue indexes; consider splitting the catalogue.
- **Two collaborators contradict each other in ratings and labels**: red labels meant different things to each. Caused by no documented convention. Fix: write the convention into the shoot-manifest template and the studio's onboarding doc.

## Examples

Example invocation: "I'm a freelance event photographer with 180,000 files across ten years, currently in dated folders with random subfolder names, no catalogue tool, no consistent backup beyond an external drive. Design the system."

Expected output: a recommendation to adopt a catalogue tool that writes sidecars; a folder rationalisation to `library_root/{year}/{yyyy-mm-dd}_{shoot-slug}/`; a controlled-vocabulary keyword set seeded from the user's typical event types; a colour-label convention for delivery state; a rights field standardised across the archive; a 3-2-1 backup plan that adds a verified off-site cloud tier; a migration plan in yearly batches from oldest to newest, with checkpoints and rollback notes; and a quarterly recovery-test reminder.

Second example: "Two-photographer studio, shared catalogue, client work, growing 30,000 files a year, currently no formal convention." Expected output: a shared catalogue convention written into a studio handbook; folder pattern identical to the personal case; a controlled vocabulary scoped to the studio's client industries; explicit rules for who writes ratings (the photographer) versus who writes labels (whoever advances the work); a backup plan that includes a NAS on-site and a cloud off-site, with daily verification.

Third example: "Stock contributor with 80,000 files across multiple agencies, each agency has different keyword and metadata requirements." Expected output: a master keyword set maintained locally; per-agency export views that translate the master keywords to each agency's required format; agency-specific rights and release tracking; a release-status filter that blocks delivery of files without a model or property release.

## Limitations

This skill does not recommend specific commercial catalogue tools, because tool choice is fast-moving and contextual. It also does not cover institutional archival preservation (PREMIS metadata, fixity audits at archival scale, OAIS reference model) — those domains have their own established methodologies and an archivist should be consulted. The rights and consent guidance is general; jurisdiction-specific image rights, especially where minors or sensitive contexts are involved, may impose additional obligations the agent should defer to qualified counsel on. Backup recommendations assume the user controls the media; managed-cloud-only archives have vendor and contractual considerations beyond what the skill covers.

## Sources reviewed

- https://github.com/KDE/digikam (GPL-2.0)
- https://github.com/exiftool/exiftool (Artistic / GPL-1.0-or-later)
- https://github.com/darktable-org/darktable (GPL-3.0)
- https://github.com/RawTherapee/RawTherapee (GPL-3.0)
- https://github.com/aferrero2707/PhotoFlow (GPL-3.0)
- https://github.com/LibRaw/LibRaw (LGPL-2.1 / CDDL-1.0)
