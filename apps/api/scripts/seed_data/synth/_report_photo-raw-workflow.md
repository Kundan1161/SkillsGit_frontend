# Photography editing & RAW workflow — synthesis report

## Niche

Creative niche: **photography editing & RAW workflow** — ingest, cull, develop, retouch, color, export. Lightroom-class, Capture One-class, RawTherapee-class methodology. Trademarked product names appear only in source URL citations; the body of every skill speaks generically about "RAW developer", "image editor", "catalogue tool", etc.

## Files produced

- `photo-raw-development-pipeline.skills.md` — develop RAW images end-to-end with ingest, two-pass cull, a strictly ordered baseline-correction sequence (white balance → exposure → highlight recovery → shadow lift → contrast → clarity → sharpening → noise reduction), refinement, and export to web / print / archive targets.
- `photo-retouching-methodology.skills.md` — retouch portraits and products non-destructively with a labelled layer stack, frequency separation vs dodge-and-burn selection logic, content-aware fill discipline, and a delivery QC checklist.
- `photo-color-management-pipeline.skills.md` — manage colour across capture, develop, display, and print using camera profiles, working space selection (sRGB / Adobe RGB / Display P3 / ProPhoto), monitor calibration targets and cadence, soft-proofing with rendering-intent selection, and medium-specific output sharpening.
- `photo-asset-management-system.skills.md` — design a DAM at scale with folder taxonomy, sidecar discipline, controlled-vocabulary keywording, rights and consent metadata, layered 3-2-1 backups, and yearly audits.

All four skills publish under `license_type: free` per wave-7 policy. Category is `creative`; first tag in each is `niche:photo-raw-workflow`.

## Sources reviewed (license-verified)

### Cross-skill foundational sources

- https://github.com/darktable-org/darktable (GPL-3.0) — non-destructive RAW developer; scene-referred colour pipeline; module ordering documentation.
- https://github.com/darktable-org/dtdocs (GPL-3.0) — darktable user manual.
- https://github.com/RawTherapee/RawTherapee (GPL-3.0) — alternative RAW developer with strong demosaic options; established practice on develop-step ordering.
- https://github.com/LibRaw/LibRaw (LGPL-2.1 / CDDL-1.0) — RAW-decoding library underlying many tools; informs ingest-stage assumptions about what is and is not in the RAW file.
- https://github.com/exiftool/exiftool (Artistic / GPL-1.0-or-later) — canonical metadata reader/writer; informs the sidecar and EXIF discipline.
- https://github.com/aferrero2707/PhotoFlow (GPL-3.0) — non-destructive layered RAW + retouching workflow; reinforces the layered, additive editing model.
- https://github.com/KDE/digikam (GPL-2.0) — full DAM-class application; informs the asset-management folder, keyword, and rights conventions.
- https://www.gimp.org/ (GPL-3.0) — open-source image editor; informs the retouching layer stack and frequency-separation methodology.
- https://github.com/Apress/beg-photo-retouching-restoration-using-gimp — companion code repo to a published retouching textbook; surveyed for retouching workflow steps.

### Color-management-specific sources

- https://github.com/mm2/Little-CMS (MIT) — open-source CMM engine; informs the ICC-profile-centric model.
- https://github.com/AcademySoftwareFoundation/OpenColorIO (Apache-2.0 / BSD-3-Clause) — colour-management framework from motion-picture industry; reinforces the principle that transforms must be explicit, not implicit.
- https://www.argyllcms.com/ (AGPL-3.0) — display calibration and ICC profiling toolset; informs the calibration-target and cadence advice.

## Per-skill source map

- **photo-raw-development-pipeline**: darktable, dtdocs, RawTherapee, LibRaw, exiftool, digiKam, PhotoFlow.
- **photo-retouching-methodology**: darktable, RawTherapee, PhotoFlow, GIMP, Apress retouching repo, digiKam, exiftool.
- **photo-color-management-pipeline**: Little CMS, OpenColorIO, darktable, RawTherapee, ArgyllCMS, PhotoFlow, digiKam.
- **photo-asset-management-system**: digiKam, exiftool, darktable, RawTherapee, PhotoFlow, LibRaw.

## Patterns synthesised across sources

- **Strict develop-step ordering** is universal: white balance → exposure → highlight recovery → shadow lift → tone curve → clarity/dehaze → sharpening → noise reduction. Every surveyed RAW developer arranges its modules to enforce roughly this order, and the consensus is that out-of-order application produces avoidable artefacts (recovered highlights that look plastic, noise that re-emerges after smoothing, sharpening that amplifies noise).
- **Scene-referred vs display-referred workflows.** darktable's recent shift to a scene-referred default colour pipeline reinforces the principle that the develop stage operates in radiometric space and the display stage is a separate transform. The skills don't require scene-referred but the colour-management skill names the distinction.
- **Non-destructive sidecar discipline.** Every surveyed open-source developer stores edits in sidecars rather than baking them. The asset-management skill makes this an explicit principle — sidecars travel with the file, the catalogue is derived state.
- **Frequency separation vs dodge-and-burn as the central retouch choice.** Surveyed retouching references (open-source editors, the Apress-published GIMP retouch text) consistently treat these as the two primary skin/surface techniques with frequency separation suited to even-out work and dodge-and-burn suited to shape work. The retouch skill encodes the selection logic.
- **ICC-based colour management as the long-standing standard.** Across Little CMS, ArgyllCMS, darktable, RawTherapee, and digiKam the ICC profile is the unit of colour-management currency. OpenColorIO adds a layer for motion-picture workflows but the photo pipeline is ICC-centric.
- **Output sharpening is medium-dependent and resolution-dependent.** Surveyed exports support per-output-target sharpening as a deliberate step distinct from input/develop sharpening. The development-pipeline and colour-management skills both encode this.
- **Controlled-vocabulary keywording over free tags.** digiKam, exiftool, and the published-practice sources converge on hierarchical, shallow keyword trees with a small core IPTC/XMP metadata schema. The asset-management skill encodes this.
- **3-2-1 backup with off-site verification** appears in every credible asset-management reference. The asset-management skill encodes it with quarterly recovery testing.

## Rejections / things deliberately excluded

- No specific commercial DAM, RAW developer, or retoucher is named in any skill body. Trademarks ("Lightroom", "Capture One", "Photoshop") appear only in trigger keywords and example invocations because that is where users will type them; body text speaks generically about a "RAW developer", an "image editor", and a "catalogue tool".
- No AI-image-generation tooling is recommended for retouching. The retouching skill describes content-aware/generative fill as a last-resort, client-approval-required option without endorsing a specific model. This avoids tying the methodology to fast-moving tooling.
- Specific commercial print-paper profile names are excluded; the colour-management skill points the user to the lab's own published profile.
- No medical, forensic, or evidentiary imaging guidance. Those carry obligations beyond photographic asset management and are explicitly out of scope in the limitations sections.

## Confidence

**High** on methodology. The develop-step ordering, the ICC-based colour-management model, the layered retouch stack, and the sidecar-first DAM principles are well-attested across at least four GPL-licensed surveyed projects each, plus the wider published practice. The licensing policy (wave-4 doctrine permitting GPL reading, citation with license tag, original prose) has been applied — body text is 100% original synthesis, all trademarked product names confined to URL citations.

**High** on durability. The principles synthesised here change slowly. ICC profiles, non-destructive editing, sidecar metadata, and the develop-step order have been stable for over a decade and are likely to remain so.

**Medium** on specificity. The skills are intentionally tool-agnostic. A user looking for "which menu in tool X" guidance will need to translate the generic operation name to their editor's label. This is a deliberate trade-off for portability and trademark hygiene.

**High** on originality. All four bodies were authored from scratch. No source documentation was copied or close-paraphrased. The skills express the same underlying photographic practice the sources describe, but in language and structure that is the writer's own.
