# Synthesis Report — Video Encoding & Delivery Pipelines

**Wave:** 7
**Niche:** creative — video encoding & delivery pipelines (FFmpeg-driven encoding ladders, ABR, HLS/DASH packaging, codec selection, captions, accessibility)
**Date:** 2026-05-14

## Skills produced

1. `video-encoding-ladder-designer.skills.md` — design an ABR encoding ladder (codec mix, per-title vs per-shot strategy, VMAF-driven quality target).
2. `streaming-package-architect.skills.md` — package an encoded ladder for HLS, DASH, or unified CMAF delivery (segment shape, DRM scaffolding, SCTE-35 ad markers, multi-track audio and captions).
3. `captions-and-accessibility-deliverable-pipeline.skills.md` — produce captions, SDH, audio description, sign-language, and multi-language deliverables conformant to WebVTT and IMSC1.
4. `live-streaming-stack-architect.skills.md` — design an end-to-end live stack (contribution, transcode, package, CDN, player) with a latency budget and resilience plan.

All four set `license_type: free`, `category: creative`, first tag `niche:video-encoding-delivery`, body sections 250–400 lines each, 100% original prose.

## Sources reviewed and license classification

| Source | URL | License | Read posture |
|---|---|---|---|
| FFmpeg | https://github.com/FFmpeg/FFmpeg | LGPL-2.1+ / GPL-2+ (build-dependent) | Wave-4 methodology recovery — read, cited, no prose or code reused |
| VMAF (Netflix) | https://github.com/Netflix/vmaf | BSD-2-Clause-Patent | Allowlisted (BSD); cited as quality criterion |
| SVT-AV1 | https://gitlab.com/AOMediaCodec/SVT-AV1 | BSD-3-Clause Clear + AOM Patent License | Allowlisted (BSD); cited as codec |
| Shaka Packager | https://github.com/shaka-project/shaka-packager | BSD-3-Clause | Allowlisted (BSD); cited as packager |
| Bento4 | https://github.com/axiomatic-systems/Bento4 | GPL-2.0 (commercial alternative) | Wave-4 methodology recovery — read, cited |
| GPAC | https://github.com/gpac/gpac | LGPL-2.1 (commercial alternative) | Wave-4 methodology recovery — read, cited |
| OvenMediaEngine | https://github.com/AirenSoft/OvenMediaEngine | AGPL-3.0 | Wave-4 methodology recovery — read for LL-HLS patterns, cited, no code reused |
| OvenPlayer | https://github.com/AirenSoft/OvenPlayer | AGPL-3.0 | Wave-4 methodology recovery — read for player buffer behavior, cited |
| HLS.js | https://github.com/video-dev/hls.js | Apache-2.0 | Allowlisted; cited for HLS manifest quirks |
| SRT (Haivision) | https://github.com/Haivision/srt | MPL-2.0 | Wave-4 methodology recovery — read, cited |
| WebVTT (W3C) | https://github.com/w3c/webvtt | W3C Software and Document License | Cited as spec source |
| IMSC (W3C) | https://github.com/w3c/imsc | W3C Software and Document License | Cited as spec source |
| imscJS | https://github.com/sandflow/imscJS | BSD-2-Clause | Allowlisted; cited |
| ttconv | https://github.com/sandflow/ttconv | BSD-2-Clause | Allowlisted; cited |
| vidstack/captions | https://github.com/vidstack/captions | MIT | Allowlisted; cited |
| srt-webvtt | https://github.com/imshaikot/srt-webvtt | MIT | Allowlisted; cited |
| ABR-video-transcode (Xilinx) | https://github.com/Xilinx/ABR-video-transcode | Apache-2.0 | Allowlisted; cited for graph patterns |
| dynamic-crf | https://github.com/terranvigil/dynamic-crf | MIT | Allowlisted; cited for VMAF-driven CRF patterns |
| mosaic (Go ABR) | https://github.com/farshidrezaei/mosaic | MIT | Allowlisted; cited |
| Edward-Wu/srt-live-server | https://github.com/Edward-Wu/srt-live-server | BSD-3-Clause | Allowlisted; cited |
| OpenIRL/srt-live-server | https://github.com/OpenIRL/srt-live-server | MIT | Allowlisted; cited |
| ML-per-title-encoding | https://github.com/Ruan-666/Machine-Learning-for-Per-Title-Encoding-Project | undeclared | Reviewed for methodology only, cited |
| ott-resources | https://github.com/thijsl/ott-resources | undeclared | Reviewed for methodology only, cited |

23 sources reviewed across 13 WebSearch / WebFetch calls (well under the 15-call budget).

## Trademark discipline

- "Netflix", "Apple", "Microsoft", "Google", "Mux", "AWS MediaConvert" do not appear in skill names, descriptions, or body content.
- "Netflix/vmaf" appears only inside repository URLs in `## Sources reviewed`.
- "FairPlay", "Widevine", "PlayReady" appear in body text only as generic DRM-system references where the architectural choice depends on identifying the system; they are not part of any skill name and are used as broadly understood industry terms rather than endorsements.
- "Shaka", "Bento4", "GPAC", "OvenMediaEngine", "Haivision SRT" appear only in `## Sources reviewed` repository URLs.

## Methodology patterns identified across the niche

1. **Quality-driven ladders over fixed bitrate tables** — the field has shifted from "encode every title at the same nine bitrates" toward "encode every title to its operating curve". VMAF is the dominant open quality metric; per-title and per-shot encoding deliver measurable bandwidth savings on heterogeneous catalogs.
2. **CMAF as the unification point** — most modern builds use one set of fMP4 segments referenced from both an HLS playlist and a DASH MPD, halving storage and unifying CDN invalidation. cbcs Common Encryption is the path that lets HLS and DASH share the same encrypted media.
3. **Open-source contribution protocols winning over RTMP** — SRT and RIST replace RTMP for IP contribution over the open internet. RTMP persists for prosumer ingest but is treated as legacy.
4. **Low-latency live is a CDN problem, not just a player problem** — LL-HLS and LL-DASH require chunked transfer support at every relevant edge POP; the manifest configuration is necessary but not sufficient.
5. **Accessibility as a first-class deliverable** — the maturity gap is closing between marquee studios and the long tail. WCAG 2.2 captioning, SDH conventions, audio description, and sign-language interpretation are increasingly explicit line items in delivery specs.
6. **Active-active redundancy with shared program time** — for premium live, the standard pattern is two transcoders and two packagers producing byte-identical output keyed to absolute time, so a CDN can pull from either without coordination.
7. **VMAF caveats are well-documented** — the field broadly understands VMAF is calibrated for SDR live-action and is unreliable on animation, screen recordings, and HDR. Operator review supplements automated metrics in those classes.

## Confidence

**High.** The niche has stable, well-documented open-source tooling (FFmpeg, VMAF, Shaka Packager, Bento4, GPAC, SRT, OvenMediaEngine, the W3C subtitle specs) and well-established architectural patterns. The four skills cover the natural decomposition of the workflow (encode → package → caption → deliver-live) and reuse each other's outputs as inputs at well-defined boundaries.

Open risk: codec patent-license posture changes over time and varies by jurisdiction; the skills surface this as a flag and route the operator to counsel rather than asserting a license outcome. DRM integration is scaffolded only; real key-server contracts are out of scope and the skills say so.

## Efficiency

13 WebSearch + WebFetch invocations of the 15-call budget. All four skill bodies are within the 250–400 line target. No code copied from any source; all prose original.
