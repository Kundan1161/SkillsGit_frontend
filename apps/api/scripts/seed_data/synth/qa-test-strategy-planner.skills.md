---
id: skillsgit-curated/qa-test-strategy-planner
version: 1.0.0
name: QA Test Strategy Planner
description: Given a system or feature, produce a layered test plan covering unit, integration, contract, end-to-end, and exploratory tests with risk-based prioritization and tooling picks.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:testing-qa, test-strategy, test-plan, risk-based, test-pyramid, coverage, qa, planning]
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
  estimated_tokens_per_invocation: 6500
trigger_keywords:
  - test strategy
  - test plan
  - how should we test
  - testing approach
  - qa plan
  - test coverage plan
  - risk based testing
  - layered tests
  - test pyramid
  - what tests do we need
  - test design
  - feature test plan
example_invocations:
  - "Write a test strategy for the new checkout flow — what layers, what risks, what tools."
  - "Propose a layered test plan for this microservice spec and prioritize by risk."
  - "We have 6 weeks before launch. Plan tests for this feature so we hit the critical paths first."
inputs:
  - name: system_description
    type: text
    required: true
    description: Architecture overview, the feature spec, or the user story set the plan must cover.
  - name: tech_stack
    type: text
    required: false
    description: Languages, frameworks, datastores, deploy targets. Lets the agent recommend ecosystem-appropriate tools.
  - name: existing_tests
    type: text
    required: false
    description: Summary of what tests already exist so the agent can complement rather than duplicate.
  - name: constraints
    type: text
    required: false
    description: Deadline, team size, CI time budget, compliance bars (SOC2, HIPAA, PCI).
  - name: known_risks
    type: text
    required: false
    description: Areas the team already suspects are fragile or high-blast-radius.
outputs:
  - name: test_strategy
    type: markdown
    description: Layered plan with risk matrix, per-layer test inventory, tooling picks, coverage targets, and a sequenced rollout.
  - name: risk_matrix
    type: json
    description: Machine-readable list of risks with likelihood, impact, owning test layer, and exit criteria.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# QA Test Strategy Planner

## When to use

Use this skill at the start of a feature, before a release hardening sprint, or when a team is rebuilding a testing program that drifted. The trigger is a moment where the question is not "is this single test correct" but "what *set* of tests do we need, and in what order should we build them so the highest-risk failure modes are covered first."

Good fit:

- A new feature spec is approved and the lead asks "what's our test plan."
- A microservice is being extracted from a monolith and inherits no tests.
- A team has 80% unit coverage but production keeps breaking — the strategy is unbalanced.
- A compliance auditor asks for documented testing approach by control area.

Poor fit:

- Single test authoring (use a unit-test generator).
- Debugging a specific flaky test (use the flaky-test-investigator skill).
- Reviewing one diff (use a code-review auditor).

The output is a *plan*, not the tests themselves. It tells the team what to build, in what order, with what tools, and what "done" looks like.

## How to apply

1. **Restate scope in one paragraph.** Before generating any layers, restate what is in and out of scope. List the user-visible behaviors and the system boundaries. If the agent cannot identify the boundary cleanly (e.g. is the third-party payment processor in scope or stubbed?), ask once and proceed.

2. **Inventory the externally observable behaviors.** Walk the spec and emit a numbered list of behaviors the system promises. Each behavior is a candidate for at least one acceptance-level test. Tag each behavior `critical | important | nice-to-have` based on user blast radius and revenue impact.

3. **Inventory the components and seams.** For each module, datastore, message channel, and external integration, list it with a one-line responsibility. The seams between components are where contract tests will live.

4. **Build a risk matrix.** For each behavior and each seam, assign a likelihood (1-5) that it could fail and an impact (1-5) if it did. Product of likelihood and impact yields a risk score. Sort descending. The top quartile gets the most aggressive coverage.

5. **Pick the testing layers.** Default to a pyramid with these tiers: unit, integration (component + datastore + adjacent), contract (between this service and external providers/consumers), end-to-end (user-journey through deployed stack), and exploratory/manual. Add property-based, performance, security, and chaos as cross-cutting layers when the risk matrix demands.

6. **Allocate tests by layer.** For each row in the risk matrix, decide which layer is cheapest and most diagnostic to catch the failure. A wrong calculation in one function: unit. A schema mismatch with an external API: contract. A page that does not render after login: end-to-end. Avoid putting a test at a layer where it cannot diagnose the failure — an e2e test that says "checkout broke" without pointing at the cause is a bug, not a feature.

7. **Set coverage targets per layer, not globally.** A flat "90% line coverage" target encourages testing trivial getters. Instead: critical-path branch coverage 95%, integration coverage of every persisted-state transition, contract coverage of every consumer-producer pair, end-to-end coverage of every revenue-bearing user journey.

8. **Pick concrete tools per layer.** Recommend specific tools that match the stack. For each pick name 1-3 alternatives and the trade-off. Do not over-prescribe; if the team already uses a tool that works, keep it. Examples of categories to fill: unit runner, mocking library, integration harness (containers or in-memory fakes), contract framework, e2e driver, property-based library, mutation testing tool, accessibility scanner.

9. **Decide on test data strategy.** Three options: factories (programmatic builders for each entity), fixtures (versioned static files), and ephemeral generation (faker + seed). Recommend a primary and a fallback. Specify cleanup strategy: per-test transactions, per-suite truncation, or disposable namespaces.

10. **Plan environments.** Local developer loop must run unit and integration in under two minutes or developers will not run them. CI runs everything on every PR. A pre-prod environment runs the e2e suite against a deployed artifact. Production runs synthetic e2e probes for the top three user journeys.

11. **Define the deterministic-ness contract.** Every test must have a defined source for time (frozen clock or injected now()), a defined source for randomness (seeded), and a defined source for IDs (deterministic generators). Without this, the plan will produce flakes.

12. **Sequence the build-out.** Order the work: (a) failing unit tests for any critical-path code that has none, (b) contract tests at every seam, (c) integration tests for every persisted-state transition, (d) e2e probes for top user journeys, (e) cross-cutting layers. Each tier is independent and produces value even if the next tier is never built.

13. **Specify the CI execution model.** Parallelism strategy (shard count, shard-by-file vs shard-by-test), retry policy (retry once only on infrastructure error, never on assertion failure), and the merge-block bar (which suites must be green to merge vs. which run nightly).

14. **Plan reporting.** Pick a structured output format (JUnit XML, CTRF JSON, or platform-native) so trends and ownership can be mined. Designate a flake dashboard owner. Define the SLO for test-suite runtime and the burn-down for flake rate.

15. **Define exit criteria per layer.** "Done" for unit: all critical-path branches covered, mutation score above target. "Done" for integration: every persisted state transition exercised. "Done" for contract: every consumer-producer pair has a published contract. "Done" for e2e: every behavior tagged `critical` has a passing journey.

16. **Plan exploratory testing.** Schedule charters: a 90-minute timeboxed session with a written mission ("explore the password-reset flow on mobile Safari, focusing on what happens when the email link is stale"). Record findings as new automated tests, not as a separate report stream.

17. **Plan negative space.** For every behavior, list at least one anti-behavior: input that should be rejected, race that should be detected, timeout that should be enforced. Negative-space tests catch the bugs the team did not imagine.

18. **Plan performance tests.** Define a representative workload, the metric that matters (p99 latency, throughput, memory ceiling), and the regression threshold (fail if p99 worsens by more than 10% vs the last main build). Run on every PR for hot paths, nightly for the whole system.

19. **Plan security testing.** SAST in CI for every PR, dependency scan nightly, DAST against a deployed environment weekly. For features that touch auth, payment, or PII, add a dedicated abuse-case test set.

20. **Plan chaos and resilience tests.** For each external dependency, define the failure mode (timeout, 500, slow, partial response) and ensure there is a test that exercises the system under that mode. Run periodically against a staging environment.

21. **Document the strategy.** Emit a single markdown document with sections: scope, risk matrix, layers and tool picks, coverage targets, environments, data strategy, CI model, exit criteria, and the sequenced rollout. Keep it under ten pages — anything longer is not read.

22. **Make ownership explicit.** Assign each layer to a person or sub-team. Untaken ownership leads to silent rot. Include a quarterly review cadence to re-score the risk matrix.

23. **Build the risk-matrix JSON.** Emit machine-readable rows so they can be tracked in a tool: `{behavior, seam, likelihood, impact, score, layer, status}`.

24. **Predict the cost.** Estimate engineer-weeks per layer to reach the exit criteria, and the steady-state CI minutes per PR. Surface this so the team can negotiate scope.

25. **Highlight known unknowns.** Close with a section "what this plan does not catch" — explicit out-of-scope categories such as cross-browser visual regressions if no tool is in the plan for them. Buyers of the plan must know its blind spots.

## Inputs

- `system_description` (required): the spec, RFC, or architecture summary to plan against.
- `tech_stack` (optional): languages, frameworks, datastores. Without this the agent recommends tool-agnostic categories.
- `existing_tests` (optional): brief summary of what already exists so the plan complements.
- `constraints` (optional): deadline, team size, CI budget, compliance regime.
- `known_risks` (optional): prior incidents, fragile areas, dependencies the team distrusts.

## Outputs

- `test_strategy` (markdown): the strategy document with all sections.
- `risk_matrix` (json): rows of behavior/seam, likelihood, impact, score, owning layer, status.

## Examples

**Example: payment-capture microservice**

Input: a service that authorizes and captures card payments against three external processors with idempotent retry semantics. Team of three engineers, six-week timeline.

The agent produces:

- Scope statement excluding the front-end checkout (covered by another team) but including the internal idempotency store.
- Behavior list: 14 items, four tagged `critical` (authorize, capture, refund, idempotent retry).
- Risk matrix top entries: processor-A timeout under load (5x5), idempotency-key collision (4x5), partial-capture reconciliation (4x4).
- Layer plan: unit for amount-arithmetic and currency conversion; integration for the idempotency store with a containerized database; contract tests for each of the three processor adapters; e2e for the four critical behaviors against a sandbox processor; chaos for processor timeout and 5xx; performance for the capture endpoint at the documented peak.
- Tool picks: language-native unit runner, testcontainers for integration, a contract-testing framework with a broker, a headless e2e runner, a property-based library for the currency-conversion module, a mutation-testing tool to validate unit suite quality.
- Sequenced rollout: week 1 unit, week 2 contract, week 3-4 integration, week 5 e2e and performance, week 6 chaos and exploratory.
- Exit criteria: unit mutation score 75+, contract coverage 100%, e2e green for all four critical behaviors, p99 capture latency under 400ms at 500 rps.

## Limitations

- The plan is only as good as the supplied spec. A vague spec yields a vague plan; the agent will ask one clarifying question but will not invent requirements.
- Tool picks are starting points, not endorsements. Always validate licensing and operational fit before adopting.
- Coverage numbers are heuristics. A 75% mutation score in one codebase is excellent; in another it hides a critical untested branch. Treat targets as conversation starters, not contracts.
- The plan does not estimate calendar time precisely. Engineer-week estimates are rough.
- This skill does not generate the tests themselves. It produces the plan and inventory; pair it with code-generation skills to author the tests.
- The skill cannot judge organizational readiness. A great plan dies on a team without test infrastructure ownership. The plan flags this risk but cannot fix it.
- Compliance regimes (HIPAA, PCI, SOC2) are surfaced as constraints but the plan is not a substitute for a formal compliance assessment.

## Sources reviewed

- https://github.com/microsoft/playwright
- https://github.com/cypress-io/cypress
- https://github.com/pact-foundation/pact-python
- https://github.com/pact-foundation/pact-jvm
- https://github.com/dubzzz/fast-check
- https://github.com/stryker-mutator/stryker-js
- https://github.com/ctrf-io/github-test-reporter
