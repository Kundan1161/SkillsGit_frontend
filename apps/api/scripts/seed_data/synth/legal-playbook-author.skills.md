---
id: skillsgit-curated/legal-playbook-author
version: 1.0.0
name: Negotiator Playbook Author
description: Translate a clause library into a working negotiator playbook — per-clause want/accept/refuse positions, supporting arguments, counterparty objections, red flags, and escalation triggers.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: legal
tags: [niche:contract-clause-library, playbook, negotiation, fallback-ladder, red-flags, escalation, contract-ops, deal-desk]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: [file_io]
  min_context_tokens: 64000
  estimated_tokens_per_invocation: 14000
trigger_keywords:
  - write a negotiator playbook
  - clause playbook authoring
  - want accept refuse positions
  - negotiation arguments per clause
  - red flag triggers
  - escalation rules
  - convert clause library to playbook
  - playbook per clause
  - fallback rationale
  - counterparty objection responses
example_invocations:
  - "Convert our clause library into a negotiator playbook the deal desk can actually use."
  - "Author the playbook entries for our top ten most-negotiated clauses with arguments and red flags."
  - "Draft a per-clause want/accept/refuse playbook with escalation triggers we can hand to junior counsel."
inputs:
  - name: clause_register
    type: json
    required: true
    description: The clause register (taxonomy + position metadata) produced by the clause-library-architect skill or equivalent. Each entry must include clause_id, topic, sub_topic, risk_tier, applies_to_doc_types, owner_role.
  - name: positions_per_clause
    type: json
    required: false
    description: If positions are already authored, the existing preferred / fallback / walk-away values. If absent, the skill produces placeholder positions and explicitly flags them for owner authoring.
  - name: audience
    type: choice
    required: false
    description: Who will read and use the playbook day-to-day. Calibrates depth and vocabulary.
    choices: [contracts_team_only, deal_desk_and_sales_counsel, sales_self_serve, mixed]
  - name: house_voice
    type: text
    required: false
    description: Short description of the company's institutional tone (e.g., "plain-language, direct, no hedging"). Used so playbook copy reads like a single author wrote it.
outputs:
  - name: playbook_md
    type: markdown
    description: Per-clause playbook entries with want/accept/refuse positions, supporting arguments, common counterparty objections and responses, red-flag triggers, escalation rules. Indexed by clause_id with a navigable table of contents.
  - name: playbook_json
    type: json
    description: Machine-readable playbook for CLM ingestion — clause_id, want, accept (ladder), refuse, arguments[], counterparty_objections[], red_flags[], escalation_trigger, owner_role, last_reviewed.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Negotiator Playbook Author

## When to use

**Mandatory legal disclaimer.** This skill produces methodology guidance only. Clause-library decisions affect contractual liability. Every output must be reviewed by qualified counsel before incorporation into any agreement. The skill does not provide legal advice and use does not create an attorney-client relationship.

Use this skill when a clause library has been designed (the architecture exists, taxonomy is settled, owners are named, positions per clause are either written or stubbed) and the next step is to turn the library into a working artefact that a reviewer can read at the moment of negotiation and act on without escalation. A clause library tells you *what* the company's position is; a negotiator playbook tells you *how to defend it, when to bend, and when to walk*. The two artefacts share a register but serve different readers.

Typical triggers: a clause library has been authored and the deal desk is still escalating clauses that the library covers, because nobody can tell from the library entry alone what arguments to make or what objections to expect; a head of legal needs to ramp three new contract managers in a quarter and cannot do it by shadowing; a sales-counsel team has been working from a senior lawyer's mental playbook and that lawyer is about to leave; a CLM rollout requires structured playbook content to power inline guidance during redline.

It is also appropriate when an organisation wants to expose lightweight playbook content to non-lawyer reviewers (deal desk, customer success, sales operations) for the small number of clauses they can resolve without legal involvement. The playbook is the surface through which the library reaches the front line.

The skill is not appropriate without an existing clause library or register — a playbook authored against no library produces inconsistent positions that drift from the templates. It is also not appropriate as a substitute for live counsel involvement on tier-one clauses; the playbook can route to the right escalation, not replace the escalation.

## How to apply

A playbook entry per clause is a small, dense, opinionated document. The reviewer reads it under time pressure with a customer on the other side of the table. Every word that does not help the reviewer make a decision should be cut. Build each entry as a fixed-template document so reviewers learn the structure once and find the right section instantly.

1. **Audit the input register before authoring.** Walk the `clause_register` and verify each entry has the metadata the playbook depends on: clause_id, topic, sub_topic, risk_tier, applies_to_doc_types, owner_role. Any clause missing risk_tier or owner_role is unwriteable — flag and stop. Authoring a playbook entry against a malformed library entry produces guidance that cannot be maintained.

2. **Adopt a single per-clause template, and use it everywhere.** A reviewer who learns the template once should find the same section in the same place in every entry. The template has eight blocks: a one-sentence summary of what this clause governs; the *want* (the company's preferred position, restated in plain language); the *accept* (the fallback ladder, each step labelled with its trigger); the *refuse* (the walk-away floor and the reason it is a floor); the *arguments* (the affirmative case the company makes for the preferred position); the *counterparty objections* (the specific pushbacks the company hears and the company's response to each); the *red flags* (signals in the counterparty's redline that mean stop and escalate immediately); the *escalation* (who to contact, when, with what context).

3. **State the *want* in plain commercial language, not in legal mechanism.** A reviewer rushed for time needs to know "we want our liability capped at twelve months of fees with carve-outs for IP, confidentiality, and security breach" — not a paragraph translating the underlying drafting mechanism. The library entry holds the precise position; the playbook entry holds the actionable summary. If the playbook entry is twice as long as the library entry, the playbook is doing too much.

4. **Number the fallback ladder, do not just list it.** Each ladder step gets an explicit ordinal — step one, step two, step three, walk-away. The ordinal tells the reviewer how much room is left. "We are at step two of the ladder; one more move and we are at the floor" is a sentence the reviewer should be able to form quickly. Each step is paired with its trigger — what does the counterparty have to do or say for this step to be available? "If counterparty rejects step one citing standard policy, offer step two" is a usable trigger; "if it feels right, offer step two" is not.

5. **Author affirmative arguments before defensive ones.** For each clause, write the two or three reasons the company holds its preferred position. These are the talking points for the opening of the negotiation, not the comebacks. Frame them in terms the counterparty cares about — risk symmetry, regulatory exposure, operational reality — not in terms of "this is our standard." A reviewer who can articulate three reasons for the position closes more clauses without escalation than a reviewer who can only assert the position.

6. **Catalogue the predictable objections.** For each clause, what does the counterparty actually say when pushing back? This is the section that pays the rent — the reviewer's hardest moment is hearing an objection she has not heard before. Aim for the three to five most common objections per high-leverage clause. For each, write a one-paragraph response that begins by acknowledging the legitimate concern (most common objections have a real reason behind them) and then proposes the company's path forward. Generic responses ("our position is firm here") fail; specific responses ("we appreciate the concern about uncapped tail risk; that is exactly why we carve out IP indemnity from the cap rather than removing the cap entirely") succeed.

7. **Define red flags explicitly.** A red flag is a signal in the counterparty's text or behaviour that means *stop negotiating and escalate now*. Examples in this category (not language to use, just signal classes): a counterparty replacing the company's mutual indemnity with a one-way indemnity that runs only against the company; a counterparty removing the consequential damages waiver entirely; a counterparty redirecting jurisdiction to a forum the company has no nexus to; a counterparty adding a most-favoured-customer pricing clause not previously discussed; a counterparty removing termination rights in entirety. Red flags are not severities; they are stop-work triggers. A reviewer hitting a red flag stops the redline and escalates within one business day.

8. **Make escalation routable, not aspirational.** Each entry names the escalation contact by role (not by name — names change; roles are stable). Each entry states the maximum response time for the first escalation (usually one business day during active negotiation) and the format of the escalation packet (the redline section, the counterparty's argument, the reviewer's recommendation). Vague escalation paths ("escalate to legal") are equivalent to no escalation path.

9. **Calibrate depth by audience.** From the `audience` input, modulate the entry. For a contracts-team-only audience, deeper legal reasoning is appropriate; the entries can reference doctrinal concepts the reader is presumed to understand. For a deal-desk-and-sales-counsel audience, lean on commercial framing and avoid jargon where possible. For a sales-self-serve audience (limited to a small set of tier-three clauses with safe defaults), entries are extremely short and effectively binary — "you can accept this change if X; otherwise escalate." Authoring a single playbook to serve all audiences uniformly will fail every audience.

10. **Voice consistency matters more than legal sophistication.** A playbook in three different voices reads like three different organisations' rules. Adopt the `house_voice` brief if present, or default to: plain-language, direct, second-person, no hedging. Phrases like "may, depending on the deal context, in certain circumstances" are quiet hedges that make a playbook useless. Either the company will accept the change or it will not; if the answer is conditional, the conditions are stated in the trigger.

11. **Anchor each entry to the library version.** Every entry carries the library version it was authored against and a last-reviewed date. When the library changes, the playbook entries derived from changed clauses are flagged stale and re-authored. A playbook entry referencing a clause version no longer in the library is worse than no entry — it tells the reviewer to defend a position that has been superseded.

12. **Stress-test with a counterparty scenario.** Before declaring an entry complete, run the entry against a realistic counterparty redline scenario. Does the entry tell the reviewer what to do? If the reviewer would still need to ask a question after reading the entry, that question's answer belongs in the entry. The acid test is "could a competent contract manager who joined six weeks ago resolve this clause with this entry alone?"

13. **Layer in argument depth for tier-one clauses only.** Tier-one clauses (high-stakes risk allocation, IP, data) deserve longer entries with multiple objection-response pairs and detailed arguments. Tier-two clauses receive a shorter entry. Tier-three clauses may merit only a two-line guidance block ("accept as-is; if the counterparty proposes to add X, escalate"). A uniform-depth playbook bloats the tier-three entries and starves the tier-one entries.

14. **Cross-link clauses that interact.** Some clauses cannot be negotiated independently: the limitation-of-liability cap interacts with the indemnification cap; the data-protection obligations interact with the security exhibit; the IP-ownership clause interacts with the licence-back clause. Each entry that depends on or affects another names the related entries explicitly so the reviewer sees the interaction. A package of three related concessions read separately is dangerous; read as a package, it is a recoverable trade.

15. **Build the navigation up front.** The playbook is an indexed reference document. Each entry is anchorable by clause_id. A table of contents grouped by topic and risk tier sits at the top. A risk-tier-one index page lists the dozen clauses a reviewer in a fast-moving negotiation needs to reach without scrolling. A glossary of recurring terms (in-house jargon, key defined terms) sits at the back. Reviewers spend more time finding the right entry than reading it; navigation is product, not packaging.

16. **Surface unknowns honestly.** When a clause's position is stubbed in the register and not yet authored, the playbook entry says so explicitly — "position pending owner authoring; escalate to the named owner for any deviation." A blank entry is acceptable; a fabricated entry is not.

17. **Plan the maintenance loop.** Each entry carries a review cadence (typically every six to twelve months for tier-one entries, twelve to twenty-four months for tier-two, opportunistic for tier-three) and an event-driven re-author trigger (regulatory change, repeated deviation pattern, change in the underlying library clause). The playbook is a living document; an entry that has not been reviewed in three years should be quarantined and flagged for re-author before it is relied on in a deal.

## Inputs

- `clause_register` (required, JSON) — the library register produced by the architect skill. Each entry must include clause_id, topic, sub_topic, risk_tier, applies_to_doc_types, owner_role.
- `positions_per_clause` (optional, JSON) — pre-authored positions per clause. If absent, the playbook stubs the position fields and flags them for owner authoring.
- `audience` (optional, choice) — contracts_team_only / deal_desk_and_sales_counsel / sales_self_serve / mixed. Calibrates entry depth.
- `house_voice` (optional, text) — institutional tone brief for voice consistency across entries.

## Outputs

- `playbook_md` (markdown) — navigable per-clause entries with want / accept (ladder) / refuse / arguments / counterparty objections / red flags / escalation. Includes a table of contents and a tier-one quick-index.
- `playbook_json` (JSON) — machine-readable per-clause objects for CLM ingestion or downstream tooling.

## Examples

### Example 1 — high-risk clause for a deal-desk audience

**Input clause_register entry:** `{"clause_id": "RA-LOL", "topic": "risk_allocation", "sub_topic": "limitation_of_liability", "risk_tier": 1, "applies_to_doc_types": ["msa", "saas"], "owner_role": "commercial_counsel_director"}`

**Playbook entry output (excerpt):**

> **Summary.** Governs the cap on what each side can owe the other when something goes wrong.
>
> **Want.** Twelve months of fees, with the standard four carve-outs: indemnification obligations, breach of confidentiality, breach of security obligations, willful misconduct.
>
> **Accept (ladder).** Step one: twelve months with three carve-outs (drop willful misconduct as separate; it remains implicit). Step two: nine months with the four carve-outs. Walk-away: anything below six months of fees, or any version without the indemnification carve-out, or any version that excludes data-security-breach from the carve-outs on a deal involving personal data.
>
> **Refuse.** Walk-away as above.
>
> **Arguments.** The cap exists to bound predictable commercial exposure, not unpredictable catastrophic exposure. The carve-outs ensure that the categories of harm the company cannot recover commercially from — third-party IP claims, customer data loss — sit outside the cap. A counterparty that wants a three-month cap is asking the company to absorb risk it has no commercial mechanism to price.
>
> **Counterparty objections.**
> - "Our policy is fees paid in the prior twelve months, not payable." *Response:* the cap should reflect the value at risk during the agreement, not the timing of payments. If the counterparty insists, fall to step two and tighten the carve-outs.
> - "Carve-outs swallow the cap." *Response:* the carve-outs are bounded categories, not open-ended. Each is itself usually capped at the indemnity cap if separately negotiated.
>
> **Red flags.** Counterparty removes the indemnification carve-out. Counterparty proposes a one-way cap. Counterparty caps confidentiality breach explicitly. Any of these — escalate now.
>
> **Escalation.** Commercial counsel director, one business day. Packet: counterparty's text, our position from the library, the specific carve-out being challenged.

### Example 2 — tier-three clause for a self-serve audience

**Playbook entry output (excerpt):**

> **Summary.** Governs the order-of-precedence between the main agreement and the order form.
>
> **Want.** Main agreement controls except where the order form is expressly inconsistent.
>
> **Accept.** Counterparty edits limited to clarifying that pricing in the order form controls — accept.
>
> **Refuse.** Counterparty edits that make the order form supersede the main agreement entirely. Escalate.
>
> **Escalation.** Sales counsel, one business day.

## Limitations

- **Not legal advice.** Playbook entries are reviewer-aid artefacts. Every entry presumes qualified counsel owns the underlying position and is reachable for escalation.
- **Library-dependent.** The playbook is only as good as the clause register it derives from. A poorly-tiered library produces a misshapen playbook.
- **Maintenance overhead.** A playbook un-refreshed for eighteen months silently misleads reviewers. The skill outputs a maintenance schedule, but the schedule must be staffed.
- **Audience drift.** A playbook authored for sales-self-serve cannot be safely repurposed for contracts-team use without re-authoring; the depth and vocabulary differ.
- **Counterparty diversity.** Predictable counterparty objections are predictable only across a typical population. Unusual counterparties (governments, regulated entities, certain non-US jurisdictions) generate objections the playbook will not cover and that require live counsel.
- **No drafting language.** The playbook directs the reviewer to the position; it does not provide drop-in clause text. Clause text lives in the templated library and is owned by the position owner.

## Sources reviewed

Methodology informed by public references on contract playbook construction and clause libraries. Industry standardised agreement libraries (CC BY 4.0) and a public engineering-culture handbook section (CC BY-SA 4.0) were consulted at the structural level — three-position framework, fallback ladders, escalation patterns. No clause text or source-specific objection-response language was copied or close-paraphrased.

- https://bonterms.com/ (CC BY 4.0 — methodology only)
- https://commonpaper.com/ (CC BY 4.0 — methodology only)
- https://handbook.gitlab.com/handbook/legal/ (CC BY-SA 4.0 — handbook structure only)
- https://www.contractken.com/post/contract-playbook-guide (industry reference)
- https://contractnerds.com/creating-a-useful-contract-playbook/ (industry reference)
- https://www.pactly.com/blog/creating-contract-negotiation-playbooks (industry reference)
- https://www.spellbook.legal/learn/contract-playbook-example-template (industry reference)
- https://github.com/accordproject/template-archive (Apache-2.0 — clause structure patterns)
