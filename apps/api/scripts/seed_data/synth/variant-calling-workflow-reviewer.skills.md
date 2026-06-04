---
id: skillsgit-curated/variant-calling-workflow-reviewer
version: 1.0.0
name: Variant Calling Workflow Reviewer
description: Audits a DNA variant-calling workflow end to end — QC gates, alignment, caller choice, joint calling, filtering thresholds, annotation, and validation cohort — and returns a prioritized list of changes before results are trusted.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: biotech
tags: [niche:bioinformatics-pipelines, variant-calling, gatk, dna-seq, joint-calling, vep, germline, somatic]
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
  - variant calling
  - gatk haplotypecaller
  - mutect2
  - joint calling
  - vqsr
  - hard filtering
  - vep annotation
  - tumor normal
  - germline variants
  - somatic variants
  - sarek
  - dna-seq pipeline
example_invocations:
  - "Review our germline exome variant-calling pipeline before we run it on 500 samples."
  - "We are seeing too many low-frequency variants — is our filtering wrong?"
  - "Audit our tumor/normal Mutect2 setup against current best practices."
  - "Why do our VCFs look different between two cohorts that should be comparable?"
inputs:
  - name: workflow_description
    type: text
    required: true
    description: The workflow as it stands — tools and versions at each step (trimming, alignment, dedup, BQSR, calling, joint calling or panel of normals, filtering, annotation), the reference genome build, and intervals or capture target.
  - name: study_design
    type: text
    required: true
    description: Germline or somatic, single-sample or cohort, tumor/normal/relapse, trio/pedigree, population. Sample count, sequencing modality (WGS, WES, targeted panel), expected coverage, and read length.
  - name: known_issues
    type: text
    required: false
    description: Symptoms the team has already noticed — high false-positive rate, missing known variants, Ts/Tv ratio off, low concordance with an orthogonal assay, runs failing on specific samples.
  - name: validation_data
    type: text
    required: false
    description: Any reference truth set available — GIAB samples, internal Sanger-confirmed variants, an array-based comparison, replicate samples.
  - name: downstream_use
    type: text
    required: false
    description: How outputs are consumed — research-only, clinical research, IRB-bound, regulated. Affects how strict the audit must be.
outputs:
  - name: audit_findings
    type: markdown
    description: A prioritized list of findings, each labeled critical, major, or minor, with the specific risk and the recommended fix.
  - name: qc_gate_map
    type: markdown
    description: The QC gates that should sit between each pipeline stage and what each gate should accept or reject.
  - name: filtering_recipe
    type: markdown
    description: A concrete filtering recipe appropriate to the study design — VQSR or hard filters for germline, Mutect2 filtering for somatic — with thresholds and rationale.
  - name: validation_plan
    type: markdown
    description: How to demonstrate the workflow is calling correctly — truth-set evaluation, replicate concordance, orthogonal validation, and a pass/fail criterion.
  - name: open_questions
    type: markdown
    description: Decisions the team has not made yet that block a clean audit, with the trade-offs of each option.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

This skill produces methodology guidance for bioinformatics workflows. Outputs are not validated clinical or research conclusions and must be reviewed by qualified scientific staff before being acted upon. Pipelines built from this guidance must be wet-lab-validated and version-locked before any decisions are made on the results.

Use this skill when a DNA variant-calling workflow needs an outside read before its outputs are trusted. Specifically:

- A new pipeline is built and about to run on a real cohort.
- An existing pipeline is producing results that look off — Ts/Tv ratio drifting, novel-variant rate climbing, concordance with an orthogonal assay slipping.
- A team is switching reference builds, callers, or capture kits and wants a sanity check.
- A new analyst inherited a workflow and needs an outside opinion before signing their name on results.
- A consortium or sponsor requires a documented audit of the calling pipeline.

Do not use this skill to design a pipeline from scratch — pair it with the bioinformatics pipeline architect. Do not use it to interpret specific variants biologically; that is downstream of the calling and filtering this skill audits.

## How to apply

Walk the workflow stage by stage, top to bottom. Most variant-calling problems are upstream of the caller: poor QC, wrong intervals, missed dedup, miscalibrated BQSR. The caller usually gets blamed for noise it inherited.

### 1. Reconstruct the workflow as a stage map

Before judging anything, redraw what the workflow actually does. List every tool in order with its version and the relevant parameters. A typical germline short-variant workflow looks roughly like:

1. Raw read QC (FastQC or fastp report).
2. Adapter and quality trimming (fastp, Trim Galore).
3. Alignment to the reference (BWA-MEM, BWA-MEM2, DRAGMAP, or minimap2 for long reads).
4. Sort and index (samtools).
5. Mark duplicates (Picard MarkDuplicates, GATK MarkDuplicatesSpark, or sambamba).
6. Base quality score recalibration (GATK BQSR) — optional but conventional.
7. Per-sample calling (GATK HaplotypeCaller in GVCF mode, DeepVariant, Strelka, or freebayes).
8. Joint genotyping across the cohort (GATK GenotypeGVCFs, or GLnexus for DeepVariant).
9. Variant filtering (VQSR if cohort and platform are appropriate; hard filters otherwise).
10. Normalization and decomposition (bcftools norm).
11. Annotation (VEP, SnpEff, or both, with appropriate caches).
12. Downstream filtering and reporting.

A somatic short-variant workflow swaps caller (Mutect2, Strelka2-Somatic, DeepSomatic, Varlociraptor) and adds a panel of normals plus contamination and orientation-bias filtering. Structural variants (Manta, DELLY, TIDDIT) and copy-number callers (CNVkit, Control-FREEC, ASCAT) sit alongside.

Once stages are listed, the audit asks of each stage: is the right tool used, are the parameters right for this study, and is the handoff to the next stage clean?

### 2. Audit the inputs and intervals

Trace what is actually being called against. Errors at this stage are common and ruinous.

- Reference genome build: confirm one build is used end to end. GRCh38 and GRCh37 cannot be mixed. Within GRCh38, "with alt contigs," "no-alt," and "primary assembly" make a real difference in some tools.
- Interval list: for WES and panels, the calling interval must match the capture kit's targets plus a small padding (commonly 100 bp). Calling genome-wide with WES data wastes compute and creates spurious off-target noise; calling only the design intervals misses genuine variants in padding.
- Decoy sequences: GRCh38 ships with decoys for a reason. Confirm they are included.
- Sample sex handling: chrY and the X PARs deserve explicit handling, especially for joint calling.
- Mitochondrial DNA: typically called separately with a ploidy of 1 (Mutect2 in mitochondria mode is a common pattern). Confirm it is not silently dropped or called as diploid.

### 3. Audit pre-alignment QC

Look at fastp or FastQC outputs across samples. Flag:

- Per-base quality dropping early (suggests sequencer or chemistry issue).
- Adapter content remaining after trimming.
- Duplication estimates wildly out of line with peers in the cohort.
- Overrepresented sequences pointing to rRNA contamination (a problem for RNA-derived DNA libraries) or sample-swap-style cross-contamination.
- Read-length and insert-size distributions that disagree with the protocol.

Trimming should remove adapters and very low-quality bases; aggressive quality trimming distorts BQSR and is rarely worth it.

### 4. Audit alignment and duplicate marking

Alignment is mostly mechanical, but a few things still go wrong:

- Read group tags. Each library must have a correct, unique RG, with `ID`, `SM`, `LB`, `PL`, and `PU` set. Joint calling depends on it. Tools silently misbehave when read groups collide.
- Mark-duplicates strategy. For multi-lane libraries, the merge-then-mark order matters; PCR duplicates and optical duplicates should be marked across all lanes of a library.
- For tumor samples, the duplication rate is often higher; investigate libraries whose rate exceeds peers by more than a few percentage points.
- For UMI-based libraries, MarkDuplicates is wrong — consumer-grade dedup using UMI consensus (fgbio, UMI-tools, Picard UmiAwareMarkDuplicatesWithMateCigar) is required.

### 5. Decide on BQSR and audit it if used

GATK BQSR adjusts base qualities against known-variant sites. It helps with older platforms and capture data; the marginal benefit on modern WGS with high-quality chemistries is smaller than it once was. Independent of preference, audit:

- A known-sites bundle matching the reference build and including dbSNP plus the Mills/1000G indel set (or equivalent jurisdiction-appropriate resources).
- That recalibration tables are computed per sample (or per library) and applied to the correct BAM.
- No re-recalibration loops. BQSR runs once on the merged-library BAM.

If BQSR is skipped, document the choice and confirm the chosen caller tolerates uncalibrated qualities (DeepVariant is largely robust; HaplotypeCaller is somewhat more sensitive to it).

### 6. Audit the caller and its parameters

For germline:

- HaplotypeCaller in GVCF mode is the dominant pattern for joint-callable cohorts. Confirm GVCFs are produced per sample with `-ERC GVCF`.
- DeepVariant has become a strong default for accuracy on Illumina data, with model selection (WGS, WES, PacBio, ONT) matching the platform.
- Confirm the caller is given the same intervals as the rest of the pipeline. Mismatches here silently truncate the call set.
- For sex chromosomes, the ploidy hint should be set per sample.

For somatic:

- Mutect2 in tumor-normal mode requires both BAMs, a germline-resource VCF (gnomAD-derived) for prior probabilities, and a panel of normals (PoN) appropriate to the sequencing technology and pipeline. Reusing somebody else's PoN built on different chemistry is a common source of poor calls.
- Tumor-only mode is permissible when no matched normal exists, but the PoN becomes load-bearing and contamination estimation becomes harder.
- Run GetPileupSummaries plus CalculateContamination, and FilterMutectCalls with the contamination table and the read-orientation model artifacts from LearnReadOrientationModel. Skipping any of these is a finding.

For structural variants and CNV, confirm callers appropriate to the data depth (Manta and DELLY for SVs, CNVkit or Control-FREEC for tumor/normal CNVs, ASCAT for allele-specific tumor CNVs) and that their reference and interval inputs match the small-variant pipeline.

### 7. Audit joint calling

If samples are joint-called:

- All samples must use the same reference, intervals, and calling parameters. Mixing a sample called against a different reference is a finding.
- For HaplotypeCaller GVCFs, GenomicsDBImport (or CombineGVCFs for small cohorts) plus GenotypeGVCFs is the convention. Verify the cohort manifest used.
- For DeepVariant outputs, GLnexus is the typical joint caller.
- Watch for sample-name collisions in the GVCFs (a downstream consequence of the read-group hygiene above).
- For very large cohorts, joint calling is sharded by interval; verify the recombination step concatenates correctly and that no intervals were silently dropped.

### 8. Audit filtering

This is where pipelines diverge from "passable" to "trustable." Filtering is study-dependent; specify the recipe.

Germline:

- VQSR (Variant Quality Score Recalibration) is appropriate for cohorts on the order of 30+ exomes or 1+ WGS, with separate models for SNPs and indels. It requires training resources (HapMap, omni, 1000G, Mills). Confirm tranches are picked deliberately (commonly 99.7% for SNPs, 99.0% for indels).
- For small cohorts, GATK hard filters are the documented alternative — QualByDepth, FisherStrand, StrandOddsRatio, RMSMappingQuality, MappingQualityRankSumTest, ReadPosRankSumTest — with thresholds applied separately to SNPs and indels.
- Normalize and left-align with `bcftools norm -m- -f reference.fa` before downstream comparisons. Failure to normalize creates phantom non-concordance.

Somatic Mutect2:

- Apply FilterMutectCalls with contamination and orientation-bias models attached.
- Consider further filtering for sample-specific artifacts: tumor-in-normal contamination, mapping-quality outliers, repeat regions.
- For panels with shallow normals, raise vigilance on novel and recurrent-site artifacts; an internal blacklist of recurrent site-specific artifacts is common and warranted.

In all cases, the filter step should set FILTER tags rather than dropping variants; downstream consumers choose what to drop.

### 9. Audit annotation

VEP and SnpEff are the dominant annotators. Audit:

- The annotation cache version matches the reference build and is recent enough for the study's purposes (gene definitions and clinical resources update frequently).
- Population frequencies attached (gnomAD genomes and exomes for human cohorts) match the reference build.
- Pick a single canonical transcript convention (`--pick` in VEP, or MANE Select) and apply it consistently. Mixing canonical and all-transcript outputs across cohorts will look like biology when it is reporting.
- Clinical resources (ClinVar) carry version metadata; record what version was used.
- For tumor work, COSMIC or equivalent oncogene resources may be relevant; check licensing for any non-permissive resource.

### 10. Establish a validation cohort

Before trusting the workflow, demand evidence. The audit should always recommend a validation pass.

- Run a Genome in a Bottle (GIAB) reference sample through the pipeline and compare against the truth set using a tool such as hap.py or rtg-tools `vcfeval`. Report sensitivity and precision separately for SNPs and indels, and within the high-confidence regions provided with the truth set.
- If GIAB is not directly applicable (non-human, unusual capture kit), define an internal truth set — replicates with high concordance, prior orthogonal-assay variants, family trios with Mendelian-error analysis.
- Acceptance thresholds depend on study. Research projects commonly accept SNP precision and recall above 0.99 and indel above 0.95 inside high-confidence regions; clinical research typically tightens this further.
- Record the validation run with the same provenance discipline as production runs.

### 11. Plan recurring quality checks for production

Even a validated pipeline drifts. Recommend ongoing checks:

- Per-sample Ts/Tv ratio (germline SNPs commonly around 2.0–2.1 for WGS and 3.0–3.3 for exomes against canonical transcripts; significant drift is a flag).
- Het/Hom ratio and novel-variant rate in dbSNP.
- Sex-chromosome calling sanity check (sex inferred from genotypes should match metadata).
- Sample-swap detection via genotype concordance with prior runs of the same individual, or via genotype fingerprints.
- Periodic re-run of the GIAB sample as a sentinel; a drop in performance flags drift before scientists notice.

### 12. Score and prioritize findings

Group the audit findings into:

- **Critical.** Block release of results until fixed. Example: joint call combining samples called against different references; missing duplicate marking; PoN built on different chemistry; no filtering applied.
- **Major.** Should be fixed before the next cohort; results may need re-analysis. Example: BQSR with a wrong known-sites bundle; VEP cache mismatched to reference; missing FilterMutectCalls steps; no normalization before downstream use.
- **Minor.** Improve next iteration. Example: an out-of-date but functioning tool version; a non-canonical annotation choice; missing per-run Ts/Tv reporting.

Present them with the specific risk and the specific remediation. The lab decides what to fix when; the audit makes the trade-offs visible.

### 13. Spot the recurring upstream causes of "the caller is broken"

Many calls to audit a pipeline begin with "the caller is giving us nonsense." In the great majority of these, the caller is fine; something upstream is wrong. Patterns to look for:

- **Cohort drift.** Samples from a new sequencing run mixed with samples from a year ago. Even with the same kit, chemistry batches differ; joint calling will compress the difference into apparent variation. Recommend per-batch QC comparisons and, when batch effects are real, batch-aware joint calling or stratified analysis.
- **Contaminated normals.** A "normal" sample with hidden tumor contamination tanks somatic calling by allele frequency. Use CalculateContamination on the normal as well, and look for an unexpectedly high contamination fraction.
- **Reference padding mismatches.** Capture-kit BED files come in two flavors — design targets and probe regions. Calling on probes-only may miss variants near the edges; calling on design plus padding catches them. Verify which is in use.
- **Decoy and alt contigs.** Reads aligning to alt contigs in GRCh38-with-alt scenarios behave differently from reads aligning to the primary assembly. Many calling pipelines assume primary-only; alt-aware processing is a deliberate choice.
- **Sex-chromosome surprises.** A male sample called as diploid on chrX accumulates heterozygous calls that are not biologically real. Configure per-sample ploidy.

The audit should explicitly check for each of these before concluding the caller needs replacing.

### 14. Document the audit and the close-out criteria

The audit is incomplete until findings have a destination. For each finding, capture:

- The finding statement (what is wrong, in concrete terms).
- The risk (what happens scientifically if it stays unfixed).
- The remediation (the specific change to the workflow).
- The verification (how the team will confirm the fix worked — often a re-run on a small cohort with documented expectations).
- An owner and a target date.

The audit's value comes from the close-out, not the finding. Pipelines that get audited and never re-audited drift back to where they were. Recommend a re-audit cadence — annual, on major version bumps of GATK or VEP, or after any chemistry or reference change.

### 15. Establish the change-control discipline

A validated variant-calling pipeline is fragile. Small, well-intentioned changes break it in subtle ways. Recommend a change-control protocol:

- All pipeline changes go through code review.
- Reference-data updates are version-bumped explicitly, never in place.
- A regression check (the GIAB-or-equivalent sentinel) runs on every release candidate and the result is documented before deploy.
- The team distinguishes "validated for cohort X" from "validated in general." A pipeline that works on exomes may need re-validation for whole genomes; the audit should call this out.

## Inputs

- A stage-by-stage description of the existing workflow with versions and parameters.
- The study design — germline/somatic, cohort size, sequencing modality, expected coverage.
- Known symptoms or concerns.
- Any available truth or orthogonal data for validation.
- The intended downstream use of the calls.

## Outputs

- A prioritized findings list with severity and remediation.
- The QC gates that belong between stages and what they accept.
- A concrete filtering recipe tied to the study design.
- A validation plan with explicit pass/fail criteria.
- The open decisions the team has not made yet.

## Examples

**Example A — germline exome cohort, 300 samples.** Findings include: VQSR appropriate at this scale, but the team had hard filters applied — recommend switching, with documented tranches. The interval list was the kit's design region with no padding; recommend 100 bp padding. BQSR known-sites mixed dbSNP build 151 with reference GRCh38-with-alt; recommend rebuilding the bundle on the no-alt primary. Validation: GIAB HG002 exome through the same pipeline with hap.py against v4.2.1 truth, with SNP precision and recall thresholds set before the run.

**Example B — tumor/normal Mutect2 workflow, 80 cases.** Findings include a critical gap that LearnReadOrientationModel was not in the workflow and FilterMutectCalls was run without orientation-bias artifacts — recommend addition immediately and a re-run of prior cases. The panel of normals was inherited from a previous chemistry; recommend rebuilding from this study's normals. Annotation was VEP with `--pick` but with the cache one major version behind the current ClinVar; recommend a cache upgrade and re-annotation pass with both versions recorded.

**Example C — small WGS pilot, 8 samples.** Findings include that joint calling is being attempted on too few samples to support VQSR. Recommend hard filters with the documented GATK thresholds, and defer to joint calling with VQSR until the cohort grows to the appropriate scale. Add a GIAB control sample to every batch as a sentinel. Document that with this cohort size, validation is best framed as a sanity check against GIAB and a replicate concordance test, not a population-genetics analysis.

## Limitations

- This audit is structural, not biological. It cannot tell whether a specific variant is real; it can tell whether the workflow is set up to find variants reliably.
- Long-read variant calling (PacBio HiFi, Oxford Nanopore) and graph-based calling have different conventions; the framework here applies, but the tool-level audit needs a long-read or graph-specific pass.
- Somatic structural-variant and CNV calling have idiosyncratic tool combinations; this skill identifies the categories of audit but does not exhaustively cover every caller.
- Clinical use requires documented validation, accreditation, and regulatory scrutiny far beyond what a methodology audit provides. Use this skill as a pre-validation review, not a substitute for it.

## Sources reviewed

- https://github.com/nf-core/sarek
- https://github.com/broadinstitute/gatk
- https://github.com/snakemake-workflows/dna-seq-gatk-variant-calling
- https://github.com/snakemake-workflows/dna-seq-varlociraptor
- https://github.com/nextflow-io/nextflow
- https://github.com/snakemake/snakemake
