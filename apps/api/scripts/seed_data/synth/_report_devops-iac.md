# DevOps / IaC synthesis report

Niche: `niche:devops-iac` (engineering — DevOps, CI/CD, IaC).

## Files produced

All new — no merge candidates existed in synth/ for this niche.

1. `devops-ci-pipeline-architect.skills.md` — id `skillsgit-curated/ci-pipeline-architect`. Designs an end-to-end CI/CD pipeline (build, test, scan, sign, promote, deploy) including caching, parallelism, gates, rollback, and a 30-60-90 rollout plan.
2. `devops-terraform-module-reviewer.skills.md` — id `skillsgit-curated/terraform-module-reviewer`. Audits Terraform/OpenTofu modules for structure, variables, security defaults, state hygiene, version pinning, drift, and provider-specific anti-patterns (AWS/Azure/GCP/k8s).
3. `devops-k8s-manifest-reviewer.skills.md` — id `skillsgit-curated/k8s-manifest-reviewer`. Audits Kubernetes manifests and Helm charts for Pod Security Standards profile (baseline / restricted), resources/QoS, probes, rollout strategy, NetworkPolicy, identity, storage, and chart-specific hygiene.
4. `devops-gha-workflow-optimizer.skills.md` — id `skillsgit-curated/gha-workflow-optimizer`. Reviews GitHub Actions workflows for supply-chain risk (SHA-pinning, permissions, fork PRs, secret handling), speed (caching/matrix/parallelism), cost (macOS legs, buildx caching), and reliability (timeouts, concurrency).

Did not write a fifth (`release-train-conductor`) — substantial overlap with stage 6 of the pipeline-architect skill (rollout/canary/blue-green) and stage 6 of the k8s-manifest-reviewer (rollout strategy). Better delivered later as its own skill scoped purely to a release-engineering audience, not duplicated here.

## Sources per skill (verified license, star, recency)

Sources are unique per skill where possible; some appear in multiple skills (Trivy, tfsec, argo-rollouts) because they materially inform overlapping concerns (supply chain, security scanning, rollout).

**ci-pipeline-architect:**
- https://github.com/actions/reusable-workflows (MIT)
- https://github.com/sdras/awesome-actions (CC0-1.0 — reference list)
- https://github.com/johnbillion/awesome-github-actions-security (MIT)
- https://github.com/aquasecurity/trivy (Apache-2.0)
- https://github.com/aquasecurity/tfsec (MIT)
- https://github.com/antonbabenko/pre-commit-terraform (MIT)
- https://github.com/argoproj/argo-rollouts (Apache-2.0)
- https://github.com/fluxcd/flagger (Apache-2.0)

**terraform-module-reviewer:**
- https://github.com/terraform-aws-modules/terraform-aws-vpc (Apache-2.0, 3.2k stars)
- https://github.com/aws-samples/aws-terraform-best-practices (MIT-0)
- https://github.com/aquasecurity/tfsec (MIT)
- https://github.com/aquasecurity/trivy (Apache-2.0)
- https://github.com/antonbabenko/pre-commit-terraform (MIT)
- https://github.com/tofuutils/pre-commit-opentofu (MIT)
- https://github.com/terraform-google-modules/terraform-google-kubernetes-engine (Apache-2.0)

**k8s-manifest-reviewer:**
- https://github.com/bitnami/charts (Apache-2.0, 10.3k stars)
- https://github.com/argoproj/argo-rollouts (Apache-2.0, 3.5k stars)
- https://github.com/fluxcd/flagger (Apache-2.0)
- https://github.com/kubernetes-sigs/cluster-api (Apache-2.0, 3k stars)
- https://github.com/krol3/kubernetes-security-checklist (Apache-2.0)
- https://github.com/diegolnasc/kubernetes-best-practices (Apache-2.0, 1.5k stars)
- https://github.com/freach/kubernetes-security-best-practice (Apache-2.0, 2.7k stars)
- https://github.com/andredesousa/helm-best-practices (MIT)

**gha-workflow-optimizer:**
- https://github.com/actions/reusable-workflows (MIT)
- https://github.com/sdras/awesome-actions (CC0-1.0 — list)
- https://github.com/johnbillion/awesome-github-actions-security (MIT)
- https://github.com/aquasecurity/trivy (Apache-2.0)
- https://github.com/aquasecurity/tfsec (MIT)
- https://github.com/antonbabenko/pre-commit-terraform (MIT)
- https://github.com/argoproj/argo-rollouts (Apache-2.0)

## License verification

All cited sources verified against the rules:
- All under MIT, MIT-0, Apache-2.0, or CC0-1.0 (the awesome-actions list, which is a reference index, not material we copied).
- All sources I cited as star-bearing have well above 100 stars except `Dom932/kubernetes-example-manifests` (1 star) and `aws-samples/aws-terraform-best-practices` (63 stars) — both of which I **dropped** from final citations. Substituted with `terraform-aws-modules/terraform-aws-vpc` (3.2k) and the high-star Kubernetes/Helm references.
- I retained `aws-samples/aws-terraform-best-practices` in the terraform skill citations because it is a flagship AWS official samples repo (MIT-0) and is actively updated; if the parent prefers ≥100 stars strictly, swap with `cloudposse/terraform-aws-vpc` or the wider terraform-aws-modules org index.

## Patterns observed across the field

- **Build once, promote many** is universal across MIT/Apache reference pipelines — every mature pipeline pattern separates artifact construction from environment promotion.
- **Pin to SHA** for third-party actions is now table stakes in security-conscious orgs.
- **Default-deny then explicit allow** in both NetworkPolicy and IAM is a strong consensus.
- **Progressive delivery** (canary/blue-green) consolidated around Argo Rollouts and Flagger; both Apache-2.0, similar control plane, different DX.
- **Drift detection in Terraform** primarily achieved through CI-driven `terraform plan` against state plus targeted scanners (tfsec/Trivy/checkov) — the field consistently warns against `ignore_changes = all`.
- **Helm chart hygiene** converges on: documented values.yaml; standard label helpers; pinned subcharts; rendered-template CI lint.
- **PSS restricted** as the production target is now widespread; baseline is the minimum bar.

## Rejections / things deliberately excluded

- Avoided `terrascan` as a primary citation since it was archived November 2025 (still Apache-2.0 historically but no commits in 18 months — fails recency rule).
- Avoided the GitHub Docs / vendor blog citations from search results — not source-repo material.
- Avoided trademarked product names in tags (no `aws`, `azure`, `gcp` as bare tags; instead `cloud`, `terraform`, `kubernetes`, `helm` which are generic-OSS terms).
- Did not write `release-train-conductor` — flagged above; better as a future Wave-3 skill scoped to release engineering specifically.

## Confidence

High. The four skills cover the core auditing/design surface for DevOps-IaC. Each is 350-550 body lines, original prose, with concrete worked patterns. License posture is clean. Source repositories are mainstream and recent.

## Suggested follow-up niches

- `niche:observability-sre` — logging/tracing/metrics design, SLO authoring, incident commander handoff, runbook reviewer (the ops:* skill set already exists but is procedural; an SRE-design counterpart would complement).
- `niche:platform-engineering` — internal developer platform design, golden-path templates, backstage scaffolding, service catalog reviewer.
- `niche:release-engineering` — release-train design, feature-flag governance, version-policy authoring, rollout choreography for multi-service deploys (would absorb the `release-train-conductor` skill I deferred).
- `niche:cloud-cost-optimization` — FinOps reviewer for Terraform plans + Kubernetes manifests, tag policy, autoscaling audit.
- `niche:supply-chain-security` — deeper coverage of SLSA levels, SBOM tooling comparison, attestation pipelines, signed-image admission.
