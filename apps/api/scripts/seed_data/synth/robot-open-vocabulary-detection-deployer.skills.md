---
id: skillsgit-curated/robot-open-vocabulary-detection-deployer
version: 1.0.0
name: Robot Open-Vocabulary Detection Deployer
description: Deploy an open-vocabulary text-conditioned detector or segmenter on a robot — prompt-vocabulary discipline, score calibration, fallback strategy, and field evaluation methodology.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: robotics
tags: [niche:vlm-multimodal-perception, open-vocabulary-detection, prompt-engineering, segment-anything, grounding-detector, score-calibration, field-evaluation]
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
  estimated_tokens_per_invocation: 8800
trigger_keywords:
  - deploy open vocabulary detector
  - text conditioned detection robot
  - grounding detector deployment
  - segment anything robot
  - prompt vocabulary discipline
  - open vocabulary score calibration
  - text prompt detection robot
  - rare class long tail detection
  - zero shot detection robot
  - text-conditioned segmentation
  - open vocabulary fallback
  - open set detection deployment
example_invocations:
  - "We want to use an open-vocabulary detector on our delivery robot to handle rare objects our YOLO can't. How do we deploy it without a flood of false positives?"
  - "Help me design the prompt vocabulary and evaluation methodology for a text-conditioned detector on an inspection drone."
  - "What is the right fallback strategy when our open-vocab detector returns a low-confidence match for a safety-relevant class?"
inputs:
  - name: deployment_context
    type: text
    required: true
    description: Robot, environment, the role the open-vocabulary detector plays in the perception stack, and how it relates to the existing detector(s).
  - name: target_classes_or_concepts
    type: text
    required: false
    description: The classes, attributes, or concepts the team wants to detect — open-ended phrasing is fine; the skill will press for the actual decision list.
  - name: latency_budget
    type: text
    required: false
    description: Per-frame latency budget for the open-vocabulary layer and the rate at which it runs.
  - name: existing_detector
    type: text
    required: false
    description: The closed-vocabulary detector already on the platform and its known limitations.
  - name: data_available
    type: text
    required: false
    description: What labelled or unlabelled data the team has access to for calibration and evaluation.
  - name: safety_class
    type: choice
    required: false
    description: How autonomous the platform is.
    choices: [research-only, supervised-tele-op, supervised-autonomy, fully-autonomous-low-risk, fully-autonomous-high-risk]
outputs:
  - name: deployment_plan
    type: markdown
    description: A deployment plan covering prompt vocabulary, calibration procedure, fallback logic, integration contract, evaluation methodology, and rollout phases.
  - name: plan_json
    type: json
    description: Machine-readable plan with `prompt_vocabulary`, `calibration_procedure`, `thresholds`, `fallback_policy`, `evaluation_suite`, `rollout_phases`, and `open_risks`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Robot Open-Vocabulary Detection Deployer

## When to use

Use this skill when a robotics team is preparing to add a text-conditioned detector or segmenter — a model that takes a natural-language prompt and returns regions of an image matching that prompt — to a production-bound perception stack. The skill is concerned with deployment discipline, not with model selection or training. It produces a written plan covering the prompt vocabulary, the calibration procedure for the per-prompt thresholds, the fallback when the model abstains or disagrees with neighbouring layers, the integration contract with the rest of the stack, and the evaluation methodology that proves the deployment is fit for use.

The skill is appropriate when the team has already decided that an open-vocabulary layer belongs in the stack (typically because a higher-level architecture decision has named the layer — see the perception-stack architect skill) and now needs to make it work in the field without overwhelming downstream consumers with false positives, drifting against the prompt vocabulary, or introducing a load-bearing dependency on a model that hallucinates regions.

**Mandatory safety disclaimer.** This skill produces methodology guidance for VLM-augmented robotic perception. VLMs hallucinate, miss safety-critical edge cases, and degrade in low-light, adverse-weather, and out-of-distribution conditions. Every recommendation must be reviewed by qualified roboticists, validated in simulation, and never deployed as the sole perception layer in safety-critical contexts.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `deployment_context` | yes | Anchors the deployment to the platform's role and integration points. |
| `target_classes_or_concepts` | no | Seeds the prompt vocabulary discipline pass. |
| `latency_budget` | no | Selects the model class and run cadence. |
| `existing_detector` | no | Defines the boundary between closed and open vocabulary responsibilities. |
| `data_available` | no | Determines whether calibration thresholds can be set empirically or only conservatively. |
| `safety_class` | no | Determines the strictness of the fallback policy and rollout gating. |

## How to apply

The skill walks a thirteen-stage pipeline. Stages 1 through 3 frame the deployment; stages 4 through 8 design the operational mechanics; stages 9 through 11 design the evaluation and rollout; stages 12 and 13 produce the deliverable.

### Stage 1 — Anchor the role of the open-vocabulary layer

1. Read `deployment_context` and `existing_detector` and state in one sentence the *job* the open-vocabulary layer is being asked to do — for example, "detect rare classes that our closed-vocab detector cannot, on frames the closed detector marks as low-confidence, with results routed to the planner's semantic-annotation bus." Vague answers ("detect more things") get pushed back to concrete answers.
2. State the *non-job* of the open-vocabulary layer — what it is not allowed to do. By default the open-vocabulary layer is forbidden from deleting or moving boxes from a closed-vocabulary detector, from producing safety-critical signals on its own, and from running on the planner's blocking critical path unless an explicit exception is justified.
3. State the *complementary failure modes* the open-vocabulary layer brings against the existing stack. Open-vocabulary detectors typically fail by over-firing on visually plausible but textually mismatched regions; closed detectors typically fail by silence on rare classes. The combination is meant to cover both.
4. Decide whether the open-vocabulary layer is *bounded* (operates on a closed list of text prompts that the team curates) or *unbounded* (accepts arbitrary prompts at runtime). Bounded is the default for production; unbounded is reserved for research and for instruction-grounding flows handled by the instruction-grounding skill.

### Stage 2 — Build the prompt vocabulary

5. Treat the prompt vocabulary as the most important artifact of the deployment. It is the layer's effective class list and lives under version control.
6. For each candidate class or concept on the team's wish-list, write a *canonical prompt* (a short noun phrase or noun-phrase-plus-attribute) and a *positive exemplars set* (3 to 10 reference images for the team's evaluation set) and a *negative exemplars set* (counterexamples that historically confuse similar models — visually similar but wrong class). The negative set is what protects against false positives.
7. Where a class has natural sub-types, decide whether to enumerate sub-prompts ("orange traffic cone", "white traffic cone", "construction barrel") or to keep a single broad prompt ("traffic cone"). Sub-prompts are more precise but multiply the per-frame compute; the decision depends on the latency budget.
8. Where a class has confusable cousins, add the cousin as an *anti-prompt* — a prompt that exists in the vocabulary purely to absorb visually similar but semantically incorrect matches. A common pattern is to include both a target prompt and an anti-prompt for the most common false-positive substrate.
9. Where a class has compositional structure (an object with an attribute, an object in a state, an object holding another object), prefer separate prompts joined by a downstream rule rather than a single long prompt. Long prompts degrade detector accuracy and are harder to calibrate per-component.
10. For every prompt, record provenance: who proposed it, why, the evaluation result that justifies it, the date it entered the vocabulary, and the model checkpoint it was calibrated against. Vocabulary changes are deployments and require regression testing.

### Stage 3 — Score calibration

11. State explicitly that the model's raw similarity score (cosine, logit, or whatever the model emits) is not directly meaningful across prompts. A score of 0.4 for one prompt may be a confident match; 0.7 for another may still be a false positive. The deployment calibrates *per-prompt thresholds*.
12. Build a *calibration set* per prompt: at minimum 50 positives and 200 negatives drawn from the platform's environment. For prompts that fire rarely in the operating environment, augment with held-out frames from a representative public benchmark. Document the dataset provenance.
13. For each prompt, compute the precision-recall curve on the calibration set and select a threshold that meets the platform's per-class reliability budget. Safety-relevant prompts pick a higher threshold (favouring precision); coverage-driving prompts pick a lower threshold (favouring recall). Each choice is justified in writing.
14. Where the model returns multiple scores per region (a similarity score plus a "objectness" or region-quality score), calibrate a *composite* score, typically a weighted product or a learned gating function on a held-out set. Do not let the model's vendor-default composite leak into the platform without verification.
15. Record the calibration provenance per prompt: the calibration set, the model checkpoint, the threshold, the operator. A new model checkpoint requires a recalibration.

### Stage 4 — Integration contract with neighbouring layers

16. Define the *input contract*: which frames the open-vocabulary layer runs on. Typical patterns are run-every-Nth-frame (a slower clock than the main detector), run-on-promotion (only on frames where Layer 1 flagged low confidence), and run-on-demand (only when an upstream consumer requests it).
17. Define the *output contract* in the platform's existing detection schema: bounding box plus class label plus calibrated score plus prompt-id plus model-version plus prompt-version. The prompt-id and prompt-version are non-negotiable; they are what makes the output reproducible and auditable.
18. Define the *merging policy* with the closed-vocabulary detector. Default: closed-vocabulary detections are authoritative on geometry; open-vocabulary detections are merged in only when they do not overlap a closed-vocabulary box above a threshold, and they enrich rather than replace existing labels.
19. Define the *publish gate*. A detection is published only if it passes the per-prompt threshold and the geometric-consistency check (the box is in a plausible depth range, has plausible aspect ratio for its class, is within the freespace polygon, etc.). The gate is part of the contract.
20. Define the *throttling policy*. The publish rate is bounded by an upper limit per prompt to defend against pathological frames that produce hundreds of low-confidence boxes.

### Stage 5 — Promotion and gating logic from upstream layers

21. Where the open-vocabulary detector runs only on promoted frames, define the promotion conditions precisely. Common conditions: closed detector emits no boxes in a region of interest; closed detector's maximum confidence in the frame is below threshold; the planner has requested a semantic annotation; a tele-op operator has flagged the frame.
22. Define the *de-promotion* condition. A frame that has been processed by the open-vocab layer does not need to be reprocessed for a tunable cool-down period unless the scene has changed materially.
23. Define *backpressure*. When promotions arrive faster than the open-vocab layer can process, the queueing policy drops oldest frames or coalesces promotions on the same scene. A growing queue is itself a telemetry signal.

### Stage 6 — Fallback when the layer is unavailable, slow, or low-confidence

24. Enumerate the conditions under which the layer cannot deliver: model warm-up at boot, GPU saturation, out-of-memory, prompt-vocabulary version mismatch, or simply a frame where every prompt scores below threshold.
25. For each condition, specify the *fallback*. The default fallback is *silence with a documented capability gap*: the planner is informed that the semantic-annotation bus is empty for the affected frames and treats them as if the rare-class capability is offline. A degraded but predictable mode beats an unpredictable mode every time.
26. For safety-relevant prompts (a prompt whose mention triggers cautious behaviour), specify an *escalation fallback*: when the model is unavailable, the platform operates with a more conservative policy (lower speed, larger safety margin) until the layer returns. The conservative policy is itself versioned.
27. For boot warm-up, specify a *no-motion-until-ready* gate at platform startup for any safety-class above supervised-tele-op. The platform does not authorize motion until the open-vocab layer has passed its self-test.

### Stage 7 — Adversarial and out-of-distribution behaviour

28. Enumerate adversarial conditions: motion blur, low light, high dynamic range scenes (sun glare), reflective surfaces (mirrors, polished floors), repetitive textures (chain-link fences, tiled walls), partially occluded objects, and concept-drift scenes that did not appear in the calibration set.
29. For each, specify the expected behaviour: an explicit refusal pattern (the publish gate rejects the frame and the layer emits a structured "low-confidence frame" signal), a graceful degradation (the layer's threshold is auto-raised under known-bad lighting conditions), or a hand-back to the closed-vocab detector (in some adversarial regimes the closed detector outperforms the open-vocab layer and the merge policy reflects that).
30. Specify a *retro-reflective and saturated-pixel* check. Many open-vocab detectors hallucinate against retro-reflective surfaces; an image-statistics gate disables the layer on frames with saturated-pixel mass above threshold.
31. Specify *prompt-conditioning* against known adversarial prompts. Some prompts are reliable in clean weather and unreliable in rain or fog; the per-prompt threshold can be conditioned on a weather classifier or a daylight estimator.

### Stage 8 — Hallucination guardrails specific to open-vocabulary detection

32. The first guardrail is *geometric plausibility*: a detection whose depth or size is inconsistent with the class is rejected. A traffic-cone detection at 0.1 m height in the image but 200 m away on the LiDAR is a false positive.
33. The second guardrail is *cross-model agreement* for safety-relevant prompts. A safety-relevant prompt's detection is published only if a second independent model (a closed-vocab specialist, a second open-vocab model with a different backbone, a downstream geometric consistency check) agrees.
34. The third guardrail is *temporal consistency*: a transient single-frame detection of a safety-relevant prompt is held in a "pending" state for K frames; if it does not persist, it is dropped. K is per-prompt.
35. The fourth guardrail is the *visual-prompt audit*: periodically, a random sample of published detections is logged with the underlying crop image; an offline reviewer (human or another model) audits the sample for false positives. The audit rate is part of the deployment plan.
36. The fifth guardrail is the *known-bad-prompt* list: prompts that empirically over-fire in the deployment environment are quarantined and either removed from the vocabulary or routed only to advisory consumers, not to the planner.

### Stage 9 — Evaluation methodology

37. Build a multi-tier evaluation suite. Tier 1 is the per-prompt calibration set from Stage 3, used for threshold tuning. Tier 2 is a hard-case set: scenes where prior versions of the model historically failed, scenes from prior incidents, and scenes representing the most painful operational tail. Tier 3 is a field-replay set: recorded mission logs with retrospective ground truth, used for regression.
38. Define the *metrics*. Mean average precision across the prompt vocabulary is a starting point but is not sufficient; report per-prompt precision-at-fixed-recall, false-positive rate at the deployment threshold, and a hallucination rate (boxes with no matching ground-truth object) on the hard-case set.
39. Define *acceptance criteria*. A new model checkpoint or a new prompt vocabulary version must meet or exceed the previous version on every metric in the hard-case set; regressions on any safety-relevant prompt block deployment. Improvements that come with regressions in non-safety prompts are negotiated through review.
40. Define *coverage testing*. For every prompt in the vocabulary, the evaluation must show non-trivial positive and negative examples in the test set. A prompt with no test coverage is a deployment risk.
41. Define *robustness testing*. Apply synthetic perturbations to the test set: brightness shifts, blur, JPEG compression, additive noise, weather simulation. Report metric stability across perturbations.

### Stage 10 — Field rollout phases

42. Phase 1, shadow: the open-vocab layer runs alongside the existing stack but its detections are not consumed by the planner. Outputs are logged and audited. Duration: a defined mission-day count or an event-count threshold.
43. Phase 2, advisory: the layer's outputs are exposed to the operator console for tele-op visibility but still do not gate planner decisions. Operators report visible false positives and missed detections.
44. Phase 3, soft-engagement: the layer's outputs influence non-critical planner behaviour (speed reductions, semantic annotations on the operator map) but do not gate safety-critical decisions. Telemetry tracks operator overrides as an inverse-quality signal.
45. Phase 4, full engagement: subject to the safety case and operator review, the layer's outputs are merged into the perception state as designed. The fallback to a prior phase remains a one-click operation for at least one mission cycle.
46. Each phase has *exit criteria* (metric thresholds, operator-acceptance scores, cumulative event counts without unhandled regressions) and a *rollback procedure* defined before entry.

### Stage 11 — Telemetry, drift detection, and lifecycle

47. Log per-detection telemetry: prompt-id, score, threshold, accept/reject decision, neighbouring closed-vocab detections, model version, prompt version, image hash.
48. Log per-frame aggregates: detections-per-frame distribution, score-distribution per prompt, false-positive rate as estimated by the audit sample, queue depth.
49. Define drift monitors: a statistically significant shift in any prompt's score distribution from baseline triggers a recalibration alert; a shift in the audit-estimated false-positive rate triggers a deployment review.
50. Define the recalibration cadence: at fixed intervals, on model upgrade, on prompt-vocabulary change, on a drift-monitor alert, or after a defined number of operating hours.

### Stage 12 — Risk register and open questions

51. Enumerate residual risks: vocabulary maintenance burden (every new class is an evaluation-set expansion), score-calibration debt (thresholds that have not been re-validated against the current environment), model-vendor lock-in, dependence on a specific GPU class for latency, and the inherent unfalsifiability of "we did not miss anything important" without a representative ground truth.
52. Maintain a known-unknowns register: classes the team expects to encounter but has not yet evaluated, environmental conditions outside the calibration set, and safety-relevant prompts the team has not yet validated cross-model agreement for.

### Stage 13 — Compose the deliverable

53. Open with a one-paragraph deployment intent: what the layer does, what it does not do, what its acceptance criteria are.
54. Render the prompt vocabulary as a table: prompt, canonical phrase, threshold, calibration-set size, safety-relevance flag, version.
55. Render the integration-contract diagram (in prose) and the merging policy.
56. Render the rollout-phase table with exit criteria and rollback procedures.
57. Emit `plan_json` with structured fields for the prompt vocabulary, the thresholds, the calibration provenance, the fallback policy, the evaluation suite definition, and the rollout phases.
58. Close with the mandatory safety disclaimer restated, an open-risks list, and pointers to the perception-stack architect skill and the multimodal-evaluation skill for adjacent decisions.

## Outputs

The skill returns:

1. `deployment_plan` (markdown) — full deployment plan with prompt vocabulary, calibration, integration, fallback, evaluation, rollout.
2. `plan_json` (JSON) — structured plan for downstream automation.

## Examples

**Input (placeholder):**

`deployment_context`: "Delivery robot operating on suburban sidewalks. Existing YOLO-class detector for cars, pedestrians, bicycles, dogs. We want to add detection of long-tail obstacles — pallets, traffic cones, sign-A-frames, mobility scooters."

`target_classes_or_concepts`: "Pallets, traffic cones, A-frame signs, mobility scooters, low-height bollards, fallen tree branches, debris piles."

`latency_budget`: "Open-vocab layer at 5 Hz on promoted frames; existing detector untouched at 20 Hz."

`existing_detector`: "Closed-vocab CNN trained on 8 classes. Calibrated. Fails silently on long-tail."

`data_available`: "1200 labelled field frames; 8 weeks of unlabelled recorded mission logs."

`safety_class`: "supervised-autonomy."

**Plan (abbreviated):**

- Prompt vocabulary: 12 canonical prompts including anti-prompts for the two most common confusions (pallet vs. cardboard box, A-frame sign vs. open laptop on a stand). Each prompt with 50+ calibration positives.
- Per-prompt thresholds: precision-favouring for safety-relevant prompts (fallen-tree branch, pallet); recall-favouring for advisory prompts.
- Integration: run on promoted frames where closed detector has no box or max confidence below threshold; published with prompt-id and version; merged only where there is no closed-detector overlap.
- Fallback: layer-unavailable triggers conservative speed cap and reduces planner trust in semantic-annotation bus; safety-relevant prompts require cross-model agreement (closed-detector "unknown object" plus open-vocab match plus depth-plausibility).
- Evaluation: hard-case set seeded from prior tele-op interventions; weekly audit sample of 50 published detections; metric pack reported pre-deployment and on each model upgrade.
- Rollout: 2-week shadow, 2-week advisory, 4-week soft engagement, then full engagement subject to operator sign-off.

**Output excerpt:** the markdown plan plus a JSON object whose `prompt_vocabulary` is an array of prompt objects with thresholds and provenance, and whose `rollout_phases` array enumerates phase entry, exit criteria, and rollback.

## Limitations

- The skill is methodology, not a model. Choosing between specific open-vocabulary detector checkpoints is out of scope.
- Threshold calibration depends on representative data; a deployment without representative data must use conservative defaults and an aggressive audit programme.
- The skill assumes a closed-vocabulary detector exists as the load-bearing baseline. Pure open-vocabulary deployments (with no closed-vocab baseline) require additional layers of safety argumentation not covered here.
- The skill does not address latency optimization at the model-implementation level (quantization, distillation, ONNX export). Those decisions go to the model-serving skill.
- Vocabulary maintenance is unavoidable. A team that cannot commit to ongoing vocabulary curation should not deploy this layer.
- Open-vocabulary detection in adverse weather (heavy rain, snow, fog) remains an open research area; the plan flags this as a residual risk rather than solving it.

## Sources reviewed

- https://github.com/IDEA-Research/GroundingDINO (Apache-2.0)
- https://github.com/facebookresearch/segment-anything (Apache-2.0)
- https://github.com/facebookresearch/sam2 (Apache-2.0)
- https://github.com/mlfoundations/open_clip (MIT)
- https://github.com/openai/CLIP (MIT)
- https://github.com/IDEA-Research/Grounding-DINO-1.5-API (Apache-2.0)
- https://github.com/AILab-CVC/YOLO-World (license: GPL-3.0 — read and cited for methodology only; no code reuse)
