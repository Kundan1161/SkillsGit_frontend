---
id: skillsgit-curated/captions-and-accessibility-deliverable-pipeline
version: 1.0.0
name: Captions and Accessibility Deliverable Pipeline
description: Produce a complete captions and accessibility deliverable set for a streaming title — captions, SDH, audio descriptions, sign-language, multi-language, conformant to WebVTT/TTML/IMSC1.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: creative
tags: [niche:video-encoding-delivery, captions, sdh, webvtt, ttml, imsc1, accessibility, audio-description]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - captions pipeline
  - subtitle deliverables
  - sdh authoring
  - audio description
  - sign language pip
  - webvtt authoring
  - ttml imsc1
  - wcag 2.2 captions
  - multi-language subtitles
  - accessibility delivery
  - forced narrative subtitles
  - caption qc
example_invocations:
  - "Plan the captions and audio-description deliverables for a 6-episode documentary series."
  - "Author an SDH WebVTT pass over an English transcript and check conformance."
  - "Wire sign-language picture-in-picture into the delivery package."
  - "Set up a multi-language subtitle workflow with translation and QC gates."
inputs:
  - name: title_profile
    type: text
    required: true
    description: What is being made accessible — duration, genre, dialog density, sound design density, on-screen text, original language, target languages.
  - name: audience_requirements
    type: text
    required: true
    description: Regulatory and platform obligations and audience expectations — WCAG 2.2 conformance level, regional broadcast rules, platform-specific spec (HLS device families, DASH device families), in-house accessibility commitments.
  - name: existing_assets
    type: text
    required: false
    description: What inputs already exist — transcripts, draft captions in any format, dubbed audio, descriptive audio, signed video.
  - name: timeline
    type: text
    required: false
    description: Release schedule and any hard deadlines that constrain authoring and review.
outputs:
  - name: deliverable_set
    type: markdown
    description: The list of accessibility deliverables to produce, with the format, language, and intended use of each.
  - name: authoring_guide
    type: markdown
    description: Per-deliverable authoring instructions covering conventions, style, and conformance checks.
  - name: qc_plan
    type: markdown
    description: A QC matrix with the validation steps, tools, and acceptance criteria before publish.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when an agent is asked to define, author, or audit the accessibility deliverables that accompany a streaming title. Common framings:

- "What captions and subtitle deliverables do we need for this release?"
- "Author SDH captions from this transcript."
- "Plan a multi-language subtitle workflow."
- "Wire audio description and sign-language interpretation into the package."
- "Audit existing captions for conformance to WCAG 2.2 and the WebVTT specification."

Out of scope: choosing renditions to encode (use the encoding-ladder-designer skill), packaging captions into the manifest (use the streaming-package-architect skill, which references this skill's deliverables), and dubbing direction (use a dubbing or localization skill if your library has one).

This skill treats accessibility as a first-class deliverable, not a post-release retrofit. It assumes the operator can run open-source caption tooling (WebVTT validators, IMSC/TTML conversion libraries, accessibility checkers — license tags collected in `## Sources reviewed`) and can route human review through trained captioners and descriptive-audio writers.

## How to apply

Follow the procedure in order. Where a step is not needed — for example, no sign-language deliverable is required — say so explicitly and continue.

1. Restate the title profile and the accessibility obligations. Total runtime, original language, target languages, regulatory regime (commercial captioning standards in the operator's jurisdictions, internal accessibility commitments, platform certification requirements), and the WCAG conformance level being targeted (default to WCAG 2.2 AA when not specified). Make the obligations explicit so reviewers can challenge them.

2. Enumerate the deliverable set. The full menu includes:
   - **Captions** in the original language for hearing audiences who prefer text (CC).
   - **SDH** in the original language for the deaf and hard of hearing — adds non-dialog sound cues and speaker identification.
   - **Subtitles** translated into target languages for hearing audiences (translation only).
   - **Subtitles for the deaf and hard of hearing** in target languages (translation plus SDH conventions).
   - **Forced narrative subtitles** for parts of the original-language audio that are foreign or unintelligible to the original-language audience.
   - **Audio description (AD)** in the original language for blind and low-vision audiences, often released in target languages too.
   - **Sign-language interpretation** as a picture-in-picture video track when policy or audience needs require it.
   - **Extended chapters** with descriptive markers for keyboard and assistive navigation.

   Pick the subset that the obligations require, name the others as not in scope, and call out any near-misses (for example, AD in English only when policy expected AD in two languages).

3. Decide verbatim versus edited captions. Verbatim transcribes everything the speaker says, including disfluencies. Edited cleans for readability while preserving meaning and intent. Default to verbatim for documentary and news, edited for fiction and educational content where reading speed matters. State the decision and the reading-speed budget that follows from it (commonly 17 to 20 characters per second for adult viewers, lower for children's content).

4. Pick the caption format per delivery channel. Streaming distribution today centers on three formats:
   - **WebVTT** — text-based, the de facto standard for HLS and the most common DASH option. Use for streaming-only deliverables.
   - **TTML / IMSC1** — XML-based, broadcast-grade, supports richer positioning and styling. Use when broadcast partners require it or when downstream conversion to other formats is anticipated.
   - **SRT** — interchange-only, no styling, no positioning. Accept as a source format and convert; do not ship SRT as the primary streaming deliverable.

   Specify the primary deliverable format and the conversions needed to satisfy each channel.

5. Author the SDH conventions. SDH is verbatim by default and adds:
   - Speaker identification at the start of each turn or when speaker changes are non-obvious (`[ANNA]`, `[NARRATOR]`).
   - Sound effect descriptions in brackets that name the sound source and quality (`[door slams]`, `[distant siren]`, not `[noise]`).
   - Music indication (`[melancholic piano]`) with lyrics on a separate cue when they carry meaning.
   - Off-screen and parenthetical dialog clearly indicated.
   - Tone descriptors only when not inferable from the visible performance (`[whispering]`, `[sarcastically]`).
   
   Forbid filler descriptors like `[indistinct]` when the source can be transcribed. State the SDH style guide for the title so multiple captioners produce consistent output.

6. Author the timing conventions. Caption cues should:
   - Appear at the moment the speech begins, not earlier, not noticeably later (within ±100 ms).
   - Remain on screen for at least 1.5 seconds (preferably 2 seconds) to be readable.
   - Not exceed 32 to 42 characters per line, depending on language and presentation context.
   - Use at most two lines per cue.
   - Break lines at clause boundaries, not mid-phrase, to support comprehension.
   - Avoid orphan single-word lines.
   
   Specify the reading-speed target (characters per second) and the maximum cue duration (typically 7 seconds).

7. Author the positioning metadata where meaningful. WebVTT and IMSC1 both support placement. Use it to:
   - Move a cue out of the way of burned-in titles, lower-thirds, and key on-screen text.
   - Reflect speaker direction when there is no other speaker cue.
   - Place forced narrative subtitles where the source text appears, when it preserves meaning.
   
   Avoid over-positioning that introduces inconsistency between cues. Document the default position and the exceptions.

8. Plan audio description. AD is a separate audio track that describes visual events between dialog. Decide:
   - **Standard AD** — descriptions fit between dialog lines without extending runtime.
   - **Extended AD** — pauses program audio to allow longer descriptions; rarely supported by streaming players today, used in linear broadcast.
   
   Specify the description style guide: describe what advances the plot, what is visually surprising, who is on screen and what they are doing; do not describe what is already announced by dialog. Voice the track in a register consistent with the program — same accent as the original, a single narrator for fiction, multiple narrators only when the program structure justifies it.

9. Plan sign-language interpretation. Sign-language interpretation requires:
   - A second video track containing the interpreter, framed waist-up against a contrasting background, lit so hand shapes are unambiguous.
   - Sign language matched to the audience's region (BSL for UK, ASL for US/Canada, Auslan for Australia, regional sign languages elsewhere). Do not assume a single global sign language.
   - Picture-in-picture rendering by the player, configurable in position and size, with a per-user toggle.
   - Synchronization to the program audio within a perceptual tolerance (typically ±100 ms).
   
   Sign-language interpretation is the most expensive accessibility deliverable. Recommend it only where policy requires or where the audience is large enough to justify the spend; otherwise scope SDH and AD only.

10. Plan multi-language workflow. For each target language:
    - Source the master transcript from the original language captioning. Localize the transcript first; caption-author second; do not translate finished cues, which embeds segmentation that does not survive translation.
    - Re-author cues against the localized text honoring the new reading-speed and line-length budgets, which differ by language (German tends to lengthen English source; Mandarin and Japanese tend to shorten; right-to-left languages mirror text alignment).
    - Maintain a translation memory so recurring proper nouns, technical terms, and franchise terminology stay consistent across episodes and seasons.
    - Match SDH conventions in the target locale's caption style — sound-effect description norms vary, and some markets prefer descriptive narration over bracketed cues.

11. Plan conformance checks for each format:
    - **WebVTT**: lexical conformance to the W3C WebVTT specification, cue overlap (forbidden by the spec on the same track), correct STYLE blocks, valid cue identifiers, correct timestamp form.
    - **IMSC1 / TTML**: schema validation against the IMSC1 text profile, region and style references resolve, no use of features outside IMSC1.
    - **SRT**: structural validity only; cue numbering monotonically increases, timestamps valid, no malformed lines.
    Run a syntactic validator on every produced file before the QC gate.

12. Plan the QC gate. Captions are not done when they are syntactically valid; they need editorial QC. The QC matrix should include:
    - Spot-check 10% of cues for transcription accuracy against the audio.
    - Read-through every cue for grammar, punctuation, and reading speed.
    - Watch the full program with captions on to verify timing, positioning, and SDH coverage of significant non-dialog audio.
    - Listen to the full audio description with the program video to verify the description does not collide with dialog and is informative without being intrusive.
    - Watch the sign-language track to verify framing, synchronization, and clarity.
    - Verify accessibility metadata in the manifest (CHARACTERISTICS attributes, LANGUAGE tags, FORCED flag where applicable, the DEFAULT and AUTOSELECT flags) match the deliverable inventory.

13. Specify the deliverable inventory and naming convention. For each language and each accessibility type, produce a file with a deterministic name (for example `episode-01.en.cc.vtt`, `episode-01.en.sdh.vtt`, `episode-01.es-419.sub.vtt`, `episode-01.en.ad.m4a`). Include a manifest entry indicating language, type, intended audience, and conformance level. Hand this inventory to the packaging step so the manifest references match the produced files.

14. Plan the publish gate. Captions must not ship if:
    - The syntactic validator returns errors.
    - The QC pass returned blocking notes (timing failures, transcription errors, missed sound cues that change meaning).
    - The manifest characteristics do not match the deliverable type.
    - The forced narrative cues are present in non-forced tracks (this confuses player auto-selection).
    
    State the gate explicitly so the pipeline can enforce it.

15. Plan post-release monitoring. Player telemetry should report on caption track selection rates, AD enablement rates, and errors fetching subtitle segments. A spike in caption-fetch errors usually means a packaging regression on a specific rendition group; a sudden drop in caption usage often means the DEFAULT or AUTOSELECT flag changed on publish.

16. Output the three artifacts: the deliverable inventory, the authoring guide, and the QC plan. Note the gaps for any deliverable type that is out of scope (a particular target language, AD in a particular market) so it cannot be quietly assumed.

## Inputs

- Title profile: runtime, genre, languages, dialog and sound design density.
- Audience requirements: regulatory regime, platform obligations, WCAG target, in-house commitments.
- Existing assets: transcripts, draft captions, descriptive audio, signed video.
- Timeline: release schedule and review windows.

## Outputs

- Deliverable inventory listing every accessibility file by language and type.
- Authoring guide with style conventions per deliverable.
- QC plan with syntactic, editorial, and manifest checks.

## Examples

**Six-episode documentary, English original, German and Spanish targets, WCAG 2.2 AA.** Deliverables: English CC verbatim WebVTT, English SDH verbatim WebVTT, German subtitle (translation) WebVTT, German SDH WebVTT, Spanish subtitle WebVTT, Spanish SDH WebVTT, English audio description AAC, German audio description AAC. No sign-language track. QC includes spot-check at 10% cues, full read-through, manifest characteristics audit.

**Children's animated series, English original, WCAG 2.2 AAA target.** Deliverables: English CC edited (lowered reading speed to 12 characters per second, line length capped at 32), English SDH edited, English audio description AAC with descriptive narration tuned to children's program style. Forced narrative subtitles where on-screen text is decorative (sign-painted credits, written notes), with FORCED=YES in the HLS manifest. Multi-language deferred; will be authored as licensing expands.

**Live news channel, English original, no time for editorial QC of each cue.** Deliverables: English real-time captions via human captioner with vocabulary feed, with auto-correction for proper nouns, in WebVTT served as live subtitle segments. SDH conventions enforced for sound cues but realism caveat is published in the brand's accessibility statement. AD not available live. Post-broadcast VOD asset re-authored with edited captions and AD.

## Limitations

- Caption transcription quality remains a human judgement call; automated transcripts require qualified-captioner editorial review for accessibility-grade deliverables.
- Audio description authoring is a craft skill; this skill produces a plan, not finished AD.
- Sign-language interpretation requires interpreters trained in the specific sign language; do not substitute machine translation.
- Some legacy players and devices implement WebVTT and TTML partially; final delivery must be validated on every device family in scope.
- Regulatory captioning rules vary by country and by content category; route final compliance through qualified review.

## Sources reviewed

- https://github.com/w3c/webvtt — WebVTT specification source (W3C Software and Document License).
- https://github.com/w3c/imsc — TTML Profiles for Internet Media Subtitles and Captions, IMSC family (W3C Software and Document License).
- https://github.com/sandflow/imscJS — JavaScript renderer for IMSC1 documents (BSD-2-Clause).
- https://github.com/sandflow/ttconv — subtitle format conversion library between TTML, IMSC, WebVTT, SRT, STL, SCC (BSD-2-Clause).
- https://github.com/vidstack/captions — modern captions parser and renderer supporting VTT, SRT, SSA (MIT).
- https://github.com/imshaikot/srt-webvtt — SRT to WebVTT conversion patterns (MIT).
- https://github.com/Netflix/vmaf — perceptual quality context for AD audio production gates (BSD-2-Clause-Patent).
