# Wave-4 Synthesis Report — Engineering: Real-Time Object Detection Deployment

Niche: **engineering — real-time object detection deployment methodology**.
Date: 2026-05-14.
Author: skillsgit-curated (synthesis agent).

## Files produced

- `realtime-detector-deployment-architect.skills.md` (v1.0.0) — production deployment architecture for an RT detector (model class choice, precision, batching, NMS strategy, post-processing, uncertainty fallback, observability, rollout).
- `detector-evaluation-rig-designer.skills.md` (v1.0.0) — offline and online evaluation regime (test-set portfolio, mAP/mAR/FPS, cohort and slice analysis, false-positive sweeps, drift signals, release gates).
- `detector-edge-deployment.skills.md` (v1.0.0) — edge-hardware deployment planning (vendor toolchain selection, conversion pipeline, INT8 calibration, per-layer profiling, dynamic resolution, thermal defences, per-device qualification, OTA security).

All three files include the mandatory safety disclaimer verbatim.
All three are `license_type: free` with no pricing.
All three use `category: engineering` with `niche:real-time-object-detection` as the first tag.

A fourth skill (`detector-data-pipeline`) was scoped as optional; it was not produced in this wave because the existing seed skill `robot-perception-test-suite-designer` and the new `detector-evaluation-rig-designer` already cover labelling discipline, leakage prevention, and cohort construction at the level a methodology-recovery wave should provide. Adding a third near-overlap would dilute discoverability without adding methodology. A separate "training-data pipeline" skill is a candidate for a later, training-side wave.

## Existing-skills overlap check

The existing seed `robot-object-detection-pipeline-reviewer` covers *review* of an in-place pipeline focused on robotics-perception consumers. The new skills are deliberately complementary: deployment architecture (forward design), evaluation rig (measurement infrastructure), and edge deployment (toolchain mechanics). No section was duplicated; cross-references between the new skills and the existing one are explicit in the "When to use" and "Limitations" sections of each file.

The existing seed `robot-perception-test-suite-designer` overlaps with the new `detector-evaluation-rig-designer` only at the abstract level (both design evaluation regimes). The new skill is purpose-built for general real-time detection (camera-first, multi-tenant, server and edge) whereas the existing skill is robotics-perception specific. The "When to use" sections direct buyers to the right one.

## Source-repo verification

All sources verified for licensing (Apache-2.0, MIT, BSD-3-Clause, BSD-2-Clause) and currency where applicable. Each skill cites 7–10 sources, comfortably above the 5–10 floor.

### Approved & used as sources (permissive)

| Repo | License | Used in skills |
| --- | --- | --- |
| NVIDIA/TensorRT | Apache-2.0 | 1, 3 |
| microsoft/onnxruntime | MIT | 1, 2, 3 |
| onnx/onnx | Apache-2.0 | 1, 3 |
| triton-inference-server/server | BSD-3-Clause | 1, 2, 3 |
| open-mmlab/mmdetection | Apache-2.0 | 1, 2 |
| PaddlePaddle/PaddleDetection | Apache-2.0 | 1, 2, 3 |
| openvinotoolkit/openvino | Apache-2.0 | 1, 3 |
| apple/coremltools | BSD-3-Clause | 1, 3 |
| pytorch/vision | BSD-3-Clause | 1, 2, 3 |
| cocodataset/cocoapi | BSD-2-Clause | 2 |
| nutonomy/nuscenes-devkit | Apache-2.0 | 2 |
| waymo-research/waymo-open-dataset | Apache-2.0 | 2 |

### Read-only for methodology study (copyleft / restricted; cited with explicit license tag)

| Repo | License | Use |
| --- | --- | --- |
| ultralytics/ultralytics | AGPL-3.0 | Methodology study only. No code, no trademarked names, no close paraphrase, no anchoring of the methodology on the family name in body content. Cited with `(AGPL-3.0; methodology study only; no code or trademarked names used)` tag. |

Per the wave-4 policy: previously-rejected GPL/AGPL repos may be READ for methodology and cited; the body content avoids brand and trademark anchors entirely.

## Methodology-vs-expression boundary checks

The following passes were performed on every body section:

1. **Brand and trademark anchors.** "YOLO", "Ultralytics", "MMDetection" do not appear in body content. Detector families are described generically — single-stage, two-stage, transformer-based set-prediction, anchor-based vs anchor-free. The Ultralytics reference appears only in the `## Sources reviewed` section with the explicit license tag.
2. **No prose copying or close paraphrase.** Every paragraph is original instructional prose written to a generic methodology. No README sentences, code comments, or documentation excerpts from any source were reused. The instructional structure (stages, gates, observability surface) reflects field convention, not the structure of any single source.
3. **No code.** No code blocks, no library function names, no command-line invocations. The closest the body gets to code is naming JSON output fields, which are generic schema and not copied from any source.
4. **Operator names and algorithm references.** Generic algorithm names (greedy NMS, soft NMS, intersection-over-union, mean average precision) are field terms of art and appear as generic methodology references, never with attribution to a specific repository.
5. **License-typed citations.** Every source in every `## Sources reviewed` block carries its license tag. The AGPL source carries the additional "methodology study only" qualifier.

## Methodology patterns extracted

Patterns that recur across the surveyed sources and that anchor the three skills:

1. **Latency-budget-first model selection.** Every mature deployment narrative begins with a stated latency budget and works the model class down to fit. The deployment-architect skill encodes this as Stage 2.
2. **Calibration with stratified representative data.** Every integer-precision deployment guide converges on the same recipe: stratified calibration set, per-channel weights, per-tensor activations, sensitive-layer protection. The edge-deployment skill encodes this as Stage 4.
3. **Dynamic batching with a bounded waiting window.** Multi-tenant serving stacks consistently bound the batch-collection window to a fraction of the latency budget with an early-flush rule. Encoded as deployment-architect Stage 6.
4. **NMS as a deployment knob, not a model knob.** Score floor, IoU threshold, and class-aware vs class-agnostic are deployment-time parameters tuned per consumer, not model-training parameters. Encoded as deployment-architect Stage 7.
5. **Cohort-stratified evaluation as the default.** Every modern detection benchmark publishes per-condition metrics, not just aggregates; deployment teams that do not stratify get caught by hidden weak cohorts. Encoded as evaluation-rig Stage 5.
6. **Latency histograms, not averages.** Mature inference stacks publish P50/P90/P99 because real-time consumers fail on tails. Encoded as deployment-architect Stage 11 and evaluation-rig Stage 7.
7. **Engine cache and warm-up.** Every accelerator-backed runtime has a non-trivial first-call cost; the cache and warm-up are deployment design decisions, not implementation details. Encoded as deployment-architect Stage 4 and 12, and edge-deployment Stage 3.
8. **Per-layer profiling on edge accelerators.** Vendor-blessed profilers expose per-layer latency and the operator coverage gap; mature edge deployments depend on them. Encoded as edge-deployment Stage 5.
9. **Thermal soak qualification.** Edge deployment regularly fails in the field because lab-benchmarked devices throttle under sustained operation; thermal soak in production housing is the canonical defence. Encoded as edge-deployment Stage 8.
10. **Drift monitoring as a first-class system.** Server and edge deployments alike depend on rolling input-side and output-side drift signals as the early warning when training-distribution drift is happening in the field. Encoded as deployment-architect Stage 11 and evaluation-rig Stage 11.

## Tag patterns

First tag is `niche:real-time-object-detection` on all three skills (required). Other tags chosen for discovery:

- Deployment architect: `inference`, `latency-budget`, `quantization`, `batching`, `nms`, `observability`, `deployment-architecture`.
- Evaluation rig: `evaluation`, `map`, `mar`, `regression-suite`, `edge-cases`, `drift-monitoring`, `release-gate`.
- Edge deployment: `edge-inference`, `int8-calibration`, `npu`, `mobile-inference`, `thermal-throttling`, `profiling`, `dynamic-resolution`.

## Confidence

- **High** on license verification. Each cited permissive repo was fetched and the license confirmed against the repo footer or LICENSE evidence. The AGPL source is explicitly tagged with its license and the methodology-study qualifier.
- **High** on the brand-and-trademark guard. The body content names no trademarked product family, no library, and no specific model name. The "AGPL repos may be cited with license tag" policy is honoured by the explicit tag in the source list.
- **High** on the safety disclaimer. The disclaimer appears verbatim in the body of every skill and is referenced from the closing sections.
- **High** on methodology coverage. The three skills span the deployment lifecycle (architect → evaluate → deploy to edge) without internal overlap.
- **Medium-high** on numeric defaults (latency thresholds, regression budgets, calibration set sizes). These are commonly cited operating points across the surveyed repos and the field, but every skill flags them as defaults to be confirmed by the user.
- **Medium** on long-tail edge cases for any specific deployment. The three skills are deliberately deployment-agnostic at the methodology level; users in highly regulated or exotic domains (medical, biometric, public-safety) need to extend the plans.

## No-overlap statement

No content from any cited repository has been copied, paraphrased, or close-paraphrased. The skills are original instructional prose. Citations exist for transparency and as methodology pointers for users who want to dig deeper into one approach. The AGPL source is cited only in source lists, with its license and "methodology study only" qualifier, and never anchors body content.
