---
id: skillsgit-curated/long-read-genomics-pipeline-architect
version: 1.0.0
name: Long-Read Genomics Pipeline Architect
description: Plans a long-read sequencing analysis pipeline for Oxford Nanopore or PacBio HiFi data — basecalling, alignment, structural variant calling, methylation, and assembly — with the trade-offs that matter at each step.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: biotech
tags: [niche:long-read-sequencing, nanopore, pacbio-hifi, structural-variants, methylation, genome-assembly, bioinformatics-pipelines, nextflow]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: [code_execution, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - long read sequencing
  - nanopore pipeline
  - oxford nanopore
  - pacbio hifi
  - structural variant calling
  - genome assembly
  - methylation calling
  - hifiasm
  - clair3
  - sniffles
  - de novo assembly
  - haplotype phasing
example_invocations:
  - "Plan a pipeline for ONT R10.4 whole-genome data: basecalling to phased SNVs, SVs, and methylation."
  - "We have a PacBio HiFi cohort for de novo assembly — what should the workflow look like?"
  - "How should I structure variant calling for nanopore tumor/normal samples?"
  - "Design a long-read methylation analysis covering both ONT and HiFi inputs."
inputs:
  - name: platform_and_chemistry
    type: text
    required: true
    description: Which long-read platform (Oxford Nanopore PromethION/MinION/GridION, or PacBio Sequel II/IIe/Revio), which chemistry/flowcell generation, and any kit details that influence basecaller choice and expected accuracy.
  - name: scientific_goal
    type: text
    required: true
    description: What the analysis must produce — small variants, structural variants, methylation calls, de novo assembly, transcript discovery, or some combination. Drives module selection.
  - name: sample_design
    type: text
    required: false
    description: Number of samples, single-genome versus trio/family versus tumor-normal versus cohort, ploidy assumptions, and any reference comparison expected.
  - name: reference_strategy
    type: choice
    required: false
    description: Whether the analysis maps to an existing reference, builds a de novo assembly, or uses a pangenome graph.
    choices: [reference-mapping, de-novo-assembly, pangenome-graph, hybrid]
  - name: constraints
    type: text
    required: false
    description: GPU availability for basecalling, storage budget for raw signal data, regulated environment requirements, turn-around-time targets.
outputs:
  - name: module_plan
    type: markdown
    description: Stage-by-stage module plan from raw signal through final artifacts, with the tool families considered at each stage and the chosen ones.
  - name: basecalling_decision
    type: markdown
    description: Whether to keep raw signal, which basecaller and model to use, and the trade-off between accuracy mode and throughput.
  - name: variant_calling_strategy
    type: markdown
    description: How small variants and structural variants are called, phased, and filtered, including platform-specific tool choices.
  - name: assembly_or_methylation_path
    type: markdown
    description: "If assembly: assembler, haplotype-resolution approach, polishing, and QC. If methylation: caller, aggregation, and differential methylation strategy."
  - name: qc_and_acceptance_gates
    type: markdown
    description: Per-sample QC metrics and the explicit thresholds below which a sample is excluded or flagged for re-prep.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

This skill produces methodology guidance for bioinformatics workflows. Outputs are not validated clinical or research conclusions and must be reviewed by qualified scientific staff before being acted upon. Pipelines built from this guidance must be wet-lab-validated and version-locked before any decisions are made on the results.

Use this skill when a team needs an analysis pipeline for long-read sequencing data — Oxford Nanopore or PacBio HiFi — and the project is past the "should we use long reads?" stage. Specifically:

- A core facility is bringing up a long-read service and needs the analysis stack laid out before the first production run.
- A research group has FAST5/POD5 from ONT or unaligned BAM/HiFi reads from PacBio and needs to get to variants, methylation, or an assembly.
- A lab is migrating from short-read variant calling to long-read variant calling and wants the structural-variant story handled.
- A consortium is harmonizing long-read analysis across sites and needs a shared methodology.

This skill does not pick the sequencing platform or coverage target — those are wet-lab decisions made before the pipeline. It does not generate executable Nextflow or Snakemake code; pair it with the bioinformatics pipeline architect skill for that scaffolding. It does not cover short-read or hybrid assembly except where long reads are the primary signal.

## How to apply

Work the steps in order. Long-read analysis differs from short-read in three places — basecalling, alignment, and the variants you can actually see — and the right answer at each step depends on the platform and the scientific goal.

### 1. Anchor the analysis on the goal, not the data type

"Long-read pipeline" is not yet a specification. The goal sets everything:

- For small variant calling on a reference, the pipeline ends with phased VCFs and you can be aggressive about discarding raw signal early.
- For structural variant calling, you need the alignment to preserve long supplementary records and the caller to read them; trimming is different from short-read trimming.
- For methylation, you need to preserve modified base information from basecalling all the way to the BED output. If methylation is added later, you almost always re-basecall.
- For de novo assembly, you do not align at all in the primary path; you assemble first, then optionally map back. Polishing and haplotype phasing matter; off-target reads matter less.
- For full-length transcript discovery, you map with a splice-aware long-read aligner and your downstream tools are RNA-specific.

Write the goal as the final artifact set: phased VCFs with SV calls and methylation BEDs, or a haplotype-resolved assembly with QC report, or a per-isoform count matrix. Every subsequent choice is in service of that artifact set.

### 2. Decide what to do with raw signal

This is the largest cost-and-storage decision in any long-read pipeline.

For Oxford Nanopore, the question is whether to keep POD5 (the modern signal container, having replaced FAST5 in most workflows) or only the basecalled outputs. Reasons to keep POD5:

- You expect to re-basecall when an improved model is released. ONT model improvements have changed accuracy meaningfully over recent generations.
- You need modified-base calls and the calls were not produced at basecalling time.
- The data is going into a long-lived resource (a reference cohort, a regulated archive).

Reasons not to keep POD5: it is large (often ~6-10x the size of a compressed FASTQ for the same data), and your science is point-in-time enough that re-basecalling is not worth the storage cost.

For PacBio, the analogous question is whether to keep the subreads/HiFi unaligned BAM. HiFi reads are already consensus and re-basecalling does not apply, but having the unaligned BAM with kinetics preserved enables methylation calling (5mC via primrose/jasmine derivatives) and re-alignment to alternative references.

Decide the policy explicitly: keep signal/unaligned BAM for N years for which sample classes; archive after; delete after. Write it down.

### 3. Plan basecalling deliberately

For ONT, this is the first compute step and it dominates the rest. Decisions:

- **Model choice.** Pick "super-accurate" (SUP) when accuracy matters for variant calling at low coverage, downstream phasing, or methylation. Pick "high-accuracy" (HAC) when throughput matters and downstream tools tolerate the lower base quality. Pick "fast" only for triage, real-time monitoring, or troubleshooting. Document the exact model identifier; it travels with the data.
- **Modified base calling.** Decide which modifications to call (5mC, 5hmC, 6mA) at basecalling time. Calling them later requires re-basecalling and revisiting the signal. Build the methylation calls into the same pass when methylation is in scope.
- **GPU planning.** Basecalling is the GPU-bound step. Estimate runtime against your fleet; for production cores, pinned GPU allocations matter more than CPU profiles.

For PacBio, "basecalling" is on-instrument and produces HiFi reads directly. The analogous decision is whether to run an instrument-side workflow that produces 5mC alongside HiFi, and whether to retain kinetics in the unaligned BAM.

The output of this stage is a (modified-base-aware where relevant) read set with a clear platform/model annotation in its header or sidecar metadata. Carry that annotation forward; tools that follow may need it to pick the right calling model.

### 4. Choose an aligner suited to long reads

Short-read aligners do not work for long reads. The default choices are:

- **minimap2** for general-purpose long-read alignment to a reference, DNA or RNA, on both ONT and PacBio HiFi. Preset matters: pick `map-ont`, `map-hifi`, `splice`, or `asm5/asm10/asm20` based on read type and target.
- **pbmm2** is PacBio's minimap2 wrapper that preserves PacBio-native BAM tags and is the right call for HiFi data going into PacBio-supplied callers.
- **winnowmap** and **NGMLR** appear in older pipelines and still have niches for highly repetitive regions or specific structural-variant callers; default to minimap2 unless the caller demands a different aligner.

Long-read alignments produce many supplementary records per read. Downstream tools depend on them; do not strip with naive scripts. CRAM is reasonable for storage if the reference is also preserved.

### 5. Decide between reference mapping and de novo assembly early

For human resequencing or model-organism work where the reference is good, reference mapping is the path. For non-model organisms, samples expected to carry large insertions or copy-number variation, or any project that wants a haplotype-resolved primary product, assembly is the path. Some projects want both — a draft assembly per sample plus alignment to a reference for comparison.

If you go down the assembly path, the sub-steps differ enough that they constitute a separate pipeline:

- **PacBio HiFi assembly.** Hifiasm is the strong default and is well-supported on diploid samples. With Hi-C reads or trio data, it produces fully phased haplotype assemblies. Without phasing data, it produces unphased primary and alternate assemblies.
- **Oxford Nanopore assembly.** Flye is widely used; combinations of Flye, NextDenovo, and downstream polishing with Medaka or DeepVariant-derived approaches are common. Pure-ONT assemblies historically polished with short reads; modern high-accuracy ONT can avoid that step but verify by QC.
- **Hybrid HiFi + ONT ultra-long.** Hifiasm-UL paths use ONT ultra-long reads to resolve repeats while HiFi carries the base accuracy. Telomere-to-telomere efforts run this pattern.
- **QC.** Use BUSCO for gene completeness, Merqyl-style k-mer evaluation, contig N50 and contiguity metrics, and (for diploids) phasing accuracy where truth data is available.

If reference mapping is the path, continue with the variant-calling steps.

### 6. Call small variants with a long-read-aware caller

Generic short-read variant callers do not work well on long-read alignments because the error profile is different. Pick a caller built for the platform:

- **Clair3** (and Clair3-Trio for families) is widely adopted for both ONT and HiFi. It uses platform-and-model-specific neural models; getting the model right is essential, and the right model is determined by the basecaller and chemistry, not by guesswork.
- **DeepVariant** has long-read modes for both PacBio HiFi and ONT and is often used inside larger workflows.
- **PEPPER-DeepVariant** workflows still appear, particularly in ONT contexts; check whether the supported tooling has moved to Clair3 or remained on this stack before committing.

Configure the caller for ploidy and produce a phased output where the caller supports it. Phasing using long reads is one of the practical advantages of the platform; do not throw it away by emitting unphased VCFs as the only artifact.

Normalize the VCF (left-align indels, decompose multi-allelics) before any downstream comparison or annotation.

### 7. Call structural variants — the long-read superpower

Long reads see structural variants that short reads cannot. Treat SV calling as a first-class output, not an afterthought.

- **Sniffles2** and **CuteSV** for ONT and HiFi single-sample or multi-sample SV calling. Sniffles2 supports joint calling across cohorts and produces population-level VCFs.
- **pbsv** for PacBio-native workflows where the input is unaligned HiFi BAM with PacBio tags.
- **SVIM** and **SVision** appear in some pipelines, often as orthogonal calls.

Define the SV types in scope (DEL, INS, DUP, INV, BND/TRA) and a minimum size threshold; long-read callers see down to ~30-50 bp in good data, but most workflows set a higher floor and rely on the small-variant caller for the lower end.

Merge calls when running multiple callers (SURVIVOR is a common choice) but only after deciding what "agreement" means: positional overlap with size tolerance, type match, and (where supported) genotype concordance.

Filter against published reference SV catalogs (gnomAD-SV, dbVar, population-specific resources) to flag common variants. For non-human work, build a small in-house catalog from control samples and reuse it.

### 8. Plan methylation calling if it is in scope

Methylation is a per-base output of the basecaller in modern ONT and is computed from kinetics in PacBio. The analysis pipeline:

- Aggregate per-read modified-base calls into per-position methylation frequencies. Modkit (for ONT) and similar tools produce BED or BEDGRAPH outputs of per-CpG methylation frequency with read depth.
- Phase methylation calls using the variant phasing produced earlier. Allele-specific methylation is one of the practical wins of long reads over array-based methylation.
- For differential methylation analysis across conditions, use a tool that respects the read-level information (DSS, methylKit-style approaches adapted for long reads, or specialized long-read DMR tools).

The output set is per-sample BED with read depth and methylation frequency, optionally split by haplotype, and (for cohort analyses) a DMR table.

### 9. Build per-sample QC into the pipeline

The QC metrics that matter for long-read data include:

- Read N50 — the median read length weighted by base count. The single most important quality indicator for long-read runs.
- Total yield in bases, and the equivalent coverage given the genome size.
- Mean per-read accuracy (Phred-equivalent). For HiFi this should be Q30+; for modern SUP-basecalled ONT, Q20+ is achievable.
- Mapped percentage and mean coverage when reference mapping.
- For methylation, the fraction of CpGs called and their mean depth.
- For assembly, the assembly contiguity (N50, NG50), gene-completeness via BUSCO, and (where data permits) a switch error rate.

Set explicit thresholds for sample-level pass/fail and surface them in the run report. NanoPlot, NanoStat, FastQC long-read modes, and pycoQC are common QC tooling. Aggregate with MultiQC where supported.

### 10. Build provenance for platform-and-model coupling

Long-read provenance has more axes than short-read provenance. Record per run:

- Sequencer platform and instrument identifier.
- Chemistry/kit/flowcell version.
- Basecaller name and exact model identifier (including modified-base model).
- Reference assembly version and any custom contigs.
- Caller versions and the platform-specific model identifiers they used.
- Read pre-processing parameters (any quality or length filtering).
- The container digests of every tool, as with any pipeline.

When the basecaller changes, the data effectively changes. Treat a re-basecalled cohort as a new dataset and gate downstream comparisons accordingly.

### 11. Cohort and joint analysis considerations

Cohort-level long-read analysis is younger than its short-read counterpart and the practices are still settling. Conservative defaults:

- Joint-call SVs with Sniffles2's population mode or by per-sample call + merge + re-genotyping with a compatible tool.
- For small variants, call per sample and joint-genotype with a tool that supports long-read VCFs. Avoid mixing long-read and short-read calls at the joint-genotyping step without explicit lift.
- For methylation, aggregate per-position methylation frequency tables across samples and build the differential analysis on top of those.

Document the joint-calling approach explicitly. Cohort comparisons across studies that used different basecallers or different chemistry are often invalid; flag the limitation in the run report.

### 12. Storage and lifecycle decisions

Long-read raw data is large. Plan the lifecycle:

- POD5/unaligned BAM — keep for the period defined in step 2.
- Aligned BAM/CRAM — keep durably; CRAM with reference-based compression is the right durable form for ONT and HiFi.
- VCFs, BEDs, count matrices — keep with provenance; these are the artifacts scientists read.
- Intermediate work directories — clean on success, preserve on failure.

Estimate storage per run at planning time. A single PromethION flowcell or one PacBio Revio SMRT cell each produce large outputs; budgeting one quarter at a time avoids surprise overruns.

### 13. Anti-patterns to avoid

- **Using a short-read aligner.** BWA or Bowtie2 on long reads produces fragmented, often nonsense alignments. Always use a long-read aligner.
- **Calling SVs with a short-read SV caller.** Manta, DELLY, and similar do not interpret long-read alignment patterns. Use Sniffles2, CuteSV, pbsv, or SVIM.
- **Discarding signal without a documented policy.** Re-basecalling next year is impossible if the signal is gone.
- **Mixing basecaller models within a cohort.** Re-basecall older samples with the current model, or analyze them as a separate stratum.
- **Treating long-read VCFs as drop-in replacements for short-read VCFs.** Annotation tools, population databases, and downstream filters often need adjustment.
- **Skipping phasing.** Long reads phase naturally; emitting only unphased outputs throws away one of the platform's main advantages.
- **Ignoring methylation when the basecaller produced it for free.** Even if the analysis does not need methylation today, propagating the modified-base BAM through the pipeline is cheap and the data is sometimes the answer to a future question.

### 14. The shape of the deliverable

A complete long-read genomics pipeline plan from this skill includes:

- The stage diagram from raw signal/unaligned BAM through to the final artifact set.
- The basecalling decision (model and modified bases) with rationale.
- The aligner and parameter preset choice.
- The variant-calling stack (small variants and SVs) with platform-specific models pinned.
- If applicable, the assembly path (assembler, polishing, phasing data source) and assembly QC plan.
- If applicable, the methylation path (caller, aggregation tool, DMR strategy).
- The QC thresholds and what happens to samples that fail.
- The provenance fields the pipeline records and how they reach the results bundle.
- The storage and lifecycle policy for each artifact class.

## Inputs

- The sequencing platform and chemistry/model details.
- The scientific goal — small variants, structural variants, methylation, assembly, or a combination.
- Sample design, cohort size, and any family or tumor-normal structure.
- Reference strategy (map, assemble, or pangenome).
- Hard constraints on GPU availability, storage budget, regulatory regime, or turn-around time.

## Outputs

- A module plan from raw signal to final artifacts.
- A basecalling and signal-retention decision.
- A variant-calling strategy covering small variants and SVs with phasing.
- Either an assembly path or a methylation path (or both) where in scope.
- QC metrics with explicit acceptance gates.

## Examples

**Example A — clinical ONT germline pipeline for rare disease.** A diagnostic lab is bringing up Oxford Nanopore for unsolved rare-disease cases. The plan is: POD5 retention for the lifetime of the case; SUP basecalling with 5mC modified-base calling on; minimap2 alignment to GRCh38 with the `map-ont` preset; Clair3 with the matching SUP model for small variants, phased; Sniffles2 for SVs filtered against a curated population SV catalog; modkit for methylation BED outputs phased by the variant-derived haplotypes. A per-case report includes per-sample QC, the variant table after filtering against gnomAD and ClinVar, the SV table after rare-SV filtering, and a methylation summary at known imprinted loci. The pipeline records basecaller model, reference build, and Clair3 model in the provenance bundle of every case.

**Example B — PacBio HiFi de novo assembly for a non-model plant genome.** A research group has Revio HiFi reads and Hi-C from a wild plant species. The plan is: HiFi unaligned BAM retained; hifiasm with Hi-C integration for haplotype-resolved primary and alternate assemblies; assembly QC via BUSCO (with the appropriate lineage), Merqyl k-mer evaluation, contig N50, and (where read coverage supports) a phasing-accuracy estimate. Polishing is skipped because HiFi base quality is sufficient; that decision is documented. The deliverable is a primary FASTA, an alternate FASTA, an assembly stats report, a BUSCO completeness report, and a small annotation pass for downstream comparative work.

**Example C — ONT methylation cohort for an epigenetics study.** Twenty PromethION samples across two tissue conditions. The plan is: SUP basecalling with 5mC and 5hmC modified-base models; minimap2 alignment to GRCh38; per-sample modkit-derived methylation BED at single-CpG resolution with read depth; a cohort-level DMR analysis using a long-read-aware tool; per-sample QC including coverage and CpG-call rate. Phasing is included for allele-specific methylation at a curated list of imprinted regions. Provenance records the basecaller model and the modified-base model identifier so the cohort remains internally consistent even if newer models are released mid-study.

## Limitations

- This skill does not pick the sequencing platform or coverage strategy; those decisions are upstream and wet-lab-driven.
- It does not generate executable pipeline code. Pair with the bioinformatics pipeline architect skill for the Nextflow or Snakemake scaffolding.
- Tooling for long-read analysis evolves quickly. The named tools reflect the current default set; verify currency at implementation time and substitute newer versions where their methodology is equivalent.
- Joint-cohort long-read analysis is younger than the per-sample case; the guidance here is conservative and may underuse newer joint methods where they are well-validated.
- Pangenome and graph-reference workflows are a fast-moving frontier; this skill treats them as a route but does not detail their internal sub-architecture.

## Sources reviewed

- https://github.com/nf-core/nanoseq (MIT)
- https://github.com/nf-core/methylong (MIT)
- https://github.com/epi2me-labs/wf-human-variation
- https://github.com/PacificBiosciences/HiFi-human-WGS-WDL
- https://github.com/PacificBiosciences/pbmm2
- https://github.com/PacificBiosciences/pbsv
- https://github.com/chhylp123/hifiasm (MIT)
- https://github.com/lh3/minimap2
