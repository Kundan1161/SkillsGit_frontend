---
id: skillsgit-curated/factor-research-pipeline-architect
version: 1.0.0
name: Factor Research Pipeline Architect
description: Design a factor-research pipeline — data hygiene, point-in-time correctness, factor construction, look-ahead avoidance, multi-period backtest, robustness, and decay analysis.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: finance
tags: [niche:open-financial-analytics, factor-research, quant-pipeline, point-in-time, backtesting, signal-decay, robustness, look-ahead-bias]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: [code_execution]
  tools_optional: [web_search, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 12000
trigger_keywords:
  - factor research
  - factor pipeline
  - alpha factor
  - point in time data
  - look ahead bias
  - signal decay
  - factor backtest
  - information coefficient
  - quintile spread
  - factor robustness
  - cross-sectional factor
  - factor portfolio
example_invocations:
  - "Design a factor-research pipeline for a value-quality composite on US equities."
  - "Lay out how to build a point-in-time fundamentals pipeline that won't leak."
  - "Architect a robustness-and-decay framework for a momentum factor across sectors."
inputs:
  - name: factor_idea
    type: text
    required: true
    description: The candidate factor or factor family being researched (e.g., "earnings revisions momentum on global mid-caps").
  - name: universe
    type: text
    required: true
    description: The investable universe — region, market-cap band, sector inclusions/exclusions, liquidity floor.
  - name: data_inputs
    type: text
    required: true
    description: The data sources that will feed the factor — price, fundamentals, estimates, alternative data, corporate actions.
  - name: rebalance_frequency
    type: choice
    required: false
    description: How often the factor portfolio rebalances.
    choices: [daily, weekly, monthly, quarterly, annual]
  - name: horizon_targets
    type: text
    required: false
    description: The forward-return horizons of interest — 1-day, 5-day, 1-month, 3-month, 12-month.
outputs:
  - name: pipeline_design
    type: markdown
    description: A stage-by-stage pipeline design from raw data to backtested factor portfolio, with the contract at each stage.
  - name: pit_protocol
    type: markdown
    description: A point-in-time data protocol that prevents look-ahead bias.
  - name: backtest_design
    type: markdown
    description: A multi-period, multi-cut backtest design with information coefficient, quantile spread, turnover, and decay diagnostics.
  - name: robustness_plan
    type: markdown
    description: A robustness program — perturbations, subsamples, regimes, transaction costs, and capacity tests.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Reach for this skill when a researcher or team needs to design a pipeline that turns a candidate factor idea into a defensible, reproducible, and decay-aware analysis. The skill is calibrated for the design stage — the stages, the contracts between stages, the diagnostics that get run, the failure modes that the design guards against — rather than for running a specific factor or producing a single backtest.

Use this skill when the user can name the factor idea, the universe, and the data inputs they have access to. Use it when the goal is to build a pipeline that will survive transition from research to a paper portfolio to (potentially) deployment with careful capacity and cost analysis. The skill is built to surface the dozens of small choices that determine whether a factor that looks alive in research stays alive in production.

Do not use this skill for high-frequency or microstructure-driven strategies — the pipeline assumes the holding period is days or longer and that intraday execution detail is not the source of edge. Do not use it for discretionary equity research (a companion skill covers that workflow). Do not use it for portfolio construction beyond simple quantile or rank-weighted long-short portfolios; production-grade portfolio optimization, risk-model integration, and capacity-aware execution belong to a downstream stage that this pipeline feeds into.

All outputs are educational and methodological. Backtests are historical reconstructions and are not predictions; nothing produced by this skill is investment advice. Any deployment of a strategy designed using this skill requires independent validation, compliance review, and risk approval appropriate to the user's firm and jurisdiction.

## How to apply

A factor-research pipeline is a series of stages with explicit contracts between them. The contracts matter more than the implementations. A pipeline whose stages are clean but whose contracts are loose produces results that move around when the implementation is touched. A pipeline whose contracts are tight is reproducible, falsifiable, and survives the transitions that production demands.

The skill organizes the pipeline into ten stages. Each stage has inputs, outputs, and a small set of guardrails. The order matters; later stages presume the integrity of earlier stages.

### Stage 1 — Universe definition

The universe is the population of securities over which the factor will be ranked and the portfolio constructed. Get this wrong and everything downstream is wrong in ways that are hard to detect.

Make the universe definition fully time-varying. At every rebalance date, the universe is "the set of securities that, on that date and using only information available on or before that date, met the inclusion criteria." Common criteria:

- **Listing region or exchange** — accounting for cross-listed shares and dual classes.
- **Market capitalization band** — using a defined snapshot rule (typically the prior month-end shares outstanding times the prior month-end price, adjusted for splits).
- **Liquidity floor** — average daily volume or average daily dollar volume measured over a trailing window, with a defined floor.
- **Sector inclusions or exclusions** — banks, REITs, ADRs, recently IPO'd names, micro-caps. Each exclusion is a design choice that should be defensible.

The universe must be **survivorship-bias-free**. Use a database that includes delisted securities and reflects them in the universe at the time they were live. Backtests run on a survivor-only universe produce systematically inflated returns; the bias is large enough on long horizons to make a dead factor look alive.

The universe must be **point-in-time**. A security that was in the universe on a historical rebalance date should be evaluated using the metadata that was known about it on that date — including its sector at that date (sector reclassifications happen), its share class (reorganizations happen), and its inclusion status (the security may have entered or exited the universe several times over its history).

### Stage 2 — Data ingestion and reference architecture

The raw inputs are price and volume, corporate actions, fundamentals, estimates, and any alternative data feeds.

Three properties of the ingested data are non-negotiable:

- **Timestamped to the moment the data became available to a researcher.** Filings have a release date that is later than the reporting period; analyst estimates have a publication time; alt-data has a delivery time. Storing the data with the **publication timestamp** (also called the **point-in-time timestamp** or as-of date) is the foundation of look-ahead avoidance.
- **Vintaged.** Estimates and even fundamentals get restated. The data store should preserve the original-as-released version and the restated version separately, so the researcher can choose which to use depending on whether the analysis is meant to reflect real-time decision-making (use original) or the cleanest underlying signal (use restated, with explicit justification).
- **Adjusted with auditable lineage.** Splits, stock dividends, spin-offs, and other corporate actions affect price and shares-outstanding histories. Store the unadjusted data and apply adjustments in a separate layer; never overwrite the raw values.

Document the latency of each source — the lag between the data being created and being available to the pipeline. Latency varies meaningfully across sources and is one of the largest determinants of whether a factor's edge survives realistic implementation.

### Stage 3 — Point-in-time protocol

This is the highest-leverage stage and the easiest one to get wrong. Look-ahead bias contaminates pipelines silently and produces backtests that look excellent in research and fail in deployment.

The protocol:

- **Every datum has an as-of timestamp.** At any rebalance date T, the pipeline may use only data whose as-of timestamp is less than or equal to T (minus a safety margin if appropriate, e.g., to model the time it takes to compute and trade).
- **Fundamental data uses report-availability date, not period-end date.** A quarter ending March 31 may not be filed until early May. Using March 31 data on April 1 is a forty-day look-ahead. The protocol enforces use of the actual filing date or, more conservatively, the filing date plus a small buffer to model the time required to ingest and validate.
- **Estimates use the original publication time.** When a researcher's history shows that an estimate was revised, the version known on date T is the version published on or before T.
- **Universe membership is determined point-in-time.** A security that was added to an index on date T+10 was not in the index on date T, even if a later snapshot says it was.
- **Risk model exposures are point-in-time.** A risk model fitted on data through date T must use only data available at T, not a model fitted using the entire history.

Build a small set of regression tests that try to break the protocol. The classic test is to compute the factor on the published-date timeline and on the period-end timeline; the difference between the two backtests reveals how much look-ahead is being prevented (or, in a broken pipeline, generated).

### Stage 4 — Factor construction

A factor is a transformation from raw inputs to a cross-sectional score that ranks the universe at each rebalance date. Construction choices include:

- **Numerator and denominator selection.** A value factor might be earnings yield, free-cash-flow yield, book yield, sales yield, or a composite of several. Each captures a different facet and each has different stability and exposure properties.
- **Normalization.** Cross-sectional scores must be made comparable across time. Common normalizations include cross-sectional ranking, cross-sectional z-scoring, and winsorization at named percentiles. Document which is used and why.
- **Sector neutralization.** Industries have different baseline ratios; a pure value factor may collect a structural sector bet (e.g., financials look perpetually cheap, technology perpetually expensive). Sector-neutralization (demeaning within sector) removes that bet, at the cost of removing any genuine alpha that is sector-driven. The choice should be deliberate.
- **Smoothing.** Single-snapshot factors are noisy. A trailing-window average (e.g., the average of three prior month-end z-scores) reduces noise at the cost of slowing the signal. Calibrate to the rebalance frequency.
- **Composite construction.** When combining sub-factors into a composite, choose the combination rule explicitly — equal-weighted, inverse-volatility-weighted, or a regression-based weighting fitted to in-sample data. Composites fitted in-sample are particularly prone to overfit; prefer simple weightings unless the more complex weighting is justified by out-of-sample evidence.

Save the factor as a panel — security by date — with the as-of timestamp clearly stamped on each row. The panel becomes the input to the analytical stages.

### Stage 5 — Information coefficient analysis

The information coefficient (IC) measures the cross-sectional correlation between the factor on date T and the forward return over a chosen horizon. It is the most common single diagnostic and one of the most useful.

Compute the IC at each rebalance date for each forward-return horizon of interest. Summarize across time with:

- **Mean IC** — the average predictive correlation. Higher is better; for cross-sectional equity factors, sustained mean ICs above roughly 0.03–0.05 are common for live factors and above roughly 0.08 are strong.
- **IC standard deviation** — the dispersion of the predictive correlation through time.
- **IC information ratio** — mean IC divided by IC standard deviation. The most useful single number for comparing factors.
- **IC autocorrelation** — does today's IC predict tomorrow's IC? High autocorrelation suggests the signal is regime-dependent.
- **IC by sub-period** — split the sample into halves, thirds, and rolling windows. A factor whose IC concentrates in a single period is suspect.

Prefer rank-based (Spearman) IC over level-based (Pearson) IC for cross-sectional analysis; rank-IC is more robust to outliers and aligns better with how the portfolio actually uses the signal.

### Stage 6 — Portfolio formation and quantile spread

Form portfolios from the factor by sorting the universe into quantiles (typically quintiles or deciles) and computing the return of each. The quantile spread (top minus bottom) is the second-most-common diagnostic.

Track:

- **Average quantile returns** — are returns monotonic across quantiles? Non-monotonicity is a yellow flag; the relationship between factor and return may be non-linear or driven by extreme deciles only.
- **Long-short return** — the time series of (top quantile minus bottom quantile) returns.
- **Risk-adjusted long-short return** — Sharpe, information ratio, or similar. A factor with reasonable IC but high turnover may have a low Sharpe after transaction costs.
- **Long-only and short-only legs** — short legs often look weaker than longs (financing, borrow cost, asymmetric implementation), and many factors live almost entirely in the long leg.
- **Hit rate** — fraction of rebalance periods in which the long-short return is positive.

Beware of the temptation to report only the long-short headline. Decompose by leg, by sector, by region, by size band; the headline can hide concentration in a thin slice of the universe.

### Stage 7 — Turnover and decay

Turnover and decay are the two most under-appreciated diagnostics in factor research. A factor that turns over rapidly may have its real-world edge consumed by transaction costs; a factor that decays slowly may be easier to harvest than its short-horizon IC suggests.

Compute:

- **Portfolio turnover** — fraction of the long (or long-short) portfolio that changes from one rebalance to the next. Express annualized.
- **Factor-return decay** — the IC and quantile spread as a function of forward-return horizon. A factor whose IC is strong at 1 day but collapses at 10 days is a different beast from one whose IC is moderate at 1 day and persistent out to 60 days. The persistent factor is typically easier to harvest at scale.
- **Decay across the calendar** — rolling windows of IC at each horizon. Decay that is itself decaying (the factor's persistence shrinking over years) is the strongest single sign of crowding and degradation.

The decay profile guides the rebalance frequency. A factor whose signal persists for weeks should not be rebalanced daily; doing so pays transaction costs to capture noise. A factor that decays in days cannot be rebalanced monthly without paying performance.

### Stage 8 — Robustness

Robustness testing distinguishes factors that capture a structural pattern from factors that fit historical noise. The discipline is to make the factor uncomfortable in several ways and see what survives.

The robustness program should include:

- **Parameter perturbation.** Vary the construction parameters — the lookback window, the winsorization threshold, the smoothing window — over a sensible range. A factor whose performance collapses with a small parameter change has been overfit.
- **Universe perturbation.** Run the factor on adjacent universes — drop the smallest decile of names, drop the largest, exclude financial sector, exclude recent IPOs, restrict to a different region. A factor whose edge concentrates in a thin slice may be vulnerable.
- **Sub-period analysis.** Split the sample into multiple sub-periods. A factor that worked in the 2000s, dimmed in the 2010s, and is flat in the 2020s is a different story from a factor whose performance is roughly stable.
- **Regime analysis.** Identify regimes (volatility regimes, growth-vs-value regimes, rising-vs-falling-rate regimes) and examine factor performance within each. Regime-conditional factors are legitimate but should be labelled as such, not sold as all-weather.
- **Reasonable transaction-cost overlay.** Subtract an honest estimate of transaction costs and re-evaluate. Many strong-looking factors lose much of their edge to cost. Use a cost model calibrated to the universe and the rebalance frequency.
- **Capacity test.** Estimate the implementable AUM at which the factor's edge survives the market impact it would generate. A factor with a small capacity is not a flawed factor — but it is a different deployment story than a high-capacity one.

A useful summary diagnostic is the **robustness halo**: the range of construction choices and conditions over which the factor's IC and Sharpe stay above stated minimums. A wide halo is a strong signal; a halo that is one point in parameter space with a sharp drop in every direction is overfit.

### Stage 9 — Multi-period and multi-cut backtest

The headline backtest is a single line; the supporting backtests are dozens. The skill recommends a structured matrix:

- **Forward-return horizons** — 1, 5, 21, 63, 252 trading days (i.e., approximately one day, one week, one month, one quarter, one year).
- **Rebalance frequencies** — daily, weekly, monthly, quarterly.
- **Cuts** — by sector, by size, by region, by liquidity decile.
- **Cost overlays** — gross, conservative cost, harsh cost.

The matrix surfaces where the factor is robust and where it is fragile. Most factors do not look the same on every cut; the question is whether the factor looks like a single coherent story when viewed across the cuts (e.g., decay is consistent with the construction logic, capacity is consistent with the universe) or whether the factor's headline performance is a thin slice that the user has accidentally found.

### Stage 10 — Decay monitoring and decommissioning

Factors decay. Even structurally-motivated factors lose edge over years as more capital pursues them or as the conditions that gave rise to them change. Production-bound research pipelines should design for decay from the outset.

The decommissioning protocol:

- **Pre-commit minimums.** Before deployment, name the minimum IC, the minimum Sharpe after costs, and the minimum decay-half-life that the factor must clear. If the live performance falls below the minimums for a sustained window, the factor is taken down.
- **Rolling-window live monitoring.** Compute IC and Sharpe on a rolling window during deployment. Compare to the in-sample distribution; large negative deviations are early signs.
- **Reason-led down-weighting.** If the factor underperforms because the underlying behavioral or structural mechanism has plausibly changed, down-weight or retire it. If the underperformance is consistent with the in-sample variance of the factor, hold the position.

The pipeline outputs a small dashboard of monitoring metrics that translate the in-sample diagnostics into ongoing measures. The dashboard is the connective tissue between research and live deployment.

### Cross-cutting practices

- **Version every input and every parameter.** The pipeline produces a hash that names the inputs, the universe definition version, the factor parameters, the rebalance frequency, and the cost model. Re-running with a different hash should produce different results; re-running with the same hash should produce identical results.
- **Separate research and production data paths.** Production should not be allowed to use restated data without an explicit flag. Research can use restated data freely with the caveat documented.
- **Document the bias inventory.** A short table of every known bias (survivorship, look-ahead, selection, in-sample fitting, restatement, calendar) with the mitigation applied and the residual risk.
- **Maintain a single source of truth for the universe and corporate-action history.** When two analyses on the same factor disagree, the most common cause is an inconsistency in the universe membership or in the corporate-action treatment. Pinning these to versioned references prevents the most painful debugging sessions.
- **Treat the cost model as a research artifact in its own right.** Many factors live or die on whether the cost overlay is honest. The cost model deserves the same version-and-test discipline as the factor itself, and changes to it should trigger a re-evaluation of every active strategy.

### Common failure modes

The pipeline is built to make these failures rare, but they are common enough to name explicitly:

- **Silent look-ahead via fundamentals.** Period-end timestamps are easier to use than filing-date timestamps; the pipeline that takes the easier path produces backtests that systematically overstate the factor's edge. The protocol must enforce the harder path.
- **In-sample parameter selection masquerading as research.** Picking the lookback, the winsorization threshold, and the smoothing window that maximize Sharpe on the full sample produces a result that is fit to the sample. The robustness halo discipline is the primary defense.
- **Universe drift.** A universe defined informally and re-extracted at each rerun can drift in ways the researcher does not notice. Pinning the universe to a versioned definition prevents the drift.
- **Cost-model laxity.** A cost model calibrated to large-cap US equities applied to a mid-cap global portfolio produces a fantasy. Calibrate the cost model to the actual universe.
- **Capacity neglect.** A factor that looks strong at $1M deployed may not survive at $1B. Capacity testing as a routine diagnostic prevents the post-deployment surprise.

## Inputs

- **factor_idea** (required) — the factor or factor family.
- **universe** (required) — region, size, liquidity, exclusions.
- **data_inputs** (required) — price, fundamentals, estimates, alt-data, corporate actions.
- **rebalance_frequency** (optional) — daily through annual.
- **horizon_targets** (optional) — forward-return horizons of interest.

## Outputs

- A stage-by-stage pipeline design with contracts between stages.
- A point-in-time data protocol that prevents look-ahead.
- A multi-period, multi-cut backtest design with IC, quantile-spread, turnover, and decay diagnostics.
- A robustness program including perturbations, subsamples, regimes, costs, and capacity.

## Examples

### Worked example — Pipeline for an earnings-revisions momentum factor on global mid-caps

**Inputs given to the skill:**

- factor_idea: "Three-month change in trailing-twelve-month consensus EPS, ranked cross-sectionally; sector-neutralized."
- universe: "Global mid-caps, $2B–$15B market cap, ADV floor $5M USD, excluding REITs and financials, point-in-time membership."
- data_inputs: "Vendor fundamentals (vintaged), consensus estimates (with original publication timestamps), prices (split- and dividend-adjusted in a separate layer), corporate-action calendar."
- rebalance_frequency: "monthly."
- horizon_targets: "1, 21, 63 trading days."

**Output (abridged):**

> **Pipeline design.** Ten stages as described. Universe is constructed at each month-end using prior-month-end shares and the ADV measured over the prior 60 trading days; survivorship-free vendor used; sector classification is point-in-time. Consensus estimates are anchored to publication timestamp with a one-business-day buffer applied to T to model ingestion latency. Factor is computed at each month-end as the trailing three-month change in TTM consensus EPS, cross-sectionally winsorized at 1%/99%, z-scored, then sector-demeaned.
>
> **Point-in-time protocol.** Estimate as-of date is the original publication time of the estimate; restated estimates are not used in the production path. Filing-date convention is used for the underlying EPS data, with a two-business-day buffer. Universe is constructed using only information dated on or before the rebalance date.
>
> **Backtest design.** IC computed at the three named horizons. Quintile portfolios formed at each rebalance; quantile spread reported gross and net of a transaction-cost model calibrated to mid-cap global liquidity. Turnover, decay across forward horizons, IC sub-period stability, and regime conditional performance all reported.
>
> **Robustness program.** Lookback (1, 3, 6 months) varied; winsorization (0.5%/99.5%, 1%/99%, 2%/98%) varied; with-and-without sector neutralization; with-and-without smoothing; full universe and excluding-smallest-decile cuts; transaction-cost overlay at three levels; capacity estimate using a daily-volume-based market-impact model.
>
> **Decommissioning protocol.** Minimum monthly-IC three-month rolling mean of 0.03; minimum quintile-spread Sharpe after costs of 0.5; maximum acceptable decay-half-life shortening of 30% from in-sample. Live monitoring computed monthly; underperformance for two consecutive quarters triggers a research review.

The full output produced by the skill would include the data protocol, backtest design, and robustness program in their own structured sections with the metric definitions, the parameter grids, and the cut definitions filled in.

## Limitations

This skill produces a pipeline design, not a built pipeline. Implementation, data engineering, performance tuning, and production deployment require engineering effort beyond what the design specifies. The contracts the design specifies are necessary but not sufficient; an honest implementation may discover additional constraints from the data infrastructure that require revisions.

The skill assumes the user has access to point-in-time data. Many open data sources are not point-in-time; using them for factor research without acknowledging the limitation can produce results that do not reflect what was actually knowable at the time. If the user's data is not point-in-time, the limitation should be disclosed in any downstream report.

The skill is focused on cross-sectional equity factors and on factors with holding periods of days to months. It is less directly applicable to time-series factors (which compare a security to its own history rather than to a cross-section), to macroeconomic-style factors (which require very different data), or to private-market factors (which lack the depth of comparable history). Adaptations are possible but the diagnostic suite changes meaningfully.

Backtests are historical reconstructions. They are not predictions. A factor that backtested well may not work in the future; a factor that backtested badly may work in the future. The discipline of the pipeline is to make the backtest as honest as it can be, not to make the future certain.

Outputs are educational and methodological. Nothing produced by this skill is investment advice. Any deployment of a factor strategy designed using this pipeline requires independent validation, compliance review, capacity and impact analysis, risk approval, and supervision appropriate to the user's firm and jurisdiction.

## Sources reviewed

- https://github.com/microsoft/qlib (MIT)
- https://github.com/quantopian/alphalens (Apache-2.0)
- https://github.com/jerryxyx/AlphaTrading (no LICENSE file — methodology pointer only)
- https://github.com/JerBouma/FinanceToolkit (MIT)
- https://github.com/pmorissette/ffn (MIT)
- https://github.com/ranaroussi/yfinance (Apache-2.0)
- https://github.com/AI4Finance-Foundation/FinRobot (Apache-2.0)
- https://github.com/OpenBB-finance/OpenBB (AGPL-3) — referenced for methodology of open financial data terminals; no code or prose reused
