# Synthesis Report — Color Grading & Color Science

**Wave:** 7
**Niche:** creative — color grading & color science
**Date:** 2026-05-14
**Agent:** wave-7 methodology-synthesis (color)

## Skills produced

1. `color-pipeline-architect.skills.md` — pipeline design from camera log to delivery, working space choice, IDT/RRT/ODT vs custom transforms, SDR vs HDR mastering, deliverables matrix across Rec.709, P3-D65, Rec.2020 PQ/HLG, DCI-P3 theatrical.
2. `color-grading-shot-methodology.skills.md` — per-shot grading discipline, ordered primary correction (exposure → contrast → white balance → saturation), secondaries (qualifiers, power windows), node tree structure, scope-driven shot-to-shot matching.
3. `lut-and-cdl-management.skills.md` — LUT categorization across the production (on-set, dailies, editorial viewer, VFX viewer, delivery), ASC CDL slope-offset-power roundtrip through editorial and VFX, bake-vs-preserve decisions per artifact, scope-based QC.
4. `hdr-deliverable-prep.skills.md` — HDR deliverable end-to-end: PQ vs HLG, MaxCLL/MaxFALL measurement on the encoded master, mastering display metadata, SDR trim from an HDR master, dynamic-metadata authoring for HDR10+ and proprietary dynamic-metadata pipelines.

All four files conform to `prompts/shared/skills-md-spec.md`. Frontmatter sets `license_type: free`, `category: creative`, first tag `niche:color-grading`. Bodies include required `## When to use` and `## How to apply` plus recommended `## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources reviewed`. Each body lands in the 250-400 line band.

## Sources reviewed (with license tags)

Permissive (preferred per wave-4 policy):

- https://github.com/AcademySoftwareFoundation/OpenColorIO — BSD-3-Clause
- https://github.com/aces-aswf/aces — Modified BSD 3-Clause
- https://github.com/aces-aswf/CTL — Modified BSD 3-Clause
- https://github.com/aces-aswf/aces-input-and-colorspaces — Modified BSD 3-Clause
- https://github.com/colour-science/colour — BSD-3-Clause
- https://github.com/colour-science/OpenColorIO-Configs — BSD-3-Clause
- https://github.com/colour-science/colour-hdri — BSD-3-Clause
- https://github.com/colour-science/awesome-colour — BSD-3-Clause
- https://github.com/shidarin/cdl_convert — MIT
- https://github.com/EaryChow/AgX — MIT
- https://github.com/AcademySoftwareFoundation/OpenTimelineIO — Apache-2.0

Read for methodology (license unclear or proprietary; cited URL-only with explicit tag, no content copied):

- https://github.com/sobotka/filmic-blender — license unclear (no LICENSE file detected); read for view-transform methodology only
- https://github.com/walter-arrighetti/edl2cdl — license check before redistribution; informed CDL roundtrip discussion only
- https://github.com/HDRWCG/HDRStaticMetadata — license check before redistribution; informed MaxCLL/MaxFALL measurement methodology only
- https://github.com/jessielw/HDR-Multi-Tool — license check before redistribution; informed dynamic-metadata verification methodology only
- https://en.wikipedia.org/wiki/ASC_CDL — CC BY-SA 4.0; read for slope/offset/power semantics
- https://professionalsupport.dolby.com/s/article/Calculation-of-MaxFALL-and-MaxCLL-metadata — proprietary documentation; cited URL-only as a measurement-methodology reference
- https://www.movielabs.com/md/practices/color/ManifestPractices_HDR_v1.0.pdf — industry consortium practice document; cited URL-only as a delivery-practice reference

Total: 10 source URLs in the permissive set plus 7 reference URLs across the four `## Sources reviewed` sections. WebSearch+WebFetch call count: 9 (well under the 15 cap).

## Trademark discipline

Per wave-4 policy, body content uses generic terminology only:

- "Color grading suite" instead of any specific application name.
- "Primary correction node" instead of vendor-specific node names.
- "Reference rendering transform plus output device transform stack" instead of branded color-management names.
- "Dynamic-metadata variant" and "proprietary dynamic-metadata pipeline" instead of brand names for the dominant licensed HDR format.
- "Working space favored by colorists" instead of a vendor-branded log-working-space name.

Branded product names appear only in source-citation URLs.

## Methodology patterns identified

Common across the surveyed sources:

1. **Scene-referred is the default for any non-trivial pipeline.** Every modern reference framework treats display-referred grading as a special case for legacy SDR-only work; multi-deliverable and multi-camera pipelines are scene-linear at their core.
2. **Order of operations in primary correction is sequential by dependency.** Exposure → contrast → white balance → saturation is consistent across sources because each step changes what the next step is operating on.
3. **The view transform is structural, not creative.** A creative "look" is layered on top of a structural view transform that handles dynamic-range compression and gamut mapping. Conflating the two produces non-portable grades.
4. **Scopes are the only reliable arbiter when displays diverge.** Every source emphasizes scope reading over monitor reading for color decisions that have to roundtrip across rooms.
5. **CDLs are sidecars, never bakes.** ASC CDL roundtrip discipline is consistently the source of dailies-to-grading mismatch when it fails; sources converge on a single-authority pattern.
6. **HDR static metadata is measured, not estimated.** MaxCLL and MaxFALL are computed from the final master post-encode, with linearization required before the arithmetic.
7. **SDR trim is a colorist pass, not an automatic conversion** for premium content; automatic tone-mapping is a budget-constrained fallback with QC review.

## Confidence

- **High confidence** in the methodology presented for color-pipeline-architect, color-grading-shot-methodology, and lut-and-cdl-management. These domains have well-established practices across permissive open-source references and the synthesis aligns with the consistent pattern across those sources.
- **Medium-high confidence** in hdr-deliverable-prep. The static metadata measurement, PQ/HLG choice, and SDR-trim discipline are well-documented. The dynamic-metadata authoring discussion is deliberately generic because the dominant proprietary format is licensor-controlled — the skill describes the workflow shape correctly but does not enumerate licensor-specific certification details, which is appropriate for a generic methodology skill.
- **No medical/regulatory/safety stakes** in this niche, so no mandatory disclaimers were added. The limitations sections name pipeline-stage risks (uncalibrated displays, format conversion edge cases, streaming spec drift) without raising health-or-safety flags.

## Validator readiness

All four files use the canonical frontmatter shape from the spec, with the same key ordering and types as the reference example (`apps/api/tests/fixtures/skills/dcf-valuation.skills.md`) as observed via the sibling `ai-ux-pattern-picker.skills.md` already passing in this folder. Each file has unique `id`, `1.0.0` version, dated changelog, required-models populated, `license_type: free`, inputs and outputs declared. Bodies have the required sections. No secrets, no script tags, no non-HTTPS links, no pricing claims in body that contradict the frontmatter.
