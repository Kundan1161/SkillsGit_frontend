---
id: skillsgit-curated/ux-interview-guide-designer
version: 1.0.0
name: User Interview Guide Designer
description: Draft a discovery interview guide tuned to a stated research goal and participant profile, with warm-up, story-prompts, behavioral probes, anti-leading guardrails, and a debrief checklist.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: design
tags: [niche:ux-research, interviews, discovery, qualitative, research-plan, probes, generative-research]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 5500
trigger_keywords:
  - interview guide
  - discovery interview
  - user interview
  - research questions
  - probes
  - generative research
  - customer interview
  - qualitative research
  - exploratory interview
  - research plan
  - interview protocol
  - field study
example_invocations:
  - "Build me a 45-minute discovery interview guide for parents who use our scheduling app."
  - "I need a generative interview script for developers evaluating observability tools."
  - "Draft an interview protocol — research goal is understanding how SMB owners handle expense receipts."
  - "Turn this research brief into a guide with warm-up, story prompts, and probes."
inputs:
  - name: research_goal
    type: text
    required: true
    description: One or two sentences naming the decision or question this study will inform. Specific is better than broad — "understand why trial users churn before day 7" beats "learn about users."
  - name: participant_profile
    type: text
    required: true
    description: Who you are talking to. Role, context, relevant behaviors, and any segment cuts. Include what you do NOT want (exclusions) if known.
  - name: session_length_minutes
    type: number
    required: false
    description: Target session length in minutes. Defaults to 45. The guide will be calibrated to fit, with optional sections marked.
  - name: study_modality
    type: choice
    required: false
    description: How the session will be run. Affects pacing, screen-share moments, and recording reminders.
    choices: [in-person, remote-video, phone, async-written]
  - name: existing_hypotheses
    type: text
    required: false
    description: What the team currently believes about the user or problem. The guide will probe these without leading. List them as separate lines or short bullets.
  - name: sensitive_topics
    type: text
    required: false
    description: Subjects that may trigger discomfort — money, health, employment status, family, etc. Triggers softer transitions and explicit opt-out language.
  - name: stakeholder_context
    type: text
    required: false
    description: Who will consume the findings and what decision they are making. Used to keep the guide tight to what stakeholders can act on.
outputs:
  - name: interview_guide
    type: markdown
    description: The full guide — title block, learning objectives, screener confirmation, warm-up, main sections with primary questions and follow-up probes, wrap-up, and a thank-you script.
  - name: moderator_briefing
    type: markdown
    description: A one-page briefing for the moderator — rapport tips, anti-leading reminders, how to probe without steering, and what to do when the participant goes off-track.
  - name: debrief_template
    type: markdown
    description: A structured debrief form for use immediately after each session — five-minute version and fifteen-minute version.
  - name: probe_bank
    type: markdown
    description: A separate list of probes the moderator can drop in based on participant cues, organized by the cue type (vague answer, strong emotion, contradiction, etc.).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# User Interview Guide Designer

## When to use

Use this skill when a research team or product team needs a discovery, exploratory, or generative interview guide and wants something better than a list of questions. A good guide gets past what people say they do to what they actually do, surfaces the surprises that change product direction, and protects against the moderator's own beliefs leaking into the conversation.

Trigger this skill when the input includes:

- A research goal phrased as a decision, a question, or a "we don't know" statement.
- A participant profile — even a rough one. ("Five power users of our analytics product.")
- A request for a guide, protocol, script, questions to ask, or a discovery plan.
- Phrases like "discovery interviews," "customer interviews," "user interviews," "field study," "generative research," "foundational research," or "1:1s with users."

Do not trigger this skill when the user wants:

- A usability test plan for a specific design (use the usability-test-planner skill).
- A survey or questionnaire (use the survey-question-bank-builder skill).
- An analysis of interview data already collected (use the research-synthesis skill).
- Customer-success or sales discovery calls — these have different goals and a different shape.

If the research goal is missing or so broad it would not change any decision, ask one clarifying question first. The single most common failure mode of interview guides is studying everything and learning nothing.

## How to apply

Work through these steps in order. Do not skip the goal interrogation step even when the user seems impatient — a vague goal produces a vague guide that wastes participant time and stakeholder trust.

### Step 1. Interrogate the research goal

A research goal is a decision waiting on evidence. Before writing anything, restate the input goal in this shape: "We want to learn X so we can decide Y." If you cannot fill in Y, ask the user what changes once findings land. If the user cannot answer, mark the study as exploratory and reduce the guide's specificity claims accordingly.

Reject these as goals and ask for a replacement:

- "Understand our users." (Too broad — every guide ever written fits this.)
- "Validate the new feature." (Validation is rarely possible from interviews; reshape as "learn how users currently solve X.")
- "Get feedback on the prototype." (That is a usability test, not a discovery interview.)

A usable goal: "Learn how solo accountants close their monthly books so we can decide whether to build an automated reconciliation feature or a manual checklist tool."

### Step 2. Convert the goal into learning objectives

Break the goal into three to five learning objectives — concrete things you must walk out knowing. Each objective should map to a section of the guide. Aim for objectives that begin with verbs like "describe," "identify," "characterize," "trace," or "compare." Avoid verbs like "validate" or "prove" — interviews cannot do either reliably and the framing pulls the moderator toward confirmation.

Cap the count at five. A 45-minute session covers three to four objectives well; five is the ceiling; six guarantees something gets shortchanged.

### Step 3. Plan the time budget

Allocate minutes against this rough envelope (scale to session length):

- Two to four minutes — consent, recording, pre-roll comfort.
- Five to seven minutes — warm-up and context.
- Sixty to seventy percent of remaining time — main sections, one per learning objective.
- Five minutes — wrap-up, anything-we-missed, and thank-you.

Mark optional sections with a clear flag so the moderator can drop them if the conversation slows. Do not mark consent or wrap-up as optional.

### Step 4. Write the warm-up

The warm-up is not throwaway time. It anchors the participant in concrete, present, lived experience — the mode you want them in for the rest of the session — and gives the moderator a baseline for how this person talks, what jargon they use, and what their energy is like.

Use questions that are easy, recent, and specific:

- "Walk me through what you did the last time you [activity related to the topic]."
- "Tell me about your role and what a typical Wednesday looks like."
- "When did you first start [doing the relevant activity]?"

Avoid asking about hypotheticals, preferences, or the future in the warm-up. Save those for later, if at all.

### Step 5. Write the main sections — one per learning objective

Each section needs three layers.

**Primary questions** (one to three per section). These are open, story-eliciting, and grounded in past behavior or present state. Write them in the participant's plausible vocabulary, not the team's. Each primary question should produce at least two to three minutes of answer when asked well.

Strong patterns to use:

- "Tell me about the last time you..."
- "Walk me through what happened when..."
- "What were you trying to get done that day?"
- "What did you do right before / right after that?"

**Follow-up probes** (three to six per primary question). Probes are not new questions — they are surfacing tools that get the participant to expand, slow down, or notice their own pattern. Include at least one of each:

- Story-deepening probe — "What happened next?" or "Then what?"
- Specificity probe — "What did that look like in practice?" or "Show me, if you can."
- Emotional probe — "How did that feel in the moment?" or "What ran through your head?"
- Contrast probe — "Was that different from how it usually goes?"
- Silence probe — a note to the moderator to wait without filling the silence.

**Anti-leading cautions** (one or two per section). Spell out the trap the moderator is at risk of falling into. Examples:

- "Do not say 'and that was frustrating, right?' — let the participant supply the affect."
- "Avoid naming the feature concept. If the participant volunteers it, ask them to describe it in their own words first."
- "Resist agreeing with criticism of competitors — neutral acknowledgment only."

### Step 6. Add hypothesis probes — last, and gently

If the team supplied existing hypotheses, the guide must probe them without telegraphing them. Place hypothesis-probe questions late in the relevant section, after the participant has already told the story in their own words. Frame them as exploration, not confirmation:

- Not: "Would it help if we built X?"
- Instead: "Have you ever tried anything to make this easier? What happened?"
- Not: "We think people give up at step three. Did you?"
- Instead: "Take me through what happened at each step. Anywhere you nearly stopped?"

The participant should never be able to guess from the question wording what the team hopes they will say. If a question fails this test, rewrite it.

### Step 7. Write the wrap-up

The wrap-up does three jobs:

- Surfaces anything the guide missed: "Is there anything important about this that I did not ask about?"
- Gathers an artifact lead if relevant: "Would you be open to sharing a screenshot or a redacted example?"
- Closes warmly and confirms incentive and next-steps logistics.

Always include the missed-topic question. Roughly one in eight sessions produces a finding from that single prompt that reshapes the study.

### Step 8. Layer in modality-specific reminders

For remote-video, insert reminders to confirm recording at the top, check audio in the first thirty seconds, ask before screen-share, and note time-zone-aware language for follow-ups.

For in-person, add reminders about location comfort, observers in the room, and artifact collection (notebooks, sticky notes, whiteboard photos).

For phone, drop visual-context questions and replace them with "describe what you are looking at right now" prompts.

For async-written, restructure into a sequenced prompt set with reasonable per-question word-count guidance and a "skip if not applicable" affordance. Reduce question count by half — text answers tire participants faster than spoken ones.

### Step 9. Handle sensitive topics carefully

When the input flags sensitive topics, do these things explicitly in the guide:

- Add a top-of-session statement: "Some of what we talk about might be personal. You can skip any question or stop at any time, and your data will be handled confidentially."
- Place sensitive questions after rapport is built — never in the first ten minutes.
- Use third-person framing as an escape hatch: "Some people in your situation tell us X. Does that resonate, or is your experience different?"
- Add a recovery prompt to use if the participant becomes upset, plus the moderator's exit script.

### Step 10. Add the moderator briefing

The briefing is a separate document the moderator reads right before the session. It contains:

- The research goal in plain language.
- The top three biases or assumptions the team is bringing in. Naming them helps the moderator notice when they leak into a question.
- Three anti-leading reminders specific to this guide.
- The probe bank, organized by cue type — pull these out so the moderator can scan when stuck mid-session.
- One paragraph on "what counts as a good session" so the moderator knows when to push and when to let things breathe.

### Step 11. Add the debrief template

Right after the session — within fifteen minutes — the moderator and any observers should fill out a structured debrief. This is not the synthesis step; it is the memory-capture step.

A five-minute version covers:

- Top three things the participant said in their own words (quotes, if possible).
- One thing that surprised you.
- One thing that confirmed or disconfirmed a hypothesis.
- A confidence rating on how candid the participant was, with a one-line reason.

A fifteen-minute version adds:

- A timeline of how the session went section by section.
- Anything you would change about the guide for the next session.
- Open questions you now want to chase in the next interview.

### Step 12. Pressure-test the draft

Before delivering, run the guide through these checks:

- **Lead test.** Can a reader predict which answers would make the team happy? If yes, rewrite the worst offenders.
- **Compound test.** Are any questions actually two questions stapled together? Split them.
- **Jargon test.** Are there words only the team uses? Replace with the participant's likely vocabulary.
- **Yes-no test.** Are open questions accidentally answerable with one word? Convert to "walk me through" or "tell me about."
- **Time test.** Read it aloud at conversation pace. Does it fit the budget with buffer? If not, cut the lowest-priority section.
- **Decision test.** For every section, can you say what stakeholder decision it informs? If not, cut it or merge it.

## Inputs

- `research_goal` (required): the decision the study will inform.
- `participant_profile` (required): who is in the room and why they qualify.
- `session_length_minutes` (optional): the time budget.
- `study_modality` (optional): in-person, remote-video, phone, or async-written.
- `existing_hypotheses` (optional): what the team currently believes, for probe planning.
- `sensitive_topics` (optional): subjects that need softer handling.
- `stakeholder_context` (optional): who reads the findings and what they will decide.

## Outputs

- `interview_guide`: the structured guide ready for use in sessions.
- `moderator_briefing`: a one-page warm-up for the person running the conversation.
- `debrief_template`: a structured form for post-session capture.
- `probe_bank`: a standalone list of probes organized by participant cue, for mid-session reference.

## Examples

### Example 1 — solo-accountant book-closing study

Input research goal: "Learn how solo accountants close their monthly books so we can decide whether to build automated reconciliation or a manual checklist tool."

Participant profile: "Solo or two-person accounting practices, three to fifteen SMB clients each, currently using QuickBooks or Xero, has closed at least three months for at least one client."

Session length: 50 minutes, remote-video.

Existing hypotheses: "Reconciliation is the most-disliked task; checklists are abandoned; integrations are mistrusted."

The output guide would have five learning objectives — describe the monthly close shape, identify the parts that hurt most, trace what they have already tried, characterize trust in automation, and compare practices across client types. The warm-up would ask the accountant to walk through last month's close for one specific client. The probes would chase contradictions between "I hate this task" and "I still do it the same way I did five years ago." The hypothesis-probe in the automation section would never name the feature — it would ask "have you ever set up something to do part of this for you? What happened?"

### Example 2 — onboarding-drop-off study

Input research goal: "Understand why trial users of our team-collaboration product drop off between day 2 and day 7, so we can decide whether to invest in in-product education or admin-led setup."

Participant profile: "People who started a free trial in the last 60 days at a company of 10–200 employees, used the product at least once, and then stopped logging in by day 7."

Session length: 30 minutes, remote-video.

Sensitive topics: "Avoid making participants feel judged for not adopting — many will be self-conscious."

The output guide would lead with a permission frame ("we are genuinely trying to understand what got in the way, not selling you on anything") and structure questions around the participant's whole working week rather than the product. The strongest section would be a walkthrough of the day they first opened the product and what they were hoping to do — followed by a tracing of what they did with that goal afterward, inside the product or out of it.

## Limitations

- Interview guides are tools, not scripts. A guide that the moderator reads verbatim produces wooden sessions and weak data. The moderator must internalize it, then converse.
- This skill does not recruit participants, schedule sessions, or pay incentives. It assumes a research-ops capability exists or will be set up separately.
- Five-to-eight-participant studies are the minimum for thematic findings. The guide will not save a study that under-recruits.
- The skill cannot detect when a research goal is the wrong one — only when it is too vague. If stakeholders have asked the wrong question, the guide will dutifully answer it.
- Probes for highly specialized domains (clinical, legal, regulated finance, defense) may need expert review beyond what this skill produces.
- The guide is not a substitute for moderator training. A skilled moderator with a mediocre guide outperforms a novice with an excellent one.

## Sources reviewed

The methodology synthesized here was informed by surveying these public open-source repositories and noting common patterns across UX research guides, agent-skill collections that touch user research, and qualitative methodology resources. No content from any source was copied; all prose above is original.

- https://github.com/VoltAgent/awesome-claude-code-subagents
- https://github.com/msitarzewski/agency-agents
- https://github.com/product-on-purpose/pm-skills
- https://github.com/aakashg/pm-claude-code-setup
- https://github.com/ruxailab/RUXAILAB
- https://github.com/surveyjs/survey-library
