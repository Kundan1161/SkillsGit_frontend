# DevOps Occupation — Verified Member Slugs (T-08)

**Owner:** Curation (Wave 1)
**Date:** 2026-05-26
**Purpose:** Hand Wave-3 Curation (T-08, `build_devops_vault.py`) a known-good 30-member set so the vault build is non-blocking on slug verification.

## Spec'd set (from `05-mvp-plan.md` T-08, lines 244–279)

### Core (10)
1. `devops-ci-pipeline-architect`
2. `devops-gha-workflow-optimizer`
3. `devops-k8s-manifest-reviewer`
4. `devops-terraform-module-reviewer`
5. `ops-incident-commander`
6. `ops-runbook-generator`
7. `observability-dashboard-architect`
8. `alert-policy-architect`
9. `alert-fatigue-reviewer`
10. `eng-chaos-experiment-planner`

### Supporting (12)
11. `cloud-cost-audit`
12. `cloud-cost-alert-designer`
13. `kubernetes-cost-optimizer`
14. `eng-secrets-architecture-designer`
15. `eng-workload-identity-architect`
16. `artifact-signing-and-verification-designer`
17. `internal-platform-strategy-author`
18. `imported-alirezarezvani-chaos-engineering`
19. `cardinality-cost-reviewer`
20. `imported-google-skills-waf-reliability`
21. `imported-google-skills-waf-cost`
22. `imported-google-skills-networking-observability`

### Optional (8)
23. `cross-platform-stack-chooser`
24. `spark-on-kubernetes-architect`
25. `kafka-topic-architect`
26. `kafka-consumer-pattern-picker`
27. `kafka-streams-pipeline-designer`
28. `kafka-schema-evolution-architect`
29. `imported-voltagent-cloudflare-platform`
30. `imported-voltagent-cloudflare-workers-best-practices`

## Verification

All 30 spec'd slugs **exist as files** under `apps/api/scripts/seed_data/synth/{slug}.skills.md` — verified by `Test-Path` against each filename. The 30-out-of-30 file-existence rate is the easy news.

The harder news: **two slugs name a file whose frontmatter is not a DevOps fit.** They were almost certainly chosen by the spec author from a slug-list scan without opening the body, and now name something else.

| # | Slug | File exists? | Frontmatter fit for DevOps occupation? | Recommended action |
|---|---|:---:|:---:|---|
| 1 | `devops-ci-pipeline-architect` | yes | yes (`category: engineering`, `niche:devops-iac`) | keep |
| 2 | `devops-gha-workflow-optimizer` | yes | yes (`niche:devops-iac`) | keep |
| 3 | `devops-k8s-manifest-reviewer` | yes | yes (`niche:devops-iac`) | keep |
| 4 | `devops-terraform-module-reviewer` | yes | yes (`niche:devops-iac`) | keep |
| 5 | `ops-incident-commander` | yes | yes (`category: operations`, `incident-response`) | keep |
| 6 | `ops-runbook-generator` | yes | yes (`category: operations`, `runbook`/`sre`) | keep |
| 7 | `observability-dashboard-architect` | yes | yes (`niche:observability-dashboards`) | keep |
| 8 | `alert-policy-architect` | yes | yes (`niche:observability-sre`) | keep |
| 9 | `alert-fatigue-reviewer` | yes | **NO** — `category: healthcare`, `niche:clinical-decision-support` (CDS alerts in EHRs, not Prometheus/Alertmanager) | **substitute** with `slo-designer` (see below) |
| 10 | `eng-chaos-experiment-planner` | yes | yes (`niche:distributed-systems`, chaos engineering) | keep |
| 11 | `cloud-cost-audit` | yes | yes (`niche:cloud-finops`) | keep |
| 12 | `cloud-cost-alert-designer` | yes | yes (`niche:cloud-finops`) | keep |
| 13 | `kubernetes-cost-optimizer` | yes | yes (`niche:cloud-finops`, k8s) | keep |
| 14 | `eng-secrets-architecture-designer` | yes | yes (`niche:identity-and-secrets`) | keep |
| 15 | `eng-workload-identity-architect` | yes | yes (`niche:identity-and-secrets`) | keep |
| 16 | `artifact-signing-and-verification-designer` | yes | yes (`niche:supply-chain-security`) | keep |
| 17 | `internal-platform-strategy-author` | yes | yes (`niche:platform-engineering`) | keep |
| 18 | `imported-alirezarezvani-chaos-engineering` | yes | yes (chaos / resilience / SRE) | keep |
| 19 | `cardinality-cost-reviewer` | yes | yes (`niche:observability-sre`) | keep |
| 20 | `imported-google-skills-waf-reliability` | yes | yes (Google WAF reliability pillar) | keep |
| 21 | `imported-google-skills-waf-cost` | yes | yes (Google WAF cost pillar) | keep |
| 22 | `imported-google-skills-networking-observability` | yes | yes (GCP networking obs) | keep |
| 23 | `cross-platform-stack-chooser` | yes | **NO** — `niche:mobile-dev` (decides between React Native / Flutter / Kotlin Multiplatform / native). Not DevOps. | **substitute** with `instrumentation-coverage-reviewer` (see below). The spec brief explicitly says "Curation may swap any optional slot if a better candidate exists; do not change the count without updating QA's fixtures." |
| 24 | `spark-on-kubernetes-architect` | yes | borderline (`category: data`, k8s adjacent — pairs naturally with `devops-k8s-manifest-reviewer` for data-platform DevOps) | keep — it's optional and the spec explicitly anticipates Spark/Kafka as data-platform-DevOps extensions |
| 25 | `kafka-topic-architect` | yes | borderline (`category: data`, platform-team relevant) | keep — same rationale |
| 26 | `kafka-consumer-pattern-picker` | yes | borderline | keep |
| 27 | `kafka-streams-pipeline-designer` | yes | borderline | keep |
| 28 | `kafka-schema-evolution-architect` | yes | borderline | keep |
| 29 | `imported-voltagent-cloudflare-platform` | yes | yes (Cloudflare platform selection) | keep |
| 30 | `imported-voltagent-cloudflare-workers-best-practices` | yes | yes (Workers code review) | keep |

### Why the two substitutions

**`alert-fatigue-reviewer` (slot 9) is a CDS skill.** Wave-3 Methodology Synthesis put the clinical-decision-support alert-fatigue audit at the bare slug because no DevOps alert-fatigue skill was authored as a standalone — the 12-point fatigue audit lives *inside* `alert-policy-architect` (per `_report_observability-sre.md` line 12). For the DevOps occupation we need a SRE-relevant skill. The best replacement is `slo-designer`: it's the natural counterpart to `alert-policy-architect` (alerts derive from SLO burn-rates per Google SRE Workbook), it's in `niche:observability-sre`, and it closes the SLO → alerting → incident-response → runbook loop the Core 10 is trying to construct.

**`cross-platform-stack-chooser` (slot 23) is a mobile-dev skill.** The slug sounds platform-y, but the body picks React Native vs Flutter vs Kotlin Multiplatform. Wrong tribe. The best replacement is `instrumentation-coverage-reviewer` (also in `niche:observability-sre`, from the same Wave-3 batch as `alert-policy-architect` and `cardinality-cost-reviewer`). It's the missing leg of the observability triangle: coverage first (instrumentation-coverage-reviewer), then cost trim (cardinality-cost-reviewer), then dashboards (observability-dashboard-architect). Adding it makes the observability sub-bundle complete.

Both substitutes already exist in `synth/`. No new authoring required. Verification:

```powershell
Test-Path D:\skillsgit\apps\api\scripts\seed_data\synth\slo-designer.skills.md                       # True
Test-Path D:\skillsgit\apps\api\scripts\seed_data\synth\instrumentation-coverage-reviewer.skills.md  # True
```

Both come from the same `wave3-observability-sre` author batch (commit `b4487aa`) as `alert-policy-architect` and `cardinality-cost-reviewer`, so the voice and rubric style are consistent with the rest of the Core/Supporting set.

## Final 30

The reconciled member set for Wave-3 Curation's `build_devops_vault.py`:

### Core (10)
1. `devops-ci-pipeline-architect`
2. `devops-gha-workflow-optimizer`
3. `devops-k8s-manifest-reviewer`
4. `devops-terraform-module-reviewer`
5. `ops-incident-commander`
6. `ops-runbook-generator`
7. `observability-dashboard-architect`
8. `alert-policy-architect`
9. ~~`alert-fatigue-reviewer`~~ → **`slo-designer`** (substitute: CDS skill replaced with SRE SLO counterpart)
10. `eng-chaos-experiment-planner`

### Supporting (12)
11. `cloud-cost-audit`
12. `cloud-cost-alert-designer`
13. `kubernetes-cost-optimizer`
14. `eng-secrets-architecture-designer`
15. `eng-workload-identity-architect`
16. `artifact-signing-and-verification-designer`
17. `internal-platform-strategy-author`
18. `imported-alirezarezvani-chaos-engineering`
19. `cardinality-cost-reviewer`
20. `imported-google-skills-waf-reliability`
21. `imported-google-skills-waf-cost`
22. `imported-google-skills-networking-observability`

### Optional (8)
23. ~~`cross-platform-stack-chooser`~~ → **`instrumentation-coverage-reviewer`** (substitute: mobile-stack skill replaced with the missing observability-triangle leg)
24. `spark-on-kubernetes-architect`
25. `kafka-topic-architect`
26. `kafka-consumer-pattern-picker`
27. `kafka-streams-pipeline-designer`
28. `kafka-schema-evolution-architect`
29. `imported-voltagent-cloudflare-platform`
30. `imported-voltagent-cloudflare-workers-best-practices`

**Count: 30 (unchanged from spec).** QA's fixture in `tests/integration/test_occupation_flow.py` and `tests/fixtures/vaults/expected-devops-vault/` will need to reflect the two substituted slugs.

### Domain grouping for the vault's `base/` folder layout (per `03-vault-generation.md` §1)

Suggested mapping into the five domain folders the vault format expects:

| Folder | Members |
|---|---|
| `base/ci-cd/` | `devops-ci-pipeline-architect`, `devops-gha-workflow-optimizer`, `artifact-signing-and-verification-designer`, `imported-voltagent-cloudflare-workers-best-practices` |
| `base/observability/` | `observability-dashboard-architect`, `alert-policy-architect`, `slo-designer`, `instrumentation-coverage-reviewer`, `cardinality-cost-reviewer`, `imported-google-skills-networking-observability` |
| `base/infra-as-code/` | `devops-terraform-module-reviewer`, `devops-k8s-manifest-reviewer`, `eng-secrets-architecture-designer`, `eng-workload-identity-architect` |
| `base/incident-response/` | `ops-incident-commander`, `ops-runbook-generator`, `eng-chaos-experiment-planner`, `imported-alirezarezvani-chaos-engineering`, `imported-google-skills-waf-reliability` |
| `base/platform/` | `internal-platform-strategy-author`, `cloud-cost-audit`, `cloud-cost-alert-designer`, `kubernetes-cost-optimizer`, `imported-google-skills-waf-cost`, `cross-platform-stack-chooser` *(if kept)*, `spark-on-kubernetes-architect`, `kafka-topic-architect`, `kafka-consumer-pattern-picker`, `kafka-streams-pipeline-designer`, `kafka-schema-evolution-architect`, `imported-voltagent-cloudflare-platform` |

The grouping above is a suggestion for `occupation.yaml`; Wave-3 Curation may re-bucket without re-validating slugs since the file set is fixed.

## Cross-link recipe seed

Sketch for `apps/api/scripts/seed_data/devops/cross-link-recipe.yaml`. **Wave-3 Curation will author the actual YAML file** — this is a first draft of the structure plus the high-confidence link payload.

Each entry shapes as: `{from: <member-slug>, to: <member-slug>, relation: <enum>}`. The relation enum comes from `apps/api/src/skills/validator.py:142-149`:

```python
class LinkRelation(str, Enum):
    APPLIES = "applies"
    EXTENDS = "extends"
    CONTRADICTS = "contradicts"
    SEE_ALSO = "see-also"
    RECORDED_INSTANCE_OF = "recorded-instance-of"
```

`recorded-instance-of` is for memory neurons → base skills (T-12 territory). The recipe below uses only `applies`, `extends`, `see-also`. We have no `contradicts` pairs (everything in the set is methodology-aligned). Wave-3 may augment with new relations if backend ships them (Backend Wave-1 flagged this as O-4 in `dev-diary-backend-wave1.md` §Open questions for Wave 2).

```yaml
# devops/cross-link-recipe.yaml — Wave 1 draft, ~50 links
# Each link is added to the `from` skill's frontmatter.links[] at build time.
links:

  # ── CI/CD axis ──────────────────────────────────────────────────────
  - {from: devops-ci-pipeline-architect, to: devops-gha-workflow-optimizer, relation: see-also}
  - {from: devops-ci-pipeline-architect, to: artifact-signing-and-verification-designer, relation: extends}
  - {from: devops-ci-pipeline-architect, to: imported-voltagent-cloudflare-workers-best-practices, relation: see-also}
  - {from: devops-gha-workflow-optimizer, to: devops-ci-pipeline-architect, relation: applies}
  - {from: devops-gha-workflow-optimizer, to: artifact-signing-and-verification-designer, relation: see-also}
  - {from: artifact-signing-and-verification-designer, to: devops-ci-pipeline-architect, relation: applies}
  - {from: artifact-signing-and-verification-designer, to: eng-secrets-architecture-designer, relation: see-also}

  # ── IaC axis ────────────────────────────────────────────────────────
  - {from: devops-terraform-module-reviewer, to: devops-k8s-manifest-reviewer, relation: see-also}
  - {from: devops-terraform-module-reviewer, to: eng-secrets-architecture-designer, relation: see-also}
  - {from: devops-k8s-manifest-reviewer, to: devops-terraform-module-reviewer, relation: see-also}
  - {from: devops-k8s-manifest-reviewer, to: eng-workload-identity-architect, relation: see-also}
  - {from: devops-k8s-manifest-reviewer, to: kubernetes-cost-optimizer, relation: see-also}
  - {from: devops-k8s-manifest-reviewer, to: spark-on-kubernetes-architect, relation: see-also}

  # ── Observability triangle ──────────────────────────────────────────
  - {from: instrumentation-coverage-reviewer, to: cardinality-cost-reviewer, relation: see-also}
  - {from: instrumentation-coverage-reviewer, to: observability-dashboard-architect, relation: applies}
  - {from: observability-dashboard-architect, to: instrumentation-coverage-reviewer, relation: applies}
  - {from: observability-dashboard-architect, to: alert-policy-architect, relation: see-also}
  - {from: observability-dashboard-architect, to: slo-designer, relation: applies}
  - {from: cardinality-cost-reviewer, to: instrumentation-coverage-reviewer, relation: applies}
  - {from: cardinality-cost-reviewer, to: cloud-cost-audit, relation: see-also}

  # ── SLO → alerting → incident response chain ────────────────────────
  - {from: slo-designer, to: alert-policy-architect, relation: extends}
  - {from: slo-designer, to: observability-dashboard-architect, relation: see-also}
  - {from: alert-policy-architect, to: slo-designer, relation: applies}
  - {from: alert-policy-architect, to: ops-incident-commander, relation: extends}
  - {from: alert-policy-architect, to: ops-runbook-generator, relation: see-also}
  - {from: ops-incident-commander, to: ops-runbook-generator, relation: applies}
  - {from: ops-incident-commander, to: alert-policy-architect, relation: applies}
  - {from: ops-runbook-generator, to: ops-incident-commander, relation: see-also}

  # ── Chaos / resilience ──────────────────────────────────────────────
  - {from: eng-chaos-experiment-planner, to: imported-alirezarezvani-chaos-engineering, relation: see-also}
  - {from: eng-chaos-experiment-planner, to: ops-incident-commander, relation: see-also}
  - {from: eng-chaos-experiment-planner, to: imported-google-skills-waf-reliability, relation: applies}
  - {from: imported-alirezarezvani-chaos-engineering, to: eng-chaos-experiment-planner, relation: see-also}
  - {from: imported-google-skills-waf-reliability, to: slo-designer, relation: applies}
  - {from: imported-google-skills-waf-reliability, to: eng-chaos-experiment-planner, relation: see-also}

  # ── Cost / FinOps ───────────────────────────────────────────────────
  - {from: cloud-cost-audit, to: cloud-cost-alert-designer, relation: extends}
  - {from: cloud-cost-audit, to: kubernetes-cost-optimizer, relation: see-also}
  - {from: cloud-cost-audit, to: imported-google-skills-waf-cost, relation: applies}
  - {from: cloud-cost-alert-designer, to: cloud-cost-audit, relation: applies}
  - {from: cloud-cost-alert-designer, to: alert-policy-architect, relation: see-also}
  - {from: kubernetes-cost-optimizer, to: cloud-cost-audit, relation: applies}
  - {from: kubernetes-cost-optimizer, to: devops-k8s-manifest-reviewer, relation: see-also}
  - {from: imported-google-skills-waf-cost, to: cloud-cost-audit, relation: see-also}

  # ── Identity / secrets ──────────────────────────────────────────────
  - {from: eng-secrets-architecture-designer, to: eng-workload-identity-architect, relation: extends}
  - {from: eng-secrets-architecture-designer, to: artifact-signing-and-verification-designer, relation: see-also}
  - {from: eng-workload-identity-architect, to: eng-secrets-architecture-designer, relation: applies}
  - {from: eng-workload-identity-architect, to: devops-k8s-manifest-reviewer, relation: see-also}

  # ── Platform / internal developer platform ──────────────────────────
  - {from: internal-platform-strategy-author, to: devops-ci-pipeline-architect, relation: see-also}
  - {from: internal-platform-strategy-author, to: observability-dashboard-architect, relation: see-also}
  - {from: internal-platform-strategy-author, to: ops-runbook-generator, relation: see-also}

  # ── Data-platform extensions (optional cluster) ─────────────────────
  - {from: spark-on-kubernetes-architect, to: devops-k8s-manifest-reviewer, relation: applies}
  - {from: spark-on-kubernetes-architect, to: kubernetes-cost-optimizer, relation: see-also}
  - {from: kafka-topic-architect, to: kafka-consumer-pattern-picker, relation: extends}
  - {from: kafka-topic-architect, to: kafka-schema-evolution-architect, relation: see-also}
  - {from: kafka-consumer-pattern-picker, to: kafka-streams-pipeline-designer, relation: see-also}
  - {from: kafka-streams-pipeline-designer, to: kafka-topic-architect, relation: applies}
  - {from: kafka-schema-evolution-architect, to: kafka-topic-architect, relation: applies}

  # ── Networking ──────────────────────────────────────────────────────
  - {from: imported-google-skills-networking-observability, to: observability-dashboard-architect, relation: see-also}
  - {from: imported-google-skills-networking-observability, to: ops-incident-commander, relation: see-also}

  # ── Cloudflare cluster ──────────────────────────────────────────────
  - {from: imported-voltagent-cloudflare-platform, to: imported-voltagent-cloudflare-workers-best-practices, relation: extends}
  - {from: imported-voltagent-cloudflare-workers-best-practices, to: devops-ci-pipeline-architect, relation: see-also}
```

**Count: 60 links across 30 skills.** Every link is bi-directionally meaningful (the inverse link is implied — but the file format only stores outbound links per ADR-007, so the inverse pairs are explicitly listed where they add value, e.g. `slo-designer ↔ alert-policy-architect`).

Average ≈ 2.0 outbound links per skill, with hubs at `observability-dashboard-architect` (5 in/out), `devops-ci-pipeline-architect` (6 in/out), and `ops-incident-commander` (4 in/out). Sparse skills (1 link each) are the niche optional ones: `imported-google-skills-waf-cost`, the Kafka cluster's end-leaves.

## Open questions for Wave 3

1. **Substitution acceptance** — does the Architect / QA accept the `alert-fatigue-reviewer → slo-designer` and `cross-platform-stack-chooser → instrumentation-coverage-reviewer` swaps? If not, fallback options:
   - For slot 9 (alert-fatigue): drop to 29 and let `alert-policy-architect`'s embedded 12-point fatigue audit cover the gap; or author a new `devops-alert-fatigue-reviewer.skills.md` (Wave-2/3 work, not Wave-1 inventory).
   - For slot 23 (cross-platform): keep `cross-platform-stack-chooser` even though it's mobile (the spec brief said "Curation may swap any optional slot"); or substitute `developer-experience-metrics-designer` or `developer-portal-architect` (also platform-engineering relevant, both exist in `synth/`).

2. **Cross-link relation extensibility** — Backend Wave-1 flagged in `dev-diary-backend-wave1.md` §Open questions item 4 that adding `requires` / `supersedes` to `LinkRelation` is non-breaking but coordinated. The recipe seed above doesn't need those, but a few links currently typed as `extends` are arguably `requires` (`slo-designer → alert-policy-architect` because alerts depend on SLO definitions). Wave-3 should decide: ask Backend to add `requires`, or keep using `extends` with the looser semantic.

3. **Domain folder layout assignments** — the suggested grouping in §Final 30 puts the Kafka cluster under `base/platform/`. That's a stretch (Kafka is more naturally a `data-platform/` folder). Wave-3 may want to add a sixth domain folder for data-platform skills, but the vault-format spec (`03-vault-generation.md` §1) only enumerates 5. Decision: stretch `platform/` to include data-platform, OR ask the Architect to extend the spec's folder list.

4. **`alert-fatigue-reviewer` future home** — if the substitution is accepted, the CDS skill stays in the library but stops being part of the DevOps occupation. It'll still be discoverable by buyers via search/tag, just not bundled. No file deletion required.

5. **`vault_path` for occupation members** — the validator (Backend Wave-1) rejects creator-set `vault_path`. The vault builder is supposed to set it. T-08 should write `vault_path: "base/<domain>/<slug>"` when emitting each member into the bundle. Wave-3 should confirm Backend's vault builder (T-06) sets this field at build time, not Curation. (Curation only authors the recipe; T-06 emits the file with the field.)
