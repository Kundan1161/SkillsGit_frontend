---
id: skillsgit-curated/motion-control-and-consistency-architect
version: 1.0.0
name: Motion Control and Consistency Architect
description: Preserve subject identity, motion, and look across multiple AI-generated video shots — reference frames, identity conditioning, character LoRAs, persistent background plates, and an explicit drift audit.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: creative
tags: [niche:ai-video-generation, consistency, identity-preservation, character-lora, ip-adapter, drift-audit, multi-shot]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: []
  tools_optional: [web_search, file_io]
  min_context_tokens: 24000
  estimated_tokens_per_invocation: 6500
trigger_keywords:
  - video character consistency
  - subject identity preservation
  - character lora video
  - ip adapter video
  - reference frame video diffusion
  - background plate consistency
  - shot to shot drift
  - multi-shot video generation
  - consistent character across cuts
  - persistent identity video
  - identity conditioning
  - drift audit
example_invocations:
  - "I have three shots of the same character; help me keep the face consistent across all three generations."
  - "The background drifts between cuts in my AI-generated sequence; what tactics fix it?"
  - "Plan an identity-conditioning strategy for a recurring character across a 60-second piece."
  - "Audit my current sequence for shot-to-shot drift and tell me which shots need to be regenerated."
inputs:
  - name: sequence_brief
    type: text
    required: true
    description: A description of the sequence — number of shots, recurring subjects, recurring environments, the role of each shot in the edit.
  - name: identity_inputs
    type: text
    required: false
    description: What identity reference material exists — a hero still of the character, a short reference video, a set of training images for a LoRA, or none.
  - name: model_class
    type: choice
    required: false
    description: The class of video-diffusion model in use, which sets the identity-conditioning surface available.
    choices: [frontier_hosted, open_source_dit, open_source_unet_animatediff, image_to_video_only]
  - name: tolerance
    type: choice
    required: false
    description: How tight the consistency target is. Drives which tactics are appropriate.
    choices: [hero_character_documentary_tight, narrative_tight, narrative_loose, b_roll]
  - name: shots_completed
    type: text
    required: false
    description: If shots have already been generated, a description of what exists and what is drifting.
outputs:
  - name: consistency_plan
    type: markdown
    description: The consistency strategy — identity-conditioning recipe, environment-plate plan, prompt-level lock-ins, cut-level masking tactics, and the drift-audit checklist tailored to the sequence.
  - name: drift_audit
    type: markdown
    description: When existing shots are provided, a per-shot drift call-out with severity, the likely cause, and the recommended remediation (regenerate, mask, accept).
  - name: consistency_summary
    type: json
    description: Structured record with `identity_strategy`, `environment_strategy`, `prompt_lockins`, `mask_strategy`, `audit_checklist`, and `regenerations_required` keys.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Motion Control and Consistency Architect

## When to use

Use this skill when an AI-generated video has more than one shot of the same subject or the same environment, and the team needs the subject and the environment to feel like the same subject and the same environment across cuts. The skill produces a consistency plan up front when shots are being designed, and produces a drift audit when shots have already been generated and something is wrong. It is the right skill for any narrative piece with a recurring character, any product piece with a recurring product, any documentary piece with a recurring location, and any sequence where two consecutive shots show the same thing from different angles.

This skill produces methodology guidance for AI video generation. The skill does not address copyright status of training data or generated outputs in any jurisdiction; consult counsel for commercial use. The skill explicitly does not produce or recommend non-consensual likeness use (deepfakes), CSAM, defamatory content, or content that violates platform policy or applicable law. The identity-conditioning tactics described here are powerful and the team is responsible for using them only with the consent of the depicted person, with appropriate license to any reference material, and in compliance with the platform's terms.

The skill complements the shot architect (which designs individual shots) and the post-integration pipeline (which finishes the cut). It sits between them as the layer that keeps the shots feeling like one piece.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `sequence_brief` | yes | The grounding case for every recommendation. |
| `identity_inputs` | no | Decides which identity-conditioning tactics are available. |
| `model_class` | no | Sets which conditioning surfaces and adapter families apply. |
| `tolerance` | no | Drives how aggressively to invest in consistency tactics. |
| `shots_completed` | no | Triggers the drift-audit pathway over the plan pathway. |

## How to apply

The skill walks five decisions in order. Each decision contributes to the consistency plan; the drift audit is a sixth pathway that runs when shots already exist.

### Decision 1 — Identity strategy

1. Identity strategy decides how the model knows what the subject looks like in every shot. Five tactics are useful, in increasing order of effort and effectiveness.
2. **Prompt-level identity.** Write a fixed identity sentence and paste it into every shot's prompt verbatim. "A man in his thirties, short dark hair, a stubble beard, wearing a navy wool coat" is a workable identity sentence. This is the cheapest tactic and works for `b_roll` and `narrative_loose` tolerances. It fails for `narrative_tight` and above — clothing details survive, but the face drifts.
3. **Hero-frame image-to-video.** Generate or photograph a single hero still of the subject and use it as the image-to-video reference for every shot that contains the subject. The subject's first-frame identity is locked; the model invents the motion. This is the workhorse for narrative-tight productions on frontier hosted models. The limitation is that the hero still dictates the framing of the first frame, so every shot starts on a similar composition unless multiple hero stills are prepared (one per intended framing).
4. **Identity adapter conditioning (IP-Adapter family).** Feed a reference image through an identity adapter that conditions the diffusion process on identity features separate from the prompt. Stronger than prompt-level identity and more compositionally flexible than image-to-video. Available on open-source pipelines; frontier hosted products are increasingly exposing equivalent surfaces.
5. **Character LoRA adapted for video.** Train a low-rank adaptation on a curated set of identity images (or short clips), then load it alongside the base model. This is the strongest tactic and the most expensive — it requires a clean training set, training compute, and a model family that supports LoRA loading. For recurring characters across a long piece, the LoRA cost amortises and pays back; for a one-shot piece, prefer hero-frame image-to-video.
6. **Frequency-decomposition identity (research-grade).** Recent research splits facial identity into low-frequency global features and high-frequency intrinsic features and conditions on each separately. Production tools that surface this directly are emerging; until they do, the skill names it as a tactic to watch and recommends one of tactics 2–5 for current work.
7. The decision is grounded in the tolerance: `b_roll` picks tactic 2; `narrative_loose` picks 2 or 3; `narrative_tight` picks 3 or 4; `hero_character_documentary_tight` picks 4 or 5 plus mask-and-composite repair in post.

### Decision 2 — Environment and background-plate strategy

1. Environment consistency is the second axis of drift. The same room, the same street, the same product backdrop has to read as the same place across cuts. Three useful tactics.
2. **Prompt-level environment lock-in.** A fixed environment sentence pasted into every shot's prompt. Works for generic environments ("a sunlit kitchen with white walls and a window on the left"); fails for distinctive environments because distinctive details ("the brass faucet shaped like a swan") will be reinterpreted on every generation.
3. **Persistent background plate.** Generate or photograph a single high-quality background frame and use it as a structure-conditioning reference for every shot. The subject and the camera move are generated against the plate. Where the model exposes a "structure" or "scribble" or "depth" conditioning input, this is where it earns its keep.
4. **Composite-the-background-in-post.** Generate the shots on a clean, controllable background (a solid colour, a simple gradient) where the subject motion is the only thing the model has to get right, then composite the real background underneath in the editor. The post-integration skill covers this tactic in detail; the decision here is whether to commit to it up front.
5. The grade and the lighting are part of the environment. A fixed lighting sentence ("warm morning light from the right, soft shadows") repeated in every shot prompt is cheap and surprisingly effective.

### Decision 3 — Prompt-level lock-ins

1. Once identity and environment are settled, certain prompt phrases are repeated verbatim across every shot to lock the look. The skill names four lock-in slots.
2. **Style anchor.** One medium cue plus one grade cue, repeated verbatim. "Shot on 35mm film, natural grade, warm tones" appears in every shot's prompt.
3. **Identity sentence.** From Decision 1's tactic 2 if used, repeated verbatim.
4. **Environment sentence.** From Decision 2's tactic 2 if used, repeated verbatim.
5. **Lighting sentence.** A fixed lighting sentence repeated verbatim.
6. The shot-specific text — subject's current action, camera move, framing — is written per shot. Everything else is shared. Order the prompt so the locked phrases come first and the shot-specific text comes second; many models weight earlier tokens more heavily.

### Decision 4 — Cut-level masking and seam tactics

1. Even with strong identity and environment strategies, two consecutive shots will have visible seams — small differences in face shape, in skin tone, in the colour of an object, in the angle of a shadow. The cut hides them. Useful tactics.
2. **Cut on motion.** Place the cut on a moment of high motion (a head finishing a turn, a footstep landing). The viewer's eye is tracking the motion and forgives small identity shifts across the cut.
3. **Cut on a graphic match.** A circular shape or a strong vertical in the outgoing frame matched by the same in the incoming frame. The viewer reads the match as continuity.
4. **Cut on an angle change.** A large change in camera angle (over-the-shoulder to wide, profile to three-quarter) gives the viewer permission to interpret the subject afresh; small identity drift becomes invisible.
5. **Mask the seam.** When two shots have to be consecutive and the drift is large, the post-integration pipeline can use a rotoscope mask to swap the face from one shot into the other, or to colour-match a drifting region. The skill flags the seam in the audit; the post skill executes the repair.

### Decision 5 — Motion consistency between shots

1. Motion consistency is a subtler axis than identity consistency, and the one teams most often forget to plan for. The same character should walk with the same gait, throw a punch with the same handedness, hold the cigarette in the same hand. The model has no memory across generations.
2. **Prompt-level motion lock-in.** Repeat a motion characteristic sentence in every shot that contains the subject. "He moves slowly and deliberately, dominant right hand". The model will mostly obey on aggregate; outliers happen.
3. **Reference-driving video.** Where the model exposes a video-reference conditioning input, supply a short reference clip of the subject's motion (or of a stand-in performing the desired motion) and let the model transfer the motion characteristics to the generated shot.
4. **Storyboard the cuts to avoid contradiction.** If shot A shows the subject right-handed and shot B reveals the subject as left-handed, the cut breaks. The skill audits the storyboard for handedness, gait, and posture contradictions before generation rather than after.
5. The motion-LoRA family — training a LoRA on motion characteristics rather than appearance — is an emerging tactic. The skill names it and recommends prompt lock-in plus reference-driving video for current work.

### Decision 6 — Drift audit (pathway for completed shots)

1. When shots have already been generated, the skill audits them for drift instead of (or in addition to) planning. The audit produces a per-shot table.
2. **Identity drift.** Score each shot's subject against the hero still or the LoRA reference: 0 (indistinguishable), 1 (small differences, defensible), 2 (clear differences, fixable), 3 (clear differences, must regenerate). Severity 2 goes to the post-pipeline for face-mask repair; severity 3 returns to generation with a different seed or a different identity strategy.
3. **Environment drift.** Score each pair of consecutive shots that share an environment: 0 (continuous), 1 (small drift, viewer probably forgives), 2 (clear drift, fixable with grade match), 3 (clear drift, must regenerate or composite). Severity 2 goes to the post-pipeline for grade matching; severity 3 returns to generation.
4. **Style drift.** Score the sequence as a whole against the style anchor: 0 (consistent), 1 (small drift), 2 (clear drift, fixable in grade), 3 (clear drift, regenerate). Style drift is most often fixable in grade and rarely requires regeneration.
5. **Motion contradiction.** Walk through the storyboard for handedness and gait contradictions. Any contradiction is severity 3 — the shot must be regenerated with a corrected prompt or the cut order must be revised.
6. The audit output is a markdown table per shot plus a remediation list ordered by impact-over-cost: cheap fixes first (grade match), then masking (face swap, region paint), then regeneration.
7. The audit also calls out cross-shot temporal seams that no individual shot causes. A subject whose hair is wet in shot two and dry in shot three is a continuity break invisible inside either shot but visible across the cut. Continuity breaks are severity 2 or 3 depending on whether they are repairable in post (a subtle wetness pass on the dry shot) or only by regeneration.
8. The audit excludes seam phenomena that the cut hides successfully — the Decision 4 tactics turn many severity-2 drifts into invisible-in-context drifts when the cut is placed correctly. A drift call that disappears under a re-edit of the cut order is documented as such; the consistency plan recommends the re-edit before the regeneration.

### Decision 7 — When to break the consistency rule

1. Not every multi-shot piece wants tight consistency. Some briefs explicitly want each shot to feel like a different aesthetic — a music video with shot-by-shot style shifts, a dream sequence, a montage of perspectives. The skill names this as a separate mode and recommends a different toolkit.
2. **Aesthetic-shift mode.** Identity and environment lock-ins are kept; style anchors are deliberately varied per shot. The viewer reads the style shift as intentional and the consistency demand drops to identity-only.
3. **Vignette mode.** Identity is not maintained across shots — each shot is its own character. Environment and style anchors carry the piece's coherence. The consistency plan focuses entirely on the environment-plate strategy and the style anchor.
4. **Anthology mode.** Each shot is its own world. Coherence comes from the audio, the pacing, and the cut grammar. The consistency plan is a short note: no cross-shot consistency required, audit only for in-shot artefacts.
5. The decision belongs at brief time, not generation time. Teams that try to retro-fit consistency onto a piece designed as a vignette discover the work doubles for no creative gain.

## Outputs

The skill emits three artifacts.

**Consistency plan.** A markdown document covering Decisions 1–5 with the chosen tactics, the identity sentence and environment sentence templates ready to paste, and the cut-level masking notes.

**Drift audit.** When `shots_completed` is provided, a per-shot table with severity scores on the four axes, the cause, and the recommended remediation.

**Consistency summary.** A JSON object with `identity_strategy`, `environment_strategy`, `prompt_lockins`, `mask_strategy`, `audit_checklist`, and `regenerations_required` keys for handoff to the generation and post pipelines.

## Examples

A narrative-tight production has a recurring character across five shots over 30 seconds, with one consistent kitchen environment. The skill picks hero-frame image-to-video as the identity strategy (one frontal hero still, one profile hero still, one over-the-shoulder hero still for the three intended framings), persistent background plate as the environment strategy (a single rendered kitchen plate used as structure conditioning on all shots), four prompt-level lock-ins (style anchor "shot on 35mm film, natural grade, warm tones"; identity sentence "a woman in her forties, shoulder-length brown hair, wearing a grey sweater"; environment sentence "a sunlit kitchen with white walls and a window on the left"; lighting sentence "warm morning light from the right, soft shadows"), and a cut plan that places cuts on motion punctuations. The drift-audit checklist is templated and ready for review post-generation.

A team has generated six shots and the third shot's face is visibly different from the rest. The drift audit scores shot 3 at identity severity 2 (clear differences, fixable). The remediation is a face-mask comp in post — the post-integration skill picks up from there with a face-rotoscope and a frequency-domain face swap from a good frame in shot 2.

A documentary-tight production needs to insert four AI-generated reconstruction shots into a piece that depicts a deceased historical figure. The team has photographic reference. The skill picks LoRA-on-photographic-reference for the identity strategy, persistent background plate for the (period-accurate) environment, four prompt-level lock-ins, and a drift audit that is run at the highest tolerance. The skill also routes the team to the content-policy-and-disclosure skill before generation begins because the depiction of a real (deceased) person at this fidelity carries provenance and right-of-publicity considerations the consistency work alone does not address.

## Working with the drift audit in practice

A worked walk-through. A narrative-tight production has generated five shots and the team brings the rushes to the drift audit.

The audit table is built shot by shot. Shot 1: identity 0, environment 0, style 0, motion 0 — the establishing hero shot, used as the reference for all subsequent audits. Shot 2: identity 1 (small difference in jawline, defensible), environment 0, style 0, motion 0. Shot 3: identity 2 (clear difference, the face is rounder), environment 1, style 0, motion 0. Shot 4: identity 0, environment 0, style 1 (the grade is slightly cooler), motion 3 (the subject is now left-handed; was right-handed in shots 1 and 2). Shot 5: identity 0, environment 0, style 0, motion 0.

The remediation list is ordered by impact-over-cost. Style severity 1 on shot 4 is the cheapest fix (a grade tweak in post, picks up at Stage 5 of the post pipeline). Environment severity 1 on shot 3 is also a grade-level fix. Identity severity 2 on shot 3 goes to the post pipeline for face-mask repair (Stage 6). Motion severity 3 on shot 4 is the expensive item — the shot must be regenerated with a corrected prompt or the cut order must be revised.

The team reviews the cut order. Shots 1, 2, 4, 5 read fine in order; the left-handedness of shot 4 reads as a continuity break if shot 4 is consecutive with shots showing right-handedness. The team re-orders so that the cut goes 1, 2, 3, 5 with shot 4 dropped or re-purposed for a B-roll insert where handedness is not visible. The motion severity 3 becomes "shot dropped" rather than "shot regenerated", saving the regeneration budget.

The audit ends with a remediation worksheet handed to the post pipeline (face-mask repair on shot 3, grade tweaks on shots 3 and 4) and the cut order change going to the editor.

## Identity strategy selection in detail

Which identity tactic to use is the single biggest decision the skill makes for production. A more detailed walk-through of when each tactic fits.

**Prompt-level identity** fits B-roll where the subject is a generic person rather than a specific person. A "shopper walking through a grocery store" can vary in face details across shots and the piece still works. The tactic costs nothing and the failure mode is acceptable.

**Hero-frame image-to-video** fits narrative-tight productions on frontier hosted models where the subject is specific but the production timeline does not justify LoRA training. Three to five hero stills per character cover most framings; each shot uses the still that best matches its intended framing. The hero stills are themselves generated or photographed once and reused across the project.

**Identity-adapter conditioning** fits open-source pipelines where adapter loading is supported and the team is comfortable with the additional pipeline complexity. The adapter conditions every shot on the same reference image set, producing tighter identity coherence than prompt-level alone with less infrastructure than a custom LoRA.

**Character LoRA** fits productions where the same character appears across many shots over many days, where the LoRA training cost amortises against the consistency benefit. The LoRA also unlocks compositional flexibility — the subject can be placed in any framing, any environment, any pose without a hero still constraining the first frame.

**Frequency-decomposition identity** is research-grade as of mid-2026; production tools that surface it directly are emerging. The skill names it as a tactic to monitor and recommends one of the first four for current work.

The choice is not always one tactic per project. A long-form piece may use a LoRA for the hero character, hero-frame image-to-video for a supporting character, and prompt-level identity for background extras. The consistency plan documents the mixture and the drift audit measures each character against its appropriate reference.

## Limitations

## Common pitfalls

**Pitfall 1 — Identity sentence too elaborate.** A 40-word identity description loads more constraints than the model can satisfy and produces a face that drifts on every shot. Corrective: pick the five strongest identity cues (rough age, hair colour and length, skin tone, one wardrobe item, one distinguishing feature) and stop there.

**Pitfall 2 — Inconsistent hero stills.** Using a different hero still for every shot defeats the purpose. The hero still is the lock; every shot that uses it must use the same hero still or a small set of pre-planned hero stills covering the intended framings. Corrective: prepare the hero stills before generation begins.

**Pitfall 3 — Adapter weight too low.** IP-Adapter style conditioning has a strength parameter. At default strength, many adapters produce a face that loosely resembles the reference. Identity-preserving work usually wants the adapter pushed harder. Corrective: probe the strength on a test shot before committing the full sequence.

**Pitfall 4 — LoRA trained on a wide range of looks.** A character LoRA trained on photos with widely varying lighting, hairstyles, and makeup learns the union of the photos and produces a character that drifts across the union. Corrective: curate the training set tight around the canonical look you want the LoRA to reproduce.

**Pitfall 5 — Background plate ignored after pass one.** Teams put the work into the background plate and then forget to keep using it as the conditioning input on each shot. The result is a backslide to text-only generation and the background drifts. Corrective: the conditioning recipe lives in the shot template; each shot inherits it.

**Pitfall 6 — Hidden contradictions in the prompt lock-ins.** "Warm morning light from the right" plus "deep shadows from a streetlight" plus "blue hour" gives the model three incompatible lighting cues. The lock-ins must be internally consistent. Corrective: lock-ins are reviewed once at design time and never edited mid-sequence.

**Pitfall 7 — Auditing only on a small monitor.** Drift visible at delivery resolution is invisible at thumbnail size. The audit must be done at the playback context the piece will be seen in, or at the delivery resolution if the playback context is uncertain. Corrective: audit on a calibrated full-size display.

**Pitfall 8 — Skipping the motion-consistency check.** The skill names motion-consistency as a separate axis precisely because teams forget it. Handedness and gait drift are common and embarrassing. Corrective: walk the storyboard explicitly for motion contradictions before generation.

## Decision summary

| Decision | Question | Default | When to override |
| --- | --- | --- | --- |
| 1. Identity | How does the model know what the subject looks like? | Hero-frame image-to-video for narrative-tight. | Documentary-tight pushes to LoRA; B-roll drops to prompt-only. |
| 2. Environment | How does the model know what the place looks like? | Persistent background plate as structure conditioning. | Generic environments may run on prompt-level lock-in only. |
| 3. Lock-ins | Which phrases are repeated verbatim across shots? | Style anchor, identity sentence, environment sentence, lighting sentence. | Aesthetic-shift mode varies the style anchor deliberately. |
| 4. Cuts | How are seams hidden? | Cut on motion. | Graphic match and angle change when motion is wrong. |
| 5. Motion | How does the model know how the subject moves? | Prompt-level motion lock-in. | Hero motion or signature actions push to reference-driving video. |
| 6. Audit | When are completed shots checked? | After each generation pass, on a calibrated display. | Tight tolerance projects audit after every pass; B-roll audits at the end. |
| 7. Mode | What kind of consistency does the piece want? | Tight consistency on identity and environment. | Vignette, anthology, or aesthetic-shift modes drop different axes. |

## Handing off to other skills

The consistency architect sits between the shot architect (upstream) and the post-integration pipeline (downstream).

**Inputs from the shot architect.** Each shot's design — subject sentence, environment phrases, style anchor, conditioning recipe — feeds the consistency plan. Where shots share a subject or an environment, the architect names the shared lock-ins; where shots deliberately differ, the architect documents the difference as intentional rather than as drift.

**Outputs to the generation pipeline.** The identity strategy, the environment strategy, the prompt lock-ins, and the conditioning inputs (hero stills, reference clips, LoRA weights, plates) all need to be available to the generation system at the time each shot is rendered. The plan documents which artifacts live where and how the pipeline loads them per shot.

**Outputs to the post pipeline.** The drift audit's remediation list is the work order for the post pipeline. Cheap fixes (grade matching, region paint) and expensive fixes (face mask comp) are both routed through Stages 5–6 of the post pipeline. Severity-3 motion contradictions return to generation rather than post.

## Building a hero-still set

When the identity strategy is hero-frame image-to-video, the hero-still set is the single most important asset. A practical method.

**Coverage.** Plan the framings the shots will use — frontal close-up, three-quarter medium, profile, over-the-shoulder, full body. A hero still for each framing keeps the first-frame composition usable without forcing every shot into the same framing.

**Lighting consistency.** Each hero still depicts the subject in the lighting the final shots will use. Frontal-flat-lit hero stills produce frontal-flat-lit first frames; if a shot wants a side-lit look, the hero still for that shot's framing also needs to be side-lit. Mismatched lighting between hero still and shot prompt produces a first frame that fights the rest of the shot's lighting.

**Source.** Hero stills can be generated (an image model with strong identity tools), photographed (a stand-in with similar features, or the actual depicted subject with proper consent), or composited (a photo of the subject with the lighting altered). Whichever source, the hero stills are part of the project archive and the consent record covers them.

**Curation.** Five strong hero stills beat fifteen mediocre ones. The set is curated tight, and underperforming stills are dropped rather than kept "just in case". The discipline keeps the look coherent across the project.

## Building a character LoRA for video

When the identity strategy escalates to LoRA, the training set is the most important asset. A practical sketch.

**Training-set curation.** 30 to 100 images of the subject is a typical range. Variation should be intentional and bounded — multiple angles, multiple expressions, a consistent overall look (similar hair, similar age, similar wardrobe range). Wild variation produces a LoRA that learns the union and drifts; tight variation produces a LoRA that locks the look.

**Captioning.** Each training image is captioned with what it depicts, using the same vocabulary the shot prompts will use. The captioning grammar matters; vague captions ("a person") train a less identity-specific LoRA than specific captions ("a woman in her forties, shoulder-length brown hair, wearing a grey sweater"). Consistent captioning across the training set teaches the LoRA which features are the identity and which are incidental.

**Training duration.** Under-trained LoRAs produce loose identity (the subject is approximate); over-trained LoRAs produce rigid identity (the subject is correct but every generation looks the same in pose, lighting, and expression). The team trains, tests on held-out prompts, and tunes. Two to three training runs is normal.

**Strength at inference.** A LoRA loaded at full strength dominates the model's behaviour. Many production setups load LoRAs at partial strength to balance identity preservation against compositional flexibility. The setting is per-project and per-shot tunable; the consistency plan names the starting setting and lets the per-shot iteration tune from there.

**Re-use.** A character LoRA built for one project can be re-used in subsequent projects with the same character. The consistency plan documents the LoRA's training set, the captioning convention, and the strength setting so a future project can pick up where this one left off.

## Limitations

The skill does not train LoRAs or execute identity conditioning; it specifies them. The execution lives in the team's generation pipeline. The skill assumes the team has the rights to the reference imagery they are conditioning on; it refuses to plan identity preservation for non-consensual likeness use. The drift audit relies on the user describing what is drifting; for direct image evaluation, pair the audit with a multimodal reviewer. The motion-consistency tactics are weaker than the identity-consistency tactics in current models; for productions that demand exact motion repeatability (a hero stunt, a synchronised dance), capture the motion practically and use the AI generation only for non-hero shots, or use motion-capture-driven generation if the pipeline supports it.

## When the audit recommends re-editing rather than regenerating

A subtle but high-value recommendation the audit can make is to change the cut order rather than to regenerate a shot. Examples.

A sequence of five shots has a hero severity-2 identity drift on shot 3. Regeneration is expensive. The audit notices that shot 3 is a cutaway to a hand action that could be repositioned in the cut order; placed between shots 1 and 2 rather than between shots 2 and 4, the drift is invisible because shots 1 and 2 have other identity variations the drift sits within. Recommendation: re-edit to reorder shot 3 rather than regenerate.

A piece has motion-contradiction severity 3 on shot 4 (the subject is left-handed while shots 1, 2, 5 show right-handed). Regeneration of shot 4 is one option; dropping shot 4 from the cut is another; re-purposing shot 4 as a B-roll cutaway where handedness is not visible is a third. The audit names all three and ranks by cost.

A two-shot sequence has continuous-environment severity 2 (small shift in wall colour between shots). Regeneration of either shot would address it; a grade-match in post addresses it more cheaply; cutting on a closer shot between the two breaks the direct comparison and addresses it for free. The audit suggests the cheapest fix that meets the consistency target.

The principle is that consistency is judged in context. A drift visible in shot-by-shot review may be invisible in the finished cut; a drift invisible in shot-by-shot review may be glaring in the finished cut. The audit walks the cut, not just the shots.

## Multi-character and multi-environment plans

Productions with more than one recurring subject or more than one recurring environment scale the methodology rather than abandoning it.

**Multi-character plans.** Each recurring character gets its own identity strategy. Pick the strategy per character based on their on-screen prominence: the hero gets the most expensive treatment (LoRA or aggressive image-to-video), supporting characters get hero-frame image-to-video, background extras run on prompt-level identity. The drift audit is run per character, not per shot — a hero-character drift in shot 5 is severity 3; a background-extra drift in shot 5 is severity 0 because the audit does not even score background extras at hero severity.

**Multi-environment plans.** Each recurring environment gets its own background plate or its own environment sentence. A shot that transitions between environments (a character walks from a kitchen into a garden) is one shot for design purposes but inherits both environments' lock-ins; the consistency plan documents the inheritance.

**Character-environment interactions.** A character that appears in multiple environments must look like the same character across the environments. The identity strategy stays constant; the environment strategy varies. The drift audit catches the case where the identity adapts to the environment (the character's face shifts subtly between the kitchen and the garden); the remediation is to strengthen the identity strategy or to accept the small drift if the audit calls it severity 1.

**Documentation.** The consistency plan documents every recurring subject and every recurring environment with its strategy and its conditioning inputs. A piece with six recurring subjects and four recurring environments has a 24-cell consistency matrix; the plan presents it as a table for the generation team to reference.

## A short note on motion-capture-driven consistency

Where the production has access to motion capture or video reference of actual human performance, motion consistency becomes much more tractable. The reference captures gait, handedness, posture, and timing simultaneously; conditioning on the reference transfers all of these to the generated shot.

The catch is that motion-capture-driven video generation is a fast-moving area; tools and methods change month to month. The skill names the approach and recommends that teams who plan to rely on motion capture pilot the workflow on a non-critical shot before committing the production to it.

Motion capture also re-opens the consent and likeness questions handled by the policy skill. A motion-captured performance is the captured person's performance even when the rendered identity is different; consent and credit are part of the workflow.

## When the consistency plan crosses into post

Some of the consistency architect's recommendations are executed in the post pipeline rather than at generation. The plan names which.

**Grade-match for environment drift** is a post job. The consistency plan documents the target colour, the reference shot, and the per-shot adjustments; the colourist implements them.

**Face-mask repair for identity drift** is a post job. The consistency plan documents which shot needs the repair, what reference frame is the source for the swap, and how aggressive the swap should be. The compositor implements.

**Region paint for environment artefacts** is a post job. The plan documents what needs painting and from where.

**Regeneration for severity-3 drifts** returns to generation. The plan documents what should change in the prompt or the conditioning to make the next generation land.

The plan is the contract between the consistency architect and the post pipeline. Without it, the post team is reverse-engineering what the consistency architect intended; with it, the post team executes the plan.

## Sources reviewed

- https://github.com/hpcaitech/Open-Sora (Apache-2.0)
- https://github.com/zai-org/CogVideo (Apache-2.0 code; model weights have additional terms)
- https://github.com/genmoai/mochi (Apache-2.0)
- https://github.com/guoyww/AnimateDiff (Apache-2.0)
- https://github.com/Stability-AI/generative-models (Stability AI Community License — limited commercial use, disclose)
- https://www.mercity.ai/blog-post/understanding-and-training-ip-adapters-for-diffusion-models/ (vendor blog, methodology reference)
- https://pku-yuangroup.github.io/ConsisID/ (research project page)
- https://arxiv.org/html/2402.09368v2 (arXiv preprint, methodology reference)
- https://papers.nips.cc/paper_files/paper/2024/file/c7138635035501eb71b0adf6ddc319d6-Paper-Conference.pdf (NeurIPS 2024 paper)
