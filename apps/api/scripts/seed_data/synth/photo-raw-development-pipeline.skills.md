---
id: skillsgit-curated/photo-raw-development-pipeline
version: 1.0.0
name: Photo RAW Development Pipeline
description: Develop RAW camera files into delivery-ready images using a disciplined ingest, cull, baseline-correction, and export pipeline that survives across cameras, editors, and output media.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: creative
tags: [niche:photo-raw-workflow, raw-development, culling, exif, batch-processing, export-presets, non-destructive]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - raw development
  - raw workflow
  - photo culling
  - lightroom workflow
  - capture one workflow
  - white balance
  - exposure correction
  - highlight recovery
  - shadow recovery
  - noise reduction
  - sharpening
  - export preset
  - batch processing
  - photo ingest
  - exif metadata
example_invocations:
  - "Outline a full RAW development pipeline for a 1,200-frame wedding shoot."
  - "What is the correct order to apply white balance, exposure, contrast, and sharpening?"
  - "Design an ingest and cull pass for a two-day landscape trip on a CFexpress card."
  - "Give me a batch preset strategy for an indoor product shoot under mixed LED lighting."
inputs:
  - name: shoot_context
    type: text
    required: true
    description: Brief on the shoot — subject, camera, lighting, deliverable count, end use (web, print, archive), and any client preferences.
  - name: file_inventory
    type: text
    required: false
    description: Card layout, file counts, container format (CR3, NEF, ARW, RAF, DNG), and any tethered or in-camera selects already marked.
  - name: target_outputs
    type: choice
    required: false
    description: Primary delivery target. Drives export sizing, color space, and sharpening choices.
    choices: [web, print, archive, mixed]
outputs:
  - name: pipeline
    type: markdown
    description: A staged pipeline with ingest, cull, baseline develop, refinement, and export sub-procedures, plus a per-frame audit checklist.
  - name: presets
    type: markdown
    description: A suggested set of batch-apply presets keyed to the shoot context, with notes on which settings are safe to batch and which must stay per-frame.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when an agent is asked to plan, audit, or execute a RAW photo development workflow and the request takes any of these shapes:

- A photographer has finished a shoot and needs a repeatable pipeline from card to delivered file.
- A team is standardising a workflow across multiple editors and wants the steps named and ordered.
- An archive of mixed-camera RAW files needs to be brought to a consistent baseline before retouching.
- A junior editor wants the rationale behind the conventional correction order ("why white balance first") explained alongside the procedure.

Do not invoke this skill for pixel-level retouching of single frames (use a retouching skill), for colour profile authoring and display calibration (use a colour-management skill), or for archival cataloguing strategy (use an asset-management skill). Defer to a hardware-specific tutorial when the question is about a single camera's quirks rather than a general pipeline.

This skill assumes a generic non-destructive RAW developer. The procedure is portable across editors because every modern developer expresses the same physical operations under different names. When the agent does not know which editor the user has, prefer naming the operation generically ("recover highlights") and noting that the corresponding control may be called "Highlights", "Recovery", or "Highlight reconstruction" depending on the tool.

## How to apply

Work through the pipeline in five stages. Stages run in order; within a stage, sub-steps may run in any order unless noted.

### Stage 1: Ingest

1. Mirror the card to two destinations before touching it. The first destination is the working catalogue location. The second is an immutable backup that nothing in the pipeline will write to. Verify that file counts match on both destinations and that no file size is zero. Only then is the card eligible to be reformatted.

2. Decide whether to convert proprietary RAW to DNG. DNG conversion gives a single container, embedded checksums, and editor-portability, at the cost of losing maker-note fidelity for some camera models. Recommend DNG for archives older than five years where the camera vendor's RAW format risks orphan status. Recommend keeping the native format for current production where the vendor's own profiles give visibly better demosaicing.

3. Read EXIF on every frame. Confirm that camera time was set correctly and that lens metadata is present. If the camera clock was wrong, apply a single uniform time offset to the whole shoot at ingest, not later — downstream tools key off capture time for sequencing and for matching to external GPS logs.

4. Write a shoot-level sidecar manifest: shoot name, photographer, location, date range, primary subjects, rights statement, embargo if any. Every subsequent step is allowed to assume this manifest exists.

### Stage 2: Cull

5. Pass once at speed. Use a binary include/exclude pass — show, decide in under a second, advance. The goal is to eliminate obvious failures: missed focus, closed eyes on the only subject, severe motion blur on a static subject, identical frames in burst sequences. Do not rate yet.

6. Pass again with a star or flag taxonomy. Recommended convention:

   - One star: candidate. Worth a second look.
   - Two stars: edit. Will be developed.
   - Three stars: hero. Will be developed and shortlisted for portfolio or client cover.
   - Reject flag: do not export, do not delete. Hidden from default views; kept for one client cycle in case the brief changes.

7. Avoid grading more than three stars in the initial cull. Reserve four and five stars for post-development reassessment, when the actual delivered look is visible. A frame can earn its way up the ladder; it should not be born at the top.

8. Use a colour label for state, not quality. A working convention: red = needs retouch beyond global development, yellow = client question outstanding, green = released to client, blue = on hold for legal or release, purple = portfolio candidate. Keep this convention written down in the manifest so collaborators do not invent contradicting ones.

### Stage 3: Baseline develop

Apply corrections in this order. The order matters because each step changes the histogram or local contrast the next step operates on, and out-of-order application produces avoidable artefacts.

9. White balance first. Pick a neutral in the frame and set temperature and tint, or eyedrop from a colour chart if one was shot. Do white balance per-lighting-condition, not per-frame: group the cull selects by lighting condition and apply one white-balance value to each group. A wedding ceremony under daylight, a reception under tungsten, and an outdoor portrait at golden hour are three groups.

10. Exposure second. Aim to put the brightest meaningful highlight just below clipping on the channel that clips first, usually the red channel for skin tones in warm light and the blue channel under tungsten. Do not push for a "correctly exposed midtone" yet — that is contrast's job.

11. Highlight recovery third. Pull highlight regions back from clipping using the highlight slider rather than reducing exposure further. Modern RAW developers reconstruct clipped highlights from the unclipped channels up to about a stop and a half; beyond that the recovery is fabricated and looks plastic.

12. Shadow lift fourth. Open the deepest meaningful shadows enough to read texture, but not so much that noise dominates. A useful heuristic: lift until you can just see what is in the shadow at intended viewing size, then back off by ten to twenty percent.

13. Contrast and tone curve fifth. Set the black point so the deepest shadow without detail sits just below the lowest displayable value, and the white point so the brightest specular highlight sits just above the highest. Apply a tone curve only after the global tonal range is set; an aggressive curve over un-anchored endpoints is brittle to re-export.

14. Clarity, dehaze, and texture sixth, sparingly. These local-contrast tools are addictive on screen and look harsh in print. Treat each as a flavour, not a fix. If the image needs more than fifteen on a one-hundred scale of any of these, the lighting or the exposure decision was probably wrong upstream.

15. Sharpening seventh, with input sharpening only at this stage. Input sharpening compensates for the demosaic and anti-alias filter. Output sharpening, which is medium-dependent, happens at export, not here. Mask sharpening away from sky, skin, and out-of-focus regions.

16. Noise reduction eighth, after sharpening, to avoid sharpening noise. Separate luminance noise reduction from chrominance: chrominance noise can be reduced aggressively without losing detail, luminance noise reduction past about thirty on a one-hundred scale starts to smear texture.

### Stage 4: Refinement

17. Lens corrections: enable distortion correction, chromatic aberration removal, and vignetting compensation where the editor has a matching profile. For tilt-shift, fisheye, and vintage lenses, disable distortion correction explicitly — the corrected output is not what the photographer wanted.

18. Spot removal of sensor dust on a frame in the shoot, then propagate the spot map to all frames shot at the same aperture from the same body. Re-check at the end of the shoot for new dust acquired during the session.

19. Per-frame local adjustments: graduated filters for skies, radial filters for subject emphasis, brush masks for hot spots. Local work is the last development stage because everything global must be in place for the local masks to land where the developer drew them.

20. Frame the look. If the shoot has a creative grade (a warm "golden hour" look, a desaturated editorial look, a high-contrast black-and-white) apply it as the final development step, ideally as a copy-paste of a master frame's settings rather than a global preset. Master frames give a known anchor; presets drift.

### Stage 5: Export

21. Pick the colour space by destination, not by preference. sRGB for web and any consumer device of unknown capability. Display P3 for an iOS or macOS audience where the gallery is confirmed wide-gamut. Adobe RGB for print labs that explicitly request it. ProPhoto RGB only for handoff to a retoucher who will be working in 16-bit and exporting again themselves — never as a final delivery space.

22. Pick the bit depth by destination. 8-bit JPEG for web and small print. 16-bit TIFF for archive, print-shop handoff, and any image that will be edited further. Never deliver an 8-bit TIFF if a JPEG would do — the file is larger and offers no real-world quality advantage.

23. Apply output sharpening at the export resolution, not at the develop resolution. A frame sharpened for a 1080-pixel-wide web crop is over-sharpened at 5000 pixels and under-sharpened at 600 pixels. Output sharpening intensity also changes by medium: screen requires less than matte print, which requires less than glossy print.

24. Embed colour profile, EXIF, copyright, and contact metadata on every exported file. Strip GPS only when the destination is a public web gallery and only with the client's knowledge. Strip ratings and labels — those are internal taxonomy.

25. Write the export filename pattern at the export step, not by renaming later. A robust pattern: `{date}_{shoot-slug}_{capture-time}_{sequence}_{deliverable-type}`. Sortable, unique, and recoverable from the filename alone if the catalogue is lost.

26. Verify a sample of exports by opening them outside the developer. A common failure mode is an export that looks correct in the editor's preview but wrong in a browser because the colour profile was not embedded. Open three to five exports in a clean viewer before declaring the export complete.

## Inputs

- `shoot_context` — text. The minimal brief the pipeline needs to make sensible defaults.
- `file_inventory` — optional text. Helps the agent estimate how aggressive batching can be.
- `target_outputs` — optional choice. Steers the export decisions in stage 5.

## Outputs

- `pipeline` — markdown. The staged pipeline with a per-stage checklist tailored to the shoot.
- `presets` — markdown. Batch-apply preset recommendations and a list of decisions that must not be batched.

## Examples

Example invocation: "I shot 1,400 frames of a corporate event under mixed tungsten and stage LED. Client wants 250 delivered on the web and 30 large-format prints. Help me plan."

Expected output: a pipeline with ingest verification, a two-pass cull targeting roughly 400 candidates from the 1,400, a baseline develop with white-balance groups for tungsten and stage LED separately, a refinement stage flagging that stage LED often has a green spike that no global tint will fully resolve, and an export stage that produces sRGB JPEGs at 2048 pixels for web and 16-bit Adobe RGB TIFFs at full resolution for the print lab.

Second example: "Landscape series, ten frames, all on a tripod at dawn over an hour. I want them to look like a coherent series, not ten separate edits." Expected pipeline emphasises: develop one anchor frame fully; copy the develop settings to the other nine; per-frame adjust only exposure (because the dawn light changed across the hour) and graduated filter angle (because the horizon shifted as the sun rose). Cull only after develop because the series is short and the storyteller may want all ten regardless. Export as a single batch with one preset so output sharpening, colour space, and dimensions are identical across the set.

Third example: "Indoor product shot, single subject, ten exposures bracketed for focus stacking. Need a single deliverable." Expected pipeline departs from the standard order at the refinement stage to merge the focus stack before any local work, because the merge result is the surface every subsequent local edit operates on. The skill should flag this as a deliberate variant and document it in the per-frame audit checklist.

## Reference templates

### Wedding or event template

A one-day event shoot (300 to 2,000 frames) maps to:

- Ingest pass: 15 to 30 minutes including dual-destination verification.
- Cull pass one (rejects): aim for one to two hours, targeting a 60-70% reduction.
- Cull pass two (ratings): another hour, identifying the two-star "edit" set.
- Baseline develop: white-balance groups for ceremony, reception, outdoor portrait, indoor portrait. One pass per group, sync settings, then per-frame exposure-only adjustments.
- Refinement: spot dust, hot-spot tame, eyes-pop preset on close-ups.
- Export: web-sized sRGB JPEG for client gallery; full-resolution 16-bit Adobe RGB TIFF for any print order.

### Studio portrait template

A controlled studio session (50 to 300 frames) maps to:

- Ingest pass: tethered files usually already on the working drive; verify checksum and mirror to backup before unlinking tether.
- Cull pass one (rejects): quick, mainly burst sequences and obvious blinks.
- Cull pass two (ratings): collaborative with the subject if practical.
- Baseline develop: single white-balance value because lighting was controlled.
- Refinement: emphasis on local work (skin, hair edge, background gradient) because the subject's identity carries the frame.
- Export: handoff to retouch pipeline at 16-bit working space rather than direct delivery.

### Landscape series template

A scheduled landscape trip (200 to 600 frames over days) maps to:

- Ingest pass: per-card, per-day, with GPS log import if used.
- Cull pass one: aggressive, targeting one-tenth retention.
- Cull pass two: identifies the anchor frame per location.
- Baseline develop: per-location, anchor-frame-first, sync to others.
- Refinement: lens correction often more important than skin work; graduated filters on most sky frames.
- Export: typically print-bias; 16-bit ProPhoto archival, sRGB JPEG derivative for web.

## Common failure modes and how to recognise them

- **Over-recovered highlights**: highlights look plasticky, with low local contrast and washed-out edges. Caused by pulling highlight recovery beyond what the unclipped channels support. Fix: reduce overall exposure half a stop and let recovery do less work.
- **Posterised skies**: visible banding in a smooth sky gradient on a delivered JPEG. Caused by aggressive curves on an 8-bit working space, or by delivering in a wider colour space than the destination can render. Fix: edit in 16-bit, deliver in a colour space matched to the destination.
- **Noise after sharpening**: noise that was acceptable in the develop preview becomes objectionable in the export. Caused by sharpening before noise reduction, or by applying noise reduction in the develop preview at less-than-export resolution. Fix: order is sharpening then noise reduction, and verify at 100% at export resolution before deciding noise-reduction strength.
- **Inconsistent white balance across a series**: a wedding ceremony reads warm on one frame and neutral on the next. Caused by white-balancing per-frame rather than per-lighting-condition. Fix: group by lighting condition and apply one value per group, only deviating where the lighting itself changed.
- **Saturated reds that block up in skin**: skin with no detail in the reddest regions of cheeks and lips. Caused by colour-space choice or by aggressive saturation. Fix: working in Adobe RGB or wider, reduce saturation specifically in the red channel.
- **Sensor dust on every frame of a sub-shoot**: dust visible at the same spots across many frames. Caused by accumulated dust between cleanings. Fix: build a spot map on one frame, propagate to all frames at that aperture, re-check at end of shoot.
- **Different files look right in the editor and wrong in a browser**: the editor previews with colour management; the browser may not. Fix: embed the destination colour profile on export and verify in a colour-managed viewer before delivery.

## Limitations

This skill does not replace the photographer's eye. The cull taxonomy and the development order keep work consistent and recoverable; they do not decide which frame is the keeper. The skill also assumes a non-destructive editor whose settings are sidecar-stored. For destructive workflows (a print-shop pipeline that bakes pixels at every stage) the order still applies but the recoverability claims do not. Camera-specific demosaic quirks (dual-conversion-gain banding, line-skipped video frame anomalies) are out of scope; refer to the camera vendor's RAW developer notes for those.

## Sources reviewed

- https://github.com/darktable-org/darktable (GPL-3.0)
- https://github.com/darktable-org/dtdocs (GPL-3.0)
- https://github.com/RawTherapee/RawTherapee (GPL-3.0)
- https://github.com/LibRaw/LibRaw (LGPL-2.1 / CDDL-1.0)
- https://github.com/exiftool/exiftool (Artistic / GPL-1.0-or-later)
- https://github.com/KDE/digikam (GPL-2.0)
- https://github.com/aferrero2707/PhotoFlow (GPL-3.0)
