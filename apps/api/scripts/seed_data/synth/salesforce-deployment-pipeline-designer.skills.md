---
id: skillsgit-curated/salesforce-deployment-pipeline-designer
version: 1.0.0
name: Salesforce Deployment Pipeline Designer
description: Design a Salesforce DX CI/CD pipeline with scratch orgs, source tracking, package versioning, smoke tests, and rollback.
authors:
  - name: Wave-3 Synthesis Agent
    handle: synth-wave3
    role: author
category: enterprise-software
tags:
  - niche:salesforce-development
  - sfdx
  - ci-cd
  - deployment
  - scratch-org
  - unlocked-package
  - github-actions
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - claude-haiku-4-5
    - gpt-4o
  min_context_tokens: 24000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - sfdx pipeline
  - salesforce ci cd
  - scratch org workflow
  - unlocked package
  - github actions salesforce
  - sandbox lifecycle
  - deploy salesforce
  - source tracking
  - rollback salesforce
  - sf cli pipeline
example_invocations:
  - Design a CI/CD pipeline for our Salesforce team using GitHub Actions and scratch orgs.
  - We want to move from change-set deploys to source-driven. What does the pipeline look like?
  - Help me build an unlocked-package release flow with smoke tests.
  - What is the right sandbox lifecycle for a team of eight Salesforce developers?
inputs:
  - name: team_profile
    type: text
    required: true
    description: Team size, roles (developer/admin/consultant), CI host (GitHub / GitLab / Jenkins / Azure DevOps), and target environments.
  - name: project_shape
    type: choice
    required: true
    description: Source organisation that will run through the pipeline.
    choices: [org-development, unlocked-packages, second-generation-managed-package, hybrid]
  - name: constraints
    type: text
    required: false
    description: Compliance, data-residency, security-review, or budget constraints.
outputs:
  - name: pipeline_design
    type: markdown
    description: Stage-by-stage pipeline design with concrete commands and gate criteria.
  - name: starter_workflow
    type: markdown
    description: A skeleton GitHub Actions workflow (or pseudo-equivalent for other CI hosts).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Salesforce Deployment Pipeline Designer

## When to use

Use this skill when a Salesforce team needs a CI/CD pipeline designed from
scratch, or when an existing pipeline is being upgraded (change sets → source
DX, unmanaged → unlocked packages, single sandbox → multi-environment, manual
deploys → automated). Trigger on phrases like "design a Salesforce pipeline",
"set up scratch orgs", "GitHub Actions for SFDX", "what is the right sandbox
lifecycle", "we want to package our metadata".

Do not use this skill for:

- Authoring a specific deployment artefact (a `package.xml`, a destructive
  changes file). This skill designs the pipeline; the developer authors the
  artefacts.
- Pure Apex/LWC reviews — see the Apex reviewer skill.
- Production-incident response — that needs an incident playbook, not a
  pipeline design.

## How to apply

### Step 1 — Establish the project shape

Pick one of:

- **Org Development Model.** Source of truth is a sandbox; metadata is
  retrieved into source control as it changes. Simpler; suited to teams with
  many admin-driven changes and few developers. Deployment unit: metadata
  delta computed against the target environment.
- **Unlocked Packages.** Metadata is partitioned into one or more unlocked
  packages owned by a Dev Hub. Each package is versioned. Deployment unit: a
  package version (`04t...` id). Recommended default for new green-field work
  with ≥ 3 developers.
- **Second-Generation Managed Package (2GP).** Same mechanics as unlocked, but
  the package is signed for AppExchange distribution; carries namespacing,
  security-review obligations, and stricter API-version constraints. Required
  for ISV work.
- **Hybrid.** Some metadata in unlocked packages (the bits that are
  shareable / namespaced); the long tail (page layouts, reports, dashboards)
  remains org-tracked. Common in mature orgs.

The choice drives every other decision. Refuse to design the pipeline until
this is settled.

### Step 2 — Sandbox lifecycle

Map each environment to a role and a refresh cadence:

| Environment        | Purpose                                              | Source                | Refresh cadence | Auto-deploy from   |
|--------------------|------------------------------------------------------|-----------------------|-----------------|--------------------|
| Scratch org        | Per-developer / per-feature ephemeral org            | Dev Hub               | Per branch      | local + PR builds  |
| Developer Pro      | Long-lived feature branch integration                | Production sandbox    | Weekly          | `feature/*` merges |
| Partial Copy       | UAT with realistic data                               | Production subset     | Per release     | `release/*` branch |
| Full Copy          | Pre-prod, performance, training                       | Production full       | Per release     | `main` (pre-prod)  |
| Production         | Live                                                  | Customer org          | n/a             | `main` (tag)       |

For small teams (≤ 3 developers) collapse Developer Pro into Partial Copy.
For ISV teams, the lifecycle is package-version-centric: scratch → packaging
org → linked subscriber test orgs.

### Step 3 — Branching model

Default to a trunk-based model with short-lived feature branches:

- `main` — protected, always deployable to production. Every commit is
  associated with a passing pipeline run.
- `feature/<ticket>` — branched off `main`. PR back to `main`. CI on push,
  full validation on PR open.
- `release/<version>` — only used in the unlocked-package and 2GP models, to
  freeze the candidate while smoke tests run in Partial/Full Copy.
- `hotfix/<ticket>` — branched off the production tag, fast-tracks to `main`
  via cherry-pick after deploy.

GitFlow's long-lived `develop` branch is **not recommended** for Salesforce —
source tracking conflicts grow super-linearly with branch age and merge cost
quickly exceeds the benefit.

### Step 4 — Pipeline stages

Design six stages. Each has a clear gate that, when broken, halts promotion.

#### Stage A — Static analysis (pre-merge, every push)

Runs on the CI host's standard runner; no Salesforce org needed.

Tools (all permissively licensed):

- `forcedotcom/code-analyzer` (BSD-3-Clause) — invokes PMD, ESLint, RetireJS,
  and the Salesforce Graph Engine under one CLI. Required check.
- `prettier-plugin-apex` (verify license per release) — formatting; not a gate,
  but a lint warning.
- LWC ESLint config from `salesforce/eslint-config-lwc` — required check on
  any `*.js` under `force-app/main/default/lwc/**`.

Gate: zero high-severity violations, zero formatting drift on changed files.

#### Stage B — Scratch org integration (pre-merge, every PR)

Steps:

1. Authenticate to the Dev Hub using a JWT bearer flow with a server key
   secret. **Never** use the username/password OAuth flow in CI.
2. `sf org create scratch --definition-file config/project-scratch-def.json
   --duration-days 1 --no-namespace`. Set `--duration-days 1` for PR runs to
   keep the active scratch org count low; production-blocking runs may pin to
   7 days.
3. `sf project deploy start --source-dir force-app --wait 30` (or
   `sf package install` for unlocked-package consumers).
4. Optional: `sf data tree import` to seed sample data.
5. `sf apex test run --code-coverage --result-format json --wait 30 --test-level RunLocalTests`.
6. Capture coverage; fail if overall < 85% or any single class < 75%
   (production deploy requires ≥ 75%; CI uses the stricter floor).
7. `sf org delete scratch --target-org <alias> --no-prompt`. Always run in a
   cleanup step, including on failure, to avoid Dev Hub limit pollution.

Gate: scratch deploy succeeds, all local tests pass, coverage threshold met.

#### Stage C — Package versioning (post-merge, unlocked-package and 2GP only)

On merge to `main`:

1. `sf package version create --package <pkgAlias> --installation-key-bypass
   --code-coverage --wait 30 --branch main`. Pin the branch so subscriber
   metadata tracks the source branch.
2. Capture the `SubscriberPackageVersionId` (`04t...`) as a build artefact.
3. Promote to released only after Stage E passes:
   `sf package version promote --package <04t...> --no-prompt`.
4. Commit a `sfdx-project.json` bump (a new dependency entry referencing the
   `04t...`) back to `main` via an automated PR.

Gate: package version creates successfully; code coverage in the package
context ≥ 75%.

#### Stage D — Sandbox deployment (post-merge, gated)

For org-development: deploy the metadata delta to Developer Pro on every
merge to `main`. For package models: install the new package version into
Developer Pro.

Commands:

- `sf project deploy start --source-dir force-app --target-org devpro
  --test-level RunSpecifiedTests --tests <changed-and-related>
  --ignore-conflicts=false`.
- `sf package install --package <04t...> --target-org devpro --wait 20`.

Gate: deploy succeeds without conflicts. A conflict ("Source Conflict
detected") on a non-source-tracked sandbox means someone changed the sandbox
directly — this should fail the build and surface a "drift detected" alert,
not be silently `--ignore-conflicts=true`'d.

#### Stage E — UAT smoke tests (release candidate)

Triggered by tagging or branching `release/<version>` from `main`.

Steps:

1. Deploy / install into Partial Copy.
2. Run a curated smoke suite — Apex tests tagged `@isTest(SeeAllData=false)`
   plus a UI smoke pass via Playwright or a Salesforce-aware tool. Smoke
   coverage targets the top user journeys, not unit-level paths.
3. Run security checks: `sf code-analyzer run --target force-app
   --rule-selector security` and assert zero high-severity findings.
4. Manual UAT sign-off captured as a PR approval on the release branch.

Gate: all smoke pass, no new high-severity security findings, UAT sign-off
recorded.

#### Stage F — Production deploy

Triggered by tagging `vX.Y.Z` on `main` after Stage E passes.

Pre-deploy checklist (machine-checked where possible):

- Validation deploy: `sf project deploy validate --target-org prod
  --test-level RunSpecifiedTests --tests <changed-and-related> --wait 60`.
  The returned `quickDeployId` is captured.
- Change announcement posted to the team channel.
- Maintenance window confirmed.

Deploy:

- `sf project deploy quick --quickdeploy-id <id> --target-org prod --wait 60`
  for org development.
- `sf package install --package <04t...> --target-org prod --wait 30
  --security-type AdminsOnly` for unlocked / 2GP.

Post-deploy:

- Run a post-deploy Apex script if needed (`sf apex run -f scripts/post-deploy.apex`).
- Smoke a known-good user journey.
- Verify scheduled jobs were preserved (`sf data query --query "SELECT Id,
  CronExpression, NextFireTime FROM CronTrigger"`).

### Step 5 — Rollback strategy

Salesforce production has **no built-in rollback**. Plan accordingly.

For each release define:

1. **Forward fix path** — the default. Identify the broken metadata, ship a
   corrective release through Stage F (often hotfix-fast-tracked).
2. **Reverse deploy** — keep the previous package version `04t...` (or a
   `mdapi:retrieve` archive of the prior production state) as a build artefact
   for the last 5 releases. Reverse-deploy by installing the older package
   version, or by deploying the archived metadata with `--destructive-changes`
   for components added in the broken release.
3. **Data rollback** — if the release wrote data (migrations, backfills),
   capture a `sf data query --query-all` snapshot of affected records before
   the migration; provide a `bulk:update` script to restore.
4. **Feature flag fallback** — when the change is gated behind a custom
   metadata feature flag, "rollback" is flipping the flag, which is instant.
   Prefer this for any high-risk feature.

A release plan that lacks a documented rollback path should be blocked in
Stage E review.

### Step 6 — Secrets and authentication

- Use JWT bearer flow with a server key. The connected app has the JWT
  certificate uploaded; CI stores the private key as a masked secret
  (`SF_JWT_KEY`), the consumer key as `SF_CONSUMER_KEY`, and the auth
  username as `SF_AUTH_USERNAME`.
- `sf org login jwt --jwt-key-file <key> --client-id <consumer-key>
  --username <username> --alias prod --set-default`.
- Rotate the JWT certificate annually and after any suspected compromise.
- Never echo `sf org display --verbose` in CI logs — it includes the access
  token.
- Use OIDC federation where the CI host supports it (GitHub Actions supports
  AWS / GCP OIDC out of the box; Salesforce JWT is the equivalent here).

### Step 7 — Observability

The pipeline should produce:

- A per-run summary comment on the PR with deploy result, test result,
  coverage delta, and code-analyzer delta.
- A persisted artefact bundle: `package-version-id.txt`, `test-results.xml`,
  `code-analyzer-results.json`, `validation-deploy-id.txt`. Retained 90 days.
- A deploy log written to the Salesforce org via Nebula Logger (MIT) on
  post-deploy with the release tag and commit SHA. This gives auditors a
  single in-org trail.

### Step 8 — Emit the starter workflow

Provide a skeleton GitHub Actions workflow that the user can adapt. Use it as
pseudo-code if the user is on GitLab/Jenkins/Azure DevOps — the stages map
1:1 across CI hosts. Reference `github/octoforce-actions` (MIT) as a worked
example the user can fork.

```yaml
name: salesforce-pipeline
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
    tags: ['v*']

jobs:
  static-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint
      - run: npx @salesforce/cli code-analyzer run --target force-app

  scratch-org-test:
    needs: static-analysis
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install sf
        run: npm install -g @salesforce/cli
      - name: Auth Dev Hub
        env:
          SF_JWT_KEY: ${{ secrets.SF_JWT_KEY }}
          SF_CONSUMER_KEY: ${{ secrets.SF_CONSUMER_KEY }}
          SF_AUTH_USERNAME: ${{ secrets.SF_AUTH_USERNAME }}
        run: |
          echo "$SF_JWT_KEY" > server.key
          sf org login jwt --jwt-key-file server.key \
            --client-id "$SF_CONSUMER_KEY" \
            --username "$SF_AUTH_USERNAME" \
            --alias devhub --set-default-dev-hub
      - run: sf org create scratch -f config/project-scratch-def.json -a ci -d 1
      - run: sf project deploy start -d force-app -o ci -w 30
      - run: sf apex test run -o ci -l RunLocalTests -w 30 -c -r json
      - if: always()
        run: sf org delete scratch -o ci -p

  package-version:
    needs: scratch-org-test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      # auth as above
      - run: sf package version create -p MyPackage -x -c -w 30 --branch main
        # capture 04t... id as artifact

  prod-deploy:
    needs: package-version
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    environment: production   # requires manual approval gate
    steps:
      # auth as above, target prod
      - run: sf package install -p <04t...> -o prod -w 30 --security-type AdminsOnly
```

Adapt thresholds, environment names, and the package id to the team's reality.

## Inputs

- `team_profile` (required) — team size, role mix, CI host, target environments.
- `project_shape` (required) — drives whether the design centres on metadata
  deploys or package versions.
- `constraints` (optional) — packaging org, security-review, compliance.

## Outputs

- `pipeline_design` (markdown) — the full stage-by-stage plan as a doc the
  team can paste into their wiki.
- `starter_workflow` (markdown) — the workflow skeleton above, customised
  with the user's branch and environment names.

## Examples

### Example 1 — 6-developer team, unlocked packages, GitHub

Output: project_shape=unlocked-packages, sandbox lifecycle of
scratch → Developer Pro → Partial → Full → Prod, branching trunk-based,
all six pipeline stages active, JWT auth, octoforce-actions referenced as
the starter.

### Example 2 — 2-developer team, org-development model, GitLab

Output: project_shape=org-development, collapsed lifecycle (scratch →
Partial → Prod), trunk-based with feature branches, Stages A/B/D/F only
(skip Stage C package versioning, skip Stage E full UAT and rely on Partial
smoke tests), the pseudo-workflow translated to a `.gitlab-ci.yml`.

## Limitations

- **No live org inspection.** This skill cannot examine the current org's
  technical debt to recommend a phased migration; it designs the target
  pipeline. Pair with a discovery / debt-assessment skill.
- **CI-host coverage.** The skeleton is GitHub Actions. GitLab, Jenkins,
  Azure DevOps, and Bitbucket Pipelines have the same stage structure but
  different YAML; translate accordingly.
- **2GP packaging nuances.** Managed-package-2GP signing, namespace
  registration, and version-deprecation flows are described at the policy
  level here; specific AppExchange security-review submission requires
  Salesforce-internal templates that this skill cannot reproduce.
- **Source-thinness disclosure.** A meaningful chunk of authoritative
  Salesforce CI/CD doctrine lives in vendor blogs (Copado, Gearset,
  Flosum, Salto, AutoRABIT) under proprietary terms, or in the AGPL-licensed
  `sfdx-hardis` tool (explicitly rejected here). Permissively-licensed
  reference material is thinner: primarily `github/octoforce-actions` (MIT),
  `forcedotcom/code-analyzer` (BSD-3-Clause), `forcedotcom/sfdx-core`
  (BSD-3-Clause), and `SFDO-Tooling/CumulusCI` (BSD-3-Clause, Salesforce.org's
  open-source pipeline framework). The design above synthesises common
  practice from those sources and the synthesist's own model of the SF CLI
  command surface.
