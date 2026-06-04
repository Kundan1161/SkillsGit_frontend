# Wave-3 Supply-Chain Security — Synthesis Report

**Niche:** engineering — software supply-chain security (SLSA, SBOM, signing, attestation, dependency review)
**Wave-2 boundary respected.** Wave 2 covered `eng-security-code-review` (defensive code review) and `devops-gha-workflow-optimizer` (supply-chain GHA practices). My scope is broader supply-chain hygiene methodology that is not pipeline-specific and not code-review-specific.
**Date:** 2026-05-14

## Files produced

- `D:\skillsgit\synth\slsa-maturity-assessor.skills.md`
- `D:\skillsgit\synth\sbom-program-architect.skills.md`
- `D:\skillsgit\synth\artifact-signing-and-verification-designer.skills.md`
- `D:\skillsgit\synth\dependency-review-policy-author.skills.md`

Four skills, all `license_type: free`, no pricing, frontmatter conformant to `prompts/shared/skills-md-spec.md`, bodies in the 300-700 line range with the required `## When to use` and `## How to apply` sections plus Inputs / Outputs / Examples / Limitations / Sources.

## Merge analysis

No existing synth files overlap with this niche. The four existing files in `synth/` are robotics, signal-detection, lakehouse-formats, and academic submission strategy. No merges or version bumps required. All four files are new at `1.0.0`.

The prompt mentioned external Wave-2 skills (`eng-security-code-review`, `devops-gha-workflow-optimizer`) that are not on disk; I intentionally pitched each skill to a different scope than those names imply: methodology / program design rather than pipeline tweaks or code review. No content overlap with those names.

## Sources used (all verified)

License + freshness + stars verified by WebFetch on 2026-05-14.

| Source | License | Stars | Last release |
|---|---|---|---|
| sigstore/cosign | Apache-2.0 | 5.9k | v3.0.6 (2026-04-06) |
| sigstore/policy-controller | Apache-2.0 (verified via repo) | 172 | v0.15.1 (2026-03-26) |
| in-toto/attestation | Apache-2.0 (LICENSE confirmed) | 335 | v1.2.0 (2026-03-18) |
| slsa-framework/slsa-github-generator | Apache-2.0 | 573 | v2.1.0 (2025-02-24) |
| anchore/syft | Apache-2.0 | 8.9k | v1.44.0 (2026-05-01) |
| aquasecurity/trivy | Apache-2.0 | 35k | v0.70.0 (2026-04-17) |
| CycloneDX/cyclonedx-cli | Apache-2.0 | 495 | v0.32.0 (2026-05-14) |
| CycloneDX/specification | Apache-2.0 | 504 | v1.7 (2025-10-21) |
| ossf/scorecard | Apache-2.0 | 5.4k | v5.5.0 (2026-04-23) |
| google/osv-scanner | Apache-2.0 | 10.2k | v2.3.8 (2026-05-08) |
| chainguard-dev/apko | Apache-2.0 | 1.6k | v1.2.12 (2026-05-11) |
| pypa/pip-audit | Apache-2.0 | 1.3k | v2.10.0 (2025-12-01) |
| DataDog/guarddog | Apache-2.0 | 1.1k | v2.9.0 (2026-02-06) |

All within 18-month freshness from 2026-05-14. All >= 100 stars. All on the approved license list.

## Rejections

- **SLSA framework itself (slsa-framework/slsa).** The framework's specifications are CC-BY-4.0 / Community Spec License — not on the approved license list (MIT/Apache/BSD/ISC/Unlicense only). **Rejected as a methodology source.** SLSA is referenced in the skills *statutorily* — as a name for an industry convention and a target maturity vocabulary — but no SLSA prose, structure, or wording is adopted into the skills. Source links in the skills are to Apache-2.0 tooling that *implements* SLSA-style flows (slsa-github-generator), not to the framework repo.
- **spdx/spdx-spec.** Contributions are under the SPDX Community Specification Contributor License Agreement (CC-BY-style community spec). **Rejected** as a source for the same reason. SPDX is mentioned in the SBOM skill as a format choice; format-name and field-name references are factual nomenclature, not adopted content. No SPDX prose is included.
- **OpenSSF specifications repository.** Mixed license posture and the documents are aspirational. Avoided as a source; used the Apache-2.0 tooling repos (Scorecard) instead.

## Sources cited per skill (5-10 each, URL only as required)

- `slsa-maturity-assessor`: cosign, in-toto/attestation, slsa-github-generator, ossf/scorecard, syft, trivy — 6 sources.
- `sbom-program-architect`: syft, trivy, cyclonedx-cli, cyclonedx/specification, osv-scanner, pip-audit — 6 sources.
- `artifact-signing-and-verification-designer`: cosign, sigstore/policy-controller, in-toto/attestation, slsa-github-generator, chainguard-dev/apko, ossf/scorecard — 6 sources.
- `dependency-review-policy-author`: ossf/scorecard, osv-scanner, trivy, DataDog/guarddog, pip-audit, cyclonedx/specification — 6 sources.

## Patterns observed across the niche

- The recurring failure mode is **"control without evidence."** Teams adopt signing, SBOMs, or scanning, but produce no auditable artifact a third party can verify. Every skill emphasizes the evidence axis explicitly.
- **Verification at consumption** is the highest-leverage missing control across the industry. Signing without verification is theater; SBOMs without correlation pipelines are filing cabinets; provenance without policy enforcement at admission is decoration. Each skill terminates at the verifier, not at the producer.
- **Workload-identity-bound (keyless) signing** is the modern default; long-lived keys persist mainly for air-gapped and regulated contexts. The artifact-signing skill treats keyless as the primary path and key-based as the exception.
- **Tiered policy** is the only sustainable shape for dependency review — uniform scrutiny breaks. The dependency-policy skill builds tiering into Phase 1.
- **Transparency log monitoring** is a frequently-skipped but cheap and high-signal control. Called out explicitly in the signing skill.
- I dropped the optional fifth skill (`package-typosquat-defense-designer`) because typosquat / dependency-confusion content is already substantively covered in the dependency-review-policy-author (Phase 4 supply-chain attack surface + Phase 5 typosquat gate) and would be redundant rather than additive. Four focused skills > five overlapping ones.

## Confidence

**High.** The supply-chain space has a stable, well-documented vocabulary; all source repositories are heavily used and current; license verification was unambiguous on every cited project. The main methodological judgment calls — keyless-by-default, tiered dependency policy, evidence-axis emphasis, VEX in the SBOM program — reflect current industry consensus and are framed as defaults with stated exceptions, not absolutes. No skill prescribes specific vendor tooling beyond the cited open-source projects. All scope guardrails and limitations sections are explicit about where methodology stops and qualified review begins (legal counsel for licensing, security auditors for compliance, cryptography expertise for HSM operation).
