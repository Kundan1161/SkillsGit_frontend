---
id: skillsgit-curated/on-device-llm-deployment
version: 1.0.0
name: On-Device LLM Deployment Planner
description: Deploy a small language model on a device — model and tokenizer choice, context-window discipline, KV-cache memory budget, batch and concurrency limits, energy budget, cloud fallback, and prompt patterns tuned for constrained context.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:edge-inference, on-device-llm, kv-cache, context-window, tokenizer, energy-budget, cloud-fallback]
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
  - on device llm
  - mobile language model
  - small language model deployment
  - llama on phone
  - kv cache budget
  - context window discipline
  - tokenizer choice on device
  - phi mistral gemma on device
  - llm energy budget
  - cloud fallback llm
  - llm prompt for small context
  - constrained context prompt
example_invocations:
  - "We want to run a small LLM on phones for an offline writing-assist feature — plan the deployment."
  - "Design the KV-cache and context budget for a 3B-parameter model on a flagship phone with 8 GB RAM."
  - "Plan the cloud-fallback policy when the on-device LLM can't fit the prompt."
inputs:
  - name: feature_description
    type: text
    required: true
    description: What the LLM is used for, what the user sees, expected interaction pattern (one-shot, conversational, streaming), and how often it is invoked.
  - name: candidate_models
    type: text
    required: false
    description: Candidate base models the team is considering (e.g. small open-weights families and their parameter counts). Leave blank for the skill to propose.
  - name: target_devices
    type: text
    required: false
    description: Device tiers in scope, with RAM, accelerator availability, and OS minimum versions. The plan only commits to tiers where the model fits.
  - name: latency_and_energy_budget
    type: text
    required: false
    description: Time-to-first-token budget, tokens-per-second budget, energy cost per interaction, and thermal limits.
  - name: privacy_posture
    type: text
    required: false
    description: Whether prompts may leave the device, whether telemetry on prompts is permitted, and any regulated-data categories.
  - name: cloud_endpoint_available
    type: choice
    required: false
    description: Whether the team has a cloud LLM endpoint that can serve fallback requests.
    choices: ["yes", "no", "planned"]
outputs:
  - name: deployment_plan
    type: markdown
    description: Structured plan covering model choice, tokenizer, quantization handoff, context window, KV-cache budget, concurrency, energy, prompt patterns, fallback policy, and rollout guardrails.
  - name: plan_json
    type: json
    description: Machine-readable plan with keys `model_choice`, `tokenizer`, `quantization`, `context_budget`, `kv_cache`, `concurrency`, `energy`, `prompt_patterns`, `fallback`, `rollout`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# On-Device LLM Deployment Planner

## When to use

Use this skill when a team wants to put a language model — typically in the one-to-eight-billion parameter range — onto a consumer device (phone, tablet, laptop, embedded board) and have it serve a real product feature. The deliverable is a deployment plan that names a specific model size and family, a tokenizer, a quantization handoff, a context-window discipline, a KV-cache memory budget, a concurrency policy, an energy budget, a cloud-fallback policy, and prompt patterns that work inside the constraints. The plan does not include the surrounding pipeline (use the edge-inference pipeline-architect skill for conversion chain, runtime selection, telemetry, and OTA) or the deep quantization decisions (use the quantization-strategist skill for those).

The skill applies to features like local summarisation, on-device writing assist, offline classification with explanation, code completion, voice command parsing, and small-context Q&A over local content. It does not apply to large frontier-model use cases that require multi-hundred-billion-parameter capability — those run in the cloud. The skill is opinionated about being conservative: it prefers a smaller model that works to a larger model that intermittently fails.

It is not the right skill for choosing whether to use an LLM in the first place, for fine-tuning the LLM, for evaluating LLM output quality (use a dedicated LLM-eval skill), or for cloud LLM-serving architectures.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `feature_description` | yes | Anchors model size and latency budget. |
| `candidate_models` | no | Constrains or guides the model recommendation. |
| `target_devices` | no | Determines which tiers can host the model. |
| `latency_and_energy_budget` | no | Sets the gating quantization and concurrency choices. |
| `privacy_posture` | no | Determines whether cloud fallback is allowed and what telemetry is permitted. |
| `cloud_endpoint_available` | no | Gates the fallback policy. |

## How to apply

The skill walks a twelve-stage pipeline. Stages are sequential because model choice gates tokenizer, tokenizer gates context budget, context budget gates KV-cache budget, and KV-cache budget gates concurrency.

### Stage 1 — Frame the feature

1. Restate the feature in one paragraph. The paragraph must answer: what is the user doing, what does the LLM produce, how long is the typical prompt, how long is the typical output, how often is the feature invoked per session, and what does a failure look like to the user.
2. Decide the interaction shape. One-shot (single request, single response) is the simplest and forgives latency hiccups. Streaming (tokens appear as generated) raises the bar on time-to-first-token. Conversational (multi-turn) raises the bar on KV-cache management. Each shape gates later stages.
3. Decide acceptable quality. On-device small models will be worse than frontier cloud models at the same task. State the acceptable quality floor concretely — pass rate on an internal eval, helpfulness rating, agreement-rate with a larger reference model. If the user cannot accept the quality of small models, the right answer is "do not deploy on-device for this feature" and the plan halts.
4. Decide the offline-first vs network-preferred posture. An offline-first feature must work without network and may use cloud as an enhancement; a network-preferred feature uses on-device only as a fallback. The fallback policy in Stage 9 depends on this.

### Stage 2 — Choose the model size and family

5. Anchor model size to the lowest-tier device that must be supported. If the lowest tier has 6 GB RAM with 3 GB available to the app, the model in 4-bit quantization plus its activations and KV cache must fit in roughly 1.5 GB. That is consistent with a model on the order of one to three billion parameters in 4-bit weights, depending on the architecture.
6. Prefer model families with well-supported on-device toolchains: small models in the 1-3B range from open-weights families, instruction-tuned variants that have been validated for chat-style outputs, and models whose tokenizer is small enough that the tokenizer file does not itself bloat the artifact.
7. Reject models whose license is incompatible with the deployment. Some "open" weights forbid commercial use or have field-of-use restrictions. The plan must record the license and confirm fit.
8. If the team has multiple device tiers, recommend a single model rather than a per-tier lineup unless the smallest tier truly cannot host the model. Per-tier model lineups multiply the evaluation and OTA burden.
9. Record the exact model variant: parameter count, training recipe, instruction-tuning recipe if any, base or chat variant, and the version tag. "Phi-style 3B" is not a variant; a specific checkpoint hash is.

### Stage 3 — Pick the tokenizer

10. The tokenizer ships with the model and is typically not interchangeable. Confirm the tokenizer file format is supported by the chosen runtime — byte-pair-encoding, SentencePiece, and tiktoken-style tokenizers have different runtime support.
11. Tokenizer choice affects context length. A tokenizer with a larger vocabulary compresses common text into fewer tokens, effectively giving more context for the same budget. For multilingual features, a tokenizer with multilingual coverage is critical; a primarily-English tokenizer triples the token cost of non-English text and silently halves the usable context.
12. Pin the tokenizer artifact and its hash alongside the model artifact. Tokenizer mismatches between training and inference are a silent catastrophe — outputs degrade quietly with no obvious error.
13. Plan tokenizer streaming-decode discipline. Some tokenizers split tokens across characters in ways that make incremental decoding mid-word produce broken UTF-8; the runtime must buffer or the UI must hide partial tokens until the next decodable boundary.

### Stage 4 — Quantize for the device

14. The deep mechanics belong to the quantization-strategist skill. The deployment plan must record the high-level handoff: target precision (4-bit weight-only is the practical default for memory-constrained on-device LLM deployment; 8-bit for larger memory budgets), group size, calibration data source, and accuracy regression budget against the floating-point baseline.
15. The accuracy regression budget must be re-measured on the actual on-device feature, not just on a general LLM benchmark. A 4-bit quantization that loses one point on a generic benchmark may lose three points on the user's specific task.
16. The quantization step must be wired into CI: every change to the source model triggers a quantization run and a regression test. Hand-quantized one-off artifacts are a maintenance trap.
17. Pin the quantization toolchain version. The same model and the same calibration set with two different tool versions produce different artifacts.

### Stage 5 — Budget the context window

18. The context window is the maximum number of tokens the model can attend to in one forward pass. Models advertise large theoretical context windows; on-device practical context windows are smaller because the KV cache must fit in memory.
19. Compute the practical context window from first principles: available memory after weights and activations, divided by the per-token KV cache size (two tensors, key and value, with size equal to head dimension times number of attention heads times number of layers, in the activation precision). The result is a hard ceiling, not a target.
20. Pick a working context window comfortably below the ceiling — typically 50% to 70%. The headroom absorbs longer-than-expected inputs and avoids out-of-memory crashes that the OS reports as the app being killed.
21. The system-prompt budget, the user-input budget, the retrieval-context budget (if any), and the output budget all sum to the working context window. The plan must allocate them explicitly. A common pattern: 256 tokens for the system prompt, 1,024 for user input, 1,024 for retrieved context, 512 for the output, summing to 2,816 of a 4,096-token working window with a 1,280-token cushion.
22. Enforce the per-section budgets at the prompt-builder layer, not by hoping. Truncate retrieved context, summarise long user input, and trim multi-turn history before the model sees it.

### Stage 6 — Budget the KV cache

23. The KV cache dominates memory for long-context generation. The deployment plan must record the maximum KV cache size in bytes for the chosen context window.
24. The KV cache is itself a candidate for quantization. INT8 KV cache is widely supported and roughly halves the cache footprint with a small quality cost. INT4 KV cache is more aggressive and may show quality regressions on certain tasks; pre-register a quality probe before committing.
25. For multi-turn conversations, the KV cache holds the history. The plan must define a history-trimming policy: keep the last N turns, summarise older turns into a system-prompt addendum, or hard-truncate at a token limit. Unbounded history will eventually crash the app on a long-running conversation.
26. Cache reuse across calls: a system prompt that is identical across calls can have its KV cache reused, saving the prefill cost of those tokens. The plan should call out which prompt segments are cacheable and which are per-call.
27. For features that fan out to multiple LLM calls in quick succession (e.g. a multi-step agent), KV cache reuse compounds; the plan should pre-prefill stable segments.

### Stage 7 — Set concurrency and queueing

28. On-device LLM inference is typically serialized: one inference at a time per accelerator. The plan must define what happens when a second request arrives while the first is running. Options: queue, cancel-and-replace (drop the older request), reject (return a "busy" signal to the caller).
29. For user-facing features, cancel-and-replace is usually the right default — the user has changed their mind and the older response is stale. For background features (a feature pre-emptively summarising new content), queueing with a bounded queue is appropriate.
30. Concurrency between LLM and the rest of the app: the LLM thread must not block the UI thread. Pin the LLM to its accelerator and yield CPU to the UI. The plan must call out the threading model of the chosen runtime; some runtimes monopolise the CPU.
31. For streaming features, the time-to-first-token (TTFT) is dominated by prompt prefill. A 2,000-token prompt on a mid-tier device takes hundreds of milliseconds to prefill; the plan must surface this to the UI as a "thinking" indicator. After prefill, subsequent tokens arrive at the steady-state decode rate.

### Stage 8 — Budget the energy

32. LLM inference is energy-intensive. The plan must include an energy cap: maximum joules per interaction, maximum sustained tokens-per-second under thermal load, and how the feature behaves when the device is in low-power mode.
33. In low-power mode, the OS may throttle the accelerator. The plan must define the throttled behaviour: lower throughput (acceptable), fallback to a smaller model (an option), or graceful degradation of the feature (the safest).
34. Sustained inference heats the device. Thermal throttling reduces throughput unpredictably. For features used in short bursts (one or two interactions per session), this is not a concern; for features used continuously (a live captioning feature), the plan must include a duty cycle and a thermal-monitoring guard.
35. Background invocations have a much smaller energy budget than foreground. The plan must define which invocations are allowed in background, which only in foreground, and what to do when a background invocation is requested but the device is on battery.
36. Energy telemetry: emit per-interaction energy estimates and aggregate them. A regression in energy per interaction is a quiet bug that surfaces as user complaints about battery life.

### Stage 9 — Define the cloud fallback policy

37. The fallback policy depends on `privacy_posture` and `cloud_endpoint_available`. If prompts may not leave the device, fallback is restricted to "smaller on-device model" or "feature degraded". If a cloud endpoint exists and prompts may leave, fallback to cloud is permitted.
38. Define the trigger conditions for fallback, ordered by priority:
    - The device is below the minimum supported tier.
    - The model artifact is not yet downloaded or failed integrity check.
    - The prompt exceeds the working context window even after trimming.
    - On-device inference timed out beyond the latency budget.
    - The device is in low-power or thermal-throttled state and the feature is not graceful-degradation-safe.
    - The quality probe (a periodic self-check inference) failed recently.
39. For each trigger, the fallback action: smaller on-device model, cloud, the previous version, or a graceful-degradation path (hide the feature, prompt the user to try again).
40. The fallback path must be exercised in CI on a regular cadence. A fallback that has not run in months is not a fallback.
41. Match the user-visible behaviour between on-device and cloud as far as possible. Inconsistent answers between the two are a top source of user-reported inconsistency.
42. Document a privacy-aware fallback: when prompts may leave the device only with consent, the fallback prompts for consent on first use and remembers the choice. The plan must specify the consent UI and the storage of the choice.

### Stage 10 — Design prompt patterns for constrained context

43. Small on-device models cannot follow long, complex instructions as reliably as frontier models. The plan must recommend prompt patterns that fit the model's instruction-following capacity.
44. Recommended patterns:
    - Short, imperative system prompts (a few hundred tokens max). Long systems prompts confuse small models.
    - Concrete few-shot examples for any non-trivial output format. Two examples are typically better than five for small models because they take less context.
    - Structured output prompted by a clear schema and a leading bracket or fence. Small models can mis-format JSON; use a forgiving parser.
    - Tool-use patterns simplified to a single tool per call. Multi-tool routing is unreliable in this size range.
    - Refusal patterns built into the system prompt for safety-relevant categories.
45. Add a fallback prompt for cases where the primary prompt failed (output empty, malformed, or off-task). The fallback prompt is simpler and explicitly tells the model what to do; it can also degrade to "summarise the input and stop".
46. For retrieval-augmented features, retrieve aggressively but inject minimally. Top-1 to top-3 retrieved chunks are usually a better trade-off than top-10 on small models.
47. For multilingual features, prompt in the user's language rather than English where the model supports it. Small models often hallucinate translation steps that cost tokens and quality.
48. The plan must include at least one regression-test prompt per language and per failure mode, run on every model update.

### Stage 11 — Plan the rollout guardrails

49. The first launch of an on-device LLM to a real fleet is high-risk. Plan a staged rollout: a closed beta, a small percentage rollout, and a full rollout. Each stage has a pass criterion against the model-health composite (quality probe pass rate, latency p95, fallback rate, energy per interaction, crash rate).
50. Define a kill switch: a server-controlled feature flag that disables the on-device LLM and degrades the feature gracefully. The kill switch must be fast (under a minute to take effect) and must default to "feature disabled" if the server is unreachable, to avoid a runaway broken feature.
51. Quality monitoring at scale is hard without sending prompts off-device. Use synthetic probes: a fixed set of prompts run on a sampled set of devices on a schedule, with the outputs compared to expected behaviour using on-device heuristics, and only the pass/fail rates leaving the device.
52. Plan for model deprecation. When the model is replaced, devices must update; devices that fail to update must continue to receive at least correctness-fixes for a defined window. Otherwise long-tail devices ship a known-bad model indefinitely.

### Stage 12 — Compose the deliverable

53. Open with a one-paragraph deployment intent: model family and size, target devices, expected quality versus cloud reference, and feature shape.
54. Render the plan in stage order. Include the explicit token-budget allocation (Stage 5) and the explicit KV-cache budget (Stage 6) as small tables.
55. Render the fallback policy as a decision table: trigger -> action.
56. Emit the JSON in `plan_json` with stable keys for downstream tooling.
57. Close with a "what this plan does not cover" section. Specifically: it does not run the inference, it does not benchmark the model on real hardware, it does not adjudicate license fit, and it does not encode platform store policies on on-device generative models.

## Outputs

The skill returns two artifacts:

1. `deployment_plan` (markdown) — the stage-organised plan with explicit budgets and a fallback decision table.
2. `plan_json` (JSON) — structured plan with keys `model_choice`, `tokenizer`, `quantization`, `context_budget`, `kv_cache`, `concurrency`, `energy`, `prompt_patterns`, `fallback`, `rollout`.

## Examples

**Input (placeholder):**

`feature_description`: "An offline writing-assist feature in a note-taking app. The user selects a passage and asks for a rewrite or a summary. Typical input is 200-800 words. Output should stream so the user sees progress."

`candidate_models`: "We are considering a 3B-parameter instruction-tuned open-weights model."

`target_devices`: "iOS 17+ on devices with at least 6 GB of RAM; Android 12+ on devices with at least 8 GB of RAM. Lowest-tier supported phone has Neural Engine on Apple and an NPU on Android."

`latency_and_energy_budget`: "TTFT under 800 ms, sustained 25 tokens/second; energy under 1.5 J per typical interaction."

`privacy_posture`: "Notes never leave the device. No prompt content in telemetry."

`cloud_endpoint_available`: "no."

**Plan (abbreviated):**

- Model: 3B-parameter instruction-tuned variant, 4-bit weight-only quantization with group size 64, INT8 KV cache, license confirmed for commercial mobile distribution.
- Tokenizer: SentencePiece, vocabulary size sufficient for multilingual coverage with the supported languages explicitly enumerated; tokenizer artifact pinned with hash.
- Context budget: 4,096-token working window. System prompt 192 tokens, user-selected passage up to 1,536, conversation history 512, output 1,024, cushion 832.
- KV cache: 256 MB ceiling, INT8 cache, history-trim policy keeps the last two turns plus a summarised system addendum.
- Concurrency: cancel-and-replace on new request; LLM on its accelerator, UI on main thread.
- Energy: under 1.5 J per 200-token rewrite; thermal guard stops sustained generation after 5 s of continuous decode and recommends a smaller selection.
- Fallback: no cloud (privacy). Triggers map to "previous on-device model version" or "feature unavailable; please try a smaller selection" with consent-free graceful degradation.
- Prompt patterns: short imperative system prompt with two few-shot rewrite examples and one summary example; a fallback prompt that asks only for a summary if the primary prompt yields no usable output.
- Rollout: closed beta on the developer's own devices, then 5% to flagship-tier users, then 100% after seven days of clean canary health.

## Limitations

- The skill produces a plan, not running code. Model loading, tokenizer integration, and prompt-builder layers are engineering tasks the user executes.
- Quality of on-device small models for a specific feature must be measured, not assumed. The plan recommends a quality floor but does not estimate it.
- Energy estimates are heuristic. On-device measurement is the only reliable source.
- Long-running features (multi-minute continuous generation) need thermal modeling beyond the duty-cycle heuristic the plan provides.
- The skill assumes single-user, single-device deployment. Shared-device or multi-user scenarios need additional KV-cache isolation that this plan does not encode.
- Model licensing is a legal question; the plan flags it but does not adjudicate.
- Some platforms have policies on generative on-device features (age-gating, disclosure, content moderation) that vary by jurisdiction and store; the plan recommends a separate compliance review.

## Sources reviewed

- https://github.com/ggml-org/llama.cpp
- https://github.com/mlc-ai/mlc-llm
- https://github.com/pytorch/executorch
- https://github.com/microsoft/onnxruntime
- https://github.com/apple/coremltools
- https://github.com/huggingface/transformers
- https://github.com/tensorflow/tensorflow
