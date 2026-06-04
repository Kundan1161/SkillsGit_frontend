---
id: skillsgit-curated/video-editing-pipeline-architect
version: 1.0.0
name: Video Editing Pipeline Architect
description: Design an end-to-end editorial pipeline — ingest, proxy creation, footage organization, multicam sync, edit-decision discipline, picture lock, and handoffs to color, sound, and online finishing.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: creative
tags: [niche:video-editing-pipeline, post-production, proxy, ingest, picture-lock, handoff, conform, render-queue]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6500
trigger_keywords:
  - video editing pipeline
  - post-production workflow
  - proxy workflow
  - ingest workflow
  - picture lock
  - editorial pipeline
  - conform
  - online finishing
  - render queue
  - footage organization
  - offline online editing
  - turnover
example_invocations:
  - "Design a post-production pipeline for a 6-camera documentary with 40 hours of footage."
  - "We are shooting a 3-week corporate brand piece — plan the editorial workflow end to end."
  - "Our edits keep falling apart at finishing. Help me set up a pipeline with proper proxies and conform."
  - "Set up a turnover-ready editorial workflow for a short narrative film."
inputs:
  - name: project_shape
    type: text
    required: true
    description: What is being cut and roughly how long the final piece will be. Include format (doc, narrative, branded, corporate, music video), final delivery duration, and broad story shape if known.
  - name: source_footage_profile
    type: text
    required: true
    description: Camera count, codec(s), resolution and frame rate, approximate total hours, and any audio recorders feeding the edit. Note multi-frame-rate or mixed-camera shoots explicitly.
  - name: team_composition
    type: text
    required: false
    description: Who is on the project — picture editor(s), assistant editor(s), colorist, sound designer, online editor, producer. One-person bands and full crews need different pipelines.
  - name: delivery_targets
    type: text
    required: false
    description: Where the final cut goes — theatrical, broadcast, streaming platform, web, social, internal. Each implies different finishing specs and downstream handoffs.
  - name: schedule_window
    type: text
    required: false
    description: Time from first ingest to final delivery, including any external deadlines (test screening, client review, festival, broadcast slot).
  - name: storage_and_collaboration
    type: text
    required: false
    description: Storage topology (local SSD, NAS, cloud sync, shared SAN) and whether multiple editors will touch the project concurrently or sequentially.
  - name: known_constraints
    type: text
    required: false
    description: Hard limits — locked finishing facility, fixed colorist, executive-producer review cycle cadence, a remote editor on bad bandwidth, etc.
outputs:
  - name: pipeline_plan
    type: markdown
    description: A staged plan from ingest through delivery, with named stages, gates, and responsibilities. Includes proxy strategy, organization standards, sync method, version discipline, and handoff packages.
  - name: folder_and_naming_spec
    type: markdown
    description: A folder structure and naming convention for the project — source media, proxies, project files, exports, deliverables — with examples a junior assistant can follow.
  - name: handoff_packets
    type: markdown
    description: A checklist for each handoff package — picture-to-color, picture-to-sound, picture-to-online — with required artifacts, frame counts, reference media, and a sign-off block.
  - name: risk_register
    type: markdown
    description: A short list of likely failure modes for this specific project and the mitigations baked into the pipeline.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Video Editing Pipeline Architect

## When to use

Use this skill when a project needs an editorial pipeline designed before footage starts piling up, or when an in-flight edit is failing because the pipeline was never designed in the first place. A good pipeline removes most of the panic from post-production. A missing pipeline produces the familiar pattern: the edit looks great on the editor's local machine, then breaks on every handoff downstream.

Trigger this skill when the input describes:

- A new project ramping up with significant footage volume (more than one shoot day, more than one camera, or non-standard formats).
- A team larger than one editor, with hand-offs to colorists, sound designers, or finishing facilities.
- An in-progress edit where versions are getting lost, links are breaking, or the colorist is rejecting turnovers.
- Phrases like "post-production workflow," "editorial pipeline," "ingest plan," "proxy strategy," "turnover," "conform," "online," "picture lock."

Do not trigger this skill when the user wants:

- The mechanics of syncing specific multicam clips or generating proxies for a single delivery (use the multicam-and-proxy-workflow skill).
- Guidance on which cuts to make inside a scene (use the cut-decision-methodology skill).
- The handoff package contents for sound only (use the sound-design-handoff-architect skill).
- A render farm setup or codec/bitrate selection for distribution (these are downstream of the pipeline; reference but don't replace).

If the input describes a one-shot, one-camera, one-editor project under ten minutes of footage, the pipeline can be three folders and a backup — say so plainly and refuse to over-engineer.

## How to apply

Move through the steps in order. The pipeline plan should read like a production document, not an essay — concrete, named stages, named owners, named files.

### Step 1. Classify the project shape

Pull four facts out of the input before designing anything: total source-footage hours, camera count, editor count, and handoff count (color, sound, online, graphics, VFX — each is one handoff). These four numbers drive every decision below.

Sketch one of three pipeline archetypes and tell the user which one applies:

- **Solo cut.** One editor, one to two handoffs, under twenty hours of source. The pipeline is lean — five folders, named exports, a single proxy resolution, one render queue.
- **Small-team episodic / branded.** Two to four collaborators, three to five handoffs, twenty to two hundred hours of source. Needs explicit version discipline, shared storage rules, and turnover packets.
- **Long-form documentary or narrative.** Multi-month, four-plus collaborators, hundreds of hours, several handoffs, often a finishing facility. Needs an assistant-editor role explicitly, a string-out and selects discipline, and a conform plan from day one.

If the input is ambiguous, ask a single question to disambiguate, then proceed.

### Step 2. Design the ingest stage

Ingest is the gate that catches most downstream pain. Specify these explicitly:

- **Verified copy procedure.** Card to two destinations, checksum-verified, before any card is wiped. Name the checksum approach (xxhash or md5 are common); never trust drag-and-drop alone.
- **Camera card folder convention.** Preserve the camera's native folder structure inside the verified copy — do not let the editor reach into the original card structure during editing. Original card trees are the backup of last resort.
- **Per-day card report.** A short text file per shoot day listing card IDs, camera, scenes or topics, audio recorder, frame rate, codec, and any notes from the DIT or shooter. This is the document that saves the project when a clip turns up that nobody recognizes.
- **Audio ingest.** If audio is recorded on a separate device, ingest it next to the matching video day in the same hierarchy. Don't separate audio and video by media type at this stage — separation by shoot day is the right cut.

### Step 3. Choose the proxy strategy

The proxy is the working copy the editor cuts with; the camera original is what finishes. Specify three things:

- **Proxy resolution and codec.** Pick the smallest comfortable working resolution and a codec the editor's machine decodes cheaply. Common choices: 1/4-resolution ProRes Proxy or DNxHR LB at 1280x720 for 4K sources; or H.264 at 5–10 Mbps if storage is the constraint and the editor's CPU can take it. Lock the choice in writing.
- **Proxy generation timing.** Either at ingest (preferred for documentary and any multi-editor project) or on-demand (acceptable for solo cuts). Generating at ingest costs hours but produces a clean library; on-demand spreads the cost but creates "where is the proxy for clip X" gaps.
- **Proxy storage location.** Local fast storage for the editor; original camera media on slower archival storage. The pipeline document must say which is which, where they live, and which gets backed up.

Include a one-line rule: the editor never edits against camera originals during the offline. That rule prevents most conform disasters.

### Step 4. Design the organization layer

After ingest and proxy generation, organize the media for editing. The discipline here is consistent labeling, not aesthetic perfection.

- **Bin or folder taxonomy.** Group by source (camera card, day, interview subject) at the bottom layer; group by story or scene at the top layer. Don't try to nest more than three deep.
- **Naming convention.** Lock a clip-naming scheme that survives across applications. A useful pattern: `YYMMDD_<cam>_<scene>_<take>_<descriptor>`. Keep it ASCII, no spaces, no punctuation that varies between operating systems.
- **String-outs and selects.** For documentary, plan for a "string-out" pass — every relevant clip in source-time order, before story structure — and a "selects" pass — the keepers, organized by theme or character. Both pay for themselves once a story shape emerges and you need to know what coverage you have.
- **Markers and tagging.** Define one or two marker types that survive export (color = story-beat candidate, color = problem, etc.) and forbid the rest. Marker proliferation is a leading indicator of an editor losing the thread.

### Step 5. Plan the sync stage

If audio was recorded separately, or multiple cameras need to be cut as a single performance, sync is its own stage with its own discipline. Defer the mechanics to the multicam-and-proxy-workflow skill — but in the pipeline plan, name the sync method, name when it happens (before or after proxy?), and name who is responsible.

Specify the "post-sync hygiene" rule: once a take is synced, the synced version is the canonical version. Editors do not re-sync; they pull from the synced bin.

### Step 6. Establish version discipline

Versioning is the single biggest discriminator between a pipeline that holds and one that collapses. Specify all of these:

- **Project file naming.** A version stamp in the filename — `Project_v014_2026-05-14.<ext>` — incremented on every save-as. The most recent version is the one the editor is touching; older versions are read-only safety nets.
- **Save-as cadence.** A new version at the start of each working session and after any structurally significant change (locking a scene, deleting a sequence, rebuilding the timeline). Trivial saves accumulate within a version; meaningful saves bump it.
- **Backup target.** Auto-backups to a second location, with a daily snapshot retained for the life of the project plus thirty days.
- **One "master" sequence per cut tier.** A single "Latest" or "Cutting" sequence is the working timeline; named milestone sequences ("Assembly," "Rough Cut," "Fine Cut," "Picture Lock") are immutable checkpoints. Editors copy a milestone to a new working sequence; they don't edit on the milestone itself.

### Step 7. Define the cut tiers and their gates

A pipeline needs explicit gates so reviewers and editors know what they are looking at. Use this five-tier sequence and adjust to project scale:

- **Assembly.** All selects in order, no pacing decisions. Watchable end-to-end. Gate: "do we have a movie in here?"
- **Rough cut.** Story shape, scenes in order, rough timing, no fine work. Gate: "is the story working?"
- **Fine cut.** Pacing tuned, scenes optimized, music sketched in, b-roll in place. Gate: "does it play?"
- **Picture lock.** No further timing changes. Frame counts frozen. Gate: "are we sure?" — followed by a 48-hour cooling period before turnovers ship.
- **Online / finishing.** Color, sound, graphics, online edit, deliverables.

Document who signs off on each gate and how. Without named sign-off, picture lock keeps slipping.

### Step 8. Plan the handoffs

For each handoff downstream of picture lock, specify the deliverable package. The standard packages:

- **Picture-to-color.** A reference render (typically a Quicktime with burned-in timecode and reel/version), the conformed timeline as XML or AAF, the camera-original media list, and a notes document on intended look and any tricky shots.
- **Picture-to-sound.** A reference render with timecode burn-in and a stereo guide mix, an AAF (modern) or OMF (legacy) export with audio handles of at least one second, a track-layout document, and notes on intended music placement and any temp tracks that need licensing-aware replacement.
- **Picture-to-online.** The final approved timeline as XML/AAF/EDL, the camera-original location, reference renders, a delivery-spec document (frame rate, resolution, color space, codec, audio configuration), and a list of any picture changes since the locked turnover (there should be none — but document it if there are).
- **Picture-to-graphics or VFX.** A shot list with in/out timecodes, plate exports, reference renders, and frame-accurate handles.

Specify a 24-hour pause between sending a turnover and answering questions, so the receiving department has time to ingest and review before the conversation starts. Picture editors are often the bottleneck in turnover Q&A; the pause prevents context-switch thrash.

### Step 9. Design the render queue

A render queue is not a build script; it's a discipline. Specify:

- **Render farm or local.** If local, name the working hours during which renders run (overnight is usually right). If a render farm or shared machine is available, name how jobs are queued and prioritized.
- **Reference render naming.** `<project>_<cut-tier>_v<version>_<date>.mov` is enough. Burn-in: timecode + version + watermark.
- **Deliverable render naming.** Match the delivery spec exactly. Many platforms will reject files based on filename alone.
- **Render verification.** Spot-check the head, tail, and one random middle frame of every reference render. Catches the broken-effect-on-frame-7421 problem before it ships.

### Step 10. Write the risk register

For the specific project, list four to six likely failure modes and the pipeline element that mitigates each. Examples:

- "Card wiped before checksum verified" — mitigated by Step 2 procedure.
- "Editor cuts against camera originals on day one" — mitigated by Step 3 storage rule.
- "Picture lock slips because of late notes" — mitigated by Step 7 sign-off discipline.
- "Conform breaks because of mixed frame rates" — mitigated by Step 1 classification surfacing the issue early.
- "Music license issue surfaces after lock" — mitigated by Step 8 sound turnover notes.

The register is the document the producer reads. Keep it short and direct.

### Step 11. Calibrate to the team's actual constraints

Re-read the user's `team_composition` and `known_constraints` inputs and shave the pipeline accordingly. A one-person band doesn't need a turnover packet template; they need a "future-me handoff" version of the same idea. A remote editor on bad bandwidth needs cloud-aware proxy resolutions and an explicit upload cadence. A locked finishing facility needs the conform format that facility prefers, not a vendor-neutral one.

A pipeline that ignores team realities is decoration. A pipeline calibrated to team realities is infrastructure.

## Inputs

- `project_shape` (required): what is being cut and how long the final piece is.
- `source_footage_profile` (required): cameras, codec, hours, audio sources.
- `team_composition` (optional): who is involved, including assistants and downstream specialists.
- `delivery_targets` (optional): where the cut goes after finishing.
- `schedule_window` (optional): time from ingest to delivery.
- `storage_and_collaboration` (optional): storage topology and concurrency model.
- `known_constraints` (optional): fixed facilities, fixed people, hard deadlines, bandwidth limits.

## Outputs

- `pipeline_plan`: the staged plan from ingest through delivery.
- `folder_and_naming_spec`: a concrete structure and naming convention an assistant can apply.
- `handoff_packets`: a per-handoff checklist with required artifacts and sign-off.
- `risk_register`: project-specific failure modes and their mitigations.

## Examples

### Example 1 — fifteen-minute documentary, two-month schedule

Input: "A fifteen-minute documentary on a community garden. Six interviews shot 4K on two cameras, approximately twelve hours of interview footage, eight hours of b-roll across four shoot days. Audio recorded on a separate device with lavs and a boom. One editor, one assistant for two days a week, going to an external colorist and an external sound designer. Final delivery to a streaming platform and a festival cut."

Pipeline shape: small-team episodic. The plan would specify a verified ingest with per-day card reports, 1/4-resolution ProRes Proxy generated at ingest by the assistant, a bin taxonomy organized by subject for interviews and by location for b-roll, audio sync performed by the assistant on day two using waveform matching for any non-timecoded takes, a string-out per interview before the editor starts story work, save-as cadence per editing session, and named milestone sequences for assembly, rough cut, fine cut, and lock. The picture-to-color packet would include a Rec.709 reference render with timecode burn-in, the timeline as XML, and a notes document on the intended naturalistic look. The picture-to-sound packet would include the same reference render, an AAF with one-second handles, and a notes document on the temp music ("looking for a guitar-and-strings cue, similar mood, will license original"). The risk register would flag mixed frame rates between the two cameras (one shot 23.976, one shot 24 by accident) as the most likely conform failure, with a mitigation: pre-flight every camera card during ingest, log the frame rate in the card report, and conform-test a single day's worth of footage end-to-end before the editor starts.

### Example 2 — one-person branded social piece, two-week schedule

Input: "A 90-second brand piece for an apparel client, shot on one camera, two-hour shoot, edited solo, going to one round of client review then web."

Pipeline shape: solo cut. The plan would be five folders (`source`, `proxy`, `project`, `audio`, `delivery`), no proxy step (the original codec edits fine on the editor's machine — but state that explicitly so the choice is intentional), a single milestone sequence at fine cut and at delivery, a save-as on each working session, one handoff to the client (a watermarked reference render with version and timecode), and a single delivery package with web specs. The risk register would have two entries: "client asks for changes after delivery — keep the project archive complete for sixty days" and "color drift between editor monitor and client laptop — include a one-line color spec in the delivery note."

## Limitations

- The pipeline produced here is a plan, not a project file. The editor still has to set up bins, conform settings, and render presets in their chosen application.
- The skill cannot select between specific professional editors or finishing applications. It deliberately describes pipelines in vendor-neutral terms; the team's existing tooling and the finishing facility's preferences should drive that choice.
- High-end finishing pipelines (DCP creation, IMF packages, HDR mastering) need specialist input from the finishing facility. The plan should name the facility's contact and defer specs to them, not invent them.
- Streaming-platform delivery specs change frequently. The pipeline names the delivery target; the producer fetches the current spec from the platform's documentation at delivery time.
- Pipelines for live-event or news cuts (same-day turnaround) compress most of these steps drastically. The skill can adapt, but flag the speed/safety trade-off explicitly when it does.
- The skill does not address rights management, music licensing, or talent clearances directly — those are upstream of editorial and need their own discipline.

## Sources reviewed

The methodology synthesized here was informed by surveying public open-source video editor repositories, post-production methodology articles, and editorial workflow documentation. No content from any source was copied; all prose above is original. Trademarked product names are confined to URL citations and do not appear in the body.

- https://github.com/KDE/kdenlive (GPL-3.0)
- https://github.com/mltframework/shotcut (GPL-3.0)
- https://github.com/OpenShot/openshot-qt (GPL-3.0)
- https://github.com/olive-editor/olive (GPL-3.0)
- https://github.com/Zulko/moviepy (MIT)
- https://github.com/mifi/editly (MIT)
- https://workflow.frame.io/guide/common-conform-issues (commercial documentation, read-only)
- https://blog.frame.io/2018/12/10/offline-online-workflow-pitfalls/ (commercial documentation, read-only)
- https://soundgirls.org/post-production-basics-what-is-an-omf-or-aaf-and-why-does-it-matter/ (editorial article, read-only)
