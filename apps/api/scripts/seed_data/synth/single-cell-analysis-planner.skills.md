---
id: skillsgit-curated/single-cell-analysis-planner
version: 1.0.0
name: Single-Cell RNA-seq Analysis Planner
description: Plans an end-to-end scRNA-seq analysis — QC, doublet removal, normalization, integration across samples, clustering, cell-type annotation, and differential expression — so the result reproduces and the biology survives review.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: biotech
tags: [niche:bioinformatics-pipelines, single-cell, scrna-seq, scanpy, seurat, integration, clustering, cell-type-annotation]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: [file_io, code_execution]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - scrna-seq
  - single cell rna-seq
  - scanpy
  - seurat
  - doublet removal
  - cell type annotation
  - batch integration
  - leiden clustering
  - cellranger
  - anndata
  - integration scvi
  - single-cell de
example_invocations:
  - "Plan the analysis for 10x scRNA-seq data — 12 samples across two conditions."
  - "We have integration artifacts mixing cell types — how do we fix this?"
  - "Pick a doublet-removal and QC strategy for our Chromium runs."
  - "Plan cell-type annotation and pseudobulk DE for our atlas project."
inputs:
  - name: study_description
    type: text
    required: true
    description: The biology and design — species, tissue, conditions compared, samples per condition, chemistry (10x v3/v4, Drop-seq, Smart-seq), and approximate cell counts per sample.
  - name: existing_artifacts
    type: text
    required: false
    description: What is already done — counts matrices already produced by CellRanger/STARsolo/Alevin-fry, prior atlas references for annotation, existing pipelines.
  - name: known_confounders
    type: text
    required: false
    description: Batch and donor structure, library prep dates, instrument, ambient-RNA concerns, freezing artifacts, lab-specific dissociation effects.
  - name: question_focus
    type: choice
    required: false
    description: What the analysis is trying to learn. Drives where to spend time.
    choices: [discover-cell-types, condition-comparison-within-type, trajectory, atlas-integration, reference-mapping]
  - name: downstream_use
    type: text
    required: false
    description: How findings will be used — discovery, follow-up validation, atlas integration, clinical research.
outputs:
  - name: analysis_plan
    type: markdown
    description: The full plan — preprocessing, QC, doublet removal, normalization, feature selection, dimensionality reduction, integration, clustering, annotation, and DE.
  - name: qc_thresholds
    type: markdown
    description: Concrete QC thresholds tailored to tissue and chemistry, with the rationale for each.
  - name: integration_strategy
    type: markdown
    description: How to handle batch and donor structure — integration method, when to run it, and how to validate the result is biology not artifact.
  - name: annotation_and_de_plan
    type: markdown
    description: How to assign cell types and how to compare conditions within type without inflating false positives.
  - name: pre_registration_checklist
    type: markdown
    description: Decisions to lock before unblinding to specific cluster-level results.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

This skill produces methodology guidance for bioinformatics workflows. Outputs are not validated clinical or research conclusions and must be reviewed by qualified scientific staff before being acted upon. Pipelines built from this guidance must be wet-lab-validated and version-locked before any decisions are made on the results.

Use this skill when planning the analysis of a single-cell RNA-seq study. Specifically:

- A new scRNA-seq project is moving from raw counts to a first analysis.
- An existing analysis is showing integration artifacts, suspicious clusters, or unstable cell-type calls and needs a methodology pass.
- An atlas or reference-mapping project needs a defensible plan that scales beyond a single sample.
- A team is doing condition comparisons within cell type and wants the differential expression done correctly.
- A reviewer or collaborator is going to ask "why these thresholds and parameters" and the team wants ready answers.

Do not use this skill for spatial transcriptomics, multi-omic (CITE-seq, ATAC) integration beyond a high level, or perturbation screens (Perturb-seq) — those need specialized approaches. Pair with the bulk RNA-seq planner if pseudobulk analysis is the right answer; pair with the pipeline architect for production-grade pipeline structure.

## How to apply

The order is non-negotiable: QC and doublet handling before normalization, normalization before integration, integration before clustering, clustering before annotation, annotation before condition comparison. Doing them out of order produces results that look reasonable but are not.

### 1. Frame the question and pick the unit of analysis

Single-cell experiments answer at least three classes of questions, and they want different analyses:

- **What cell types are present?** This is an atlas question. The work goes into integration, clustering, and annotation. Differential expression is mostly between cell types.
- **How does a known cell type change between conditions?** Within-type DE between conditions, ideally on pseudobulk aggregations of cells per sample to respect sample-level replication.
- **How does the composition of cell types change between conditions?** Compositional analysis of cell-type proportions, with appropriate tests that handle the compositional nature of the data.

The plan looks different for each. Name the primary question first; lock secondary questions as exploratory.

### 2. Confirm upstream quantification is sound

Single-cell starts from a counts matrix. Before any analysis, verify:

- The quantifier (CellRanger, STARsolo, Alevin-fry, Kallisto-BUStools) is appropriate to the chemistry and was run with the right reference and annotation.
- Empty-droplet calling has been done (CellRanger's default, EmptyDrops in DropletUtils, or the quantifier's equivalent). Including empty droplets in downstream analysis is a common, fatal error.
- Ambient-RNA correction (SoupX, DecontX, CellBender) has been considered. For tissues with high ambient RNA — solid tumors, brain — it materially changes downstream results.
- The annotation version is recorded. Gene-symbol drift across releases is a recurring source of mismatched results.

If any of these are unclear, fix them before continuing. They are not analysis steps to revisit; they are inputs to the analysis.

### 3. Run per-sample QC before integration

The QC step is per cell, applied per sample (or per batch). Standard metrics:

- Total counts per cell (UMI count).
- Number of genes detected per cell.
- Percentage of reads from mitochondrial genes (a marker of cell stress or damage in most tissues).
- For tissues with relevant biology, percentage of ribosomal or hemoglobin genes.

Pick thresholds per tissue, not universally. A liver hepatocyte naturally has high mitochondrial content; a peripheral blood mononuclear cell does not. Conventional starting points:

- Minimum genes per cell: a value derived from the per-sample distribution, often the 1st-percentile cell or a fixed floor (500–800 for 10x v3 chemistry on solid tissue).
- Maximum genes per cell: an upper percentile (98th or 99th) flags likely doublets.
- Maximum mitochondrial percentage: tissue-dependent. PBMC commonly under 10%; many solid tissues tolerate 15–25%; tumors often require careful, tissue-specific thresholds.

Plot the distributions per sample. Apply thresholds informed by the distributions, document them per sample if they vary, and report cells removed at each step. The QC report is part of the deliverable, not a footnote.

### 4. Remove doublets explicitly

Doublet rates rise with cell loading and matter a lot for clustering — doublets form their own clusters and are mistaken for hybrid cell types. Use a doublet detector per sample (Scrublet, DoubletFinder, scDblFinder, scvi-tools' SOLO). These work by simulating doublets and scoring real cells against them.

Run doublet detection per sample, before integration, on the per-sample counts. Conventional approach: simulate at the expected rate (manufacturer's loading guidance plus a margin), score cells, and remove the top-scoring cells consistent with the simulated doublet rate.

Doublet calls are not perfect; flag them and review whether suspected doublet clusters disappear after removal. If a cluster looks biologically interesting and is flagged as doublets, dig in — it may be either real biology or a doublet artifact, and you need to know which.

### 5. Normalize, then choose features

Library-size normalization followed by log transformation (`log1p` of counts-per-10,000 or similar) is the dominant approach and works for most analyses. Variance-stabilizing alternatives (Pearson residuals via `scanpy.pp.normalize_pearson_residuals`, sctransform in Seurat) are competitive for feature selection and downstream embedding but add complexity; pick one and document.

Pick highly variable genes (HVGs) for downstream dimensionality reduction. Common range: 2,000–5,000 HVGs. Compute HVGs after normalization, and — for multi-sample studies — compute them in a way that respects batch (e.g., per-batch HVGs intersected or pooled via batch-aware methods). Computing HVGs on the pooled, un-corrected matrix lets batch effects drive feature selection.

### 6. Choose dimensionality reduction and integration deliberately

PCA on HVGs gives the initial embedding. The number of principal components matters less than commonly thought; the field has converged on 30–50 for typical experiments, with elbow-plot inspection as a sanity check.

For multi-sample studies, integration is needed to align cells of the same type across samples and conditions. Common methods:

- Harmony — fast, embedding-level, batch correction without modifying counts. A good default for moderately sized studies.
- BBKNN — modifies the neighborhood graph to be batch-aware; pairs well with the standard scanpy workflow.
- scVI / scANVI — variational autoencoder integration that handles batch and supports query-to-reference mapping; strong for large or atlas-scale studies.
- Seurat anchors (`IntegrateData`, `IntegrateLayers`) — Seurat's native approach, robust and well-documented.
- scaling-only with no integration — appropriate when batch is negligible (single donor, single batch).

The wrong move is over-integration. Aggressive batch correction can flatten genuine biological differences between conditions into noise. Validate integration with diagnostics:

- A UMAP colored by batch versus colored by inferred cell type. Batch should be mixed within type; types should be distinguishable.
- Per-cluster batch composition. Clusters dominated by a single batch deserve scrutiny.
- For condition comparisons, never integrate so aggressively that cells from different conditions are forced together. Some biological-driven separation is the point.

Decide integration strength before clustering, not after.

### 7. Build the neighborhood graph and cluster

The standard pattern is k-nearest-neighbor graph on the (integrated) embedding, followed by Leiden clustering. Practical defaults:

- k = 15 for small studies, up to 30–50 for large ones.
- Leiden resolution between 0.4 and 1.5, with the right value chosen by stability and by interpretability of resulting clusters.

Cluster stability checks: rerun clustering at adjacent resolutions and observe how cluster boundaries move. Stable clusters reappear; unstable ones split and merge wildly. Use a tool like `clustree` to visualize.

Compute UMAP on the same neighborhood graph for visualization. Do not interpret UMAP distances quantitatively; positions are decorative.

### 8. Annotate cell types

Annotation is the bridge from clusters to biology. Three approaches, often combined:

- **Marker-based.** Compute differential expression per cluster against the rest, intersect top markers with curated cell-type marker lists (CellMarker, PanglaoDB, tissue-specific references), and assign labels. Confirm with canonical-marker dot plots.
- **Reference-mapping.** Use an annotated reference (Tabula Sapiens, Human Cell Atlas, tissue-specific atlas) and map query cells with tools like scArches, Symphony, or Seurat's `MapQuery`. Strong when a reference of the same tissue exists.
- **Automated classifier-based.** Tools like SingleR, CellTypist, or scANVI assign labels from a reference. Useful as a first pass and a sanity check on manual labels.

Use at least two approaches; cell types where they agree are robust, and disagreements deserve investigation. Be honest about uncertain calls. Label them "unknown" rather than guessing; downstream interpretation depends on this rigor.

Hierarchical labeling helps — major lineage labels first (T cell, myeloid, epithelial), then subtypes within each lineage. The two scales serve different audiences and downstream analyses.

### 9. Compare conditions — pseudobulk where possible

The most common single-cell DE error is testing cells as replicates rather than samples. Cells from the same donor are not independent observations. Sample-level pseudobulk corrects this.

For DE between conditions within a cell type:

- Aggregate counts per sample within the cell type (sum, not mean).
- Discard cell types with too few cells per sample (a common floor is 10–30 cells per sample per type) or document the limitation.
- Run DE on the pseudobulk matrix using DESeq2, edgeR, or limma-voom with a model that includes condition and any donor or batch covariates.
- Report adjusted p-values and shrunken effect sizes.

Cell-level DE methods (Wilcoxon on cells, MAST) are appropriate for within-sample comparisons (one cluster versus another in a single sample) but inflate type-I error when used across samples as if cells were replicates. Use them for marker discovery and within-sample contrasts, not for cross-condition tests with multiple donors.

For studies with very small numbers of donors (one per condition), cross-condition DE is exploratory at best; flag it as such and consider whether the question can be answered at all without more biological replicates.

### 10. Run compositional analysis when proportions matter

If the question is "does the proportion of cell type X differ between conditions," use a method appropriate to compositional data — `scCODA`, propeller from speckle, or a beta-binomial mixed model — not a naïve proportion test. Compositional data has implicit constraints (proportions sum to one); standard tests treat the components as independent and produce inflated significance.

Report proportions as point estimates per sample with uncertainty intervals, alongside the test result.

### 11. Plan for trajectory and other advanced analyses with skepticism

Pseudotime, RNA velocity, and trajectory inference look like signal even on null data; their outputs can be over-interpreted easily. If trajectory analysis is in scope:

- Verify the biology supports a continuous process; not every transition is a trajectory.
- Pick one method (PAGA, Monocle3, slingshot, scVelo for RNA velocity) and use it consistently.
- Sanity-check against known landmark genes whose temporal expression is documented.
- Report uncertainty; pseudotime estimates can be noisy and the absolute scale is rarely interpretable.

Treat trajectory and velocity results as hypothesis-generating unless validated independently.

### 12. Document, version, and pre-register

Lock the analysis decisions before looking at results:

- QC thresholds per sample.
- Doublet method and rate.
- Normalization and HVG strategy.
- Integration method and parameters.
- Clustering resolution.
- Annotation strategy and references.
- DE method and any pseudobulk thresholds.

Record the package versions for Scanpy, scvi-tools, Seurat, AnnData, and any tools in the workflow. Single-cell tooling moves fast; an analysis is reproducible only when the versions are pinned. Save the final AnnData or Seurat object with its provenance attached.

### 13. Watch for common failure modes specific to single-cell

A short list of pitfalls that recur across studies and that the plan should explicitly guard against:

- **Empty-droplet leakage.** Cells with very low UMI counts that survived empty-droplet filtering form a "background" cluster of indistinct identity. If a cluster shows uniformly low UMIs and high mitochondrial proportion, suspect it.
- **Over-integration.** A UMAP where condition is invisible because integration was too aggressive. Validate by checking whether known marker genes still discriminate cell types and whether biologically expected condition shifts remain.
- **Under-integration.** A UMAP where batches form parallel islands of the same cell type. Validate that integration metrics (silhouette by batch, kBET-style mixing) move in the right direction.
- **Cluster splitting at the wrong resolution.** Resolution too high splits noisy clusters into spurious subtypes; resolution too low merges biologically distinct cells. Use stability tools rather than picking by eye.
- **Annotation circularity.** Annotating a cluster from its top markers, then describing the markers as "cell-type-specific" because they came from that cluster. Cross-validate against external references.
- **Single-cell DE without donor structure.** Reporting thousands of significant genes from a Wilcoxon test on cells across donors. The result is mostly inter-donor variation. Pseudobulk.

### 14. Plan for atlas-scale concerns when relevant

For studies that span many samples, donors, or sources:

- Decide whether to integrate everything in one pass or build a reference and map queries against it. Reference mapping scales better when the atlas grows.
- For very large studies, scVI / scANVI plus a GPU is often the practical choice; CPU-only Harmony or BBKNN may not scale.
- The annotation hierarchy matters more at scale. Major-lineage annotations are usually robust; rare-subtype annotations need explicit confidence labels.
- Storage and I/O become real constraints. Backed-AnnData (HDF5 or zarr) is the typical solution; plan for it before the project doubles in size.

### 15. Tie the analysis back to wet-lab validation

Single-cell findings are easy to over-interpret. Plan validation before the figures are made:

- For headline cell-type findings, plan a confirmatory experiment — flow cytometry for surface markers, immunohistochemistry for tissue context, a smaller targeted panel.
- For headline DE findings, plan a follow-up at protein level or in a second cohort.
- For trajectory or velocity findings, plan a time-course or lineage-tracing experiment.

The analysis plan should name which findings would trigger which follow-up. A scRNA-seq result without a downstream validation path is a poster, not a discovery.

## Inputs

- A description of the study, design, and chemistry.
- Any prior artifacts already produced (counts, atlas references, prior pipelines).
- Known batch and confounder structure.
- The primary biological question.
- The downstream use.

## Outputs

- A full analysis plan from raw counts to comparison.
- Concrete, tissue-aware QC thresholds.
- An integration strategy with validation diagnostics.
- An annotation and DE plan with the right replication structure.
- A pre-registration checklist locking decisions before unblinding.

## Examples

**Example A — discovery atlas, single tissue, six donors.** Plan: Scanpy workflow. QC per donor on UMI count, gene count, and percent mitochondrial, with tissue-appropriate ceilings. Scrublet for doublets. Log-normalize and pick 3,000 HVGs in a batch-aware way. Harmony integration over donor. Leiden at resolution 0.6 on 30 PCs. Manual annotation cross-checked with CellTypist using a tissue-matched model. DE between major lineages with Wilcoxon (within-sample marker discovery), not cross-sample, because the question is cell types not conditions.

**Example B — condition comparison, 8 vs 8, two batches.** Plan: Seurat workflow with sctransform normalization. Per-sample QC with scDblFinder. Integrate by batch using Seurat's anchors. Cluster at resolution 0.4 to keep major types stable. Annotate hierarchically with reference mapping against a public PBMC atlas. For DE between conditions, aggregate to pseudobulk per donor per cell type, then DESeq2 with `~ batch + condition`. Flag any cell types with fewer than 15 cells per donor as "insufficient power, exploratory only."

**Example C — atlas integration project, ten data sources.** Plan: scvi-tools with scANVI for integration plus label transfer from a high-quality reference cohort. Stricter QC because mixed sources differ in chemistry and depth — per-source thresholds rather than global. Output is an integrated embedding plus harmonized annotations, with explicit "low confidence" labels for cells whose nearest-neighbor mapping has weak support. Composition tests are deferred because the atlas spans heterogeneous sources where composition reflects sampling, not biology.

## Limitations

- This skill covers transcriptomic single-cell. CITE-seq, multiome, and spatial transcriptomics need additional steps not covered.
- It assumes mainstream chemistry (10x Chromium, similar). Plate-based protocols (Smart-seq) and very-high-cell-count technologies have different conventions.
- Perturbation screens (Perturb-seq, CROP-seq) need guide-assignment and screen-specific analysis steps beyond the scope here.
- Tools and best practices in single-cell evolve quickly; lock versions and revisit the plan when the field has moved.

## Sources reviewed

- https://github.com/scverse/scanpy
- https://github.com/satijalab/seurat
- https://github.com/nf-core/scrnaseq
- https://github.com/nextflow-io/nextflow
- https://github.com/snakemake/snakemake
