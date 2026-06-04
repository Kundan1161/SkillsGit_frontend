# Wave-7 Synthesis Report — Video Editing Pipeline

Niche: **creative — video editing pipeline (multicam, proxies, edit decisions, cuts, transitions, sound design integration)**

## Skills produced

All under `D:\skillsgit\apps\api\scripts\seed_data\synth\`:

1. `video-editing-pipeline-architect.skills.md` — end-to-end editorial pipeline design (ingest, proxy strategy, organization, sync stage placement, version discipline, picture-lock gates, handoff packets, render queue, risk register).
2. `multicam-and-proxy-workflow.skills.md` — multicam sync (timecode / audio waveform / slate fallbacks), proxy resolution and codec selection per project, offline/online boundary, conform checklist.
3. `cut-decision-methodology.skills.md` — narrative editing methodology (scene job, coverage audit, geometry/180-degree axis, pacing curve, motivated cuts, J/L cuts, b-roll discipline, match cuts, montage structure, continuity audit, alternative passes).
4. `sound-design-handoff-architect.skills.md` — picture-to-sound handoff (lock verification, AAF/OMF/XML choice, track layout, audio handles, room tone, ADR candidate list, temp-music documentation, reference render, turnover letter, change-list discipline).

All four use:
- `license_type: free`, no pricing values.
- `category: creative`, first tag `niche:video-editing-pipeline`, 4-7 additional tags.
- Required `## When to use` and `## How to apply` (numbered steps); recommended `## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources reviewed`.
- Body length within 250-400 line target.

## Sources reviewed across the suite (license-tagged)

Open-source repositories (read for methodology, no content copied):
- `https://github.com/KDE/kdenlive` (GPL-3.0) — full-featured open-source NLE, multi-track architecture, proxy generation, MLT-based clip handling.
- `https://github.com/mltframework/shotcut` (GPL-3.0) — cross-platform NLE, native timeline editing, hardware decoding.
- `https://github.com/OpenShot/openshot-qt` (GPL-3.0) — open-source NLE with EDL/XML import-export; libopenshot LGPL.
- `https://github.com/olive-editor/olive` (GPL-3.0) — node-graph non-linear editor, ~9k stars.
- `https://github.com/Zulko/moviepy` (MIT) — Python video-editing library, declarative composition.
- `https://github.com/mifi/editly` (MIT) — declarative Node.js CLI / API video editor on top of FFmpeg.

Editorial / industry methodology sources (read-only, free web articles, no copying):
- `https://workflow.frame.io/guide/common-conform-issues` — conform pitfalls.
- `https://blog.frame.io/2018/12/10/offline-online-workflow-pitfalls/` — offline-online discipline.
- `https://blog.frame.io/2024/07/29/updated-guide-premiere-pro-proxies-and-proxy-workflows/` — proxy resolution/codec heuristics.
- `https://elements.tv/blog/everything-you-need-to-know-about-the-proxy-workflow-in-davinci-resolve/` — proxy storage topology.
- `https://postperspective.com/xml-aaf-edl-wtf/` — format trade-offs across XML/AAF/EDL/OMF.
- `https://soundgirls.org/post-production-basics-what-is-an-omf-or-aaf-and-why-does-it-matter/` — picture-to-sound handoff fundamentals.
- `https://apriltucker.com/omf-aaf-audio/` and `https://apriltucker.com/dialog-editing-part-5/` — dialog-edit prep.
- `https://www.forte-ai.com/blog/aaf-guide-for-audio-post-production` — AAF metadata structure.
- `https://www.production-expert.com/production-expert-1/aaf-and-omfs-post-audio-expert-panel-on-the-good-the-bad-and-the-ugly` — handoff failure modes.
- `https://www.studiobinder.com/blog/what-is-a-film-cut-definition/`, `https://www.premiumbeat.com/blog/8-essential-cuts-every-editor-should-know/`, `https://www.filmsupply.com/articles/film-editing-cuts/`, `https://www.adobe.com/creativecloud/video/post-production/cuts-in-film.html` — cut taxonomy and pacing craft.

All open-source repos cited above are GPL-3.0 or MIT. GPL repos were read for methodology only under wave-4+ "methodology recovery" doctrine, with no code or prose copying and license tagged in citations. No AGPL, no CC-BY-SA, no source-available licenses cited in this batch — all reviewed sources are either permissive or copyleft-as-used-by-readers-only.

## Trademark discipline

Trademarked product names (the four dominant commercial NLEs and the two major commercial DAWs) appear nowhere in the skill bodies. The body content uses generic terminology — "professional NLE," "picture-edit application," "sound designer's DAW," "consumer mobile editor," "finishing facility." Trademarked names from external articles only surface as URL fragments inside `## Sources reviewed` citations, where transparency to the buyer is the priority.

## Patterns synthesized across sources

1. **Verified ingest is the load-bearing first stage.** Every credible methodology source describes checksum-verified copying with a two-destination rule before any card is wiped. Open-source NLE projects assume the editor has done this; pro post-production sources insist on it explicitly.
2. **Proxy generation timing is a fork in the pipeline.** At-ingest produces clean libraries at the cost of front-loaded time; on-demand spreads cost but produces gaps. The right answer depends on team size and editor count — solo cuts can run on-demand; team cuts cannot.
3. **The offline/online boundary is rarely written down but always present.** Sources describe the same set of "what survives conform vs what doesn't" without naming it as a boundary; the skill makes the boundary explicit because un-named boundaries are where pipelines fail.
4. **Multicam sync has three primary methods (timecode, waveform, slate) and the best workflows always document a fallback.** Timecode is fastest, audio-waveform is most universal in modern post, slate is the universal last resort.
5. **The picture-to-sound handoff is dominated by AAF in 2026, with OMF as legacy.** AAF's multichannel and metadata support are the structural reasons. Handle length, track layout, and a turnover letter together prevent the "forensic archaeology" failure mode.
6. **Cut craft has a deep, well-articulated taxonomy** (cut on action / look / line / beat / motivated sound; J-cuts and L-cuts; match cuts; continuity rules including the 180-degree axis and screen direction). The methodology is well-established; the synthesis is in scaffolding scene-by-scene application rather than reciting the taxonomy.
7. **Picture lock + cooling period + change-list discipline** is the recurring pattern that survives across every credible source for how to manage post-lock changes without re-mix disasters.

## Efficiency

Used 8 WebSearch calls, 0 WebFetch calls — well under the 15-call budget. No tool needed for code-repo deep reads since methodology was the goal, not implementation specifics.

## Confidence

**High** on the editorial methodology content. The patterns are widely documented, well-converged across sources, and reflect long-standing post-production practice. The skill bodies translate well-understood craft into structured AI-agent instructions without claiming proprietary insight.

**Medium** on the proxy codec specifics. Codec landscape shifts faster than methodology; the skill uses rule-of-thumb starting points and instructs the user to verify against the current state of their application, which is the honest framing.

**Medium-high** on the cut-decision methodology, with one caveat: cut craft has a strong cultural slant toward Western narrative film grammar. The skill flags this in `## Limitations` and invites the user to override conventions when working in other traditions.
