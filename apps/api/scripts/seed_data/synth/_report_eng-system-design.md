# Engineering — System Design & Architecture: Synthesis Report

**Date:** 2026-05-14
**Author agent:** methodology-synthesis (engineering / system design & architecture)
**Skills produced:** 3

## Files produced

- `eng-api-design-reviewer.skills.md` — API Design Reviewer ($99 one-time)
- `eng-adr-drafter.skills.md` — ADR Drafter ($7/mo subscription with support)
- `eng-service-decomposition.skills.md` — Service Decomposition Advisor ($11/mo subscription with support)

## Source candidates evaluated and outcome

### Accepted (allowed license, ≥100 stars, commit within 18 months from 2026-05-14)

| Repo | License | Stars | Last push | Used in |
|---|---|---|---|---|
| OAI/OpenAPI-Specification | Apache-2.0 | 30.9k | recent | API Design Reviewer, ADR Drafter |
| stoplightio/spectral | Apache-2.0 | 3.1k | 2026-05-12 | API Design Reviewer |
| github/rest-api-description | MIT | 1.6k | 2026-05-14 | API Design Reviewer |
| paypal/paypal-rest-api-specifications | Apache-2.0 | 393 | 2026-04-07 | API Design Reviewer |
| mingrammer/diagrams | MIT | 42.3k | recent | API Design Reviewer, Service Decomposition |
| structurizr/structurizr | Apache-2.0 | 192 | 2026-05-14 | all three |
| ContextMapper/context-mapper-dsl | Apache-2.0 | 257 | 2025-07-08 | API Design Reviewer, ADR Drafter, Service Decomposition |
| adr/madr | MIT or CC0-1.0 | 2.2k | 2026-04-17 | all three |
| thomvaill/log4brains | Apache-2.0 | 1.5k | 2024-12-17 | ADR Drafter, Service Decomposition (within 18-month limit by ~1 month) |
| backstage/backstage | Apache-2.0 | 33.3k | recent | ADR Drafter, Service Decomposition |
| simskij/awesome-software-architecture | CC0-1.0 | 2.8k | 2026-04-19 | ADR Drafter, Service Decomposition |

CC0-1.0 was treated as equivalent to Unlicense (public-domain dedication). It is functionally as permissive as the listed allowed licenses.

### Rejected candidates and reasons

| Repo | Reason |
|---|---|
| joelparkerhenderson/architecture-decision-record | CC BY-NC-SA 4.0 — NonCommercial clause disqualifies |
| donnemartin/system-design-primer | CC BY 4.0 (not on allowed list) |
| zalando/restful-api-guidelines | CC BY 4.0 (not on allowed list) |
| microsoft/api-guidelines | CC BY 4.0 (not on allowed list) |
| interagent/http-api-design (Heroku) | CC BY 3.0 plus last push 2024-01-16 (~28 months stale) |
| arc42/arc42-template | CC BY-SA 4.0 (ShareAlike clause; not on allowed list) |
| ddd-crew/bounded-context-canvas | CC BY-SA 4.0 |
| ddd-crew/context-mapping | CC BY-SA 4.0 |
| ddd-by-examples/library | MIT but last push 2023-07-07 (~34 months stale) |
| kgrzybek/modular-monolith-with-ddd | MIT but last push 2024-06-04 (~23 months stale, exceeds 18-month rule) |
| microservices-patterns/ftgo-application | NOASSERTION at API; could not confirm a permissive license cleanly |
| pmerson/ADR-template | MIT, only 90 stars (under 100 threshold), last push 2023-10-21 (stale) |
| socialsoftware/mono2micro | MIT, only 11 stars (under threshold) |
| Azure/azure-api-style-guide | MIT but only 55 stars (under threshold) |
| stoplightio/spectral-owasp-ruleset | No license declared (effectively all rights reserved) |
| json-api/json-api | CC0-1.0 / 7.7k stars — eligible, but not directly cited to avoid over-loading API skill with format-spec sources |
| OpenAPI rate-limiting discussions, AWS docs | Not GitHub-source-of-truth; informational only, not cited |

## Methodology patterns identified

Across the surveyed material, several recurring patterns emerged. The skills synthesize these into their step lists and heuristics rather than copying any single project's prose.

### API design patterns (informing the API Design Reviewer)
- Style-guide-as-code: Spectral-style lint rules pattern. API style is enforceable, not merely advisory.
- Hierarchical resource modeling with collection/item pairing.
- HTTP method semantics tied to safety/idempotency: GET/PUT/DELETE idempotent; POST not.
- Versioning is a single, global strategy — not mixed per endpoint.
- Standardized error envelope, with RFC 7807 / 9457 problem details as common reference.
- Pagination must be round-trippable; cursor pagination favored for large/streaming data, offset only for small bounded sets.
- Idempotency-Key header pattern for unsafe operations with replay safety.
- Rate-limit headers (RFC 9331 / X-RateLimit family) as a documented client contract.
- Consistent casing/naming across paths, parameters, headers, body fields.
- Schema discipline: named schemas, explicit nullable/required, examples validate against schemas.

### ADR patterns (informing the ADR Drafter)
- MADR template structure: title, status, context, drivers, options, decision, consequences.
- Nygard short form: Title/Status/Context/Decision/Consequences.
- Y-statement as compression test for a decision.
- Status lifecycle: proposed → accepted → deprecated / superseded.
- One decision per ADR; coupled decisions split into linked ADRs.
- Relationships between ADRs (supersedes / refines / relates to).
- Linking external evidence (benchmarks, design docs) is mandatory for non-trivial decisions.
- Both positive and negative consequences must be listed; absence of negatives is suspect.
- ADRs sit in source control alongside the code they govern.
- Tooling pattern (log4brains, Structurizr): ADRs render to a navigable web view from the markdown source.

### Service decomposition patterns (informing the Service Decomposition Advisor)
- Bounded contexts as the primary unit of decomposition (DDD strategic design).
- Context relationship taxonomy: shared kernel, customer-supplier, conformist, anti-corruption layer, open host service, published language, partnership, separate ways.
- Change-together / fail-together / conversation-together heuristics as boundary signals.
- Strangler fig migration pattern with explicit phases: facade → shadow → ramp → cutover → retire.
- Data ownership: one table, one owner; cross-context reads via API, never direct SQL.
- Saga / process manager for cross-context transactions.
- Conway's law alignment between team topology and service boundaries.
- Modular-monolith-first as a respectable destination when extraction risk is high.
- Operational tax: distributed tracing, service discovery, on-call coverage, runbooks before the cut-over.

## Synthesis decisions

- **No verbatim copying.** All step text, heuristic phrasing, and example output is original. Where standard vocabulary exists (HTTP methods, RFC numbers, context-mapping vocabulary, MADR status values), the terminology is used because it is industry-standard, but no source's phrasing is reused.
- **No trademarked methodology names** beyond plain-English category labels (no "Microservices Patterns" book content, no Zalando-named rule packs, no IBM Mono2Micro algorithms reused).
- **5–8 sources per skill**, all cited URL-only at the bottom of each file.
- **Cross-pollination across sources is the point.** No skill wraps a single repo's approach. For example, the ADR Drafter blends MADR template structure, Y-statement compression, Nygard short form, and log4brains' lifecycle handling into one decision pipeline.
- **Pricing follows the cuts suggested in the brief**: $99 one-time for the high-reference-value API audit; $7 and $11 monthly subscriptions for the recurring decision-record and decomposition tools.
- **License rule conservatism.** CC-BY and CC-BY-SA were treated as outside the allowed list despite being widely permissive in practice. CC0 was treated as inside because it is a public-domain dedication.

## Confidence per skill

- **API Design Reviewer — high.** Eight strong sources, well-established methodology, the rule set is industry-standard. Spec maps closely to existing tooling (Spectral). Output format is concrete and verifiable.
- **ADR Drafter — high.** Seven sources, templates are public and well-codified (MADR), no contested methodology choices. The Y-statement piece is well-grounded. Skill should produce immediately usable docs.
- **Service Decomposition Advisor — medium-high.** Seven sources. The skill is necessarily more judgment-laden than the other two because real decomposition depends on system-specific facts the agent cannot inspect. The skill compensates by being explicit about its limitations and by recommending conservative paths (modular monolith first, single small extraction, kill switches per phase). Lower confidence than the other two because the surveyed open-source repos that survived the license filter were thinner here — the most popular DDD/decomposition repos failed either license or staleness checks. The skill leans on the surviving repos plus widely standardized vocabulary.

## Anything skipped

- The original brief allowed for an optional third skill; it is included.
- No "system design interview" skill was synthesized because the highest-quality candidate (donnemartin/system-design-primer) is CC BY 4.0 and falls outside the allowed-license set.
- C4-model-specific tooling skills (e.g. a Structurizr DSL generator) were considered but set aside; that's a narrower craft skill better suited to a future area pass focused on diagramming.
- No event-driven architecture / async messaging skill produced in this pass; that area would need its own source survey (Kafka patterns, AsyncAPI, CloudEvents) and is a candidate for a follow-up.
