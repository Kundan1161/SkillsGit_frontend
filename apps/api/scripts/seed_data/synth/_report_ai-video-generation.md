# Wave-7 Synthesis Report — AI Video Generation Methodology

**Niche:** creative — AI video generation methodology
**Category:** creative
**Curator:** wave-7 methodology-synthesis agent
**Date:** 2026-05-14

## Skills produced

1. `ai-video-shot-architect` — designs a single AI-generated video shot across subject, action, camera, lighting, style, length budget, conditioning recipe (text vs image vs video reference), seed/CFG strategy, and the iterative narrowing loop.
2. `motion-control-and-consistency-architect` — preserves subject identity, environment, and motion across multiple shots via prompt-level lock-ins, image-to-video hero frames, identity adapters, character LoRAs adapted for video, persistent background plates, and an explicit drift audit.
3. `ai-video-post-integration-pipeline` — eight-stage finishing pipeline (ingest, uprez, frame-interpolate, deflicker, grade-match, mask-and-composite, audio design, delivery) for integrating AI plates with live-action footage.
4. `ai-video-content-policy-and-disclosure` — content policy gate (non-negotiable refusals), consent regime for likeness, deepfake distinction, C2PA Content Credentials authoring, platform policy alignment, and on-screen disclosure best practices.

All four skills carry the mandatory disclaimer and refuse non-consensual likeness, CSAM, defamation, election misinformation, and fraud applications.

## Sources reviewed (with license tags)

### Open-source video diffusion repositories

- https://github.com/hpcaitech/Open-Sora — Apache-2.0. Diffusion-Transformer video model; informed the "open-source DiT" model class in the shot architect and the coherence-horizon framing.
- https://github.com/zai-org/CogVideo — Apache-2.0 (code); model weights have additional terms. Informed text-to-video methodology and DiT prompt grammar.
- https://github.com/genmoai/mochi — Apache-2.0. AsymmDiT architecture; informed open-source large-model methodology.
- https://github.com/guoyww/AnimateDiff — Apache-2.0 (base model weights may carry separate constraints). Informed the "open-source U-Net AnimateDiff" model class with shorter coherence horizons.
- https://github.com/Stability-AI/generative-models — Stability AI Community License (commercial use permitted up to $1M revenue threshold; disclose). Informed image-to-video conditioning patterns and CFG-scheduling methodology.
- https://huggingface.co/docs/diffusers/en/using-diffusers/svd — Apache-2.0 documentation. Image-to-video conditioning surface and linear-CFG schedule details.

### Research papers and project pages (open access)

- https://arxiv.org/html/2502.13234v1 — MotionMatcher (arXiv preprint). Motion-feature-matching methodology, informed motion-consistency tactics.
- https://arxiv.org/html/2402.14780v1 — Customize-A-Video (arXiv preprint). One-shot motion customization, informed LoRA-adapted-for-video tactic.
- https://motion-canvas25.github.io/ — MotionCanvas (research project page). Cinematic shot design with controllable image-to-video.
- https://motion-prompting.github.io/ — Motion Prompting (research project page). Trajectory-based control informed motion-strength conditioning notes.
- https://pku-yuangroup.github.io/ConsisID/ — ConsisID (research project page). Frequency-decomposition identity preservation, named as research-grade tactic.
- https://arxiv.org/html/2402.09368v2 — Magic-Me (arXiv preprint). Identity-specific video customised diffusion.
- https://papers.nips.cc/paper_files/paper/2024/file/c7138635035501eb71b0adf6ddc319d6-Paper-Conference.pdf — StoryDiffusion (NeurIPS 2024). Consistent self-attention for long-range generation.

### Vendor and methodology references

- https://www.mercity.ai/blog-post/understanding-and-training-ip-adapters-for-diffusion-models/ — vendor blog. IP-Adapter family methodology overview.
- https://www.topazlabs.com/topaz-video — vendor reference. Frame-interpolation and uprez methodology only; no code or prose used.
- https://www.actionvfx.com/blog/top-10-ai-tools-for-vfx-workflows — vendor blog. Composite-and-integration methodology context.
- https://www.aiarty.com/ai-video-enhancer/frame-interpolation.htm — vendor blog. Frame-interpolation methodology overview.
- https://academy.runwayml.com/prompt-guide — vendor documentation. Prompt-grammar methodology reference; no copying of vendor prose; vendor name confined to URL citation.

### Open standards

- https://spec.c2pa.org/specifications/specifications/2.4/explainer/Explainer.html — open specification (C2PA). Manifest contents and disclosure framing.
- https://spec.c2pa.org/specifications/specifications/2.2/explainer/_attachments/Explainer.pdf — open specification (C2PA).
- https://contentauthenticity.org/how-it-works — Content Authenticity Initiative methodology reference.
- https://contentcredentials.org/ — open standard reference.
- https://c2pa.wiki/ — open standard reference.

## Methodology patterns identified

Across the open-source video-diffusion repositories and research literature, six patterns recur:

1. **Coherence horizon as the dominant constraint.** Every model has a duration past which subject identity, background structure, and motion degrade. The horizon varies by model family (AnimateDiff-class: 1–2 s; current frontier hosted: 6–10 s). Designs that respect two-thirds of the horizon land; designs that exceed the horizon either degrade visibly or require multi-shot decomposition with cuts hiding the seams.

2. **Conditioning hierarchy.** Image-to-video conditioning beats text-only for identity-anchored shots. Video-reference conditioning beats both for motion-specific shots. Adapter-conditioning (IP-Adapter family) and LoRA-conditioning sit between these for subject identity. The right conditioning recipe is the dominant determinant of generation success; prompt-engineering alone has diminishing returns past a basic competent prompt.

3. **Seed search beats seed luck.** Production teams that treat seed selection as an explicit small-N search (three low-cost seeds at preview quality, surviving seed at full quality) consistently outperform teams that reroll a single high-cost seed.

4. **Prompt-level lock-ins for consistency.** Across multi-shot pieces, repeating identical phrases for style, identity, environment, and lighting verbatim across shot prompts is cheap and surprisingly effective. Order matters — locked phrases first, shot-specific text second.

5. **Cuts hide what generation cannot.** Multi-shot AI video pieces are not extended generations; they are cuts of short generations where the cut points are designed at storyboard time to hide identity, environment, and motion drift. Cut on motion, cut on graphic match, cut on angle change.

6. **Post is non-optional.** AI-generated video that goes to public delivery without an uprez pass, a deflicker pass, and a grade-match pass against the rest of the piece reads as AI-generated even when the generation itself is strong. The finishing pipeline is the difference between a deliverable and a demo.

A seventh pattern around content provenance — the convergence on C2PA Content Credentials as the cross-industry open standard for embedded AI disclosure — informed the policy-and-disclosure skill and is unique to this niche; other creative niches that have to disclose AI involvement will face the same questions.

## Trademark and product-name discipline

Per wave-4 policy, frontier hosted video-diffusion product names ("Sora", "Veo", "Runway", "Pika", "Kling") appear only in URL citations in the `## Sources reviewed` sections. The skill body content refers to "frontier hosted video-diffusion model" or "frontier video model" generically. The open-source families are named by their repository paths in `## Sources reviewed` only. The four skills are entirely model-agnostic in their prose and can be applied to any current or future video-diffusion model with comparable conditioning surfaces.

## Confidence

- `ai-video-shot-architect` — high. Cross-validated against open-source documentation and research literature; the seven decisions cover the conditioning surface every modern video-diffusion model exposes.
- `motion-control-and-consistency-architect` — high. The five tactics for identity and three for environment are stable across the cited research; production-grade execution (LoRA training, IP-Adapter conditioning) requires tools the skill names but does not depend on any one product.
- `ai-video-post-integration-pipeline` — high. The eight stages are standard finishing practice adapted to AI source material; the specific recommendations on flicker repair and grade-match are conservative and widely applicable.
- `ai-video-content-policy-and-disclosure` — medium-to-high. The non-negotiable refusals and the C2PA disclosure pattern are stable; the platform-specific rules and the jurisdictional regulatory frame are moving targets, and the skill flags counsel review aggressively rather than asserting current law.

## Rejected directions

- An "AI video model selection" skill was considered and rejected. Model selection in this space is dominated by access (which frontier model the team has API or product access to), pricing (which the policy excludes from these free skills), and rate of change (model families ship new versions on a months-not-years cadence). A model-selection skill written in May 2026 would be partially stale by year-end.
- A "training-data copyright analysis" skill was considered and rejected as out-of-scope for methodology synthesis; the policy explicitly delegates copyright questions to counsel, and the four skills here all carry that disclaimer.
- A "video-LoRA training methodology" skill was considered and held back as a future addition; current training methodology is highly tool-specific and a generic skill would either be vague or quickly stale.

## Disclaimer applied to every skill

> This skill produces methodology guidance for AI video generation. The skill does not address copyright status of training data or generated outputs in any jurisdiction; consult counsel for commercial use. The skill explicitly does not produce or recommend non-consensual likeness use (deepfakes), CSAM, defamatory content, or content that violates platform policy or applicable law.

Search budget used: 6 WebSearch calls of the 15 permitted. No WebFetch calls were necessary; the WebSearch summaries plus prior literature context were sufficient for methodology synthesis without copying any source prose.
