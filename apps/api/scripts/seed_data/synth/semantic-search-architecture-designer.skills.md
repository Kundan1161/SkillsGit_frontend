---
id: skillsgit-curated/semantic-search-architecture-designer
version: 1.0.0
name: Semantic Search Architecture Designer
description: Design a hybrid semantic search system — BM25 plus vectors plus cross-encoder rerank, hard negatives, embedding model selection, index sharding, freshness, and multi-tenant isolation.
authors:
  - name: Wave-5 Synth
    handle: wave5-data
    role: author
category: data
tags:
  - niche:knowledge-graph-architecture
  - semantic-search
  - hybrid-retrieval
  - embeddings
  - cross-encoder
  - reranking
  - hard-negatives
  - multi-tenant
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: []
  tools_optional: [web_search, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - semantic search design
  - hybrid search architecture
  - bm25 vector hybrid
  - cross encoder rerank
  - embedding model selection
  - hard negatives
  - vector index sharding
  - search freshness
  - multi tenant search
  - retrieval architecture
  - vector store design
  - search system architecture
example_invocations:
  - "Design a hybrid semantic search system for our product catalog — BM25, vectors, and a reranker."
  - "Pick an embedding model and an index strategy for a multi-tenant SaaS knowledge base search."
  - "Plan the freshness and re-indexing story for a search system over a content corpus that updates hourly."
  - "Design hard-negative mining for our domain-specific search system."
inputs:
  - name: corpus
    type: text
    required: true
    description: What is being searched — domain, document count, document shape, language mix, update rate.
  - name: query_shape
    type: text
    required: false
    description: How users phrase queries — keywords, natural-language questions, structured filters, mixed.
  - name: success_metric
    type: text
    required: false
    description: What "good" looks like — nDCG@10, success@1, click-through, downstream task quality, business KPI.
  - name: latency_budget
    type: choice
    required: false
    description: Acceptable end-to-end query latency.
    choices: [sub_100ms, sub_500ms, sub_2s, batch]
  - name: tenancy
    type: choice
    required: false
    description: Tenancy model.
    choices: [single_tenant, multi_tenant_shared, multi_tenant_isolated, hierarchical]
  - name: stack_constraints
    type: text
    required: false
    description: Constraints on embedding provider, vector store, runtime, cost ceilings, data residency.
outputs:
  - name: search_architecture
    type: markdown
    description: The end-to-end design — indexing, hybrid retrieval, reranking, embedding selection, freshness, sharding, tenancy, and evaluation.
  - name: search_summary
    type: json
    description: Structured summary with `indexing`, `retrieval`, `reranking`, `embeddings`, `freshness`, `sharding`, `tenancy`, and `eval`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Semantic Search Architecture Designer

## When to use

Use this skill when a team is designing or rebuilding a search system that has to do more than keyword matching but is not a chat product. Semantic search sits at the intersection of classical information retrieval and modern embedding-based retrieval. Done well, it is a quiet, fast, accurate component that powers product features other people get credit for. Done poorly, it is the source of "search is bad" complaints that no amount of UI polish can fix.

This skill produces the architecture document — indexing pipeline, hybrid retrieval strategy, reranker design, embedding-model selection rubric, freshness handling, index sharding, tenancy model, and evaluation methodology. It does not pick a specific vector database or hosted embedding service; those are constraints the design names. It is complementary to the rag-product-loop-designer and graphrag-pipeline-architect skills in this library — semantic search is the retrieval layer those skills build on top of, and a generative answer is one consumer of a search system but not the only one.

The skill applies to product catalog search, enterprise document search, code search, customer-support knowledge base search, legal and regulatory search, scientific literature search, and the retrieval substrate of an AI agent. It applies to small corpora (tens of thousands of documents) where the architecture decisions are about quality, and to large corpora (hundreds of millions of documents) where the decisions are about quality and scale jointly.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `corpus` | yes | Anchors the indexing and embedding decisions. |
| `query_shape` | no | Drives the hybrid mix and reranker design. |
| `success_metric` | no | Sets the eval target. |
| `latency_budget` | no | Constrains the retrieval and rerank depth. |
| `tenancy` | no | Decides the isolation and sharding strategy. |
| `stack_constraints` | no | Bounds the implementation options. |

## How to apply

The design walks through twelve stages. Output is an architecture document; engineering implements against it.

### Stage 1 — Anchor on the search task

1. The most common architecture mistake is designing a search system without naming the task it serves. Search is a means; the task is the end.
2. From `corpus` and `query_shape`, write a paragraph describing the user, the intent, the typical query, the typical good result, and what the user does with the result. "A support agent finds the article that lets them answer a customer question in the next thirty seconds" is a task. "Search the help centre" is not.
3. Decide what "relevance" means for this task. For e-commerce, relevance is buying intent translated to product matches. For internal docs, relevance is the document that answers the question. For code search, relevance is the function the user actually wants to call. The definition drives the eval design downstream.
4. Decide what is *out of scope* for this search system. Trying to be a question-answering system, a recommendation engine, and a fuzzy-match deduplication tool in the same component is the road to a bloated architecture that does none of those things well. Pin scope.

### Stage 2 — Survey the corpus

5. The corpus shapes every downstream decision. Survey it before designing.
6. **Document count and growth.** A million documents today growing at ten thousand a day is a different system from a million documents stable for years. Pin both.
7. **Document shape.** Average and ninety-fifth-percentile length. Structural content — titles, headings, body, code, tables. Multilingual mix. Each shape has implications for chunking, embedding, and reranking.
8. **Update characteristics.** What fraction of documents change per day. Whether changes are content edits or status changes (which affect retrieval but not text). Whether deletions and unpublishings happen and on what cadence.
9. **Metadata.** What structured fields accompany each document — author, timestamp, tag, region, permissions. Metadata is the first lever for relevance and the foundation of filtering and faceted search.
10. **Quality bar.** Are there documents that should be excluded from indexing — drafts, deprecated, low-quality, off-topic? A noisy corpus produces noisy results regardless of how good the retriever is.

### Stage 3 — Pick the hybrid mix

11. Pure-dense vector retrieval and pure-sparse keyword retrieval each have well-known weaknesses; hybrid retrieval, done right, outperforms both. Pin the hybrid design.
12. **BM25 (or equivalent sparse).** Excellent for exact-match queries, rare-token queries, identifier lookups, and short queries that share vocabulary with the corpus. Cheap and well-understood. Every serious semantic-search architecture includes a sparse component.
13. **Dense vector retrieval.** Excellent for paraphrased queries, semantic similarity, multilingual matching when the model supports it, and natural-language queries that do not share vocabulary with the corpus. More expensive than sparse and requires embedding-model selection.
14. **Fusion strategy.** Two main options. *Reciprocal-rank fusion* combines the ranked lists from each retriever by summing reciprocal ranks; it is robust, requires no calibration, and is the right default. *Score-based fusion* combines normalised scores with weights; it is more powerful but requires careful normalisation per retriever and per corpus, and is sensitive to score drift when the underlying models change.
15. **Per-query weighting.** A query classifier can route queries to dense-heavy, sparse-heavy, or balanced fusion. Short keyword queries lean sparse; long natural-language questions lean dense. The classifier is a small upstream call; its accuracy is a tuning target.
16. **Filters as first-class.** Structured filters (region, permission, status, date range) apply before the fusion. A great relevance ranking over results the user is not allowed to see, or over deprecated content, is a worse result than a slightly worse ranking over correctly filtered candidates.

### Stage 4 — Embedding model selection

17. The embedding model is a load-bearing choice. Design a rubric and pick deliberately.
18. **Dimensionality and storage cost.** A model that produces 1536-dimension vectors costs roughly three times the storage and search cost of a model producing 512-dimension vectors. Storage scales linearly; ANN-search cost scales with both dimension and dataset size.
19. **Domain fit.** A model trained on web text is a strong default for web-like corpora. A model fine-tuned on code, or on legal text, or on a specific language, can substantially outperform a general model on its domain. Bench the candidate models on a held-out slice of the actual corpus before picking.
20. **Multilingual.** If `corpus` covers more than one language, prefer a model that produces a shared embedding space across those languages. Per-language indexes are operationally heavier and lose cross-lingual matching.
21. **Asymmetric models.** Some models offer distinct query and document encoders trained for asymmetric search. They tend to outperform symmetric models on question-document retrieval at moderate added complexity.
22. **Self-hosted vs hosted.** A hosted embedding service is cheap to start, expensive at scale, and ties freshness to a vendor. A self-hosted model is the inverse. Pin the trade-off against `stack_constraints` and the expected corpus size.
23. **Versioning and migration.** Embedding models change. Plan for re-embedding from day one: the index records the model version, the application records the embedding version at query time, and the migration path is a parallel index that backfills in the background and cuts over with measurement.
24. **Quantisation.** Product quantisation, scalar quantisation, and binary quantisation trade recall for memory. At small scale, full-precision is the right default; at scale, quantisation is a meaningful cost lever with quality cost that must be measured, not assumed.

### Stage 5 — Indexing pipeline

25. The indexing pipeline ingests documents into both the sparse and dense indexes. Design it as named, independently-measurable stages.
26. **Fetch and normalise.** Read documents from their source of truth, normalise to a canonical representation (canonical character encoding, normalised whitespace, expanded short forms where appropriate), strip boilerplate, preserve structure.
27. **Field extraction.** Pull out the structured fields used as filters and as ranking signals. Field extraction is its own quality target; a mis-extracted timestamp poisons every freshness-aware ranking that touches it.
28. **Chunking.** For long documents, chunking decisions follow the rules in the rag-product-loop-designer skill: structure-aware chunks by default, sliding windows as a fallback, tables and code with their own patterns. Each chunk records its parent document and position.
29. **Embedding.** Pass chunks (or whole short documents) through the embedding model. Embedding is the costly stage; cache aggressively keyed by chunk hash and model version.
30. **Sparse-index update.** Update the BM25 (or equivalent) index with the chunk text. Sparse indexes are cheap and fast to update.
31. **Dense-index update.** Update the vector index with the embedding and the chunk metadata. Vector indexes vary widely in update cost; some require periodic rebuilds, others support incremental updates with eventual consistency. Pin the operating model.
32. **Smoke probes.** After each index update, a fixed set of probe queries runs against the index and asserts the expected top-k results. A silent index breakage that surfaces as "search quality dropped" three days later is a much harder incident than one caught at the ingestion stage.

### Stage 6 — Reranking

33. A cross-encoder reranker is the single most impactful quality lever in modern semantic search. Pin its role.
34. **What it does.** The retriever produces a top-k candidate list with a coarse score. The reranker pairs the query with each candidate and produces a fine-grained relevance score, using a model with full cross-attention between query and document. Cross-encoders are too expensive to run over the whole corpus; reranking the top-k of a hybrid retrieval is the standard pattern.
35. **k tuning.** A common operating point is to retrieve a top-50 to top-200 from each underlying retriever, fuse, and rerank the top-25 to top-100 with the cross-encoder. The right number depends on the reranker's strength, the retrieval recall, and the latency budget. Measure recall@k of the retriever before rerank to set a floor.
36. **Model choice.** Open-source cross-encoders cover a wide quality and cost range. As with embedding models, pick by benchmark on a held-out slice of the actual corpus. The cost in latency and money is significant; the quality lift justifies it on most production corpora.
37. **Domain adaptation.** Fine-tuning a reranker on in-domain query-document pairs typically beats the strongest off-the-shelf model. The fine-tuning data is the next stage's deliverable; budget for collecting it.
38. **Skip conditions.** Some queries do not need a reranker — a unique identifier lookup, a query that returned only one candidate, a query with extreme keyword specificity. A small upstream classifier can skip rerank to save latency and cost on these cases.

### Stage 7 — Training data, hard negatives, and offline learning

39. The quality of a reranker (and a fine-tuned embedding model) depends on the data it learns from. Pin the data strategy.
40. **Positive pairs.** A positive pair is a query and a document that is a good result for it. Sources: labelled examples from the team, click-through data from production search logs (with caveats about position bias), human ratings, downstream task success ("this document let the user answer their question"). A few thousand high-quality pairs beats a million noisy ones.
41. **Hard negatives.** A negative pair is a query and a document that should not have ranked highly. Random documents are easy negatives — the model learns nothing from them. Hard negatives are documents the retriever surfaced but a human judges irrelevant; they are the data that teaches the reranker to draw fine distinctions.
42. **Hard-negative mining.** Run candidate retrieval over the training queries, surface the top-k, exclude the known positives, and surface the rest for human or model-graded labelling. Pinned negatives become training pairs. Refresh hard negatives as the retriever improves; today's hard negatives become tomorrow's easy negatives.
43. **In-batch negatives.** During training, other queries' positives in the same batch can serve as additional negatives. The technique is cheap and improves embedding-model training; use it as a complement to mined hard negatives, not a replacement.
44. **Position bias correction.** Click data is biased by position — users click result one more often than result two regardless of relevance. Correct with a click model (a propensity-weighted loss or an inverse-propensity estimator) before using clicks as supervision.
45. **Refresh cadence.** Training data is not a one-time artefact. Plan to refresh it on a cadence matched to corpus volatility — quarterly for a stable corpus, monthly or faster for a fast-evolving one.

### Stage 8 — Freshness

46. Stale results are a quality regression that users feel quickly. Design the freshness story explicitly.
47. **Per-source SLA.** Each source feeding the index has a freshness SLA — how long between a change in the source and the change reflected in search. Real-time, near-real-time (minutes), batch (hours), and slow (daily or worse) are all valid; pin the right level per source.
48. **Event-driven updates.** Where sources can emit change events, the indexer subscribes and applies updates incrementally. Event-driven is the cheapest path to near-real-time when the source supports it.
49. **Polling and diffs.** Where sources do not emit events, the indexer polls on a schedule and diffs against the previous extract. Diffs are smaller and cheaper to apply than full-index rebuilds.
50. **Deletes and unpublishings.** A removed document that lingers in the index is the most damaging freshness failure — search surfaces content that no longer exists. Treat deletes as first-class events, propagate them within minutes, and audit for orphans regularly.
51. **Recency as a signal.** When the corpus has a notion of "newer is better" (news, social, real-time alerts), include recency as a ranking signal alongside relevance. Pin the decay function and re-tune on the eval — a wrong recency weight is hard to feel and easy to mis-calibrate.
52. **Snapshot search.** Some workloads (compliance, research, point-in-time analysis) require searching the corpus as it was at a particular date. Snapshot search is incompatible with naive in-place index updates; design a snapshot strategy upfront if the requirement exists.

### Stage 9 — Sharding, replication, and scale

53. At scale, the index is sharded for capacity and replicated for availability. Pin the shape.
54. **Shard key.** The shard key trades off query parallelism against query fan-out. Sharding by tenant is the right default when most queries are tenant-scoped — each shard is small, queries do not fan out, and isolation is structural. Sharding by content hash spreads load evenly but every query fans out to every shard.
55. **Replicas.** Read replicas absorb query load and improve availability. Write paths flow through the primary and replicate asynchronously; staleness between primary and replica is bounded and monitored.
56. **Cross-shard queries.** When queries do fan out, the coordinator merges results across shards. The merge requires comparable scores across shards — same retriever, same parameters, same recency configuration. Cross-shard score normalisation is a known hazard; the design specifies how it is handled.
57. **Backpressure and timeouts.** A slow shard should not slow the whole query. Pin per-shard timeouts and a degradation policy — return fewer results, return cached results, return a graceful "search is degraded" rather than a thirty-second hang.
58. **Rebuilds.** A full rebuild is required when the embedding model, the chunking strategy, the analyser, or the schema changes. Design rebuilds as background jobs against a parallel index that is cut over after verification. Avoid in-place rebuilds that block live traffic.

### Stage 10 — Tenancy and access control

59. From `tenancy`, design the isolation model.
60. **Single tenant.** No isolation concerns. The architecture is the simplest, and most of the rest of the design applies as written.
61. **Multi-tenant shared.** All tenants share the index, each document carries a tenant identifier, and queries filter by the calling tenant. The model is cheap and operationally simple but requires iron-clad filter enforcement at the query layer — a missed filter is a cross-tenant data leak.
62. **Multi-tenant isolated.** Each tenant has its own index (or its own shard with strict routing). Isolation is structural; cross-tenant leakage is harder. Operationally heavier — more indexes to manage, more rebuilds, more monitoring.
63. **Hierarchical.** Some tenancy models nest — an enterprise tenant contains team tenants contains user views. The query layer enforces the hierarchy and the design names the inheritance rules.
64. **Permission-aware retrieval.** Inside a tenant, documents may have per-user permissions. Two patterns: filter at query time against a permission service (slow, accurate, robust to revocation), or denormalise permissions onto each document as a tag and filter against the tag set (fast, requires re-indexing on permission change). Pin one per workload; mixing is dangerous.
65. **Audit.** Every search query touches potentially sensitive content. Audit retains the query, the calling principal, the tenant, and the returned document set (or a fingerprint of it) for the regulatory window. For high-sensitivity workloads, sample human review of audit records is part of the operating model.

### Stage 11 — Evaluation methodology

66. A search system without an evaluation harness is a search system whose quality is a guess. Pin the evaluation methodology.
67. **Offline relevance judgement.** Build a query set representative of production: a curated head, a sampled torso, an adversarial tail. For each query, annotate ground-truth relevance for the top-k results from baseline retrieval. The annotations support nDCG, MAP, and recall metrics.
68. **Online metrics.** When production traffic exists, track click-through rate, time to first click, query reformulation rate, zero-result rate, and any downstream task-success metric. Online metrics are noisier than offline but capture user behaviour offline cannot.
69. **A/B discipline.** A new embedding model, a new reranker, a new fusion weighting goes out as an A/B experiment with a defined success metric, a defined sample size, and a defined run length. Promotion is conditional on pre-registered outcomes, not on cherry-picked subsets.
70. **Slicing.** Aggregate metrics hide regressions. Slice by query length, query language, tenant, document type, and intent category. A change that improves the aggregate by two points while dropping the long-query slice by ten is a regression.
71. **Diff dashboards.** Every retrieval-stack change produces a side-by-side dashboard of the metrics across slices, with statistical significance and confidence intervals. Reviewers look at the dashboard, not the headline number.
72. **Regression suite.** A frozen query set with known good results runs after every deploy; meaningful drops on the regression suite are treated as outages.

### Stage 12 — Operations, observability, and roadmap

73. Close the architecture with operational shape and the roadmap.
74. **Latency and error budgets.** Pin a p50, p95, and p99 latency target. Pin an error-rate budget per quarter. Pin a freshness budget — how often the freshness SLA is allowed to slip.
75. **Observability.** Per-stage timings (retrieval, rerank, fusion, filter), per-shard health, per-query cost in vector-store reads and reranker calls, per-index size and growth. The observability stack supports the eval, the on-call, and the cost review.
76. **Capacity planning.** Embedding storage, vector-search compute, reranker compute, and source-fetch bandwidth each have growth curves. Project them under the corpus and query growth assumptions; flag inflection points.
77. **Roadmap.** Phase one is BM25 with one structured filter set, a dense index using an off-the-shelf embedding model, reciprocal-rank fusion, no reranker, an offline eval against a curated query set. Phase two adds a cross-encoder reranker and a hard-negative mining loop. Phase three adds tenant-aware sharding, freshness SLAs per source, and fine-tuned embeddings or reranker. Phase four is consolidation — retiring legacy keyword-only search, expanding to new corpora, integrating with downstream RAG and graph systems. Pin which phase the team starts in and the exit criteria for each transition.
78. **Exit criteria for the design.** The architecture document is done when a user-research partner can read it and recognise the user; an engineer can read it and start implementing without further questions; a security reviewer can read it and approve the tenancy and audit controls; and a product manager can read it and understand the cost and latency consequences.

## Outputs

The `search_architecture` markdown contains the twelve stages in order. The `search_summary` JSON mirrors the structure for tooling and review automation.

## Examples

A semantic search system for an enterprise document-management product lands with: hybrid BM25-plus-dense retrieval with reciprocal-rank fusion; a domain-suited multilingual embedding model self-hosted to support data-residency; a cross-encoder reranker on the top-50 fused candidates; permissions denormalised onto each document with re-indexing on permission change; sharding by tenant with per-tenant indexes; near-real-time freshness via change events from the document store; offline eval against a thousand-query curated set with weekly online metrics from production; phased rollout starting with hybrid retrieval and adding the reranker once the gold set is large enough to fine-tune on.

A semantic search system for a code search product lands with: BM25 over symbol and identifier text plus a dense index over function-level chunks using a code-tuned embedding model; reranker fine-tuned on click-through data with hard negatives mined from same-function-name confusables; freshness driven by repository webhook events with sub-minute target; sharding by repository with cross-repo queries handled by fan-out and score normalisation; single-tenant per organisation with deep visibility-permission enforcement at query time; eval blending offline relevance judgement with downstream task-success metrics (did the user copy a result, did the result compile in the user's context).

## Limitations

The skill produces an architecture, not an implementation. It does not pick a specific vector database, embedding service, or reranker; those decisions are constrained by the design but resolved by the engineering team in context.

The skill does not cover the user interface of search — query input affordances, faceting UI, result presentation, click instrumentation. Those are real product concerns and they affect what the architecture must support, but the architecture is the substrate they sit on, not their design.

The skill does not eliminate the need for an evaluation harness. The architecture names the evaluation methodology and the metrics; the design and operation of the harness is a sustained project, not a one-time deliverable.

## Sources reviewed

- https://github.com/qdrant/qdrant (Apache-2.0)
- https://github.com/weaviate/weaviate (BSD-3-Clause)
- https://github.com/opensearch-project/OpenSearch (Apache-2.0)
- https://github.com/UKPLab/sentence-transformers (Apache-2.0)
- https://github.com/microsoft/graphrag (MIT)
- https://github.com/HKUDS/LightRAG (MIT)
