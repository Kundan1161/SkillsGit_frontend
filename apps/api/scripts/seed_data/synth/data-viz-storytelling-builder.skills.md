---
id: skillsgit-curated/data-viz-storytelling-builder
version: 1.0.0
name: Data Storytelling Builder
description: Turns a data finding into a 5-slide narrative — claim, evidence, mechanism, implication, action — with chart specs and speaker notes for each slide.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:data-viz, data-storytelling, narrative, presentation, executive-communication, slides, insights]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: []
  min_context_tokens: 16000
  estimated_tokens_per_invocation: 5000
trigger_keywords:
  - data storytelling
  - data narrative
  - insight to story
  - data presentation
  - executive narrative
  - five-slide story
  - data findings deck
  - chart narrative
example_invocations:
  - "Turn this finding into a five-slide executive narrative: our enterprise churn jumped 40% in Q1."
  - "I have a chart showing pricing experiment results — help me build the story around it."
  - "Build a narrative arc for this insight before I present to the board."
  - "I have a regression result that says X drives Y — turn it into a story."
inputs:
  - name: finding
    type: text
    required: true
    description: The data finding in one or two sentences. Should include the metric, the direction or magnitude of change, and the segment if relevant.
  - name: supporting_data
    type: text
    required: true
    description: Numbers, charts, or analyses that back the finding. Enough that the evidence and mechanism slides can be specified concretely.
  - name: audience
    type: text
    required: true
    description: Who hears the story — role, prior knowledge of the metric, decision authority.
  - name: action_requested
    type: text
    required: false
    description: The action the storyteller wants the audience to take. If unknown, the methodology will help derive a candidate.
outputs:
  - name: narrative_arc
    type: markdown
    description: A one-paragraph summary of the five-slide arc — the through-line the audience should hold in working memory.
  - name: slide_specs
    type: markdown
    description: Five slide specifications, each with title, key visual, supporting text, and speaker notes.
  - name: chart_specs
    type: markdown
    description: Concrete chart specs for any data slide (encoding, sort order, annotations).
  - name: anticipated_objections
    type: markdown
    description: Likely objections from the audience and how the story addresses them in advance.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when a user has a data finding and needs to present it to an audience — executives, board, customers, public — in a tight narrative arc. Typical situations:

- A quarterly business review needs a five-minute "here is what we learned" segment.
- An experiment finished and the team must convince leadership to act on it.
- A surprising metric movement needs to be explained without raising more confusion than it answers.
- A complex regression or model result must be communicated to non-technical decision makers.

Do not invoke this skill for raw analysis (the finding must already exist), for academic-style paper writing (different conventions for evidence and mechanism), or for a full deck longer than ten slides — this skill produces a tight five-slide spine that may be embedded in a larger deck or stand alone.

## How to apply

The methodology forces a single through-line across five slides. Each slide does one job. If a slide cannot be summarized in one sentence, the structure is wrong; re-divide before adding content.

### 1. Anchor the finding

1. **Restate the finding in one sentence.** Verb, magnitude, segment, time period. "Enterprise churn rose from 4% to 6% in Q1 among customers acquired before 2024." Vague findings ("churn is up") produce vague stories.
2. **State the metric definition explicitly.** A finding is only as trustable as the metric. Note the formula, denominator, and exclusions if any.
3. **State the comparison.** Up against what — last quarter, last year, plan, peers? Without a comparison, "rose" is not yet a finding.
4. **Confirm the finding is robust.** A signal at p > 0.1 with n = 30 is a hypothesis, not a finding. Note the confidence; the story will need to match.
5. **Ask whether the audience already knows the finding.** Familiarity changes pacing — for known findings, the story is about implication and action; for surprising findings, the evidence and mechanism slides need more weight.

### 2. Identify the audience and the decision

6. **Name the primary listener.** Role, prior knowledge, decision authority. A CEO who can reallocate a quarter's budget is a different listener from a director who can reprioritize a sprint.
7. **Name the decision the audience must make.** If no decision is at stake, the story is a report — fine, but adjust expectations. The most effective five-slide narratives end in a decision.
8. **Identify the cost of being wrong in both directions.** If the audience acts and the finding is spurious, what is the downside? If they do not act and the finding is real, what is the downside? The asymmetry tells you how strongly to advocate.
9. **Identify the listener's likely first objection.** Almost every audience has one. The story should address it before they raise it — usually on the evidence or mechanism slide.

### 3. Lay out the five-slide arc

The arc is fixed: Claim → Evidence → Mechanism → Implication → Action. Use it as a checklist; reorder only if you can defend the choice.

10. **Slide 1 — Claim.** The single most important sentence of the talk. State the finding as a takeaway, not a topic. Include magnitude and segment. The headline is the slide title.
11. **Slide 2 — Evidence.** The chart or numbers that make the claim incontrovertible. One chart, not five. Annotated, with the key number labeled.
12. **Slide 3 — Mechanism.** Why the finding is what it is. A second chart or decomposition that shows the proximate driver. This is where most stories collapse if the team has not done the work; if the mechanism is genuinely unknown, say so and frame slide 3 as "what we are doing to find out."
13. **Slide 4 — Implication.** What changes if the finding is true. The bridge from "interesting" to "matters" — a forecast, a risk-adjusted impact, a counterfactual.
14. **Slide 5 — Action.** What we should do, by when, with which owner. The slide must contain a verb and a date. If the audience needs to make a decision, frame it as "we recommend X; we need a decision by Friday."

### 4. Compose Slide 1 — Claim

15. **Write the headline as a sentence, not a title.** "Enterprise churn doubled in Q1" beats "Q1 churn analysis."
16. **Make the magnitude unambiguous.** Absolute and relative; percentage points and percentage change are different and the listener will conflate them. Spell out which.
17. **Bound the claim.** "Among customers acquired before 2024" — without the boundary the listener generalizes.
18. **Choose a single supporting visual.** A big number with a sparkline, or a single chart with the headline annotated. Resist the urge to put the full analysis on slide 1; the chart on slide 1 should convey the magnitude in one second.
19. **Avoid hedging that undermines the claim.** "We may possibly be seeing an indication of" is a topic, not a claim. If the confidence is low, state confidence explicitly ("an early-warning signal, two months of data") rather than hedging the verb.

### 5. Compose Slide 2 — Evidence

20. **Choose the chart that most directly supports the claim.** Almost always a line chart for change-over-time findings; a bar chart for comparison findings; a slopegraph for two-period comparisons.
21. **Annotate the chart with the key number.** A line with "4% → 6%" labeled at the relevant points beats a clean unlabeled line.
22. **Include the comparison baseline visually.** Same chart, different period — or a horizontal reference line for plan / target.
23. **Show the denominator and sample size.** Particularly important when the audience is statistical or skeptical.
24. **Pre-empt the "what about [confound]?" objection.** If revenue rose alongside churn, show both. If a seasonal pattern explains part of the move, show seasonally-adjusted alongside raw.
25. **Avoid dual y-axes.** Use side-by-side panels or index-to-100 if two series must coexist.

### 6. Compose Slide 3 — Mechanism

26. **Identify the proximate driver.** One step deeper than the headline metric — usually a decomposition (churn = first-90-day churn + later-stage churn; revenue = price × volume; conversion = stage1 × stage2 × stage3).
27. **Show the decomposition visually.** A waterfall, a stacked bar, a funnel — whichever isolates the moving part.
28. **State the causal claim at the level of confidence you have.** "Correlated with" if you ran no experiment; "driven by" if you have causal evidence (RCT, regression discontinuity, instrument). The audience will conflate these unless you separate them on the slide.
29. **Acknowledge alternative explanations.** A one-line "alternatives we ruled out" bullet beats a question from the audience that you cannot answer.
30. **If the mechanism is unknown, label the slide accordingly.** "Mechanism — open" with a one-line "we are running a survey + experiment to confirm; results in three weeks" is a strong slide. A pretend mechanism that the audience will not believe is a terrible slide.

### 7. Compose Slide 4 — Implication

31. **Translate the finding into stakes the audience cares about.** Revenue, retention, runway, market share, customer trust. The right currency depends on the audience.
32. **Quantify the implication with a range, not a point estimate.** "$2-4M annual revenue at risk" beats "$3M at risk" because the listener accepts the range and challenges the point.
33. **Time-frame the implication.** Same quarter? Same year? Steady-state? Short-term implication and long-term implication are different stories.
34. **Identify the counterfactual.** What happens if we do nothing — the implication slide should make the counterfactual concrete.
35. **Connect to a strategic priority the audience already endorses.** "This puts our 2026 retention OKR at risk" anchors the implication in something the audience cares about; without it, the implication floats.

### 8. Compose Slide 5 — Action

36. **State the recommended action in one verb-led sentence.** "Pause the SMB-segment price increase until cohort retention recovers."
37. **Specify the decision required.** "We need approval to pause by Friday." A story without a deadline rarely closes.
38. **Name the owner.** Who will execute, who will report back.
39. **State the success criterion and review date.** "We will reassess on July 15 when cohort 90-day churn data is in."
40. **Offer at least one alternative considered.** "Alternative: continue the increase and absorb the churn — projected impact $2-4M annually." Showing the alternative anchors the recommendation as a choice, not a foregone conclusion.
41. **State what the audience should not decide today.** Boundaries make the request smaller and more likely to be approved.

### 9. Pacing and speaker notes

42. **Aim for 60–90 seconds per slide.** Five minutes total for a five-slide spine; ten minutes including questions.
43. **Write speaker notes as bullets, not paragraphs.** The presenter should not read; the bullets remind them of the beat.
44. **State the transition between slides.** "We saw the magnitude — let's look at why" — between slides 2 and 3.
45. **Rehearse the cuts.** If a slide does not fit in 90 seconds, it carries too much; move detail to backup slides.

### 10. Anticipate objections

46. **List the audience's likely objections in advance.** Common families: "is the data right?", "is the sample big enough?", "what about [confound]?", "have we seen this before?", "what would competitors do?", "what's the cost of the action?"
47. **For each objection, decide whether to address proactively (on a slide), in speaker notes (ready if asked), or via a backup slide.**
48. **Build two to three backup slides.** Detailed methodology, segment cuts, sensitivity analyses. They are not in the main spine but you reference them when challenged.

### 11. Make every visual carry weight

49. **No chart that does not support the slide's one job.** A pretty chart on slide 4 that does not directly demonstrate the implication is a distraction.
50. **Annotate every chart with the takeaway.** Numbers, arrows, text — the reader sees the takeaway before parsing the encoding.
51. **Use one consistent palette across the deck.** A single accent color for the focal metric; gray for context. Resist the rainbow.
52. **Keep one chart type per analytical task across the deck.** Switching from bar to dot plot mid-deck adds cognitive load with no payoff.

### 12. Compose the output

53. **Lead with the narrative arc.** One paragraph that walks the five beats. The presenter should memorize this.
54. **Specify each slide.** Title, key visual, supporting text, speaker-note bullets.
55. **Specify the chart for each data slide.** Encoding, sort order, annotations — at the level the chart-picker skill would produce.
56. **List the anticipated objections.** For each: when and how the story addresses it.
57. **Flag every assumption.** If the user did not provide the audience role, the action ask, or the confidence level, name the assumption.

### 13. Self-check before responding

58. **Confirm every slide does one job.** If a slide is doing two jobs, split or cut.
59. **Confirm the arc is Claim → Evidence → Mechanism → Implication → Action.** If you rearranged, defend the choice.
60. **Confirm the action slide contains a verb and a date.**
61. **Confirm the evidence slide can be defended at the audience's level of scrutiny.**
62. **Confirm the deck would still cohere if a slide were removed.** If yes, the slide may not be earning its place.

## Inputs

- The finding (one or two sentences with magnitude and segment).
- Supporting data, charts, or analyses.
- Audience description.
- Optional: the action being requested.

## Outputs

- A narrative arc paragraph.
- Five slide specs.
- Chart specs for the data slides.
- Anticipated objections and the story's response.

## Examples

**Example invocation**

> "Finding: enterprise churn rose from 4% to 6% in Q1 among customers acquired before 2024. Supporting data: cohort retention table, exit-survey codes (40% cited 'price'), our list-price increased 18% in November. Audience: CEO + exec team. We want approval to pause the price increase for the affected segment for one quarter."

**Expected high-level output**

Narrative arc: Q1 enterprise churn doubled (claim), driven by pre-2024 customers responding to the November price increase (mechanism). At current run-rate that is $3-5M annual ARR at risk (implication). Pause the increase for that segment this quarter; reassess July 15 (action).

Slide 1 — Claim: "Enterprise churn doubled in Q1 — 4% → 6%, concentrated in pre-2024 customers." Visual: big number 6%, sparkline of the last 8 quarters, segment label.

Slide 2 — Evidence: cohort retention curve for pre-2024 vs post-2024 customers, last 12 months, with November price-increase date marked. Annotation: "Pre-2024 cohort: −2pp; post-2024 cohort: −0.2pp."

Slide 3 — Mechanism: stacked bar of exit reasons by quarter; "price" segment grows from 22% to 40% of exits in Q1. Side annotation noting the November price-increase event.

Slide 4 — Implication: range chart — "$3-5M annual ARR at risk if Q1 run-rate continues, versus $1.5M revenue gain from the price increase." Net annual impact: −$1.5 to −$3.5M. Reference line for the 2026 retention OKR threshold.

Slide 5 — Action: "Pause the November price increase for pre-2024 enterprise customers through Q2." Decision required by Friday. Owner: VP Pricing. Reassess July 15 with full Q2 cohort retention. Alternative considered: maintain the increase, absorb the churn.

Anticipated objections: (1) sample size — answer: 600 enterprise customers in the affected segment, statistically significant at p < 0.01; (2) seasonality — answer: Q1 typically softer but the magnitude is 3× normal; (3) why not target only flight-risk accounts — answer: backup slide on the cost of a programmatic pause vs the operational cost of individual targeting.

## Limitations

- This skill produces the narrative spine; it does not generate finished slides in PowerPoint, Google Slides, or Keynote. Visual design is a downstream step.
- It assumes the finding has been analytically validated. If the underlying analysis is wrong, the story is wrong.
- For highly regulated communications (financial disclosures, public health), legal and compliance review is required and overrides storytelling preferences.
- The five-slide form is a forcing function. Longer narratives may need additional structure (e.g., a problem-statement slide before the claim); use the spine as the backbone and add slides only with a defended reason.
- It cannot substitute for the presenter's domain knowledge during Q&A; speaker notes and backup slides only prepare the presenter, they do not replace them.

## Sources reviewed

The methodology synthesized here draws on patterns observed across the following permissively licensed open-source repositories. None of the prose above is derived from any single source.

- https://github.com/d3/d3
- https://github.com/vega/vega-lite
- https://github.com/observablehq/plot
- https://github.com/plotly/plotly.py
- https://github.com/apache/superset
- https://github.com/mwaskom/seaborn
