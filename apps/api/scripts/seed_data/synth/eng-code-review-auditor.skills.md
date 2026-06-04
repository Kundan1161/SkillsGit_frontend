---
id: skillsgit-curated/pr-review-auto-auditor
version: 1.0.0
name: PR Review Auto-Auditor
description: Audit a pull request diff for correctness, security, performance, test coverage, naming, and missing edge cases — produce a triaged, line-anchored review.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [code-review, pull-request, audit, refactoring, testing, quality, ci, diff-analysis]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  tools_optional: [web_search, code_execution]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - review this pr
  - audit this diff
  - code review
  - pr review
  - review my pull request
  - pre-merge review
  - check this change
  - review before merge
  - find issues in this diff
  - pr auditor
  - patch review
  - merge-ready review
  - review checklist
example_invocations:
  - "Audit this PR diff and flag anything I should fix before I merge."
  - "Run a full code review pass on the patch in the clipboard — correctness, security, perf, tests."
  - "Review this pull request like a senior engineer would; sort findings by severity."
inputs:
  - name: diff
    type: text
    required: true
    description: Unified diff (git diff or PR patch) or list of changed files with before/after content.
  - name: context_files
    type: file
    required: false
    description: Surrounding files the diff calls into; helpful for cross-file reasoning.
  - name: language
    type: choice
    required: false
    description: Primary language of the change. Helps the agent pick the right idiom checks.
    choices: [python, typescript, javascript, go, java, ruby, rust, csharp, php, kotlin, swift, mixed]
  - name: project_conventions
    type: text
    required: false
    description: Style guide, naming rules, or team norms the agent should enforce.
  - name: pr_description
    type: text
    required: false
    description: The author's stated intent — used to detect intent/implementation gaps.
outputs:
  - name: review_report
    type: markdown
    description: Triaged review with summary, blockers, recommended changes, nits, and per-finding line anchors.
  - name: findings_json
    type: json
    description: Machine-readable findings list with severity, category, file, line range, and suggested fix.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# PR Review Auto-Auditor

## When to use

Use this skill when a developer hands you a pull request, a unified diff, a patch file, or a list of changed files and asks for a pre-merge review. The skill is built for the moment between "I think this is ready" and "I'm clicking merge" — the last chance to catch correctness regressions, security holes, expensive performance traps, missing tests, and ergonomic problems before they enter the main branch.

It applies whether the user is reviewing their own change ("did I miss anything?"), reviewing a teammate's change ("be the second pair of eyes"), or reviewing an AI-generated change ("the model wrote this — sanity-check it"). It also applies to retroactive reviews on already-merged commits when investigating a regression or onboarding to unfamiliar code.

Do not use this skill for greenfield design review (where there is no diff yet), for pure security audits that require taint analysis across the full codebase rather than a localized patch, or for refactor proposals where the user wants opportunity-spotting rather than defect-finding. For those, prefer the dedicated security-review or refactor-spotter skills.

The skill assumes that mechanical issues (formatting, linter violations, type errors) are caught by tooling upstream of this review — it focuses on the issues that require judgement.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `diff` | yes | The unified diff or per-file before/after snapshot. |
| `context_files` | no | Files the diff calls into or imports from, so the agent can reason about callers and types. |
| `language` | no | Lets the agent select language-idiomatic checks; inferred from file extensions if omitted. |
| `project_conventions` | no | A style guide, naming rules, layering rules, or team conventions to enforce. |
| `pr_description` | no | The author's stated goal — used to flag scope creep and missed acceptance criteria. |

## How to apply

The agent runs a deterministic pipeline. Each stage produces structured findings that get merged, deduplicated, and ranked at the end.

### Stage 1 — Frame the change

1. Read the PR description (if present) and extract a one-sentence goal: what is this change supposed to do? Note whether the goal is a feature, a bug fix, a refactor, a perf change, a security fix, or a chore.
2. Skim the diff once front-to-back without commenting. Build a mental map: which files are added, modified, deleted; which directories are touched; which subsystems sit behind those directories.
3. Compute a rough size class: tiny (<50 lines changed), small (50-200), medium (200-800), large (800-2000), huge (>2000). For "huge" diffs, the first finding the report emits is a recommendation to split the PR — large diffs are reviewed worse by both humans and models.
4. Identify the kind of change: pure addition, pure deletion, surgical modification, mixed refactor-plus-feature. Mixed refactor-plus-feature is a yellow flag the report should call out: it makes regressions hard to bisect.
5. If a `pr_description` was provided, list the explicit deliverables it claims, then check whether each appears in the diff. Missing deliverables are recorded as a Stage 5 finding.

### Stage 2 — Read each changed file in dependency order

6. For each modified file, read the full file (not just the hunk) when context permits. The full-file read catches "the rename broke a caller two screens down."
7. Process files in a reasonable order: schema/types first, then library/utility code, then the call sites, then tests, then docs/config. This order means you have type information available when you read the call sites.
8. While reading, build a lightweight symbol map of new or renamed identifiers and where they're used. This map drives the rename-safety check and the dead-code check.
9. Record the public-surface delta: which exported functions, classes, routes, CLI flags, env vars, schema fields, or migration files were added/changed/removed. Anything in the public-surface delta is a candidate for the backward-compatibility check.

### Stage 3 — Run the seven-category check matrix

For every changed file, evaluate against the categories below. Each category produces zero or more findings. A finding has: file path, line range, severity (blocker / major / minor / nit), category, one-sentence description, and either a suggested code change or a question for the author.

10. **Correctness.** Look for off-by-one errors, inverted conditions, wrong operator precedence, swapped arguments at call sites, default-value bugs (especially mutable defaults in Python, copy-by-reference in JS/TS), uninitialized fields, missing returns on some branches, exception-swallowing `try/except` or `catch` blocks, unhandled `null`/`undefined`/`None`/`nil`, async functions never awaited, promises with no error handler, `async` calls inside `forEach`, race conditions on shared state, timezone-unaware datetimes, currency in float, integer overflow on machines with 32-bit ints, comparison of floats with `==`.

11. **Security.** Hard-coded credentials, API keys, or tokens (commit-secret heuristic: 20+ char base64-ish strings near identifier names like `key`, `token`, `secret`, `password`). String-concatenated SQL or template-rendered HTML with user input. Shell commands built from user input. `eval`, `exec`, `Function()`, `pickle.loads` on untrusted bytes, `yaml.load` without a safe loader, `Marshal.load`, `ObjectInputStream.readObject`. Permissive CORS (`Access-Control-Allow-Origin: *` combined with credentials). Auth/authz checks missing on new routes. Reflected user input in HTTP responses without escaping. Path concatenation that allows `..` traversal. Open redirects. Disabled TLS verification. Weak crypto (MD5, SHA-1 for passwords or signatures, ECB mode, hard-coded IVs, `Math.random()` for security purposes). Untrusted deserialization. Note: defer deep security work to the dedicated security-review skill — here we flag obvious instances only and tag them `security:flag-only`.

12. **Performance.** N+1 query patterns (a loop containing a DB or HTTP call that varies per item). Repeated work inside loops that could be lifted out. O(n^2) algorithms on inputs that can grow. Memory loaded that should be streamed (reading whole files when line-by-line works). Synchronous IO in async contexts. Missing indices implied by new query patterns. New cache reads with no eviction. Cold-start regressions: new dependencies loaded at import time, large objects built at module load. Re-rendering loops in UI code that won't memoize. Unbounded pagination (returning all rows). Background jobs with no concurrency cap.

13. **Tests.** New code paths without test coverage (find each new branch and check whether a test exercises it). New error branches without negative-path tests. Tests asserting on implementation details (mock call ordering, private method names) — fragile. Test names that don't describe behavior. Tests that only assert "no exception thrown" — too weak. Tests with hidden dependencies on test order. Snapshot tests where the snapshot is large and was likely accepted without reading it. Skipped or `.only`'d tests left behind. Removed tests with no replacement.

14. **Naming and clarity.** Names that lie (a function `validate_x` that mutates `x`). Abbreviations that are not standard for the codebase. Boolean parameters whose call sites read `f(true)` with no clue what `true` means. Magic numbers and magic strings that should be named constants. Nested ternaries beyond one level. Functions longer than ~50 lines that have no internal headings. Files longer than ~600 lines added in one shot. Comments that say what the code does (delete) vs. why it does it (keep). Dead code: commented-out blocks, unused imports, unused parameters.

15. **API and contract surface.** Breaking changes to exported types, function signatures, route paths, request/response schemas, env var names, CLI flags, or DB schema without a migration plan. Defaults that change behavior silently. Renames that don't update all call sites (re-check using the symbol map from step 8). New required parameters without sensible defaults. Backwards-incompatible serialization changes (enum reordering, field type widening). For public packages: semver implications — flag if the diff is a minor bump but contains a breaking change.

16. **Edge cases and missing branches.** For each new function, enumerate the obvious inputs: empty list, single element, very large input, duplicates, all-same input, null/undefined in optional fields, negative numbers, zero, very large numbers, unicode (combining characters, emoji, RTL), strings exactly at boundary lengths, concurrent callers. Ask: does the code handle each? Does a test exist for each? Each unhandled case is a finding.

### Stage 4 — Cross-file checks

17. **Caller/callee compatibility.** For every signature change in the diff, re-walk all callers across the provided context files. Each mismatched caller is a blocker. If callers were not provided, emit a finding requesting them.
18. **Migration and data shape.** If schema files (Prisma, SQLAlchemy, Django models, Sequelize, etc.) changed: is there a corresponding migration? Are migrations reversible? Will the migration block writes on a hot table? Does the new column have a default for existing rows?
19. **Configuration drift.** Are new env vars or feature flags added? Are they documented? Is there a default? Is there a way for the deploy environment to know it needs to set them?
20. **Documentation drift.** If a public function changed, did its docstring update? If a CLI flag was added, did the help text update? If a README example exists that now compiles wrong, flag it.

### Stage 5 — Intent reconciliation

21. Re-read the PR description (or, if absent, infer intent from commit messages and the dominant change shape). For each stated deliverable, locate it in the diff and mark "present", "partial", or "missing". For each large code block in the diff that is *not* a stated deliverable, label it "scope creep" and decide whether it should split into a separate PR.
22. Detect "trojan refactors" — a feature PR that also reformats unrelated files. Recommend splitting these out so the feature diff stays reviewable.
23. Detect "abandoned scaffolding" — files added but never imported, classes defined but never instantiated, feature flags introduced but never read. Each is a finding tagged `dead-on-arrival`.

### Stage 6 — Severity assignment

24. Assign every finding one severity:
    - **Blocker** — merging this will break correctness, security, or backwards compatibility for known users. Examples: SQL injection, lost data on migration, broken API contract, panic on empty input on a hot path.
    - **Major** — likely to cause a real bug in the next 90 days but not the moment merged. Examples: missing tests on a complex branch, an N+1 query that scales with users, a race condition under load.
    - **Minor** — small defect that would be embarrassing in review. Examples: a misleading variable name, a commented-out block, a redundant check.
    - **Nit** — style or taste, no functional impact. Examples: a comment typo, a one-liner that could be slightly clearer.
25. When in doubt between two severities, pick the lower one. A reviewer who cries wolf is ignored; a reviewer who calls only the real fires is read.
26. Cap nits at 8 in the output. If more nits exist, summarize them in a single "minor style observations" bullet.

### Stage 7 — Compose the report

27. Open with a one-paragraph summary: the goal of the PR (as you understood it), your overall verdict (Ready to merge / Ready after blockers / Needs rework), and the headline finding count (`3 blockers, 5 major, 8 minor, 4 nits`).
28. Group findings by severity, not by file. Inside each severity group, order by file path, then by line number.
29. For each finding, emit a fenced markdown block:
    ```
    ### [BLOCKER] correctness: off-by-one on slice bound
    **File:** `src/parser.py` lines 142-146
    **Why it matters:** When `tokens` is exactly `max_len` long, the current code drops the final token; the regression test added in this PR does not exercise this length.
    **Suggested fix:** Use `tokens[:max_len + 1]` or, better, refactor the loop to terminate on the sentinel rather than the slice bound.
    **Question for author:** Is the off-by-one intentional to leave room for the EOS token? If so, add a comment.
    ```
    Always include the "why it matters" — never assume the author sees what you see.
30. End with a "What I did not check" section listing categories you skipped because of missing inputs (e.g., "no callers provided, so cross-file signature changes were not verified"). This is a trust signal.
31. Produce `findings_json` in parallel: each finding becomes one object with keys `severity`, `category`, `file`, `line_start`, `line_end`, `summary`, `suggested_fix`, `question_for_author`. The host application can render or filter this.

### Stage 8 — Self-check before returning

32. Re-read your own report. Count the findings. If you produced zero findings, explicitly state "no issues found" with a one-sentence justification — never return an empty report silently; the user will assume you crashed.
33. If you produced more than 30 findings, you are over-reviewing. Re-rank, drop nits, and aim for a report a busy reviewer will actually read.
34. Check every line-number reference against the diff: a wrong line number destroys trust. If you cannot anchor a finding to a specific line, anchor it to a file and say "across the file" — never invent a line.
35. Never quote large blocks of the user's code back at them. Reference by file and line.
36. Do not lecture. The user is an engineer; you are an engineer; speak as peers.

### Stage 9 — Language-specific guardrails

For each detected language, the agent layers an extra pass on top of the universal checks. These are the patterns that experience says recur in PRs and that a generalist reviewer misses.

37. **Python.** Mutable default arguments (`def f(x=[])`). `except:` without a class, or `except Exception` that swallows `KeyboardInterrupt`/`SystemExit`. `assert` used for runtime checks (Python strips them under `-O`). Implicit f-string log formatting with sensitive data. `dict.get(k)` then `.lower()` without `or ''` guard. `subprocess` with `shell=True` and any interpolation. New top-level imports inside hot paths. `@property` that mutates. `dataclass` with mutable defaults missing `field(default_factory=...)`. Use of `eval`, `exec`, `pickle.loads`, `yaml.load` without `SafeLoader`. Iterating a dict while mutating it.
38. **TypeScript / JavaScript.** `==` instead of `===`. `JSON.parse` of untrusted with no try/catch. `Object.assign` mutating an argument the caller still uses. Async functions called without `await` whose promise is discarded. `Array.prototype.forEach` with an `async` callback (the loop doesn't wait). `for...in` over an array. Implicit `any` introduced by removing a type annotation. New `process.env` reads at module scope (breaks tests that mutate env). `Date` arithmetic without timezone awareness. `setInterval` without `clearInterval`. React-specific: missing dependency array entries in `useEffect`, mutating state, `key={index}` on dynamic lists, components that re-fetch on every render because of an unstable object dependency. Node-specific: stream `data` listener without error handler; `child_process.exec` instead of `execFile`.
39. **Go.** Loops capturing the loop variable in a goroutine without copying. `defer` inside a loop accumulating. Ignored errors (`_ = f()` or `f()` returning error that isn't checked). `nil` map writes. `time.Sleep` for synchronization. Maps iterated when order matters. `panic` in library code. `context.Background()` in request paths (should be the request context). Missing `Close()` on response bodies. Returning concrete pointer types where an interface would suffice for testability.
40. **Java / Kotlin.** Raw exception types caught. `equals` on `null`. Mutable static fields. `SimpleDateFormat` shared across threads. Stream not closed (try-with-resources missing). `Optional` returned but caller still null-checks. Kotlin: platform types accepted into non-null parameters; `!!` on values that could be null; data class equality assumed in places where reference equality is used.
41. **Ruby / Rails.** Mass assignment without strong params. `find_by_sql` with interpolation. Scopes that call `to_a` and break chaining. `N+1` from missing `includes`. `before_save` mutating attributes a callback later relies on. Default scopes that leak into unrelated queries.
42. **Rust.** `unwrap()` and `expect()` in library or request-path code. `clone()` on large types in hot loops. `unsafe` blocks added without a comment justifying invariants. `Arc<Mutex<>>` where `&mut` would do. Async `.await` inside a sync mutex guard. Missing `Send + Sync` bounds where they're required.
43. **C# / .NET.** `async void` outside event handlers. `Task.Result` / `.Wait()` causing deadlocks. `IDisposable` not in a `using`. LINQ expressions that materialize when they shouldn't (`.ToList()` mid-pipeline). Configuration reads against a singleton `IConfiguration` lacking `IOptionsSnapshot`.
44. **Multi-language signal.** Whenever the diff crosses language boundaries (e.g., a Python backend with a TS frontend), check the contract between them: did the API response shape change without the consumer being updated? Did an enum gain a value the client doesn't handle in its `switch`?

### Stage 10 — Calibration heuristics

45. **Author intent inference.** If the PR is labeled "WIP" or "Draft" in the description, soften nits and emphasize blockers; the author is signaling they know the work isn't done. If the PR is described as a "small fix" but touches >300 lines, surface the scope mismatch as a major finding — not because the code is wrong, but because the framing will mislead reviewers.
46. **Test-only diffs.** If the diff is exclusively test files, switch posture: review for test quality (false-positive risk, flakiness, redundancy) and skip product-code categories.
47. **Generated code.** Diffs that include generated files (lockfiles, OpenAPI clients, protobuf outputs, schema migrations from an ORM) should not have those files reviewed line by line. Note the presence of generated content; treat the hand-written change as the actual diff.
48. **First-time contributor smell signals.** If the diff contains patterns rarely seen in mature contributions to the project (different file layout, different test framework, different naming style), call this out gently in the summary as something the maintainer should align on — without making the author feel attacked.
49. **Feature flag wrap.** If new behavior is added but is not behind a flag and the project elsewhere uses flags, recommend wrapping. If a flag is added but the diff never reads it (dead-on-arrival flag), flag that.
50. **Migration safety.** For schema migrations specifically, check: is it locking? Does it backfill in chunks? Does it run before or after the code that depends on it? Are there both up and down migrations? Does the down actually undo the up? On a multi-region or multi-replica deploy, can old code read the new schema?

### Stage 11 — Communication style

51. Lead with what's right, then what's wrong, then what's missing — in that order. If the PR's central idea is good, say so once at the top. Reviewers who only criticize get tuned out.
52. Use "consider" for low-confidence opinions, "should" for high-confidence corrections, "must" sparingly for true blockers. Calibrate the verbs so the reader can scan severity from the language alone.
53. Ask, don't assume, when intent isn't clear. "I'd expect this to also handle `null` — is that out of scope here?" is better than "Bug: doesn't handle null."
54. When suggesting an alternative, show a small sketch (3-5 lines) of the alternative shape, not a full rewrite. The author owns the implementation.
55. End the report with one positive observation about the PR if you can find an honest one. Reviewers who build trust deliver tougher feedback more effectively.

### Stage 12 — Severity decision table

When uncertain, use the table below. Pick the row that matches the worst plausible outcome, then pick the column that matches likelihood, and read off severity.

```
                       likely        possible       unlikely
data loss              Blocker       Blocker        Major
security incident      Blocker       Blocker        Major
user-visible bug       Blocker       Major          Minor
internal-only bug      Major         Minor          Minor
perf regression < 2x   Major         Minor          Nit
perf regression < 10%  Minor         Minor          Nit
maintainability        Minor         Nit            (drop)
style / taste          Nit           (drop)         (drop)
```

If the table and your gut disagree, follow your gut and write a one-sentence justification. The table is a tiebreaker, not a ruler.

### Stage 13 — Test-coverage analysis details

Coverage gaps deserve special handling because they are simultaneously the most common finding and the most ignored. The agent surfaces them with extra precision.

56. For each new function in the diff, enumerate the public branches: each `if`, each `match` arm, each `try` with multiple exception types, each loop with a non-trivial body. Map each branch to a test in the diff (or in the project if context permits). Unmapped branches become findings.
57. Distinguish "tested by name" from "tested by behavior." A test that calls the function with one input and asserts it returns 42 tests one path. The other paths are still untested even though the function is "covered" by line-coverage tools.
58. For new HTTP routes, the minimum test set is: 200 path, the most-common 4xx path the route can produce, and the auth-required path (401/403). If any of these is missing, surface it.
59. For new database writes, the minimum test set is: the happy path and one rollback/error path. For migrations specifically, recommend the team run the migration against a copy of staging before merging.
60. For new background jobs, the minimum test set is: success, failure-with-retry, failure-after-max-retries, and idempotency-on-redelivery if the queue is at-least-once.
61. For pure functions with discrete return values (enums, unions), the minimum test set has one assertion per output variant.
62. Don't propose test specifics for tightly-domain code (e.g., a complex pricing engine); recommend the *kind* of test and let the author write the assertions.

### Stage 14 — Reviewing AI-generated diffs

The agent is increasingly asked to review changes that were themselves AI-generated. The failure modes differ from human-authored diffs.

63. Watch for "plausible-looking but wrong" identifiers — a function name that's almost right but not actually defined elsewhere, an import path that follows the project's convention but points nowhere, a config key that resembles an existing one.
64. Watch for tests that pass because the assertions are loose (`assert result is not None`). LLMs tend to write tests that exercise the code without verifying behavior.
65. Watch for fabricated error messages — strings that look like the project's idiom but don't exist in the codebase.
66. Watch for hallucinated library APIs — methods on objects that the library doesn't expose. If you can verify the API doesn't exist (from context or from your knowledge), call it a blocker; if uncertain, ask the author to confirm.
67. Watch for half-applied refactors — a function renamed in some call sites but not all. The PR description will not warn you; the diff will look complete.
68. Watch for "good comments, wrong code" — the comments accurately describe what the code should do but the code does something subtly different.

### Stage 14b — Concurrency-specific patterns to watch

A surprisingly large share of post-merge bugs come from concurrency. The agent watches the patterns below with extra care across all languages.

A. Read-then-write on shared state where the read and write are not atomic — even at single-threaded async runtimes, await points create the same hazard.
B. Caches written without a TTL and without a size cap, where one of the keys could vary widely (e.g., per-tenant cache with no eviction).
C. Background tasks that capture mutable state by reference and run later, after the state has changed.
D. Lock acquisition order that differs between functions — classic deadlock recipe.
E. Channels or queues with unbounded capacity where producer rate can exceed consumer rate.
F. Cancellation: long-running operations that don't check their cancellation token; cleanup that runs on the wrong thread.
G. Idempotency: write operations that lack a deduplication key when the caller will retry on transient failure.
H. Eventual consistency: code that reads after write and assumes the write is visible (especially against read replicas).

### Stage 15 — How to handle disagreements with the author

The skill is being invoked by a developer; it should expect pushback. The skill is calibrated to be helpful, not loud.

69. When the author has explicitly said in the PR description "I know about X, addressing later", do not re-flag X.
70. When the diff includes a comment like `// TODO: validate this`, treat the TODO as an acknowledged debt — surface the issue as Minor (not Major) and call it out as "the author has acknowledged this; consider sizing follow-up."
71. When the author has labeled the PR as a "hotfix", soften refactor and naming findings; the goal is to ship the fix, not to polish.
72. When the author has explicitly named you as the reviewer (e.g., "@reviewer please be aggressive on perf"), bias the report accordingly — emphasize the requested dimension.

## Outputs

The skill returns two artifacts:

1. `review_report` (markdown) — the human-readable review as specified in step 27-30.
2. `findings_json` (JSON array) — machine-readable findings list described in step 31, suitable for posting as inline PR comments through the host platform's API.

## Examples

**Input (placeholder):**

PR description: "Add `/api/v2/users/:id/posts` endpoint that returns the user's posts ordered by creation date, paginated 20 per page."

Diff: 3 files, ~80 lines added. New route handler, new query in repository layer, new test file with 2 cases.

**Agent reasoning (abbreviated):**

- Goal: feature; small PR; should be straightforward.
- Read the route handler: no auth middleware applied. The v1 routes all have auth. Likely a blocker.
- Read the repository query: `SELECT * FROM posts WHERE user_id = ? LIMIT 20`. No `OFFSET` despite description saying paginated. Major.
- Read the repository query again: order is missing, despite description specifying creation-date order. Major.
- Read the test file: tests cover happy path with one user. No test for empty result. No test for invalid user id. Major.
- N+1 check: route handler loops over posts to fetch comments — yes, one query per post. Major.
- Cross-file: route registered in `routes/index.ts`. Confirmed.
- Migration drift: no schema change.
- Scope creep: none.
- Headline: 1 blocker, 4 major, 0 minor, 1 nit.

**Output (abbreviated):**

```
**Summary:** New v2 endpoint to list a user's posts. **Verdict:** needs rework.
Headline: 1 blocker, 4 major, 0 minor, 1 nit.

### [BLOCKER] security: route is unauthenticated
File: src/routes/v2/posts.ts lines 12-30
Why it matters: ...
Suggested fix: ...

### [MAJOR] correctness: pagination parameter ignored
...
```

### Stage 15b — Style of writing findings

The agent's diction matters as much as the catch. Style rules:

P. Write each finding as if you might have to defend it on a follow-up call with the author. Specific. Falsifiable. Anchored in the file.
Q. Avoid emoji and decorative formatting; busy reviewers scan plain text faster.
R. Use the imperative for the suggested fix ("Use parameterized queries.") and the indicative for the explanation ("Currently the query is built by string concatenation.").
S. Never use the word "obviously" or "simply" in a finding. If it were obvious, the author would have done it; if it were simple, the bug wouldn't exist.
T. When proposing a fix, propose the minimal change that addresses the issue. Larger refactors belong in the refactor-spotter skill's output, not here.

### Stage 16 — Common false positives to suppress

A reviewer who reports false issues is worse than one who reports too few. The agent suppresses or downgrades the following common false-positive patterns.

I. Type warnings on code that uses `typing.cast`, `as`, or other intentional narrowings — the author has thought about it.
J. "Missing null check" on values that the caller's type system has already proven non-null.
K. "Missing error handling" on code paths that intentionally let the error propagate to a higher-level handler.
L. "Magic number" findings on values whose meaning is universal and named once would just add a redundant constant (e.g., `2` in `array.length / 2`).
M. "Long function" findings on functions that are linear sequences with no branching — splitting them rarely helps.
N. Style-only differences from the agent's preferred style when the project's existing files use the same alternative consistently.
O. Microbenchmark concerns where the surrounding code is plainly not hot.

## Worked example two — a refactor PR

**Input:** the PR description says "extract a `RateLimiter` helper from `auth.py` and reuse in `webhooks.py`". Diff includes a new `rate_limiter.py` (40 lines), changes to `auth.py` (removed 25 lines, added 5), changes to `webhooks.py` (added 7 lines), and a small test file (15 lines).

**Agent reasoning:**

- Goal: refactor. Small PR, ~90 lines net.
- Stage 1: pure refactor + addition. No mixed concerns. Good shape.
- Stage 2 file order: read `rate_limiter.py` (new helper) first, then `auth.py` (caller), then `webhooks.py` (new caller), then tests.
- Stage 3 correctness: in `rate_limiter.py`, the helper uses `time.time()` while the original used `time.monotonic()`. Wall-clock can move backward; this is a behavioral regression. Major.
- Stage 3 security: rate-limit storage moved from a per-instance dict to a module-level dict. In a multi-process deploy this means the limit applies per-process, not globally. Surface as Major with a question about deployment topology.
- Stage 3 tests: tests cover the helper in isolation but neither caller path is integration-tested. Major.
- Stage 3 naming: `RateLimiter` has a method named `check` whose return value is ambiguous (true means "allowed" or "limited"?). Minor.
- Stage 4 callers: confirmed the two import sites; no third caller missed.
- Stage 4 docs: no docstring on the new helper. Nit.
- Stage 5 intent: matches description; no scope creep.
- Stage 7 report: 0 blockers, 3 major, 1 minor, 1 nit. Verdict: Ready after blockers (none) but please address the three majors before merge.

## Limitations

- The skill cannot run code; it reasons textually. Findings about runtime behavior (e.g., a race condition) are flagged as hypotheses for the author to verify, not as ground-truth.
- Cross-file reasoning is only as good as the `context_files` the caller provides. If callers are not supplied, signature-change blast radius cannot be fully assessed; the report will say so.
- The skill does not perform deep taint-tracking for security; it pattern-spots OWASP-shaped issues. Use the dedicated security-code-review skill for second-pass security work.
- Performance findings are heuristic; they identify shapes (N+1, O(n^2)) but cannot estimate actual cost without profiling data.
- It will not catch all bugs. A clean review from this skill is not a substitute for tests, CI, and human judgement.
- Languages with thinner training coverage (e.g., Crystal, Elm, Nim) will get less idiomatic feedback than mainstream languages.
- The skill does not reason about the team's deployment topology, traffic shape, or SLO budget unless the user provides that context — performance and reliability guidance is therefore general.
- Detection of business-logic bugs (e.g., a discount rule that allows replay) requires understanding of the business, which the skill only has if the user supplies it in `project_conventions` or `pr_description`.
- The skill does not retrieve external resources (issue trackers, design docs, CI logs) unless the host wires those in.

## Sources reviewed

- https://github.com/reviewdog/reviewdog (MIT)
- https://github.com/Nayjest/Gito (MIT)
- https://github.com/codedog-ai/codedog (MIT)
- https://github.com/anc95/ChatGPT-CodeReview (ISC)
- https://github.com/Nikita-Filonov/ai-review (Apache-2.0)
- https://github.com/eslint/eslint (MIT)
- https://github.com/analysis-tools-dev/static-analysis (MIT)
- https://github.com/Luzkan/smells (MIT)
