---
id: skillsgit-curated/salesforce-flow-vs-apex-decider
version: 1.0.0
name: Salesforce Flow vs Apex Decider
description: Decide whether a Salesforce automation belongs in Flow, Apex, or both, and flag misuses of Flow that should migrate to Apex.
authors:
  - name: Wave-3 Synthesis Agent
    handle: synth-wave3
    role: author
category: enterprise-software
tags:
  - niche:salesforce-development
  - flow
  - apex
  - automation
  - architecture
  - declarative
  - migration
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - claude-haiku-4-5
    - gpt-4o
  min_context_tokens: 16000
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - flow vs apex
  - declarative vs code
  - should this be a flow
  - migrate flow to apex
  - flow in loop
  - record-triggered flow
  - flow callout
  - flow performance
  - flow error handling
  - automation strategy
example_invocations:
  - Should this rollup live in Flow or Apex?
  - My record-triggered flow is timing out — should I move it to Apex?
  - Is it OK to call an external service from Flow?
  - We have three flows and an Apex trigger on Opportunity — what is the right model?
inputs:
  - name: use_case
    type: text
    required: true
    description: Plain-language description of the automation requirement.
  - name: existing_automations
    type: text
    required: false
    description: List of existing flows, triggers, and processes on the affected objects.
  - name: org_constraints
    type: text
    required: false
    description: Constraints (admin-only team, ISV org, large data volume, strict security review, etc.).
outputs:
  - name: decision
    type: markdown
    description: Recommendation with rationale, including a fit table per criterion.
  - name: migration_plan
    type: markdown
    description: If the input is an existing flow being migrated, a step-by-step plan to refactor to Apex (or vice versa).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Salesforce Flow vs Apex Decider

## When to use

Use this skill whenever someone is deciding **how** to implement a Salesforce
automation requirement and is choosing between:

- Record-triggered Flow / Screen Flow / Autolaunched Flow / Scheduled Flow
- Apex Trigger + handler class
- Apex Batch / Queueable / Scheduled / Invocable
- A combination (Flow that invokes an Apex action; Apex that calls a subflow)

Or when an existing Flow is misbehaving (timing out, hitting limits, error-prone,
hard to test) and the question is whether to refactor inside Flow or migrate to
Apex.

Do **not** use this skill for:

- "Which is more performant?" benchmark requests — the answer is "it depends on
  data volume and operation mix" and a synthetic benchmark will mislead. This
  skill gives a rule-based decision, not a microbenchmark.
- LWC vs Aura, Visualforce vs LWC, or any UI-layer decision.

## How to apply

### Step 1 — Extract the requirement

Restate the use case in one sentence with the following structure:

> When `<trigger>` happens on `<object>` (volume: `<single | bulk | mass>`),
> perform `<actions>` so that `<business outcome>`, subject to `<constraints>`.

If the requester does not supply enough information to fill this template, ask
one clarifying question before proceeding. Common gaps: trigger context
(before vs after, insert vs update), bulk expectation, whether errors should
block the user transaction, and whether the logic touches external systems.

### Step 2 — Score against the decision matrix

For each criterion below, score the use case as **F** (Flow strongly preferred),
**A** (Apex strongly preferred), or **?** (either works). The dominant letter
across the rows wins; ties break in favour of Flow on simple admin-friendly
work and Apex on anything touching the criteria flagged "A-only".

| #  | Criterion                                                       | F if...                                                    | A if...                                                            |
|----|-----------------------------------------------------------------|------------------------------------------------------------|--------------------------------------------------------------------|
| 1  | Trigger context                                                  | Single record, screen interaction, scheduled batch         | Trigger context with bulk DML (200+ records expected)              |
| 2  | DML count                                                        | Updates 1–3 related records                                 | Updates 5+ related sObject types or chains DML through 3+ levels   |
| 3  | Loop body complexity                                             | Filter & map, simple field assignment                       | Conditional branching > 3 deep, math on lists, sort/aggregate      |
| 4  | External callouts                                                | None, or via a packaged invocable Apex action               | HTTP callouts, named credentials, multi-step API orchestration     |
| 5  | Error handling needs                                             | Fault path → email admin, retry, log; user can see error    | Compensating transactions, partial rollback, custom exception types|
| 6  | Test coverage requirements                                       | Acceptable to test manually; production-flow tests are weak | Unit tests required; want CI gate on logic correctness             |
| 7  | Versioning / packaging                                           | One org, admin maintains                                    | ISV managed package, multiple-org rollout, source-controlled       |
| 8  | Authoring team                                                   | Admin / consultant fluent in Flow Builder                   | Developer team comfortable with Apex                               |
| 9  | Data volume                                                      | < 100 records per transaction                               | 200+ records per transaction; batch jobs over millions             |
| 10 | Performance sensitivity                                          | Background, async, no user blocking                         | Sub-second user-facing transaction, CPU-tight                      |
| 11 | Recursion / re-entrancy                                          | Stateless single pass                                       | Risk of recursion; need recursion guard                            |
| 12 | Cross-object aggregation                                         | Single parent rollup with declarative summary               | Multi-object joins / non-trivial summary that rollup-summary can't |
| 13 | Custom metadata / settings-driven branching                      | Decision element on metadata record                         | Strategy pattern, polymorphic dispatch                             |
| 14 | Sharing & security model                                         | Runs in user mode automatically; admin doesn't override     | Need `without sharing` elevation for system-of-record operations   |

**A-only rows that override everything else (auto-Apex):** 4 (callouts in a
trigger-time context — Flow's HTTP callout action is restricted and has caused
governor-limit incidents), 5 (custom exception types), 7 (managed-package ISV
work — Flow versioning across packages is harder to govern), 14 (need explicit
sharing override).

### Step 3 — Apply the anti-patterns checklist

Flag and reject any of these in Flow regardless of the matrix score:

1. **DML inside a Flow loop without bulkification.** A `Get → Loop → Update`
   that issues `Update Records` per iteration will burn DML limits. The correct
   Flow shape is `Get → Loop → Assignment (into collection) → Update Records
   (after loop)`. If the requester cannot express it that way, recommend Apex.
2. **Synchronous external callouts from record-triggered Flow.** Officially
   supported but operationally fragile; one slow endpoint can blow the CPU
   budget for every user that triggers the flow. Move callouts to a Queueable
   invoked by an after-save flow at minimum.
3. **Flow recursion.** Flow does not have first-class recursion guards. If the
   automation modifies a record that re-triggers itself, build it in Apex with
   an in-transaction `Set<Id>` guard.
4. **Mass-data automation in Flow.** Scheduled flows that touch 10k+ records
   should be Apex Batch with a `Database.QueryLocator`. Scheduled flows are
   subject to per-batch limits and their failures are harder to recover.
5. **Sensitive logic shipped to admins to edit.** If a regulator or auditor
   cares about correctness, the logic belongs in Apex with tests and code review.
6. **Flow + multiple Apex triggers on the same object** without a documented
   execution-order contract. Salesforce's order is: validation rules → before
   triggers → before flows → DML → after triggers → assignment rules → after
   flows → workflow rules. If two automations both modify the same field, you
   will see ping-pong updates. Recommend consolidating: one trigger + one
   record-triggered flow per object, with the flow handling "low-risk
   declarative" and Apex handling "complex, transactional, tested".
7. **"It works in scratch org but fails in prod" pattern.** Almost always a
   data-volume or sharing-rules issue invisible in scratch orgs. Apex is easier
   to instrument and assert on; recommend Apex if observability matters.

### Step 4 — Produce the decision

Write a short verdict (one of: **FLOW**, **APEX**, **HYBRID — Flow invokes
Apex action**, **HYBRID — Apex with subflow for admin override**). Justify in
3–6 sentences referencing specific rows from the matrix and any anti-patterns
that fired.

If the verdict is HYBRID, draw a tiny ASCII flow:

```
[Record event] → [Record-triggered Flow]
                    │
                    └─→ [Invocable Apex] (the heavy lifting)
                    └─→ [Email Alert]    (the admin-friendly bit)
```

### Step 5 — Migration plan (if applicable)

When the input is an existing Flow being migrated to Apex:

1. Map every Flow element to its Apex equivalent.
   - `Get Records` → SOQL with `WHERE` and `WITH USER_MODE`.
   - `Loop` → Apex `for` over the result collection.
   - `Assignment` → field assignment on a working record.
   - `Decision` → `if/else` or `switch`.
   - `Update Records` → `Database.update(records, AccessLevel.USER_MODE)`.
   - `Subflow` → invoked Apex method or another handler class.
   - `Fault path` → `try/catch` with `Logger.error(...)` (Nebula Logger is the
     reference observability framework for this; MIT-licensed).
2. Identify what was implicit in Flow that must be made explicit in Apex:
   sharing keyword, recursion guard, bulkification, test class.
3. Replace the Flow with a thin wrapper that only fires when a fallback is
   needed — or remove it entirely. Do not leave both running on the same event
   "for safety"; that is the most common cause of Salesforce automation
   incidents.
4. Add tests: at least one bulk path (200 records) and one happy-path
   single-record test. Use `Test.startTest()` / `Test.stopTest()` to flush
   async work.
5. Deploy behind a feature flag (custom metadata) so the Flow can be reactivated
   instantly if Apex misbehaves.

### Step 6 — Reverse migration (Apex → Flow)

Occasionally an over-engineered Apex trigger should become a Flow. This is rare
but legitimate when:

- The logic is fully declarative (field copies, status transitions).
- The maintaining team is admins, not developers.
- No callouts, no complex error handling, no recursion risk.
- The org is moving toward "admin-owns-automation" governance.

Migration plan:

1. Reproduce the trigger's logic in a record-triggered flow on the same object.
2. Run them in parallel with the Apex trigger silenced via a custom-metadata
   bypass, against a UAT data set, and diff the resulting record state.
3. Retire the Apex trigger with a removal PR. Keep the test class as a
   regression suite — invoke the flow from `Test.invokeFlow(...)` or by DML.

## Inputs

- `use_case` (required) — plain-language description as described in Step 1.
- `existing_automations` (optional) — what already runs on the affected objects.
  Crucial for the consolidation question; absent this, the recommendation
  assumes a greenfield object.
- `org_constraints` (optional) — packaging, team skills, data volume, security
  posture. Drives the A-only rules and the security-review row of the matrix.

## Outputs

- `decision` (markdown) — verdict, matrix-row scoring, anti-pattern flags,
  short rationale.
- `migration_plan` (markdown, optional) — present only when the input is an
  existing automation being moved.

## Examples

### Example 1 — Opportunity stage rollup

Use case: when `Opportunity.StageName` changes, recompute a parent
`Account.Hottest_Opportunity_Score__c` based on a weighted average of all open
opportunities.

Scoring: row 2 (multi-DML, A), row 3 (math over a list, A), row 9 (a top account
can have 100+ opps, A), row 6 (need unit tests because Sales Ops depends on
this number, A). Verdict: **APEX**. Recommend a trigger handler + service class,
unit-tested at the 200-record boundary.

### Example 2 — Auto-assign Lead Owner

Use case: when a new Lead is created with `Country__c = 'France'`, set
`OwnerId` to the FR queue.

Scoring: row 1 (single-record bias, F), row 2 (one field update, F), row 3
(trivial branching, F), row 8 (admin-maintained, F). No anti-patterns fire.
Verdict: **FLOW**. Record-triggered before-save flow.

### Example 3 — Existing flow with callout timing out

Use case: a record-triggered flow updates an external ERP via HTTP callout on
every Account update.

Anti-pattern 2 fires. Verdict: **HYBRID — Flow invokes Apex action**. Move the
callout to a Queueable Apex class; have the flow enqueue it after save. The
declarative routing logic can stay in Flow.

## Limitations

- This skill encodes a 2025-era model where **before-save record-triggered
  flows are recommended over Process Builder and over Workflow Rules**.
  Process Builder is retired; Workflow Rules are deprecated. If you are
  maintaining a legacy org with those tools, treat them as in-flight migration
  targets, not authoring options.
- **Source-thinness disclosure.** Authoritative Flow architecture guidance is
  largely published by Salesforce itself under non-permissive terms (Trailhead
  modules, Architect Decision Guides). This skill restates the principles in
  the synthesist's own words and references only permissively-licensed code
  patterns (Nebula Logger MIT, fflib BSD-3, code-analyzer BSD-3, trigger
  frameworks MIT/Apache) as worked examples. Treat the matrix as a working
  heuristic, not as Salesforce-endorsed doctrine.
- **No live org introspection.** The skill cannot enumerate your existing
  automations. The `existing_automations` field is the user's responsibility
  to fill; an inaccurate list will yield an inaccurate consolidation
  recommendation.

## Appendix — Mapping Flow elements to Apex idioms

When emitting a migration plan, use this lookup so the developer ends up with
idiomatic Apex rather than a literal transliteration of the canvas:

| Flow element                  | Apex equivalent                                                          |
|-------------------------------|--------------------------------------------------------------------------|
| Get Records                   | SOQL with `WHERE`, `LIMIT`, `WITH USER_MODE`                              |
| Loop                          | `for (SObject rec : records)`                                             |
| Decision                      | `if/else` or `switch on`                                                  |
| Assignment (single record)    | field assignment on a working record                                      |
| Assignment (collection add)   | `accumulator.add(rec);` outside any DML                                   |
| Create / Update / Delete      | `Database.insert/update/delete(records, AccessLevel.USER_MODE)`           |
| Roll Back Records             | `Database.SavePoint` + `Database.rollback(sp)`                            |
| Action — Email Alert          | `Messaging.SingleEmailMessage` + `Messaging.sendEmail`                    |
| Action — Submit for Approval  | `Approval.ProcessSubmitRequest`                                           |
| Action — Apex                 | direct method call                                                        |
| Action — Subflow              | call into the migrated handler class                                      |
| Wait — Pause                  | Queueable with `System.scheduleBatch` for delay                           |
| Fault path                    | `try/catch` + Nebula Logger `Logger.error(...)`                           |

## Appendix — Common requester misconceptions

When advising, expect to correct these:

1. "Flow is always slower." Not true — before-save record-triggered flows skip
   a save cycle and are often faster than the equivalent before-update Apex
   trigger for simple field assignment.
2. "Apex has no governor limits in batch." Not true — the limits are higher
   but real (200 SOQL queries, 12 MB heap, 60 s CPU per chunk).
3. "We should put everything in Flow because admins can maintain it." Only
   true if the admins are trained on the anti-patterns above. Otherwise the
   maintenance cost shows up as production incidents, not as cleanly-handed-
   over code.
4. "Apex is more secure." Not inherently — both run as the invoking user
   unless explicitly elevated. Security comes from declared sharing keywords,
   USER_MODE operations, and review, not from the choice of authoring tool.
