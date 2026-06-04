---
id: skillsgit-curated/data-viz-critique
version: 1.0.0
name: Visualization Critique
description: Reviews a chart or dashboard for misleading axes, chartjunk, color and contrast issues, mis-encoding, missing context, and narrative gaps — producing a prioritized fix list.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:data-viz, viz-review, critique, chart-audit, accessibility, perception, dashboard-review]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - chart critique
  - dashboard review
  - viz review
  - misleading chart
  - chartjunk
  - axis truncation
  - color contrast
  - accessibility review
  - chart audit
  - visualization feedback
  - viz critique
example_invocations:
  - "Review this revenue bar chart — does anything mislead?"
  - "Critique my product dashboard before I share it with leadership."
  - "Is this dual-axis line chart fair?"
  - "Audit our public chart for accessibility issues."
inputs:
  - name: artifact
    type: text
    required: true
    description: A description, screenshot caption, image, link to the chart or dashboard, plus the underlying data shape if available.
  - name: intended_message
    type: text
    required: true
    description: What the author wants the reader to take away. The critique compares the chart's actual reading to this intended message.
  - name: audience
    type: text
    required: false
    description: Who the chart is for — affects which issues are severe versus cosmetic.
  - name: medium
    type: choice
    required: false
    description: Where the chart appears.
    choices: [interactive-web, static-print, slide-deck, mobile, email, public-press]
outputs:
  - name: severity_rated_issues
    type: markdown
    description: A list of issues ranked critical / major / minor, each with a one-line description, why it misleads, and a specific fix.
  - name: strengths
    type: markdown
    description: What works — kept short to avoid padding, but explicit so the author preserves it.
  - name: revised_takeaway
    type: markdown
    description: What the chart actually communicates as it stands, contrasted with the intended message.
  - name: rewrite_checklist
    type: markdown
    description: An ordered checklist the author can apply in one revision pass to address all critical and major issues.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when a user shares a chart, panel, or full dashboard and wants a structured critique before publishing or shipping. Typical situations:

- An author is about to share an internal chart with leadership and wants a sanity check.
- A team is reviewing a public-facing report and worried about misleading claims.
- A designer or analyst suspects something is off but cannot articulate it.
- A dashboard has accreted across multiple authors and needs a single coherent review pass.

Do not invoke this skill to rebuild the chart from scratch (use the chart picker), to design a new dashboard (use the dashboard architect), or to debate purely stylistic taste (color preferences without a perception or accessibility consequence).

## How to apply

The methodology is to read the chart twice — once as a reader sees it, once as a critic looking for known failure modes — then compare what the chart says to what the author intended.

### 1. Read the chart as a reader, not yet as a critic

1. **Look only at the chart for ten seconds.** No reading the surrounding text yet, no studying the legend, no zooming. What is the impression?
2. **Write down the takeaway.** One sentence: what does this chart say? Be honest — write the message the visual structure conveys, even if you suspect it is wrong.
3. **Compare to the stated intended message.** A gap between the two is the most important finding the critique will deliver. Many "minor" issues compound to produce that gap.
4. **Identify what made the gap.** Often it traces to one or two specific encoding or scale decisions. Note them; the rest of the methodology will confirm.

### 2. Audit the axes and scales

5. **Check for truncated y-axis on bar-length encodings.** Bars whose y-axis starts above zero are visually misleading because the bar length no longer encodes magnitude faithfully. Severity: critical. Fix: zero the axis or replace with a non-length encoding (dots, slopes).
6. **Check for truncated y-axis on line charts that hides flatness or exaggerates a small change.** Acceptable when annotated and when the audience reads trends, not magnitudes — flag for context. Severity: major when unannotated.
7. **Check for log-scale axes treated as linear.** A line chart on log scale showing exponential growth as a straight line is honest only when explicitly labeled. An unlabeled log axis is misleading. Severity: major.
8. **Check for inconsistent axis ranges across small multiples.** When the same metric is shown across panels, the y-axis should be shared unless each panel's local detail is the point. State which choice fits and call out the alternative.
9. **Check for double y-axes.** Two scales on one chart almost always misleads — the eye reads a relationship that is an artifact of the chosen ranges. Severity: critical. Fix: split into two adjacent panels or convert both series to index-to-100.
10. **Check for time axes that are not actually linear in time.** Equally spaced fiscal periods that compress vacation weeks; categorical time axes presented as continuous. Severity: major.
11. **Check for unlabeled axes.** No units, no scale, no zero indicator. Severity: critical for public charts, major for internal.
12. **Check for reversed axes.** Y-axis inverted in error (latency that improves going up) or political maps with non-standard orientation. Severity: critical.

### 3. Audit the encoding

13. **Check that the most important variable is on the most accurate channel.** Position is most accurate; then length on a common scale; then length not aligned; then angle; then area; then color saturation; then color hue. A critical metric encoded by color hue with twelve categories is mis-encoded.
14. **Check that bar-length encodings start at zero.** (Re-confirmed; this is the most common failure.)
15. **Check that area encodings are area, not radius.** A bubble whose diameter doubles has four times the area. If the author scaled by diameter expecting linear perception, the chart misreports magnitudes by squares.
16. **Check that 3D is absent for any quantitative encoding.** 3D bar / 3D pie / 3D ribbon distort magnitudes by perspective. Severity: critical.
17. **Check that pies have at most five slices and a single composition message.** Larger slice counts are illegible; multiple pies side by side to "compare composition" are nearly always better as stacked or grouped bars.
18. **Check that stacked bars do not require comparing the middle stacks.** Only the bottom stack has a common baseline; segments above it cannot be precisely compared. If the message depends on comparing the second segment, switch to grouped bars or 100% stacked.
19. **Check that line charts only connect data that are continuous.** Connecting discrete categorical values with a line implies an order that may not exist. Severity: major.
20. **Check that scatter plots are not hiding overplotting.** N > a few thousand points on a single scatter, with no transparency or 2D-density underlay, hides whatever the chart is meant to show.
21. **Check that the chosen chart type matches the analytical task.** Bar for compare, line for change-over-time, scatter for relationship, histogram for distribution. A bar chart of a distribution is mis-encoding.

### 4. Audit color

22. **Check categorical palettes have low cardinality (≤ 7).** Beyond that, colors become indistinguishable; replace with faceting.
23. **Check sequential palettes are perceptually uniform.** Rainbow / jet palettes are non-monotonic in lightness and obscure rank. Replace with viridis, magma, cividis, or any palette with documented uniformity.
24. **Check diverging palettes are used only for diverging data.** A diverging red/blue scale on data without a meaningful midpoint implies one that does not exist.
25. **Check contrast against background.** Light gray text on white, dark blue on black — fail. Use WCAG AA contrast ratios as the floor for any text or critical color encoding.
26. **Check colorblindness.** Eight percent of men have red-green color vision deficiency. Red versus green encoded categories will appear identical to them. Replace with palettes that retain distinction in deuteranopia and protanopia simulators.
27. **Check that color is not the only encoding.** A line distinguished only by hue fails for color-impaired readers and for grayscale print. Add shape, dash pattern, label, or position as a redundant channel.
28. **Check brand color does not overwhelm meaning.** A dashboard rendered entirely in one corporate hue obliterates the alert signal the same hue carries elsewhere.

### 5. Audit chartjunk and visual weight

29. **Check for redundant gridlines.** Heavy major and minor gridlines crossing every label make the chart noisy; one set of subtle gridlines suffices.
30. **Check for heavy borders around panels.** Borders consume visual weight without adding meaning.
31. **Check for dark drop shadows or background gradients.** Pure decoration; remove.
32. **Check for 3D effects and bevels.** Remove. (Restated; especially common in slide decks.)
33. **Check the data-ink ratio.** Whitespace and gridlines should not dominate the data marks themselves; if removing ink would not change the chart's reading, remove it.
34. **Check that the legend is not a lookup task.** Direct labels on lines and small-multiple panels beat a separate legend the reader must shuttle between.
35. **Check that text size is legible at the chart's display medium.** Twelve-point on a slide projected at the back of a conference room is unreadable.
36. **Check that long category labels are not rotated 45° or 90°.** Switch to horizontal bars.

### 6. Audit titles, labels, and context

37. **Check the title states a takeaway, not a topic.** "Revenue Q3 vs Q2" is a topic; "Q3 revenue is up 12%, driven by EMEA" is a takeaway. Public and executive charts benefit substantially from takeaway titles.
38. **Check units are present everywhere they could be ambiguous.** Dollars vs euros, percentage vs basis points, raw counts vs per-capita.
39. **Check the data source is named.** A chart with no source attribution is not trustable.
40. **Check the time range is unambiguous.** "Last 12 months" relative to what? Use absolute dates.
41. **Check that the comparison is shown when a delta is claimed.** If the title says "up 12%," the chart must show the comparison period or carry the comparison as an explicit annotation.
42. **Check the sample size or denominator is visible when proportions are shown.** A pie of two responses out of two is not the same as two thousand out of two thousand.
43. **Check missing data is annotated, not silently dropped.** Gaps in a line are explicit; gaps that get connected over a missing month lie to the reader.

### 7. Audit narrative and framing

44. **Check the chart matches the claim in surrounding text.** A caption that says "revenue grew steadily" does not match a chart that clearly shows two months of decline.
45. **Check for cherry-picked time ranges.** "Five-year growth" starting at a known trough is a framing choice; flag it.
46. **Check for cherry-picked baselines.** Indexed-to-100 charts that pick a baseline favorable to the author distort.
47. **Check for survivorship bias in the data.** A "top performing funds since 2010" chart shows only the survivors; flag it.
48. **Check that aggregations match the message.** A statement about typical customer behavior backed by a mean when the distribution is heavily skewed should use a median or distribution view.
49. **Check that causation is not implied where only correlation is shown.** Arrows and annotations should describe the observed pattern, not infer a cause the chart cannot demonstrate.

### 8. Audit accessibility

50. **Check that the chart has a text alternative.** Screen readers should be able to convey the headline number and the trend without rendering the visual. Provide ALT text or a structured-table fallback for the web.
51. **Check that interactive elements are keyboard-navigable on the web.** Tab order, focus styles, and ARIA roles for filters and hover information.
52. **Check that hover-only information has a non-hover fallback.** Mobile and keyboard users cannot hover; precise values must be reachable another way.
53. **Check that animation respects motion-reduction preferences.** Heavy transitions that ignore prefers-reduced-motion fail accessibility expectations.

### 9. Audit performance and resilience (for dashboards)

54. **Check the dashboard's first-paint behavior on a typical connection.** A spinner for thirty seconds before the headline panel renders is a critical issue.
55. **Check loading states.** Each panel needs a visible loading state, not a blank rectangle.
56. **Check error states.** Failed panels must explain what failed.
57. **Check empty states.** Fresh tenants or filtered-to-nothing views need guidance, not a wall of zeros.
58. **Check that high-cardinality dropdowns are searchable.** A region selector with 200 entries needs type-to-find, not a scrolling pick.

### 10. Rate, prioritize, and compose the output

59. **Rate each issue critical / major / minor.** Critical means the chart misleads or is unreadable for the intended audience. Major means it materially weakens the message or fails an accessibility floor. Minor means it lowers polish without changing comprehension.
60. **List the critical issues first.** The reader of the critique will skim; lead with what matters.
61. **For each issue, write a one-line fix.** The author should be able to apply the fix without re-reading the methodology.
62. **State the revised takeaway as written.** What the chart will say after the critical and major fixes — and how that compares to the intended message.
63. **State the strengths.** Anchor the author in what to keep. Be specific ("the small-multiple layout makes regional patterns easy to scan") rather than generic ("nice chart").
64. **Produce a rewrite checklist.** An ordered list of fixes, dependencies between them, and a one-line confirmation criterion per fix.

### 11. Self-check before responding

65. **Confirm every issue has a concrete fix, not just a diagnosis.**
66. **Confirm severity matches consequence, not aesthetic preference.** A non-uniform color palette in an internal exploration is a minor; in a public press chart it is a major.
67. **Confirm the revised takeaway is plausible after the fixes.** If applying the fixes still leaves the chart unable to support the intended message, the chart type itself is wrong — say so.
68. **Confirm there are no missing categories.** Did you skip axes? Color? Narrative framing? Accessibility?

## Inputs

- The artifact (chart description, image, or link) plus its underlying data shape if available.
- The author's intended message in one or two sentences.
- Optional: audience and medium.

## Outputs

- Issues rated critical / major / minor, each with description, why-it-misleads, and a fix.
- Strengths to preserve.
- The revised takeaway after fixes, compared to the intended message.
- A rewrite checklist.

## Examples

**Example invocation**

> "Review this chart: a 3D pie with seven slices showing market share of streaming services, title 'We are winning'. Intended message: our service is leading the market."

**Expected high-level output**

Critical issues: (1) 3D pie distorts areas; front-facing slices appear larger regardless of value — fix: replace with a sorted horizontal bar chart. (2) Seven slices on a pie exceed the legibility limit — fix: sort by share, label values directly. (3) Title "We are winning" claims market leadership but pie slices are visually similar; the chart does not support the claim — fix: re-title with the actual numeric lead ("Our service holds 28% share, ahead of #2 at 22%").

Major issues: missing source attribution; missing time period; color palette uses red and green for two adjacent competitors (colorblind hazard).

Minor: drop shadow on pie; legend placed bottom-right requiring lookup.

Revised takeaway after fixes: "Of seven streaming services, ours holds 28% share — six points ahead of the nearest competitor — over the 12 months ending Q1 2026." Matches intended message and is defensible.

Strengths: includes all seven competitors rather than cherry-picked subset; data is current.

## Limitations

- This skill critiques visual encoding and narrative framing. It does not verify the underlying data is correct — bad numbers cannot be fixed by chart redesign.
- For domain-specific charts (medical, financial, scientific) with established conventions, those conventions override the general advice here.
- Accessibility checks are heuristic; a formal WCAG audit requires tooling and human verification.
- The critique assumes a single chart or dashboard. It is not a substitute for a usability study with real readers.
- Brand-system conformance is intentionally out of scope; the brand can be applied after the encoding is correct.

## Sources reviewed

The methodology synthesized here draws on patterns observed across the following permissively licensed open-source repositories. None of the prose above is derived from any single source.

- https://github.com/d3/d3
- https://github.com/vega/vega-lite
- https://github.com/observablehq/plot
- https://github.com/plotly/plotly.py
- https://github.com/mwaskom/seaborn
- https://github.com/altair-viz/altair
- https://github.com/apache/superset
