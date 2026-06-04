---
id: skillsgit-curated/bottom-up-proteomics-pipeline-architect
version: 1.0.0
name: Bottom-Up Proteomics Pipeline Architect
description: Plans an LC-MS/MS proteomics analysis pipeline from raw spectra to differentially abundant proteins — DDA versus DIA, identification, FDR control, quantification, normalization, batch handling.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: biotech
tags: [niche:proteomics-pipelines, mass-spectrometry, dda, dia, fdr, quantification, batch-effects, bioinformatics-pipelines]
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
  - proteomics pipeline
  - lc-ms/ms
  - mass spectrometry
  - dda proteomics
  - dia proteomics
  - label-free quantification
  - tmt isobaric
  - peptide identification
  - fdr control
  - protein quantification
  - openms
  - msstats
example_invocations:
  - "Plan a DIA proteomics pipeline for a 150-sample plasma cohort."
  - "We're switching from DDA-TMT to DIA — design the analysis side of that transition."
  - "How should I structure FDR control and quantification for an OpenMS-based pipeline?"
  - "Plan a label-free proteomics workflow including batch correction and differential analysis."
inputs:
  - name: acquisition_mode
    type: choice
    required: true
    description: The data acquisition strategy. Drives nearly every downstream choice.
    choices: [dda-lfq, dda-tmt, dda-itraq, dia-lfq, srm-prm, no-preference]
  - name: experimental_design
    type: text
    required: true
    description: Sample groups, conditions, replicates per condition, expected fold changes if known, any matched pairs or time series, randomization plan.
  - name: sample_type_and_prep
    type: text
    required: false
    description: Sample matrix (cells, tissue, plasma, secretome), digestion strategy (trypsin, LysC, multi-enzyme), and any enrichment (phosphopeptide, glycopeptide, ubiquitinated peptide).
  - name: instrument_and_throughput
    type: text
    required: false
    description: Instrument class (Orbitrap, timsTOF, Astral, Stellar), gradient length, samples per day, and total cohort size.
  - name: organism_and_database
    type: text
    required: false
    description: Target organism, FASTA database choice (UniProt reviewed, full, custom), inclusion of contaminants, and any variant or PTM database considerations.
outputs:
  - name: acquisition_plan_review
    type: markdown
    description: A sanity check on the acquisition mode versus the experimental question, and the implications for the analysis pipeline.
  - name: identification_module
    type: markdown
    description: Search engine choice, search parameters, FDR control strategy, and any rescoring step.
  - name: quantification_module
    type: markdown
    description: How peptide and protein abundances are computed for the chosen acquisition mode.
  - name: normalization_and_batch_plan
    type: markdown
    description: Normalization strategy, missing-value handling, and the approach to batch and run-order effects.
  - name: differential_and_reporting_plan
    type: markdown
    description: The statistical model for differential abundance, multiple-testing control, and the artifacts that reach the biologist.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

This skill produces methodology guidance for bioinformatics workflows. Outputs are not validated clinical or research conclusions and must be reviewed by qualified scientific staff before being acted upon. Pipelines built from this guidance must be wet-lab-validated and version-locked before any decisions are made on the results.

Use this skill when a team needs an analysis pipeline for bottom-up shotgun proteomics — LC-MS/MS of tryptic (or other protease) peptides — and the project is past the acquisition-mode choice or is choosing between DDA and DIA. Specifically:

- A core facility is consolidating per-project scripts into a managed proteomics pipeline.
- A lab is transitioning from DDA-TMT or DDA-LFQ to DIA and wants the analysis side planned.
- A group has dozens to hundreds of LC-MS runs and informal Excel-based quantification is no longer tenable.
- A clinical or biomarker study needs FDR control, normalization, and batch handling that will survive peer review.
- A multi-site study is harmonizing the proteomics analysis stack across labs.

This skill does not pick the protease, label chemistry, gradient, or instrument method — those are wet-lab and mass-spec method decisions. It does not cover top-down proteomics, intact protein measurements, native MS, or imaging mass spec. It focuses on the analysis pipeline from RAW/timsTOF native files (or open-format mzML) to a protein-by-condition table with statistics.

## How to apply

Work the steps in order. Proteomics analysis has more freedom at each step than sequencing analysis, and small choices in identification or normalization can swing the biological conclusion. Decide on purpose.

### 1. Pressure-test the acquisition mode against the question

Before pipelining, validate that the data-acquisition mode fits the question.

- **DDA-LFQ (label-free).** Maximum depth per sample, lower throughput, larger missing-value rate at protein level across runs. Pick when discovery depth matters and the cohort is small-to-moderate, or when label is undesirable.
- **DDA-isobaric (TMT, iTRAQ).** Up to 16-18 samples multiplexed per run; reduces missing values within a plex; introduces ratio compression and requires careful plex randomization. Pick for medium-sized cohorts where deep coverage and consistent quantification per plex are valuable.
- **DIA-LFQ.** Reproducible quantification across runs; lower missing-value rates at peptide level; supports very large cohorts. Pick for biomarker discovery, clinical cohorts, large case-control studies. The analysis stack is different from DDA — do not run a DIA cohort through a DDA pipeline.
- **SRM/PRM.** Targeted; the answer must be known up front. Out of scope for this discovery-oriented skill except as a follow-up confirmation step.

If the experimental question (large cohort, robust quantification) does not match the acquisition mode (DDA-LFQ with high missing-value rates), flag the mismatch in the plan. Pipelines cannot retroactively fix this.

### 2. Convert and standardize the input

Vendor RAW files (Thermo `.raw`, Bruker `.d` for timsTOF) are not the analysis input format. Standardize:

- Convert to mzML using ThermoRawFileParser, msconvert, or vendor-equivalents that emit the PSI standard.
- For Bruker timsTOF data, decide whether the pipeline operates on `.d` natively (some tools do) or on converted mzML; document the choice.
- Keep the raw vendor files until the project is complete and the results are accepted; reprocessing happens.
- Compute and record per-file checksums on conversion. Mass-spec runs accidentally lost or swapped have killed analyses.

The unified input set is a list of mzML (or `.d`) files with an experimental-design table that maps each file to a sample, condition, plex (for isobaric), replicate, and batch.

### 3. Build the experimental-design table as a contract

The experimental-design table is the API between the wet lab and the pipeline. Lock it.

Minimum columns: a stable `run_id` matching the file name, a `sample_id` (one biological sample can have multiple runs), a `condition` or `group`, a `replicate` index, a `batch` identifier (typically MS acquisition batch or sample-prep batch), and a `run_order` if the order matters for analysis. For isobaric labeling add `plex_id` and `channel`. For phosphoproteomics or PTM-enriched data add an `enrichment` column.

Validate strictly at run start. Reject duplicate run IDs. Reject files missing from disk. Reject plexes with missing channels. Run-order matters in MS; do not let it be implicit.

### 4. Pick the search engine and supporting tools

For DDA, several search engines are in routine production use; for DIA, the landscape is different and a dedicated library-free or spectral-library search engine is needed.

For **DDA**:

- Comet, MS-GF+, MSFragger (open-source variants exist), X!Tandem, and OMSSA all appear in MIT-or-similarly-permissive open frameworks. nf-core/quantms and ProteomicsLFQ-style pipelines wrap several of these.
- Tide-search and Crux are common in academic settings.
- Pair the search engine with a rescoring step — Percolator is the canonical choice — to improve discrimination at FDR thresholds.

For **DIA**:

- DIA-NN (note: now closed-source for newer versions; check license fit before adoption) and OpenSwathWorkflow plus PyProphet are common.
- Library-free DIA search has matured significantly; the analysis can build an in-silico predicted spectral library from the FASTA and use it directly, or build an empirical library from companion DDA runs.

Document the engine and version explicitly. Search results from different engines on the same data differ at the margin; that is expected, but the choice should not change quietly between cohorts.

### 5. Set the search parameters with intention

Parameters drift; lock them up front and reference them from a config rather than rebuilding by hand each project. The typical set:

- Precursor and fragment tolerances matched to the instrument class (ppm-level for Orbitrap and timsTOF).
- The protease and the maximum missed cleavages (commonly trypsin with 1-2 missed cleavages).
- Fixed modifications (commonly carbamidomethyl on Cys after IAA alkylation) and variable modifications (oxidized Met, acetyl on protein N-term; phospho on S/T/Y for phospho-enriched samples; ubiquitin remnant K-GG for ubiquitinomics).
- Target-decoy strategy: reverse decoy (or shuffled), generated from the same FASTA, and used by both the search engine and the FDR-controller.
- A contaminant FASTA (cRAP or equivalent) merged into the search database.

For isobaric labeling, declare the reagent (TMT-6, TMT-10, TMT-11, TMT-16, TMT-18, iTRAQ-4 or -8) and configure both the fixed modifications on K and N-term and the reporter ion extraction step.

### 6. Control the FDR rigorously

This is where biology gets contaminated by statistics. Standard practice:

- PSM-level FDR via target-decoy or Percolator (PEP), cut at 1%.
- Peptide-level FDR via grouping PSMs and re-controlling at 1%.
- Protein-level FDR via picked-protein, two-step, or other group-based FDR at 1%.
- Optionally a run-level FDR for very large cohorts where the union grows pathologically.

The exact strategy matters less than that it is documented and consistent across all samples in the cohort. Do not run FDR control per file and then naively union; the union FDR will be inflated.

For DIA, FDR control happens at the precursor and peptide-fragment level (often via PyProphet or DIA-NN's own controller). Protein FDR in DIA is computed differently from DDA; verify the chosen tool's approach.

### 7. Quantify deliberately for the acquisition mode

The quantification logic differs by mode:

- **DDA-LFQ.** MS1 feature intensities (MaxLFQ-style summarization is widely used) or spectral counting (lower fidelity, dated). MaxLFQ and similar minimize ratio bias across runs and are the default choice. Match-between-runs (MBR) can transfer identifications across runs but inflates missing-value imputation risk if used carelessly.
- **DDA-isobaric.** Reporter-ion intensities per channel per PSM, summarized to peptide and then protein. Apply isotope-impurity correction using the reagent lot certificate. Consider SPS-MS3 or FAIMS-aware quantification for ratio compression mitigation; document whichever path the method uses.
- **DIA-LFQ.** Peptide-fragment intensities summarized to peptide and then protein. Library-free analyses produce per-precursor quantities that summarize cleanly to peptide.

The output of this step is a peptide-by-sample quantity matrix and a protein-by-sample quantity matrix, with associated metadata (FDR, number of supporting peptides, number of unique peptides).

### 8. Handle missing values with a documented strategy

Missing values are unavoidable and the choice of strategy is consequential.

- **Filtering.** Drop peptides or proteins quantified in fewer than N samples per condition. Common cut-offs are "quantified in 50-70% of samples in at least one condition." Filtering is the strongest defense against imputation-driven false positives.
- **Imputation.** When imputing, distinguish missing-at-random (MAR) from missing-not-at-random (MNAR; below limit of detection). Use a mixed strategy: kNN or similar for MAR, left-shifted Gaussian or sample-minimum-derived imputation for MNAR. Document the split and the parameters.
- **No imputation paths.** Some statistical methods (msqrob2, certain mixed models) handle missingness directly without imputation. Where available these are preferable to imputation.

Whatever the strategy, run a sensitivity analysis on a small representative dataset to confirm that imputation is not driving the eventual significant hits.

### 9. Normalize before differential analysis

Normalization sits between quantification and statistics and is often the first place a pipeline goes wrong.

- **Median or sum normalization** per run is the simplest baseline.
- **VSN (variance stabilizing normalization)** or log-transform-then-median-center is common.
- **Cyclic loess** across paired runs catches non-linear systematic differences.
- **Internal reference scaling** for isobaric experiments uses a bridge channel across plexes and is essential when plexes themselves are the batch.

Inspect the result. Boxplots of intensity per sample after normalization should be substantially aligned; if they are not, the normalization is not doing its job and step ten will inherit the problem.

### 10. Address batch effects explicitly

For any cohort larger than one MS batch, batch effects are real. Approaches:

- **Randomization at acquisition time** is the cheapest defense and the most common omission. The wet-lab/MS team must spread conditions across batches and across run order; do not run all controls first and all cases later.
- **Statistical correction** with ComBat, limma's `removeBatchEffect`, or — preferably — including batch as a covariate in the differential model rather than removing it before testing. Removing batch effects first and then testing inflates degrees of freedom.
- **Bridge samples** in isobaric designs (a pooled reference in one channel of each plex) allow scaling across plexes and should be standard for any cohort spanning multiple plexes.

Document the batch and run-order structure, the test for its presence (PCA colored by batch is the visual standard), and the chosen correction.

### 11. Differential abundance with appropriate statistics

The final analytical step is condition contrasts. Choices:

- **MSstats** (BSD-3) handles DDA-LFQ, DDA-TMT, and DIA with appropriate models for each.
- **limma** with a moderated t-statistic on log-intensities works well for label-free cases and is widely used.
- **msqrob2** uses peptide-level mixed models and avoids the protein-summarization step's biases.
- **DEqMS** extends limma with PSM count as a precision weight; useful for DDA-TMT.

For multiple testing, control FDR with Benjamini-Hochberg unless the study design demands otherwise. Decide and document the significance and fold-change thresholds before looking at the data. The thresholds are part of the protocol, not the results.

Report effect sizes alongside p-values. Volcano plots and per-protein box plots for top hits go into the deliverable; a wall of p-values does not.

### 12. Enforce reproducibility on the analysis side

Proteomics pipelines suffer from the same provenance problems as sequencing pipelines:

- Pin the FASTA database including version date and the contaminant set.
- Pin the search engine, the rescoring tool, the quantification engine, and any statistical packages, all by container digest.
- Snapshot the experimental-design table per run.
- Record the parameter set including tolerances, modifications, and FDR thresholds.
- Capture the full output of the run including FDR-controlled IDs, intensity matrices, normalization choice, the statistical model fitted, and the resulting tables.

Treat search results as data. A new FASTA, a new modification list, or a new search engine version is a new dataset. Reanalysis is fine; reanalysis that pretends to be the original analysis is not.

### 13. Plan QC at run level and cohort level

Per-run QC:

- Total ion chromatogram and base peak intensity.
- Number of MS2 scans, identification rate, and number of peptide/protein identifications.
- Retention time stability across the cohort (drift indicates instrument or column issues).
- Per-channel reporter intensity distributions for isobaric experiments.

Cohort-level QC:

- PCA on the normalized intensity matrix, colored by condition and by batch. The dominant axes should reflect biology, not batch, after correction.
- Sample-sample correlation heatmap. Outliers stand out.
- Hierarchical clustering of samples; biological replicates should cluster.

Define quantitative thresholds for sample acceptance (for example, a minimum number of quantified proteins, or correlation above a floor with the bridge). Document what happens to samples that fail.

### 14. Specialized PTM workflows are a meaningful diff

Phospho, ubiquitin, and glyco enrichments share the bulk of the pipeline but diverge at search and downstream interpretation:

- The variable modification set differs (e.g., phospho on STY, GlyGly K).
- Site localization (Ascore, PTMProphet, PhosphoRS, or a tool's built-in localizer) is part of the identification stage. Report a localization score per site.
- Quantification operates on the modified peptide / site level, not just the protein. Site-level differential analysis requires its own normalization (relative to unmodified protein abundance where measured).
- Reference databases and downstream enrichment tools differ.

If a PTM workflow is in scope, design the search and the localization step deliberately. Generic protein-level pipelines miss the point.

### 15. Plan the human-facing deliverable

The pipeline output that scientists read is not the FDR-controlled peptide table. It is:

- A protein-level differential abundance table per contrast, with effect size, p-value, adjusted p-value, and the number of supporting peptides.
- For PTM workflows, a site-level table beside the protein table.
- QC plots (PCA, sample correlations, intensity distributions) that show whether the cohort is internally coherent.
- A methods paragraph that the eventual publication or report inherits, including software versions, FDR strategy, normalization choice, and statistical model.

Without these, the pipeline is technically complete and practically useless.

### 16. Anti-patterns to avoid

- **Running DIA data through a DDA pipeline (or vice versa).** The acquisition mode dictates the analysis stack.
- **Filtering on raw intensity rather than on quantified-in-N-samples.** Threshold-on-presence is the right filter; threshold-on-magnitude pre-empts the statistics.
- **Imputing then testing without sensitivity analysis.** Imputation-driven significance is the most common false discovery class in proteomics.
- **Removing batch effects before differential analysis.** Include batch as a covariate; do not bake it out and then pretend the degrees of freedom are unchanged.
- **Per-file FDR control unioned across runs.** Inflates the effective FDR.
- **Ignoring contaminants in the database.** Keratin and trypsin self-digestion contaminate every project; build them into the database so they are accounted for, not ignored.
- **No randomization at acquisition time.** Cannot be fixed in the analysis. Catch it before the cohort runs.

### 17. The final shape of the deliverable

A complete proteomics pipeline plan from this skill includes:

- The acquisition-mode-appropriate analysis stack from mzML conversion through search, FDR, quantification, and differential analysis.
- The experimental-design table schema and validation rules.
- The FDR strategy and the search parameters that are pinned per project.
- The normalization choice and the batch-handling approach.
- The differential-analysis model and the per-contrast reporting.
- The QC plots and acceptance thresholds.
- The provenance fields the pipeline records.

## Inputs

- The acquisition mode (DDA-LFQ, DDA-TMT, DDA-iTRAQ, DIA-LFQ, or targeted).
- The experimental design including conditions, replicates, batches, and any pairing.
- Sample matrix, prep details, and any PTM enrichment.
- Instrument class, throughput, and cohort size.
- Organism, database choice, and modification set.

## Outputs

- A sanity-checked acquisition-versus-question review.
- An identification module with search engine, parameters, and FDR strategy.
- A quantification module appropriate to the acquisition mode.
- A normalization and batch-handling plan.
- A differential analysis and reporting plan.

## Examples

**Example A — DIA-LFQ plasma biomarker cohort.** A 200-sample case-control plasma study on a timsTOF Pro with library-free DIA acquisition. The plan is: mzML conversion at ingest with checksums recorded; library-free DIA search against the human UniProt reviewed FASTA plus contaminants; PyProphet FDR control at peptide and protein level at 1%; protein-level quantification with MaxLFQ-style summarization; per-run median normalization; filter to proteins quantified in at least 60% of samples in either group; no imputation, msqrob2 handling missingness in a mixed model with batch as a covariate; BH-adjusted differential output with effect size and per-contrast volcano plots. Per-batch PCA confirms biology dominates after correction. Provenance records the search engine version, the FASTA snapshot date, and the analysis config commit.

**Example B — DDA-TMT immune signaling time-course.** A 32-sample TMT-16 study across two plexes with a bridge channel in both. The plan is: vendor RAW to mzML; MSFragger search with carbamidomethyl Cys fixed and TMT-16 on K and N-term fixed; oxidized Met variable; Percolator rescoring; FDR 1% at peptide and protein; reporter-ion extraction with isotope-impurity correction; bridge-channel scaling across plexes; log-transform and median-center per plex; differential analysis with MSstatsTMT including donor as a random effect; BH-adjusted output. Site-level extension is deferred because phospho enrichment is not in scope.

**Example C — DDA-LFQ phosphoproteomics on cancer cell lines.** A 24-sample TiO2-enriched phospho dataset on Orbitrap. The plan is: search with phospho-STY variable, MSFragger with PTM-Prophet for site localization; FDR 1% at peptide and PSM, site-level filtering at localization probability above 0.75; quantification at site level via MaxLFQ-style summarization on phosphopeptides only; normalization with cyclic loess; missing values filtered (no imputation) to sites quantified in 50% per condition; limma at site level with site count as precision weight; output is a site-level table with motif annotation and a kinase-substrate enrichment summary.

## Limitations

- This skill does not pick the wet-lab method (digestion, labeling, enrichment, instrument method). Method development sits upstream.
- It does not generate executable workflow code. Pair with the bioinformatics pipeline architect skill for the Nextflow or Snakemake scaffolding.
- Top-down proteomics, native MS, and intact protein workflows are out of scope.
- Imaging mass spectrometry and spatial proteomics share concepts but have distinct pipelines not covered here.
- DIA tooling is moving quickly; named tools reflect current defaults and should be re-validated at implementation time.

## Sources reviewed

- https://github.com/nf-core/quantms (MIT)
- https://github.com/nf-core/proteomicslfq (MIT)
- https://github.com/nf-core/mhcquant (MIT)
- https://github.com/OpenMS/OpenMS (BSD-3-Clause)
- https://github.com/bigbio/quantms (MIT)
- https://github.com/percolator/percolator
- https://github.com/Nesvilab/MSFragger
