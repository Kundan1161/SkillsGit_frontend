---
id: skillsgit-curated/detector-edge-deployment
version: 1.0.0
name: Detector Edge Deployment Planner
description: Deploy a real-time object detector on edge hardware — vendor toolchain selection, INT8 calibration, per-layer profiling, thermal throttling defences, and dynamic resolution.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:real-time-object-detection, edge-inference, int8-calibration, npu, mobile-inference, thermal-throttling, profiling, dynamic-resolution]
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
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - edge detector deployment
  - int8 calibration
  - npu detector
  - mobile object detection
  - thermal throttling inference
  - per-layer profiling
  - dynamic resolution detection
  - coreml deployment
  - tensorrt edge
  - onnx runtime edge
  - openvino npu
  - operator coverage edge
example_invocations:
  - "Plan an edge deployment for our object detector on a small NPU-equipped industrial camera."
  - "Migrate a server-side detector to an iOS deployment with the neural engine and verify accuracy parity."
  - "Design a strategy to keep our drone's detector responsive when the SoC throttles in direct sunlight."
inputs:
  - name: model_artifact
    type: text
    required: true
    description: Model family, input resolution, parameter count, exchange-format availability, and the precision the model trained at.
  - name: target_hardware
    type: text
    required: true
    description: SoC and accelerator (NPU, GPU, DSP), memory envelope, OS, thermal envelope, power budget, and form factor.
  - name: latency_and_throughput_budget
    type: text
    required: false
    description: Per-frame latency budget, sustained throughput, allowed jitter, and cold-start budget.
  - name: accuracy_floor
    type: text
    required: false
    description: Acceptable accuracy loss from server baseline, per-class minimums, and any safety-critical classes.
  - name: operational_constraints
    type: text
    required: false
    description: Offline operation, OTA-update policy, security envelope (model encryption, attestation), regulatory framework.
outputs:
  - name: edge_plan
    type: markdown
    description: Edge deployment plan covering toolchain selection, conversion path, calibration, profiling, thermal defence, and acceptance.
  - name: plan_json
    type: json
    description: Structured plan with `toolchain`, `conversion`, `calibration`, `profiling`, `thermal`, `dynamic_resolution`, `gates`, `risks`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Detector Edge Deployment Planner

## When to use

Use this skill when a real-time object detector must run on hardware that is not a server — a small accelerator on a camera, an NPU on a phone, an embedded GPU on a robot, a DSP on a power-constrained device. The skill produces a written plan that selects the vendor toolchain, defines the conversion path from a portable format to a hardware-specific engine, designs the integer calibration regime, lays out the per-layer profiling pass, defends against thermal throttling, and decides whether the deployment uses dynamic resolution or a fixed resolution. The output is the plan and a structured artifact, not the converted model.

Use this skill at four moments: greenfield deployment where a working detector exists on a server and must move to an edge target; migration where the device family changes (new SoC, new OS, new accelerator); accuracy investigation where the edge build behaves differently from the server build and the team needs a structured plan to localize the drop; and thermal investigation where a device performs well on the bench and badly in the field because sustained operation triggers throttling. It is not the right skill for designing the server deployment (see the deployment-architect skill), for designing evaluation cohorts (see the evaluation-rig skill), or for choosing the detector class itself.

**Mandatory safety disclaimer.** This skill produces methodology guidance. Real-time detection failures in safety-critical contexts can cause physical harm. Edge deployment changes the failure surface — operator coverage drops, telemetry becomes thinner, thermal and power dynamics introduce nondeterminism, and per-device variation widens the distribution of outcomes. Never deploy an edge detector to a safety-critical context without per-device qualification, thermal-soak validation, sustained drift monitoring, and an explicit policy for what the device does when it cannot meet its budget.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `model_artifact` | yes | Defines what is being converted. |
| `target_hardware` | yes | Selects the toolchain, plugins, and constraints. |
| `latency_and_throughput_budget` | no | Bounds the conversion and quantization decisions. |
| `accuracy_floor` | no | Sets the regression budget for calibration. |
| `operational_constraints` | no | Shapes the security, update, and observability plan. |

## How to apply

The skill walks a fifteen-stage pipeline. The early stages bind the model to the hardware; the middle stages design the conversion, calibration, and profiling; the late stages cover thermal and lifecycle concerns.

### Stage 1 — Bind the model to the target

1. Read `model_artifact` and `target_hardware` together. Write a single paragraph that names the model, its input shape and precision, its exchange format, and the accelerator on the target with its supported precisions and operator set. If the model has unsupported operators or shapes for the target, the plan calls that out before any conversion attempt.
2. Identify the *exchange format* that bridges training and target. A portable format that both sides understand is the lingua franca; vendor-specific intermediate representations exist downstream.
3. Identify the *minimum runtime version* on the target that supports the model's opset. Devices in the field run a heterogeneous set of OS and runtime versions; the plan documents the minimum and the strategy when a device is below it (refuse, fall back to a smaller model, force update).
4. Identify *operator gaps*. Even widely-supported formats have edge operators that some accelerators do not implement at full performance or at all. The plan lists the operators the model uses, marks any that are unsupported or fall back to CPU, and proposes a replacement (model surgery, custom operator, alternative head) or a fallback path.

### Stage 2 — Select the toolchain

5. Pick the *primary toolchain* for the hardware. The choice is usually constrained: a vendor-blessed compiler is the default for the vendor's accelerator; a portable runtime with the right execution provider is the default when targeting multiple vendors from one codebase. Document the trade-off.
6. Pick the *fallback execution path*. On most edge accelerators, unsupported operators fall back to the host CPU; on some, they fail entirely. Document the fallback policy and its expected latency cost; benchmark it before depending on it.
7. Decide whether to *target a single device family* or a *family of devices*. A single target lets the team specialize; a family forces the conversion to be lowest-common-denominator. The plan picks one consciously.
8. Document the *toolchain version pinning*. Compilers change semantics across versions; the plan locks the compiler version, the runtime version, and the OS version under which the build was qualified.

### Stage 3 — Conversion pipeline

9. Lay out the conversion as a series of transforms, each of which can be inspected and unit-tested: export from the training framework to the exchange format; opset normalization; graph simplification (constant folding, dead-node removal); operator fusion where the target benefits; precision casting; final compilation to the hardware engine.
10. Pin a *graph diff* check between consecutive transforms. Most accidental accuracy drops are introduced by an unexpected operator rewrite during conversion. A diff against the previous stage surfaces the rewrite for review.
11. Pin an *output-equivalence* check at each transform. Run a fixed batch of inputs through both the upstream and the downstream form and assert that outputs match within tolerance. The tolerance widens as precision is reduced — at full precision the equality should be tight; at integer precision the tolerance is the calibration budget.
12. Plan the *engine cache*. Compilation to the final hardware engine is often expensive and device-specific. The plan documents where the engine lives on the device, how it is keyed by hardware variant and toolchain version, and how a new engine is delivered (over-the-air, baked into the firmware, lazily built on first run with a documented cold-start cost).

### Stage 4 — Calibration regime for integer precision

13. Build a *calibration set* of several hundred to a few thousand representative images. Representative means stratified across the deployment operating envelope, not random sampling of training data. Edge calibration sets often need explicit coverage of low-illumination, high-illumination, motion-blur, and the cohorts the detector struggled with on the server side.
14. Pick a *calibration algorithm*. Common choices: entropy or KL-divergence calibration that minimizes the difference between full-precision and quantized activation distributions; percentile calibration that clips activations at a high percentile of their distribution; min-max calibration that uses the observed range. Different layers benefit from different choices; the plan documents the per-layer or per-block policy.
15. Decide *per-tensor* vs *per-channel* quantization for weights. Per-channel quantization for convolution weights almost always wins on accuracy; per-tensor for activations is the default. Detection heads with sharp activation distributions sometimes need a higher-precision activation pathway.
16. Identify *sensitive layers* — the layers where integer precision drops accuracy disproportionately. Detection heads, normalization-adjacent layers, and the final classification or regression layers are typical candidates. The plan documents which layers stay at higher precision under a *mixed-precision* strategy.
17. Plan a *quantization-aware training* alternative if post-training calibration cannot meet the regression budget. The plan documents the cost (training time, data, infrastructure), the artifact-management discipline, and the gate that decides between post-training and quantization-aware training.
18. Decide the *symmetric-vs-asymmetric* convention. Many edge accelerators prefer symmetric quantization for performance; the plan calls out any layer where asymmetric is required for accuracy.
19. Set the *regression budget*. A typical floor: top-line accuracy drop within an agreed delta from the server baseline; no class with safety-critical status loses any accuracy; per-cohort gap from baseline within an agreed delta. The gate from the evaluation-rig skill applies here.

### Stage 5 — Per-layer and per-block profiling

20. Plan a *per-layer latency pass*. Run the compiled engine with profiling enabled and record the time per layer and per fused block. Most edge accelerators expose a profiler that emits this data; some require a vendor tool, some require instrumentation in the runtime API.
21. Plan a *per-layer accuracy pass*. With calibration applied, run a small validation set through the model in both the server baseline and the edge build, and record per-layer activation deltas. Spikes localize where calibration is hurting accuracy.
22. Build a *cost-and-accuracy table* per layer: parameter count, FLOP count, measured latency, activation memory, calibration delta. This table tells the optimization team where to invest — heavy layers with small calibration impact are quantization candidates; cheap layers with large calibration impact stay at higher precision.
23. Identify *operator fusion opportunities*. Convolution-batchnorm-activation triplets, attention sub-blocks, and post-processing operators often fuse on the accelerator and improve latency by tens of percent. The plan documents which fusions the toolchain applied and which were missed.
24. Identify *kernel-launch-overhead bottlenecks*. Many small operators on an accelerator pay a fixed cost per launch; in the profile they show as a long tail of cheap layers. Fusion or graph rewrites reduce this.
25. Identify *memory-bound vs compute-bound* layers. Memory-bound layers benefit from precision reduction or from tiling that improves reuse; compute-bound layers benefit from kernel selection or from algorithmic substitution. The plan annotates each significant layer with its bound.

### Stage 6 — Memory and bandwidth planning

26. Compute the *peak memory* for the engine: weights, activations, workspace, and any per-batch scratch. Compare to the device's available memory after the OS, other apps, and the camera pipeline take their share.
27. Compute the *bandwidth* from the sensor to the accelerator. On many edge platforms the bottleneck is not compute but the data path — host-to-device copy, decoder-to-accelerator handoff, or DRAM bandwidth. The plan documents the pipeline and where copies happen.
28. Plan *zero-copy* paths where the platform supports them. A pipeline that decodes directly into a buffer the accelerator can read avoids host-CPU touches that dominate latency on small devices.
29. Decide whether the engine is *resident* or *loaded on demand*. Resident engines reduce cold-start latency but consume memory while the device is idle. The plan picks one.

### Stage 7 — Dynamic resolution and adaptive inference

30. Decide whether the deployment uses *fixed* or *dynamic* resolution. Fixed resolution simplifies the engine and the calibration; dynamic resolution lets the runtime trade accuracy for latency under load or under thermal stress.
31. If dynamic, document the *resolution ladder*: the discrete set of input resolutions the engine supports, each with its own compiled variant and its own calibration. Continuous resolution scaling is rarely worth the cost on edge accelerators.
32. Document the *switching policy*: latency budget exceeded for N consecutive frames triggers a step down; sustained headroom triggers a step up; explicit operator commands override automation. Each transition must preserve any tracker state.
33. Document the *minimum acceptable resolution* below which the system refuses to operate and surfaces an explicit error rather than emitting unreliable detections.

### Stage 8 — Thermal envelope and throttling defences

34. Characterize the *thermal envelope*. Run the device under sustained inference at the target rate for the longest expected operating period, measure die temperature, throttle events, and the resulting latency and accuracy degradation. Document the result as a thermal curve.
35. Document the *throttling cascade*: clock reduction, frame drop, resolution step down, model swap to a smaller variant, fail-safe shutdown. The cascade is the device's plan for staying within budget when thermal headroom is lost.
36. Document the *cooling assumptions*: housing material, airflow, sun exposure, ambient temperature range. A camera tested in a lab at twenty degrees may throttle at thirty-five degrees in direct sunlight; the plan calls out the deployment-environment validation.
37. Document the *power envelope*. Sustained inference at maximum rate may exceed the platform's continuous power budget; the deployment may need duty cycling, sleep states between frames, or a lower-rate variant.
38. Plan a *thermal-soak qualification test*. Each new device variant or housing variant is soaked at the expected worst-case ambient and re-evaluated before fleet rollout.

### Stage 9 — Per-device variation

39. Acknowledge that edge accelerators vary device-to-device. Two units of the same SKU can run at different clocks under the same load due to silicon binning and thermal coupling.
40. Plan a *per-device qualification step* at first run: a fixed benchmark image yields a measured latency and accuracy stamp that is logged with the device identifier. Outliers are flagged for replacement or for a different variant.
41. Plan a *drift recheck* schedule: the same benchmark runs periodically and trends are reported. A device whose stamp drifts significantly is a candidate for service.

### Stage 10 — Observability on the edge

42. Pin the *edge telemetry* surface: per-frame latency, throttle counter, accelerator utilization, host CPU utilization, memory pressure, frame-drop count, fallback-execution-path count.
43. Pin the *health signal* that the device emits upstream when it is connected. Even mostly-offline devices need an "I am healthy" beacon to a fleet management plane.
44. Pin the *event capture* policy. A device that locally captures and uploads a short clip around a notable event helps diagnose field issues without continuous bandwidth.
45. Pin the *privacy boundary*. Edge deployments often run because data cannot leave the device; the telemetry surface must respect that boundary explicitly, and the plan documents what aggregate signals are uploaded versus what stays local.

### Stage 11 — Security, integrity, and update

46. Document the *model artifact integrity* check. The engine on the device is signed by the build pipeline and verified on load; a mismatched or unsigned engine is refused.
47. Document the *update path*. Over-the-air model updates require a delivery channel, a staged rollout, a verification step before activation, and a rollback to the previous engine if the new one fails its first-run benchmark.
48. Document the *attestation* model. In regulated or high-security deployments, the device proves to a server that it is running the expected build before being trusted; the plan calls out whether attestation is required.
49. Document the *model-extraction* threat. Edge engines are at higher risk of extraction than server-side ones; the plan calls out whether the engine is encrypted at rest, whether the runtime is allowed to introspect tensors, and whether the calibration data needs to remain off-device.

### Stage 12 — Acceptance gates

50. Pin the *parity gate*: edge build accuracy within agreed delta of server baseline on the acceptance set; per-class and per-cohort floors per the evaluation-rig plan.
51. Pin the *latency gate*: P95 and P99 within budget at the qualified device variant; cold-start within budget; switch latency for dynamic resolution within budget.
52. Pin the *thermal gate*: the soak test produces no failures and no drift beyond delta over its duration.
53. Pin the *update-rollback gate*: a forced update failure recovers to the previous engine within the documented window.
54. Pin the *operator-coverage gate*: zero operators on critical paths fall back to host CPU; any fallback that exists is documented and budgeted.

### Stage 13 — Lifecycle and retirement

55. Define the *lifecycle policy*: how long the same engine is supported in the field, what triggers a forced refresh, what happens to devices that cannot run the new engine.
56. Define the *deprecation schedule* for old toolchain versions. The build pipeline must continue to produce engines for the longest-supported runtime version in the field until those devices are retired.
57. Define the *end-of-life behaviour* of the device when it can no longer meet the budget. A graceful degradation to a smaller model, an explicit error mode, or a forced offline state are all valid; the plan picks one.

### Stage 14 — Risks and unknowns

58. Enumerate cross-cutting risks: an operator falls back to CPU in production but not in the lab, a calibration set under-covered a field cohort, a thermal soak that did not match field housing, an OS update that ships a different runtime version, a security update that invalidates the engine cache. Each risk has a mitigation and a verification step.
59. Maintain a *known-unknowns* register: failure modes the team has not yet characterized but suspect. Per-device variation under field thermal stress is a common entry.

### Stage 15 — Compose the deliverable

60. Open with a "deployment intent" paragraph that names the model, the target hardware, the budget, and the regression floor.
61. Render the plan as a markdown document organized by the stages above, with a conversion-pipeline diagram, a per-layer cost-and-accuracy table example, a thermal curve template, and a resolution-ladder table.
62. Emit `plan_json` with structured fields: `toolchain`, `conversion[]`, `calibration`, `profiling`, `memory`, `dynamic_resolution`, `thermal`, `per_device`, `observability`, `security`, `gates`, `risks[]`.
63. Close with the mandatory safety disclaimer restated, an "open issues" list, and pointers to the deployment-architect, evaluation-rig, and data-pipeline skills.

### Cross-cutting edge concerns

64. *Camera ISP coupling*. On many edge devices the image-signal-processor and the accelerator share memory, scheduling, and thermal envelope. A change in the ISP pipeline (auto-exposure setting, white-balance behaviour, denoising aggressiveness) silently changes the input distribution to the detector. The plan documents the ISP configuration as part of the deployed artifact and re-runs calibration when it changes.
65. *Background workload*. Edge devices often run more than the detector — a video encoder, a metadata uploader, a watchdog. The plan documents the worst-case background load and includes it in the latency measurement; a detector benchmarked in isolation can miss its budget by tens of percent under realistic system load.
66. *Power-state transitions*. Battery-powered devices oscillate between idle and active power states; cold-start latency from a deep idle is often dominated by accelerator wakeup, not by inference. The plan documents the wake-and-first-inference budget separately from the steady-state budget.
67. *Clock-source determinism*. Per-frame latency measurements depend on the timer source the runtime uses; on some accelerators, internal counters drift relative to the host clock under thermal stress. The plan documents the timer source and the calibration step that bounds the drift.
68. *Cross-platform parity*. Deployments that span multiple device families need an explicit parity policy: which is the reference, what tolerance applies between platforms, how is a regression on one platform handled. Without an explicit policy, the team optimizes for whichever device is in front of them today.
69. *Bring-your-own-runtime risk*. Some platforms expose multiple runtime options (vendor compiler, portable runtime, vendor-runtime-fallback to CPU). The plan picks one path and documents the failure mode when the chosen path is unavailable at runtime (rare driver upgrade, unsupported OS variant). The fallback path itself is qualified, not assumed.
70. *On-device debugging*. When a fielded device behaves wrong, the team needs enough on-device introspection to diagnose without recalling the device. The plan documents which inputs and intermediate states can be captured on demand, the storage budget for those captures, and the upload path. Without this, every field failure becomes a return-merchandise event.

### Stage 15.5 — Conversion-failure forensics

71. Sometimes the converted edge build fails a parity test that the server build passed. The plan documents a forensics workflow: bisect the conversion stages, compare per-layer activations between server and edge on a fixed batch, identify the first stage at which the activations diverge beyond tolerance, root-cause the divergence (operator semantic mismatch, precision cast, calibration outlier, fusion error). The workflow yields a written incident report and a regression test that prevents the same divergence reappearing.
72. Most conversion failures cluster in a small set of root causes: an operator with subtly different semantics across runtimes (boundary conditions on rounding, edge cases on integer overflow, default values for optional attributes), a fusion that elided a clipping operator the original graph relied on, a calibration outlier that produced an aggressive scaling factor, an opset upgrade that silently changed a default. The plan includes a checklist for each cluster.

### Stage 15.6 — Fleet management and observability aggregation

73. A single device's telemetry is interesting; a fleet's aggregated telemetry is decision-grade. The plan documents how per-device signals are uploaded and aggregated: rolling histograms by hardware variant, by housing variant, by firmware version, by geographic deployment region. Cross-cohort comparisons surface device-specific degradations that a single device cannot.
74. The fleet plane must support a *cohort recall*: given a set of devices identified by a query (firmware version, hardware revision, geographic region), the fleet plane can target a model update, a configuration change, or a diagnostic capture to exactly that cohort. Without cohort recall, every fleet change is a fleet-wide change, which is unacceptable for a staged rollout.
75. The fleet plane also supports *device retirement* — taking a device out of production rotation when it can no longer meet the budget. The retirement criteria, the user-visible message, and the recovery path are part of the plan.

### Worked second example

As a second worked example, consider a wearable camera for industrial-safety monitoring where the constraints are different from the first example:

- Hardware: a small SoC with a low-power NPU; 1 GB device memory; battery-powered, target eight-hour shift.
- Model: a quantized single-stage detector targeting personal-protective-equipment classes (hard hat, safety vest, eye protection) plus a person class, all at modest input resolution.
- Conversion: portable exchange format as the source of truth; vendor NPU compilation as the deployed artifact; opset pinned and verified.
- Calibration: 800 stratified images covering indoor, outdoor, low-light, and high-contrast scenes; per-channel weight quantization, per-tensor activation quantization, integer-8 throughout except the detection-head score layer which stays at integer-16.
- Profiling: per-layer pass identifies that the head's score layer is the dominant latency contributor and is also bandwidth-bound; the fix is a smaller intermediate channel count, retrained, rather than a precision compromise.
- Memory and bandwidth: zero-copy path from the camera ISP directly into the NPU input tensor; engine kept resident in memory because cold-start would exceed the latency budget.
- Dynamic resolution: not used; battery cost of switching outweighs the savings on this hardware.
- Thermal: shift-long soak in a hot-warehouse simulation shows the SoC throttles only when the device is held in direct sunlight for extended periods; the housing is updated with a heat-spreader and the soak is repeated.
- Per-device qualification: each device runs a fixed benchmark on first power-up after assembly; outliers are returned to the production line.
- Observability: latency, throttle counter, frame-drop count, battery state, fallback-execution count, accuracy-stamp drift, all batched and uploaded when the device docks at the end of shift.
- Security: model encrypted with a device-bound key; OTA updates delivered via the dock; rollback on first-run benchmark failure.

## Outputs

1. `edge_plan` (markdown) — full edge deployment plan.
2. `plan_json` (JSON) — structured plan suitable for downstream automation.

## Examples

**Input (placeholder):**

`model_artifact`: "Single-stage detector at 384-input, trained at half precision on the server; portable exchange format available at a recent opset."

`target_hardware`: "Industrial camera with an integrated NPU supporting integer-8 and integer-16, 2 GB device memory, embedded Linux, fanless aluminium housing."

`latency_and_throughput_budget`: "30 frames per second sustained; per-frame latency within 30 ms; cold-start within 1 s."

`accuracy_floor`: "Top-line drop within 1 percentage point of server baseline; no per-class drop on safety classes."

`operational_constraints`: "Outdoor mount with direct-sun exposure, ambient up to 45°C; OTA updates over cellular; signed and encrypted model artifact."

**Plan (abbreviated):**

- Toolchain: vendor NPU compiler as primary; portable runtime fallback for CPU-resident operators; toolchain version pinned to the qualified release.
- Conversion: export to exchange format; opset normalization; graph simplification; convolution-batchnorm-activation fusion; integer-8 cast for the backbone, integer-16 retained around the detection head and the score layer; engine compilation cached per (hardware variant, toolchain version).
- Calibration: 1,500 stratified images covering day, dusk, night-with-illumination, rain, and motion-blur cohorts; KL-divergence calibration on activations, per-channel symmetric on weights, asymmetric retained on one normalization-adjacent layer that exhibited accuracy drop in the profiling pass.
- Profiling: per-layer latency and accuracy pass confirms the backbone is compute-bound and the head is bandwidth-bound; one operator fell back to CPU at integer-8 and was swapped for a supported alternative.
- Dynamic resolution: ladder at 384 and 320; switch policy steps down after three consecutive frames exceeding the 30 ms budget and steps up after a two-second window of headroom.
- Thermal: forty-five-minute soak at 45°C ambient in the production housing shows steady-state throttling that costs 8 percent of throughput at the higher resolution; the dynamic-resolution policy absorbs the loss without exceeding the latency budget.
- Per-device qualification: first-run benchmark logs latency and a fixed-image accuracy stamp; deviations beyond delta flag the device for service.
- Observability: latency histogram, throttle counter, frame-drop count, fallback-execution count, accuracy-stamp drift, all reported via an upstream beacon on connectivity.
- Security: engine encrypted at rest with a device-bound key; engine signature verified on load; OTA updates staged with a first-run benchmark gate and a rollback to the previous engine on failure.

**Output excerpt:** the markdown plan plus a JSON object whose `calibration` field carries `{set_size, strata, algorithm, weight_quant, activation_quant, sensitive_layers, regression_budget}` and whose `thermal` field carries `{soak_duration, ambient_max, throttle_curve, defence_cascade}`.

### Stage 15.7 — Reproducible build pipeline

76. The plan defines a reproducible build pipeline: given the trained checkpoint and the toolchain version, the build produces a byte-identical (or semantically-identical) engine on the build host. Reproducibility lets the team bisect regressions across builds without re-running everything from scratch and lets independent reviewers verify the artifact.
77. Reproducibility requires deterministic conversion. Sources of non-determinism include operator-ordering choices in the optimizer, floating-point reductions whose order is parallel-execution-dependent, and timestamps embedded in the artifact. The plan documents each source and the determinism flags that suppress them.
78. The build pipeline emits a *manifest* that names every input (checkpoint, calibration set, toolchain version, opset, runtime version, hardware target), every output (engine, signature, manifest itself), and the checksums for each. The manifest is what an auditor inspects to verify a deployed engine is the one that passed the evaluation gates.

### Stage 15.8 — Acceptance documentation and traceability

79. Each release carries a written acceptance document that links the evaluation report (from the evaluation-rig skill) to the deployment plan (from the deployment-architect skill) to the edge artifact produced by this plan. The link is bidirectional: each release manifest references the prior release it replaces, the evaluation report that justified the promotion, and the rollback path if it fails.
80. The traceability extends to *post-deployment incidents*. When a field issue is traced to a misbehaving detection, the forensic trail goes from the detection through the engine checksum, the manifest, the build pipeline, the evaluation report, the test set, and back to the training data slice that the cohort came from. Without this trail, post-incident improvement is guesswork.

### Worked third example

As a third example, consider an edge deployment for an autonomous mobile inspection robot patrolling an industrial facility. The constraints are different again: the device moves, the camera shakes, the scene is partially known, the consumer is a safety-relevant decision loop.

- Hardware: an embedded GPU with a stable thermal envelope when the robot is moving (airflow), an unstable envelope when the robot is docked.
- Model: a single-stage detector at moderate resolution; trained at half precision and deployed at half precision because integer calibration did not meet the regression budget on the safety-critical "person" class.
- Conversion: portable exchange format; vendor compiler; an opset upgrade caused one unsupported operator that was replaced with a supported alternative followed by a re-train.
- Calibration: half-precision deployment does not require integer calibration but does require a parity verification against the server baseline; the verification ran on a 2,000-image stratified set and required no further adjustment.
- Profiling: per-layer latency pass shows the attention sub-block in the head is the dominant contributor; a kernel-launch-overhead study identified an opportunity to fuse two adjacent operators, saving 15 percent of latency.
- Memory and bandwidth: the engine is resident; the bandwidth budget is comfortable because the camera resolution is matched to the model input.
- Dynamic resolution: a two-level ladder is implemented and used during the dock-charging state when the cooling envelope shrinks; while moving the high-resolution variant runs.
- Thermal: a soak test on the docking station revealed the device throttles within fifteen minutes; the resolution-ladder policy and a duty-cycle reduction handle this gracefully.
- Per-device qualification: a fixed benchmark runs at the start of every patrol; an outlier triggers a maintenance ticket.
- Observability: the robot uploads telemetry on dock; alerts during a patrol are emitted on the local network.
- Security: model and engine encrypted; over-the-air updates delivered through the docking station with the rollback gate.

### Stage 15.9 — Common edge-deployment anti-patterns

The plan closes with anti-patterns the reviewer should flag if seen in the user's intended approach:

- *Calibration on training data*. Calibration sets must reflect the deployment distribution, not the training distribution. A model calibrated on training data may exhibit silent regression on field conditions.
- *Bench-only thermal validation*. A device that has only been tested in a temperature-controlled lab has not been thermally validated. Field-housing soak under expected worst-case ambient is non-negotiable.
- *Implicit operator fallbacks*. An accelerator runtime that silently falls back to CPU for unsupported operators may meet the budget on the bench (low load) and fail in the field (sustained load). The plan requires explicit identification of every fallback.
- *Engine reuse across hardware variants*. Engines compiled for one accelerator variant may run, slowly or incorrectly, on a different variant of nominally the same SKU. Engines are keyed by hardware variant.
- *Cold-start blindness*. A device that is benchmarked on hot caches will under-report cold-start latency, the latency the user actually experiences on power-up. The qualification includes a deliberate cold-start path.
- *Per-device blindness*. Treating a fleet as a uniform population hides per-device variation. Per-device qualification at first run and periodic re-check protects against silicon and assembly variation.
- *Update bricking*. An OTA update that succeeds on the bench but fails in the field with no rollback path bricks devices. The rollback path is qualified end-to-end before the first OTA.
- *Telemetry over-collection*. An edge deployment that uploads more telemetry than the privacy boundary allows is a regulatory failure; one that uploads less than the diagnostic budget requires is an operability failure. The plan finds the boundary explicitly.

### Stage 15.10 — Decommissioning and data-handling

When a device is retired or returned, its on-device data — models, calibration sets, captured frames, telemetry buffers — must be handled per the operational and regulatory policy. The plan documents the decommissioning steps: secure erase of model and calibration artifacts, return-to-factory image, audit log of the decommission event. For devices that store captured frames (event recordings, OTA-buffered diagnostics), the data-retention policy specifies how those frames are exfiltrated, anonymized, or destroyed.

A. The decommission script is part of the released artifact.
B. The decommission event is logged centrally with a hash of the device identifier and the operator name.
C. The fleet plane prevents a decommissioned device from rejoining production silently.

### Stage 15.11 — Mixed-hardware fleets

Many edge deployments end up with a mixed fleet — some devices on the latest accelerator, others on a previous generation, others on a CPU-only fallback. The plan documents the *per-platform model strategy*: whether a single model serves all platforms (lowest-common-denominator), whether each platform gets a tailored model (highest-performance), or whether platforms cluster into tiers with one model per tier. Tier-based strategies are usually the right answer for sustainably-managed fleets.

A. Each tier has a documented model variant, a documented evaluation suite, and a documented set of gates.
B. The fleet plane routes the right engine to each device based on the device's reported platform identity.
C. The release process qualifies every tier independently; a release that ships when one tier has not qualified is a release that ships only to the qualified tiers.
D. Cross-tier drift is reported: when one tier's accuracy diverges from another, the plan investigates whether the divergence reflects a true hardware-driven gap or a calibration error.

### Stage 15.12 — Documentation and runbook

A field engineer who arrives at a malfunctioning device should be able to consult a runbook that names the symptoms, the likely causes, the diagnostics to run, and the escalation path. The plan owns the seed of that runbook: the symptoms it knows about from the qualification work, the structured diagnostics the device supports, the rollback procedure. The runbook is updated as field experience grows.

A. The runbook lists each documented symptom with at least one root cause and one mitigation.
B. The runbook lists the diagnostic commands the device supports and where their output goes.
C. The runbook lists the conditions under which the field engineer escalates to engineering and the data to include in the escalation.

### Acceptance criteria for the plan itself

An edge plan produced by this skill is acceptable when it satisfies the following checks:

1. *Toolchain pinned*. Vendor compiler version, runtime version, OS version, and hardware target are all explicit; the qualified configuration is what ships.
2. *Conversion pipeline auditable*. Each transform stage has a graph diff and an output-equivalence check against the prior stage.
3. *Calibration documented*. The calibration set, the algorithm, the per-layer policy, and the regression budget are all named; sensitive layers are listed and protected.
4. *Profiling complete*. Per-layer latency and accuracy data exist for every significant layer; bottlenecks are localized and explained.
5. *Thermal validated*. A soak test in production housing at expected worst-case ambient has run and produced a thermal curve; the throttling cascade is documented.
6. *Per-device qualified*. First-run benchmark logs latency and accuracy stamps; the fleet plane consumes them; outliers are flagged.
7. *Security and update path qualified*. Engine integrity check, signing, OTA delivery, and rollback have been exercised end-to-end.
8. *Observability operational*. Edge telemetry is uploaded, aggregated, and tied to the deployment plan's gates.
9. *Cross-skill pointers*. The plan names the deployment-architect and evaluation-rig skills explicitly and identifies the inputs each one needs from this plan and provides back for it.

A plan that passes all nine is ready for production rollout planning. A plan that fails any one returns to the relevant stage.

## Limitations

- The plan is methodology, not vendor documentation. It will not tell the team which exact compiler flag to set; it will tell them what the flag must achieve and what to verify.
- The accuracy and latency numbers in any example are illustrative. Real numbers are measured on the target device under the real housing and the real ambient.
- The skill assumes a trained detector and a server-side baseline exist. The accuracy floor is meaningless without that baseline.
- The skill assumes the device permits introspection at the level the plan requires. Some closed accelerators expose only end-to-end latency and not per-layer detail; the plan calls out the gap and proposes the next-best diagnostic.
- Safety-critical edge deployments (medical, aviation, autonomous mobility) carry regulatory obligations that this plan does not encode. Treat the plan as a structuring aid and consult the relevant authorities.

## Sources reviewed

- https://github.com/NVIDIA/TensorRT (Apache-2.0)
- https://github.com/microsoft/onnxruntime (MIT)
- https://github.com/onnx/onnx (Apache-2.0)
- https://github.com/apple/coremltools (BSD-3-Clause)
- https://github.com/openvinotoolkit/openvino (Apache-2.0)
- https://github.com/PaddlePaddle/PaddleDetection (Apache-2.0)
- https://github.com/pytorch/vision (BSD-3-Clause)
- https://github.com/triton-inference-server/server (BSD-3-Clause)
- https://github.com/ultralytics/ultralytics (AGPL-3.0; methodology study only; no code or trademarked names used)
