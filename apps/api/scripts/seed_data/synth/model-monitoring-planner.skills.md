---
id: skillsgit-curated/model-monitoring-planner
version: 1.0.0
name: Model Monitoring Planner
description: Plan production monitoring for an ML or LLM model — data drift, concept drift, quality, safety, and business KPIs — with alert thresholds, sampling strategy, and incident-response wiring.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:ml-engineering, monitoring, drift, observability, alerts, model-quality, safety, kpi]
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
  - plan model monitoring
  - drift monitoring
  - data drift
  - concept drift
  - model quality alerts
  - ml observability plan
  - llm production monitoring
  - safety monitoring
  - alert thresholds for ml
  - kpi monitoring for model
  - silent model failure
  - shadow scoring
example_invocations:
  - "Plan monitoring for our churn-prediction model — drift, quality, and the business KPI tie-back."
  - "We have an LLM chatbot in production with no monitoring. Design the dashboards and alerts."
  - "Help me decide what alerts to wake the on-call for vs which to leave as a weekly review."
inputs:
  - name: model_description
    type: text
    required: true
    description: What the model does — task type, inputs, outputs, where it lives, how often it scores.
  - name: business_kpis
    type: text
    required: false
    description: The business metrics the model is meant to move (conversion, revenue per session, support deflection, etc.) and how the team currently measures them.
  - name: ground_truth_lag
    type: choice
    required: false
    description: How long until the true label is known after the prediction.
    choices: [seconds, minutes, hours, days, weeks, months, never]
  - name: data_sensitivity
    type: text
    required: false
    description: Sensitivity classification of the inputs and outputs (PII, financial, health, public). Drives the safety monitors and access controls.
  - name: incident_tolerance
    type: choice
    required: false
    description: How sensitive the business is to a model regression.
    choices: [tolerant, normal, intolerant]
  - name: existing_observability
    type: text
    required: false
    description: What logging, metrics, and dashboards already exist that the plan can build on.
outputs:
  - name: monitoring_plan
    type: markdown
    description: Plan covering signals, sampling, thresholds, dashboards, alerts, escalation, and incident response.
  - name: signals_json
    type: json
    description: Structured list of monitored signals with `signal_name`, `category`, `computation`, `frequency`, `alert_threshold`, `severity`, `owner`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Model Monitoring Planner

## When to use

Use this skill when a model — classical ML or LLM-powered — is in production or about to be, and the team realises they need monitoring beyond "the service responds with 200". The trigger is usually one of: a silent regression that everyone discovered too late, a new model launch where the team wants to be confident the rollout is safe, a compliance requirement that demands documented monitoring, or the on-call team complaining they have no way to know when the model is wrong.

The skill produces a written monitoring plan — the signals to track, how to sample them, the thresholds that fire alerts, who responds, and how the plan wires back into the incident-response process. It does not stand up the monitoring stack; it tells the user exactly what to stand up.

The skill is appropriate for classification, regression, ranking, recommendation, forecasting, and LLM-driven features. The signals differ — a classification model has confusion-matrix-style monitors, an LLM has refusal-rate and judge-score monitors — but the methodology is the same: pick signals that connect to the business outcome, sample at a rate the team can sustain, set thresholds that don't cry wolf, and route alerts to humans who can act.

The skill is not a substitute for the eval harness — the eval harness measures quality on a fixed test set under controlled conditions; monitoring measures quality on live traffic under whatever conditions arrive. Both are needed and they share signals.

The skill is not the right tool for infrastructure monitoring of the serving plane itself (latency, error rates, GPU utilisation) — that belongs in the model-serving-reviewer skill. This skill assumes the serving plane is observed and focuses on the model-quality side.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `model_description` | yes | Anchors which signals are applicable. |
| `business_kpis` | no | Drives the highest-priority monitors. |
| `ground_truth_lag` | no | Determines whether quality can be measured directly or only proxied. |
| `data_sensitivity` | no | Drives the safety monitors. |
| `incident_tolerance` | no | Calibrates alert thresholds. |
| `existing_observability` | no | Avoids re-recommending what is already in place. |

## How to apply

The skill walks a ten-stage planning pipeline.

### Stage 1 — Define what "the model failing" means in this product

1. Restate the model's purpose and the user-visible consequence of model error in one sentence each. "The fraud model fails when fraudulent transactions are approved" is concrete; "the fraud model fails when it makes a wrong prediction" is not actionable.
2. Identify the failure mode that hurts most. For a recommender it may be irrelevance, not error. For an LLM it may be hallucination, not low-quality phrasing. For a forecaster it may be under-prediction, not over-prediction. The monitoring plan weights the highest-cost failure mode most heavily.
3. Identify the failure modes that hurt least, so the plan does not over-monitor them. Every signal added is a maintenance cost.
4. Identify what changes about the failure profile if a regression goes undetected for one hour, one day, one week. This drives the cadence of each monitor — anything whose damage scales linearly with time-undetected gets near-real-time monitoring; anything that compounds slowly can be weekly.

### Stage 2 — Catalog the signals

5. Group signals into six categories:
    - **Input data drift**: distribution of features going into the model.
    - **Concept drift / output drift**: distribution of model outputs (predictions, scores, generated text).
    - **Direct quality**: comparison of predictions to ground truth when ground truth is available.
    - **Proxy quality**: user-feedback signals when ground truth is delayed (clicks, dwell time, conversions, refunds, escalations, thumbs-up/down, edit-after-suggestion rates).
    - **Safety / policy**: refusal correctness, prohibited-content rate, PII exposure, jailbreak success, fairness metric across slices.
    - **Business KPI tie-back**: the actual product metric the model exists to move.
6. Every monitor maps to one category. A monitor without a category does not have a clear consumer and should be cut.
7. Apply Pareto: the plan should have 6-15 signals total, weighted toward the highest-cost failure modes. Monitoring everything monitors nothing.

### Stage 3 — Input data drift

8. For each input feature, identify whether it is continuous or categorical. Continuous features are monitored with distribution-shift tests (Kolmogorov-Smirnov, Wasserstein, Population Stability Index). Categorical features are monitored with categorical-distribution-shift tests (Chi-squared, Jensen-Shannon divergence, PSI on bucketed categories).
9. Pick a **reference window** for the comparison. The reference is usually the training-data feature distribution or a recent stable production window. Pin the reference explicitly and re-pin only when the team makes a deliberate decision to.
10. Pick a **detection window** for the live data. Trade-off: shorter windows detect faster but are noisier; longer windows are smoother but lag. Default: a rolling 1-day window for high-volume features, longer for lower volumes.
11. Set thresholds in terms of effect size, not p-value. A KS-test on a million-row dataset is "significant" for almost any difference; the question is whether the difference is *large enough to matter*. Use PSI bands (0.1 low, 0.25 high) or Jensen-Shannon thresholds calibrated to historical noise on the same feature.
12. Differentiate **upstream** drift from **the model's view** of the input. The data pipeline can be working, but the feature value the model sees is stale because the online store has a lag. Monitor the feature value at the moment of inference, not the value in the warehouse.
13. Drift in a single feature is not always a problem. Recommend that drift alerts route to a daily review unless the drifting feature is on the top-N-importance list for the model. Drift on a low-importance feature usually does not move predictions; drift on a top feature usually does.
14. Multivariate drift — features moving in concert — can be invisible to univariate tests. Recommend a multivariate drift signal (PCA reconstruction error, autoencoder reconstruction error) as a single guardrail metric in addition to per-feature monitors.

### Stage 4 — Output drift and concept drift

15. The model's own output distribution is a cheap, leading indicator. If a classification model suddenly predicts the rare class 5x more often than before, something has changed. Track the output distribution and alert on shifts that are larger than the natural day-of-week variation.
16. For ranking and recommendation models: track the distribution over the top-K predicted items, not just the top-1. Concentration shifts (the system suddenly recommending fewer distinct items) are an early signal.
17. For LLM outputs: track the distribution of output lengths, the distribution of structured-field values (categories chosen, sentiment classifications), and the rate of model-flagged uncertainty (when the model says it doesn't know).
18. Concept drift means the *relationship* between input and label has changed, not just the input distribution. It is best detected with direct quality metrics (Stage 5) when ground truth is available; otherwise approximate it with proxy metrics.
19. Set thresholds on output drift in terms of historical baseline variance. A two-standard-deviation drift over a week, sustained, is usually a real shift; a one-day spike usually is not.

### Stage 5 — Direct quality monitoring

20. If `ground_truth_lag` is seconds-to-hours, the plan can include a near-real-time quality monitor: as labels arrive, update a rolling estimate of the primary metric and alert on regressions.
21. If lag is days-to-weeks, near-real-time direct monitoring is impossible; the plan must rely on proxy metrics (Stage 6) for fast feedback and direct quality for a weekly or monthly verdict.
22. If `ground_truth_lag` is "never" (true label is fundamentally unobservable), direct quality monitoring is unavailable. The plan must rely on proxy metrics plus targeted human auditing of a sample.
23. The direct-quality monitor reports the same metric as the offline eval (primary metric from the experiment-design skill) so that an online regression maps cleanly back to the offline harness.
24. Slice the direct-quality monitor by the slices that mattered in the eval harness. A regression that affects only one slice will not move the headline number much but will hurt real users.
25. For models with very imbalanced positive classes (e.g. fraud), use a metric that survives imbalance (precision-recall curve, recall at fixed precision) and compute the metric over a window long enough to accumulate enough positives. A daily metric with 5 positives per day is too noisy.

### Stage 6 — Proxy quality and feedback signals

26. Proxy signals are the leading indicators that the team can act on before direct ground truth arrives:
    - Click-through rate on recommendations.
    - Conversion rate downstream of the model's decision.
    - Refund / chargeback rate downstream of fraud or pricing decisions.
    - Escalation-to-human rate downstream of a support chatbot.
    - Edit rate when the model's output is presented to a human as a suggestion (code completion accept-rate, draft-email edit-distance).
    - Explicit thumbs-up / thumbs-down on individual outputs.
    - "Regenerate" or "show another" requests as implicit dissatisfaction.
27. Each proxy needs a careful causal interpretation. Conversion can drop because of seasonality, not because of the model. Recommend that proxy alerts always check a counterfactual: would conversion have dropped anyway? An A/B holdout with a non-model arm (or shadow baseline) gives that counterfactual.
28. Implicit feedback signals are biased — users who give feedback are not representative. The plan must note this and avoid overreacting to small absolute changes in feedback rate without a denominator check.
29. For LLM features, the regenerate-rate, the edit-distance-on-final-message, and the disengagement (user leaves the conversation) are the three most informative proxies in many products.
30. Recommend that proxy metrics be available within minutes of the event, with end-to-end attribution to the model version that produced the output. Without model-version attribution, comparing across versions is unsound.

### Stage 7 — Safety, fairness, and policy monitors

31. Safety monitors operate on every output (or a sample if cost is high):
    - Prohibited-content rate (toxicity, sexual content, violent content, dangerous instructions) for generation models. The detector is itself a model; pin its version.
    - PII exposure rate: a regex + classifier pass that flags outputs containing PII the user did not provide.
    - Refusal correctness rate on a continuously-generated probe set of synthetic prompts.
    - Jailbreak-success rate: a small set of red-team prompts is sent on a schedule and the response is checked for policy compliance.
32. Fairness monitors compare the primary metric across protected slices (demographic, geographic, content type). Recommend computing the gap between the worst and best slice, weekly, with the same statistical-significance discipline used in the eval harness.
33. For policy-sensitive features, recommend that safety regressions trigger a higher-severity response than quality regressions. A 5% drop in helpfulness can wait until business hours; a 5% increase in policy violations cannot.
34. Recommend an "incident-class" definition for safety: any single unambiguous policy violation in the sampled stream triggers a manual review, not just a metric. Treating safety as purely statistical misses one-off severe events.
35. Privacy: monitoring must not itself leak sensitive data. Recommend hashed or redacted versions of inputs in the monitoring store; full inputs available only to authorised reviewers, with access logged.

### Stage 8 — Business KPI tie-back

36. The reason for the model is a business outcome; the monitoring plan must connect to that outcome explicitly. For each primary KPI, list:
    - Which model is intended to move it.
    - The current baseline value of the KPI.
    - The lift the model was launched to produce, with its confidence interval.
    - The frequency at which the KPI is computed and reviewed.
37. The monitoring plan does not own KPI alerting (that is a product or analytics function) but it owns the link: when a model regresses on its quality monitor, the team must be able to trace the impact to the KPI. Recommend a "model health report" that includes a KPI panel even if the KPI metric itself lives in a different system.
38. For multi-model interactions (a recommender plus a ranker plus a personalised email scheduler), recommend monitoring each model's individual contribution via a controlled A/B that periodically rotates each model off. Without this, attribution to a specific model is guesswork.
39. Long-cycle KPI confirmation (revenue per cohort after 90 days) cannot be a frontline monitor. Recommend a quarterly review where the monitoring lead and the product analyst correlate model events with KPI events and revise threshold assumptions.

### Stage 9 — Alert thresholds and escalation

40. The biggest failure mode of monitoring is alert fatigue. The plan should classify each signal into one of four destinations:
    - **Page the on-call** (high severity, real-time): safety incidents, blocker-level quality regressions on revenue-critical models. Default cap: 1-2 pages per week.
    - **Ticket the team** (medium severity, next business day): meaningful drift on important features, sustained proxy regression, slice-specific quality regression.
    - **Email or chat the team** (low severity, weekly review): minor drift on low-importance features, gradual proxy shifts, fairness-gap widening.
    - **Dashboard only** (no alert): informational signals that the on-call may look at if related signals fired.
41. Set thresholds in terms of historical noise on the signal — not absolute values, not "twice the average". Recommend two weeks to two months of baseline collection before alert thresholds are finalised; alerts set on day one without baselines will be miscalibrated.
42. Multi-condition alerts reduce noise. Recommend that "fire a page" require both a meaningful effect size AND sustained duration (e.g. metric below threshold for 30 minutes, not a single noisy point). Single-point alerts fire too often to be trusted.
43. Severity calibration: `incident_tolerance = intolerant` businesses should err on tighter thresholds and more pages; `tolerant` businesses should err on looser thresholds and more tickets. The plan tunes itself to this input.
44. Every alert must answer two questions in its body: "what changed?" and "what does on-call do next?". An alert without a runbook link is theatre. The plan must include a runbook stub per alert.
45. Recommend an alert-volume review monthly: which alerts fired, how many were actionable, which would the team disable. Without this review, the alert set ossifies and on-call burns out.

### Stage 10 — Incident response wiring and the deliverable

46. The plan must connect monitoring to action:
    - On a high-severity alert, the on-call has a runbook with diagnostic steps: check serving health, check upstream data pipeline lag, check whether a model rollout is in progress, check whether the feature store has a recent failed materialization, contact the model owner.
    - On a quality regression, the plan must define the rollback authority: who can revert to a prior model version, and how fast can they do it.
    - Recommend a "stop-the-rollout" capability tied to monitoring: if a canary deployment trips a quality monitor, the rollout halts automatically.
    - Postmortems for monitoring-triggered incidents are owned by the model team; the incident-response process learns from them and the plan is updated.
47. Connect the plan to the eval harness: a production regression should produce examples that get added to the regression test set so the same bug cannot recur silently.
48. Define ownership: each signal has a named owner (an individual or a team alias). The owner is responsible for keeping the signal calibrated and acting on its alerts.
49. Compose the deliverable as a markdown document with one section per category and a final summary table of all signals with their thresholds, owners, and destinations. Emit the JSON variant for downstream tooling.
50. End with a "first 30 days" rollout plan: which 3-5 signals to instrument first (the highest-cost failure modes), how to collect baselines, when to enable paging vs ticketing, and the date of the first calibration review.

## Outputs

The skill returns two artifacts:

1. `monitoring_plan` (markdown) — the section-by-section plan.
2. `signals_json` (JSON) — a structured list of signals as described under `outputs`.

## Examples

**Input (placeholder):**

`model_description`: "Churn-prediction model scored daily for 5M B2B accounts. Output is a probability used to prioritise customer-success outreach."

`business_kpis`: "Quarterly logo churn rate, and the conversion rate from outreach to a retention save."

`ground_truth_lag`: "months" (true churn is observed 30-90 days after the prediction).

`data_sensitivity`: "PII and revenue data."

`incident_tolerance`: "normal".

`existing_observability`: "Datadog for infra metrics; daily Looker dashboard reviewed by the analytics team."

**Plan (abbreviated):**

- Highest-cost failure mode: missing accounts that churn (false negatives), since outreach capacity is the binding constraint.
- Input drift: PSI on the top-15 features daily; multivariate PCA-reconstruction error as a single guardrail.
- Output drift: distribution of predicted churn probability, weekly. Alert on a sustained right-tail shift.
- Direct quality: monthly precision-at-top-decile (the actionable population) versus the prior month. Quarterly review of recall on actually-churned accounts.
- Proxy quality: outreach-conversion-rate per decile of model score, weekly. A flat or inverted curve means the score is no longer ordering correctly.
- Safety / fairness: monitor the gap in precision across customer segments quarterly.
- Business KPI tie-back: quarterly retention-save attribution dashboard linked from the model health report.
- Alerting: ticket the team for any feature with PSI > 0.25 sustained for 3 days; ticket the team for prediction-distribution shift > 2 sigma sustained for a week. No paging on this model — it is not real-time.
- 30-day rollout: instrument PSI + output drift in week 1, baseline for two weeks, enable ticketing in week 4, schedule monthly precision review.

**Output excerpt:** the markdown plan and a `signals_json` array enumerating each signal with its computation, threshold, severity, destination, and owner.

## Limitations

- The skill writes the plan, not the dashboards. The user instruments the chosen tools.
- Threshold suggestions are heuristics calibrated against typical historical noise; the user must collect baseline data and refine.
- Causal attribution from proxy metrics to model behaviour is hard; the plan flags this and recommends counterfactual A/B holdouts but cannot substitute for them.
- For long-cycle KPIs (revenue per cohort over months), the plan tells the team what to track but cannot accelerate the cycle time.
- LLM-specific monitors (judge agreement, hallucination rate) are summarised here; the deeper design lives in the eval-harness skill, which this plan should be paired with.
- The skill does not deeply specialise to regulated domains (medical, financial); domain experts must extend the safety section.
- Multivariate drift detection is recommended but the choice of method (PCA, autoencoder, density estimation) is left to the user; the skill is method-agnostic.

## Sources reviewed

- https://github.com/evidentlyai/evidently
- https://github.com/NannyML/nannyml
- https://github.com/mlflow/mlflow
- https://github.com/langfuse/langfuse
- https://github.com/traceloop/openllmetry
- https://github.com/zenml-io/zenml
- https://github.com/truera/trulens
