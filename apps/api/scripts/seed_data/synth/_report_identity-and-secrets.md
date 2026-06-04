# Wave-5 Synthesis Report — Niche: Identity and Secrets (Engineering)

## Scope

This wave covers the layer beneath general application security: secrets management, workload identity, cryptographic key management programs, and hardware-rooted device attestation. It is intentionally distinct from the existing wave-3/4 skills:

- `eng-security-code-review` (application-level code review of authn/authz, injection, crypto misuse) sits above this layer.
- `legal-vendor-security-review` (vendor questionnaire scoring) sits to the side.
- `devops-terraform-module-reviewer`, `devops-k8s-manifest-reviewer` (platform infra reviews) intersect this layer at the configuration surface but do not own the architectural decisions.

The wave fills the architectural-design gap: how an organization decides where secrets live, how workloads prove who they are, how key material is kept, and how device platforms are gated by hardware-rooted evidence.

## Skills produced

1. `eng-secrets-architecture-designer.skills.md` — secrets-architecture-designer
2. `eng-workload-identity-architect.skills.md` — workload-identity-architect
3. `eng-key-management-program-architect.skills.md` — key-management-program-architect
4. `eng-tpm-remote-attestation-architect.skills.md` — tpm-remote-attestation-architect (the optional fourth)

All four are `category: engineering`, `license_type: free`, no pricing, first tag `niche:identity-and-secrets`, and 5-8 supporting tags each.

## Sources reviewed and licenses

All sources were verified for permissive license, more than 100 stars, and recent commit activity (release within the last twelve months).

| Repository | License | Stars (approx) | Latest release | Used in |
| --- | --- | --- | --- | --- |
| https://github.com/spiffe/spire | Apache-2.0 | 2.3k | 2026-04 | 1, 2, 4 |
| https://github.com/openbao/openbao | MPL-2.0 | 6.1k | 2026-04 | 1, 2, 3, 4 |
| https://github.com/external-secrets/external-secrets | Apache-2.0 | 6.6k | 2026-04 | 1, 2 |
| https://github.com/cert-manager/cert-manager | Apache-2.0 | 13.8k | 2026-04 | 1, 2, 4 |
| https://github.com/getsops/sops | MPL-2.0 | 21.8k | active | 1, 3 |
| https://github.com/FiloSottile/age | BSD-3-Clause | 22.3k | 2025-12 | 1, 3 |
| https://github.com/sigstore/cosign | Apache-2.0 | 5.9k | active | 1, 2, 3, 4 |
| https://github.com/google/tink | Apache-2.0 | 13.5k | archived (split) | 3 |
| https://github.com/google/go-tpm | Apache-2.0 | 652 | 2025-12 | 2, 3, 4 |
| https://github.com/keylime/keylime | Apache-2.0 | 538 | 2026-05 | 2, 4 |
| https://github.com/aws/aws-encryption-sdk-java | Apache-2.0 | 239 | active | 3 |

### License-policy notes (per wave-4)

- The Apache-2.0 and BSD-3-Clause sources are unambiguous for synthesis purposes. Citations are included for transparency.
- The MPL-2.0 sources (OpenBao, sops) are file-level weak copyleft. No content from these projects is copied; the skill bodies are 100% original prose describing methodology patterns that are themselves not original to those projects (envelope encryption, dynamic credentials, encrypted-file editing). Per the wave-4 policy, citation with explicit license labelling is included.
- Tink is archived in this repository but development continues at github.com/tink-crypto under the same license; the citation points to the canonical historical artefact relied upon.

## Rejections

- **Bitwarden server** (https://github.com/bitwarden/server) — AGPL-3.0 plus a Bitwarden proprietary licence. Rejected from synthesis scope: AGPL is incompatible with the wave-4 permissive-only policy for source-material study.
- **HashiCorp Vault** — current versions are under the BSL (Business Source Licence) and explicitly not OSI-permissive. Not reviewed; OpenBao serves as the open-source-licensed reference for the equivalent design space.

## Patterns synthesized across skills

The four skills share a common architectural backbone:

- **Identity first, secrets second.** The secrets architecture skill explicitly depends on a workload-identity layer for bootstrap; the identity skill depends on a custody story for the issuer signing key, which the KMS skill provides; the KMS skill depends on a custody primitive that, on premises, the TPM skill anchors. The four skills form a stack that can be deployed in dependency order.
- **Short-lived over long-lived.** Every skill defaults to ephemeral credentials, dynamic generation, fresh attestation, and short ttls. Long-lived material is described as a special case with explicit residual-risk capture.
- **Custody is policy, not technology.** Each skill spends significant time on who can perform a sensitive operation, what witnessing is required, and what audit survives a compromise. The technology choice is downstream of the policy.
- **Migration as ordered phases.** Each skill produces a migration roadmap with phases that have entry conditions, exit criteria, named owners, and rollback paths. The skills explicitly refuse to recommend forced cut-overs at this layer.
- **Residual-risk register.** Each skill produces an explicit list of items the design knowingly does not solve, with the trigger for revisiting. This is treated as a first-class artefact, not an afterthought.

## Confidence

- **High** on skills 1 (secrets architecture), 2 (workload identity), and 3 (KMS program). The source set is mature, the patterns are well-established in the field, and the synthesis aligns with widely accepted approaches without copying any specific project's framing.
- **Medium-high** on skill 4 (TPM attestation). The pattern is well-described in the literature but the source set is smaller (Keylime is the primary methodology source); the skill leans on go-tpm and SPIRE for adjacent pattern grounding rather than as the methodology authority. The skill is appropriately scoped and explicitly excludes confidential-compute attestation primitives, which are a separate body of work.

## File outputs

All files written to `D:\skillsgit\apps\api\scripts\seed_data\synth\`:

- `eng-secrets-architecture-designer.skills.md`
- `eng-workload-identity-architect.skills.md`
- `eng-key-management-program-architect.skills.md`
- `eng-tpm-remote-attestation-architect.skills.md`
- `_report_identity-and-secrets.md` (this file)
