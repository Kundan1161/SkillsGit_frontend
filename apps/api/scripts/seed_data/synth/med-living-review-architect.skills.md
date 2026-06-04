---
id: skillsgit-curated/med-living-review-architect
version: 1.0.0
name: Medical Living Review Architect
description: Design a living systematic review process — search refresh cadence, screening triage, update-vs-rewrite decisions, version control, and reader-facing communication of changes.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: healthcare
tags: [niche:systematic-review-methodology, living-review, evidence-surveillance, continuous-evidence-synthesis, version-control, update-strategy]
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
  estimated_tokens_per_invocation: 11000
trigger_keywords:
  - living systematic review
  - living evidence synthesis
  - rolling search
  - evidence surveillance
  - update vs rewrite
  - review refresh cadence
  - active learning screening
  - signal of new evidence
  - version control review
  - retire living review
example_invocations:
  - "Design the surveillance plan for our living review on emerging oncology biomarkers."
  - "We want to convert a static review on neonatal sepsis prophylaxis into a living format — what does the process look like?"
  - "Define the trigger that flips a living review from monitoring to a full re-grade."
inputs:
  - name: review_topic
    type: text
    required: true
    description: The clinical scenario the living review covers, why a static review is insufficient, and the intended audience (guideline group, clinical society, payer, patient organization).
  - name: existing_review_state
    type: choice
    required: false
    description: Where the review currently sits in its lifecycle.
    choices: [pre_protocol, protocol_registered, baseline_review_published, prior_update_published, retiring]
  - name: team_constraints
    type: text
    required: false
    description: Capacity available for surveillance — number of reviewers, hours per month, statistical capacity, information specialist availability, infrastructure for active-learning screening.
  - name: stakeholder_cadence
    type: text
    required: false
    description: How often downstream stakeholders (guideline panels, formulary committees, patient-facing summary publishers) need updates.
  - name: signal_definition_draft
    type: text
    required: false
    description: Any draft definition the team has for what counts as a triggering signal of new evidence (number of new trials, sample-size threshold, registry-listed but unpublished result).
outputs:
  - name: surveillance_plan_markdown
    type: markdown
    description: The full living-review surveillance plan with cadence, screening pipeline, triage rules, update vs. rewrite decision tree, versioning approach, communication plan, and retirement criteria.
  - name: triage_matrix
    type: markdown
    description: A decision table mapping new-evidence patterns to the next action (do nothing, summary update, conclusions update, full re-grade, scope review).
  - name: open_questions
    type: markdown
    description: Items the methodology lead and stakeholder owner must confirm before the surveillance plan goes live.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release. Synthesized from open-access methodology references with original instructional prose.
---

# Medical Living Review Architect

## When to use

Use this skill when a clinical evidence base is moving fast enough that a one-time review becomes stale before it ships — or quickly after — and the team needs a defensible plan for continuous surveillance, periodic re-grading, and reader-facing communication of changes. A living review is not a review that the team intends to update "eventually"; it is a review with a pre-specified surveillance process, a pre-specified update trigger, and a pre-specified retirement condition.

**This skill produces methodology guidance only. Outputs are not clinical recommendations. Every conclusion about treatment efficacy or safety must be reviewed by qualified clinical/research staff and confirmed against current clinical practice guidelines and primary literature.**

Typical triggers:

- A guideline group needs evidence that stays current between major guideline cycles.
- A regulator-approved therapy has rapidly evolving real-world evidence, and a static review will be wrong within months.
- A patient organization or clinical society wants a publicly readable evidence summary that visibly tracks the literature.
- A drug class is in active phase-three development; multiple trials will read out over the next two years and the team wants to fold them in as they appear rather than wait.
- A pandemic-style situation produces hundreds of relevant reports per month and the team needs triage rather than backlog growth.

Do not use this skill for:

- Authoring the baseline protocol — that is the protocol-author skill's job. A living-review surveillance plan is layered on top of a baseline protocol.
- Per-study risk-of-bias appraisal or certainty grading — those are upstream activities. The surveillance plan invokes them on a cadence.
- Clinical decision-making — the surveillance plan tells the team when the evidence base has shifted enough to merit reader-facing action; the action itself is a clinical and stakeholder decision.

## Inputs

- `review_topic` (required) — A description of the clinical scenario, why a static review is insufficient (rapidly evolving evidence, downstream guideline tempo, patient demand), and the intended audience.
- `existing_review_state` — Where the review currently sits. Determines whether the output focuses on setting up the surveillance process (pre-protocol or protocol-registered) or on operating it (baseline published or prior update published).
- `team_constraints` — The capacity envelope. A living review with one reviewer at four hours per month requires a very different cadence and screening pipeline than one with three reviewers and statistical support.
- `stakeholder_cadence` — How often downstream stakeholders expect updates. The surveillance cadence usually has to be at least as frequent as the stakeholder cadence.
- `signal_definition_draft` — Any draft definition of "triggering signal." The skill will refine this into a usable matrix.

## How to apply

Apply the steps in order. The output should be implementable: a person reading it should be able to start the surveillance process the next day.

### 1. Confirm that the topic warrants a living format

Not every review benefits from a living format. The conditions that favor it:

- **Active evidence stream.** New eligible studies are appearing at a rate of at least several per year, and the rate is unlikely to fall to zero soon.
- **Decision-relevance of incremental evidence.** Individual new studies are large enough or directly relevant enough that they could change conclusions, not just confirm them.
- **Stakeholder appetite for updates.** A downstream audience (a guideline group, a formulary committee, a clinical society) wants to act on updates.
- **Capacity for sustained work.** The team has either dedicated headcount or institutional support that can sustain the surveillance process. Living reviews that depend on one volunteer typically retire abruptly.

If any of the four is missing, the output should recommend a different format — a planned update cycle (e.g., every two or three years), a one-time review with a "next review by" date, or a scoping review followed by a static systematic review when the evidence stabilizes.

State the four conditions and the team's status against each. If recommending against a living format, propose the alternative.

### 2. Lock the baseline protocol assumptions before surveillance

The surveillance process cannot smooth over a soft baseline. Before defining cadence and triggers, confirm:

- The structured question (population, intervention, comparator, outcomes, designs) is stable and explicit.
- Eligibility criteria are testable.
- The information-source list and per-database search strings are documented and validated against a seed set.
- The extraction form is piloted.
- The bias-appraisal instrument is named.
- The synthesis approach (quantitative pooling vs. narrative) and the per-outcome certainty framework are stated.
- The baseline review (or pre-protocol) is registered in a public registry.

If any of these is unstable, recommend stabilizing them as Phase Zero before launching surveillance.

### 3. Set the search refresh cadence

Cadence is the heartbeat of the living process. Decide:

- **Continuous** — searches re-run weekly or daily; suitable only for high-stakes, high-tempo topics with infrastructure for automated retrieval and active-learning-assisted screening.
- **Monthly** — re-run searches once per month; the default for most living reviews with active evidence streams and moderate capacity.
- **Quarterly** — re-run searches every three months; appropriate when evidence is slowly accumulating, capacity is tight, or downstream cadence is quarterly.

The cadence should be:

- At least as fast as the stakeholder update cadence.
- At least as fast as the time it takes a single substantive new study to displace prior conclusions in the field.
- Slow enough that the team can actually keep up; a missed cadence becomes a backlog within weeks.

State the chosen cadence and the rationale.

### 4. Design the screening pipeline for incremental records

The incremental pipeline differs from the baseline screening pipeline in two ways: it operates on a stream rather than a snapshot, and it has the benefit of an already-curated set of included and excluded studies to learn from.

Design choices:

4.1. **Active-learning-assisted screening.** Use a screener trained on the baseline included/excluded set. New records are ranked by predicted relevance; reviewers screen in ranked order. Pre-specify the stopping rule (e.g., screen until N consecutive irrelevant records).

4.2. **Dual independent screening for borderline records.** For records that the screener ranks above a high-confidence threshold, single-reviewer screening with calibration may be acceptable; for records near the borderline, dual independent screening with conflict resolution is the standard.

4.3. **Triage tags.** Tag each new record with a triage category at first pass: clearly out of scope, plausibly in scope (needs full text), already included (a new report of an included study), or duplicate of an excluded record. Triage tags drive the next-action decision.

4.4. **Author and registry surveillance.** Beyond database searches, monitor a small set of trial registries, conference proceedings, and high-yield journals. Define the supplementary sources explicitly.

4.5. **Cross-check against prior-iteration outputs.** New records that are reports of already-included studies are not "new evidence"; they may update what is known about an included study but do not change the pool.

### 5. Define the signal-of-new-evidence matrix

The signal matrix is what flips the review from "surveillance" to "action." It is the most important single piece of a living-review design. Common signals:

- **New trial of substantive size.** A new randomized trial with sample size comparable to or larger than the largest included trial.
- **First trial in a previously-empty subgroup.** A trial that fills a gap (e.g., a previously absent pediatric subgroup).
- **Registry result without publication.** A registry-listed trial with results posted but no peer-reviewed publication; record but flag for caution.
- **Safety signal.** A safety report (regulatory, post-market) that touches an outcome in the review.
- **Methodological change.** A new bias instrument is recommended for the design family, or a new certainty framework is adopted by the team's stakeholders.
- **Conclusion-shifting accumulation.** Several small studies that together would alter a pooled estimate by more than a pre-specified margin.

For each signal type, specify the action triggered. Common actions:

- **Log only.** Record the new evidence in the living register; no reader-facing change.
- **Summary update.** Update the per-outcome study count and pooled estimate; re-render the summary table; flag in the changelog.
- **Conclusions update.** Re-run the synthesis and certainty grading for the affected outcome(s); update reader-facing conclusions.
- **Full re-grade.** Re-run synthesis and certainty grading across all outcomes; update the review version number.
- **Scope review.** Convene the team to reconsider whether the original question is still the right one (e.g., a new active comparator has displaced the placebo comparison in clinical practice).

Express the matrix as a small decision table that maps signal patterns to actions.

### 6. Set the update-versus-rewrite decision tree

Two failure modes haunt living reviews: updating endlessly without ever closing a version (which fatigues readers), and rewriting versions that should have been simple updates (which fatigues the team).

Heuristic decision tree:

- **No change** when no signal has fired in a cycle. Record "no change" in the public log so readers see surveillance is active.
- **Patch update** when a single new study has been incorporated and conclusions are unchanged. Increment the patch version (e.g., v1.0 → v1.1).
- **Minor update** when conclusions for one or more outcomes have shifted modestly (a certainty rating changes, a subgroup analysis appears, a new outcome is added). Increment the minor version (e.g., v1.1 → v1.2). Generate a per-outcome changelog.
- **Major update** when conclusions for the primary outcome have shifted, or when the question's scope has changed. Increment the major version (e.g., v1.2 → v2.0). Re-grade across all outcomes. Re-engage the stakeholder advisory group.
- **Rewrite** when the question itself needs replacement (different population, different comparator family) or the methodology has been overtaken by the field. A rewrite starts a new review with a new identifier; the old review is archived with a pointer to the successor.

State the criteria for each level explicitly and apply them per cycle.

### 7. Design the version control and provenance trail

A living review's credibility depends on a clear record of what changed when, and on the readers' ability to compare versions. Required elements:

- **Stable identifier and version number per release.** Use semantic versioning or an equivalent.
- **Per-release changelog.** What new studies were added, which outcomes shifted, which certainty ratings changed, and what reader-facing conclusions are affected.
- **Date stamps on every certainty rating.** A rating reflects the evidence as of a date; this date should travel with the rating.
- **Archived snapshots.** Each released version is archived in a way that makes the prior text comparable to the current text. A reader who cited an older version should be able to retrieve it.
- **Public surveillance log.** A simple log entry per cycle ("on YYYY-MM-DD, search re-run, N new records screened, M included, no conclusion change") is informative to readers and disciplines the team.
- **Methods register.** Every change to the protocol (eligibility, search, extraction, synthesis, grading) is logged with the date and rationale; deviations from the registered protocol are documented per cycle.

### 8. Plan the screening-fatigue and reviewer-burnout mitigations

Living reviews fail more often from human factors than methods. Plan for:

- **Rotation.** Multiple reviewers share the screening duty; no single person carries the whole cycle indefinitely.
- **Time budgeting.** Estimate the hours per cycle and book them; living reviews that depend on after-hours volunteer time tend to drift.
- **Re-calibration.** At a regular interval (e.g., every six months), all reviewers re-screen a small calibration set together to confirm that the screening decision rules have not silently drifted.
- **Sustainable software.** Use a citation manager, a screening tool, and an extraction tool that the team is comfortable maintaining. Bespoke spreadsheets often outlive the people who wrote them but only at a high error cost.
- **Onboarding script.** When a new reviewer joins, they read the protocol, the changelog, and the calibration set before taking a cycle.

### 9. Plan reader-facing communication

The audience for a living review wants to know two things on every visit: what is the current state, and what changed since last time. Plan:

- **Front-matter changelog.** A short block at the top of the review that lists changes in the current version with dates.
- **Per-outcome status flags.** Each outcome's row in the summary table carries a flag — unchanged, updated, new — relative to the prior version.
- **Plain-language alerts for major updates.** When a major update lands, push a short plain-language alert through the channels the audience already uses (mailing list, journal RSS, partner organization newsletter).
- **Citation guidance.** Tell readers how to cite the current version, and how to retrieve and cite an archived prior version.
- **Stable URL per version.** Each release has a stable, citable URL. The "latest" URL points to the most recent release.

### 10. Set the retirement criteria

Living reviews should not be eternal. Pre-specify the conditions under which the review is retired and what happens next:

- **The clinical question is no longer decision-relevant.** The intervention is withdrawn, the comparator is no longer used, or the underlying clinical context has changed.
- **The evidence base has stabilized.** New eligible studies have not appeared for a pre-specified period (often 18 to 36 months), and the conclusions are stable. The review converts to a static review with a "next review by" date.
- **A more appropriate format has emerged.** A guideline group has absorbed the synthesis into its recommendation; the team's role becomes maintaining the inputs to the guideline rather than maintaining a standalone review.
- **Capacity has ended.** The team can no longer sustain the surveillance process. In that case, the review is published as a final static version with a clear retirement note; readers should not encounter a living review that has silently stopped updating.

State the retirement criteria and the announcement plan.

### 11. Plan the stakeholder advisory cadence

Living reviews thrive when stakeholders own part of the process. Suggested structure:

- **Standing advisory group.** Clinical lead, methodology lead, patient or community representative, statistician, information specialist, downstream-stakeholder liaison (e.g., guideline group member).
- **Light cadence between major updates.** A short asynchronous note per cycle ("here is what we screened and what we found; no action requested"). A live meeting only when a major update is being weighed.
- **Decision points logged.** Any time the advisory group's input changes a methodology decision (eligibility, outcomes, thresholds), log the input and the rationale.

### 12. Internal validation before emit

Before producing the final plan, check:

- The four warrant conditions are addressed.
- The baseline protocol is locked or the plan flags it as a prerequisite.
- Cadence is set with rationale and is at least as fast as stakeholder cadence.
- Screening pipeline includes active-learning-assisted or equivalent ranking, dual independent screening for borderline records, and triage tags.
- Signal matrix maps to actions; the actions are tied to versioning rules.
- Update-vs-rewrite tree is concrete.
- Version control includes stable identifiers, dated certainty ratings, archived snapshots, and a public surveillance log.
- Reviewer burnout mitigations are pre-specified.
- Reader-facing communication includes a changelog, status flags, plain-language alerts for major updates, and citation guidance.
- Retirement criteria are stated.
- Stakeholder advisory cadence is named.

### 13. Emit

Produce `surveillance_plan_markdown` covering all twelve sections, a compact `triage_matrix` table, and an `open_questions` list of items requiring methodology-lead and stakeholder-owner sign-off.

### Decision rules and heuristics

- **Cadence beats reactivity.** A predictable monthly cycle outperforms heroic catch-ups every six months.
- **Pre-specify the trigger.** A signal that is judged ad hoc in each cycle drifts into "we update when we feel like it." That is not a living review.
- **Version numbers are reader trust.** A v2.0 with a clear changelog says the review has been re-grounded; a string of v1.x patches says nothing has fundamentally changed since baseline.
- **Active learning is a tool, not a method.** It speeds screening; it does not lower the methodological bar for inclusion or quality. The stopping rule and the validation against a held-out set are what make it defensible.
- **Make retirement boring.** A pre-stated retirement criterion that triggers cleanly is far better than a slow fade.
- **Communicate when nothing changed.** A "no change this cycle" log entry is reassuring to the audience and disciplining to the team.

### Edge cases

- **Pandemic-style surge in records.** Hundreds of records per month can saturate even active-learning-assisted screening. Pre-specify a triage protocol that escalates inclusion thresholds during surge periods and documents the methodological compromise.
- **Network of related living reviews.** If multiple living reviews share search infrastructure (e.g., a class of drugs across several conditions), centralize the search and de-duplication; let each review consume the shared output via its eligibility filter.
- **Single-team capacity collapse.** A pre-specified handover protocol (which artifacts are archived, which credentials and tools are transferred, how readers are notified) keeps a credible retirement available.
- **Major methodological change in the field.** When a new bias instrument or certainty framework becomes the de facto standard, plan a one-time re-grade against the new framework at the next major update; do not silently switch.
- **Conflicting guideline cycles.** When two stakeholder guidelines update on different cadences, align the living review's update cadence with the faster cycle and provide a stable "guideline-aligned snapshot" at each slower cycle.
- **Living scoping reviews.** Scoping reviews can be living too; the matrix is simpler (new study types or new sub-domains rather than new conclusions) but the architecture is the same.
- **Living overview of reviews.** The signal types shift toward "new included review" and "withdrawal of an included review." Plan an overlap-recomputation step on each new-review signal.

## Outputs

- `surveillance_plan_markdown` — Full plan document covering warrant, baseline assumptions, cadence, screening pipeline, signal matrix, update-vs-rewrite tree, version control, burnout mitigation, reader communication, retirement, and advisory cadence.
- `triage_matrix` — Compact decision table mapping signal patterns to next actions and version impacts.
- `open_questions` — Items requiring methodology-lead and stakeholder-owner sign-off.

## Examples

### Worked example (abbreviated)

Input:

> Topic: Living review of monoclonal antibody therapies for early Alzheimer's disease. Pipeline is active, with multiple phase-three readouts expected over the next 18 months. Audience: a clinical society's clinical practice committee and a patient advocacy organization. Team: 2 clinical reviewers, 1 methodologist, statistical support, monthly information-specialist support. Stakeholder cadence: clinical society updates its practice statement twice yearly; patient organization wants quarterly summaries.

Output (abbreviated):

```
Warrant: all four conditions met. Active evidence stream (≥2 large trials reading out per
  year), decision-relevance high (each readout could shift conclusions on benefit-harm balance),
  stakeholder appetite confirmed by two stakeholder owners, capacity sufficient for monthly cycle.

Baseline assumption check: protocol registered; outcomes locked; certainty framework chosen;
  bias instrument family chosen; baseline review published. PROCEED.

Cadence: monthly search re-run. Faster than stakeholder cadence (quarterly is faster of the two).

Screening pipeline:
  - Active-learning ranker trained on baseline includes/excludes; stopping rule when 50
    consecutive irrelevant records.
  - Dual independent screening for the top 100 ranked records per cycle.
  - Triage tags: out-of-scope, plausibly in-scope (full text), known-included new report, duplicate.
  - Supplementary monitoring: 2 trial registries, 1 conference proceedings set, 2 high-yield journals.

Signal matrix:
  - New phase-three trial of >=500 participants → Conclusions update for affected outcome,
    version minor bump.
  - New regulatory safety signal → Conclusions update for safety outcome, version minor bump.
  - Accumulation of >=3 small trials shifting pooled estimate by >=10% relative → Conclusions
    update, version minor bump.
  - First trial in a previously-empty subgroup (e.g., earliest-stage population) → Conclusions
    update, version minor bump.
  - New methodological standard adopted by stakeholder → Major update at next cycle, version
    major bump.
  - No qualifying signal → Log-only, no version change.

Update-vs-rewrite tree:
  - Patch (v1.0 → v1.1): one new study, conclusions unchanged.
  - Minor (v1.1 → v1.2): conclusions shifted on one or more secondary outcomes.
  - Major (v1.2 → v2.0): conclusions shifted on primary outcome OR scope changed.
  - Rewrite: new clinical question (e.g., move from monoclonal antibody class to a broader
    disease-modifying-therapy review).

Version control:
  - Semantic versioning. Stable DOI per release. Archived snapshot per version. Public
    surveillance log entry per cycle.

Burnout mitigation:
  - Reviewer rotation every 3 cycles. Booked 6 hours per cycle per reviewer. Re-calibration
    every 6 months on a 50-record set.

Reader-facing communication:
  - Front-matter changelog. Per-outcome status flags (unchanged/updated/new).
  - Plain-language alert through stakeholder channels at every minor or major update.
  - "Cite this version" block with DOI and date.

Retirement criteria:
  - Pipeline matures and no new eligible studies appear for 24 months, OR
  - Stakeholder absorbs synthesis into a maintained guideline and requests retirement, OR
  - Team capacity ends — issue final static version with retirement notice.

Stakeholder advisory cadence:
  - Async note every cycle; live meeting only for minor or major updates.
  - Patient-organization representative reviews the plain-language alert before each release.
```

Triage matrix (abbreviated):

```
Signal                                          | Action                | Version impact
------------------------------------------------|-----------------------|---------------
No new eligible record                          | Log only              | No change
1 small new trial, conclusions unchanged        | Patch update          | v1.x → v1.(x+1)
1 large new trial OR accumulation crossing 10%  | Conclusions update    | Minor bump
Safety signal on a critical outcome             | Conclusions update    | Minor bump
Primary-outcome conclusion shift                | Full re-grade         | Major bump
Scope change                                    | Rewrite               | New review id
Methodological standard change                  | Schedule major update | Major bump at next cycle
```

Open questions (abbreviated):

```
- Confirm the active-learning stopping-rule threshold (50 consecutive irrelevant) against the
  baseline corpus before launch; validate on a held-out set.
- Confirm with stakeholders that minor-update plain-language alerts are wanted, or whether
  alerts should be reserved for major updates only.
- Confirm DOI infrastructure and snapshot archival venue with the publishing partner.
- Confirm budget for monthly information-specialist support over the planned 24-month horizon.
- Confirm the patient-organization representative's role: review only, or co-author of the
  plain-language alert.
```

## Limitations

- A living review's value depends on sustained team capacity. The plan can document the cadence; it cannot guarantee the time.
- Active-learning-assisted screening lowers throughput cost but does not eliminate the need for human judgment on borderline records.
- Signal matrices are pre-specified but the field's idea of "decision-relevant" can shift. The matrix should be revisited at every major update.
- Reader-facing changelogs are most useful when readers actually read them; if the audience treats the review as monolithic, the version distinctions blur. Mitigate by linking specific reader-facing claims to specific versions.
- The skill produces a process, not the underlying clinical content. Every conclusion still requires the upstream methodology (protocol, extraction, bias appraisal, certainty grading) to have been done correctly.
- Retirement is awkward to plan for at launch but essential. A living review that silently stops updating is worse than a static review.

## Sources reviewed

- Cochrane Handbook chapters on living systematic reviews (CC-BY for some editions; methodology read, not text copied)
- PRISMA 2020 reporting framework, prisma-statement.org (cited for terminology)
- GRADE Working Group documentation, gradeworkinggroup.org (methodology read for certainty considerations applied at each surveillance cycle)
- AMSTAR 2 documentation (read for context on how living reviews are appraised by downstream readers)
- Open-access journal articles on living-systematic-review methods, JCE / BMJ open-access set (methodology read)
- https://github.com/asreview/asreview (active-learning-assisted screening, Apache-2.0)
- https://github.com/prisma-flowdiagram/PRISMA2020 (flow-diagram tooling)
- https://github.com/mcguinlu/robvis (bias-table visualization, MIT)
- https://www.equator-network.org/ (reporting-guideline registry)
