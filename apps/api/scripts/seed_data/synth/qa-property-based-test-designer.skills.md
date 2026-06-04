---
id: skillsgit-curated/qa-property-based-test-designer
version: 1.0.0
name: QA Property-Based Test Designer
description: Convert example-based tests into property-based tests — identify invariants, design generators, set shrinking strategy, and produce runnable test code in the target framework.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:testing-qa, property-based, generative-testing, invariants, shrinking, generators, unit-tests]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1]
  tools_required: [file_io]
  tools_optional: [code_execution]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 5500
trigger_keywords:
  - property based test
  - property based testing
  - generative test
  - invariant test
  - fast-check
  - quickcheck
  - hypothesis
  - shrinking strategy
  - test generator
  - replace example tests
  - find edge cases
  - random testing
example_invocations:
  - "Convert this example-based test into a property-based test in fast-check."
  - "What invariants should I test for this serialization function? Give me properties."
  - "Design generators and shrinkers for this domain object so I can fuzz the parser."
inputs:
  - name: function_or_module
    type: text
    required: true
    description: The code under test — function signature, types, and any preconditions.
  - name: existing_tests
    type: text
    required: false
    description: Example-based tests already written. The agent uses them to infer intended behavior.
  - name: target_framework
    type: choice
    required: false
    description: Which property-based library to emit code for.
    choices: [fast-check, hypothesis, scalacheck, quickcheck-rust, jqwik, stream-data, proptest, auto-detect]
  - name: domain_notes
    type: text
    required: false
    description: Business rules, invariants the team already knows, or known edge cases.
outputs:
  - name: properties_design
    type: markdown
    description: Identified invariants, generator design, shrinking notes, and rationale for each property.
  - name: test_code
    type: text
    description: Runnable property-based test code in the target framework.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# QA Property-Based Test Designer

## When to use

Use this skill when a function or module has clear inputs, clear outputs, and a behavior that can be expressed as a rule (an invariant) rather than as a list of examples. Property-based tests fuzz the input space and shrink failing cases to minimal counterexamples; they find bugs example tests miss because the developer who wrote the examples did not imagine the bad input.

Good fit:

- Parsers, serializers, encoders, decoders. Round-trip is the canonical property.
- Pure functions over algebraic types (lists, maps, trees, custom domain entities).
- State machines with verifiable invariants (sums conserve, counts monotonic, balances non-negative).
- Refactors where the team wants confidence the new implementation matches the old.
- Boundary-heavy logic: currency arithmetic, date math, paging, retry timing.

Poor fit:

- UI behavior, time-coupled code, or anything that touches the network. Stub first, then property-test the pure core.
- Functions with no expressible property — if the only spec is "do what the user wants," property tests will not help.
- Algorithms whose specification is "match this reference implementation" — that is a differential test, which is a specific property; still useful, but specify it explicitly.

The skill is for the moment the team has example tests passing and asks "what else could I test." It identifies the invariants, designs generators, and emits runnable code.

## How to apply

1. **Read the signature first.** Note the input types, output type, and any documented preconditions. The input types determine the generators; the output type determines the assertion shape.

2. **Read existing tests to learn intent.** Example tests encode the developer's understanding of the behavior. Extract the implicit rule that explains why each example produces its expected output.

3. **Find the round-trip if one exists.** For any function `f` paired with an inverse `g`, the property `g(f(x)) == x` for all `x` is gold. Parsers/printers, serializers/deserializers, encoders/decoders, encrypt/decrypt, encode/decode — these are the canonical examples.

4. **Find conservation laws.** A function preserves some quantity. `sort(xs).length == xs.length`, `sum(map(double, xs)) == 2 * sum(xs)`, `merge(a, b).count == a.count + b.count` when keys disjoint.

5. **Find ordering and monotonicity properties.** Sorted output is sorted. Adding a positive number never decreases the result. A retry's nth wait is at least as long as its (n-1)th.

6. **Find idempotence.** Applying `f` twice equals applying it once. Common for normalizers, canonicalizers, deduplicators.

7. **Find commutativity and associativity when applicable.** `merge(a, merge(b, c)) == merge(merge(a, b), c)`. `union(a, b) == union(b, a)`. Often reveals subtle bugs around order-dependence.

8. **Find oracles.** A trusted reference implementation can be the oracle: "for all `x`, `new_impl(x) == old_impl(x)." This is the differential-testing variant and is the most powerful property for refactors.

9. **Find postconditions weaker than equality.** Sometimes the exact output is hard to specify but a weaker property holds: the output is always non-empty, always within a known range, always a valid instance of the target type. Weaker properties still catch bugs.

10. **Find anti-properties.** Inputs the function should reject. Property: for all malformed inputs in some generator, the function raises a specific error type and does not corrupt state.

11. **Design the generators.** For each input type, design a generator that produces values across the expected range. Cover empty, single-element, large, sorted, reverse-sorted, all-equal, and edge values (0, MAX, negative, unicode boundaries) by composing primitive generators. Do not write one omnibus generator; layer small ones.

12. **Bias generators toward edge values.** A uniform random generator rarely produces the empty list, the boundary integer, or the all-equal case. Compose with `oneOf` or `frequency` to ensure those values appear in roughly 10-30% of samples.

13. **Constrain generators to preconditions, not assertions.** If the function has a precondition (sorted input), use a generator that produces sorted lists — do not generate random lists and skip the unsorted ones. Skipping shrinks the effective sample size and biases coverage.

14. **Design generators for domain types.** Build a generator per domain entity (user, order, invoice). Compose them to build nested fixtures. Generator code should be reusable across many properties.

15. **Plan shrinking.** When a property fails, the framework will try to shrink the counterexample to the minimum failing input. For built-in types this works out of the box. For custom domain types, ensure the generator is built from shrinkable primitives so shrinking finds the minimal trigger.

16. **Choose the sample budget.** Default 100-200 cases per property. Up to 1000 for cheap pure functions where the input space is large. Mark slow properties explicitly and run them less often.

17. **Set a seed reporting policy.** Every test run must log the seed of any failing property so the failure is reproducible. The shrink-minimized counterexample plus the seed are the bug report.

18. **Write the first property and run it once.** Do not produce a wall of properties before validating the approach. Run one property, watch it pass, then add the next. Each property is small, focused, and named for the invariant it expresses (`prop_decode_inverts_encode`, `prop_sort_preserves_length`).

19. **Specify what the property does NOT cover.** Property-based tests sample. They are not exhaustive. State explicitly which classes of inputs the generator covers and which it does not, so reviewers know the gap.

20. **Combine with examples.** Property tests do not replace example tests for documented behaviors. Keep at least one example per documented behavior as living documentation; properties cover the unspecified space.

21. **Add stateful property testing if the system has state.** For state machines and stores, model the abstract state, generate sequences of operations, and assert invariants hold after every operation. This is more involved but catches concurrency-adjacent bugs.

22. **Handle non-determinism.** If the function is non-deterministic by design (clock, random), inject the source so the property runs deterministically. If it is non-deterministic by accident, that is the bug — file it.

23. **Detect coverage of the generator.** Use the framework's coverage collector (e.g. `collect`, `classify`, `statistics`) to verify the generator produces a balanced mix. A generator that produces empty inputs 99% of the time defeats the test.

24. **Tune for speed.** A property that takes 5 seconds per case will not be run. Split slow properties into a separate suite; keep the hot loop under a second per case.

25. **Document the properties in plain English.** Above each property in the test file, a one-line comment names the invariant: `// decode is the left inverse of encode`. The comment is what someone reads when the property fails.

26. **Emit framework-idiomatic code.** Match the conventions of the target library: arbitraries in fast-check, strategies in hypothesis, generators in scalacheck. Do not invent a cross-framework abstraction.

27. **Wire the shrunken counterexample into the failure message.** Print the shrunken input, the actual output, the expected output, and the seed.

28. **Sketch the rollout.** Identify three to five high-value functions to property-test first (parsers, serializers, financial math). Save state-machine testing for after the team is comfortable with stateless properties.

## Inputs

- `function_or_module` (required): the code under test with types and preconditions.
- `existing_tests` (optional): example tests that document intent.
- `target_framework` (optional): the property-based library to emit code for; `auto-detect` picks from the stack.
- `domain_notes` (optional): business rules, invariants, known edges.

## Outputs

- `properties_design` (markdown): invariants found, generators designed, shrinking notes, rationale.
- `test_code` (text): runnable property-based test code in the chosen framework.

## Examples

**Example: a price-formatting function**

Input: a function `format(amountCents: number, currency: string): string`. Existing examples cover USD with positive amounts.

The agent identifies:

- Round-trip: `parse(format(x, c)) == x` for all integer cents and supported currencies.
- Conservation: the formatted string contains a numeric portion whose value in cents equals the input.
- Idempotence: formatting twice via a `format -> parse -> format` chain returns the same string.
- Negative amounts produce a leading minus sign or a parenthesized form, per the spec.
- Anti-property: an unsupported currency raises a specific error.

Generators:

- `amountCents`: integers from `-1_000_000_000` to `1_000_000_000`, biased toward 0, 1, -1, MAX, and locale-significant values (100, 1000, 100000).
- `currency`: `oneOf` over the supported set, plus 5% rate of a "not supported" generator for the anti-property.

The agent emits a fast-check spec with five `fc.property` blocks, each named for the invariant, and the rationale paragraph above each one.

**Example: a paginator over a list**

Input: `paginate(items, pageSize, pageIndex)` returns the slice plus a `hasMore` flag.

Invariants:

- Concatenating every page reconstructs the input list in order.
- No item appears in two pages.
- `hasMore` is false on the last page, true on every earlier page (for non-empty input).
- For `pageSize <= 0`, the function rejects with a specific error.

The agent designs a generator producing `(items, pageSize, pageIndex)` tuples with the precondition `0 <= pageIndex < ceil(items.length / pageSize)` baked in, and emits the four properties.

## Limitations

- Property-based testing only finds bugs the generator can produce. A generator that misses an entire class of inputs will not catch bugs in that class.
- Properties can hide bugs when they are too weak. "Output is non-empty" passes for many wrong outputs.
- Stateful property testing is powerful but harder to write. The skill produces a sketch; full models often need iteration.
- Some domains have no obvious properties; example tests remain primary there.
- The skill emits code in one framework. Cross-framework portability requires manual translation.
- Tuning generator coverage is an art; the skill recommends `classify`/`collect` calls but cannot guarantee balance without execution.
- Property tests can be slow. Generators that produce large inputs will need a sample-size knob the skill surfaces but does not tune.

## Sources reviewed

- https://github.com/dubzzz/fast-check
- https://github.com/typelevel/scalacheck
- https://github.com/BurntSushi/quickcheck
- https://github.com/stryker-mutator/stryker-js
- https://github.com/microsoft/playwright
- https://github.com/ctrf-io/github-test-reporter
