# Data — Visualization & Dashboards: Synthesis Report

## Files produced

1. `data-viz-chart-picker.skills.md` — license_type: free. 8 sources cited.
2. `data-viz-dashboard-architect.skills.md` — license_type: free. 8 sources cited.
3. `data-viz-critique.skills.md` — license_type: free. 7 sources cited.
4. `data-viz-storytelling-builder.skills.md` — license_type: free. 6 sources cited.

All four are 100% original prose synthesizing patterns observed across permissively licensed visualization libraries and dashboard tools. Body lengths sit between ~310 and ~430 lines (within the 300-700 range).

## Sources accepted (license verified, ≥100 stars, active within 18 months)

| Repo | License | Stars (approx) | Used in |
|---|---|---|---|
| d3/d3 | BSD-3-Clause | ~110k | chart-picker, dashboard-architect, critique, storytelling |
| vega/vega-lite | BSD-3-Clause | ~4.5k | chart-picker, dashboard-architect, critique, storytelling |
| observablehq/plot | ISC | ~4k | chart-picker, dashboard-architect, critique, storytelling |
| plotly/plotly.py | MIT | ~16k | chart-picker, critique, storytelling |
| mwaskom/seaborn | BSD-3-Clause | ~12k | chart-picker, critique, storytelling |
| altair-viz/altair | BSD-3-Clause | ~9k | chart-picker, critique |
| apache/superset | Apache-2.0 | ~62k | chart-picker, dashboard-architect, critique, storytelling |
| airbnb/visx | MIT | ~19k | chart-picker, dashboard-architect |
| plotly/dash | MIT | ~21k | dashboard-architect |
| streamlit/streamlit | Apache-2.0 | ~36k | dashboard-architect |
| holoviz/panel | BSD-3-Clause | ~5k | dashboard-architect |

Per-skill source counts: chart-picker 8, dashboard-architect 8, critique 7, storytelling 6 — all within the 5–10 range.

## Rejected candidates

- **grafana/grafana** — AGPL-3.0 from version 8 onward. Not in the allowed permissive set (free/MIT/Apache-2.0/BSD/ISC/Unlicense only). Rejected.
- **metabase/metabase** — AGPL-3.0. Rejected.
- **highcharts/highcharts** — proprietary commercial license. Rejected.
- **microsoft/powerbi-* repos** — proprietary or sample-only. Rejected.
- **tableau/* repos** — most under Tableau license, not permissive. Rejected.
- **plotly/plotly.js** — MIT, eligible, but excluded from chart-picker/critique citation lists in favor of higher-signal repos to stay within the 5–10 ceiling per skill.
- **chartjs/Chart.js** — MIT, ~64k stars, eligible but omitted from final lists for the same ceiling reason; well-represented in spirit by the other JS libraries.
- **bokeh/bokeh** — BSD-3-Clause, eligible, omitted for the ceiling reason; Python BI is already covered by Plotly, Seaborn, Altair, Streamlit, Panel.

## Key patterns observed across sources

### Chart selection (chart-picker)
- **Data shape × task drives the chart, not aesthetics.** Every reviewed grammar-of-graphics library (Vega-Lite, Altair, ggplot2-style, Observable Plot, seaborn's high-level API) frames the chart as a mapping from variables to channels — never as a catalogue of named "chart types" first.
- **Position is the most accurate visual channel; reserve it for the most important variable.** This perceptual hierarchy is implicit in every library's default encoding picks.
- **Default to small multiples over multi-line spaghetti for many-category change-over-time.** Universal across the libraries' example galleries.
- **Pie charts limited to ≤5 slices and only for composition-of-a-whole.** Either explicit in docs or absent from gallery examples in favor of sorted bars.

### Dashboard composition (dashboard-architect)
- **Twelve-column grid + responsive breakpoints** is the de facto layout primitive across Superset, Dash, Streamlit, and Panel UI conventions.
- **Top-left for the headline panel; ≤9 panels per canvas** is a recurring "less is more" pattern, with tabs and drill-downs for secondary detail.
- **Caching and materialization at the panel level** — Superset's caching layers, Dash's `dcc.Store` patterns, Streamlit's `@st.cache_data` — point to the same architectural conclusion: do not run interactive aggregations for headline metrics.
- **Default filters that show value immediately** — fresh dashboards with required-no-default filters are an anti-pattern noted across BI tool docs.

### Critique heuristics (critique)
- **Zero-baseline for bars; truncation only for line charts and only annotated.** Universal.
- **Reject dual y-axes by default.** Reinforced across docs and example galleries.
- **Perceptually uniform sequential palettes (viridis family) replace rainbow.** Now a library default in matplotlib, plotly, seaborn, altair, and Vega.
- **Avoid color-only encoding** — accessibility checklists across the visualization libraries converge on adding shape, label, or position as redundant channels.
- **Annotate the chart, do not just plot it.** Direct labeling beats legend-lookup in every example gallery.

### Narrative arc (storytelling)
- **Claim → Evidence → Mechanism → Implication → Action** is a fixed five-beat arc compatible with both analytical (Vega/Plotly notebook examples) and BI (Superset dashboard tour) framings.
- **Annotated charts with the takeaway in the title.** Example galleries consistently show titles that state findings, not topics.
- **Pre-empt the first objection on the evidence or mechanism slide.** Common pattern in case-study repos and notebook examples.

## Confidence per skill

- **Chart Picker — high confidence.** The data-shape × task mapping is highly stable across all reviewed grammar-of-graphics libraries; the recommendation logic encodes consensus that has held for ~15 years (since Wilkinson's framework was popularized by ggplot, then Vega-Lite, then Plot).
- **Dashboard Architect — high confidence on structure, medium on platform specifics.** The audience-decision-grid-interactivity-performance loop is consistent across Superset, Dash, Streamlit, Panel docs. Platform-specific implementation details (e.g., exact Superset caching toggles) are intentionally not encoded — the skill is platform-agnostic.
- **Visualization Critique — high confidence.** Failure modes are heavily replicated across library issue trackers, gallery examples, and accessibility guides. The severity rubric is the most subjective element and is documented as such.
- **Data Storytelling Builder — medium-high confidence.** The five-slide arc is robust but stylistic; teams from different backgrounds (consulting, science, journalism) sometimes prefer different orderings. The skill defends the order and surfaces it as an assumption.

## Follow-ups worth considering

- A separate "dashboard-perf-fixer" skill focused exclusively on slow-dashboard diagnosis (cache warming, materialized views, lazy panels, query simplification). Not produced in this batch to keep scope tight; warranted if user demand surfaces.
- A complementary "color-system-for-data-viz" skill that specifies palette construction beyond what the critique skill flags. Currently absorbed into critique + chart-picker; could split out.
- A "geospatial-viz" specialist skill for choropleth, cartogram, and dot-density specifics — current chart-picker handles geospatial as one of nine task families but could go deeper.
- All four skills currently target the Claude Opus 4.7 / Sonnet 4.6 family; should compatibility be re-verified against new model releases, the `compatible_models` list will need a refresh.

## Notes on merge / overlap with existing data skills

The three existing data skills in `synth/` cover **schema design, dbt patterns, and migrations** — orthogonal to visualization. No merge needed. Tag overlap is minimal (only `data` and `analytics`); the new `niche:data-viz` first-tag cleanly partitions the new files from the existing data-engineering skills.
