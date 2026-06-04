---
id: skillsgit-curated/data-experimentation-pipeline-architect
version: 1.0.0
name: Experimentation Pipeline Architect
description: Designs the end-to-end data pipeline for an A/B testing program — instrumentation, exposure logging, randomization unit, guardrail metrics, SRM checks, and power analysis — so experiments produce credible reads.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:analytics-engineering, experimentation, ab-testing, srm, guardrail-metrics, exposure-logging, statistical-power, growthbook]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: [code_execution]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - experimentation pipeline
  - a/b test
  - ab testing
  - exposure logging
  - randomization unit
  - srm check
  - sample ratio mismatch
  - guardrail metric
  - power analysis
  - mde
  - cuped
  - experiment instrumentation
  - feature flag experiment
example_invocations:
  - "Design the data pipeline for our new A/B testing platform."
  - "We have feature flags but no proper experiment readouts. What do we need to build?"
  - "Our last experiment had a 49/51 split — is that a problem?"
  - "Plan instrumentation and metrics for a homepage redesign test."
inputs:
  - name: test_context
    type: text
    required: true
    description: What is being tested (the feature, the change, the hypothesis) and the business outcome it is trying to move.
  - name: traffic_scale
    type: text
    required: false
    description: Approximate visitors, sessions, or eligible users per day or week. Drives power analysis and feasibility.
  - name: current_stack
    type: text
    required: false
    description: Feature-flag and experimentation tools in use (GrowthBook, Unleash, in-house, none) and the data warehouse. Drives integration design.
  - name: randomization_unit
    type: choice
    required: false
    description: The unit at which assignment occurs — user (logged in), device (cookie), session, or page-view. Default - user.
    choices: [user, device, session, page-view, account]
  - name: known_constraints
    type: text
    required: false
    description: Regulatory, technical, or organizational constraints (e.g., must not log on EU traffic without consent, mobile clients have flaky retry, marketing site is statically generated).
outputs:
  - name: pipeline_design
    type: markdown
    description: The end-to-end pipeline — instrumentation events, exposure logging, randomization, warehouse landing, metric tables, and analysis surface.
  - name: metric_set
    type: markdown
    description: Primary metric, secondary metrics, and guardrails for the experiment — each with grain, computation, and decision rule.
  - name: pre_launch_checklist
    type: markdown
    description: A checklist the team works before turning the experiment on, plus the continuous checks (SRM, novelty effects) that run during.
  - name: power_analysis
    type: markdown
    description: Required sample size, expected duration, and minimum detectable effect, with assumptions stated explicitly.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when an organization is moving from "we change things and watch the chart" to a credible experimentation discipline. Specifically:

- A team is launching its first formal A/B test and needs the pipeline before they start.
- A product team is rolling out feature flags and wants experimentation built into the flow from the start.
- An existing testing program produces results that nobody trusts and the diagnosis is data-pipeline weakness, not statistical confusion.
- A regulated business (fintech, health, EU consumer) is designing experiments under privacy and consent constraints.
- A team is integrating a feature-flag tool (GrowthBook, Unleash, in-house) with a warehouse and needs to define the metric pipeline.

Do not use this skill to choose between Bayesian and frequentist analysis — that is a methodology choice that lives downstream of the pipeline; pair with a statistics-focused review. Do not use it to design the feature being tested; this is about how to measure, not what to ship.

## How to apply

Work the steps in order. The pipeline-design questions are upstream of the statistics; getting the pipeline wrong invalidates the analysis no matter how clever the test.

### 1. State the question being answered

1. **Force the hypothesis into a one-sentence form.** "Showing pricing in monthly rather than annual will increase trial signups by at least 5% with no degradation in average customer value." A vaguer phrasing ("we want to test the new pricing page") cannot be analyzed and is the most common reason post-hoc that experiments produce useless reads.
2. **Identify the primary metric.** The single number the decision will rest on. If two metrics are co-primary, the test is two tests, and they each need their own decision criterion.
3. **Identify secondary metrics.** Numbers that color the read but do not decide it. Common examples: latency, error rate, downstream funnel stages.
4. **Identify guardrails.** Numbers that, if they move adversely, mean ship-it gets blocked even if the primary metric wins. Latency, crash rate, support contact rate, revenue per visitor. Guardrails express the business constraint that a successful experiment must not break.
5. **State the decision rule explicitly.** "Ship if primary > +3% with p < 0.05 and no guardrail violates its threshold." Without a decision rule, the read becomes a debate.

### 2. Pick the randomization unit

6. **Default to the user (logged in) when available.** A user randomly assigned to a variant gets the variant everywhere they go. Cross-device, cross-session, cross-page consistency is preserved.
7. **Use device or cookie when the user is not always identified.** Anonymous traffic must be tested at the device or cookie level, with the awareness that the same human in two browsers gets two assignments.
8. **Avoid session-level assignment** unless the test is about a single-session phenomenon (search-results ranking on a logged-out search engine). Session-level tests break for any user who returns and sees the other variant.
9. **Avoid page-view-level assignment.** Within-session bias and inconsistent UX produce noisy reads. Only useful for stateless tests of presentation (color, copy) where the user cannot tell they are in a test.
10. **For account-level products (B2B), assign by account.** All users in the same workspace see the same variant. Within-account contamination is the largest source of bias in B2B testing.
11. **Document the randomization function.** A deterministic hash of (user_id, experiment_id) into a bucket. The hash must be stable, monotone-ish across releases, and seeded so a re-run with the same inputs produces identical buckets. Drift in the hash function is a silent killer.

### 3. Instrument the assignment

12. **Log an exposure event on every assignment**, the moment the user is exposed to the variant. This event is the source of truth for "who was in the experiment". Without it, post-hoc inference from "users who saw page X" is unreliable.
13. **The exposure event carries:** user (or device, cookie, account), experiment id, variant id, timestamp, surface (web / iOS / Android / API), version of the assignment function, and the application version.
14. **Log exposure on every render, deduplicate downstream.** Logging once-per-user-per-experiment at the client is fragile; logging on every render and deduplicating in the warehouse is reliable.
15. **Log the exposure even when the variant is "control".** A test in which only treatment exposures are logged cannot compute SRM and cannot test for assignment bias.
16. **Log the exposure even when the user takes no further action.** Many otherwise-valid users see the page and leave; if their exposure is not logged, the denominator of every conversion-rate metric is wrong.
17. **For server-side tests, log on the server.** Client-side logging is subject to ad blockers, JavaScript errors, and network drops that bias the read toward engaged users.
18. **For mobile, log with retry and offline-buffering.** A flaky network must not silently drop exposures. Acknowledge from the warehouse, not from the egress.

### 4. Land the events in the warehouse

19. **Land raw exposure events in a single staging table.** `stg_experiment_exposures` with one row per logged exposure. No de-duplication, no joining. Late-arriving events update the table within the freshness SLA.
20. **Build an intermediate that materializes the canonical assignment per (user, experiment).** Typically the first exposure timestamp determines the assignment; later exposures must not flip the variant. Document the canonical rule and apply it as a window function over the staging table.
21. **Join exposures to the metrics fact tables** on user (or device, account) plus a time filter: the metric event must occur after the first exposure. Pre-exposure events do not belong to the experiment.
22. **Build a single `fct_experiment_metric_user_day`** table with one row per (experiment, variant, user, metric, day) and the metric value for that day. This becomes the analysis surface; everything else is sliced from it.
23. **For revenue and cumulative metrics, also build a `fct_experiment_metric_user`** with one row per (experiment, variant, user) and the cumulative metric over the experiment window. Avoids per-user aggregation at analysis time, which is expensive.
24. **Materialize as incremental.** Experiment data accumulates monotonically; rebuilding the full table is wasteful. Use the warehouse's incremental strategy and define late-arriving windows explicitly.

### 5. Define the primary metric

25. **Pick a primary metric the team agrees in advance is the right one to move.** A primary metric chosen after the data is in is post-hoc selection and invalidates the experiment.
26. **Express the primary metric at user grain.** Per-user revenue, per-user clicks, per-user conversion. User-grain metrics admit standard variance estimators; session-grain or event-grain metrics need cluster-aware estimators or they over-report significance.
27. **Reject ratios of sums as primaries.** "Average revenue per click" computed as total_revenue / total_clicks across the whole arm has the wrong variance. Use the per-user form (each user contributes their own ratio, then average) or use the delta method.
28. **For binary metrics, document the conversion event** with the same rigor as a metric definition: which event, within what window from exposure, with what filters.
29. **For continuous metrics, document the value formula** and whether it is winsorized or trimmed. Long-tail revenue distributions can be dominated by one whale; winsorize at the 99th percentile if the alternative is a noisy mean.

### 6. Define secondary and guardrail metrics

30. **Pick 2-4 secondary metrics.** Funnel stages downstream of the primary, complementary outcomes (engagement, downstream feature use). Do not throw fifty metrics in the secondary bucket; doing so guarantees multiple-testing problems and decision paralysis.
31. **Pick 3-6 guardrails.** Latency (median and p95), error rate, crash rate, support contact rate, revenue per visitor, retention. Guardrails express system-health and business-continuity constraints.
32. **Each guardrail has a threshold** stated in advance. "Latency p95 must not increase by more than 50ms" or "revenue per visitor must not decrease by more than 1%". Without thresholds the guardrail is decorative.
33. **Each guardrail has a direction.** Most guardrails are one-sided: latency can go up (bad) but improving latency is bonus, not a fail. Document the direction.
34. **For metrics where small changes are expected, use equivalence tests rather than null-hypothesis tests.** A guardrail that asks "is the change different from zero" will fail with high power on any large experiment, even for a 0.1% change that the business does not care about.

### 7. Run sample ratio mismatch (SRM) checks

35. **Compute the observed assignment ratio on every experiment, every day.** If you allocated 50/50, the observed ratio should be very close to 50/50. A statistically significant deviation is SRM and the experiment data is contaminated.
36. **Run the chi-square goodness-of-fit test** on the observed exposures per arm against the expected allocation. Flag SRM when p < 0.001 to avoid false positives at large traffic, but investigate at p < 0.01 if the variance budget allows.
37. **Common causes of SRM:** the randomization function is broken; one variant has a bug that breaks logging (e.g., the control's exposure event fires later than the treatment's); a downstream filter is biased (e.g., the analysis filters out users who hit an error, and one variant produces more errors); a CDN cache serves one variant disproportionately; bot traffic is biased into one variant.
38. **An experiment with SRM must not ship.** The bias has poisoned every metric in the readout; trying to "correct" by re-weighting introduces more uncertainty than confidence.
39. **Display the SRM check prominently.** On the experiment dashboard, above the primary metric, with a green/red flag. A buried SRM warning produces decisions made on contaminated data.

### 8. Plan the power analysis

40. **Estimate the baseline mean and variance** of the primary metric from production data over a window equal to the planned experiment length, on a population equal to the planned eligible population.
41. **Decide the minimum detectable effect (MDE).** The smallest change that, if real, would change the business decision. Setting the MDE too small produces tests that need impossible sample sizes; setting it too large makes the test useless for normal-sized wins. Anchor on the smallest move that would unblock a roadmap decision.
42. **Compute the sample size per arm** using the relevant power formula. For binary metrics, the two-proportion z-test sample size. For continuous metrics, the two-sample t-test with the estimated variance. Be explicit about alpha (typically 0.05), power (typically 0.8), and one- vs two-sided.
43. **Convert sample size to duration** by dividing by daily eligible exposures. If the duration is longer than is acceptable, options are: increase the MDE, narrow the population (tightens variance), use a paired or cross-over design, or scrap the test.
44. **Plan to run at least one full weekly cycle.** Day-of-week effects are large in most products; an experiment that runs Monday to Thursday is biased toward a single weekday pattern.
45. **Set the maximum duration.** Experiments that run forever produce drift in the underlying population, novelty effects fading, and seasonal contamination. Two to four weeks is typical for high-traffic products; longer for low-traffic, but never indefinite.
46. **Disable peeking-based decisions.** Looking at the result daily and stopping when significant inflates the false-positive rate dramatically. Either commit to the planned duration or use a sequential testing method (alpha-spending, mSPRT) that controls for repeated looks.

### 9. Variance reduction

47. **Use CUPED (Controlled-experiment Using Pre-Experiment Data) when feasible.** Subtract a per-user pre-experiment estimate of the metric from the in-experiment value. Variance reduces, sample-size requirements drop, and the test becomes feasible at scale where the unadjusted version is not.
48. **Use stratified randomization** when there are large, known segments with very different metric levels (paying vs free, mobile vs desktop, US vs non-US). Stratify and analyze per stratum, then combine.
49. **For long-tail metrics, winsorize before computing the test.** A handful of users with extreme values dominate the variance otherwise. Document the threshold.
50. **For metrics with high zero-inflation** (most users do nothing, a few do a lot), consider analyzing the conversion-and-mean separately. The two-part model often has more power than the combined model.

### 10. Build the analysis surface

51. **The analysis surface is a single dashboard** showing, for each experiment: exposure counts per arm, SRM check, primary metric with delta and CI, secondary metrics, guardrails with thresholds, and a timeline view of each metric over the experiment duration.
52. **Compute confidence intervals, not just point estimates.** A point estimate without a CI hides uncertainty. The CI is the headline.
53. **Show effect sizes in absolute and relative terms.** "Conversion went from 4.2% to 4.5% (+0.3pp, +7%)". Either alone is misleading; both together are honest.
54. **Show the test in the planned duration even before the duration has elapsed.** A team that sees "stopping at day 4 because significant" is being misled by peeking. Show the elapsed-time progress bar so the discipline of waiting is enforced visually.
55. **Surface novelty effects.** A metric that wins big in week 1 and dies by week 3 is not a winning treatment; it is a novelty bump. Plot the metric over time and watch the trend.
56. **Surface heterogeneous treatment effects.** Slice by segment (new vs returning, mobile vs desktop, country) and show whether the treatment effect is consistent. A test that wins overall but loses on the largest segment is not a clean win.

### 11. Pre-launch checklist

Run this before turning the experiment on:

57. **The hypothesis is written and agreed.** Decision rule, primary metric, MDE.
58. **The randomization is deterministic and stable.** Test by running the assignment function over a known set of users and confirming reproducibility.
59. **The exposure event is firing on both arms, including control.** Verify in staging traffic, not just in production after launch.
60. **The metric pipelines are running and producing numbers** for a recent reference period without the experiment running. If you cannot compute the metric on yesterday's data, you cannot compute it tomorrow.
61. **The dashboards are wired and the SRM check is green** on a dry-run of the assignment over a current population.
62. **The guardrails have thresholds.** Latency p95 increase < 50ms, etc.
63. **The team agrees in advance who decides at the end** and what evidence they need.
64. **A rollback plan exists.** If the experiment causes harm, what flips and how fast.

### 12. During the experiment

65. **Watch SRM daily.** If it flips red, pause and investigate; do not continue.
66. **Watch guardrails daily.** If a guardrail violates, pause and investigate; do not continue.
67. **Do not change the experiment mid-flight.** Adjusting allocation, adding variants, or fixing bugs in one arm during the run invalidates the test.
68. **Do not look at the primary metric daily for decision purposes.** Stick to the planned duration. Use the dashboard for monitoring, not for stopping.

### 13. After the experiment

69. **Read the SRM check first.** If contaminated, the experiment did not happen; document and re-run.
70. **Read the guardrails second.** If any violated, the decision is "do not ship" regardless of the primary.
71. **Read the primary metric.** If outside the CI, the decision is driven by the rule set in step 5. If inside the CI, the experiment is inconclusive — neither a win nor a loss; document and decide on follow-up.
72. **Read secondary metrics for color.** They explain why the primary moved, but they do not over-ride the decision rule.
73. **Write a one-page readout.** What was tested, what was decided, the numbers, the caveats. Stored in a permanent location; cited in the metric and feature changelog.
74. **Update the experimentation backlog.** Wins go to rollout; losses to learning; inconclusives to either bigger samples or kill-it.

### 14. Anti-patterns to surface

75. **The "no exposure log" experiment.** Inferring assignment from who-saw-what after the fact. Always wrong; refuse.
76. **The "we'll pick the metric later" experiment.** Selecting the metric that won is the canonical p-hacking pattern.
77. **The "let's just keep watching" experiment.** Sequential peeking without sequential statistics. Inflates the false-positive rate.
78. **The "ignore the SRM" experiment.** A team that sees the warning and ships anyway has decided to fly blind.
79. **The "test on 100% of traffic" launch.** Not an experiment; a launch dressed up. If a feature is going to 100%, no comparison group exists.
80. **The "test for two days" experiment.** Below one weekly cycle, the test is biased by day-of-week.
81. **The "many small experiments tested as one big one" pattern.** Running many tests and reading one combined metric inflates false positives. Either control for multiple comparisons or split the program.
82. **The "feature flag is the experiment" assumption.** A feature flag controls who sees the feature; an experiment requires that the assignment is recorded and the metrics joined to it. Many teams have flags but no experiments; flag → experiment is a pipeline build, not a config toggle.

### 15. Output discipline

83. **Open with the hypothesis and decision rule.** One line each.
84. **Then the metric set:** primary, secondary, guardrails. Each with definition.
85. **Then the pipeline:** instrumentation, exposure log, warehouse landing, analysis surface.
86. **Then the power analysis:** baseline, MDE, sample size, duration.
87. **Then the pre-launch and during-launch checklists.**
88. **End with a list of decisions the team must make before launch** that have not yet been made. Force them to choose; do not let them ship a half-decided design.

## Inputs

- The test context (feature, hypothesis, target outcome).
- Traffic scale.
- Current stack (feature-flag tool, warehouse).
- Optional randomization unit (defaults to user).
- Optional constraints (privacy, regulatory, technical).

## Outputs

- Pipeline design from instrumentation through analysis surface.
- Metric set (primary, secondary, guardrails) with definitions and thresholds.
- Pre-launch checklist and during-experiment checks.
- Power analysis with explicit assumptions.

## Examples

**Example 1 — First-test setup for a SaaS pricing change**

> Input: "We want to test a monthly-pricing-first vs annual-pricing-first variant on the pricing page. Currently 8k visitors per day. We use GrowthBook and Snowflake."
>
> Expected output: Randomization at the user level if logged in, else device; deterministic hash of (visitor_id, experiment_id); assignment logged via GrowthBook's exposure-tracking SDK and landed in `stg_experiment_exposures` in Snowflake. Primary metric: trial-signup conversion rate (binary, per-user, within 7 days of first exposure). Secondary: trial-to-paid conversion within 14 days, average plan tier on first paid subscription. Guardrails: median page load (server-rendered, not blocked by experiment), bounce rate on pricing page, support contact rate within 7 days. Power analysis on 8k visitors/day and a 4.5% baseline conversion: an MDE of +0.5pp requires ~50k users per arm, achievable in ~13 days; round up to two full weekly cycles. SRM check daily, paused if p < 0.001. CUPED on prior-7-day visit count as the pre-experiment covariate.

**Example 2 — Mobile app onboarding flow test**

> Input: "We're changing the order of onboarding screens in our iOS app. We have ~200k DAU."
>
> Expected output: Randomization at the user level via the auth-tied stable id; deterministic. Exposure logged on the first onboarding screen render with retry + offline buffer (mobile clients drop events). Primary metric: completion-of-onboarding rate (binary, per-user, within 24h of first exposure). Secondary: time-to-first-key-action, Day-1 retention. Guardrails: crash rate (per session), JS-error count, app launch time p95. Power analysis: with 200k DAU and a 60% baseline completion rate, MDE of +1pp requires ~15k per arm — half a day, but extend to one full weekly cycle to absorb day-of-week. Watch for: novelty effects on returning users — restrict the experiment to new installs to avoid contamination from users who have already completed onboarding.

**Example 3 — B2B-account-level test of a new admin feature**

> Input: "We want to test whether the new admin dashboard increases workspace retention. ~5k active workspaces."
>
> Expected output: Randomization at the account (workspace) level — all users in a workspace get the same variant. Deterministic hash of (workspace_id, experiment_id). Exposure logged on first render of the admin dashboard per workspace, then propagated to all users. Primary metric: workspace retention at 30 days (binary, per workspace). Secondary: admin DAU within the workspace, weekly active users (within workspace). Guardrails: admin-page load, support tickets per workspace. Power analysis: with 5k workspaces and a baseline retention of 85%, an MDE of +2pp requires ~3k per arm — three months of new workspaces accumulating to reach the sample. Either reduce the MDE expectation, target a higher-impact metric, or use a longer duration with an explicit acknowledgement that seasonal contamination is a risk. Consider a cluster-randomized trial with stratification by workspace size, since per-workspace metrics vary by an order of magnitude with team size.

## Limitations

- The skill produces a pipeline design and metric set, not a statistical analysis. Pair with a statistics-focused agent for inference and post-hoc analysis.
- It does not choose between frequentist and Bayesian analysis. Both can be supported by the same pipeline; the analysis layer chooses.
- It assumes the team controls the assignment surface (client, server, or feature flag). For tests on third-party-served traffic where assignment cannot be controlled, the pipeline cannot guarantee randomization integrity.
- For very low-traffic products (under a few thousand exposures per day), power analysis will frequently conclude the test is infeasible at any reasonable MDE; the recommendation in those cases is to test bigger changes or use qualitative methods.
- The skill flags but does not solve attribution problems (cross-platform users, late-arriving events, post-test contamination); attribution is a parallel data problem.
- It does not produce holdout-group designs for long-running marketing or product-led-growth experiments; those have their own additional considerations.

## Sources reviewed

The patterns and checks above were synthesized across the following permissively licensed projects. No prose was copied or closely paraphrased from any source.

- https://github.com/growthbook/growthbook
- https://github.com/Unleash/unleash
- https://github.com/cube-js/cube
- https://github.com/dbt-labs/metricflow
- https://github.com/lightdash/lightdash
- https://github.com/apache/superset
- https://github.com/evidence-dev/evidence
