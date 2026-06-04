---
id: skillsgit-curated/qa-flaky-test-investigator
version: 1.0.0
name: QA Flaky Test Investigator
description: Diagnose flaky tests from logs, code, and CI history — classify the root cause, recommend a stabilization fix, and decide quarantine vs. delete vs. rewrite.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:testing-qa, flaky-tests, ci, debugging, test-reliability, root-cause, stabilization]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1]
  tools_required: [file_io]
  tools_optional: [code_execution, web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 5500
trigger_keywords:
  - flaky test
  - flaky tests
  - intermittent test failure
  - test passes locally fails in ci
  - stabilize test
  - quarantine test
  - test flake
  - retry flaky
  - non-deterministic test
  - heisenbug
  - test failing sometimes
  - test instability
example_invocations:
  - "This test fails about 1 in 10 times in CI but never locally — diagnose and fix it."
  - "Classify the root cause of this flake and tell me whether to quarantine or rewrite."
  - "Here are three failure logs from the same test on different runs. What is the pattern?"
inputs:
  - name: test_source
    type: text
    required: true
    description: The test file source (and the production code it exercises, if available).
  - name: failure_logs
    type: text
    required: true
    description: One or more failure logs from the flake. More samples make the diagnosis stronger.
  - name: pass_history
    type: text
    required: false
    description: Recent CI history for the test (pass/fail counts, durations, branches).
  - name: stack
    type: text
    required: false
    description: Language, test runner, key dependencies (database, queue, browser).
  - name: ci_config
    type: text
    required: false
    description: Relevant CI shards, parallel workers, retry policy, timeout settings.
outputs:
  - name: diagnosis
    type: markdown
    description: Classified root cause, supporting evidence from the logs and code, and the recommended fix.
  - name: fix_diff
    type: text
    description: A suggested patch (unified diff or before/after blocks) that addresses the root cause.
  - name: triage_decision
    type: json
    description: Decision record with fields {action, category, confidence, owner_hint, follow_ups}.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# QA Flaky Test Investigator

## When to use

Use this skill when a test fails inconsistently — green on one run, red on the next, with no code change in between. The skill is for the moment after the team has noticed the pattern but before they have decided what to do with the offending test. It produces a root-cause classification, a recommended fix, and a triage decision that names the action and owner.

Good fit:

- A CI run failed, a re-run passed, and the team needs to know whether to ignore it or take action.
- A test has been flaking for weeks and someone finally has time to fix it.
- A new test was merged and immediately started flaking on `main`.
- The flake dashboard is too long and someone is triaging the top offenders.

Poor fit:

- A test that has always failed since it was written (that is a broken test, not a flake).
- A test that fails deterministically only in a specific environment (that is an environment bug).
- A general "my CI is slow" question (use a CI performance skill).

The skill operates on evidence: at least the test source and at least one failure log. With one log it produces a hypothesis; with three or more it produces a confident classification.

## How to apply

1. **Confirm flakiness before investigating.** Verify the failure is intermittent. If the supplied logs all show the same line and the same assertion, ask whether the test ever passed on the same commit. A deterministic failure is not a flake; redirect the user.

2. **Read the test top to bottom.** Identify the system under test, the test's setup, the assertion, and the teardown. Note any external resources touched: clock, network, filesystem, database, queue, browser, subprocess.

3. **Read the failure log top to bottom.** Identify the line of code that raised, the timestamp, the worker or shard, any preceding log messages from the same test, and the duration vs. the median. Long-tail durations are evidence of timing flakes.

4. **Look for variance sources.** Walk the variance checklist and mark which apply: clock-dependent assertion, randomness without seeding, ordering-dependent assertion on an unordered collection, race between parallel actors, shared state across tests, external service call without a stub, filesystem path collision, network port collision, animation or layout timing in a browser test, garbage-collection or memory pressure pause.

5. **Classify into one of the canonical categories.** Use this taxonomy:
   - **Async/timing**: assertion runs before the system has finished; fixed sleeps; missing `await`.
   - **Order dependence**: a previous test leaks state; tests assume execution order.
   - **Shared resource**: two tests write the same row, file, port, or environment variable.
   - **Network or external service**: outbound call hits a real service or an unstable stub.
   - **Concurrency**: race condition inside the system under test, surfaced only sometimes.
   - **Resource exhaustion**: memory, file descriptors, threads, connections leak across runs.
   - **Environment**: tests behave differently by OS, locale, timezone, CPU count.
   - **Non-determinism in production code**: the system itself is non-deterministic and the test is right to fail occasionally.
   - **Snapshot drift**: a snapshot test sensitive to platform-specific formatting.
   - **Real bug**: the system under test has a defect the flake reveals.

6. **Pin the evidence.** For the chosen category, cite the specific log line, code line, and variance source. Avoid hand-waving — every classification carries a one-line citation.

7. **Estimate confidence.** With one log and a clear smoking gun, confidence is medium. With three independent failure modes pointing to the same root cause, confidence is high. With a single ambiguous log, confidence is low; ask for more logs rather than fabricating.

8. **Decide the action.** Pick one of: fix, quarantine, rewrite, delete, escalate as production bug. Use this rubric:
   - Clear root cause + cheap fix → **fix**.
   - Clear root cause + expensive fix + low business value → **delete** or rewrite at higher level.
   - Unclear root cause + business-critical test → **quarantine** with an issue and a 14-day deadline; do not lose the signal.
   - Unclear root cause + low-value test → **delete**; preserve the file in git history.
   - Evidence of a real concurrency bug in production code → **escalate**; the test was right.

9. **Write the fix.** Produce a unified diff or before/after block. The fix must address the root cause, not the symptom. Replacing `sleep(2)` with `sleep(5)` is symptom-treating; replacing it with an explicit wait-for-condition is root-cause treating.

10. **Eliminate fixed sleeps.** Almost every fixed sleep in a test is a flake waiting to happen. Replace with poll-until-condition, event subscription, or fixture-emitted readiness signal. Cap with a generous timeout that fails loudly when the system genuinely hangs.

11. **Freeze time when time matters.** If the assertion compares to `now()` or a duration, inject the clock or use a time-freezing library. Never compare to wall-clock without a tolerance.

12. **Seed randomness.** Any test that uses random data must seed the generator and emit the seed on failure so the failure is reproducible. A reproducer is half the fix.

13. **Isolate shared state.** Move shared globals into per-test fixtures. Use transactional rollbacks for databases, temp directories for files, ephemeral ports for sockets, and process-scoped namespaces for queues.

14. **Stub external services.** No test below the e2e layer should hit a real network. If the system under test calls out, supply a deterministic in-process double. For e2e tests, ensure the external sandbox itself is stable and document its SLO.

15. **Order-proof the suite.** Run the suite with a randomized order locally (most runners support `--random` or `--shuffle`). Tests that fail only under shuffled order have order dependence.

16. **Detect concurrency bugs in production code.** If multiple worker counts produce different failure rates, the suspect is a race in production. Bring out logging at the suspect critical section; if the race is real, file it as a production bug and quarantine the test until it is fixed.

17. **Watch the long tail.** Failures that show p99 duration 10x the median often mean the test occasionally waits on a real resource (DNS, image pull, container start). Pre-warm the resource in a setup hook.

18. **Address snapshot flakes specifically.** If the test compares against a stored snapshot, normalize the comparison: strip timestamps, IDs, absolute paths, and ordering of unordered collections before diffing. Re-record snapshots after the fix.

19. **Decide on retry policy carefully.** Retry on infrastructure errors only (network reset, container OOM). Never retry on assertion failure — it hides real bugs. Limit to one retry. Surface the retry count in dashboards so silent flakes do not survive.

20. **Document quarantine with deadlines.** When quarantining, write an issue with: the root-cause hypothesis, the evidence, the deadline (default 14 days), the owner, and the exit criteria. Quarantined tests without deadlines become permanent.

21. **Emit the triage decision JSON.** Include `{action, category, confidence, owner_hint, follow_ups, evidence}`. The follow-ups field captures suite-wide patterns: if the same fixed-sleep antipattern shows up here, suggest a suite-wide audit.

22. **Look for patterns across multiple flakes.** If the user supplies multiple flakes, identify the common root cause across them. A single antipattern (e.g. tests relying on shared mutable fixtures) often produces dozens of flakes.

23. **Surface the cost of inaction.** Briefly quantify the impact: minutes of engineer time per failed run, merge delays, signal-loss on real regressions. Cost framing earns the fix priority.

24. **Verify the fix.** Recommend a verification protocol: run the test 100 times in the production CI environment, sharded across the actual CI workers, with the actual parallelism. Local repro is necessary but not sufficient.

25. **Close the loop.** When the fix lands, the test must come out of quarantine and the issue must be closed. Recommend a check-in cadence so quarantined tests do not accumulate.

## Inputs

- `test_source` (required): the test file and ideally the production code it exercises.
- `failure_logs` (required): one or more failure logs. More is better.
- `pass_history` (optional): CI history showing the failure pattern.
- `stack` (optional): language, runner, key dependencies for tool-specific advice.
- `ci_config` (optional): parallelism, retries, and timeouts to interpret duration anomalies.

## Outputs

- `diagnosis` (markdown): classification, evidence, root cause, and recommended fix discussion.
- `fix_diff` (text): unified diff or before/after blocks of the recommended change.
- `triage_decision` (json): action, category, confidence, owner hint, follow-ups, evidence.

## Examples

**Example: a payment-capture e2e test fails 1-in-15**

Input: a Playwright test that captures a payment and asserts a confirmation page. Three failure logs all show "expected confirmation, got loading spinner."

The agent produces:

- Diagnosis: timing flake. The test asserts the confirmation text immediately after clicking submit; the page enters a 1-2 second loading state during a real payment-processor call.
- Evidence: the failed runs all show a p99 click-to-assertion gap below 500ms; the passing runs cluster around 1500ms.
- Fix: replace the immediate text assertion with `expect(page.getByText('Confirmation')).toBeVisible({ timeout: 5000 })`. Remove the explicit `waitForTimeout(1000)` four lines above.
- Triage decision: `{action: fix, category: async/timing, confidence: high, owner_hint: checkout-team, follow_ups: [audit suite for other waitForTimeout calls]}`.

**Example: a database test fails only when shard count is greater than two**

Input: a Python integration test inserting into a `users` table.

The agent produces:

- Diagnosis: shared-resource flake. Two workers insert a row with the same email at the same time. The unique constraint raises in one of them.
- Evidence: failure log shows `IntegrityError: duplicate key value violates unique constraint "users_email_key"`. The test uses a hardcoded email.
- Fix: replace the literal email with a factory that suffixes a worker-scoped unique identifier; wrap each test in a transaction that rolls back.
- Triage decision: `{action: fix, category: shared resource, confidence: high, owner_hint: backend, follow_ups: [audit factories for hardcoded uniques]}`.

## Limitations

- One log produces a hypothesis, not a conclusion. The skill is most useful with three or more independent failure samples.
- The skill cannot run the test itself. It reasons from supplied artifacts; if the evidence is thin, the diagnosis is thin.
- Concurrency bugs that surface only under production load may be invisible from a single CI log; recommend production-scale repros.
- Snapshot flakes require the snapshot file; without it the skill can only guess at the diff.
- The skill does not refactor the entire suite. It addresses the supplied flake and flags suite-wide patterns as follow-ups.
- Quarantine guidance assumes the team has a quarantine mechanism (test tag, skip annotation, or dashboard). If none exists, the skill recommends building one before quarantining.
- The skill is conservative about declaring a production bug; it requires multiple corroborating signals before escalating.

## Sources reviewed

- https://github.com/microsoft/playwright
- https://github.com/cypress-io/cypress
- https://github.com/dubzzz/fast-check
- https://github.com/BurntSushi/quickcheck
- https://github.com/stryker-mutator/stryker-js
- https://github.com/ctrf-io/github-test-reporter
- https://github.com/typelevel/scalacheck
