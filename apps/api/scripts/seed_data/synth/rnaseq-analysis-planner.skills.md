---
id: skillsgit-curated/rnaseq-analysis-planner
version: 1.0.0
name: Bulk RNA-seq Analysis Planner
description: Plans a defensible bulk RNA-seq analysis — design matrix, batch effects, normalization, differential expression testing, multiple-testing correction, and pathway analysis — so the result holds up to review and reproduces in a second cohort.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: biotech
tags: [niche:bioinformatics-pipelines, rna-seq, differential-expression, deseq2, edger, limma, batch-effects, pathway-analysis]
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
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - rna-seq analysis
  - bulk rna-seq
  - differential expression
  - design matrix
  - batch effects
  - deseq2
  - edger
  - limma voom
  - gene set enrichment
  - pathway analysis
  - multiple testing correction
  - rnaseq plan
example_invocations:
  - "Plan the analysis for a bulk RNA-seq experiment with three treatment groups and two batches."
  - "We have a paired-design RNA-seq study — what's the right model?"
  - "Help me set up DESeq2 with a batch covariate and an interaction term."
  - "Plan a pathway analysis that won't get torn apart in peer review."
inputs:
  - name: experiment_description
    type: text
    required: true
    description: The biological question, the conditions compared, the number of samples per group, the species, the tissue or cell type, and the sequencing protocol (polyA, ribo-depleted, stranded, paired-end, read length).
  - name: design_details
    type: text
    required: false
    description: How samples are grouped — independent versus paired/repeated measures, time course, factorial design, presence of technical replicates, batch and sequencing-lane structure.
  - name: known_confounders
    type: text
    required: false
    description: Variables known to associate with biology or batch — sex, age, RIN, library prep date, sequencer, operator, cell-type composition.
  - name: existing_counts
    type: text
    required: false
    description: Whether counts already exist, the quantifier used (STAR/featureCounts, Salmon, Kallisto, RSEM), and the annotation version.
  - name: downstream_use
    type: text
    required: false
    description: How findings will be used — exploratory list, publication, follow-up validation, clinical research. Drives strictness of multiple-testing control and reporting.
outputs:
  - name: analysis_plan
    type: markdown
    description: The full plan — design matrix, modeling choice, filtering, normalization, DE testing, and shrinkage strategy.
  - name: batch_strategy
    type: markdown
    description: How to detect, model, or correct batch effects, with the decision tree for when to include batch as a covariate versus apply explicit correction.
  - name: significance_and_reporting_rules
    type: markdown
    description: Adjusted p-value thresholds, effect-size filters, and the reporting structure for differential-expression results.
  - name: pathway_analysis_plan
    type: markdown
    description: The chosen enrichment method (ORA, GSEA, camera, fgsea), background set definition, and how to interpret the output without overclaiming.
  - name: pre_registration_checklist
    type: markdown
    description: The decisions that should be locked before unblinding to results, so post-hoc tweaks do not erode the analysis.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

This skill produces methodology guidance for bioinformatics workflows. Outputs are not validated clinical or research conclusions and must be reviewed by qualified scientific staff before being acted upon. Pipelines built from this guidance must be wet-lab-validated and version-locked before any decisions are made on the results.

Use this skill when planning the statistical analysis of a bulk RNA-seq experiment. Specifically:

- A new RNA-seq study is being designed and the analysis plan needs to be locked before samples are collected or sequenced.
- A team has counts but has not committed to a design matrix or testing approach.
- A study with non-trivial design — paired samples, repeated measures, factorial conditions, time course — needs a model that respects the design.
- Batch effects are visible and the team needs a principled response.
- A draft analysis is being prepared for review and needs a methodology pass.

Do not use this skill to choose the upstream quantifier or audit the alignment pipeline; pair with the bioinformatics pipeline architect and, for single cell, with the single-cell planner. Do not use it to interpret biology; the output is the analysis structure, not the conclusions.

## How to apply

The order matters: design first, model second, filtering and normalization third, DE testing fourth, reporting last. Pathway analysis is downstream of DE; doing it before the DE is set is a common mistake.

### 1. State the biological question precisely

Write a one-sentence question the analysis is supposed to answer. "Treated versus control" is not enough. Are we asking which genes change between treated and control averaged across donors? Within each donor (paired)? Which genes change differently in treated patients compared to controls when comparing day 7 to day 0? The question dictates the design matrix and the contrast.

For each question, identify:

- The outcome variable (gene-level count, transcript-level count, exon-level for splicing).
- The primary factor of interest.
- Other factors that must be modeled (paired structure, batch, covariates).
- The specific contrast or set of contrasts.

Lock these before looking at data. Decisions made after seeing the volcano plot are not principled.

### 2. Inventory samples and design structure

Build a sample sheet that the analysis script will read. Each row is one library; columns include sample biological ID, condition factor levels, batch and lane, sex, age or covariates, RIN, library prep batch, sequencing date. If samples are paired (same donor across conditions, same site across days), add a `subject` or `pair` column. Time-course studies add `timepoint`.

Examine the cross-tabulation of factors. If treatment and batch are fully confounded (every batch contains only one condition), no model can rescue the analysis — the data cannot answer the question. Flag this immediately; the fix is wet-lab, not statistical.

Partial confounding (uneven distribution of batch across conditions) is workable but raises uncertainty; it should be modeled, not ignored.

### 3. Choose the modeling framework

The dominant choices for bulk RNA-seq differential expression are DESeq2, edgeR (including the quasi-likelihood variant), and limma-voom. All three are well-validated; the choice is taste plus context.

- DESeq2 fits a negative binomial GLM per gene with shared dispersion shrinkage and offers convenient effect-size shrinkage via `lfcShrink`. It is the default for many labs and is well-suited to small-to-medium cohorts.
- edgeR with quasi-likelihood (`glmQLFit` + `glmQLFTest`) controls type-I error well in small samples and handles complex designs.
- limma-voom transforms counts to log-CPM with associated precision weights and runs linear modeling. It scales well to large cohorts and supports duplicate correlation for repeated measures.

For very large cohorts (hundreds to thousands of samples), limma-voom or edgeR's bulk-friendly variants are typically faster. For small cohorts, dispersion shrinkage (DESeq2 or edgeR) is particularly valuable. Pick one for the primary analysis, commit, and note the choice.

### 4. Build the design matrix

Translate the biological question into a model formula.

- Simple two-group: `~ condition`.
- With batch: `~ batch + condition`. The factor of interest goes last; the contrast is specified against the last factor.
- Paired design: `~ subject + condition` when subject is treatable as a fixed effect (small numbers of subjects); use limma's `duplicateCorrelation` or random effects via `dream` (variancePartition) for many subjects with structure.
- Factorial: `~ genotype + treatment + genotype:treatment`. The interaction term tests whether the treatment effect differs by genotype.
- Time course: model time as a factor when changes are non-monotonic, or as a continuous covariate with splines when shape is interesting. The likelihood-ratio test against a reduced model identifies time-varying genes.
- Continuous covariates (age, RIN): include them when they are likely to drive variance. Center continuous covariates for interpretability.

Write the contrast explicitly. "Treated versus control" can mean treated minus control or control minus treated; sign conventions are a frequent source of confusion in downstream interpretation.

### 5. Filter low-count genes before testing

Independent filtering improves multiple-testing power. The convention is to remove genes whose expression is so low that no realistic effect could be detected.

A defensible default: keep genes with at least N counts (commonly 10) in at least the smallest group size. DESeq2's `results` already performs independent filtering by mean expression; edgeR provides `filterByExpr`. Apply filtering before testing, document the threshold, and report how many genes survived.

Do not filter on a variability or differential statistic — that is selection on the outcome and inflates type-I error.

### 6. Normalize, then check the normalization

Library-size normalization is the baseline. DESeq2 uses the median-of-ratios (size factors), edgeR uses TMM, and limma-voom uses log-CPM with TMM normalization. All three handle composition bias under most conditions.

Before testing, sanity-check the normalization with diagnostics:

- A PCA on variance-stabilized counts (DESeq2's `vst` or `rlog`, edgeR's `cpm(log=TRUE)`, limma-voom's `voom` output) plotted with each candidate factor colored. The structure visible here tells you what the model must handle.
- Box plots of normalized counts per sample to spot outliers.
- Per-sample size-factor or norm-factor values; values far from one indicate libraries that pulled hard during normalization and may behave differently downstream.
- A hierarchical clustering of sample-to-sample distances. Samples that cluster by batch rather than biology preview a problem.

If PCA shows that PC1 is batch, the design must include batch (or remove it via surrogate-variable analysis); fitting `~ condition` alone is not viable.

### 7. Handle batch effects deliberately

Three responses, in increasing strength:

- Include the known batch as a covariate in the design matrix. This is the cleanest approach when batch is recorded.
- If unknown latent factors are suspected (RNA quality, unmeasured cell composition), estimate surrogate variables (sva package's `sva` or `svaseq`) and include them as covariates.
- Explicitly remove batch from the count matrix using `ComBat-seq` (sva) only when downstream use requires a corrected matrix for visualization or clustering. Do not run DE on a ComBat-corrected matrix; instead, run DE with batch in the model.

Document which approach is used. Mixing — running ComBat and then including batch as a covariate — double-corrects and is wrong.

Cell-composition confounding deserves special attention for bulk tissues. Deconvolution (CIBERSORT-style references, MuSiC, dtangle) can estimate proportions; significant composition differences across conditions are biology, but they may also be the confound that drives a "treatment effect." Acknowledge and, when possible, model.

### 8. Run differential expression with shrinkage

Fit the model and test the contrast. Report both an adjusted p-value and an effect-size estimate.

For DESeq2, prefer `lfcShrink` with the `apeglm` or `ashr` shrinkage estimator for stable effect sizes, especially with low-count genes. edgeR's effect-size estimates are stabilized through dispersion shrinkage; limma-voom's modeling already provides shrinkage. The point is to avoid reporting wild log-fold-changes for low-count genes; they will fail to replicate.

Output: a table with gene identifier, base mean, log-fold change (shrunk), standard error, test statistic, p-value, adjusted p-value, and annotation columns (symbol, biotype, chromosome). The annotation should come from the same release used for quantification.

### 9. Apply multiple-testing correction

Benjamini-Hochberg FDR control is the dominant choice for genome-wide DE. The conventional adjusted p-value threshold is 0.05; tighter thresholds (0.01) are common when many comparisons are made or downstream effort per hit is high.

Set the threshold before unblinding. Set an effect-size threshold too — many small significant changes are noisy and rarely actionable. A common reporting rule is adjusted p-value below 0.05 and absolute log-fold change above some study-relevant value (often 0.585, equivalent to a 1.5-fold change, or 1.0 for a 2-fold change). Document both thresholds.

For studies with many contrasts (factorial designs, time course), consider whether each contrast is its own family for FDR control or whether all contrasts share one. For independent biological questions, separate families are appropriate. For closely related contrasts, sharing the family is more conservative.

### 10. Verify the result before celebrating

Before reporting results, sanity-check them:

- The number of DE genes should be on the order of biological expectation. Zero significant genes against a strong intervention is suspect; ten thousand significant genes from a subtle perturbation is also suspect.
- The top hits should pass an eyeball test on the counts plot (boxplot of normalized counts per condition for the top genes).
- House-keeping genes should be stable across conditions.
- A volcano plot should not look one-sided in an unexpected way.
- If a paired or batch design is in use, refit without the structure and confirm the results differ in the expected direction. They should.

If anything looks off, return to the design and the QC. Do not move to pathway analysis on a result that has not been sanity-checked.

### 11. Plan pathway and enrichment analysis

The two dominant families are over-representation analysis (ORA) and gene-set enrichment analysis (GSEA-style).

- ORA (`enrichGO`, `enrichKEGG` in clusterProfiler, hypergeometric tests) takes a defined hit list and tests whether gene sets are over-represented relative to a background. It is sensitive to the choice of background — use the tested-gene universe (post-filter), not the whole genome. Avoid the common error of using the genome as background when only a few thousand genes were tested.
- GSEA-style methods (fgsea, GSEA-preranked, `camera`) take a ranked list of all tested genes and test for shifts at the top or bottom of the ranking. They are more powerful when many small consistent changes share a pathway. Rank by signed test statistic, not by log-fold-change alone (the test statistic carries variance information).

Pick a small, well-curated gene-set collection (Hallmark from MSigDB is a robust default; KEGG, Reactome, GO BP, custom panels are valid). Avoid running many overlapping collections and cherry-picking; that inflates the apparent strength of findings.

Report enrichment results with adjusted p-values, effect-size analogs (NES for GSEA, fold enrichment for ORA), and the leading-edge or hit gene list for context. A pathway result without a credible underlying gene set is decorative.

### 12. Document and pre-register

Before unblinding to specific gene-level results, lock:

- The design matrix and the contrasts.
- The filtering threshold.
- The DE method and shrinkage choice.
- The significance threshold and effect-size threshold.
- The enrichment method, the gene-set collection, and the background.

This pre-analysis plan can live in the project repository as a short Markdown document. It does not need to be public; it needs to be dated and unchanged after the first peek at results. Post-hoc changes are allowed but should be explicitly labeled exploratory.

### 13. Plan for replication and external validity

A single-cohort DE list is a hypothesis, not a conclusion. Where possible, plan for replication from the start:

- A second independent cohort, even small, reruns the same model and reports concordance of effect direction and rank-correlation of effect sizes. Strict overlap of significant gene sets is too brittle; concordance metrics are more informative.
- For publicly available data (GEO, ArrayExpress, Recount) where a comparable study exists, plan a meta-style comparison. Document the comparator's design and limitations.
- If neither is feasible, frame the analysis explicitly as discovery and identify which findings the team would carry forward to wet-lab validation, with prioritization criteria written before the result.

### 14. Handle special data shapes deliberately

Some experimental designs need adjustments to the standard plan:

- **Time courses with irregular sampling.** If timepoints are unevenly spaced, treating time as a factor is safer than as a continuous variable. If continuous treatment is needed, splines (`splines::ns`) capture nonlinearity without overfitting.
- **Repeated measures within subject.** When the same donor contributes many samples, fixed-effect subject is workable for moderate counts. For large designs, mixed-effects approaches (`variancePartition` `dream`) or limma's `duplicateCorrelation` are appropriate. Specify which one and why.
- **Imbalanced batch.** If one batch contains many more samples than another, downweight the smaller batch's leverage or accept that effect estimates for biology confounded with the small batch are imprecise; do not pretend the imbalance is fixable.
- **3' RNA-seq, ribo-depleted, total RNA, small RNA.** The library type changes the quantifier and the gene-set conventions. Lock the library type in the plan; do not silently mix.
- **Allele-specific expression, fusion detection, splicing.** These are not standard DE outputs. If they are in scope, name the tools (e.g., DEXSeq for exon-level, Arriba or STAR-Fusion for fusions) and treat them as separate analyses with their own design considerations.

### 15. Write the report consumer-side

The analysis is for the biologist who will read it, not the bioinformatician who runs it. Plan the report:

- An executive summary that names the question and the answer in one paragraph.
- A diagnostics section that shows the QC and the model fit. Reviewers should be able to verify the analysis was set up correctly without re-running anything.
- The DE result table with sensible columns, annotation joined in, and a stable sort order.
- A small number of confirmatory plots — PCA, volcano, top-gene boxplots, pathway enrichment for the headline pathways.
- A methods section that names every package and version, every threshold, and every decision in plain prose.

A report a biologist can hand to a peer reviewer without reformatting is the deliverable. Anything less is internal scratch work.

## Inputs

- The biological question and study design.
- Sample-level metadata including biology, batch, and covariates.
- Known or suspected confounders.
- Existing counts or quantifier choice if upstream steps are settled.
- How the results will be used downstream.

## Outputs

- An analysis plan with design matrix, modeling choice, filtering, normalization, DE testing, and shrinkage.
- A batch-effect strategy with a decision rule.
- Significance and reporting rules locked before unblinding.
- A pathway-analysis plan with method and background.
- A pre-registration checklist of decisions to fix in advance.

## Examples

**Example A — two-arm trial, 12 vs 12, two batches.** Plan: DESeq2 with `~ batch + condition`. Filter by `rowSums(counts >= 10) >= 12`. VST for PCA. Verify batch in PC1/PC2; if so, the model already handles it. Shrink with `apeglm`. Threshold: adjusted p below 0.05 and absolute log2 fold change above 0.585. Pathway: fgsea on Hallmark with signed-statistic ranking. Pre-register the contrast as "treated minus control."

**Example B — paired design, 8 donors, two conditions each.** Plan: DESeq2 with `~ subject + condition` (subject as a fixed effect; 8 subjects keeps the model identifiable). Confirm the contrast pulls only `condition` after subject is partialed out. Pre-test diagnostic: PCA colored by subject should show subject-driven structure that the model absorbs. Reporting: same FDR convention; report effect sizes alongside per-pair count plots for the top hits, since pairing is the central design feature.

**Example C — factorial design with interaction, 4 groups of 6.** Plan: edgeR quasi-likelihood with `~ genotype + treatment + genotype:treatment`. Three contrasts of interest: treatment effect in WT, treatment effect in KO, and the interaction. Apply FDR per contrast as separate families because each answers a distinct biological question; flag that decision in the report. Pathway analysis on the interaction term needs careful framing — pathways "differently affected by treatment in KO" — and a small, hypothesis-driven gene set rather than a broad scan.

## Limitations

- This skill addresses bulk RNA-seq. Single-cell RNA-seq has different conventions; use the single-cell planner.
- Splicing and isoform-level analysis (DEXSeq, rMATS, swish at transcript level) is not covered in depth; the principles transfer but the modeling differs.
- This is a planning skill, not a replacement for a statistician's review on complex studies (mixed models with many random effects, hierarchical designs, large clinical cohorts).
- Power and sample-size calculation are not the focus; a separate power analysis is recommended for borderline-sized studies.

### 16. Anti-patterns to refuse

- **Running DE on TPM or RPKM.** Differential expression methods expect counts. Transforming away the count nature before testing breaks variance models. TPM is for visualization, not testing.
- **Using a heatmap of "significant genes" to claim a pattern.** Selecting genes for the heatmap by significance and then describing the pattern in the same data is selection bias. Use independent samples or independent contrasts.
- **Reporting "no genes were significant" without a power check.** A null result with eight underpowered samples is not biology; it is study design.
- **Cherry-picking the gene-set collection.** Running fifteen pathway collections and reporting only the one with the most hits inflates the apparent strength.
- **Re-doing the analysis until the result looks reasonable.** Pre-registration exists for this reason. Document the path actually taken.

### 17. Final shape of the deliverable

A complete plan from this skill comprises:

- The biological question and the contrast(s).
- The sample table and the cross-tabulation that shows the design is identifiable.
- The model formula in code-ready form.
- The filtering, normalization, and DE method with the chosen shrinkage estimator.
- The thresholds for significance and effect size.
- The pathway plan with method, collection, and background.
- The pre-registration checklist, dated.

This plan should be reviewable by a statistician unfamiliar with the project in under thirty minutes.

## Sources reviewed

- https://github.com/nf-core/rnaseq
- https://github.com/snakemake-workflows/rna-seq-star-deseq2
- https://github.com/alexdobin/STAR
- https://github.com/nextflow-io/nextflow
- https://github.com/snakemake/snakemake
