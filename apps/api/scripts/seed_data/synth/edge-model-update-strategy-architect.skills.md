---
id: skillsgit-curated/edge-model-update-strategy-architect
version: 1.0.0
name: Edge Model Update Strategy Architect
description: Design fleet-wide OTA model-update strategy — signed payloads, canary cohorts, rollback triggers, telemetry pipeline, atomic A/B partitions, kill-switch, and version-skew handling between client and model.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:edge-inference, ota-updates, model-deployment, canary-rollout, rollback, code-signing, atomic-partition, kill-switch, telemetry, version-skew]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: []
  tools_optional: [web_search, code_execution, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8800
trigger_keywords:
  - edge model update strategy
  - ota model rollout
  - fleet model deployment
  - canary cohort selection
  - signed model payload
  - rollback trigger design
  - telemetry pipeline edge
  - atomic a/b partition
  - kill switch model
  - version skew client model
  - edge cache eviction
  - model promotion gate
example_invocations:
  - "Design an OTA strategy to push a new vision model to 200,000 devices without bricking the fleet."
  - "Plan the canary cohort, rollback triggers, and telemetry pipeline for a quarterly model refresh."
  - "How do we handle version skew between the client app and the model file when an older app gets a newer model?"
inputs:
  - name: fleet_description
    type: text
    required: true
    description: Fleet size, device classes and tiers, OS minimums, baseline connectivity, update channel currently in use, and the failure modes the team has already seen.
  - name: model_description
    type: text
    required: false
    description: Model family or families being updated, file sizes, runtime in use, input or output schema, and any backward-compatibility obligations between model versions.
  - name: telemetry_capability
    type: text
    required: false
    description: What telemetry the platform already collects and what the legal and product limits on telemetry are. Drives the gating signals available to the rollout.
  - name: update_cadence
    type: choice
    required: false
    description: How frequently the team intends to ship model updates and whether updates can be paused mid-rollout.
    choices: [continuous, weekly, monthly, quarterly, on-incident-only]
  - name: ops_capacity
    type: choice
    required: false
    description: Team capacity for staffing the rollout — drives how elaborate the gates and dashboards can realistically be.
    choices: [solo, small_team, dedicated_ml_platform]
  - name: criticality_class
    type: choice
    required: false
    description: How severe a bad update would be — drives signing rigor, canary breadth, and rollback aggressiveness.
    choices: [consumer-low-risk, consumer-high-trust, industrial, safety-relevant]
outputs:
  - name: update_strategy
    type: markdown
    description: A written rollout strategy covering payload signing, canary cohorts, gates, rollback triggers, kill-switch, telemetry, edge-cache management, atomic partition design, and version-skew handling.
  - name: design_json
    type: json
    description: Machine-readable plan with `payload`, `signing`, `canary_cohorts`, `gates`, `rollback_triggers`, `kill_switch`, `telemetry`, `cache_policy`, `partition_layout`, `version_skew_policy`, `open_risks`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Edge Model Update Strategy Architect

## When to use

Use this skill when a team is responsible for pushing a machine-learning model to a fleet of devices it does not directly operate — phones, kiosks, set-top boxes, point-of-sale terminals, robots, industrial cameras, automotive head-units, gateways, or appliances — and needs a strategy for shipping new model versions without surprising the fleet. The deliverable is a written strategy, not running code. The strategy answers seven questions: how the model payload is built and signed; how a device decides to accept and load a new model; how the team rolls a new model out to a fraction of the fleet before everyone else; what signals demand a rollback; how the team kills a bad model fast; how the team learns from the fleet what is going wrong; and how the client app and the model file stay compatible across asynchronous updates.

The skill is appropriate for any team that ships models at any cadence beyond "rebuild the app each release". It is most valuable when models are updated independently of the application binary, when the fleet is too large to babysit, when the cost of a bad update is high enough that "ship and pray" is not acceptable, and when devices may sit on stale versions for weeks at a time.

It is not the right skill for designing the model itself, for designing the inference pipeline on a single device (use the edge inference pipeline architect), or for designing server-side model serving where the operator controls every instance. It assumes the team has already chosen a runtime and a packaging format.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `fleet_description` | yes | Anchors device classes, scale, baseline connectivity, and prior failure modes. |
| `model_description` | no | Drives payload size, signing scheme rigor, and version-compatibility plan. |
| `telemetry_capability` | no | Determines the gating signals available to the canary policy. |
| `update_cadence` | no | Shapes how compact the rollout state machine must be. |
| `ops_capacity` | no | Scopes how elaborate gates, dashboards, and on-call rotations can be. |
| `criticality_class` | no | Sets the signing rigor, canary breadth, and rollback aggressiveness. |

## How to apply

This skill walks an eighteen-stage pipeline. Stages 1 through 4 frame the problem. Stages 5 through 10 design the payload, signing, and partition layout. Stages 11 through 15 design the canary rollout, gates, rollback, and kill-switch. Stages 16 through 18 produce the deliverable.

### Stage 1 — Restate the rollout job

1. Take `fleet_description` and write down the deployment surface: number of devices, device tier distribution, OS minimums, the channel the team currently uses to push updates, whether device check-in is push-based or pull-based, and the fraction of devices online at any given moment.
2. Write down the worst-case cost of a bad update: corrupted local state, app crash, accuracy regression that silently corrupts downstream features, billing impact, regulatory impact, brand impact. The cost class drives every later decision; an industrial fleet and a casual consumer app deserve different rigor.
3. Write down the *update unit*: the smallest artifact the team ships independently. A single model file is the common case; a model bundled with a tokenizer, a pre-processor, a prompt template, and a runtime patch is another. The strategy treats the update unit as atomic and signs and rolls it back as a single object.
4. Note prior incidents — past bad updates, past silent regressions, past versioning bugs. The strategy is shaped by those scars, not by a generic checklist.

### Stage 2 — Define the update lifecycle

5. The update lifecycle is the state machine the team operates against: *built* (artifact produced in CI), *signed* (artifact has a valid signature against the production key), *staged* (artifact is in the distribution channel but not addressable by clients), *canary* (a named subset of clients is eligible to receive it), *rolling* (eligibility expands over cohorts), *generally-available* (any eligible client may receive it), *deprecated* (no new client may receive it, existing clients may keep using it), *recalled* (clients are instructed to roll back or refuse). Every model artifact transitions through this state machine and the system records every transition.
6. Specify which transitions are gated by an automated check and which require a human approval. Production rollouts always require human approval to enter `generally-available`; the human reviews the canary telemetry before approving.
7. Specify *time-in-state* expectations: a canary that sits for less than a defined window cannot graduate. The window guards against the "looks fine for an hour" failure mode that catches teams when an issue surfaces only at peak hour or under a weekly batch job.

### Stage 3 — Pick the artifact and metadata format

8. Define the artifact as a *bundle* with a deterministic layout: the model weights, any preprocessor or tokenizer, a manifest file listing every component with its hash, a compatibility descriptor (minimum client app version, runtime version, hardware capability bits), and a human-readable release-notes block. The bundle is content-addressed by the hash of its manifest.
9. Define the *version identifier* as a triple of (model-version, manifest-hash, signing-key-id). The model-version is the human label; the manifest-hash is the immutable identity used by every system to refer to this build; the signing-key-id pins which key signed it.
10. Define what the manifest declares about the model: input schema, output schema, expected hardware capabilities, expected runtime version range, memory and storage footprint, and any side-effect declarations (does the model require new permissions, does it call out to a remote endpoint, does it write a cache). The on-device loader uses the manifest to refuse a bundle it cannot satisfy.

### Stage 4 — Build a clean codesign chain

11. The signing chain has three layers: a root key held offline in a hardware security module, intermediate keys for environments (production versus staging versus development), and per-build signing operations. Production keys never leave the HSM; build-time signing is a request to the HSM, not a copy of the key.
12. Every artifact is signed at build time before it enters the distribution channel. The signature covers the manifest hash, not the file bytes directly; the manifest, in turn, covers every component's hash. This nesting means a tampered single component invalidates the manifest hash, which invalidates the signature.
13. Define the *verify-before-load* contract on the device. The client never executes a model that has not been verified against an embedded set of pinned root keys. Verification happens after download, after on-disk integrity check, and one more time immediately before load. Two-of-three is not enough; all three are required because they catch different threats.
14. Define *key rotation*: a planned schedule for rotating intermediate keys, a tested emergency rotation path for compromised keys, and a forward-compatibility window where clients accept either the old or the new intermediate key during a rotation window.
15. Define *signature failure semantics*: a client that fails verification refuses the bundle and reports the failure via telemetry. A client never falls back to an unsigned bundle, ever, regardless of how stale its current model is.

### Stage 5 — Atomic A/B partition layout on the device

16. Design the on-device storage as two named slots, an *active* slot and an *inactive* slot. A new bundle is written into the inactive slot; on commit, the active pointer flips to the inactive slot. The previous slot's contents remain on disk for as long as storage permits, supporting a fast rollback by flipping the pointer back.
17. Make the slot flip a single atomic write — a journaled symlink swap, a database transaction, or a vendor-supplied atomic partition switch. The fleet must never end up with neither slot active or both slots active.
18. Define a *boot-time integrity check* that re-validates the active bundle before the app uses it. If validation fails, the app reverts the slot pointer to the prior slot and reports the failure. This is the safety net for a write that succeeded on disk but corrupted in flight.
19. Define *staging space* policy when storage is tight. On low-storage devices, the inactive slot may be evicted to recover space; the policy must record that eviction happened so the team knows the device is one slip away from being unable to roll back.
20. Where the runtime supports it, prefer the platform's native A/B update primitive (the OS-supplied update mechanism) over a custom one. The platform's mechanism handles power-loss durability that a custom one is unlikely to get right on the first try.

### Stage 6 — Distribution channel and CDN policy

21. The distribution channel serves signed bundles by manifest hash. Clients fetch by hash, not by name. A name-to-hash mapping is held in a small, fast index that the client polls; the bundles themselves are immutable and infinitely cacheable.
22. Define cache invalidation policy. Bundles never invalidate (they are content-addressed and immutable); the name-to-hash mapping may invalidate when a new release is promoted or recalled. Caching the mapping for a short window is acceptable; caching it for hours is dangerous because a recall takes too long to propagate.
23. Define *bandwidth ceilings*. A fleet of 200,000 devices that each download a 200-megabyte model in the same hour will saturate any CDN tier without active rate-shaping. The strategy spreads the rollout over a window proportional to the fleet's bandwidth budget.
24. Define *resume and retry* semantics. Mobile and embedded clients lose connectivity mid-download routinely; the strategy specifies resumable downloads and bounded retries with exponential backoff, capped to a daily budget so a stuck client does not consume the user's data allowance.

### Stage 7 — Edge cache management

25. Decide what the device keeps on local storage. The active bundle is always kept; the previous bundle is kept for the rollback window; older bundles are evicted on a least-recently-needed schedule.
26. Where the device serves multiple models (a vision model and an audio model, say), the cache budgets are allocated per model family, with a documented priority order for eviction when storage pressure rises.
27. The cache is *not* a security boundary. Anything stored locally must be assumed to be readable by a curious user; sensitive model weights need a complementary protection layer outside the cache policy.

### Stage 8 — Client-side eligibility and check-in protocol

28. The client polls a small *eligibility endpoint* on a defined cadence. The endpoint returns, per-client, the set of bundle hashes the client is eligible to receive, in priority order. The client downloads the highest-priority bundle it does not have and that fits its storage and connectivity envelope.
29. Define the *check-in cadence*: aggressive enough that a recall propagates within the rollback window, gentle enough that the eligibility endpoint does not get pounded. A common pattern is on-app-foreground plus a daily background poll with jitter.
30. Define what the client reports on check-in: current active hash, current inactive hash, current runtime version, current app version, hardware capability bits, last verification status, and last applied gate decision. The eligibility endpoint uses these to refuse to advance a client whose state is inconsistent.

### Stage 9 — Canary cohort selection

31. A canary cohort is a named, persistent subset of the fleet that receives a new bundle before the rest of the fleet. Cohorts are layered: an *internal* cohort (employees, test devices), an *opt-in* cohort (beta-programme users), a *small-percentage* cohort (a stratified random sample of the production fleet), and a *broad* cohort (a larger random sample that gates `generally-available`).
32. Cohort selection is *sticky*: a device assigned to the 1% cohort stays in that cohort across releases unless deliberately rotated. Sticky cohorts make telemetry comparable across releases and prevent the same unlucky device from being a canary every time.
33. Cohort *stratification* covers device tier, OS version, region, and traffic level. A canary that under-samples low-end devices misses the most common production failure mode; a canary that under-samples a region misses locale-specific bugs.
34. Define *canary size by criticality class*. Consumer-low-risk products may graduate from 1% to 100% in days; safety-relevant products require multi-week canaries at multiple sizes with explicit human review at each gate.

### Stage 10 — Telemetry gating signals

35. Define the per-bundle metrics the rollout watches. Engagement metrics (crash rate, ANR or watchdog rate, foreground time, retention) drive whether the model is destabilising the app. Inference metrics (latency p50 and p95, success rate, refusal rate, verification-failure rate) drive whether the model itself is healthy. Quality metrics (downstream consumer feedback, on-device A/B comparisons against the prior model, accuracy proxies where available) drive whether the model is regressing on output quality.
36. Where the team has cohort-comparable evaluation infrastructure (see the multimodal eval harness designer), pipe a *shadow score* per device or per cohort that estimates output quality and is comparable across model versions.
37. Define *guardrail metrics* that the strategy refuses to regress on. A new model that improves accuracy at the cost of doubling p95 latency or doubling crash rate is not eligible for promotion; the guardrail is a hard precondition, not a tradeoff.
38. Define *novel-signal monitors*: a metric that has never been seen before on this fleet (a new crash signature, a new refusal pattern, a new accuracy class) is reported as a separate alarm even if no single metric crossed its threshold. Novelty itself is a risk signal.

### Stage 11 — Gates that promote a bundle through the lifecycle

39. Define a *gate* as a tuple of (cohort, metrics, threshold, time-in-state, human-approval). A gate evaluates whether a bundle in one state may advance to the next state. Promotion to `canary` requires a passing build, a valid signature, and a green internal cohort. Promotion to `rolling` requires the canary cohort to hold for a time-in-state window with no regression on guardrail metrics and a positive trend on inference success. Promotion to `generally-available` requires named human approval after reviewing the canary dashboard.
40. Promotion is *one-way* on the timescale of a rollout. A bundle that has graduated to `generally-available` is not silently demoted; if it must come back, it enters `recalled` and the next bundle takes its place.
41. Define *gate observability*. A gate that fails records why, what cohort, what metric, what value, what threshold. Silent gate failures are a leading cause of harness rot.
42. Define *override discipline* for gate failures. Overrides require a named approver, a written justification, and an attached follow-up ticket. Override usage is itself a tracked metric — a team that overrides routinely is in technical debt that the strategy must surface.

### Stage 12 — Rollback triggers and policy

43. Define the rollback triggers: a sustained regression on a guardrail metric beyond a documented band, a spike on a novel-signal monitor, a verification-failure rate above a low ceiling on the canary cohort, a downstream-consumer accuracy alarm tied to a known regression-cohort item, a crash-rate spike on a specific device tier.
44. Define rollback *granularity*. The strategy supports rolling back a single bundle for the cohort that received it (a partial rollback) and rolling back fleet-wide (a full rollback). The default for safety-relevant criticality classes is full rollback on first trigger; consumer-low-risk classes may use partial rollback first to limit blast radius.
45. Define the *rollback path on the device*. The client receives a new eligibility entry that names the prior bundle hash as the preferred bundle; the client flips its A/B pointer back to the prior slot (which is still on disk) and resumes service. No new download is required; this is the entire point of the A/B layout.
46. Define a *rollback budget*: how many devices the channel can roll back per unit time without saturating telemetry intake and on-call. The budget shapes how aggressive the rollback can be without becoming an outage in its own right.

### Stage 13 — Kill-switch design

47. The kill-switch is the hardest control surface in the strategy and the easiest to break in a panic. It is a small, mechanically simple capability with the single function of disabling a named bundle on every device that has it, immediately, regardless of the rest of the rollout state.
48. The kill-switch operates by publishing a *deny-list* of bundle hashes through the eligibility endpoint and, where possible, through a secondary fast-path channel that bypasses normal cache TTLs. A client that sees one of its loaded bundle hashes in the deny-list refuses to use it on the next inference call and falls back to the prior bundle or to a documented safe-fallback path.
49. The kill-switch is *tested on a schedule*. An untested kill-switch is not a kill-switch; the team runs a quarterly drill that exercises the deny-list path end-to-end on a non-production bundle.
50. Access to the kill-switch is gated and audited. A small number of named operators may publish to the deny-list; every publish is logged with the operator, the time, the affected hash, and the reason.

### Stage 14 — Telemetry pipeline back to training

51. The fleet's telemetry must reach the training side of the team within a useful turnaround. Define the pipeline: device telemetry to ingest, ingest to filtering and PII scrubbing, filtering to the data lake, lake to the harness's hard-case-mining pipeline, hard-case items to the next training run's data slice.
52. Define *enrichment*: the device telemetry record includes enough context (bundle hash, runtime version, hardware bits, app version, anonymized cohort id) to reconstruct the inference environment offline. Without that context, the data lake is a graveyard.
53. Define *privacy floors*: raw inputs do not leave the device unless the user or contract explicitly permits. Where raw inputs cannot leave, the device computes and uploads a feature digest or a probe response rather than the input itself.
54. Define the *feedback loop expectations*: how often the team expects to see a fleet-observed failure mode appear as a labelled training example, and what the latency from observation to next-release inclusion is. A team that cannot answer this question has a one-way pipeline that does not learn.

### Stage 15 — Version-skew handling between client and model

55. Client and model evolve on different cadences. The strategy specifies the compatibility contract: the bundle manifest declares the minimum client app version it supports and the maximum client app version it has been validated with; the client refuses to load a bundle outside that range and reports the refusal.
56. Define *forward-compatibility* policy. A client receiving a bundle with new output fields ignores fields it does not recognize and continues to operate on the fields it does. A client receiving a bundle with new input fields it cannot supply refuses the bundle. The asymmetry favours adding optional outputs over adding required inputs.
57. Define *backward-compatibility* obligations on the model. A new model version that breaks the existing output schema requires either a coordinated app-and-model release or a translation shim that maps the new schema onto the old. Silently breaking schema is the most common version-skew bug.
58. Define *deprecation windows*. When the team intends to retire a bundle, the eligibility endpoint stops handing it out new (so the channel drains), and the client receives a "deprecated" flag in its check-in response with a window before refusal. Clients with stale apps that cannot upgrade are routed to a documented fallback model rather than being left to fail silently.
59. Where the model uses prompt templates or tokenizers as separate artifacts, version those alongside the model and pin the compatible ranges in the manifest. Mismatched tokenizers are a top cause of "the model is fine but the output is wrong" incidents.

### Stage 16 — Operator communications

60. Where the fleet includes operators or administrators (kiosks, robots, industrial gateways, enterprise-managed devices), define the comms surface. A scheduled-update calendar tells operators what to expect; a release note describes the change; an incident channel reports recalls and degradations promptly.
61. Define *operator-controlled holds*: an operator may pin a device to a specific bundle for a window (regulatory inspection, an in-flight project that cannot tolerate change). The eligibility endpoint honours holds and reports them in fleet dashboards.
62. Define *consumer-side messaging* where end-users see model behaviour change. A model that materially changes user-visible behaviour is announced; silent behaviour shifts erode trust.

### Stage 17 — Risk register and open questions

63. Enumerate residual risks. Key compromise (the signing chain depends on operational discipline beyond what the strategy can enforce by itself). Telemetry blind spots (a metric the team is not collecting may be the one that matters). CDN single-point-of-failure (the channel can be a fleet-wide outage source). Manifest evolution (changes to the manifest schema itself are version-skew bugs at one level up). Kill-switch latency (the deny-list path is only as fast as its slowest cache TTL). Stuck devices (a fraction of the fleet will not check in for weeks; the strategy treats them as a tracked tail).
64. Maintain a known-unknowns register of failure modes the team has not characterized. The rollout-on-call engineer is expected to add to it as field events surface.

### Stage 18 — Compose the deliverable

65. Open with a one-paragraph statement of the rollout intent: what the update unit is, what fleet it covers, what cadence it ships on, and what the worst-case blast radius is.
66. Render the lifecycle state machine as a diagram-described-in-prose. Render the signing chain. Render the partition layout. Render the cohort table with size and stratification. Render the gate matrix. Render the rollback trigger table. Render the kill-switch path. Render the telemetry-and-training feedback loop.
67. Emit `design_json` with structured fields so a downstream tool can derive a CI configuration, a rollout-orchestrator configuration, an on-call runbook, and an audit log schema from the JSON.
68. Close with the open-risks list, a "what this design does not cover" section pointing at the edge inference pipeline architect, the multimodal eval harness designer, and the on-device deployment skills, and the explicit limitation that model regressions in safety-critical fleets require qualified-engineer sign-off — automated gates and rollbacks are decision-support, not authority.

## Outputs

The skill returns:

1. `update_strategy` (markdown) — a structured plan covering payload, signing, partition layout, distribution channel, canary cohorts, gates, rollback triggers, kill-switch, telemetry pipeline, version-skew policy, operator comms, and risk register.
2. `design_json` (JSON) — a machine-readable plan suitable for downstream orchestration.

## Examples

**Input (placeholder):**

`fleet_description`: "180,000 industrial inspection cameras across three regions, on a mix of LTE and wired backhaul, each running an embedded Linux with a vendor-supplied A/B partition primitive, checking in once per hour."

`model_description`: "An object-detection model, roughly 80 megabytes quantized, paired with a small calibration file and a configuration JSON. Quarterly cadence, with backward-compatible output schema."

`telemetry_capability`: "Per-device crash, watchdog, inference latency, inference success, and an on-device shadow-eval comparison against the prior model on a small embedded probe set; raw inputs do not leave the device."

`update_cadence`: "quarterly."

`ops_capacity`: "small_team."

`criticality_class`: "industrial."

**Plan (abbreviated):**

- Update unit: signed bundle of model weights, calibration file, configuration JSON, and a manifest. Identity is the manifest hash; production signing chain rooted in an HSM with quarterly intermediate-key rotation.
- Lifecycle: built, signed, staged, canary, rolling, generally-available, deprecated, recalled. Time-in-state minimums of three days for canary and seven days for rolling.
- Partition: vendor A/B primitive, boot-time integrity check, previous bundle retained until disk pressure forces eviction.
- Canary cohorts: internal (~50 devices), opt-in (~500), small-percentage (1%, stratified across region and device tier), broad (10%) before generally-available.
- Gates: inference success rate, p95 latency, watchdog rate, shadow-eval score not regressing beyond a rolling band, verification failure below a low ceiling; human approval to graduate to generally-available.
- Rollback: triggers on guardrail regression, watchdog spike, verification-failure spike, or shadow-eval regression. Default to fleet-wide rollback for industrial criticality; A/B slot flip on the device.
- Kill-switch: deny-list published via the eligibility endpoint plus a secondary fast-path; quarterly drill on a non-production bundle.
- Telemetry to training: filtered, enriched with bundle hash and cohort, fed into the next-release hard-case pool.
- Version-skew: manifest declares supported client app version range; tokenizer-equivalent calibration file is versioned alongside the model.
- Operator comms: scheduled-update calendar, release notes, operator-controlled holds.

**Output excerpt:** the markdown strategy plus a JSON object whose `canary_cohorts` array enumerates each cohort with size and stratification, `rollback_triggers` lists triggers with thresholds, `signing` documents the chain, `partition_layout` documents the A/B scheme, and `version_skew_policy` documents the compatibility contract.

## Limitations

- The skill produces a strategy, not an orchestration system or a CDN. The team must build or buy the underlying infrastructure and connect it to the strategy's contracts.
- The skill assumes the team can collect telemetry from the fleet. Without telemetry, the canary gates are blind and the strategy degrades to a slow uniform rollout, which is the minimum viable safety net but is not what the deliverable is designed for.
- The skill is conservative on signing, kill-switch, and rollback for industrial and safety-relevant criticality. Research and consumer-low-risk teams may relax explicitly with written rationale.
- Model regressions in safety-critical fleets require qualified-engineer sign-off. Automated gates, canary thresholds, and rollback triggers in this strategy are decision-support, not authority. A passing gate matrix does not authorize a safety-relevant release; a named engineer with accountability does.
- The skill does not encode jurisdiction-specific update-notification or consent law (medical-device update regulation, automotive type approval, telecom certification). Teams must layer those obligations on top.
- The skill does not address training-side model selection or data curation; it ships the artifact the training side produces.
- Costs and bandwidth ceilings vary by CDN, region, and time; the skill flags the rate-shaping pattern but does not pin numeric ceilings that age well.

## Sources reviewed

- https://github.com/feaser/openblt (MIT)
- https://github.com/konrad1s/Bootloader (MIT)
- https://github.com/firmwaremodules/stm32-secure-patching-bootloader (license: source-available — read and cited for methodology only; no code reuse)
- https://github.com/advancedtelematic/ota-community-edition (MPL-2.0 — read and cited for methodology only; no code reuse)
- https://github.com/kubeflow/example-seldon (Apache-2.0)
- https://github.com/AlexIoannides/kubernetes-mlops (MIT)
- https://github.com/mendersoftware/mender (Apache-2.0)
- https://github.com/SeldonIO/seldon-core (Apache-2.0)
- https://github.com/kserve/kserve (Apache-2.0)
