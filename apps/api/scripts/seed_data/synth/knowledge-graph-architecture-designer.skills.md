---
id: skillsgit-curated/knowledge-graph-architecture-designer
version: 1.0.0
name: Knowledge Graph Architecture Designer
description: Design a knowledge graph for a domain — entity model, ontology-depth tradeoffs, source-of-truth strategy, ingestion patterns, schema evolution, query patterns, and governance.
authors:
  - name: Wave-5 Synth
    handle: wave5-data
    role: author
category: data
tags:
  - niche:knowledge-graph-architecture
  - knowledge-graph
  - ontology
  - rdf
  - property-graph
  - entity-model
  - schema-evolution
  - graph-governance
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
  - knowledge graph design
  - kg architecture
  - ontology design
  - entity model design
  - property graph schema
  - rdf schema
  - knowledge graph governance
  - graph ingestion pipeline
  - source of truth knowledge graph
  - schema evolution graph
  - linked data design
  - graph query patterns
example_invocations:
  - "Design a knowledge graph for our enterprise product catalog — entities, ontology depth, ingestion, and governance."
  - "We have data scattered across CRM, ERP, and docs. Plan a unified knowledge graph and its source-of-truth strategy."
  - "Pick between RDF and property graph for our compliance-evidence knowledge graph and justify the choice."
  - "Design schema evolution for a knowledge graph that has to absorb three new acquisitions next year."
inputs:
  - name: domain
    type: text
    required: true
    description: The business domain the knowledge graph will model — what it represents and who consumes it.
  - name: source_systems
    type: text
    required: false
    description: Existing systems whose data will flow into the graph — CRMs, ERPs, lakehouses, document stores, manual curation tools.
  - name: consumers
    type: text
    required: false
    description: Who and what consume the graph — analysts, applications, AI agents, search systems. Drives the query-pattern design.
  - name: ontology_appetite
    type: choice
    required: false
    description: How formal the ontology needs to be.
    choices: [light_taxonomy, structured_schema, formal_ontology, w3c_compliant]
  - name: scale
    type: text
    required: false
    description: Rough scale — node count, edge count, ingestion volume, query QPS.
  - name: governance_context
    type: text
    required: false
    description: Existing governance — data stewards, policy regimes, audit obligations, regulated industry constraints.
outputs:
  - name: kg_architecture
    type: markdown
    description: The end-to-end design — entity model, ontology, source-of-truth strategy, ingestion patterns, query patterns, schema evolution, and governance.
  - name: kg_summary
    type: json
    description: Structured summary with `entities`, `ontology_choice`, `source_of_truth`, `ingestion`, `query_patterns`, `evolution`, and `governance`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Knowledge Graph Architecture Designer

## When to use

Use this skill when a team is starting, refactoring, or rescuing a knowledge graph and needs an architecture document before any code lands. A knowledge graph is not "a Neo4j instance" or "a SPARQL endpoint" — it is a modelled body of facts about a domain, with a schema that constrains those facts, an ingestion process that keeps it accurate, a query surface that lets consumers extract value, and a governance regime that keeps it trustworthy. Each of those pieces is a design decision with consequences, and the consequences interact. This skill produces the design that names the decisions and reconciles them.

The skill is appropriate for product knowledge graphs, customer 360 graphs, compliance and evidence graphs, scientific and biomedical graphs, content metadata graphs, threat-intelligence graphs, supply-chain graphs, and the new generation of graphs that exist primarily to feed AI agents. It is less useful when the right answer is a relational warehouse and someone has misdiagnosed the problem as a graph problem — the first stage of this skill includes a graph-fit check to flag that case.

The skill is complementary to the graph-augmented RAG and semantic-search skills in this library, which design retrieval surfaces sitting on top of a graph. It is also complementary to the entity-resolution skill, which designs the upstream resolution pipeline whose output flows into the graph as canonical entities.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `domain` | yes | Anchors the entity model and ontology. |
| `source_systems` | no | Decides ingestion patterns and source-of-truth strategy. |
| `consumers` | no | Drives query-pattern design. |
| `ontology_appetite` | no | Calibrates depth versus pragmatism. |
| `scale` | no | Constrains storage and partitioning choices. |
| `governance_context` | no | Sets the policy and audit overlay. |

## How to apply

The design walks through twelve stages. Each stage produces a section of the deliverable. The output is an architecture document, not an implementation; engineering teams take the document and build against it.

### Stage 1 — Confirm the graph fit

1. Before the design begins, pin why a graph is the right shape. The signals are: the domain has rich, irregular, evolving relationships; queries traverse those relationships more than one hop deep; new relationship types appear faster than a relational schema can absorb; or the consumers explicitly need a graph (an AI agent reasoning over connections, a linked-data publishing obligation, a graph-native analytic).
2. The anti-signals are: the workload is overwhelmingly tabular aggregations; relationships are shallow and stable; the team has no operational appetite for a graph store; the data already lives cleanly in a warehouse and nobody is asking for graph queries. When the anti-signals dominate, write that conclusion and stop. The cheapest knowledge graph is the one that was never built.
3. From `domain` and `consumers`, write a short paragraph describing the *graph-shaped questions* the system has to answer. Examples: "show every product variant that shares a component with this recalled batch", "find every customer touched by every service that depends on this database", "explain why this claim is approved by walking from the policy node to the evidence nodes". If the team cannot write three such questions, return to Stage 1.

### Stage 2 — Choose the graph paradigm

4. Pick between a property graph and an RDF graph deliberately. The choice constrains tooling, talent, and integrability.
5. **Property graph.** Nodes and edges carry typed properties; there is no global identifier scheme by default; querying is via traversal languages (Cypher, Gremlin) that read like programming. Strengths: developer ergonomics, performant traversal at moderate scale, mature operational tooling. Weaknesses: weak schema, harder cross-graph federation, no native open-standard semantics.
6. **RDF graph.** Every fact is a `(subject, predicate, object)` triple with global URIs; querying is via SPARQL with set-oriented semantics; schemas are modelled in RDFS or OWL with formal entailment. Strengths: open standards, federation across organisations, formal reasoning, mature in regulated and scientific domains. Weaknesses: steeper learning curve, fewer modern developer tools, traversal performance can lag at very large scale.
7. **Hybrid.** A property graph for the operational store and an RDF projection for cross-organisation publishing, or vice versa. The hybrid is correct when both modes are required; it is wrong when the team picks it to defer the choice.
8. Reconcile with `ontology_appetite`. A `formal_ontology` or `w3c_compliant` appetite points strongly to RDF. A `light_taxonomy` appetite with a single operator and rapid iteration points to a property graph. Note the choice and the reasons before proceeding.

### Stage 3 — Entity model

9. The entity model is the list of node types in the graph and the properties each carries. Design the model from the domain outward, not from the source systems inward — source systems contain incidental modelling that should not leak into the graph.
10. List the core entity types. A useful test: a domain expert with no database experience should recognise every entity name and disagree with none. "Customer", "Product", "Component", "Policy", "Claim", "Evidence" pass the test. "DimCustomer_v3" does not.
11. For each entity, list the identity attributes — the properties that make two records refer to the same real-world thing. Identity is independent of the source-system primary key; an entity has identity even when no system has yet recorded it.
12. For each entity, list the descriptive attributes — properties that describe the entity but do not establish identity. Descriptive attributes are versionable and may carry source attribution.
13. Mark every entity with a stewardship owner. An entity without a steward is an entity whose data quality nobody is responsible for; the graph will degrade at that node type fastest.
14. Decide which entities have first-class identifiers (the canonical entity IRI or property-graph node key) and which are dependent — modelled as nodes for queryability but identified only through their relationship to a parent. The dependent pattern is correct for things like "an address belongs to this customer" or "a line item belongs to this order".

### Stage 4 — Relationship model

15. List the core relationship types. Edges are first-class in a knowledge graph — their semantics matter as much as the nodes.
16. Each relationship carries: a direction (or an explicit symmetry rule), a source and target type or set of allowed types, a cardinality constraint (one-to-one, one-to-many, many-to-many), and a list of properties (when the relationship has its own attributes — a start date, a confidence score, a source citation).
17. Decide whether the relationship is *asserted* (a fact directly stated by a source) or *inferred* (derived by a rule from other facts). Inferred relationships are materialised cautiously: when the inference rule changes, every materialised edge has to be reconsidered. Many regulated graphs forbid persisting inferred edges and recompute them at query time.
18. Pin the provenance model for each relationship type — which source(s) can assert it, what citation is recorded, what happens when two sources disagree. Edges without provenance turn the graph into a rumour mill.
19. Note relationships you considered and rejected. A short rejected-relationships list saves a future contributor from re-proposing them.

### Stage 5 — Ontology depth and reuse

20. Ontology depth is a sliding scale. Pin the team's position on it.
21. **Light taxonomy.** A flat list of types with no inheritance, no equivalence axioms, no formal constraints. Cheapest to build and run; weakest at supporting reasoning and integration.
22. **Structured schema.** Types organised in a small hierarchy with explicit property domains and ranges; cardinalities enforced at write time. Good middle ground for product engineering teams.
23. **Formal ontology.** A modelled domain with class hierarchies, equivalence and disjointness axioms, property characteristics (transitivity, symmetry), and constraints expressed in OWL or SHACL. Justified when the domain requires formal reasoning or external interoperability.
24. **Reuse existing ontologies** rather than minting your own when an established vocabulary covers part of the domain. Common candidates: SKOS for taxonomies and thesauri, FOAF and schema.org for people and organisations, Dublin Core for content metadata, PROV-O for provenance, BFO or DOLCE for upper-level structure in scientific domains, domain-specific ontologies in biomedicine, finance, and manufacturing. Reusing reduces modelling work and increases the chance of integrating with adjacent systems.
25. Where the existing vocabulary is close but not exact, extend rather than replace — define the new class as a subclass of the standard class with the extra constraints. This preserves federation while letting the domain be precise.
26. For property graphs, the ontology concept maps to a *schema* enforced by the application layer or a validation step. Even without a formal ontology language, the schema lives somewhere — pin where.

### Stage 6 — Identifier and IRI strategy

27. Identifiers are the durable currency of a knowledge graph. Design them before any data lands.
28. **Pattern.** Adopt one identifier pattern per entity type. Common patterns: a UUID minted at first sight; a hash of a normalised identity tuple; a stable IRI under a domain the organisation controls; a composite of a source-system prefix and the source primary key (use sparingly — see below).
29. **Source-system identifiers as IRIs are a trap.** They embed the source's lifecycle into the graph. When the source is replaced, every identifier breaks. Use source identifiers as *attributes* of the entity (`crmId`, `erpId`) but mint your own canonical identifier independent of any source.
30. **Resolved versus unresolved.** When entity resolution is part of the ingestion pipeline (see the entity-resolution skill), distinguish between a *raw observation* (a record from a source, identified by its source key) and a *resolved entity* (the canonical entity the observation maps to). The graph stores both and the edge between them.
31. **Persistence promise.** Document the IRI policy: identifiers are never reused, never silently merged without an audit trail, and any merge or split is itself a recorded event. A graph that quietly remaps identifiers is a graph whose downstream consumers cannot trust their bookmarks.
32. **External alignment.** For each entity type, decide whether to publish `sameAs` or `equivalent` links to external identifier systems (a vendor catalog ID, an industry registry, a standards-body ID). Alignment is the lever for federation, but it accumulates maintenance debt — each alignment is a relationship the team has promised to keep correct.

### Stage 7 — Source-of-truth strategy

33. A knowledge graph almost always pulls from multiple sources. Pin the rules for resolving conflicts.
34. **Per-property source of truth.** For each descriptive attribute on each entity type, name the single source whose value wins. The source-of-truth table is the most useful single artefact for downstream consumers — "where did this customer email come from".
35. **Tiered fallback.** When the primary source is silent for a particular entity, define the fallback order. Without an explicit order, the answer is "the last write wins", which is the same as "the answer is random".
36. **Stewardship overrides.** A human steward must be able to override the source-of-truth rule for a specific entity when the source is known to be wrong. Record the override with author, justification, and effective date so a future audit can reconstruct why the graph held that value.
37. **Conflict telemetry.** Even with a clear policy, conflicts surface signal — a property whose sources frequently disagree is a data-quality smell upstream. Emit a per-property conflict count to the data-quality dashboard.
38. **No silent merges.** When two sources both supply identity claims for the same entity and the entity resolution pipeline merges them, the merge is an event with an audit trail. Property values from the merged entities are reconciled by the source-of-truth rule, with the losing values preserved as historical attributes, not discarded.

### Stage 8 — Ingestion patterns

39. Design ingestion as a sequence of named, independently-measurable stages so each can be re-run.
40. **Connect.** A connector per source system. The connector records what it read, the source version or change cursor, and the read timestamp. For sources that emit change events, prefer event-driven ingestion; for sources that only support full extracts, schedule the extract and diff against the previous extract.
41. **Map.** Translate source records into graph fragments — a set of (node, edge, property) assertions. The mapping is the most opinion-heavy step and the one most likely to need iteration; keep it declarative and versioned.
42. **Validate.** Enforce schema constraints, identifier formats, cardinality rules, and any SHACL or application-level shape checks. Records that fail validation route to a quarantine, not the graph; quarantine has an owner and an SLA.
43. **Resolve.** Run identity resolution against the existing graph. New entities create new IRIs; matched entities update existing ones. The resolution result is itself a recorded event — which source record mapped to which canonical entity at which time.
44. **Merge.** Apply the source-of-truth rules to combine the incoming assertions with the existing graph. Property updates produce a property-history record; relationship changes produce an edge-history record.
45. **Index.** Update derived indexes — full-text indexes over entity labels, vector indexes over textual descriptions, materialised paths for hot query patterns. Indexes are downstream of the merge; the merge step does not block on index updates unless the query layer requires it.
46. **Audit.** Every stage emits structured events to the audit log: connector reads, validation failures, resolution decisions, merge outcomes. The audit log is a first-class artefact of the graph, not an operational nicety.

### Stage 9 — Query patterns

47. Map `consumers` to concrete query patterns. The query patterns drive index design, partitioning, and the choice of operational store.
48. **Lookup.** Find a specific entity by identifier or by an external key. Trivial in any store; the design lever is the secondary-index strategy.
49. **One-hop expansion.** Given an entity, return its directly-connected entities filtered by edge type and edge properties. The most common production pattern; storage and indexes must make it cheap.
50. **Multi-hop traversal.** Walk between two entities or accumulate properties across a path. The pattern that justifies a graph store. Pin the typical depth, the branching factor, and the time budget.
51. **Subgraph extraction.** Return a connected subgraph around a seed entity for downstream rendering (a UI graph view, an AI agent context). Bound the size at the query layer; an unbounded subgraph extraction is a denial-of-service waiting for a hub node.
52. **Analytic.** Run a graph-shape computation — community detection, centrality, shortest path, reachability — over the whole graph or a typed subgraph. Analytics typically run against a snapshot rather than the live store; pin the snapshot cadence.
53. **Question answering.** Translate a natural-language question into a graph query, return the answer with citations. Designed in detail in the graphrag-pipeline-architect skill; here, pin the patterns the question-answering layer is allowed to depend on.

### Stage 10 — Schema evolution

54. Plan how the schema changes without breaking consumers.
55. **Additive changes are free.** New node types, new optional properties, new edge types do not require migration. Document the addition; ship it.
56. **Renames are not free.** Renaming a property or relationship type requires a window during which both names are accepted, a migration of historical data, and a clear consumer cut-over. Avoid renames when an addition would suffice; when a rename is required, plan it explicitly with a deprecation deadline.
57. **Type narrowing.** Tightening a constraint (a cardinality, a required property, a type restriction) requires a backfill of non-conforming data first. The backfill is itself a project, not a side effect of the schema change.
58. **Splits and merges.** Splitting one entity type into two, or merging two into one, is the most invasive change. It requires a re-resolution pass, downstream notification, and almost always a versioned alias for a grace period.
59. **Versioning.** The schema itself is versioned. Consumers can pin to a schema version for an explicit support window. The window length is a policy decision; a year is generous, a quarter is the floor.
60. **Migration playbook.** For each evolution pattern, document the steps: write the schema change, write the backfill, run the backfill on a staging snapshot, verify, run on production, deprecate the old shape, remove. Without a playbook, evolution proposals stall and the schema gradually drifts away from the domain.

### Stage 11 — Governance, access control, and audit

61. A knowledge graph that nobody trusts is unused. Governance is the work of being trusted.
62. **Stewardship.** Pin a named steward per entity type. The steward signs off on schema changes, source additions, and source-of-truth rule changes affecting that entity. The steward is also the escalation path for data-quality issues.
63. **Access control.** Design the authorisation model at the entity level (which entities a principal can read), the property level (which properties on a readable entity are visible), and the relationship level (which edges out of a readable entity are visible). For regulated graphs, also require justification capture for sensitive reads.
64. **Multi-tenant isolation.** When the graph serves multiple customers or business units, decide between a single shared graph with per-tenant filtering and per-tenant graph instances. Shared graphs are cheaper but require iron-clad filtering at the query layer; per-tenant graphs are more operationally expensive but make accidental cross-tenant leakage harder.
65. **Provenance.** Every property and every edge carries a source citation. Provenance is queryable — a consumer can ask "why does the graph claim this" and receive the chain of sources and rules that produced the claim. PROV-O or a property-graph equivalent is the modelling target.
66. **Audit.** The audit log records reads of sensitive properties, all writes, all schema changes, all stewardship overrides, and all resolution merges and splits. Audit retention matches the regulatory regime in `governance_context` or defaults to one year minimum.
67. **Quality metrics.** Pin the dashboard: completeness (percentage of entities with required properties), freshness (median age of last-update per source), consistency (count of constraint violations by type), provenance coverage (percentage of edges with citation), conflict rate (per-property disagreement frequency). The dashboard is a steward's tool and a buyer's confidence signal.

### Stage 12 — Operational shape and roadmap

68. Close the design with the operational shape and a six-to-twelve-month roadmap.
69. **Operational shape.** Number of stores (single graph store, plus secondary stores for full-text or vectors, plus analytic snapshot store). Replication and backup story. Disaster-recovery RPO and RTO. On-call ownership.
70. **Sizing.** From `scale`, sketch storage and compute. A property graph at a hundred million nodes and a billion edges has very different operational shape from a billion nodes and ten billion edges; the sizing reveals which one this is.
71. **Roadmap.** Phase one is the entity and relationship model with one or two source systems wired in, no resolution, light governance. Phase two adds resolution, source-of-truth rules, and the first non-trivial consumer. Phase three layers analytics, query-pattern optimisation, and integration into AI agents. Phase four is consolidation — retiring legacy systems whose data now lives canonically in the graph. Pin which phase the team is starting in and what success looks like at the phase boundary.
72. **Exit criteria for the design.** The architecture document is done when a domain expert can read it and recognise the domain; an engineer can read it and start implementing without further questions; a steward can read it and accept the responsibilities it assigns; and a security reviewer can read it and approve the controls. If any of those four cannot, the design has gaps and the gaps are named explicitly as open questions.

## Outputs

The `kg_architecture` markdown contains the twelve stages in order. The `kg_summary` JSON mirrors the structure for tooling and review automation.

## Examples

A customer-360 knowledge graph for a mid-market SaaS company lands with: a property graph paradigm (developer ergonomics, single-team operator); entity model centred on Customer, Account, Contact, Subscription, Product, Event; an identifier strategy where Customer and Contact carry organisation-minted UUIDs and reference CRM and billing system IDs as attributes; per-property source of truth that names billing as canonical for plan and revenue, CRM as canonical for ownership and lifecycle stage; ingestion as event-driven for CRM and scheduled extract for billing; query patterns dominated by one-hop expansion from Account; light schema-evolution policy with quarterly review; stewardship owned by the revenue-operations team with the data platform team responsible for the pipeline.

A compliance and evidence knowledge graph for a regulated financial-services team lands with: an RDF paradigm with W3C-compliant publishing; an entity model aligned to a published regulatory ontology; structured schema with SHACL shapes enforcing required properties and cardinalities; per-property source of truth with stewardship overrides recorded in a tamper-evident log; ingestion staged through a validation gate that quarantines non-conforming records; query patterns mixing one-hop expansion (find evidence for a control) and multi-hop traversal (walk a control to the regulation it satisfies); strict access control with per-property visibility and justification capture; full PROV-O provenance on every edge; audit retention of seven years.

## Limitations

The skill produces an architecture document, not an operational deployment. It does not pick a specific graph database product, an embedding provider, or a particular SHACL engine; those decisions are constrained by the design but resolved by the engineering team in context.

The skill assumes the team has, or can acquire, at least one domain expert who can validate the entity model. A graph designed without a domain expert in the room models the source systems rather than the domain, and the resulting graph is a relational warehouse with a graph veneer.

The skill does not cover natural-language interfaces in depth. Question answering over the graph is mentioned as a query pattern but its detailed design lives in the graphrag-pipeline-architect skill in this library.

## Sources reviewed

- https://github.com/apache/jena (Apache-2.0)
- https://github.com/RDFLib/rdflib (BSD-3-Clause)
- https://github.com/dgraph-io/dgraph (Apache-2.0)
- https://github.com/vesoft-inc/nebula (Apache-2.0)
- https://github.com/kuzudb/kuzu (MIT)
- https://github.com/neo4j-labs/llm-graph-builder (Apache-2.0)
- https://github.com/microsoft/graphrag (MIT)
