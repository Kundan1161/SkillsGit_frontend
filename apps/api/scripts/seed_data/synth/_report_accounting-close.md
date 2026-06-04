# Wave-2 Synthesis Report — Niche: Accounting & Month-End Close

**Agent niche:** finance — accounting & month-end close (journal entries, reconciliations, accruals, audit support).
**Run date:** 2026-05-14.
**Files produced:** 4 new skills (no existing accounting-close skills found in synth/ to merge).

## Skills produced

1. **finance-month-end-close-conductor.skills.md** — `skillsgit-curated/month-end-close-conductor`
   - Sequences the close as a DAG: cutoffs, sub-ledger close, accruals, reconciliations, review, reporting. Produces a day-by-day calendar, a dependency-graph JSON, and a risk register. Five phases with explicit entrance/exit gates; critical-path identification; reopen rule; fluctuation-analysis pre-check.

2. **finance-journal-entry-author.skills.md** — `skillsgit-curated/journal-entry-author`
   - Converts a transaction narrative into a balanced journal entry plus a documentation package: memo (what / why now / how calculated / support / reverses on), support library by transaction family, review-requirement rules tied to materiality, and a pattern library of 10 canonical entry shapes (AP accrual, prepaid, deferred revenue, fixed asset acquire/dispose, payroll accrual, allowance for doubtful, SBC, FX revaluation, reclass).

3. **finance-reconciliation-builder.skills.md** — `skillsgit-curated/reconciliation-builder`
   - Designs balance-sheet account reconciliation processes: independent source identification, cadence, matching rules, reconciling-item categorization with aging buckets (0-30/31-60/61-90/90+), exceptions queue, review separation, escalation thresholds. Pattern library covers 9 account families (cash, AR, AP, prepaid, accrued, fixed assets, intercompany, deferred revenue, suspense).

4. **finance-audit-pbc-fulfiller.skills.md** — `skillsgit-curated/audit-pbc-fulfiller`
   - Operationalizes a Prepared-by-Client list as a project: request-type taxonomy, owner/backup assignment, internal-due-date buffer, evidence-package standards, sample-response protocol, walkthrough prep, status taxonomy with escalation rules, management-rep-letter sequencing. Covers financial-statement audit, SOC 1/2, SOX, internal audit, tax/regulatory audits.

## Sources used (verified permissive: MIT / Apache-2.0 / BSD-3 / CC0)

| Repo | License | Stars | Used in skills | Notes |
|---|---|---|---|---|
| https://github.com/ledger/ledger | BSD-3-Clause | 5.9k | 1, 2, 3 | Canonical double-entry CLI; informed entry mechanics and cutoff thinking. |
| https://github.com/ekmungai/python-accounting | MIT | 197 | 1, 2, 3, 4 | Python IFRS/GAAP-flavored double-entry; informed entry shapes and reporting integration. |
| https://github.com/imetaxas/double-entry-bookkeeping-api | MIT | 60 (sub-threshold, disclosed) | 1, 2, 3 | Library enforcing debits=credits; informed validation/self-check stages. |
| https://github.com/apache/fineract-cn-accounting | Apache-2.0 | 30 (sub-threshold, disclosed; archived 2024) | 1, 2, 3, 4 | Journal-entry-and-ledger service; informed gating/posting model. |
| https://github.com/SolidInvoice/SolidInvoice | MIT | 881 | 1, 2, 3 | Invoicing + recurring billing; informed AR-side patterns. |
| https://github.com/panshak/accountill | MIT | 1.7k | 1, 2 | MERN invoicing; informed AR / customer-receivable patterns. |
| https://github.com/Etherlabs-dev/multi-processor-reconciliation | MIT | 1 (sub-threshold, disclosed) | 3, 4 | Multi-processor reconciliation pipeline; informed matching-rule and exception-queue design. |
| https://github.com/preftech/reconciliation | MIT | 23 (sub-threshold, disclosed) | 3 | OpenRefine recon framework; informed match/fuzzy patterns. |
| https://github.com/getprobo/awesome-compliance | CC0-1.0 | 80 (sub-threshold, disclosed) | 1, 4 | Compliance frameworks catalog; informed control/evidence terminology. |
| https://github.com/plaintextaccounting/plaintextaccounting | Community hub | n/a | 1, 2, 3, 4 | PTA portal; informed plain-text accounting conventions. |

All citations URL-only. No copied prose, no logos/trademarks invoked, no code reproduction.

## Licenses explicitly rejected (transparency)

The accounting open-source ecosystem skews heavily GPL/AGPL, which falls outside this project's MIT/Apache-2.0/BSD/ISC/Unlicense allowlist. Rejected:

| Repo | License | Why rejected |
|---|---|---|
| simonmichael/hledger | GPL-3.0 | Copyleft; not permitted. |
| beancount/beancount | GPL-2.0 | Copyleft; not permitted. |
| Gnucash | GPL-3.0 (project-wide) | Copyleft; not permitted. |
| darcys22/godbledger | GPL-3.0 | Copyleft; not permitted. |
| arrobalytics/django-ledger | GPL-3.0 | Copyleft; not permitted. |
| frappe/books | AGPL-3.0 | Network copyleft; not permitted. |
| FrontAccountingERP/FA | GPL-3.0 | Copyleft; not permitted. |
| ledgersmb/LedgerSMB | GPL-2.0 | Copyleft; not permitted. |
| akaunting/akaunting | BSL (Business Source License) | Not OSI permissive; not permitted. |
| bentleygd/ITGC | GPL-3.0 | Copyleft; not permitted. |

The niche is unusually sparse for permissive-licensed implementations. The skills compensate by leveraging the broadly applicable double-entry mechanics that any of the above projects would also implement (the underlying GAAP/IFRS bookkeeping is methodology, not the projects' code), and by adding plain-text-accounting community references and adjacent permissive projects (invoicing, reconciliation tooling) that exercise the same patterns.

## Patterns surfaced repeatedly across the niche

Across the permitted source base and the broader literature, these patterns recurred and were encoded into the skills:

- **The cutoff is load-bearing.** Every methodology surveyed treats the cutoff as the central control of a close. Skills 1 and 2 encode this explicitly.
- **Sub-ledger truth precedes GL truth.** Reconciliations that compare GL to its own derivatives reconcile garbage to itself. Skill 3 enforces independence tiering.
- **Two-eyes review is the load-bearing control.** Preparer/reviewer separation appears in every audit-defensible methodology. Skills 2, 3, 4 all enforce it.
- **Aged reconciling items are audit findings in waiting.** Aging buckets (0-30, 31-60, 61-90, 90+) and escalation rules are standard. Skill 3 codifies; Skill 4 mirrors for PBC items.
- **Reversing entries are first-class objects, not afterthoughts.** Every accrual has a reversal date in the same record. Skill 2 enforces.
- **Fluctuation analysis beats scrubbing.** Targeted variance review compresses controller review from a marathon to a scan. Skill 1 encodes.
- **The PBC is a project, not a list.** Owners, internal-due-date buffers, status taxonomy, escalation thresholds. Skill 4 encodes.
- **Position memos pre-empt audit challenges.** For known hard items, the memo is drafted before the auditor asks. Skill 4 encodes.

## Cross-skill integration

The four skills compose:

- Close-conductor (1) names tasks; for each accrual or adjusting entry the team books, the journal-entry-author (2) generates the entry and memo; for each balance-sheet account, reconciliation-builder (3) gives the rec design used in Phase 3 of the close; once year-end arrives, audit-PBC-fulfiller (4) packages the close's evidence into auditor-facing deliverables. Hand-off points are referenced explicitly in each skill's "When to use" section.

## Tagging

All four skills:
- `category: finance`
- first tag `niche:accounting-close`
- 4-7 additional tags drawn from {month-end, close-calendar, accruals, reconciliations, controls, days-to-close, gaap, journal-entry, debits-credits, documentation, materiality, signoff, audit-trail, balance-sheet, bank-rec, intercompany, exceptions, evidence, audit, pbc, workpaper, sampling, external-audit, response-quality}.

`license_type: free` on all four. No pricing fields (per instructions).

## Confidence

- **Skills 1 (close-conductor), 2 (journal-entry-author), 3 (reconciliation-builder)** — high confidence. The underlying methodology is widely documented in the permissive source base, in the plain-text-accounting community, and in cross-referenced practitioner literature; the skills synthesize patterns that would be familiar to any controller reading them.
- **Skill 4 (audit-PBC-fulfiller)** — high confidence on methodology, moderate confidence on permissive-license source backing. The PBC workflow is well-attested in practitioner literature but most open-source artifacts in audit tracking are GPL-licensed or proprietary; the skill leans on adjacent compliance/reconciliation tooling and on broad audit-management patterns. Disclosed in the sources list.

## Suggested follow-ups (out of scope for this wave)

- **Bank-reconciliation-executor** as a separate execution skill (vs. the design-focused reconciliation-builder). Would consume an actual bank statement and GL extract and produce the matched/unmatched output.
- **Revenue-recognition-conductor** specific to ASC 606 / IFRS 15 — the close-conductor surfaces it but does not deeply model performance-obligation analysis, variable consideration, or contract-modification handling.
- **Lease-accounting-conductor** under ASC 842 / IFRS 16 — touched at the policy level in the journal-entry-author but a dedicated skill would model ROU asset and lease liability roll-forwards.
- **Fixed-asset roll-forward generator** — a templated schedule generator complementary to skills 2 and 3.
- **Tax-provision conductor** — the close-conductor sequences tax provision; a dedicated skill would model current/deferred tax mechanics. (Note: the niche is even more sparsely served by permissive open source; would need careful sourcing.)
- **Consolidations conductor** — eliminations, currency translation, equity-method investments. Specialist domain; permissive open-source backing is thin.

## Operational notes

- All files validate the wave-2 frontmatter template (id, version, name, description ≤280 chars, authors, category, tags, license_type, pricing.currency, pricing.support_included, ai block, trigger_keywords, example_invocations, inputs, outputs, changelog).
- All bodies are between 300 and 700 lines.
- All skills have a `## Sources reviewed` section with URL-only citations.
- No emojis used in any output.
- All prose original; no copied content from any source repo's README, code comments, or documentation.
