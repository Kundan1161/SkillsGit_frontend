---
id: skillsgit-curated/kubernetes-cost-optimizer
version: 1.0.0
name: Kubernetes Cost Optimizer
description: Surface Kubernetes-specific cost levers — requests/limits rightsizing, HPA/VPA tuning, spot adoption, node-pool design, idle workload detection, and namespace chargeback.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:cloud-finops, kubernetes, eks, gke, aks, rightsizing, spot, karpenter, opencost]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  tools_optional: [code_execution, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - kubernetes cost
  - eks cost optimization
  - gke cost optimization
  - aks cost optimization
  - pod rightsizing
  - hpa tuning
  - vpa
  - karpenter design
  - spot adoption
  - cluster autoscaler
  - node pool design
  - namespace chargeback
  - idle workload
example_invocations:
  - "Our EKS cluster is at ~25% CPU utilization across the fleet. Walk me through how to optimize."
  - "Design a node-pool and spot strategy for a Karpenter-managed cluster running mixed batch and online workloads."
  - "Help us set up namespace chargeback using OpenCost data so each product team gets their own cost line."
inputs:
  - name: cluster_profile
    type: text
    required: true
    description: A description of the cluster(s) under review — provider (EKS/GKE/AKS/self-managed), node count and family mix, autoscaler in use (Cluster Autoscaler, Karpenter, GKE Autopilot, AKS Cluster Autoscaler), workload type mix (online services, batch, ML training, data processing).
  - name: cost_data_source
    type: choice
    required: true
    description: What cost telemetry is available. Drives how confidently the skill can attribute spend.
    choices: [opencost, kubecost, cloud_provider_only, none, mixed, unknown]
  - name: utilization_data
    type: text
    required: false
    description: Available utilization signals — Prometheus retention period, kube-state-metrics presence, VPA recommender installed, metrics-server only. Used to estimate how reliable rightsizing recommendations will be.
  - name: workload_profile
    type: choice
    required: false
    description: Dominant workload type the user wants to optimize first.
    choices: [stateless_online, stateful_databases, batch_processing, ml_training, ml_inference, mixed, unknown]
  - name: spot_tolerance
    type: choice
    required: false
    description: Self-assessed tolerance for spot/preemptible interruptions.
    choices: [none, low_for_some_workloads, partial, high, full_except_critical, unknown]
  - name: chargeback_goal
    type: choice
    required: false
    description: Whether chargeback is in scope and at what level.
    choices: [none, showback_only, soft_chargeback, hard_chargeback, unknown]
outputs:
  - name: optimization_report
    type: markdown
    description: Narrative report with current-state findings, prioritized levers (rightsizing, autoscaling, spot, node-pool design, idle detection, chargeback), per-lever estimated impact and effort, and a sequenced 90-day plan.
  - name: optimization_json
    type: json
    description: Machine-readable structure — levers (array of {lever, current_state, recommended_state, estimated_savings_monthly, effort, confidence, prerequisites}), node_pool_recommendation (object), spot_strategy (object), chargeback_recommendation (object), sequenced_plan (array of {phase, lever, weeks_offset}), confidence (float).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Kubernetes Cost Optimizer

## When to use

**Mandatory framing.** This skill produces methodology guidance for Kubernetes cost optimization. Outputs must be reviewed by an engineer with cluster authority before any change is applied. Many recommended actions (lowering pod requests, enabling spot, redesigning node pools, adjusting HPA thresholds) can degrade application reliability if applied without context; the skill cannot see your SLOs and does not have access to your live cluster.

Use this skill when a team has a Kubernetes footprint that is meaningfully expensive — practically, $5K/month and up of cluster spend — and is asking the question "where is this money going and what is the leverage to reduce it without breaking the application?" Typical entry points: a platform engineer whose monthly EKS bill grew 40% YoY without a proportional workload increase; an SRE lead being asked to defend cluster utilization numbers to engineering management; a FinOps practitioner trying to do namespace-level chargeback for the first time; an architect designing a new cluster and wanting the cost-optimal node-pool and autoscaler shape from day one.

The skill is appropriate for *opening the question*. It compresses a few days of cluster spelunking into a structured first-draft plan. It is **not** appropriate as:

- A replacement for SRE judgment. Lowering requests on a customer-facing tier without understanding the SLO is reckless. The skill always recommends a canary-style rollout for any change that could affect availability.
- A live optimizer. The skill does not connect to the cluster, does not write manifests, does not run kubectl. It is methodology, not automation.
- A cost-attribution oracle. If OpenCost or equivalent is not running, namespace attribution will be heuristic at best.

## How to apply

Kubernetes cost optimization is a stack of levers, each with different leverage and different blast radius. The methodology walks the stack in the order that matters: visibility first (you can't optimize what you can't measure), then the high-leverage low-risk levers (idle workloads, bin-packing), then the higher-risk levers (requests rightsizing, spot adoption, autoscaler redesign), then the operating model (chargeback) that locks the gains in.

1. **Confirm the cost-visibility foundation before recommending any optimization.** Without per-namespace, per-controller, per-pod cost attribution, any optimization recommendation is hand-waving. The minimum acceptable foundation is one of:
   - OpenCost (or Kubecost) installed against the cluster with reasonable Prometheus retention (≥14 days, ideally 28+).
   - The cloud-provider's native Kubernetes-cost view (EKS Cost Monitoring, GKE Cost Allocation, AKS cost analysis) with namespace labels propagated.
   - At minimum, a node-cost rollup with namespace tagging via labels — degraded but acceptable.
   If none of these is in place, the first recommendation is "install OpenCost and wait 14 days." Anything else is theater.

2. **Identify idle and zombie workloads first.** This is the highest-leverage, lowest-risk lever in almost every cluster. Surface:
   - **Deployments with 0 ready pods that have been at 0 for >7 days** — orphaned, can be deleted after owner confirmation.
   - **Deployments running but never receiving traffic** — typically dev or staging services left running. PromQL pattern: services whose `istio_requests_total` or equivalent is zero over 7 days while pods are healthy. Recommend HPA-min-zero with Keda, or scheduled scale-to-zero outside business hours.
   - **PersistentVolumes attached to deleted pods** — direct cost with zero workload value.
   - **Old replicasets with non-zero history depth** — minor but worth a pass.
   Idle-workload cleanup typically returns 5-15% of cluster cost with near-zero risk. Always do this first.

3. **Walk the requests-and-limits problem with utilization data, not vibes.** Pod CPU/memory requests determine bin-packing; requests are what the scheduler and autoscaler see. The classic finding — 60% of clusters bill in CPU requests that are 4-10x p95 actual usage — is usually true and is the single biggest source of structural waste.
   - Pull p50, p95, p99 utilization for each pod template over a 14-day window.
   - Recommend requests at roughly p95 + a buffer, where buffer is workload-dependent (10-15% for stateless online, 25-50% for stateful, 100%+ for memory of GC'd runtimes that have caching behavior).
   - **Never set requests = p99 without understanding the runtime.** For JVM workloads, memory requests should accommodate the heap plus non-heap (metaspace, direct buffers, code cache); a too-tight memory request causes OOMKills, which is a worse outcome than a moderately-high request.
   - For CPU, limits should generally be *unset* or set far above requests — CPU throttling at the limit is a notorious latency-degradation source. Memory limits should match or modestly exceed requests; unbounded memory is worse than CPU.
   - Use Goldilocks-style VPA-recommendation tooling as the data source, not VPA in auto-update mode, which is rarely safe in production for online services.
   - Stage rollouts: dev → staging → one canary cell in production → broader prod. Never bulk-edit all production workloads in one PR.

4. **Tune HPA before introducing VPA in production.** HPA reacts to load; VPA reacts to long-term utilization shape. The two interact badly when uncoordinated (HPA scales replicas, VPA scales pod size, both based on the same signal). Default:
   - HPA on the workload's natural load signal (CPU is the default but is often wrong — request-rate, queue-depth, or in-flight-requests are usually better).
   - VPA in **recommendation-only** mode for sizing data, applied manually via deployment template updates during normal release cycles.
   - HPA's `behavior` block tuned: longer stabilization on scale-down (5-10 minutes), shorter on scale-up, to avoid thrash that creates fleeting-but-real cost.

5. **Redesign node pools around workload archetypes, not historical accidents.** Most clusters have node pools that grew organically and now have either too many (operational noise) or too few (poor bin-packing) groups. The methodology:
   - One pool for **online stateless services** — modest-sized instances (e.g., m-family medium-large), on-demand or 1-yr commitment, high taint tolerance.
   - One pool for **batch and CI** — spot/preemptible, larger instances for better packing, generous scale-to-zero.
   - One pool for **stateful workloads** — on-demand, larger memory, often with topology spread constraints and PVC affinity.
   - One pool for **GPU workloads** — separate by GPU family; never share with general-purpose because of bin-packing pathology.
   - With Karpenter, this can be expressed as multiple NodePools with explicit `requirements` rather than statically-sized ASGs.

6. **Adopt spot/preemptible by *workload class*, not by percentage.** "We want 50% spot adoption" is a target that produces bad decisions. Better:
   - **Always spot:** batch, CI, stateless idempotent workers, dev/staging.
   - **Mostly spot with on-demand floor:** stateless online services where the application tolerates a controlled interruption (graceful drain, PDB-aware), with a minimum on-demand pod count to absorb the interruption.
   - **Never spot:** stateful databases, long-running data-pipeline jobs that can't checkpoint, anything single-replica.
   With Karpenter, this is encoded via `karpenter.sh/capacity-type` and PDBs. With Cluster Autoscaler, this is via separate ASGs and node selectors.
   Spot adoption typically returns 50-80% of compute cost on the adopted workloads, but the operational cost (drain-handling, PDB hygiene, monitoring of interruption rates) is real — recommend a 4-6 week ramp.

7. **Treat the autoscaler choice as architectural, not as a default.** The choice between Karpenter, Cluster Autoscaler, GKE Autopilot, AKS Cluster Autoscaler, and KEDA-for-workload-scaling is a real decision:
   - **Karpenter (EKS, increasingly on GKE):** strong default for new clusters; flexible NodePool design; native consolidation; spot-aware. The cost-optimization win comes mostly from its consolidation behavior (moves pods to fewer nodes when possible) and from removing the manual ASG math.
   - **Cluster Autoscaler:** mature; works everywhere; less flexible. Acceptable for stable clusters; consider migration if cluster has frequent node-shape changes.
   - **GKE Autopilot:** trades per-pod premium for zero node management. The math wins for small-to-medium clusters with stable workloads; loses for large or volatile clusters.
   - **KEDA:** event-driven workload scaling (scale-to-zero on queue depth, custom signals). Pairs with one of the above; not a replacement.

8. **Stand up chargeback only after the technical levers have been pulled.** Chargeback is an operating-model change, not a technology one. It tells you who owns the cost; it doesn't reduce the cost. Recommend:
   - **Showback first:** per-namespace cost reports sent to the namespace owners weekly, no consequences. This builds awareness and surfaces tagging-and-attribution gaps.
   - **Soft chargeback next:** cost lands on the team's budget but does not affect personal/team-level performance metrics. Pairs well with a goal-setting cycle.
   - **Hard chargeback last (and rarely):** an internal billing transaction. Powerful but creates incentives to game the system (artificial spread, premature optimization). Only appropriate in mature orgs with strong tagging and a real budgeting process.

9. **Surface the "shared cost" attribution problem honestly.** A lot of cluster cost is *shared* — system pods, ingress controllers, monitoring stack, control-plane premium. Allocating these proportionally by namespace usage is a defensible default; allocating them equally per namespace is also defensible but produces different incentives. Recommend one method, state it explicitly, and stick with it.

10. **Sequence the plan over 90 days.** A typical recommended sequence:
    - **Weeks 1-2:** Install/verify OpenCost. Pull baseline cost-by-namespace report. Communicate the upcoming initiative.
    - **Weeks 3-4:** Idle-workload sweep. Quick wins. Build credibility.
    - **Weeks 5-8:** Requests rightsizing, dev/staging first, prod canary by week 7.
    - **Weeks 9-12:** Node-pool redesign and spot adoption on the safe workload classes.
    - **Weeks 13+:** Showback launch; iterate.
    Adjust based on cluster size and team bandwidth. A team of two cannot do this in 90 days for a 500-node cluster.

11. **Self-check before returning.** Confirm: (a) the visibility foundation question has been addressed; (b) every recommendation has an estimated savings range, an effort level, and a confidence; (c) idle-workload sweep is recommended before rightsizing; (d) rightsizing is gated on having utilization data; (e) spot adoption is broken down by workload class, not as a percentage; (f) chargeback is not recommended until later phases; (g) the disclaimer is present.

12. **Calibrate confidence.** Below 0.6, recommend a 30-day baseline-data collection phase before any aggressive action. Common drivers: no OpenCost; no Prometheus history; mixed cluster ownership where workload owners can't be reached; very high churn in deployments.

## Inputs

- `cluster_profile` (required, text) — provider, scale, autoscaler, workload mix.
- `cost_data_source` (required, choice) — gates which recommendations are unlocked.
- `utilization_data` (optional, text) — gates the confidence of rightsizing recommendations.
- `workload_profile` (optional, choice) — biases the recommendations toward the dominant workload.
- `spot_tolerance` (optional, choice) — caps the spot-adoption recommendation.
- `chargeback_goal` (optional, choice) — drives whether chargeback content appears in the plan.

## Outputs

- `optimization_report` (markdown) — current-state summary (cluster shape, visibility maturity); idle-workload findings; rightsizing plan with utilization caveats; HPA/VPA recommendations; node-pool redesign sketch; spot strategy by workload class; chargeback recommendation; 90-day sequenced plan; explicit limitations.
- `optimization_json` (JSON) — fully structured per the frontmatter schema.

## Examples

### Example 1 — EKS, ~50 nodes, ~$30K/month, Karpenter

**Input cluster_profile:** "EKS 1.30, ~50 nodes mixed m5/m6i, Karpenter as autoscaler, ~250 pods across 12 namespaces; mostly online Go services, some Python ML inference, no batch." **cost_data_source:** `opencost`. **utilization_data:** "Prom retention 30d, kube-state-metrics yes, no VPA installed." **workload_profile:** `mixed`. **spot_tolerance:** `partial`.

**Output optimization_report (excerpt):**

> **Current state.** OpenCost reports ~$31K/month, of which 18% is the `staging` namespace and 12% is `default` — both candidates for sweep. Average CPU request-to-usage ratio cluster-wide is ~6.2x (p95 actual is ~16% of requested). This is the dominant waste shape.
>
> **Lever 1 — idle (estimated savings $2-4K/month, low effort, high confidence).** `staging` has 9 deployments with no traffic in 14 days; recommend `Keda` scale-to-zero outside business hours.
>
> **Lever 2 — requests rightsizing (estimated savings $6-10K/month, medium effort, medium confidence).** Install Goldilocks in recommendation mode for 14 days, then trim requests on the top-10 most-expensive deployments first. Stage dev → staging → 1 canary prod cell → fleet.
>
> **Lever 3 — spot for the ML-inference pool (estimated savings $1.5-3K/month, medium effort, medium confidence).** Add a Karpenter NodePool with `karpenter.sh/capacity-type: spot` for the `ml-infer` namespace; require PDB minAvailable=1, image pre-pull, and a 2-minute drain hook. Do **not** put online Go services on spot in phase 1.
>
> **Do not yet:** chargeback (premature; one team owns 80% of the cluster); VPA auto-mode (no production track record); broad on-demand → spot migration (interruption-handling not yet proven on this workload).

### Example 2 — GKE Autopilot, small cluster

**Input cluster_profile:** "GKE Autopilot, ~$4K/month, 5 namespaces, all stateless." **cost_data_source:** `cloud_provider_only`. **chargeback_goal:** `showback_only`.

**Output optimization_report (excerpt):**

> **Current state.** Autopilot is paying per-pod. The dominant lever is requests rightsizing — Autopilot's premium magnifies overprovisioning.
>
> **Lever 1.** Install OpenCost (community Helm chart) for per-namespace visibility, since GKE's native view is workload-level only at this scale.
> **Lever 2.** Pull pod utilization from Cloud Monitoring; reduce requests on overprovisioned pods. Estimated 20-30% savings if the typical Autopilot overprovisioning pattern holds.
> **Lever 3.** Showback only — too small for chargeback. Send a weekly per-namespace summary.

### Example 3 — large ML training cluster

**Input cluster_profile:** "Self-managed Kubernetes on AWS, 200 nodes, mostly g5/g6 GPUs, ML training workloads, Cluster Autoscaler." **spot_tolerance:** `high`. **chargeback_goal:** `soft_chargeback`.

**Output optimization_report (excerpt):**

> **Current state.** GPU clusters have very different cost mechanics from general-purpose. The dominant levers are (a) checkpoint-and-restart discipline so spot is safe, (b) GPU bin-packing (multiple smaller jobs on one node beats one job per node when shapes allow), (c) idle GPU detection (notorious — researchers leave nodes provisioned overnight).
>
> **Lever 1.** Idle-GPU detection. PromQL on `DCGM_FI_DEV_GPU_UTIL` < 5% for >30 minutes; auto-cordon and notify the user. Estimated savings 15-30% in research-heavy clusters.
> **Lever 2.** Spot GPU pools. AWS g5/g6 spot interruption rates are workload-dependent but typically <10%. Combined with frequent checkpoint cadence, spot adoption on training jobs is the largest single lever; estimated 40-60% on those workloads.
> **Lever 3.** Soft chargeback per research team. GPU spend is one of the few areas where researchers' incentives respond to cost visibility.

## Limitations

- The skill does not access the cluster. All recommendations are conditional on the user's description being accurate.
- Rightsizing recommendations without utilization data are heuristics, not measurements. Confidence drops accordingly.
- Spot interruption rates vary by region, instance type, and time of day in ways the skill cannot predict. Estimated savings assume historical-average interruption behavior; pilot before scaling.
- The skill does not generate manifests or Karpenter NodePool YAML. That is implementation work.
- Cluster autoscaler behavior under load differs by version and config; recommendations are at the design level, not the parameter level.
- Chargeback recommendations are operational guidance, not accounting or tax advice; internal-billing implementations should be reviewed with finance.

## Sources

The methodology synthesizes patterns from these permissively-licensed open-source Kubernetes-cost projects (used for cost-attribution conventions, VPA-recommender usage, NodePool design idioms, and scale-to-zero patterns). No code or text is copied; the methodology is original.

- https://github.com/opencost/opencost
- https://github.com/aws/karpenter-provider-aws
- https://github.com/kubernetes-sigs/karpenter
- https://github.com/FairwindsOps/goldilocks
- https://github.com/cloud-custodian/cloud-custodian
- https://github.com/kubecost/cost-analyzer-helm-chart
- https://github.com/infracost/infracost
