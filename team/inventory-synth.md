# Inventory — `apps/api/scripts/seed_data/synth/`

**Owner:** Curation (Wave 1)
**Date:** 2026-05-26
**Source of truth:** filesystem state at this commit.

## Counts

| Bucket | Count |
|---|---:|
| `*.skills.md` (skill files) | **450** |
| `_report_*.md` (per-wave synthesis reports) | **79** |
| Other files (`README.md`) | **1** |
| **Total entries in `synth/`** | **530** |

### Reconciling 456 / 452 / 450

The number that floats around the docs has three different values; they all describe the **same library** measured under different conventions. None of the deltas is a data bug.

| Reported | Where | What it actually counts |
|---|---|---|
| **456** | `team/README.md`, `context/README.md` total, `prompts/` | 450 in `synth/` **plus** 6 demo-creator seed files that live one folder up at `apps/api/scripts/seed_data/*.skills.md` (the `janedoe-*`, `marcoart-*`, `samdata-*` files that exercise the third-party publisher path). |
| **452** | `team/dev-diary-backend-wave1.md` (Backend's smoke-test run) | An off-by-two against the live count. Most likely cause: the parametrized fixture path globbed something it shouldn't have at the time the test was authored (a transient artifact under `synth/`, or the 7 fixture skill files committed by Wave-1 Backend at `apps/api/tests/fixtures/skills/*.skills.md` got picked up by a too-broad glob). The Backend diary flags the count as drifted and defers reconciliation. **No skill files were deleted between Backend's run and now** — `git log --diff-filter=D` shows zero deletions under `synth/`. The 452 ↔ 450 gap is a counting artifact, not a curation artifact. |
| **450** | This inventory (current filesystem) | Strict count of `synth/*.skills.md` only. |

Wave totals from commit messages confirm 450 in `synth/`:

```
W1   30  (5403db4)
W2   89  (cea12b7)
W3   90  (b4487aa)
W4   37  (3920cec)
W5   36  (cd9b6f8)
W5c+W6+W7  168  (2d07e1b)
----
sum  450 ✓
```

**Recommendation for downstream docs:** quote **456** when describing the published library (synth + 6 seed); quote **450** when describing the curation pipeline's working set. The 452 figure in Backend's diary should be edited to 450 in Wave-2's diary follow-up (or just superseded — Backend already flagged it as "the live count has drifted by 4").

## Files by category

The `synth/` filenames mostly start with a domain-ish kebab prefix (e.g. `devops-`, `eng-`, `data-`), but the convention isn't strict — many domain-specific skills got bare names (`kafka-topic-architect`, `slo-designer`) because Wave-2 onward dropped the prefix when a niche tag in frontmatter made it redundant. The grouping below collapses the 124 raw prefixes into coarse domains by reading the `category:` and first `niche:*` tag of each file's frontmatter, then bucketing.

| Domain bucket | Count | Sample files (3) |
|---|---:|---|
| imported (W6 — third-party permissively-licensed skills) | 123 | `imported-alirezarezvani-chaos-engineering`, `imported-google-skills-waf-reliability`, `imported-voltagent-cloudflare-platform` |
| engineering — generic (`eng-*`, code review, system design) | 24 | `eng-adr-drafter`, `eng-api-design-reviewer`, `eng-code-review-auditor` |
| marketing (`mkt-*`) | 19 | `mkt-blog-post-architect`, `mkt-ab-test-designer`, `mkt-content-gap-hunter` |
| legal (`legal-*`) | 17 | `legal-nda-triage-classifier`, `legal-msa-redline-helper`, `legal-privacy-impact-assessment` |
| data engineering / analytics (`data-*`, `dag-*`, `pipeline-*`, `duckdb-*`, `iceberg-*`, `lakehouse-*`, `trino-*`, `bi-*`) | ~25 | `data-dbt-model-reviewer`, `data-star-schema-designer`, `iceberg-table-architect` |
| finance (`finance-*`) | 13 | `finance-annual-operating-plan-author`, `finance-monthly-variance-narrative`, `finance-saas-metrics-builder` |
| operations (`ops-*`) | 12 | `ops-incident-commander`, `ops-runbook-generator`, `ops-postmortem-writer` |
| product management (`prod-*`) | 8 | `prod-prd-drafter`, `prod-okr-set-reviewer`, `prod-meeting-summarizer` |
| robotics (`robot-*`, `ros1-*`, `ros2-*`, `slam-*`, `vio-*`, `lidar-*`, `motion-*`, `trajectory-*`, `collision-*`, `safety-*`, `real-time-*`) | ~22 | `slam-stack-architect`, `ros2-navigation-stack-tuner`, `robot-hazard-analysis-conductor` |
| biotech / healthcare / clinical (`biotech-*`, `clinical-*`, `med-*`, `bioinfo-*`, `rnaseq-*`, `multi-omic-*`, `eln-*`, `case-*`, `signal-*`, `submission-*`, `periodic-*`, `predicate-*`, `risk-*`, `pharmacovigilance`, `experiment-*`, `batch-*`, `reproducibility-*`, `lab-*`) | ~25 | `biotech-clinical-protocol-author`, `med-evidence-extraction-coordinator`, `rnaseq-analysis-planner` |
| creative production (W7: 3d/photo/video/vfx/color/brand/captions/inpainting/lora/controlnet/motion/sound/streaming/multicam/cut/rotoscoping/lighting/lut/hdr/pbr/logo/node-based) | ~36 | `3d-asset-pipeline-architect`, `video-encoding-ladder-designer`, `brand-asset-pipeline` |
| ml / ai engineering (`ml-*`, `llm-*`, `model-*`, `embedding-*`, `feature-*`, `synthetic-*`, `active-*`, `cv-*`, `vector-*`, `multimodal-*`, `rag-*`, `graphrag-*`, `semantic-*`, `entity-*`, `annotation-*`, `prompt-*`, `realtime-*`, `on-*`, `edge-*`, `detector-*`) | ~24 | `llm-eval-harness-designer`, `model-serving-reviewer`, `rag-product-loop-designer` |
| design / UX / frontend / mobile (`design-*`, `ux-*`, `frontend-*`, `mobile-*`, `cross-platform-*`, `documentation-*`, `docs-*`) | ~17 | `design-accessibility-reviewer`, `ux-interview-guide-designer`, `frontend-architecture-reviewer` |
| qa / testing (`qa-*`) | 5 | `qa-test-strategy-planner`, `qa-flaky-test-investigator`, `qa-property-based-test-designer` |
| support (`support-*`) | 3 | `support-ticket-triager`, `support-kb-article-synthesizer`, `support-reply-drafter` |
| sales (`sales-*`) | 3 | `sales-battlecard-builder`, `sales-cold-email-crafter`, `sales-discovery-call-conductor` |
| HR / hiring (`hr-*`) | 5 | `hr-job-description-author`, `hr-interview-loop-designer`, `hr-candidate-debrief-facilitator` |
| devops / sre / platform / observability / cloud-finops / supply-chain / identity (`devops-*`, `observability-*`, `slo-*`, `alert-*`, `cardinality-*`, `distributed-tracing-*`, `log-*`, `metric-*`, `instrumentation-*`, `cloud-cost-*`, `kubernetes-*`, `artifact-*`, `slsa-*`, `sbom-*`, `dependency-*`, `developer-*`, `internal-*`, `template-*`, `service-catalog-*`, `handbook-*`, `pre-deployment-*`) | ~28 | `devops-ci-pipeline-architect`, `slo-designer`, `internal-platform-strategy-author` |
| enterprise / SAP / Salesforce / ABAP | ~7 | `s4hana-migration-strategy-author`, `salesforce-apex-reviewer`, `abap-review-helper` |
| spark / data-processing | 6 | `spark-cluster-sizer`, `spark-job-tuner`, `spark-on-kubernetes-architect` |
| kafka | 4 | `kafka-topic-architect`, `kafka-consumer-pattern-picker`, `kafka-streams-pipeline-designer` |
| firmware / embedded | 4 | `firmware-architecture-reviewer`, `firmware-update-and-rollback-architect`, `embedded-ci-and-hardware-in-the-loop` |
| live streaming / commitment / remote / meeting / orchestrator / case / commitment / live / etc. (long tail singletons) | ~50 | `live-streaming-stack-architect`, `commitment-strategy-planner`, `meeting-and-decision-recording-discipline` |

Counts are approximate where the bucket aggregates many prefixes — the source of truth is the raw 124-prefix breakdown which the inventory script produced and which can be re-derived with:

```powershell
Get-ChildItem D:\skillsgit\apps\api\scripts\seed_data\synth\ -Filter *.skills.md `
  | ForEach-Object { ($_.BaseName -replace '\.skills$','').Split('-')[0] } `
  | Group-Object | Sort-Object Name
```

For Wave-3 (T-08), only the **devops / sre / platform / observability / cloud-finops / supply-chain / identity** bucket plus selected `eng-*`, `kafka-*`, `spark-*`, `imported-*` files are relevant. See `team/devops-occupation-slugs.md` for the verified DevOps-occupation member set.

## What's NOT in `synth/`

Reminder for any downstream agent that does its own counting:

- The **6 demo-creator seed files** live at `apps/api/scripts/seed_data/*.skills.md` (one level up), not in `synth/`. They are NOT part of the curated `@skillsgit-curated` library. They simulate three independent creators (`janedoe`, `marcoart`, `samdata`) for exercising the third-party publish path.
- Validator **test fixtures** live at `apps/api/tests/fixtures/skills/*.skills.md` (7 files added by Backend Wave 1 — `occupation_valid`, `persona_valid`, `memory_neuron_valid`, plus 4 negative cases). They are never published.

The "450 curated + 6 seed = 456 published" identity holds; any tool that wants to count "everything we ship" should glob both directories.
