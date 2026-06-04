---
id: skillsgit-curated/data-viz-chart-picker
version: 1.0.0
name: Chart Picker
description: Given a data shape and an analytical task (compare, composition, distribution, relationship, change over time), recommend the appropriate chart with rationale, encoding choices, and anti-patterns to avoid.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:data-viz, chart-selection, encoding, visualization, exploratory-analysis, perception, dashboards]
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
  estimated_tokens_per_invocation: 4500
trigger_keywords:
  - chart type
  - which chart
  - visualization choice
  - chart selection
  - bar vs line
  - pie chart
  - scatter plot
  - heatmap
  - encoding
  - data viz
  - chart picker
  - viz recommendation
example_invocations:
  - "I have weekly revenue for 12 product lines over 24 months — what's the right chart?"
  - "Should I use a pie chart for browser market share?"
  - "How do I show the relationship between price and conversion rate across 200 SKUs?"
  - "What chart fits this dataset: status counts across five categories and three regions?"
inputs:
  - name: data_shape
    type: text
    required: true
    description: A description of the dataset — number of records, variable names with types (categorical, ordinal, continuous, temporal), cardinality per categorical, time granularity if any.
  - name: analytical_task
    type: choice
    required: true
    description: The primary question the chart must answer.
    choices: [compare, composition, distribution, relationship, change-over-time, ranking, deviation, geospatial, flow]
  - name: audience
    type: choice
    required: false
    description: Who reads the chart.
    choices: [analyst-exploratory, executive-summary, public-report, operational-dashboard, scientific-paper]
  - name: medium
    type: choice
    required: false
    description: Where the chart will appear.
    choices: [interactive-web, static-print, slide-deck, mobile, email]
outputs:
  - name: primary_recommendation
    type: markdown
    description: One recommended chart with rationale linking the data shape and task to the encoding choices.
  - name: alternatives
    type: markdown
    description: One or two viable alternatives with the trade-offs that distinguish them from the primary recommendation.
  - name: anti_patterns
    type: markdown
    description: Chart types that look reasonable but will mislead for this data shape, with the specific failure mode.
  - name: encoding_spec
    type: markdown
    description: A concrete encoding specification (which variable maps to x, y, color, size, facet, sort order) the implementer can hand to any charting library.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when a user has a dataset (or a clear description of one) and an analytical question, and needs to choose a chart type. Typical situations:

- The user has tried one chart, it feels wrong, and they want a second opinion before iterating.
- The user is staring at a fresh dataset and does not yet know what visual form will reveal the answer.
- The user is building a dashboard or report and must pick one chart per panel from a small budget of attention.
- A stakeholder has requested a specific chart (often "let's just use a pie chart") and the user wants to confirm or push back with a defensible alternative.

Do not invoke this skill purely to debate aesthetic preferences (e.g., "do you like blue or green?"). Do not invoke it to build statistical models, perform forecasts, or compute statistics — this skill is about visual encoding only; the data has already been prepared.

## How to apply

The methodology is decision-driven, not aesthetic. Each step pares the option space until exactly one chart is the natural fit, with one or two backup choices documented for context.

### 1. Parse the data shape rigorously

1. **Restate the dataset in normalized form.** Even if the user gives a paragraph, internally re-state it as: number of rows, list of columns with type for each (categorical with cardinality K, ordinal with K levels, continuous with range, temporal with granularity, geographic with hierarchy level), and whether the data is tidy long-form or wide-form. If anything is unclear, ask before recommending.
2. **Count the variables that will be encoded.** A "two-variable" chart and a "five-variable" chart are entirely different problems. Tally categorical, ordinal, continuous, and temporal separately.
3. **Note cardinality.** A categorical with three values can be shown as a bar; a categorical with three thousand values cannot, regardless of task. Cardinality changes the recommendation.
4. **Note whether values can be negative.** Bars showing both positive and negative deviations need a different layout (diverging) than purely positive bars.
5. **Note whether categories sum to a meaningful whole.** Composition charts presume a meaningful whole (a budget, a population). Comparing four products that do not represent the total market is not a composition problem.
6. **Identify the temporal axis if present.** Is time a single ordered axis (line chart territory), a cyclical axis (radial or seasonal subseries), or a sequence of snapshots (small multiples)?

### 2. Clarify the analytical task

7. **Force the task into one of nine families.** Most ambiguity collapses once the task is named:
   - **Compare** — which is bigger / smaller across discrete things.
   - **Composition** — what shares make up a whole.
   - **Distribution** — how values spread across a continuous range.
   - **Relationship** — how two or more continuous variables co-vary.
   - **Change over time** — how a value trends.
   - **Ranking** — explicit ordered list, top-N or bottom-N.
   - **Deviation** — how each value differs from a reference (zero, target, prior period).
   - **Geospatial** — values located on a map.
   - **Flow** — quantities moving between states or nodes.
8. **Reject compound tasks.** "Compare composition over time across regions" is three tasks; pick the primary one and address the others through faceting or a separate chart. The reader's eye can answer one question per chart well; trying to answer three answers none.
9. **Identify the comparison unit.** "Compare" means compare what — categories, time periods, scenarios, against a target? The answer determines whether bars, slopegraphs, or bullet charts apply.

### 3. Map (data shape × task) to chart family

The crux of the method. Use the following mapping. When the input does not match a row cleanly, prefer the row whose data shape matches and call out the task mismatch in the rationale.

10. **Compare across few categories (K ≤ 10), one measure.** Use a bar chart. Horizontal bars when category labels are long or numerous; vertical bars when categories are short and the visual sequence is meaningful. Order bars by value unless the categorical is intrinsically ordered (months, quartiles, NPS bands).
11. **Compare across many categories (K > 30), one measure.** Use a horizontal bar chart with sort by value and consider a top-N + "other" rollup. Avoid rotated 45° labels on vertical bars.
12. **Compare across two categorical dimensions, one measure.** Use a heatmap if both cardinalities are moderate (e.g., 5 × 10), or a grouped/stacked bar chart if one cardinality is small (≤ 3 groups). If one dimension is time, prefer faceted lines.
13. **Composition with one whole, few parts (K ≤ 5).** A simple bar chart or a horizontal stacked bar will outperform a pie chart for precision. A pie is acceptable only when parts are vastly different in size, there are ≤ 4 slices, and the audience expects "share of total" framing (executive dashboards, news graphics).
14. **Composition over time.** Use a stacked area chart for continuous time and stacked bars for discrete periods. Switch to a stream graph only when the audience values shape over precision (popular-science context). For change in share, use a 100% stacked area or, more precisely, faceted small-multiple lines of each part's share.
15. **Distribution of one continuous variable, single group.** Histogram (binned) or density plot. Histograms are easier for non-technical audiences; density plots are smoother for analysts.
16. **Distribution of one continuous variable across several groups (K ≤ 8).** Box plots, violin plots, or strip / jitter plots overlayed with summary marks. Box plots when the audience is statistically literate; violins when shape matters; strip plots when N per group is small enough to show every point.
17. **Distribution across many groups.** A ridgeline plot (a.k.a. joyplot) or a faceted small-multiple histogram. Avoid stacking many violins in one panel.
18. **Relationship between two continuous variables.** Scatter plot. Add a smoothed trend (LOESS or linear) when overall direction matters. Use a 2D density / hexbin when N is large enough that overplotting hides structure (typically N > 5,000).
19. **Relationship between three continuous variables.** A scatter plot with size or color as the third encoding. Do not encode it as a 3D rotation — perception of 3D positions on a 2D screen is unreliable. For more than three continuous variables, use a small-multiple scatter matrix (pair plot) or a parallel-coordinates plot.
20. **Change over time, one series.** A line chart. Use bars only when the time axis is discrete (months, fiscal quarters) and the audience reads each period as a separate event rather than a continuous trend.
21. **Change over time, few series (K ≤ 5).** A multi-line chart with direct labels (no legend lookup). Distinguish lines with hue and emphasis (one focal line darker, others gray) when one series is the focus.
22. **Change over time, many series (K > 5).** Small-multiple line charts, one panel per series, with a faint gray ghost of all series in each panel for context. A spaghetti chart with all lines stacked rarely communicates anything.
23. **Change over time, two snapshots only.** A slopegraph (paired points connected by a line, one per category) outperforms paired bars for showing direction and magnitude of change simultaneously.
24. **Ranking with explicit ordinal output.** Ordered horizontal bar chart, sorted, with the top-N labeled. Dot plots (Cleveland dot plot) work well when comparing across two periods on the same ranking.
25. **Deviation against a single reference.** A diverging bar chart (zero in the middle), or a bullet chart for performance-vs-target. Heatmaps with a diverging color palette work for deviation across two categorical axes.
26. **Geospatial, region-aggregated.** Choropleth map with a sequential color scale for magnitude and a diverging scale for deviation. Always include a legend that is itself perceptually uniform. Use a cartogram when region areas distort the data severely (electoral results).
27. **Geospatial, point-located.** Dot map or bubble map for counts; consider hex binning for dense point clouds.
28. **Flow between nodes.** Sankey diagram for clearly quantitative flow; chord diagram for symmetric flow (A↔B). Avoid Sankeys when more than ~15 nodes per side make labels collide.

### 4. Choose the encodings within the chart

29. **Map the most important variable to position (x or y).** Position is the most accurate visual encoding human perception offers; reserve it for the variable the reader most needs to compare precisely.
30. **Map a categorical with low cardinality (K ≤ 7) to hue when needed.** Use a qualitative palette. Above 7, replace hue with faceting (small multiples) or sequential gray + direct label.
31. **Map an ordered or numeric variable to a sequential color palette.** Choose one with perceptually uniform lightness steps (viridis, magma, cividis families). Never use rainbow palettes for ordered data; lightness is non-monotonic and obscures rank.
32. **Map deviation from a reference to a diverging palette.** Two hues meeting at a neutral midpoint, e.g., red↔blue or orange↔purple.
33. **Reserve size for one continuous variable when position is already used.** Size encoding is best for unsigned magnitudes and is roughly half as accurate as position. Cap the size range so the smallest dot is still visible and the largest does not crowd neighbors.
34. **Avoid encoding more than four variables at once.** Position-x, position-y, color, and one of {size, facet} is the upper bound for a single panel. Beyond that, use small multiples or a second chart.
35. **Choose explicit sort orders.** Default to descending value for nominal categories (so the reader sees the top item first). Preserve intrinsic order for ordinal categories. Sort small multiples by panel summary statistic when comparing across panels.
36. **Set axis ranges thoughtfully.** Bar charts must start at zero (their length encodes magnitude). Line charts may start above zero when zero is irrelevant and obscures the trend — but flag this to the user as a perception trade-off.

### 5. Identify anti-patterns for this exact case

37. **3D bars / 3D pies.** Always reject. Foreshortening distorts the very magnitudes the chart is meant to communicate.
38. **Dual y-axes with two scales.** Almost always misleading; the implied correlation is an artifact of independent axis ranges. Replace with two panels or with index-to-100 lines.
39. **Pie with more than five slices.** Replace with a sorted bar.
40. **Stacked bars when the comparison is the second-category value (not totals).** The second segment up has no shared baseline and cannot be compared precisely. Use grouped bars or 100% stacked instead.
41. **Truncated y-axis on a bar chart.** Visually exaggerates differences; never permitted on bars. Acceptable only on lines when explicitly annotated.
42. **Rainbow color scales for sequential data.** Replace with a perceptually uniform palette.
43. **Spaghetti line charts (more than ~7 lines stacked).** Replace with small multiples or a focal/context emphasis.
44. **Choropleth with raw counts (not normalized).** A population map will always look like population. Normalize per capita (or per relevant denominator) and state the denominator.
45. **Word clouds for any analytical purpose.** Word clouds encode frequency by font size; perception of area is unreliable, ordering is implicit, and comparisons are impossible. Replace with a sorted bar of top terms.
46. **Polar / radar charts for general comparison.** Angle and radius are hard to compare. Acceptable only for cyclical data (24-hour, monthly seasonality) and only when shape itself is the message.

### 6. Adapt to audience and medium

47. **Executive summary.** Single chart with one clear message in the title (e.g., "Q4 revenue grew 12%, driven by EMEA"), generous whitespace, no chartjunk, no legend lookups. Direct-label every line.
48. **Analyst-exploratory.** Density of information matters more than clarity at a glance; small multiples and overlaid statistics are welcomed.
49. **Public report.** Assume one chance to communicate; default to the most common chart form (bars, lines) and resist novel forms. Add a sentence-long caption that states the takeaway.
50. **Operational dashboard.** Optimize for fast scanning, monotone palettes with a single alert color reserved for thresholds, sparkline + value pairs over full-size charts when space is tight.
51. **Scientific paper.** Precise axis labels with units, statistical annotations (CI bands, error bars), monochrome-safe palettes, and explicit sample sizes.
52. **Mobile / small-screen.** Reduce to one or two encodings; long horizontal scrolls beat squashed labels. Replace small multiples with a swipeable carousel where the platform supports it.
53. **Static print.** Test in grayscale; reserve hue only for categorical distinction the figure can lose to a photocopier.

### 7. Compose the output

54. **Lead with the primary recommendation.** One chart, named, with one or two sentences linking the data shape and task to the choice.
55. **State the encoding spec explicitly.** Variable name → channel (x, y, color, size, facet, sort). The implementer should be able to write the chart in any library from this spec alone.
56. **List one or two alternatives.** For each, give the trade-off that would make it preferable (e.g., "use stacked area instead if the audience cares about total as well as composition").
57. **List the anti-patterns specific to this case.** Not generic warnings — the actual mistakes a reader is likely to make given this dataset.
58. **Flag the assumptions you made.** If the user did not specify cardinality, audience, or whether categories sum to a whole, name the assumption.
59. **Recommend one labeling and annotation move.** A direct label, a reference line, an annotation arrow on the key data point. The skill is not done at "use a bar chart" — it ends at "use a bar chart sorted descending with the top bar annotated `+12% YoY`".

### 8. Self-check before responding

60. **Re-read the user's question.** Did you answer the question they asked, or a question you preferred?
61. **Walk the recommended chart through the task in your head.** Can the reader actually answer the analytical task with the encoding you specified? If not, revise.
62. **Confirm the recommended chart respects perceptual hierarchy.** Position > length > angle/area > color saturation > color hue. The most important variable should be on the most accurate channel.
63. **Confirm cardinality fits.** Did you accidentally recommend a chart that breaks down at the user's K?
64. **Confirm zero baselines and axis truncation choices.** Bars from zero; lines explicitly flagged if truncated.

## Inputs

- A description of the dataset shape: row count, columns with types, cardinalities, time granularity.
- The analytical task, one of the nine families.
- Optional: audience and medium.

## Outputs

- A primary chart recommendation with rationale.
- One or two alternative charts with the trade-offs that would prefer them.
- A concrete encoding spec.
- Anti-patterns specific to the dataset.
- Open questions if input was incomplete.

## Examples

**Example invocation**

> "I have monthly revenue and gross margin percentage for 8 product lines over 36 months. I want to show executives how each line is trending and where margin is compressing."

**Expected high-level output**

Primary: small-multiple line chart, one panel per product line (8 panels, 4×2 grid), x = month, y = revenue, secondary thin line = gross margin percentage on a separate panel-internal axis with explicit legend. Panels sorted by latest revenue descending. A faint gray ghost line of total revenue in every panel for reference.

Alternative: a single focal line chart of total revenue with 8 product-line sparklines arrayed beside it; preferable when the audience cares about total above all and product lines are context.

Anti-patterns to avoid: spaghetti line chart with all 8 lines and margin on a dual axis; stacked area chart (hides individual product-line shapes); 3D ribbon plot.

Encoding spec: x = `month` (temporal), y = `revenue` (continuous, zero-baseline), facet = `product_line` (categorical, K=8), color = focal (gray for context, single accent for the line in the active panel), annotation = arrow + label on the largest month-over-month decline.

## Limitations

- This skill recommends chart types and encodings; it does not generate code. Implementation in D3, Vega-Lite, Plotly, ggplot2, matplotlib, or Observable Plot is downstream.
- It assumes data is already prepared (tidy, units harmonized, missing values handled). Bad inputs cannot be rescued by chart choice.
- It cannot evaluate aesthetic fit with a brand system; brand styling is overlaid after the encoding is correct.
- It does not compute the statistics underlying the chart (forecasting, smoothing parameters, statistical tests); those are upstream tasks.
- For specialized scientific charts (phylogenetic trees, manhattan plots, RNA-seq heatmaps), domain conventions override the general advice here.

## Sources reviewed

The methodology synthesized here draws on patterns observed across the following permissively licensed open-source repositories. None of the prose above is derived from any single source.

- https://github.com/d3/d3
- https://github.com/vega/vega-lite
- https://github.com/observablehq/plot
- https://github.com/plotly/plotly.py
- https://github.com/mwaskom/seaborn
- https://github.com/altair-viz/altair
- https://github.com/apache/superset
- https://github.com/airbnb/visx
