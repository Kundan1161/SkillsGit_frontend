---
id: skillsgit-curated/cloud-cost-audit
version: 1.0.0
name: Cloud Cost Audit Planner
description: Audit a multi-cloud bill end-to-end — surface top cost drivers, weekly anomalies, rightsizing candidates, commitment coverage gaps, storage class mix, and data-transfer egress.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:cloud-finops, aws, azure, gcp, cost-audit, rightsizing, anomaly-detection, egress]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  tools_optional: [code_execution, file_io, web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8500
trigger_keywords:
  - cloud cost audit
  - finops audit
  - aws bill review
  - azure cost analysis
  - gcp billing review
  - cost drivers
  - cost anomaly
  - rightsizing report
  - egress audit
  - storage class audit
  - commitment coverage
  - savings opportunities
example_invocations:
  - "Audit our AWS bill for last 90 days and surface the top 10 cost drivers and biggest rightsizing wins."
  - "Walk our GCP CUR export and produce a FinOps audit report we can take to the engineering leads."
  - "Look at this CSV of monthly Azure costs by service and find the anomalous weeks plus likely root causes."
inputs:
  - name: cost_dataset
    type: file
    required: true
    description: A cost export — AWS CUR (Parquet or CSV), Azure Cost Management export, GCP Billing BigQuery export, or a normalized FOCUS-format CSV. Daily granularity strongly preferred; hourly accepted; monthly only acceptable for a high-level scan.
  - name: cloud_provider
    type: choice
    required: true
    description: Primary cloud the dataset covers. Drives which service-naming taxonomy and pricing constructs the audit uses.
    choices: [aws, azure, gcp, multi_cloud, unknown]
  - name: audit_window
    type: text
    required: false
    description: Date range to audit, e.g. "2026-02-01 to 2026-04-30". Defaults to the trailing 90 days present in the dataset.
  - name: known_context
    type: text
    required: false
    description: Anything the team already knows — recent launches, migrations, planned shutdowns, large one-off jobs, M&A. Used to suppress false-positive anomalies and to weight findings.
  - name: tagging_quality
    type: choice
    required: false
    description: Self-reported tagging maturity. Affects how confidently the audit can do per-team or per-product attribution.
    choices: [none, minimal, partial, good, excellent, unknown]
  - name: commitment_state
    type: text
    required: false
    description: Plain-language summary of existing Savings Plans, Reserved Instances, or Committed Use Discounts (term, payment, coverage rough %). Used to compute coverage gaps and on-demand leakage.
outputs:
  - name: audit_report
    type: markdown
    description: Narrative report with executive summary, top 10 cost drivers, anomaly callouts, rightsizing candidates with estimated savings, commitment-coverage gap, storage and egress findings, prioritized action list.
  - name: audit_json
    type: json
    description: Machine-readable structure — top_drivers (array of {service, monthly_cost, share, trend}), anomalies (array of {week, service, expected, actual, delta, candidate_causes}), rightsizing_candidates (array of {resource_id_or_pattern, current_spec, recommended_spec, estimated_monthly_savings, confidence}), commitment_gap (object), storage_findings (array), egress_findings (array), recommended_actions (ordered array of {action, owner_role, estimated_savings, effort, confidence}), tagging_coverage_estimate (float), confidence (float).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Cloud Cost Audit Planner

## When to use

**Mandatory framing.** This skill produces methodology guidance. Outputs are not invoices, are not financial advice, and must not be presented as audited financial statements. Any commitment purchase, contract change, or workload migration recommended in the output must be reviewed by a human with authority over the account before action is taken. Savings estimates are model-based and should be treated as upper bounds for prioritization, not as committed numbers for forecasting.

Use this skill when a team has a cloud bill they do not yet understand and needs a defensible first pass at where the money goes, where it is leaking, and what to do about it. Typical entry points: a new FinOps practitioner at a company with $50K–$5M monthly cloud spend who has been handed the CUR export and a vague mandate; an engineering manager whose team just got pinged about a sudden bill increase and needs to know whether it is a real anomaly or normal seasonality; a cloud architect preparing for a quarterly business review and wanting a one-page narrative that holds up to scrutiny; a platform engineer doing a pre-renewal sweep before a Savings Plan term ends.

The skill is appropriate when the audit is *opening a question*, not closing one. It compresses a week of CUR spelunking into a first-draft narrative that a human can pressure-test. It is **not** appropriate as a replacement for:

- A real FinOps practitioner. The skill does not negotiate with vendors, does not file tickets, does not modify resources, and does not have access to the live account.
- A pricing API. Estimates are based on the provided dataset; if pricing has changed since the export, the estimates drift. Quote the dataset's pricing snapshot date in the output.
- An attribution system. If tagging quality is `none` or `minimal`, per-team attribution must be flagged as low-confidence; do not invent ownership.

Do not use this skill for: forecasting next-year spend in absolute terms (a planning skill is more appropriate); negotiating Enterprise Discount Program / private pricing (that is procurement, not FinOps methodology); compliance audits (different framework).

## How to apply

The audit's value comes from being *boring and disciplined*. The same six lenses, every time, in the same order, with the same defaults. Surprises in cloud bills come from the same dozen patterns; the methodology's job is to walk those patterns systematically rather than chase whichever number is largest on the first chart.

1. **Establish the dataset's shape before producing any number.** Confirm: provider, granularity (daily vs hourly vs monthly), window covered (and any gaps), currency, whether amortized or unblended costs, whether credits are included or excluded, whether tax is in scope, whether the export is post-discount or pre-discount, and the export's snapshot date. State every one of these in the report header. If the dataset is unblended and the org has commitments, the picture is misleading; insist on amortized for a real commitment-coverage view. If credits are included, separate them; a $0 line item due to credits is not the same as a $0 line item due to optimization.

2. **Anchor the audit to one currency, one time zone, and one granularity.** Convert everything once at the top. Mixing UTC and account-local time zones causes false anomalies at week boundaries. Mixing currencies inside the same chart is a credibility-killer.

3. **Produce the top-10-cost-drivers list at the service level first, then at the usage-type level.** Service-level (EC2, S3, RDS, Lambda; or Compute, Storage, Network for GCP/Azure equivalents) gives the headline. Usage-type (e.g., `BoxUsage:r5.4xlarge`, `DataTransfer-Out-Bytes`, `EBS:VolumeUsage.gp3`) is where the actual leverage lives. A "Compute is 60% of spend" headline is true but useless; "instance-hours on r5.4xlarge in us-east-1 are 22% of spend, of which 78% is on-demand" is actionable. Always pair each driver with its trailing-90-day trend (flat, growing, declining, spiky).

4. **Detect anomalies with a baseline, not a threshold.** A static threshold ("alert if a service exceeds $X/day") generates noise for small services and misses gradual creep on large ones. Use a per-service trailing 28-day median plus a robust dispersion measure (MAD or IQR) and flag weeks where the actual sits more than 3 robust-deviations from baseline. For each anomaly, name *candidate causes*, not a single cause: a new workload, a misconfigured autoscaling group stuck high, a backfill job, a region failover, a leaked credential spinning GPU instances, a stuck Lambda loop, a misrouted egress flow. The methodology's job is to enumerate the candidates plausibly; the human's job is to confirm which one occurred.

5. **Identify rightsizing candidates by usage shape, not by spend rank.** Big spend on an instance family is not by itself evidence of waste. Look for the shape of the utilization: chronically idle (CPU<10% p95 for 14 days), bursty-overprovisioned (p99 well below 50% of capacity), or chronically saturated (which is the inverse problem — under-provisioned, where the recommendation is to *increase* size and reduce error budget burn, not decrease). Where CloudWatch / Azure Monitor / Cloud Monitoring metrics are not in the input, downgrade rightsizing confidence and explicitly call out that recommendations are based on cost-shape heuristics, not utilization data. Always recommend the smallest defensible move (one size down, not three) and flag instance family migrations (e.g., m5 → m7g) as separate, higher-effort actions with their own confidence rating.

6. **Compute commitment coverage at the *family level*, not the account level.** A 70% account-wide Savings Plan coverage hides the fact that one team's GPU workload is at 0% coverage and another team's general-purpose fleet is at 110% (overcommitted, paying for unused commitment). Break coverage down by instance family / SKU and surface both *under-covered* (on-demand leakage) and *over-committed* (waste) blocks separately. The recommendation is rarely "buy more commitment"; it is more often "redistribute, or let the over-committed block expire and rebuy at the right size."

7. **Treat storage as a class-mix problem before treating it as a deletion problem.** Most storage savings come from moving objects to the right class (S3 Standard → Infrequent Access → Glacier Instant Retrieval → Glacier Deep Archive; Azure Hot → Cool → Archive; GCS Standard → Nearline → Coldline → Archive), not from deleting data. For each storage service, estimate: percentage of objects that have not been accessed in 30/90/180 days; whether lifecycle policies exist; the gap between current class mix and an optimized mix. Flag any large bucket with no lifecycle policy as a high-leverage win. Be cautious recommending Glacier classes for data that is read with any regularity — the retrieval cost can dwarf the storage savings.

8. **Disaggregate data-transfer egress aggressively.** The single line item "Data Transfer" is famous for hiding a five-figure cross-AZ traffic pattern, a NAT Gateway funnel charge, a public-internet egress that should be a VPC endpoint, or an inter-region replication that should be regional. Decompose egress into: cross-AZ within a region, cross-region within the same cloud, cross-cloud, public internet (broken down by destination if the data allows), CDN-origin pulls, and NAT-Gateway processing. Each has different fixes (VPC endpoints, Private Link, regional replication strategy, CDN caching, NAT alternatives). Egress findings should always pair with an architectural cause hypothesis, not just a dollar number.

9. **Estimate savings with explicit, separable confidence.** Distinguish:
   - **High confidence (≥0.8):** policy-only changes — turning on a lifecycle policy, removing unattached EBS volumes, deleting orphaned snapshots and old AMIs, releasing unused Elastic IPs.
   - **Medium confidence (0.5–0.8):** rightsizing within a family, increasing commitment coverage to a defensible target, switching storage classes for objects with clear access-pattern data.
   - **Low confidence (<0.5):** family migrations (e.g., x86 → Graviton, m5 → m7i), architectural changes (e.g., NAT → VPC endpoint), spot adoption for workloads whose tolerance for interruption is unknown.
   Never aggregate the three into a single headline number without breakdown. "Up to $X/month in savings" with the breakdown is honest; the same number without the breakdown is theater.

10. **Sort the action list by leverage, not by savings size.** Leverage = estimated savings × success probability ÷ effort. A $5K/month win that costs one engineer a half-day beats a $20K/month win that requires a quarter-long migration plus a customer-facing change-window. Surface the top three actions for *this week*, the next set for *this quarter*, and the strategic items for *next year*.

11. **Surface tagging coverage as a first-class finding.** If the audit cannot attribute >70% of spend to a team or product, that is itself the top finding. Recommend a tagging policy push (mandatory tags enforced at create-time via SCPs, Azure Policy, or Org Policy) before any expensive optimization work, because optimization without attribution becomes a political fight rather than an engineering exercise.

12. **Self-check before returning.** Confirm: (a) every dollar figure has a window and a currency; (b) every anomaly has at least two candidate causes; (c) every rightsizing recommendation has a confidence rating and notes whether utilization data was used; (d) commitment-coverage findings call out both under-covered and over-committed blocks; (e) egress findings name an architectural cause; (f) the action list is sorted by leverage; (g) the disclaimer is present; (h) the pricing-snapshot date is named.

13. **Calibrate confidence at the report level.** Top-line confidence below 0.6 should add an explicit "this audit's dataset has gaps that limit its usefulness; before acting, pull the following additional data" note. Common low-confidence drivers: monthly-granularity only; no commitment information; no tagging; unblended-only costs; missing services (e.g., only EC2 exported but spend is dominated by RDS).

## Inputs

- `cost_dataset` (required, file) — CUR / Cost Management export / BigQuery billing export / FOCUS CSV. Larger is better up to a point; >12 months tends to add noise rather than signal.
- `cloud_provider` (required, choice) — anchors taxonomy.
- `audit_window` (optional, text) — default trailing 90 days.
- `known_context` (optional, text) — used to weight findings.
- `tagging_quality` (optional, choice) — drives attribution confidence.
- `commitment_state` (optional, text) — drives coverage-gap analysis.

## Outputs

- `audit_report` (markdown) — header (provider, window, currency, snapshot date, blended/amortized, credits in/out, tax in/out); executive summary (one paragraph + one number with confidence); top 10 cost drivers (service then usage type); anomalies; rightsizing candidates table; commitment coverage breakdown; storage findings; egress findings; tagging coverage finding; prioritized action list; explicit limitations.
- `audit_json` (JSON) — fully structured per the frontmatter schema, for downstream automation (e.g., feeding a ticketing system).

## Examples

### Example 1 — AWS, 90 days, $400K/month

**Input cost_dataset:** AWS CUR (Parquet, hourly, amortized, credits excluded, tax excluded, USD), Feb-Apr 2026.
**cloud_provider:** `aws`. **commitment_state:** "1-year no-upfront Compute Savings Plan, ~$120K/yr, bought 8 months ago." **tagging_quality:** `partial`.

**Output audit_report (excerpt):**

> **Headline.** Spend is $402K/month +/- $18K, growing ~3% MoM. Biggest single-line lever: ~$28K/month of cross-AZ NAT Gateway processing on usage-type `NatGateway-Bytes` from the `data-platform` VPC; high confidence this is architectural and addressable with VPC interface endpoints for S3 and DynamoDB.
>
> **Anomalies.** Week of 2026-03-17 in EC2 SpotUsage: actual $14.2K vs baseline $4.1K. Candidate causes: (a) backfill job restarted from a checkpoint failure, (b) spot capacity churn causing repeated re-launches, (c) a misconfigured Karpenter NodePool with high weight on a costly family. Recommend pulling the EMR/Karpenter logs for that week.
>
> **Commitment coverage.** Account-wide CSP coverage is 71%, but breakdown reveals: r5/r6i general-purpose at 96% covered (healthy); g5/g6 GPU at 4% covered (large on-demand leakage, ~$22K/month exposed); m5 fleet at 118% covered (over-committed by ~$6K/month). Recommend (a) extend GPU coverage via a 1-year no-upfront SP targeted at the g-family, (b) do not renew the existing SP at current size; right-size to ~$104K/yr at next renewal.

### Example 2 — GCP, monthly granularity only

**Input cost_dataset:** GCP billing export, monthly, 6 months, USD. **cloud_provider:** `gcp`. **tagging_quality:** `none`.

**Output audit_report (excerpt):**

> **Header caveat.** Dataset is monthly-only and unlabeled. Per-team attribution is not possible; anomaly detection is limited to MoM step-changes; rightsizing recommendations are restricted to cost-shape heuristics.
>
> **Top finding (confidence 0.9).** Tagging is the highest-leverage investment. Recommend turning on labels enforcement via Organization Policy plus a 30-day backfill via Cloud Asset Inventory before any optimization work. Estimated payoff: enabling all other findings.
>
> **Storage finding.** GCS spend is 17% of total; no lifecycle policies detected (inferred from monotonic growth). Recommend a default Coldline/Archive lifecycle on buckets older than 90 days after access-pattern review. Estimated savings: 30–50% of GCS line, **low confidence** until access logs are in scope.

### Example 3 — Spike investigation

**Input:** Azure cost dump, daily, 30 days. **known_context:** "We launched a new analytics service on 2026-04-10."

**Output audit_report (excerpt):**

> **Confirmed-expected anomaly.** Synapse and Storage Blob spend stepped up ~$3.4K/day starting 2026-04-10, aligned with the documented launch. Not flagged as anomalous.
>
> **Unexplained anomaly.** Azure Front Door egress spiked from $400/day to $2.1K/day on 2026-04-22 with no documented context. Candidate causes: (a) a misconfigured caching rule causing origin pulls, (b) a customer doing an unusually large export, (c) a credential leak driving abnormal request volume. Recommend pulling Front Door logs and WAF telemetry for the day in question.

## Limitations

- The skill cannot fetch live pricing. If the dataset is more than ~30 days stale relative to today, downgrade savings-estimate confidence one notch.
- The skill does not see utilization metrics unless they are provided alongside the cost dataset. Rightsizing recommendations from cost data alone are heuristics.
- Commitment math assumes the org can purchase commitments; some enterprise accounts have purchasing gated on procurement. Surface as a process risk, not a methodology gap.
- Tag-based attribution depends on the org's tagging policy; the skill estimates coverage but cannot fix bad tags.
- The skill does not perform negotiation modelling (Enterprise Discount Program, private pricing). That is a procurement workstream.
- Anomaly detection over short windows (<28 days) is statistically weak; the methodology will flag this and refuse high-confidence anomalies on thin data.

## Sources

The methodology synthesizes patterns from these permissively-licensed open-source FinOps projects (used as reference for usage-type taxonomy, anomaly heuristics, attribution patterns, and rightsizing conventions). No code or text is copied; the methodology is original.

- https://github.com/opencost/opencost
- https://github.com/infracost/infracost
- https://github.com/cloud-custodian/cloud-custodian
- https://github.com/project-koku/koku
- https://github.com/aws-samples/coast-grafana-cost-intelligence-dashboards
- https://github.com/aws-samples/near-realtime-aws-usage-anomaly-detection
- https://github.com/aws-samples/Cost-Anomaly-Detection-Resource-Insight
