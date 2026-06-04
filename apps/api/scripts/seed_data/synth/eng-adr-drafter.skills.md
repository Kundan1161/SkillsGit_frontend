---
id: skillsgit-curated/adr-drafter
version: 1.0.0
name: ADR Drafter
description: Turn a technical decision in progress into a structured Architecture Decision Record — context, decision, consequences, alternatives, trade-offs, and a Y-statement summary.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [adr, architecture, decision-record, documentation, design-doc, madr, trade-off-analysis]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  tools_optional: [web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - write an adr
  - draft an architecture decision record
  - document this decision
  - capture this trade-off
  - adr for
  - decision record
  - madr
  - architecture decision
  - record this choice
  - design decision doc
  - architectural choice writeup
  - y-statement
  - log this decision
  - turn this discussion into an adr
example_invocations:
  - "Turn this Slack thread into an ADR — we picked Postgres over DynamoDB for the catalog service."
  - "Draft an ADR for choosing protobuf gRPC over JSON-REST for internal service-to-service calls."
  - "We just settled on cursor pagination for the public API — write the decision record."
inputs:
  - name: decision_context
    type: text
    required: true
    description: Free-form description of the problem, the options on the table, what was chosen, and any side discussion (chat threads, meeting notes, design doc fragments).
  - name: decision_status
    type: choice
    required: false
    description: Where the decision is in its lifecycle. Defaults to "accepted" if the user implies a chosen option.
    choices: [proposed, accepted, rejected, deprecated, superseded]
  - name: adr_template
    type: choice
    required: false
    description: Which template flavor to emit. Defaults to MADR-style.
    choices: [madr, nygard, y-statement, long-form]
  - name: deciders
    type: text
    required: false
    description: Who owned the decision (names, roles, or "team"). Used in the metadata block.
  - name: linked_adrs
    type: text
    required: false
    description: Other ADRs this one supersedes, refines, or relates to. Free text or a list of slugs.
outputs:
  - name: adr_markdown
    type: markdown
    description: Final ADR in the requested template, ready to drop into the team's docs folder.
  - name: y_statement
    type: text
    description: One-sentence summary of the decision in the In-the-context-of / facing / we-chose / to-achieve / accepting form.
  - name: open_questions
    type: markdown
    description: Anything the input did not answer that the team should resolve before merging the ADR.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# ADR Drafter

## When to use

Use this skill the moment a team makes — or is about to make — a technical choice that future engineers will want to understand without rereading three months of chat. An Architecture Decision Record captures the "why" so reversing or revisiting a decision later is a deliberate act, not an archaeological one.

Common triggers:

- A thread closed with "OK, we're going with X" and nobody has written it down.
- A spike comparing two databases, two queue technologies, two languages, or two protocols, ended.
- A design review meeting needs a follow-up document.
- A previously written ADR needs to be superseded because the constraints changed.
- An onboarding hand-off needs a record of why the current shape exists.

Do not use this skill for:

- Day-to-day implementation choices that affect only one file or one PR. Capture those in code comments or PR descriptions.
- Product decisions ("should we build feature X"). Those belong in product specs, not ADRs.
- Pure technology surveys with no chosen outcome. ADRs are records of decisions, not literature reviews. If no decision was reached, mark the ADR `proposed` and list the choice as "deferred".

## Inputs

- `decision_context` (required) — Everything the user can dump in: chat transcript, bullet notes, a paragraph of free prose, partial design doc, links to benchmarks. The skill's job is to extract a structured record from messy input.
- `decision_status` — Indicates where the ADR sits. The lifecycle states this skill supports are:
  - `proposed` — drafted but not yet accepted; reviewers expected.
  - `accepted` — current law of the land.
  - `rejected` — explored and explicitly declined; useful so the same idea is not revisited blindly.
  - `deprecated` — was law, now sunset, but no replacement yet.
  - `superseded` — replaced by another ADR; the replacement is linked.
- `adr_template` — Output flavor. Available styles described below in step 6.
- `deciders` — Names or roles. Used in the metadata header.
- `linked_adrs` — Slugs or titles of related records. The drafter inserts cross-links in a "Relationships" section.

## How to apply

This is a structured extraction-and-writing task. Apply the steps in order. Where information is missing from the input, write a placeholder enclosed in `<TODO: ...>` and surface those placeholders in the `open_questions` output rather than guessing facts.

### 1. Read the raw input twice

1.1. First pass: identify the **decision sentence**. The decision sentence is the smallest sentence that tells a future reader what was chosen, e.g. "We will use PostgreSQL with logical replication for the catalog service." If there is no clear decision sentence, the input is not yet ADR-ready — return an `open_questions` block asking the user to pick.

1.2. Second pass: harvest the supporting material into five buckets — `context` (why we had to decide), `forces` (constraints, trade-offs in tension), `options considered` (each with pros/cons), `consequences` (positive and negative), and `references` (links, benchmarks, prior art).

1.3. If the input is a chat transcript, strip social noise (greetings, emojis, scheduling chatter) but keep technical claims and counter-claims. Track who made which technical claim; this becomes part of the deciders block when names are clear.

### 2. Write the title

2.1. The title is a short noun phrase that names the decision, not a question and not a sentence. Good: "Use PostgreSQL for catalog persistence". Bad: "Should we use PostgreSQL?" or "We decided to use PostgreSQL".

2.2. Use present-tense imperatives that read as the team's policy: "Adopt cursor-based pagination", "Standardize on JWT for service-to-service auth". This phrasing carries forward to the slug and the filename.

2.3. Compute a kebab-case slug from the title. Prepend the ADR number if one was supplied: `0007-use-postgresql-for-catalog-persistence.md`. If the user did not give a number, suggest the next sequential number based on `linked_adrs`.

### 3. Decide the status block

3.1. Default to `accepted` if the input contains decision verbs in past tense ("we chose", "we are going with") or first-person plural future ("we will use").

3.2. Use `proposed` when the input contains hedges ("leaning toward", "tentative") or when the deciders list is incomplete.

3.3. Use `superseded` if `linked_adrs` includes a record this one replaces, and add the supersession cross-reference to the linked ADR too (note it in `open_questions` as a follow-up action).

3.4. Always include the decision date. If the input gives a date, use it; otherwise use today's date and note "date inferred from drafting day" in the metadata.

### 4. Write the Context section

4.1. Lead with the **problem statement** in one or two sentences. Avoid jargon that is not defined elsewhere in the doc or by linked ADRs.

4.2. Describe the **forces** — the competing pressures the decision must balance. Useful forces to surface: latency budgets, cost ceilings, team familiarity, operational maturity, compliance constraints, vendor lock-in tolerance, migration cost, expected growth curve.

4.3. State the **scope and non-scope** explicitly. A common ADR failure is sliding from the small decision actually made into adjacent claims; an explicit non-scope sentence prevents that.

4.4. Quote any hard constraints verbatim from the input ("must support EU data residency", "must respond in under 100 ms at p99"). Do not paraphrase constraints — paraphrasing constraints is how scope creeps in revision.

### 5. Write the Decision section

5.1. State the decision in one sentence. This is the same sentence harvested in step 1.1, polished.

5.2. Add a paragraph naming the **mechanism** — the specific technology, version, pattern, or shape chosen. "PostgreSQL 16 with logical replication and pgvector" is mechanism; "a relational database" is not.

5.3. State the **rationale** in three or four bullets that map back to the forces. Each bullet should connect a force to a property of the chosen option. If a force has no corresponding rationale bullet, ask why — it is either irrelevant (drop the force) or unaddressed (add it to consequences).

5.4. Resist the urge to write the decision as a sales pitch. ADRs are most useful to future readers when they read like a fair-minded analysis with a chosen winner, not like marketing copy.

### 6. Write the Options Considered section

6.1. For each option, give: a one-line description, two to four pros, two to four cons, and the reason it was not chosen (or, for the chosen option, why it won the tie-break).

6.2. Use a consistent table or bullet structure across all options. The reader will compare them side by side; asymmetric depth obscures the comparison.

6.3. Include a "do nothing" or "status quo" option whenever the decision could plausibly be deferred. Many ADRs benefit from naming inaction as a real alternative.

6.4. Cite benchmarks and external sources by URL. Do not write claims like "everyone knows X is faster"; either link to a measurement or downgrade the claim to "the team's experience suggests".

6.5. Watch for "straw-man options" — alternatives written so weakly they exist only to make the chosen option look strong. If an option's cons read as a caricature, either flesh it out fairly or remove it.

### 7. Write the Consequences section

7.1. Split into **positive consequences** and **negative consequences**. Both lists must exist; if the negative list is empty, the decision is not honest yet.

7.2. Positive consequences are the things this decision unlocks — capabilities, simplifications, performance headroom, reduced risk in a specific area.

7.3. Negative consequences are the costs incurred — new operational complexity, a skill gap, a vendor relationship, a migration cost, a coupling that did not exist before, a class of bugs newly possible.

7.4. Distinguish **immediate consequences** (within this sprint) from **long-tail consequences** (will be felt in six to twenty-four months). Future readers care most about long-tail consequences they may be living with.

7.5. Where possible, name the **owner** of each consequence. "The on-call team will inherit logical-replication lag monitoring" is more actionable than "monitoring will be required".

### 8. Add the Y-statement

8.1. Compose a one-sentence summary in this form:

> In the context of `<situation>`, facing `<concern>`, we decided for `<option>` and against `<rejected options>`, to achieve `<quality>`, accepting `<downside>`.

8.2. The Y-statement is a compression test. If you cannot write one without rewriting the Context section, the decision is too broad — split it into two ADRs.

8.3. Include the Y-statement in the body and also surface it as the separate `y_statement` output for use in indexes and search.

### 9. Add Relationships and Links

9.1. List ADRs this decision supersedes, is superseded by, refines, or relates to. Use slugs and link relative paths if a docs structure is known.

9.2. Link the design doc, spike branch, benchmark write-up, vendor evaluation, or ticket that prompted the decision. ADRs without external links are usually missing evidence.

9.3. If the decision touches an API contract, link the relevant OpenAPI/proto/GraphQL file. If the decision touches a service boundary, link the relevant module or system-context diagram.

### 10. Add Compliance, Security, and Cost callouts (when relevant)

10.1. If the decision affects data residency, retention, encryption, or access logging, add a Compliance subsection naming the specific regimes (GDPR, HIPAA, PCI-DSS, SOC 2 control) and how the chosen option satisfies them.

10.2. If the decision changes the attack surface, name the new surface and the controls put in place. "Adopting JWT for service-to-service auth" must explain key management, rotation, and the failure mode when a key is leaked.

10.3. If the decision creates a recurring cost, include an order-of-magnitude estimate and the assumptions behind it.

### 11. Validate the draft against an internal checklist

Before emitting, run through:

- Title is a noun phrase that names the decision.
- Status is set and consistent with the decision verbs in the body.
- Date is present.
- Deciders are named (or "team" with a follow-up to identify by name).
- Context section names the forces and the scope.
- Decision section is one sentence plus rationale tied to forces.
- At least two alternatives are seriously considered (status quo counts).
- Both positive and negative consequences are listed.
- A Y-statement compresses the decision into one sentence.
- Every external claim has a link or is downgraded to team judgment.
- No personally identifiable information beyond names of deciders.
- No secrets in any linked URLs or pasted snippets.

If any check fails, fix it or surface it in `open_questions`.

### 12. Emit in the chosen template

12.1. **MADR style (default)** — Markdown Architectural Decision Records. Sections, in order: title with ADR number, metadata block (status, date, deciders, consulted, informed), Context and Problem Statement, Decision Drivers, Considered Options, Decision Outcome, Consequences, Confirmation, More Information.

12.2. **Nygard short style** — The classical compact form. Sections: Title, Status, Context, Decision, Consequences. No options section; treat as a record of the chosen path with consequences only. Useful for internal teams allergic to long documents.

12.3. **Y-statement style** — A near-one-page ADR whose center is the Y-statement, expanded with three to five bullet points of context and three to five of consequences. Useful for teams adopting ADRs for the first time who balk at long forms.

12.4. **Long-form style** — Adds Compliance, Security, Cost, Migration plan, and Validation plan subsections. Useful for decisions with regulatory or financial weight.

12.5. Whichever style is emitted, keep the Y-statement somewhere in the document for indexing.

### Decision rules and heuristics

- **One decision per ADR.** When the input contains two coupled decisions (e.g. "use Postgres and switch to gRPC"), split into two ADRs and add a Relationship link.
- **Past-tense for decisions, present-tense for consequences.** "We decided to adopt X. The system now requires Y."
- **Don't argue with the deciders.** If the rationale in the input is thin or you disagree with the choice, write the ADR fairly and surface gaps in `open_questions` — the ADR records what the team chose, not what an AI thinks.
- **Prefer concrete over abstract.** "Postgres 16" not "an RDBMS". "p99 < 100 ms" not "fast enough".
- **No anonymous "they".** Replace ambient pronouns with specific actors when possible ("the platform team owns rotation").
- **Length is not a quality signal.** A two-page ADR that captures the decision and its consequences beats a six-page one that buries them.
- **Keep wins humble.** Avoid superlatives ("the perfect solution"). The future reader will not believe them.
- **Make negative consequences as crisp as positive ones.** ADRs that hide the costs lose authority.

### Edge cases

- **The decision was a non-decision.** When the input shows the team chose to defer, that is still a recordable decision: status `proposed` with a clear "we will revisit when X" trigger condition. Future-you will thank you for the marker.
- **The decision overturns an earlier one.** Mark this ADR `accepted` and the earlier ADR `superseded`. Add a Relationship link in both directions and include a one-line explanation of what changed in the world.
- **The decision is conditional.** "We use Postgres unless data residency in jurisdiction X is required, in which case we use Y." Capture the condition explicitly in the Decision section; do not bury it in Consequences.
- **The decision spans multiple teams.** Name each team and its responsibility. Do not write a cross-team ADR signed by one team only.
- **The input is contradictory.** When the chat transcript shows two deciders saying different things, do not synthesize a phantom agreement. Surface the contradiction in `open_questions` and leave the ADR as `proposed`.
- **The input contains secrets or PII.** Strip them before drafting. Replace tokens or hostnames with `<redacted>` and note the redaction in the metadata.

## Outputs

- `adr_markdown` — The fully drafted ADR ready to commit to a docs folder. Filename suggestion is the slug from step 2.3.
- `y_statement` — The single-sentence summary suitable for an ADR index or search tool.
- `open_questions` — A markdown list of items the team still owes the document. Each item has a one-line description and, where possible, the section it would fix.

## Examples

### Worked example

Input:

> Slack thread: We've been going back and forth on storage for the new catalog service. Postgres has been our default for the last five years and everyone knows it. DynamoDB came up because the read pattern is mostly point reads by SKU and we expected hot keys. Did a spike — Postgres on RDS with pgvector and a primary-replica setup hit 12 ms p99 at our test load, which is plenty. DynamoDB needs a careful partition-key design and the team has no production DynamoDB experience. Cost about the same up to ten million items. We're going with Postgres. Alex and Priya were on the call; Jamie was async.

Expected output (MADR style, abbreviated):

```
# ADR 0007: Use PostgreSQL for catalog persistence

- Status: Accepted
- Date: 2026-05-14
- Deciders: Alex, Priya (Jamie consulted async)

## Context and Problem Statement
The catalog service needs durable storage for SKU-keyed product data with a read-heavy
access pattern dominated by point lookups by SKU. We need to commit to a primary store
before we generate client SDKs and write the migration playbook.

## Decision Drivers
- Read-heavy point-lookup workload by SKU
- p99 latency budget of 50 ms end-to-end (storage budget ~20 ms)
- Team operational familiarity (five years on Postgres, zero on DynamoDB)
- Risk of hot keys at scale
- Total cost of ownership at the ten-million-item horizon

## Considered Options
1. PostgreSQL on RDS with read replicas and pgvector
2. DynamoDB with carefully chosen partition keys
3. Status quo / defer (not viable; the service has no store)

## Decision Outcome
Chosen option: PostgreSQL on RDS with read replicas and pgvector.

### Rationale
- Spike hit 12 ms p99 at test load, well inside the storage budget.
- Team has deep operational experience; no new on-call training required.
- Cost parity with DynamoDB up to ten million items.
- pgvector keeps embedding-based recommendations on the same store.

## Consequences

### Positive
- Reuse of existing backup, monitoring, and runbook tooling.
- Embeddings live with the catalog, simplifying recommendation queries.

### Negative
- Vertical-scale ceiling on the primary requires a planned re-shard at the
  fifty-million-item horizon — owner: platform team.
- Logical replication lag becomes a new SLO; needs a dashboard.

## Y-statement
In the context of the new catalog service, facing a read-heavy point-lookup workload
with a tight p99 budget and zero team experience on DynamoDB, we chose Postgres on RDS
with pgvector over DynamoDB to achieve fast operational onboarding and to keep
embeddings co-located, accepting a future re-shard at the fifty-million-item horizon.

## More Information
- Spike write-up: <link>
- Catalog service design doc: <link>
```

`y_statement` output is the single sentence pulled out of that section.

`open_questions` example output:

```
- Confirm Jamie's async sign-off and add to Deciders.
- Pick a specific Postgres version (suggest 16) and add to the Decision section.
- Define the lag SLO (proposed: < 5 s replication lag at p95) before this ADR ships.
```

## Limitations

- The skill drafts ADRs from the information you give it. Missing rationale becomes `<TODO>` placeholders — the skill does not invent justifications.
- It assumes a single decision per record. Coupled decisions are split, which can produce two short ADRs instead of one if the user expected a longer document.
- It writes neutrally; teams that prefer a more opinionated voice can post-edit.
- It does not yet auto-update related ADRs (e.g. setting an earlier ADR to `superseded`); that step is surfaced in `open_questions`.

## Sources reviewed

- https://github.com/adr/madr
- https://github.com/thomvaill/log4brains
- https://github.com/structurizr/structurizr
- https://github.com/backstage/backstage
- https://github.com/ContextMapper/context-mapper-dsl
- https://github.com/simskij/awesome-software-architecture
- https://github.com/OAI/OpenAPI-Specification
