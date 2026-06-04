---
id: skillsgit-curated/motion-graphics-shot-architect
version: 1.0.0
name: Motion Graphics Shot Architect
description: Design a motion-graphics shot end to end — brief, storyboard, animatic, asset prep, scene hierarchy, animation principles, easing curves, render passes, and export specs.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: creative
tags: [niche:motion-graphics-vfx, motion-design, keyframes, easing-curves, render-passes, animatic, scene-hierarchy]
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
  estimated_tokens_per_invocation: 5000
trigger_keywords:
  - motion graphics
  - motion design
  - animatic
  - storyboard
  - keyframe easing
  - scene hierarchy
  - render passes
  - shot brief
  - mograph
  - title sequence
  - animation principles
  - export spec
example_invocations:
  - "I have a 15-second product reveal brief — walk me through architecting the shot from board to final render."
  - "How should I structure the scene hierarchy and pre-comps for a logo sting with three nested mechanical pieces?"
  - "What render passes do I need so the colorist can grade the explainer without re-rendering?"
  - "Plan the easing curves and animation principles for a coin-flip transition between two scenes."
inputs:
  - name: brief
    type: text
    required: true
    description: The creative brief — duration, deliverable resolution and aspect, message, brand constraints, references, hard deadline.
  - name: shot_style
    type: choice
    required: false
    description: The dominant visual style for the shot.
    choices: [2d-flat, 2.5d-parallax, 3d-rendered, mixed-media, kinetic-typography, infographic-explainer, logo-sting, title-sequence, ui-mock-promo]
  - name: integration_target
    type: choice
    required: false
    description: Where the shot will live.
    choices: [broadcast, web-hero, social-vertical, in-product, cinema-dcp, trade-show-loop]
  - name: pipeline_tools
    type: text
    required: false
    description: A short list of the motion-graphics tool, 3D suite, and compositor in use so render-pass and export advice can be tuned.
outputs:
  - name: shot_plan
    type: markdown
    description: A sequenced plan from brief interpretation through final delivery, including timing budget, board beats, asset list, and review checkpoints.
  - name: scene_hierarchy
    type: markdown
    description: A concrete hierarchy of comps, pre-comps, null parents, and groups with naming conventions ready to implement.
  - name: animation_spec
    type: markdown
    description: Per-beat easing-curve and animation-principle recipe, including hold frames, anticipation windows, and follow-through tails.
  - name: render_and_export_spec
    type: markdown
    description: Render-pass list with file-format and color-space settings, plus deliverable specs (resolution, frame rate, codec, loudness target if audio).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when a motion-design artist or generalist has a brief for a single shot (or a tight sequence of related shots) and needs a structured plan before keyframing anything. Typical situations:

- A new shot brief landed and the artist must turn loose creative intent into a board, an animatic, an asset list, and a final deliverable spec before the timer starts.
- The shot exists as a rough comp in a motion-graphics tool, but the layer stack has grown unmanageable and a clean re-architecture is needed.
- The render pipeline must hand off cleanly to a colorist, an editor, or a downstream compositor and the artist needs to decide upstream what passes and channels to expose.
- The brief includes nested mechanical pieces, parented rigs, or a 3D element that must read as 2D, and the artist needs a hierarchy plan before placing the first null.

Do not invoke this skill for purely technical questions about a single tool feature (e.g. "what is the keyboard shortcut for splitting a layer"). Do not invoke it for live-action plate work that has no graphics overlay — that is a compositing job and the node-based compositing skill applies. Do not use it as a substitute for art direction; the creative concept must already exist in the brief.

## How to apply

The methodology runs from brief to delivery in seven phases. Each phase produces an artifact the next phase consumes. Skipping a phase is permissible but must be explicit and reasoned, not accidental.

### Phase overview

- Phase 1 parses the brief and produces a timing budget broken into beats.
- Phase 2 builds the storyboard, promotes it to an animatic, and locks the timing against stakeholders.
- Phase 3 prepares every asset and normalizes color, resolution, and alpha conventions.
- Phase 4 builds the scene hierarchy with naming and pre-comp discipline.
- Phase 5 applies animation principles and tunes easing curves.
- Phase 6 plans render passes and export formats.
- Phase 7 packages the deliverables and the working project for handoff.
- Phase 8 documents pitfalls and self-checks before declaring the plan complete.

A typical shot of 10 to 20 seconds passes through all eight phases. A title sequence of 60 seconds or more may iterate phases 4–6 several times as the design evolves. Whatever the scale, the order of phases is fixed; skipping forward (e.g. into final art before lockdown of the animatic) is the single largest cause of motion-design rework.

### 1. Parse the brief into a timing budget

1. **Restate the brief in one paragraph.** Include duration in seconds and frames at the project frame rate, deliverable aspect ratios, the one-sentence message, and any non-negotiable brand or legal constraints. If two pieces of the brief contradict (e.g. "feels playful" and "use only the corporate serif"), surface the contradiction and ask.
2. **Break duration into beats.** Most graphics shots have between three and seven beats. A 15-second piece typically lands at intro hold (1.5s), establish (2s), build (4s), payoff (3s), brand lock-up (2.5s), tail (2s). Convert each beat to integer frames at the working frame rate; round so the sum equals the deliverable length exactly.
3. **Reserve handles at head and tail.** Add at least 12 frames of pre-roll and 24 frames of post-roll on the working timeline. Handles are non-negotiable on broadcast and edit-bay deliverables; web-hero loops can drop the tail handle if it loops seamlessly.
4. **Identify any music or VO track.** If audio is locked, mark every transient hit and word stress as a frame number; those are anchor frames the animation must respect. If audio is not yet locked, set placeholder hits at the beat boundaries and flag every animation choice that will need to retime when real audio arrives.
5. **Confirm the deliverable ratios.** A single shot frequently ships at 16:9, 9:16, 1:1, and 4:5. Plan the composition with a safe area for all required ratios from the start; do not crop after the fact.

### 2. Storyboard and animatic

6. **Sketch one frame per beat at minimum.** Storyboards do not have to be polished; they have to be readable. Each frame names the on-screen elements, the camera or composition framing, and the action that begins on that beat.
7. **Promote the boards to an animatic.** Hold each board frame for its assigned beat duration and play it back. If a beat reads dead, it is either too long, the framing is wrong, or the prior beat over-resolved the energy. Adjust beat durations before producing any final art.
8. **Run a one-line caption pass.** Under each board, write the single thing the viewer is meant to think or feel on that beat. If two beats produce the same thought, one is redundant; cut or merge.
9. **Identify camera moves.** A "static" graphics shot still has implicit moves — a parallax push, a rack focus, a whip pan into the next beat. Name them explicitly so they are in the asset plan, not improvised later.
10. **Lock the animatic with stakeholders before any final art is built.** Final art produced against a soft animatic is the leading cause of motion-graphics rework.

### 3. Asset preparation

11. **List every asset and its source.** Vector logos, illustrations, photographs, type, 3D models, footage plates, audio stems. For each, name the source file, the version, the color space it was authored in, and who owns approval.
12. **Force vector assets to outlined paths.** Live type and live vector strokes shift across versions of editorial tools. Outline type before bringing the file into the motion-graphics scene unless typographic editing is required mid-shot (in which case freeze the font version and ship the font with the project).
13. **Normalize raster assets.** Resample raster art to at least 2× the deliverable resolution along its longest in-shot dimension so scale-ups do not soften. Strip embedded color profiles only after converting into the working color space.
14. **Tag every asset with a working color space.** Body-of-work motion design today happens in a scene-linear working space (a linear variant of an sRGB or P3 gamut) with view transforms applied at the display pipeline. Pre-multiply alpha discipline applies — see the node-based compositing skill — but at this stage the rule is simply that every asset is tagged with the color space its values are encoded in.
15. **Pre-build 3D-to-2D bridges.** For any 3D element rendered for graphics use, decide now whether it ships as a flat alpha-channel render with passes baked in, or as a multi-channel EXR with arbitrary output variables that the compositor will manipulate. The choice constrains scene hierarchy.

### 4. Scene hierarchy and naming

16. **Build the hierarchy top-down by beat first, then by element.** The top level of the scene is one container per beat; inside each beat container is the set of elements active in that beat; inside each element is its animation rigging. This makes the scene navigable by anyone who has seen the boards.
17. **Use null parents (or empty parents) for every animated transform group.** Animate the null, not the leaf. This makes it trivial to retime, reuse, or hand off an animation rig.
18. **Adopt a single naming convention and enforce it.** Recommended pattern: `beat##_role_element_descriptor` (e.g. `b03_hero_logo_anticipation`). Numbered beats sort cleanly; the role token (`hero`, `bg`, `fx`, `txt`) lets the artist filter the layer panel quickly.
19. **Cap nesting depth at four levels in 2D and six in 3D.** Deeper nesting is almost always a sign that an element should be promoted to a pre-comp or its own scene.
20. **Pre-comp by intent, not by convenience.** A pre-comp exists because a group of layers should be treated as a single unit for effects, retiming, or repetition. Do not pre-comp "to clean up the panel"; flatten or hide layers instead, or the pre-comp boundary will hide a timing bug later.
21. **Color-code or tag layer roles.** Hero foreground elements, background plates, lighting and effects layers, and matte holdouts should be visually distinguishable at a glance. The exact color is arbitrary; consistency across the studio is what matters.

### 5. Animation principles applied to graphics

22. **Decide which of the twelve principles each beat must respect.** Not every shot uses all twelve. For most graphics work the recurring set is: squash and stretch, anticipation, slow-in / slow-out (easing), follow-through and overlapping action, arcs, secondary action, timing, and exaggeration. Solid drawing, appeal, staging, and straight-ahead-vs-pose-to-pose apply but show up implicitly in the boards.
23. **Apply squash and stretch to give weight.** A shape that arrives and stops must compress on contact and rebound. A shape that accelerates must elongate along its velocity vector. Preserve volume — squash and stretch is a deformation, not a scale; the bounding box area should remain roughly constant.
24. **Anticipate every major action.** Before a shape leaps right, it pulls left for two to four frames. Before a title pops on, the world contracts inward by a few pixels. Without anticipation, motion reads as a teleport.
25. **Use easing curves with discipline.** The default Bezier handles produced by a graphics tool are rarely correct on the first try. The defaults usually need adjustment: stronger ease-out on a hero element entering, harder ease-in on a piece coming to rest, near-linear motion only for purely mechanical or technical readouts.
26. **Tune curves in the curve editor, not in the timeline.** The graph editor (or curve editor) shows velocity over time as a curve; the timeline shows only keyframe positions. Most timing bugs reveal themselves only in the graph editor.
27. **Add follow-through tails.** A trailing element on a hero shape (a cape, a particle puff, a flag) continues moving for four to twelve frames after the parent has stopped. Overlapping action staggers the offsets so the elements do not all stop on the same frame.
28. **Hold for a beat after motion resolves.** A shape that arrives, springs once, and immediately moves again gives the viewer no time to read it. Hold the resolved pose for at least eight frames before initiating the next action.
29. **Stagger by milliseconds, not whole frames.** A two- or three-frame offset between sibling layers reads as life; a same-frame action on every sibling reads as a machine. Use the offset / staggered-array helpers in modern motion-graphics tools to apply staggers programmatically across many layers.
30. **Cap the count of competing animations on screen.** Beyond roughly five simultaneous independent animations, the viewer cannot track any of them. Either group them (one shared parent animation that affects all) or stagger so only a few are at peak motion at any frame.

### 6. Render passes and export

31. **Decide whether the shot finishes in the motion-graphics tool or in a compositor.** If the colorist or editor will only place the shot on a timeline, render a single final file with the view transform baked in. If a compositor downstream will key, grade, or integrate with live action, render to a multi-channel format with the view transform NOT baked in.
32. **List the render passes needed by every downstream task.** Typical passes: beauty (RGB+A), depth (Z), motion vectors (for retimes and motion-blur reconstruction), object or material IDs (for selective grading), ambient occlusion, lighting and shadow passes for 3D elements. Cryptomatte-style ID encoding is preferred over flat ID passes because it survives motion blur and transparency.
33. **Export in a format that preserves precision.** For a finishing-quality master, render to a 16-bit-per-channel half-float EXR sequence (multi-channel if passes are split, single-channel if flat). For intermediate review and reference, a ProRes or DNxHR family codec at the deliverable bit depth is acceptable.
34. **Bake color space into the file metadata.** Every EXR should carry a chromaticities or color-space attribute readable by the downstream tool. A ProRes file should carry a color tag matching the working space.
35. **Set frame rate and pixel aspect explicitly.** Inheriting the frame rate from the project default is a frequent source of cross-tool drift; set it per render.
36. **Render in linear, view-transform in the display path.** Apply the view transform (the encoding that maps scene-linear values to display values) only when producing the review or final delivery clip; never bake it into the working EXR sequence.

### 7. Delivery and handoff

37. **Produce a deliverables matrix.** One row per required aspect ratio and platform; columns for resolution, frame rate, codec, color tag, audio loudness target, file name token. Fill the matrix before exporting anything.
38. **Add file naming with version and date.** A file name like `proj_shot010_v007_2026-05-14.mov` survives reviews better than `final_FINAL_v3.mov`. Adopt a naming pattern and enforce it.
39. **Embed slate and head pop where required.** Broadcast and DCP deliveries require a slate frame, head pop, and tail pop. Web-hero loops require a clean cut. Match the deliverable spec, not the artist's preference.
40. **Produce a frame for review still.** A poster frame at the strongest visual beat (often the brand lock-up) doubles as a thumbnail and a fallback for any tool that does not render preview animations.
41. **Hand off the working project as the deliverable, not in addition.** Many studios deliver the working file alongside the rendered output so a future change can be made without rebuilding. Include the asset library, the fonts, and a README that names the working color space and the view transform.

### 8. Common pitfalls to call out in the plan

42. **The "render at the end" trap.** Artists frequently defer render-pass decisions until the comp is locked, then discover that re-rendering a 3D element to add a Cryptomatte costs hours per shot. Decide render passes during scene-hierarchy planning, not at delivery.
43. **The "single mega-comp" trap.** A single 800-layer scene with all beats stacked vertically becomes uneditable. Always pre-comp by beat or by element group; the small overhead at setup is repaid every iteration.
44. **The "default ease" trap.** Default Bezier handles produced by every motion-graphics tool generate identical, soft, lifeless motion. Treat default easing as a placeholder, not a result; review every curve in the curve editor before delivery.
45. **The "stagger by frame" trap.** A two-frame stagger across many siblings is perceptible at 24fps; the same stagger at 60fps disappears. Tune staggers to the project frame rate, not to a memorized count.
46. **The "music drives art" trap.** When music arrives late, the entire animation may need to retime to match. Plan boards and animations to multiples of an integer frame count per beat so the retime is a global stretch rather than a per-keyframe rebuild.
47. **The "framing for one aspect" trap.** A composition tightly framed for 16:9 fails when reframed to 9:16. Compose with a center-safe area that survives every required aspect from the start.

### 9. Self-check before responding

48. **Does the plan respect the beats from the animatic?** If your spec drifts from the agreed-on board, surface it; do not silently relocate beats.
49. **Is every animated transform on a null parent?** If a leaf layer has its own animation, flag the layer for re-rigging.
50. **Is the render-pass list sufficient for every downstream task named in the brief?** If the colorist needs object IDs and the plan does not produce them, fix the plan, not the render.
51. **Are the deliverable ratios all framable within the working composition?** Re-frame, do not re-crop.
52. **Has the view transform been kept out of the working file but applied in delivery?** If unsure, state the assumption explicitly so the next artist does not double-apply it.
53. **Did you reserve handles, head pop, and tail pop where the deliverable requires them?** A delivery that drops a frame is a rejected delivery.
54. **Did you name every working file with version and date?** Even a draft handoff gets a versioned name; the cost of versioning is far smaller than the cost of confusion.

## Anti-patterns the plan must avoid

- **Animating every layer on the same frame.** Even a perfectly choreographed "everything snaps on the beat" reads as mechanical; offset siblings by a few frames.
- **Easing with the default Bezier and hoping it reads natural.** Default easing is uniform and slow; review and customize every curve.
- **Baking the view transform into the working EXR.** A view-transformed working file cannot be regraded without re-rendering.
- **Pre-comping for visual tidiness instead of intent.** A pre-comp boundary blocks retiming and effect propagation; use it when grouping behavior, not when grouping appearance.
- **Treating the animatic as a sketch and starting final art without locking it.** A soft animatic is a guaranteed rework path.
- **Cropping after the fact for vertical or square aspects.** A composition planned for one aspect will rarely crop to another without losing the message.
- **Skipping handles to save render time.** The minutes saved during render are repaid tenfold when the editor needs an extra frame at the cut point.

## Easing-curve vocabulary

The vocabulary of easing curves is small but disciplined. The plan should name the easing intent rather than the numeric handle values, because handle numerics vary by tool while intent is portable:

- **Linear.** Equal velocity across the interval. Reserved for purely mechanical motion (digital readouts, scientific simulations). Linear motion on a living shape reads as a fail.
- **Ease-out.** Fast start, slow finish. The default for an element arriving at its hero pose.
- **Ease-in.** Slow start, fast finish. The default for an element leaving the frame after its beat.
- **Ease-in-out.** Slow at both ends, fast in the middle. The default for transitions where neither end is the hero pose.
- **Anticipated ease-out.** The motion first overshoots slightly opposite to its target, then snaps toward the target. Adds life to mechanical motion.
- **Spring or bounce.** The motion overshoots the target, returns past it once or twice, and settles. Useful for snap-into-place beats; over-use makes a shot read as cartoonish.
- **Cubic-bezier with custom handles.** Any curve the artist tunes by hand in the curve editor. Hero beats almost always require custom handles; default presets are rarely correct on the first try.

Name the easing intent in the plan and let the artist tune handles in the tool. The intent travels across tools; the handle values do not.

## Pacing and energy curves

A motion-graphics shot has an energy curve over its duration as surely as it has a timing budget. The energy curve maps roughly to viewer attention; a flat energy curve loses the viewer mid-shot, a continuously rising curve exhausts attention before the payoff.

- **The classic curve.** Low introduction, gradual build to a payoff at roughly 70% of the shot's duration, resolved hold at the end. The brand lock-up lands in the payoff zone; the tail gives the viewer a moment to register it.
- **The cold open.** High energy in the first second, hold, then taper. Suited to social-vertical contexts where the first frame must arrest scroll.
- **The reveal.** Long buildup, single sharp peak, immediate resolution. Suited to product reveals where the product itself is the payoff.
- **The continuous push.** Increasing energy throughout, ending at the brand. Risky; consumes viewer attention rapidly and is generally limited to short pieces of three to five seconds.

Choose the energy curve in step 2 of the methodology (alongside boards) and check it again in step 5 (animation principles). The choice of curve constrains how many anticipation beats are appropriate, how aggressive the easing should be, and where the hero hold lands.

## Inputs

- A creative brief with duration, message, deliverable platforms, and references.
- Optional: dominant shot style, integration target platform, and tool chain.

## Outputs

- A sequenced shot plan from board through delivery.
- A scene hierarchy and naming convention.
- A per-beat animation principle and easing-curve spec.
- A render-pass list, color-space plan, and deliverables matrix.

## Examples

**Example invocation**

> "I have a 12-second product reveal for a wristwatch. Brand wants a kinetic typographic intro, the watch flies in from off-frame, components separate and reassemble, then a logo lock-up. Deliver 16:9 hero web and 9:16 social. Locked music with hits at 0:02, 0:05, 0:08, 0:11."

**Expected high-level output**

Shot plan: six beats — typographic intro (1.5s ending on 0:02 hit), watch entry (1.5s ending on 0:03.5), component separation (2s ending on 0:05.5), free-float pose (1.5s landing on 0:07 hit), reassemble (2s landing at 0:09), lock-up (1.5s plus 1s hold to 0:12). Music hits at 0:02 / 0:05 / 0:08 / 0:11 map to typographic snap, separation impact, free-float peak, and lock-up arrival.

Scene hierarchy: `00_typo_intro/`, `01_watch_entry/`, `02_components_explode/`, `03_freefloat/`, `04_reassemble/`, `05_lockup/`. Inside `02_components_explode`, one null per component (`b02_part_bezel`, `b02_part_dial`, `b02_part_movement`, `b02_part_strap`) with sub-nulls for primary and secondary motion. Logo lock-up in its own pre-comp so the 16:9 and 9:16 versions can swap framings.

Animation spec: typo intro uses two-frame anticipation back-tracking before each word, near-linear motion through the body, hard ease-in to a four-frame hold. Watch entry uses an arc from off-frame upper-right with stretch along the velocity vector and a squash-on-arrival. Component separation staggers four components by two frames each with secondary spinning motion at a different rate per component. Lock-up uses a slow-in / slow-out with a four-frame hold then a one-pixel inward pulse on the brand hit.

Render and export: render multichannel EXR with beauty, depth, motion vectors, and Cryptomatte object IDs for components. Working space scene-linear with a Rec.709 view transform applied at delivery. Deliverables matrix: 1920×1080@24p ProRes 422 HQ for hero web; 1080×1920@30p H.264 high-bitrate for social. Both with metadata color tags matching their delivery space.

**Second example invocation**

> "Six-second logo sting for an enterprise software brand. Brand uses navy and gold. The logo has three mechanical pieces that must seem to assemble in 3D space and settle into the final mark. Deliver 16:9 for trade-show kiosk loops at 30fps."

**Expected high-level output**

Shot plan: three beats — components arrive (2s), components align and seat (2.5s), brand hold (1.5s with one-frame inward pulse on the seat moment). Loop tail blends to the head frame for seamless kiosk playback.

Scene hierarchy: `00_arrival/`, `01_alignment/`, `02_hold_with_pulse/`. Three null parents for piece A, piece B, piece C. Each piece null has a `position` child null and a `rotation` child null so the animator can re-time translation independently of rotation. Camera and lighting in a sequence-level group reused across the trade-show loop family.

Animation spec: pieces arrive from three different off-screen positions on a shared arc; piece A leads by four frames, piece B by two, piece C arrives on-beat — staggered overlapping action. Each piece has a six-frame anticipation back-motion before its arrival vector. Easing curves: aggressive ease-out at velocity peak, hard ease-in to alignment, micro-spring on contact with the seated position. Brand hold has a single one-pixel inward pulse on the alignment frame to mark the seat without overplaying it.

Render and export: 3D pieces render as multichannel EXR with beauty, Z, motion vectors, Cryptomatte material IDs. View transform applied in delivery only. Loop deliverable as a 1920×1080@30p ProRes 422 HQ file with head and tail frame-matched for kiosk software's loop point. A 15-second filler-loop variant produced by holding the brand for an extra 9 seconds; specs note this variant explicitly.

## Working with locked vs unlocked audio

A surprising amount of motion-design rework comes from animation built against placeholder audio that drifts when real audio arrives. The discipline below limits the damage:

- **Lock the music before final art when possible.** A locked music track defines every beat, transient, and emphasis the animation can attach to.
- **When music is unlocked, animate to beat boundaries, not to specific transients.** A beat-aligned animation tolerates a music swap; a transient-locked animation does not.
- **Build a music-driven retime control.** A single retime knob that warps the animation timeline against the music timeline lets the artist accommodate a tempo change in minutes rather than hours.
- **Render scratch animations against the placeholder music.** When the final mix arrives, swap the music and re-render; do not rebuild keyframes unless the music has fundamentally restructured.
- **Negotiate audio delivery early.** A producer who knows that audio drift costs a day per shot will push the audio vendor to deliver sooner.

## Typography in motion

Typography is a frequent failure point in motion graphics because type that reads well in print fails when it moves. Apply the following constraints whenever type animates:

- **Hold type long enough to read.** A rule of thumb is one second per six to eight words for adult viewers on a typical web viewing distance, longer for executive review where the audience may be glancing rather than fixed on the screen.
- **Avoid animating during the reading window.** If type must be read, animate it on, hold it static for the reading window, then animate it off. Animation during reading destroys legibility.
- **Set kerning by hand for hero type.** Auto-kerning produced by the motion-graphics tool is rarely sufficient at hero scale. Kern manually for the strongest typographic beats.
- **Set tracking generously for small or fast type.** Tighter tracking that works in print collapses when type moves quickly. Open tracking by 5 to 15 units at hero scale, more at small sizes.
- **Test the type at deliverable resolution and on the deliverable medium.** Type that reads on a calibrated studio monitor at 1:1 may fail on a phone in daylight. Preview at deliverable resolution on the target medium where possible.
- **Animate type in groups.** Word-by-word reveals work for short phrases; line-by-line reveals work for paragraphs. Letter-by-letter animation is rarely worth the production cost and seldom serves comprehension.

## Color and motion together

Color and motion interact in ways that are easy to miss in static review. Apply the following discipline:

- **Animations operating on luminance read more clearly than animations operating on hue.** A piece that brightens to draw attention works on any display; a piece that color-shifts may fail under different display calibration or color blindness.
- **Saturated colors in fast motion create chromatic aberration artifacts on consumer displays.** Reduce saturation for the fastest beats; restore for the hero holds.
- **Light-on-dark and dark-on-light contrast levels must hold throughout the animation.** A title that has good contrast on its hero pose may fall to insufficient contrast mid-animation as background elements pass behind.
- **Color-blind safe pairs survive translation across the audience.** Choose color pairs that hold contrast in achromatic preview as a baseline check.

## Review and approval cadence

Each beat of the plan corresponds to a natural review point:

- After phase 1 (timing budget), share the beat breakdown with the producer. A 30-minute conversation here saves days.
- After phase 2 (animatic), screen for the director or client. Lock the animatic explicitly before final art begins.
- After phase 4 (hierarchy), screen for the lead artist or technical director. A misnamed pre-comp on day one becomes everyone's problem on day fifteen.
- After phase 5 (animation principles applied to a first-pass blocking), screen for the director. The animation read should be clear even from rough art.
- After phase 6 (final render with passes), screen for the colorist and downstream comp. Render-pass mistakes caught here cost minutes; caught at delivery they cost reruns.
- After phase 7 (delivery package), the editor screens against the cut. Confirm the deliverable lands where the cut expects it.

Documenting these screening points in the plan keeps unanticipated reviews from injecting late notes that force re-architecture.

## Limitations

- This skill plans a shot; it does not generate finished art, write expressions, or render frames. Implementation in any motion-graphics tool is downstream.
- It does not perform retiming for a music track that arrives after the boards are locked; it surfaces the retime as a flagged risk.
- It does not address live-action plate compositing — that belongs to the node-based compositing pipeline skill.
- It does not handle stereoscopic or volumetric (head-mounted display) deliverables, which carry their own depth-budget and parallax rules.
- It assumes a single artist or a tight team; multi-studio outsourcing has additional package-and-review steps in the shot-breakdown-and-handoff skill.

## Sources reviewed

The methodology synthesized here draws on patterns observed across the following open-source repositories and reference projects. None of the prose above is derived from any single source. Trademarked product names are confined to URLs and are absent from the body.

- https://github.com/JacquesLucke/animation_nodes (GPL-3.0)
- https://github.com/3DSinghVFX/animation_nodes (GPL-3.0)
- https://github.com/mrachinskiy/commotion (GPL-3.0)
- https://github.com/quollism/blender-keyframetools (GPL-3.0)
- https://github.com/cgwire/awesome-cg-vfx-pipeline (MIT)
- https://github.com/AcademySoftwareFoundation/OpenColorIO (Apache-2.0)
- https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES (Apache-2.0)
- https://github.com/Psyop/Cryptomatte (BSD-3-Clause)
