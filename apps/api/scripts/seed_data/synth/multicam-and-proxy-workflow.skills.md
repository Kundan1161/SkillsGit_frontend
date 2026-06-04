---
id: skillsgit-curated/multicam-and-proxy-workflow
version: 1.0.0
name: Multicam and Proxy Workflow Designer
description: Plan multicam sync (timecode, audio waveform, or slate), choose proxy resolution and codec per editor and project shape, draw a clean offline/online boundary, and lock in a conform discipline that survives finishing.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: creative
tags: [niche:video-editing-pipeline, multicam, proxy, sync, offline-online, conform, timecode, audio-sync]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 5500
trigger_keywords:
  - multicam sync
  - multicam editing
  - proxy workflow
  - proxy resolution
  - timecode sync
  - audio waveform sync
  - clapperboard sync
  - offline online
  - conform
  - relink media
  - proxy codec
  - genlock
example_invocations:
  - "Plan a multicam sync workflow for a four-camera concert recording."
  - "What proxy codec and resolution should we use for 6K Blackmagic raw on M-series laptops?"
  - "We are about to start a multicam interview series — design the sync and proxy plan."
  - "Our conform is failing on a multicam edit — help me redesign the offline/online boundary."
inputs:
  - name: shoot_configuration
    type: text
    required: true
    description: Camera count, sensor/format per camera, frame rate(s), and whether timecode was genlocked, jam-synced, free-running, or absent. Note any cameras started/stopped independently.
  - name: audio_capture
    type: text
    required: true
    description: How audio was captured (in-camera, external recorder, both), whether a slate was used, and any timecode link between audio recorder and cameras.
  - name: edit_environment
    type: text
    required: true
    description: Editor's primary application family (professional NLE, consumer mobile editor, programmatic), machine class (laptop, desktop, workstation), storage type, and bandwidth from storage to machine.
  - name: finishing_target
    type: text
    required: false
    description: Where finishing happens — local color/sound on the same project, external colorist, full finishing facility, or no separate finishing. Affects how strict the conform discipline must be.
  - name: project_volume
    type: text
    required: false
    description: Hours of source footage and number of multicam groups expected. Determines whether sync is a person-day, a person-week, or a person-month.
  - name: delivery_resolution
    type: text
    required: false
    description: Final delivered resolution and codec. Drives proxy ratio decisions; a final at 1080p tolerates more aggressive proxying than a final at 4K HDR.
outputs:
  - name: sync_plan
    type: markdown
    description: A method-by-method sync plan — primary method, fallback method, and the order in which clips are processed. Includes the rule for what "synced" means and where synced groups live.
  - name: proxy_spec
    type: markdown
    description: Proxy resolution, codec, scaling rules, file-naming pattern, generation tool/command-line sketch (vendor-neutral), and the storage location relative to source media.
  - name: offline_online_boundary
    type: markdown
    description: A written boundary that says what the editor does in offline, what is forbidden in offline, and what online inherits. Includes effects that survive, effects that need redoing, and the conform list.
  - name: conform_checklist
    type: markdown
    description: A pre-conform and post-conform checklist with frame-count verification, audio-channel verification, timecode verification, and a smoke test on a known-good clip.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Multicam and Proxy Workflow Designer

## When to use

Use this skill when a project needs synchronized multi-angle editing, when source media is too heavy to edit natively, or when a previous edit has fallen apart at the conform stage. Multicam sync and proxy management are two technical problems that share one root failure mode: a sloppy offline that the online cannot reproduce.

Trigger this skill when the input describes:

- Two or more cameras filming the same performance, interview, event, or scene.
- Source media in heavy codecs (raw, log-encoded camera codecs, high-bitrate intra-frame masters) that strain the editor's machine.
- A pipeline where the editor is not the finisher (separate colorist, separate sound, external online).
- Phrases like "multicam," "sync," "proxies," "offline edit," "relink," "conform," "online finishing," "media offline."

Do not trigger this skill when the user wants:

- A whole-pipeline design from ingest to delivery (use the video-editing-pipeline-architect skill).
- Guidance on cuts inside a multicam scene (use the cut-decision-methodology skill).
- A solo-cut, single-camera, native-codec edit — there is no multicam and no proxy problem to solve.

If the input is genuinely tiny — one camera, one short take, edited and finished on the same machine — say so and refuse to manufacture work.

## How to apply

Work through the steps in order. The output is concrete, not abstract — name the tools by capability and the targets by number.

### Step 1. Triage the sync evidence

Multicam sync has three primary methods, each with prerequisites. Determine in this order which one applies to each multicam group:

- **Timecode-based sync.** Available if cameras and audio recorder were genlocked, jam-synced from the same master, or running stable internal timecode for the day's shoot. Most accurate, fastest in the application, fragile if any camera drifted or was power-cycled mid-day. Verify by spot-checking timecode burn-in across cameras on a frame where all are pointed at the same action — if the readouts agree within a frame, trust it.
- **Audio-waveform sync.** Available if every camera captured at least scratch audio of the same acoustic environment as the master audio recorder, and the cameras were close enough that latency is sub-frame. Works well for interviews, panel events, and any tight grouping; degrades for cameras with very different distance to the sound source or markedly different microphones.
- **Slate-based sync.** Available if a clapperboard (analog or digital) was used at the head of each take with every camera rolling. Slowest, most manual, but the universal fallback. Requires the editor to find the clap frame on each camera and align audio.

For each multicam group, pick a primary method and an explicit fallback. Document which is which.

### Step 2. Define what "synced" means

A clip is "synced" only after these three checks pass:

- Sub-frame audio alignment confirmed by listening to both tracks together for at least ten seconds and hearing zero phasing or echo.
- Visual continuity confirmed by stepping to a moment of clear physical action (hand clap, mouth movement, slate) and watching the cameras roll together frame-for-frame.
- Sync verified at three points in the take: head, middle, tail. Long takes drift more than short ones; checking only the head misses the most common failure.

State this rule explicitly in the sync plan. The editor must not skip the tail check on long takes, no matter how good the head looked.

### Step 3. Handle frame-rate hazards before sync

Mixed frame rates are the single largest source of silent conform failure. Before any sync:

- Inventory each camera's recorded frame rate per take. Do not assume.
- Decide a project base rate — usually the timeline frame rate the deliverable demands — and decide how every other rate gets in (conformed, time-warped, or rejected).
- If any camera shot a different frame rate than expected (a common accident — 24 vs 23.976, or 30 vs 29.97), conform it explicitly during ingest, before sync. Name the tool and the target.
- If anything is high-frame-rate intentional (slow-motion captured at 60, 120, or 240), tag the clip as a time-warp source and exclude it from automatic multicam alignment; sync it manually as a single-cam insert.

### Step 4. Plan the proxy spec

Choose a proxy resolution, codec, and naming pattern that satisfies these constraints simultaneously:

- The editor's machine plays back at least four streams of proxy at the timeline frame rate without dropping frames. (For four-cam editing, this is the floor.)
- The proxy file footprint is at least four times smaller than the camera original, ideally ten times smaller.
- The proxy resolution and aspect ratio match the camera original's aspect ratio exactly. Squeezed or letterboxed proxies break framing decisions.
- The proxy embeds a watermark — version stamp, "PROXY" tag, timecode burn-in — if the proxy will leave the edit suite for review.

Reasonable starting points:

- **4K or 6K log/raw source.** 1/4 linear (1920x1080 or 1280x720), ProRes Proxy or DNxHR LB. Editor machine plays four streams comfortably on a midrange laptop.
- **HD intra-frame masters.** Optional — many machines play HD intra-frame masters natively. Make proxies if the storage round-trip is the bottleneck rather than the codec.
- **Very high-bitrate raw (8K, 12-bit linear).** 1/8 linear, the editor's preferred edit codec at a low bitrate. Don't be precious about quality — proxies are a tool, not a delivery.
- **Mobile-grade source for fast turnaround.** Skip the proxy entirely; cut native. The proxy plan is overhead the project may not need.

### Step 5. Define proxy generation timing and tooling

State explicitly:

- **When proxies are generated.** Best: during ingest, before the editor opens the project. Acceptable: overnight after each shoot day. Bad: on-demand mid-edit, which produces a partial-proxy library and a constant context switch.
- **Where proxies live.** A parallel folder tree mirroring the source media tree. Each proxy file has a deterministic path relative to its source; this is what relinking depends on.
- **How proxies are named.** Identical filename as the source, identical extension family, in a parallel `proxy/` tree — or identical base name with a `_prx` suffix, in the same tree. Most professional NLEs support either; pick one and never deviate.
- **Verification.** A simple count check after generation: source clip count equals proxy clip count. Any mismatch surfaces a failed generation that would otherwise show up as "media offline" mid-edit.

### Step 6. Draw the offline/online boundary

Write down what is permitted in offline and what is forbidden:

**Permitted in offline:**

- All cuts, in/out points, multicam angle switches.
- Speed changes at any ratio, as long as the source clip is the camera original (not a time-warp baked into a proxy).
- Audio level moves, pan moves, basic equalization for editorial monitoring.
- Basic color corrections for monitoring only — labeled as "viewing LUT" or "monitor color," not "final color."
- Temp graphics and temp music — labeled as temp, with the originals tracked.

**Forbidden in offline (or done with explicit awareness):**

- Final color decisions — the colorist will redo them and editor's monitor calibration is unreliable.
- Final audio mix moves below the level needed for review — the sound designer will redo them and the AAF only carries certain move types reliably.
- Effects bound to specific proxy resolutions (filters with hard-coded pixel-radius parameters). Use ratio-based effects.
- Edits inside a "flattened" multicam clip that the conform tool cannot decompose. Some applications collapse multicam edits into a single source-clip reference; the conform may need a "commit multicam edits" pass before turnover so all angles resolve.

### Step 7. Plan the relink path

Relinking from proxy to camera original is where bad pipelines reveal themselves. Specify:

- **The link identifier.** Most applications relink by filename; some use clip metadata or hash. Whichever the application uses, the proxy filename rule from Step 5 must satisfy it.
- **The relink test.** Before any creative editing begins, relink one bin from proxy to camera original, play three random clips at full quality, then relink back to proxy. If any clip goes offline, the proxy spec is broken — diagnose before continuing.
- **The conform copy.** Before relinking the working project to camera originals for turnover, duplicate the project file with a `_conform` suffix. The working project stays on proxy; the conform copy is the one that gets relinked, exported, and never edited again.

### Step 8. Plan the conform itself

Conform is the process of moving the locked offline edit onto camera-original media, verifying every cut, and producing the deliverable for finishing. The discipline:

- **Frame-count match.** The conformed timeline's total frame count must equal the offline's total frame count. A one-frame discrepancy somewhere means the conform broke.
- **Per-clip in/out match.** Spot-check at least ten random cuts: source clip name, source timecode in, source timecode out, duration. They must match between offline and conform.
- **Audio channel match.** The conformed timeline carries the same audio channel mapping as the offline. Stereo pairs stay stereo; mono dialog stays mono on the named track.
- **Effects survival.** Note which offline effects survive the conform and which need rebuilding. A typical loss list: third-party plug-ins, custom title styles, certain transition variants. Plan to rebuild on the conform copy, not the offline.
- **Reference render comparison.** Side-by-side the conform's render against the locked offline's render at three points: head, midpoint, tail. They should be visually identical apart from improved fidelity from camera originals.

### Step 9. Match the workflow to the finishing target

If finishing is a separate facility, the conform's output format is non-negotiable: it matches what the facility accepts. Common targets:

- An XML export with a path to the camera-original media tree.
- An AAF export for sound, with audio handles configured to the facility's spec (often one to two seconds).
- An EDL — limited but universal — for color where the timeline is straightforward and single-layer.

Ask which the facility wants if it isn't stated, and design the conform discipline around their requirements. The conform that "works for the editor" but breaks the facility is no conform at all.

### Step 10. Document the failure modes

Add a short, specific failure-mode list to the output, derived from the project's actual configuration. Examples:

- "Camera 3 free-running timecode drifted by two frames over the day — use audio waveform sync on takes after lunch."
- "Multicam angle 4 was started during the slate clap — find a secondary sync point inside the take."
- "Proxy generation skipped the audio-only recorder files — those sync to the timeline by waveform, not by file relink."
- "The final delivery is 4K HDR; the 1/4-resolution proxies suffice for editorial but the editor must spot-check graphics readability against the camera original before lock."

These notes are the reason this skill is more than a generic guide. The user's specific shoot has specific traps; name them.

## Inputs

- `shoot_configuration` (required): cameras, formats, frame rates, timecode discipline.
- `audio_capture` (required): how audio was recorded and synced to picture.
- `edit_environment` (required): editor's application family, machine, storage.
- `finishing_target` (optional): where color and sound happen.
- `project_volume` (optional): hours of source and number of multicam groups.
- `delivery_resolution` (optional): final delivered resolution and codec.

## Outputs

- `sync_plan`: primary method, fallback, processing order, sync definition.
- `proxy_spec`: resolution, codec, naming, location, generation timing.
- `offline_online_boundary`: permitted vs forbidden in offline, with rationale.
- `conform_checklist`: pre- and post-conform verification steps.

## Examples

### Example 1 — four-camera concert recording, no timecode

Input: "Four-camera concert. Three on the band, one wide. Two cameras are professional mirrorless bodies; two are compact action cameras. No genlock, no jam-sync, no clapperboard. Master audio recorded on a multitrack desk feed; each camera also has scratch audio from its on-board mic. Editor is on a laptop, finishing is local. Final delivers at 1080p H.264."

Sync plan: audio-waveform sync against the master multitrack mix is primary for all cameras, since every camera has scratch audio of the same acoustic environment. Fallback is visual-cue sync at a distinct moment (a drum hit visible on all four angles, for example). "Synced" means three-point verification head, mid, tail. Document that the wide camera will likely show audio latency of two to three frames from speaker distance — pre-roll it by the measured offset before fine-sync.

Proxy spec: source is HD or 4K from the mirrorless bodies and 4K from the action cameras. Generate 1/2-resolution proxies in the editor's preferred lightweight intermediate, named `<source-stem>_prx.<ext>` in a parallel `proxy/` tree. Editor's laptop plays four streams at this ratio comfortably.

Offline/online boundary: permitted to cut and switch angles freely; permitted to do basic level moves; forbidden to do "auto color match" between cameras because the colorist will redo it; forbidden to bake in zooms inside multicam — set zooms on the post-multicam output clip so the conform sees them once.

Conform checklist: total frame count match; spot-check ten cuts; verify audio is conformed from the multitrack master, not from a camera's scratch track; reference render comparison.

### Example 2 — two-camera documentary interview, professional bodies, timecode-locked

Input: "Two-camera documentary interview, both cameras professional bodies jam-synced at the top of each day, separate audio recorder timecode-linked. Source is 4K log codec, 23.976. Eight interviews, 60–90 minutes each. Editor on a workstation. Going to an external colorist and external sound designer. Final delivery 4K Rec.709."

Sync plan: timecode-based, primary. Fallback to audio waveform if any take shows a one-or-more-frame timecode discrepancy on spot-check. "Synced" verification at head, mid, tail of every interview — long takes will drift more, and the sound designer will see it before you do.

Proxy spec: 1/4-resolution ProRes Proxy, parallel folder tree, generated during ingest by the assistant. Editor's workstation can technically play the camera original, but 1/4 proxies cut the storage round-trip and leave headroom for graphics work.

Offline/online boundary: as above; specifically forbid baking in window-shape vignettes during offline because the colorist will redo them in a higher color space. Permit "ISO" multicam cuts (single-angle hero takes pulled out and edited as single-cam) but require the multicam group to remain intact in the bin in case the editor wants to recut.

Conform checklist: AAF for sound with two-second handles per the sound designer's spec; XML for color with the camera-original path; frame-count match; three-point reference render comparison at full 4K Rec.709 rendered from the conform copy on camera originals.

## Limitations

- The skill does not detect sync drift automatically — it specifies the discipline that catches it, but the editor or assistant performs the checks.
- Proxy codec recommendations are rules of thumb at the time of writing. Application defaults shift; whenever the application offers a "create proxies" preset, evaluate it against the constraints in Step 4 before accepting.
- Conform support for advanced effects (warps, stabilizations, third-party plug-ins) varies wildly by application and facility. Treat the failure-mode list as a starting point; consult the finishing facility for the authoritative survival list.
- Multicam grouping that mixes radically different sensor formats (anamorphic with spherical, 4:3 with 16:9, 24p with 50p) is fundamentally a creative-and-technical problem; the skill flags it, but the resolution is a decision the producer and editor must make together.
- High-end finishing pipelines (DCP, IMF, HDR mastering) introduce extra conform steps beyond this skill's scope. The skill produces the editorial-side conform; the finishing facility produces the deliverable-side conform.
- The skill cannot substitute for a sync test before principal photography. If timecode chain reliability matters, test it on day zero, not during the edit.

## Sources reviewed

The methodology synthesized here was informed by surveying public open-source video editor repositories, post-production methodology articles, and workflow documentation from the editorial community. No content from any source was copied; all prose above is original. Trademarked product names are confined to URL citations and do not appear in the body.

- https://github.com/KDE/kdenlive (GPL-3.0)
- https://github.com/mltframework/shotcut (GPL-3.0)
- https://github.com/olive-editor/olive (GPL-3.0)
- https://github.com/OpenShot/openshot-qt (GPL-3.0)
- https://github.com/mifi/editly (MIT)
- https://blog.frame.io/2024/07/29/updated-guide-premiere-pro-proxies-and-proxy-workflows/ (commercial documentation, read-only)
- https://elements.tv/blog/everything-you-need-to-know-about-the-proxy-workflow-in-davinci-resolve/ (commercial documentation, read-only)
- https://workflow.frame.io/guide/common-conform-issues (commercial documentation, read-only)
- https://postperspective.com/xml-aaf-edl-wtf/ (editorial article, read-only)
