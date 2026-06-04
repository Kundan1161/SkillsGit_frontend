# Synthesis Report — Engineering / ML & AI Engineering & Deployment

**Date:** 2026-05-14
**Author:** wave-2 methodology-synthesis agent
**Area:** engineering — MLOps, model evals, model serving, feature stores, model monitoring

## Skills produced

1. `ml-experiment-design.skills.md` — ML Experiment Designer
2. `llm-eval-harness-designer.skills.md` — LLM Eval Harness Designer
3. `model-serving-reviewer.skills.md` — Model Serving Setup Reviewer
4. `feature-store-architect.skills.md` — Feature Store Architect (optional, produced)
5. `model-monitoring-planner.skills.md` — Model Monitoring Planner (optional, produced)

All five skills exceed 300 lines of original instructional prose, cite at least six permissively-licensed sources each, and use `license_type: free` with no pricing. The first tag on each is `niche:ml-engineering` and the category is `engineering`. No overlap was found with existing skills in the synth folder — there was no merge to perform; all five files are new additions.

## Sources reviewed

All sources verified live for license, ≥100 stars, and last activity within the past 18 months as of May 2026. URLs only — no quoted content from any source appears in the produced skills.

### Accepted (used across the five skills)

| Repo | License | Stars | Last release | Used by |
| --- | --- | --- | --- | --- |
| `mlflow/mlflow` | Apache-2.0 | 25.9k | 2026-05 | experiment, serving, feature-store, monitoring |
| `EleutherAI/lm-evaluation-harness` | MIT | 12.6k | 2026-05 | experiment, eval-harness |
| `openai/evals` | MIT | 18.5k | 2026-04 commit | experiment, eval-harness |
| `confident-ai/deepeval` | Apache-2.0 | 15.4k | 2026-05 | experiment, eval-harness |
| `explodinggradients/ragas` | Apache-2.0 | 13.9k | 2026-01 | experiment, eval-harness |
| `truera/trulens` | MIT | 3.3k | 2026-05 | eval-harness, monitoring |
| `langfuse/langfuse` | MIT (core; `ee/` excluded) | 27.2k | 2026-05 | eval-harness, serving, monitoring |
| `traceloop/openllmetry` | Apache-2.0 | 7.1k | 2026-04 | eval-harness, serving, monitoring |
| `vllm-project/vllm` | Apache-2.0 | 80k | 2026-05 | serving |
| `bentoml/BentoML` | Apache-2.0 | 8.6k | 2026-05 | serving |
| `kserve/kserve` | Apache-2.0 | 5.5k | 2026-04 | serving |
| `feast-dev/feast` | Apache-2.0 | 7.0k | 2026-05 | feature-store |
| `feathr-ai/feathr` | Apache-2.0 | 1.9k | recent | feature-store |
| `zenml-io/zenml` | Apache-2.0 | 5.4k | 2026-05 | experiment, feature-store, monitoring |
| `evidentlyai/evidently` | Apache-2.0 | 7.5k | 2026-03 | experiment, serving, feature-store, monitoring |
| `NannyML/nannyml` | Apache-2.0 | 2.1k | 2025-07 | feature-store, monitoring |

Per skill, the `## Sources reviewed` block cites exactly the 6-7 most relevant of these.

### Rejected (and why)

| Repo | Reason |
| --- | --- |
| `Arize-ai/phoenix` | Elastic License 2.0 — not in allowed list. |
| `SeldonIO/alibi-detect` | Business Source License 1.1 — not yet open source per its own terms; converts to Apache after a 4-year delay per version. |
| `whylabs/whylogs` | Last release December 2024 — exceeds 18-month freshness threshold by May 2026. |
| `prometheus-eval/prometheus-eval` | Last release September 2024 — exceeds 18-month freshness threshold. |
| `langchain-ai/openevals` | Cannot confirm star count above 100 from search; not used out of caution. |
| `bentoml/OpenLLM` | Reviewed but no additional methodology beyond core BentoML; not separately cited. |
| `Lightning-AI/lit-gpt` and other training-side repos | Out of scope — these skills are deployment-side, not training-side. |
| `huggingface/transformers` | Used as a model source by buyers, not a methodology source for these skills. |

## Methodology patterns identified across sources

These patterns recurred across multiple permissively-licensed sources and shaped the structure of the produced skills. None of the prose is borrowed — the abstractions are.

1. **Tracked-run lineage as the foundational primitive.** MLflow's run / experiment / artifact model, ZenML's pipeline-step lineage, Langfuse's trace-and-observation hierarchy, and OpenLLMetry's trace spans all converge on the same shape: an immutable record per execution with config, code-commit, inputs, outputs, and metadata, queryable across runs. This shapes the reproducibility section of the experiment-design skill and the observability sections of the serving and monitoring skills.
2. **Two-store feature pattern.** Feast and Feathr both expose a clear separation between an offline historical store (warehouse / lake) and an online point-lookup store, with a materialization process bridging them. This is the spine of the feature-store-architect skill.
3. **Point-in-time correctness as a first-class invariant.** Feast's PIT-join semantics and the broader warehouse pattern of as-of joins converge on the same correctness invariant: training data must not contain values that postdate the row's event. The skill makes this an explicit stage with a unit-test recommendation.
4. **Continuous batching is the LLM-serving default.** vLLM popularised continuous (in-flight) batching for autoregressive LLM serving; BentoML and KServe both surface it as a recommended mode. The model-serving-reviewer treats static batching for an autoregressive LLM as a major finding.
5. **LLM-as-judge with a calibration set.** DeepEval, Ragas, TruLens, and the OpenAI Evals templates all centre on a judge that is itself evaluated against human grades on a calibration set. The eval-harness skill makes this a dedicated stage with a kappa target.
6. **Pairwise judging beats pointwise on consistency.** Multiple eval frameworks document the bias issues (position, verbosity, style) and recommend pairwise comparison with position-swapped runs and a tie option. The eval-harness skill encodes these as required mitigations.
7. **Distribution-drift detection split into univariate and multivariate.** Evidently and NannyML both expose univariate per-feature tests (KS, JSD, PSI) alongside multivariate reconstruction-error signals. The monitoring skill carries both.
8. **Effect size, not p-value, as the threshold metric.** Multiple drift and monitoring tools (Evidently, NannyML) caution against using statistical significance directly on production-scale data. The monitoring and experiment-design skills both encode this.
9. **Alert categorisation into page / ticket / email / dashboard.** Recurring across observability tools (Langfuse, OpenLLMetry, Evidently dashboards) and reflecting standard SRE practice; the monitoring skill uses these as explicit alert destinations.
10. **Layered eval architecture: smoke → regression → frontier.** Multiple LLM-eval frameworks recommend a fast small set for CI plus a larger nightly set plus a periodic adversarial set. The eval-harness skill encodes the three-tier pattern directly.
11. **Canary rollouts wired to evals.** BentoML, KServe, and several MLOps platforms expose canary deployments; the eval-harness and serving skills both connect canary stages to eval gating.
12. **Feature ownership and catalog as governance primitives.** Feast and Feathr both expose feature definitions as code with metadata; the feature-store-architect skill encodes ownership and catalog discovery as required components.
13. **Reproducibility = pin everything.** MLflow's model registry, ZenML's component versioning, and the broader practice across all tracked-experiment frameworks converge on the same advice: pin the dataset hash, code commit, library versions, and even the judge model version. The experiment-design skill makes this a checklist.

## Originality discipline

- All prose in the five skill files was authored from scratch. No verbatim text was copied or paraphrased from any source.
- For each source the agent extracted concepts (run-lineage shape, PIT-join semantics, batching modes, judge calibration practice) and re-expressed them in the agent's own framing and vocabulary.
- No trademarked methodology names were used. Tool names appear only in the `## Sources reviewed` URLs.
- Common-vocabulary terms (PSI, KS test, ROC-AUC, recall@k, KV cache, p95, A/B, canary) are field-standard and predate the cited repos.
- The skills do not claim affiliation with any cited project.

## Decisions made under ambiguity

- **Phoenix and alibi-detect.** Both have public adoption but neither carries a permissive license — Phoenix is Elastic License 2.0, alibi-detect is Business Source License 1.1 with a 4-year delay before Apache. The task is explicit on permissive-only, and both were excluded.
- **whylogs and prometheus-eval freshness.** Whylogs last release December 2024 and prometheus-eval September 2024 both exceed the 18-month freshness threshold by May 2026. Both excluded.
- **Triton Inference Server** is a relevant production reality but the upstream repo is BSD-3-Clause and active; it would be acceptable. I did not add it as a citation because the four serving citations already cover the relevant batching, KV cache, and continuous-batching patterns; adding a fifth would be redundant.
- **Pricing.** Task spec said `license_type: free` with no pricing. The frontmatter retains a `pricing.currency` and `pricing.support_included` block (in line with the support-* and other recent free skills in the folder) but no `*_cents` fields, conforming to validation rules for the free license type.

## Confidence assessment

- **ML Experiment Designer — High.** The pattern of hypothesis / splits / baselines / metrics / ablations / significance / productionization gate is well-trodden across the MLflow, ZenML, OpenAI Evals, and LM-eval-harness ecosystems. The skill encodes a thorough version of it. The riskiest parts are LLM-specific extensions (LLM judge calibration) which the eval-harness skill covers in more depth.
- **LLM Eval Harness Designer — High.** Strong source diversity (5 dedicated LLM-eval frameworks plus 2 LLM observability tools). The methodology aligns with the documented best practices across all of them. The judge-calibration kappa targets and the bias mitigations are the parts most likely to need post-publication tuning.
- **Model Serving Setup Reviewer — High.** The serving sources (vLLM, BentoML, KServe, MLflow, langfuse, openllmetry, evidently) cover continuous batching, autoscaling, observability, and canary patterns. The hardware sizing math is approximate by design — buyers must validate with a load test, as the skill says.
- **Feature Store Architect — Medium-High.** Feast and Feathr provide the canonical two-store / PIT-join shape. The skill encodes their architectural pattern accurately. Less confident about migration-phasing duration estimates — those depend heavily on team and existing data quality.
- **Model Monitoring Planner — High.** Evidently and NannyML provide explicit, well-documented drift methodologies, and the LLM observability tools (Langfuse, OpenLLMetry, TruLens) cover the LLM-side signals. The alert-fatigue thresholds and the page/ticket/email/dashboard partition are the parts most likely to need tuning per buyer.

## Open follow-ups (not blocking)

- The serving skill's hardware-sizing math is approximate. A v1.1 could split per-framework variants (vLLM-specific, Triton-specific) once buyer feedback indicates which platform users want depth on.
- The monitoring skill is method-agnostic on multivariate drift; a future v1.1 could include explicit method recommendations once the team chooses an implementation library.
- The eval-harness skill mentions human-review SLA but does not deeply spec the review-UI design; a companion skill could specifically target "build the human review surface for an LLM eval".
- The experiment-design skill does not deeply cover RLHF or DPO-style preference-data experiments; if the buyer base trends that way, a companion preference-experiment skill is the natural extension.
- The feature-store skill does not deeply cover vector / embedding feature pipelines; a companion skill for vector-feature governance could be useful as embedding-driven features proliferate.
