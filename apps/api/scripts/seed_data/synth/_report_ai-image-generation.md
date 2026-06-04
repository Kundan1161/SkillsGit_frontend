# Creative — AI Image Generation: Synthesis Report

## Files produced

1. `ai-image-prompt-designer.skills.md` — license_type: free. 8 sources cited.
2. `controlnet-conditioning-architect.skills.md` — license_type: free. 9 sources cited.
3. `lora-and-finetune-methodology.skills.md` — license_type: free. 8 sources cited.
4. `inpainting-outpainting-workflow.skills.md` — license_type: free. 8 sources cited.

All four are 100% original prose synthesizing patterns observed across the broader diffusion-image-generation ecosystem. Body lengths land between ~280 and ~370 lines (within the 250-400 instructed range). Each body carries the mandatory project disclaimer verbatim and refuses copyright-/consent-sensitive use cases inline.

## Sources reviewed (license verified)

| Repo | License | Used in |
|---|---|---|
| huggingface/diffusers | Apache-2.0 | prompt-designer, controlnet, lora, inpaint |
| invoke-ai/InvokeAI | Apache-2.0 | prompt-designer, controlnet, lora, inpaint |
| tencent-ailab/IP-Adapter | Apache-2.0 | controlnet, lora |
| lllyasviel/ControlNet | Apache-2.0 (code); CreativeML OpenRAIL-M (weights) | controlnet, lora, inpaint |
| lllyasviel/ControlNet-v1-1-nightly | Apache-2.0 (code) | controlnet |
| kohya-ss/sd-scripts | Apache-2.0 (portions under separate terms) | lora |
| bmaltais/kohya_ss | Apache-2.0 | lora |
| comfyanonymous/ComfyUI | GPL-3.0 | prompt-designer, controlnet, lora, inpaint (methodology study only; no code or trademarked names used) |
| comfyanonymous/ComfyUI_examples | GPL-3.0 | prompt-designer (methodology study only) |
| AUTOMATIC1111/stable-diffusion-webui | AGPL-3.0 | prompt-designer, controlnet, lora, inpaint (methodology study only) |
| lllyasviel/stable-diffusion-webui-forge | AGPL-3.0 | prompt-designer, controlnet, inpaint (methodology study only) |
| Fannovel16/comfyui_controlnet_aux | (study only; license per repo) | controlnet |
| cubiq/ComfyUI_Workflows | (study only; license per repo) | prompt-designer |
| Ling-APE/ComfyUI-All-in-One-FluxDev-Workflow | (study only; license per repo) | prompt-designer |
| lkwq007/stablediffusion-infinity | (study only; license per repo) | inpaint |
| Uminosachi/inpaint-anything | (study only; license per repo) | inpaint |

Per-skill source counts: prompt-designer 8, controlnet 9, lora 8, inpaint 8 — all within the 5-10 range.

## Wave-4 policy application

Per the Wave-4 methodology-recovery doctrine, copyleft (GPL-3.0, AGPL-3.0) and OpenRAIL-licensed sources were *read* for methodology understanding only. No code, no source prose, no example workflows, no trademarked product/methodology names appear in the skill bodies or names. Citations carry explicit `(license)` tags and, where appropriate, the `methodology study only; no code or trademarked names used` flag.

Trademarked product names ("Midjourney", "DALL-E", "Imagen", and the like) are absent from all skill names, body content, and tags. ComfyUI and AUTOMATIC1111 / Forge appear only in source-citation URLs. Body content uses generic descriptors: "diffusion image model", "graph-based runner", "rich web UI", "transformer-based diffusion (Flux-class)", "rectified-flow models".

## Key patterns observed across sources

### Prompt design (prompt-designer)
- **Six structural prompt bands** (subject, action, environment, lighting, medium/style, composition/technical) appear across documentation and example galleries as the de facto pattern; word order matters because earlier tokens carry stronger attention.
- **Sampler/CFG defaults bifurcate by model family**: SD 1.5 likes CFG 7-9, SDXL 5-7, SD 3.x and Flux-class 3-5. DPM++ 2M Karras is the workhorse for SD-family; Euler-class with sigma-uniform is the workhorse for rectified-flow.
- **Step count plateaus around 25-30 steps** for the SD families; more steps mostly burn compute.
- **Negative prompts have asymmetric strength across model families**; SD 1.5/SDXL get strong negatives, Flux-class get weak or absent ones. Workflows reframe exclusions as positive avoidance descriptors when negatives are unsupported.
- **Reproducibility requires pinning more than the seed**: checkpoint hash, sampler, scheduler, steps, CFG, resolution, precision, backend version. Recognised consistently across the runners.

### Spatial conditioning (controlnet)
- **Anchor-control + secondaries** pattern: identify the single structural attribute that must be locked, weight that control highest, scale secondaries down by 0.2-0.4.
- **Start/end ramps are underused but powerful**: applying a control for only the first 50-70% of denoising preserves prompt-driven detail in the late steps.
- **Mask-scoped controls** beat full-frame controls for multi-character or foreground/background separation scenes.
- **Preprocessor/control-model pairing is rigid** — a canny preprocessor only conditions a canny-trained control model; pairing mismatch is a top "wasted run" cause.
- **Per-model VRAM headroom and adapter availability** differ sharply by family; SD 1.5 has the broadest catalogue, SDXL has matured, SD 3.x/Flux-class adapters are still consolidating.

### Training (lora-and-finetune)
- **Method tier ladder**: textual inversion -> LoRA -> IP-Adapter (no training) -> full fine-tune. LoRA covers the bulk of contributor needs; escalation only with justification.
- **Captioning is the second-largest lever after dataset selection**: subject LoRAs caption what is *not* the subject; style LoRAs caption the scene with a single trigger token; regularisation sets prevent class drift in subject training.
- **Rank/alpha ranges**: style LoRAs 8-32 rank, subject 16-64, alpha = rank or rank/2 as a stable starting point.
- **Prodigy as auto-tuned learning rate** is a recurring modern default; AdamW8bit / Adafactor for VRAM constraint.
- **Stacking strength budget ~1.0-1.5 total** across all simultaneous LoRAs; two LoRAs at 1.0 each routinely interfere.
- **Overfit signals are stratified**: memorisation, trigger collapse, style bleed (subject leaking style), subject bleed (style leaking subject), pose lock-in, mode collapse — each has a distinct remediation path.

### Inpainting / outpainting (inpaint)
- **Mask quality dominates** every other parameter. Bad masks make hyperparameter tuning irrelevant.
- **Denoise strength band**: 0.2-0.4 polish, 0.4-0.7 surgical, 0.7-1.0 full regenerate. Recognised across runners.
- **Inpaint-trained checkpoints + soft-feathered masks** is the highest-quality default; latent inpaint with a base model + mask blending is the fallback.
- **Pixel paste-back for preservation-strict work** — strict logo/face preservation gets a composite restore at the end.
- **Progressive outpaint strips** beat large single-pass outpaint; small extensions keep colour and lighting context.
- **Seam policy is not "feather harder"**: histogram match, overlap-strip refinement, lighting-aware seam masking, and depth/canny control along the seam edge are the recurring fixes.

## Confidence per skill

- **Prompt Designer — high confidence.** Six-band prompt structure, family-specific CFG/sampler defaults, and seed-discipline patterns are extensively documented across the ecosystem and shift slowly. Risk: family-specific defaults will need updates as new model families ship.
- **ControlNet Conditioning Architect — high confidence on the framework, medium on family-specific defaults.** The anchor + secondaries + ramps framework is robust. Per-family adapter availability shifts every quarter; the skill calls out the verification step rather than hard-coding lists.
- **LoRA and Fine-Tune Methodology — high confidence on the framework, medium on hyperparameter defaults.** Method-tier ladder, captioning discipline, validation harness, overfit detection are stable. Specific rank/LR numbers vary by trainer; the skill calls out a pilot run before a full schedule.
- **Inpainting and Outpainting Workflow — high confidence.** Mask discipline, denoise band, seam policy, and composite preservation are extensively patterned across runners. Method-specific modes (differential diffusion, inpaint-conditioning ControlNet) shift faster than the underlying discipline; the skill flags availability as a verification step.

## Trademark and ethics discipline

- No trademarked product names ("Midjourney", "DALL-E", "Imagen", "Adobe Firefly", and the like) appear in skill names, bodies, or tags. They are absent from source citations too because no skill cites a trademarked vendor's repo.
- The mandatory project disclaimer appears verbatim in each skill body's `When to use` section.
- Each skill refuses, inline, three high-risk use cases:
  - NSFW content.
  - Person impersonation (especially via subject LoRA and IP-Adapter-face).
  - Style-by-artist-name targeting living artists.
- The LoRA skill additionally requires a rights chain per training image and refuses subject training without a written consent / model release.
- The inpaint skill refuses workflows whose intent is misrepresentation (forensic alteration of evidence images, watermark removal, attribution removal).

## Follow-ups worth considering

- A separate `production-batch-rendering-pipeline` skill (queue + deterministic seeds + version tracking + asset organisation + QC gate + post-generation upscale, face restore, colour sync + DAM integration). The pattern is well-supported by sources and warranted for buyers running studio-scale generation; not produced in this batch to keep scope tight.
- A separate `diffusion-upscale-and-restoration-pipeline` skill covering tile-based upscaling, latent upscaling, GFPGAN/CodeFormer-style face restoration discipline, and colour grade unification.
- A separate `image-prompt-adapter-strategy` skill that goes deeper on IP-Adapter family (full / plus / face / style / composition variants), choice criteria, and stacking with LoRA.
- The four skills target Claude Opus 4.7 / Sonnet 4.6 as required; `compatible_models` lists should be reviewed when new model versions land.

## Notes on overlap with existing creative skills

The synth library already carries `ai-ux-pattern-picker` and several design skills; those are orthogonal to diffusion image generation methodology. No merge needed. Tag overlap is limited to `creative`; the new `niche:ai-image-generation` first tag cleanly partitions this niche.
