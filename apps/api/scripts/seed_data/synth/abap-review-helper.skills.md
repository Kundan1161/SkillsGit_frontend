---
id: skillsgit-curated/abap-review-helper
version: 0.1.0
name: ABAP Review Helper
description: Review ABAP code for performance, security, and maintainability with concrete fix suggestions.
authors:
  - name: Wave-3 Synthesis Agent
    handle: wave3synth
    role: author
category: enterprise-software
tags:
  - niche:sap-integration
  - abap
  - code-review
  - s4hana
  - performance
  - security
  - clean-abap
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
    - gpt-4.1
  min_context_tokens: 40000
  tools_required: []
  tools_optional:
    - file_io
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - abap review
  - clean abap
  - abap performance
  - select in loop
  - authority-check
  - s/4hana custom code
  - atc finding
  - abap security
example_invocations:
  - "Review this ABAP report for performance and security issues."
  - "Check my custom Z-program against Clean ABAP before S/4 migration."
  - "Audit this ABAP class for SELECT-in-loop and missing authority checks."
  - "Find FOR ALL ENTRIES bugs and dynamic SQL risks in this code."
inputs:
  - name: abap_source
    type: text
    required: true
    description: ABAP source (report, class, function module, include) to review.
  - name: target_release
    type: choice
    required: false
    description: SAP release the code must run on; affects which syntax/features are allowed.
    choices:
      - ecc-6
      - s4-on-premise
      - s4-cloud
      - btp-abap
  - name: focus
    type: choice
    required: false
    description: Optional emphasis area.
    choices:
      - all
      - performance
      - security
      - maintainability
      - s4-readiness
outputs:
  - name: review_report
    type: markdown
    description: Findings grouped by severity (blocker/major/minor) with line refs and fixes.
  - name: suggested_diffs
    type: markdown
    description: Before/after snippets for the top fixes.
changelog:
  - version: 0.1.0
    date: 2026-05-14
    notes: Initial release. Synthesised from Clean ABAP, SAP styleguides, abap-cheat-sheets, and SAP custom-code migration workshops.
---

# ABAP Review Helper

## When to use

Use this skill when the user pastes ABAP source (report, class, function module, BAdI implementation, enhancement, CDS-related ABAP, or RAP behaviour pool) and asks for a review, audit, code-review feedback, or a pre-merge sanity check. It also fires for pre-conversion checks before an ECC->S/4HANA project: catching `SELECT *`, implicit client handling, table buffering misuse, missing authority checks, and obsolete statements that the ATC will flag later.

Do **not** use it for:

- Functional logic correctness (the skill cannot run the code; it inspects patterns).
- JavaScript/Java backends on BTP (use the SAP integration-pattern skill).
- Reviewing UI5/Fiori front-end code.

## How to apply

Run the review in four passes. Always produce findings in this order so the consumer can fix high-severity items first.

### Pass 1 - Structural intake

1. Identify the artefact type: report, class, function module, include, RAP behaviour pool, AMDP, CDS view-related ABAP. Note ABAP variant (classic vs ABAP for Cloud Development / RAP).
2. Extract symbol table: declared tables, internal tables, classes/interfaces used, authority objects referenced, dynamic SQL fragments.
3. Note the target release from input. If `s4-cloud` or `btp-abap`, mark any released-API-only violations as blockers automatically (e.g. direct `SELECT` from `BSEG`, native SQL).

### Pass 2 - Performance checks

For each pattern, search the source, list every occurrence with a line citation, and propose a fix.

**Database access**

- `SELECT` inside `LOOP` / `DO` / `WHILE`. Recommend a single `SELECT ... FOR ALL ENTRIES` with a precondition guard, or a JOIN.
- `SELECT *` when only a few columns are used. Recommend explicit field list and a matching structured target.
- `FOR ALL ENTRIES` against an internal table without a `IF lt_keys IS NOT INITIAL` guard. This is a classic foot-gun: an empty driver table reads the whole base table.
- `FOR ALL ENTRIES` with duplicate or unsorted driver values that the developer forgot to `SORT` / `DELETE ADJACENT DUPLICATES`. Result rows can be deduplicated unexpectedly.
- Nested joins of more than four tables, or a join that drives off a non-indexed key. Recommend checking `SE11` index coverage and adding a secondary index or rewriting.
- Use of `INTO TABLE` without `PACKAGE SIZE` for potentially large result sets. Recommend cursor or package-size loop.
- `SELECT SINGLE` without a full key. In some kernels this returns an arbitrary row; recommend an explicit `UP TO 1 ROWS ... ORDER BY ... ENDSELECT` if the row choice matters.
- Reading transparent tables that have been simplified out in S/4HANA (e.g. `BSEG`, `BSAS`, `BSAD`, `BSIS`, `BSID` for finance, `MKPF/MSEG` for materials, `LIKP/LIPS` deltas) - flag for target `s4-*` releases and recommend the released compatibility views.

**Internal-table operations**

- `READ TABLE ... WITH KEY` on a `STANDARD TABLE` inside a loop. Recommend `SORTED` / `HASHED` table or a secondary key.
- `APPEND` then `SORT` then `DELETE ADJACENT DUPLICATES` when a `HASHED` or `SORTED UNIQUE` table would model the intent natively.
- `LOOP AT ... WHERE` on a `STANDARD TABLE` without a secondary key. For tables over a few thousand rows this is O(n*m); recommend a sorted secondary key.
- Copying entire internal tables by value into method parameters. Pass by reference (`IMPORTING ... TYPE STANDARD TABLE OF ... BY REFERENCE` or use `TYPE REF TO`).
- String concatenation in loops using `CONCATENATE` / `&&`. Recommend a string table + `CONCATENATE LINES OF`.

**Parallel / async**

- Long-running synchronous logic that fans out per row. Recommend `CALL FUNCTION ... STARTING NEW TASK` (aRFC), `CL_ABAP_PARALLEL`, or bgRFC for newer releases, with a worker pool and a results collector.
- Missing `WAIT UNTIL` or `RECEIVE` handlers after parallel dispatch. Flag as a correctness risk.
- For SAP BTP ABAP Environment, recommend `IF_OO_PARALLEL_CONCURRENCY_CONTROL` or the released background-process APIs instead of legacy task-spawning, which is not available.

### Pass 3 - Security checks

- **Authority checks.** Every entry point that reads or modifies sensitive data must call `AUTHORITY-CHECK OBJECT '<obj>' ID ... FIELD ...` with explicit `sy-subrc` evaluation before the data action, not after. RAP code should rely on declared `authority` in the behaviour definition rather than re-rolling checks in ABAP.
- **Dynamic SQL injection.** Any `SELECT ... WHERE (lv_where)` where `lv_where` is built from external input is a blocker. Recommend `CL_ABAP_DYN_PRG=>QUOTE`, `ESCAPE_QUOTES`, `CHECK_VARIABLE_NAME`, or restructuring to use ranges / static where clauses.
- **Dynamic program calls.** `GENERATE SUBROUTINE POOL`, `CALL FUNCTION lv_fn`, `CALL TRANSACTION lv_tcode`, and `SUBMIT (lv_prog)` with externally-influenced names. Require a whitelist via `CL_ABAP_DYN_PRG=>CHECK_WHITELIST_*`.
- **OS command execution.** `SXPG_COMMAND_EXECUTE`, `CALL 'SYSTEM'`. Almost always a finding - recommend reviewing whether the command is needed at all and, if so, pinning to a pre-registered SM69 command without parameter splicing.
- **File access.** `OPEN DATASET` paths must be validated against the authorization-group config; otherwise flag path-traversal risk. On S/4 Cloud and BTP, application-server file access is not available - blocker.
- **Hard-coded credentials.** Strings that look like keys, passwords, or tokens. Recommend the Secure Store (`CL_ABAP_SECURE_STORAGE`) or BTP destination service.
- **Logging.** Avoid logging full payloads of fields that may contain PII (BUT000 names, addresses, bank data) without masking. Note GDPR / data-protection exposure.
- **Trusted RFC.** Unchecked `CALL FUNCTION ... DESTINATION lv_dest` where the destination is user-supplied lets an attacker pivot. Restrict to a configured whitelist.

### Pass 4 - Maintainability and S/4 readiness

- Naming: legacy Hungarian (`lv_`, `lt_`, `gt_`) is acceptable in classic ABAP shops but Clean ABAP recommends intent-revealing names. Note but do not block.
- Method length over 50 statements, classes over 1000 statements - flag as major refactor candidates.
- `FORM` / `PERFORM` in greenfield code - recommend a class-based structure. Existing legacy code: not a blocker.
- Empty `CATCH` blocks, `CATCH cx_root`, `MESSAGE` with literal text outside a message class.
- Translatable text outside the text pool / message class.
- Obsolete statements removed or restricted in S/4HANA cloud: `TABLES` declarations for transparent tables (header-line behaviour), `OCCURS`, `WITH HEADER LINE`, native SQL, `EXEC SQL`. Mark these as blockers for `s4-cloud` / `btp-abap`.
- Direct read of CDS view source tables that have been simplified - prefer the released CDS view itself.
- Missing unit tests for non-trivial logic. Note as a minor finding with a suggested ABAP Unit skeleton.

### Severity rubric

- **Blocker.** Will not run on the target release, opens a security hole, or causes data loss / unbounded resource use.
- **Major.** Causes meaningful performance regression or future migration cost.
- **Minor.** Style, naming, missing comments, refactor opportunities.

## Inputs

- `abap_source` - required. Paste full source; do not truncate. The reviewer needs surrounding context to judge loops and authority-check placement.
- `target_release` - optional, drives which findings are blockers. Default `s4-on-premise`.
- `focus` - optional, default `all`. Set to a single area to get a shorter report.

## Outputs

- `review_report` - markdown grouped by severity. Each finding has: file/line, category, rule, why-it-matters (one sentence), recommendation.
- `suggested_diffs` - up to ten before/after snippets for the highest-impact findings, using `--- before` / `+++ after` style.

## Examples

> Input: a 300-line `ZFI_REPORT` that pulls open items from `BSIS` inside a loop over customers, no authority check, with a dynamic WHERE built from a selection screen.

Output (abridged):

```
[BLOCKER] L142 - SQL injection
  Dynamic WHERE clause `(p_where)` is concatenated from selection-screen
  input. Wrap with CL_ABAP_DYN_PRG=>CHECK_WHERE_NAME or restructure as
  ranges. See: cl_abap_dyn_prg documentation.

[BLOCKER] L88 - Missing authority check
  Report reads BSIS for any company code; AUTHORITY-CHECK on F_BKPF_BUK
  is absent. Add before the SELECT:
    AUTHORITY-CHECK OBJECT 'F_BKPF_BUK' ID 'BUKRS' FIELD ls_kna1-bukrs
                                       ID 'ACTVT' FIELD '03'.
    IF sy-subrc <> 0. ... ENDIF.

[BLOCKER] L88 - Simplified table on S/4HANA target
  BSIS is replaced by the ACDOCA-based compatibility view. Use V_BSIS or
  rewrite against I_JournalEntryItem CDS.

[MAJOR] L120 - SELECT inside LOOP
  Loop over 1..N customers issues one SELECT each. Refactor to a single
  FOR ALL ENTRIES on a pre-built key table; guard with IS NOT INITIAL.

[MINOR] L17  - SELECT *
  Only four columns used downstream. Specify the field list.
```

## Limitations

- Static review only. The skill does not run ATC, does not connect to a system, and cannot judge data volumes or runtime stats. Pair with ATC and SQL trace (ST05) for evidence-based tuning.
- The simplification-database knowledge is a snapshot. For an authoritative S/4HANA conversion, run the official Custom Code Migration Fiori app on your tenant.
- It will not catch every flavour of dynamic SQL injection (e.g. composed via `CL_ABAP_DYN_PRG` but with a flawed whitelist). The reviewer flags risk, not certainty.
- RAP behaviour-pool review is partial. Authorization in RAP is declarative; the reviewer notes when `authority` / `instance authority` is missing from the BDEF but does not parse `.cds` files directly.
- Not a substitute for a human code review. Use this as the first pass; the four-eyes principle still applies.

## Sources synthesised (all permissive)

- `SAP/styleguides` (Clean ABAP, ABAP Code Review) - Creative Commons; methodology only, no code copied.
- `SAP-samples/abap-cheat-sheets` - Apache-2.0; idioms for internal tables, RAP, authority checks.
- `SAP-samples/abap-platform-ccm-workshops` - Apache-2.0; ATC and simplification-database workflow.
- `ilyakaznacheev/abap-best-practice` - CC-BY-4.0; performance and clean-code categorisation.
- `SAP/abap-file-formats` - MIT; reference for repository-object structure.
- `abapGit/abapGit` - MIT; reference for what reviewable artefacts look like in git.
