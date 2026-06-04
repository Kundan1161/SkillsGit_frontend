---
id: skillsgit-curated/model-serving-reviewer
version: 1.0.0
name: Model Serving Setup Reviewer
description: Audit a model-serving setup against a latency budget — batching, quantization, GPU/CPU mix, autoscaling, observability, A/B routing, and fallback — and produce a prioritized fix list.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:ml-engineering, model-serving, inference, latency, batching, quantization, autoscale, observability]
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
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - review my model serving
  - audit inference setup
  - latency budget for ml
  - batching strategy
  - quantize my model
  - gpu cpu split
  - autoscale ml inference
  - model serving fallback
  - canary rollout for model
  - inference observability
  - llm serving review
  - tail latency
  - cost per request inference
example_invocations:
  - "Audit our model-serving setup — we are missing the latency budget by 40ms at p95 and not sure why."
  - "Review this Triton + Kubernetes deployment and tell me what to fix before traffic doubles."
  - "Should we quantize the model or add a second replica? Walk me through the trade-offs."
inputs:
  - name: serving_topology
    type: text
    required: true
    description: How the model is served today — framework (Triton, BentoML, vLLM, KServe, hand-rolled), hardware, replica count, load balancer, any sidecars, and how requests reach it.
  - name: model_details
    type: text
    required: false
    description: Architecture, parameter count, precision today (fp32 / fp16 / bf16 / int8 / int4), batch sizes supported, current throughput per replica.
  - name: traffic_pattern
    type: text
    required: false
    description: Average and peak QPS, request-size distribution, time-of-day pattern, latency budget (p50, p95, p99), and the source of those numbers.
  - name: cost_budget
    type: text
    required: false
    description: Monthly cost ceiling, cost-per-request target, or hardware-units cap.
  - name: failure_history
    type: text
    required: false
    description: Recent incidents — what broke, what saturated, what fell over under load.
  - name: review_scope
    type: choice
    required: false
    description: Scope of the audit.
    choices: [latency, throughput, cost, reliability, all]
outputs:
  - name: review_report
    type: markdown
    description: Triaged audit covering latency budget, batching, precision, GPU/CPU mix, autoscale, observability, A/B routing, fallback, and a prioritized fix list.
  - name: findings_json
    type: json
    description: Machine-readable findings with `area`, `severity`, `current_state`, `recommended_change`, `expected_impact`, `effort`, `risk`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Model Serving Setup Reviewer

## When to use

Use this skill when an ML or platform team has a model in production (or about to go to production) and needs a senior pair of eyes on the serving setup before something gets worse. The trigger is usually one of: latency is missing budget, cost is rising faster than traffic, an incident exposed a fragile path, traffic is about to grow, or the team is debating whether to move to a different runtime.

The skill applies to classical-ML inference (gradient-boosted trees, classical neural networks, recommender models) and to LLM inference (transformer-based generation and embedding services). The decisions overlap heavily — batching, precision, autoscale, observability — but the constants differ. The skill calls out where LLM-specific behaviour (KV cache, prefix sharing, continuous batching) changes the trade-off.

The skill is not a substitute for a load test; its findings are hypotheses that ground a load test. It is also not a substitute for a security review of the serving plane.

The skill is also not for choosing a model — that is upstream. It assumes the model is fixed and the question is "how should we run this model".

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `serving_topology` | yes | The system under review. |
| `model_details` | no | Determines batching, precision, and memory math. |
| `traffic_pattern` | no | Sets the latency, throughput, and autoscale targets. |
| `cost_budget` | no | Calibrates the trade-off recommendations. |
| `failure_history` | no | Drives reliability-focused findings. |
| `review_scope` | no | Lets the user narrow the audit to the most pressing axis. |

## How to apply

The skill runs an eleven-stage review. Each stage produces findings; findings are merged, prioritized, and emitted as a triaged list at the end.

### Stage 1 — Establish the budget

1. Restate the latency budget in absolute milliseconds. If only "fast" or "low-latency" was provided, ask the user for p50, p95, and p99 targets explicitly. Without numbers, the audit cannot judge whether anything is wrong.
2. Decompose the budget into the components the request will traverse: network ingress, load balancer, queue wait, batching wait, framework overhead, model forward, post-processing, network egress. Each component must fit inside a sub-budget that sums to the overall budget; otherwise the architecture cannot meet the target by construction.
3. Establish the throughput target in QPS at peak. If the user gave only "thousands of requests per day", convert to peak QPS assuming a worst-case 5x concentration around peak hours unless told otherwise.
4. Establish the cost budget in dollars per request or dollars per million tokens for LLMs. Make the conversion to hardware-hours per million requests explicit — that is the unit that maps to capacity decisions.
5. Establish the availability target (e.g. 99.5% monthly). The harder the target, the more redundancy each stage of the audit must verify.
6. If any of the four budgets (latency, throughput, cost, availability) is incompatible with the others given the model size, surface this as the first finding. A 7B-parameter LLM cannot serve 5ms p95 on a CPU under any configuration — say so before reviewing anything else.

### Stage 2 — Walk the request path

7. Build a mental diagram: client → ingress → load balancer → service → batcher → model → response → client. Note the queueing point at each hop and the timeout at each hop.
8. Identify single points of failure: a single load balancer, a single GPU host, a single model storage path the boot path depends on. Each is a finding with "reliability" severity.
9. Identify hidden synchronous calls: a model call that fetches features from an online store before predicting, a postprocessing step that calls an external API, a logging sidecar that blocks on flush. Each adds to the tail.
10. Identify timeouts at each hop: ingress timeout, framework timeout, model-level timeout, client timeout. Mismatched timeouts cause cascading failures (a downstream timeout fires after the upstream gives up; the upstream retries; load amplifies). Recommend that timeouts decrease as you go inward (client > ingress > service > model).
11. For LLM serving specifically: identify whether streaming is supported, whether time-to-first-token (TTFT) is part of the budget, and whether inter-token latency (ITL) has a separate target. Streaming changes the budget conversation fundamentally — TTFT and ITL are different metrics from "p95 of the whole response".

### Stage 3 — Batching strategy

12. Identify whether batching exists. Per-request inference without batching is the most common waste at moderate load.
13. Identify the batching mode: static batching (collect N requests, then run), dynamic batching (collect up to N or wait T milliseconds, whichever comes first), continuous batching (for autoregressive LLMs; new requests join the batch mid-generation).
14. For static and dynamic batching: the wait time must fit inside the latency sub-budget. If the latency sub-budget for batching is 20ms and the dynamic-batch timeout is 50ms, the budget is unreachable. Surface as a blocker.
15. For dynamic batching: review the maximum batch size and the maximum wait time. Recommend a curve-fit experiment: vary batch size, measure latency and throughput, find the knee. A team that batches "because the default does" is leaving throughput on the table.
16. For LLM serving: continuous batching (also called in-flight batching) is the right default. If the deployment uses static batching for an autoregressive LLM, that is a major finding; throughput will be 3-10x worse than the achievable baseline.
17. For batching with mixed request sizes (LLM with varying input or output lengths), bucketed batching by length avoids one short request being held up by one long request in the same batch. Recommend a 2-3 bucket scheme.
18. For batching with priority traffic (e.g. premium-tier users), recommend a separate queue or a preemptive scheduling policy. Mixing priority and non-priority in the same first-come-first-served queue gives premium users worse tail latency.

### Stage 4 — Precision and quantization

19. Identify the model's current precision. Default for trained-in-fp32 weights is to serve in bf16 or fp16 on GPUs; staying in fp32 doubles memory and halves throughput for almost no quality gain.
20. Recommend quantization candidates:
    - **bf16 / fp16**: nearly free quality cost; ~2x throughput vs fp32 on most GPUs. The default starting point.
    - **int8 weight-only quantization**: ~2x further memory savings; small quality cost on most models. Verify with the eval harness, not vibes.
    - **int8 activation quantization**: more sensitive; requires calibration data. Quality cost is task-dependent.
    - **int4 weight-only quantization** (for large LLMs): substantial memory savings; quality cost should be verified per-model.
    - **fp8** (where hardware supports): increasingly the preferred LLM serving precision.
21. The audit must require evidence that quality was measured before and after quantization, on the same eval harness. "We quantized and it felt the same" is not evidence. Surface a finding if quantization is in production without a quality regression report.
22. For classical-ML serving, quantization is less common but still worth considering for tree-ensembles and small NNs; recommend an ONNX or TensorRT path if not already in use.
23. For embedding models specifically: int8 is often free; the embedding-similarity score is robust to weight quantization in a way generation isn't.

### Stage 5 — Hardware mix

24. Identify the hardware: CPU type, GPU type if any, RAM per host, VRAM per GPU, NIC bandwidth, storage class for model weights.
25. Match the workload to the hardware:
    - Small classical-ML models: CPU is often correct. GPUs add cost without proportional benefit.
    - Medium NNs at moderate QPS: GPU often dominates on cost per request if utilisation is > 30%.
    - Large LLMs: GPU is mandatory; the question is which generation and how many per replica.
    - Embedding workloads: CPU can be competitive at low QPS; GPU dominates beyond a threshold.
    - Sparse-feature recommender models: CPU is often correct; GPUs help only for dense embedding lookups.
26. Calculate **achievable utilization** at the stated peak QPS. If a GPU is sized for 10x peak, the user is paying for idle silicon. Recommend either downsizing or consolidating multiple models onto one host.
27. For LLM serving: the binding constraint is usually VRAM for the model weights + KV cache. The audit must compute approximate memory: `params * bytes_per_param + max_concurrent_sequences * sequence_length * 2 * num_layers * hidden_dim * bytes_per_kv_element`. If the math says the configuration cannot hold the stated concurrency, that is a blocker.
28. Recommend prefix caching for LLM workloads with shared system prompts or repeated retrieval contexts. Prefix caching alone can cut p50 by 30-60% for chat-style workloads.
29. Recommend speculative decoding only when the model and traffic mix support it and the team can operate a draft model; do not recommend it as a default.
30. For inference at the edge or on-prem: check that the model + runtime fit in the target memory and that no host-internet dependency exists at request time.

### Stage 6 — Autoscaling

31. Identify the autoscaling mode: none, replica count tied to CPU/GPU utilization, replica count tied to QPS, replica count tied to queue depth, or scheduled scaling.
32. Replica-count tied to CPU/GPU utilization is the most common and the worst for GPU-bound LLM workloads: the GPU is busy waiting on the GPU long before the metric reflects it. Recommend **queue-depth-based scaling** for LLM workloads.
33. The autoscaler must have a **scale-up time budget** that fits within the traffic surge tolerance. If a new replica takes 6 minutes to come up and traffic doubles in 90 seconds, the autoscaler cannot rescue the cluster. Recommend warm replicas or pre-warming for known peak windows.
34. The autoscaler must have a **scale-down hysteresis** to prevent thrashing under fluctuating load. Recommend a 5-10 minute cooldown depending on cold-start cost.
35. Identify minimum replica count for availability targets. A single replica means a single failure removes the service; for 99.5%+ availability, minimum 2 across at least two failure domains (zones, racks, nodes).
36. For burst protection: recommend a request queue with a bounded size in front of the model and a 429 response when the queue is full, rather than letting the model timeout-and-retry. The bounded queue is the explicit version of the implicit backpressure that should not exist.
37. For LLM serving: continuous batching changes the metric the autoscaler should watch. "Pending tokens" or "active concurrent sequences" is a more accurate signal than "GPU utilization".

### Stage 7 — Observability

38. The audit must verify that each of the following is logged or metricked:
    - Per-request latency, broken down by component (queue, batch wait, model, post).
    - Per-request status (success / client-error / model-error / timeout).
    - Per-request input size, output size, token counts.
    - Per-replica QPS, GPU utilization, GPU memory utilization, CPU utilization, host memory.
    - Batch sizes used (histogram).
    - Queue depth (gauge).
    - Cold-start count and duration.
    - Cache hit-rates (prefix cache, response cache if any).
    - Model-version label on every metric.
    - Cost per request (computed from token counts and hardware-hour cost).
39. Verify that latency metrics are **p50, p95, and p99**, not "average". An average that meets budget can hide a 5% of users above budget.
40. Verify that traces are sampled or full — for LLM workloads with long tails, full tracing of slow requests is more useful than uniform sampling.
41. Verify that errors are distinguishable by class: OOM is not the same as timeout is not the same as bad input. Bucketed error metrics drive faster incident response.
42. Verify that drift / quality signals exist if the model is exposed to changing data — input feature distribution, output score distribution. Recommend the user pair this skill with the dedicated monitoring skill.
43. Verify that a dashboard exists for serving health and is the one the on-call uses, not a vanity report nobody reads.

### Stage 8 — A/B and canary routing

44. The audit must check whether the serving plane supports running two model versions concurrently and routing a fraction of traffic to each. Without this, every model swap is a hard cutover.
45. Recommended pattern: shadow → 1% canary → 5% → 25% → 100% with the eval harness from the eval-harness skill running on each stage. Stages last hours-to-days; auto-rollback on regression.
46. Verify that routing is sticky by user where the user-experience requires it (chat sessions in particular) and random otherwise. Per-request random routing inside a session can produce inconsistent behaviour the user notices.
47. Verify that the A/B layer captures the request and the response from both arms in a comparable form so offline scoring can compute the difference. Without this, A/B claims are unfalsifiable.
48. Verify that the rollback path is fast — sub-minute traffic shift from challenger to champion. A 30-minute rollback means a regression burns 30 minutes of users before the fix lands.

### Stage 9 — Fallback and graceful degradation

49. Identify the fallback when the model is down: serve a cached response, serve a simpler model, serve a static default, return a polite error with a retry hint. Each is a deliberate choice; "the request 5xx's" is a default, not a choice.
50. For LLM workloads: define a fallback prompt or a smaller model that can be invoked when the primary is overloaded. A circuit breaker that opens after K consecutive timeouts and routes to the fallback for a cooldown is a robust pattern.
51. For classical ML: a cached prediction or a heuristic baseline (the simple baseline from the experiment-design skill) is often the right fallback.
52. The audit must verify that fallbacks are exercised in load tests, not just designed. Untested fallbacks usually fail when called for the first time during an incident.
53. Recommend a "kill switch" — a single config flag that disables the model entirely and forces the fallback. Useful when a regression is detected after rollout and rollback is not fast enough.

### Stage 10 — Reliability of the serving plane itself

54. Identify the dependencies of the serving plane: object store for weights, secrets store, feature store, retrieval database, sidecar logging, autoscaler control plane. Each is a potential failure mode at start-up and at request time.
55. Verify that model weights are baked into the image or pre-pulled to local disk before the container is marked ready, not fetched at first request. A first-request weight download is a guaranteed cold-start outlier.
56. Verify that readiness probes test the model actually responding, not just the HTTP server listening. A readiness probe that returns 200 before the model is loaded routes traffic to a non-functional replica.
57. Verify that liveness probes do not cause restart loops on heavy load — a liveness probe that times out because the model is busy will kill replicas at exactly the wrong moment. Recommend separating liveness (process alive) from readiness (process able to serve).
58. Verify that GPU drivers, CUDA versions, framework versions, and model formats are pinned. A silent driver upgrade is a classic incident.
59. Verify that there is an incident-runbook entry for the most likely failure modes (OOM, queue overflow, model serialisation failure, weight download failure, sidecar crash). Without runbooks, every incident is a clean-room debugging exercise.

### Stage 11 — Findings, severity, and the fix list

60. Severity rubric:
    - **Blocker**: violates the stated budget by construction, or causes outage on a single point of failure, or quality is unverified after a quantization step that is already in production.
    - **Major**: meets budget today but will fail within a known traffic horizon, or one failure mode away from an incident.
    - **Minor**: cost or efficiency leak; not user-visible at current scale.
    - **Nit**: stylistic — naming, dashboards, runbook polish.
61. For each finding emit: area (latency / throughput / cost / reliability / observability), current state, recommended change, expected impact (quantitative if possible), effort estimate (small / medium / large), and risk of the change.
62. Order the fix list by impact-divided-by-effort. The first three items should be the ones a team can ship in a sprint with the largest reduction in risk or cost.
63. Open with a one-paragraph summary: budget compliance status, top three findings, and a one-line verdict (Ready / Ready after fixes / Needs rework).
64. End with "what I did not review" — categories the audit skipped because of missing inputs (e.g. "no recent traffic data, so the autoscale recommendation is speculative").

## Outputs

The skill returns two artifacts:

1. `review_report` (markdown) — the audit organised by stage and severity.
2. `findings_json` (JSON) — the machine-readable findings as described.

## Examples

**Input (placeholder):**

`serving_topology`: "One Triton Inference Server replica behind an internal load balancer on a single A100 40GB. Model is a 13B-parameter LLM in fp16."

`model_details`: "Llama-style 13B. Currently serves with batch size 1, no continuous batching, no prefix caching."

`traffic_pattern`: "Peak 30 QPS, target p95 TTFT 1500ms, p95 end-to-end 6000ms for an average 200-token output."

`cost_budget`: "Hardware-units cap is 4 A100s across all our LLM features combined."

`failure_history`: "OOM under burst last month; replica restart took 4 minutes."

`review_scope`: "all"

**Audit reasoning (abbreviated):**

- Budget: A 13B model in fp16 on a single A100 cannot sustain 30 QPS with the stated TTFT and end-to-end budget under per-request inference. Batching is needed.
- Stage 3 batching: static batch-of-1 is the leading finding. Recommend continuous batching; expected throughput gain 4-8x.
- Stage 4 precision: fp16 is reasonable; consider int8 weight-only or fp8 if the hardware supports it. Require a quality regression check before adopting.
- Stage 5 hardware: KV cache memory math at concurrency 32 says fp16 weights take 26GB; KV cache at 4k context, 32 sequences pushes the total above 40GB. Either reduce concurrency, switch to int8 weights, or move to A100 80GB. Blocker on current configuration.
- Stage 6 autoscale: single replica is a SPOF; recommend a second replica plus queue-depth autoscaling.
- Stage 7 observability: TTFT and ITL are not separately tracked — add them. GPU memory is not tracked — add it.
- Stage 8 routing: no canary path exists — recommend one before the next prompt change.
- Stage 9 fallback: no fallback at all — recommend a smaller model fallback behind a circuit breaker.
- Stage 10 reliability: 4-minute restart implies weights download at startup — bake into image or pre-pull.

**Output excerpt:** ranked fix list — (1) enable continuous batching; (2) add second replica; (3) bake weights into image; (4) instrument TTFT/ITL; (5) plan canary and fallback paths.

## Limitations

- The skill reasons textually about a configuration; it does not run a load test. Quantitative throughput claims must be validated.
- Memory math is approximate; actual KV cache size depends on layer count, attention type, and runtime. The audit flags the order-of-magnitude problems, not exact byte counts.
- For workloads with hardware features the skill does not deeply know (specialist accelerators, custom kernels), recommendations may underweight options the user already has.
- Cost recommendations depend on provider pricing the user may not have shared; absolute dollar amounts are illustrative.
- Quantization quality claims must be validated by the user against their eval harness — the skill cannot certify quality.
- The skill is not a substitute for a network-level audit; assume the audit stops at the service boundary unless the user provides upstream details.
- Recommendations are biased toward stable, well-understood patterns. Bleeding-edge optimizations (speculative decoding, structured-sparsity hardware) are flagged only when the input shows they are already in use.

## Sources reviewed

- https://github.com/vllm-project/vllm
- https://github.com/bentoml/BentoML
- https://github.com/kserve/kserve
- https://github.com/mlflow/mlflow
- https://github.com/traceloop/openllmetry
- https://github.com/evidentlyai/evidently
- https://github.com/langfuse/langfuse
