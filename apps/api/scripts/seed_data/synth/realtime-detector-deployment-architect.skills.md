---
id: skillsgit-curated/realtime-detector-deployment-architect
version: 1.0.0
name: Real-Time Detector Deployment Architect
description: Architect a production deployment of a real-time object detector — model class choice by latency budget, quantization, batching, NMS strategy, post-processing, uncertainty fallback, and observability.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:real-time-object-detection, inference, latency-budget, quantization, batching, nms, observability, deployment-architecture]
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
  estimated_tokens_per_invocation: 8500
trigger_keywords:
  - real-time detector deployment
  - object detection latency budget
  - detector quantization strategy
  - dynamic batching detector
  - nms strategy
  - detector post-processing
  - detector uncertainty fallback
  - detector observability
  - single-stage vs two-stage detector
  - detector inference pipeline architecture
  - production detection service
  - detector reliability
example_invocations:
  - "We need to deploy a video object detector at 30 FPS on a single GPU server — architect the inference pipeline end to end."
  - "Design a deployment for a body-worn safety camera that flags hazards under 100 ms on-device."
  - "Plan the production architecture for a multi-tenant detection API with mixed latency and throughput tiers."
inputs:
  - name: detection_task
    type: text
    required: true
    description: What is being detected, image source (video stream, still images, batch), expected scene types, number of classes, and consumer of detections (alert, controller, downstream analytics).
  - name: latency_and_throughput_budget
    type: text
    required: false
    description: End-to-end latency target (P50/P95), required frames-per-second per stream, number of concurrent streams or requests per second.
  - name: hardware_target
    type: text
    required: false
    description: Server class, GPU/NPU/CPU presence, memory envelope, whether on-device, on-edge, or in cloud, and any multi-tenant constraints.
  - name: accuracy_constraints
    type: text
    required: false
    description: Minimum acceptable mAP / recall at a given precision, per-class minimums, safety-critical classes that must not be missed.
  - name: operational_constraints
    type: text
    required: false
    description: Privacy, data-retention, offline operation, regulatory framework, on-call coverage, rollback expectations.
outputs:
  - name: deployment_design
    type: markdown
    description: Architecture document covering model class choice, preprocessing, batching, quantization, post-processing, fallback policy, and observability.
  - name: design_json
    type: json
    description: Structured plan with `model`, `runtime`, `batching`, `nms`, `post_processing`, `fallback`, `observability`, `risks`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Real-Time Detector Deployment Architect

## When to use

Use this skill when an engineering team is about to deploy, or is replanning, a production object-detection inference pipeline that must run under a stated latency or throughput budget. The skill produces a written deployment architecture covering model-class choice, preprocessing, batching, numeric precision, post-processing including non-maximum suppression, an uncertainty fallback, and the observability surface that lets operators tell a healthy pipeline from a degraded one. The output is the design document and a structured plan, not training code, not a tuned model, and not a final library selection.

This skill is the right pick at three moments: greenfield deployment where the team has a trained detector and needs to turn it into a service or on-device component; a hardware or precision migration where an existing model must move to a new runtime or precision tier; and a post-incident review where the deployed pipeline has shown latency regressions, recall regressions, or runaway false positives and the team wants a structured redesign rather than a patch. It is not the right skill for designing training data (see the data-pipeline skill), for designing evaluation cohorts (see the evaluation-rig skill), or for the edge-toolchain mechanics of a specific accelerator (see the edge-deployment skill).

**Mandatory safety disclaimer.** This skill produces methodology guidance. Real-time detection failures in safety-critical contexts can cause physical harm, financial loss, or violations of individual rights. Every recommendation must be validated in the target operating envelope; never deploy a detector to a safety-critical context without rigorous test coverage of edge conditions (illumination, weather, occlusion, distribution shift), explicit human-in-the-loop policy where appropriate, and a documented fallback when the pipeline is uncertain or degraded.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `detection_task` | yes | Anchors model class, output schema, and consumer contract. |
| `latency_and_throughput_budget` | no | Bounds the model size, precision, and batching policy. |
| `hardware_target` | no | Determines runtime, plugin set, and memory plan. |
| `accuracy_constraints` | no | Drives precision-vs-recall trade-offs and post-processing thresholds. |
| `operational_constraints` | no | Shapes the observability and fallback policy. |

## How to apply

The skill walks a fifteen-stage pipeline. Stages are mostly sequential because each downstream decision narrows the next. The post-processing and fallback stages feed back into the model-class stage when a constraint cannot be met, so plan one or two design iterations rather than a single pass.

### Stage 1 — Restate the detection contract

1. Read `detection_task` and rewrite it as a one-paragraph contract in the form: "Given <input modality> at <rate> from <source>, the pipeline must produce <output schema> with <accuracy floor> within <latency budget>, consumed by <downstream system> for <decision>." If any clause is empty or vague, stop and ask the user to fill it. A contract with "indoor camera" instead of "fixed 1080p ceiling camera in a warehouse with mixed fluorescent and skylight lighting" leads to a wrong design.
2. Distinguish between *event detection* (the pipeline raises an alert when an object appears), *stream detection* (the pipeline emits detections every frame), and *batch detection* (the pipeline scores a backlog of images or video). Each maps to a different batching, post-processing, and observability shape.
3. List the *output schema* fields: class id, class label, confidence, bounding box (axis-aligned or rotated), instance id if tracked, optional attributes (orientation, depth, keypoints, segmentation mask). The schema is the contract the downstream consumer locks to.
4. List the *unacceptable failures*. Missed-detection on a safety-critical class is one kind of failure; false-positive that triggers a costly downstream action is another; latency spike past the budget is a third. Each becomes a watch-item in Stage 13.

### Stage 2 — Choose the detector class

5. Map the contract to a detector family. Three families dominate the field: single-stage detectors that emit dense predictions in one pass (favoured for tight latency budgets and modest class counts), two-stage detectors that first propose regions then classify them (favoured for high accuracy on small or rare objects with relaxed latency), and transformer-based detectors that set-predict object queries (favoured for crowded scenes or end-to-end training but with attention-cost considerations on long sequences). Choose the family before the specific model.
6. Decide *anchor-based* vs *anchor-free* heads within the family. Anchor-free heads simplify deployment because there are no anchor-tuning knobs to maintain; anchor-based heads still win on certain class-imbalanced or extreme-aspect-ratio tasks. Document the decision and the reason.
7. Decide *fixed-resolution* vs *multi-resolution* inference. Multi-scale inference improves recall on small objects at the cost of additional forward passes. For tight latency budgets prefer a single resolution sized to the smallest object the contract requires plus a safety margin.
8. State the *parameter and FLOP envelope*. A first-pass guess: the latency budget per frame divided by the per-flop cost on the target hardware sets the FLOP ceiling. If no candidate model fits, either relax the budget, drop a stage, or move to a smaller model class.

### Stage 3 — Decide numeric precision and quantization plan

9. Pick the *baseline precision*. Most modern detectors deploy at half precision on GPUs; integer-8 on edge or CPU; mixed precision when a layer family is unstable in lower precision. The baseline is the precision that meets the latency budget without sacrificing measurable accuracy.
10. Plan *post-training quantization* if integer precision is needed. The plan must include: a representative calibration set of several hundred images covering the operating distribution; a calibration algorithm (per-channel symmetric for weights, per-tensor for activations is a common starting point, with histogram-based calibrators where required); an evaluation pass that compares accuracy at full precision against the quantized model on a held-out set; and a rollback if drop exceeds tolerance.
11. Plan *quantization-aware training* if post-training drop exceeds tolerance. The plan documents the additional training cost and the version-control discipline for the QAT artifact.
12. Identify *sensitive layers* that must stay at higher precision. Detection heads with sharp activations, normalization layers, and the final score-and-box prediction layer often need protection. The runtime must support mixed-precision execution if the precision plan calls for it.
13. State the *regression budget*. A typical operating point is "no class loses more than half a percentage point of average precision, no class with safety-critical status loses any". Pin the numbers in the plan so the team has a stop-the-line trigger.

### Stage 4 — Choose the runtime and graph format

14. Pick the *exchange format*. A portable graph format gives the team flexibility to move between runtimes without retraining; vendor-specific formats squeeze out additional performance at the cost of lock-in. For multi-target deployments, prefer the portable format as the source of truth and treat the vendor build as a derived artifact.
15. Pick the *runtime*. On server-class GPU the choice is between a tensor-compiler runtime (best raw throughput, more build-time complexity), a portable accelerated runtime (decent throughput, simpler ops), and a framework-native runtime (simplest pipeline, lowest peak throughput). On CPU the choice is between a vectorized portable runtime and a vendor toolkit. On NPU or DSP the choice is the vendor toolkit. Document the trade.
16. Pin the *opset and version* of the exchange format. Build pipelines must reject artifacts at unknown opsets. The plan documents how a model is promoted from training opset to deployment opset, and what regression tests gate that promotion.
17. Plan *compiled-engine caching*. Many runtimes build a hardware-specific plan the first time they see a model; this can take seconds to minutes. The plan documents where engines live, how they are keyed by hardware and driver version, and what happens on a cold start.

### Stage 5 — Preprocessing pipeline

18. Specify *decode* — whether frames arrive pre-decoded, whether the pipeline decodes JPEG or H.264 itself, and whether decode runs on the same accelerator as inference. Co-locating decode with inference on the GPU avoids host-to-device copies but consumes capacity.
19. Specify *resize and pad*. The model expects a fixed input size; the preprocessing must letterbox or stretch consistently. Document the resampler (bilinear, bicubic, area), the padding colour, and the aspect-ratio policy. The same preprocessing must run at training and inference; mismatches silently lose accuracy.
20. Specify *colour-space conversion and normalization*. State the channel order (RGB vs BGR), the mean and standard deviation, and whether the input is scaled to a fixed range. Pin these as constants in the deployment artifact, not as defaults assumed by the runtime.
21. Specify *frame-rate matching* when the input stream rate differs from the inference rate. Drop policy (drop the newest frame, drop the oldest, drop on a schedule) affects observed latency; freeze policy affects observed false negatives.
22. Specify *region-of-interest* preprocessing if the camera covers a fixed scene and the consumer cares only about a sub-region. Cropping to the relevant region before inference reduces compute and false positives but introduces a calibration-drift risk if the camera shifts.

### Stage 6 — Batching strategy

23. Decide *static* vs *dynamic* batching. Static batching uses a fixed batch size every step; it minimizes scheduling overhead but wastes capacity when load is below saturation. Dynamic batching waits up to a tunable window for additional requests, trading a small latency penalty for throughput; it is the default for multi-tenant or many-stream services.
24. Set the *maximum batch size* by GPU memory headroom plus runtime kernel-launch overhead. Beyond a point, additional batch size buys little throughput because compute saturates; below that point, throughput scales near-linearly.
25. Set the *batch-collection window* for dynamic batching. The window must be a small fraction of the latency budget so the worst-case waiting time is bounded. A typical default is a tenth of the budget with an early-flush rule when the batch reaches the maximum.
26. Decide *per-stream sticky batching* for video. Frames from the same stream often share preprocessing context (tracker state, region-of-interest mask) and benefit from being scheduled together.
27. State the *backpressure policy*. When the queue grows beyond a threshold the pipeline must shed load explicitly — drop frames, reject requests, or hand back to a slow-path queue — not silently degrade.

### Stage 7 — Post-processing and non-maximum suppression

28. Pick a *post-processing topology*. Three patterns dominate: on-accelerator (the NMS runs on the same device as inference via a plugin or operator), on-host CPU (the model returns raw outputs and the host filters), and on-streamer (a downstream service consolidates detections across frames). On-accelerator wins when the operator is well-supported and host-device copies are dominant; on-host wins for portability and ease of debugging.
29. Choose the *NMS algorithm*. Standard greedy NMS sorts by score and suppresses overlapping boxes above an IoU threshold. Soft variants reduce the suppressed score rather than dropping the box, which improves recall in crowded scenes. Class-aware NMS suppresses only within the same class; class-agnostic NMS suppresses across classes. Pick the variant that matches the contract: crowded-scene applications usually want a soft or score-decay variant, single-instance-per-region applications want class-aware standard.
30. Pin the *IoU threshold* and the *score threshold* as deployment constants tied to a calibration run, not picked from a paper. Lowering the score threshold buys recall at the cost of false positives and runtime; the trade is application-specific.
31. Specify *top-k pre-filtering* before NMS to bound the worst-case compute. A typical default is a few hundred candidates per class; values much higher rarely change the result and inflate latency tails.
32. Specify *box decoding* — whether the model emits absolute coordinates, anchor-relative offsets, or normalized coordinates. The decoder must invert exactly what the model produces; a mismatch produces silently shifted boxes.
33. Specify *output coordinate normalization* — whether the consumer expects pixel coordinates in the original frame, in the resized frame, or in a normalized [0,1] range. Apply the inverse of the preprocessing transform so the consumer sees the original-image frame.

### Stage 8 — Temporal aggregation and tracking handoff

34. Decide whether the deployment includes *temporal aggregation*. A per-frame detector that hands raw detections to a downstream consumer makes a different contract than one that emits stable tracks. For event-detection use cases, a debouncing aggregator that waits for N-of-M consecutive frames before raising an alert reduces false positives substantially.
35. Decide whether to include a *tracker* in the pipeline. The tracker adds stateful complexity and changes the failure surface — track identity switches, false continuations across occlusion. If a tracker is included, document the association cost function (intersection over union, embedding distance, motion-model gating), the lifetime policy (birth, confirmed, lost, deleted), and the maximum gap the tracker tolerates without losing identity.
36. Document the *detection-to-track handoff schema*. Each detection enters the tracker with a class, a confidence, a box, and a timestamp; each track exits the tracker with an identity, a smoothed state, and a confidence band. The output of the pipeline is one or the other, not both blended ambiguously.

### Stage 9 — Uncertainty fallback

37. Define what *uncertain* means for this pipeline. Useful indicators include: low maximum class probability, high entropy across classes, low intersection-over-union among overlapping high-score boxes (the model disagrees with itself), measured precision-on-this-stream falling below the calibrated operating point, agreement-score with a secondary verifier model dropping below threshold.
38. Define what the pipeline does when uncertain. Options ordered by escalation: emit the detection with an explicit `uncertain` flag for the consumer to filter; suppress the detection and emit nothing; run a slower, more accurate model on the same frame and use its answer; route the frame to a human-in-the-loop queue; trigger a safe-stop or fail-safe in the downstream system.
39. Define the *budget* for the fallback. A slow-path model that runs on a small fraction of frames is acceptable; one that runs on most frames defeats the latency budget. The plan caps the fraction and documents what happens when the cap is exceeded (alert, throttle, refuse new work).
40. Define the *human review escalation* if the consumer is safety-critical. Pin the queue, the response SLA, and the post-review feedback loop that updates the training corpus with corrected labels.

### Stage 10 — Concurrency, isolation, and multi-tenancy

41. Decide the *number of model instances* per accelerator. Multiple instances increase throughput when each instance underuses the device; they increase latency variance when contention rises. The plan documents the instance count, the memory budget per instance, and the contention model.
42. Decide the *priority model*. In multi-tenant services, latency-sensitive traffic shares hardware with throughput-oriented traffic. The runtime must support priorities or the deployment must shard across separate devices.
43. Decide whether to run *preprocessing on a separate executor* from inference. Preprocessing-bound workloads benefit from this separation; inference-bound workloads do not.
44. Plan *graceful shutdown*. The deployment must drain in-flight requests, persist any required state, and reject new work cleanly during a rolling update.

### Stage 11 — Observability surface

45. Pin the *latency histogram* per stage: decode, preprocess, inference, post-process, publish. Aggregate latencies hide the bottleneck; per-stage histograms expose it. Publish P50, P90, P99, and the maximum.
46. Pin the *load metrics*: requests per second, frames per second per stream, queue depth at each boundary, accelerator utilization, host CPU utilization, host memory, accelerator memory.
47. Pin the *quality signals*: rolling per-class detection rate, rolling false-positive proxy (high-score detections in known-empty regions, if available), rolling agreement with the secondary verifier when one exists, rolling NMS suppression rate (a sudden drop in suppressions can indicate a saturated score head).
48. Pin the *drift signals*: input-distribution moments (mean colour, edge density, brightness percentiles) compared against the training-data baseline; a sustained drift triggers a re-evaluation cycle.
49. Pin the *integrity signals*: model checksum, runtime version, opset, hardware identifier, build identifier. Every emitted detection carries the build it came from for forensic traceability.
50. Pin the *log-and-record policy*: which frames are persisted, for how long, under what privacy and retention rules. Cameras in regulated contexts require a stricter, documented policy.

### Stage 12 — Reliability and rollout

51. Decide the *rollout strategy*: canary on a fraction of streams or tenants, shadow-traffic comparison against the incumbent, blue-green swap with a documented rollback trigger.
52. Decide the *health-check semantics*. A liveness check confirms the process is up; a readiness check confirms the model is loaded and the warm-up pass has succeeded; a deep-health check verifies a known-good test image produces a known-good result within the latency budget.
53. Plan *warm-up*. Many runtimes show outlier latency on the first request after load; the warm-up runs N inference passes before traffic is admitted to absorb the JIT or kernel-build cost.
54. Plan *cold-start recovery*. After a crash, the supervisor restarts; the engine cache must survive the restart or the recovery time exceeds the budget. Persist engines outside the process and key them by hardware and runtime version.

### Stage 13 — Risk register and acceptance gates

55. Enumerate cross-cutting risks: input drift not detected, quantization regression on a rare class, NMS threshold tuned to one dataset but deployed to another, batching window starves a low-rate stream, fallback path used more than budgeted, observability surface incomplete, no rollback path. Each risk has an owner, a mitigation, and a verification step.
56. Specify the *go-live gates*. Common gates: accuracy regression test against the training-side baseline; latency budget met at the agreed load; soak test for several hours with no leak or drift; rollback rehearsal documented; on-call runbook reviewed.
57. Specify the *trigger conditions for stop-the-line*. Examples: P99 latency exceeds 1.5x budget for a sustained window; per-class precision drops below floor; agreement with verifier falls; cold-start recovery exceeds budget. Each trigger has a documented response.

### Stage 14 — Lifecycle and retraining

58. Define the *retraining trigger*. Sustained drift, a new operating environment, a new class, or a regulatory change triggers a retrain. Pin the data, the budget, and the evaluation gate up front so retraining is reproducible.
59. Define the *deprecation policy*. Old engine artifacts persist for rollback; old models in long-running services are replaced on a schedule, not on a whim.
60. Define the *labelling feedback loop*. Detections flagged by the fallback or by post-deployment review feed back to the training set with explicit provenance.

### Stage 15 — Compose the deliverable

61. Open with a "deployment intent" paragraph: what the pipeline must detect, at what budget, on what hardware, with what fallback.
62. Render the design as a markdown document organized by the stages above. Include a per-stage budget table for latency and a per-stage table for throughput.
63. Emit `design_json` with structured fields: `model`, `preprocessing`, `runtime`, `batching`, `nms`, `temporal`, `fallback`, `concurrency`, `observability`, `rollout`, `risks`, `gates`.
64. Close with the mandatory safety disclaimer restated, an "open risks" list, and pointers to the evaluation-rig skill, the edge-deployment skill, and the data-pipeline skill for adjacent decisions.

### Stage 15.1 — Multi-model ensembles and verifier chains

When a single model cannot meet the accuracy floor at the latency budget, the deployment may run a chain of models. A common pattern is a fast primary that produces candidate detections, followed by a slower verifier that re-scores low-confidence or high-cost candidates. The chain has its own design decisions: which detections go to the verifier, what budget the verifier consumes, how disagreements are resolved, and how the chain is observed end-to-end. The plan documents the routing policy, the verifier's input contract, the merge logic that produces the final detection, and the fallback when the verifier itself fails.

A. *Routing*. Common routing rules: route below a score threshold; route on a specific class; route on a region-of-interest match; route on an out-of-distribution score. The routing rule is part of the deployment contract.
B. *Budget*. The verifier runs on a fraction of detections; the plan caps the fraction and documents what happens when the cap is exceeded. A verifier that runs on every frame defeats the latency budget; one that runs on too few defeats its purpose.
C. *Merge*. The verifier's output may *replace*, *augment*, or *veto* the primary's output. The plan picks one per class and documents the rationale.
D. *Observation*. The disagreement rate between primary and verifier is a quality signal; sudden drift in disagreement indicates a problem in either model. The rig publishes the disagreement rate alongside the primary metrics.

### Stage 15.2 — Streaming versus request-response semantics

Detection pipelines come in two consumption shapes. A streaming pipeline ingests an unbounded sequence of frames from a producer it does not control and emits a parallel stream of detections; a request-response pipeline accepts discrete requests, each containing one or a few images, and returns the detections. The semantics differ in how backpressure is handled, in how cold starts are amortized, in how budget is measured, and in how observability is shaped. The plan picks one and documents the contract.

A. Streaming consumers care about *frame-to-frame latency variance*; request-response consumers care about *per-request latency distribution*.
B. Streaming consumers tolerate frame drops only when they are signalled; silent drops are a contract violation.
C. Request-response consumers may need *batch endpoints* for offline analysis; the plan documents whether the same model serves both shapes and what isolation prevents one workload from starving the other.

### Stage 15.5 — Capacity planning and load modelling

A deployment plan is not complete without an explicit capacity model. The model answers two questions: how many requests per second can a single instance sustain at the budgeted latency, and how does the system scale beyond that. The capacity plan documents the saturation point measured under realistic load (including preprocessing, post-processing, observability, and any background work), the headroom margin above the expected steady-state load, the burst-handling policy, and the horizontal scaling story (whether by replicating instances, sharding by tenant, or partitioning by stream). The plan also documents the *fan-out* limit — the maximum number of concurrent streams a single instance is willing to serve before the dynamic-batching window or the queue depth violates the latency contract — and the *fan-in* limit when multiple producers feed one instance. Capacity that is theoretical only is not capacity; measured saturation is what matters.

A. Establish a *load profile*: the expected distribution of requests over time, including diurnal patterns, event-driven spikes, and the relationship between the load profile and the latency budget. A deployment that meets its budget at the average load but not at the peak is not deployable without a smoothing layer or an explicit overload policy.
B. Measure *headroom*. Run the deployment at progressively higher load and record the latency-vs-load curve. Mark the point at which the budget is no longer met; the deployment runs at no more than a fraction of that capacity in production to absorb noise and growth.
C. Document the *scaling unit*. If the deployment scales by adding instances, the cost-per-instance and the lead time to add one are part of the plan; if it scales by adding accelerators within an instance, the saturation behaviour at high accelerator counts is part of the plan.

### Stage 15.6 — Disaster recovery and degraded modes

71. Define the *degraded operating modes* explicitly. Common modes: a smaller, lower-accuracy model when the primary is unavailable; a CPU-only path when the accelerator is missing; a "store-and-forward" mode where the device captures inputs locally and processes them when the primary path returns. Each mode has a documented accuracy and latency profile.
72. Define the *triggers* into and out of each mode. A primary-engine load failure is one trigger; an accelerator-driver crash is another; sustained latency-budget violation is a third. The plan documents what counts as recovery and how long the system stays in the degraded mode before re-attempting the primary path.
73. Define the *user-visible signal* when the system is degraded. A consumer that does not know the system is degraded cannot make safe decisions. The signal is part of the contract.

### Cross-cutting concerns the stages reference

65. *Score calibration*. A model's score is not a probability unless it has been calibrated; the post-processing and fallback stages depend on the score-to-probability mapping being well-behaved. Document whether the deployment ships with a calibration map (temperature scaling, isotonic regression, or a Platt fit) and how that map is re-fitted when the model is retrained. If the deployment relies on absolute score thresholds (Stage 7), an uncalibrated drift in score distribution silently shifts the operating point.
66. *Tie-breaking determinism*. Two candidate boxes with equal scores after NMS must produce the same decision on every replay or downstream consumers cannot reproduce a frame. The plan documents the tie-break rule (lexicographic on coordinates, deterministic random seed, or earliest-emitted) and the runtime guarantee that ordering is stable across runs.
67. *Numerical precision boundaries*. Different stages of the pipeline operate at different precisions. Preprocessing may run at integer, inference at half precision, post-processing at full precision. Each cast is a place where rounding behaviour differs across hardware. The plan documents the cast points and the tolerance the verification step uses for output-equivalence checks.
68. *Coordinate-frame discipline*. Detections may be expressed in image pixels, in normalized image coordinates, in camera coordinates, or in a downstream world frame. The plan picks one frame at every interface and documents the transforms between them. Mismatched frames produce silently misaligned downstream actions.
69. *Time discipline*. Each detection carries a timestamp; the timestamp must be sourced consistently (frame-capture time, model-completion time, publish time) and the choice is the consumer's contract. Streaming consumers that compare detections across time-aware boundaries depend on this.
70. *Failure isolation*. If preprocessing fails for one frame, the rest of the pipeline must continue with the next frame; if the inference engine crashes, the supervisor restarts it without affecting unrelated pipelines on the same host. The plan documents the isolation boundaries and the failure-recovery time for each.

## Outputs

1. `deployment_design` (markdown) — full deployment architecture document.
2. `design_json` (JSON) — structured plan suitable for downstream automation and review tools.

## Examples

**Input (placeholder):**

`detection_task`: "Detect people, vehicles, and unattended packages in a fixed 1080p outdoor camera feed; emit alerts to a control-room dashboard."

`latency_and_throughput_budget`: "End-to-end alert latency under 400 ms P95; one camera per worker; up to 32 cameras per server."

`hardware_target`: "Single mid-range GPU per server, 16 GB device memory, x86 host with 16 cores."

`accuracy_constraints`: "Recall on people at least 0.95 at precision at least 0.85; no missed person near the perimeter line."

`operational_constraints`: "On-premises only; per-camera retention rules vary; rollback within five minutes."

**Plan (abbreviated):**

- Detector class: single-stage anchor-free detector at fixed 640-pixel input; standard precision half on the GPU; mixed precision around the prediction head to protect score calibration on the safety-critical class.
- Runtime: portable graph format as source of truth; vendor tensor-compiler engine as derived artifact, cached per hardware-driver-build triple; engine warm-up of ten inferences during readiness probe.
- Preprocessing: GPU-side decode, letterbox to 640, RGB normalization with pinned constants, region-of-interest crop applied per camera from a versioned mask.
- Batching: dynamic batching with maximum batch size eight and a thirty-millisecond window; per-camera sticky scheduling; explicit backpressure drops oldest frame when per-camera queue exceeds two frames.
- Post-processing: on-host class-aware soft NMS with a calibrated score floor of 0.35 and IoU threshold 0.5; top-200 pre-filter per class; box decode followed by inverse letterbox into original frame coordinates.
- Temporal aggregation: three-of-five frame debouncer for the perimeter-line alert class; no debouncing for vehicle class because the downstream consumer handles it.
- Fallback: when the per-frame maximum class probability is below 0.55 and the box overlaps the perimeter line, the frame is re-scored by a larger verifier model running on a small fraction of the budget; if the verifier still disagrees, the alert is raised with the `uncertain` flag and routed to human review.
- Observability: per-stage latency histograms, per-class rolling detection rate, drift on input mean brightness and edge density, model checksum and build id stamped on every alert.
- Rollout: blue-green at the camera-group level; canary on two cameras for twenty-four hours before fleet rollout; rollback trigger if P99 latency exceeds 600 ms for ten consecutive minutes or per-class recall on the shadow set drops by more than half a percentage point.

**Output excerpt:** the markdown design plus a JSON object whose `nms` field carries `{algorithm, iou_threshold, score_threshold, top_k, class_aware, on_device}` and whose `fallback` field carries `{trigger_signals, action, budget_fraction, escalation}`.

**Second example (placeholder):**

`detection_task`: "Detect printed-circuit-board defects on a moving conveyor — classes are missing-component, misaligned-component, solder-bridge, and unknown-anomaly; the line speed is fixed and the camera is calibrated."

`latency_and_throughput_budget`: "Per-image latency under 12 ms P99; sustained 80 frames per second; one workstation per line."

`hardware_target`: "Industrial workstation with a single mid-range GPU, 8 GB device memory, isolated network."

`accuracy_constraints`: "Recall on each defect class at least 0.99; false-positive rate budgeted at less than 0.5 percent per inspected board because false rejects are expensive."

`operational_constraints`: "Air-gapped facility; model updates delivered by USB; full audit trail required for every flagged board."

**Plan (abbreviated):**

- Detector class: small single-stage anchor-free detector with a fine-grained classification head fed from cropped region proposals; trained at half precision and deployed at half precision to preserve the score head's calibration; the unknown-anomaly class is handled by an out-of-distribution score derived from feature-space distance rather than a dedicated detector head.
- Runtime: vendor tensor-compiler engine targeting the workstation GPU; engine cached on local disk and signed; warm-up of fifty passes during the morning shift-start procedure to absorb compilation cost.
- Preprocessing: fixed-region crop tied to the calibrated conveyor pose; bilinear resize to the model's expected input; channel order and normalization pinned; no augmentation at inference time.
- Batching: static batching at four images because the line rate is predictable and dynamic batching offers no benefit; static batches simplify the latency-tail story.
- Post-processing: on-host class-aware standard NMS with a tight IoU threshold of 0.3; top-100 pre-filter; box decode followed by inverse crop into the original frame; per-class score thresholds calibrated against a held-out validation set.
- Temporal aggregation: not applicable for single-image inspection; the consumer sees one decision per board.
- Fallback: when the maximum class probability is below 0.7 or the out-of-distribution score exceeds threshold, the board is routed to a human inspector queue with the full crop and the model's top-three guesses; the fallback fraction is monitored to detect drift.
- Observability: per-class detection rate, fallback rate, per-stage latency, model build identifier stamped on every audit record.
- Rollout: model updates staged on a single line for forty-eight hours of soak before fleet rollout; the air-gapped delivery protocol includes a signed manifest and a first-run benchmark against a fixed test board.

**Third example (placeholder):**

`detection_task`: "Detect lane markings, vehicles, pedestrians, and traffic signs on a moving development vehicle equipped with multiple cameras; consumer is the perception stack of a partially-automated driving system; safety-critical."

`latency_and_throughput_budget`: "Per-camera frame latency below 50 ms P99; eight cameras at 20 frames per second each; jitter below 5 ms; cold-start within 3 s after ignition."

`hardware_target`: "Automotive-grade compute module with one accelerator per camera pair, ASIL-rated power and thermal envelope."

`accuracy_constraints`: "Recall on pedestrians at least 0.99 at precision 0.95 across day, night, rain; recall on stop signs at least 0.999 across all conditions; no class regression beyond a tenth of a percent from the qualified baseline."

`operational_constraints`: "Functional-safety framework applies; every release goes through hazard analysis; rollback within thirty seconds; recordings retained for incident review under documented privacy controls."

**Plan (abbreviated):**

- Detector class: two-stage detector for distant small classes (signs, pedestrians at range), single-stage detector for near-field obstacle classes; transformer-based set-prediction was considered and rejected because the attention cost over multiple cameras did not fit the latency budget on the qualified hardware.
- Precision: half precision on the backbone, full precision on the detection head, integer-8 considered only for the backbone if the calibration regression budget is met across all safety-critical cohorts; quantization-aware training is the default rather than post-training calibration because the regression budget is tight.
- Runtime: vendor tensor-compiler engine; engine cached and signed; warm-up runs during the vehicle's pre-drive self-test sequence and is gated by a deep-health probe.
- Preprocessing: per-camera ISP configuration version-pinned; letterbox to the model input; calibrated geometric transforms applied so detections land in vehicle coordinates downstream.
- Batching: per-accelerator static batching at two cameras per accelerator; jitter is more important than aggregate throughput.
- Post-processing: on-accelerator NMS with calibrated thresholds per class; class-aware variant; deterministic tie-breaking by detection index so two replays of the same input produce identical outputs.
- Temporal aggregation: three-of-five consecutive-frame debouncing on the high-cost-of-false-positive classes; a tracker stage downstream consumes the per-frame detections.
- Fallback: when the maximum class probability is below 0.6 on a safety-critical class, the system emits the detection with the `uncertain` flag, runs the larger verifier model on the same frame, and reconciles before publication; the verifier budget is capped at fifteen percent of frames.
- Observability: full per-stage latency histograms; per-class detection rates; agreement with verifier; drift in input distribution; every published detection carries the model build id, engine cache key, ISP configuration version, and timestamp source.
- Rollout: shadow-traffic comparison against the incumbent for a documented mileage threshold; canary on a small number of vehicles before fleet release; rollback automated on documented triggers.

### Common anti-patterns to flag

The plan closes with a short list of common anti-patterns the reviewer should call out if it sees them in the user's intended design:

- *Magic thresholds*. Score floors, IoU thresholds, batch windows, and queue depths are sometimes carried over from a tutorial or a prior project without justification. Every threshold in the design must point back to either a calibration run or an explicit operating-point trade.
- *Single-number quality stories*. "We're at 0.85 mAP" is not a deployment statement. A deployment statement names the cohorts, the operating point, the latency under load, and the failure surface.
- *Observability as logging*. Logging text strings is not observability. Observability is structured signals — histograms, counters, gauges — that an operator can compare against thresholds without reading lines of text.
- *Soft fallback only*. A fallback that exists only as a `try/except` is not a fallback. A fallback is named, budgeted, observable, and qualified by the evaluation rig.
- *Aspirational latency budgets*. A budget that no measured configuration meets is a wish. The plan calls out aspirational budgets and either revises the budget or revises the design.
- *Implicit retraining triggers*. A model that drifts and gets quietly retrained on whatever data was available is a model whose behaviour is no longer audited. Retraining triggers are documented; retraining outcomes pass the same gates as the original release.
- *Trust in vendor defaults*. A runtime's default fusion settings, NMS plugin, or precision policy may not match the deployment's needs. The plan documents which defaults were accepted, which were overridden, and why.

### Acceptance criteria for the deliverable itself

A deployment design produced by this skill is acceptable when it satisfies the following checks:

1. *Latency budget reconciled*. The per-stage budget table sums to a number that fits under the contract, with margin. No stage is "to be measured later".
2. *Accuracy floor named*. Per-class and per-cohort floors are explicit, tied to the evaluation rig's gates, with a stop-the-line trigger for breaches.
3. *Failure surface enumerated*. Every input that the pipeline could see and behave incorrectly on is listed, either as an in-scope cohort with a test or as an out-of-scope condition with an explicit refusal.
4. *Fallback budgeted*. The uncertainty fallback has a named action, a budget, and a measured cost; it is not vapor.
5. *Observability lined up*. Every gate the rollout depends on is observable from the metrics surface; an operator can confirm the deployment is healthy without reading the source.
6. *Rollback rehearsed*. The rollback path is documented and has been executed end-to-end in a staging environment before the live rollout.
7. *Risks owned*. Every risk in the register has an owner, a mitigation, and a verification step; orphan risks are unacceptable.
8. *Cross-skill pointers*. The design names the evaluation-rig and edge-deployment skills explicitly and identifies the inputs each one needs from this design and produces back for it.

A design that passes all eight is ready for engineering review. A design that fails any one returns to the relevant stage.

## Limitations

- The skill produces a deployment architecture, not an implementation. Picking a specific runtime build, writing the kernels, or configuring a particular cluster is outside the scope.
- The latency and throughput numbers in any example are illustrative, not benchmarks. The team must measure on the target hardware and revisit the design when measurements disagree with the budget.
- The skill assumes a trained detector exists. Training-time concerns — loss functions, augmentation schedules, optimizer choices — belong to the data-pipeline and training-side skills.
- The skill is hardware-agnostic at the methodology level. The edge-deployment skill carries the per-accelerator toolchain details.
- High-regulation contexts (medical imaging, biometric identification, public-safety surveillance) impose constraints — bias auditing, demographic-parity analysis, retention and consent rules — that this skill flags but does not encode in full. Treat the architecture as a structuring aid and consult the relevant compliance frameworks.

## Sources reviewed

- https://github.com/NVIDIA/TensorRT (Apache-2.0)
- https://github.com/microsoft/onnxruntime (MIT)
- https://github.com/onnx/onnx (Apache-2.0)
- https://github.com/triton-inference-server/server (BSD-3-Clause)
- https://github.com/open-mmlab/mmdetection (Apache-2.0)
- https://github.com/PaddlePaddle/PaddleDetection (Apache-2.0)
- https://github.com/openvinotoolkit/openvino (Apache-2.0)
- https://github.com/apple/coremltools (BSD-3-Clause)
- https://github.com/pytorch/vision (BSD-3-Clause)
- https://github.com/ultralytics/ultralytics (AGPL-3.0; methodology study only; no code or trademarked names used)
