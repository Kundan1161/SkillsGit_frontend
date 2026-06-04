---
id: skillsgit-curated/blog-post-architect
version: 1.0.0
name: Blog Post Architect
description: Given a topic, audience, and objective, plan and draft a research-backed blog post with target keywords, outline, supporting points, examples, and a calibrated call-to-action.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [copywriting, content, blog, seo, editorial, longform, outline, draft]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - blog post
  - article
  - longform
  - outline
  - draft
  - editorial brief
  - content brief
  - thought leadership
  - pillar page
  - SEO article
  - explainer
  - listicle
  - how-to post
  - comparison post
example_invocations:
  - "Draft a 1800-word blog post on multi-region database failover for senior backend engineers."
  - "Write a beginner-friendly explainer on retrieval-augmented generation for a developer marketing blog."
  - "Plan a pillar page about vendor risk management aimed at compliance leads at mid-market SaaS companies."
  - "Outline and draft a comparison post between event-driven and request-response architectures."
inputs:
  - name: topic
    type: text
    required: true
    description: The subject of the post, ideally narrowed (e.g., "queueing patterns for at-least-once delivery" rather than "queues").
  - name: audience
    type: text
    required: true
    description: Who reads this — role, seniority, sophistication, and the publication or context it appears in.
  - name: objective
    type: choice
    required: true
    description: Why the post exists.
    choices: [educate, rank, convert, position, recruit, announce]
  - name: target_length_words
    type: number
    required: false
    description: Target word count for the draft. Defaults to a length appropriate to format (800 for opinion, 1500 for explainer, 2500 for pillar).
  - name: format
    type: choice
    required: false
    description: The article archetype to follow.
    choices: [explainer, how-to, listicle, comparison, opinion, case-study, pillar, announcement]
  - name: primary_keyword
    type: text
    required: false
    description: The lead search phrase if the post is search-driven.
  - name: must_include
    type: text
    required: false
    description: Sources, products, customer quotes, internal pages, or claims the writer wants present.
outputs:
  - name: editorial_brief
    type: markdown
    description: A structured plan covering positioning, search intent, outline, evidence inventory, and CTA logic.
  - name: full_draft
    type: markdown
    description: Publish-ready draft with headline options, deck, body, pull quotes, and CTA.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Blog Post Architect

## When to use

Invoke this skill when a marketer, founder, or editor needs to move from a topic prompt to a finished article in a single working session and wants both the plan and the draft. It fits cases where the writer already knows the audience and outcome but has not yet decided angle, structure, or claim hierarchy. Typical signals: the user supplies a working title and a publication target; the user mentions a keyword or a competing article they want to outrank; the user pastes a customer interview and asks for a teardown post; the user says "write a long version" of an existing tweet or LinkedIn thread; the user provides a product launch context and wants a corresponding article to accompany the release.

Avoid this skill when the task is a short social post (use a social copy skill), a sales email (use an outreach skill), or a landing page (use the landing page copywriter). Also skip when the user wants pure information retrieval without authoring; this skill always produces an article-shaped artifact, not a Q&A.

## How to apply

1. **Read the request twice before writing anything.** First pass, identify the three required inputs: topic narrowness, audience precision, and objective. Second pass, list any constraints the user named (length, must-include sources, banned topics, deadline-relevant tone).
2. **Convert "objective" into a publication contract.** If the objective is *educate*, success is comprehension and shareability. If *rank*, success is search coverage of the head term and its long-tail. If *convert*, success is a measurable downstream action and the body must support the call. If *position*, success is a distinctive claim the audience would not have made on their own. If *recruit*, success is making the reader picture themselves in the role. If *announce*, success is clarity and reach. Name the contract explicitly in the brief; the rest of the work flows from it.
3. **Resolve the angle.** A topic is not an angle. State the angle as a single declarative sentence the writer is willing to defend (e.g., not "queues" but "most teams over-engineer queueing because they confuse delivery guarantees with retry policy"). If the user did not specify, propose two or three candidate angles tied to audience pain and pick the strongest with a one-line rationale.
4. **Locate the reader on a sophistication ladder.** For each audience, write down what they already know, what they think they know but is wrong, and what they have not yet encountered. The article's job is to move them one rung. The intro acknowledges rung N, the body installs rung N+1, the close hints at rung N+2.
5. **Choose the archetype.** The format constraint forces structural decisions. *Explainer* opens with a question and answers it; the body builds a model. *How-to* opens with the outcome and gives ordered steps with checkpoints. *Listicle* leads with a count and a promise; each entry is independently valuable. *Comparison* opens with the decision the reader is making and ends with a recommendation grounded in trade-offs. *Opinion* opens with a stake-in-the-ground; the body defends it. *Case study* opens with the protagonist and stakes; the body narrates the arc. *Pillar* opens with the field map and links outward to component pieces. *Announcement* opens with what changed and why it matters.
6. **Decide search intent only if the objective is rank.** Map the primary keyword to the SERP archetype currently winning (informational, navigational, transactional, commercial-investigation). Do not fight the SERP format — if every top result is a listicle, the article will struggle to rank as an opinion piece. If the keyword's intent contradicts the user's chosen archetype, surface the conflict and offer to either change format or pick a sibling keyword.
7. **Build a topic graph.** Write the angle in the center. Branch out three to seven supporting claims. Under each claim, list evidence types: data points, examples, anecdotes, quotes, screenshots, code snippets, or analogies. Mark each evidence slot as *have*, *need-to-fetch*, or *need-from-user*. This graph becomes the outline scaffold and the gap list.
8. **Draft the outline.** Headings must be parallel in form and complete in scope. For a how-to, every H2 is an imperative verb phrase. For a listicle, every H2 is a noun phrase of the same shape. For a comparison, the H2s are the dimensions, not the contenders. Add a one-sentence intent under each H2 stating what the section must accomplish, not what it will contain.
9. **Engineer the hook.** Reject "In today's world…" openings. Prefer one of: a counterintuitive fact, a named reader scenario, a recent event with a clear consequence, a question the audience cannot answer comfortably, or a one-sentence story whose protagonist is the reader. Test the hook against the angle: if you could swap the hook into a different article, it is not strong enough.
10. **Write a deck.** The deck is the one or two sentences under the headline that tells the reader what they will learn and why to keep reading. It is a contract; the body must honor it. Drafting the deck before the body forces the writer to commit to scope.
11. **Generate three to five headline options.** Vary by formula: number-led ("Seven failure modes of…"), question-led ("What does it cost to…"), benefit-led ("Cut your build time in half by…"), curiosity-led ("The mistake every team makes with…"), and direct ("A guide to…"). Note for each which audience segment it best targets. Recommend one with rationale.
12. **Draft section by section.** Lead each section with the section's claim, then provide the evidence, then a one-line implication. Do not bury the claim; the section is not a mystery novel. Move on once the implication is clear.
13. **Vary sentence rhythm.** Mix one short declarative every three to five sentences. Read each paragraph aloud silently — if the cadence is monotonous, break a sentence in two or merge two into a longer one.
14. **Insert concrete anchors every 150–250 words.** Concrete anchors are numbers, named entities, code, dialogue, diagrams, or sensory detail. Abstract paragraphs without anchors lose readers regardless of how true they are.
15. **Earn each claim.** Every nontrivial assertion needs evidence, an example, or a citation. If you have none, soften the claim ("often," "in our experience") or remove it.
16. **Engineer transitions.** A good transition links forward, not backward — it tells the reader why the next section matters given what they just read. Avoid "Now that we have covered X…" in favor of a connecting question or a logical "but."
17. **Write the conclusion as a payoff, not a recap.** The conclusion should give the reader something they could not have inferred from the rest of the article: a synthesis, a next step, a question that reframes the topic, or a checklist they can act on tomorrow.
18. **Calibrate the CTA to the objective.** Educate → newsletter or related post. Rank → internal link to a conversion page. Convert → a single bold CTA tied to the article's frame. Position → no CTA, or a soft "what do you think?" prompt. Recruit → role link with a sentence on what excites the writer about the team. Announce → docs, demo, or signup. One CTA per article is the rule; two is the exception; three signals indecision.
19. **Run a structural audit.** Read only the headlines and first sentence of each section. Does that skim make sense as a coherent argument? If not, reorder or rewrite the topic sentences. A reader who skims should still get value; a reader who reads should get more.
20. **Run a claim audit.** List every numeric or quantitative claim. For each, mark its source. Remove or attribute anything you cannot ground.
21. **Run a jargon audit.** Circle every acronym and term-of-art on first use; either define it inline (eight words or fewer) or replace it. Replace where the audience is junior; define where they are senior but in an adjacent specialty; leave undefined only when the audience is the term's home community.
22. **Run a passive-voice audit.** Identify passive constructions; convert to active unless the actor is unknown or genuinely less important than the action.
23. **Run a credit audit.** If the article uses someone's framework, data, or argument, name them. Uncredited borrowing is the fastest way to lose authority with the very practitioners the writer is trying to reach.
24. **Add metadata.** Slug, meta title (≤60 chars including brand), meta description (≤155 chars, contains the primary phrase, ends in an implicit CTA), suggested OG image concept (one sentence), and three to seven internal link recommendations to existing pages.
25. **Add 2-3 pull quotes.** Pull quotes are the article's elevator pitches. Pick lines that stand alone and convey the angle. They double as social copy.
26. **Estimate reading time.** Assume 230 words per minute; round to the nearest minute. Place it under the deck.
27. **Produce a publication checklist.** Image alt text written, footnotes resolved, internal links checked, author bio attached, canonical tag set, tracking parameters on outbound CTAs, social preview verified.
28. **Return both artifacts.** First, the editorial brief (so a reviewer can sign off on direction before publishing). Second, the full draft (so the writer can publish or revise immediately).

## Inputs

- `topic` — the subject in one sentence; narrower is better.
- `audience` — role, seniority, sophistication, and reading context.
- `objective` — educate, rank, convert, position, recruit, or announce.
- `target_length_words` (optional) — the target draft length.
- `format` (optional) — explainer, how-to, listicle, comparison, opinion, case-study, pillar, announcement.
- `primary_keyword` (optional) — supply only when the objective is rank.
- `must_include` (optional) — sources, quotes, screenshots, or claims to weave in.

## Outputs

- An editorial brief: angle, contract, outline, evidence inventory, hook draft, headline options, CTA plan.
- A full draft: headline + deck + body + pull quotes + conclusion + CTA + metadata + publication checklist.

Both outputs are markdown; the draft includes inline `// note:` comments where the writer should swap in proprietary data, customer names, or screenshots.

## Examples

**Example 1: Explainer for a developer audience.**

*Input* — topic: "what changed in the consensus protocol when our database moved from single-leader to raft-based replication"; audience: senior backend engineers evaluating a migration; objective: educate; format: explainer; length: 2000.

*Output sketch* — Angle: "Raft did not buy us more durability; it bought us simpler operational reasoning." Outline: (1) The single-leader era and what its failure modes actually were; (2) Raft as a model — terms, log indices, commit rules, in plain prose with one diagram; (3) The first thing that surprised the team after rollout (operational, not academic); (4) Where Raft does not help (cross-region writes, large-state snapshots); (5) Reading list and an implicit "if you are considering this migration, here's what we wish we had known." CTA: link to the engineering blog index, not a sales page, because the objective is educate.

**Example 2: Comparison aimed at ranking.**

*Input* — topic: "event-driven vs. request-response for internal services"; audience: tech leads at series-B startups; objective: rank; primary_keyword: "event driven vs request response"; format: comparison.

*Output sketch* — Outline by dimension: coupling, observability, ordering, replay, debugging, team coordination, cost. Recommendation section calls out three deciding questions (how often do you need to add a consumer; how much do you care about ordered, exactly-once semantics; how distributed is your team). Headline option recommended: "Event-driven vs. request-response: seven trade-offs that should decide it" (number-led, contains keyword, promises specificity). Internal link plan: three to four links to architecture reference pages and a "talk to an architect" CTA page.

**Example 3: Conversion-focused post for marketers.**

*Input* — topic: "the hidden cost of running a marketing campaign without a measurement plan"; audience: head-of-marketing at $20M-$100M ARR companies; objective: convert (book-a-demo); format: opinion; length: 1200.

*Output sketch* — Hook: a one-paragraph scenario of a CMO presenting numbers they cannot defend. Body: three claims, each with a customer-quote pull-out (placeholder for the brand to fill). Close: a one-sentence reframe ("measurement is not a step in your campaign; it is the campaign's contract with itself") and a single-button CTA to a teardown service. Internal link to a public case study.

## Limitations

- The skill cannot pull live SERP data; if search intent calibration matters (objective=rank), the writer should supply current SERP screenshots or notes.
- The skill cannot fabricate proprietary metrics. Claims that require a number the company does not publish will be marked with `// need-from-user` and left for human fill-in.
- The skill assumes the audience speaks English; multilingual adaptation requires a follow-up pass.
- Citations to academic papers or specific books are not auto-fetched; if the writer wants page-cite-level accuracy, attach the sources directly and ask for inline references.
- The skill follows generally accepted editorial norms; it does not enforce a specific publication's house style. For house style fidelity, provide a style guide excerpt and re-prompt for a style pass.
- Legal or regulated copy (medical, financial advice, securities disclosures) must be reviewed by qualified counsel; the skill flags but does not vet such claims.

## Sources reviewed

- https://github.com/f/awesome-chatgpt-prompts
- https://github.com/langgptai/awesome-claude-prompts
- https://github.com/aminblm/awesome-chatgpt-content-creation-prompts
- https://github.com/Blazity/next-saas-starter
- https://github.com/PaulleDemon/awesome-landing-pages
- https://github.com/Adrinlol/landy-react-template
- https://github.com/sendwithus/templates
