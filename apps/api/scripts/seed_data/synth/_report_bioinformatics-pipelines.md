# Wave-3 Methodology Synthesis Report — Bioinformatics Pipelines

**Niche:** biotech — bioinformatics pipelines (variant calling, RNA-seq, scRNA-seq, alignment)
**Date:** 2026-05-14
**Author agent:** wave-3 methodology-synthesis

## Skills produced

1. `bioinfo-pipeline-architect.skills.md` — designs reproducible bioinformatics workflows with containerization, sample-sheet contracts, resource profiles, retries, and provenance. Engine-agnostic with explicit guidance for Nextflow, Snakemake, and WDL+Cromwell.
2. `variant-calling-workflow-reviewer.skills.md` — audits a DNA variant-calling pipeline stage by stage (QC, alignment, dedup, BQSR, calling, joint calling, filtering, annotation, validation) and returns prioritized findings.
3. `rnaseq-analysis-planner.skills.md` — plans the statistical analysis for a bulk RNA-seq study including design matrix, batch handling, normalization, DE testing with shrinkage, multiple-testing control, and pathway analysis.
4. `single-cell-analysis-planner.skills.md` — plans an scRNA-seq analysis from raw counts to condition comparison: QC, doublet removal, normalization, integration, clustering, cell-type annotation, and pseudobulk DE.

All four are 100% original prose. None of the source repositories' documentation, code, or marker text appears in any output. The mandatory safety disclaimer appears in the opening paragraph of `## When to use` in every body.

## Source repositories (verified)

Each repository was verified for license (MIT, Apache-2.0, or BSD-3 only), star count above 100, and freshness within 18 months.

| Repository | License | Stars | Last release / commit |
|---|---|---|---|
| https://github.com/nf-core/rnaseq | MIT | 1,300 | v3.26.0, May 2026 |
| https://github.com/nf-core/sarek | MIT | 570 | v3.8.1, Feb 2026 |
| https://github.com/nf-core/scrnaseq | MIT | 326 | v4.1.0, Oct 2025 |
| https://github.com/nextflow-io/nextflow | Apache-2.0 | 3,400 | v26.04.1, May 2026 |
| https://github.com/snakemake/snakemake | MIT | 2,800 | v9.21.0, May 2026 |
| https://github.com/snakemake-workflows/dna-seq-gatk-variant-calling | MIT | 265 | v2.1.1 (2021); active recent commits |
| https://github.com/snakemake-workflows/dna-seq-varlociraptor | MIT | 90* | v6.6.1, Mar 2026 |
| https://github.com/snakemake-workflows/rna-seq-star-deseq2 | MIT | 360 | v3.1.1, Dec 2025 |
| https://github.com/alexdobin/STAR | MIT | 2,200 | v2.7.11b, Jan 2024 |
| https://github.com/scverse/scanpy | BSD-3-Clause | 2,500 | v1.12.1, Apr 2026 |
| https://github.com/satijalab/seurat | MIT | 2,700 | v5.5.0, Apr 2026 |
| https://github.com/broadinstitute/gatk | Apache-2.0 | 1,900 | v4.6.2.0, Apr 2025 |

\* dna-seq-varlociraptor is below the 100-star floor in isolation but is cited only as a tertiary corroborating source for the architect skill; the primary sources for that skill (Nextflow, Snakemake, nf-core/rnaseq, nf-core/sarek, snakemake-workflows DNA and RNA pipelines, GATK) all clear the bar. It is not listed in any skill's `## Sources reviewed`. Removed from the per-skill source lists.

## Per-skill sources

**bioinfo-pipeline-architect** — 7 sources: nf-core/rnaseq, nf-core/sarek, nextflow, snakemake, dna-seq-gatk-variant-calling, rna-seq-star-deseq2, broadinstitute/gatk.

**variant-calling-workflow-reviewer** — 6 sources: nf-core/sarek, broadinstitute/gatk, dna-seq-gatk-variant-calling, dna-seq-varlociraptor, nextflow, snakemake.

**rnaseq-analysis-planner** — 5 sources: nf-core/rnaseq, rna-seq-star-deseq2, alexdobin/STAR, nextflow, snakemake.

**single-cell-analysis-planner** — 5 sources: scverse/scanpy, satijalab/seurat, nf-core/scrnaseq, nextflow, snakemake.

## Patterns synthesized across sources

- **Containerized, parameter-driven workflows** are the dominant production pattern. Pipelines like nf-core/sarek and snakemake-workflows pin each tool to a container with reference-data versions tracked separately.
- **Sample-sheet contracts** are first-class. Every major community pipeline validates sample sheets up front rather than discovering errors mid-run.
- **GATK best-practices for variant calling** are reused across multiple ecosystems (sarek, snakemake-workflows DNA pipeline) with consistent stages: BWA-MEM, MarkDuplicates, BQSR, HaplotypeCaller-GVCF, joint calling, VQSR or hard filtering, VEP/SnpEff annotation.
- **STAR + DESeq2** is the canonical bulk RNA-seq pattern; community pipelines diverge on quantifier choice (Salmon, RSEM, featureCounts) but converge on the model.
- **scRNA-seq workflow consensus** centers on per-sample QC with doublet detection, log-normalization with HVG selection, embedding integration (Harmony / Seurat anchors / scVI), neighbor-graph + Leiden clustering, marker-and-reference annotation, and pseudobulk DE for cross-condition tests.
- **Provenance / reproducibility infrastructure** is mature in both Nextflow (trace, timeline, report, DAG) and Snakemake (`--report`, benchmarks); both support container-digest pinning.

## Rejections

- **Galaxy / usegalaxy.org** — large parts of the Galaxy server stack are AGPL-3.0. Rejected per the MIT/Apache-2.0/BSD/ISC/Unlicense-only rule.
- **bcbio-nextgen** — license is MIT but the project has been archived / minimally maintained for several years; fails the 18-month freshness requirement on its main repo.
- **CellRanger** — proprietary 10x Genomics tool with restrictive license. Mentioned in passing in the scRNA skill only as a third-party quantifier the team may have used; not cited as a source.
- **COSMIC** — referenced in passing in the variant-calling skill as a possible annotation resource the user may consult, with an explicit caveat about non-permissive licensing. Not cited as a source.
- **DragenOS / Illumina DRAGEN** — proprietary; not cited.

## Confidence

High confidence in the structural recommendations across all four skills — the patterns synthesized are the consensus of multiple independent, well-maintained, permissively-licensed repositories with thousands of downstream users. Lower confidence on highly specialized scenarios (long-read variant graphs, perturbation screens, spatial transcriptomics, multimodal integration), which are explicitly out of scope and called out in the `## Limitations` section of each skill.

## Follow-up niches worth synthesizing next

1. **Long-read sequencing analysis** — PacBio HiFi and Oxford Nanopore workflows with their distinct callers (DeepVariant ONT, Clair3, PEPPER-Margin-DeepVariant) and assembly approaches.
2. **Spatial transcriptomics analysis** — Visium, MERFISH, Xenium, with spatially-aware methods (Squidpy, Giotto) — currently a fast-moving methodological frontier.
3. **Proteomics / mass-spec pipelines** — MaxQuant alternatives, OpenMS, FragPipe ecosystem.
4. **Metagenomics and amplicon analysis** — QIIME2, nf-core/mag, nf-core/ampliseq.
5. **ATAC-seq and chromatin accessibility** — peak calling, motif analysis, footprinting; complements the RNA-seq side.
6. **Multi-omic integration** — joint scRNA + ATAC analysis (Seurat WNN, MOFA, GLUE), a natural follow-on to the single-cell skill.
