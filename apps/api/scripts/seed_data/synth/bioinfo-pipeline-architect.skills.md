---
id: skillsgit-curated/bioinfo-pipeline-architect
version: 1.0.0
name: Bioinformatics Pipeline Architect
description: Designs a reproducible bioinformatics workflow — containerized tools, parameterized samples, intermediate caching, resource profiles, retries, and provenance — so analyses run the same way on a laptop, an HPC cluster, and the cloud.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: biotech
tags: [niche:bioinformatics-pipelines, nextflow, snakemake, reproducibility, containers, hpc, provenance, workflow-management]
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
  estimated_tokens_per_invocation: 8500
trigger_keywords:
  - bioinformatics pipeline
  - nextflow pipeline
  - snakemake workflow
  - reproducible analysis
  - workflow management
  - containerized pipeline
  - hpc bioinformatics
  - sample sheet
  - resource profiles
  - pipeline provenance
  - nf-core
  - workflow design
example_invocations:
  - "Design a Nextflow pipeline for our sequencing core that runs on Slurm and AWS Batch."
  - "We have shell scripts gluing FastQC, BWA, and GATK together — turn this into a real pipeline."
  - "How should we structure a Snakemake workflow so different cohorts can re-run it without code changes?"
  - "Plan resource profiles and retries for a variant-calling pipeline that processes 2,000 exomes."
inputs:
  - name: analysis_intent
    type: text
    required: true
    description: What the pipeline is supposed to do scientifically — the input data type (WGS, WES, bulk RNA-seq, scRNA-seq, ChIP-seq, methylation, etc.), the target output (VCF, count matrix, peaks, methylation report), and the downstream consumer.
  - name: scale_and_environment
    type: text
    required: false
    description: Expected sample throughput per run, typical input file sizes, and the execution environment (laptop, on-prem Slurm or SGE, AWS Batch, Google Batch, Kubernetes, hybrid).
  - name: existing_assets
    type: text
    required: false
    description: Any existing scripts, modules, containers, reference bundles, or partial pipelines the team already has. Drives whether to wrap, port, or rebuild.
  - name: workflow_engine
    type: choice
    required: false
    description: Preferred workflow engine, if the team has already chosen one. Default — recommend based on context.
    choices: [nextflow, snakemake, wdl-cromwell, no-preference]
  - name: constraints
    type: text
    required: false
    description: Hard constraints — air-gapped HPC, no Docker (Singularity only), regulated data residency, restricted egress, fixed reference genome build, license-bound tools.
outputs:
  - name: pipeline_architecture
    type: markdown
    description: The top-level design — modules, the dataflow graph, where intermediate files land, container strategy, and parameter surface.
  - name: sample_sheet_contract
    type: markdown
    description: The schema for the sample sheet that drives the pipeline, validation rules, and how multi-lane or multi-run samples are merged.
  - name: resource_and_retry_profile
    type: markdown
    description: Per-process resource requests, retry policies with escalating memory, and the execution profile mapping for each target environment.
  - name: provenance_plan
    type: markdown
    description: How the run records its inputs, tool versions, container digests, parameters, and outputs so any result can be traced back to the exact run that produced it.
  - name: handoff_checklist
    type: markdown
    description: What must be true before the pipeline is considered shippable to the wider lab or production environment.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

This skill produces methodology guidance for bioinformatics workflows. Outputs are not validated clinical or research conclusions and must be reviewed by qualified scientific staff before being acted upon. Pipelines built from this guidance must be wet-lab-validated and version-locked before any decisions are made on the results.

Use this skill when a team needs to take an analysis from "a folder of scripts that worked on one machine" to a reproducible pipeline other people and other environments can run. Specifically:

- A sequencing core or bioinformatics group is consolidating ad hoc shell scripts into a managed workflow.
- A lab is moving from interactive analysis on a workstation to batch execution on HPC or cloud.
- An organization is adopting Nextflow, Snakemake, or WDL and wants the first pipeline laid out correctly.
- A multi-site collaboration needs the same pipeline to run identically across institutions.
- A team is preparing a pipeline for audit, publication, or regulated use and needs explicit provenance.

Do not use this skill to choose between alignment tools, callers, or biological methods — those choices live in the methodology-specific skills (variant calling, RNA-seq, single cell). This skill answers "how do we structure the pipeline" not "what should the pipeline scientifically do." Pair with the relevant analysis-planner skill for the science.

## How to apply

Work the steps in order. Architecture decisions are sticky; making them deliberately at the start prevents the all-too-common rewrite eighteen months in.

### 1. Pin down the analysis contract

Before drawing any boxes, name the inputs and the outputs as precisely as possible. The inputs are not "FASTQ files." They are paired-end Illumina reads, single-cell, with a known chemistry, from a sample sheet that includes pool, lane, library, and biological identifiers. The outputs are not "results." They are a normalized count matrix per sample with a specific row and column convention, or a joint-called VCF normalized against a specific reference and decomposed in a specific way, plus a QC report whose recipients have specific questions.

Write the contract as a small document with: input file types and their metadata, the sample sheet schema, the reference genome and annotation versions, the produced artifacts and where they go, and the QC outputs that a human will read. The pipeline exists to honor this contract. Every later decision is in service of it.

### 2. Choose the workflow engine, briefly

If the team has a preference, take it. If not, the choice is largely between Nextflow and Snakemake, with WDL+Cromwell a third option common in clinical and consortium settings.

- Nextflow uses a dataflow channel model and a Groovy-flavored DSL. It dominates the multi-pipeline community space (nf-core) and has first-class executors for HPC, AWS Batch, Google Batch, and Kubernetes. Pick it when you want to plug into existing nf-core modules, when execution targets are heterogeneous, or when the team is comfortable with a domain DSL.
- Snakemake uses Python and a rule-based, file-driven model. Pick it when the team is Python-fluent, when the analysis is more bespoke than community, and when the dataflow is naturally expressed as "this file depends on those files."
- WDL+Cromwell is verbose but well-suited to consortium standards (GA4GH, GATK reference workflows). Pick it when you must align with one of those ecosystems.

Do not relitigate this choice every quarter. Commit, write down why, and move on. The shape of the pipeline matters more than the engine.

### 3. Decompose the analysis into modules

Sketch the dataflow as a directed acyclic graph (DAG) of processing modules. A module is a unit that takes typed inputs and produces typed outputs and is independently testable. Typical primary modules across sequencing-based pipelines include:

- Input validation (sample sheet, FASTQ integrity, reference compatibility).
- Pre-alignment QC (FastQC, fastp/Trim Galore, optional contamination screen).
- Alignment or pseudoalignment (BWA-MEM, STAR, HISAT2, Salmon, Kallisto, minimap2, Bowtie2).
- Post-alignment processing (sort, mark duplicates, BQSR or equivalent).
- The scientific step (variant calling, quantification, peak calling, methylation calling).
- Annotation and filtering.
- Per-sample QC aggregation and multi-sample QC (MultiQC).
- Reporting and export.

Each module should be replaceable. If you are using STAR today and a future cohort needs HISAT2, swapping one module should not ripple through the rest.

### 4. Design the sample sheet contract

Most pipelines fail in production not because of the science but because the sample sheet drifted. Lock its schema up front and treat it like an API.

Recommended columns at minimum: a stable `sample` identifier (biological), an optional `library` identifier (technical, for samples sequenced multiple times), `lane`, paired `fastq_1` and `fastq_2` paths (or a URI scheme that resolves consistently across environments), and a `condition` or `group` field where biologically meaningful. For tumor/normal designs add a `match` column and a `status` column. For time-course or longitudinal designs add `subject` and `timepoint`.

Validate at run start with a real schema check, not a typo-prone shell parser. Fail loudly and early. Reject duplicate rows. Reject paths that don't exist. Reject unknown reference identifiers. The pipeline should never start a six-hour alignment job to discover at step three that two samples have the same name.

Specify the merge rule for multi-lane samples explicitly: merge before alignment, merge after, or both depending on tool. Document it. Do not let the merge be implicit.

### 5. Containerize every tool

Pin every tool to a container image with a digest, not a tag. Tags float, digests do not. The pipeline must record which digest ran. Prefer official BioContainers or community-built nf-core/Snakemake-Workflows images; build only when necessary and store internally with the same versioning discipline.

Separate runtime containers from data. The reference genome, annotation files, and indexes are not inside the container; they are mounted or fetched at runtime, with their own version pinning recorded next to the container digest. This lets a single image serve many cohorts and lets reference updates be tracked independently.

Pick one container runtime per environment and document it: Docker on cloud, Singularity or Apptainer on HPC, often both. Engines like Nextflow handle this translation; verify your tool images work in both modes if you cross environments.

### 6. Decide the intermediate-file strategy

Bioinformatics pipelines produce enormous intermediates — BAMs, sorted BAMs, dedup BAMs, BQSR BAMs, on and on. The cost discipline is to keep what is durable and recomputable cheaply, and to publish what scientists will actually look at.

A workable model has three tiers:

- A scratch tier where the engine stages work directories. Tools write here. The engine cleans up on success unless told otherwise.
- A results tier (`results/` in Nextflow, an explicit output rule in Snakemake) where named, durable outputs land — final BAMs (or CRAMs), final VCFs, count matrices, QC reports.
- An archive tier where long-term storage lives, often a cheaper cloud class or a dedicated archival filesystem. The pipeline writes; lifecycle policy moves.

Use CRAM with reference compression for long-term alignment storage where the tools support it. Aim for write-once, read-many publishing; do not stomp on prior outputs of the same sample without an explicit re-run.

### 7. Set resource profiles, with retries that escalate

The dirtiest secret of bioinformatics is that resource estimation is hard and variable. A 30x exome and a 120x exome both call themselves "exomes," and the second eats four times the memory. Plan for it.

For each process, set:

- A baseline `cpus`, `memory`, and `time` request that covers the median sample. Err slightly high; queue waits cost less than failed reruns.
- A retry policy with escalating memory on the documented out-of-memory exit codes. Nextflow processes commonly retry with `task.memory * task.attempt`; Snakemake rules can specify `mem_mb=lambda wildcards, attempt: ...`. Two retries is usually enough.
- A maximum cap so a runaway process does not bring the cluster down.

Express these in a profile system: one profile per environment (`laptop`, `slurm_internal`, `aws_batch`, `gcp_batch`, `kubernetes`). The pipeline body should be environment-agnostic. The profile picks the executor, queues, and resource limits. Reviewers can read the profile and immediately see whether the run will fit the cluster.

### 8. Build the provenance layer

If a result cannot be traced back to the exact run that produced it, treat it as untrusted. Every run should record:

- The pipeline version (Git commit, ideally a tagged release).
- The container digests of each tool that executed.
- The reference and annotation versions, with their checksums.
- The full parameter set, in resolved form (not "default" — the actual value).
- The sample sheet content, snapshotted.
- The runtime environment (engine version, executor, instance types).
- The exit status, duration, and resource usage of each task.

Nextflow's report, timeline, trace, and DAG outputs cover most of this; Snakemake's `--report` and per-rule benchmarks do similarly. Publish all of these alongside the results, not just on the run server.

A useful test: a colleague should be able to take the provenance bundle, recreate the inputs, and reproduce the outputs bit-for-bit (or where tools are nondeterministic, scientifically equivalent within documented tolerance). If they cannot, the provenance is incomplete.

### 9. Add quality control as a first-class output

QC is not an afterthought; it is the artifact biologists read first. Wire it in:

- Run FastQC or fastp on raw reads. Capture failures.
- Capture alignment QC — duplication rate, insert size distribution, coverage, on-target percentage for capture experiments, ribosomal/mitochondrial content for RNA-seq.
- Aggregate everything with MultiQC into a single report per run.
- Define explicit thresholds for sample-level pass/fail (for example, a minimum mapped-read count, a maximum duplication rate, a minimum mean coverage). Mark samples that fail; do not silently include them in joint calls or differential analysis.

The pipeline should expose a clean "samples-passing-QC" list as a downstream input. Anything that consumes pipeline outputs reads this list, not the raw output directory.

### 10. Plan testing at three levels

- **Unit-style tests** for any custom scripts, especially anything that munges sample-sheet or VCF/MAF/AnnData structure. Run these in CI on every commit.
- **Stub-mode pipeline tests** that exercise the DAG end-to-end with no real computation, just process stubs that produce empty outputs. Nextflow supports `-stub-run`; Snakemake supports `--dry-run` and `--touch`. These catch wiring bugs in seconds.
- **Small-data integration tests** that run the full pipeline on a tiny dataset (a few thousand reads, a small genomic region) on every release. nf-core test profiles and Snakemake's test data conventions are good models. Aim for under twenty minutes wall time so it fits in CI.

Add a yearly or per-release "golden cohort" test: a small known dataset (often GIAB samples for variant calling) where outputs are compared against a frozen reference. Drift here flags a regression before scientists notice.

### 11. Decide how the pipeline gets parameters

Three common patterns, in order of preference:

- A versioned config file checked into the repository for each cohort or experiment, with the run command pointing at it.
- Command-line overrides on top of a default config, used sparingly.
- Environment variables, used only for things that genuinely belong to the environment (credentials, scratch paths).

Avoid the anti-pattern of long command lines repeated by hand. The cohort config is documentation; the command line is not.

### 12. Plan the human side — versioning and release

Treat the pipeline like software. Tag releases. Write a changelog. Note which reference and tool versions ship with which pipeline version. Lock the combination — version 1.4 of the pipeline ships with GATK 4.5 and reference build GRCh38-no-alt. Mixing pipeline 1.4's code with pipeline 1.3's container set is the kind of decision that ruins a downstream analysis six months later.

Decide who owns the pipeline, who reviews changes, and how production cohorts are pinned. A cohort that started on 1.4 finishes on 1.4 unless there is an explicit migration; otherwise samples that arrive late in a study get a different analysis from samples that arrived early.

### 13. Plan reference-data hygiene

Reference data is the second axis of reproducibility next to tool versions, and it is treated worse in most pipelines. Pin it explicitly.

- A reference bundle for human work commonly includes the primary assembly FASTA, the corresponding index files (BWA, samtools faidx, sequence dictionary), the matching annotation GTF or GFF for transcript-aware tools, known-sites VCFs for BQSR or somatic filtering, gnomAD VCFs for population frequencies, and the matching VEP or SnpEff cache.
- Every file in the bundle has a checksum recorded next to it. The pipeline verifies checksums at run start. Reference drift — somebody re-downloading "the same" GTF and getting a different gene set — is otherwise invisible until results disagree.
- Distribute the bundle as a single immutable archive per version. "GRCh38 build 5.1" is a thing the pipeline can require. A loose directory of files is not.
- Document the provenance of the bundle. Which Ensembl, GENCODE, RefSeq, or UCSC release; which gnomAD version; which dbSNP build. The bundle is not "the reference" — it is a snapshot.

For non-human work, the same discipline applies even if the resources are smaller. The reference genome version, the annotation source and release, and any tissue- or species-specific transcriptome are all pinned together.

### 14. Decide a logging and observability convention

Pipelines run for hours to days. A run failing at hour 18 with no detail is wasteful. Lock the conventions early:

- Per-task stdout and stderr land in named files under the run's work directory and are preserved on failure. Cleaning up on success is fine; cleaning up on failure hides the cause.
- Long-running pipelines emit status to a place a human can watch — a log file, a dashboard, a Slack hook, an email on failure. Pick one and document.
- Resource usage is captured per task. Nextflow's trace and Snakemake's benchmarks both supply this. Reviewers reading the next sprint plan need the data.
- Pipeline-level events (run start, sample failures, completion) are logged at INFO or WARN so they survive log filtering.

### 15. Plan for production handoff explicitly

A pipeline that runs once for the developer is not yet shippable. The handoff checklist commonly includes:

- An end-to-end run on a representative small cohort with success criteria documented.
- The README or operating doc reachable by anyone who needs to run the pipeline, with the run command, the sample-sheet format, and the expected outputs.
- A test cohort or small dataset stored in the repository or referenced by URL that exercises the pipeline.
- The "what to do when it fails" guidance — which logs to read, which retries to attempt, when to escalate.
- A named owner for the pipeline and a named secondary.

Without these, the pipeline is a personal project that happens to run. With them, it is shared infrastructure.

## Inputs

- A description of what the pipeline is meant to analyze and produce.
- Expected scale and the target execution environments.
- Any existing scripts, modules, or partial pipelines to reuse or replace.
- Workflow engine preference, if any.
- Hard constraints from the environment, data, or compliance regime.

## Outputs

- A module-level architecture with the DAG, container strategy, and parameter surface.
- The sample sheet schema and validation rules.
- A resource-and-retry profile per target environment.
- A provenance plan covering versions, parameters, and per-task records.
- A handoff checklist gating the move from prototype to shared use.

## Examples

**Example A — sequencing core consolidating ad hoc scripts.** A core has been running variant calling via a folder of shell scripts and a `screen` session. The output is a recommendation to adopt Nextflow with nf-core/sarek as the starting baseline, define a sample sheet schema that captures library and lane, build a Slurm profile keyed to the local cluster's partitions, add an AWS Batch profile for overflow, and lock the reference bundle to a specific GRCh38 build with checksum verification. Provenance comes from Nextflow's built-in trace plus a per-run snapshot of the sample sheet and config to a results-adjacent `pipeline_info/` directory.

**Example B — Snakemake bulk RNA-seq pipeline for a translational lab.** The lab wants reproducible counts for several ongoing studies. The output is a Snakemake workflow modeled on the snakemake-workflows STAR+DESeq2 pattern, with rules for fastp, STAR alignment against a pinned GENCODE annotation, MarkDuplicates, featureCounts for gene-level counts, and MultiQC for aggregation. The sample sheet is a CSV with `sample`, `condition`, `batch`, and paired FASTQ paths, validated by a Python schema check at workflow start. Resources use `mem_mb` lambdas that escalate on retry. Differential expression is deliberately a separate downstream step so the pipeline stays study-agnostic and the DE step travels with each study.

**Example C — multi-site clinical research project.** The analysis must run identically at four institutions, two of which are on-prem with Singularity-only HPC and two of which are on cloud. The output is a Nextflow pipeline with one config file per site that picks the executor, queue, and storage backend, plus a strict policy that all tool containers are published from a single registry with digest pinning. Reference data is distributed as a versioned bundle with checksums. Each run uploads its provenance JSON to a shared store so the consortium can verify identical inputs and tool versions before pooling results.

## Limitations

- This skill cannot pick which tool is right for the science; it organizes the pipeline around whatever tools the methodology demands. Pair with the variant calling, RNA-seq, or single-cell planner skills.
- It does not generate executable workflow code. The output is the design, the contracts, and the checks. Implementation in Nextflow DSL2 or Snakemake Python is downstream.
- It assumes the team has at least one experienced bioinformatician to drive implementation. The skill structures their work; it does not replace expertise.
- Highly specialized data types (long reads with complex graph references, spatial omics, multi-modal single cell) need adaptations that are beyond a single planning pass. Use this as a starting frame and iterate.

### 16. Anti-patterns to avoid

A short list of structural choices that look reasonable on a slide and corrode in practice:

- **Tool versions tracked in a wiki.** Versions belong in code (containers, lock files), not in a document somebody updates by hand.
- **A single mega-process.** A "do everything" rule that runs the full per-sample pipeline as one shell script defeats caching and retries. Decompose.
- **Branching the pipeline per cohort.** Forks accumulate. Parameterize instead, with a config file per cohort and a single shared pipeline body.
- **Custom in-house caller for an established methodology.** Unless there is a strong methodological reason, prefer well-validated community tools. Custom callers are debt magnets.
- **Skipping QC because "the data looks fine."** QC is cheap; the cost of trusting bad samples is high.
- **Hand-edited results.** A spreadsheet of variants with rows added by hand is not an output of the pipeline. The pipeline either emits the truth or the pipeline is wrong.

### 17. Final shape of the deliverable

A complete pipeline architecture from this skill comprises:

- A one-page summary of the analysis contract, modules, and the engine.
- The sample-sheet schema and validation rules.
- A per-environment profile file outline.
- A provenance plan with the exact artifacts each run will produce.
- A handoff checklist with named owners and target dates.

Implementation in Nextflow DSL2 or Snakemake Python follows; the architecture is the contract under which implementation proceeds.

## Sources reviewed

- https://github.com/nf-core/rnaseq
- https://github.com/nf-core/sarek
- https://github.com/nextflow-io/nextflow
- https://github.com/snakemake/snakemake
- https://github.com/snakemake-workflows/dna-seq-gatk-variant-calling
- https://github.com/snakemake-workflows/rna-seq-star-deseq2
- https://github.com/broadinstitute/gatk
