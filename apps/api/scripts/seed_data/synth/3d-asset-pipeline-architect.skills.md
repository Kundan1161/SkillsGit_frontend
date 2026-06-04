---
id: skillsgit-curated/3d-asset-pipeline-architect
version: 1.0.0
name: 3D Asset Pipeline Architect
description: Design a 3D-asset production pipeline — modeling, UVs, texturing, rigging, lookdev, and publish — anchored on a universal-scene-description exchange format, LOD strategy, naming conventions, and binary version control.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: creative
tags: [niche:3d-pipeline, usd, asset-management, lookdev, lod, dcc-agnostic, naming-conventions, publish-workflow]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: []
  tools_optional: [web_search]
  min_context_tokens: 24000
  estimated_tokens_per_invocation: 6500
trigger_keywords:
  - 3d pipeline
  - asset pipeline
  - usd pipeline
  - scene description
  - lookdev
  - asset publish
  - lod strategy
  - dcc agnostic
  - naming convention
  - binary version control
  - asset assembly
  - shot assembly
  - rig publish
  - texture publish
example_invocations:
  - "Design an asset pipeline for a short film that goes from modeling to lookdev with a hand-off into shot assembly."
  - "Help me set up a USD-based publish workflow so modeling, texturing, and rigging can iterate in parallel."
  - "What naming and folder convention should we use for a studio of six people producing fifty hero assets?"
  - "We have one DCC for modeling, another for texturing, and a third for layout — design the exchange points."
inputs:
  - name: production_brief
    type: text
    required: true
    description: Project type (short, episodic, game, archviz, advertising), team size, number of hero/background assets, target render engine, target delivery resolutions, and timeline.
  - name: dcc_inventory
    type: text
    required: true
    description: Which application is used for modeling, UVs, sculpt, texturing, rigging, layout, animation, lookdev, lighting/rendering, and compositing. Note seats and whether each tool supports USD natively.
  - name: existing_pipeline_constraints
    type: text
    required: false
    description: Any tooling locked in (a chosen render engine, an asset-management database, on-prem vs cloud storage, an established naming convention) that cannot be re-decided.
  - name: lod_targets
    type: text
    required: false
    description: How many LOD levels are needed per asset class and what their use cases are (hero close-up, mid-distance, far-distance, real-time/game, viewport proxy).
  - name: team_skill_profile
    type: choice
    required: false
    description: Average pipeline-engineering skill level on the team.
    choices: [generalists_only, mixed_with_one_pipeline_td, experienced_pipeline_team]
outputs:
  - name: pipeline_design
    type: markdown
    description: Step-by-step pipeline design covering departments, exchange formats, publish gates, and ownership.
  - name: directory_and_naming_spec
    type: markdown
    description: Folder hierarchy, naming convention, and version-numbering scheme for assets, shots, and renders.
  - name: lod_and_proxy_plan
    type: markdown
    description: Level-of-detail tiers, geometry budgets per tier, and proxy/viewport-representation strategy.
  - name: risk_register
    type: markdown
    description: Failure modes (broken references, mismatched units, baked-in transforms, lost authorship) with mitigations.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# 3D Asset Pipeline Architect

## When to use

Use this skill at the start of any project where more than one person will touch a 3D asset, where more than one application is involved, or where the same asset has to appear in more than one shot or context. It is the right skill for a producer scoping a short film, for a small studio setting up its first proper publish workflow, for a generalist hired to define the asset pipeline for an animated commercial, and for a technical director documenting the current pipeline before it grows past the point where the team remembers all of the conventions.

Skip it for one-person turntables, single-shot illustration work, or game-engine prototypes that will never leave the engine. Reach for it the moment a second seat of the modeling tool is opened, the moment a separate texturing application is introduced, or the moment a shot pulls more than one asset that has to be re-rendered after a model fix.

## How to apply

1. Start with the **delivery target**, not the modeling step. Final delivery dictates every choice upstream: a real-time game build with hard triangle budgets caps modeling resolution and texture sizes; an animated short rendered at 4K with deep close-ups demands hero LODs and tiled textures; a product visualization needs lossless authoring and exact dimensions in real-world units. Write down the deliverable: resolution, frame count, render engine, output format, and the final viewing context.
2. Decide on a **scene-description backbone**. The pipeline needs one canonical, application-agnostic format for asset assembly so that modeling, texturing, rigging, and lighting can iterate in parallel without one department stepping on another. A composable scene-description format with layering, variants, references, and payloads is the modern default; choose it unless every tool in the pipeline lacks support, in which case fall back on a structured interchange of meshes plus sidecar metadata files. The decision applies whether the studio is two seats or two hundred.
3. Define the **department graph**. Asset production splits into modeling, UV layout, sculpt/displacement, texture authoring, rigging, lookdev, and asset publish. Shot production splits into layout, animation, simulation, lighting, rendering, and compositing. Draw the arrows: each department consumes a published artifact from upstream and produces a published artifact for downstream. The arrows are the only places where data crosses a boundary; everything else is internal to a department and not visible outside it.
4. Establish **unit and orientation conventions** before anything is modeled. Decide the working unit (centimeters is the common default for film and VFX; meters for archviz and real-time; millimeters for fabrication). Decide the up axis (Y-up is common in animation and VFX; Z-up is common in CAD and some real-time engines). Decide the front axis. Bake these into the asset template so no one ever has to remember them. Mismatched units between departments is the single most common source of silent breakage in a pipeline.
5. Author a **folder hierarchy and naming convention**. A workable shape: a project root with `assets/`, `shots/`, `library/`, `publish/`, `work/`, and `output/`. Under `assets/`, one folder per asset, with `model/`, `lookdev/`, `rig/`, `texture/` subfolders. Names are lowercase, alphanumeric with underscores, with a short type prefix (`prop_`, `char_`, `set_`, `veh_`). Asset names never embed version numbers; versions live in filenames using a stable scheme (`v001`, `v002`) and a `latest` symlink or a manifest pointer maintained by the publish step.
6. Separate **work files from publishes**. Work files live under `work/` and are owned by an artist — they are messy, unversioned in the formal sense, and can be deleted without affecting the pipeline. Publishes live under `publish/` and are immutable, versioned, hash-checkable, and have a manifest describing inputs, outputs, and ownership. Downstream departments reference publishes only; they never reach into a peer department's work directory. This rule alone prevents most of the "I made a fix and now the lighter is rendering yesterday's mesh" failures.
7. Design the **publish artifact** per department. Modeling publishes a watertight mesh in the scene-description format with named subsets for material assignment, a clean UV layout, and a sidecar JSON of metadata (vertex count, bounding box, triangle ranges per subset, dimensions in real units). Texture publishes maps grouped by UDIM tile and material slot, named to a fixed pattern, with a sidecar describing color space and intended channel role. Rig publishes a USD layer that contributes joints, controls, and skinning weights composited over the model. Lookdev publishes a material binding layer with references to the texture publish. Each publish is reproducible from its inputs.
8. Plan **asset assembly via composition**, not via copy. An asset is composed by sublayering or referencing each department's publish into a single asset-level scene description. The asset file owns no geometry of its own — it composes the model layer, the rig layer, the material layer, and any variant layers. Adding a new lookdev variant is a new sublayer; switching to a new model version updates one reference. The asset-level file is small, fast to open, and stable to diff.
9. Define a **level-of-detail strategy**. Three tiers cover most film work: a hero tier with full displacement and tessellation suited to close-ups; a mid tier with baked normal maps and reduced geometry; a proxy tier that is a bounding box or a low-poly stand-in for layout and viewport responsiveness. Real-time and game pipelines add one or two more tiers below proxy. Each tier is a separate publish path with a deterministic naming convention (`asset_hero`, `asset_mid`, `asset_proxy`). The shot pipeline selects the tier per shot based on screen coverage and use.
10. Choose a **subdivision-surface contract** for hero models. Modelers author a control mesh with quads and clean topology; the pipeline subdivides at render time via a published subdivision evaluator. The contract names the subdivision scheme (Catmull-Clark with creases is the studio default), the boundary interpolation rule, and the maximum subdivision level. Edge creasing is authored in the model and survives through to render via the scene-description format; it must not be re-authored in lookdev.
11. Treat **binary assets as first-class version-controlled artifacts**. Source-control systems built for text scale poorly to multi-gigabyte caches. Use a binary-asset-friendly store — a centralized object store keyed on content hash, a large-file extension to source control, or a purpose-built asset-management database. Each publish writes its bytes once, addressed by hash, and the human-readable filename is a symlink or manifest pointer. Rollback is "change the pointer," not "find yesterday's file."
12. Separate the **on-disk format** from the **build cache**. The authoritative artifact is the scene-description file referencing the binary store. A render-time cache (procedurally generated displacement, baked simulation, hairs, point clouds) is derivative and can be rebuilt from inputs. Mark cache directories as ephemeral; do not version them; build a tool that re-creates them from manifest. This keeps the persistent storage small and the recovery story clean.
13. Specify **shot assembly** in the same composition idiom as asset assembly. A shot composes references to the assets it uses, plus a layout layer (transforms, instance placements), an animation layer (cached transforms and deformations), a simulation layer (cached cloth, hair, smoke), and a lighting/render-settings layer. A shot does not own asset geometry; it owns its own composition arcs. Layout edits, animation edits, and lighting edits are independent and survive each other.
14. Plan **DCC integration** explicitly. Each application gets two integrations: an import action that resolves a publish into the application's native scene, and a publish action that converts the application's working scene into a publish artifact. Both go through the same publish service so naming, version selection, hash checking, and manifest creation are centralized. Artists never write to the publish directory directly.
15. Document **the contract between asset and shot**. A shot expects a published asset with a known interface — geometry hierarchy, material assignment, rig controls if applicable, variant set if applicable. If an asset publish changes its interface (renames the hero mesh, drops a control, splits a material), shots referencing it can break. Mark interface changes as breaking changes in the publish manifest, bump a major version, and route the change through a producer for sign-off before it lands in the latest pointer.
16. Build a **publish validator** before opening publishes to artists. The validator checks: units and up axis match the project; UV islands exist and do not overlap unless intentional; texture maps cover every UDIM tile referenced by the model; the rig binds to the latest model version; naming matches the project convention; no namespace collisions; no untextured material slots. Reject a publish that fails. The validator is the cheapest insurance the pipeline buys.
17. Plan **archival** from the start. At end of project, the publish directory plus the binary store plus a manifest of latest pointers is the complete project. Work files can be deleted. A re-render twelve months later starts by restoring the archive, resolving the manifest pointers, and submitting frames. If the manifest does not survive archival, the project does not survive archival; treat the manifest as the index of record.

## Inputs

- Production brief with team size, asset counts, render engine, and delivery requirements.
- DCC inventory listing modeling, texturing, rigging, layout, lighting, and compositing tools.
- Any existing pipeline constraints (locked-in tools, established conventions).
- LOD targets per asset class.
- Team skill profile for setting an appropriate level of automation.

## Outputs

- A pipeline design document covering departments, exchange artifacts, and publish gates.
- A folder hierarchy and naming convention specification.
- A LOD and proxy plan with geometry budgets per tier.
- A risk register naming the likely failure modes and mitigations.

## Examples

**Six-person animated short, two-year timeline, USD-aware DCC stack.** Backbone: composable scene-description format end-to-end. Departments: modeling, UVs, lookdev, rigging, layout, animation, lighting/render. Working unit: centimeters, Y-up. Folder hierarchy: `assets/{type_name}/{model,lookdev,rig,texture}/publish/v{n}` with a `latest` symlink. Publishes: model layer, lookdev material binding layer, rig layer, texture set with UDIM tiles. Asset file composes the layers. Three LODs (hero/mid/proxy); proxy used during layout; hero used in final renders. Subdivision evaluated at render time, creasing authored in modeling. Publish validator runs before any artifact is promoted. Archival: at end of project, publish directory and binary store are committed to long-term storage with the manifest of latest pointers.

**Twenty-person episodic series, mixed-DCC stack with two applications that do not speak the scene-description format.** Backbone: scene-description format for everything that supports it; a structured interchange-mesh format plus sidecar metadata files for the two outliers, with a conversion service maintained by the pipeline team. Publish validator runs on both paths and refuses to promote anything that does not match the project unit and orientation. LODs: hero, mid, proxy plus a layout-only bounding box. Asset-management database tracks publishes; binary store is content-hashed. Shots compose published assets via reference; the two outlier applications consume materialized scenes generated by the conversion service.

**Two-person archviz studio, single render engine, no animation.** Lighter backbone: the render engine's native scene format plus a minimal manifest. Working unit: meters, Z-up to match CAD imports. Folder hierarchy: per-project, with `library/` shared across projects for repeated furniture, vegetation, and materials. Publish is "the artist clicks save in the publish dialog and the asset gets a versioned copy in the library." No rigging, no animation, two LOD tiers (hero and proxy). Archival is project-level: zip the project plus the references it draws from the library, with a snapshot of those library versions captured at the time.

## Limitations

- This skill does not prescribe a specific render engine, DCC tool, or asset-management product; it describes the methodology and leaves vendor choices to the team. Plug-in maturity for the scene-description backbone varies by application, and some workflows require fallback paths.
- Real-time and game pipelines have engine-specific constraints (texture streaming, virtualized geometry, runtime memory budgets) that this skill names but does not enumerate exhaustively.
- Migrating an existing project mid-flight from an ad-hoc pipeline to a composed-publish pipeline is a different problem than greenfield setup; expect a transitional period in which both styles coexist.
- This skill assumes a producer or technical director will make the final tooling decisions and own the rollout. It organizes those decisions; it does not replace the human accountable for them.

## Sources reviewed

- https://github.com/PixarAnimationStudios/OpenUSD — universal scene description, the composition arcs, layering, variants, and references that anchor modern asset pipelines (Modified Apache-2.0)
- https://github.com/PixarAnimationStudios/OpenUSD-proposals — proposal repository documenting evolving conventions around assembly, variants, and instancing (Modified Apache-2.0)
- https://github.com/PixarAnimationStudios/OpenSubdiv — subdivision-surface evaluation referenced as the render-time evaluator pattern (Modified Apache-2.0)
- https://github.com/AcademySoftwareFoundation/MaterialX — material exchange format informing the lookdev publish-layer pattern (Apache-2.0)
- https://github.com/blender/blender — open production DCC, informing the integration pattern for tools that mix native and exchange formats (GPL-3.0; read for methodology only, no content copied)
- https://github.com/ynput/OpenPype — production-pipeline framework informing the publish/validate/manifest pattern (MIT)
- https://github.com/cgwire/awesome-cg-vfx-pipeline — curated index of pipeline components, used as a survey of categories (CC0)
- https://github.com/AcademySoftwareFoundation/OpenImageIO — image I/O library informing the texture-publish patterns (Apache-2.0)
