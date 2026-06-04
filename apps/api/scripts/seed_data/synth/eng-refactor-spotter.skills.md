---
id: skillsgit-curated/refactor-opportunity-spotter
version: 1.0.0
name: Refactor Opportunity Spotter
description: Scan code or a diff for refactor candidates — long methods, primitive obsession, duplicated logic, dead code, conditional complexity — with concrete refactor moves.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [refactoring, code-smells, code-quality, maintainability, technical-debt, cleanup, design-patterns]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  min_context_tokens: 16000
  estimated_tokens_per_invocation: 6500
trigger_keywords:
  - find refactor opportunities
  - refactor this
  - code smells
  - clean up this code
  - too complex
  - long method
  - duplicated code
  - dead code
  - technical debt scan
  - improve this code
  - extract method suggestions
  - simplify this
example_invocations:
  - "Scan this module for refactor opportunities and rank them by impact."
  - "Find code smells in the file I just pasted and suggest specific refactor moves."
  - "Look for duplicated logic and primitive obsession in this directory snapshot."
inputs:
  - name: code
    type: text
    required: true
    description: One or more files or a directory snapshot. Whole files are strongly preferred over diffs for refactor work.
  - name: language
    type: choice
    required: false
    description: Primary language. Inferred from extensions if omitted.
    choices: [python, typescript, javascript, go, java, ruby, rust, csharp, php, kotlin, swift, scala, mixed]
  - name: codebase_style
    type: text
    required: false
    description: Idiom preferences — e.g. "functional Kotlin, avoid inheritance", "prefer small modules over big classes".
  - name: scope
    type: choice
    required: false
    description: Whether the agent should emit big architectural moves or stay surgical.
    choices: [surgical, balanced, ambitious]
outputs:
  - name: refactor_report
    type: markdown
    description: Ranked list of refactor opportunities, each with smell, refactor move, payoff, risk, and a sketch of the change.
  - name: opportunities_json
    type: json
    description: Machine-readable opportunities for tooling (file, line range, smell, refactor, impact, effort).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Refactor Opportunity Spotter

## When to use

Use this skill when a developer is staring at code that "works but feels wrong" and wants concrete, ranked suggestions for what to refactor and how. Typical moments:

- A module has grown by accretion and now resists change.
- Before opening a feature ticket in a hot file, the team wants to know what to tidy first.
- After a bug, the developer suspects the bug had structural roots and wants to know what structure to fix.
- Pre-merge: a reviewer wants to flag refactor opportunities the author should consider before approval — without blocking merge.
- During a quarterly tech-debt review.

This skill is opportunity-spotting, not defect-finding. It does not report bugs (use PR Review Auto-Auditor) or security issues (use Security Code Review Pass). It reports structural improvements that would make the code easier to read, change, and test in the future.

The skill is calibrated to *not* over-fire. Refactors have a cost; the report is conservative and only surfaces opportunities where the payoff visibly exceeds the disruption. Empty reports are valid outputs — code that has no compelling refactor opportunity should be told as much.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `code` | yes | The code to scan. Whole files give much better refactor signals than diffs. |
| `language` | no | Selects idiom-specific moves (e.g. Python dataclasses, TS discriminated unions). |
| `codebase_style` | no | Avoids fighting the team's chosen style. |
| `scope` | no | Surgical keeps moves under ~30 lines each; ambitious includes module splits and design-pattern introductions. |

## How to apply

### Stage 1 — Map the code

1. List the files received. For each file, count: total lines, number of functions/methods/classes, longest function, deepest nesting, longest parameter list, public surface (exported symbols).
2. Build a dependency sketch: which files import which, which functions are called only from one place, which are called from many.
3. Identify "hot spots" — files in the top 25% of length or nesting. Refactor candidates concentrate here.
4. Identify "frozen islands" — files with no callers found in the provided code; these are either entry points (don't refactor without intent) or dead code (potential big win).

### Stage 2 — Walk the smell catalog

Each smell below is checked file-by-file. The agent records an opportunity record with: file, line range, smell tag, severity (high / medium / low), proposed refactor move name, estimated payoff (high / medium / low), estimated effort (S / M / L), risk (S / M / L), and a 3-5 sentence sketch of the move.

5. **Long method.** Any function longer than ~50 lines, or ~30 lines with nested conditionals, is a candidate. Move: Extract Method on the largest sub-block; or Replace Loop With Pipeline; or Decompose Conditional. Prefer extracting the named concept (the part that has a name in the developer's head) over arbitrary chunking.
6. **Long class / God object.** A class with more than ~7 public methods, or more than ~300 lines, or holding multiple unrelated responsibilities. Move: Extract Class on the clusters of methods that share state; or Extract Subclass; or Move Method to where the data lives.
7. **Long parameter list.** Functions with more than ~4 parameters, especially when several of them are always passed together. Move: Introduce Parameter Object (turn the always-together group into a struct/dataclass/record); or Replace Parameter With Method Call when the caller can already produce the value.
8. **Primitive obsession.** Strings or ints standing in for richer types (e.g., `userId: string`, `emailAddress: string`, `currency: string`, `cents: int`). The smell is strongest when the same primitive flows through many functions and constraints on it live in comments. Move: Introduce a small value type (newtype / opaque type / branded type / Value Object). Especially impactful for money, time, identifiers, units.
9. **Data clumps.** The same 2-4 fields appear together in many signatures or many class fields (`firstName, lastName, dob, email` in five places). Move: Extract Class / Extract Record. After extraction, the methods that operate on the clump usually want to move onto the new type (see "feature envy" below).
10. **Feature envy.** A method that calls more methods on another object than on its own; or a function that destructures another struct and operates on it heavily. Move: Move Method to the data; or Extract Method then Move Method.
11. **Inappropriate intimacy.** Two classes/modules that reach deep into each other's internals. Move: Move Method, Move Field, or Extract Class to create a clean intermediary.
12. **Switch statements / type-coded dispatch.** Repeated `switch` or `if/elif` chains on a "kind" field, especially when the same shape appears in more than one place. Move: Replace Conditional With Polymorphism (object-oriented contexts); Replace Type Code With Strategy; Discriminated Union + exhaustive `match` (TS/Rust/Scala). When polymorphism would be over-engineering, prefer a dispatch table.
13. **Boolean parameters.** Calls like `f(x, true)` where `true`'s meaning is obscure. Move: Split Phase (one function for each meaning); or named-argument style; or Introduce Parameter Object.
14. **Flag arguments threaded through call stacks.** A boolean (often `dryRun`, `force`, `debug`) passed through 5+ functions. Move: Inject Behavior (pass a strategy/callback instead) or Replace With Context Object near the boundary.
15. **Mutable shared state.** Module-level mutable variables, singletons that hold business state, classes whose methods mutate instance fields in surprising orders. Move: Encapsulate Variable, Pure Function extraction, or Hide Mutability behind an explicit transaction-style API.
16. **Comments that explain code.** Long block comments above complicated code. The comment is a smell — the code should be rewritten to obviate it. Move: Extract Method with the comment's first sentence as the method name. Different smell: comments explaining *why* (intent, history) — those are valuable; keep them.
17. **Magic numbers and strings.** Literal values without names. Move: Replace Magic Number With Named Constant; or Introduce Enum / Sealed Type for sets of related literals.
18. **Speculative generality.** Abstract classes with one subclass, interfaces with one implementation, parameters never varied at call sites, configuration options never overridden, "extensibility points" with no extensions. Move: Inline Class, Inline Interface, Remove Parameter, Delete Dead Hook. Pay attention to scope: in a library this may be intentional; in app code it is usually waste.
19. **Dead code.** Functions never called, imports never used, classes defined but never instantiated, conditional branches that are statically unreachable, feature flags long set to a constant. Move: Delete. Then re-check tests still pass (in the report, recommend the verification step explicitly).
20. **Duplicated code.** Same logic copied across 2+ sites. Three flavors: exact copies (high confidence, easy move); near-copies with small parameter differences (Extract Method with parameter); structural duplication (the same shape implemented differently — usually indicates a missing abstraction). Move: Extract Method, Pull Up Method (inheritance), or Introduce Template.
21. **Divergent change.** A file changes for many unrelated reasons (every feature touches it). Move: Split Module along the reasons-for-change axis.
22. **Shotgun surgery.** One conceptual change requires edits in many files. Move: Move related state and behavior together so the change becomes local.
23. **Nested conditionals beyond 3 levels.** Move: Decompose Conditional, Replace Nested Conditional With Guard Clauses, Extract Method.
24. **Negative names.** Methods like `is_not_empty`, conditions like `if !isInvalid()`. Double negatives are a smell. Move: Rename or invert.
25. **Lying names.** A function `getX` that mutates state, `parse` that throws based on environment, `Validator` that transforms. Move: Rename.
26. **Boolean blindness.** Functions that return booleans where a richer return would convey reason (`canRead()` → `readPermission(): Allowed | Denied(reason)`). Move: Replace Boolean With Algebraic Type, especially impactful at module boundaries.
27. **Train wrecks.** Long `.a.b.c.d.e` chains across object boundaries. Move: Hide Delegate or extract an aggregate method that returns the final value.
28. **Loop with shape baked in.** Hand-rolled loops that implement standard operations (map/filter/reduce/groupBy). Move: Replace Loop With Pipeline (where the language has the idiom).
29. **Mutable defaults / shared default.** Python `def f(x=[])`, JS object literals as defaults shared by reference. Move: Sentinel and create per-call. Note: this overlaps with the auditor's correctness check; the spotter records it as a structural smell when many defaults in the file follow the same pattern.
30. **Test smells (when test files included).** Tests that share excessive setup (Move to factory/builder), tests with multiple distinct assertions (Split test), tests that compare large JSON snapshots without explanation (Add focused assertions), tests that depend on each other (Isolate).

### Stage 3 — Rank and prune

31. Score each opportunity: `impact = severity × payoff / effort × (1 - risk)`. Numerical scoring need not be exposed; the agent uses it internally.
32. Group near-duplicate opportunities: if "long method on `processOrder`" and "duplicated logic between `processOrder` and `processRefund`" are surfaced, present them together because the same Extract Method move addresses both.
33. Apply `scope`:
    - `surgical` — keep only opportunities whose proposed move is < 30 lines of code change and touches ≤ 2 files. Drop the rest.
    - `balanced` (default) — include surgical moves and module-internal restructures up to ~150 lines, but exclude cross-module architectural moves.
    - `ambitious` — include cross-module moves, class extractions, dependency-direction changes, design-pattern introductions.
34. Cap the report at the top 10 opportunities by impact. If `ambitious` scope, allow 15.
35. Drop any opportunity whose move conflicts with stated `codebase_style`. (Example: don't propose Replace Conditional With Polymorphism in a codebase the user described as "functional, avoid inheritance" — propose discriminated unions instead.)

### Stage 4 — Compose each opportunity card

36. For every surviving opportunity, write a card:
    ```
    ### #3 Replace nested conditional with guard clauses — `src/billing/charge.py:88-152`
    **Smell:** Long method (65 lines) with 4 levels of nesting and three early-return concepts buried inside.
    **Proposed move:** Decompose Conditional + Guard Clauses. Lift the three sentinel cases (`is_test_account`, `is_already_charged`, `amount <= 0`) to the top of the function and return early. The remaining body collapses to one happy path.
    **Payoff:** High — the function becomes scannable, the test cases align with the conditions, and the bug-prone interleaving of refund and charge logic disappears.
    **Effort:** S (~30-line change, no public-surface change).
    **Risk:** S — covered by existing tests `test_charge_*`. Add one test for the new ordering of the guard clauses.
    **Sketch:**
    1. Extract the three sentinel conditions as named locals.
    2. Replace the outer `if/else` with early returns for the sentinels.
    3. Remove the now-redundant nested `else` branches.
    ```
37. The card always includes: smell, proposed move (by canonical name from the smell catalog), payoff, effort, risk, and a 3-5 step sketch. Never include the user's code pasted verbatim — paraphrase by line reference.
38. If multiple alternative moves exist, name the agent's first choice and parenthetically note the alternative. The user is busy; the agent makes a recommendation.

### Stage 5 — Compose the report

39. Open with a one-paragraph diagnosis of the file/module: dominant smells, structural temperature ("the file reads as 3 concepts braided into one"), and the top three opportunities listed by ID.
40. Then the cards in ranked order.
41. End with "Out of scope this pass": a one-line list of opportunities the agent saw but dropped — either because of `scope` setting, conflicting `codebase_style`, or low impact. This lets the user reconsider with a different scope.
42. Optionally end with a "Refactor sequence": if several opportunities cleanly compose (Move Method → Extract Class → Rename), suggest the order, so the user knows which to do first.

### Stage 6 — Self-check

43. Re-walk every card and ask: "Would this refactor make a future change easier — and which change?" If the agent can't name a concrete future change, the opportunity probably isn't worth surfacing. Drop it.
44. Avoid the "rewrite the file" anti-pattern. If the report's recommended changes touch >60% of a file, the agent should propose a phased path rather than a single big move.
45. Never propose a rename whose new name is materially worse than the old one. Bad rename suggestions undermine trust.
46. If the input is a diff (not whole files), bias toward smaller moves; lack of full-file context makes large moves risky.
47. If the input language is unfamiliar (rare languages, DSLs), keep moves to universal categories (long method, duplicated code, dead code) and skip idiom-specific ones.

### Stage 7 — Language-specific moves

The smell catalog is universal. Each language has idiomatic targets the agent prefers when proposing the move.

48. **Python.** Convert classes whose only state is data into `@dataclass(frozen=True)` (or `pydantic.BaseModel` when validation is wanted). Replace getter/setter pairs with attributes plus `@property` where computation is needed. Convert tuple-of-values returns into `NamedTuple` or dataclass. Replace `if/elif` chains on a `kind` string with `match` statements (3.10+) keyed on a `Literal` union. Replace nested loops accumulating into a list with comprehensions when the result is small; with generators when the result is large.
49. **TypeScript.** Replace shape-based unions (`{kind: string, ...}`) with discriminated unions and exhaustive `switch` checked by a `never` default. Replace `any` introduced for convenience with `unknown` plus type guards. Promote magic strings to string-literal unions (`'pending' | 'paid'`). Move data-only classes to interfaces or `type` aliases. Replace `Promise.then` chains with `async/await` where readability improves.
50. **JavaScript.** Replace `var` with `const`/`let`. Replace IIFE-based modules with ES modules. Replace `arguments` with rest parameters. Replace deep callback chains with `async/await`. Replace `Object.keys(o).forEach` with `for...of Object.entries(o)`.
51. **Go.** Replace switch-on-type with interface methods when several call sites switch on the same type. Replace `if err != nil { return err }` boilerplate (when it appears in many copies) with a helper only if the helper meaningfully clarifies — Go culture prefers explicit error handling, so don't over-extract. Introduce a struct for grouped parameters when call sites repeat the same 4+ arguments.
52. **Java / Kotlin.** Replace JavaBean getters/setters used only as data carriers with `record` (Java 16+) or `data class` (Kotlin). Replace deep inheritance hierarchies with sealed classes and pattern matching. Replace `Optional<T>` returned and immediately `.orElseThrow` with `T` and an explicit throw.
53. **Ruby.** Replace `case` on type with polymorphism. Extract long methods into private methods named after their concept. Replace `attr_accessor :foo` mutable everywhere with `attr_reader` plus explicit setter when invariants are involved.
54. **Rust.** Replace `Option<T>` chains with `?` operator and helper combinators (`map`, `and_then`). Replace deep `match` on `Result` with `?`. Replace large `Box<dyn Trait>` with an enum when the variant set is closed. Extract repeated `unwrap_or_else` patterns into a helper trait.
55. **C# / .NET.** Replace property-bag classes with `record` types. Replace nested `if`/`return` ladders with pattern-matching `switch` expressions. Replace `IEnumerable` reified with `.ToList()` mid-pipeline with a single terminal materialization.

### Stage 8 — Idiom and architecture suggestions (ambitious scope only)

When `scope=ambitious`, the agent may surface higher-level moves. These are gated by visible evidence in the code, not speculative.

56. **Hexagonal / ports-and-adapters.** If the file under review mixes HTTP/SQL/business logic in a single class, propose extracting a pure-domain core and pushing IO to adapters at the edges. Only suggest if at least three IO concerns are entangled with business rules in the same file.
57. **Repository pattern.** If queries are duplicated across multiple service files, propose a repository per aggregate. Justify with the duplication count.
58. **Strategy.** If a configuration boolean drives different runtime behavior in ≥3 branches, propose strategy classes / function tables.
59. **Builder.** If construction requires more than ~6 parameters and several have defaults, propose a builder (Java/C#) or named-arg factory (Python/Kotlin/Rust/Swift).
60. **State machine.** If a field with 4+ enum values is referenced in multiple `switch` statements and transitions are checked ad-hoc, propose an explicit state-machine type with allowed transitions.
61. **Dependency injection.** If a class instantiates its collaborators internally and is awkward to test, propose constructor injection — but only if the team's idiomatic style already uses DI.
62. **Module boundaries.** If divergent change is severe (a file changes for 5+ unrelated reasons), propose splitting into modules with names that match the reasons.

### Stage 9 — Anti-patterns to avoid suggesting

63. Do not propose abstractions to satisfy "rule of three" when only two duplicates exist — premature DRY creates worse coupling than mild duplication.
64. Do not propose design patterns by name unless the code visibly wants them. "Apply the Visitor Pattern" without a concrete case-by-case need is a smell in itself.
65. Do not propose moving every method into its own file. File proliferation has its own readability cost.
66. Do not propose renames into "enterprise-style" names (`AbstractFactoryStrategyManager`) — match the project's existing naming temperature.
67. Do not propose extracting a "utils" class. Utils classes become magnets for unrelated functions. Suggest specific named modules instead.
68. Do not propose introducing a new dependency to enable a refactor unless the dependency is already used in the project and the saving is large.
69. Do not propose rewriting tests to a different framework unless the user explicitly asked.
70. Do not propose changing public API contracts as part of an internal refactor — separate that into a Stage 10 follow-up item with a migration note.

### Stage 10 — Producing the refactor sequence

When multiple opportunities compose, the agent emits a recommended ordering.

71. Renames first. They are cheap, low-risk, and make subsequent moves easier to discuss.
72. Local extractions next (Extract Method, Extract Variable, Replace Magic Number).
73. Module-internal restructuring next (Extract Class, Move Method within a file).
74. Cross-module moves last (Move Class, Module Split). These are the highest-risk and benefit from the earlier cleanup as scaffolding.
75. Before each step, recommend ensuring tests pass. Refactor in green; if tests are missing, add characterization tests first and call this out as Step 0.
76. Avoid sequences longer than 6 steps. Beyond 6 the developer should stop and re-plan rather than execute a long script blindly.

### Stage 11 — When the input is a diff rather than full files

77. Diffs lose the surrounding context that drives most refactor moves. The agent narrows to: dead-on-arrival code added in the diff; new duplications that already shipped to the diff itself; new magic numbers; new long methods born in this PR; new boolean parameters.
78. Avoid proposing Extract Class or Module Split on diff-only input — there's not enough context to recommend a destination.
79. Always note in the report that the input was diff-only and that broader refactor opportunities likely exist that the agent could not see.

### Stage 12 — Calibration to team velocity

80. If `codebase_style` describes a fast-moving startup, lean toward small surgical moves with high payoff; large refactors are unlikely to be sequenced in.
81. If `codebase_style` describes a mature codebase with stability requirements, lean toward documentation, characterization tests, and renames; structural moves should come with explicit safety steps.
82. If neither is specified, default to `balanced` and surface at most 8 opportunities so the report stays actionable.

### Stage 13 — Triage decision table

Use the table to decide whether an opportunity makes the cut. Pick the row by payoff and the column by effort; opportunities in the shaded zone make it; others get dropped or held for `ambitious` scope.

```
              effort=S    effort=M    effort=L
payoff=High   include     include     include (ambitious only)
payoff=Med    include     consider    drop
payoff=Low    consider    drop        drop
```

"Consider" means include only if the opportunity composes with another that's already included.

### Stage 14 — Special cases by file role

84. **Test files.** Refactor moves apply but the priorities shift: extract shared setup into builders/factories; replace large snapshots with focused assertions; remove tests that duplicate coverage of other tests; rename tests to describe behavior in the name.
85. **Configuration files.** Apply Magic Number renames cautiously — config keys are sometimes contractual. Recommend renames only when a comment in the diff or a recent commit hints the name is internal.
86. **Migrations.** Generally not a target for refactor. Recommend code-style improvements only if the migration is in a project that runs migrations as Python/Ruby code with logic, and the logic is hard to read.
87. **Generated code.** Skip entirely. Note that the file is generated and continue.
88. **Vendored code.** Skip; recommend the team upgrade the upstream version if the vendored copy is significantly behind.

### Stage 15 — Risk-aware sketches

Every refactor card has a `risk` field. The agent estimates risk using these signals:

89. **Public-surface risk.** If the refactor changes signatures or names used outside the file, risk is at least M.
90. **Test-coverage risk.** If the area has no tests visible in the input, risk is at least M; if it's a hot path of the business, risk is L (use characterization tests before).
91. **Concurrency risk.** If the code involves threads, async, locks, or shared state, risk is at least M.
92. **Persistence risk.** If the refactor touches code that writes to storage, risk is at least M; recommend a feature-flag rollout for large versions.
93. **Behavior-preservation risk.** If the move requires non-trivial reasoning to confirm equivalence (e.g., Replace Conditional With Polymorphism on a 100-line `switch`), risk is at least M; recommend an intermediate refactor (Extract Method on each case first) to make the equivalence visible.

### Stage 16 — Communicating refactor opportunities to the author

94. Open the report with the file's dominant problem in one sentence. ("`orders.py` reads as three classes braided together — order intake, pricing, and shipping.")
95. Tie each opportunity to a future change the team will want to make. ("Extract Class on the pricing methods makes the upcoming volume-discount feature 1-class to implement instead of 4-file.")
96. Estimate effort in t-shirt sizes (S/M/L), not hours — hours imply a precision the agent doesn't have.
97. Estimate risk on the same S/M/L scale.
98. Never use the word "should" without alternatives — refactors are taste-dependent. Use "consider" for medium-confidence and reserve "would help" or "would unlock" for high-confidence moves with concrete justification.
99. End the report with one observation about what's already well-structured. Code reviewers who acknowledge strengths get traction on weaknesses.

### Stage 17 — When to recommend "do nothing"

The most honest output is sometimes an empty report. The agent should produce zero opportunities when:

100. The input is short (<100 LOC) and exhibits no smells.
101. The input is already idiomatic for the stated `codebase_style`.
102. The opportunities the agent sees all carry payoff:effort ratios below the threshold.
103. The input is so unfamiliar (rare language, heavy DSL, internal framework) that the agent cannot confidently recommend moves.

In each case the agent says so explicitly with one sentence of reasoning. Silent empty reports look like failures; reasoned empty reports are valuable.

## Outputs

- `refactor_report` (markdown) — diagnosis + ranked opportunity cards + out-of-scope list + optional refactor sequence.
- `opportunities_json` (JSON array) — each entry: `id`, `file`, `line_start`, `line_end`, `smell`, `refactor_move`, `payoff`, `effort`, `risk`, `sketch` (string).

## Examples

**Input (placeholder):**

A 420-line Python file `orders.py` containing one `OrderService` class with 11 public methods, two private helpers, a 90-line `process_order` method, and a `status` field that's a string with 6 documented values.

**Agent reasoning (abbreviated):**

- Long method on `process_order` — High severity, Extract Method on the validation block and the discount block.
- Long class — 11 public methods, but a clean cluster around "discount" math (3 methods) and a cluster around "shipping" math (3 methods). Extract Class candidate.
- Primitive obsession on `status` — string with 6 values, switched on in 4 places. Introduce Enum.
- Duplicated calculation inside `process_order` and `quote_order`: tax math appears twice with small variation. Extract Method (`compute_tax`).
- Magic numbers: `0.07`, `0.085` appear in tax math. Rename as `STANDARD_TAX_RATE`, `LUXURY_TAX_RATE`.
- Boolean parameter: `process_order(..., dry_run=False)` threaded through 3 helpers. Recommend Split Phase: a planning function returning a plan, an executor function that runs the plan.

Output ranks Extract Class > Extract Method on `process_order` > Introduce Enum > Split Phase > magic-number renames > duplicated tax math.

### Stage 18 — Composability of moves

Some refactor moves enable others. The agent looks for these compositions and prefers the move that unlocks the most subsequent value.

A. **Extract Method enables Move Method.** Once a concept is extracted with a clean signature, moving it to where its data lives becomes possible.
B. **Introduce Parameter Object enables Extract Class.** Once the always-together parameters become a type, the methods that operate on the type become candidates for a new class.
C. **Replace Magic Number With Constant enables Introduce Enum.** Once each magic literal has a name, related constants cluster naturally into an enum.
D. **Replace Type Code With Polymorphism enables Inline Class.** Once dispatch happens through polymorphism, the type-code field can be removed entirely.
E. **Decompose Conditional enables Replace Conditional With Polymorphism.** Naming each branch is the gateway to noticing the polymorphic structure.

When the agent surfaces a single opportunity, it also notes any composable follow-up as a "next move" hint — without recommending the follow-up be done in the same change.

### Stage 19 — Reading the room

The agent tunes recommendations to the project's apparent maturity.

F. **Greenfield project (few files, no tests).** Recommend characterization tests first, even before any refactor; surface only the most blatant smells.
G. **Pre-1.0 project (active design churn).** Lean toward small surgical moves; large refactors will be invalidated by the next feature.
H. **Mature, stable project.** Lean toward documentation, naming, and dead-code removal; structural moves should justify the risk.
I. **Library projects.** Be conservative about public-API renames — any rename is a breaking change for consumers; surface as ambitious-only with an explicit migration note.
J. **Legacy codebase being modernized.** Prefer the Strangler pattern: small surface area at a time. Surface opportunities that fit that pattern (small extractions adjacent to new code) over big-bang rewrites.

## Worked example two — small clean module

**Input:** a 110-line Python module with three small functions and one dataclass. Tests exist alongside it. `scope=balanced`.

**Agent reasoning:**

- Files: 1 module, 110 LOC. None of the size thresholds are crossed.
- Smell sweep: no long methods (longest is 22 lines); no long parameter lists (longest is 3); no primitive obsession (the dataclass is well-formed); no duplicated logic across the three functions; one magic number (`60` representing seconds in a minute — but the variable it multiplies is named `minutes` and the multiplication is local; the value is self-evident).
- Dead code check: all functions are imported and used.
- The module is healthy; refactor would be net-negative.

**Output (abbreviated):**

```
**Diagnosis:** The module is small, focused, and idiomatic for the
stated codebase style. No refactor opportunities make the cut at
balanced scope.

**Out of scope this pass:** Naming the literal `60` as `SECONDS_PER_MINUTE`
is a nit; if you keep a constants file for similar literals it might be
worth adding there. Skipped because the single-use context makes the
literal self-explanatory.

If you want a broader scan, run again with `scope=ambitious`.
```

## Limitations

- The skill makes structural recommendations from code shape and naming alone; it cannot know commit history, ticket context, or team velocity.
- It cannot verify that a refactor preserves behavior — it always recommends running the existing test suite (and adding tests if coverage is thin) before the change.
- It will not redesign domain models from scratch; it operates on what's there.
- It is biased toward established refactoring moves; novel patterns or domain-specific architectures may be under-served.
- Performance refactors (e.g., replacing a data structure for asymptotic gains) are out of scope unless they are also clarity wins.
- For very small inputs (<100 lines), the report will often be short or empty — small code rarely needs structural change.

## Sources reviewed

- https://github.com/Luzkan/smells (MIT)
- https://github.com/eslint/eslint (MIT)
- https://github.com/analysis-tools-dev/static-analysis (MIT)
- https://github.com/reviewdog/reviewdog (MIT)
- https://github.com/codedog-ai/codedog (MIT)
- https://github.com/Nayjest/Gito (MIT)
- https://github.com/anc95/ChatGPT-CodeReview (ISC)
- https://github.com/Nikita-Filonov/ai-review (Apache-2.0)
