---
id: skillsgit-curated/rotoscoping-and-keying-methodology
version: 1.0.0
name: Rotoscoping and Keying Methodology
description: Clean keying and rotoscoping workflow — green-screen prep, multi-keyer extraction, edge treatment, light wrap, despill, garbage matte hierarchy, roto for hair and motion blur, conform across frames.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: creative
tags: [niche:motion-graphics-vfx, rotoscoping, chroma-key, greenscreen, despill, edge-treatment, matte-discipline]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: []
  min_context_tokens: 16000
  estimated_tokens_per_invocation: 4500
trigger_keywords:
  - rotoscoping
  - roto
  - chroma key
  - greenscreen
  - bluescreen
  - despill
  - matte
  - light wrap
  - edge treatment
  - garbage matte
  - hair roto
  - motion blur matte
example_invocations:
  - "Plan the keying and roto pipeline for an actor in a green-screen plate with hair detail and motion-blurred arms."
  - "How do I combine two keyers to get clean core and edges without halos?"
  - "Build a roto hierarchy for a hand holding a glass with refraction visible through it."
  - "Set up despill and light wrap for an actor in front of a green screen who will land on a sunset background."
inputs:
  - name: plate_description
    type: text
    required: true
    description: A description of the plate — keying type (green or blue or none), subject content, problem areas (hair, motion blur, transparency, spill, lighting issues), and intended background.
  - name: keying_difficulty
    type: choice
    required: false
    description: Difficulty tier for the plate.
    choices: [clean-screen-flat-lit, screen-with-spill, uneven-screen-lighting, motion-blurred-edges, fine-detail-hair-fur, semi-transparent-elements, no-screen-pure-roto]
  - name: delivery_resolution
    type: choice
    required: false
    description: Final delivery resolution affects how aggressively edges can be tuned.
    choices: [hd-1080, uhd-4k, theatrical-2k, theatrical-4k, social-vertical]
  - name: working_color_space
    type: choice
    required: false
    description: Working color space of the pipeline.
    choices: [ACEScg, scene-linear-rec709, log-rec709, raw]
outputs:
  - name: prep_plan
    type: markdown
    description: Plate-prep steps before any keyer or roto tool touches the image.
  - name: keying_strategy
    type: markdown
    description: The keyer combination (core and edge), the order of operations, and the despill plan.
  - name: roto_plan
    type: markdown
    description: Roto shape hierarchy with assigned coverage areas, frame-by-frame conform strategy, and motion-blur or hair sub-mattes.
  - name: edge_and_integration
    type: markdown
    description: Edge-treatment recipe (erode, feather, light wrap, color-correct edge), with parameters that respect the destination background.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when a compositor or generalist must extract a foreground from a plate cleanly, either through chroma keying, rotoscoping, or a combination. Typical situations:

- A green- or blue-screen plate has arrived and the matte must support a final composite with fine detail (hair, fabric, motion blur, transparent elements).
- A plate has no screen and the subject must be cut out manually frame by frame.
- An existing key has visible halos, edge fringe, spill, or chattering edges and a structured cleanup is needed.
- A hand-held shot requires per-frame matte conforming because automatic trackers fail on the subject.

Do not invoke this skill for graphics overlays on a clean plate where no extraction is needed (use the node-based compositing skill instead). Do not invoke it for purely 3D matte extraction where Cryptomatte or per-object render passes give a clean alpha for free. Do not use it as a stand-in for on-set fix; some plate problems (poor lighting, undersized screen, motion-blurred limbs touching the edge of the screen) cannot be fixed in post and the right answer is a reshoot.

## How to apply

The methodology treats matte extraction as a layered system: core (the body of the subject), edge (the few-pixel band where the keyer is least reliable), and corrections (despill, light wrap, edge color match). Each layer has its own treatment and the final alpha is a controlled combination, not a single keyer's output.

### Phase overview

- Phase 1 analyzes the plate to identify problem areas before any extraction.
- Phase 2 prepares the plate (screen clean, denoise, pre-key correction).
- Phase 3 builds a garbage-matte hierarchy that limits where keyers look.
- Phase 4 runs the core+edge keyer strategy that produces the foundation matte.
- Phase 5 fills with roto every region the keyer cannot reach.
- Phase 6 treats edges with erode, feather, light wrap, and color correction.
- Phase 7 despills the foreground to remove screen color from the subject.
- Phase 8 verifies frame-to-frame consistency, particularly motion blur and hair.
- Phase 9 packages the matte streams and documents the recipe for handoff.
- Phase 10 self-checks the plan before declaring it complete.

The single most important pattern across the phases: a final matte is the combination of multiple independent contributions (core, edge, garbage, roto, ID-derived), each tuned to a specific role. A single-keyer-output matte is brittle and should be flagged in the plan.

### 1. Analyze the plate before touching it

1. **Watch the plate end to end, twice.** Identify the toughest frames before tuning the easiest ones. Tuning to a hero frame and discovering later that the toughest frame breaks the recipe is a common rework path.
2. **Identify the keying mode.** Greenscreen, bluescreen, partial screen, or no screen at all (pure roto). A plate with sky might be approached as a key against sky color even though it was not staged as a screen.
3. **Catalog problem areas.** List by frame range: spill on skin and hair, screen shadows or hot spots, motion-blurred limbs, semi-transparent props (glass, smoke, hair), edges that cross from clean screen onto cluttered set, contact shadows the comp may need to preserve.
4. **Note the screen color and uniformity.** Sample the screen in five regions; if luminance varies more than roughly 15% or hue drifts noticeably, the keyer will struggle and a screen-clean pass is required.
5. **Note the destination background.** A subject going onto a bright sky needs a different edge color than the same subject going into a dim interior; light wrap and edge color must be planned for the final background.
6. **Confirm the working color space.** Keying in a log encoding is generally less reliable than keying in a linear encoding, but some keyers expect a specific encoding. Choose deliberately and document.

### 2. Plate preparation before keying

7. **Stabilize only if necessary.** A locked-off plate is easier to key; if the camera moves, stabilization can simplify roto but introduces interpolation softness. Stabilize only when the time saved exceeds the softness cost, and de-stabilize at output.
8. **Screen clean pass.** Patch screen shadows, garbage, and lighting unevenness with a "clean plate" composed from regions of clean screen. The keyer should see a uniform color where the screen is meant to be.
9. **Degrain or denoise temporarily.** A noisy plate gives a noisy matte. Denoise the plate before the keyer; reintroduce grain on the integrated comp at the end so the foreground does not look smoothed against the new background.
10. **Color-correct the plate to where the keyer is happiest.** Some keyers prefer a slight lift of the screen color (a small saturation boost in the screen hue band). This is a pre-key correction, not the show grade; apply it on a branch and discard it after the matte is extracted.
11. **Mask out non-keyable regions.** Anywhere the keyer should never look (off-screen apple-box, lighting stand, microphone) gets a generous garbage matte before the keyer runs.

### 3. Garbage matte hierarchy

12. **Build garbage mattes coarse to fine.** Start with a large outer shape that excludes everything outside the subject's working area. Add inner shapes for stand-mounted gear, set walls, and crew encroachment.
13. **Use animated garbage mattes for moving non-subject objects.** A boom mic dipping in from the top requires a per-frame moving shape, not a static one.
14. **Separate "always foreground" from "always background" garbage.** A hold-in matte forces a region to be opaque regardless of the key; a hold-out matte forces a region to be transparent. Both have their place; never collapse them into a single track.
15. **Cap garbage matte count.** A plate with more than roughly fifteen garbage shapes is a sign that the screen lighting failed; revisit the screen-clean step.

### 4. Keyer strategy: core plus edge

16. **Use a strong keyer for the core.** A core matte covers the body of the subject with no concern for edges; over-key it so the core is fully opaque even at the cost of edge artifacts.
17. **Use a gentle keyer for the edges.** An edge matte preserves hair, motion blur, and translucency; under-key it so edges retain detail even at the cost of some screen leakage that the core handles.
18. **Combine core and edge mattes with a controlled merge.** The final alpha is the core matte expanded slightly, masked into the edge matte's edge region. The combination is the deliverable matte; neither keyer alone is.
19. **Run keyers in scene-linear or in the encoding the keyer specifies.** Some keyers operate best in YUV-like spaces, some in chrominance-difference math, some in 3D color volumes. Read the keyer's spec; do not run a keyer in an encoding it was not tuned for.
20. **Use multiple keyer types per shot when one is insufficient.** A chrominance keyer for the core, a difference keyer against a clean plate for the edge, a luma keyer for a specific highlight region. The mattes combine; the keyers do not replace one another.
21. **Tune keyers on a hero frame, then verify on the toughest frame.** A keyer that breaks on the toughest frame fails the shot; revise the recipe.

### 5. Roto for what the keyer cannot reach

22. **Roto begins where the keyer ends.** Edges with similar luminance to the screen (dark hair against green), holdouts that the screen color does not cover, and frames where the subject leaves the screen frame all require roto.
23. **Build the roto shape hierarchy by anatomy.** Major shapes for torso, head, arms, legs as separate tracks; each with its own animation. Small overlapping shapes for fingers, hair clumps, fabric edges. Never roto an entire subject as a single shape; future fixes are impossible.
24. **Set roto keyframes at action extremes.** Keyframe the shape at the start, end, and at every direction change. Let the spline interpolate between; do not key every frame unless the motion requires it.
25. **Use motion-tracker data to drive roto.** If a planar or point tracker can solve the subject's motion, parent the roto shape's transform to the tracker. The roto then becomes a per-frame shape tweak rather than a per-frame redrawing.
26. **Hair and fur belong to the matte, not the roto.** Do not roto every hair strand. Let the edge keyer recover hair; for shots where the keyer cannot, use a roto envelope that includes the hair region with a soft inside falloff, and let the keyer fill detail inside the envelope.
27. **Roto motion-blurred edges with motion-aware feather.** A blurred arm sweeping across the frame needs a wider feather on the leading and trailing edge than on the rest of the limb. Some tools support per-vertex feather animation; if not, use a separate motion-blur sub-shape with a wider feather.
28. **Roto semi-transparent objects with a density treatment.** A glass, a hair veil, a smoke wisp has alpha less than 1 throughout. Roto the shape, then multiply the matte by a density less than 1 and tune; sometimes a luminance-driven density gives the right gradation.
29. **Conform roto across frames in pairs.** Compare frame N to frame N+1 and frame N-1. A roto that conforms only to a single hero frame chatters. Adjust handles for smooth motion between adjacent frames before tuning shape on a hero frame.

### 6. Edge treatment

30. **Erode the matte by a fractional pixel.** Default matte edges sit a hair outside the subject and pull in screen color. A sub-pixel erode (0.3 to 0.8 pixels) pulls the edge in without losing detail.
31. **Feather to taste.** A flat edge looks digital; a slight feather softens it. Tune feather per region — a sharp prop edge can be sharper than a hair edge.
32. **Choke separately from erode.** Choke (a parameterized contraction of the alpha) is distinct from erode (a morphological operation) and behaves differently on soft edges. Use the right tool for the edge type.
33. **Color-correct the edge band.** Pull a thin edge band from the matte and color-grade it toward the destination background's color. A subject going onto a warm sunset background gets a slight warmth in the edge band; the same subject going into a cool interior gets a slight cool tint.
34. **Apply light wrap inside the edge.** A light wrap takes background luminance, blurs it, and adds it inside the matte's edge with a controlled width. Width depends on the perceived softness of the destination lighting; over-wrapped edges read as a halo.

### 7. Despill

35. **Identify spill regions.** Spill is screen color reflected onto the subject's skin, hair, white fabric, and any reflective surface. It often appears strongest on the side of the subject facing the screen.
36. **Despill in stages.** A first pass clamps the screen channel where it exceeds a neutral relationship to the other channels (the canonical "green minus the max of red and blue"). A second pass replaces the despilled region's color with a target color sampled from the destination background or from an unaffected region of the subject.
37. **Avoid over-despill.** Pushing the despill too far turns the subject magenta on a greenscreen or yellow on a bluescreen. Tune until the spill is gone, then back off by a quarter.
38. **Treat hair despill separately.** Hair is the most spill-prone region and the most sensitive to over-despill (which turns hair magenta or purple). Use a hair-specific matte (luminance or roto envelope) and a gentler despill within it.
39. **Re-light spill regions where the destination demands.** If the original spill was strong and the destination background is dark, the despilled region may need a darken to match the destination lighting; if the destination is bright, the despilled region may need a slight grade up.

### 8. Frame-to-frame consistency

40. **Spot-check edges at every keyframe in the shot.** A matte that holds on frame 1 and frame 60 may chatter on frame 30. View at 100% on motion-heavy frames.
41. **Watch the alpha channel at full speed.** Many edge defects (chatter, flicker, breathing) are invisible when stepping frame by frame but obvious at full speed.
42. **Confirm motion blur reads correctly.** A motion-blurred limb against the new background should preserve the plate's blur characteristic; if your matte erased the blur edge, integrate a motion-blur recovery step using motion-vector data or a per-frame envelope.
43. **Compare against the destination, not against black.** Some matte defects show only against the destination background. Final QC is on the composite, not on the matte alone.
44. **Diff with a previous version when iterating.** A small change in one parameter can ripple unexpectedly. A diff between versions catches regressions.

### 9. Hand-off and documentation

45. **Save the matte streams separately.** Core matte, edge matte, garbage matte, roto matte, and despilled foreground are each useful to the next compositor or to a future fix. Save them; the disk space is small relative to the rework cost.
46. **Document the keyer recipe.** Which keyers, in which order, with which parameters, on which color space. The next artist or you in three months should be able to re-derive the matte from the document alone.
47. **Document the roto convention.** Shape names, layer order, and the meaning of each track (anatomy region, hold-in, hold-out).
48. **Render the matte at full bit depth.** A 16-bit half-float or higher matte preserves edge gradation that 8-bit clips. Final delivery may downconvert; the working matte stays high precision.

### 10. Self-check before responding

49. **Did you separate core and edge?** A single-keyer plan is brittle and should be flagged.
50. **Is despill in the plan, not assumed?** A composite without explicit despill bleeds screen color.
51. **Did you account for the destination background?** Edge color and light wrap depend on what the subject lands on.
52. **Did you call out motion blur and hair?** These are the two failure modes that ship; surface them or accept the risk.
53. **Is the QC against the final composite, not against black?** Recommend QC on the composite background.

## Special cases

Some plate situations have known solutions worth surfacing in the plan up front so they are not rediscovered mid-shot.

### Hair against a similar-luminance background

When dark hair sits against the green screen and the chrominance keyer cannot separate them, build a luminance-driven hair recovery matte. The recovery matte is a luminance keyer running on a desaturated copy of the plate, restricted by a roto envelope to the hair region only. The recovery matte combines with the chrominance edge matte to give hair detail without screen leakage.

### Motion-blurred limbs

A limb sweeping across the screen produces motion blur that the keyer renders as a soft, partially screen-colored band at the leading and trailing edges. Treat the motion-blurred edge with a wider feather, a slight color tint pulled from the limb's clean-edge region, and a motion-vector-aware densify. If a motion-vector AOV exists from the plate (uncommon for live action but possible for rotoanimate or stabilized plates), use it; if not, hand-feather the blurred edge by frame.

### Semi-transparent fabric, glass, smoke

Semi-transparent elements should resolve to an alpha less than 1 across their entire visible region. A binary roto on a glass produces an opaque silhouette that breaks the comp. Instead, roto the shape, then drive its density from luminance or from a hand-painted density map. For smoke and atmosphere, prefer a density-driven matte over a hard roto in every case.

### Eyes and glints

Eye whites and specular glints on skin or hair sit near the brightest screen highlights and can be eaten by an aggressive luminance keyer. Protect them with a small hold-in roto envelope before the keyer runs.

### Reflections and refractions in props

A glass or shiny prop carries reflections of the screen and refractions through the glass body. The reflection of the screen on the glass must be replaced (or recolored) with the destination background's content during integration; the refraction through the glass must allow some of the destination background to pass through. This is more an integration problem than a keying problem, but the matte must preserve the alpha gradation through the glass so the integration step has the data it needs.

### Crowds and dense detail

A crowd against a screen is many small mattes rather than one big one. Plan for screen replacement only at hero distance; further back, the audience reads the crowd as silhouettes and a single envelope matte for the whole crowd suffices.

## Working color space for keying

Different keyers behave differently in different color spaces. Use the following guidance:

- **Chrominance-difference keyers operate best in a slightly desaturated linear space.** Saturation pre-boost on the screen, then key in scene-linear, then turn the pre-boost back off after extraction.
- **Hue-based keyers operate best on a hue-rotated representation.** Most modern keyers handle the rotation internally; trust the keyer's documentation.
- **Luminance keyers operate in the same space they are tuned in.** Do not switch luminance keying between log and linear without retuning.
- **Difference keyers (against a clean plate) operate in any space, provided the plate and clean plate are in the same space.**
- **Keep keying separate from integration grade.** A graded plate keys differently from the original; key on the original, integrate on the graded copy.

## Anti-patterns to surface in the plan

- **A single keyer producing the final matte.** Mattes are layered; surface and fix.
- **Roto on every frame instead of keyframes-and-interpolation.** Per-frame redrawing is a sign of an unbroken shape; subdivide.
- **A single-shape roto for the whole subject.** Future fixes are impossible; subdivide by anatomy.
- **No despill.** Spill is almost always present on a screen plate; the absence of despill produces green halos on the foreground.
- **A light wrap with no width or color tuning.** A default light wrap produces a halo, not integration.
- **A matte rendered at 8-bit.** Edge gradation requires 16-bit half-float; 8-bit clips edge values to integer steps.
- **A despill that pushes the hair magenta.** Over-despill is as visible as no despill; back off until the shift disappears.

## Inputs

- A description of the plate — keying type, subject, problem areas, destination background.
- Optional: difficulty tier, delivery resolution, working color space.

## Outputs

- A prep plan for the plate.
- A keyer strategy combining core and edge with despill.
- A roto plan with shape hierarchy and conform strategy.
- An edge and integration recipe matched to the destination background.

## Examples

**Example invocation**

> "Greenscreen plate of an actress turning her head, mid-length hair, soft studio lighting. Some spill visible on the right shoulder. She is being placed onto a warm sunset window background."

**Expected high-level output**

Plate prep: screen-clean pass replaces a hot spot on camera-left of the screen using a synthesized clean region. Denoise applied to a copy used for keying; original plate retained for regrain. Pre-key correction adds a small saturation boost to the green band to help the keyer; correction discarded after the matte is extracted.

Garbage mattes: large outer matte excludes the floor mark on the bottom of the frame and a lighting flag visible top-right. One animated garbage matte follows the boom shadow that briefly dips in on frames 18–24.

Keying strategy: chrominance keyer for the core, tuned aggressive so the body fills cleanly even where the screen lighting falls off; difference keyer using the screen-clean plate for the edge, tuned gentle so hair retains detail. Core matte is eroded by 1 pixel and merged into the edge matte's hair region. Both keyers run in scene-linear ACEScg.

Roto plan: large body shape parented to a planar tracker on the actress's torso, animated by exception on direction changes. Hair envelope as a single soft-feathered shape — does not roto strands; lets the edge keyer fill detail inside the envelope. Hands and shoulders as separate sub-shapes with their own keyframes.

Edge treatment: erode 0.5 pixel, feather 1.5 pixels generally, 2.5 pixels in the hair region. Light wrap pulls warm sunset luminance into the edge with a 2-pixel width on the right side of the face (camera left of frame, screen-side of the actress) and a 1-pixel width on the off-screen side.

Despill: channel-clamp greenscreen despill on the body, gentler despill in a hair-specific envelope (luminance plus roto), no despill in the eye region (the keyer did not introduce spill there). Slight warm color injection on the shoulder spill region to match the sunset's warm backlight.

Frame-to-frame: spot-check edges on frames 10, 24, 35, 48 where head turn motion-blurs the hair edge; confirm the hair envelope follows. Render alpha as 16-bit half-float EXR alongside the despilled foreground.

## Second example

**Example invocation**

> "No-screen plate: a moving shot of a busy street where we must replace a single moving vehicle. Hand-held camera with handheld motion. Working at scene-linear ACEScg, delivery at UHD-4K."

**Expected high-level output**

Plate prep: no screen, so no screen-clean step. Denoise a copy for roto reference; original kept for regrain. Stabilize the plate on the vehicle to ease roto, but de-stabilize at output so the comp lives in the original camera motion.

Garbage mattes: large outer matte excluding the upper third of the frame (sky), confining work to the lower two-thirds where the vehicle lives.

Keying strategy: no keyer; this is pure roto. A 2D planar tracker pinned to the vehicle's side panel feeds the roto's transform; the roto shape itself moves only when the vehicle's silhouette changes.

Roto plan: vehicle body as one shape; wheels as four sub-shapes (each with independent rotation track); mirrors and antenna as three small sub-shapes; window glass interior as a density-driven sub-shape so the comp can see partway through the windows. Keyframes at start, end, and at every direction change of the vehicle (turning a corner, decelerating). Between keyframes, the planar tracker carries the motion.

Edge treatment: erode 0.3 pixels, feather 1.0 pixel on body edges, 2.0 pixels on the windows. No light wrap unless the destination background is significantly different from the plate background.

Despill: not applicable for a no-screen plate.

Frame-to-frame: spot-check at every keyframe plus every 10th in-between. Watch the alpha at full speed for chatter; the planar-tracker-driven roto should hold motion-blur edges that hand keyframing would chatter on.

## Tools and tracker integration

A roto-and-keying workflow benefits from the following supporting tools, named generically in the plan and instantiated by the artist:

- **2D planar tracker.** Solves a flat surface's motion across the plate; feeds roto transform tracks.
- **Point tracker.** Solves a feature's 2D motion; useful for small details and as anchors for planar trackers.
- **3D camera solver.** When a 3D-aware operation is needed, the camera solver produces a 3D camera for the plate; roto and matte mattes can be projected into 3D space.
- **Optical-flow analysis.** Produces forward and backward motion vectors that the matte can use for motion-aware feathering.
- **Planar-tracker-driven roto tool.** A specialized roto tool that uses planar tracking to carry shapes between keyframes; cuts roto effort dramatically for plates with mostly flat motion.
- **Machine-learning matte extraction.** Modern AI matters can produce a first-pass alpha that traditional roto refines. Treat AI mattes as the equivalent of a keyer output — one contribution to the layered final matte, never the final matte alone.

The plan should name which tools the artist will use and why; do not assume.

## Quality bar by deliverable resolution

The acceptable tolerance for edge defects scales with deliverable resolution:

- **HD-1080 web.** Edges chatter by up to half a pixel without visible defects; soft feather hides most edge color mismatch.
- **Theatrical 2K.** Edges chatter by up to a quarter pixel; edge color must match within a small chromatic tolerance.
- **UHD-4K and theatrical 4K.** Edges chatter by up to one-eighth of a pixel; edge color must match within a tight chromatic tolerance; hair detail must survive the resolution.
- **Cinema 4K.** Same as UHD-4K but with a larger viewing audience; defects amplify in social proof.

The plan should note the resolution and adjust feather, erode, and tolerance accordingly. A recipe that works at HD often fails at 4K and almost always fails at cinema.

## Limitations

- This skill plans a keying and roto workflow; it does not draw shapes or set keyer parameters with specific numeric values for a specific plate.
- It does not perform optical-flow or AI-assisted roto, which require their own tooling and review pass; the methodology accommodates them as one keyer or one roto track among many.
- It cannot substitute for an on-set fix. Plates with under-exposed screens, motion blur that exceeds the screen extent, or fundamentally similar foreground and screen luminance may not yield a usable matte regardless of post effort.
- It does not handle stereo or VR roto, which requires per-eye disparity and additional conform passes.
- For shots with extensive crowd or background plate replacement at scale, an automated matting pipeline is more appropriate than the per-shot recipe described here.

## Sources reviewed

The methodology synthesized here draws on patterns observed across the following open-source repositories and reference projects. None of the prose above is derived from any single source. Trademarked product names are confined to URLs and are absent from the body.

- https://github.com/NatronGitHub/Natron (GPL-2.0)
- https://github.com/AcademySoftwareFoundation/OpenColorIO (Apache-2.0)
- https://github.com/Psyop/Cryptomatte (BSD-3-Clause)
- https://github.com/cgwire/awesome-cg-vfx-pipeline (MIT)
- https://github.com/hradec/pipeVFX (GPL-3.0)
- https://github.com/nikopueringer/CorridorKey (educational reference)
