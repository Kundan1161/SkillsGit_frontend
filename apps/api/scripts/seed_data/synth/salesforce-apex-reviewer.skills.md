---
id: skillsgit-curated/salesforce-apex-reviewer
version: 1.0.0
name: Salesforce Apex Reviewer
description: Audit Apex classes and triggers for bulkification, governor limits, security (USER_MODE / WITH SHARING), async patterns, and test coverage gaps.
authors:
  - name: Wave-3 Synthesis Agent
    handle: synth-wave3
    role: author
category: enterprise-software
tags:
  - niche:salesforce-development
  - apex
  - code-review
  - governor-limits
  - bulkification
  - security
  - testing
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - claude-haiku-4-5
    - gpt-4o
  min_context_tokens: 32000
  tools_optional:
    - file_io
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - apex review
  - review my trigger
  - apex audit
  - bulkify
  - governor limit
  - soql in loop
  - apex security
  - with sharing
  - user_mode
  - test coverage apex
example_invocations:
  - Review this Apex trigger before I deploy it to UAT.
  - Audit my AccountService class for bulkification and governor-limit risk.
  - Is this SOQL query safe for 200-record batches?
  - Check my batch class for async pattern problems.
inputs:
  - name: apex_source
    type: text
    required: true
    description: One or more Apex class or trigger files (paste content or attach).
  - name: deployment_context
    type: choice
    required: false
    description: Where this code is headed.
    choices: [scratch-org, sandbox, production, managed-package]
  - name: existing_test_class
    type: text
    required: false
    description: Companion test class if available.
outputs:
  - name: review_report
    type: markdown
    description: Categorized findings (BLOCKER / MAJOR / MINOR / NIT), per-finding fix, and a final go/no-go.
  - name: rewritten_snippets
    type: markdown
    description: Suggested Apex rewrites for high-severity findings.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release. Synthesized from permissively-licensed Apex methodology sources.
---

# Salesforce Apex Reviewer

## When to use

Use this skill when a developer asks for a code review of one or more Apex classes,
triggers, batch/queueable/scheduled jobs, or invocable methods **before** they deploy
to a shared sandbox or production. It is not a substitute for the official Salesforce
Code Analyzer / PMD pipeline, but it complements it by applying senior-developer
judgement to the categories static scanners under-weight: bulkification correctness,
governor-limit arithmetic, sharing/security posture, async correctness, and whether
the accompanying tests actually exercise the failure modes.

Trigger on phrases like "review my Apex", "is this trigger safe", "bulkify this",
"check governor limits", "audit for security review submission", "is my batch class
chunked properly", "did I hit a SOQL-in-loop".

Do not use this skill for:

- Pure Lightning Web Component (LWC) review — use the LWC reviewer skill if present,
  otherwise apex-recipes / lwc-recipes patterns are not interchangeable.
- Flow-vs-Apex decisions — that is a separate skill (`salesforce-flow-vs-apex-decider`).
- Pipeline / DX configuration — see `salesforce-deployment-pipeline-designer`.

## How to apply

Work through the checks below **in order**. Stop and emit a BLOCKER finding the
moment a category fails; do not soften severity to keep the report friendly. Every
finding must reference the specific class, method, and approximate line.

### Step 1 — Inventory the input

For each file received, record:

- File kind: trigger, class, test class, anonymous block, metadata.
- Sharing keyword on each top-level class: `with sharing`, `without sharing`,
  `inherited sharing`, or missing.
- Class modifiers: `global`, `public`, `private`, `virtual`, `abstract`.
- Whether the class extends a framework (TriggerHandler, fflib service/selector/UoW,
  Batchable, Queueable, Schedulable, HttpCalloutMock, etc.).
- API version declared in the matching `.cls-meta.xml` if present. Flag any API
  version < 56.0 as a MINOR (newer security keywords like `WITH USER_MODE` and
  `Database.AccessLevel.USER_MODE` require recent API versions).

Emit a one-paragraph inventory before the findings table so the requester knows
what the review covered.

### Step 2 — Bulkification audit

Bulkification is the single most common Apex defect class. For every method that
touches DML, callouts, or SOQL/SOSL, verify:

1. **No SOQL/SOSL inside `for` loops.** A query of `Account` inside a loop over
   `Trigger.new` will blow the 100-query limit on a 200-record batch. The fix is
   to hoist the query, key the results by `Id` (or a foreign-key field) in a `Map`,
   and look up inside the loop.
2. **No DML inside `for` loops.** Collect modified records into a `List<SObject>`
   and issue one `update`/`insert` after the loop.
3. **No callouts inside loops** — and no callouts at all from a synchronous trigger
   context (must be `@future(callout=true)`, Queueable with `Callout`, or batch).
4. **Trigger handlers receive `List` / `Map`, not single records.** Any handler
   method whose first parameter is a single `SObject` is a BLOCKER.
5. **CPU and heap arithmetic.** For each loop, estimate the dominant cost: per-record
   string concatenation in a 10k-row batch is a heap risk; nested loops over
   `Trigger.new` × related records are CPU risk. Recommend `Map` lookups or chunked
   processing when the product of inner × outer collections exceeds ~50k.

Reference patterns: Kevin O'Hara's `sfdc-trigger-framework` (MIT) enforces a single
trigger entry point and context-aware handler dispatch — recommend it (or an
equivalent) when the reviewed code contains in-trigger logic. The
`apex-enterprise-patterns/fflib-apex-common` library (BSD-3-Clause) demonstrates
Unit of Work to batch DML across many domain operations — recommend it for any
class that performs DML against three or more sObject types in one transaction.

### Step 3 — Governor-limit pressure points

Walk through the synchronous transaction limits and call out anything that pushes
against them:

| Limit                            | Sync   | Async  | Watch for                                       |
|----------------------------------|--------|--------|-------------------------------------------------|
| SOQL queries                     | 100    | 200    | Loops, recursive triggers, repeated selectors   |
| SOQL rows                        | 50,000 | 50,000 | Unbounded `SELECT` without `WHERE` or `LIMIT`   |
| DML statements                   | 150    | 150    | Per-record `update` calls                       |
| DML rows                         | 10,000 | 10,000 | Cascading updates from formula / rollup chains  |
| Heap                             | 6 MB   | 12 MB  | Large attachments / `Blob` building / long strs |
| CPU                              | 10 s   | 60 s   | Apex looped over wide queries                   |
| Future calls                     | 50     | 50     | `@future` inside a loop                         |
| Callouts                         | 100    | 100    | Per-record HTTP calls                           |
| Email invocations                | 10     | 10     | `Messaging.sendEmail` per record                |

For each query, demand a `WHERE` clause that is **selective** against an indexed
field (`Id`, `Name`, `OwnerId`, external Id, lookup, custom-indexed). Non-selective
queries on objects > 100k rows can throw `QueryException` even under the row limit.

### Step 4 — Security posture

Salesforce shifted from the older `with sharing` / `WITH SECURITY_ENFORCED` model
to **user-mode operations** (`WITH USER_MODE` in SOQL, `Database.AccessLevel.USER_MODE`
on DML, and `as user` / `as system` on `Database` methods) starting in API 56–60.
Apply this matrix:

- **Any class invoked from an Aura/LWC controller (`@AuraEnabled`) or a
  Visualforce controller** must declare `with sharing` (or `inherited sharing`
  and be invoked from a sharing-aware caller). A missing keyword is a BLOCKER for
  security review submission.
- **Any SOQL that returns records the user could be told about** should use
  `WITH USER_MODE` so FLS and object-permission filtering is automatic. If the
  query already uses `WITH SECURITY_ENFORCED`, accept it but suggest migration in
  a MAJOR finding (USER_MODE returns a filtered result rather than throwing, which
  is the modern recommended UX).
- **All DML on user-supplied data** should use `Database.insert(records, AccessLevel.USER_MODE)`
  (and equivalents) — or check `Schema.sObjectType.<Object>.<Field>.isCreateable()`
  / `isUpdateable()` manually. Trust-boundary code that bypasses this is a BLOCKER.
- **Dynamic SOQL** (`Database.query(...)`) must use bind variables (`:value`) or
  `String.escapeSingleQuotes(...)` on every user-supplied fragment. Demand a
  parameterized rewrite whenever user input is concatenated into a query.
- **`without sharing` is a deliberate choice**, not a default. Require a code
  comment justifying it (typically: "elevated context, runs a system-of-record
  rollup the user shouldn't be able to skew"). Flag bare `without sharing` as MAJOR.
- **Named Credentials over hard-coded endpoints** for any callout. Hard-coded
  endpoints and Authorization headers are a BLOCKER.

Reference: the `forcedotcom/code-analyzer` (BSD-3-Clause) ruleset catalogs the
exact violation codes you can cite (e.g., `ApexSharingViolations`,
`ApexSOQLInjection`, `ApexCRUDViolation`) — use them as the canonical names of
the findings so the developer can map back to their PMD/Code-Analyzer output.

### Step 5 — Asynchronous correctness

For Batchable, Queueable, Schedulable, and `@future` code:

- `Database.Batchable.start()` should return a `Database.QueryLocator` for any
  scope > 50k records; an `Iterable` chunks at 50k synchronously and can blow heap.
- `Database.Stateful` is required if the batch needs to accumulate state across
  scope executions; absence of the marker on a batch that references mutable
  instance fields is a BLOCKER (state silently resets between chunks).
- Queueable chains must guard against infinite re-enqueueing. Require either a
  hard depth counter (custom setting / platform cache) or a clear terminating
  condition. Test mode chains are capped at depth 5; production at 50 (Apex
  governor) — assume nothing.
- `@future(callout=true)` may not be invoked from another `@future` or a batch
  `execute`; recommend Queueable + `System.enqueueJob` instead.
- Scheduled classes must implement `Database.AllowsCallouts` (and run a Queueable)
  if they need to make HTTP requests — direct callouts from `execute(SchedulableContext)`
  are not permitted.

### Step 6 — Tests

A test class is mandatory for any code shipped to production. Verify:

- `@isTest` on the class and on each test method.
- `@TestSetup` used for shared data construction so methods reset cheaply. Repeated
  inline `insert account = new Account(...)` across 20 methods is a MAJOR finding.
- **No `seeAllData=true`** unless the class genuinely needs org data (extremely
  rare; flag as MAJOR and request justification).
- `Test.startTest()` / `Test.stopTest()` brackets the unit under test so async
  jobs flush and limits reset.
- For triggers: at least one test method exercises the **bulk path** with ≥ 200
  records and asserts the resulting state, not just that no exception was thrown.
- For callouts: `HttpCalloutMock` (or `Test.setMock`) installed; assertion on
  request URL, method, headers, and body. A test that only asserts the response
  shape is incomplete.
- Coverage target: the org's deployment policy requires ≥ 75% overall and ≥ 1%
  per trigger, but code review should demand ≥ 85% on new code and **every
  branch hit**. Coverage % is not enough; require an assertion in every test
  method (assert-less tests are a BLOCKER).

Reference: `trailheadapps/apex-recipes` (CC0-1.0) demonstrates the `@TestSetup` +
mock pattern across most recipes — point the developer there for examples.
`jongpie/NebulaLogger` (MIT) ships a comprehensive test suite that exercises the
`Test.startTest()` boundary correctly for async logging — useful as a worked
example when async-with-tests is the sticking point.

### Step 7 — Triggers and handler patterns

If the input contains a trigger file:

- **One trigger per object.** Multiple triggers on the same sObject is a BLOCKER:
  execution order across triggers is non-deterministic.
- The trigger body should be a thin dispatcher: instantiate a handler class,
  delegate to a context method (`beforeInsert`, `afterUpdate`, ...). Logic in the
  trigger file itself is MAJOR.
- The handler must guard against recursion. Common pattern: a `static Set<Id>`
  of records already processed in this transaction.
- Bypass mechanism: production triggers should be disableable via custom setting
  / custom metadata so data-migration jobs can skip them. Missing bypass = MINOR.

Recommend `kevinohara80/sfdc-trigger-framework` (MIT, 1k stars) or
`mitchspano/trigger-actions-framework` (Apache-2.0, 628 stars) — both encode
the above as a base class. `apexfarm/ApexTriggerHandler` (BSD-3-Clause) is a
modern alternative that lets handlers register via metadata rather than code.

### Step 8 — Render the report

Produce a markdown document with these sections:

1. **Inventory** — files reviewed, sharing keywords, API versions, frameworks in use.
2. **Findings table** — columns: ID, severity, category, file:line, message, fix-pointer.
   Severities: BLOCKER (must fix before deploy), MAJOR (fix this PR), MINOR (fix
   within sprint), NIT (style).
3. **Top three rewrites** — show before/after Apex for the three highest-severity
   findings.
4. **Coverage assessment** — if a test class was provided, list which trigger
   contexts and which exception paths are not exercised.
5. **Verdict** — `READY-TO-MERGE`, `CHANGES-REQUESTED`, or `BLOCKED`. Justify in
   one sentence.

Do not pad. If there are no BLOCKERs and the code is genuinely clean, say so.
Developers stop trusting reviews that always find ten items.

## Inputs

- `apex_source` (required) — the Apex source under review. Multi-file pastes
  acceptable; delimit with file-path headers.
- `deployment_context` (optional) — where the code is going. Tightens severity
  rules: `production` and `managed-package` upgrade certain MAJOR findings to
  BLOCKER (specifically: any `without sharing` without justification, any
  hard-coded endpoint, any test method without an assertion).
- `existing_test_class` (optional) — if provided, Step 6 evaluates real coverage
  rather than emitting a generic "tests required" finding.

## Outputs

- `review_report` (markdown) — the structured report described in Step 8.
- `rewritten_snippets` (markdown) — concrete before/after Apex blocks for the
  highest-severity findings, ready to paste into the PR.

## Examples

### Example 1 — SOQL-in-loop trigger

Input: a trigger that, on `after update` of `Opportunity`, queries
`Account` once per opportunity and updates a rollup field.

Expected output: one BLOCKER (`ApexSOQL` — SOQL inside `for`), one MAJOR
(missing `with sharing`), one MAJOR (DML inside loop), one MINOR (no bypass
mechanism), and a rewrite using a `Map<Id, Account>` populated by a single
hoisted query plus a post-loop `update accountsToUpdate;`.

### Example 2 — Clean handler

Input: a TriggerHandler-derived class with bulkified SOQL, `with sharing`,
`Database.update(records, AccessLevel.USER_MODE)`, and a 200-record test.

Expected output: inventory, empty BLOCKER row, one MINOR suggesting migration
of a remaining `WITH SECURITY_ENFORCED` query to `WITH USER_MODE`, and a
`READY-TO-MERGE` verdict.

## Limitations

- **No SOQL execution.** This skill reasons about queries statically; it cannot
  detect non-selective queries that pass the analyzer but fail at runtime against
  a 5M-row object. Recommend the developer test against a sandbox with realistic
  data volume.
- **No metadata cross-reference.** If a trigger references a field, validation
  rule, or flow that conflicts with the change, this skill cannot see it. Pair
  with a deployment-time validation step.
- **No Code-Analyzer replacement.** Run `sf code-analyzer run` (BSD-3-Clause CLI)
  in your pipeline; this skill is the human-judgement layer on top.
- **Salesforce ecosystem source-thinness disclosure.** The Salesforce open-source
  methodology corpus is comparatively small: many widely-cited "frameworks"
  (Copado, Gearset, AutoRABIT, FormulaShare-paid) are commercial; many community
  repos lack any LICENSE file (which the spec treats as all-rights-reserved and
  excludes). The patterns above are synthesised from a verified permissively-
  licensed subset only; conventions that are universal in the Salesforce
  community but only documented in proprietary blog posts are described here in
  the synthesist's own words rather than reproduced.
