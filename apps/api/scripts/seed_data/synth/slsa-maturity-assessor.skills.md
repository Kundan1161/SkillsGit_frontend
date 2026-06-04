---
id: skillsgit-curated/slsa-maturity-assessor
version: 1.0.0
name: SLSA Maturity Assessor
description: Gap-analyze a build pipeline against modern supply-chain hardening expectations across source, build, dependency, and deployment stages, and produce a prioritized remediation plan.
authors:
  - name: Wave-3 Methodology Synthesis
    handle: wave3-supplychain
    role: author
category: engineering
tags:
  - niche:supply-chain-security
  - slsa
  - provenance
  - build-integrity
  - hermetic-build
  - reproducible-build
  - ci-hardening
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
    - gpt-4.1
    - gemini-1.5-pro
  min_context_tokens: 32000
  tools_optional:
    - web_search
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - slsa
  - supply chain
  - build provenance
  - hermetic build
  - reproducible build
  - ci hardening
  - sigstore
  - in-toto
  - attestation
  - build integrity
example_invocations:
  - "Assess our GitHub Actions pipeline against SLSA-style maturity expectations."
  - "Where are the gaps in our build that an attacker could exploit?"
  - "We sign artifacts but don't generate provenance — what's the priority?"
  - "Plan a 90-day roadmap to harden our build pipeline."
inputs:
  - name: pipeline_description
    type: text
    required: true
    description: How the build pipeline is structured (CI system, runners, build steps, language toolchains, where artifacts land).
  - name: source_control_practices
    type: text
    required: true
    description: SCM (GitHub/GitLab/etc.), branch-protection rules, code-review policy, signed commits, two-person rule for releases.
  - name: artifact_handling
    type: text
    required: true
    description: How artifacts are stored, signed, and consumed (registry, package manager, OS packages, container images, internal repos).
  - name: existing_controls
    type: text
    required: false
    description: Any current SBOM, signing, attestation, scanning, or admission-control practices.
  - name: threat_profile
    type: text
    required: false
    description: Adversaries you care about (script kiddies, criminal groups, insider risk, nation-state). Drives the level of investment justified.
outputs:
  - name: maturity_report
    type: markdown
    description: A staged gap analysis (source / build / dependency / deployment) with a current-state score, target-state, and a sequenced remediation roadmap.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# SLSA Maturity Assessor

## When to use

Use this skill when a team needs to honestly evaluate the supply-chain integrity of their build pipeline and produce a sequenced remediation plan. Typical situations:

- A new compliance requirement (FedRAMP, EU CRA, internal security review) asks for "supply-chain maturity" evidence.
- After a public incident in a peer organization, leadership asks "could that happen to us?"
- A new product is going to ship with stronger security claims and the team needs to walk the build pipeline end-to-end.
- An auditor or customer is reviewing build integrity controls.
- The team has a partial control surface (e.g., they sign artifacts but lack provenance) and wants a roadmap.

This skill does **not** implement the controls. It identifies the gaps, assigns severity, and orders the work. Implementation belongs to platform/engineering teams.

**Scope guardrail.** This is methodology guidance. Every recommendation must be reviewed against your actual regulatory, contractual, and threat-model context before adoption. Public references to "SLSA" levels here describe industry conventions, not certification. Compliance certifications, where required, must be validated by qualified auditors.

## How to apply

Work the four stages in order — Source, Build, Dependency, Deployment — and within each stage, walk the *intent → control → evidence* triad. Skipping the evidence axis is the single most common failure: teams adopt a control but cannot prove it ran on the artifact that shipped.

### Stage 1 — Source integrity

Goal: every byte that enters the build is attributable to a reviewed, authenticated change.

Probe these controls:

- **Identity.** Are committers strongly authenticated (SSO + WebAuthn / hardware keys), or only password + TOTP? Service accounts in particular: are they scoped, time-limited, rotated?
- **Branch protection on release branches.** Required reviews >= 2, no force-push, no admin bypass, stale-review dismissal on new commits, required status checks must pass, signed commits required.
- **Code review enforcement.** Reviews from a different person than the author (no self-merge), reviewers from a code-owners file, dismiss stale approvals on rewrite.
- **Bot policy.** Bots that can push (release-please, dependabot, renovate) have least-privilege tokens, are reviewable, and cannot bypass branch protection without an additional human approval.
- **Commit signing.** Signed commits or signed tags using OpenPGP, SSH signing, or Sigstore gitsign. Critically: signatures are *verified* server-side, not just collected.
- **Repo-config drift.** A central record of expected branch-protection / required-checks settings; an automated check that fails when settings drift.
- **Source provenance.** Is there an SCM-side attestation (e.g., signed protected-branch state at release) that downstream stages can consume?

Severity weighting: missing branch protection on release branches or admin-bypass enabled is **critical**; unsigned commits without verification is **high**; missing repo-config drift detection is **medium**.

### Stage 2 — Build integrity

Goal: a build is reproducible from declared inputs, runs on isolated and ephemeral infrastructure, and emits cryptographic provenance binding the artifact to the source revision and the build instructions.

Probe these controls:

- **Build definition is in-repo and reviewed.** No "click-ops" jobs, no out-of-band release scripts, no admin-only build configs that bypass review.
- **Ephemeral, isolated runners.** Each build runs on a fresh runner, no shared mutable state, network restricted to declared egress. Self-hosted runners pinned to ephemeral VMs/containers, not long-lived pets.
- **Pinned toolchain.** Compiler, language runtime, package manager, and base images pinned by content digest (not floating tags). A lockfile-equivalent for the toolchain itself.
- **Pinned actions / plugins.** Reusable CI actions and plugins pinned by commit SHA, not by tag. Tags are mutable; SHAs are not.
- **Hermeticity.** Build cannot reach the public internet during compile/link; dependencies are pre-fetched into a controlled cache. If full hermeticity is infeasible, at minimum the dependency fetch step is separated, logged, and produces a lockfile-verified manifest.
- **Two-person rule for release builds.** Producing a build that will be signed for distribution requires approval from a second authorized human, recorded in an auditable event log.
- **Provenance generation.** The build produces an in-toto attestation (or equivalent) that lists: source repo URL, source commit, builder identity, build entrypoint, parameters, build start/end time, materials (inputs), and subject (output digest). The provenance is signed by a key the *builder controls*, not by a human.
- **Provenance non-falsifiability.** The signing identity for provenance is bound to the build platform's identity (workload identity, OIDC), so a human cannot mint a provenance off the builder. This is the qualitative jump from "we sign things" to "the builder attests to itself."
- **Reproducibility (stretch).** Two builds of the same source revision on the same toolchain produce byte-identical artifacts. Track which artifact classes are reproducible; many are not, and that is a known limitation, not a failure.

Severity weighting: missing build provenance is **critical** above a certain maturity tier; floating-tag actions/runners is **high**; lack of two-person release is **high** for software with broad distribution; non-reproducibility is **medium** (track, don't block).

### Stage 3 — Dependency integrity

Goal: every third-party input is pinned, audited, and continually monitored; supply-chain attacks via dependencies are caught before they ship.

Probe these controls:

- **Lockfiles committed and enforced.** Every direct and transitive dependency resolved to a specific version + content hash. CI fails if the lockfile is missing, stale, or has unverified hashes.
- **Integrity verification.** Package manager configured to verify hashes against the lockfile and fail closed. Mirror or private registry pinned; no fall-through to public registries.
- **Vulnerability scanning.** Continuous scanning (e.g., OSV-based) on the lockfile and on container base images. Triage SLA defined by severity. Critical vulnerabilities block release.
- **License review.** Licenses on every dependency are tracked, with an allowlist/denylist by license class. Copyleft and unknown-license dependencies are flagged for human review.
- **SBOM generation.** A signed SBOM (CycloneDX or SPDX) is generated as part of the build and attached as an artifact attestation.
- **Maintainership signals.** New direct dependencies are evaluated for maintainership health (recent activity, multiple maintainers, response to past CVEs) using objective scorecards. This is a process control, not a build-time gate.
- **Source-of-truth registry.** Internal artifacts and approved third-party artifacts live in a private registry with audit logging. Builds pull from this registry, not from public mirrors directly.
- **Typosquat / confusion defense.** Dependency-confusion blocked at the registry (scope locks for internal packages); typosquat detection on new dependencies; namespace pinning for internal scopes.

Severity weighting: missing lockfile or unverified hashes is **critical**; no vulnerability scanning is **critical**; no SBOM is **high**; no maintainership review is **medium**; no typosquat defense is **high** if you use ecosystems with name-confusion risk (npm, PyPI).

### Stage 4 — Deployment & consumption integrity

Goal: only artifacts that pass policy reach production; provenance is verified at admission, not just generated.

Probe these controls:

- **Signature verification at deploy.** The runtime platform (Kubernetes admission controller, OS package manager, deployment tool) verifies the artifact signature against an allowed identity set. Unsigned or wrong-identity artifacts are rejected.
- **Provenance policy.** Beyond "is this signed?", policy enforces "was this built from our repo, on our builder, from a protected branch, by a workflow we trust?" Provenance attestations are evaluated, not just collected.
- **Transparency log presence.** Signatures and attestations are recorded in a tamper-evident transparency log so that silent re-signing is detectable.
- **Promotion gates.** A separate, audited step promotes an artifact from staging to production. The promotion records which version was promoted, by whom, and what policies were checked.
- **Rollback capability.** Last-known-good artifacts are retained and re-deployable. Rollback does not require a fresh build.
- **Runtime egress monitoring.** Workloads can be alerted/blocked when they fetch code or binaries at runtime (curl | bash, plugin loaders), since those bypass the build's supply-chain controls.
- **Incident response readiness.** If an artifact must be revoked, there is a defined process: revoke signing identity, push policy update to deny the artifact's digest, surface affected deployments, notify downstream consumers.

Severity weighting: no signature verification at deploy is **critical** (you have provenance theater without it); no provenance policy is **high**; no transparency log is **medium**; no runtime egress controls is **medium** to **high** depending on workload sensitivity.

### Step 5 — Score and prioritize

For each control above, assign a state:

- **Absent** — no implementation.
- **Partial** — implemented for some artifacts, manually or with gaps.
- **Implemented** — covers all release artifacts but evidence is weak.
- **Enforced with evidence** — covers all release artifacts, machine-verifiable, audit-logged.

Aggregate into a maturity tier per stage (not a single global number — global numbers hide imbalance):

- **Tier 0** — pipeline runs, no integrity controls.
- **Tier 1** — basic hygiene: branch protection, lockfiles, vulnerability scanning, signed artifacts (signature trust is human-based).
- **Tier 2** — builder-issued provenance, hermetic-ish build, SBOM, signature verification at deploy.
- **Tier 3** — fully hermetic build, two-person release, provenance policy enforcement, transparency log, revocation rehearsed.

Most production teams sit at Tier 1 with patches of Tier 2. Honest scoring is more useful than aspirational scoring.

### Step 6 — Build the remediation roadmap

Sequence remediation by **cost-adjusted risk**, not by stage order. A typical good ordering for a Tier-1 team moving toward Tier 2:

1. **Pin all CI actions/plugins to commit SHAs.** Cheap, blocks a real attack class (tag hijack), audit-evidence trivial. Do this first.
2. **Generate SBOM in build, attach as artifact.** One CI step, unblocks vulnerability correlation downstream.
3. **Adopt keyless signing (workload-identity-bound) for artifacts.** Removes a long-lived secret, builder identity becomes machine-attestable.
4. **Add signature verification at deploy.** Without verification, signing is decorative. This is the highest-leverage control to add second.
5. **Generate in-toto-style provenance attestations from the builder.** Costs more (often a builder template change); converts "we sign" into "the builder attests."
6. **Enforce provenance policy at admission.** Reject artifacts whose provenance points at the wrong repo, branch, or workflow.
7. **Two-person release approvals.** Process control; should land before broad public distribution.
8. **Hermeticity / reproducibility work.** Most expensive, longest tail. Track reproducibility per-artifact, don't expect 100%.

For each item produce: owner, dependency on other items, an effort estimate, an evidence artifact (what proves it's done), and a rollback plan.

### Step 7 — Define evidence the auditor will read

For each remediated control, define the *machine-verifiable evidence* it produces. Process notes are not evidence. Examples:

- Branch protection enforced → a periodic export of branch-protection settings, diffed against expected config, archived.
- Pinned actions → a CI lint that fails the build if any action reference is not a 40-char SHA.
- Provenance generated → the attestation file, retrievable from the registry, with a known schema and signing identity.
- Provenance verified at deploy → the admission controller's decision log, retained per retention policy.

If no evidence artifact is produced, the control will silently rot. This is the single most common audit failure.

## Inputs

- **Pipeline description.** CI system, runner topology, build languages, where artifacts land.
- **Source-control practices.** SCM, branch protection, review policy, signing posture.
- **Artifact handling.** Registries, signing tools, consumption pattern.
- **Existing controls.** Anything already in place (SBOM, signing, scanning).
- **Threat profile.** What adversary class justifies what level of investment.

## Outputs

A markdown report containing:

1. **Per-stage state table.** Source / Build / Dependency / Deployment, with each control marked Absent / Partial / Implemented / Enforced-with-evidence.
2. **Tier assessment.** Honest current tier per stage and overall.
3. **Top-five critical gaps.** With severity and the attacker capability each gap enables.
4. **Sequenced 90-day remediation plan.** With owner / effort / evidence per item.
5. **Evidence catalogue.** What auditors / customers will be shown for each control.
6. **Open questions.** Where the team's input was ambiguous and follow-up is needed.

## Examples

**Example A — Mid-size SaaS, Tier 1 with patches of Tier 2.**

The team uses GitHub Actions, signs container images with cosign keyless, has lockfiles, runs OSV-Scanner in CI. Gaps surface in three places: (1) actions referenced by tag, not SHA; (2) signatures are not verified at deploy — they're collected and logged only; (3) no provenance attestation, only signature. Remediation plan in order: pin actions (week 1), add cosign verification gate in deploy pipeline (week 2-3), generate SLSA-style provenance via the GitHub generator (week 4-6), enforce provenance policy (week 7-9). Stretch: two-person release approvals before public marketplace launch.

**Example B — Enterprise monorepo, Tier 0 building toward Tier 1.**

Self-hosted runners are long-lived VMs. No lockfile enforcement. No vulnerability scanning. Container images pushed unsigned. Critical gaps dominate: re-image runners as ephemeral (foundational), enforce lockfile + hash verification, add OSV scanning, sign images. All of Tier 2 work is deferred until Tier 1 is solid; pushing Tier 2 features on a Tier 0 base produces evidence theater.

## Limitations

- This skill assumes the user accurately describes their pipeline. It cannot detect lies or blind spots without inspecting the pipeline directly.
- "SLSA" levels in industry usage have evolved. Treat the tier descriptions here as a stable internal vocabulary; map to whatever external framework version is current at audit time.
- Reproducibility is treated as an aspirational track, not a gate. Many real-world artifacts (timestamps, randomized linker output, JIT-compiled assets) resist easy reproducibility.
- The skill does not address insider-threat scenarios beyond two-person release. Comprehensive insider-risk programs require additional controls (separation of duties, key custody, monitoring) outside the build pipeline.
- Nation-state-level adversaries can compromise build platforms themselves. This skill's recommendations raise the bar but do not eliminate that class of risk.

## Sources

- https://github.com/sigstore/cosign
- https://github.com/in-toto/attestation
- https://github.com/slsa-framework/slsa-github-generator
- https://github.com/ossf/scorecard
- https://github.com/anchore/syft
- https://github.com/aquasecurity/trivy
