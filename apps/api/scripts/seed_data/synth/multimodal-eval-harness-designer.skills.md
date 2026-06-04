---
id: skillsgit-curated/multimodal-eval-harness-designer
version: 1.0.0
name: Multimodal Eval Harness Designer
description: Design an evaluation harness for multimodal robot perception — hard-case curation, OOD probes, calibration metrics, spatial grounding, hallucination tests, and regression cohorts with golden-set discipline.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: robotics
tags: [niche:vlm-multimodal-perception, evaluation, hard-case-mining, ood-detection, calibration, hallucination, spatial-grounding, regression-cohort, golden-set]
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
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - multimodal eval harness
  - vlm evaluation design
  - robot perception evaluation
  - hard-case curation
  - ood probe set
  - calibration metrics ECE MCE brier
  - spatial grounding eval
  - hallucination benchmark
  - regression cohort design
  - golden set discipline
  - perception ablation matrix
  - vlm prompt template eval
example_invocations:
  - "We have a VLM-augmented perception stack on a delivery robot. Design an evaluation harness that catches regressions before we ship a new model."
  - "Lay out an OOD probe set covering weather, lighting, occlusion, and adversarial perturbations for our outdoor inspection platform."
  - "Our current eval is one accuracy number. Replace it with a harness that measures calibration, hallucination, and grounding separately."
inputs:
  - name: stack_description
    type: text
    required: true
    description: The perception stack under evaluation — what classical layers exist, what neural and VLM layers exist, what outputs the harness must score, and the platform's operational envelope.
  - name: operating_conditions
    type: text
    required: false
    description: Environments the platform operates in — indoor or outdoor, weather range, lighting range, time-of-day distribution, terrain, typical scene composition. Used to scope OOD probes.
  - name: failure_history
    type: text
    required: false
    description: Known field failures, near-misses, and incident reports. These seed the hard-case set with reality rather than synthetic guesses.
  - name: model_lineup
    type: text
    required: false
    description: Models the harness must compare or ablate over — base versus quantized, small versus large, prompt-template A versus B, with-fallback versus without.
  - name: cadence
    type: choice
    required: false
    description: How often the harness runs and what gates it sits in front of.
    choices: [pre-commit, nightly, per-release, shadow-on-fleet]
  - name: safety_class
    type: choice
    required: false
    description: Autonomy level and harm class for the platform; drives required acceptance gates.
    choices: [research-only, supervised-tele-op, supervised-autonomy, fully-autonomous-low-risk, fully-autonomous-high-risk]
outputs:
  - name: harness_design
    type: markdown
    description: A design document covering the eval cohorts, the metric suite, the gate policy, the golden-set governance, the perturbation library, and the regression-tracking plan.
  - name: design_json
    type: json
    description: Machine-readable plan with `cohorts`, `metrics`, `perturbations`, `gates`, `golden_set_policy`, `ablations`, `dashboards`, `open_risks`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Multimodal Eval Harness Designer

## When to use

Use this skill when a robotics or autonomy team needs to evaluate a perception stack that mixes classical computer vision, specialist neural detectors, and visual-language models, and the existing evaluation is either a single accuracy number, a hand-curated demo loop, or a vendor-supplied benchmark that does not reflect the platform's deployment distribution. The skill produces an architecture for an evaluation harness — what cohorts of data to maintain, what perturbations to apply, what metrics to compute, what gates the harness sits in front of, and how to govern the golden set over time as the platform and its models evolve.

The skill is correct at three moments. The first is when a team has a working stack and is about to ship a model update — they need to know whether the new model is better, worse, or different in ways that matter. The second is after a field incident — the team needs the incident to become a permanent regression test that can never silently disappear from the harness. The third is at the start of a serious deployment when a single number is no longer enough — the team needs to decompose performance into closed-vocabulary accuracy, open-vocabulary recall, hallucination rate, spatial grounding error, calibration error, and out-of-distribution behaviour, each gated separately.

The skill is not appropriate for designing the perception stack itself (use the perception stack architect), for selecting or training specific models, or for running general data labelling operations.

**Mandatory safety disclaimer.** This skill produces methodology guidance for evaluating robot perception. Evaluation harnesses are necessary but never sufficient: a harness that passes does not prove a stack is safe to deploy. Every harness design must be reviewed by qualified roboticists, every gate threshold must be empirically tuned to the platform's safety class, and every release that depends on the harness must also clear simulation, on-vehicle shakedown, and operator-in-the-loop review. No automated metric replaces qualified-engineer sign-off for safety-critical autonomy.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `stack_description` | yes | Anchors the harness to the layers, outputs, and integration surfaces under evaluation. |
| `operating_conditions` | no | Scopes the OOD probe set to conditions the platform will plausibly encounter. |
| `failure_history` | no | Seeds the hard-case cohort with real field events rather than synthetic guesses. |
| `model_lineup` | no | Determines the ablation matrix the harness must support. |
| `cadence` | no | Drives how compact the harness must be (a pre-commit gate is small; a per-release gate may be hours of compute). |
| `safety_class` | no | Sets the gate thresholds and the required cohort coverage. |

## How to apply

This skill walks an eighteen-stage pipeline. Stages 1 through 4 scope the harness. Stages 5 through 11 build the cohorts and metrics. Stages 12 through 15 design the gates, ablations, and golden-set discipline. Stages 16 through 18 produce the deliverable.

### Stage 1 — Restate the evaluation job in terms the harness can answer

1. Take `stack_description` and list every output the stack emits that a downstream consumer relies on. For each output, record its consumer, the consequence of an error, and the platform's tolerance shape — does a false negative or a false positive hurt more, does a slightly wrong answer hurt less than a confidently wrong answer, does a refusal hurt at all.
2. Group outputs into four families: *deterministic geometry* (pose, range, free-space), *closed-vocabulary classification or detection*, *open-vocabulary or language-conditioned detection and grounding*, and *generative or reasoning outputs* (captions, instruction grounding, scene Q&A). Each family will get a different metric suite in Stage 7.
3. Mark which outputs are *on-the-control-path* (a controller or safety stop blocks on them) versus *advisory* (a planner or operator console consumes them). The gate severity in Stage 12 will differ accordingly.
4. Reject outputs the harness cannot fairly measure. A free-text caption with no schema cannot be scored automatically without either a reference caption or a typed yes/no probe; the harness must either impose a schema upstream or fall back to a probe-based metric.

### Stage 2 — Define the cohort taxonomy

5. Define cohorts as named, frozen subsets of evaluation data. The harness scores each cohort separately and reports a metric vector, never a single average across cohorts. The taxonomy includes: *nominal* (representative of the deployed distribution), *long-tail* (rare classes and rare compositions sampled from logs), *hard-case* (curated from failure history and from confident-but-wrong cases), *out-of-distribution* (conditions outside the deployment distribution that the platform must degrade gracefully on), *adversarial* (deliberate perturbations and pathological compositions), *regression* (every cohort element that has ever caused a field incident, frozen permanently), and *acceptance* (a small fast cohort suitable for pre-commit gating).
6. Specify the *size budget* per cohort. A pre-commit acceptance cohort is dozens of items and runs in minutes. A nightly cohort is thousands. A per-release cohort is the full set. Tying budget to cadence keeps the harness honest.
7. Specify the *labelling regime* per cohort. Some cohorts admit automatic ground truth (synthetic perturbations from a known clean source), some require human labels with double-coding, some are *anchor* cohorts where the label is a high-cost expert annotation that is never re-derived.

### Stage 3 — Mine hard cases from real signal

8. Define hard-case mining sources: confident-but-wrong samples from production logs (model emitted high confidence and the downstream consumer or operator flagged a correction), near-miss events recorded by the safety layer, samples where two layers in the stack disagreed, samples where the stack returned a refusal or `unknown`, and samples flagged by the on-fleet drift monitor.
9. Define mining cadence: hard cases enter the candidate pool continuously, are reviewed in a weekly triage, and the accepted subset is promoted into the hard-case cohort with full provenance metadata (where the sample came from, who labelled it, why it was promoted).
10. Define the *promotion contract*: a hard case is never promoted without a corresponding label and a documented expected-behaviour. A bare image with no ground truth is data, not an evaluation item.

### Stage 4 — Build the OOD probe set

11. Enumerate the OOD axes that matter on the platform. Weather (rain, fog, snow, glare, dust); lighting (night, low-light, mixed indoor-outdoor, headlamp-only, backlit subjects, strobe); occlusion (partial, heavy, mutual, sensor-occluding dirt or rain on the lens); motion (motion blur from platform speed, rolling-shutter artefacts, dynamic scenes with fast-moving subjects); viewpoint (tilted horizons, unusually high or low mountings, fish-eye edges); composition (rare class combinations, dense scenes, sparse scenes, novel backgrounds); and modality degradation (a camera failure simulated by colour shift or by partial frame loss).
12. For each axis, identify whether real samples exist in logs or whether the harness must use synthetic perturbations of in-distribution samples. Both sources are valid; the harness tracks them separately and reports OOD performance by axis, not as a single number.
13. Pair every synthetic perturbation with its un-perturbed parent so the harness can measure *delta-from-clean* — the change in output as a function of the perturbation. A model whose answer shifts violently under a small perturbation is brittle even if every individual answer was nominally correct.
14. Include an *adversarial* sub-cohort with text-prompt injection probes (for VLM layers) and image-overlay probes (small visual artefacts known to mislead generative VLMs). These probes are intentionally pathological and tracked as a separate cohort, not folded into nominal accuracy.

### Stage 5 — Define synthetic perturbations precisely

15. Treat the perturbation library as a versioned artifact. Each perturbation has a name, a deterministic seed, an intensity scale, a documented expected effect, and a reference implementation that the harness can replay bit-for-bit. Perturbations include photometric (exposure, gamma, colour temperature, noise, blur, JPEG compression), geometric (small translations, rotations, perspective shifts), occlusion (cutout patches, simulated rain or snow streaks), and semantic (text-overlay injection, distractor object pasting from a held-out object bank).
16. Use perturbations to construct *invariance tests* (the model's output should not change) and *equivariance tests* (the model's output should change in a known way). A bounding box should translate when the image translates; a scene caption should mention the rain when rain is added.
17. Pin a per-perturbation *severity grid* so the harness reports a degradation curve rather than a single pass-or-fail at one severity. Brittleness shows up at the knee of the curve and is invisible at a single threshold.

### Stage 6 — Design the spatial grounding eval

18. For any layer that emits spatial outputs (bounding boxes, masks, points, region references in a caption), define the grounding eval cohort. Reference cohorts in the public benchmark family — referring-expression detection sets with IoU thresholds at 0.25 and 0.50 — and pair them with platform-specific cohorts drawn from the deployment distribution.
19. Score grounding separately from classification. A layer that names the right class but localizes to the wrong region is a different bug than a layer that localizes correctly but names the wrong class. The harness reports both metrics; collapsing them into mean Average Precision hides the failure shape.
20. Add *relational* grounding probes — "the cup on the left", "the panel behind the door", "the second person from the right". Relational language is where VLM grounding most often fails and where simple object-detection metrics give a false sense of competence.

### Stage 7 — Define the metric suite per output family

21. Deterministic geometry: traditional regression metrics (translation error, rotation error, IoU on free-space polygons) plus tail metrics (95th-percentile error, worst-case error) because mean error hides safety-relevant tails.
22. Closed-vocabulary detection: per-class precision and recall at multiple IoU thresholds, average precision per class, plus a *worst-class* metric — the harness reports the lowest per-class AP, not the macro average, because in deployment the worst class is what fails first.
23. Open-vocabulary detection: per-prompt precision and recall against the versioned prompt vocabulary, plus a *prompt-stability* metric measuring how output changes under semantically equivalent rewordings of the same prompt.
24. Generative outputs: structured-output validity rate (does the response parse against the required schema), probe-based correctness (does a follow-up yes/no probe agree with the answer), and hallucination rate. Hallucination scoring follows the polling-probe pattern — paired probes that ask "is X present" and "is Y present" for both real and absent objects, scored by precision and recall on presence.
25. Calibration: expected calibration error and maximum calibration error over confidence bins for every layer that emits a score, plus the Brier score for binary outputs. Calibration is reported per cohort because a model can be well calibrated on nominal data and badly miscalibrated on OOD data.
26. Refusal correctness: when the platform expects `unknown` as a valid response, the harness scores the *refusal-when-uncertain* rate and the *false-refusal-when-confident* rate as separate quantities.
27. End-to-end behaviour: where the harness can run a closed-loop simulation, score downstream metrics — time-to-completion, intervention rate, near-miss count — gated by the same per-cohort policy.

### Stage 8 — Calibration evaluation in depth

28. For each scoring layer, define the calibration bin policy (equal-width versus equal-mass; ten bins is the standard floor). Report ECE and MCE per cohort, not pooled, because pooled calibration hides cohort-specific miscalibration.
29. For multi-class classifiers, distinguish *top-label* calibration from *class-wise* calibration. A model can be calibrated on its top label while being badly miscalibrated on the second-and-third choices that downstream consumers actually use.
30. For generative VLMs whose confidence is not natively numeric, define the confidence proxy the harness will use (token log-probability, self-consistency over multiple samples, agreement with a second model) and treat the proxy itself as a versioned artifact. Changing the proxy is a harness change, not a model change.
31. Track *calibration drift* across model versions. Two models with similar accuracy and different calibration are not interchangeable from a downstream perspective; the harness flags the gap.

### Stage 9 — Hallucination evaluation in depth

32. Define hallucination probes for every generative output. Object-presence probes (paired "is X visible" and "is Y absent" probes with controlled positive and negative sampling), attribute probes (correct object, correct attribute), relation probes (subject-relation-object triples grounded in the scene), and count probes (numeric grounding for small counts).
33. For each probe family, sample negatives from three pools — *random* (uniform), *popular* (objects common in the training distribution but absent in this scene), and *adversarial* (objects that frequently co-occur with present objects, where the model is most likely to confabulate). Each pool stresses a different hallucination mechanism.
34. Score hallucination as a precision-and-recall pair, not a single accuracy. A model that refuses every probe achieves perfect precision and zero recall; a model that affirms every probe achieves perfect recall and zero precision; both are unsafe.
35. Track hallucination *rate by cohort*. Nominal hallucination is the cheapest to fix; OOD hallucination is the dangerous one and is reported separately.

### Stage 10 — Out-of-distribution detection evaluation

36. Where the stack exposes an OOD-detector layer (a classifier or score that flags "this input is outside my training distribution"), evaluate it as its own classification problem on the OOD cohort. Report area-under-ROC, area-under-PR, and a fixed-false-positive-rate operating point matched to the platform's tolerance for spurious OOD flags.
37. Distinguish *near-OOD* (same modality, shifted distribution — for example, a new building interior) from *far-OOD* (different modality or pathological input — for example, a sensor failure). Both must score, and the operating point for each may differ.
38. Where no OOD detector exists, evaluate *graceful degradation*: on OOD inputs the harness expects the stack to either return `unknown` at higher rates or to lower its confidence; sustained high confidence on OOD inputs is a critical failure that is reported with high visibility.

### Stage 11 — Latency, energy, and integration metrics

39. Beyond accuracy-shaped metrics, the harness records per-layer latency at p50, p95, and p99; end-to-end latency under realistic load; and where applicable, energy per inference and thermal trajectory under sustained load. Accuracy that degrades silently under thermal throttling is a known field-failure pattern and the harness catches it deliberately.
40. Record *integration metrics*: schema-parse failure rate, downstream-rejection rate, refusal rate, retry rate, and cost per mission for any cloud-served layer. A perception output that the downstream planner cannot parse is functionally a missing output even if the model produced it.

### Stage 12 — Define the gates and gate policy

41. The harness produces a metric vector; a gate maps that vector to a pass-or-fail decision. Gates are specified per cadence. Pre-commit gates check that no regression cohort regresses (zero tolerance on the frozen regression set) and that the acceptance cohort holds steady within a documented tolerance band. Nightly gates check OOD axes and calibration. Per-release gates check the full suite and require human review for any metric outside its tolerance.
42. Gate thresholds are *empirical*: they are tuned on the current production model's metric distribution, not borrowed from a paper or a vendor benchmark. A regression is defined as a statistically significant degradation against the rolling baseline, not as a deviation from an absolute number.
43. Critical gates trip on hallucination rate on the OOD cohort, on worst-class accuracy, on calibration error on safety-relevant outputs, and on regression-cohort failure. These four are non-negotiable; other gates may use softer thresholds.
44. Define *override discipline*: a gate trip can only be overridden by a named reviewer with a written justification that is stored alongside the release manifest. Silent overrides are the most common cause of harness rot and must be impossible by construction.

### Stage 13 — Ablations across model size, prompt template, and configuration

45. Define an *ablation matrix* whose rows are stack configurations and whose columns are cohorts. Typical rows include base versus quantized, small versus large, prompt-template A versus B, with-fallback versus without, with-OOD-detector versus without, deterministic versus stochastic sampling. The harness runs each row on the relevant cohorts and reports the matrix.
46. Track *delta tables*: for each cell, the change from a named baseline. The matrix is too dense to read at a glance; the delta table is the artefact the reviewer actually scans.
47. Treat prompt templates as full ablation rows, not as tweaks. A prompt change can shift hallucination rate by tens of points; the harness measures it under the same discipline as a model change.

### Stage 14 — Regression cohort governance

48. Every field incident becomes one or more regression-cohort items, with a label, an expected behaviour, and provenance. Items are immutable once promoted. The regression cohort grows monotonically; items are never deleted, only deprecated with a written reason.
49. The regression cohort runs on every release. A failure on a regression item blocks the release by default. The override discipline from Stage 12 applies.
50. The harness reports *regression coverage*: how many distinct incident classes have at least one regression item, how recent the most recent addition is, and which incident classes have zero coverage. Coverage gaps are a tracked risk.

### Stage 15 — Golden-set discipline

51. The *golden set* is a small, frozen, high-quality cohort whose labels are produced by expert annotation and whose composition is curated to span the platform's deployment surface. It is the harness's source of truth for cross-version comparison.
52. Govern access to the golden set tightly. Train-time pipelines do not touch the golden set, ever. The harness is the only consumer. A model that has accidentally seen golden-set data during training is no longer eligible to be evaluated against it; the harness assumes contamination and refuses to score.
53. Rotate a small portion of the golden set on a slow schedule — typically a single-digit percentage per quarter — to prevent overfitting against it. Rotated items are archived, not deleted, so prior results remain reproducible.
54. Treat golden-set labels as versioned. A label correction is a harness change that re-runs the historical score table so prior model performance is comparable under the corrected labels.

### Stage 16 — Reporting, dashboards, and observability

55. Specify the reporting surfaces. Per-run reports show the metric vector, the delta table against the baseline, the gate-pass status, and a top-K list of cohorts where performance changed most. A persistent dashboard shows time-series of every gate-relevant metric across releases.
56. Specify *drill-down paths*: from a regressed metric to the cohort, from the cohort to the affected items, from the item to the raw input and the model's raw response. Without drill-down the reviewer cannot diagnose a regression and the harness becomes ceremonial.
57. Specify *alarms*: a calibration regression on a safety-relevant output, a regression-cohort failure, a worst-class accuracy drop, a hallucination-rate spike on OOD. Alarms route to the on-call engineer and create a tracked ticket; no alarm is silently auto-closed.

### Stage 17 — Risk register and open questions

58. Enumerate residual risks: golden-set contamination, regression-cohort decay (incidents that have not been promoted), OOD-axis blind spots (axes the platform encounters but the harness does not cover), label drift (annotators apply different criteria over time), and metric gaming (a model whose training inadvertently optimizes the harness's metric proxies).
59. Maintain a known-unknowns register listing failure modes the team has not yet characterized. The harness reviewer is expected to add to this register, not only to the metrics.

### Stage 18 — Compose the deliverable

60. Open with a one-paragraph statement of harness intent: which outputs the harness scores, which gates it sits in front of, and what release decisions depend on it.
61. Render the cohort taxonomy with size, source, labelling regime, and refresh policy. Render the metric suite per output family. Render the gate matrix mapping cohort and metric to gate severity. Render the ablation matrix.
62. Emit `design_json` with structured fields so a downstream tool can derive a CI configuration, a dashboard layout, and a label-task brief from the JSON.
63. Close with the mandatory safety disclaimer restated, the open-risks list, and pointers to adjacent skills — the perception stack architect, the open-vocabulary detection deployer, and the edge model update strategy architect — for decisions the harness depends on but does not own.

## Outputs

The skill returns:

1. `harness_design` (markdown) — a written design with cohort taxonomy, metric suite, gate policy, golden-set governance, perturbation library, and regression-tracking plan.
2. `design_json` (JSON) — a structured plan suitable for downstream automation.

## Examples

**Input (placeholder):**

`stack_description`: "Indoor inspection robot with a LiDAR-depth geometry layer, a closed-vocabulary detector for fifteen building classes, an on-device open-vocabulary detector against a versioned eighty-prompt vocabulary, and a cloud frontier VLM called on stationary frames for scene Q&A with a typed JSON schema."

`operating_conditions`: "Commercial buildings, night-shift operation, mixed indoor lighting from emergency-only to fully lit, occasional contractor presence."

`failure_history`: "Three field events in the last quarter: a false 'fire-extinguisher' classification on a red signage panel, a hallucinated 'open door' caption when the door was closed, and a missed wet-floor sign under low light."

`model_lineup`: "Base versus quantized open-vocabulary detector; small versus medium scene VLM; two candidate prompt templates for the VLM."

`cadence`: "per-release."

`safety_class`: "supervised-autonomy."

**Plan (abbreviated):**

- Cohorts: nominal (1,500 items sampled from logs), long-tail (300 items emphasizing rare building objects), hard-case (200 items including the three field events and their cousins), OOD (400 items across low-light, occlusion, lens-dirt, and motion-blur axes), adversarial (100 items with text-overlay injection and distractor pasting), regression (52 items, frozen, including the three field events), acceptance (40 items for pre-commit), golden (200 expert-labelled items, rotation 4% per quarter).
- Metrics: classical detection precision and recall per class with worst-class flagged; open-vocabulary per-prompt precision and recall with prompt-stability; VLM schema-validity, probe-based correctness, hallucination rate (random and adversarial pools), calibration ECE and MCE per cohort, refusal correctness, p50 and p95 latency, cost per mission.
- Gates: zero-tolerance on regression cohort; hallucination rate on OOD cohort below the rolling baseline within a documented band; worst-class accuracy no worse than two points below baseline; calibration ECE on safety-relevant outputs flat or improving.
- Ablations: base versus quantized detector, small versus medium VLM, prompt-template A versus B; full matrix on nightly, top-K on pre-commit.
- Reporting: per-release dashboard with time-series, drill-down to raw inputs, alarms wired to on-call.

**Output excerpt:** the markdown harness design plus a JSON object whose `cohorts` array enumerates each cohort with size and refresh policy, `metrics` enumerates per-family metrics, `perturbations` lists the versioned perturbation library, `gates` lists the gate matrix, and `golden_set_policy` documents access and rotation.

## Limitations

- The skill produces a harness design, not a labelling operation or a data-collection plan. Acquiring the data and labels the harness assumes is its own programme.
- The skill assumes the team has representative production logs. Without representative logs, the hard-case cohort cannot be mined from reality and the harness will under-represent real failure modes.
- The skill is conservative on golden-set discipline and on override policy; research teams may relax these explicitly with documented rationale. Production teams should not.
- Metric thresholds in the deliverable are stated as *empirical and rolling*; the skill does not pin absolute numbers because they depend on the platform's safety class and on the operating distribution.
- The skill does not own model selection, prompt design, or training-data curation; it scores the artefacts those processes produce.
- The skill does not encode jurisdiction-specific regulatory acceptance criteria for autonomous systems; teams must layer those on top.

## Sources reviewed

- https://github.com/open-compass/VLMEvalKit (Apache-2.0)
- https://github.com/TRI-ML/vlm-evaluation (MIT)
- https://github.com/Jingkang50/OpenOOD (MIT)
- https://github.com/kkirchheim/pytorch-ood (Apache-2.0)
- https://github.com/EFS-OpenSource/calibration-framework (Apache-2.0)
- https://github.com/RUCAIBox/POPE (license: research/CC-BY-NC — read and cited for methodology only; no code reuse)
- https://github.com/The-AI-Alliance/GEO-Bench-VLM (Apache-2.0)
- https://github.com/cleanlab/ood-detection-benchmarks (AGPL-3.0 — read and cited for methodology only; no code reuse)
- https://github.com/showlab/Awesome-MLLM-Hallucination (MIT)
