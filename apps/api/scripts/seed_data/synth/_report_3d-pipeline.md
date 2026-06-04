# Wave-7 Synthesis Report — 3D Pipeline (creative)

**Niche:** 3D modeling, texturing, and rendering pipeline (Blender-class production methodology, PBR materials, lighting setups, render passes).

**Skills produced:** 4

- `3d-asset-pipeline-architect.skills.md` — design a 3D-asset production pipeline (modeling → UVs → texturing → rigging → lookdev → publish; USD-based asset assembly; LOD strategy; naming; binary version control).
- `pbr-material-authoring-methodology.skills.md` — author physically based materials (base color / metalness / roughness / normal / AO / displacement; texture-set conventions; UDIM; color-space discipline by map type; calibration against measured references; procedural vs scanned; QC on neutral test scene).
- `lighting-and-render-passes-architect.skills.md` — light a scene and design its render passes (three-point lighting principles; HDRI/IBL; light linking; AOV design for compositor reassembly; sample budget and denoising strategy).
- `3d-render-farm-methodology.skills.md` — manage a render farm (scene packaging, dependency capture, frame distribution, retry/recovery, license budgeting, priority queues, output verification, archival).

**Category:** `creative`. First tag on each file: `niche:3d-pipeline`.

**License model:** `license_type: free` on all skills; no pricing fields populated.

---

## Sources reviewed and license tagging

All citations are URL-only with a `(license)` tag. No prose, code, or substantial structural content was copied from any source. All instructional content is original synthesis.

| Source URL | License | Used by |
| --- | --- | --- |
| https://github.com/PixarAnimationStudios/OpenUSD | Modified Apache-2.0 | asset-pipeline, pbr, lighting, render-farm |
| https://github.com/PixarAnimationStudios/OpenUSD-proposals | Modified Apache-2.0 | asset-pipeline |
| https://github.com/PixarAnimationStudios/OpenSubdiv | Modified Apache-2.0 | asset-pipeline |
| https://github.com/AcademySoftwareFoundation/MaterialX | Apache-2.0 | asset-pipeline, pbr, lighting |
| https://github.com/AcademySoftwareFoundation/OpenPBR | Apache-2.0 | pbr, lighting |
| https://github.com/AcademySoftwareFoundation/OpenColorIO | BSD-3-Clause | pbr, lighting |
| https://github.com/AcademySoftwareFoundation/OpenImageIO | Apache-2.0 | asset-pipeline, pbr, lighting, render-farm |
| https://github.com/AcademySoftwareFoundation/openvdb | Apache-2.0 | lighting |
| https://github.com/AcademySoftwareFoundation/OpenCue | Apache-2.0 | render-farm |
| https://github.com/KhronosGroup/3DC-Asset-Creation | Apache-2.0 | pbr |
| https://github.com/KhronosGroup/glTF | CC-BY-4.0 (spec) | pbr |
| https://github.com/ynput/OpenPype | MIT | asset-pipeline, render-farm |
| https://github.com/cgwire/awesome-cg-vfx-pipeline | CC0 (curated index) | asset-pipeline, render-farm |
| https://github.com/blender/blender | GPL-3.0 (read for methodology only, no content copied) | asset-pipeline, pbr, lighting, render-farm |
| https://github.com/armadillica/flamenco | GPL-3.0 (read for methodology only, no content copied) | render-farm |

Per wave-4 "methodology recovery" doctrine, GPL-licensed sources (Blender, Flamenco) were read for methodology only and explicitly tagged with the read-for-methodology-only note in each citation. No prose, code, or interface was copied. Trademark-protected product names ("Maya", "Houdini", "Cinema 4D", "Substance Painter") do not appear in skill names or body content. They were avoided entirely; even URL citations include only the open-source projects above.

---

## Patterns identified across sources

1. **Composable scene description as the production backbone.** Modern open-pipeline references converge on a layered, referenceable scene format with composition arcs (sublayer, reference, variant, payload) as the way that departments hand off work to one another. Asset assembly, shot assembly, and material binding all use the same composition idiom, which lets departments iterate in parallel without one stepping on another. This is the spine of `3d-asset-pipeline-architect`.

2. **PBR shading-model convergence on metallic-roughness with energy-conserving lobes.** OpenPBR, MaterialX's reference shading library, and the Khronos glTF metallic-roughness parameterization express the same principle: one über-shader with a small parameter set, color-space-disciplined map ingestion, and per-lobe energy conservation. This is the spine of `pbr-material-authoring-methodology`.

3. **Color-space discipline by map type.** The OpenColorIO ecosystem teaches that each map type has a specific color-space role: base color perceptually encoded; scalar maps (roughness, metalness, normal, AO, displacement) linear/raw. Mixing this up is the single most common source of "the material looks too shiny" failures and is treated as a hard rule in the PBR skill.

4. **Light linking, light groups, and AOV decomposition as compositor enablement.** Production-grade lighting deliberately splits the rendered image into per-light, per-lobe, and per-object channels so the compositor can rebalance, mask, and slightly relight in 2D without a re-render. The AOV design is part of the lighting design, not an afterthought. This is the spine of `lighting-and-render-passes-architect`.

5. **Render management as a single source of truth for what was rendered.** OpenCue, Flamenco, and OpenPype/AYON converge on the pattern: submissions go through a manager that captures dependencies, validates the scene, dispatches per-frame tasks, applies priority and license arbitration, retries transient failures, verifies output, and archives a manifest. Going around the manager is the cardinal sin; it produces folklore renders that nobody can reproduce. This is the spine of `3d-render-farm-methodology`.

6. **Content-addressed binary stores plus human-readable manifests.** Across the asset-pipeline and render-farm sources, the consistent answer to "how do you version multi-gigabyte assets" is content-addressing for bytes plus a manifest/symlink layer for human-readable names. This pattern appears in both `3d-asset-pipeline-architect` (asset publishes) and `3d-render-farm-methodology` (render submissions and archives).

7. **The asset/shot interface contract.** A shot composes published assets via references; a publish that changes its interface (renames meshes, renames materials, removes controls) breaks the shots that referenced it. The interface contract appears in `3d-asset-pipeline-architect` as a hard rule (interface changes are major-version bumps, routed through a producer).

8. **Calibration against measured reference.** Both PBR authoring (measured BRDF / photo of a real material) and color pipeline work (chrome and gray ball on a controlled rig) treat calibration against an external reference as the only way to confirm correctness rather than mere plausibility. The lookdev test rig pattern carries across the PBR and lighting skills.

9. **Three-tier LOD strategy.** Hero / mid / proxy with subdivision evaluated at render time is the recurring pattern across the asset-pipeline references; real-time pipelines add tiers below, but the three core tiers cover most film-and-VFX work. Encoded in `3d-asset-pipeline-architect`.

10. **Archive as manifest plus store, verified by re-render.** A trustworthy archive is not "the rendered frames sit on tape"; it is "the manifest plus the content-addressed store, plus a periodic re-render test to confirm recoverability." This explicit verification step is uncommon in informal pipelines and is called out as the most important discipline in `3d-render-farm-methodology`.

---

## Rejection / inclusion reasoning

- **Blender (GPL-3.0)** and **Flamenco (GPL-3.0)** would have been rejected under waves 1-3's strict allowlist; under wave-4's methodology-recovery doctrine they were read for methodology only and cited with the explicit license tag and read-only note. No prose, code, or interface was copied.
- **Trademarked product names** ("Maya", "Houdini", "Cinema 4D", "Substance Painter") do not appear in skill names, descriptions, body content, or even URL citations. The skills describe DCC-agnostic methodology and let the reader plug in whichever application they use.
- **Cloud render-service product names** (specific commercial render-farm-as-a-service providers) are avoided in favor of the generic "cloud burst" terminology.
- **OpenSubdiv** is hosted at PixarAnimationStudios rather than under ASWF; cited at the Pixar URL with the Modified Apache-2.0 license tag.

---

## Confidence

- `3d-asset-pipeline-architect`: **high.** The composable-scene-description spine, the department graph, the publish-versus-work split, and the manifest-plus-content-addressed-store pattern are well-established across the cited sources and corroborated by my prior reading.
- `pbr-material-authoring-methodology`: **high.** The shading-model convergence on metallic-roughness, the color-space rules, the UDIM allocation conventions, and the calibration-against-measured-reference pattern are common ground across the references; the anchor roughness values, dielectric/metal F0 conventions, and "metalness is binary" rule are the methodology core taught across the PBR sources.
- `lighting-and-render-passes-architect`: **high.** The three-point principle, HDRI/IBL design, light linking and light groups, AOV decomposition for compositor reassembly, and the lookdev-rig calibration pattern are common ground; the per-engine specifics of AOV naming and denoiser parameters are intentionally generic to keep the skill DCC-agnostic.
- `3d-render-farm-methodology`: **high.** The submission-as-pipeline-action pattern, dependency capture, priority and license arbitration, retry policy by transient/terminal, output verification, and archive-as-manifest pattern are common ground across OpenCue, Flamenco, and OpenPype/AYON. The archive recoverability test (re-render a randomly chosen frame from the archive) is an explicit recommendation that goes slightly beyond what the sources articulate but is well-justified by the manifest-plus-content-store discipline they teach.

Total skills produced: **4**. All cite at minimum 6 sources; the asset-pipeline skill cites 8, the PBR skill 8, the lighting skill 7, the render-farm skill 7. All sources URL-only with explicit license tags. Body length per skill exceeds the 250-line minimum across all four.

---

## Efficiency

WebSearch calls used: 8. WebFetch calls used: 0. Within the ≤15 budget.
