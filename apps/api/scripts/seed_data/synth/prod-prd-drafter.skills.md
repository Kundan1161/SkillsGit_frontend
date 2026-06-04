---
id: skillsgit-curated/prd-drafter
version: 1.0.0
name: PRD Drafter
description: Turn a problem statement plus context into a complete product requirements document — goals, non-goals, users, journeys, requirements, edge cases, success metrics, risks, and the open questions a reader will ask back.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: productivity
tags: [niche:product-management, prd, requirements, specification, discovery, scoping, planning]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - write a PRD
  - product requirements document
  - draft requirements
  - product spec
  - feature brief
  - product brief
  - one-pager
  - scoping doc
  - requirements doc
  - functional requirements
  - user stories
  - product narrative
example_invocations:
  - "Draft a PRD for an in-app referral program targeted at our paid teams cohort."
  - "I have a problem statement and three user interviews. Turn it into a PRD I can share with engineering."
  - "Write the requirements doc for a CSV export improvement, including edge cases and success metrics."
  - "Give me a one-pager PRD I can share in a Slack channel before the full doc is ready."
inputs:
  - name: problem_statement
    type: text
    required: true
    description: A description of the problem the product change is meant to solve. Two to ten sentences. The crisper, the better; if it is fuzzy, the skill will surface that as an open question.
  - name: audience_and_users
    type: text
    required: false
    description: Who the change is for. Segment, role, the situation in which they hit the problem. Quotes from research, support tickets, or sales notes are welcome.
  - name: context_and_constraints
    type: text
    required: false
    description: Anything that limits or shapes the solution space — current architecture, regulatory limits, brand commitments, dates the team has to hit, partner dependencies, or strategic bets the PRD must fit inside.
  - name: prior_art
    type: text
    required: false
    description: Pointers to previous attempts, competitor patterns, internal experiments, or related skills the work touches. Helps the PRD acknowledge what is already known and avoid reinventing.
  - name: doc_length
    type: choice
    required: false
    description: How long the document should be. Defaults to standard.
    choices: [one-pager, standard, deep]
  - name: today
    type: text
    required: false
    description: ISO date used to anchor any "by quarter end" or "this half" phrases in the source material.
outputs:
  - name: prd
    type: markdown
    description: The full requirements document in the canonical section order — TL;DR, context, goals, non-goals, users and journeys, requirements, edge cases, success metrics, risks, dependencies, rollout, and open questions.
  - name: one_pager
    type: markdown
    description: A short companion version (under 400 words) suitable for a kickoff Slack post or an exec preview, regardless of which length was chosen for the main PRD.
  - name: open_questions_register
    type: markdown
    description: A standalone list of every unresolved question raised during drafting, with the recommended owner for each. Used to drive the next discovery conversation.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# PRD Drafter

## When to use

Use this skill when a product manager, engineering lead, or founder has a problem worth solving but does not yet have a document that an interdisciplinary team can build against. The output is a PRD: a structured artifact that names the problem, the users, the requirements, the edge cases, the success metrics, and the things still not known. It is the document that sits between "we should do something about X" and "here are the tickets to do it."

Engage when the asker can describe the problem in a few sentences and can name an audience or a constraint, even if loosely. The skill is designed to handle ambiguity by surfacing it explicitly in the *Open questions* section, not by guessing.

Decline or push back when:

- The asker is actually trying to write a *strategy* document (a multi-quarter bet, a market thesis). PRDs scope to a feature or program; strategies scope to a market or business unit. Recommend the prioritization or strategy skill instead.
- The asker wants a marketing or launch brief, not a build brief. PRDs are for the engineering and design team; launch briefs are for go-to-market. Different audience, different content.
- The problem statement is "make the product better." That is a vision, not a problem. Ask one round of clarifying questions before drafting; if the asker cannot get more specific, write a discovery document instead — a PRD against a vague problem produces a vague PRD.
- The work is a pure bug fix or a small follow-up. A ticket is enough. PRDs are for changes that meaningfully cross team boundaries or carry product risk.

The skill is also the right tool for *rescuing* a stalled doc. If the asker pastes in half-written notes, treat them as raw input — extract what is usable, surface what is missing, and produce a document that is materially better than what they had.

## How to apply

Run the methodology in six phases. Each phase reduces a specific class of PRD defect.

### Phase 1 — Pin down the problem before describing the solution

1. **Read the problem statement twice.** Once for the surface claim, once for what is being implied. A statement like "our trial-to-paid conversion is below target" is the *surface*; the implied problem may be "new users do not see the value before the trial expires," and those produce different solutions.
2. **Restate the problem in one sentence.** No solution language, no feature names. The sentence should be readable by someone outside the team. If you cannot restate it in one sentence, the problem is two problems; split them.
3. **Name the user and the situation.** A problem without a user is a hypothesis floating in the air. Use the `audience_and_users` input. If absent, infer from the problem statement and flag the inference as an open question — never pretend you know more than you do.
4. **Identify the trigger.** What event puts the user in the situation where the problem bites? "Logs in for the first time," "tries to invite a teammate," "renews their plan." Triggers anchor everything that follows; without one, the journey section becomes generic.
5. **Estimate the size.** Is this a problem one user hits once a year or a million users hit weekly? Pull from `context_and_constraints` if available. If unknown, mark "size unknown — proxy from instrumentation needed" and put it in the open questions register.
6. **Decide the PRD length.** Use `doc_length` if supplied. Otherwise default to **standard** (1,200–2,500 words). A one-pager is appropriate when the change is small or the team already shares deep context. Deep is for cross-org, multi-quarter programs.

### Phase 2 — Set goals and non-goals separately and explicitly

7. **Write the goals as outcomes, not features.** "Reduce time-to-first-value for new trial accounts from N minutes to M minutes" is an outcome; "ship an onboarding wizard" is a feature. Outcomes give the team room to find the best solution.
8. **Bound the goals to a measurable target.** A goal that cannot be checked at the end is a sentiment. If the asker does not have a number, propose one with a clear "we believe X is achievable because Y" rationale, and flag for confirmation.
9. **Write at least two non-goals.** This is the most-skipped section and the most-cited cause of scope drift. A good non-goal names a tempting adjacent problem and explicitly defers it ("Not in scope: redesigning the team-invite flow, even though it shares the same screen — we'll revisit in a follow-up PRD.").
10. **Disambiguate "later" from "never."** A non-goal that is "we'll do this in Q3" is a sequencing constraint; a non-goal that is "we won't do this in this product" is a strategic stance. Mark each.

### Phase 3 — Describe the users and the journey before the requirements

11. **List the user segments.** Be specific. "Trial users on team plans, between day 3 and day 7" beats "trial users." If multiple segments are in scope, rank them by priority — the design decisions will favor the top segment when they conflict.
12. **Write each segment's current journey in 3–7 steps.** Plain English. Use verbs. Mark the step where the problem bites with `<<<— pain point.` This anchors the rest of the document; a reader who knows where the pain bites can follow the requirements without needing to back-read.
13. **Write the desired journey alongside the current one.** Same structure, marked with the change. Resist the urge to design the UI; describe what the user *experiences*, not what the screen *shows*.
14. **Cover at least one edge journey.** What does the user with no internet, no payment method, no teammates, no permissions, or no English experience? Edge journeys are where products break their promises. List the three most likely edge cases and address them in the requirements section.

### Phase 4 — Translate the journey into requirements

15. **Lead with functional requirements.** Numbered list, each item one sentence, verb-led. "FR-1: The system shall present an invite-teammate prompt within 90 seconds of first sign-in." Numbered IDs let downstream tickets, designs, and tests reference back.
16. **Separate functional from non-functional.** Non-functional includes performance, scale, availability, security, accessibility, internationalization, compliance, and observability. Each gets its own subsection; do not bury "must meet WCAG AA" inside a list of features.
17. **Mark must-have, should-have, could-have.** Steal from MoSCoW. Be honest about could-haves — anything you would not personally cut if the date slips by a week is a must.
18. **Specify the inputs and outputs of each requirement.** "FR-3: When the user clicks Invite, the system sends an email and shows a confirmation toast" — name the email template, the toast copy as a placeholder, and the audit-log event. Implicit specs become arguments at review.
19. **Cover the error states.** For every requirement that can fail, describe what the user sees, what the system logs, what the support team can do, and what triggers a retry. Skipping this is the most-cited cause of "the spec was incomplete" in postmortems.
20. **Cover the empty states.** First use, zero data, permissions denied, network offline. Empty states are not edge cases; they are the user's first impression.
21. **Specify the data model changes.** If the feature touches storage, name the new entities, the relationships, the migration path, and the retention rules. A PRD that hand-waves data is a PRD that produces a regrettable schema.

### Phase 5 — Wire in metrics, risks, and rollout

22. **Define the success metric upfront.** One primary metric, no more than two secondary, and exactly one *guardrail* metric (the thing you watch to make sure success did not come at a cost elsewhere). Match each goal in phase 2 to a metric here.
23. **Pre-register the measurement plan.** How will you read the metric? What instrumentation must ship with the feature? What is the analysis window? Without this, the team will ship the feature and then discover the data was never collected.
24. **List the top three risks with their likelihood and impact.** Be specific: "Risk: invite emails land in spam for Google Workspace tenants due to our shared sending domain — likelihood medium, impact high, mitigation: route via dedicated subdomain before launch." A risk without a mitigation is a wish.
25. **Name the dependencies and the owner.** Engineering teams, vendors, legal review, marketing assets, support training. Dependencies left implicit become launch blockers discovered the week before launch.
26. **Specify the rollout plan.** Behind a flag? Cohort by cohort? All at once? Include the kill-switch path and the rollback criteria ("if the guardrail metric drops by more than 5% in 24 hours, disable the flag and triage"). Even a small change benefits from a written rollback.
27. **Specify the launch criteria.** What must be true on the day the feature is enabled for general availability — instrumentation green, docs published, support trained, internal demo recorded, marketing assets approved. A launch checklist embedded in the PRD beats a launch checklist tracked in a separate doc that no one reads.

### Phase 6 — Compose, self-review, and produce the auxiliaries

28. **Assemble the document in the canonical order.** TL;DR first (3–6 sentences), then context, goals, non-goals, users and journeys, requirements (FR then NFR), edge cases, success metrics, risks, dependencies, rollout, open questions, glossary. Always include the glossary if any acronym appears more than once.
29. **Write the TL;DR last.** It is a summary, not a preamble. After the rest of the document is drafted, write a TL;DR that answers: what problem, for whom, what we will do (one sentence), what success looks like, and the biggest open question. A reader who reads only the TL;DR should be able to decide whether to keep reading.
30. **Self-review as the skeptical engineer.** Is each requirement testable? Are there acceptance criteria, even implicit? Where the answer is no, rewrite.
31. **Self-review as the skeptical designer.** Is there enough about the user journey to design from? Are the empty and error states named? Where the answer is no, rewrite.
32. **Self-review as the skeptical exec.** Is the goal an outcome? Is the metric measurable in the time horizon stated? Is there a single sentence the exec can repeat to their boss? Where the answer is no, tighten.
33. **Produce the one-pager.** Under 400 words. Use the structure: problem, who, what we will do (3 bullets), success metric (one line), the biggest open question, the date the full PRD will be ready. Suitable for a Slack post.
34. **Produce the open-questions register.** Every "TBD" and every "needs research" in the body gets its own row with a recommended owner (use `known_owners` if available; otherwise mark "TBD") and a recommended deadline (default: before kickoff). The register is the asker's to-do list for the next week.
35. **Confidence-tag the output.** If significant portions of the inputs were ambiguous or absent, add a confidence note at the bottom of the PRD: "Medium confidence — no user research provided; user segment is inferred from the problem statement." Honest uncertainty beats false precision.

## Inputs

- **`problem_statement`** — required. Two to ten sentences. Even a rough version is enough; the skill will sharpen it.
- **`audience_and_users`** — optional but strongly recommended. Without it, the user section will be inferred and flagged.
- **`context_and_constraints`** — optional. Architecture, legal, brand, time, dependencies. Anything that bounds the solution space.
- **`prior_art`** — optional. Previous attempts, competitor patterns, internal experiments. Helps avoid duplication and acknowledges institutional memory.
- **`doc_length`** — optional. `one-pager`, `standard`, `deep`. Defaults to `standard`.
- **`today`** — optional. ISO date for resolving "this half," "by Q3," "before launch."

## Outputs

- **`prd`** — the full document in the canonical section order.
- **`one_pager`** — a short companion version suitable for the kickoff post.
- **`open_questions_register`** — every unresolved question with recommended owner and deadline.

## Examples

### Example 1 — Trial-to-paid conversion problem with minimal inputs

**Source.** A four-sentence problem statement: "Our trial-to-paid rate is below target. We think users do not invite teammates before their trial ends. We have no user research. We need a PRD by Friday." No audience details, no constraints.

**Output highlights.**

- **Problem (restated).** "New trial users on team plans do not invite teammates before the trial expires, which causes them to under-experience the product's collaboration value and churn instead of converting."
- **TL;DR.** "Trial users on team plans are not inviting teammates early enough. We will add an in-trial nudge to surface the invite flow at the moment of highest intent (first signed-in session after first project creation) and measure the impact on trial-to-paid rate over a 6-week window. Biggest open question: do we have instrumentation today to measure invite-send-within-72-hours?"
- **Goals.** Outcome-shaped: "Increase invite-send-within-72-hours by 30% for trial accounts on the team plan."
- **Non-goals.** Two named, each with rationale: redesigning the team-invite UI; targeting solo trial users.
- **Users.** Segment named with an inferred profile, flagged: "Inferred — no research provided." Listed in the open-questions register with a recommended owner: "PM to validate with 3 trial accounts before kickoff."
- **Risks.** Top three: instrumentation gap, email-deliverability for Google Workspace, prompt fatigue if combined with onboarding nudges already in place.
- **Confidence.** "Medium-low: no user research, no current funnel data. Treat goals as hypotheses pending validation."

### Example 2 — A deep PRD for a regulated industry change

**Source.** Detailed problem statement plus a paragraph each on architecture, legal review, and dates. Asker selected `doc_length: deep`.

**Output highlights.**

- **Length.** ~4,000 words across the canonical sections.
- **Requirements.** 28 numbered functional requirements, 9 non-functional (with explicit security, accessibility, and audit-log sections), 4 explicit edge-journey requirements covering offline, permissions-denied, and locale-mismatch.
- **Rollout.** Three-stage rollout with a documented kill switch and rollback criteria, plus a pre-launch legal sign-off as a launch criterion.
- **Open questions.** 11 items in the register, each with a recommended owner from the supplied team, deadlines spread across the next three weeks.

### Example 3 — Rescue of a half-written PRD

**Source.** A 1,200-word doc the asker started two weeks ago and is unhappy with. Goals are missing, requirements are mixed with implementation detail, no edge cases.

**Output highlights.**

- **Method.** The skill extracts the usable material (user descriptions, three of the requirements, the rough success metric) and discards or refactors the rest. It writes a new TL;DR and goals section, separates FR from NFR, adds edge cases and error states, and produces an open-questions register that names the gaps the asker had been avoiding ("no rollout plan," "no metric instrumentation plan," "non-goals not defined").
- **Confidence.** "Medium: source had usable user descriptions but no measurement plan; success metric proposed needs validation with the data team before kickoff."

## Limitations

- The skill cannot replace user research. If `audience_and_users` is absent, the user section is inferred and explicitly flagged. The asker is responsible for validating before kickoff.
- The skill writes a build-side PRD. It does not produce launch plans, marketing briefs, or sales enablement content; those need their own documents and different audiences.
- The skill does not estimate engineering effort. Effort goes in a separate sizing exercise after the PRD is reviewed.
- The skill assumes good faith inputs. If the problem statement misrepresents the situation ("users love feature X" when usage data says otherwise), the resulting PRD will be wrong; the skill cannot independently verify claims.
- The skill defaults to English and to common Western product conventions. Localization, accessibility for non-Latin scripts, and culturally-specific journey patterns are flagged for human review.
- The skill produces a document, not a decision. The PRD does not commit anyone to building anything; that commit happens at a review meeting or in a planning ritual the team owns.

## Sources reviewed

The methodology in this skill was synthesized after reviewing the following permissively-licensed open-source projects. None of their prose, structure, or code was copied. Each contributed a pattern or a constraint that informed the steps above; the synthesis is original.

- https://github.com/phuryn/pm-skills
- https://github.com/product-on-purpose/pm-skills
- https://github.com/anombyte93/prd-taskmaster
- https://github.com/github/spec-kit
- https://github.com/ploi/roadmap
