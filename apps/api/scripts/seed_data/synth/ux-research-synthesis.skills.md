---
id: skillsgit-curated/ux-research-synthesis
version: 1.0.0
name: Research Synthesis
description: Turn raw interview or usability-test notes into themed findings — affinity clusters, quotes-as-evidence, severity, recommendations, and a confidence rating per finding, traceable back to the participants who said it.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: design
tags: [niche:ux-research, synthesis, affinity, thematic-analysis, findings, qualitative-coding, insights]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 100000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - synthesize research
  - research synthesis
  - thematic analysis
  - affinity mapping
  - cluster notes
  - interview notes analysis
  - findings report
  - insight statements
  - research writeup
  - share research
  - quote evidence
  - usability findings
example_invocations:
  - "Synthesize these 8 interview transcripts into themes and findings."
  - "I have notes from 6 usability sessions — give me severity-ranked issues with quotes."
  - "Turn this raw research data into a findings report for the design review tomorrow."
  - "Cluster these participant quotes into themes and tell me which ones are confident."
inputs:
  - name: raw_notes
    type: text
    required: true
    description: The source material — transcripts, structured debrief notes, observation guides, or a mix. Include participant identifiers (P1, P2, etc.) so quotes can be traced. Longer is fine; the synthesis quality depends on having real participant words.
  - name: study_context
    type: text
    required: true
    description: Research goal, method, participant profile, and any hypotheses going in. Without this, the synthesis cannot weight findings against what the team needed to learn.
  - name: decision_to_inform
    type: text
    required: false
    description: The stakeholder decision the findings will feed. Used to scope recommendations and prioritize which findings lead.
  - name: known_constraints
    type: text
    required: false
    description: What the team can and cannot change — engineering limits, brand rules, budget, timeline. Recommendations will respect these and flag when a finding implies stepping outside them.
  - name: audience
    type: text
    required: false
    description: Who reads the findings. Defaults to "the product team plus stakeholders." If executive, the writeup tightens; if engineers, technical detail increases.
  - name: prior_findings
    type: text
    required: false
    description: Anything from earlier studies on this topic. The synthesis will note where the new data confirms, extends, or contradicts the old.
outputs:
  - name: findings_report
    type: markdown
    description: The structured writeup — headline, top findings with severity and confidence, supporting quotes per finding, recommendations, and an outliers section.
  - name: theme_map
    type: markdown
    description: The clustering view — themes, sub-themes, and which participants contributed to each. Useful for stakeholders who want the shape of the data behind the headlines.
  - name: quote_log
    type: markdown
    description: The participant quote bank, organized by theme, with attribution. Used for slide content, internal comms, and audit trails.
  - name: confidence_audit
    type: markdown
    description: Why each finding got its confidence rating — n of participants, strength of evidence, contradiction count, and what would raise or lower the rating.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Research Synthesis

## When to use

Use this skill when the team has finished collecting qualitative research data and now has to turn raw material — transcripts, notes, observation forms, recordings-summarized — into findings someone can act on. This is the slow, careful part of research where most teams under-invest, where analyst bias most often slips in, and where rushed work produces "insights" that are actually just the first thing the analyst noticed.

Trigger this skill when the input includes:

- Multiple sessions worth of qualitative material (transcripts, debrief notes, structured observation guides).
- A request for findings, themes, insights, a report, a writeup, or "what does it all mean."
- Phrases like "synthesize," "thematic analysis," "affinity mapping," "cluster these," "what are the patterns," or "give me the findings."
- A deadline tied to a decision the research was supposed to inform.

Do not trigger when:

- The team has not collected data yet (use the interview-guide-designer or usability-test-planner skill).
- The need is to write a survey (use the survey-question-bank-builder skill).
- The input is one participant's notes — that is not synthesis, that is a session summary.
- The input is quantitative survey data — different analytical method.

If `raw_notes` is missing or so thin that no honest synthesis is possible (one or two short paragraphs total, no participant attribution), ask for more material. Synthesis cannot manufacture evidence.

## How to apply

Work through these steps in order. Tempting shortcuts — "I can see the themes already, let me just write them up" — produce findings that confirm the analyst's prior beliefs and miss what the data actually contains. Resist them.

### Step 1. Ground the synthesis in the study context

Before reading the notes, restate:

- The research goal in one sentence.
- The decision the findings inform.
- The participant profile and total N.
- Any hypotheses the team had going in.
- Any prior findings that this study was meant to confirm, extend, or revisit.

Make this section explicit in the working document. The frame matters because the same quote can be a finding or a curiosity depending on what the team is trying to decide.

### Step 2. Extract observations, not interpretations

Read the raw notes session by session. For each session, list the observations — specific things the participant said, did, or showed, in their own words or as close as the notes allow. An observation is:

- Concrete (an action, a quote, a workaround, a stated belief).
- Attributed (P3 said it, P3 did it, P3 had this on their desk).
- Verifiable (someone could find it in the source notes).

An interpretation is:

- General ("users find it confusing").
- Unattributed (no specific participant).
- Inferential ("the design is broken").

Keep observations and interpretations strictly separated at this stage. The temptation is to leap to interpretation; resist it. A single session might yield 20–60 observations.

Tag each observation with:

- Participant ID.
- Session timestamp or note location, if known.
- A short topic label (the analyst's first-pass guess at what it is about). Do not commit to this label yet.

### Step 3. Cluster observations into themes

Once observations across all sessions are extracted, cluster them. Group observations that seem to point at the same underlying thing. Aim for these properties per cluster:

- **Specificity.** A cluster should be tight enough that the observations belong together. "Things about onboarding" is too broad; "participants couldn't figure out what to do after creating an account" is right-sized.
- **Multi-source.** Clusters with observations from at least two participants are stronger candidates for themes. Single-participant clusters become "noted, not patterned" or "interesting outlier."
- **Stability.** If two clusters keep wanting to merge, merge them. If one cluster keeps splitting, split it.

Iterate. The first clustering is rarely the final one. Walk the clusters at least twice — once to consolidate duplicates, once to look for clusters that should split. When stuck, ask: "If this finding were true, what would I see in the data?" and check whether you see it.

Aim for five to twelve themes from a typical 6–10-session study. Fewer than five usually means the clustering is too abstract; more than twelve usually means duplicate clusters or low-confidence noise.

### Step 4. Name themes in participant-grounded language

Theme names should:

- Be specific. "Trust" is not a theme; "people don't trust the system to handle their refund without manual verification" is.
- Use plain language. Jargon-free, even when the team's internal vocabulary is tempting.
- State the substance, not the feeling. "Frustration with the dashboard" is weaker than "the dashboard hides the metric most people open it for."
- Pass the surprise test for the reader. If a theme name is something the team already knew before the study, double-check whether the study actually surfaced new evidence or whether the analyst is back-filling old assumptions.

### Step 5. Promote themes to findings with evidence

A finding is a theme that has been articulated as a claim the team can do something with. The shape:

- One-sentence claim, written so a reader can disagree with it.
- Two to five supporting quotes, attributed.
- Number of participants who contributed (n out of total N).
- Severity (for evaluative studies) or impact assessment (for generative studies).
- Confidence rating (see step 7).
- A one-line "what changes if this is true" implication.

Drop themes that cannot reach this form. They become "noted observations" in an appendix — never the headline.

### Step 6. Apply a severity or impact rubric

For evaluative studies (usability tests), use a severity scale:

- **Blocker.** A typical user cannot complete the task or will abandon the product. Found in multiple participants or strongly anticipated.
- **Major.** Most users will struggle and lose time or confidence; some will fail. Strong evidence across more than one participant.
- **Minor.** Some users hit it; workaround is available; not on the critical path.
- **Cosmetic.** Polish or consistency, no behavioral impact.

For generative studies (interviews, field studies), use an impact rubric:

- **Strategic.** Implies a change to product direction, target user, or value proposition.
- **Roadmap.** Implies a specific feature, change, or investment.
- **Experience.** Implies a refinement to an existing flow, surface, or copy.
- **Background.** True and useful context but not directly action-implying.

State severity or impact explicitly per finding. Do not let "all findings are important" survive into the report — the team will pick anyway, and they will pick poorly without guidance.

### Step 7. Rate confidence honestly

Confidence is not the same as severity. A finding can be severe but low-confidence (one participant saw a blocker but the rest didn't try the path) or minor but high-confidence (every single participant agreed on something small).

Rate each finding on three sub-factors:

- **Evidence breadth.** How many participants? Out of how many on the path?
- **Evidence depth.** Did participants describe the same thing in different ways, or did they all use one shared phrase that might be coincidence?
- **Counter-evidence.** Did any participants experience the opposite? Was the contradiction explored?

Roll those into a four-level confidence rating:

- **High** — multiple participants, multiple modes of evidence, no significant counter-evidence.
- **Medium** — multiple participants but limited variety, or one strong participant with corroborating context.
- **Low** — single source or thin evidence; worth flagging but not action-driving on its own.
- **Speculative** — analyst inference with thin participant support; included only if useful as a hypothesis for the next round.

The team will trust the report more when low-confidence findings are clearly labeled. Hiding weak findings in confident language is the fastest way to lose stakeholder trust on the next study.

### Step 8. Capture outliers separately

Single-participant findings, contradictions, and surprises that did not fit any theme do not disappear. They go in a clearly marked outliers section with:

- The observation.
- The participant.
- Why it is interesting.
- What would be needed to know if it generalizes.

Outliers are often the seed of the next study. Bury them in an appendix and the team forgets; promote them with a label that says "not patterned but interesting" and they get attention.

### Step 9. Translate findings into recommendations

For each finding that can be acted on, write a recommendation:

- Direct action — "fix copy on the confirmation modal to say what users called it" — with the specific design or product change.
- Open exploration — "test two alternatives in the next round" — for findings where the right answer is not obvious.
- Decision input — "raise this in the trade-off discussion on shipping timing" — for findings that inform a judgment call rather than a fix.

Match recommendations to the constraints in the input. If the team cannot change the engineering stack, do not recommend a fix that requires it; flag the constraint instead.

Order recommendations by leverage, not by where they appeared in the data. The first recommendation should be the one that, if done, would shift the most for the team.

### Step 10. Compose the findings report

A clean report has this skeleton:

- **Headline.** One paragraph that someone can read and walk into a meeting with. Names the top one or two findings and the recommended action.
- **Study at a glance.** Goal, method, N, dates, who ran it.
- **Top findings.** Each finding gets a sub-section: claim, supporting quotes, n out of N, severity or impact, confidence, implication, recommendation.
- **Themes map.** A short summary of all themes (including those that did not make the top tier).
- **Outliers and surprises.** Bullet form.
- **Open questions.** What the study did not answer, with a recommendation on how to learn more.
- **Appendix.** Quote log, observation log if needed, screener used, anything reproducible.

Keep the top-findings section short. Three to seven findings in the main report; the rest get the themes-map summary. A 20-finding report is a no-finding report.

### Step 11. Build a confidence audit

A separate audit document explains, for each top finding, why it received its confidence rating. This is the artifact that makes the synthesis defensible when a stakeholder pushes back. It contains:

- The finding.
- Evidence breadth (n participants, who).
- Evidence depth (variety of mode).
- Counter-evidence found, or "none found, here is what I looked for."
- What would raise the rating.
- What would lower it.

This is also the artifact that lets a future researcher reopen the data and re-rate, which is the only way a research repository accumulates value over time.

### Step 12. Cross-check against the goal and decision

Before delivery, re-read the study goal and the decision to inform. For each:

- Does the report answer the goal? If not, name what is missing.
- Does the report give the decision-maker what they need? If not, add a "what we cannot tell you yet" section.
- Are any findings included that do not tie to the goal? Move them to the appendix unless they are unmissable.

Stakeholders forgive missing findings more easily than they forgive findings that distract from the decision.

## Inputs

- `raw_notes` (required): the source material, with participant attribution.
- `study_context` (required): research goal, method, N, hypotheses.
- `decision_to_inform` (optional): the stakeholder decision.
- `known_constraints` (optional): what the team can and cannot change.
- `audience` (optional): who reads the findings.
- `prior_findings` (optional): earlier studies on the topic.

## Outputs

- `findings_report`: the structured writeup.
- `theme_map`: the clustering view of all themes.
- `quote_log`: attributed quotes organized by theme.
- `confidence_audit`: per-finding rating rationale.

## Examples

### Example 1 — onboarding interviews, six participants

Inputs include six structured debrief notes from interviews with new users of a financial-planning product, the goal "understand why people abandon during the first session," and a decision pending on whether to invest in guided setup vs. self-serve education.

The synthesis produces five themes — three rise to top findings, two to "noted." The top finding is that participants opened the product with a specific question in mind (often a single number they wanted to look up or a single calculation) and abandoned when the product made them complete profile setup before answering. Five of six participants showed this pattern; their language was varied ("just trying to see X," "wanted to play with the numbers first," "didn't realize it was going to ask me all that"). Severity: roadmap-impacting. Confidence: high. Recommendation: investigate a "preview first, configure later" path; do not invest in guided onboarding until the abandon-on-setup hypothesis is tested against this.

A second finding is about trust — three of six expressed unease when asked for income; varied in how, but consistent enough to flag. Confidence: medium. Recommendation: explore copy and timing in the next round.

An outlier — one participant who completed setup quickly and reported enjoying it — is preserved with a note that this participant had used a similar product before and may not generalize.

### Example 2 — usability test, eight participants on a checkout flow

Inputs include observation guides from eight moderated remote sessions on a redesigned checkout, the goal "decide whether to ship in the May release," and the team's predefined kill criterion ("hold if any step blocks more than 2 of 6 participants").

The synthesis produces three severity-blocker findings (one of which exceeds the kill criterion), four major findings, six minor findings, and two cosmetic. The blocker that exceeds the kill criterion is named in the headline; the recommended action is "hold the May release on this flow." Confidence: high — six of eight participants hit it, all with the same root cause. The report includes the verbatim moderator-observed path for each affected participant.

A second blocker with three-of-eight evidence is rated medium confidence and the recommendation is to fix and verify in a small follow-up before shipping.

The report's "what we cannot tell you yet" section flags that the test did not cover the gift-card path, which was excluded from this round's scope.

## Limitations

- Synthesis quality is bounded by data quality. Sparse notes, missing attribution, or vague observations produce sparse findings.
- This skill cannot detect when participants were unrepresentative. If recruiting failed, the synthesis will faithfully report what those particular participants said, but the team must understand the recruit bias.
- For very large studies (30+ sessions), this skill produces a strong first-pass synthesis but human review is essential before publishing — patterns can shift at scale.
- Severity and confidence ratings are based on the available evidence; they do not encode strategic priority. The team must combine them with business context to prioritize action.
- The synthesis will not catch fabrication. If raw notes contain invented or fraud-prone responses (unmoderated panel issues), it cannot detect this from text alone.
- Cross-cultural or non-English data may need a researcher fluent in the relevant language and context for trustworthy theme naming.

## Sources reviewed

The synthesis methodology here was informed by surveying these open-source repositories covering research workflows, agent-skill collections including synthesis steps, and qualitative methodology tooling. All prose is original; no source text was reproduced.

- https://github.com/VoltAgent/awesome-claude-code-subagents
- https://github.com/msitarzewski/agency-agents
- https://github.com/aakashg/pm-claude-code-setup
- https://github.com/product-on-purpose/pm-skills
- https://github.com/ruxailab/RUXAILAB
- https://github.com/surveyjs/survey-library
