---
id: skillsgit-curated/robot-object-detection-pipeline-reviewer
version: 1.0.0
name: Robot Object Detection Pipeline Reviewer
description: Review an object-detection inference pipeline for robots — model choice, quantization, latency budget, batching, NMS, tracking association, and false-positive mitigation.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: robotics
tags: [niche:robot-perception, object-detection, inference, quantization, nms, tracking, latency, false-positive, embedded-ai]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: []
  tools_optional: [web_search, code_execution, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - review my object detector
  - object detection on robot
  - quantize detector
  - detection latency
  - false positives robot
  - nms threshold
  - bytetrack vs sort
  - 3d detection pipeline
  - embedded inference review
  - detector to tracker
  - perception pipeline review
  - tensorrt detector
example_invocations:
  - "Review our 3D LiDAR detector for the warehouse AMR — is the latency budget safe and how do we reduce false positives on shelf legs?"
  - "We're moving from a server-class detector to an embedded NPU; review the quantization plan."
  - "Audit our detection-to-tracking handoff — we keep losing tracks across occlusion."
inputs:
  - name: pipeline_description
    type: text
    required: true
    description: Description of the current pipeline — input modality, model family, output type (2D/3D boxes, masks), framework, hardware, and any preprocessing/postprocessing steps.
  - name: deployment_constraints
    type: text
    required: false
    description: Latency budget, framerate, power envelope, target hardware (NPU/GPU/CPU), max memory, mission duration.
  - name: error_modes_seen
    type: text
    required: false
    description: Failure modes observed in the field — false positives, missed detections, identity switches, latency spikes, class confusion. Be specific.
  - name: data_pipeline
    type: text
    required: false
    description: Training data origin, label provenance, current dataset size, slice distribution, augmentation strategy, evaluation set.
  - name: tracker_description
    type: text
    required: false
    description: Tracker in use (IoU-association, deep-feature reID, Kalman-filter, JPDA, etc.) and its tuning.
outputs:
  - name: review_report
    type: markdown
    description: Structured review covering model, quantization, runtime, NMS, tracking, false-positive mitigation, and an action list with priorities.
  - name: report_json
    type: json
    description: Machine-readable findings with `findings[*]`, each having `area`, `severity`, `evidence`, `recommendation`, `effort`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Robot Object Detection Pipeline Reviewer

## When to use

Use this skill to audit an object-detection inference pipeline that already runs on a robot or is about to ship. The skill produces a structured review — not a redesign — identifying issues in model selection, quantization, runtime configuration, postprocessing, detection-to-tracking handoff, and false-positive mitigation. It assumes a working pipeline exists; for greenfield design choose the perception-stack-architect skill instead.

The skill is appropriate for 2D image detection (camera-only), 3D detection (LiDAR or LiDAR+camera fusion), instance segmentation, and panoptic stacks. It is appropriate for any deployment target (server, edge GPU, NPU, mobile CPU). It is not the right skill for training-loop debugging, dataset construction (use the perception-test-suite-designer), or general ML-experimentation planning.

**Mandatory safety disclaimer.** This skill produces methodology guidance. Perception failures in safety-critical robots can cause physical harm. Every recommendation must be validated in target operational design domains; never deploy a perception stack to safety-critical hardware without rigorous test coverage of edge conditions (weather, lighting, occlusion, sensor degradation).

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `pipeline_description` | yes | Establishes what is being reviewed. |
| `deployment_constraints` | no | Anchors latency, memory, power findings. |
| `error_modes_seen` | no | Targets the review at observed failures. |
| `data_pipeline` | no | Surfaces dataset-driven failure modes. |
| `tracker_description` | no | Enables review of the detection-to-tracking handoff. |

## How to apply

The skill walks a thirteen-stage review pipeline. Stages are mostly independent but later stages (tracking, false-positive analysis) depend on a clean picture from the earlier stages (preprocessing, runtime, postprocessing).

### Stage 1 — Restate the pipeline contract

1. Read `pipeline_description` and write a one-paragraph reconstruction: input topic and rate, preprocessing, model, postprocessing, output topic and rate, who consumes the output. If anything is ambiguous, ask before continuing. A reviewer who has not understood the pipeline cannot find its bugs.
2. State the *output contract*: schema of detections (2D box, 3D box, mask, class set), confidence semantics, frame the output is published in, timestamp policy (sensor capture time vs. inference completion time). Mismatches between the detector's frame-of-record and the consumer's expectation cause spectacular silent failures.
3. State the *upstream contract*: image format, colour space, exposure assumptions, ROS-topic queue depth, dropped-frame policy. Pipelines that silently drop alternate frames on backpressure get reviewed for tail-latency causing missed objects.
4. Pin the *failure budget*: at what false-positive rate, missed-detection rate, identity-switch rate, and latency budget does the pipeline cease to be acceptable? If the user has not declared this, propose defaults and flag them.

### Stage 2 — Review the model choice

5. Identify the model family: anchor-based (e.g. classic single-stage), anchor-free, transformer-based, point-cloud voxel, point-cloud point-based, multi-modal fusion. Each family has known operating regimes.
6. Identify the *backbone*. A backbone tuned for ImageNet pretraining and 224x224 inputs is not automatically good at 1280x720 robot cameras with motion blur. Question whether the backbone matches the data distribution.
7. Identify the *head*. Detection heads tuned for COCO-style class imbalance may underperform on robot-domain class distributions (where a single class is 99% of seen instances). Recommend re-balancing or focal loss tuning if class distribution is skewed.
8. Question whether the model receives the *resolution* it was trained at. Robots routinely change camera resolution after deployment and the inference resize crops fine detail; small objects evaporate.
9. Question whether the model was trained on *similar* viewing geometry. A model trained on dashcam viewpoints does badly when re-purposed for low-angle AMR cameras. Recommend either fine-tuning on robot-domain data or replacing the model.
10. Identify *single-modality models forced into multi-modal use* (a camera detector projected into 3D using flat-ground assumption) and the opposite (a 3D detector evaluated only on 2D metrics). Recommend re-aligning the metric with the deployed output.

### Stage 3 — Review preprocessing

11. Resize policy: does the pipeline letterbox or stretch? Letterbox is correct for aspect-preserving detection; stretch silently distorts geometry. Flag any pipeline that resizes via a non-aspect-preserving method without compensating in the postprocessing.
12. Normalization: confirm pixel-mean and standard-deviation are correct for the model. A model trained ImageNet-normalized but inferred with [0,1] inputs is undetectably bad on familiar objects and catastrophic on novel ones.
13. Colour space: BGR vs. RGB is a perennial source of detector silent failure. Confirm by inspecting visualizations of a known-good frame.
14. For point clouds, confirm voxelization parameters (voxel size, point limits per voxel) match training. A model trained at 5 cm voxels and inferred at 10 cm voxels behaves like a degraded model with no clear error signal.
15. Inspect the *temporal* preprocessing. If the model assumes temporal accumulation (multi-frame stacking, motion-compensated history), confirm the runtime supplies the right history with the right transforms. Pose-compensation errors degrade results subtly.

### Stage 4 — Review model export and quantization

16. For exported models (ONNX, TensorRT, TFLite, CoreML), confirm operator coverage. Operators that fall back to CPU silently slow the pipeline 10–100×. Recommend export verification and a benchmark of every layer's chosen kernel.
17. Quantization plan: identify whether weights are FP32, FP16, INT8, INT4, or mixed. For each quantized layer, identify the calibration data used. INT8 calibration with a non-representative dataset produces accuracy cliffs.
18. Per-channel vs. per-tensor quantization for weights; symmetric vs. asymmetric for activations. Mis-matched choice produces systematic class-specific errors.
19. Test the quantized model against a *quantization regression set* — a fixed, labelled set used only for quantization-vs-baseline comparisons. The regression must include hard examples and ODD edges, not only easy clean frames.
20. Confirm post-quantization the per-class average precision did not drop more than a stated tolerance. Quantization regressions concentrate in rare classes; check small-object AP specifically.
21. For accelerators with mixed-precision kernels (NPUs, NVDLA), confirm the operators that run in lower precision and the accuracy implication. Vendor documentation is often optimistic; benchmark.

### Stage 5 — Review runtime configuration

22. Batching: a robot pipeline rarely benefits from batch > 1 because batches add latency for a real-time consumer. Flag any inference path that batches across time steps without explicit consumer awareness.
23. Confirm GPU/NPU stream configuration: concurrent kernels, async copies, pinned memory. A pipeline that synchronizes the host on every frame loses 30–50% of available throughput.
24. Confirm camera-to-tensor DMA: zero-copy from sensor buffer to inference buffer is the difference between a 30 ms and a 60 ms end-to-end on embedded platforms. Flag any pipeline that runs an `np.array` copy or a colour-convert on the CPU host between camera and inference.
25. Confirm thermal headroom. Embedded inference benchmarks that show good latency at lab temperature collapse at field temperature. Recommend a sustained-load thermal test.
26. Confirm scheduling priority. Detection inference should run on isolated cores or with realtime priority; otherwise logging and visualization can introduce 50+ ms jitter spikes.
27. Confirm memory pool. Allocations during steady-state inference cause periodic spikes; pre-allocate buffers and bind to fixed addresses where the runtime supports it.

### Stage 6 — Review postprocessing — NMS and decoding

28. Confirm NMS variant: classical greedy NMS, soft-NMS, weighted-box-fusion, class-aware vs. class-agnostic. Class-aware is correct for most robot tasks; class-agnostic discards co-occurring different-class detections (a person carrying a box).
29. Confirm IoU threshold for NMS. Default 0.45–0.5 is fine for many domains but inadequate for crowded scenes (pedestrians at a forklift, vehicles in dense traffic) where it merges adjacent objects.
30. Confirm score threshold. Pipelines often use a global threshold; per-class thresholds (high recall for safety-critical classes like pedestrians, conservative for low-stakes classes) usually fit the deployment better.
31. For 3D detection, confirm BEV-NMS (Bird's-Eye-View NMS) vs. 3D-IoU NMS. 3D-IoU is more correct but more expensive; BEV-NMS is fine for ground-aligned objects.
32. For instance segmentation, confirm mask-NMS or mask-aware aggregation. IoU on masks is more discriminative than IoU on bounding boxes; pipelines that fall back to box-NMS lose precision.
33. Decode latency: postprocessing can dominate inference time on slow hosts (NMS on Python with thousands of candidates can take 20 ms). Confirm the postprocessing runs on the accelerator where supported.

### Stage 7 — Confidence calibration

34. Confirm confidence calibration. Modern detectors are routinely over-confident; a 0.9-score detection is not 90%-reliable. Recommend a calibration step (Platt scaling, temperature scaling, conformal prediction) when downstream consumers use the score as a probability.
35. Recommend reporting *both* a calibration-error metric (ECE) *and* a precision-at-fixed-recall metric in the regression suite. Score thresholds tuned without calibration drift over time as the data distribution shifts.

### Stage 8 — Detection-to-tracking handoff

36. Identify the tracker family: IoU-association (e.g. classical short-term), Kalman-filter-aided association, deep-feature reID, joint detection-tracking. Each handles occlusion and clutter differently.
37. Confirm the *association cost*. IoU-only fails when motion is fast or detections jitter; a cost combining IoU, motion-prediction distance, and appearance feature is more robust.
38. Confirm track lifecycle policy: how many frames of detection before a track is "born"; how many missed frames before "death"; how identity-confirmation is gated. Pipelines that flap (births and deaths every few frames on the same object) almost always have lifecycle thresholds tuned wrong.
39. For long-term occlusion, recommend an appearance-feature-based re-association component. Without it, ID switches across occlusion are inevitable.
40. For multi-class trackers, confirm class-consistency: once a track is born with class X, the associator should not silently flip it to class Y across a single frame. Flag pipelines that do not enforce class consistency through track history.
41. Confirm time-stamp alignment. A tracker that receives detections with stale or unsynchronized timestamps produces position-velocity estimates that are wrong by milliseconds × actor velocity — at 10 m/s and 50 ms skew, that's 0.5 m of phantom translation per track.
42. Confirm the tracker exposes *uncertainty*. The downstream planner needs to know not just the track position but its covariance, age, and association confidence. Flag pipelines whose tracker emits only point estimates.

### Stage 9 — False-positive mitigation

43. List the user-reported `error_modes_seen` and group them: hallucinated objects (FP), missed objects (FN), class confusions, identity switches, latency spikes.
44. For each FP class, hypothesize the cause and propose a test. Common causes: domain-shift edges (shelves and pallet legs look like people-legs to a person detector), lighting (a wet floor reflects a person and the detector fires on the reflection), out-of-distribution scenes (the robot enters a new aisle and the detector never saw it during training).
45. Propose multi-frame consistency gating: require a track to persist N frames before publishing. The cost is N frames of latency on real new objects; the benefit is silencing flickering FPs.
46. Propose modality cross-check: a detection that only fires in camera but not LiDAR (when LiDAR has clear line of sight) is suspect. Conversely, a LiDAR detection with no plausible camera evidence is suspect.
47. Propose a *negative-mining* loop: collect the FPs in production, label them, add to the training set. Pipelines without a feedback loop calcify their FP modes.
48. Propose explicit *masking zones*: regions of image or BEV where the detector's output is ignored (e.g. the robot's own forklift mast). Static masks resolve some FP categories without retraining.
49. Propose *confidence-by-region* thresholds: be stricter on the far-field where projections are noisy, looser on the near-field where the safety budget is tighter.

### Stage 10 — Missed-detection mitigation

50. For systematic FNs, identify the data slice: small objects, distant objects, partially occluded, motion-blurred, dark scene, unusual class. Pipelines miss the same way repeatedly.
51. Recommend tiling for small-object detection: instead of one resized inference of the full frame, infer on overlapping crops. Cost in latency, gain in small-object recall.
52. Recommend modality redundancy: if camera FN-rate is high in dark scenes, add a thermal or LiDAR cross-check on the same scene region.
53. Recommend score-threshold tuning per safety-criticality. For a pedestrian detector on a safety-critical platform the precision-recall operating point should be biased toward recall, with downstream FP filtering picking up the slack.

### Stage 11 — Latency budget audit

54. Build a *per-stage latency table*: image capture, DMA, preprocessing, inference, postprocessing, tracking, publish. Use measured (not nominal) numbers. Sum gives end-to-end latency.
55. Identify the *tail* (p95, p99) latency stage. A pipeline whose mean is 25 ms but whose p99 is 250 ms is dangerous; the p99 dominates safety reasoning.
56. Verify the latency budget under realistic load: at deployment temperature, with simultaneous logging and visualization running, on the actual platform — not a development workstation.
57. Recommend pipelining stages on a real-time scheduler so preprocessing of frame N+1 happens during inference of frame N. Single-threaded pipelines waste 30–50% of available throughput.

### Stage 12 — Findings and action plan

58. Group findings by area: model, preprocessing, quantization, runtime, postprocessing, tracking, FP mitigation, FN mitigation, latency. Within each, list findings with severity (`blocker`, `high`, `medium`, `low`) and evidence (a concrete observation, not a hunch).
59. For each finding, propose a recommendation with an effort estimate (`hours`, `days`, `weeks`) and an expected impact (latency delta, recall delta, ID-switch reduction). Recommendations without an effort estimate get ignored.
60. Prioritize: blockers must be resolved before deployment to the declared ODD; highs are tracked with an owner and a date; mediums are backlog; lows are documented.
61. Recommend a *regression-test addition* for any class of bug found, so the issue does not regress silently after a fix.

### Stage 13 — Compose the deliverable

62. Open with a one-paragraph "review intent" summary: what was reviewed, what the headline findings are, what the recommended next steps are.
63. Render the report as a markdown document with one section per area and an action-plan table at the end.
64. Emit `report_json` with the structured findings.
65. Close with the mandatory safety disclaimer and a "what this review does not cover" section pointing at the test-suite-designer and the perception-stack-architect skills.

## Outputs

The skill returns:

1. `review_report` (markdown) — structured review with findings and action plan.
2. `report_json` (JSON) — machine-readable findings list.

## Examples

**Input (placeholder):**

`pipeline_description`: "ROS 2 node receives 1280x720 RGB at 30 Hz from a forward camera; preprocesses via Python OpenCV (resize to 640x640, BGR-to-RGB, /255 normalization); runs an exported INT8 ONNX detector on an embedded NPU; postprocesses with Python NMS; publishes 2D detections; a downstream Python tracker associates by IoU and Kalman-filtered velocity."

`deployment_constraints`: "p95 end-to-end ≤ 100 ms; AMR moves at up to 1.5 m/s; embedded NPU with 4 GB shared memory."

`error_modes_seen`: "Persistent FPs on shelf legs labelled as 'person'. Track flicker in crowded aisles. Occasional p99 latency spikes to 350 ms during logging."

`data_pipeline`: "Trained on a mix of COCO + 8k labelled robot-camera frames; no rare-class balancing; eval on a held-out 1k frames."

`tracker_description`: "IoU + constant-velocity Kalman; track born after 3 hits, killed after 10 missing frames; no appearance feature."

**Findings (abbreviated):**

- **Blocker — runtime:** Preprocessing in Python on the host CPU contributes ~22 ms; under logging load it spikes to >200 ms, explaining the observed p99. Move preprocessing to the NPU's vendor preprocessor or to a native C++ node with pre-allocated buffers.
- **High — quantization:** INT8 calibration used only the held-out eval set; calibration data has no shelf-leg distractors. Re-calibrate using a representative robot-domain set including known FP scenes; re-run the regression and check pedestrian AP.
- **High — false positives:** Shelf-leg FPs match a domain gap. Mitigations: (a) negative-mining loop on production captures; (b) multi-frame persistence gate of 3 frames before publishing pedestrian tracks; (c) LiDAR cross-check (no LiDAR return in a person-sized box at expected distance → suppress).
- **High — tracking:** No appearance feature. Recommend a small reID head trained on robot-domain crops; switch association cost to weighted IoU + appearance distance; lifecycle thresholds tuned with the new cost.
- **Medium — postprocessing:** NMS in Python costs ~5 ms; move to the inference accelerator's batched-NMS plugin.
- **Medium — confidence:** Detector is over-confident; calibrate with temperature scaling on a representative validation set; emit calibrated scores to the tracker.
- **Low — masking:** Add a static mask covering the AMR's own near-field forklift profile so it is never a candidate.

**Output excerpt:** the markdown review plus a JSON `findings` array whose entries each include `area`, `severity`, `evidence`, `recommendation`, `effort`, and an optional `regression_test_to_add`.

## Limitations

- The skill reviews; it does not execute training or inference. Any recommendation needs validation against the user's actual numbers.
- Severity ratings are heuristic. The user's safety case is the authoritative ranking.
- Some hardware-specific recommendations (NPU plugin operator coverage, vendor preprocessor) are platform-specific; the skill flags the category but the user must check vendor docs.
- The review assumes the pipeline is functioning at some level; pipelines that crash on launch or never produce output need debugging, not review.
- The skill does not benchmark; it relies on user-supplied measurements. Recommend the user produce measured latency tables before the review pass.
- For multi-camera or multi-LiDAR fusion detectors, the review touches the fusion at a high level only; deep fusion-architecture review belongs in the perception-stack-architect skill.

## Sources reviewed

- https://github.com/opencv/opencv
- https://github.com/pytorch/vision
- https://github.com/open-mmlab/mmdetection3d
- https://github.com/autowarefoundation/autoware
- https://github.com/NVIDIA/TensorRT
- https://github.com/isl-org/Open3D
- https://github.com/IntelRealSense/librealsense
