# Synthesis Report — Motion Graphics, Compositing & VFX Pipeline

**Wave:** 7
**Niche:** creative — motion-graphics-vfx
**Date:** 2026-05-14
**Agent:** methodology-synthesis (wave-7)

## Skills produced

1. `motion-graphics-shot-architect.skills.md` — designing a motion-graphics shot from brief through animatic, asset prep, scene hierarchy, animation principles, easing curves, render passes, and delivery.
2. `node-based-compositing-pipeline.skills.md` — node-graph composite design with lane organization, alpha/matte discipline, color management at every node, deep vs flat compositing decision, denoising, regrain, and QC.
3. `rotoscoping-and-keying-methodology.skills.md` — clean keying and rotoscoping workflow with green-screen prep, multi-keyer core+edge strategy, edge treatment, light wrap, despill, garbage matte hierarchy, hair/motion-blur roto, and frame-to-frame conform.
4. `vfx-shot-breakdown-and-asset-handoff.skills.md` — packaging a VFX shot for handoff with plate prep, tracking and camera-match data, asset versioning, edit-locked timing, review loop, and QC.

All four are 250–400 body-line range and conform to `prompts/shared/skills-md-spec.md`.

## Sources reviewed (with license tags)

| Source URL | License | Used for |
|---|---|---|
| https://github.com/JacquesLucke/animation_nodes | GPL-3.0 | Motion-graphics node-based scripting patterns, easing recipes |
| https://github.com/3DSinghVFX/animation_nodes | GPL-3.0 | Extension patterns extending node-based motion-graphics scripting |
| https://github.com/mrachinskiy/commotion | GPL-3.0 | Motion-graphics offset/stagger automation, multi-object animation patterns |
| https://github.com/quollism/blender-keyframetools | GPL-3.0 | Keyframe easing tooling, curve-editor workflow patterns |
| https://github.com/NatronGitHub/Natron | GPL-2.0 | Node-graph compositor architecture, OpenFX-host conventions |
| https://github.com/AcademySoftwareFoundation/OpenColorIO | Apache-2.0 | Color-management transform discipline across pipeline |
| https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES | Apache-2.0 | ACES working space and view-transform convention |
| https://github.com/AcademySoftwareFoundation/openvdb | MPL-2.0 | Volumetric FX pass conventions, render-pass thinking |
| https://github.com/Psyop/Cryptomatte | BSD-3-Clause | ID-matte encoding, matte hierarchy and motion-blur preservation |
| https://github.com/cgwire/awesome-cg-vfx-pipeline | MIT | VFX pipeline structure, handoff conventions, asset versioning |
| https://github.com/hradec/pipeVFX | GPL-3.0 | Shot package structure, asset manager conventions |
| https://github.com/LumaPictures/openvdb-render | Apache-2.0 | Volume render-pass tooling reference |
| https://github.com/nikopueringer/CorridorKey | educational reference | Green-screen keying workflow heuristics |

## Methodology patterns identified across sources

Several themes recurred across nearly every source and now anchor the skills:

1. **Color management is a contract, not a tool feature.** OCIO and ACES sources converge on the principle that every read decodes once, the working space is uniform across all nodes, and the view transform is applied at the display path only — never baked into intermediate writes. This shaped the color sections of all four skills.

2. **Mattes are layered, not single-output.** Cryptomatte's deep-EXR encoding plus traditional roto practice plus key-and-fill workflows from Natron consistently show that a final alpha is the controlled combination of core, edge, garbage, and ID-derived contributions. The keying skill is built around this layering.

3. **Node graphs read like text.** Natron's and pipeVFX's conventions agree on left-to-right read order with vertical lanes for plate, mid, foreground, FX, grade, output. This shaped the node-graph organization in the compositing skill.

4. **Hierarchy is by intent.** Animation Nodes, Commotion, and motion-graphics pipeline references converge on null-parented animation rigs, beat-organized scene hierarchies, and stagger/offset patterns that produce life from milliseconds of timing difference. This is the spine of the shot-architect skill.

5. **Handoffs are versioned packages, not directories.** Pipeline sources (pipeVFX, awesome-cg-vfx-pipeline) consistently treat a handoff as an immutable, manifested package with explicit camera/tracking/asset versions. This drove the structure of the shot-breakdown-and-handoff skill.

6. **The 12 principles still apply to motion graphics.** Squash and stretch, anticipation, easing (slow-in / slow-out), follow-through, and staggered overlapping action recur across every motion-graphics reference. The animation-principles section of the shot-architect skill names them explicitly because their absence is the most common cause of "robotic" motion graphics.

## Trademark and license discipline

Per the wave-4-onward policy, trademarked product names appear only in source-citation URLs. The body of every skill uses generic terminology:

- "motion-graphics tool" rather than the trademarked motion-design product
- "node-based compositor" rather than trademarked compositors
- "procedural 3D suite" rather than the trademarked procedural tool
- "matchmove tool" rather than trademarked matchmove software
- OCIO, ACES, OpenVDB, EXR, and Cryptomatte are technology/format names (not trademarked product names) and appear in the body where they are technical terms.

GPL-2/GPL-3 sources (Natron, Animation Nodes, Commotion, blender-keyframetools, pipeVFX) were read for methodology learning only — no source code or source prose was copied or close-paraphrased. All instructional prose is original.

## Confidence

**High** on:
- Color-management discipline (ACES/OCIO are well-documented public standards).
- Matte layering and Cryptomatte usage (the technology is open and well-specified).
- Animation principles applied to motion design (broadly settled craft knowledge).
- Node-graph organization conventions (consistent across the compositors reviewed).

**Medium** on:
- Specific despill recipes and edge-treatment numeric ranges. Different shows and lighting conditions vary; the skill states ranges and reasoning rather than fixed values.
- Deep vs flat compositing trade-offs. The decision criteria stated (interpenetration, motion blur with depth of field) are widely accepted but project-specific exceptions exist.
- Handoff manifest format. Studios use varied conventions; the skill names the common pattern but acknowledges studio-specific overrides.

**Caveats:**
- The skills assume a film/TV/streaming VFX context. Real-time pipelines (game cinematics, immersive) require additional engine-specific considerations called out as limitations.
- The skills assume an artist or small team; very large multi-vendor shows require additional production-tracking systems beyond a per-shot handoff package.
- High-end stereo and immersive deliverables have additional per-eye and depth-budget rules outside the scope of these skills.

## Validation status

Pending — to be validated against `apps/api/src/skills/validator.py` at integration time. All four files follow the frontmatter schema, include required `## When to use` and `## How to apply` sections, and recommended `## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources reviewed` sections. `license_type: free` is set per wave-7 policy. Tags begin with `niche:motion-graphics-vfx`.
