---
id: skillsgit-curated/gha-workflow-optimizer
version: 1.0.0
name: GitHub Actions Workflow Optimizer
description: Review GitHub Actions workflows for cost, speed, security posture, and reliability — flag wasted minutes, third-party-action risk, and missing concurrency or caching.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:devops-iac, github-actions, ci-cd, workflow-optimization, supply-chain, cost-optimization, runners]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  tools_optional: [web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - optimize github actions
  - review gha workflow
  - speed up github actions
  - cut ci minutes
  - github actions cost
  - workflow review
  - actions security review
  - reusable workflow review
  - matrix optimization
  - cache strategy github actions
  - concurrency group github
  - pin actions sha
example_invocations:
  - "Our CI minutes bill doubled this month. Review these workflows and tell me where the waste is."
  - "Audit our GitHub Actions workflows for security and supply-chain risk."
  - "These three workflows all rebuild the same image. Help me consolidate without losing PR coverage."
inputs:
  - name: workflows
    type: text
    required: true
    description: Contents of `.github/workflows/*.yml` files. Multiple files welcome; note file boundaries in comments.
  - name: usage_signal
    type: text
    required: false
    description: Recent run stats — average duration, queue time, cost per month, frequency of triggers; anything that hints where the pain is.
  - name: repo_shape
    type: text
    required: false
    description: Monorepo / polyrepo, primary language(s), runner type (GitHub-hosted vs self-hosted vs hybrid), and any constraints (e.g., enterprise rules).
  - name: optimization_priority
    type: choice
    required: false
    description: Which axis the reviewer should weight most heavily.
    choices: [cost, speed, security, reliability, all]
outputs:
  - name: optimization_report
    type: markdown
    description: Triaged findings (security blockers first, then high-leverage perf/cost wins, then nits) with concrete per-workflow recommendations and an estimated savings note where calculable.
  - name: findings_json
    type: json
    description: Machine-readable findings for tooling ingestion.
---

# GitHub Actions Workflow Optimizer

## When to use

Use this skill when a team hands you one or more GitHub Actions workflow files and asks for a review that goes beyond "does it run?" The common triggers are: an unexplained jump in CI minutes (cost); slow merges (speed); a security audit finding (supply chain); flakiness causing retries (reliability); or consolidation after a migration where multiple workflows accumulated and now overlap.

The skill applies to repositories of any language. It applies whether workflows run on GitHub-hosted runners, self-hosted runners, or a hybrid. It applies whether the team uses reusable workflows, composite actions, both, or neither. Output severity weights are tuned by the optimization priority the user names.

It does not apply to: writing new workflows from scratch (use the pipeline-architect skill instead); debugging a specific run failure (that needs the log, not the YAML); or migrating workflows from another CI tool (that has different scaffolding concerns). For those, prefer dedicated tools.

The bar applied is "would a careful platform engineer be happy to inherit these workflows tomorrow without surprises?" Surprises include unsigned third-party actions, runners that retain state between jobs, secrets leaked into untrusted contexts, and matrix legs that double the bill silently.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `workflows` | yes | The YAML under review. |
| `usage_signal` | no | Actual run data that pinpoints the pain. |
| `repo_shape` | no | Repository topology, primary language, runner choices. |
| `optimization_priority` | no | Which axis to weight heaviest. |

## How to apply

The agent walks the workflows deterministically. Each stage produces structured findings; the final stages rank and render them.

### Stage 1 — Inventory

1. Parse every workflow. Build a table of workflows, jobs, and steps. Note the triggers (`on:`) for each workflow.
2. Identify *trigger overlap*. Workflows that share `pull_request` and `push` triggers commonly duplicate work. Flag overlap.
3. Identify *runner choice* per job. `runs-on: ubuntu-latest` is the default; `runs-on: [self-hosted, label]` and matrix selectors are alternatives. Each has cost and risk implications.
4. Identify *third-party actions* (anything under `uses:` that does not start with `actions/` or the team's own org). Build a list; the supply-chain review uses it.
5. Identify *reusable workflows* (`workflow_call`) and *composite actions* used. Note whether the references are pinned by SHA, tag, or floating ref.

### Stage 2 — Security and supply chain

6. Every third-party action `uses:` reference is pinned to a full commit SHA, not to a tag. Pinning by tag is a Major; pinning by floating ref (`@main`, `@master`, no ref) is a Blocker.
7. The team's own org actions can use semver tags if the org enforces release immutability; flag if the org policy isn't documented.
8. Every job declares explicit `permissions:`. Workflow-level or job-level `permissions:` with the minimum needed is the pattern. Missing `permissions:` (relying on the repo default) is a Major; an explicit `contents: write` or `id-token: write` without justification is a Major.
9. `GITHUB_TOKEN` permissions follow least-privilege. Read-only is the default in most modern repos; if the workflow needs write, it's scoped.
10. `pull_request_target` is used only where strictly required (a workflow that needs to access secrets on PRs from forks). It runs in the context of the base ref with full secrets; mishandling is the single most common supply-chain exploit in the ecosystem. Any `pull_request_target` workflow that checks out the PR head and runs untrusted code from it is a Blocker.
11. Workflows that handle PRs from forks do not pass secrets to untrusted code. `env:` inside a step that runs user-supplied scripts is a Major.
12. Secrets are referenced via `secrets.NAME`; never logged. The agent looks for patterns that print env into logs (`env | sort`, `printenv`, `set -x` near a secret reference). Each is a Blocker.
13. Self-hosted runners are only used for trusted contexts — never on `pull_request` from public-repo forks. Self-hosted on a public repo's PRs is a Blocker.
14. Self-hosted runners are ephemeral (a fresh VM/container per job). Persistent runners are a Major for any workload touching secrets.
15. OIDC federation (with cloud providers) replaces long-lived access keys. Static cloud credentials in secrets are a Major where OIDC is available.
16. `permissions: id-token: write` is scoped to jobs that need it for OIDC, not workflow-wide.
17. `concurrency` is set on workflows that should not race themselves (deploy workflows, release workflows). Missing is a Major.
18. Reusable workflows passing secrets do so with explicit `secrets:` inheritance, not `secrets: inherit` unless the called workflow is owned by the same team.
19. Caches do not store secrets. A step that caches a directory containing decoded secret files is a Blocker.
20. Workflow `env:` does not contain secrets — only `secrets.X` references inside steps that need them.

### Stage 3 — Speed: caching

21. Dependency installs are cached. For Node, `actions/setup-node` with `cache:` enabled or `actions/cache` keyed on the lockfile. For Python, `actions/setup-python` with `cache:` enabled or `pip-tools` lockfile. For Go, `actions/setup-go` with the module cache. For Java, the relevant Maven/Gradle cache action. Missing dependency caching is a Major when the install step is more than a few seconds.
22. Cache keys include the lockfile hash. A cache key of `${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}` is correct; a key without the hash is stale-prone (Major).
23. Restore keys provide fallback for partial hits: a primary key (full lockfile hash) and a restore key (lockfile-prefix or none) so cold branches still warm-fill.
24. Build outputs are cached where deterministic. Compiled binaries, generated code, and test fixtures are all candidates. Specifically for Rust (`Cargo` target/), for Gradle/Maven (build outputs), for Bazel (the remote-cache pattern), for Docker layers (`docker/build-push-action` with `cache-from` and `cache-to`). Missing layer caching is a Major for container builds.
25. The cache is bounded. A cache larger than ~500MB warrants discussion; GitHub eviction is LRU and a large cache may push out smaller more-valuable ones. Note when caches are over-stuffed.
26. The cache is scoped. Branch-level caches are normal; cross-branch caches help shared dependencies but require care about race conditions.

### Stage 4 — Speed: parallelism

27. Matrix builds are used where the build is naturally parallel (multi-version test, multi-OS test, sharded test suite). Missing matrix where it applies is a Minor; over-matrix (every language version on every OS when the team only ships one) is a Major (cost).
28. `fail-fast: false` is set deliberately. Default `fail-fast: true` cancels other legs when one fails, which is fine for "do they all pass?" gating but wrong for "show me every failure at once" diagnostics. Note when defaults look misaligned.
29. Jobs that can run in parallel are not chained via `needs:`. Spurious `needs:` is a Major (waste of wall-clock).
30. Test sharding is in place when test runtime exceeds a threshold (a few minutes). Recommend the test framework's native sharding.
31. Independent linting/formatting/type-checking steps run in their own jobs, not serialized in one job, so they fail in parallel.
32. Long jobs are split. A 45-minute monolithic job hides the slow step; split for visibility.

### Stage 5 — Speed: avoiding work

33. `paths:` filters on `pull_request` and `push` triggers prevent unrelated changes from running the full pipeline. A monorepo without path filters is a Major.
34. `paths-ignore:` documents intent (e.g., never run on docs-only changes).
35. The "should I run?" check is itself cheap. A `setup-node` + `install` just to decide there's nothing to do defeats the purpose; lightweight change-detection (e.g., `dorny/paths-filter`) is the pattern.
36. Workflows skip on draft PRs unless deliberately not (`if: github.event.pull_request.draft == false`).
37. `concurrency:` with `cancel-in-progress: true` cancels stale runs on the same ref (typical for PRs: a new push obsoletes the prior run). Missing is a Minor (slow), wrong on release/deploy workflows (would kill a release in flight).
38. `if:` conditions filter out branch/event combinations that don't matter (e.g., skip a deploy job when the actor is dependabot).

### Stage 6 — Speed: runners

39. The runner image fits the workload. `ubuntu-latest` is 2 vCPU, 7GB RAM, 14GB disk by default — workloads that need more get throttled. Larger runners (4-core, 8-core) cost more per minute but may reduce total minutes and queue time. The skill flags jobs that consistently bump against the resource ceiling.
40. Self-hosted runners are used where the workload genuinely benefits (GPU, large memory, custom hardware, on-prem network access). Self-hosted "for cost" without measurement is a Minor — managed cost is a real expense.
41. The runner is started fast. Container-image-based runners or pre-warmed self-hosted pools shave queue time on bursty workloads.
42. Steps that run on every job (login, setup) are minimal. Each is a few seconds; multiplied across hundreds of runs per day it's real money.

### Stage 7 — Cost-specific patterns

43. Multi-OS matrices that don't change the result: a JS-only project running tests on `macos-latest` and `windows-latest` at full cost in addition to Linux. Recommend dropping unless the team genuinely supports those platforms.
44. Nightly workflows that run a small change against a giant test matrix. Recommend a `schedule:` event with a slimmer matrix and a fuller weekly schedule.
45. Container builds that don't use build-cache exports between runs. Recommend `cache-to: type=gha,mode=max` and `cache-from: type=gha`.
46. Re-downloading large dependencies per job (artifacts that should be passed between jobs via `actions/upload-artifact`/`actions/download-artifact`).
47. Slow test frameworks that aren't sharded. Recommend sharding or sub-suites.
48. The "boil the ocean" matrix: every job × every language × every OS × every version. Each leg is real money; trim.
49. Self-hosted runner pools sized for peak instead of average; recommend autoscaling pools (controller projects exist in the ecosystem) or buying smaller hosted runners.
50. macOS minutes used where Linux would do. macOS is the most expensive runner type; reserve for genuinely Apple-platform-specific work.

### Stage 8 — Reliability

51. Retries are bounded and use a real retry action (with backoff), not `for i in 1..5; do step; done`. Manual retry loops are a Minor.
52. Flaky steps are identified and quarantined, not silently retried. The skill flags `continue-on-error: true` on test steps as a Major unless the workflow explicitly handles the result.
53. Steps have appropriate `timeout-minutes`. Default 6-hour timeouts let runaway tests burn budget; recommend tight per-step or per-job timeouts.
54. `if: always()` on cleanup steps so artifacts and logs are uploaded even on failure. Missing is a Minor.
55. Artifact uploads use compression where it helps and avoid uploading entire workspaces.
56. Workflow dispatch inputs are typed (`type: choice` etc.) so a release manager can't typo a target.

### Stage 9 — Maintainability

57. Shared logic lives in a *reusable workflow* (`workflow_call`) or a *composite action*, not duplicated across files. Duplication is a Major.
58. Reusable workflows live in a dedicated repository or a `.github/workflows/` path with a clear naming convention. Anonymous one-offs become legacy.
59. Workflows have a top comment explaining purpose, trigger, and ownership. Missing is a Minor.
60. Workflow names are descriptive (`ci-pr.yml`, `release-prod.yml`), not `ci.yml`, `ci2.yml`.
61. Long shell blocks live in scripts in the repo (`./.github/scripts/foo.sh`), not inline in YAML, so they can be linted and tested. Inline shell over a few lines is a Minor.
62. Workflows do not depend on undocumented external endpoints (a `curl` to an internal status page in a step). Document or remove.
63. Workflows do not depend on `set -e` being implicit. Be explicit; explicit `set -euo pipefail` at the top of shell blocks.

### Stage 10 — Observability of workflows

64. Long-running steps emit progress (a `--progress` flag, or periodic status). Silent 20-minute steps are a debugging nightmare.
65. Failure output is informative. A step that ends with `exit 1` after a one-line "error" is hostile; recommend richer error output.
66. Workflows that ship something to production write a Job Summary (`$GITHUB_STEP_SUMMARY`) with what shipped, where, and with what version.
67. Workflows emit OpenTelemetry-style metrics where the org collects them; or at minimum, the team has a dashboard tracking workflow run counts, durations, and failure rates.

### Stage 11 — Severity assignment

68. Assign every finding one severity:
    - **Blocker** — the workflow is dangerous (unpinned third-party action with full repo access, secret leak, `pull_request_target` running fork code, self-hosted runner on public PRs).
    - **Major** — likely to bite within 90 days: missing dependency cache on slow installs, no `concurrency` on a deploy, no `permissions:` declared, large matrix without justification, `fail-fast: false` missing where diagnostics need it (or set wrong way for gating).
    - **Minor** — small defect: missing top-of-file comments, inline shell over a few lines, missing job summary.
    - **Nit** — taste: naming, ordering, formatting.
69. When in doubt, lower. The optimization_priority input biases the table: under `priority: security`, security findings round up; under `priority: cost`, cost findings round up.
70. Cap nits at 8 in the rendered output.

### Stage 12 — Compose the report

71. Lead with a one-paragraph summary: which workflows were reviewed, the optimization priority applied, the headline counts, and an estimated savings note where the agent can quantify (e.g., "moving the Node matrix from 4 versions to 2 saves roughly half of those jobs' minutes; verify with usage data").
72. Group findings by severity. Within each severity, group by workflow file, then job, then step or field.
73. For each finding, emit a fenced block with: severity tag, category, workflow/job/step reference, "Why it matters," and "Suggested fix" with a small concrete YAML snippet illustrating the change.
74. Include a separate top-of-report block titled "Top three actions you should take this week" — the highest-leverage findings called out for executives or busy maintainers.
75. End with "What I did not check": anything the inputs left ambiguous (e.g., "no usage data provided, so cost savings are heuristic").
76. Produce `findings_json` in parallel.

### Stage 13 — Self-check

77. Verify every "Blocker" matches the standard in step 68.
78. Verify every "Suggested fix" YAML snippet parses (check key names, indentation).
79. Verify no finding references a nonexistent workflow or job — that's worse than no finding.
80. If the report has more than 25 findings, consolidate or downgrade; reviewers don't read past 25.
81. Verify the savings estimates do not over-claim. If usage data is absent, use words like "roughly" and "depending on run count."

### Stage 14 — Common anti-patterns

A. **The bash heredoc workflow.** A workflow that's 80% one giant shell block. Move to a script file.
B. **The "we'll fix it later" pin.** A third-party action pinned to a moving tag with a comment "TODO pin sha." Pin now.
C. **The over-shared secret.** A repo-wide secret used by one workflow; should be environment-scoped via Environments.
D. **The phantom job dependency.** A `needs:` chain that exists "to make jobs run in order in the UI" even though the steps are independent.
E. **The forever cache.** A workflow that creates new caches every push but never invalidates; eventually the team's cache budget evicts useful caches first.
F. **The retry-as-fix.** Tests flaky? Re-run from the UI. The skill flags this as a process smell, not a workflow smell, but surfaces it.
G. **The mandatory comment-step.** A step that posts to a chat tool that's broken half the time; recommend `continue-on-error: true` *only here* and consider removing the dependency.
H. **The matrix that prints "skip" 14 times.** A matrix leg whose primary action is to detect that it shouldn't run; build the filter into `include`/`exclude` instead.
I. **The reusable workflow whose inputs are stringly-typed.** Use typed inputs; document defaults.
J. **The big bang composite action.** A composite action that does five unrelated things; split.

### Stage 15 — Reusable workflow checks

When the input contains `workflow_call` workflows, layer these checks.

82. Inputs and secrets are explicit, documented, and minimal. Avoid `secrets: inherit` unless caller and callee are owned by the same trust boundary.
83. Outputs are explicit so callers can chain.
84. The callee version-pins by tag or SHA — callers should pin too, but the callee can support `@v1` semantics if a release scheme exists.
85. The callee documents its required `permissions:` and the caller can satisfy them.
86. The callee logs its inputs (without secrets) to a Job Summary for traceability.

### Stage 16 — Self-hosted runner checks

When the input names self-hosted runners, layer these.

87. Runner pools are labeled descriptively (`linux-x64-ci`, `gpu-a100`) rather than `self-hosted` alone.
88. Pools are ephemeral; the agent flags any sign that the team uses long-lived stateful runners.
89. Network policy restricts runner egress to required endpoints (registries, package mirrors, OIDC issuer). Open-internet egress on a privileged runner is a Major.
90. Maintenance is scheduled; runners are reset on a cadence (kernel updates, base image refresh).

## Outputs

The skill returns two artifacts:

1. `optimization_report` (markdown) — the human-readable review with top-three actions, ranked findings, and savings notes.
2. `findings_json` (JSON) — structured findings for automation.

## Examples

**Input (placeholder):**

Three workflows: `ci.yml` (lint + unit + integration on PR), `docker.yml` (build & push on main), `release.yml` (production deploy on tag). Stack: Python + a Docker image. No `permissions:` block in any workflow. `actions/checkout@v3` and several third-party actions pinned by tag. `docker.yml` rebuilds with no cache. `ci.yml` runs on a 4-version Python matrix on Linux+macOS. No `concurrency`. No path filters.

**Agent reasoning (abbreviated):**

- Stage 2: third-party actions pinned by tag — Major. No `permissions:` — Major. Token defaults are repo-wide read+write — Major.
- Stage 3: `docker.yml` has no buildx cache — Major (savings high). `ci.yml` has no pip cache — Major.
- Stage 4: matrix is 4 × 2 = 8 legs. macOS adds little for a Python-only Linux deploy — Major (cost).
- Stage 5: no path filters; doc-only changes run full CI — Major. No `concurrency` on PR runs — Minor (cost).
- Stage 6: `ubuntu-latest` is fine for size.
- Stage 11: Major × 6, Minor × 3, Nit × 1.
- Top three: pin third-party actions by SHA; add buildx cache to `docker.yml`; drop the macOS matrix leg.

**Output (abbreviated):**

```
**Summary:** Three workflows, mixed quality. Priority: cost.
**Top three this week:**
1. Pin every third-party action to a full commit SHA — security blocker class.
2. Enable buildx layer caching in docker.yml — saves roughly the build time per main-push.
3. Drop macOS from the Python matrix — halves the matrix cost; bring it back if the team actually targets macOS.

### [MAJOR] supply-chain: third-party actions pinned by tag
File: .github/workflows/ci.yml
Why it matters: ...
Suggested fix:
```yaml
- uses: pnpm/action-setup@e3e6c4c   # pin to commit SHA
```
```

## Limitations

- Savings estimates are heuristic without `usage_signal` data. The skill says "roughly" and names the assumption.
- The skill cannot run workflows; behavioral findings (timing, flake) are inferred.
- GitHub Actions evolves; this skill encodes mid-2020s best practice. Features (large runners, organization-level pin policy, build provenance) appear regularly; the skill's recommendations should be re-validated quarterly.
- Custom enterprise rules (org-mandated approvers, federated identity quirks) are visible only if the input names them.
- Cost recommendations assume GitHub-hosted pricing models; self-hosted economics differ and the skill names the trade.
- The skill does not write a brand-new workflow from scratch. Use the pipeline-architect skill for greenfield design.

## Sources reviewed

- https://github.com/actions/reusable-workflows (MIT)
- https://github.com/sdras/awesome-actions (CC0-1.0 list referencing MIT/Apache actions)
- https://github.com/johnbillion/awesome-github-actions-security (MIT)
- https://github.com/aquasecurity/trivy (Apache-2.0)
- https://github.com/aquasecurity/tfsec (MIT)
- https://github.com/antonbabenko/pre-commit-terraform (MIT)
- https://github.com/argoproj/argo-rollouts (Apache-2.0)
