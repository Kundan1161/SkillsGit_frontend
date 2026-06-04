---
id: skillsgit-curated/prioritization-frame-picker
version: 1.0.0
name: Prioritization Frame Picker
description: Recommend the right prioritization framework for the situation — RICE, value/effort, opportunity scoring, MoSCoW, or ICE — then run it on a candidate list and produce a ranked output with the reasoning visible.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: productivity
tags: [niche:product-management, prioritization, rice, moscow, ice, value-effort, opportunity-scoring, roadmap]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  min_context_tokens: 16000
  estimated_tokens_per_invocation: 4500
trigger_keywords:
  - prioritize features
  - prioritization framework
  - RICE
  - MoSCoW
  - ICE
  - value vs effort
  - opportunity scoring
  - rank backlog
  - roadmap prioritization
  - which framework
  - how should I prioritize
example_invocations:
  - "I have a list of 14 candidate features. Recommend a prioritization frame and rank them."
  - "Should I use RICE or MoSCoW for our Q3 planning? Here's the context."
  - "Run value/effort on this list and flag anything where the inputs are too soft to trust."
  - "We're prioritizing customer-requested improvements. Pick the right frame and produce a ranked output."
inputs:
  - name: candidates
    type: text
    required: true
    description: The list of items to prioritize. Each item can be a sentence or a small block. Names, descriptions, and any quantitative inputs the asker already has (reach numbers, effort estimates, customer count) are welcome.
  - name: context
    type: text
    required: true
    description: A description of the situation — the team's stage, the time horizon, what kind of decision the prioritization is feeding (annual planning, a sprint, a board meeting), the audience, and any constraints on the output.
  - name: known_metrics
    type: text
    required: false
    description: Any numbers the asker already trusts — recent reach figures, conversion rates, customer counts, effort estimates from engineering, a confidence score from a discovery process. Reduces guesswork.
  - name: forced_framework
    type: choice
    required: false
    description: Override the recommendation and force a specific framework. Use only when the asker has a strong reason; the skill will still note where the choice is suboptimal.
    choices: [rice, value-effort, opportunity-scoring, moscow, ice, weighted-shortest-job-first, kano]
outputs:
  - name: recommendation
    type: markdown
    description: The framework recommendation with rationale, plus the alternative frames considered and why they were not chosen.
  - name: ranked_list
    type: markdown
    description: The ranked candidates with all scoring inputs visible, the calculated score, and a one-sentence justification per item.
  - name: reliability_notes
    type: markdown
    description: An honest read on where the inputs are weak, which rankings are likely to flip with better data, and the top three things to learn before committing.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Prioritization Frame Picker

## When to use

Use this skill when someone has a list of candidate things to do and needs to put them in order before a planning conversation, a roadmap update, or a build decision. The "candidates" can be features, bugs, experiments, customer requests, technical investments, or any mix. The output is twofold: a recommendation of *which* prioritization framework to use, and a *ranked output* against that framework with every input visible.

Engage when the candidate list is between three and roughly thirty items. Below three, the frame-picking exercise costs more than the prioritization itself; just decide. Above thirty, the asker is doing two jobs at once — cluster first into themes, then prioritize within. Suggest that pre-step if you see a flood of items.

Decline or push back when:

- The asker has already decided what to build and is looking for justification. Prioritization frameworks reveal preferences; they do not launder them. If the answer is predetermined, the skill will surface that as a tell.
- The list is a mix of incomparable items — "rewrite the auth service" alongside "tweak the homepage copy." Recommend splitting into roadmap-grade items and tactical items, then prioritizing each list separately.
- The asker wants a single "winner" but the context is one where multiple bets are obviously needed. Many teams need three or four items, not one. Push back on framings that force unnecessary tournament play.
- The asker is in a regulated context where prioritization must follow a documented process (legal hold lists, security backlogs). The skill is the wrong tool for those — the process itself is the answer.

The skill is at its best when the asker has soft inputs and is trying to convert them into a decision they can defend. The hidden value is not the rank — it's the *visible reasoning* that lets the team challenge the inputs in the next conversation.

## How to apply

Run the methodology in five phases.

### Phase 1 — Read the context and pick the framework

1. **Read `context` first, then `candidates`, then `known_metrics`.** The order matters; context determines which framework is appropriate. Read candidates before scoring so you know what kind of items you are dealing with.
2. **Pick the framework using the decision tree below.** Each branch lists the conditions for choosing the frame.
   - **RICE (reach × impact × confidence / effort)** when items have differentiated reach (some affect 100 users, others 100,000), effort estimates exist or can be roughed in, and the asker wants a number-driven comparison. Best for product backlog work in stable teams.
   - **Value/effort (or value-vs-cost 2×2)** when reach is similar across items (a fixed user base) or when the asker is early and ranking by gut. The 2×2 surfaces quick wins, strategic bets, fill-ins, and time-sinks. Best for early-stage teams or for a fast first cut.
   - **Opportunity scoring** when the asker has importance and satisfaction data per *user need* from a survey or interview series. Best when discovery has produced importance/satisfaction pairs.
   - **MoSCoW (must, should, could, won't)** when scope must fit a fixed deadline (a launch date, a regulatory cutoff) and the question is "what makes the cut." Best for release planning and statement-of-work scoping.
   - **ICE (impact × confidence × ease)** when items are experiments rather than features, and effort is small and roughly comparable. Best for growth and experimentation backlogs.
   - **Weighted-shortest-job-first (WSJF)** when the asker is operating in a SAFe-style program and needs cost-of-delay reasoning. Best for portfolio-level program increments.
   - **Kano** when items are about user satisfaction relative to expectations (must-be, performance, delight). Best when the question is which improvements move loyalty, not which ship next quarter.
3. **Document the choice.** Write one paragraph that names the framework, why it fits, and what other framework you considered and rejected. Transparency about the choice is more valuable than the choice itself.
4. **Respect `forced_framework` if supplied.** Use the chosen frame, but in the recommendation section note where the forced frame is a poor fit and where the result will be brittle.

### Phase 2 — Prepare the inputs honestly

5. **For RICE:** for each item estimate *reach* (number of users per time period — explicit time window matters), *impact* on a 0.25 / 0.5 / 1 / 2 / 3 scale per the canonical Intercom variant or a 1–10 scale (pick one and use it consistently), *confidence* as a percentage that triangulates research, instrumentation, and conviction, and *effort* in person-weeks or person-months (be consistent). Where a number is a guess, mark it `(guess)` and lower confidence.
6. **For value/effort:** assign each item to a value bucket (low, medium, high, very high) and an effort bucket (small, medium, large, very large). Resist sliding into fake precision — the 2×2 works because the buckets are coarse.
7. **For opportunity scoring:** each item is a *user need* with an importance score (0–10) and a satisfaction score (0–10). Opportunity = importance + max(importance − satisfaction, 0). Without importance/satisfaction data, switch frames; the skill will note this.
8. **For MoSCoW:** each item gets a single tag (must, should, could, won't-this-cycle). A must is something whose absence makes the release fail to meet its goal; a should is high-value but cuttable; a could is nice-to-have; a won't is explicitly out of scope for this cycle. Force "won't" entries — a MoSCoW with no won't list is incomplete.
9. **For ICE:** impact 1–10, confidence 1–10, ease 1–10. Each on the same scale; the score is the product. Ease is the inverse of effort and works because experiments are small.
10. **For WSJF:** cost of delay (user-business value + time criticality + risk-reduction / opportunity-enablement) divided by job size. Each component on a comparable scale (Fibonacci 1, 2, 3, 5, 8, 13).
11. **For Kano:** map each item to must-be, performance, attractive (delight), indifferent, or reverse. Use survey data where available; mark inferred classifications.
12. **Mark every weak input.** If `known_metrics` did not cover an input you needed, you guessed. Flag it (`(guess)`, `(inferred)`, `(asker-supplied; unverified)`). This is the most important discipline in the skill — buyers should never receive a clean-looking number that hides a bad input.

### Phase 3 — Score and rank

13. **Compute the score per the framework's formula.** Show the inputs and the result side-by-side; never present only the final score.
14. **Rank by score, then break ties deliberately.** Common tie-breakers in order: lower effort wins; higher confidence wins; faster to learn from wins; closer to a strategic theme wins. Document which rule applied to each tie.
15. **Watch for known failure modes.** If a single item dominates (5× the next), the inputs are probably wrong, or the item belongs in its own category. Flag for review.
16. **Watch for the "all big" pattern.** If every effort estimate is "large," the team has not decomposed enough; the prioritization will be brittle. Recommend a decomposition pass and proceed with caveats.
17. **For MoSCoW, sanity-check the must list.** If "must" exceeds 60% of total effort, the team is over-committed — recommend down-leveling some musts to shoulds and note the implication.

### Phase 4 — Annotate, sensitivity-test, and explain

18. **Add a one-sentence justification per item.** Not just the inputs — the reason this item is where it is. "Top of list because it serves 70% of the user base with a confident reach number and an effort estimate from engineering." A reader who reads only the justification should understand the rank.
19. **Identify the unstable boundaries.** Where do small input changes flip the rank? "Items 4 and 5 swap if effort estimates are off by more than 20%." This is the most useful artifact the skill produces; it tells the asker where to invest more discovery before committing.
20. **Surface anti-recommendations.** Items at the bottom of the list that someone is likely to advocate for in the room. Naming them in advance prevents the meeting from re-litigating the rank.
21. **Note category effects.** If three of the top five items affect the same code area, the team can probably pack them into one larger investment for better economy — flag this and let the asker decide.

### Phase 5 — Compose, audit, and produce the reliability note

22. **Compose the recommendation section.** Two paragraphs. First: the framework chosen and why. Second: the alternative considered, why it lost, and the conditions under which the asker should reconsider.
23. **Compose the ranked list.** A table is best when there are more than five items; a numbered list is fine for fewer. Columns: rank, name, framework-specific inputs, score, one-sentence justification. Below the table, a section "items not ranked" if any candidates were excluded (e.g., MoSCoW won'ts, items that did not fit the framework), with reasons.
24. **Compose the reliability note.** Three to seven bullets covering: which inputs are weak and how to strengthen them; which ranks will likely flip with better data; which items deserve a discovery investment before they appear on a roadmap again; the cost of acting on the current rank versus the cost of waiting one more week to firm up the inputs.
25. **Audit the work.** Re-read the ranking. Does it match a gut check from someone who knows the product? If two items at the top look obviously wrong, your inputs are wrong; revisit them, do not ship the rank.
26. **Tag confidence on the overall output.** "High confidence — engineering provided effort estimates and reach numbers are from instrumentation." "Medium confidence — three of seven items have guessed effort." "Low confidence — every input is the asker's gut feel; treat this as a starting point for conversation, not a decision."

## Inputs

- **`candidates`** — required. The list. Free-form, one item per line or paragraph.
- **`context`** — required. What the prioritization is for and what constraints apply. Two or three sentences is usually enough.
- **`known_metrics`** — optional. Anything the asker already has measured. Reach numbers, conversion rates, effort estimates, importance/satisfaction survey data. Reduces guesswork dramatically.
- **`forced_framework`** — optional. Use only when the asker has a process reason (their company always uses MoSCoW for release planning) or wants to test a specific frame. The skill will still note where it does not fit.

## Outputs

- **`recommendation`** — the framework chosen with rationale and the alternative considered.
- **`ranked_list`** — the ordered candidates with every input visible.
- **`reliability_notes`** — where the rank is fragile, what to learn, and how to firm up before committing.

## Examples

### Example 1 — A growth team with 12 experiments

**Source.** 12 candidate experiments (copy changes, onboarding tweaks, paywall variations). Context: weekly experimentation cadence, small team, no formal effort estimates beyond "small/medium" guesses. No reach data per item.

**Output highlights.**

- **Frame.** ICE. Rationale: items are experiments, effort is small and comparable, reach is approximately the same across all (all hit the same active-user cohort). RICE was considered and rejected because reach does not differentiate.
- **Ranking.** 12 items scored on impact/confidence/ease (1–10 each), with three items above 250, six in the 100–200 band, and three below 100. The top three are a paywall pricing test, an onboarding step-skip, and an empty-state copy change.
- **Reliability.** "Confidence inputs are the asker's gut; ranks 4–8 are essentially tied within input uncertainty. Recommend running the top two in parallel and revisiting after the first results."

### Example 2 — Q3 planning with 18 features and engineering effort estimates

**Source.** A standard product backlog with rough reach numbers from product analytics, impact estimates from the PM, confidence flags from the discovery process, and effort in person-weeks from engineering.

**Output highlights.**

- **Frame.** RICE. Rationale: differentiated reach, real effort estimates, mix of large and small items.
- **Ranking.** Top of list is an item with reach 50,000 / impact 2 / confidence 0.8 / effort 4 weeks = RICE 20.0. Bottom of list is an item with reach 800 / impact 0.5 / confidence 0.3 / effort 8 weeks = RICE 0.015. The middle has six items clustered between 1.5 and 3.0.
- **Reliability.** "Items ranked 5–8 will reshuffle if effort estimates change by more than 15%. Recommend a refinement pass on those four before committing. Also: three items in the top 10 share the analytics-pipeline dependency; consider packing them together."

### Example 3 — A release-scope decision with a fixed launch date

**Source.** 22 candidate items for a launch six weeks out. Engineering team capacity is fixed. Context: a launch announcement is already scheduled.

**Output highlights.**

- **Frame.** MoSCoW. Rationale: fixed deadline, fixed capacity, need a yes/no answer per item. RICE was considered and rejected because the question is "what fits in 6 weeks," not "what is the best ROI."
- **Categorization.** 6 musts (4 weeks of effort total), 7 shoulds (3 weeks), 5 coulds (3 weeks), 4 won'ts (out of scope, named explicitly so they do not return as last-minute requests). Sanity check: musts are at 67% of capacity, leaving room for one or two shoulds.
- **Reliability.** "Two musts have effort estimates that are still soft. If either grows, one should becomes a could. Flag for engineering re-estimation by Friday."

## Limitations

- The skill cannot validate inputs the asker supplies. If `known_metrics` includes a reach number that is wrong, the rank will be wrong. The reliability notes are the only safeguard, and they only flag inputs that look soft on their face.
- Frameworks are tools, not truth. Two reasonable teams using the same framework on the same list can disagree because their input assignments differ. The skill exposes the inputs so the disagreement is about the inputs, not the rank.
- The skill does not negotiate. If two stakeholders disagree on impact, the skill flags the disagreement but does not resolve it; that is a human conversation.
- Some frameworks are political. MoSCoW in particular is often used to shield must-haves from challenge; the skill will sanity-check the must list but will not refuse to score a politically-loaded list.
- The skill assumes the candidate list is the right list. If the asker has missed an obvious candidate (a known critical bug, a regulatory deadline), the skill will not catch it unless it appears in `context`.
- The output is a starting point for a conversation. A ranking that no human owner endorses will not change behavior, no matter how clean the math.

## Sources reviewed

The methodology in this skill was synthesized after reviewing the following permissively-licensed open-source projects. None of their prose, structure, or code was copied. Each contributed a pattern or a constraint that informed the steps above; the synthesis is original.

- https://github.com/phuryn/pm-skills
- https://github.com/product-on-purpose/pm-skills
- https://github.com/ploi/roadmap
- https://github.com/anombyte93/prd-taskmaster
- https://github.com/github/spec-kit
