---
id: skillsgit-curated/rag-product-loop-designer
version: 1.0.0
name: RAG Product Loop Designer
description: Design the product loop for a retrieval-augmented generation system — corpus curation, retrieval-quality eval, chunking strategy, citations UX, freshness handling, and content-gap mining from query logs.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: productivity
tags: [niche:ai-product-design, rag, retrieval, citations, corpus-curation, content-gaps, freshness, knowledge-product]
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
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - rag product loop
  - rag design
  - retrieval product
  - corpus curation
  - chunking strategy
  - rag citations
  - rag freshness
  - content gap mining
  - rag eval
  - knowledge product
  - rag answer ux
  - rag content strategy
example_invocations:
  - "Design the product loop for our help-centre RAG assistant — what to retrieve from, how to chunk, how to handle freshness."
  - "We're building a RAG over our internal wiki. Plan the corpus, the eval, and the citations UX."
  - "How do we mine query logs for content gaps and feed them back into the corpus?"
  - "Plan the freshness story for our RAG over product docs that update weekly."
inputs:
  - name: use_case
    type: text
    required: true
    description: What the RAG system is for, who uses it, and what success looks like.
  - name: corpus_description
    type: text
    required: false
    description: The candidate sources the RAG will retrieve from — internal wikis, help centres, document stores, product docs, code, customer data, etc.
  - name: query_examples
    type: text
    required: false
    description: A handful of representative user queries. Drives chunking and slicing decisions.
  - name: freshness_requirement
    type: choice
    required: false
    description: How fresh the retrieved content must be.
    choices: [real_time, daily, weekly, monthly, stable]
  - name: stack_constraints
    type: text
    required: false
    description: Constraints on vector store, embedding model, retriever stack, tenancy, residency, etc.
  - name: team_shape
    type: text
    required: false
    description: Who owns the corpus content vs the retrieval pipeline. Decides the content-gap workflow.
outputs:
  - name: loop_design
    type: markdown
    description: The end-to-end design for the RAG product loop — corpus curation, ingestion, chunking, retrieval eval, generation pattern, citations UX, freshness handling, content-gap mining, and the loop that ties it together.
  - name: loop_summary
    type: json
    description: Structured summary with `corpus`, `ingestion`, `chunking`, `retrieval_eval`, `generation`, `citations_ux`, `freshness`, `gap_mining`, `loop_cadence`, and `roles`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# RAG Product Loop Designer

## When to use

Use this skill when a team is building or operating a retrieval-augmented generation system and needs more than a prototype. A working prototype has an embedding model, a vector store, and a prompt. A working product also has a curated corpus, a measured retrieval pipeline, a citations UX users trust, a freshness story, and a closed loop that turns failed queries back into improved content.

This skill produces the product-level design for that loop. It is complementary to the engineering implementation: it does not pick the vector database, the embedding model, or the rerank library, but it defines the constraints those pieces have to meet. It is also complementary to the evaluation harness skill, which designs the test set and the metric stack in detail; this skill designs the *product* loop that the harness measures.

The skill applies to any RAG product — help-centre assistants, internal knowledge bots, document Q&A, code assistants over a private codebase, customer-data assistants, research tools over a publication corpus. It applies regardless of whether the RAG is a chatbot, an inline answer in a search UI, or a backend that produces structured outputs informed by retrieval. It is less useful for "just stuff everything into the context window" patterns, where retrieval is degenerate; those have their own design considerations not covered here.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `use_case` | yes | Anchors the loop. |
| `corpus_description` | no | Drives the curation and ingestion design. |
| `query_examples` | no | Drives chunking and retrieval-eval slices. |
| `freshness_requirement` | no | Decides the ingestion cadence and TTL design. |
| `stack_constraints` | no | Limits the embedding and reranker options. |
| `team_shape` | no | Decides who owns the content-gap pipeline. |

## How to apply

The skill walks through eleven stages, each producing a section of the deliverable. The output is a design document, not an implementation.

### Stage 1 — Define the answerable scope

1. The first failure mode of RAG products is users asking questions the corpus cannot answer. Pin the scope explicitly.
2. From `use_case` and `query_examples`, write a one-paragraph description of what the system *can* answer. Include the kinds of questions, the kinds of users asking, and the level of detail expected.
3. Write a paired description of what the system *cannot* answer. Include questions that fall outside the corpus, questions whose answer is in the corpus but in a form the system cannot synthesise (e.g. mathematical reasoning over tables), and questions whose answer requires actions outside retrieval (writing code, taking an action on the user's behalf).
4. Decide the system's response to out-of-scope questions. The default and almost always correct answer is a graceful "I do not have that information" with a path forward — search the broader product, open a ticket, request the content. Silence is worse; confident hallucination is much worse.
5. Pin a slogan: one sentence that the team agrees describes what this RAG is for. If two team members give different one-sentence answers, the scope is not settled and Stages 2+ will compound the ambiguity.

### Stage 2 — Curate the corpus

6. Inventory candidate sources from `corpus_description`. For each source, record: who owns it, how often it changes, how authoritative it is, whether it is public or restricted, and whether the content is structured (a table, a database) or unstructured (a wiki page, a PDF).
7. Decide whether each source is in scope for v1. Inclusion criteria: the source covers part of the answerable scope from Stage 1, the source is authoritative, the source is maintained, and the content is usable (parseable, not behind a paywall, not in a format the pipeline cannot read).
8. Decide deduplication strategy. The same content often lives in three places — a wiki page, a help-centre article, a PDF export. Pick the canonical version and exclude the others. Without deduplication, retrieval surfaces redundant chunks and citations become misleading.
9. Mark sources by trust tier. Tier-one sources (the canonical product documentation, the engineering wiki) win on conflicts; tier-two sources (community-contributed notes, vendor blog posts) supplement. The retrieval pipeline uses the tier to break ties and to label citations.
10. Define a content-quality bar. Sources below the bar are excluded — out-of-date pages with a "last updated three years ago" stamp, draft documents, internal scratchpads. A noisy corpus produces noisy answers regardless of how good the retriever is.
11. Pin the corpus owner. The retrieval pipeline cannot improve content the team does not own. If the content lives in someone else's system, the curation plan must include a working relationship with that team.

### Stage 3 — Ingestion pipeline

12. The ingestion pipeline takes the curated corpus and produces searchable artifacts. Design the pipeline as a sequence of named steps so each can be measured and re-run independently.
13. **Fetch.** A connector per source type — wiki API, document store, Git repository, database. Connectors record what they fetched, the source version, and the fetch timestamp.
14. **Normalise.** Convert each document to a canonical internal representation. Strip boilerplate (headers, footers, navigation). Preserve structure that matters (headings, tables, code blocks). Discard structure that does not (page styling).
15. **Chunk.** See Stage 4. Chunking is an explicit step, not a side effect of the embedder.
16. **Embed.** Pass the chunks through the embedding model. Record the model version, the dimensionality, and the chunk-to-embedding mapping. A re-embed is a full rebuild; the pipeline must support it.
17. **Index.** Write embeddings, chunk text, and metadata to the vector store and any keyword index. Maintain both: hybrid retrieval (dense plus keyword) outperforms pure-dense in most production settings.
18. **Verify.** A post-ingestion smoke test runs a fixed set of probe queries and asserts that the expected top-k chunks are returned. Without this step, a silent breakage in the pipeline is invisible until a user reports a bad answer.

### Stage 4 — Chunking strategy

19. Chunking is the single most underrated decision in RAG product design. Design the chunking strategy explicitly per source type, not globally.
20. **Default: structure-aware chunking.** Split on document structure (headings, list items, code blocks, table rows) rather than fixed token counts. A chunk is "one heading and its body up to the next heading of equal or higher level". This preserves the semantics of the source and means each chunk is independently meaningful.
21. **Fallback: sliding-window chunking.** For unstructured sources (long prose without headings, transcripts), use overlapping fixed-size chunks. Typical sizes: 400-800 tokens per chunk with 80-160 tokens of overlap. Smaller chunks are more precise but lose context; larger chunks are more contextful but bury the relevant span.
22. **Special case: tables.** Embed each table row as a chunk with the column headers prepended, or summarise the table into a paragraph and embed both. Embedding a whole table as a blob almost always retrieves nothing useful.
23. **Special case: code.** Embed by function or class, not by line. Include the docstring and the surrounding file context in the chunk metadata so the generation step has enough to reason about.
24. **Hierarchical retrieval.** For very long documents, store both leaf chunks (the searchable units) and parent chunks (the surrounding section). Retrieve at the leaf level for precision; expand to the parent for the generation step so the model has context.
25. Record the chunking strategy as a versioned configuration alongside the embedding model. A chunking change is a re-build, not a hot-swap; users who saw a previous answer based on the previous chunking will see different behaviour after the rebuild and the team should expect to re-baseline.

### Stage 5 — Retrieval evaluation

26. Evaluate retrieval *separately* from generation. If a wrong answer comes from a wrong retrieval, fixing the generation is wasted work. The eval must split the two.
27. Build a retrieval test set: a list of representative queries from `query_examples` and from production logs, each annotated with the set of chunks that should ideally be retrieved (the "gold passages").
28. Compute standard retrieval metrics: recall@k for the top one, three, and ten results; mean reciprocal rank; nDCG. Track each by slice — query category, source, length bucket, language.
29. Set a recall@5 gate. A common shape: at least eighty percent of evaluated queries must have at least one gold passage in the top five results. Tighten the gate as the corpus matures.
30. Evaluate the reranker (if any) separately from the retriever. The reranker's job is to take the top-k from the retriever and produce a better top-k'. Measure recall before and after rerank; the reranker is only justified if it moves recall@k' above the retriever's recall@k.
31. Probe the failure modes. Build a small set of "should not retrieve" queries — queries that are out of scope, malformed, or designed to elicit irrelevant chunks. Confirm the retriever ranks these low or that the system refuses to answer them. A retriever that confidently surfaces irrelevant content for any input is more dangerous than no retriever.

### Stage 6 — Generation pattern

32. The generation prompt takes the retrieved chunks and the user query and produces the answer. Pin the pattern.
33. **Faithfulness rule.** The generation prompt instructs the model to answer only from the retrieved context, to say "I do not have that information" when the context is insufficient, and to never invent details. Faithfulness is measured separately (see the eval-harness skill); the prompt is the first line of defence.
34. **Citation rule.** Every sentence or claim in the answer must be linked to the chunk it came from. The generation prompt asks the model to emit citations inline (e.g. `[1]`) and the system renders them as links. Unsourced claims are a generation bug, not a styling choice.
35. **Refusal rule.** If the retrieved context does not contain the answer, the model refuses with a short explanation and a path forward. The refusal is not a failure mode for the system; it is the system working as designed when the corpus is incomplete.
36. **Tone and length.** Pin both at the generation prompt. Most RAG systems suffer from over-long answers — the model summarises every retrieved chunk regardless of whether the user asked for that depth. Set explicit length caps per user intent.
37. **Structured output.** When the answer has a stable shape (a list of options, a comparison table, a definition), ask the model to emit structured output that the UI can render. Free text where structure exists is a missed opportunity.
38. **Conversation handling.** For conversational RAG, the retrieval step takes the *rewritten* question rather than the last user message. A separate small-model call rewrites the conversation into a standalone question, which becomes the retrieval input. Retrieval against raw chat turns drops badly.

### Stage 7 — Citations UX

39. Citations are the single highest-impact pattern for trust in a RAG product. Design them carefully.
40. Every citation links to the exact passage the model used, not to the top of the document. Users must be able to verify the claim in one click.
41. Citations are visible alongside the claim, not collected at the end. The user reading a sentence with a citation can see and click the source without losing context. End-collected citations are read by nobody.
42. The citation tooltip or preview shows the relevant excerpt before the user commits to a click-through. Most users do not need to read the full source; the preview is the lightweight verification.
43. When a sentence is unsupported (no chunk justifies it), the system either suppresses the sentence or flags it as "general knowledge" with a different visual treatment. Citations that link to chunks that do not actually contain the claim are worse than no citations.
44. Track citation-click rate as a product metric. A drop signals either users have lost trust in the citations (and stopped clicking) or have gained too much trust (and stopped verifying). Either is worth investigating.
45. For multi-document answers, show the source-tier mix. A user reading an answer composed half of tier-one product docs and half of community notes should be able to see that mix at a glance.

### Stage 8 — Freshness handling

46. Decide the freshness story per source from Stage 2 and reconcile against `freshness_requirement`.
47. Each source has an ingestion cadence — real-time webhook, scheduled batch, manual trigger. Pin the cadence per source and publish it in the system documentation so users know what to expect.
48. Each chunk carries a `last_updated` timestamp. The generation step is aware of the timestamp and can flag answers based on stale content.
49. For time-sensitive queries ("what is our current pricing"), the system surfaces the freshness of the supporting content prominently. A confident answer based on six-month-old pricing is a worse outcome than a hedged answer with the date.
50. Plan invalidation. When a source document is deleted or marked obsolete in the source system, the corresponding chunks are removed from the index within the SLA. A stale chunk that no longer has a source is a hallucination factory.
51. For freshness-critical use cases, build the "is this answer fresh enough" check into the generation pipeline. The generation prompt receives the freshness of the retrieved chunks and is instructed to decline answering when the chunks are older than a configurable threshold.

### Stage 9 — Content-gap mining

52. The most valuable signal in a RAG product is the queries it could not answer. Build the loop that turns those queries into corpus improvements.
53. Classify every production query into one of: "answered correctly" (judge score above threshold, user did not regenerate), "answered incorrectly" (judge score below threshold or negative user feedback), "refused due to scope" (the system declined because the corpus was insufficient), and "refused due to safety" (the system declined for policy reasons).
54. The "refused due to scope" bucket is the content gap. Cluster the queries by topic — a recurring cluster of refusals on the same topic is a content gap with a name.
55. Surface the clusters to the content owners on a regular cadence (weekly or biweekly). Each cluster becomes a candidate piece of content: title, scope, audience, priority based on query volume.
56. Track the closure. When the content owner publishes the new content, the system re-runs a held-out subset of the cluster's queries and confirms the answer rate improves. Without closure tracking, content-gap mining becomes a "interesting metrics" exercise that does not change the product.
57. The "answered incorrectly" bucket feeds the eval harness and the prompt-management strategy. The content-gap pipeline focuses on what the corpus is missing, not what the generation got wrong with existing content.
58. Beware privacy when mining queries. Queries can contain PII. The pipeline either redacts before storage or aggregates so that individual queries are not reviewable. Per-query review for content gaps requires reviewer eligibility and an audit trail.

### Stage 10 — Loop cadence and roles

59. The product loop is a recurring cadence. Pin who runs each step and on what schedule.
60. **Daily.** The ingestion pipeline runs (for daily-cadence sources). The smoke test runs. Production logs flow into the analytics pipeline.
61. **Weekly.** The retrieval eval runs on the full test set. The content-gap clusters are reviewed by content owners. The judge calibration drift is checked.
62. **Per release.** A new prompt version, a new chunking configuration, a new embedding model goes through the staged promotion pipeline from the prompt-management strategy.
63. **Quarterly.** The corpus curation is revisited — new sources considered, retired sources removed, trust tiers reassessed. The freshness SLAs are reviewed against actual fresh-arrivals.
64. **Roles.** Name the directly-responsible-individual for each piece: the corpus owner, the retrieval-pipeline owner, the generation-prompt owner, the eval owner, the content-gap pipeline owner. One person can hold multiple roles in a small team, but each role must have a name.

### Stage 11 — Failure-mode playbook

65. End the design with a short playbook of failure modes and the loop step that catches each.
66. **Wrong answer with confident citations.** Generation is confident, citations point to chunks that do not justify the claim. Caught by the faithfulness judge in the eval harness and by user feedback. Fix path: improve the faithfulness instruction in the prompt; tighten the citation-required rule.
67. **Right answer based on stale content.** Caught by the freshness check in generation and by user reports. Fix path: tighten ingestion cadence on the affected source; flag stale chunks.
68. **Confident hallucination on an out-of-scope query.** Caught by the refusal-correctness slice in the eval harness and by the "refused due to scope" classifier. Fix path: tighten the refusal instruction; add an out-of-scope detector before retrieval.
69. **Right retrieval but mangled generation.** Caught by the split-eval (retrieval-metrics fine, generation-metrics bad). Fix path: prompt iteration on the generation step; better structured output.
70. **Right generation but missed retrieval.** Caught by retrieval recall@k drop. Fix path: chunking changes, hybrid retrieval, reranker.
71. **Empty corpus on a hot topic.** Caught by content-gap mining. Fix path: content owner publishes; system re-evaluates.
72. **Drift after re-embed.** Caught by the smoke test and by retrieval-eval delta. Fix path: re-baseline; communicate to users if the change is user-visible.

## Outputs

The `loop_design` markdown contains, in order: the scope, the corpus curation, the ingestion pipeline, the chunking strategy, the retrieval evaluation, the generation pattern, the citations UX, the freshness handling, the content-gap mining, the loop cadence and roles, and the failure-mode playbook. The `loop_summary` JSON mirrors the same structure for tooling consumption.

## Examples

A help-centre RAG for a SaaS product lands with: in-scope answerable questions limited to product features and pricing, out-of-scope answers refused with a path to support; corpus is the public help centre as tier one, the internal engineering wiki as tier two; structure-aware chunking on the help centre and sliding-window on the wiki; retrieval evaluation against a hundred curated queries with recall@5 gate at eighty-five percent; generation prompt enforces citations and refusals; citations link to the exact help-centre anchor; ingestion is daily; content-gap mining clusters weekly with the docs team as owners.

An internal-wiki RAG for engineering knowledge lands with: in-scope answerable questions about architecture, runbooks, and team practices, out-of-scope answers about external services declined with a link to the vendor docs; corpus is the wiki, Git README files, and architecture decision records; hierarchical chunking on the wiki, function-level chunking on the code; retrieval eval against fifty engineer-curated queries; generation prompt enforces "answer only from internal context" and refuses on external-vendor questions; citations link to the wiki anchor or the Git permalink; ingestion is daily for the wiki and per-commit for the Git sources; content gaps surfaced to the engineering enablement team monthly.

## Limitations

The skill produces a product design, not the implementation. It does not select a vector database, an embedding model, or a reranker; those decisions are constrained by `stack_constraints` and by the retrieval-quality gates the design pins.

The skill assumes a corpus that the team can curate. RAG over a corpus the team does not control — the open web, a third-party customer-owned data store — has a constrained set of levers and needs an overlay specific to that situation.

The skill does not cover the security model in depth. Per-user document permissions, redaction of restricted content, and tenant isolation are explicit gates the loop must satisfy, but the implementation of those gates is the security team's domain. The design notes them as guardrails and refers out.

## Sources reviewed

- https://github.com/run-llama/llama_index
- https://github.com/langchain-ai/langchain
- https://github.com/deepset-ai/haystack
- https://github.com/explodinggradients/ragas
- https://github.com/langfuse/langfuse
- https://github.com/openai/openai-cookbook
- https://github.com/microsoft/generative-ai-for-beginners
- https://github.com/Shubhamsaboo/awesome-llm-apps
