---
id: skillsgit-curated/knowledge-base-content-audit
version: 1.0.0
name: Knowledge Base Content Audit
description: Audits an existing knowledge base or company handbook for staleness, duplication, missing ownership, orphan pages, and conflicting sources of truth, then prescribes a prioritized remediation plan.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: operations
tags: [niche:handbook-as-code, knowledge-management, content-audit, documentation, governance, technical-debt, remediation, single-source-of-truth]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - knowledge base audit
  - wiki audit
  - handbook audit
  - documentation cleanup
  - stale documentation
  - orphan pages
  - content audit
  - documentation rot
  - duplicate pages
  - source of truth conflict
  - documentation debt
  - wiki cleanup
example_invocations:
  - "Our internal wiki has 3,000 pages and we're not sure which are still accurate. Audit and prescribe what to do."
  - "We just inherited a knowledge base from a merger. Identify duplications and conflicts."
  - "Our handbook has decayed over two years. Build the remediation plan."
inputs:
  - name: kb_overview
    type: text
    required: true
    description: Description of the knowledge base — tool, size in pages, age, scope (engineering-only, full handbook, mixed), and any visible structure.
  - name: page_inventory
    type: text
    required: false
    description: A page list or sample — paste a table of contents, a sitemap, or a CSV export of page titles plus last-modified dates. Even a partial sample sharpens the audit.
  - name: known_issues
    type: text
    required: false
    description: Pain points the team has already named — pages they know are stale, conflicts they've spotted, areas where readers have complained.
  - name: time_budget
    type: choice
    required: false
    description: How much remediation effort the team can sustain. Drives whether the plan is staged over a quarter or a year.
    choices: [light-1-quarter, medium-6-months, deep-12-months]
  - name: deletion_authority
    type: choice
    required: false
    description: Whether the auditor (or whoever runs the audit) has authority to delete pages, or can only recommend deletion to page owners.
    choices: [can-delete, recommend-only]
outputs:
  - name: audit_report
    type: markdown
    description: A complete audit report with findings categorized by issue type, severity-tagged, with a prioritized remediation backlog.
  - name: remediation_plan
    type: markdown
    description: A standalone plan sized to the time budget, with sequenced milestones and named owners.
  - name: page_triage_table
    type: markdown
    description: A page-by-page triage table for the sampled pages, with categorization (keep, update, merge, deprecate, delete) and rationale.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a knowledge base has accumulated enough sediment that nobody trusts it anymore. The forcing event is usually one of a few patterns: a new joiner reports they cannot tell which of three pages on the same topic is current; a leader discovers that a policy in the handbook contradicts the one their team has been operating under for a year; a search returns six results for a question and none of them are unambiguously right; a security or compliance review surfaces pages with information that should not exist there; the team decides to migrate to a new handbook system and needs to know what to bring forward. In all of these cases the underlying problem is the same: the knowledge base has drifted, and the remediation is not a single edit but an audit-plus-plan.

The skill operates on knowledge bases of any age, size, and tool. It is most valuable on knowledge bases that crossed roughly five hundred pages with no consistent ownership model, the threshold at which decay becomes ambient rather than spot-fixable. It works on internal wikis, public handbooks, engineering documentation portals, and operations playbook libraries — any artifact where the relationship between pages and the systems or processes they describe has loosened.

The skill is not the right tool for a fresh knowledge base under a year old (the issues it diagnoses have not had time to develop), for a knowledge base that has been actively curated against a stated standard (the audit will find little), or for a single-page reference document. It also stops short of executing the remediation: the audit produces categorization and a plan, but the actual edits, merges, and deletions are work the team does over weeks. Treating the audit output as if it were the remediation is the most common reason teams run audits and see no change.

## How to apply

The skill follows a ten-step audit method. The order matters: inventory before classification, classification before scoring, scoring before remediation planning. Skipping straight to "what should we do?" produces remediation that targets visible symptoms but misses the structural issues underneath.

1. **Build a representative page inventory.** If a full list is available, use it. If not, sample carefully — by section, by age, by recent-activity, by reader-traffic if traffic data is available. The sample should over-represent the high-traffic pages (where decay produces the most reader pain) and the oldest pages (where decay is most likely). A 100-200 page sample from a 3,000 page knowledge base is enough to characterize the issue patterns; trying to audit every page is the most common reason audits never finish.

2. **Capture three pieces of metadata per page, even when the tool does not surface them well.** Title, last-modified date (or last-substantively-edited date — typo fixes do not count as substantive), and apparent owner if any is visible. If the tool does not record owners, infer from the page history (who has edited it most, who created it) and mark inferred owners as low-confidence. These three fields determine most of the downstream classification.

3. **Run the seven decay checks against each sampled page.** The decay checks are: (a) staleness — last-modified date older than the page's natural review cadence; (b) ownership — no owner or an owner who has left the organization; (c) duplication — another page covers the same topic with comparable depth; (d) conflict — another page makes a statement that contradicts this one; (e) orphan — no page links to this one and it is not on any standard reader path; (f) drift — the systems or processes the page describes have changed but the page has not; (g) scope-creep — the page has expanded to cover topics beyond its stated purpose and now violates the single-source-of-truth boundary. Each check produces a yes/no per page; a page can fail more than one.

4. **Categorize each page into one of five remediation classes.** The classes are: KEEP (the page is current and well-shaped, no action needed); UPDATE (the page is structurally fine but content needs refresh — the lightest remediation); MERGE (the page overlaps with another and the two should be combined into one); DEPRECATE (the topic the page covers is no longer active and the page should be marked deprecated with a tombstone but retained for historical reference); DELETE (the page is wrong, misleading, or duplicates a current source and should be removed). The mapping from decay checks to remediation class is the heart of the methodology: staleness alone often maps to UPDATE, duplication maps to MERGE if both have value or DELETE if one is plainly inferior, conflict maps to MERGE or DELETE depending on which side is correct, orphans map to DELETE unless they document something valuable that needs a path built to them, drift maps to UPDATE if reachable owner exists or DELETE if it does not.

5. **Score severity by reader cost, not by issue count.** Not all stale pages are equally costly. A stale page on a high-traffic onboarding path is severity-high; a stale page on a low-traffic historical reference is severity-low even if the staleness is extreme. The severity score is what drives prioritization. Pages with a severity-high tag get remediated first regardless of how easy they are to fix; pages with severity-low can wait or be batched. Score on a 1–5 scale: 5 for "actively misleads readers making consequential decisions"; 1 for "technically inaccurate but nobody reads it." A team should expect roughly 10–20% of decayed pages to be severity-4-or-5, and that fraction is where the audit's value concentrates.

6. **Identify the structural patterns the per-page findings reveal.** Per-page findings are useful but not sufficient. The audit's interpretive value is in finding structural patterns: an entire section with no owner; a topic that has duplicate pages because two different teams each thought they owned it; an entire policy area that has drifted because the team that wrote it dissolved; a recurring pattern of pages with the same one or two prolific editors and no review process. These structural patterns are usually three to seven findings that account for half or more of the per-page issues. Naming them is what turns the audit from a triage list into a diagnosis.

7. **Distinguish content debt from architectural debt.** Content debt is per-page issues fixable by per-page work — stale text, broken links, missing owner. Architectural debt is structural — the knowledge base has no section for a topic that has emerged, multiple sections cover overlapping ground because the information architecture predates current reality, ownership cannot be assigned because the underlying team structure changed. Architectural debt is more expensive to fix and cannot be batched; it requires re-architecting before the per-page work makes sense. The audit must separate the two so the remediation plan does not try to fix architectural issues with page-by-page work.

8. **Build the remediation plan in three waves.** Wave one is the severity-high content debt and any quick-wins (delete the obviously-dead pages, fix the conflicts the audit identified, assign owners where the answer is unambiguous). Wave one should be completable in the time budget's first quarter and produces visible signal that the audit had teeth. Wave two is the rest of the content debt, distributed across page owners to do alongside their regular work. Wave three is the architectural debt — re-section, re-assign ownership, redesign the broken parts. Wave three is the slowest and benefits from being explicit about its slowness: a six-month wave-three milestone for a moderate-sized handbook is realistic; a one-week milestone is fantasy.

9. **Decide the deletion policy and document it visibly.** Deletion is the action team members are most reluctant to take. The audit should specify the deletion threshold (e.g., severity-4-or-5 pages with no current owner and no inbound links are deleted by the auditor; severity-3 and below require page-owner concurrence; deletion is logged with a 30-day soft-delete window before permanent removal). Without a stated deletion policy, deletions get litigated case by case, the audit slows to a crawl, and the bulk of the cleanup never happens. With a stated policy, the team can defend the deletions to anyone who later objects.

10. **Schedule the next audit before this one finishes.** The audit is a recurring event, not a project. A knowledge base that was audited once and never again will return to its prior state within eighteen months. The remediation plan should include the cadence of subsequent audits (lightweight quarterly, deeper annual) and the trigger for an unscheduled audit (a major reorganization, a tool migration, a leadership change in the team that owns the handbook).

### Severity scoring guide

The severity score combines three factors. The skill applies the following matrix:

- **Reader traffic / proximity to onboarding paths.** A page on the first-week onboarding path scores +2 on traffic regardless of measured visits; pages reachable from any "Working here" or "How we work" top-level page score +1; pages reachable only from a search query score 0; pages with no inbound links score 0 on traffic but produce other findings.
- **Consequence of acting on stale information.** Pages whose stale guidance could result in payroll error, compliance failure, customer-data mishandling, or production outage score +2; pages whose stale guidance results in personal inconvenience score +1; pages whose stale guidance has no operational consequence score 0.
- **Visibility of the staleness to the reader.** A page that confidently states something wrong is worse than a page whose staleness is obvious (an unfilled placeholder, an obviously old screenshot) because the reader will act on the wrong content. Confidently-wrong pages get +1.

Sum the factors; cap at 5. Severity 4 or 5 enters wave one. Severity 3 enters wave two. Severity 1 or 2 enters wave three or is deferred indefinitely.

### Output structure

The audit report follows this layout:

1. `# Knowledge Base Audit Report`
2. `## Inventory summary` — what was sampled, how, why this sample is representative
3. `## Findings by issue type` — counts and examples for each of the seven decay checks
4. `## Structural patterns` — the three-to-seven cross-cutting diagnoses
5. `## Content debt vs architectural debt` — explicit separation
6. `## Severity-scored remediation backlog` — the actionable list, ordered by severity
7. `## Three-wave remediation plan` — milestones, owners, time budget
8. `## Deletion policy` — the explicit rule the team will operate under
9. `## Audit cadence going forward` — when to run this again
10. `## Appendix: page triage table` — the per-page categorization for the sampled pages

### Pitfalls the audit must call out explicitly

- **The audit-as-project trap.** The team runs the audit, produces the report, files it, and moves on. Nothing changes. Fix: the audit's deliverable is the wave-one execution, not the report. The report alone is half the work.
- **The everyone-owns-everything trap.** The remediation plan distributes pages back to "the team" without naming individual owners. Nothing happens. Fix: every wave-one and wave-two item names a specific role and a target date.
- **The cleanup-without-architecture trap.** The team executes wave one and wave two but skips wave three because architectural work is harder. Within two years the same audit produces the same findings. Fix: schedule wave three with leadership commitment before wave one starts.
- **The deletion-blockage trap.** The team is uncomfortable deleting pages, so deletion candidates linger forever as "deprecated but kept just in case." The knowledge base remains large and confusing. Fix: the deletion policy includes hard removal after a soft-delete window.
- **The vanity-metric trap.** The team measures "pages remediated" instead of reader pain reduced. A team can remediate 500 low-severity pages and not improve a single reader's experience. Fix: severity-weighted progress, plus a reader-survey re-take after wave one.
- **The audit-by-fiat trap.** The audit is run by an outside party or a newcomer who does not know the team's context. Pages are flagged for deletion that look stale but actually encode hard-won institutional knowledge. The team revolts. Fix: every wave-one deletion candidate is reviewed with at least one long-tenured team member who can flag historical significance the audit missed.
- **The single-axis trap.** The audit focuses on staleness alone. Duplication, conflict, and orphan issues go unaddressed. The knowledge base becomes a current but poorly-organized graveyard. Fix: the seven decay checks are run as a set; staleness alone is insufficient diagnosis.
- **The tool-migration trap.** The audit is framed as preparation for a tool migration ("we'll fix this when we move to the new platform"). Migration becomes the excuse to defer cleanup. Then migration imports everything, including the rot, and the new tool starts decayed. Fix: cleanup happens before migration in scope; migration imports only pages that have passed audit.

### Audit conducted by an AI assistant vs. a human

When the audit is run by an AI assistant against an exported corpus, three additional considerations apply.

First, the assistant cannot easily judge reader traffic without instrumentation. The audit should request traffic data or a proxy (the page's mention frequency in chat history, the count of inbound links from other handbook pages). Without it, severity scoring degrades to a content-quality assessment only.

Second, the assistant can scan for conflicts (two pages making contradictory claims) more reliably than a human can over a large corpus. The audit should lean into this capability — running explicit checks for contradictions on specific topics (compensation philosophy, security practices, operational procedures) where conflict is most costly.

Third, the assistant cannot judge whether a long-tenured team member would recognize a page as institutionally important. Pages that look stale by the seven decay checks may be load-bearing in non-obvious ways. The audit's deletion recommendations should be tagged "verify with [role] before action" rather than treated as fait accompli.

### Pre-audit setup the audit document should request

Before running an audit, the team benefits from preparing five inputs. The audit output should request these explicitly if missing:

- **The page inventory** with last-modified dates and edit history at minimum; with view counts if available.
- **The ownership intent.** Where does the team think ownership should sit, even if the actual pages do not reflect it? This becomes the target state for wave-three reassignment.
- **The named pain points.** What has gone wrong because of the knowledge base's current state? Concrete failures, not generic complaints.
- **The deletion authority and the soft-delete window.** Without this the audit can categorize but cannot execute.
- **The sponsoring leader.** Who is going to hold the team to the remediation plan when wave-two energy flags? Without a named sponsor, the audit becomes wave-one-only.

## Inputs

- **Knowledge base overview (required, text).** Sets scope and tone. A 200-page wiki gets a different remediation cadence than a 5,000-page handbook.
- **Page inventory (optional, text).** Even a partial inventory sharpens the audit; without it the skill produces a generic audit method rather than a findings-grounded report.
- **Known issues (optional, text).** The team's own diagnosis, even if partial, calibrates the audit and lets the skill validate or revise the team's hypothesis.
- **Time budget (optional, choice).** Drives wave sizing.
- **Deletion authority (optional, choice).** A "recommend-only" auditor needs to design the recommend-to-owner workflow explicitly; a "can-delete" auditor can act on findings directly within the deletion policy.

## Outputs

A complete audit report; a standalone remediation plan suited to the time budget; a per-page triage table for the sampled pages.

## Examples

### Worked example: a five-year-old engineering wiki and its general handbook

**Input KB overview:** "An engineering wiki and a general handbook share the same hosting tool. Around 2,400 pages total. The wiki started narrow but has accumulated process, meeting notes, and ad-hoc references. The handbook has clearer top-level sections but they're outdated."

**Input page inventory:** "A 180-page sample stratified across age and section was provided. Average last-edited date: 14 months ago. About 22% of sampled pages have no apparent owner; 18% have an owner who has left the company."

**Input known issues:** "Onboarding suffers — new engineers ask their manager rather than reading the wiki. We suspect we have at least three pages each on incident response, code review, and deployment, with different content."

**Input time budget:** "medium-6-months"

**Input deletion authority:** "can-delete with logging"

**Expected output (excerpt):**

> ## Structural patterns
>
> Five structural patterns explain most of the per-page findings.
>
> 1. **The "former owners" cliff.** 18% of sampled pages have an owner who has left. Ownership was never reassigned, the pages have not been updated since, and there is no mechanism for owner-departure to trigger reassignment. This pattern explains most of the severity-3-and-above stale pages.
>
> 2. **The "incident response sprawl."** Five distinct pages cover incident response, written by different people at different times, each reflecting a slightly different process. The pages cross-link inconsistently; new joiners cannot tell which is current. This pattern alone accounts for one of the named pain points.
>
> 3. **The "meeting-notes-as-reference" anti-pattern.** Roughly 8% of sampled pages are old meeting notes that have become quasi-reference because they are the only written record of a decision. They are not labeled as such; they are not maintained. Most should be converted to decision records and the originating note pages should be archived.
>
> 4. **The "experiment archive."** Around 12% of pages document experiments, spikes, or prototypes from earlier years. They are accurate as historical record but actively confusing as current reference because they describe approaches that were not adopted. Most should be deprecated with a clear tombstone rather than deleted.
>
> 5. **The "onboarding gap."** The handbook's onboarding section has three pages, all over a year stale, none of which match the current engineering onboarding process. Engineers have built workarounds (manager-maintained docs, shared with each new hire) that further fragment the canonical source.
>
> ## Three-wave remediation plan (six-month budget)
>
> **Wave one (weeks 1–6): severity-high content debt and quick wins.**
>
> - Resolve the three duplicate-process areas (incident response, code review, deployment) by selecting the most current of each and deprecating the others. One technical writer plus the manager of each respective area. Target: end of week 4.
> - Reassign ownership for the 33 sampled pages whose owners have left, prorated to current team leads. Target: end of week 3.
> - Delete the 14 severity-5 pages that are confidently wrong and have no current owner, after a one-week soft-delete window for objection. Target: end of week 6.
>
> **Wave two (weeks 7–16): bulk content debt.**
>
> - Distribute the remaining severity-3 stale pages to current owners with a four-week review-or-deprecate window. Target: end of week 14.
> - Convert ~20 high-value meeting-notes-as-reference pages to decision records. Target: end of week 16.
>
> **Wave three (weeks 17–26): architectural debt.**
>
> - Rebuild the onboarding section against the current engineering onboarding process, owned by the head of engineering with the lead recruiter. Target: end of week 22.
> - Establish a quarterly owner-departure trigger that reassigns ownership on offboarding. Target: end of week 20 (process design); ongoing thereafter.
> - Schedule the next audit for month 12 (lightweight quarterly checks beginning month 9). Target: scheduled by end of week 26.

### Worked example: a newly merged knowledge base from two companies

**Input KB overview:** "Post-acquisition, we have two knowledge bases: ours (1,100 pages, organized) and theirs (1,800 pages, recently chaotic during the integration). We need to converge them within nine months."

**Input page inventory:** "Full inventory available. Two coverage maps were built showing topic overlap; about 40% of topics have pages in both sources."

**Input known issues:** "Conflicting compensation philosophies. Conflicting incident-response runbooks. Two different sets of values content. Confusion among integrated employees about which set of pages applies."

**Input time budget:** "deep-12-months" (with a 9-month soft target)

**Input deletion authority:** "can-delete with logging and joint-side approval for cross-side conflicts"

**Expected output (excerpt):**

> ## Structural patterns specific to a merger context
>
> 1. **Conflicting-source-of-truth pairs.** Approximately 480 topics have pages in both source bases. For each, one must become canonical and the other deprecated. Default rule: where both pages are accurate, the page from the acquiring company is canonical and the acquired company's page links to it; where the acquired company has stronger content (it has been demonstrated, e.g. by referee review, to be more accurate or more usable), that page becomes canonical instead. Decisions are recorded as decision records during the convergence so the rationale survives.
>
> 2. **Value statements that cannot be merged.** Cultural artifacts (values, principles, "how we work" content) carry organizational identity. Mechanical merge produces lifeless committee output. These pages are re-written from scratch by leadership rather than merged page-by-page.
>
> 3. **Process content with materially different histories.** Incident response, deployment, code review, hiring — both organizations had working processes. Convergence is a small project per process area, not a per-page audit. These are scoped as wave-three architectural items.
>
> 4. **Tool-specific content for tools being deprecated.** The acquired company's tooling that will not survive integration produces pages that should be archived rather than reconciled. Identify these early and remove from convergence scope.
>
> 5. **The "we always did it this way" pages.** Both organizations have these — pages that codify the founding team's preferences with no current rationale. Use the convergence as the opportunity to ask whether the practice survives the merger, and re-write the page only if it does.
>
> ## Three-wave plan adapted to convergence
>
> Wave one (weeks 1–10): resolve the highest-pain conflicts (compensation philosophy, incident response, security practices). One reconciliation lead per area, with explicit decision-making authority from each side's prior leadership.
>
> Wave two (weeks 11–28): bulk per-page reconciliation. Tagged in batches by topic area; each batch has a named owner from the integrated organization. Decisions recorded; deletions soft-deleted with thirty-day window.
>
> Wave three (weeks 29–40): architectural integration. Re-section the converged handbook around the post-merger team structure (which may not match either original). Reassign ownership against the new structure. Establish the freshness audit cadence for the post-integration steady state.

## How to sample when a full inventory is unavailable

A knowledge base of a few thousand pages cannot always be inventoried completely before the audit begins. Strategic sampling produces results that characterize the corpus reliably while keeping the audit tractable.

The sampling strategy stratifies along four axes:

- **By section.** Take a proportional sample from each top-level section so no area is unexamined. Twenty pages per section, capped at a reasonable total, is a defensible default for large knowledge bases.
- **By age.** Over-sample the oldest pages (highest decay risk) and the newest pages (where issues like missing owner or unclear scope are common). Middle-aged pages are sampled at the base rate.
- **By edit frequency.** Pages that have been edited frequently in the last year are usually maintained; pages with no edits in two years are usually decayed. Sample heavily from both ends — frequently-edited pages may have drift or scope-creep issues that frequent editing masks; rarely-edited pages are the staleness leading indicators.
- **By reader traffic, if available.** Over-sample the high-traffic pages because their decay produces the most reader pain. Under-sample (but do not skip) the low-traffic pages — they are candidates for deletion that may not be caught by other axes.

A 150-200 page sample drawn this way characterizes the issue patterns in a 2,000-5,000 page knowledge base reliably. For larger corpuses, double the sample size and accept that the audit takes proportionally longer.

## Communicating the audit findings without alienating contributors

The audit can be received as a critique of the people who built the knowledge base. This is a real political risk and the audit communication matters as much as the findings.

The framing principles:

- **Describe decay structurally, not personally.** "These twenty-eight pages have decayed because the page-owner role was never assigned" is true and useful; "the team did not maintain these pages" is true but received as blame.
- **Celebrate what works.** A meaningful percentage of any decayed knowledge base has well-maintained pages. The audit's structural-patterns section should name two or three areas where the team has done well, and the cover note for the audit should lead with these.
- **Make remediation feel like an investment, not a cleanup.** Wave one is presented as the team building the conditions for wave-two and wave-three benefits, not as paying down debt that someone incurred.
- **Frame deletions carefully.** A page being deleted is the closure of a topic that no longer applies. Pages with historical significance are deprecated rather than deleted; the distinction matters for contributors who care about their past work.
- **Share the audit before publishing it.** Sponsoring leaders see the audit privately first, can flag context the audit missed, and become advocates rather than reactive.

## What success looks like a year after the audit

A successful audit-plus-remediation cycle produces measurable changes. The audit report should name what the team will check for at month twelve:

- Reader survey scores on "the handbook gave me the information I needed" trending up from the pre-audit baseline.
- Time-to-find for routine questions decreasing (sampled in onboarding feedback and in support-channel patterns).
- Reduction in the volume of "is this still accurate?" questions in chat.
- The next audit (a lighter quarterly check or the annual deep audit) finding meaningfully fewer severity-high issues, especially in areas that received wave-three architectural attention.
- Page-owner coverage approaching 100% (the easiest leading indicator that the practice has taken hold).

Naming these explicitly in the audit report turns the remediation from a project into the start of a maintenance practice.

## Stakeholder roles in the audit

The audit succeeds when several roles play their part. The audit report should name these roles even if the team has not formally assigned them yet.

- **The sponsor.** A leader with authority over the affected area, who can commit time and resources to remediation. The sponsor reviews the audit findings, approves the deletion policy, and surfaces blockers when wave-two energy slows. Without a named sponsor, the audit becomes documentation of decay rather than a force for change.
- **The auditor.** The person (or AI assistant) running the audit. The auditor is responsible for the inventory, the decay checks, the categorization, the severity scoring, and the draft remediation plan. The auditor's bias is toward objective categorization; they should resist becoming the remediation executor for everything they identify.
- **The page owners.** The roles or teams currently responsible for each page (or the roles inferred to be responsible if no formal ownership exists). Page owners execute wave-two remediation on their pages. The audit's distribution to owners is the moment the work transfers from the auditor to the team.
- **The steward.** The role that owns the knowledge base architecture going forward. If no steward exists, the audit identifies the need for one and the remediation plan creates the role. The steward inherits the audit's residual responsibilities — running the next audit, maintaining the deletion log, holding the line on freshness practice.
- **The long-tenured advisor.** A team member with enough institutional history to flag content the audit might mis-categorize. The advisor reviews wave-one deletion candidates before action.

## The audit report's executive summary

The audit report leads with a short executive summary suitable for the sponsor's leadership team. The summary contains five elements:

1. Two sentences describing what the audit examined and how.
2. The headline finding — typically a single most-impactful structural pattern.
3. Severity-by-volume breakdown (how many pages at each severity level).
4. The recommended wave-one investment (in person-weeks) and the wave-three commitment needed for full remediation.
5. The risk of not acting — what continues to happen if the remediation does not get prioritized.

The executive summary's job is to get the sponsor's commitment to wave one and to the wave-three architectural work. The detailed body of the report is for the people doing the work.

## Limitations

- The skill audits content quality and structure; it does not audit factual accuracy in deep domains. A stale page on a complex regulatory topic may need a subject-matter expert to verify, not just a category. The skill flags such pages with a "requires SME review" tag rather than recommending direct action.
- The skill's sampling is statistical, not exhaustive. A 180-page sample of a 2,400-page wiki characterizes the patterns reliably but cannot guarantee that an unusual issue in an unsampled page will be caught. The team should plan for additional spot-checks during remediation.
- The skill cannot enforce the remediation plan. Audit-fatigue is real; teams complete wave one with energy, slow in wave two, and skip wave three. Sustained sponsorship from a leader who reviews progress monthly is the single biggest predictor of full execution.
- The skill assumes the knowledge base is technically accessible — pages have titles, dates, edit history, and can be exported or sampled. Knowledge bases on platforms that lock this metadata away (some closed wikis, some legacy intranets) require manual sampling that limits the audit's depth.
- The skill does not address translated or multi-language knowledge bases beyond noting that translation introduces a class of staleness (the English source updates, translations lag) that needs specific policy outside this skill's scope.

## Sources reviewed

Sources informed the methodology only — no prose was copied. License tags below.

- https://github.com/clef/handbook — CC0-1.0 (reviewed for handbook structure and page-owner patterns)
- https://github.com/hkdobrev/awesome-handbooks — CC0-1.0 (index used to understand the breadth of knowledge base shapes a generic audit must address)
- https://github.com/madetech/handbook — license not explicit in repository README (reviewed structurally; no content reproduced)
- Generic single-source-of-truth methodology in technical writing literature (industry references reviewed for the SSOT-violation taxonomy that informs the seven decay checks)
- Open documentation-as-code methodology references (used to ground the wave-three architectural-debt framing)
- CC-BY-SA-licensed transparent-company handbook reference material was reviewed for niche patterns; no prose, structure, or trademarked names were carried into this skill — methodology only.
