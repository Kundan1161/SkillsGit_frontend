---
id: skillsgit-curated/month-end-close-conductor
version: 1.0.0
name: Month-End Close Conductor
description: Sequence the month-end accounting close from sub-ledger cutoffs through reporting — owners, dependencies, evidence, and a target days-to-close.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: finance
tags: [niche:accounting-close, month-end, close-calendar, accruals, reconciliations, controls, days-to-close, gaap]
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
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - month end close
  - close calendar
  - close checklist
  - days to close
  - close the books
  - period end
  - quarter end close
  - sub-ledger cutoff
  - close conductor
  - finance close plan
  - accounting close
  - close dependency map
example_invocations:
  - "Build a 5-business-day close calendar for our SaaS company, 80 GL accounts, two entities."
  - "Sequence our month-end close so journal entries are blocked before recs are signed off."
  - "Our close drifts to day 10 every month — design a tighter schedule and identify the bottlenecks."
inputs:
  - name: entity_profile
    type: text
    required: true
    description: Number of legal entities, industries, ERP system, headcount of the accounting team, current days-to-close baseline.
  - name: subledgers_in_scope
    type: text
    required: false
    description: AP, AR, payroll, expense management, billing, inventory, fixed assets, treasury — which sub-ledgers feed the GL and who owns each.
  - name: target_days_to_close
    type: number
    required: false
    description: Business days from period end to books-closed. Default 5 for mid-market, 3 for fast-close ambition.
  - name: known_pain_points
    type: text
    required: false
    description: Recurring blockers (late vendor invoices, slow bank feed, manual fixed-asset roll-forward, etc.).
  - name: reporting_deliverables
    type: text
    required: false
    description: Internal flash report, board package, consolidations, statutory filings, investor reporting — and their due dates.
outputs:
  - name: close_calendar
    type: markdown
    description: Day-by-day close plan with tasks, owners, dependencies, evidence required, and gating rules.
  - name: dependency_graph
    type: json
    description: Machine-readable task list with predecessors, owners, and target start/finish offsets from period end.
  - name: risk_register
    type: markdown
    description: Top close risks, the controls that should mitigate them, and the early-warning signals to monitor.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Month-End Close Conductor

## When to use

Use this skill when an accounting leader needs to design, tighten, or stress-test the monthly accounting close. The inputs are the company's shape — legal entities, sub-ledgers, ERP, headcount, current performance — and the output is a sequenced close plan with owners, dependencies, evidence requirements, and a realistic days-to-close target. The skill is appropriate for the controller who wants to compress a slipping close from day 10 to day 5, the finance leader spinning up a close calendar for a newly post-revenue startup, or the audit-prep team who needs the close to be defensible against an external auditor's walkthrough.

The skill is opinionated about sequencing. It assumes that a close fails most often not because any single task is hard, but because the wrong task runs before the right one and the team ends up reopening sub-ledgers, reposting journals, and chasing reconciliations that depended on numbers that later moved. A correctly sequenced close pushes those reopen events to near zero. The skill therefore treats sequencing as a directed acyclic graph, not as a checklist: tasks have predecessors, evidence, and gating conditions that block downstream work until upstream work is signed off.

Do not use this skill for the bookkeeping mechanics of any single journal entry (use `journal-entry-author`), for a balance-sheet account reconciliation design (use `reconciliation-builder`), or for management-reporting decisions about how to present numbers to leadership. The skill plans the assembly line; it does not build the parts.

The skill also will not advise on highly entity-specific tax provisions, consolidations involving foreign-currency translation of complex intercompany structures, or industry-specific accounting (lease accounting, oil-and-gas reserve accounting, percentage-of-completion construction) — those need a domain expert as a final reviewer. The skill produces a plan structured enough that such an expert can drop into it.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `entity_profile` | yes | Establishes scale, ERP, team size, and baseline performance to calibrate ambition. |
| `subledgers_in_scope` | no | Names the upstream feeders; missing inputs are flagged in Stage 1. |
| `target_days_to_close` | no | Sets the deadline against which sequencing is built; default 5 business days. |
| `known_pain_points` | no | Drives the risk register and where to place buffers. |
| `reporting_deliverables` | no | Pulls the close finish line forward when reporting due dates are aggressive. |

## How to apply

The conductor runs a deterministic ten-stage method. Each stage produces a fragment of the plan; the final stage assembles them and runs a sanity pass.

### Stage 1 — Profile the close

1. Read the entity profile. Identify the close type: single-entity SMB, multi-entity domestic, multi-currency multinational, consolidated group with intercompany eliminations. The close type sets the structural skeleton.
2. List the sub-ledgers that feed the GL. Default sub-ledger inventory: accounts payable, accounts receivable, billing and revenue, payroll, employee expense reimbursement, fixed assets, prepaid expenses, inventory, treasury and cash, equity and stock-based compensation, tax, intercompany. For each, note whether the company runs it: ignore "n/a" lines silently in the plan.
3. Pair each sub-ledger with an owner role. Roles, not people — "AP clerk," "revenue accountant," "FP&A analyst," "controller." If the input names individuals, retain them parenthetically, but treat roles as the unit of assignment so the plan survives turnover.
4. Establish the target days-to-close. If the user supplied a target, accept it; if not, set 5 business days for a mid-market company, 3 for an ambitious fast-close shop, 8 for a complex multi-entity multinational. Note the assumption in the output.
5. Record the explicit blockers the user named, plus the implicit ones the profile suggests. A company on a non-Tier-1 ERP with two-stage approval routing will have manual JE friction; a company with a manual fixed-asset schedule will have FA bottleneck; a company with month-end vendor invoice cutoff problems will have a high-risk AP accrual.

### Stage 2 — Set the cutoff line and freeze the inputs

6. The cutoff is the most under-respected concept in a close. The skill enforces a clear cutoff: at end of business on the last calendar day of the period (or last business day, per company convention), the sub-ledgers stop accepting new transactions dated within the period. The plan explicitly names the cutoff time and the system actions that enforce it: closing AP/AR posting periods, locking expense submissions, locking time entry, freezing inventory adjustments.
7. For each sub-ledger, decide whether late items go into accruals (the typical answer for AP) or into next period (the typical answer for credit memos, expense reports). Document the rule per sub-ledger so the team is not making it up under deadline pressure.
8. Identify any sub-ledgers that intentionally have a longer tail — for example, vendor invoices that arrive after period end for goods/services received within the period. These define the accrual workload at month-end and the size of the AP accrual estimate.
9. Establish a hard-and-fast bank cutoff: the bank statement date the close uses. If banks deliver statements late, plan the bank reconciliation accordingly — never let bank-statement availability set the entire close pace; use the bank feed and reconcile to the official statement when it arrives.
10. Document the FX rate source and snap time for any multi-currency activity. If the rate source is the period-end central bank rate, fetch it on day 0. If a monthly average rate is used, decide when the average is finalized.

### Stage 3 — Lay out the close phases

The conductor decomposes the close into five phases. Each phase has a gate: the next phase cannot start until the prior phase is signed off, with explicitly named exceptions.

11. **Phase 0 — Pre-close (days -3 to -1).** Soft activities the team does before period end to reduce day-1 load: vendor outreach to accelerate invoice receipt, expense report submission reminders, manual estimate work that does not depend on actuals (depreciation schedule confirmation, headcount-driven accrual tables), reviewing the prior month's reopen log to ensure causes were remediated.
12. **Phase 1 — Cutoff and sub-ledger close (day 1 to day 2).** Sub-ledgers reconcile to themselves, post their entries to the GL, and close their periods. Sub-ledger owners formally hand off "GL feed complete" before Phase 2 begins. AP is typically the long pole; revenue close depends on billing cutoff.
13. **Phase 2 — Accruals and adjusting entries (day 2 to day 3).** Once sub-ledgers are closed, the GL accountants book accruals and adjusting entries: AP accrual for goods received not invoiced, accrued payroll for the partial pay period, accrued bonuses and commissions, prepaid expense amortization, deferred revenue recognition adjustments, fixed asset depreciation, lease accounting entries, stock-based compensation expense.
14. **Phase 3 — Balance-sheet reconciliations and intercompany (day 3 to day 4).** Every material balance-sheet account is reconciled to a subledger or external source. Intercompany balances are matched and any imbalance is investigated and cleared. This phase is where Stage 6 of the reconciliation-builder methodology runs in parallel across accounts.
15. **Phase 4 — Review, close, and report (day 4 to day 5).** Controller review of the trial balance, fluctuation analysis against prior month and budget, sign-off, posting of any final adjustments, period lock in the ERP, and generation of the management reporting package and any consolidations.

### Stage 4 — Sequence within each phase

16. Within Phase 1, AP closes before AR for most companies because AP accrual sizing in Phase 2 depends on knowing what AP has booked. Billing closes when bills for the period are issued and the AR sub-ledger reflects them. Payroll closes when the final payroll run for the period is posted. Each sub-ledger close produces a "GL feed complete" artifact: the period-end balance per the sub-ledger.
17. Within Phase 2, sequence accruals from those that affect the largest accounts downward, so the team has time to refine the big numbers and revisit if needed. Typical order: revenue and deferred revenue, payroll and bonus, AP for goods/services received, prepaid amortization, depreciation, lease, equity. Equity-related entries (stock-based comp, equity issuance) can lag because they rarely impact the reportable trial balance materially in any single month.
18. Within Phase 3, run cash reconciliation first because it's a true-or-false check that pulls forward problems. Then AR aging and AR reserves, AP and accrued liabilities, prepaid roll-forward, fixed assets, equity, then intercompany matching across entities. Intercompany imbalances often require entry adjustments that go back through Phase 2 — design Phase 3 to detect these by day 3 morning so Phase 2 has time to re-run.
19. Within Phase 4, structure the controller review so it does not become serial bottleneck. The controller reviews each account family as it's signed off by the staff, not all at once at the end. The review backlog is the leading indicator of close slip — surface it.

### Stage 5 — Build the dependency graph

20. Every task in the plan has the following fields: id, name, phase, owner role, predecessor task ids, target start (in business days from period end), target finish, evidence required, sign-off rule.
21. Encode the gates as predecessors. "Book AP accrual" predecessor "AP sub-ledger closed." "Reconcile cash" predecessor "Bank feed available." "Post depreciation" predecessor "Fixed asset additions for the period booked."
22. Use only essential dependencies. The temptation is to over-sequence; this creates artificial bottlenecks. Two tasks that share an owner but do not share an artifact are not predecessors of each other unless the owner cannot do them concurrently. The skill explicitly notes when a dependency is "logical" versus "resource-constrained" so the user can revisit the latter by adding headcount.
23. Highlight the critical path: the longest chain through the graph. Compressing the close means compressing the critical path. If AP accrual is on the critical path and is currently a day-3 task, ask whether the AP team can move it to day-2 by working the cutoff differently.
24. Identify parallel work streams: cash reconciliation can run alongside AR reserve work; depreciation can run alongside prepaid; intercompany matching can run alongside accruals when both entities use the same close calendar.

### Stage 6 — Define evidence per task

25. Each task names the evidence its owner produces to declare the task complete. Evidence is the artifact that lands in the workpaper file: a reconciliation, a journal entry support memo, a schedule, an aging report, a system screenshot, an approval email. Evidence is what the auditor will see, what the next reviewer needs to verify, and what the team will reference next month.
26. Default evidence library:
    - Sub-ledger close: period-end balance report from the sub-ledger, reconciled to the GL.
    - Accrual entry: schedule supporting the accrual calculation, prior-month comparable, materiality note, reviewer initials.
    - Bank reconciliation: bank statement, GL cash balance, list of reconciling items with aging.
    - AR aging: aging report, allowance for doubtful accounts roll-forward, write-off approvals.
    - Fixed asset: roll-forward of additions, disposals, depreciation; capex authorization for any addition above the capitalization threshold.
    - Intercompany match: two entities' subledger balances matched, FX-adjusted, with the difference explained.
27. Evidence quality has tiers: green (clean, signed, reviewed), yellow (complete but waiting on review), red (incomplete or unsupported). The plan asks the close lead to declare every task's tier daily — the daily tier report is the close health signal.

### Stage 7 — Sign-off and review rules

28. Every journal entry above a materiality threshold requires preparer-and-reviewer sign-off — two different humans. Default materiality: 0.5% of monthly revenue or $10k, whichever is lower, for a mid-market business; adjust with the controller. Below the threshold, single sign-off is fine but the entry is still preserved with support.
29. Sub-ledger close is signed off by the sub-ledger owner. The GL close gate is signed off by the controller. The reporting package is signed off by the CFO or equivalent before external distribution.
30. The "two-eyes rule" is the load-bearing control of the close. If the same person prepares and approves, the control fails and external audit will find it. The plan structures pairs of roles so the rule is automatic, not heroic.

### Stage 8 — Buffers and contingency

31. Add a buffer to the critical path equal to roughly 10-15% of the close duration. For a 5-day close, that's a half-day buffer between Phase 4 sign-off and the reporting deliverable. The buffer is where unexpected JE corrections live; treat it as planned, not as a contingency you can erode.
32. Identify the top three risks from the known pain points and produce a contingency for each. Examples: "If bank statement is unavailable by day 2, reconcile to bank feed and accept day-3 swap"; "If AP accrual exceeds prior-month accrual by more than 30%, escalate before posting"; "If intercompany difference exceeds materiality, post to suspense and resolve in the following period with a documented plan."
33. Build a reopen rule: if a material error is found after the period is locked, the rule for when to reopen the period versus when to book the correction in the following period. Default: reopen if the error exceeds reporting-materiality and is identified before external distribution; otherwise correct prospectively and disclose in the workpaper.

### Stage 9 — Compose the artifacts

34. Produce `close_calendar` (markdown). Structure:
    - Header: company profile summary, target days-to-close, period.
    - Day-by-day table: each business day from -3 to +5, listing the tasks active that day, their owners, gates, and evidence.
    - Phase summaries: one paragraph per phase explaining the goal, the entrance gate, and the exit gate.
    - Sign-off ladder: who signs off on what, in order.
    - Reopen rule: stated once, plainly.
35. Produce `dependency_graph` (JSON). Schema: array of task objects with fields `id`, `name`, `phase`, `owner_role`, `predecessors` (list of ids), `start_day` (int), `finish_day` (int), `evidence`, `signoff_rule`, `critical_path` (bool). Downstream tools can render this as a Gantt or a DAG view.
36. Produce `risk_register` (markdown). Top 5-10 risks, each with: risk description, likelihood (low/med/high), impact (low/med/high), mitigating control already in the plan, early-warning signal to monitor in real time, owner.

### Stage 10 — Self-check

37. Walk the dependency graph from any sink task back to a source. If the longest such chain exceeds the target days-to-close, the plan is infeasible — surface this and recommend compression options: cutoff redesign, headcount add on the critical-path role, automation candidate, or relaxing the target.
38. Verify every task has an owner role and at least one piece of evidence. A task with no owner is unowned by definition; a task with no evidence is unauditable.
39. Verify that no role is overloaded in any single day. A close fails when one accountant has 14 tasks on day 2 and nothing on day 4 — surface load balancing.
40. Verify that the sign-off chain ends in a single named role: the controller for GL close, the CFO for reporting. Diffuse sign-off chains rot into ambiguity.

## Sequencing patterns the conductor uses

### Pattern A — The pull-forward cutoff

For companies whose close has slipped because vendors deliver invoices late, pull more activity into Phase 0 (days -3 to -1): freeze travel and expense submissions earlier, send vendor accelerator outreach, ask category managers for estimated invoice amounts for goods/services received but not invoiced. The result moves the AP accrual estimate from a guess on day 2 to an informed estimate by day 1.

### Pattern B — Sub-ledger truth precedes GL truth

The skill never lets the GL be the truth source for what a sub-ledger should hold. The sub-ledger reconciles to itself first, then to the GL. A common close anti-pattern is reconciling AR by trusting the AR aging report against the AR control account — if the aging is broken, you've reconciled garbage to itself. The plan requires that subledgers be internally consistent (e.g., AR sub-ledger balance equals sum of customer accounts equals sum of open invoices) before the GL handshake.

### Pattern C — Reconciliations run in waves

Group reconciliations into waves rather than running them sequentially. Wave 1: cash, AR aging, AP aging — the high-volume balance-sheet accounts that drive the trial balance. Wave 2: prepaids, accruals, fixed assets — the schedules-based accounts that depend on Phase 2 entries being final. Wave 3: equity, intercompany, suspense accounts — the audit-bait accounts where errors are rare but expensive. Each wave has a single owner who reports its wave-complete status; the controller reviews wave by wave, not item by item.

### Pattern D — The fluctuation pre-check

Before Phase 4 review, the GL accountants run a fluctuation analysis: every income-statement line, every balance-sheet account compared to prior month and to budget. Lines outside a tolerance (default ±10% and ±$25k) get a one-sentence explanation drafted by the accountant who owns the line. The controller then reviews the fluctuations, not the trial balance. This compresses Phase 4 from a marathon scrub to a targeted scan.

### Pattern E — The reopen ledger

Maintain a log of every reopen the close has experienced in the prior twelve months: account, root cause, hours lost, remediation. Begin every close cycle by reviewing the top three remediations from the log. This is how close performance compounds — without the log, the same fires recur.

### Pattern F — Daily intercompany matching

Companies with material intercompany activity (multiple legal entities trading with each other) should not wait for close to surface intercompany imbalances. The conductor recommends a daily soft-match: each entity's intercompany sub-account is exported daily, and the matching engine (or a person, for small operations) reconciles the previous day's activity. Imbalances at close are then small and resolvable; imbalances discovered for the first time at close are systemic and expensive to clear.

### Pattern G — The close health dashboard

Real-time visibility into close progress is itself a control. The plan defines a one-page dashboard the close lead reviews at least twice daily during close week: tasks complete, tasks in progress, tasks blocked, tasks late, reconciling-item count by aging bucket, journal-entry count posted vs. estimated, controller review queue depth. The dashboard pulls from the dependency-graph JSON the skill produces. Without the dashboard, close status is folklore; with it, status is fact and slippage shows up at hour granularity.

### Pattern H — Materiality calibration

The plan respects two materiality thresholds: posting materiality (the dollar amount below which an entry is single-sign-off and does not need a separate workpaper memo) and reporting materiality (the dollar amount below which a reconciling item or estimate variance does not need to be cleared before close). Posting materiality is typically tighter ($1k-$10k); reporting materiality is typically looser (1-5% of pretax income, or per the audit firm's threshold). The plan distinguishes the two so the team does not over-rotate on small items or under-rotate on large ones.

## Common close anti-patterns the conductor avoids

- **"We'll book it after close."** Material adjustments left for next period accumulate and corrupt comparability. The plan posts them in the period they belong to even if it slips the close by half a day.
- **"The controller will review everything at the end."** Concentrated review at the end creates a bottleneck and pushes errors to day 6+. The plan distributes review across Phase 3 and Phase 4.
- **"Just trust the system."** The trial balance reconciles to itself by construction; this proves nothing about whether the entries are correct. The plan never lets system reconciliation substitute for substantive reconciliation.
- **"We don't have time for fluctuation analysis."** Fluctuation analysis is the cheapest control with the highest detection power. The plan never skips it; it scales it instead.
- **"We'll fix the cutoff next month."** Cutoff drift is the single most common cause of close slippage. The plan treats cutoff failures as a Sev-1 issue, not a process improvement opportunity.
- **"That's a small variance, let's just plug it."** Plug entries are the audit-finding generators. The plan refuses plug-entry behavior at any materiality and routes unexplained variance to suspense with a clearance plan.
- **"The reviewer can sign off later."** Sign-off after the period is locked is sign-off in name only. The plan requires sign-off before lock, even if it means a half-day delay.
- **"Let's skip the fluctuation analysis this month, we're rushed."** Fluctuation analysis is cheap and catches the most embarrassing errors. The plan does not skip it; it scales it down to top accounts only if the team is genuinely capacity-bound.
- **"The auditor won't ask about that."** Designing for auditor surprises rather than for accurate books is backwards. The plan books for accuracy first; auditability follows naturally.

## Days-to-close benchmarks

The conductor calibrates the target against industry-typical baselines:

- **1-2 days:** Fast-close companies, typically large public filers with mature automation, real-time consolidation, and a heavily automated reconciliation suite. Achievable only with significant investment in ERP and process automation.
- **3-5 days:** Best-in-class mid-market — most companies the skill serves. Achievable with disciplined process and modest tooling.
- **6-10 days:** Typical mid-market starting state. The skill's compression playbook (cutoff redesign, intercompany daily matching, fluctuation pre-check, dashboard) targets this range.
- **10+ days:** Distressed close. Usually a sign of one of: chronic understaffing, an ERP transition mid-close, a major accounting policy change, or systemic data-quality problems. The plan must address the root cause; faster sequencing alone will not fix it.

The skill does not promise a target it cannot back. If the inputs suggest the target is infeasible, the plan surfaces the constraint and proposes which lever (headcount, automation, scope) would unlock the target.

## Outputs

The skill returns three artifacts:

1. `close_calendar` — the day-by-day plan with owners, gates, and evidence; intended for the close lead and the team.
2. `dependency_graph` — the JSON DAG suitable for rendering or importing into a project tracker.
3. `risk_register` — the top risks with mitigations and early-warning signals.

## Examples

**Input (placeholder):** "Mid-market SaaS company, $40M ARR, NetSuite ERP, two domestic entities, accounting team of four. Current close drifts to day 10. Pain points: vendor invoices arrive late, manual revenue recognition schedule in spreadsheets, intercompany never matches the first time. Target: 5 business days."

**Agent reasoning (abbreviated):**

- Profile: mid-market multi-entity SaaS, four-person team, NetSuite. Target 5 is ambitious but feasible; revenue rec spreadsheet is the obvious automation candidate but out of scope here.
- Cutoff: pull AP accelerator into Phase 0, lock expense submissions by day 0 close-of-business, define a clear AP cutoff plus a goods-receipt-not-invoiced accrual sized by category-manager input.
- Critical path likely: AP close (day 2) → AP accrual (day 2 late) → trial balance complete (day 3) → controller review (day 4) → CFO sign-off (day 5). Revenue rec is parallel but at risk because manual.
- Intercompany: design Phase 3 to surface mismatches by day 3 morning so Phase 2 has time to re-run if needed.
- Risk register top three: late vendor invoices (mitigate with Phase 0 accelerator), revenue rec spreadsheet errors (mitigate with two-eyes on the spreadsheet output and a fluctuation pre-check), intercompany mismatch (mitigate with a daily intercompany match starting day 1 of the new period, not waiting until close).

**Output structure (abbreviated):**

```
## Close Calendar — Period 2026-04

Target days-to-close: 5 business days.
Reporting deliverable: management package by day 6, board pack by day 8.

### Phase 0 — Pre-close (-3 to -1)
Day -3: AP accelerator emails to top 20 vendors (Owner: AP clerk; Evidence: outreach log).
Day -2: Expense submission reminder to all employees (Owner: AP clerk; Evidence: Slack send).
Day -1: Confirm depreciation schedule for the period (Owner: FA accountant; Evidence: schedule).

### Phase 1 — Cutoff and sub-ledger close (Day 1-2)
...
```

## Limitations

- The skill does not write the company's accounting policies. It assumes policies (revenue recognition method, capitalization threshold, materiality) are decided elsewhere and accepts them as inputs or applies sensible defaults clearly labeled.
- The skill assumes the team's ERP and sub-ledgers actually support a period close (period locking, role-based access, posting controls). For shops on spreadsheets or legacy systems, the plan still works but some controls are manual and slower; the skill flags that explicitly.
- The skill produces a target days-to-close but cannot guarantee it; the target depends on people executing the plan and the inputs being honest. A team in chronic understaffing cannot close in 5 days regardless of plan quality.
- The skill is opinionated about sequencing and may conflict with a team's existing ritual. The plan exposes the rationale for every dependency so the team can knowingly override; an unexplained override is the most common cause of close drift.
- Industry-specific accounting (lease accounting under ASC 842/IFRS 16, percentage-of-completion construction, oil-and-gas, insurance reserves) appears as named tasks but the skill does not produce the underlying calculation methodology.
- The risk register reflects the inputs supplied. Risks the user did not surface (fraud risk, segregation-of-duties gaps, system reliability) will be under-represented; the skill notes this in the register.
- Consolidations across multiple entities with foreign-currency translation are partially addressed: the plan sequences entity-level close before consolidation, but currency translation adjustments and equity-method investment accounting will need specialist input.
- The skill does not negotiate with the auditor about the audit timeline; that handoff lives in the `audit-pbc-fulfiller` skill.

## Sources reviewed

- https://github.com/ledger/ledger (BSD-3-Clause)
- https://github.com/ekmungai/python-accounting (MIT)
- https://github.com/imetaxas/double-entry-bookkeeping-api (MIT)
- https://github.com/apache/fineract-cn-accounting (Apache-2.0)
- https://github.com/SolidInvoice/SolidInvoice (MIT)
- https://github.com/panshak/accountill (MIT)
- https://github.com/plaintextaccounting/plaintextaccounting (community hub / docs)
- https://github.com/getprobo/awesome-compliance (CC0-1.0)
