---
id: skillsgit-curated/cv-dataset-curation-architect
version: 1.0.0
name: CV Dataset Curation Architect
description: Architect a computer-vision dataset for a target task — taxonomy, sourcing, ODD coverage, edge-case mining, split discipline, anti-leakage, versioning, and lineage.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: robotics
tags: [niche:cv-dataset-curation, dataset-design, taxonomy, sourcing, split-discipline, anti-leakage, lineage, versioning]
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
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - cv dataset design
  - dataset curation
  - class taxonomy
  - dataset sourcing
  - edge case mining
  - train val test split
  - data leakage prevention
  - dataset versioning
  - dataset lineage
  - odd coverage dataset
  - vision dataset plan
  - dataset card
example_invocations:
  - "Plan the dataset for a warehouse robot's pallet detector — taxonomy, sourcing, splits, anti-leakage."
  - "Design the curation strategy for a drone-based crop disease classifier across three regions and four seasons."
  - "Our detector is plateauing because the dataset is a mess — give me a curation re-architecture plan."
inputs:
  - name: task_description
    type: text
    required: true
    description: Brief of the target task — object detection, segmentation, classification, keypoint, tracking, or multi-task setup, plus the platform that will consume the model.
  - name: operational_design_domain
    type: text
    required: false
    description: Environments the model must work in — lighting, weather, geography, viewpoint, sensor configuration, dynamic-actor density.
  - name: existing_assets
    type: text
    required: false
    description: Data already on hand — recorded logs, prior labelled corpora, public datasets in use, simulators or generators available.
  - name: known_constraints
    type: text
    required: false
    description: Cost ceilings, privacy regimes, regulatory class constraints, vendor relationships, contracted labelling capacity.
  - name: target_performance
    type: text
    required: false
    description: Headline performance the model must reach and the operating points the downstream consumer cares about.
outputs:
  - name: curation_plan
    type: markdown
    description: Structured plan covering taxonomy, sourcing strategy, ODD coverage matrix, edge-case mining, split discipline, anti-leakage protocol, versioning and lineage.
  - name: plan_json
    type: json
    description: Structured plan with `taxonomy`, `sources`, `odd_matrix`, `edge_cases`, `splits`, `leakage_controls`, `lineage`, `versioning`, `risk_register`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# CV Dataset Curation Architect

## When to use

Use this skill when a team needs a written plan for *building or rebuilding* the dataset that backs a computer-vision model. The plan covers the conceptual scaffolding (class taxonomy, the operational envelope the dataset must represent), the sourcing strategy (how raw imagery enters the pipeline), the curation strategy (how it is selected, deduplicated, and stratified), the discipline that keeps training and evaluation honest (anti-leakage, splits, versioning), and the lineage record that lets future contributors understand how the corpus came to be.

The skill is appropriate for any CV task: 2D object detection, segmentation (semantic, instance, panoptic), classification, keypoint estimation, tracking, 3D detection from camera or LiDAR, and the multi-task heads that mix them. It is upstream of labelling-program design, active-learning loop design, and synthetic-data strategy — those skills consume the artefact this skill produces. It is also upstream of test-suite design: a sound dataset is the precondition for a sound evaluation regime.

**Mandatory safety disclaimer.** This skill produces methodology guidance. Perception failures in safety-critical robots can cause physical harm. Every recommendation must be validated in target operational design domains; never deploy a perception stack to safety-critical hardware without rigorous test coverage of edge conditions (weather, lighting, occlusion, sensor degradation).

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `task_description` | yes | Anchors taxonomy, output type, and the curation discipline that fits. |
| `operational_design_domain` | no | Drives the ODD coverage matrix and rare-condition mining. |
| `existing_assets` | no | Avoids re-curating, lets the plan re-use what is salvageable, and identifies what must be retired. |
| `known_constraints` | no | Caps the plan to realistic costs, privacy regimes, and capacity ceilings. |
| `target_performance` | no | Drives sample-size estimates and the priority order of curation work. |

## How to apply

The skill walks a fourteen-stage pipeline. Early stages build the conceptual scaffolding (intent, taxonomy, ODD). Middle stages produce the sourcing plan, the curation rules, and the split discipline. Late stages cover lineage, versioning, the risk register, and the deliverable.

### Stage 1 — Restate the dataset's purpose

1. From `task_description` derive the exact output the model produces and the consumer that consumes it. A pallet detector inside a warehouse robot's stack is a different artefact from a pallet detector inside a logistics analytics dashboard, even if the bounding-box format is identical. Write the consumer-facing contract before anything else.
2. Enumerate the *primary outputs* the dataset must support: detection boxes, segmentation masks, keypoints, classifications, attribute predictions, 3D extents, instance IDs across frames. Each output is a separate labelling product with its own quality envelope.
3. Name the *operating points* the consumer cares about. A safety-critical pedestrian detector cares about recall at very high precision. A search index cares about precision at top-K. The dataset's per-class composition and the eval-set's per-condition stratification flow from these operating points.
4. Identify the *blast radius* of each failure mode the model can produce. False positives that wake a sleeping operator are different from false negatives on a pedestrian crossing. Curation effort scales with blast radius, not with frequency.

### Stage 2 — Class taxonomy

5. Draft the taxonomy as a tree, not a flat list. A two-level taxonomy with super-classes (vehicle, person, infrastructure) and leaf classes (car, truck, bicycle, pedestrian, child, worker-in-vest, bollard, cone, etc.) lets the labelling team see the conceptual shape and lets the model fall back gracefully when leaf uncertainty is high.
6. Define each class operationally. The definition must answer: what counts, what does not count, where do you draw the boundary, how do you handle the edges. "Pedestrian" needs to spell out the treatment of a person inside a vehicle, a person on a bicycle, a person on a wheelchair, a person carrying a child, a mannequin, a reflection. The class spec is the contract between curation and labelling.
7. Decide the *don't-care* and *ignore* policy explicitly. Classes that should not be detected (a person inside a building visible through a window) and classes that should be suppressed (motion blur of the ego-vehicle's own structure) need an explicit handling rule. Without this rule, the labelling team will invent one inconsistently.
8. Decide the *open-set* policy. If the model will operate in environments where unseen classes appear, the taxonomy needs an "other-known", "unknown-stuff", or "novel-actor" pseudo-class so the labelling and evaluation can recognise the gap without forcing it into a known class.
9. Decide the *granularity* per consumer. Some downstream consumers want only "vehicle". Others need "car" vs "truck" vs "bus". The taxonomy supports both by being hierarchical and by making the leaf-vs-super-class choice a config rather than a re-curate.
10. Plan *taxonomy evolution*. When a class splits (the consumer needs "delivery-rider-with-cargo" carved out of "cyclist") or merges, the plan describes the re-labelling, the partitioning of historical data by taxonomy version, and the compatibility table between versions.

### Stage 3 — Operational design domain coverage matrix

11. Take `operational_design_domain` and structure it as a matrix. Rows are environment dimensions (lighting, weather, surface, time-of-day, geography, season, viewpoint, sensor configuration, dynamic-actor density). Columns are taxonomy classes (or super-classes for sparse cells).
12. For each cell record: scenes available, image or frame count, last-collection date, freshness, demographic representativeness, and whether the cell is *required-for-deployment* or *required-for-evaluation-only*. Required-for-deployment cells must be covered before the model ships; eval-only cells govern how confidently you can claim coverage of an ODD condition you do not deploy into.
13. Define a *coverage floor* — every required cell has at least N distinct scenes and M labelled instances per class, where N and M scale with the blast radius from Stage 1.
14. Identify *rare-but-catastrophic* cells: glare at sunrise, retro-reflective vests at night, occluded child-sized actors, fog at dusk, ground glare on wet pavement. These cells get bespoke collection sprints.
15. Identify *boring-but-dominant* cells: ordinary daytime scenes with no edge cases. The plan deliberately under-collects from these once a baseline density is reached; otherwise the corpus drowns the rare cells and the model overfits to the average.

### Stage 4 — Sourcing strategy

16. Enumerate available sourcing channels: field collection (own platform recording), partner data, public datasets, crowd-sourced imagery, web scraping under explicit licence terms, synthetic generation, simulator output. For each, record provenance, licence, consent regime, refresh cadence, and unit cost.
17. Reject channels whose licence does not permit the intended use. Web-scraped imagery without a permissive licence is unsafe for commercial models. Public datasets with non-commercial-only clauses cannot back a product. Document each rejection in the lineage record so a later contributor does not re-introduce the same source.
18. Plan the *targeted-collection* programme for rare cells. The plan names the operator team, the route or scenario, the sensor configuration, the time-of-day window, the safety protocol, the weather trigger, and the volume target. Random collection rarely fills rare cells; targeted collection does.
19. Plan the *opportunistic-collection* programme for the dominant cells. Routine logging from the deployed fleet, with retention and sampling rules that keep storage costs bounded, produces the bulk of the corpus.
20. Plan the *public-dataset-blend* policy. Mature public datasets are useful for pretraining and as auxiliary training data; they are usually unsafe for final evaluation because their definitions drift from the consumer's contract. The plan tags every public corpus with "training-allowed / eval-allowed" status and documents why.
21. Plan the *partner-data* policy: data exchange agreements, the indemnification chain, the consent record, the right to retain after the partnership ends. Without explicit policy, partner data accretes and becomes legally inseparable from owned data.
22. Plan the *retirement* policy. Sources retire when their licence changes, when consent expires, when the platform moves to a sensor that makes the source non-representative, or when the source's labelling quality is no longer trusted. Retired data is removed from training, retained in lineage, and never re-introduced silently.

### Stage 5 — Pre-label curation rules

23. Define what enters the labelling queue and what does not. Raw collection produces vastly more frames than the labelling budget can absorb; curation is the gate.
24. Apply *near-duplicate removal*. Sequential frames from the same recording are heavily correlated; a perceptual-hash, embedding-similarity, or temporal-stride policy keeps one representative per cluster. Without this, the corpus is bloated and the model overfits to the dominant scenes.
25. Apply *quality filters*. Saturated frames, fully blurred frames, fully occluded frames, frames where the sensor is occluded by debris, frames that fail the integrity check (corrupted bytes, partial reads), and frames outside the platform's operational envelope (e.g. transit between sites for a stationary platform) are dropped before labelling. The drop record is logged.
26. Apply *content filters*. Frames that contain PII or third-party content that the licence regime forbids are either blurred at source or excluded. The filter is auditable.
27. Apply *coverage steering*. For each cell in the ODD matrix that is under-covered, prioritise frames from that cell. For each cell that is over-covered, sample down. The steering rule is explicit and reproducible so re-running it gives the same selection.
28. Apply *uncertainty steering* once a baseline model exists (this is the active-learning hand-off). Frames where the baseline is uncertain or where two baseline models disagree are prioritised. This is detailed in the active-learning-loop-designer skill; the curation plan reserves a budget slot for it.

### Stage 6 — Edge-case mining

29. Edge cases are the rare-but-load-bearing examples that prevent rare-class failures. The plan describes how they are mined, not only what they are.
30. Mining sources: incident reports, near-miss flags, customer complaints, low-confidence production predictions, high-uncertainty predictions, model disagreement between two model versions, model disagreement between modalities (camera vs LiDAR), high-loss frames during training (after one or two epochs), gradient-driven hard-example mining, manual scouting by operators in field.
31. For each mined case, attach a structured record: scene reference, condition tags, expected behaviour ("detect X with confidence ≥ 0.8", "remain silent on Y", "publish low confidence on Z"), failure history, and the curated source.
32. Curate edge cases with the same anti-leakage discipline as ordinary data. An edge case that appears in training and evaluation will lift the metric without lifting the model.
33. Plan a *promotion path*: when an edge case is consistently solved across K releases, promote it from the long-tail bucket into the ordinary cohorts; archive the long-tail entry. Otherwise the long-tail grows unboundedly and curation cannot maintain it.

### Stage 7 — Split discipline

34. Define training, validation, and test partitions with explicit purpose for each. Training is for fitting; validation is for hyperparameter and architecture choice; test is for release-gate evidence. The partitions never swap roles. Re-using the test set during development is the perception-equivalent of training on the test set.
35. Define a *frozen test set* that is touched only when releasing. Once the test set is fixed, looking at its predictions during model iteration disqualifies it. A separate iteration-validation set serves the development loop.
36. Choose the *split unit* per task. For independent images, the unit is the image. For temporally correlated frames, the unit is the recording (or the geo-spatial chunk, or the location-and-day combination). Splitting at the frame level when frames come from the same recording leaks information across partitions.
37. Choose the *stratification scheme*. The split is stratified by ODD cell, by class, and by geography so the partitions are representative. Without stratification, splits randomly under- or over-represent rare conditions and the metric is noisy.
38. Decide the *adversarial split* policy for stress tests. A held-out partition that captures conditions the training partition deliberately excludes (a new city, a new weather class, a new sensor variant) measures generalisation. Mature programmes maintain at least one adversarial split.
39. Pin the random seed and the split-construction algorithm. The plan documents the exact recipe so a new contributor reproduces the partition byte-for-byte.

### Stage 8 — Anti-leakage protocol

40. Enumerate the leakage vectors and the defence against each:
    - **Frame-from-same-recording leakage** — defended by recording-level splits.
    - **Same-actor-across-recordings leakage** — defended by actor identifiers when feasible (faces, vehicle plates, distinctive operator gear); when actor IDs are not feasible, by geographic or temporal separation.
    - **Site leakage** — defended by site-level splits when the platform deploys across distinct sites.
    - **Sensor-and-rig leakage** — defended by recording the platform configuration and treating it as a stratification key; a model that has never seen a specific sensor variant in training will not be evaluated against it without the limitation called out.
    - **Operator leakage** — when operators or annotators correlate with sites or conditions, their identifiers feed the split discipline so a model is not silently evaluated on a held-out operator's biases.
    - **Synthetic-bleed leakage** — defended by tagging every synthetic record and excluding synthetics from evaluation partitions unless explicitly paired with real cohorts under the paired-validation rule (covered by the synthetic-data-augmentation-strategist skill).
    - **Public-dataset cross-contamination** — defended by hashing public images and ensuring no near-duplicate appears in evaluation partitions when public data is also used in training.
41. Run a *leakage audit* before declaring the splits final. Embedding-similarity searches across partition boundaries flag near-duplicates; clusters that span partitions are reassigned or dropped. The audit is repeatable and is part of the lineage record.
42. Treat leakage as a release-gating defect. The plan names a *leakage owner* who signs off on each release that the audit passes.

### Stage 9 — Sample-size and budget

43. Estimate per-class instance counts that hit the target performance, using the consumer's operating point. A high-recall pedestrian operating point requires more positive instances and more rare-condition examples than a moderate-recall search index.
44. Estimate budget per class: number of frames, number of annotated instances, hours of annotator time, review time, gold-standard time. The annotation cost is the single largest line item in most CV programmes.
45. Plan *over-collection*: collect ten to twenty times more frames than will be labelled, because curation will reject most. The exact ratio depends on the source-quality and the rare-cell density.
46. Plan *budget allocation across cohorts*: training, validation, test, long-tail. Long-tail is more expensive per example because it is hand-mined; the plan budgets accordingly.
47. Plan *re-labelling reserve*. A fixed percentage of the budget (a typical default is ten to fifteen percent) is reserved for re-labelling: taxonomy revisions, error correction, label-quality re-audits, and senior-reviewer adjudication of disputed cases.

### Stage 10 — Versioning and lineage

48. Every dataset has a *version* and every model trained on a dataset records that version. Without versioning, "the dataset" becomes mythical and any reported metric is provisional.
49. Version both the *content* (which images are in the dataset) and the *spec* (what the labels mean). A spec change without a content change still bumps the version because the labels mean something different.
50. Maintain a *lineage record* per image: where it came from, when it was collected, who has it, what licence governs it, what consent regime applies, when the consent expires, what filters it has passed, when it was last re-labelled, who labelled it, who reviewed it. Lineage is the audit trail when something goes wrong.
51. Maintain a *dataset card* — the human-readable summary that documents intent, composition, known limitations, known biases, recommended uses, and excluded uses. The card is published with every release and updated when material changes occur.
52. Maintain a *change log* per dataset version. Every entry names what was added, what was removed, what was re-labelled, what filters changed, and why. The change log is the diff between versions and is the only mechanism by which trends across versions can be interpreted.
53. Maintain a *retirement record* for removed data. Removed data is not deleted from lineage; the record names what was removed, why, when, and which model versions used it. Removed data is excluded from future training and from future evaluation.

### Stage 11 — Demographic and bias hygiene

54. For datasets that contain people, plan demographic representation explicitly: ages, body sizes, skin tones, mobility-aid users, occupational and protective clothing variants, weather-appropriate clothing, cultural-context variations. The plan names what is collected, what is under-represented, and the targeted-collection sprint to close the gap.
55. For datasets that contain places, plan geographic representation: urban / suburban / rural, regional variations, infrastructure styles, signage conventions. A dataset collected in one region underperforms in another precisely along these axes.
56. Audit the model's per-group performance during evaluation, not only the aggregate. The dataset plan creates the slicing that the evaluation will use.
57. Document the bias hygiene plan in the dataset card with named limitations. Under-representation that the plan has not yet remedied is disclosed; the model card downstream inherits the disclosure.

### Stage 12 — Privacy, licensing, retention

58. For each source channel and each class of subject, name the privacy regime: applicable data protection regulations, consent basis, blurring or redaction required, retention horizon, deletion-on-request procedure.
59. For each source channel, name the licence and the licence's restrictions. Mark each as "training-allowed", "evaluation-allowed", "commercial-allowed", and "redistribute-allowed". Sources that fail any required permission are not used for that purpose.
60. Plan *PII redaction*: face blurring, plate redaction, voice removal, geolocation truncation, metadata stripping. The plan names the redaction tool and the audit step that verifies redaction.
61. Plan *retention*: how long raw recordings are kept, how long labelled data is kept, the deletion procedure when consent expires, the verification that deletion happened. Retention is part of the dataset card.
62. Plan *deletion propagation*. When an item is deleted from the dataset, downstream models trained on it are noted; whether they need retraining is decided per the platform's retention contract.

### Stage 13 — Risk register

63. Enumerate dataset risks with owner, detector, mitigation:
    - A class definition that drifted during labelling and produced an inconsistent training signal.
    - A near-duplicate cluster that leaked across partitions and inflated the test metric.
    - A source whose licence changed and which is no longer safe to use.
    - A geographic over-fit because collection drifted to a single region.
    - A demographic under-representation that emerges only when a deployment region changes.
    - A spec change without a version bump that silently invalidated historical metrics.
    - A retired source whose data is still in a forgotten cached partition.
    - A consent expiry that the retention policy missed.
    - A model trained on a privacy-redacted version but evaluated on a pre-redaction version.
64. For each risk, the plan names the detector (the audit, the dashboard, the periodic review), the mitigation, and the escalation path when the risk fires.

### Stage 14 — Compose the deliverable

65. Open with a one-paragraph *dataset intent* statement: what the corpus supports, what consumer relies on it, what it is not.
66. Render the plan as a markdown document covering taxonomy, ODD matrix, sourcing, curation rules, edge-case strategy, split discipline, anti-leakage protocol, budget, versioning, lineage, demographic hygiene, privacy and licensing, and the risk register.
67. Emit `plan_json` with structured fields: `taxonomy` (tree), `sources[*]` (channel, licence, status), `odd_matrix` (cells with status), `edge_cases[*]`, `splits` (units, stratification, partitions), `leakage_controls[*]` (vector, defence, owner), `budget` (per cohort), `lineage` (per-record fields enumerated), `versioning` (current version, change-log structure), `risk_register[*]`.
68. Close with the mandatory safety disclaimer and a "what this plan does not cover" note that points the user at the annotation-quality-program-designer, the active-learning-loop-designer, and the synthetic-data-augmentation-strategist for the downstream pieces.

## Outputs

The skill returns:

1. `curation_plan` (markdown) — full curation-architecture document.
2. `plan_json` (JSON) — structured plan suitable for tracking in dataset tooling and for hand-off to labelling, active-learning, and synthetic-data planning.

## Examples

**Input (placeholder):**

`task_description`: "Warehouse autonomous mobile robot needs a 2D detector for pallets, racks, pedestrians-in-vests, forklifts, and ground obstacles, from a forward-facing wide-angle camera; output is fed to the planner and an obstacle-stop safety layer."

`operational_design_domain`: "Indoor warehouse aisles, mixed fluorescent and LED lighting, dusty conditions, polished concrete floors with glare, pedestrian density low-to-medium, occasional forklift traffic, four customer sites with different rack styles."

`existing_assets`: "8k labelled frames from one site, 200 hours of unlabelled fleet recordings from three sites, a procedurally-generated warehouse simulator, no public dataset in the same domain."

`known_constraints`: "Privacy: faces of pedestrians must be blurred. Budget: 30k labelled frames over six months. Vendor relationship with one labelling partner."

`target_performance`: "Pallet recall 0.99 at precision 0.95, pedestrian recall 0.995 at precision 0.99, forklift recall 0.98 at precision 0.97."

**Plan (abbreviated):**

- Taxonomy: super-classes {actor, equipment, infrastructure, ground-hazard}; leaves {pallet, rack, pedestrian-vest, forklift, debris, spill, cable}; explicit ignore policy for the robot's own visible structure; pedestrian definition includes mobility-aid users and seated operators on stools.
- ODD matrix: aisles × {lighting, dust level, glare} × {pedestrian density} × site (1..4); site 4 under-covered → targeted collection sprint; glare-on-polished-floor flagged rare-but-catastrophic.
- Sourcing: own fleet recordings (primary), simulator (training only, never in test, paired-validation required for trust); no public dataset blend.
- Pre-label curation: perceptual-hash near-duplicate removal with 1-frame-per-5-seconds stride; saturation and integrity filters; face-blur applied at ingest.
- Edge-case mining: spill, fallen cable, pallet partially in shadow, retro-reflective vest under direct ceiling LED, child-sized prop (mannequin) for vendor pedestrian-test scenarios.
- Splits: recording-level partition by `(site, day)`; stratified by `(class, lighting, density)`; frozen test set drawn from a held-out month and one held-out site (site 4 partly reserved as adversarial); training:val:test = 80:10:10 on coverage budgets, with a separate held-out adversarial split.
- Anti-leakage: hash-based public-dataset audit (no public data used); recording-level discipline; embedding-near-duplicate audit between training and evaluation partitions; leakage owner named, audit blocks release.
- Budget: 30k frames split 22.5k train, 3k val, 3k test, 1.5k long-tail, 10–15% reserve for re-labelling.
- Versioning: v1.0.0 for first cut; spec-change taxonomy bump (1.0.0 → 2.0.0) when the open-set pseudo-class is introduced; lineage record per image with site, recording id, collection date, licence, consent status, redaction status.
- Demographic hygiene: pedestrian skin-tone and clothing-variation balance audited; mobility-aid sub-class explicitly seeded; under-representation declared in the dataset card.
- Privacy: face blur enforced at ingest; verification audit at 5% sample; no plate or voice capture in scope; retention horizon 24 months past the last model trained on the corpus.
- Risk register: site-4 over-fit (detector: per-site eval, mitigation: targeted collection); simulator-bleed (detector: paired-validation, mitigation: exclude synthetics from test partition); consent drift (detector: quarterly audit, mitigation: deletion propagation).

**Output excerpt:** the markdown plan plus a JSON object whose `taxonomy` is a nested tree, whose `odd_matrix` enumerates each cell with coverage status, whose `splits` describes the unit, stratification, and seed, whose `leakage_controls` enumerates vectors and defences with owners, and whose `risk_register` names each risk with detector and mitigation.

## Limitations

- The skill plans the dataset; it does not collect data, label data, or run training. It is the contract between data-engineering and modelling.
- Coverage-matrix completeness depends on the user's stated ODD. Gaps that the user has not surfaced will be missing from the matrix until field experience exposes them.
- Privacy and licensing guidance is generic. Regulated domains (medical imaging, biometric, public-safety, automotive type-approval, juvenile-protected content) require domain-specific legal review beyond the scope of this plan.
- Sample-size estimates are heuristic. Final budget should be confirmed with pilot training runs that produce learning-curve evidence.
- The skill assumes a labelling partner or in-house labelling team will execute the labelling. The labelling-quality programme is the responsibility of the annotation-quality-program-designer skill.
- The skill defers active-learning loop design and synthetic-data strategy to companion skills; the curation plan reserves the integration points and identifies the hand-offs.
- For very small teams without dedicated data-engineering capacity, full execution exceeds available engineering capacity; the plan flags which stages are highest-value and can be staged.

## Sources reviewed

- https://github.com/HumanSignal/label-studio (Apache-2.0)
- https://github.com/voxel51/fiftyone (Apache-2.0)
- https://github.com/cvat-ai/cvat (MIT)
- https://github.com/roboflow/supervision (MIT)
- https://github.com/cleanlab/cleanlab (Apache-2.0)
- https://github.com/voxel51/fiftyone-brain (Apache-2.0)
- https://github.com/snorkel-team/snorkel (Apache-2.0)
- https://github.com/SkalskiP/make-sense (GPL-3.0; methodology study only; no code or trademarked names used)
