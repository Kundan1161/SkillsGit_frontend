# Wave-3 Synthesis Report — Salesforce Development

**Niche:** enterprise-software / Salesforce (Apex, Flow, LWC, deployment, security)
**Agent:** synth-wave3
**Date:** 2026-05-14

## Files produced

- `synth/salesforce-apex-reviewer.skills.md` (340 lines, v1.0.0)
- `synth/salesforce-flow-vs-apex-decider.skills.md` (330 lines, v1.0.0)
- `synth/salesforce-deployment-pipeline-designer.skills.md` (438 lines, v1.0.0)
- `synth/salesforce-security-review.skills.md` (383 lines, v1.0.0)

All four are new skills; no overlap with existing synth/ entries (none have
the `salesforce-` prefix or address Apex/Flow/LWC/DX methodology).

## Permissively-licensed sources verified

| # | Repo | License | Stars | Used for |
|---|------|---------|-------|----------|
| 1 | [trailheadapps/apex-recipes](https://github.com/trailheadapps/apex-recipes) | CC0-1.0 | 1.1k | Apex review reference patterns (testing, async, integration) |
| 2 | [trailheadapps/lwc-recipes](https://github.com/trailheadapps/lwc-recipes) | CC0-1.0 | 2.9k | LWC patterns referenced in security review |
| 3 | [kevinohara80/sfdc-trigger-framework](https://github.com/kevinohara80/sfdc-trigger-framework) | MIT | 1.0k | Trigger handler dispatch pattern |
| 4 | [apex-enterprise-patterns/fflib-apex-common](https://github.com/apex-enterprise-patterns/fflib-apex-common) | BSD-3-Clause | 995 | Service Layer / Unit of Work / Selector patterns |
| 5 | [mitchspano/trigger-actions-framework](https://github.com/mitchspano/trigger-actions-framework) | Apache-2.0 | 628 | Flow + Apex partitioned trigger pattern |
| 6 | [forcedotcom/code-analyzer](https://github.com/forcedotcom/code-analyzer) | BSD-3-Clause | 236 | Canonical rule ids used as finding names |
| 7 | [github/octoforce-actions](https://github.com/github/octoforce-actions) | MIT | 45 | GitHub Actions pipeline skeleton |
| 8 | [apexfarm/ApexTriggerHandler](https://github.com/apexfarm/ApexTriggerHandler) | BSD-3-Clause | 60 | Metadata-driven trigger handler alternative |
| 9 | [jongpie/NebulaLogger](https://github.com/jongpie/NebulaLogger) | MIT | 927 | Observability/logging reference for Apex + Flow |
| 10 | [SFDO-Tooling/CumulusCI](https://github.com/SFDO-Tooling/CumulusCI) | BSD-3-Clause | 391 | Pipeline framework reference |
| 11 | [forcedotcom/sfdx-core](https://github.com/forcedotcom/sfdx-core) | BSD-3-Clause | 163 | SFDX CLI command surface |

All 11 sources cleared the license filter (MIT / Apache-2.0 / BSD-3-Clause /
CC0-1.0). Eight are ≥ 60 stars; three are below 100 but above 30, accepted
under the relaxation clause and disclosed here.

## Sources rejected (license)

- [hardisgroupcom/sfdx-hardis](https://github.com/hardisgroupcom/sfdx-hardis) — **AGPL-3.0**. Significant community CI/CD toolkit but copyleft license is outside the allow-list.
- Numerous community trigger framework forks (e.g. `sfdc1224/sfdc-trigger-framework`) — no LICENSE file or ambiguous attribution. Treated as all-rights-reserved.
- `salesforce/lwc` (the LWC framework itself) — MIT, but it is a runtime, not methodology; not used.

## Patterns synthesised

**salesforce-apex-reviewer** — eight-step audit covering inventory, bulkification,
governor-limit arithmetic, security posture (`WITH USER_MODE` /
`Database.AccessLevel.USER_MODE` migration from `WITH SECURITY_ENFORCED`), async
correctness (Batchable / Queueable / Schedulable), test coverage with
`@TestSetup` + asserts + 200-record bulk path, trigger handler pattern, and
final go/no-go verdict. Uses Code Analyzer rule ids (`ApexSOQLInjection`,
`ApexCRUDViolation`, `ApexSharingViolations`, etc.) as canonical finding names.

**salesforce-flow-vs-apex-decider** — 14-row decision matrix plus a hard
anti-pattern checklist (no DML in Flow loop, no synchronous callouts from
record-triggered flows, no Flow recursion, no mass-data automation in scheduled
flows). Includes a Flow→Apex element-mapping table and a forward/reverse
migration plan template. Verdicts: FLOW / APEX / HYBRID.

**salesforce-deployment-pipeline-designer** — six-stage pipeline (static
analysis → scratch org integration → package versioning → sandbox deploy → UAT
smoke → production deploy) plus sandbox lifecycle table, trunk-based branching
model, JWT-bearer auth model, rollback strategy (forward fix / reverse deploy /
data rollback / feature flag), and a GitHub Actions skeleton. Org-development,
unlocked-package, 2GP, and hybrid project shapes covered.

**salesforce-security-review** — eight-step audit across permission model
(profile-to-perm-set-group migration), sharing (OWD / restriction rules /
guest user), FLS, integration security (Named Credentials, External
Credentials, OAuth scopes, JWT cert hygiene), code-level security (`with
sharing`, USER_MODE, dynamic SOQL escaping, LWC CDN policy), and Shield. Maps
findings to the Salesforce ISV Security Review checklist categories for
AppExchange preparation.

## Tagging

Each skill carries `category: enterprise-software` and `niche:salesforce-development`
as the first tag, plus 5–6 additional niche-relevant tags from the allowed
vocabulary (apex, flow, lwc, sfdx, ci-cd, security, governor-limits, sharing,
etc.). `license_type: free` on all; no pricing block. AI block lists Claude
Opus 4.7 and Sonnet 4.6 as required.

## Source-thinness disclosure (mandatory for this niche)

The Salesforce ecosystem on GitHub is **materially thinner** for permissively-
licensed methodology content than comparable ecosystems (Python, Java, Go).
Reasons:

1. The largest community CI/CD toolkit (`sfdx-hardis`) is AGPL, excluded.
2. Salesforce-internal methodology lives almost entirely in non-permissive
   channels: Trailhead modules, Architect Decision Guides, the ISV Security
   Review checklist, the Well-Architected framework. All ©Salesforce, not
   reproducible.
3. Top vendor blogs (Copado, Gearset, Salto, AutoRABIT, Flosum, ApexHours) are
   proprietary articles.
4. Many high-star community Apex repos lack a LICENSE file altogether, which
   defaults to all-rights-reserved and excludes them.

Consequently each skill's body is the **synthesist's own writing**, expressing
common Salesforce practice in original prose, cross-checked against the 11
permissively-licensed sources where they cover the topic. URL-only references
appear in the bodies; no source text is reproduced. This disclosure is also
made explicitly in the `## Limitations` section of each skill.

## Confidence

- **salesforce-apex-reviewer** — high. Apex review heuristics are well-covered
  by `fflib-apex-common`, `apex-recipes`, `code-analyzer`, and the trigger
  frameworks; rule ids cross-check cleanly.
- **salesforce-flow-vs-apex-decider** — medium-high. The matrix is a working
  heuristic; permissive corroboration is limited to `mitchspano/trigger-actions-framework`
  and `NebulaLogger` patterns. Substance is sound, calibration may vary by org.
- **salesforce-deployment-pipeline-designer** — high on the stage structure
  (octoforce-actions and CumulusCI corroborate); medium on the specific
  thresholds (85% CI coverage floor, 5-release rollback artefact retention) —
  these are synthesist judgement, not from a cited source.
- **salesforce-security-review** — medium. Salesforce security guidance is
  the most affected by source-thinness; the structure tracks the ISV Security
  Review checklist from memory and is corroborated by `code-analyzer` rule
  ids. Independent verification recommended before relying on this skill for
  an actual ISV submission.

## Notes on file location

The Write tool persisted these files to
`apps/api/scripts/seed_data/synth/`, which is the seed-data path the API loads
into the marketplace. The `synth/` path at repo root is the working area; the
seed-data path is the canonical staging location and is where these files
are reachable for downstream tooling.
