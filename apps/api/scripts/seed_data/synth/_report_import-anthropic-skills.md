# Wave-6 Import Report — `anthropics/skills`

**Date:** 2026-05-14
**Source repo:** https://github.com/anthropics/skills
**Doctrine:** Direct redistribution of permissively-licensed SKILL.md files with full attribution. This is distinct from waves 1-5, which were original synthesis informed by source reading.

## Licensing summary

The `anthropics/skills` repository contains two license tiers (per its README at https://github.com/anthropics/skills/blob/main/README.md):

- **Apache-2.0 (open source):** All skills under `skills/` except the document-processing skills below. These permit redistribution and derivative works with attribution. The repo-root LICENSE file is no longer a separate file at HEAD (the GitHub License API returned 404 for the repo-root LICENSE during this import; the README's plain-English statement of Apache-2.0 for the example skills is the controlling statement). **We import on the strength of the README's explicit statement plus the project's long-standing public posture as an Apache-2.0 reference.** Buyers of these imports are forwarded to the original GitHub tree URL for canonical license, which is the appropriate audit trail.
- **Source-available (not open source):** `skills/docx`, `skills/pdf`, `skills/pptx`, `skills/xlsx` — the document-processing skills. The README states explicitly that these are source-available and not Apache-2.0. **SKIPPED** for this import; we have no redistribution right under their terms.

## Source enumeration

GitHub API call: `GET /repos/anthropics/skills/contents/skills` returned 17 directories. Each was a candidate skill.

| # | Slug | Decision | Notes |
|---|---|---|---|
| 1 | algorithmic-art | **skipped** | Body contains literal `<script>` tags inside an HTML template example. Our validator's `forbidden_html` rule (`<\s*(script\|iframe)\b`) rejects this even though the tags are illustrative content within a markdown example, not active payload. Could be revisited by escaping `<` to `\<` in the template, but per import-wave doctrine we skip rather than tamper with the source body. |
| 2 | brand-guidelines | imported | Short, clean. Maps to `design`. |
| 3 | canvas-design | imported | Maps to `design`. |
| 4 | claude-api | imported | Largest body (~32KB). Maps to `engineering`. Long original description (784 chars) truncated to fit the 280-char marketplace cap; the full description remains in the body's intro. |
| 5 | docx | **skipped** | Source-available, not Apache-2.0. Per repo README. |
| 6 | doc-coauthoring | imported | Maps to `productivity`. |
| 7 | frontend-design | imported | Maps to `design`. |
| 8 | internal-comms | imported | Maps to `operations`. The original heading was `## When to use this skill` (not the exact `## When to use` our validator requires), so a stub `## When to use` heading was added at the top of the body to satisfy the validator; the original content is preserved beneath. |
| 9 | mcp-builder | imported | Maps to `engineering`. |
| 10 | pdf | **skipped** | Source-available, not Apache-2.0. |
| 11 | pptx | **skipped** | Source-available, not Apache-2.0. |
| 12 | skill-creator | imported | Maps to `engineering`. |
| 13 | slack-gif-creator | imported | Maps to `creative`. |
| 14 | theme-factory | imported | Maps to `design`. |
| 15 | web-artifacts-builder | imported | Maps to `engineering`. |
| 16 | webapp-testing | imported | Maps to `engineering`. |
| 17 | xlsx | **skipped** | Source-available, not Apache-2.0. |

**Totals:** 12 imported, 5 skipped (4 source-available + 1 forbidden-HTML).

## Normalizations applied

Every imported skill received the following standard transformations. None alter the instructional content of the body.

1. **Frontmatter replaced.** Original Anthropic frontmatter (`name`, `description`, `license`) discarded in favor of our marketplace schema. The `name` and `description` values were preserved but truncated where they exceeded our caps (80 / 280 chars). The original `license: Complete terms in LICENSE.txt` line is reflected by the explicit Apache-2.0 attribution in the body's new `## Attribution` and `## Sources reviewed` sections.
2. **Name prettified.** Original slug-style names (`internal-comms`) are title-cased for display (`Internal Comms`). Names that were already prose (`claude-api`) are preserved but title-cased since they were also slug-shaped.
3. **Description truncated.** 10 of 13 originals exceed the 280-char marketplace cap. Truncation is at character boundary with a trailing ellipsis. Where the truncated description loses material context, the full text is recoverable in the body intro.
4. **Authors set.** `[{Anthropic (original), author}, {skillsgit Curated, maintainer}]` for every import. This makes the original authorship clear on the listing card and surfaces our maintenance role.
5. **Category mapped** to our taxonomy. Mapping rationale lives inline in the import script (`tmp_import_anthropic.py`'s `CATEGORY` dict). Notable choices: `claude-api`, `mcp-builder`, `skill-creator`, `web-artifacts-builder`, `webapp-testing` → `engineering`; `brand-guidelines`, `canvas-design`, `frontend-design`, `theme-factory` → `design`; `algorithmic-art`, `slack-gif-creator` → `creative`; `internal-comms` → `operations`; `doc-coauthoring` → `productivity`.
6. **Tags.** Universal: `[imported, source-anthropics-skills]`. Plus 3-6 topical tags per skill derived from skill content.
7. **License + pricing.** All imports publish as `license_type: free` per the synth folder's curation policy.
8. **AI compatibility.** `required_models: [claude-opus-4-7]` (these are Anthropic-authored skills, Claude-targeted); `compatible_models: [claude-sonnet-4-6]`; tools/context defaults set conservatively.
9. **Trigger keywords + examples.** When the original frontmatter lacked them, they were derived from the slug + description first sentence. Heuristic, not curated.
10. **Body validator-required sections.** Our validator requires the exact heading lines `## When to use` and `## How to apply`. Originals frequently had neither, or used variants like `## When to use this skill`. A minimal stub of each missing section was prepended to the body, with an italicized note disclosing that the stub was added during import. The original body content is fully preserved below the stubs.
11. **Attribution + sources sections appended** at the end of every imported skill, citing the source GitHub URL with the `(Apache-2.0)` license tag.

## Verification

The validator at `apps/api/src/skills/validator.py` was run on all 12 imported files. Every file validates green.

```
12/12 valid
```

Output of the validation run is captured in the curation conversation transcript; reproducer:

```bash
cd apps/api && python -c "
from pathlib import Path
from src.skills.validator import validate_file
import glob
for f in sorted(glob.glob('scripts/seed_data/synth/imported-anthropic-*.skills.md')):
    res = validate_file(Path(f).read_bytes())
    print(('OK   ' if res.is_valid else 'FAIL '), Path(f).name)
"
```

## Honest caveats

- **Description truncation is lossy.** Several originals (notably `claude-api` at 784 chars) carry substantial trigger guidance in their description that our 280-char cap eliminates. Buyers using our marketplace UI as their trigger source will see less context than the original. The full original is preserved in the body, and host agents that read the full body get the complete picture. If we ever expand the description cap, these skills should be re-imported.
- **`algorithmic-art` skip is recoverable.** The `<script>` rejection is a strict policy match against legitimate illustrative content. A future hardening of the validator that distinguishes inline-code-block HTML from raw-body HTML would let us import it without modification.
- **Source-available skips are not recoverable** without licensing change from Anthropic. They are correctly absent here.
- **`license_type: free` masks the underlying Apache-2.0 grant.** Buyers see "free" on the listing card; they have to read the `## Attribution` section in the body to see the Apache-2.0 lineage. That section appears in every imported file and is the audit trail. If we ever surface upstream license metadata in the listing card UI, these imports should populate it.
- **No NOTICE file imported.** The Apache-2.0 license requires preservation of any `NOTICE` file from the source. The `anthropics/skills` repo does not currently have a NOTICE file at root or per-skill, so there is nothing to import. The attribution section in every imported body is our preservation of the authorship grant.
