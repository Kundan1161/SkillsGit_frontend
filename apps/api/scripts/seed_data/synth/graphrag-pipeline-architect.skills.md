---
id: skillsgit-curated/graphrag-pipeline-architect
version: 1.0.0
name: GraphRAG Pipeline Architect
description: Design a graph-augmented RAG pipeline — entity and relationship extraction, community detection, hierarchical summaries, hybrid retrieval, citation discipline, and evaluation methodology.
authors:
  - name: Wave-5 Synth
    handle: wave5-data
    role: author
category: data
tags:
  - niche:knowledge-graph-architecture
  - graphrag
  - retrieval-augmented-generation
  - entity-extraction
  - community-detection
  - hierarchical-summaries
  - hybrid-retrieval
  - citation-discipline
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
  estimated_tokens_per_invocation: 8500
trigger_keywords:
  - graphrag
  - graph rag
  - graph augmented retrieval
  - entity relationship extraction
  - community detection rag
  - hierarchical summaries
  - hybrid retrieval graph
  - rag with knowledge graph
  - graph-aware retrieval
  - citation graph
  - global question answering
  - rag pipeline design
example_invocations:
  - "Design a GraphRAG pipeline over our compliance corpus — extraction, community summaries, and retrieval."
  - "We need global question answering across thousands of documents. Plan the graph-augmented pipeline."
  - "How should we mix vector retrieval with a knowledge graph for our enterprise search assistant?"
  - "Design extraction prompts, schema, and eval for a graph-augmented RAG over financial filings."
inputs:
  - name: corpus
    type: text
    required: true
    description: The document corpus the pipeline will operate on — domain, volume, formats, freshness, language mix.
  - name: question_types
    type: text
    required: false
    description: Representative questions the system has to answer — local (about one entity or document) vs global (themes across the whole corpus).
  - name: existing_graph
    type: text
    required: false
    description: An existing knowledge graph or schema the pipeline should align to, if any.
  - name: latency_budget
    type: choice
    required: false
    description: Acceptable query latency.
    choices: [interactive_sub_second, interactive_few_seconds, batch_minutes, batch_hours]
  - name: stack_constraints
    type: text
    required: false
    description: Constraints on LLM provider, graph store, vector store, tenancy, residency, cost ceilings.
  - name: trust_requirement
    type: choice
    required: false
    description: How strict the citation and audit obligations are.
    choices: [casual, professional, regulated_high_stakes]
outputs:
  - name: graphrag_design
    type: markdown
    description: The end-to-end design — extraction schema, indexing pipeline, retrieval strategy, generation pattern, citation discipline, and evaluation.
  - name: graphrag_summary
    type: json
    description: Structured summary with `extraction`, `indexing`, `community_summaries`, `retrieval`, `generation`, `citations`, `eval`, and `operations`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# GraphRAG Pipeline Architect

## When to use

Use this skill when a team is building retrieval-augmented generation over a corpus where plain vector retrieval is hitting a ceiling and the missing ingredient is structure. Vector retrieval is excellent at finding *passages similar to a query*. It is poor at answering questions that require *connecting facts across passages*, *summarising themes across an entire corpus*, or *traversing a chain of relationships to reach an answer*. Graph-augmented retrieval addresses those failure modes by indexing the corpus as a knowledge graph in parallel with a vector store, and routing queries to the index that fits the question shape.

The skill produces the pipeline design — extraction schema, indexing stages, community summarisation, retrieval routing, generation pattern, citation discipline, and evaluation. It assumes a working understanding of plain RAG; it is a design overlay on top of the RAG product loop, not a replacement for it. It does not select the LLM provider, the graph database, or the vector store; those are constraints that shape the design but are resolved by engineering.

The skill is the natural sequel to the knowledge-graph-architecture-designer skill when the graph in question is being built from text rather than from structured sources. It is also a peer of the rag-product-loop-designer skill in this library: where that skill designs the product loop for plain vector RAG, this skill designs the pipeline for the graph-augmented case.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `corpus` | yes | Anchors the extraction schema and chunking decisions. |
| `question_types` | no | Decides the retrieval-routing strategy and the global-vs-local emphasis. |
| `existing_graph` | no | Aligns the extraction targets to an existing schema if one exists. |
| `latency_budget` | no | Constrains community-summary depth and retrieval breadth. |
| `stack_constraints` | no | Bounds the implementation options. |
| `trust_requirement` | no | Sets the citation, refusal, and audit standard. |

## How to apply

The design walks through thirteen stages. The output is a pipeline design document with extraction prompts sketched, retrieval flows diagrammed in prose, and an explicit evaluation plan.

### Stage 1 — Decide whether GraphRAG is the right answer

1. The first stage is a fit check. Graph augmentation adds construction cost (an extraction pass over the corpus, an LLM-driven graph build, ongoing maintenance) and retrieval complexity. The added cost is justified when the question mix includes the patterns vector RAG handles poorly.
2. The fit signals are: many questions require synthesising information from passages that share entities but no surface-text similarity; users ask thematic or global questions about the corpus; the corpus has rich entity structure (people, organisations, products, events, claims) that recurs across documents; the team needs traceability that crosses document boundaries.
3. The anti-signals are: questions are almost always answerable from a single passage; the corpus is small enough that the whole corpus fits in context for the questions that matter; the operating budget cannot absorb an extraction pass and ongoing community-summary refresh; the team lacks the operational capacity to keep a graph in sync with a moving corpus.
4. From `question_types`, classify each example as *local* (answerable from one or a few neighbouring passages) or *global* (requires the corpus as a whole). If the mix is overwhelmingly local, document the conclusion and recommend vector RAG with reranking instead. If global questions are a meaningful fraction, proceed.

### Stage 2 — Pin the question taxonomy

5. The pipeline routes queries to different retrieval strategies depending on what they ask for. Pin the taxonomy explicitly so the router has a target.
6. **Lookup questions** ask for a specific fact about a specific entity. The retrieval is "fetch this entity and its immediate neighbourhood" plus the supporting passages.
7. **Connection questions** ask how two or more named entities relate. The retrieval is "find the shortest or most-cited paths between these entities" plus the passages that justify the edges.
8. **Local-context questions** ask for an explanation grounded in a small region of the corpus around a topic. The retrieval is "find the relevant passages and the entities they mention" — the graph augments but does not lead.
9. **Global-theme questions** ask about patterns across the whole corpus — what are the major themes, which entities are most connected, what does the corpus claim about a topic. The retrieval is "consult the community summaries and aggregate".
10. **Reasoning questions** ask for an inference that combines facts the corpus contains but no passage states. The retrieval is a hybrid — graph traversal for the chain, passages for the citations, and generation for the synthesis.
11. Map each example in `question_types` to a category. The category distribution drives the rest of the design — a pipeline answering ninety-percent global questions invests heavily in community summarisation; a pipeline answering ninety-percent connection questions invests heavily in entity resolution.

### Stage 3 — Extraction schema

12. The extraction schema defines what entities and relationships the pipeline will pull out of the text. The schema is the contract between the LLM extractor and the rest of the pipeline; getting it right is the highest-leverage decision.
13. **Reuse existing schema where possible.** If `existing_graph` is provided, the extraction schema mirrors its entity types and relationship types. Inventing a parallel schema and reconciling later is more work than aligning from the start.
14. **Entity types.** List the small number — typically five to twenty — of entity types the pipeline will extract. Each type has a clear definition, a list of expected attributes, and a note on the kind of mentions the extractor should and should not capture. Overly broad types ("Thing") produce a graph that is dense and meaningless; overly narrow types fragment the entity space.
15. **Relationship types.** List the relationship types — typically ten to fifty. Each type has a directionality, a domain and range of allowed entity types, and a definition of when the relationship is asserted. "Mentioned with" is too weak to be useful; "acquired" or "regulates" or "depends on" are useful because they constrain interpretation.
16. **Open-ended vs closed.** Some pipelines pin a fixed schema and reject extractions that fall outside it. Others run with an open schema and emerge the types from the corpus. Closed schemas are easier to evaluate and use; open schemas are easier to start with and harder to operationalise. The middle path: seed with a closed schema, allow the extractor to propose new types into a staging area, and review proposals before promoting them.
17. **Attributes.** For each entity type, list the attributes the extractor should populate. Attributes are textual claims the entity carries — a role, a date, a value. Attribute extraction multiplies the extractor's failure modes; include only attributes whose query value justifies the cost.
18. **Provenance.** Every extracted entity, relationship, and attribute carries a citation back to the source chunk. The chunk is the unit of evidence; without citations, the graph is unverifiable and the downstream answers cannot cite their sources.

### Stage 4 — Chunking and pre-extraction processing

19. Extraction runs over chunks, not whole documents. Design chunking with extraction in mind.
20. **Chunk size.** Larger chunks give the extractor more context but raise extraction cost and dilute attention. Smaller chunks miss relationships that span chunk boundaries. A typical operating point is a few hundred to a few thousand tokens with modest overlap; the right size depends on the corpus, and the design pins a starting size with a plan to tune from the eval.
21. **Boundary awareness.** Chunk on structure (paragraphs, sections, headings) rather than fixed tokens. A chunk that splits a sentence in half throws context away.
22. **Metadata.** Each chunk carries its document identifier, position, source date, source authority tier, and any structural ancestry (which section, which document type). Extracted entities inherit this metadata as provenance.
23. **Pre-processing.** Strip boilerplate, normalise whitespace, expand abbreviations the extractor cannot decode from context, replace template tokens with their meaning. The extraction prompt then sees text that resembles natural prose.

### Stage 5 — Entity and relationship extraction

24. The extractor is an LLM call (or sequence of calls) that maps a chunk to a structured set of entity, relationship, and attribute assertions.
25. **Prompt design.** The prompt names the schema (the entity and relationship types from Stage 3), describes the output format (typically a JSON list of typed assertions with a span citation), and instructs the model to abstain when no relevant entities are present rather than fabricate them. The prompt names the cost of fabricated entities loudly; a confident hallucinated edge poisons every downstream query that touches it.
26. **Few-shot anchoring.** Include a handful of high-quality examples covering the common entity types, the trickier relationship types, and at least one negative example where the chunk contains no extractable structure. Few-shot examples bound the model's interpretation of the schema in a way prose definitions cannot.
27. **Two-pass extraction.** A first pass extracts entities only; a second pass, given the entities and the chunk, extracts relationships between them. Two-pass extraction outperforms single-pass on most corpora because the second pass can focus on the relational pattern without re-deciding which spans are entities.
28. **Span fidelity.** Each extraction records the exact span in the chunk it came from. Spans support audit, support disagreement resolution, and support deterministic re-extraction when the model changes.
29. **Confidence.** Ask the extractor to emit a calibrated confidence for each assertion. Calibrate the threshold empirically against the eval; below-threshold assertions route to a quarantine for human review rather than the graph.
30. **Idempotence and re-runs.** Extraction is expensive. Cache results keyed by chunk hash and extractor version. When the schema or the model changes, the version bump invalidates the cache and the next run re-extracts; the cache makes incremental ingestion cheap.

### Stage 6 — Entity resolution and graph construction

31. Extractions from independent chunks frequently refer to the same real-world entity. Resolution stitches them into one node.
32. **Surface normalisation.** Casefold, strip honorifics, normalise corporate suffixes, expand common abbreviations. The normalised surface form is the first resolution key.
33. **Type-aware blocking.** Candidate matches are constrained to entities of the same type. A "Smith" of type Person is not a candidate match for a "Smith" of type Organisation.
34. **Embedding-based candidate generation.** For each extracted mention, retrieve the top-k existing entities of the same type by embedding similarity over the surface form plus a short descriptive context. Embedding candidates capture spelling variation and translation that exact matching misses.
35. **Pairwise judgement.** A pairwise classifier (a model call or a learned classifier) decides whether two candidates refer to the same entity. The judgement uses the surface forms, the attributes the chunks provide, and the local neighbourhood (the relationships already extracted around each candidate). The judgement is recorded with its evidence so a downstream auditor can reconstruct the decision.
36. **Conflict policy.** When extractions disagree on an attribute, the resolution stores both values with their citations rather than picking one. The source-of-truth rules (from the knowledge-graph-architecture-designer skill) decide which value the query layer surfaces.
37. **Provenance preservation.** A resolved entity has a many-to-one relationship from the mentions to the canonical node. Queries can drill from the canonical entity to the mentions and from the mentions to the source chunks. The chain is the audit story.

### Stage 7 — Community detection

38. A knowledge graph extracted from a corpus is unevenly clustered: dense neighbourhoods around frequently-mentioned entities, sparser tendrils around the long tail. Communities are the natural unit for global summarisation.
39. **Algorithm choice.** Use a community-detection algorithm appropriate to the graph scale and structure — Leiden and Louvain for modularity-based community finding on large graphs, hierarchical variants for nested communities, label-propagation for streaming updates. The choice is downstream of `latency_budget` and the size of the graph; pin one default and a fallback.
40. **Hierarchy.** Communities are typically nested — small tight clusters inside larger thematic regions. Compute the hierarchy explicitly; queries at different abstraction levels consult different layers.
41. **Edge weighting.** Community detection runs on a weighted graph. Edge weights combine extraction confidence, citation count (how many chunks support the edge), and edge-type importance (some relationship types should weigh more than others). Pin the weighting scheme.
42. **Refresh cadence.** Communities are recomputed when enough new edges have arrived to shift the structure meaningfully. The cadence depends on corpus volatility — daily for a fast-moving newsroom, monthly for a regulatory archive. Stale communities produce summaries that no longer reflect the corpus.
43. **Identity across refreshes.** Communities are not stable identifiers across recomputations. Map each new community to its closest predecessor by member overlap so that downstream consumers of community summaries can track drift rather than experiencing a clean break.

### Stage 8 — Hierarchical community summaries

44. Each community gets an LLM-generated summary — a short paragraph or page-length article describing the entities in the community, the relationships among them, the themes the community represents, and the supporting citations.
45. **Bottom-up summarisation.** Summarise the leaf communities first from the members and their edges. Summarise the parent communities from their children's summaries plus a sample of edges that cross child boundaries. The hierarchical roll-up keeps each summary within an LLM context budget regardless of total graph size.
46. **Schema for summaries.** A summary is a structured document with a title, a one-sentence headline, a few-paragraph description, a list of the most central entities, a list of representative relationships, and a citation manifest mapping every claim back to source chunks. Free-form summaries are harder to retrieve over and harder to evaluate.
47. **Faithfulness.** The summary prompt instructs the model to ground every claim in the entities and edges it was given, to abstain when the inputs do not support a claim, and to flag where a claim was inferred rather than observed. Unfaithful summaries are the most damaging single failure mode in a graph-augmented system because they shape the answer to a class of questions, not just one query.
48. **Indexing.** Summaries are stored alongside their structured form and embedded for vector retrieval. Queries asking global-theme questions retrieve over summaries; queries asking lookup questions retrieve over entities; the router decides which.

### Stage 9 — Hybrid retrieval routing

49. Retrieval is a router on top of multiple indexes. The router classifies the question, consults the appropriate indexes, and assembles a context for generation.
50. **Question classification.** A small model call classifies the question into the taxonomy from Stage 2. Cache classifications; the same question rarely needs classification twice within a session.
51. **Local route.** Lookup, connection, and local-context questions hit the entity and chunk indexes. Retrieve the named entities, their neighbourhood (one or two hops), and the chunks supporting the surfaced entities and edges. Rerank by relevance to the question.
52. **Global route.** Global-theme questions hit the community-summary index. Retrieve the top summaries, aggregate the claims that appear across multiple summaries with their citations, and pass the aggregate to generation.
53. **Hybrid route.** Reasoning questions trigger both routes: a graph traversal for the connecting structure and a passage retrieval for the textual grounding. The generation step receives both.
54. **Confidence and fallback.** When the router's classification is low-confidence or the chosen route returns thin results, the pipeline falls back to a broader retrieval rather than producing a confident answer from too little. Refusal is a valid output.
55. **Rerank discipline.** A cross-encoder or LLM reranker scores the retrieved chunks and entity neighbourhoods for relevance to the question. The reranker is the single most cost-effective lever for retrieval quality; pin its model and its score threshold.

### Stage 10 — Generation pattern and citation discipline

56. The generation step receives the assembled context and produces the answer.
57. **Faithfulness rule.** Generation answers only from the supplied context. When the context does not support the answer, generation says so. Faithfulness is enforced by the prompt and measured separately in evaluation; the prompt is the first line of defence.
58. **Citation rule.** Every sentence or claim links to the entities, edges, or chunks that justify it. For graph-augmented answers, citations come in two flavours — a *chunk citation* points to a source passage, an *edge citation* points to a graph edge with its own provenance. The UI renders both, and the user can drill from the answer to the underlying passages.
59. **Inference flagging.** When the answer combines multiple facts to reach a conclusion no single source states, the inference is flagged as such and the supporting facts are each cited. Inferences should never masquerade as direct citations.
60. **Refusal rule.** When `trust_requirement` is `regulated_high_stakes`, refusal is preferred over a hedged answer. The refusal explains what was missing — an entity not in the graph, a relationship not supported by any chunk, an inference too speculative to make.
61. **Structured output.** For lookup and connection questions, structured output is often the right shape — a named entity card, a list of paths, a comparison. Free text is the right shape for global-theme questions where narrative matters.
62. **Streaming with citations intact.** When streaming the answer to the user, hold citation rendering until the surrounding text is complete enough to attach to the right span. Premature citation rendering leads to misaligned hyperlinks.

### Stage 11 — Evaluation methodology

63. A graph-augmented pipeline has three places to evaluate independently: extraction quality, retrieval quality, and answer quality. Build the eval as three nested loops.
64. **Extraction eval.** Annotate a held-out set of chunks with the ground-truth entity, relationship, and attribute assertions. Compute per-type precision, recall, and F1 against the extractor's output. Track over time; a regression after a model change is the most common silent failure.
65. **Retrieval eval.** Compose a question set with the right mix from the question taxonomy. For each question, annotate the ground-truth set of entities, edges, communities, and chunks that should be retrieved. Compute recall and rank metrics per route; a global question whose summary index does not surface the right community is a routing failure, not a retrieval failure.
66. **Answer eval.** Use a model-graded judge with a rubric covering faithfulness, completeness, citation correctness, and refusal correctness. Sample human review on a fixed slice each cycle to calibrate the judge.
67. **Adversarial probes.** Add probes for the known failure modes — questions whose answer requires an entity not in the corpus (refusal should fire), questions whose answer requires connecting facts across documents (the hybrid route should fire), questions whose answer requires inference (the inference flag should appear), questions with named entities the extractor regularly mis-types (resolution should succeed or refuse).
68. **Cost and latency.** Track end-to-end cost and latency per question category. A pipeline that answers global questions correctly but burns ten dollars and three minutes per question is a research demo, not a product. Pin budget gates per category.
69. **Regression discipline.** Every change to the pipeline — a new extractor model, a new schema, a refreshed community partition, a router change — runs the full eval and the diff is reviewed. Improvements on one slice that regress another are flagged for explicit acceptance.

### Stage 12 — Operations and freshness

70. The graph and its summaries are not built once. Plan the ongoing operations.
71. **Incremental extraction.** New documents enter the pipeline through the same extractor but only their chunks need re-extraction. The graph absorbs the new assertions through the resolution step; communities are dirtied for re-computation but not re-computed immediately on every ingest.
72. **Community refresh.** Pin the cadence and the trigger conditions. A volume threshold (re-compute after this many new edges) and a time threshold (re-compute at least this often) together avoid both over- and under-refreshing.
73. **Drift monitoring.** Track the rate of new entity types proposed (a sign the schema is wrong or the corpus has shifted), the resolution-rate of new mentions to existing entities (a sign of entity-space drift), and the average summary refresh delta (a sign of corpus volatility). Each metric has an alarm threshold.
74. **Versioning.** The extraction schema, the extractor prompt, the resolution model, the community algorithm, and the summary prompt are each independently versioned. An answer is reproducible to its inputs only when all five versions are recorded at query time.
75. **Cost ceilings.** Extraction and summarisation are the two cost centres. Track per-document extraction cost and per-community summary cost; alert on regressions. A model upgrade that doubles extraction cost is a conversation, not a silent deployment.

### Stage 13 — Failure-mode playbook

76. Close the design with the failure-mode playbook.
77. **Confident hallucinated entity.** Extractor invents an entity the chunk does not contain. Caught by extraction eval and by per-entity citation audit. Fix path: tighten the extractor prompt; raise confidence threshold; add a chunk-grounding check.
78. **Mis-resolution.** Resolution merges two distinct real-world entities or splits one. Caught by resolution eval and by user reports. Fix path: improve blocking; tighten the pairwise classifier; add a human-review queue at low confidence.
79. **Stale community summary.** Summary describes a community state from a prior refresh. Caught by drift monitoring and answer eval. Fix path: tighten refresh cadence or add an event-driven refresh for high-impact entities.
80. **Wrong-route classification.** Router sends a global question to the local route or vice versa. Caught by retrieval eval. Fix path: improve the classifier examples; add a fallback to a hybrid route at low confidence.
81. **Inference passed off as direct citation.** Generation combines facts but cites only one. Caught by faithfulness judge and by inference-flag audit. Fix path: tighten the generation prompt; surface the inference flag prominently in the UI.
82. **Cost runaway.** A spike in question volume or in average chunks-per-question pushes cost above budget. Caught by per-question cost dashboard. Fix path: tighten the rerank top-k; cache aggressively; consider routing low-stakes questions to a smaller model.

## Outputs

The `graphrag_design` markdown contains the thirteen stages in order, with extraction-schema sketches, retrieval-routing diagrams in prose, and the evaluation plan. The `graphrag_summary` JSON mirrors the structure for tooling and review automation.

## Examples

A GraphRAG pipeline over a regulatory-filing corpus for a financial-services compliance team lands with: extraction schema aligned to the existing compliance ontology (Filer, Filing, Control, Regulation, Citation); two-pass extraction with span fidelity and per-edge provenance; Leiden community detection with a quarterly refresh; hierarchical summaries published as structured documents with citation manifests; a router that classifies questions into lookup, connection, and global-theme buckets; generation with strict refusal on out-of-corpus questions and inference flagging on multi-hop reasoning; extraction eval against a fifty-document gold set; retrieval and answer eval against a curated question set with regulatory subject-matter experts in the loop.

A GraphRAG pipeline over an internal engineering knowledge base lands with: an open-schema extractor seeded with five common types (Service, Team, Incident, RFC, Person), permitting extractor-proposed types into a staging area; chunking on heading boundaries with parent-section metadata; weekly community refresh aligned to the release cadence; community summaries titled by theme ("Auth platform reliability", "Data-pipeline ownership"); a router that defaults global engineering-strategy questions to the community-summary index and specific incident questions to the entity and chunk indexes; generation that emits structured incident timelines for chronological questions and prose answers for explanatory ones; eval slimmed to extraction precision, retrieval recall, and a weekly human-rated sample of answers.

## Limitations

The skill produces a pipeline design, not an implementation. It does not pick an LLM, a graph store, a vector store, a community-detection library, or a reranker; those decisions are constrained by `stack_constraints` and resolved by engineering in context.

The skill assumes the corpus is text-shaped and extractable by a language model. Tabular corpora (spreadsheets, structured databases) benefit from different ingestion patterns; multimodal corpora require multimodal extractors not covered here.

The skill does not eliminate the need for the knowledge-graph-architecture-designer skill. When the graph in question will also receive data from non-text sources, the architecture skill covers the rest of the design; this skill covers only the text-extraction half.

## Sources reviewed

- https://github.com/microsoft/graphrag (MIT)
- https://github.com/HKUDS/LightRAG (MIT)
- https://github.com/neo4j-labs/llm-graph-builder (Apache-2.0)
- https://github.com/apache/jena (Apache-2.0)
- https://github.com/RDFLib/rdflib (BSD-3-Clause)
- https://github.com/dgraph-io/dgraph (Apache-2.0)
- https://github.com/UKPLab/sentence-transformers (Apache-2.0)
