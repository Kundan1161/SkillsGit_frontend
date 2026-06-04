---
id: skillsgit-curated/embedding-model-selector
version: 1.0.0
name: Embedding Model Selector
description: Pick the right embedding model for a retrieval workload — dimension, family, domain fit, latency-versus-quality trade-off, fine-tune-versus-zero-shot decision, evaluation-set construction, and drift watch.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:vector-database-ops, embeddings, retrieval-eval, mteb, fine-tuning, model-selection, embedding-drift, semantic-search]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: []
  tools_optional: [web_search, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - which embedding model
  - choose embedding model
  - embedding dimension
  - mteb benchmark
  - fine tune embeddings
  - domain embeddings
  - multilingual embeddings
  - embedding drift
  - evaluation set for embeddings
  - embedding latency vs quality
  - sentence transformer model
  - retrieval eval set
example_invocations:
  - "Pick an embedding model for legal-contract retrieval — we need recall, multilingual coverage, and on-prem CPU inference."
  - "We are deciding between a 384-dim and a 1024-dim embedding. What evaluation will resolve it?"
  - "Build an evaluation set so we can compare three candidate embedding models on our own data."
inputs:
  - name: use_case
    type: text
    required: true
    description: One paragraph describing what is being retrieved, who is querying, and the downstream consumer (a reranker, an LLM, a human, a recommender).
  - name: corpus_description
    type: text
    required: false
    description: Document type, average length, language mix, domain (legal, biomedical, code, e-commerce, general web), and any structural features.
  - name: query_description
    type: text
    required: false
    description: Query style — natural-language questions, short keywords, code snippets, structured filters, conversational turns.
  - name: latency_budget_ms
    type: text
    required: false
    description: Acceptable embedding-time latency for queries, batch budget for corpus encoding.
  - name: deployment_constraints
    type: text
    required: false
    description: Self-hosted versus hosted, CPU versus GPU, on-prem versus cloud, data-residency restrictions, allowed model licenses.
  - name: existing_eval_set
    type: text
    required: false
    description: Whether the user already has labelled query-document pairs to evaluate on. If not, the skill builds one.
outputs:
  - name: selection_report
    type: markdown
    description: Structured report covering shortlist, evaluation plan, recommended model, fallback, and drift watch.
  - name: selection_json
    type: json
    description: Machine-readable selection with `shortlist`, `eval_plan`, `recommendation`, `fallback`, `drift_plan`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Embedding Model Selector

## When to use

Use this skill when someone has to pick an embedding model for a retrieval or similarity task and the wrong choice would be expensive to undo. The skill produces a written report covering a shortlist, a way to measure them on the user's own data, a recommendation with justification, a fallback if the recommendation underperforms in production, and a watch plan for model drift over time.

The skill applies to text, multilingual text, code, and most other embedding modalities where pre-trained candidate models exist. It applies whether the user plans to self-host an open model or call a hosted embedding API. The skill assumes the surrounding vector-database design is being handled elsewhere — the recommendation must be feasible inside the index family chosen by the architecture skill, but this skill does not redo that decision.

The skill is not the right tool for "should we use embeddings at all?" — that question belongs upstream. Nor is it the right tool for running benchmarks; it tells the user which benchmarks to run and how to interpret them. It is also not a substitute for training an embedding model from scratch; it covers selection, with fine-tuning as a refinement step.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `use_case` | yes | Defines the retrieval objective and consumer. |
| `corpus_description` | no | Sets the domain-fit filter on candidate models. |
| `query_description` | no | Sets asymmetric versus symmetric model preference. |
| `latency_budget_ms` | no | Filters by inference cost. |
| `deployment_constraints` | no | Filters by license and infrastructure. |
| `existing_eval_set` | no | Decides whether the skill must construct an eval set. |

## How to apply

The skill walks a twelve-stage pipeline. The output is a report, not a model — selection is only as good as the evaluation it survives.

### Stage 1 — Frame the retrieval objective

1. Rewrite the `use_case` as a sentence in the form "Given a <query type>, return the <k> most relevant <document type> from a corpus of <size> in domain <domain>, judged by <relevance criterion>." If any slot is empty, ask before continuing.
2. Identify whether the task is **symmetric** (query and document are the same kind of text, e.g. duplicate detection) or **asymmetric** (query is short and document is long, e.g. question-to-passage). Many models are trained for one and underperform on the other. The recommendation depends on this.
3. Identify the downstream consumer of the retrieved set. If the consumer is a cross-encoder reranker, the embedding model needs to recall broadly; final precision is the reranker's job. If the consumer is a human or a generative model with no rerank, the embedding model is on the hook for both recall and precision.
4. Identify the "good enough" recall target at the top-k the consumer actually reads. A reranker with k=100 needs recall@100; a chat assistant that reads only the top 3 needs recall@3. The target drives the discriminating power the eval must measure.
5. Identify the cost model. The embedding model is paid at corpus-encode time (one-shot, amortised over many queries) and at query-encode time (per-query, latency-critical). Cheap query encoding is more valuable than cheap corpus encoding for high-QPS workloads.

### Stage 2 — Profile the corpus

6. Read the `corpus_description` and record: average document length in tokens, length distribution (mean, p95, max), language mix, dominant domain vocabulary (legal, medical, code, finance, general), presence of structured fields (titles, headings, code blocks), and corpus size.
7. Flag the **truncation risk.** If average document length exceeds the candidate model's context window (typical for older sentence-transformer models at 512 tokens), the document must be chunked before encoding. The chunking strategy affects retrieval quality more than the model choice for long-document workloads.
8. Flag the **domain shift risk.** If the corpus is heavily domain-specific (case law, clinical notes, source code, chemical structures) and the candidate is general-purpose, expect a meaningful recall hit versus a domain-adapted model. Earmark fine-tuning as a candidate path.
9. Flag the **multilinguality requirement.** If the corpus or queries span more than one language, the candidate must be a multilingual model or a translation-pivoting design. Monolingual models on multilingual corpora collapse silently.
10. Flag the **negation and instruction sensitivity.** General-purpose embeddings often fail to distinguish "A causes B" from "A does not cause B". If the use case depends on logical structure inside the text, evaluation must include adversarial pairs.

### Stage 3 — Build a candidate shortlist

11. Generate a shortlist of three to six candidate models that survive the filters from Stages 1 and 2. The shortlist must include at least one small open model (well under 200M parameters), one large open model (a few hundred million to a billion parameters), and one hosted API model. Including a hosted option even when self-hosting is the plan provides a quality ceiling reference.
12. Apply the **license filter.** Reject candidates whose license is incompatible with the deployment (e.g. non-commercial-only licenses for commercial deployments, encumbered weights for regulated environments). State the license of each surviving candidate.
13. Apply the **dimension filter.** If the architecture has pinned a dimension budget (memory and latency in the vector DB scale with dimensionality), drop candidates outside the budget or add a dimensionality-reduction step (Matryoshka representation learning models, PCA, or random projection) to the shortlist with the relevant caveat.
14. Apply the **context filter.** Drop candidates whose maximum sequence length cannot accommodate the corpus's typical chunk size after planned chunking.
15. Apply the **inference-throughput filter.** For each candidate, estimate tokens-per-second on the target hardware. A model that needs a GPU when only CPUs are available is rejected, regardless of quality.
16. Apply the **community signal filter.** Prefer candidates with active maintenance, recent releases, broad downstream use, and published reproducible benchmark numbers. A model that is unmaintained today is unmaintained forever.

### Stage 4 — Read public benchmarks with skepticism

17. Consult published retrieval benchmark leaderboards as a starting filter — they rank general performance across many tasks and languages. Use them to confirm that no candidate is wildly off the pace, not to pick the winner.
18. **Public benchmark trap.** A model that wins on average across dozens of public datasets often loses on a specific user's data. Public benchmarks are reference points, not selection criteria. The selection must come from the user's own evaluation set in Stage 6.
19. **Domain-specific benchmarks.** If a benchmark exists in the user's domain (legal, biomedical, code, financial), weight it heavily but still expect the user's data to disagree by a few points.
20. **Asymmetric retrieval benchmarks** (question-to-passage tasks like a public open-domain QA evaluation) generalise better to chat-style retrieval than symmetric similarity benchmarks. Match the benchmark family to the task family.

### Stage 5 — Decide between zero-shot and fine-tuned

21. **Zero-shot first.** Default to zero-shot with the best general or domain-adapted candidate. Fine-tuning costs labelling, training, evaluation, and lifetime ownership of a custom model. Many workloads are saturated by a strong zero-shot baseline.
22. **Fine-tune triggers.** Recommend fine-tuning only when (a) the domain vocabulary is sufficiently far from the candidate's training distribution that zero-shot recall is below target, (b) the user has or can produce at least a few thousand labelled query-document pairs, and (c) the user is prepared to own the training pipeline forever, including re-training when the base model is upgraded.
23. **Fine-tune strategy.** When fine-tuning, prefer contrastive learning with mined hard negatives on the user's own corpus over generic margin objectives. The hardness of the negatives drives the quality more than the loss function.
24. **Adapter approach.** Before full fine-tuning, evaluate parameter-efficient adapters (LoRA-style) on top of the base model. Adapters are cheaper, easier to swap when the base is upgraded, and often capture 70-90% of the full fine-tune gain.
25. **Continual training risk.** A fine-tuned embedding model is married to its training distribution. If the corpus or query style shifts (new product category, new jargon, new language), the fine-tune may underperform a fresh zero-shot model. The drift plan in Stage 11 must cover this.

### Stage 6 — Construct the user's own evaluation set

26. If `existing_eval_set` is present, validate it: at least a few hundred queries, each with at least one judged-relevant document, ideally with graded relevance labels. Flag any quality issues (auto-generated queries that mirror the document, label-leakage, single-annotator labels with no inter-annotator agreement check).
27. If absent, build one. The skill describes a four-source construction plan: (a) historical query logs from the production system if any exist, (b) synthetic queries generated by a strong LLM from sampled documents, (c) judge-validated hard negatives mined by an existing baseline encoder, (d) a small human-annotated gold set for the final calibration.
28. Set the eval set size against the discriminating power needed. To distinguish two models that differ by one point of recall, plan at least a few hundred queries; for half-point differences, plan a few thousand.
29. Include three categories of queries: typical (real user phrasings), adversarial (paraphrases, negations, code-mixed language, typos), and edge (very short, very long, ambiguous). A model that wins on typical and loses on adversarial is fragile.
30. Hold out a separate test set used exactly once. The development eval set may be looked at and tuned against; the test set decides the recommendation.
31. Lock the relevance criterion in writing. "Relevant" must mean the same thing to every annotator: pin a rubric, agree on graded versus binary, sample a fraction for inter-annotator agreement.

### Stage 7 — Run the bake-off

32. Encode the corpus with each shortlisted model. Record corpus-encode wall-clock and cost per million tokens.
33. For each candidate, run the eval queries and measure: recall@k at the target k, recall@1 (precision proxy), nDCG@10, mean reciprocal rank, and a per-query latency distribution at the target batch size.
34. Run a brute-force flat baseline for each candidate at small scale so that the index's effect on recall is separated from the model's. The reported numbers in the bake-off should be the brute-force ceiling, not the production index's recall.
35. Run **slice metrics.** Report each metric on the slices identified in Stage 2 — per language, per document type, per query category. Headline averages hide slice failures.
36. Pair every comparison with a confidence interval (bootstrap over queries) and a paired significance test. A 0.5-point lead with overlapping confidence intervals is not a winner.
37. Report **cost per million queries** and **cost per million corpus tokens** alongside the quality numbers. A model that wins by half a recall point at 5x cost may not be the right choice.

### Stage 8 — Recommend the model

38. The recommended model is the one that meets the recall target at the lowest cost-per-million-queries on the held-out test set, with no slice regressing below a stated floor, and with a license and footprint compatible with the deployment.
39. State a **fallback** — a smaller, cheaper model that would be used if cost or latency budgets tightened. The fallback should have run the same evaluation; the report quantifies the quality loss of switching.
40. State a **stretch** — a more expensive model that would be used if quality budgets loosened. The stretch quantifies the headroom available if the user invests more.
41. Provide a **pinning rule.** The recommendation names a specific model snapshot or version. Re-running the same selection a week later may produce different scores if the hosted API has changed under the hood; the recommendation includes how to detect that.
42. Where the recommendation depends on fine-tuning, the report includes the labelled-data requirement, the expected training compute, and a "do not fine-tune yet" branch for users who do not meet the data requirement.

### Stage 9 — Plan the dimensionality decision

43. Calculate the per-vector storage cost at the chosen dimension. For a corpus of millions of vectors, the difference between 384, 768, and 1536 dimensions translates into very different infrastructure budgets.
44. If the model supports **Matryoshka representations** (truncatable embeddings), evaluate the truncated variants in the same bake-off. Often a model truncated to 256 or 384 dimensions still meets recall while costing a fraction of the full-dimension storage.
45. **Quantisation interacts with the embedding choice.** Some models survive int8 or binary quantisation almost losslessly; others lose several recall points. Run the quantised variant in the bake-off, not just the full-precision version.
46. State the chosen dimension and quantisation in the recommendation as an inseparable pair. Changing one later changes the other's verdict.

### Stage 10 — Plan query-encoding latency and batching

47. Query encoding latency is part of the user-facing budget. For online retrieval, the budget is typically a few milliseconds — this often eliminates the largest open models on CPU.
48. **Batch versus single-query latency** differs by an order of magnitude. Decide whether the production path will batch queries (for short tail QPS, hard) or encode one at a time (the common case). Tune accordingly.
49. For self-hosted models, plan **warmup** and **model caching.** Cold-start latency is irrelevant if the model is loaded once at boot; relevant if the model is loaded per request.
50. For hosted APIs, plan **resilience.** The selection includes a degraded-mode path: what does the system do if the API is unavailable? Either a local fallback model or a graceful degradation to keyword search.

### Stage 11 — Plan for drift

51. **Embedding-space drift** has three causes: the corpus distribution shifts (new vocabulary, new domains), the query distribution shifts, or the model itself changes (hosted API upgraded, base model fine-tuned). Each requires a different mitigation.
52. **Re-evaluation cadence.** Re-run the held-out evaluation monthly for hosted-API models, quarterly for self-hosted, and on any model upgrade. A drop greater than the noise floor of the evaluation triggers a deeper investigation.
53. **Re-embedding policy.** If the model is upgraded with a different output space (different dimension, different geometry), the entire corpus must be re-embedded. Treat this as a planned migration; never serve queries encoded with version A against documents encoded with version B.
54. **Canary corpus.** Maintain a small, frozen "canary" set of query-document pairs whose relevance never changes. Drift on the canary set is unambiguously model-side, not corpus-side.
55. **Production sampling.** Sample a small fraction of live queries with relevance feedback (click-through, downstream LLM judge, human label) into a continuous evaluation stream. Recompute headline metrics weekly.

### Stage 12 — Compose the deliverable

56. Open with a one-paragraph summary: chosen model, the runner-up, the gap, the cost of the gap, the most important risk.
57. Render the report with sections per stage: framing, corpus profile, shortlist, public benchmarks consulted, zero-shot versus fine-tune decision, evaluation set, bake-off results, recommendation, dimension and quantisation, latency, drift plan.
58. Emit `selection_json` with the structured fields enumerated under `outputs`.
59. End with a "what would change this recommendation" section: which input would flip the decision, which corpus shift would invalidate the bake-off, which new benchmark release should trigger a re-evaluation.

## Outputs

The skill returns two artifacts:

1. `selection_report` (markdown) — the readable report organised by stage.
2. `selection_json` (JSON) — structured selection with the keys listed under `outputs`.

## Examples

**Input (placeholder):**

`use_case`: "We are building a customer-support assistant that retrieves the top three help-centre articles for an English-language query and feeds them to an LLM that writes the answer."

`corpus_description`: "About 60 thousand articles, average length 800 tokens, English only, general SaaS support domain."

`query_description`: "Natural-language user questions, often two or three sentences long, sometimes with product jargon."

`latency_budget_ms`: "Embedding the user query must finish under 30 ms p95 on a CPU-only fleet."

`deployment_constraints`: "Self-hosted, no GPUs, permissive open-source license required."

**Report (abbreviated):**

- Framing: asymmetric, top-3 consumed by an LLM with no rerank; recall@3 is the headline metric.
- Shortlist: one small open model around 100M parameters, two medium open models around 400M parameters, one hosted API as a quality ceiling reference.
- Evaluation set: 500 historical real-user queries, augmented with 1500 LLM-synthesised paraphrases over sampled articles, judged in part by an LLM-judge against article ground-truth pairings, with a 200-query human-graded test set held out.
- Bake-off: medium open model A leads recall@3 by 1.2 points over the small model and trails the hosted API by 0.6 points. Latency on CPU is 22 ms p95.
- Recommendation: medium open model A with int8 quantisation. Fallback: small model if QPS triples and latency budget tightens. No fine-tune required at this scale; revisit if corpus crosses 500k articles.
- Drift plan: monthly canary re-evaluation; re-run full bake-off if the small or medium model publishes a new release tagged as a quality update.

## Limitations

- The skill is not a benchmark runner; it specifies the benchmarks and interprets results.
- For very low-resource languages, public benchmark coverage is thin and the recommendation will lean more heavily on the user's own evaluation set.
- The skill does not cover image, audio, or arbitrary multimodal embeddings beyond noting that the framework transfers; specific modality benchmarks differ.
- Fine-tuning advice is high-level; once the user commits to fine-tuning, the ML-experiment-design skill should pick up the training-run-level decisions.
- The skill does not pick a reranker; assume reranker selection is a downstream decision once recall is solved.
- Hosted-API recommendations age quickly as providers change defaults; the report should be re-validated whenever the provider announces a model update.
- For corpora under a few thousand documents, retrieval quality is dominated by chunking and prompt design rather than embedding choice; the skill should detect this and recommend the simplest model with the lowest latency.

## Sources reviewed

- https://github.com/embeddings-benchmark/mteb
- https://github.com/huggingface/sentence-transformers
- https://github.com/qdrant/qdrant
- https://github.com/milvus-io/milvus
- https://github.com/facebookresearch/faiss
- https://github.com/chroma-core/chroma
- https://github.com/lancedb/lancedb
